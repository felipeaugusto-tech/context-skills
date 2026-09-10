#!/usr/bin/env python3
"""HTTP transport for the TestRail API v2. Standard library only.

Scope
-----
This module knows how to make an authenticated, retried, redirect-safe request
to TestRail and hand back parsed JSON. It knows nothing about MCP, and nothing
about which operations are *permitted* — that is ``guards.py``'s job. Keeping
the two apart means the authorisation logic can be tested without a socket, and
read that way in review.

Transport hardening, and why each piece is here
-----------------------------------------------
* **Cross-host redirect blocking.** urllib's default redirect handler copies
  request headers — including ``Authorization`` — onto the redirected request.
  An open redirect on the instance, or a typo'd ``TESTRAIL_URL``, would hand the
  Basic Auth blob to a third party. The redirect has to be refused *before* it
  is followed; checking afterwards is too late, the credential is already gone.
* **HTTPS downgrade blocking.** Same reasoning for a same-host ``https -> http``
  redirect, which would put the credential on the wire in cleartext.
* **Landed-host assertion.** Belt and braces, in case a handler is ever swapped.
* **Retry-After clamping.** A server-supplied delay is untrusted input: an
  unbounded value would hang the agent for hours, and NaN would crash
  ``time.sleep``.
* **Method is passed explicitly, never inferred.** urllib silently switches to
  POST the moment ``data=`` is non-None. Every call site therefore states its
  method, and ``request()`` asserts the two agree.
"""

from __future__ import annotations

import base64
import http.client
import json
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable

from config import Config

API_PATH = "/index.php?/api/v2/"

USER_AGENT = "QA-GenDD-testrail-bridge/1.0"

# Server states worth retrying for a *read*.
RETRYABLE_STATUS = frozenset({429, 500, 502, 503, 504})

# For a write, only 429 is safely retryable. A 429 is refused before TestRail
# applies anything, so replaying it cannot duplicate. A 5xx or a timeout is
# ambiguous — TestRail may well have created the case and failed on the way back
# — and retrying would silently produce a duplicate that nothing in the response
# reveals. TestRail's API has no idempotency-key mechanism to lean on, so the
# only safe choice is to surface the ambiguity and let the caller check.
RETRYABLE_STATUS_FOR_WRITES = frozenset({429})

REDIRECT_STATUS = frozenset({301, 302, 303, 307, 308})

MAX_BACKOFF_SECONDS = 60.0
MAX_RETRY_AFTER_SECONDS = 60.0

# A server that ignores `offset` would otherwise page forever.
MAX_PAGES = 500


class TestRailError(RuntimeError):
    """Base class for every failure this module raises."""


class AuthError(TestRailError):
    """401 or 403 from TestRail: bad credential, or the API is disabled."""


class NotFoundError(TestRailError):
    """400/404 for a referenced entity. Usually a bad id, not a bug."""


class TransportError(TestRailError):
    """Network or server failure that survived every retry."""


class AmbiguousWriteError(TestRailError):
    """A write failed in a way that leaves it unknown whether it was applied.

    Raised instead of retrying, because a retry could duplicate. The message
    always tells the caller to verify before re-sending — that instruction is the
    entire point of having a distinct exception type.
    """


class RateLimitError(TestRailError):
    """429 that survived every retry."""


# --------------------------------------------------------------------------- #
# redirect safety
# --------------------------------------------------------------------------- #


class _StrictRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Refuses any redirect that would leak or downgrade the credential."""

    def __init__(self, allowed_host: str, require_https: bool) -> None:
        self.allowed_host = (allowed_host or "").lower()
        self.require_https = require_https

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        target = urllib.parse.urlparse(newurl)
        target_host = (target.hostname or "").lower()

        reason = None
        if target_host != self.allowed_host:
            reason = f"cross-host redirect to {target.scheme}://{target.netloc}"
        elif self.require_https and target.scheme != "https":
            reason = f"https->{target.scheme} downgrade on {target.netloc}"

        if reason:
            raise urllib.error.HTTPError(
                newurl,
                code,
                f"refused {reason}; credentials are never forwarded",
                headers,
                fp,
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


# --------------------------------------------------------------------------- #
# client
# --------------------------------------------------------------------------- #


class TestRailClient:
    """Authenticated TestRail API v2 client.

    ``transport`` is injectable purely so the test suite can run the whole stack
    — retries, pagination, error mapping — with no network. Production passes
    None and gets urllib.
    """

    def __init__(
        self,
        config: Config,
        transport: Callable[[urllib.request.Request, int], tuple[int, str, dict]] | None = None,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.config = config
        self._sleep = sleep
        self._transport = transport or self._urllib_transport
        self.request_count = 0
        self.write_count = 0

        if config.api_key:
            blob = base64.b64encode(
                f"{config.user}:{config.api_key}".encode()
            ).decode()
            self._auth_header = ("Authorization", f"Basic {blob}")
            # The base64 blob is itself credential-equivalent, so it must be
            # scrubbed as well as the raw key it was built from.
            config.redactor.register(blob)
        else:
            self._auth_header = ("Cookie", config.session_cookie or "")

        self._opener = urllib.request.build_opener(
            _StrictRedirectHandler(
                config.host, require_https=config.scheme == "https"
            )
        )

    # -- convenience -------------------------------------------------------- #

    def scrub(self, text: str) -> str:
        return self.config.redactor.scrub(text)

    # -- transport ---------------------------------------------------------- #

    def _urllib_transport(
        self, request: urllib.request.Request, timeout: int
    ) -> tuple[int, str, dict]:
        with self._opener.open(request, timeout=timeout) as response:
            # Cross-host redirects are already blocked before being followed.
            # Compare hostnames only, so a port or letter-case difference is not
            # mistaken for an attack.
            landed = urllib.parse.urlparse(getattr(response, "url", "") or "")
            landed_host = (landed.hostname or "").lower()
            if landed_host and landed_host != self.config.host:
                raise TransportError(
                    f"response came from {landed_host}, not {self.config.host} — "
                    f"refusing to trust it. Check TESTRAIL_URL, and rotate the "
                    f"credential if this was not expected."
                )
            body = response.read().decode("utf-8", errors="replace")
            return response.status, body, dict(response.headers)

    # -- core --------------------------------------------------------------- #

    def request(
        self,
        method: str,
        endpoint: str,
        payload: dict[str, Any] | None = None,
        **params: Any,
    ) -> Any:
        """Issue one API call, retrying transient failures.

        ``endpoint`` is a bare API method such as ``get_case/12`` or
        ``add_case/34``.
        """
        method = method.upper()
        if method not in ("GET", "POST"):
            raise TestRailError(f"unsupported HTTP method {method!r}")
        if method == "GET" and payload is not None:
            # urllib turns any request with data= into a POST. Catching the
            # mismatch here keeps a mislabelled call from silently writing.
            raise TestRailError(
                f"internal error: GET {endpoint} was given a request body"
            )
        if method == "POST" and not self.config.write_enabled:
            # Defence in depth. guards.py should have stopped this already and
            # write tools are not even registered in read mode, but the single
            # place every byte leaves for TestRail is worth a second check.
            raise TestRailError(
                f"refusing to POST {endpoint}: the bridge is in read-only mode "
                f"(TESTRAIL_MODE=read)"
            )

        url = self.config.base_url + API_PATH + endpoint
        # TestRail's router already carries the method in the query string, so
        # extra params append with '&', not '?'.
        for key, value in params.items():
            if value is None:
                continue
            url += (
                f"&{urllib.parse.quote(str(key), safe='')}"
                f"={urllib.parse.quote(str(value), safe='')}"
            )

        body: bytes | None = None
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")

        is_write = method == "POST"
        retryable = RETRYABLE_STATUS_FOR_WRITES if is_write else RETRYABLE_STATUS

        attempt = 0
        while True:
            attempt += 1
            request = urllib.request.Request(url, data=body, method=method)
            if request.get_method() != method:
                raise TestRailError(
                    f"internal error: request method became "
                    f"{request.get_method()}, expected {method}"
                )
            request.add_header(*self._auth_header)
            request.add_header("Content-Type", "application/json")
            request.add_header("User-Agent", USER_AGENT)

            try:
                self.request_count += 1
                if method == "POST":
                    self.write_count += 1
                status, raw, _headers = self._transport(request, self.config.timeout)
                return self._parse(raw, endpoint)

            except urllib.error.HTTPError as exc:
                detail, retry_after = self._read_error(exc)

                if exc.code in REDIRECT_STATUS:
                    raise TransportError(
                        f"blocked redirect on {endpoint}: {self.scrub(str(exc.reason))}. "
                        f"Point TESTRAIL_URL at the instance's canonical https host."
                    ) from exc

                if exc.code in (401, 403):
                    raise AuthError(self._auth_hint(exc.code, endpoint, detail)) from exc

                if exc.code == 404:
                    raise NotFoundError(
                        f"HTTP 404 on {endpoint}. The endpoint or id does not "
                        f"exist on this instance: {detail}"
                    ) from exc

                if exc.code == 400:
                    # TestRail returns 400 for both "bad id" and "invalid field
                    # value", and its message is the only way to tell them apart,
                    # so pass it through verbatim rather than paraphrasing.
                    raise NotFoundError(f"HTTP 400 on {endpoint}: {detail}") from exc

                if exc.code in retryable and attempt <= self.config.max_retries:
                    self._sleep(self._backoff(attempt, retry_after))
                    continue

                if exc.code == 429:
                    raise RateLimitError(
                        f"still rate limited on {endpoint} after "
                        f"{self.config.max_retries} retries. Reduce the page size "
                        f"or narrow the query."
                    ) from exc

                if is_write and exc.code >= 500:
                    raise AmbiguousWriteError(
                        f"HTTP {exc.code} on {endpoint}. The write was NOT retried, "
                        f"because a 5xx can mean TestRail applied the change and "
                        f"then failed on the way back — retrying would risk a "
                        f"duplicate. Check TestRail for the intended change before "
                        f"re-sending. TestRail said: {detail}"
                    ) from exc

                raise TransportError(f"HTTP {exc.code} on {endpoint}: {detail}") from exc

            except urllib.error.URLError as exc:
                if is_write:
                    raise AmbiguousWriteError(
                        f"network failure during {endpoint}: {exc.reason}. The write "
                        f"was NOT retried, because the request may have reached "
                        f"TestRail and been applied before the connection broke. "
                        f"Check TestRail before re-sending."
                    ) from exc
                if attempt <= self.config.max_retries:
                    self._sleep(self._backoff(attempt, None))
                    continue
                raise TransportError(
                    f"could not reach {self.config.base_url} after "
                    f"{self.config.max_retries + 1} attempts: {exc.reason}. If "
                    f"TestRail is only reachable on the corporate network, "
                    f"connect to the VPN first."
                ) from exc

            except (
                TimeoutError,
                ConnectionError,
                ssl.SSLError,
                http.client.HTTPException,
            ) as exc:
                # urllib only wraps failures raised while *opening* the
                # connection into URLError. A timeout, reset, truncated TLS
                # record or short body during response.read() escapes both
                # clauses above — they are OSError siblings of URLError, not
                # subclasses — so without this branch a read-phase failure would
                # surface as a bare "Unexpected TimeoutError", never be retried,
                # and on a write would skip the do-not-re-send warning.
                if is_write:
                    raise AmbiguousWriteError(
                        f"{type(exc).__name__} while reading the response to "
                        f"{endpoint}. The write may have been applied — the "
                        f"response was lost, not the request. Check TestRail "
                        f"before re-sending."
                    ) from exc
                if attempt <= self.config.max_retries:
                    self._sleep(self._backoff(attempt, None))
                    continue
                raise TransportError(
                    f"{type(exc).__name__} on {endpoint} after "
                    f"{self.config.max_retries + 1} attempts. The instance may be "
                    f"overloaded; try a smaller page size."
                ) from exc

    # -- helpers ------------------------------------------------------------ #

    def _parse(self, raw: str, endpoint: str) -> Any:
        if not raw.strip():
            # add_* endpoints answer with a body; delete_* legitimately do not.
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            hint = (
                "This is usually an SSO or login interstitial, which means the "
                "request was not authenticated as an API call."
            )
            if self.config.auth_mode == "session_cookie":
                hint += (
                    " In session-cookie mode it most often means the cookie has "
                    "expired — refresh it from the browser."
                )
            else:
                hint += (
                    " Check that the API is enabled under Administration -> Site "
                    "Settings -> API."
                )
            raise TransportError(
                f"{endpoint} returned a non-JSON body. {hint} ({exc})"
            ) from exc

    def _read_error(self, exc: urllib.error.HTTPError) -> tuple[str, str | None]:
        """Extract a scrubbed, length-capped message and any Retry-After."""
        retry_after = None
        try:
            if exc.headers:
                retry_after = exc.headers.get("Retry-After")
        except Exception:  # pragma: no cover - defensive
            retry_after = None
        try:
            raw = exc.read().decode("utf-8", errors="replace")
        except Exception:  # pragma: no cover - defensive
            raw = ""
        detail: Any = raw
        try:
            parsed = json.loads(raw)
            if isinstance(parsed, dict):
                detail = parsed.get("error", raw)
        except json.JSONDecodeError:
            pass
        return self.scrub(str(detail))[:400], retry_after

    def _auth_hint(self, code: int, endpoint: str, detail: str) -> str:
        if self.config.auth_mode == "session_cookie":
            cause = (
                "the session cookie has expired or was invalidated by a logout "
                "(this is the main drawback of cookie mode), or this account "
                "lacks access to the entity"
            )
        else:
            cause = (
                "the API key is wrong or revoked; TESTRAIL_USER is not the login "
                "email; the API is disabled instance-wide (Administration -> Site "
                "Settings -> API -> Enable API); or this account lacks access to "
                "the entity"
            )
        return f"HTTP {code} on {endpoint}. Likely cause: {cause}. TestRail said: {detail}"

    def _backoff(self, attempt: int, retry_after: str | None) -> float:
        """Honour Retry-After when sane; otherwise exponential backoff.

        Retry-After is untrusted: clamp it so a hostile or broken value cannot
        stall the agent, and reject NaN, which would make ``time.sleep`` raise.
        """
        if retry_after:
            try:
                wait = float(retry_after)
            except (TypeError, ValueError):
                wait = None
            else:
                if wait == wait and wait != float("inf"):  # NaN/inf check
                    return min(max(1.0, wait), MAX_RETRY_AFTER_SECONDS)
        return min(float(2 ** attempt), MAX_BACKOFF_SECONDS)

    # -- public verbs ------------------------------------------------------- #

    def get(self, endpoint: str, **params: Any) -> Any:
        return self.request("GET", endpoint, None, **params)

    def post(self, endpoint: str, payload: dict[str, Any]) -> Any:
        return self.request("POST", endpoint, payload)

    def get_collection(
        self,
        endpoint: str,
        key: str,
        max_items: int | None = None,
        **params: Any,
    ) -> list[dict[str, Any]]:
        """Read a list endpoint, tolerating both response shapes.

        TestRail 6.7+ wraps list responses as
        ``{"offset":.., "limit":.., "size":.., "<key>":[..]}``; older versions
        return a bare array. Handle both rather than pinning a version, because
        the bridge does not control when the instance is upgraded.
        """
        if max_items is not None and max_items <= 0:
            return []

        page_size = self.config.page_size
        if max_items is not None:
            page_size = min(page_size, max_items)

        items: list[dict[str, Any]] = []
        offset = 0
        for _ in range(MAX_PAGES):
            payload = self.get(endpoint, limit=page_size, offset=offset, **params)

            if payload is None:
                break
            if isinstance(payload, list):  # legacy unpaginated
                items.extend(v for v in payload if isinstance(v, dict))
                break
            if not isinstance(payload, dict):
                break

            batch = payload.get(key)
            if not isinstance(batch, list) or not batch:
                break
            items.extend(v for v in batch if isinstance(v, dict))

            if max_items is not None and len(items) >= max_items:
                return items[:max_items]
            if len(batch) < page_size:
                break
            offset += page_size
        else:
            raise TransportError(
                f"{endpoint}: stopped after {MAX_PAGES} pages — the server may be "
                f"ignoring `offset`. Narrow the query rather than trusting this."
            )

        return items[:max_items] if max_items is not None else items


def as_list(value: Any, key: str | None = None) -> list[dict[str, Any]]:
    """Coerce an API payload to a list of dicts.

    When ``key`` is given it is authoritative: a wrapper such as
    ``{"errors": [], "cases": [...]}`` would otherwise yield the wrong list
    depending on dict ordering. If the key is absent the result is empty rather
    than a guess — falling back to "first list found" here would reintroduce
    exactly the ordering dependence the key exists to remove.
    """
    if isinstance(value, list):
        return [v for v in value if isinstance(v, dict)]
    if isinstance(value, dict):
        if key is not None:
            found = value.get(key)
            return [v for v in found if isinstance(v, dict)] if isinstance(found, list) else []
        for candidate in value.values():
            if isinstance(candidate, list):
                return [v for v in candidate if isinstance(v, dict)]
    return []

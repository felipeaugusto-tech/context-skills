#!/usr/bin/env python3
"""TestRail read-only discovery — derives the field map from a live instance.

Purpose
-------
Before any AI-generated test case is pushed to TestRail, the generation flow needs
a *field map*: which of our case fields correspond to which real TestRail fields,
what vocabularies are configured, and what conventions the existing suite already
uses. Inventing that map is how imports silently produce garbage. This script
reads it off the instance instead.

It is deliberately **read-only**. Every request is constructed with a literal
``method="GET"``, no ``data=`` payload is ever attached, and no TestRail write
endpoint (``add_*``, ``update_*``, ``delete_*``) is referenced anywhere in this
file. There is also an ``assert`` on the request method, though note that asserts
are stripped under ``python -O`` -- the literal is the real guarantee.

Output is a Markdown report (default `testrail-field-map.md`) intended to be
committed and referenced by the TestRail connector doc and the case-push skill.

Configuration (environment variables only — never CLI flags, never literals)
---------------------------------------------------------------------------
    TESTRAIL_URL          e.g. https://accurate.testrail.io
                          (TESTRAIL_INSTANCE_URL also accepted, same name the
                          community MCP server uses)
    TESTRAIL_USER         your TestRail login, normally your email
                          (TESTRAIL_USERNAME also accepted)
    TESTRAIL_API_KEY      generated under My Settings -> API Keys

The key inherits *your* permissions. Treat it as a password: never commit it,
never paste it into a chat or ticket, and prefer a key you can revoke.

Usage
-----
    export TESTRAIL_URL=https://accurate.testrail.io
    export TESTRAIL_USER=you@example.com
    export TESTRAIL_API_KEY=...            # or read from your secret store

    # what can I see, and is the API even enabled?
    python3 engine/ci/testrail_discovery.py --probe

    # full discovery against one project, sampling 200 cases
    python3 engine/ci/testrail_discovery.py --project 12 --max-cases 200

    # every visible project (slower; watch the rate limit)
    python3 engine/ci/testrail_discovery.py --all-projects

Exit codes
----------
    0  success
    1  configuration error (missing/invalid env vars, bad URL)
    2  authentication or authorisation failure (bad key, API disabled)
    3  transport failure after retries
    4  nothing discoverable (no visible projects)

Dependencies: none. Python 3 standard library only.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

API_PATH = "/index.php?/api/v2/"

# TestRail custom-field type ids. Verify against your instance if a label here
# looks wrong -- the raw type_id is always printed alongside the name so a
# mismatch is visible rather than silent.
CUSTOM_FIELD_TYPES: dict[int, str] = {
    1: "String",
    2: "Integer",
    3: "Text",
    4: "URL",
    5: "Checkbox",
    6: "Dropdown",
    7: "User",
    8: "Date",
    9: "Milestone",
    10: "Steps",
    11: "Step Results",
    12: "Multi-select",
}

SUITE_MODES: dict[int, str] = {
    1: "single suite",
    2: "single suite + baselines",
    3: "multiple suites",
}

# Our case structure (see .cursor/skills/qa-test-case-writer/SKILL.md) mapped to
# what TestRail offers natively, plus keywords used to hunt for an existing
# custom field before recommending that one be created.
REPO_FIELDS: list[dict[str, Any]] = [
    {"name": "Name", "native": "title", "keywords": []},
    {"name": "Ticket", "native": "refs", "keywords": ["ref", "ticket", "story", "jira"]},
    {"name": "Steps", "native": "custom_steps_separated", "keywords": ["step"]},
    {"name": "Preconditions", "native": "custom_preconds", "keywords": ["precond", "prereq"]},
    {"name": "Priority", "native": "priority_id", "keywords": ["priority"]},
    {"name": "Test Type", "native": "type_id", "keywords": ["type"]},
    {"name": "Objective", "native": None, "keywords": ["objective", "goal", "purpose", "descript", "summary"]},
    {"name": "Feature", "native": None, "keywords": ["feature", "component", "module", "area", "epic"]},
    {"name": "Coverage Tier", "native": None, "keywords": ["tier", "coverage"]},
    {"name": "Severity", "native": None, "keywords": ["severity", "impact"]},
    {"name": "Suggested Layer", "native": None, "keywords": ["layer", "level", "automat"]},
    {"name": "Test Data", "native": None, "keywords": ["data", "fixture"]},
    {"name": "Assumptions", "native": None, "keywords": ["assumption", "note", "comment"]},
    {"name": "Confidence", "native": None, "keywords": ["confidence"]},
]

TICKET_KEY_RE = re.compile(r"\b([A-Z][A-Z0-9]{1,9})-(\d+)\b")


class ConfigError(RuntimeError):
    """Bad or missing configuration."""


class AuthError(RuntimeError):
    """401/403 from TestRail."""


class TransportError(RuntimeError):
    """Network or server failure that survived retries."""


class _NoCrossHostRedirect(urllib.request.HTTPRedirectHandler):
    """Redirect handler that refuses to follow a redirect to another host.

    urllib's default handler copies request headers -- including Authorization --
    onto the redirected request, so an open redirect (or a misconfigured
    TESTRAIL_URL) would hand the Basic Auth blob to a third party. Blocking the
    redirect *before* it is followed is the only way to prevent that; checking
    after the fact is too late.
    """

    def __init__(self, allowed_host: str, require_https: bool) -> None:
        self.allowed_host = (allowed_host or "").lower()
        self.require_https = require_https

    def redirect_request(self, req, fp, code, msg, headers, newurl):  # noqa: D102
        target = urllib.parse.urlparse(newurl)
        reason = None
        if (target.hostname or "").lower() != self.allowed_host:
            reason = f"cross-host redirect to {target.scheme}://{target.netloc}"
        elif self.require_https and target.scheme != "https":
            # Same host, but downgraded -- following this would put the Basic Auth
            # header on the wire in cleartext.
            reason = f"https->{target.scheme} downgrade on {target.netloc}"
        if reason:
            raise urllib.error.HTTPError(
                newurl,
                code,
                f"refused {reason} (credentials are never forwarded)",
                headers,
                fp,
            )
        return super().redirect_request(req, fp, code, msg, headers, newurl)


# --------------------------------------------------------------------------- #
# client
# --------------------------------------------------------------------------- #


class TestRailClient:
    """Minimal read-only TestRail API v2 client. GET only, by construction."""

    def __init__(
        self,
        base_url: str,
        user: str,
        api_key: str,
        timeout: int = 30,
        max_retries: int = 5,
        verbose: bool = False,
    ) -> None:
        parsed = urllib.parse.urlparse(base_url)
        if parsed.scheme not in ("http", "https") or not parsed.netloc:
            # Deliberately does NOT echo the value: the commonest way to land here
            # is swapping TESTRAIL_URL and TESTRAIL_API_KEY, and echoing it would
            # print the key into CI logs.
            raise ConfigError(
                "TESTRAIL_URL must be an absolute http(s) URL such as "
                "https://example.testrail.io (value not shown -- it may be a "
                "mis-assigned secret). Check for swapped environment variables."
            )
        if parsed.username or parsed.password:
            raise ConfigError(
                "TESTRAIL_URL must not embed credentials. Put the login in "
                "TESTRAIL_USER and the key in TESTRAIL_API_KEY."
            )
        if parsed.scheme == "http":
            print(
                "WARNING: TESTRAIL_URL uses http://. The API key is sent as a Basic "
                "Auth header -- use https://.",
                file=sys.stderr,
            )
        self.base = base_url.rstrip("/")
        self._host = (parsed.hostname or "").lower()
        self._secret = api_key
        self._auth = base64.b64encode(f"{user}:{api_key}".encode()).decode()
        self.timeout = timeout
        self.max_retries = max_retries
        self.verbose = verbose
        self.request_count = 0
        self._opener = urllib.request.build_opener(
            _NoCrossHostRedirect(self._host, require_https=parsed.scheme == "https")
        )

    # -- redaction ---------------------------------------------------------- #

    def redact(self, text: str) -> str:
        """Strip the API key and Basic Auth blob from anything we print."""
        for secret in (self._secret, self._auth):
            if secret:
                text = text.replace(secret, "***REDACTED***")
        return text

    # -- core --------------------------------------------------------------- #

    def get(self, endpoint: str, **params: Any) -> Any:
        """Issue a single GET against /api/v2/<endpoint>."""
        url = self.base + API_PATH + endpoint
        # TestRail's router puts the method in the query string already, so extra
        # params are appended with '&', not '?'.
        for key, value in params.items():
            if value is None:
                continue
            url += (
                f"&{urllib.parse.quote(str(key), safe='')}"
                f"={urllib.parse.quote(str(value), safe='')}"
            )

        attempt = 0
        while True:
            attempt += 1
            request = urllib.request.Request(url, method="GET")
            assert request.get_method() == "GET", "read-only script issued a non-GET"
            request.add_header("Authorization", f"Basic {self._auth}")
            request.add_header("Content-Type", "application/json")
            request.add_header("User-Agent", "QA-GenDD-testrail-discovery/1.0 (read-only)")

            try:
                self.request_count += 1
                if self.verbose:
                    print(f"  GET {self.redact(url)}", file=sys.stderr)
                with self._opener.open(request, timeout=self.timeout) as response:
                    # Cross-host redirects are blocked before they are followed by
                    # _NoCrossHostRedirect. This is belt-and-braces in case a
                    # handler is ever swapped out: compare hostnames only, so a
                    # port or case difference is not treated as an attack.
                    landed = urllib.parse.urlparse(getattr(response, "url", "") or "")
                    landed_host = (landed.hostname or "").lower()
                    if landed_host and landed_host != self._host:
                        raise TransportError(
                            f"response came from {landed_host}, not {self._host} -- "
                            f"refusing to trust it. Check TESTRAIL_URL, and rotate "
                            f"the API key if this was not expected."
                        )
                    body = response.read().decode("utf-8", errors="replace")
                return json.loads(body) if body.strip() else None

            except urllib.error.HTTPError as exc:
                try:
                    raw = exc.read().decode("utf-8", errors="replace")
                    parsed_body = json.loads(raw)
                    detail = (
                        parsed_body.get("error", raw)
                        if isinstance(parsed_body, dict)
                        else raw
                    )
                except json.JSONDecodeError:
                    detail = raw
                except Exception:
                    detail = ""
                detail = self.redact(str(detail))[:400]

                if exc.code in (301, 302, 303, 307, 308):
                    raise TransportError(
                        f"blocked redirect on {endpoint}: "
                        f"{self.redact(str(exc.reason))}. Point TESTRAIL_URL at the "
                        f"instance's canonical https host."
                    ) from exc

                if exc.code in (401, 403):
                    raise AuthError(
                        f"HTTP {exc.code} on {endpoint}. Usual causes: the API key is "
                        f"wrong or revoked; TESTRAIL_USER is not the login email; or "
                        f"the API is disabled instance-wide (Administration -> Site "
                        f"Settings -> API -> Enable API). TestRail said: {detail}"
                    ) from exc

                if exc.code == 429 and attempt <= self.max_retries:
                    wait = self._retry_after(exc, attempt)
                    print(
                        f"  rate limited on {endpoint}; sleeping {wait:.1f}s "
                        f"(attempt {attempt}/{self.max_retries})",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                    continue

                if exc.code >= 500 and attempt <= self.max_retries:
                    wait = min(2 ** attempt, 30)
                    print(
                        f"  HTTP {exc.code} on {endpoint}; retrying in {wait}s "
                        f"(attempt {attempt}/{self.max_retries})",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                    continue

                raise TransportError(f"HTTP {exc.code} on {endpoint}: {detail}") from exc

            except urllib.error.URLError as exc:
                if attempt <= self.max_retries:
                    wait = min(2 ** attempt, 30)
                    print(
                        f"  network error on {endpoint} ({exc.reason}); retrying in "
                        f"{wait}s (attempt {attempt}/{self.max_retries})",
                        file=sys.stderr,
                    )
                    time.sleep(wait)
                    continue
                raise TransportError(
                    f"could not reach {self.base} after {self.max_retries + 1} attempts: "
                    f"{exc.reason}. If TestRail is only reachable on the corporate "
                    f"network, connect to the VPN first."
                ) from exc

            except json.JSONDecodeError as exc:
                raise TransportError(
                    f"{endpoint} returned a non-JSON body -- often an SSO/login "
                    f"interstitial, which means the request was not authenticated "
                    f"as an API call: {exc}"
                ) from exc

    @staticmethod
    def _retry_after(exc: urllib.error.HTTPError, attempt: int) -> float:
        """Honour Retry-After when TestRail sends it; fall back to backoff."""
        header = exc.headers.get("Retry-After") if exc.headers else None
        if header:
            try:
                # Clamp: an unbounded server-supplied value would either hang the
                # run for hours or overflow time.sleep(). min() also rejects inf/nan.
                wait = float(header)
                if wait == wait:  # not NaN
                    return min(max(1.0, wait), 60.0)
            except (TypeError, ValueError):
                pass
        return float(min(2 ** attempt, 60))

    def get_collection(
        self,
        endpoint: str,
        key: str,
        max_items: int | None = None,
        page_size: int = 250,
        **params: Any,
    ) -> list[dict[str, Any]]:
        """Read a list endpoint, handling both response shapes.

        TestRail 6.7+ wraps list responses as {"offset":.., "limit":.., "size":..,
        "<key>":[..]}. Older versions return a bare array. Handle both rather than
        assuming a version.
        """
        if max_items is not None and max_items <= 0:
            return []
        page_size = max(1, page_size)
        if max_items is not None:
            page_size = min(page_size, max_items)

        items: list[dict[str, Any]] = []
        offset = 0
        pages = 0
        max_pages = 500  # hard stop: a server that ignores `offset` must not spin
        while pages < max_pages:
            pages += 1
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
            print(
                f"  ! {endpoint}: stopped after {max_pages} pages -- the server may be "
                f"ignoring `offset`. Treat this collection as truncated.",
                file=sys.stderr,
            )

        if max_items is not None:
            return items[:max_items]
        return items


# --------------------------------------------------------------------------- #
# discovery
# --------------------------------------------------------------------------- #


def load_config() -> tuple[str, str, str]:
    url = os.environ.get("TESTRAIL_URL") or os.environ.get("TESTRAIL_INSTANCE_URL")
    user = os.environ.get("TESTRAIL_USER") or os.environ.get("TESTRAIL_USERNAME")
    key = os.environ.get("TESTRAIL_API_KEY")

    missing = [
        name
        for name, value in (
            ("TESTRAIL_URL (or TESTRAIL_INSTANCE_URL)", url),
            ("TESTRAIL_USER (or TESTRAIL_USERNAME)", user),
            ("TESTRAIL_API_KEY", key),
        )
        if not value
    ]
    if missing:
        raise ConfigError(
            "missing environment variable(s): "
            + ", ".join(missing)
            + ". See the module docstring. Do not pass secrets on the command line."
        )
    assert url and user and key
    return url, user, key


def safe(label: str, errors: list[str], fn, *args, **kwargs):
    """Run a discovery call; record and swallow per-endpoint failures.

    Both auth and transport failures are recorded and swallowed, because a 403 on
    a single project is a permission gap that should not abort discovery of the
    rest. A *systemically* bad key is caught instead by the unwrapped probe at the
    top of `discover()`, which is what guarantees exit code 2.
    """
    try:
        return fn(*args, **kwargs)
    except (AuthError, TransportError) as exc:
        errors.append(f"{label}: {exc}")
        print(f"  ! {label} failed: {exc}", file=sys.stderr)
        return None


def discover(
    client: TestRailClient,
    project_ids: list[int] | None,
    all_projects: bool,
    max_cases: int,
    errors: list[str],
) -> dict[str, Any]:
    # Unwrapped auth probe. Everything after this is wrapped in safe() so one
    # permission gap can't abort the run -- but that would also mask a bad key, so
    # prove authentication works here first and let AuthError propagate to exit 2.
    print("Checking authentication...", file=sys.stderr)
    client.get("get_projects", limit=1)

    print("Reading global metadata...", file=sys.stderr)
    data: dict[str, Any] = {
        "base_url": client.base,
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "priorities": safe("get_priorities", errors, client.get, "get_priorities") or [],
        "case_types": safe("get_case_types", errors, client.get, "get_case_types") or [],
        "case_fields": safe("get_case_fields", errors, client.get, "get_case_fields") or [],
        "statuses": safe("get_statuses", errors, client.get, "get_statuses") or [],
        "projects": [],
    }

    print("Listing projects...", file=sys.stderr)
    projects = (
        safe("get_projects", errors, client.get_collection, "get_projects", "projects")
        or []
    )
    data["all_projects"] = [
        {
            "id": p.get("id"),
            "name": p.get("name"),
            "suite_mode": p.get("suite_mode"),
            "is_completed": p.get("is_completed"),
        }
        for p in projects
    ]

    if project_ids:
        wanted = [p for p in projects if p.get("id") in project_ids]
        unknown = set(project_ids) - {p.get("id") for p in projects}
        for pid in sorted(unknown):
            errors.append(f"project {pid} not visible to this API key")
    elif all_projects:
        wanted = [p for p in projects if not p.get("is_completed")]
    else:
        wanted = []

    for project in wanted:
        pid = project.get("id")
        name = project.get("name")
        print(f"Reading project {pid} ({name})...", file=sys.stderr)

        entry: dict[str, Any] = {
            "id": pid,
            "name": name,
            "suite_mode": project.get("suite_mode"),
            "templates": safe(
                f"get_templates/{pid}", errors, client.get, f"get_templates/{pid}"
            )
            or [],
            "suites": [],
            "suites_sampled": [],
            "sections": [],
            "cases": [],
        }

        suites = (
            safe(
                f"get_suites/{pid}",
                errors,
                client.get_collection,
                f"get_suites/{pid}",
                "suites",
            )
            or []
        )
        # suite_mode 1/2 have an implicit single suite; get_suites still returns it.
        entry["suites"] = [{"id": s.get("id"), "name": s.get("name")} for s in suites]

        multi = project.get("suite_mode") == 3
        # In multi-suite mode both get_sections and get_cases require a suite_id, so
        # walk every suite rather than silently characterising the project from
        # suite #1 alone. The case budget is shared across suites.
        if multi and not suites:
            # suite_id is mandatory in multi-suite mode, so without the suite list
            # every downstream call would fail one by one. Say so once and move on.
            errors.append(
                f"project {pid} ({name}) is in multiple-suite mode but its suites "
                f"could not be listed -- sections and cases were not sampled"
            )
            entry["sections"] = []
            entry["cases"] = []
            data["projects"].append(entry)
            continue

        suite_ids: list[int | None] = (
            [s.get("id") for s in suites if s.get("id") is not None]
            if multi
            else [None]
        )
        sampled: list[int] = []
        sections: list[dict[str, Any]] = []
        cases: list[dict[str, Any]] = []

        for suite_id in suite_ids:
            # Check the budget before doing any work for this suite, so a suite
            # never contributes sections without also contributing cases.
            remaining = max_cases - len(cases)
            if remaining <= 0:
                entry["case_budget_exhausted"] = True
                break

            tag = f"/suite {suite_id}" if suite_id is not None else ""
            if suite_id is not None:
                sampled.append(suite_id)
            sections.extend(
                safe(
                    f"get_sections/{pid}{tag}",
                    errors,
                    client.get_collection,
                    f"get_sections/{pid}",
                    "sections",
                    suite_id=suite_id,
                )
                or []
            )
            cases.extend(
                safe(
                    f"get_cases/{pid}{tag}",
                    errors,
                    client.get_collection,
                    f"get_cases/{pid}",
                    "cases",
                    max_items=remaining,
                    suite_id=suite_id,
                )
                or []
            )

        entry["suites_sampled"] = sampled
        entry["sections"] = sections
        entry["cases"] = cases
        if len(cases) >= max_cases:
            # Also true when the *last* suite was the one truncated, which the
            # loop's break cannot detect.
            entry["case_budget_exhausted"] = True
        print(
            f"  {len(entry['suites'])} suite(s), {len(sections)} section(s), "
            f"{len(cases)} case(s) sampled",
            file=sys.stderr,
        )
        data["projects"].append(entry)

    return data


# --------------------------------------------------------------------------- #
# analysis
# --------------------------------------------------------------------------- #


def as_list(value: Any, key: str | None = None) -> list[dict[str, Any]]:
    """Coerce an API payload to a list of dicts.

    Most metadata endpoints return a bare array, but TestRail has progressively
    moved list endpoints to a paginated wrapper. Accept either rather than
    assuming a version, and drop anything that isn't a dict.

    When `key` is given it is preferred over scanning, because a wrapper like
    ``{"errors": [], "cases": [...]}`` would otherwise yield the wrong list
    depending on dict ordering.
    """
    if isinstance(value, list):
        return [v for v in value if isinstance(v, dict)]
    if isinstance(value, dict):
        if key is not None and isinstance(value.get(key), list):
            return [v for v in value[key] if isinstance(v, dict)]
        for candidate in value.values():
            if isinstance(candidate, list):
                return [v for v in candidate if isinstance(v, dict)]
    return []


def field_catalogue(case_fields: Any) -> list[dict[str, Any]]:
    """Flatten get_case_fields into something reportable."""
    out = []
    for field in as_list(case_fields, "case_fields"):
        # Shape-guard rather than trust: an unexpected scalar here would raise an
        # AttributeError at the very end of a long run and lose the whole report.
        raw_configs = field.get("configs")
        configs = [c for c in raw_configs if isinstance(c, dict)] if isinstance(
            raw_configs, list
        ) else []
        options: list[str] = []
        required_in: list[str] = []
        for config in configs:
            opts = config.get("options")
            opts = opts if isinstance(opts, dict) else {}
            if opts.get("is_required"):
                ctx = config.get("context")
                ctx = ctx if isinstance(ctx, dict) else {}
                scope = (
                    "all projects"
                    if ctx.get("is_global")
                    else f"projects {ctx.get('project_ids')}"
                )
                required_in.append(scope)
            items = opts.get("items")
            if items:
                # TestRail stores dropdown/multi-select items as "1, Label" lines.
                # Keep only the label, and dedupe across configs.
                for line in str(items).splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    _, _, label_part = line.partition(",")
                    options.append((label_part or line).strip())
                options = list(dict.fromkeys(options))
        type_id = field.get("type_id")
        try:
            type_id = int(type_id)  # some deployments return this as a string
        except (TypeError, ValueError):
            # Must stay hashable for the dict lookup below.
            if not isinstance(type_id, (int, str, type(None))):
                type_id = str(type_id)
        out.append(
            {
                "system_name": field.get("system_name") or "",
                "label": field.get("label") or "",
                "type_id": type_id,
                "type": CUSTOM_FIELD_TYPES.get(type_id, f"unknown({type_id})"),
                "options": options,
                "required_in": required_in,
                "is_global": any(
                    isinstance(c.get("context"), dict)
                    and c["context"].get("is_global")
                    for c in configs
                ),
            }
        )
    return sorted(out, key=lambda f: str(f["system_name"]))


def match_repo_fields(catalogue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """For each of our fields, find a plausible existing TestRail target."""
    rows = []
    for spec in REPO_FIELDS:
        candidates = []
        for field in catalogue:
            haystack = f"{field['system_name']} {field['label']}".lower()
            if any(kw in haystack for kw in spec["keywords"]):
                candidates.append(f"{field['system_name']} ({field['label']})")
        if spec["native"]:
            verdict = "native"
            target = spec["native"]
        elif candidates:
            verdict = "candidate custom field found"
            target = "; ".join(candidates[:3])
        else:
            verdict = "no target -- fold into text, or request a custom field"
            target = "--"
        rows.append(
            {
                "repo_field": spec["name"],
                "target": target,
                "verdict": verdict,
            }
        )
    return rows


def analyse_cases(
    cases: Any,
    priorities: Any,
    case_types: Any,
    templates: Any,
) -> dict[str, Any]:
    cases = as_list(cases, "cases")
    total = len(cases)
    result: dict[str, Any] = {"total": total}
    if not total:
        return result

    priority_names = {
        p.get("id"): p.get("name") for p in as_list(priorities, "priorities")
    }
    type_names = {
        t.get("id"): t.get("name") for t in as_list(case_types, "case_types")
    }
    template_names = {
        t.get("id"): t.get("name") for t in as_list(templates, "templates")
    }

    def label(mapping: dict[Any, Any], value: Any) -> str:
        try:
            name = mapping.get(value, "unknown")
        except TypeError:  # unhashable id from a malformed payload
            name = "unknown"
        return f"{name} (id {value})"

    result["priority_usage"] = Counter(
        label(priority_names, c.get("priority_id")) for c in cases
    ).most_common()
    result["type_usage"] = Counter(
        label(type_names, c.get("type_id")) for c in cases
    ).most_common()
    result["template_usage"] = Counter(
        label(template_names, c.get("template_id")) for c in cases
    ).most_common()

    # Fill rate across every key seen on any sampled case.
    keys: set[str] = set()
    for case in cases:
        keys.update(case.keys())
    def is_populated(value: Any) -> bool:
        # An unchecked checkbox is not "populated" for our purposes; counting it as
        # such reported 100% fill on every boolean field. Note `0` from an
        # integer-typed field is genuinely a value and IS counted -- so a checkbox
        # that a deployment returns as 0/1 rather than false/true will still be
        # over-counted. Read boolean fill rates with that caveat.
        if value is None or value is False:
            return False
        if isinstance(value, str) and not value.strip():
            return False
        if isinstance(value, (list, dict, tuple)) and len(value) == 0:
            return False
        return True

    fill: list[tuple[str, int, float]] = []
    for key in sorted(keys):
        filled = sum(1 for c in cases if is_populated(c.get(key)))
        fill.append((key, filled, 100.0 * filled / total))
    result["fill_rates"] = fill

    # refs conventions -- this is our traceability hook, so read it carefully.
    refs_present = [str(c.get("refs")) for c in cases if c.get("refs")]
    prefixes = Counter()
    for value in refs_present:
        for match in TICKET_KEY_RE.finditer(value):
            prefixes[match.group(1)] += 1
    result["refs"] = {
        "populated": len(refs_present),
        "populated_pct": 100.0 * len(refs_present) / total,
        "prefixes": prefixes.most_common(10),
        "multi_value": sum(1 for v in refs_present if ("," in v or " " in v.strip())),
        "samples": refs_present[:5],
    }

    # How are steps actually stored?
    separated = sum(1 for c in cases if c.get("custom_steps_separated"))
    plain = sum(1 for c in cases if c.get("custom_steps"))
    result["steps_style"] = {
        "custom_steps_separated": separated,
        "custom_steps": plain,
        "both": sum(
            1 for c in cases if c.get("custom_steps_separated") and c.get("custom_steps")
        ),
        # Counted independently rather than by subtraction: a case can populate both
        # fields, which would make a `total - a - b` figure go negative.
        "neither": sum(
            1
            for c in cases
            if not c.get("custom_steps_separated") and not c.get("custom_steps")
        ),
    }
    step_counts = [
        len(c["custom_steps_separated"])
        for c in cases
        if isinstance(c.get("custom_steps_separated"), list)
        and c.get("custom_steps_separated")
    ]
    if step_counts:
        result["steps_per_case"] = {
            "min": min(step_counts),
            "max": max(step_counts),
            "mean": round(sum(step_counts) / len(step_counts), 1),
        }

    result["preconds_populated"] = sum(1 for c in cases if c.get("custom_preconds"))
    result["automation_hint"] = Counter(
        str(c.get("custom_automation_type"))
        for c in cases
        if c.get("custom_automation_type") is not None
    ).most_common(10)
    return result


def analyse_sections(sections: Any) -> dict[str, Any]:
    sections = as_list(sections)
    if not sections:
        return {"total": 0}
    by_id = {s.get("id"): s for s in sections}

    def depth(section: dict[str, Any], guard: int = 0) -> int:
        parent = section.get("parent_id")
        if parent is None or parent not in by_id or guard > 20:
            return 1
        return 1 + depth(by_id[parent], guard + 1)

    depths = [depth(s) for s in sections]
    roots = [s for s in sections if s.get("parent_id") is None]
    return {
        "total": len(sections),
        "max_depth": max(depths),
        "roots": [(s.get("id"), s.get("name")) for s in roots[:15]],
        "root_count": len(roots),
    }


# --------------------------------------------------------------------------- #
# report
# --------------------------------------------------------------------------- #


def md_table(headers: list[str], rows: list[list[str]]) -> list[str]:
    def clean(cell: Any) -> str:
        return str(cell).replace("|", "\\|").replace("\n", " ")

    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for row in rows:
        out.append("| " + " | ".join(clean(c) for c in row) + " |")
    return out


def build_report(
    data: dict[str, Any],
    errors: list[str],
    requests: int,
    redact,
) -> str:
    L: list[str] = []
    L.append("# TestRail Discovery — Field Map")
    L.append("")
    # Redacted defensively: if a secret was mis-assigned into TESTRAIL_URL it must
    # not be committed along with this report.
    L.append(f"- **Instance:** `{redact(str(data['base_url']))}`")
    L.append(f"- **Generated:** {data['generated_at']}")
    L.append(f"- **API requests issued:** {requests} (all GET — this script never writes)")
    L.append("")
    L.append(
        "> Generated by `engine/ci/testrail_discovery.py`. This is the authoritative "
        "field map for pushing generated cases to TestRail. Regenerate it whenever "
        "TestRail's fields, priorities, or templates change — a stale map is how an "
        "import silently produces malformed cases."
    )
    L.append("")

    # 1. projects
    L.append("## 1. Visible projects")
    L.append("")
    all_projects = data.get("all_projects") or []
    if all_projects:
        L += md_table(
            ["ID", "Name", "Suite mode", "Completed"],
            [
                [
                    p["id"],
                    p["name"],
                    SUITE_MODES.get(
                        p.get("suite_mode"), f"unknown ({p.get('suite_mode')})"
                    ),
                    "yes" if p.get("is_completed") else "no",
                ]
                for p in all_projects
            ],
        )
    else:
        L.append("_No projects visible to this API key._")
    L.append("")

    # 2. vocabularies
    L.append("## 2. Configured vocabularies")
    L.append("")
    L.append("These are the **only** values a push may use. Resolve our internal "
             "schemes to these ids — do not invent names.")
    L.append("")
    L.append("### Priorities")
    L.append("")
    priorities = as_list(data.get("priorities"), "priorities")
    if priorities:
        L += md_table(
            ["priority_id", "Name", "Short", "Is default"],
            [
                [p.get("id"), p.get("name"), p.get("short_name", ""),
                 "yes" if p.get("is_default") else ""]
                for p in priorities
            ],
        )
    else:
        L.append("_Not retrieved._")
    L.append("")
    L.append("### Case types")
    L.append("")
    case_types = as_list(data.get("case_types"), "case_types")
    if case_types:
        L += md_table(
            ["type_id", "Name", "Is default"],
            [[t.get("id"), t.get("name"), "yes" if t.get("is_default") else ""]
             for t in case_types],
        )
    else:
        L.append("_Not retrieved._")
    L.append("")

    statuses = as_list(data.get("statuses"), "statuses")
    if statuses:
        L.append("### Result statuses (for later result push, not case creation)")
        L.append("")
        L += md_table(
            ["status_id", "Name", "Label"],
            [[s.get("id"), s.get("name"), s.get("label", "")] for s in statuses],
        )
        L.append("")

    # 3. case fields
    catalogue = field_catalogue(data.get("case_fields") or [])
    L.append("## 3. Case fields")
    L.append("")
    if catalogue:
        L += md_table(
            ["system_name", "Label", "Type", "Global", "Required in", "Options"],
            [
                [
                    f"`{f['system_name']}`",
                    f["label"],
                    f"{f['type']} ({f['type_id']})",
                    "yes" if f["is_global"] else "no",
                    "; ".join(f["required_in"]) or "—",
                    ", ".join(f["options"][:8]) + (" …" if len(f["options"]) > 8 else ""),
                ]
                for f in catalogue
            ],
        )
        L.append("")
        L.append(
            "**Required fields are mandatory on every `add_case` call.** Any field "
            "marked required above must be populated by the push skill or the write "
            "fails."
        )
    else:
        L.append("_Not retrieved._")
    L.append("")

    # 4. proposed map
    L.append("## 4. Proposed field map")
    L.append("")
    L.append(
        "Our case structure (`.cursor/skills/qa-test-case-writer/SKILL.md`) against "
        "what this instance offers. Candidate matches are keyword guesses — **a human "
        "must confirm each one** before it goes into the connector doc."
    )
    L.append("")
    L += md_table(
        ["Our field", "TestRail target", "Status"],
        [[r["repo_field"], f"`{r['target']}`" if r["target"] != "--" else "—",
          r["verdict"]] for r in match_repo_fields(catalogue)],
    )
    L.append("")
    L.append(
        "For anything marked *no target*: prefer folding it into a structured block "
        "inside an existing text field over requesting new custom fields. Fewer admin "
        "requests means the integration actually ships."
    )
    L.append("")

    # 5. per-project observed conventions
    projects = data.get("projects") or []
    if not projects:
        L.append("## 5. Observed conventions")
        L.append("")
        L.append(
            "_No project sampled. Re-run with `--project <id>` (see section 1) or "
            "`--all-projects` to derive conventions from real cases — this is the "
            "part that tells you what the existing suite actually does._"
        )
        L.append("")
    for index, project in enumerate(projects, start=1):
        suffix = f".{index}" if len(projects) > 1 else ""
        L.append(
            f"## 5{suffix}. Observed conventions — {project['name']} "
            f"(id {project['id']})"
        )
        L.append("")
        L.append(
            f"- Suite mode: **{SUITE_MODES.get(project.get('suite_mode'), project.get('suite_mode'))}**"
        )
        L.append(f"- Suites: {len(project.get('suites') or [])}")
        for suite in (project.get("suites") or [])[:10]:
            L.append(f"  - `{suite['id']}` {suite['name']}")

        if project.get("case_budget_exhausted"):
            if len(project.get("suites") or []) > 1:
                L.append(
                    "- ⚠️ The case sample budget was exhausted before every suite was "
                    "read; later suites are unrepresented. Raise `--max-cases`."
                )
            else:
                L.append(
                    "- ⚠️ The case sample hit the `--max-cases` ceiling, so this is a "
                    "truncated view of the suite. Raise `--max-cases` for a fuller "
                    "picture."
                )

        sec = analyse_sections(project.get("sections") or [])
        L.append(
            f"- Sections: **{sec.get('total', 0)}**, max nesting depth "
            f"**{sec.get('max_depth', 0)}**, {sec.get('root_count', 0)} top-level"
        )
        for sid, sname in sec.get("roots", []):
            L.append(f"  - `{sid}` {sname}")
        L.append("")

        stats = analyse_cases(
            project.get("cases") or [],
            data.get("priorities") or [],
            data.get("case_types") or [],
            project.get("templates") or [],
        )
        total = stats.get("total", 0)
        L.append(f"### Sample: {total} case(s)")
        L.append("")
        if not total:
            L.append("_No cases sampled._")
            L.append("")
            continue

        L.append("**Template usage**")
        L.append("")
        L += md_table(["Template", "Cases"],
                      [[k, v] for k, v in stats.get("template_usage", [])])
        L.append("")
        L.append("**Priority usage** — this is the real vocabulary our tiers must map onto")
        L.append("")
        L += md_table(["Priority", "Cases"],
                      [[k, v] for k, v in stats.get("priority_usage", [])])
        L.append("")
        L.append("**Type usage**")
        L.append("")
        L += md_table(["Type", "Cases"],
                      [[k, v] for k, v in stats.get("type_usage", [])])
        L.append("")

        refs = stats.get("refs", {})
        L.append("**Traceability (`refs`)**")
        L.append("")
        L.append(
            f"- Populated on **{refs.get('populated', 0)}/{total}** cases "
            f"({refs.get('populated_pct', 0):.0f}%)"
        )
        if refs.get("prefixes"):
            L.append(
                "- Ticket-key prefixes seen: "
                + ", ".join(f"`{k}` ×{v}" for k, v in refs["prefixes"])
            )
        L.append(f"- Cases with multiple refs: {refs.get('multi_value', 0)}")
        for sample in refs.get("samples", []):
            L.append(f"  - e.g. `{sample}`")
        L.append("")
        if refs.get("populated_pct", 0) < 50:
            L.append(
                "> ⚠️ `refs` is populated on under half the sample. If the existing "
                "suite does not link cases to tickets, our generated cases should "
                "still do so — but confirm the convention with the team first rather "
                "than inventing one."
            )
            L.append("")

        steps = stats.get("steps_style", {})
        L.append("**Steps representation**")
        L.append("")
        L += md_table(
            ["Storage", "Cases"],
            [
                ["`custom_steps_separated` (structured)", steps.get("custom_steps_separated", 0)],
                ["`custom_steps` (single text blob)", steps.get("custom_steps", 0)],
                ["both populated", steps.get("both", 0)],
                ["neither", steps.get("neither", 0)],
            ],
        )
        if stats.get("steps_per_case"):
            spc = stats["steps_per_case"]
            L.append("")
            L.append(
                f"Steps per case — min {spc['min']}, mean {spc['mean']}, max {spc['max']}."
            )
        L.append("")
        L.append(
            f"`custom_preconds` populated on "
            f"{stats.get('preconds_populated', 0)}/{total} cases."
        )
        L.append("")
        if steps.get("custom_steps", 0) and steps.get("custom_steps_separated", 0):
            L.append(
                "> ⚠️ Both step styles are in use in the same project. Pick one for "
                "generated cases and state it in the connector doc, or the suite "
                "becomes unreadable."
            )
            L.append("")

        if stats.get("automation_hint"):
            L.append("**`custom_automation_type` values seen**")
            L.append("")
            L += md_table(["Value", "Cases"],
                          [[k, v] for k, v in stats["automation_hint"]])
            L.append("")

        L.append("<details><summary>Field fill rates across the sample</summary>")
        L.append("")
        L += md_table(
            ["Field", "Populated", "%"],
            [[f"`{k}`", n, f"{pct:.0f}%"] for k, n, pct in stats.get("fill_rates", [])],
        )
        L.append("")
        L.append("</details>")
        L.append("")

    # 6. gaps
    L.append("## 6. Follow-ups")
    L.append("")
    L.append("- [ ] Confirm every *candidate custom field* in section 4 with the team.")
    L.append("- [ ] Decide the canonical priority/tier scheme, resolving to the "
            "`priority_id` values in section 2.")
    L.append("- [ ] Choose the target `section_id`(s) a push is allowed to write to, "
            "and allowlist them.")
    L.append("- [ ] Confirm the `refs` convention (parent story key vs sub-task key).")
    L.append("- [ ] Record all of the above in "
            "`.cursor/skills/qa-test-case-writer/Context.md` §1 so the generation "
            "flow can offer a push at all.")
    L.append("")

    if errors:
        L.append("## 7. Errors encountered")
        L.append("")
        L.append(
            "Discovery continued past these; treat every affected section as "
            "incomplete."
        )
        L.append("")
        for err in errors:
            L.append(f"- {err}")
        L.append("")

    return "\n".join(L) + "\n"


# --------------------------------------------------------------------------- #
# entry point
# --------------------------------------------------------------------------- #


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Read-only TestRail discovery. Emits a field-map report.",
        epilog="Credentials come from environment variables only. See module docstring.",
    )
    parser.add_argument(
        "--project", type=int, action="append", dest="projects", metavar="ID",
        help="project id to sample; repeatable",
    )
    parser.add_argument(
        "--all-projects", action="store_true",
        help="sample every non-completed visible project (slower)",
    )
    parser.add_argument(
        "--probe", action="store_true",
        help="only check auth and list projects, then exit",
    )
    parser.add_argument(
        "--max-cases", type=int, default=200, metavar="N",
        help="max cases to sample per project (default 200)",
    )
    parser.add_argument(
        "--out", type=Path, default=Path("testrail-field-map.md"),
        help="report path (default ./testrail-field-map.md)",
    )
    parser.add_argument(
        "--raw", type=Path, metavar="PATH",
        help="also dump the raw discovery JSON here (contains case titles — treat "
             "as internal)",
    )
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args(argv)

    if args.max_cases <= 0:
        parser.error("--max-cases must be a positive integer")
    if args.timeout <= 0:
        parser.error("--timeout must be a positive number of seconds")
    if args.out.is_dir():
        parser.error(f"--out points at a directory: {args.out}")
    if args.raw and args.raw.is_dir():
        parser.error(f"--raw points at a directory: {args.raw}")

    try:
        url, user, key = load_config()
    except ConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    try:
        client = TestRailClient(url, user, key, timeout=args.timeout, verbose=args.verbose)
    except ConfigError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    errors: list[str] = []

    if args.probe:
        print(f"Probing {client.redact(client.base)} ...", file=sys.stderr)
        try:
            projects = client.get_collection("get_projects", "projects")
        except AuthError as exc:
            print(f"AUTH FAILED: {exc}", file=sys.stderr)
            return 2
        except TransportError as exc:
            print(f"TRANSPORT FAILED: {exc}", file=sys.stderr)
            return 3
        if not projects:
            print(
                "API reachable and authenticated, but no projects are visible to "
                "this key. Check project-level permissions.",
                file=sys.stderr,
            )
            return 4
        print(f"OK - API reachable. {len(projects)} project(s) visible:")
        for project in projects:
            mode = SUITE_MODES.get(project.get("suite_mode"), f"unknown ({project.get('suite_mode')})")
            done = " [completed]" if project.get("is_completed") else ""
            print(f"  {str(project.get('id')):>5}  {project.get('name')}  ({mode}){done}")
        print("\nNext: re-run with --project <id> to derive the field map.")
        return 0

    if not args.projects and not args.all_projects:
        print(
            "No project selected -- producing a metadata-only report (sections 1-4: "
            "vocabularies, case fields, proposed map). To also derive conventions "
            "from real cases, re-run with --project <id> or --all-projects.",
            file=sys.stderr,
        )

    try:
        data = discover(client, args.projects, args.all_projects, args.max_cases, errors)
    except AuthError as exc:
        print(f"AUTH FAILED: {exc}", file=sys.stderr)
        return 2
    except TransportError as exc:
        print(f"TRANSPORT FAILED: {exc}", file=sys.stderr)
        return 3

    if not data.get("all_projects"):
        print("No visible projects - check project permissions.", file=sys.stderr)
        return 4

    report = build_report(data, errors, client.request_count, redact=client.redact)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(report, encoding="utf-8")
    print(f"\nWrote {args.out} ({len(report):,} bytes, {client.request_count} GETs).")

    if args.raw:
        args.raw.parent.mkdir(parents=True, exist_ok=True)
        args.raw.write_text(
            client.redact(json.dumps(data, indent=2, default=str)), encoding="utf-8"
        )
        print(f"Wrote raw JSON to {args.raw} - contains case content, keep internal.")

    if errors:
        print(f"\n{len(errors)} discovery error(s) - see section 7 of the report.",
              file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nInterrupted.", file=sys.stderr)
        sys.exit(130)

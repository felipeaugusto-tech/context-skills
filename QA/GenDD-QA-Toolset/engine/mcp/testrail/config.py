#!/usr/bin/env python3
"""Configuration and credential loading for the TestRail bridge.

Why this module exists
----------------------
The bridge deliberately has **no third-party dependencies** — that is the whole
security argument for building it instead of installing a community MCP server.
So there is no ``python-dotenv``; the ``.env`` parser lives here, in ~60 lines
you can read in one sitting.

Everything that could possibly be a secret is registered with the redaction
registry the moment it is loaded. Nothing else in the codebase is trusted to
remember to redact — `Redactor.scrub()` is applied at the single choke point
where text leaves the process (see ``server.py``).

Configuration surface
---------------------
Connection (required):
    TESTRAIL_URL                  https://accurate.testrail.io
                                  (TESTRAIL_INSTANCE_URL also accepted)

Authentication — exactly one of these two modes:
    (A) API key, the officially supported path:
        TESTRAIL_USER             your TestRail login, normally your email
        TESTRAIL_API_KEY          generated under My Settings -> API Keys

    (B) Session cookie, for instances where SSO is the only way in and no API
        key can be minted:
        TESTRAIL_SESSION_COOKIE   raw Cookie header value copied from a browser
                                  session, e.g. "tr_session=abc123; other=..."

    Mode A is strongly preferred. Session cookies are short-lived, are bound to
    a browser session that logging out will invalidate, and are not a documented
    interface — see the README's "Session cookie mode" section for the caveats.

Authorisation (all optional, all fail-closed):
    TESTRAIL_MODE                 "read" (default) or "write". In read mode the
                                  write tools are not registered at all, so the
                                  agent cannot call what it cannot see.
    TESTRAIL_ALLOWED_PROJECTS     comma-separated project ids that writes may
                                  touch, e.g. "12,34". Empty means *no* project
                                  is writable, even in write mode.
    TESTRAIL_ALLOW_DELETE         "true" to register the delete tool at all.
                                  Default false.
    TESTRAIL_DRY_RUN              "true" to validate and echo writes without
                                  sending them. Default false.

Tuning (optional):
    TESTRAIL_TIMEOUT              per-request seconds, default 30
    TESTRAIL_MAX_RETRIES          default 4
    TESTRAIL_PAGE_SIZE            default 250, TestRail's maximum
    TESTRAIL_MAX_RESPONSE_CHARS   truncate tool output past this, default 60000.
                                  Guards the agent's context window, not TestRail.
"""

from __future__ import annotations

import os
import re
import urllib.parse
from dataclasses import dataclass, field
from pathlib import Path

# ---- knobs that are not worth an env var ---------------------------------- #

# Below this length a "secret" is more likely to be a substring of ordinary
# prose than a real credential, and scrubbing it would mangle every message.
MIN_REDACTABLE_LEN = 6

DEFAULT_ENV_FILENAME = ".env"


class ConfigError(RuntimeError):
    """Bad or missing configuration. Fatal, and never echoes the offending value."""


# --------------------------------------------------------------------------- #
# .env parsing
# --------------------------------------------------------------------------- #


def parse_env_file(text: str) -> dict[str, str]:
    """Parse a minimal ``.env``: ``KEY=value``, ``#`` comments, optional quotes.

    Intentionally does **not** support variable interpolation (``${FOO}``) or
    multi-line values. Both are places where a config file can surprise you, and
    a credentials file is the last place you want surprises. A literal ``$`` is
    just a ``$``.

    Unparseable lines are skipped rather than raising, so one stray line in a
    hand-edited file does not take the whole server down.
    """
    out: dict[str, str] = {}
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export "):].strip()
        key, sep, value = line.partition("=")
        if not sep:
            continue
        key = key.strip()
        if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", key):
            continue
        value = value.strip()
        # Strip matched quotes. Unquoted values get a trailing `# comment`
        # removed; quoted values keep everything inside the quotes, because a
        # '#' is perfectly legal inside a password.
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        else:
            value = value.split(" #", 1)[0].rstrip()
        out[key] = value
    return out


def load_env_file(path: Path) -> dict[str, str]:
    """Read a ``.env`` if present. A missing file is not an error.

    Real environment variables always win over the file: that is what lets CI
    inject a key from a secret store without deleting a developer's local file.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise ConfigError(f"could not read {path.name}: {exc.strerror}") from exc
    return parse_env_file(text)


# --------------------------------------------------------------------------- #
# redaction
# --------------------------------------------------------------------------- #


class Redactor:
    """Registry of strings that must never appear in output.

    Registered once at config load, then applied at the single point where text
    leaves the process. Longest-first so that a secret which happens to contain
    a shorter secret is masked whole rather than leaving fragments behind.
    """

    def __init__(self) -> None:
        self._secrets: list[str] = []

    def register(self, *values: str | None) -> None:
        for value in values:
            if value and len(value) >= MIN_REDACTABLE_LEN:
                if value not in self._secrets:
                    self._secrets.append(value)
        self._secrets.sort(key=len, reverse=True)

    def scrub(self, text: str) -> str:
        for secret in self._secrets:
            if secret in text:
                text = text.replace(secret, "***REDACTED***")
        return text

    def scrub_obj(self, value):
        """Scrub every string inside a nested structure, before serialisation.

        Scrubbing only the encoded JSON is not enough. ``json.dumps`` with
        ``ensure_ascii=True`` rewrites any non-ASCII character as ``\\uXXXX``,
        and escapes quotes, backslashes and control characters — so a secret
        containing any of those would no longer match a plain substring search
        and would survive into the output in escaped-but-readable form. A
        session cookie copied out of a browser is a realistic source of exactly
        those characters.

        Scrubbing the object first catches the raw form; ``scrub`` is still
        applied to the encoded text afterwards, which catches anything assembled
        during serialisation. Both passes are cheap relative to the request.
        """
        if isinstance(value, str):
            return self.scrub(value)
        if isinstance(value, dict):
            return {self.scrub_obj(k): self.scrub_obj(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self.scrub_obj(v) for v in value]
        return value

    def __len__(self) -> int:  # handy in tests
        return len(self._secrets)


# --------------------------------------------------------------------------- #
# config
# --------------------------------------------------------------------------- #


def _as_bool(value: str | None, default: bool = False) -> bool:
    """Strict-ish truthiness. Anything unrecognised is False, never a crash.

    Note the asymmetry: only an explicit affirmative turns a control *on*. A
    typo'd ``TESTRAIL_ALLOW_DELETE=ture`` therefore leaves delete disabled,
    which is the safe direction to fail.
    """
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on")


def _as_int(value: str | None, default: int, name: str, minimum: int = 1) -> int:
    if value is None or not value.strip():
        return default
    try:
        parsed = int(value.strip())
    except ValueError as exc:
        raise ConfigError(f"{name} must be an integer, got {value!r}") from exc
    if parsed < minimum:
        raise ConfigError(f"{name} must be >= {minimum}, got {parsed}")
    return parsed


def _parse_project_ids(value: str | None) -> frozenset[int]:
    """Parse the write allowlist. A malformed entry is fatal, not ignored.

    Silently dropping an unparseable id would be the wrong direction to fail in
    one specific way: writing ``TESTRAIL_ALLOWED_PROJECTS="12, 34x"`` and having
    it quietly mean "only 12" is confusing, but having ``"12x,34"`` quietly mean
    "only 34" while the operator believes 12 is allowed is worse. Refuse both.
    """
    if not value or not value.strip():
        return frozenset()
    ids: set[int] = set()
    for chunk in value.replace(";", ",").split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        try:
            parsed = int(chunk)
        except ValueError as exc:
            raise ConfigError(
                f"TESTRAIL_ALLOWED_PROJECTS must be a comma-separated list of "
                f"numeric project ids; {chunk!r} is not a number"
            ) from exc
        if parsed <= 0:
            raise ConfigError(
                f"TESTRAIL_ALLOWED_PROJECTS contains a non-positive id: {parsed}"
            )
        ids.add(parsed)
    return frozenset(ids)


@dataclass(frozen=True)
class Config:
    """Fully validated bridge configuration."""

    base_url: str
    host: str
    scheme: str

    # exactly one auth mode is populated
    user: str | None
    api_key: str | None
    session_cookie: str | None

    write_enabled: bool
    allowed_projects: frozenset[int]
    allow_delete: bool
    dry_run: bool

    timeout: int
    max_retries: int
    page_size: int
    max_response_chars: int

    redactor: Redactor = field(compare=False, repr=False, default_factory=Redactor)

    # -- derived ------------------------------------------------------------ #

    @property
    def auth_mode(self) -> str:
        return "api_key" if self.api_key else "session_cookie"

    @property
    def writes_possible(self) -> bool:
        """Write mode with an empty allowlist is a no-op, and says so up front."""
        return self.write_enabled and bool(self.allowed_projects)

    def describe(self) -> str:
        """Human-readable posture summary. Contains no secrets by construction."""
        if not self.write_enabled:
            posture = "read-only (write tools not registered)"
        elif not self.allowed_projects:
            posture = "write mode but the allowlist is EMPTY — every write will be refused"
        else:
            allowed = ", ".join(str(i) for i in sorted(self.allowed_projects))
            posture = f"read + write, restricted to project(s) {allowed}"
        # Reported regardless of the branch above: a dry run that is not
        # announced is how a validated-but-unsent push gets mistaken for a real
        # one.
        if self.dry_run:
            posture += " [DRY RUN — nothing is sent]"
        return (
            f"instance={self.base_url} auth={self.auth_mode} "
            f"delete={'enabled' if self.allow_delete else 'disabled'} | {posture}"
        )


def load_config(
    env: dict[str, str] | None = None,
    env_file: Path | None = None,
) -> Config:
    """Build a validated Config from the process environment and ``.env``.

    ``env`` is injectable so the test suite never touches ``os.environ``.
    """
    if env is None:
        env = dict(os.environ)
    if env_file is None:
        env_file = Path(__file__).resolve().parent / DEFAULT_ENV_FILENAME

    # Real env wins over file, so a CI secret store can override a developer's
    # local file. Blank values need opposite treatment depending on the key, and
    # the split is deliberately explicit:
    #
    #   * For connection and credential keys, a blank exported value
    #     (`TESTRAIL_API_KEY=` in a CI shell) is dropped so it cannot mask a good
    #     .env and surface as the misleading "no credentials found".
    #
    #   * For the keys below, a blank value must WIN, because for each of them
    #     "absent" resolves to the *restrictive* setting: mode -> read,
    #     allowlist -> empty, delete -> off. Dropping the blank would let a
    #     permissive .env (`TESTRAIL_MODE=write`,
    #     `TESTRAIL_ALLOWED_PROJECTS=12,34`) survive an operator exporting empty
    #     values to clamp it down — a fail-open inversion of the one precedence
    #     that actually protects the instance.
    #
    # TESTRAIL_DRY_RUN is deliberately NOT in this set. It is the one control
    # whose absent value is the *permissive* one (blank -> dry run off -> writes
    # really sent), so a blank must be dropped rather than allowed to switch off
    # a .env that had it on.
    BLANK_MEANS_RESTRICTIVE = frozenset({
        "TESTRAIL_MODE",
        "TESTRAIL_ALLOWED_PROJECTS",
        "TESTRAIL_ALLOW_DELETE",
    })
    file_values = load_env_file(env_file)
    merged = dict(file_values)
    for key, value in env.items():
        if key in BLANK_MEANS_RESTRICTIVE or (value and value.strip()):
            merged[key] = value

    def get(*names: str) -> str | None:
        for name in names:
            value = merged.get(name)
            if value is not None and value.strip():
                return value.strip()
        return None

    redactor = Redactor()

    raw_url = get("TESTRAIL_URL", "TESTRAIL_INSTANCE_URL")
    api_key = get("TESTRAIL_API_KEY")
    user = get("TESTRAIL_USER", "TESTRAIL_USERNAME")
    cookie = get("TESTRAIL_SESSION_COOKIE")

    # Register before any validation can raise: an error message built from a
    # mis-assigned variable must already be scrubbable.
    redactor.register(api_key, cookie)

    if not raw_url:
        raise ConfigError(
            "TESTRAIL_URL is not set. Copy .env.example to .env in "
            "engine/mcp/testrail/ and fill it in."
        )

    parsed = urllib.parse.urlparse(raw_url)
    if parsed.scheme not in ("http", "https") or not parsed.netloc:
        # Deliberately does not echo the value. The commonest way to reach this
        # line is swapping TESTRAIL_URL and TESTRAIL_API_KEY, and echoing would
        # print the key into a log.
        raise ConfigError(
            "TESTRAIL_URL must be an absolute http(s) URL such as "
            "https://example.testrail.io (value withheld — it may be a "
            "mis-assigned secret). Check for swapped variables."
        )
    if parsed.username or parsed.password:
        raise ConfigError(
            "TESTRAIL_URL must not embed credentials. Put the login in "
            "TESTRAIL_USER and the key in TESTRAIL_API_KEY."
        )

    # A query string means someone pasted an API URL. TestRail's own API paths
    # look like `/index.php?/api/v2/...`, so the giveaway lands in the *query*,
    # not the path — checking the path alone lets the commonest wrong value
    # through, and the resulting requests 404 in a way that looks like a
    # permissions problem.
    if parsed.query or parsed.fragment:
        raise ConfigError(
            "TESTRAIL_URL should be the instance root, not an API URL. Use "
            f"{parsed.scheme}://{parsed.netloc} and let the bridge append the "
            "API path itself."
        )

    # Self-hosted TestRail is often installed under a subpath
    # (https://tools.internal/testrail), so the path cannot simply be discarded
    # — dropping it would send every request to the web root. Normalise a
    # trailing /index.php and trailing slashes, and keep whatever is left.
    path = parsed.path.rstrip("/")
    if path.endswith("/index.php"):
        path = path[: -len("/index.php")]
    base_url = f"{parsed.scheme}://{parsed.netloc}{path}"

    # -- auth mode selection ------------------------------------------------ #

    if api_key and cookie:
        raise ConfigError(
            "both TESTRAIL_API_KEY and TESTRAIL_SESSION_COOKIE are set. Pick one "
            "auth mode — leaving a stale cookie behind makes it unclear which "
            "identity a write was made as."
        )
    if api_key:
        if not user:
            raise ConfigError(
                "TESTRAIL_API_KEY is set but TESTRAIL_USER is not. TestRail's "
                "Basic auth needs the login email as the username."
            )
        # Deliberately no check that `user` looks like an email: TestRail Server
        # instances can be configured with non-email logins, and rejecting those
        # would break a valid setup for the sake of a cosmetic assumption.
    elif cookie:
        if "=" not in cookie:
            raise ConfigError(
                "TESTRAIL_SESSION_COOKIE does not look like a Cookie header. "
                'Expected something like "tr_session=<value>".'
            )
    else:
        raise ConfigError(
            "no credentials found. Set TESTRAIL_USER + TESTRAIL_API_KEY "
            "(preferred), or TESTRAIL_SESSION_COOKIE for an SSO-only instance."
        )

    mode = (get("TESTRAIL_MODE") or "read").lower()
    if mode not in ("read", "write"):
        raise ConfigError(
            f'TESTRAIL_MODE must be "read" or "write", got {mode!r}. '
            f'Defaulting is not attempted — an ambiguous mode near a write path '
            f'should stop the server, not guess.'
        )

    config = Config(
        base_url=base_url,
        host=(parsed.hostname or "").lower(),
        scheme=parsed.scheme,
        user=user,
        api_key=api_key,
        session_cookie=cookie,
        write_enabled=mode == "write",
        allowed_projects=_parse_project_ids(get("TESTRAIL_ALLOWED_PROJECTS")),
        allow_delete=_as_bool(get("TESTRAIL_ALLOW_DELETE")),
        dry_run=_as_bool(get("TESTRAIL_DRY_RUN")),
        timeout=_as_int(get("TESTRAIL_TIMEOUT"), 30, "TESTRAIL_TIMEOUT"),
        max_retries=_as_int(get("TESTRAIL_MAX_RETRIES"), 4, "TESTRAIL_MAX_RETRIES", 0),
        page_size=min(_as_int(get("TESTRAIL_PAGE_SIZE"), 250, "TESTRAIL_PAGE_SIZE"), 250),
        max_response_chars=_as_int(
            get("TESTRAIL_MAX_RESPONSE_CHARS"), 60000, "TESTRAIL_MAX_RESPONSE_CHARS", 1000
        ),
        redactor=redactor,
    )

    # Delete without an allowlist would be enabled-but-inert; that reads as a
    # misconfiguration worth stopping for rather than discovering at call time.
    if config.allow_delete and not config.write_enabled:
        raise ConfigError(
            "TESTRAIL_ALLOW_DELETE is true but TESTRAIL_MODE is read. Set "
            'TESTRAIL_MODE=write if deletes are genuinely intended, or remove '
            "TESTRAIL_ALLOW_DELETE."
        )

    return config

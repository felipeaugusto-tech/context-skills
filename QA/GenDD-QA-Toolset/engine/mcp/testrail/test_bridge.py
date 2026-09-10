#!/usr/bin/env python3
"""Offline test suite for the TestRail bridge. No credentials, no network.

    python3 engine/mcp/testrail/test_bridge.py

Everything is exercised through a fake transport, so the tests cover the parts
that are hard to check against a live instance and easy to get wrong: the
guardrail refusals, redaction, pagination, and the protocol handshake. A live
smoke test (``server.py --probe``) is still required before trusting the bridge
against a real instance — see the README.

The suite deliberately asserts on *refusals*. A guardrail that has never been
observed to say no is not a guardrail.
"""

from __future__ import annotations

import io
import json
import sys
import traceback
import urllib.error
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import client as client_mod  # noqa: E402
from client import (  # noqa: E402
    AmbiguousWriteError,
    AuthError,
    TestRailClient,
    TransportError,
    as_list,
)
from config import Config, ConfigError, Redactor, load_config, parse_env_file  # noqa: E402
from guards import DELETE_CONFIRM_PHRASE, Guard, WriteRefused  # noqa: E402
from server import Server  # noqa: E402
from tools import ToolError, build_registry, convert_steps, render  # noqa: E402

# --------------------------------------------------------------------------- #
# harness
# --------------------------------------------------------------------------- #

PASSED: list[str] = []
FAILED: list[tuple[str, str]] = []


def test(name: str):
    def decorator(fn):
        try:
            fn()
        except AssertionError as exc:
            FAILED.append((name, f"assertion: {exc}"))
        except Exception:  # noqa: BLE001
            FAILED.append((name, traceback.format_exc(limit=3)))
        else:
            PASSED.append(name)
        return fn
    return decorator


def expect_raises(exc_type, fn, *, contains: str | None = None):
    try:
        fn()
    except exc_type as exc:
        if contains is not None:
            assert contains.lower() in str(exc).lower(), (
                f"expected message containing {contains!r}, got {exc!r}"
            )
        return exc
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(
            f"expected {exc_type.__name__}, got {type(exc).__name__}: {exc}"
        ) from exc
    raise AssertionError(f"expected {exc_type.__name__}, nothing was raised")


# --------------------------------------------------------------------------- #
# fakes
# --------------------------------------------------------------------------- #


class FakeTransport:
    """Records requests and replays scripted responses.

    Routing is by substring of the URL so tests can register ``"get_case/5"``
    without reconstructing the whole query string.
    """

    def __init__(self, routes: dict[str, object] | None = None) -> None:
        self.routes = routes or {}
        self.calls: list[tuple[str, str, dict | None]] = []

    def __call__(self, request: urllib.request.Request, timeout: int):
        url = request.full_url
        body = json.loads(request.data.decode()) if request.data else None
        self.calls.append((request.get_method(), url, body))

        for pattern, response in self.routes.items():
            if pattern in url:
                if isinstance(response, Exception):
                    raise response
                if callable(response):
                    response = response(url, body)
                return 200, json.dumps(response), {}
        return 200, json.dumps({}), {}

    @property
    def methods(self) -> list[str]:
        return [m for m, _, _ in self.calls]

    def urls_for(self, needle: str) -> list[str]:
        return [u for _, u, _ in self.calls if needle in u]


def make_config(**overrides) -> Config:
    env = {
        "TESTRAIL_URL": "https://accurate.testrail.io",
        "TESTRAIL_USER": "qa@accurate.com",
        "TESTRAIL_API_KEY": "SUPER-SECRET-KEY-1234",
    }
    env.update({k: str(v) for k, v in overrides.items()})
    # env_file points at a path that does not exist, so a developer's real .env
    # can never leak into a test run.
    return load_config(env=env, env_file=Path("/nonexistent/.env"))


def make_stack(routes=None, **overrides):
    config = make_config(**overrides)
    transport = FakeTransport(routes)
    tr_client = TestRailClient(config, transport=transport, sleep=lambda _s: None)
    return config, tr_client, Guard(tr_client), transport


# The shared fixture for write-path tests. Defined up here rather than beside the
# guard tests because @test bodies execute at decoration time, so any test that
# references this must appear textually after it.
#
# Section 500 -> suite 90 -> project 12 (allowlisted in most tests).
# Section 999 -> suite 91 -> project 77 (never allowlisted: the refusal case).
WRITE_ROUTES = {
    "get_section/500": {"id": 500, "suite_id": 90, "name": "Checkout"},
    "get_suite/90": {"id": 90, "project_id": 12, "name": "Regression"},
    "get_section/999": {"id": 999, "suite_id": 91, "name": "Other"},
    "get_suite/91": {"id": 91, "project_id": 77, "name": "Live"},
    "get_case/5": {"id": 5, "suite_id": 90, "section_id": 500, "title": "Existing"},
    "get_project/12": {"id": 12, "suite_mode": 3},
    "get_project/77": {"id": 77, "suite_mode": 3},
    "add_case/500": {"id": 4242, "title": "New case"},
    "get_run/7": {"id": 7, "project_id": 12},
}


# --------------------------------------------------------------------------- #
# config
# --------------------------------------------------------------------------- #


@test("parse_env_file handles comments, quotes, export and inline hashes")
def _():
    parsed = parse_env_file(
        "\n".join([
            "# a comment",
            "",
            "TESTRAIL_URL=https://x.testrail.io   # trailing comment",
            "export TESTRAIL_USER=me@x.com",
            "TESTRAIL_API_KEY='has#hash#inside'",
            'QUOTED="  spaced  "',
            "not a valid line",
            "1BAD=nope",
        ])
    )
    assert parsed["TESTRAIL_URL"] == "https://x.testrail.io"
    assert parsed["TESTRAIL_USER"] == "me@x.com"
    # A '#' inside quotes is part of the value; a password may contain one.
    assert parsed["TESTRAIL_API_KEY"] == "has#hash#inside"
    assert parsed["QUOTED"] == "  spaced  "
    assert "1BAD" not in parsed


@test("config defaults to read-only")
def _():
    config = make_config()
    assert config.write_enabled is False
    assert config.writes_possible is False
    assert "read-only" in config.describe()


@test("config rejects a URL that is probably a swapped secret, without echoing it")
def _():
    exc = expect_raises(
        ConfigError,
        lambda: make_config(TESTRAIL_URL="SUPER-SECRET-KEY-1234"),
        contains="absolute http(s) URL",
    )
    assert "SUPER-SECRET-KEY-1234" not in str(exc), "error message leaked the secret"


@test("config rejects credentials embedded in the URL")
def _():
    expect_raises(
        ConfigError,
        lambda: make_config(TESTRAIL_URL="https://u:p@x.testrail.io"),
        contains="must not embed credentials",
    )


@test("config rejects an API path instead of the instance root")
def _():
    expect_raises(
        ConfigError,
        lambda: make_config(TESTRAIL_URL="https://x.testrail.io/index.php?/api/v2/"),
        contains="instance root",
    )


@test("config preserves a self-hosted subpath install")
def _():
    # Discarding the path would send every request to the web root, which fails
    # in a way that looks like a permissions problem.
    config = make_config(TESTRAIL_URL="https://tools.internal/testrail/")
    assert config.base_url == "https://tools.internal/testrail", config.base_url
    trimmed = make_config(TESTRAIL_URL="https://tools.internal/testrail/index.php")
    assert trimmed.base_url == "https://tools.internal/testrail", trimmed.base_url
    root = make_config(TESTRAIL_URL="https://accurate.testrail.io/")
    assert root.base_url == "https://accurate.testrail.io", root.base_url


@test("config rejects both auth modes at once")
def _():
    expect_raises(
        ConfigError,
        lambda: make_config(TESTRAIL_SESSION_COOKIE="tr_session=abc123"),
        contains="pick one auth mode",
    )


@test("config rejects an API key with no user")
def _():
    env = {
        "TESTRAIL_URL": "https://x.testrail.io",
        "TESTRAIL_API_KEY": "key-value-here",
    }
    expect_raises(
        ConfigError,
        lambda: load_config(env=env, env_file=Path("/nonexistent/.env")),
        contains="TESTRAIL_USER",
    )


@test("config accepts session-cookie mode")
def _():
    env = {
        "TESTRAIL_URL": "https://x.testrail.io",
        "TESTRAIL_SESSION_COOKIE": "tr_session=abc123def",
    }
    config = load_config(env=env, env_file=Path("/nonexistent/.env"))
    assert config.auth_mode == "session_cookie"


@test("config refuses a session cookie that is not a cookie")
def _():
    env = {
        "TESTRAIL_URL": "https://x.testrail.io",
        "TESTRAIL_SESSION_COOKIE": "just-a-token",
    }
    expect_raises(
        ConfigError,
        lambda: load_config(env=env, env_file=Path("/nonexistent/.env")),
        contains="cookie header",
    )


@test("config refuses a non-numeric entry in the write allowlist")
def _():
    expect_raises(
        ConfigError,
        lambda: make_config(TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12,34x"),
        contains="not a number",
    )


@test("config refuses delete enabled while in read mode")
def _():
    expect_raises(
        ConfigError,
        lambda: make_config(TESTRAIL_ALLOW_DELETE="true"),
        contains="TESTRAIL_MODE is read",
    )


@test("boolean flags fail closed on a typo")
def _():
    config = make_config(TESTRAIL_MODE="write", TESTRAIL_ALLOW_DELETE="ture")
    assert config.allow_delete is False, "a typo'd affirmative must not enable delete"


@test("real env overrides the .env file")
def _():
    env_file = Path(__file__).resolve().parent / "_test_tmp.env"
    env_file.write_text(
        "TESTRAIL_URL=https://from-file.testrail.io\n"
        "TESTRAIL_USER=file@x.com\n"
        "TESTRAIL_API_KEY=file-key-value\n",
        encoding="utf-8",
    )
    try:
        config = load_config(
            env={"TESTRAIL_API_KEY": "env-key-wins-here"}, env_file=env_file
        )
        assert config.base_url == "https://from-file.testrail.io"
        assert config.api_key == "env-key-wins-here"
    finally:
        env_file.unlink()


@test("a blank exported authorisation knob wins, so an operator can clamp a .env")
def _():
    env_file = Path(__file__).resolve().parent / "_test_clamp.env"
    env_file.write_text(
        "TESTRAIL_URL=https://x.testrail.io\n"
        "TESTRAIL_USER=me@x.com\n"
        "TESTRAIL_API_KEY=file-key-value\n"
        "TESTRAIL_MODE=write\n"
        "TESTRAIL_ALLOWED_PROJECTS=12,34\n"
        "TESTRAIL_ALLOW_DELETE=true\n",
        encoding="utf-8",
    )
    try:
        # Exporting empty values is how an operator neutralises a permissive
        # .env. Dropping the blanks would let the file win — fail-open.
        clamped = load_config(
            env={
                "TESTRAIL_MODE": "",
                "TESTRAIL_ALLOWED_PROJECTS": "",
                "TESTRAIL_ALLOW_DELETE": "",
            },
            env_file=env_file,
        )
        assert clamped.write_enabled is False
        assert clamped.allowed_projects == frozenset()
        assert clamped.allow_delete is False

        # A blank credential must NOT win: it would mask a good .env and surface
        # as the misleading "no credentials found".
        kept = load_config(env={"TESTRAIL_API_KEY": ""}, env_file=env_file)
        assert kept.api_key == "file-key-value"

        # TESTRAIL_DRY_RUN is the one knob whose blank is the *permissive*
        # setting, so a blank must not switch off a .env that had it on.
        env_file.write_text(
            "TESTRAIL_URL=https://x.testrail.io\n"
            "TESTRAIL_USER=me@x.com\n"
            "TESTRAIL_API_KEY=file-key-value\n"
            "TESTRAIL_DRY_RUN=true\n",
            encoding="utf-8",
        )
        still_dry = load_config(env={"TESTRAIL_DRY_RUN": ""}, env_file=env_file)
        assert still_dry.dry_run is True, "a blank turned dry-run off"
    finally:
        env_file.unlink()


@test("describe() reports a dry run in every posture, not just the write branch")
def _():
    read_dry = make_config(TESTRAIL_DRY_RUN="true")
    assert "DRY RUN" in read_dry.describe()
    write_dry = make_config(
        TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12", TESTRAIL_DRY_RUN="true"
    )
    assert "DRY RUN" in write_dry.describe()


@test("redactor masks longest secrets first and ignores short strings")
def _():
    redactor = Redactor()
    redactor.register("abc", "SECRET", "SECRET-EXTENDED")
    scrubbed = redactor.scrub("value=SECRET-EXTENDED and abc")
    assert scrubbed == "value=***REDACTED*** and abc", scrubbed


# --------------------------------------------------------------------------- #
# client
# --------------------------------------------------------------------------- #


@test("client sends Basic auth and registers the blob for redaction")
def _():
    config, tr_client, _guard, transport = make_stack({"get_projects": {"projects": []}})
    tr_client.get("get_projects")
    assert transport.methods == ["GET"]
    # The base64 blob is credential-equivalent, so it must scrub too.
    import base64
    blob = base64.b64encode(b"qa@accurate.com:SUPER-SECRET-KEY-1234").decode()
    assert "***REDACTED***" == config.redactor.scrub(blob)


@test("client refuses to POST in read-only mode")
def _():
    _config, tr_client, _guard, _transport = make_stack()
    expect_raises(
        Exception,
        lambda: tr_client.post("add_case/1", {"title": "x"}),
        contains="read-only mode",
    )


@test("client refuses a GET carrying a body")
def _():
    _config, tr_client, _guard, _transport = make_stack()
    expect_raises(
        Exception,
        lambda: tr_client.request("GET", "get_case/1", {"title": "x"}),
        contains="request body",
    )


@test("client maps 401 to AuthError with an actionable hint")
def _():
    error = urllib.error.HTTPError(
        "https://accurate.testrail.io", 401, "Unauthorized", {}, io.BytesIO(b'{"error":"nope"}')
    )
    _config, tr_client, _guard, _transport = make_stack({"get_projects": error})
    exc = expect_raises(AuthError, lambda: tr_client.get("get_projects"), contains="Enable API")
    assert "401" in str(exc)


@test("client surfaces an SSO interstitial as a clear message, not a JSON error")
def _():
    class HtmlTransport(FakeTransport):
        def __call__(self, request, timeout):
            return 200, "<html><body>Sign in with SSO</body></html>", {}

    config = make_config()
    tr_client = TestRailClient(config, transport=HtmlTransport(), sleep=lambda _s: None)
    expect_raises(
        TransportError, lambda: tr_client.get("get_projects"), contains="non-JSON body"
    )


@test("client retries a 500 and then succeeds")
def _():
    state = {"calls": 0}

    class FlakyTransport(FakeTransport):
        def __call__(self, request, timeout):
            state["calls"] += 1
            if state["calls"] == 1:
                raise urllib.error.HTTPError(
                    request.full_url, 500, "boom", {}, io.BytesIO(b"")
                )
            return 200, json.dumps({"projects": [{"id": 1}]}), {}

    config = make_config()
    tr_client = TestRailClient(config, transport=FlakyTransport(), sleep=lambda _s: None)
    result = tr_client.get("get_projects")
    assert state["calls"] == 2
    assert result["projects"][0]["id"] == 1


@test("Retry-After is clamped, and NaN does not crash the sleep")
def _():
    _config, tr_client, _guard, _transport = make_stack()
    assert tr_client._backoff(1, "99999") == 60.0
    assert tr_client._backoff(1, "nan") == 2.0
    assert tr_client._backoff(1, "garbage") == 2.0
    assert tr_client._backoff(1, "5") == 5.0


@test("pagination walks offsets and stops on a short page")
def _():
    pages = {
        0: {"cases": [{"id": n} for n in range(250)]},
        250: {"cases": [{"id": n} for n in range(250, 260)]},
    }

    def route(url, _body):
        offset = 0
        for part in url.split("&"):
            if part.startswith("offset="):
                offset = int(part.split("=")[1])
        return pages[offset]

    _config, tr_client, _guard, transport = make_stack({"get_cases": route})
    cases = tr_client.get_collection("get_cases/1", "cases")
    assert len(cases) == 260, len(cases)
    assert len(transport.calls) == 2


@test("pagination handles a legacy bare-array response")
def _():
    _config, tr_client, _guard, _transport = make_stack(
        {"get_priorities": [{"id": 1}, {"id": 2}]}
    )
    assert len(tr_client.get_collection("get_priorities", "priorities")) == 2


@test("pagination refuses to spin when the server ignores offset")
def _():
    _config, tr_client, _guard, _transport = make_stack(
        {"get_cases": {"cases": [{"id": n} for n in range(250)]}}
    )
    expect_raises(
        TransportError,
        lambda: tr_client.get_collection("get_cases/1", "cases"),
        contains="ignoring `offset`",
    )


@test("a 5xx on a write is NOT retried, to avoid duplicating it")
def _():
    state = {"posts": 0}

    def add_route(_url, _body):
        state["posts"] += 1
        raise urllib.error.HTTPError("u", 502, "Bad Gateway", {}, io.BytesIO(b""))

    routes = {**WRITE_ROUTES, "add_case/500": add_route}
    _config, tr_client, _guard, _t = make_stack(
        routes, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    exc = expect_raises(
        AmbiguousWriteError,
        lambda: tr_client.post("add_case/500", {"title": "x"}),
        contains="NOT retried",
    )
    assert state["posts"] == 1, f"the write was retried {state['posts']} times"
    assert "duplicate" in str(exc)


@test("a network failure on a write is NOT retried either")
def _():
    class BrokenTransport(FakeTransport):
        def __call__(self, request, timeout):
            raise urllib.error.URLError("connection reset")

    config = make_config(TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12")
    tr_client = TestRailClient(config, transport=BrokenTransport(), sleep=lambda _s: None)
    expect_raises(
        AmbiguousWriteError,
        lambda: tr_client.post("add_case/500", {"title": "x"}),
        contains="may have reached",
    )


@test("a read timeout during response.read is retried, not surfaced raw")
def _():
    state = {"calls": 0}

    class SlowTransport(FakeTransport):
        def __call__(self, request, timeout):
            state["calls"] += 1
            if state["calls"] == 1:
                # urllib only wraps open() failures into URLError, so a timeout
                # here escapes both URLError and HTTPError.
                raise TimeoutError("read timed out")
            return 200, json.dumps({"projects": [{"id": 1}]}), {}

    config = make_config()
    tr_client = TestRailClient(config, transport=SlowTransport(), sleep=lambda _s: None)
    assert tr_client.get("get_projects")["projects"][0]["id"] == 1
    assert state["calls"] == 2


@test("as_list returns empty when the named key is absent, instead of guessing")
def _():
    # Falling back to "first list found" would reintroduce the dict-ordering
    # dependence the key exists to remove.
    assert as_list({"errors": [{"x": 1}]}, "cases") == []
    assert as_list({"cases": [{"id": 1}]}, "cases") == [{"id": 1}]
    assert as_list([{"id": 1}], "cases") == [{"id": 1}]


@test("cross-host redirect is refused before it is followed")
def _():
    handler = client_mod._StrictRedirectHandler("accurate.testrail.io", require_https=True)
    expect_raises(
        urllib.error.HTTPError,
        lambda: handler.redirect_request(
            None, io.BytesIO(b""), 302, "Found", {}, "https://evil.example.com/x"
        ),
        contains="cross-host redirect",
    )


@test("https to http downgrade on the same host is refused")
def _():
    handler = client_mod._StrictRedirectHandler("accurate.testrail.io", require_https=True)
    expect_raises(
        urllib.error.HTTPError,
        lambda: handler.redirect_request(
            None, io.BytesIO(b""), 302, "Found", {}, "http://accurate.testrail.io/x"
        ),
        contains="downgrade",
    )


# --------------------------------------------------------------------------- #
# guards
# --------------------------------------------------------------------------- #


@test("require_id rejects booleans, floats with a fraction, and junk")
def _():
    _config, _c, guard, _t = make_stack()
    assert guard.require_id(12, "x") == 12
    assert guard.require_id("12", "x") == 12
    assert guard.require_id(12.0, "x") == 12
    # isinstance(True, int) is True in Python; letting it become project 1 would
    # quietly defeat the allowlist.
    expect_raises(WriteRefused, lambda: guard.require_id(True, "x"), contains="boolean")
    expect_raises(WriteRefused, lambda: guard.require_id(12.5, "x"), contains="whole number")
    expect_raises(WriteRefused, lambda: guard.require_id(0, "x"), contains="positive")
    expect_raises(WriteRefused, lambda: guard.require_id("abc", "x"), contains="positive integer")


@test("write is refused in read-only mode")
def _():
    _config, _c, guard, _t = make_stack(WRITE_ROUTES)
    expect_raises(
        WriteRefused, lambda: guard.authorise(12, "add_case"), contains="read-only"
    )


@test("write is refused when the allowlist is empty")
def _():
    _config, _c, guard, _t = make_stack(WRITE_ROUTES, TESTRAIL_MODE="write")
    expect_raises(
        WriteRefused,
        lambda: guard.authorise(12, "add_case"),
        contains="TESTRAIL_ALLOWED_PROJECTS is empty",
    )


@test("write is refused for a project outside the allowlist")
def _():
    _config, _c, guard, _t = make_stack(
        WRITE_ROUTES, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    exc = expect_raises(
        WriteRefused, lambda: guard.authorise(77, "add_case"), contains="not in TESTRAIL_ALLOWED_PROJECTS"
    )
    assert "77" in str(exc) and "12" in str(exc)


@test("section resolves to its project through the suite")
def _():
    _config, _c, guard, transport = make_stack(
        WRITE_ROUTES, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    assert guard.project_of_section(500) == 12
    # Second call must be served from cache: the resolution costs two GETs and
    # a case never changes project.
    before = len(transport.calls)
    assert guard.project_of_section(500) == 12
    assert len(transport.calls) == before


@test("case resolves to its project, and an out-of-allowlist case is refused")
def _():
    _config, _c, guard, _t = make_stack(
        WRITE_ROUTES, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    assert guard.project_of_case(5) == 12
    project = guard.project_of_section(999)
    expect_raises(
        WriteRefused, lambda: guard.authorise(project, "add_case"), contains="refused"
    )


@test("an unreadable suite_mode reports None rather than defaulting to single-suite")
def _():
    # Defaulting to 1 would silently disable the "suite_id is required" gate,
    # which is the only thing suite_mode is consulted for.
    _config, _c, guard, _t = make_stack({"get_project/12": {"id": 12}})
    assert guard.suite_mode(12) is None
    _config, _c, guard2, _t = make_stack({"get_project/12": {"id": 12, "suite_mode": 9}})
    assert guard2.suite_mode(12) is None


@test("an undeterminable suite_mode gates writes but does not break reads")
def _():
    from tools import describe_suite_mode, list_suites, require_explicit_suite
    routes = {
        "get_project/12": {"id": 12},           # no suite_mode
        "get_suites/12": {"suites": [{"id": 90, "name": "Regression"}]},
    }
    _config, tr_client, guard, _t = make_stack(routes)

    # A gate must refuse — and as a ToolError, not a policy refusal, since
    # nothing about this is a write-authorisation decision.
    exc = expect_raises(
        ToolError,
        lambda: require_explicit_suite(guard, 12, None),
        contains="did not report a usable suite_mode",
    )
    assert not isinstance(exc, WriteRefused)
    # An explicit suite_id satisfies the gate without consulting the mode at all.
    require_explicit_suite(guard, 12, 90)

    # A display-only caller must still return its data. Failing list_suites (or
    # describe_schema) here would discard a whole good response over a cosmetic
    # field.
    result = list_suites(tr_client, guard, {"project_id": 12})
    assert result["suites"][0]["id"] == 90
    assert "unknown" in result["suite_mode"]
    assert "unknown" in describe_suite_mode(None)


@test("case and run project lookups are cached on every path")
def _():
    routes = {
        # No suite_id, so resolution goes through the section fallback — the path
        # that previously returned before writing to the cache.
        "get_case/5": {"id": 5, "section_id": 500},
        "get_section/500": {"id": 500, "suite_id": 90},
        "get_suite/90": {"id": 90, "project_id": 12},
        "get_run/7": {"id": 7, "project_id": 12},
    }
    _config, _c, guard, transport = make_stack(
        routes, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    assert guard.project_of_case(5) == 12
    assert guard.project_of_run(7) == 12
    before = len(transport.calls)
    assert guard.project_of_case(5) == 12
    assert guard.project_of_run(7) == 12
    assert len(transport.calls) == before, "a cached lookup hit the network again"


@test("an unresolvable suite is refused rather than guessed")
def _():
    _config, _c, guard, _t = make_stack(
        {"get_suite/90": {"id": 90}}, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    expect_raises(
        WriteRefused, lambda: guard.project_of_suite(90), contains="could not determine"
    )


@test("a suite-less, section-less case is refused")
def _():
    _config, _c, guard, _t = make_stack(
        {"get_case/5": {"id": 5, "title": "orphan"}},
        TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12",
    )
    expect_raises(WriteRefused, lambda: guard.project_of_case(5), contains="refusing the write")


@test("delete needs the feature switch and the exact phrase")
def _():
    _config, _c, guard, _t = make_stack(
        WRITE_ROUTES, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    expect_raises(
        WriteRefused, lambda: guard.authorise_delete(DELETE_CONFIRM_PHRASE, "delete"),
        contains="deletes are disabled",
    )

    _config, _c, guard2, _t = make_stack(
        WRITE_ROUTES, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12",
        TESTRAIL_ALLOW_DELETE="true",
    )
    expect_raises(WriteRefused, lambda: guard2.authorise_delete("yes", "delete"), contains="must be exactly")
    expect_raises(WriteRefused, lambda: guard2.authorise_delete(None, "delete"), contains="must be exactly")
    guard2.authorise_delete("delete permanently", "delete")  # case-insensitive


# --------------------------------------------------------------------------- #
# tools
# --------------------------------------------------------------------------- #


@test("convert_steps maps action/expected to TestRail's shape")
def _():
    steps = convert_steps([
        {"action": "Open checkout", "expected": "Summary shown"},
        {"content": "Click Place Order", "expected_result": "One charge created"},
    ])
    assert steps == [
        {"content": "Open checkout", "expected": "Summary shown"},
        {"content": "Click Place Order", "expected": "One charge created"},
    ], steps


@test("convert_steps rejects an empty action and an empty list")
def _():
    expect_raises(ToolError, lambda: convert_steps([{"action": "  ", "expected": "x"}]), contains="empty")
    expect_raises(ToolError, lambda: convert_steps([]), contains="empty list")
    expect_raises(ToolError, lambda: convert_steps("nope"), contains="must be a list")


@test("custom_fields keys must look like custom fields")
def _():
    from tools import build_case_payload
    expect_raises(
        ToolError,
        lambda: build_case_payload({"title": "x", "custom_fields": {"objective": "y"}}),
        contains="does not start with 'custom_'",
    )
    payload = build_case_payload({"title": "x", "custom_fields": {"custom_objective": "y"}})
    assert payload["custom_objective"] == "y"


@test("custom_fields cannot overwrite a field set from a dedicated argument")
def _():
    from tools import build_case_payload
    # Otherwise custom_fields could silently replace the converted steps while
    # the response still reported the conversion as authoritative.
    expect_raises(
        ToolError,
        lambda: build_case_payload({
            "title": "x",
            "steps": [{"action": "a", "expected": "b"}],
            "custom_fields": {"custom_steps_separated": "raw garbage"},
        }),
        contains="would overwrite",
    )


@test("add_result_for_case custom_fields cannot overwrite the validated status_id")
def _():
    from tools import add_result_for_case
    routes = {**WRITE_ROUTES, "add_result_for_case/7/5": {"id": 900}}
    _config, tr_client, guard, transport = make_stack(
        routes, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    expect_raises(
        ToolError,
        lambda: add_result_for_case(tr_client, guard, {
            "run_id": 7, "case_id": 5, "status_id": 1,
            "custom_fields": {"status_id": 5},
        }),
        contains="does not start with 'custom_'",
    )
    assert "POST" not in transport.methods


@test("add_section refuses a parent in another project")
def _():
    from tools import add_section
    _config, tr_client, guard, transport = make_stack(
        WRITE_ROUTES, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    # Section 999 lives in project 77; a child inherits its parent's suite, so
    # this would escape the allowlisted project despite project_id passing.
    expect_raises(
        ToolError,
        lambda: add_section(tr_client, guard, {
            "project_id": 12, "name": "New", "suite_id": 90, "parent_id": 999,
        }),
        contains="belongs to project 77",
    )
    assert "POST" not in transport.methods


@test("write tools are not registered in read-only mode")
def _():
    registry = build_registry(make_config())
    assert "testrail_list_cases" in registry
    assert "testrail_add_case" not in registry
    assert "testrail_delete_case" not in registry


@test("delete tool appears only when explicitly enabled")
def _():
    write_only = build_registry(
        make_config(TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12")
    )
    assert "testrail_add_case" in write_only
    assert "testrail_delete_case" not in write_only

    with_delete = build_registry(
        make_config(
            TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12",
            TESTRAIL_ALLOW_DELETE="true",
        )
    )
    assert "testrail_delete_case" in with_delete


@test("dry-run mode labels the write tools")
def _():
    registry = build_registry(
        make_config(
            TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12", TESTRAIL_DRY_RUN="true"
        )
    )
    assert registry["testrail_add_case"]["description"].startswith("[DRY RUN")
    assert not registry["testrail_list_cases"]["description"].startswith("[DRY RUN")


@test("add_case writes when the target is allowlisted")
def _():
    from tools import add_case
    _config, tr_client, guard, transport = make_stack(
        WRITE_ROUTES, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    result = add_case(tr_client, guard, {
        "section_id": 500,
        "title": "Verify one charge per order",
        "steps": [{"action": "Place order", "expected": "Exactly one charge"}],
        "refs": "ACC-9279",
        "priority_id": 4,
    })
    assert result["created"] is True and result["case_id"] == 4242
    posts = [(m, u, b) for m, u, b in transport.calls if m == "POST"]
    assert len(posts) == 1
    assert posts[0][2]["custom_steps_separated"][0]["content"] == "Place order"
    assert posts[0][2]["refs"] == "ACC-9279"


@test("add_case sends nothing when the target is not allowlisted")
def _():
    from tools import add_case
    _config, tr_client, guard, transport = make_stack(
        WRITE_ROUTES, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    expect_raises(
        WriteRefused,
        lambda: add_case(tr_client, guard, {"section_id": 999, "title": "Wrong project"}),
        contains="not in TESTRAIL_ALLOWED_PROJECTS",
    )
    assert "POST" not in transport.methods, "a refused write still hit the network"


@test("dry run validates and sends nothing")
def _():
    from tools import add_case
    _config, tr_client, guard, transport = make_stack(
        WRITE_ROUTES, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12",
        TESTRAIL_DRY_RUN="true",
    )
    result = add_case(tr_client, guard, {"section_id": 500, "title": "Dry"})
    assert result["dry_run"] is True
    assert "POST" not in transport.methods


@test("bulk add validates every case before writing any")
def _():
    from tools import add_cases
    _config, tr_client, guard, transport = make_stack(
        WRITE_ROUTES, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    expect_raises(
        ToolError,
        lambda: add_cases(tr_client, guard, {
            "section_id": 500,
            "cases": [{"title": "Good"}, {"title": "Bad", "custom_fields": {"nope": 1}}],
        }),
        contains="cases[2]",
    )
    assert "POST" not in transport.methods, "case 1 was written before case 2 failed validation"


@test("bulk add reports created ids on a partial failure")
def _():
    from tools import add_cases
    state = {"posts": 0}

    def add_route(_url, _body):
        state["posts"] += 1
        if state["posts"] == 2:
            raise urllib.error.HTTPError(
                "u", 400, "Bad", {}, io.BytesIO(b'{"error":"Field :title is too long"}')
            )
        return {"id": 1000 + state["posts"]}

    routes = {**WRITE_ROUTES, "add_case/500": add_route}
    _config, tr_client, guard, _t = make_stack(
        routes, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    result = add_cases(tr_client, guard, {
        "section_id": 500,
        "cases": [{"title": "A"}, {"title": "B"}, {"title": "C"}],
    })
    assert result["created_count"] == 1
    assert result["partial"] is True
    assert result["not_attempted"] == 1
    assert "re-pushing the whole batch" in result["recovery"]


@test("add_run drops include_all when specific case_ids are given")
def _():
    from tools import add_run
    routes = {**WRITE_ROUTES, "add_run/12": {"id": 300}}
    _config, tr_client, guard, transport = make_stack(
        routes, TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12"
    )
    add_run(tr_client, guard, {
        "project_id": 12, "name": "ACC-9279 regression",
        "suite_id": 90, "case_ids": [5, 6], "include_all": True,
    })
    body = [b for m, _u, b in transport.calls if m == "POST"][0]
    # TestRail lets include_all win, silently ignoring the selection.
    assert body["include_all"] is False
    assert body["case_ids"] == [5, 6]


@test("multiple-suite projects demand a suite_id instead of silently reading suite 1")
def _():
    from tools import list_cases
    _config, tr_client, guard, _t = make_stack(WRITE_ROUTES)
    expect_raises(
        ToolError,
        lambda: list_cases(tr_client, guard, {"project_id": 12}),
        contains="suite_id is required",
    )


@test("search reports when its scan ceiling truncated the result")
def _():
    from tools import search_cases
    routes = {
        "get_project/12": {"id": 12, "suite_mode": 1},
        "get_cases": {"cases": [{"id": n, "title": "checkout flow"} for n in range(250)]},
    }
    _config, tr_client, guard, _t = make_stack(routes)
    result = search_cases(tr_client, guard, {
        "project_id": 12, "query": "checkout", "scan_limit": 250,
    })
    assert "warning" in result and "partial" in result["warning"].lower()


@test("render marks truncated output as unparseable")
def _():
    text = render({"data": "x" * 5000}, max_chars=200)
    assert len(text) < 600
    assert "TRUNCATED" in text and "not valid JSON" in text


# --------------------------------------------------------------------------- #
# protocol
# --------------------------------------------------------------------------- #


def run_session(lines: list[dict], **overrides) -> list[dict]:
    routes = {**WRITE_ROUTES, "get_projects": {"projects": [{"id": 12, "name": "Accurate"}]}}
    config, tr_client, _guard, _t = make_stack(routes, **overrides)
    server = Server(config, tr_client)
    stdin = io.StringIO("\n".join(json.dumps(line) for line in lines) + "\n")
    stdout = io.StringIO()
    server.serve(stdin, stdout)
    return [json.loads(line) for line in stdout.getvalue().splitlines() if line.strip()]


@test("initialize echoes a supported protocol version and advertises tools")
def _():
    responses = run_session([{
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "clientInfo": {"name": "test"}},
    }])
    result = responses[0]["result"]
    assert result["protocolVersion"] == "2024-11-05"
    assert result["capabilities"]["tools"] == {"listChanged": False}
    assert "testrail_describe_schema" in result["instructions"]


@test("initialize falls back to the preferred version for an unknown request")
def _():
    responses = run_session([{
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "1999-01-01"},
    }])
    assert responses[0]["result"]["protocolVersion"] == "2025-06-18"


@test("read-only instructions tell the agent not to imply a push happened")
def _():
    responses = run_session([
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
    ])
    assert "READ-ONLY" in responses[0]["result"]["instructions"]


@test("write instructions name the allowlisted projects")
def _():
    responses = run_session(
        [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}],
        TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12,34",
    )
    instructions = responses[0]["result"]["instructions"]
    assert "12, 34" in instructions


@test("notifications get no response")
def _():
    responses = run_session([
        {"jsonrpc": "2.0", "method": "notifications/initialized"},
        {"jsonrpc": "2.0", "id": 2, "method": "ping"},
    ])
    assert len(responses) == 1 and responses[0]["id"] == 2


@test("ANY id-less message gets no response, not just notifications/*")
def _():
    # The id-less check has to run before the handler branches. Replying with
    # "id": null to an id-less ping would desynchronise a strict client.
    responses = run_session([
        {"jsonrpc": "2.0", "method": "ping"},
        {"jsonrpc": "2.0", "method": "tools/list"},
        {"jsonrpc": "2.0", "method": "initialize", "params": {}},
        {"jsonrpc": "2.0", "id": 9, "method": "ping"},
    ])
    assert len(responses) == 1, f"expected 1 response, got {len(responses)}"
    assert responses[0]["id"] == 9


@test("a request with no method is an invalid request, not method-not-found")
def _():
    responses = run_session([{"jsonrpc": "2.0", "id": 1}])
    assert responses[0]["error"]["code"] == -32600


@test("tools/list omits write tools in read-only mode")
def _():
    responses = run_session([{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}])
    names = {t["name"] for t in responses[0]["result"]["tools"]}
    assert "testrail_list_cases" in names
    assert not any(n.startswith("testrail_add") for n in names)
    # Every advertised tool needs a schema, or a strict client rejects the list.
    for tool in responses[0]["result"]["tools"]:
        assert tool["inputSchema"]["type"] == "object"


@test("tools/call returns a result as text content")
def _():
    responses = run_session([{
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "testrail_list_projects", "arguments": {}},
    }])
    result = responses[0]["result"]
    assert result["isError"] is False
    assert "Accurate" in result["content"][0]["text"]


@test("a policy refusal is a tool error marked non-retryable, not a crash")
def _():
    responses = run_session(
        [{
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {
                "name": "testrail_add_case",
                "arguments": {"section_id": 999, "title": "Wrong project"},
            },
        }],
        TESTRAIL_MODE="write", TESTRAIL_ALLOWED_PROJECTS="12",
    )
    text = responses[0]["result"]["content"][0]["text"]
    assert responses[0]["result"]["isError"] is True
    assert "REFUSED BY POLICY" in text
    assert "will not succeed on retry" in text


@test("calling a write tool in read-only mode explains the posture")
def _():
    responses = run_session([{
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "testrail_add_case", "arguments": {}},
    }])
    text = responses[0]["result"]["content"][0]["text"]
    assert "read-only" in text and "do not retry" in text.lower()


@test("malformed JSON gets a parse error and the loop survives")
def _():
    config, tr_client, _g, _t = make_stack()
    server = Server(config, tr_client)
    stdin = io.StringIO('{"broken\n{"jsonrpc":"2.0","id":2,"method":"ping"}\n')
    stdout = io.StringIO()
    server.serve(stdin, stdout)
    responses = [json.loads(l) for l in stdout.getvalue().splitlines() if l.strip()]
    assert responses[0]["error"]["code"] == -32700
    assert responses[1]["id"] == 2, "the server did not survive a bad line"


@test("an unknown method is reported without killing the session")
def _():
    responses = run_session([
        {"jsonrpc": "2.0", "id": 1, "method": "resources/list"},
        {"jsonrpc": "2.0", "id": 2, "method": "ping"},
    ])
    assert responses[0]["error"]["code"] == -32601
    assert responses[1]["result"] == {}


@test("secrets never reach stdout, even when echoed back by the instance")
def _():
    # Simulate the worst case: TestRail reflects the credential in an error body.
    config = make_config()
    transport = FakeTransport({
        "get_projects": {"projects": [{"id": 1, "name": "leak SUPER-SECRET-KEY-1234 here"}]}
    })
    tr_client = TestRailClient(config, transport=transport, sleep=lambda _s: None)
    server = Server(config, tr_client)
    stdin = io.StringIO(json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "testrail_list_projects", "arguments": {}},
    }) + "\n")
    stdout = io.StringIO()
    server.serve(stdin, stdout)
    output = stdout.getvalue()
    assert "SUPER-SECRET-KEY-1234" not in output, "the API key reached stdout"
    assert "***REDACTED***" in output


@test("a secret containing non-ASCII characters is still redacted")
def _():
    # json.dumps(ensure_ascii=True) rewrites 'ä' as ä, after which a plain
    # substring search no longer matches the raw secret. Scrubbing the object
    # before serialisation is what closes that hole.
    env = {
        "TESTRAIL_URL": "https://accurate.testrail.io",
        "TESTRAIL_USER": "qa@accurate.com",
        "TESTRAIL_API_KEY": "pässwort-secret-1234",
    }
    config = load_config(env=env, env_file=Path("/nonexistent/.env"))
    transport = FakeTransport({
        "get_projects": {"projects": [{"id": 1, "name": "leak pässwort-secret-1234"}]}
    })
    tr_client = TestRailClient(config, transport=transport, sleep=lambda _s: None)
    server = Server(config, tr_client)
    stdin = io.StringIO(json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "testrail_list_projects", "arguments": {}},
    }) + "\n")
    stdout = io.StringIO()
    server.serve(stdin, stdout)
    output = stdout.getvalue()
    assert "pässwort-secret-1234" not in output
    # The escaped form is the one that used to survive.
    assert "p\\u00e4sswort-secret-1234" not in output, "escaped secret leaked"
    assert "***REDACTED***" in output


@test("an unexpected handler exception becomes a tool error, not a dead server")
def _():
    config, tr_client, _g, _t = make_stack()
    server = Server(config, tr_client)
    server.registry["testrail_boom"] = {
        "name": "testrail_boom", "description": "", "inputSchema": {"type": "object"},
        "handler": lambda *_a: (_ for _ in ()).throw(ZeroDivisionError("kaboom")),
    }
    stdin = io.StringIO(
        json.dumps({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                    "params": {"name": "testrail_boom"}}) + "\n"
        + json.dumps({"jsonrpc": "2.0", "id": 2, "method": "ping"}) + "\n"
    )
    stdout = io.StringIO()
    server.serve(stdin, stdout)
    responses = [json.loads(l) for l in stdout.getvalue().splitlines() if l.strip()]
    assert responses[0]["result"]["isError"] is True
    assert "ZeroDivisionError" in responses[0]["result"]["content"][0]["text"]
    assert responses[1]["id"] == 2, "the server died on an unexpected exception"


@test("every response is a single line of ASCII JSON")
def _():
    config = make_config()
    transport = FakeTransport({
        "get_projects": {"projects": [{"id": 1, "name": "Ünïcode\nwith newline"}]}
    })
    tr_client = TestRailClient(config, transport=transport, sleep=lambda _s: None)
    server = Server(config, tr_client)
    stdin = io.StringIO(json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "testrail_list_projects", "arguments": {}},
    }) + "\n")
    stdout = io.StringIO()
    server.serve(stdin, stdout)
    lines = [l for l in stdout.getvalue().split("\n") if l]
    # A raw newline inside a case title must not split one message across two
    # lines, or the client's framing breaks.
    assert len(lines) == 1, f"expected 1 line, got {len(lines)}"
    assert lines[0].isascii()
    json.loads(lines[0])


# --------------------------------------------------------------------------- #

def main() -> int:
    print(f"\n{len(PASSED) + len(FAILED)} tests\n")
    for name, detail in FAILED:
        print(f"  FAIL  {name}\n        {detail.strip()[:400]}\n")
    print(f"  {len(PASSED)} passed, {len(FAILED)} failed\n")
    return 1 if FAILED else 0


if __name__ == "__main__":
    sys.exit(main())

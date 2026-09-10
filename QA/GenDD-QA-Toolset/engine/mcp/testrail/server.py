#!/usr/bin/env python3
"""MCP stdio server for TestRail. Python 3.10+, standard library only.

Why hand-rolled instead of the MCP SDK
--------------------------------------
The requirement that started this work was: no community TestRail MCP server,
for security reasons. Adding the official MCP SDK would pull a dependency tree
back in and undo most of that decision's value. The wire protocol needed here is
newline-delimited JSON-RPC 2.0 over stdin/stdout with three methods — small
enough to implement and audit in one file. Every byte this server sends and
receives is visible in this repository.

Protocol
--------
* One JSON object per line on stdin; one JSON object per line on stdout.
* ``initialize`` -> capabilities and server info. The client's requested
  protocol version is echoed back when we recognise it, so a newer client is not
  forced to downgrade over a version string alone.
* ``tools/list`` -> the registry for the configured posture.
* ``tools/call`` -> a handler result as MCP text content.
* ``notifications/*`` are acknowledged by producing no response, per spec.

Two rules keep the transport intact:

1. **Nothing but JSON-RPC goes to stdout.** Any stray ``print`` corrupts the
   stream and the client drops the connection with no useful error. Logging goes
   to stderr, which is what the client surfaces in its MCP log pane.
2. **A handler exception is a tool error, not a protocol error.** Tool failures
   come back as ``isError: true`` content so the agent can read the reason and
   adapt. Only malformed JSON-RPC produces a protocol-level error object.

Every outgoing message passes through the redactor. That is a single choke point
by design — relying on each call site to remember to scrub is how a credential
eventually ends up in a log.
"""

from __future__ import annotations

import json
import sys
from typing import Any, TextIO

from client import (
    AmbiguousWriteError,
    AuthError,
    NotFoundError,
    RateLimitError,
    TestRailClient,
    TransportError,
)
from config import Config, ConfigError, load_config
from guards import Guard, WriteRefused
from tools import ToolError, build_registry, render

SERVER_NAME = "testrail-bridge"
SERVER_VERSION = "1.0.0"

# Versions whose shape this server implements. If the client asks for one of
# these, echo it; otherwise answer with our preferred version and let the client
# decide whether it can proceed.
SUPPORTED_PROTOCOL_VERSIONS = ("2025-06-18", "2025-03-26", "2024-11-05")
PREFERRED_PROTOCOL_VERSION = SUPPORTED_PROTOCOL_VERSIONS[0]

# JSON-RPC 2.0 error codes
PARSE_ERROR = -32700
INVALID_REQUEST = -32600
METHOD_NOT_FOUND = -32601
INTERNAL_ERROR = -32603


# Set once in main(). stderr is surfaced in the client's MCP log pane, so it is
# outgoing too and must go through the same redaction as stdout — several log
# call sites interpolate raw exception text that has not been scrubbed.
_REDACTOR: Any = None


def log(message: str) -> None:
    """Log to stderr. Never stdout — that channel is the protocol."""
    if _REDACTOR is not None:
        message = _REDACTOR.scrub(message)
    print(f"[{SERVER_NAME}] {message}", file=sys.stderr, flush=True)


class Server:
    def __init__(self, config: Config, client: TestRailClient) -> None:
        self.config = config
        self.client = client
        self.guard = Guard(client)
        self.registry = build_registry(config)

    # -- protocol ----------------------------------------------------------- #

    def handle(self, message: dict[str, Any]) -> dict[str, Any] | None:
        """Route one JSON-RPC message. None means "send no response"."""
        method = message.get("method")
        msg_id = message.get("id")
        params = message.get("params") or {}
        if not isinstance(params, dict):
            params = {}

        # A notification has no id. Per JSON-RPC it must never be answered, so
        # this returns before any handler branch — an earlier version computed
        # the flag here but only consulted it at the bottom, which meant an
        # id-less `ping` or `tools/list` still got a reply with "id": null.
        if "id" not in message:
            return None

        if not isinstance(method, str):
            return self._error(
                msg_id, INVALID_REQUEST, "request is missing a string `method`"
            )

        if method == "initialize":
            return self._result(msg_id, self._initialize(params))

        if method.startswith("notifications/"):
            # A notification that wrongly carries an id. Acknowledge rather than
            # error: the client is confused, but nothing is broken.
            return self._result(msg_id, {})

        if method == "ping":
            return self._result(msg_id, {})

        if method == "tools/list":
            return self._result(msg_id, {
                "tools": [
                    {
                        "name": tool["name"],
                        "description": tool["description"],
                        "inputSchema": tool["inputSchema"],
                    }
                    for tool in self.registry.values()
                ]
            })

        if method == "tools/call":
            return self._result(msg_id, self._call_tool(params))

        # resources/* and prompts/* are not advertised in our capabilities, so a
        # spec-compliant client will not ask. Answer honestly if one does.
        return self._error(msg_id, METHOD_NOT_FOUND, f"method not supported: {method}")

    def _initialize(self, params: dict[str, Any]) -> dict[str, Any]:
        requested = params.get("protocolVersion")
        version = (
            requested
            if isinstance(requested, str) and requested in SUPPORTED_PROTOCOL_VERSIONS
            else PREFERRED_PROTOCOL_VERSION
        )
        client_info = params.get("clientInfo") or {}
        log(f"initialize from {client_info.get('name', 'unknown client')} "
            f"(protocol {requested or 'unspecified'} -> {version})")
        log(f"posture: {self.config.describe()}")
        log(f"tools registered: {len(self.registry)}")
        return {
            "protocolVersion": version,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {"name": SERVER_NAME, "version": SERVER_VERSION},
            "instructions": self._instructions(),
        }

    def _instructions(self) -> str:
        lines = [
            "TestRail bridge for the QA-GenDD engine.",
            "",
            "Before generating or pushing any test case, call "
            "testrail_describe_schema to get this instance's real field ids, "
            "required fields, and legal option values. Priority names, type names "
            "and result status ids are all per-instance configuration — inventing "
            "them is the main cause of malformed imports.",
            "",
            "To find where a case belongs: testrail_list_projects -> "
            "testrail_list_suites -> testrail_list_sections. Before writing new "
            "coverage, run testrail_search_cases on the ticket key to avoid "
            "duplicating a case that already exists.",
        ]
        if not self.config.write_enabled:
            lines += [
                "",
                "This bridge is READ-ONLY. No write tools are available. Export "
                "generated cases to a file for human import instead of implying a "
                "push happened.",
            ]
        elif not self.config.allowed_projects:
            lines += [
                "",
                "Write mode is on but the project allowlist is EMPTY, so every "
                "write will be refused. Report this as a configuration problem "
                "rather than retrying.",
            ]
        else:
            allowed = ", ".join(str(i) for i in sorted(self.config.allowed_projects))
            lines += [
                "",
                f"Writes are permitted ONLY in project(s) {allowed}. A write "
                f"targeting any other project is refused after the target is "
                f"resolved. Do not attempt to work around this — report it.",
            ]
        if self.config.dry_run:
            lines += [
                "",
                "DRY RUN is active: writes are validated and echoed but never "
                "sent. Never report a dry-run response as a completed push.",
            ]
        return "\n".join(lines)

    # -- dispatch ----------------------------------------------------------- #

    def _call_tool(self, params: dict[str, Any]) -> dict[str, Any]:
        name = params.get("name")
        args = params.get("arguments")
        if not isinstance(args, dict):
            args = {}

        tool = self.registry.get(name) if isinstance(name, str) else None
        if tool is None:
            available = ", ".join(sorted(self.registry)) or "none"
            hint = ""
            # The likeliest reason a write tool is "unknown" is posture, and
            # saying so saves a confused retry loop.
            if isinstance(name, str) and name.startswith("testrail_") and not self.config.write_enabled:
                hint = (
                    " This bridge is running read-only, so write tools are not "
                    "registered. That is configuration, not a transient failure —"
                    " do not retry."
                )
            return self._tool_error(f"unknown tool {name!r}.{hint} Available: {available}")

        try:
            result = tool["handler"](self.client, self.guard, args)
        except WriteRefused as exc:
            # Policy refusal. Deliberately phrased so the agent stops rather than
            # retrying or hunting for another route.
            return self._tool_error(f"REFUSED BY POLICY: {exc}", retryable=False)
        except (ToolError, NotFoundError) as exc:
            return self._tool_error(f"Invalid request: {exc}", retryable=False)
        except AmbiguousWriteError as exc:
            # Explicitly non-retryable, and phrased so the agent verifies rather
            # than re-sends: the whole reason this exception exists is that a
            # retry could duplicate a write that already landed.
            return self._tool_error(
                f"WRITE OUTCOME UNKNOWN: {exc}\n\nDo NOT re-send this write. Read "
                f"the current state back from TestRail first and report what you "
                f"find.",
                retryable=False,
            )
        except AuthError as exc:
            return self._tool_error(f"Authentication failed: {exc}", retryable=False)
        except RateLimitError as exc:
            return self._tool_error(f"Rate limited: {exc}", retryable=True)
        except TransportError as exc:
            return self._tool_error(f"TestRail unreachable or erroring: {exc}", retryable=True)
        except Exception as exc:  # noqa: BLE001
            # Never let an unexpected exception kill the server: the client would
            # lose every tool for the rest of the session over one bad call.
            log(f"unhandled error in {name}: {type(exc).__name__}: {exc}")
            return self._tool_error(
                f"Unexpected {type(exc).__name__} in {name}: {exc}"
            )

        return {
            "content": [{"type": "text", "text": render(result, self.config.max_response_chars)}],
            "isError": False,
        }

    def _tool_error(self, message: str, retryable: bool | None = None) -> dict[str, Any]:
        if retryable is False:
            message += "\n\n(This will not succeed on retry. Fix the request or "
            message += "escalate the configuration.)"
        elif retryable is True:
            message += "\n\n(This may succeed on retry after a short wait.)"
        return {"content": [{"type": "text", "text": message}], "isError": True}

    # -- envelopes ---------------------------------------------------------- #

    @staticmethod
    def _result(msg_id: Any, result: Any) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": msg_id, "result": result}

    @staticmethod
    def _error(msg_id: Any, code: int, message: str) -> dict[str, Any]:
        return {"jsonrpc": "2.0", "id": msg_id, "error": {"code": code, "message": message}}

    # -- loop --------------------------------------------------------------- #

    def serve(self, stdin: TextIO, stdout: TextIO) -> int:
        for raw_line in stdin:
            line = raw_line.strip()
            if not line:
                continue

            try:
                message = json.loads(line)
            except json.JSONDecodeError as exc:
                self._write(stdout, self._error(None, PARSE_ERROR, f"invalid JSON: {exc}"))
                continue

            if not isinstance(message, dict) or message.get("jsonrpc") != "2.0":
                # Batches are legal JSON-RPC but not used by MCP clients, and
                # accepting them would mean a second, barely-exercised code path
                # through the dispatcher.
                self._write(
                    stdout,
                    self._error(
                        message.get("id") if isinstance(message, dict) else None,
                        INVALID_REQUEST,
                        "expected a single JSON-RPC 2.0 request object",
                    ),
                )
                continue

            try:
                response = self.handle(message)
            except Exception as exc:  # noqa: BLE001
                log(f"dispatch error: {type(exc).__name__}: {exc}")
                response = self._error(
                    message.get("id"), INTERNAL_ERROR, f"{type(exc).__name__}: {exc}"
                )

            if response is not None:
                self._write(stdout, response)
        return 0

    def _write(self, stdout: TextIO, payload: dict[str, Any]) -> None:
        """The single point where anything reaches stdout — and the only scrub site.

        ``ensure_ascii=True`` is intentional: it guarantees the encoded message
        contains no raw newlines or non-ASCII bytes, which keeps one message on
        one line regardless of what TestRail put in a case title.

        Redaction runs twice, and the order matters. ``scrub_obj`` goes first
        because ``ensure_ascii=True`` would rewrite a secret containing any
        non-ASCII character as ``\\uXXXX`` and a quote or backslash as an escape
        — after which a plain substring search no longer matches it, and the
        secret survives in escaped-but-readable form. ``scrub`` then runs on the
        encoded text to catch anything assembled during serialisation.
        """
        scrubbed = self.config.redactor.scrub_obj(payload)
        text = json.dumps(scrubbed, ensure_ascii=True, default=str)
        stdout.write(self.config.redactor.scrub(text) + "\n")
        stdout.flush()


def main(argv: list[str] | None = None) -> int:
    global _REDACTOR
    argv = list(sys.argv[1:] if argv is None else argv)

    try:
        config = load_config()
    except ConfigError as exc:
        # Nothing is registered for redaction yet if load_config raised early,
        # which is why every ConfigError message is written to withhold values.
        log(f"CONFIGURATION ERROR: {exc}")
        return 1

    _REDACTOR = config.redactor
    client = TestRailClient(config)

    # --probe runs the connectivity check as a plain CLI and exits. Handy for
    # verifying credentials without wiring the server into an MCP client first,
    # which is otherwise an awkward thing to debug.
    if "--probe" in argv:
        from tools import probe as probe_handler
        log(f"posture: {config.describe()}")
        try:
            result = probe_handler(client, Guard(client), {})
        except Exception as exc:  # noqa: BLE001
            log(f"PROBE FAILED: {config.redactor.scrub(str(exc))}")
            return 2
        print(config.redactor.scrub(json.dumps(result, indent=2, default=str)))
        return 0

    if "--list-tools" in argv:
        for name, tool in sorted(build_registry(config).items()):
            print(f"{name}\n    {tool['description'][:160]}")
        return 0

    log(f"starting {SERVER_NAME} {SERVER_VERSION}")
    log(f"posture: {config.describe()}")
    if config.write_enabled and not config.allowed_projects:
        log("WARNING: write mode with an empty TESTRAIL_ALLOWED_PROJECTS — every "
            "write will be refused.")

    server = Server(config, client)
    try:
        return server.serve(sys.stdin, sys.stdout)
    except (BrokenPipeError, KeyboardInterrupt):
        # The client closing the pipe is a normal shutdown, not a failure.
        return 0


if __name__ == "__main__":
    sys.exit(main())

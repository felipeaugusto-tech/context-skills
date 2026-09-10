#!/usr/bin/env python3
"""Write authorisation for the TestRail bridge.

The problem this solves
----------------------
An agent holding a TestRail credential inherits every permission that credential
has, across every project. "Full read/write" was the intended capability, but
"full read/write *to the wrong project*" is the failure mode that matters — a
malformed bulk push into a live regression suite is expensive to undo, and
TestRail has no undo.

So every write is resolved to a **project id** and checked against an explicit
allowlist before it is sent. There is no wildcard. An empty allowlist means no
write succeeds, which is what makes the default safe.

Why resolution needs an API round trip
--------------------------------------
The obvious implementation — read ``project_id`` off the request — does not work,
because TestRail's write endpoints do not take one. ``add_case`` takes a
``section_id``; ``update_case`` takes a ``case_id``. Neither response carries a
project id, and ``get_case``/``get_section`` do not return one either.

The only reliable path is through the suite, which *does* carry ``project_id``:

    case_id    -> get_case    -> suite_id -> get_suite -> project_id
    section_id -> get_section -> suite_id -> get_suite -> project_id
    run_id     -> get_run     -> project_id            (directly available)

That is up to two extra GETs per write. They are cached for the life of the
process, since a case never changes project. The cost is real but small, and the
alternative is trusting a caller-supplied project id — which an agent could
simply get wrong, defeating the entire control.

**Ambiguity is refused, never guessed.** If the chain cannot be completed — a
suite-less case on a very old single-suite project, say — the write is rejected
with an explanation rather than allowed through.
"""

from __future__ import annotations

from typing import Any

from client import NotFoundError, TestRailClient, TestRailError

# Required for delete_case, matched case-insensitively after stripping. Chosen to
# be something an agent will not emit by accident while summarising a request.
DELETE_CONFIRM_PHRASE = "DELETE PERMANENTLY"


class WriteRefused(TestRailError):
    """A write was blocked by policy. Not a transport or credential failure.

    Separate from the client's exceptions on purpose: this one is never retried
    and never indicates a broken instance. It means the bridge did its job.
    """


class Guard:
    """Resolves write targets to projects and enforces the allowlist."""

    def __init__(self, client: TestRailClient) -> None:
        self.client = client
        self.config = client.config
        # Resolution costs up to two extra GETs per write, so every result is
        # cached for the process lifetime. A case never changes project.
        self._suite_project: dict[int, int] = {}
        self._section_suite: dict[int, int | None] = {}
        self._case_project: dict[int, int] = {}
        self._run_project: dict[int, int] = {}
        self._project_suite_mode: dict[int, int | None] = {}

    # -- id coercion -------------------------------------------------------- #

    @staticmethod
    def require_id(value: Any, name: str) -> int:
        """Coerce a tool argument to a positive int, or refuse.

        JSON-RPC clients are inconsistent about whether an id arrives as ``12``
        or ``"12"``, and a float like ``12.0`` survives JSON round-tripping. All
        three are accepted; ``12.5`` and ``"twelve"`` are not. A bool is rejected
        outright — ``isinstance(True, int)`` is True in Python, and letting
        ``True`` become project 1 is exactly the kind of silent coercion that
        makes an allowlist useless.
        """
        if isinstance(value, bool):
            raise WriteRefused(f"{name} must be a number, got a boolean")
        if isinstance(value, int):
            parsed = value
        elif isinstance(value, float):
            if value != int(value):
                raise WriteRefused(f"{name} must be a whole number, got {value}")
            parsed = int(value)
        elif isinstance(value, str) and value.strip().lstrip("-").isdigit():
            parsed = int(value.strip())
        else:
            raise WriteRefused(f"{name} must be a positive integer, got {value!r}")
        if parsed <= 0:
            raise WriteRefused(f"{name} must be a positive integer, got {parsed}")
        return parsed

    # -- resolution --------------------------------------------------------- #

    def project_of_suite(self, suite_id: int) -> int:
        if suite_id not in self._suite_project:
            suite = self.client.get(f"get_suite/{suite_id}")
            if not isinstance(suite, dict) or suite.get("project_id") is None:
                raise WriteRefused(
                    f"could not determine which project suite {suite_id} belongs "
                    f"to, so the allowlist cannot be checked. Refusing the write."
                )
            self._suite_project[suite_id] = int(suite["project_id"])
        return self._suite_project[suite_id]

    def project_of_section(self, section_id: int) -> int:
        if section_id not in self._section_suite:
            section = self.client.get(f"get_section/{section_id}")
            if not isinstance(section, dict):
                raise WriteRefused(
                    f"section {section_id} did not resolve to a section object; "
                    f"refusing the write."
                )
            self._section_suite[section_id] = section.get("suite_id")
        suite_id = self._section_suite[section_id]
        if suite_id is None:
            raise WriteRefused(
                f"section {section_id} reports no suite_id, so its project cannot "
                f"be resolved and the allowlist cannot be enforced. Refusing the "
                f"write. Pass an explicit section inside a suite instead."
            )
        return self.project_of_suite(int(suite_id))

    def project_of_case(self, case_id: int) -> int:
        if case_id not in self._case_project:
            case = self.client.get(f"get_case/{case_id}")
            if not isinstance(case, dict):
                raise WriteRefused(
                    f"case {case_id} did not resolve to a case object; refusing "
                    f"the write."
                )
            suite_id = case.get("suite_id")
            if suite_id is not None:
                project_id = self.project_of_suite(int(suite_id))
            elif case.get("section_id") is not None:
                # Single-suite projects can return a null suite_id. Fall back to
                # the section, which is always present on a real case.
                try:
                    project_id = self.project_of_section(
                        self.require_id(case["section_id"], "section_id")
                    )
                except NotFoundError as exc:
                    raise WriteRefused(
                        f"case {case_id} has no suite_id and its section could "
                        f"not be read, so the allowlist cannot be enforced: {exc}"
                    ) from exc
            else:
                raise WriteRefused(
                    f"case {case_id} reports neither a suite nor a section, so "
                    f"its project cannot be resolved. Refusing the write."
                )
            # Cached on every path, including the section fallback. An earlier
            # version returned before storing, so exactly the cases needing the
            # extra lookup were the ones that never benefited from the cache.
            self._case_project[case_id] = project_id
        return self._case_project[case_id]

    def project_of_run(self, run_id: int) -> int:
        if run_id not in self._run_project:
            run = self.client.get(f"get_run/{run_id}")
            if not isinstance(run, dict) or run.get("project_id") is None:
                raise WriteRefused(
                    f"could not determine which project run {run_id} belongs to; "
                    f"refusing the write."
                )
            self._run_project[run_id] = int(run["project_id"])
        return self._run_project[run_id]

    def suite_mode(self, project_id: int) -> int | None:
        """1 = single suite, 2 = single + baselines, 3 = multiple suites.

        Returns ``None`` when the instance did not report a usable value, rather
        than defaulting to 1. Defaulting silently disabled the "suite_id is
        required" gate on multi-suite projects — the one thing this value is
        consulted for — which would mean addressing only suite #1 while believing
        the whole project had been covered.

        ``None`` rather than an exception because the callers differ: the ones
        that use the value as a *gate* must refuse (see
        ``tools.require_explicit_suite``), but ``list_suites`` and
        ``describe_schema`` only display it, and failing those over a cosmetic
        field would throw away an otherwise complete response.

        Note this only softens an unusable *value*. A 403 or 404 on
        ``get_project`` still propagates, because that is a real access problem
        and reporting it as "mode unknown" would hide it.
        """
        if project_id not in self._project_suite_mode:
            project = self.client.get(f"get_project/{project_id}")
            mode = project.get("suite_mode") if isinstance(project, dict) else None
            try:
                parsed = int(mode)
            except (TypeError, ValueError):
                parsed = None
            # Negative results are cached too. Without this, an instance that
            # never reports a usable suite_mode would re-issue get_project on
            # every single tool call.
            self._project_suite_mode[project_id] = parsed if parsed in (1, 2, 3) else None
        return self._project_suite_mode[project_id]

    # -- enforcement -------------------------------------------------------- #

    def authorise(self, project_id: int, operation: str) -> None:
        """Allow or refuse a write against a resolved project id."""
        if not self.config.write_enabled:
            raise WriteRefused(
                f"{operation} refused: the bridge is running read-only. Set "
                f"TESTRAIL_MODE=write in engine/mcp/testrail/.env and restart the "
                f"MCP server to enable writes."
            )
        if not self.config.allowed_projects:
            raise WriteRefused(
                f"{operation} refused: TESTRAIL_ALLOWED_PROJECTS is empty, so no "
                f"project is writable. Add project {project_id} to the allowlist "
                f"if this is genuinely intended."
            )
        if project_id not in self.config.allowed_projects:
            allowed = ", ".join(str(i) for i in sorted(self.config.allowed_projects))
            raise WriteRefused(
                f"{operation} refused: it targets project {project_id}, which is "
                f"not in TESTRAIL_ALLOWED_PROJECTS (currently: {allowed}). This is "
                f"the guard against a bulk push landing in the wrong suite — if "
                f"project {project_id} is the intended target, add it to the "
                f"allowlist deliberately."
            )

    def authorise_delete(self, confirm: Any, operation: str) -> None:
        """Deletes need the feature switch *and* a per-call confirmation phrase.

        Two independent controls, because a delete is the one operation with no
        recovery path. The env switch is the operator's decision; the phrase
        makes it impossible for a caller to delete something while believing it
        was doing an update.
        """
        if not self.config.allow_delete:
            raise WriteRefused(
                f"{operation} refused: deletes are disabled. Set "
                f"TESTRAIL_ALLOW_DELETE=true to enable them, and be aware that "
                f"TestRail deletions cannot be undone."
            )
        supplied = confirm.strip() if isinstance(confirm, str) else ""
        if supplied.upper() != DELETE_CONFIRM_PHRASE:
            raise WriteRefused(
                f'{operation} refused: the `confirm` argument must be exactly '
                f'"{DELETE_CONFIRM_PHRASE}". This is deliberate friction — a '
                f'deleted TestRail case is not recoverable.'
            )

    # -- dry run ------------------------------------------------------------ #

    @property
    def dry_run(self) -> bool:
        return self.config.dry_run

    def dry_run_note(self, endpoint: str, payload: dict[str, Any]) -> dict[str, Any]:
        """The stand-in result for a write that policy allowed but did not send."""
        return {
            "dry_run": True,
            "would_call": endpoint,
            "payload": payload,
            "note": (
                "TESTRAIL_DRY_RUN=true, so nothing was sent to TestRail. The "
                "allowlist check above did pass, so removing the flag would let "
                "this write through unchanged."
            ),
        }

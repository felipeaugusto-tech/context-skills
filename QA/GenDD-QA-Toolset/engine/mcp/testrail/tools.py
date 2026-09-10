#!/usr/bin/env python3
"""Tool definitions and handlers for the TestRail bridge.

Design notes
------------
**Read tools return projections, not raw payloads.** A full TestRail case object
is 40+ keys, most of them nulls and display ordering the agent has no use for.
Returning them raw burns the agent's context and buries the fields that matter.
Every list tool therefore projects to a compact shape, with ``full=true``
available when the whole object is genuinely needed.

**Write tools take our vocabulary, not TestRail's.** ``steps`` accepts the
``{action, expected}`` pairs the QA case-writer skill already produces, and this
module converts them to TestRail's ``custom_steps_separated`` shape
(``{content, expected}``). Making the agent learn TestRail's internal field names
would be a needless source of malformed pushes.

**Custom fields are passthrough, deliberately.** The bridge does not hardcode any
instance's custom schema — it cannot, since that is per-instance configuration.
``custom_fields`` is forwarded as given, with the one check that keys look like
custom fields. Run ``testrail_describe_schema`` first to learn what exists; that
is the intended workflow, and it is why the schema tool is listed first.
"""

from __future__ import annotations

import json
from typing import Any, Callable

from client import TestRailClient, as_list
from guards import DELETE_CONFIRM_PHRASE, Guard

# TestRail custom-field type ids. The raw type_id is always reported alongside
# the label, so a wrong guess here is visible rather than silent.
FIELD_TYPES: dict[int, str] = {
    1: "String", 2: "Integer", 3: "Text", 4: "URL", 5: "Checkbox",
    6: "Dropdown", 7: "User", 8: "Date", 9: "Milestone", 10: "Steps",
    11: "Step Results", 12: "Multi-select",
}

SUITE_MODES: dict[int, str] = {
    1: "single suite",
    2: "single suite + baselines",
    3: "multiple suites",
}

# Compact projection for case lists.
CASE_SUMMARY_KEYS = (
    "id", "title", "section_id", "suite_id", "priority_id", "type_id",
    "template_id", "refs", "is_deleted",
)

# Native add_case/update_case fields the API accepts directly.
NATIVE_CASE_FIELDS = (
    "title", "template_id", "type_id", "priority_id", "estimate",
    "milestone_id", "refs",
)

DEFAULT_CASE_LIMIT = 50
MAX_CASE_LIMIT = 500
MAX_BULK_CASES = 100


class ToolError(RuntimeError):
    """A tool was called with arguments that cannot be honoured."""


# --------------------------------------------------------------------------- #
# argument helpers
# --------------------------------------------------------------------------- #


def _opt_id(args: dict[str, Any], guard: Guard, name: str) -> int | None:
    value = args.get(name)
    if value is None or value == "":
        return None
    return guard.require_id(value, name)


def _req_id(args: dict[str, Any], guard: Guard, name: str) -> int:
    if args.get(name) in (None, ""):
        raise ToolError(f"{name} is required")
    return guard.require_id(args[name], name)


def _limit(args: dict[str, Any], default: int = DEFAULT_CASE_LIMIT) -> int:
    raw = args.get("limit")
    if raw in (None, ""):
        return default
    try:
        value = int(raw)
    except (TypeError, ValueError):
        raise ToolError(f"limit must be an integer, got {raw!r}") from None
    if value < 1:
        raise ToolError("limit must be at least 1")
    return min(value, MAX_CASE_LIMIT)


def describe_suite_mode(mode: int | None) -> str:
    """Label a suite mode for display. Never raises — cosmetic use only."""
    if mode is None:
        return "unknown (instance did not report a usable suite_mode)"
    return SUITE_MODES.get(mode, f"unknown ({mode})")


def require_explicit_suite(guard: Guard, project_id: int, suite_id: int | None) -> None:
    """Refuse to proceed without a suite_id where TestRail needs one.

    In multiple-suite mode, ``get_sections``/``get_cases`` require a ``suite_id``
    and writes must name one. Omitting it does not error — it addresses suite #1 —
    so the caller would get a confident, partial answer about the project. This is
    the one place ``suite_mode`` is a gate rather than a display value, and an
    undeterminable mode is refused for the same reason: it cannot be shown to be
    safe.
    """
    if suite_id is not None:
        return
    mode = guard.suite_mode(project_id)
    if mode is None:
        raise ToolError(
            f"project {project_id} did not report a usable suite_mode, so whether "
            f"suite_id is required cannot be determined. Pass an explicit suite_id "
            f"— call testrail_list_suites to get one — rather than risk addressing "
            f"only the first suite."
        )
    if mode == 3:
        raise ToolError(
            f"project {project_id} is in multiple-suite mode, so suite_id is "
            f"required. Call testrail_list_suites first. Without it TestRail would "
            f"silently address only the first suite."
        )


def _project(item: dict[str, Any], keys: tuple[str, ...], full: bool) -> dict[str, Any]:
    if full:
        return item
    # Drop keys the instance does not populate, so the projection does not
    # invent a wall of nulls.
    return {k: item[k] for k in keys if k in item and item[k] is not None}


def convert_steps(steps: Any) -> list[dict[str, str]]:
    """Convert our ``{action, expected}`` pairs to TestRail's step shape.

    TestRail stores separated steps as ``{"content": ..., "expected": ...}``.
    Our skills, and every human writing a case, say "action" and "expected
    result". Accept both spellings rather than making the caller remember which
    layer they are talking to.
    """
    if not isinstance(steps, list):
        raise ToolError("steps must be a list of {action, expected} objects")
    out: list[dict[str, str]] = []
    for index, step in enumerate(steps, start=1):
        if isinstance(step, str):
            # A bare string is an action with no assertion. Allowed, but it
            # produces a step nobody can pass or fail, so it is worth flagging.
            out.append({"content": step, "expected": ""})
            continue
        if not isinstance(step, dict):
            raise ToolError(
                f"step {index} must be an object with `action` and `expected`, "
                f"got {type(step).__name__}"
            )
        action = step.get("action") or step.get("content") or ""
        expected = step.get("expected") or step.get("expected_result") or ""
        if not str(action).strip():
            raise ToolError(f"step {index} has an empty `action`")
        out.append({"content": str(action), "expected": str(expected)})
    if not out:
        raise ToolError("steps was an empty list; omit it instead")
    return out


def merge_custom_fields(payload: dict[str, Any], custom: Any) -> None:
    """Merge instance-specific custom fields into a payload, in place.

    Two rules, both of which exist because ``custom_fields`` is otherwise an
    unrestricted write into the request body:

    1. Keys must start with ``custom_``. Every TestRail custom field does, so a
       key that doesn't is a guess that TestRail would reject anyway — better to
       say so here, naming the tool that lists the real field names.
    2. A key already set from a dedicated argument cannot be overwritten. Without
       this, ``custom_fields`` could replace the validated ``status_id``, or
       clobber the ``custom_steps_separated`` that ``convert_steps`` just built —
       and the handler would still report the *validated* value in its response,
       so the discrepancy would be invisible.
    """
    if custom is None:
        return
    if not isinstance(custom, dict):
        raise ToolError("custom_fields must be an object of field -> value")
    for key, value in custom.items():
        if not isinstance(key, str) or not key.startswith("custom_"):
            raise ToolError(
                f"custom_fields key {key!r} does not start with 'custom_'. "
                f"TestRail custom fields always do — run "
                f"testrail_describe_schema to see this instance's real field "
                f"names. Native fields go in their own arguments."
            )
        if key in payload:
            raise ToolError(
                f"custom_fields would overwrite {key!r}, which was already set "
                f"from a dedicated argument. Pass it in one place or the other, "
                f"not both — otherwise which value gets written depends on "
                f"merge order."
            )
        payload[key] = value


def build_case_payload(args: dict[str, Any]) -> dict[str, Any]:
    """Assemble an add_case/update_case body from tool arguments."""
    payload: dict[str, Any] = {}

    for key in NATIVE_CASE_FIELDS:
        value = args.get(key)
        if value is not None and value != "":
            payload[key] = value

    if args.get("preconditions"):
        payload["custom_preconds"] = str(args["preconditions"])
    if args.get("steps") is not None:
        payload["custom_steps_separated"] = convert_steps(args["steps"])

    merge_custom_fields(payload, args.get("custom_fields"))

    if not payload:
        raise ToolError(
            "nothing to write: supply at least a title, steps, or one field"
        )
    return payload


# --------------------------------------------------------------------------- #
# read handlers
# --------------------------------------------------------------------------- #


def probe(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    """Confirm the credential works and report the security posture."""
    projects = client.get_collection("get_projects", "projects", max_items=200)
    return {
        "reachable": True,
        "instance": client.config.base_url,
        "auth_mode": client.config.auth_mode,
        "posture": client.config.describe(),
        "writes_possible": client.config.writes_possible,
        "visible_projects": [
            {
                "id": p.get("id"),
                "name": p.get("name"),
                "suite_mode": SUITE_MODES.get(p.get("suite_mode"), p.get("suite_mode")),
                "completed": bool(p.get("is_completed")),
                "writable": p.get("id") in client.config.allowed_projects,
            }
            for p in projects
        ],
        "next_step": (
            "Call testrail_describe_schema with a project_id to get the field map "
            "before generating or pushing any case."
        ),
    }


def list_projects(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    projects = client.get_collection("get_projects", "projects", max_items=_limit(args, 100))
    return [
        {
            "id": p.get("id"),
            "name": p.get("name"),
            "suite_mode": SUITE_MODES.get(p.get("suite_mode"), p.get("suite_mode")),
            "completed": bool(p.get("is_completed")),
            "writable": p.get("id") in client.config.allowed_projects,
        }
        for p in projects
    ]


def describe_schema(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    """The field map: what fields exist, what values are legal, what's required.

    This is the tool to call before generating cases. Pushing a case built from
    guessed field names and invented priority labels is the main way an import
    silently produces garbage, and every value here is read off the live
    instance instead.
    """
    project_id = _opt_id(args, guard, "project_id")

    fields = []
    for field in as_list(client.get("get_case_fields"), "case_fields"):
        raw_configs = field.get("configs")
        configs = [c for c in raw_configs if isinstance(c, dict)] if isinstance(raw_configs, list) else []
        options: list[str] = []
        required_in: list[str] = []
        for config in configs:
            opts = config.get("options") if isinstance(config.get("options"), dict) else {}
            if opts.get("is_required"):
                ctx = config.get("context") if isinstance(config.get("context"), dict) else {}
                required_in.append(
                    "all projects" if ctx.get("is_global")
                    else f"projects {ctx.get('project_ids')}"
                )
            items = opts.get("items")
            if items:
                # TestRail stores dropdown items as "1, Label" lines; keep the label.
                for line in str(items).splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    _, _, label = line.partition(",")
                    options.append((label or line).strip())
                options = list(dict.fromkeys(options))
        type_id = field.get("type_id")
        try:
            type_id = int(type_id)
        except (TypeError, ValueError):
            pass
        fields.append({
            "system_name": field.get("system_name"),
            "label": field.get("label"),
            "type": f"{FIELD_TYPES.get(type_id, 'unknown')} ({type_id})",
            "required_in": required_in or None,
            "options": options[:25] or None,
        })

    out: dict[str, Any] = {
        "priorities": [
            {"id": p.get("id"), "name": p.get("name"), "default": bool(p.get("is_default"))}
            for p in as_list(client.get("get_priorities"), "priorities")
        ],
        "case_types": [
            {"id": t.get("id"), "name": t.get("name"), "default": bool(t.get("is_default"))}
            for t in as_list(client.get("get_case_types"), "case_types")
        ],
        "result_statuses": [
            {"id": s.get("id"), "name": s.get("name"), "label": s.get("label")}
            for s in as_list(client.get("get_statuses"), "statuses")
        ],
        "case_fields": sorted(fields, key=lambda f: str(f["system_name"])),
        "usage": (
            "priority_id / type_id / status_id must be one of the ids above — "
            "never a name you invented. Fields marked required_in must be "
            "populated on every add_case, or the write fails."
        ),
    }

    if project_id is not None:
        mode = guard.suite_mode(project_id)
        out["project"] = {
            "id": project_id,
            "suite_mode": describe_suite_mode(mode),
            "suite_id_required": mode == 3 or mode is None,
            "templates": [
                {"id": t.get("id"), "name": t.get("name"), "default": bool(t.get("is_default"))}
                for t in as_list(client.get(f"get_templates/{project_id}"), "templates")
            ],
            "writable": project_id in client.config.allowed_projects,
        }
    return out


def list_suites(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    project_id = _req_id(args, guard, "project_id")
    suites = client.get_collection(f"get_suites/{project_id}", "suites")
    return {
        "project_id": project_id,
        "suite_mode": describe_suite_mode(guard.suite_mode(project_id)),
        "suites": [
            {"id": s.get("id"), "name": s.get("name"), "description": s.get("description")}
            for s in suites
        ],
    }


def list_sections(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    project_id = _req_id(args, guard, "project_id")
    suite_id = _opt_id(args, guard, "suite_id")
    require_explicit_suite(guard, project_id, suite_id)
    sections = client.get_collection(
        f"get_sections/{project_id}", "sections", suite_id=suite_id
    )
    return {
        "project_id": project_id,
        "suite_id": suite_id,
        "count": len(sections),
        "sections": [
            {
                "id": s.get("id"),
                "name": s.get("name"),
                "parent_id": s.get("parent_id"),
                "depth": s.get("depth"),
            }
            for s in sections
        ],
    }


def list_cases(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    project_id = _req_id(args, guard, "project_id")
    suite_id = _opt_id(args, guard, "suite_id")
    section_id = _opt_id(args, guard, "section_id")
    limit = _limit(args)
    full = bool(args.get("full"))
    require_explicit_suite(guard, project_id, suite_id)

    params: dict[str, Any] = {}
    if suite_id is not None:
        params["suite_id"] = suite_id
    if section_id is not None:
        params["section_id"] = section_id
    for key in ("priority_id", "type_id", "milestone_id"):
        if args.get(key) not in (None, ""):
            params[key] = args[key]
    if args.get("updated_after"):
        params["updated_after"] = args["updated_after"]
    # TestRail's `filter` is a server-side substring match on the title. Using it
    # keeps the paging down instead of fetching everything and filtering here.
    if args.get("title_contains"):
        params["filter"] = str(args["title_contains"])

    cases = client.get_collection(
        f"get_cases/{project_id}", "cases", max_items=limit, **params
    )

    result: dict[str, Any] = {
        "project_id": project_id,
        "returned": len(cases),
        "limit": limit,
        "cases": [_project(c, CASE_SUMMARY_KEYS, full) for c in cases],
    }
    if len(cases) >= limit:
        result["truncated"] = (
            f"Hit the limit of {limit}. Narrow with section_id/title_contains, or "
            f"raise limit (max {MAX_CASE_LIMIT}) — but a large dump will crowd out "
            f"the rest of the context."
        )
    return result


def get_case(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    case_id = _req_id(args, guard, "case_id")
    case = client.get(f"get_case/{case_id}")
    if not isinstance(case, dict):
        raise ToolError(f"case {case_id} did not resolve to a case object")
    if args.get("full"):
        return case
    # Keep every populated field but drop the null noise, so the agent sees the
    # instance's real custom fields without a wall of empties.
    return {k: v for k, v in case.items() if v not in (None, "", [], {})}


def search_cases(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    """Find cases by title substring or ticket reference.

    TestRail's API has no full-text case search. Title matching is pushed to the
    server via ``filter``; ``refs`` matching has no server-side equivalent, so it
    is done here over a bounded scan. The scan ceiling is reported when it is
    hit, because a silently partial search result is worse than a slow one.
    """
    project_id = _req_id(args, guard, "project_id")
    suite_id = _opt_id(args, guard, "suite_id")
    query = str(args.get("query") or "").strip()
    if not query:
        raise ToolError("query is required")
    limit = _limit(args)
    scan_cap = min(int(args.get("scan_limit") or 1000), 5000)
    require_explicit_suite(guard, project_id, suite_id)

    params: dict[str, Any] = {}
    if suite_id is not None:
        params["suite_id"] = suite_id

    needle = query.lower()
    search_refs = bool(args.get("include_refs", True))

    if search_refs:
        pool = client.get_collection(
            f"get_cases/{project_id}", "cases", max_items=scan_cap, **params
        )
        matches = [
            c for c in pool
            if needle in str(c.get("title") or "").lower()
            or needle in str(c.get("refs") or "").lower()
        ]
        scanned = len(pool)
    else:
        pool = client.get_collection(
            f"get_cases/{project_id}", "cases", max_items=limit, filter=query, **params
        )
        matches = pool
        scanned = len(pool)

    out: dict[str, Any] = {
        "query": query,
        "project_id": project_id,
        "scanned": scanned,
        "matched": len(matches),
        "cases": [_project(c, CASE_SUMMARY_KEYS, bool(args.get("full")))
                  for c in matches[:limit]],
    }
    if search_refs and scanned >= scan_cap:
        out["warning"] = (
            f"Scanned the {scan_cap}-case ceiling, so this project may hold "
            f"further matches that were never examined. Treat the result as "
            f"partial: narrow by suite_id/section, or raise scan_limit."
        )
    if len(matches) > limit:
        out["truncated"] = f"{len(matches)} matched; showing the first {limit}."
    return out


def list_runs(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    project_id = _req_id(args, guard, "project_id")
    runs = client.get_collection(
        f"get_runs/{project_id}", "runs", max_items=_limit(args, 25)
    )
    return [
        {
            "id": r.get("id"),
            "name": r.get("name"),
            "suite_id": r.get("suite_id"),
            "is_completed": bool(r.get("is_completed")),
            "passed": r.get("passed_count"),
            "failed": r.get("failed_count"),
            "blocked": r.get("blocked_count"),
            "untested": r.get("untested_count"),
        }
        for r in runs
    ]


def get_results_for_case(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    run_id = _req_id(args, guard, "run_id")
    case_id = _req_id(args, guard, "case_id")
    results = client.get_collection(
        f"get_results_for_case/{run_id}/{case_id}", "results",
        max_items=_limit(args, 20),
    )
    return [
        {
            "id": r.get("id"),
            "status_id": r.get("status_id"),
            "comment": r.get("comment"),
            "defects": r.get("defects"),
            "elapsed": r.get("elapsed"),
            "created_on": r.get("created_on"),
            "created_by": r.get("created_by"),
        }
        for r in results
    ]


# --------------------------------------------------------------------------- #
# write handlers
# --------------------------------------------------------------------------- #


def add_case(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    section_id = _req_id(args, guard, "section_id")
    if not str(args.get("title") or "").strip():
        raise ToolError("title is required and cannot be blank")

    project_id = guard.project_of_section(section_id)
    guard.authorise(project_id, f"add_case into section {section_id}")

    payload = build_case_payload(args)
    endpoint = f"add_case/{section_id}"
    if guard.dry_run:
        return guard.dry_run_note(endpoint, payload)

    created = client.post(endpoint, payload)
    return {
        "created": True,
        "case_id": created.get("id") if isinstance(created, dict) else None,
        "project_id": project_id,
        "section_id": section_id,
        "title": payload.get("title"),
    }


def add_cases(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    """Create several cases in one section.

    TestRail has no bulk-create endpoint, so this loops. It is still worth having
    as one tool: the allowlist check and section resolution happen **once**,
    before any write, so a batch cannot get halfway into the wrong project.

    Default is ``stop_on_error=true``. A partial push is the harder state to
    reason about — you must diff to find out what landed — so the failure is
    surfaced early with everything created so far reported by id.
    """
    section_id = _req_id(args, guard, "section_id")
    cases = args.get("cases")
    if not isinstance(cases, list) or not cases:
        raise ToolError("cases must be a non-empty list of case objects")
    if len(cases) > MAX_BULK_CASES:
        raise ToolError(
            f"{len(cases)} cases exceeds the {MAX_BULK_CASES}-per-call ceiling. "
            f"Split the push — it also keeps the rate limit happy."
        )

    project_id = guard.project_of_section(section_id)
    guard.authorise(project_id, f"add_cases ({len(cases)}) into section {section_id}")

    # Validate every payload before sending any, so a typo in case 9 does not
    # leave cases 1-8 committed.
    payloads = []
    for index, case in enumerate(cases, start=1):
        if not isinstance(case, dict):
            raise ToolError(f"cases[{index}] must be an object")
        if not str(case.get("title") or "").strip():
            raise ToolError(f"cases[{index}] has no title")
        try:
            payloads.append(build_case_payload(case))
        except ToolError as exc:
            raise ToolError(f"cases[{index}] ({case.get('title')!r}): {exc}") from exc

    endpoint = f"add_case/{section_id}"
    if guard.dry_run:
        return {
            "dry_run": True,
            "would_create": len(payloads),
            "would_call": f"{endpoint} (once per case)",
            "payloads": payloads,
            "note": (
                "All payloads validated and the allowlist check passed. Nothing "
                "was sent because TESTRAIL_DRY_RUN=true."
            ),
        }

    stop_on_error = args.get("stop_on_error", True) is not False
    created: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    for index, payload in enumerate(payloads, start=1):
        try:
            response = client.post(endpoint, payload)
            created.append({
                "index": index,
                "case_id": response.get("id") if isinstance(response, dict) else None,
                "title": payload.get("title"),
            })
        except Exception as exc:  # noqa: BLE001 - reported, not swallowed
            failures.append({
                "index": index,
                "title": payload.get("title"),
                "error": client.scrub(str(exc)),
            })
            if stop_on_error:
                break

    out: dict[str, Any] = {
        "project_id": project_id,
        "section_id": section_id,
        "created_count": len(created),
        "created": created,
    }
    if failures:
        out["failed_count"] = len(failures)
        out["failures"] = failures
        out["partial"] = True
        remaining = len(payloads) - len(created) - len(failures)
        out["not_attempted"] = remaining
        out["recovery"] = (
            "Some cases landed and some did not. The created ids above are the "
            "authoritative record of what exists — re-pushing the whole batch "
            "would duplicate them."
        )
    return out


def update_case(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    case_id = _req_id(args, guard, "case_id")
    project_id = guard.project_of_case(case_id)
    guard.authorise(project_id, f"update_case {case_id}")

    payload = build_case_payload(args)
    endpoint = f"update_case/{case_id}"
    if guard.dry_run:
        return guard.dry_run_note(endpoint, payload)

    updated = client.post(endpoint, payload)
    return {
        "updated": True,
        "case_id": case_id,
        "project_id": project_id,
        "fields_written": sorted(payload.keys()),
        "title": updated.get("title") if isinstance(updated, dict) else None,
    }


def add_section(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    project_id = _req_id(args, guard, "project_id")
    name = str(args.get("name") or "").strip()
    if not name:
        raise ToolError("name is required")
    guard.authorise(project_id, f"add_section in project {project_id}")

    suite_id = _opt_id(args, guard, "suite_id")
    require_explicit_suite(guard, project_id, suite_id)

    payload: dict[str, Any] = {"name": name}
    if suite_id is not None:
        payload["suite_id"] = suite_id
    if args.get("parent_id") not in (None, ""):
        parent_id = guard.require_id(args["parent_id"], "parent_id")
        # A new section inherits its parent's suite, so a parent in another
        # project could relocate the write outside the allowlisted project even
        # though project_id itself passed the check. Resolve the parent too.
        parent_project = guard.project_of_section(parent_id)
        if parent_project != project_id:
            raise ToolError(
                f"parent_id {parent_id} belongs to project {parent_project}, not "
                f"project {project_id}. A section inherits its parent's suite, so "
                f"this would place the new section outside the project you named."
            )
        payload["parent_id"] = parent_id
    if args.get("description"):
        payload["description"] = str(args["description"])

    endpoint = f"add_section/{project_id}"
    if guard.dry_run:
        return guard.dry_run_note(endpoint, payload)

    created = client.post(endpoint, payload)
    return {
        "created": True,
        "section_id": created.get("id") if isinstance(created, dict) else None,
        "project_id": project_id,
        "name": name,
    }


def add_run(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    project_id = _req_id(args, guard, "project_id")
    name = str(args.get("name") or "").strip()
    if not name:
        raise ToolError("name is required")
    guard.authorise(project_id, f"add_run in project {project_id}")

    payload: dict[str, Any] = {"name": name}
    suite_id = _opt_id(args, guard, "suite_id")
    require_explicit_suite(guard, project_id, suite_id)
    if suite_id is not None:
        payload["suite_id"] = suite_id
    if args.get("description"):
        payload["description"] = str(args["description"])
    if args.get("milestone_id") not in (None, ""):
        payload["milestone_id"] = guard.require_id(args["milestone_id"], "milestone_id")

    case_ids = args.get("case_ids")
    if case_ids:
        if not isinstance(case_ids, list):
            raise ToolError("case_ids must be a list of integers")
        payload["case_ids"] = [guard.require_id(c, "case_ids[]") for c in case_ids]
        # include_all and case_ids are mutually exclusive in TestRail: sending
        # both makes include_all win and silently ignores the selection.
        payload["include_all"] = False
    else:
        payload["include_all"] = args.get("include_all", True) is not False

    endpoint = f"add_run/{project_id}"
    if guard.dry_run:
        return guard.dry_run_note(endpoint, payload)

    created = client.post(endpoint, payload)
    return {
        "created": True,
        "run_id": created.get("id") if isinstance(created, dict) else None,
        "project_id": project_id,
        "name": name,
        "case_count": len(payload.get("case_ids", [])) or "all",
    }


def add_result_for_case(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    run_id = _req_id(args, guard, "run_id")
    case_id = _req_id(args, guard, "case_id")
    if args.get("status_id") in (None, ""):
        raise ToolError(
            "status_id is required. Call testrail_describe_schema for this "
            "instance's status ids — they are configurable, so 1=Passed is a "
            "convention, not a guarantee."
        )
    status_id = guard.require_id(args["status_id"], "status_id")

    project_id = guard.project_of_run(run_id)
    guard.authorise(project_id, f"add_result_for_case run={run_id} case={case_id}")

    payload: dict[str, Any] = {"status_id": status_id}
    if args.get("comment"):
        payload["comment"] = str(args["comment"])
    if args.get("elapsed"):
        payload["elapsed"] = str(args["elapsed"])
    if args.get("version"):
        payload["version"] = str(args["version"])
    if args.get("defects"):
        payload["defects"] = str(args["defects"])
    # Same guarded merge as the case payloads. A bare payload.update() here would
    # let custom_fields overwrite the status_id validated two lines above, while
    # the response still reported the validated value.
    merge_custom_fields(payload, args.get("custom_fields"))

    endpoint = f"add_result_for_case/{run_id}/{case_id}"
    if guard.dry_run:
        return guard.dry_run_note(endpoint, payload)

    created = client.post(endpoint, payload)
    return {
        "recorded": True,
        "result_id": created.get("id") if isinstance(created, dict) else None,
        "run_id": run_id,
        "case_id": case_id,
        "status_id": status_id,
    }


def delete_case(client: TestRailClient, guard: Guard, args: dict[str, Any]) -> Any:
    case_id = _req_id(args, guard, "case_id")
    # Confirmation is checked before the project lookup so a caller without the
    # phrase gets the friction message rather than a permissions message.
    guard.authorise_delete(args.get("confirm"), f"delete_case {case_id}")
    project_id = guard.project_of_case(case_id)
    guard.authorise(project_id, f"delete_case {case_id}")

    endpoint = f"delete_case/{case_id}"
    if guard.dry_run:
        return guard.dry_run_note(endpoint, {})

    client.post(endpoint, {})
    return {
        "deleted": True,
        "case_id": case_id,
        "project_id": project_id,
        "note": "This is not recoverable through the API.",
    }


# --------------------------------------------------------------------------- #
# registry
# --------------------------------------------------------------------------- #

Handler = Callable[[TestRailClient, Guard, dict[str, Any]], Any]

_ID = {"type": "integer", "description": "Numeric TestRail id."}
_FULL = {
    "type": "boolean",
    "default": False,
    "description": "Return raw TestRail objects instead of the compact projection.",
}
_STEPS = {
    "type": "array",
    "description": (
        "Ordered steps. Converted to TestRail's custom_steps_separated shape. "
        "Every step needs an `expected` — a step with no assertion cannot pass "
        "or fail."
    ),
    "items": {
        "type": "object",
        "properties": {
            "action": {"type": "string", "description": "What the tester does."},
            "expected": {"type": "string", "description": "Observable expected result."},
        },
        "required": ["action", "expected"],
    },
}
_CUSTOM = {
    "type": "object",
    "description": (
        "Instance-specific custom fields, passed through verbatim. Keys must "
        "start with 'custom_'. Run testrail_describe_schema first to learn what "
        "exists — guessed field names are rejected by TestRail."
    ),
    "additionalProperties": True,
}

READ_TOOLS: list[tuple[str, str, dict[str, Any], Handler]] = [
    (
        "testrail_probe",
        "Verify connectivity, authentication and the bridge's security posture. "
        "Lists visible projects and flags which are writable. Call this first "
        "when anything looks misconfigured.",
        {"type": "object", "properties": {}},
        probe,
    ),
    (
        "testrail_describe_schema",
        "Get the field map for this instance: priorities, case types, result "
        "statuses, every case field with its legal options and whether it is "
        "required, plus per-project templates and suite mode. ALWAYS call this "
        "before generating or pushing cases — it is what stops an import from "
        "silently producing malformed cases.",
        {
            "type": "object",
            "properties": {
                "project_id": {**_ID, "description": "Optional: adds project templates and suite mode."},
            },
        },
        describe_schema,
    ),
    (
        "testrail_list_projects",
        "List TestRail projects visible to this credential.",
        {
            "type": "object",
            "properties": {"limit": {"type": "integer", "default": 100}},
        },
        list_projects,
    ),
    (
        "testrail_list_suites",
        "List test suites in a project, with the project's suite mode.",
        {
            "type": "object",
            "properties": {"project_id": _ID},
            "required": ["project_id"],
        },
        list_suites,
    ),
    (
        "testrail_list_sections",
        "List sections (the case folder tree) in a project or suite. Use this to "
        "find the section_id a new case should go into.",
        {
            "type": "object",
            "properties": {
                "project_id": _ID,
                "suite_id": {**_ID, "description": "Required in multiple-suite projects."},
            },
            "required": ["project_id"],
        },
        list_sections,
    ),
    (
        "testrail_list_cases",
        "List existing test cases, compactly. Use section_id or title_contains to "
        "narrow rather than dumping a whole suite into context.",
        {
            "type": "object",
            "properties": {
                "project_id": _ID,
                "suite_id": {**_ID, "description": "Required in multiple-suite projects."},
                "section_id": _ID,
                "title_contains": {
                    "type": "string",
                    "description": "Server-side substring match on the title.",
                },
                "priority_id": _ID,
                "type_id": _ID,
                "updated_after": {
                    "type": "integer",
                    "description": "UNIX timestamp; only cases updated after it.",
                },
                "limit": {"type": "integer", "default": DEFAULT_CASE_LIMIT, "maximum": MAX_CASE_LIMIT},
                "full": _FULL,
            },
            "required": ["project_id"],
        },
        list_cases,
    ),
    (
        "testrail_get_case",
        "Read one test case in full, including its steps and custom fields. Use "
        "this to see how existing cases in the suite are actually written before "
        "generating new ones.",
        {
            "type": "object",
            "properties": {"case_id": _ID, "full": _FULL},
            "required": ["case_id"],
        },
        get_case,
    ),
    (
        "testrail_search_cases",
        "Find cases whose title or refs (ticket key) contain a string. Useful for "
        "checking whether coverage for a ticket already exists before writing a "
        "duplicate. TestRail has no full-text search, so refs matching is a "
        "bounded client-side scan and reports when it was truncated.",
        {
            "type": "object",
            "properties": {
                "project_id": _ID,
                "query": {"type": "string", "description": "Substring, e.g. 'ACC-9279' or 'checkout'."},
                "suite_id": {**_ID, "description": "Required in multiple-suite projects."},
                "include_refs": {
                    "type": "boolean",
                    "default": True,
                    "description": "Also match the refs field. False is faster but title-only.",
                },
                "scan_limit": {"type": "integer", "default": 1000},
                "limit": {"type": "integer", "default": DEFAULT_CASE_LIMIT},
                "full": _FULL,
            },
            "required": ["project_id", "query"],
        },
        search_cases,
    ),
    (
        "testrail_list_runs",
        "List test runs in a project with their pass/fail/blocked counts.",
        {
            "type": "object",
            "properties": {"project_id": _ID, "limit": {"type": "integer", "default": 25}},
            "required": ["project_id"],
        },
        list_runs,
    ),
    (
        "testrail_get_results_for_case",
        "Read recorded results for one case in one run, newest first.",
        {
            "type": "object",
            "properties": {"run_id": _ID, "case_id": _ID, "limit": {"type": "integer", "default": 20}},
            "required": ["run_id", "case_id"],
        },
        get_results_for_case,
    ),
]

WRITE_TOOLS: list[tuple[str, str, dict[str, Any], Handler]] = [
    (
        "testrail_add_case",
        "Create one test case in a section. The target section is resolved to its "
        "project and checked against the write allowlist before anything is sent.",
        {
            "type": "object",
            "properties": {
                "section_id": {**_ID, "description": "Destination section. Find it with testrail_list_sections."},
                "title": {"type": "string", "description": "Behaviour-focused case title."},
                "steps": _STEPS,
                "preconditions": {"type": "string", "description": "Maps to custom_preconds."},
                "priority_id": {**_ID, "description": "Must be an id from testrail_describe_schema."},
                "type_id": {**_ID, "description": "Must be an id from testrail_describe_schema."},
                "template_id": _ID,
                "refs": {"type": "string", "description": "Ticket key(s) for traceability, e.g. 'ACC-9279'."},
                "estimate": {"type": "string", "description": "e.g. '30s', '5m'."},
                "milestone_id": _ID,
                "custom_fields": _CUSTOM,
            },
            "required": ["section_id", "title"],
        },
        add_case,
    ),
    (
        "testrail_add_cases",
        "Create several cases in one section. Every payload is validated and the "
        "allowlist checked before the first write, so a batch cannot get halfway "
        "into the wrong project. Reports created ids even on partial failure.",
        {
            "type": "object",
            "properties": {
                "section_id": _ID,
                "cases": {
                    "type": "array",
                    "description": f"Up to {MAX_BULK_CASES} case objects, same shape as testrail_add_case minus section_id.",
                    "items": {"type": "object"},
                },
                "stop_on_error": {
                    "type": "boolean",
                    "default": True,
                    "description": "Stop at the first failure rather than pressing on.",
                },
            },
            "required": ["section_id", "cases"],
        },
        add_cases,
    ),
    (
        "testrail_update_case",
        "Update fields on an existing case. Only the fields you pass are written; "
        "omitted fields are left alone.",
        {
            "type": "object",
            "properties": {
                "case_id": _ID,
                "title": {"type": "string"},
                "steps": _STEPS,
                "preconditions": {"type": "string"},
                "priority_id": _ID,
                "type_id": _ID,
                "template_id": _ID,
                "refs": {"type": "string"},
                "estimate": {"type": "string"},
                "milestone_id": _ID,
                "custom_fields": _CUSTOM,
            },
            "required": ["case_id"],
        },
        update_case,
    ),
    (
        "testrail_add_section",
        "Create a section (case folder) in a project or suite.",
        {
            "type": "object",
            "properties": {
                "project_id": _ID,
                "name": {"type": "string"},
                "suite_id": {**_ID, "description": "Required in multiple-suite projects."},
                "parent_id": {**_ID, "description": "Nest under an existing section."},
                "description": {"type": "string"},
            },
            "required": ["project_id", "name"],
        },
        add_section,
    ),
    (
        "testrail_add_run",
        "Create a test run. Pass case_ids to scope it to specific cases, or leave "
        "them out to include the whole suite.",
        {
            "type": "object",
            "properties": {
                "project_id": _ID,
                "name": {"type": "string"},
                "suite_id": {**_ID, "description": "Required in multiple-suite projects."},
                "description": {"type": "string"},
                "case_ids": {"type": "array", "items": {"type": "integer"}},
                "include_all": {
                    "type": "boolean",
                    "default": True,
                    "description": "Ignored when case_ids is supplied.",
                },
                "milestone_id": _ID,
            },
            "required": ["project_id", "name"],
        },
        add_run,
    ),
    (
        "testrail_add_result_for_case",
        "Record a result for a case in a run. status_id is instance-specific — get "
        "it from testrail_describe_schema, do not assume 1 means Passed.",
        {
            "type": "object",
            "properties": {
                "run_id": _ID,
                "case_id": _ID,
                "status_id": {**_ID, "description": "From testrail_describe_schema.result_statuses."},
                "comment": {"type": "string", "description": "Evidence: logs, observations, links."},
                "defects": {"type": "string", "description": "Defect key(s), e.g. 'ACC-9301'."},
                "elapsed": {"type": "string", "description": "e.g. '2m 30s'."},
                "version": {"type": "string", "description": "Build or version under test."},
                "custom_fields": _CUSTOM,
            },
            "required": ["run_id", "case_id", "status_id"],
        },
        add_result_for_case,
    ),
]

DELETE_TOOLS: list[tuple[str, str, dict[str, Any], Handler]] = [
    (
        "testrail_delete_case",
        "Permanently delete a test case. Requires TESTRAIL_ALLOW_DELETE=true and "
        f'the exact confirm phrase "{DELETE_CONFIRM_PHRASE}". Not recoverable.',
        {
            "type": "object",
            "properties": {
                "case_id": _ID,
                "confirm": {
                    "type": "string",
                    "description": f'Must be exactly "{DELETE_CONFIRM_PHRASE}".',
                },
            },
            "required": ["case_id", "confirm"],
        },
        delete_case,
    ),
]


def build_registry(config) -> dict[str, dict[str, Any]]:
    """Assemble the tool registry for the configured posture.

    Write tools are **not registered** in read-only mode rather than registered
    and then refused. An agent cannot misuse a tool it was never told about, and
    it saves a pointless round trip and a confusing error.
    """
    selected = list(READ_TOOLS)
    if config.write_enabled:
        selected += WRITE_TOOLS
        if config.allow_delete:
            selected += DELETE_TOOLS

    registry: dict[str, dict[str, Any]] = {}
    for name, description, schema, handler in selected:
        if config.dry_run and name not in {t[0] for t in READ_TOOLS}:
            description = f"[DRY RUN — validated but not sent] {description}"
        registry[name] = {
            "name": name,
            "description": description,
            "inputSchema": schema,
            "handler": handler,
        }
    return registry


def render(result: Any, max_chars: int) -> str:
    """Serialise a handler result for the agent, capped in size.

    The cap exists to protect the agent's context window, not TestRail. A
    truncated payload is marked as truncated in-band, because silently-cut JSON
    would be parsed as complete and quietly believed.
    """
    if isinstance(result, str):
        text = result
    else:
        text = json.dumps(result, indent=2, ensure_ascii=False, default=str)
    if len(text) <= max_chars:
        return text
    return (
        text[:max_chars]
        + f"\n\n[TRUNCATED at {max_chars} characters. This output is INCOMPLETE and "
        f"is not valid JSON — do not parse it as a whole. Re-run with a smaller "
        f"limit or a narrower filter.]"
    )

---
name: testrail-publisher
description: >-
  Take structured test cases already generated through the GenDD engine
  (engine/prompts/06-testcases.md output, e.g. a docs/test-cases-*.md file)
  and publish them: push reviewed cases into TestRail via the first-party MCP
  bridge, AND always generate a CSV suitable for manual TestRail import —
  regardless of whether the live push succeeds. Use this whenever someone
  asks to "upload/push/sync test cases to TestRail," "create a TestRail
  suite/section for these cases," or "give me a CSV for manual import." Do
  NOT use this to generate the test cases themselves (use
  engine/prompts/06-testcases.md / qa-test-case-writer) and do NOT use it to
  record execution results (see engine/connectors/testrail.md's run/result
  tools) — this skill only covers getting case *definitions* into TestRail
  or into an importable file.
---

# TestRail Publisher

Take a finished, human-reviewed GenDD test-case set and get it into TestRail —
live via the MCP bridge when write access allows it, and always as a CSV file
so there's a manual-import fallback and an offline record either way.

This skill is the **publishing step**, not the generation step. It assumes
`engine/prompts/06-testcases.md` (or `qa-test-case-writer`) already produced
the cases and a human has reviewed them (core principle 4, human-in-the-loop —
never push unreviewed cases). Full TestRail tool semantics, concept mapping,
and anti-patterns live in [`engine/connectors/testrail.md`](../../../engine/connectors/testrail.md)
— read it if this is the first TestRail task this session. This skill adds
the workflow sequencing and the specific failure modes hit in practice that
the connector doc doesn't cover.

## Step 0 — Load the input and confirm it's reviewed

Read the source test-case file (e.g. `docs/test-cases-YYYY-MM-DD.md`). Confirm
with the user that these cases have been reviewed and are ready to publish —
if there's any doubt, ask before proceeding. Note the ticket/story reference
(e.g. `ACC-9279`) that every case's `refs` field will carry.

## Step 1 — Check TestRail configuration before generating anything

Run, in this order:

1. `testrail_probe` — confirms reachability, auth, and **`writes_possible`**.
   If `writes_possible: false`, write tools are not registered (dry-run/
   read-only posture) — skip straight to Step 5 (CSV-only) and say so plainly.
   Never treat a dry-run echo as a completed push.
2. `testrail_describe_schema` (with the target `project_id`) — get the real
   `priorities`, `case_types`, `result_statuses`, and every `case_fields`
   entry with its `required_in` flag. **Never invent or assume an id/label
   mapping** — re-derive it every session, this instance's config can change.
3. `testrail_list_suites` for the project — note `suite_mode`. In
   **multiple-suite** mode, `suite_id` is mandatory on section/case calls and
   there is no tool to create a new suite in this bridge — target an
   *existing* suite (ask the user which one if unclear) and create a
   **section** inside it instead.
4. Confirm the target project is actually writable per `testrail_probe`'s
   `visible_projects` list — a project can appear in the schema/suite calls
   while still being outside the write allowlist.

### Resolving required custom fields — ask, don't guess

`describe_schema`'s `case_fields` marks some fields `required_in: ["all
projects"]`. These vary per instance and are **not derivable from the test
case content**. For each required field:

- If the test cases already imply a clear value (e.g. `refs` = the ticket
  key), fill it.
- If it's a plain dropdown/business field with no basis in the cases (a team
  code, an "Amazon_Impact"-style toggle, etc.), **ask the user** — present
  the real options from the schema. Do not default silently on a field that
  carries real business meaning.
- **Dropdown custom fields may take a numeric option index, not the label
  string.** If the user gives you a number for a dropdown option, that's very
  likely how this instance's dropdown fields are actually stored — pass it
  through as given rather than substituting a label, but say plainly in your
  summary which label position you assumed it corresponds to, since that
  mapping isn't confirmed by the schema response itself.
- If a required field silently doesn't appear when you read a pushed case
  back (see Step 4), that's a signal the field may not actually be enabled
  for this project/template despite showing in the schema — flag it, don't
  re-guess a different value and retry.

## Step 2 — Check for existing coverage

Run `testrail_search_cases` with the ticket key before writing anything.
Duplicated coverage is worse than no coverage. Report what exists and ask
before proceeding if there's a meaningful overlap.

## Step 3 — Map GenDD fields to the schema

Translate the source file's fields using the real ids from Step 1, not a
hardcoded table:

| GenDD field | TestRail field | Notes |
|---|---|---|
| Test Case ID / Title | `title` | |
| Priority (P0/P1/P2/P3 or High/Medium/Low) | `priority_id` | Map to *this instance's* priority names — order and count vary |
| Test Type (Functional/Security/Integration/Regression/…) | `type_id` | Pick the closest real option; note where GenDD's type has no exact match (e.g. "Integration" often maps to "End-To-End") |
| Preconditions | `preconditions` (→ `custom_preconds`) | |
| Steps (action + expected) | `steps` (→ `custom_steps_separated`) | Every step **must** carry an `expected` — a step with no assertion can't pass/fail |
| Linked Scenario / traceability note | Fold into `preconditions` or a text custom field if no dedicated field exists | Don't drop it silently |
| Ticket/story | `refs` | Required on every case |
| Required business fields (Step 1) | Their `custom_*` field | Resolved per Step 1, never invented |

## Step 4 — Create the section and push, then verify

1. `testrail_add_section` (single-suite: `project_id` only; multi-suite: add
   `suite_id`) — name it after the ticket/feature, e.g. `"ACC-9279 -
   Identity Verification Results"`.
   **Use a plain hyphen, not an em dash or other non-ASCII punctuation, in
   any text sent through this bridge.** An em dash sent through this
   connector has been observed coming back corrupted into garbled HTML
   entities (e.g. `—` → `â€"`-shaped mojibake) in both section names and case
   step text. There is no `update_section` tool to fix a section name after
   the fact, so getting this right on creation matters more for the section
   than for cases (which *can* be patched). Apply the same plain-ASCII-
   punctuation rule to every string field in every case, not just the section.
2. `testrail_add_cases` (up to 100 per call) with `stop_on_error: false` —
   it validates the whole batch against the write allowlist before the first
   write, and reports created ids even on partial failure. Those created ids
   are authoritative; don't re-push the whole batch on a partial failure,
   only retry what's missing.
3. **Verify, don't assume.** `testrail_get_case` (with `full: true`) on at
   least one created case and check:
   - Every required custom field actually appears in the response (see the
     "silently doesn't appear" note in Step 1).
   - No punctuation corruption made it into `custom_steps_separated` or
     other text fields.
   - `priority_id`/`type_id`/`refs` match what was intended.
4. If corruption or a mismatch is found, use `testrail_update_case` to fix
   the specific affected cases (it accepts the same `steps`/`preconditions`/
   field shape as `add_case` — pass the corrected full value, not a diff).
   Re-verify after fixing.

## Step 5 — Always generate the CSV, regardless of push outcome

Whether or not Step 4 ran (or succeeded), produce a CSV for manual import.
This is not merely a fallback — it's parallel output for tracking and
flexibility, even after a successful live push.

**Format:** one row per case, columns matching this project's actual template
(read from `describe_schema`'s `templates`, typically the step-based
`"Test Case (Steps)"` template):

```
Title, Section, Type, Priority, References, Preconditions,
Step 1, Expected Result 1, Step 2, Expected Result 2, ... (up to the max step count in this batch),
<one column per required/relevant custom field>
```

Rules:
- **Use real label text** for `Type`/`Priority` (e.g. `"Critical"`, not `4`)
  — a human importing manually reads labels, not ids. If a dropdown custom
  field's value was resolved as a numeric index (Step 1), write the label at
  that position instead of the bare number, and note the mapping assumption
  to the user.
- Use plain hyphens instead of em dashes here too — consistency with what
  actually landed in TestRail (if it did), and general CSV/tool portability.
- Wrap any field containing a comma, quote, or newline in double quotes,
  doubling embedded quotes — standard CSV escaping. Multi-line preconditions
  are valid inside a quoted field.
- Pad unused step columns with empty strings so every row has the same
  column count as the header (max step count across the batch).
- After writing, verify the CSV parses cleanly with the expected column count
  on every row before handing it off (e.g. via a quick `Import-Csv`/`csv`
  round-trip) — a silently malformed row is worse than no CSV.

Save it alongside the source test-case file (e.g.
`docs/test-cases-YYYY-MM-DD.csv`) and tell the user where it is.

## Step 6 — Report

State plainly, for this run:
- Whether a live push happened, and if not, why (no write access / dry-run /
  refused by policy / project not writable) — never imply a push occurred if
  it didn't.
- Section id and case ids created (or updated), if any.
- Any corruption found and fixed, and anything that could **not** be fixed
  (e.g. a section name, since there's no update tool for it) — tell the user
  to fix it manually if so.
- Any required field whose value was assumed/asked rather than derived, and
  what was assumed.
- Where the CSV was saved and what it contains.

## Hard rules

1. Never report a dry-run or `writes_possible: false` response as a
   completed push.
2. Never push cases that haven't been confirmed reviewed.
3. Never guess a required custom field's value when it carries real business
   meaning — ask.
4. Never invent a `priority_id`/`type_id`/`status_id`/custom field name —
   always resolve from `testrail_describe_schema` this session.
5. Never assume a non-ASCII punctuation mark (em dash, curly quotes, etc.)
   survives the bridge intact — use plain ASCII equivalents in text sent to
   TestRail, and verify a sample case after pushing.
6. Always produce the CSV, even after a fully successful push — it's for
   tracking/flexibility, not just a fallback.
7. Never batch-delete or silently overwrite existing TestRail cases while
   doing this — if `testrail_search_cases` shows existing coverage, stop and
   ask how the user wants to handle it (see `engine/connectors/testrail.md`).
8. If `REFUSED BY POLICY` or `WRITE OUTCOME UNKNOWN` comes back, follow
   `engine/connectors/testrail.md`'s error reference — don't retry blindly.

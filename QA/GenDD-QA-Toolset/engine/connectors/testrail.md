# TestRail Connector

> **Purpose:** Agent-consumable instructions for reading Accurate's existing test
> suite and pushing AI-generated cases and results to TestRail.
> **When to load:** The agent needs suite context before writing cases, or has
> reviewed cases ready to push.
> **Backed by:** the first-party MCP bridge in `engine/mcp/testrail/`. Setup and
> security posture: [`engine/mcp/testrail/README.md`](../mcp/testrail/README.md).

---

## When to Use

Use this connector when:

- The project's `Context.md` §1 names TestRail as the test-case-management tool
- The agent needs to know how the **existing** suite is written before generating
  new cases (this is the common case, and it is a read-only need)
- Reviewed cases need to land in TestRail
- Execution results need recording against a run

Do NOT use for:

- Projects on Xray or Zephyr — see `xray.md`
- Pushing cases that have not been human-reviewed
- Lightweight/informal QA where markdown cases are the deliverable
- Exploratory testing (capture evidence directly; no TestRail run needed)

**If the bridge is not configured, say so and export to a file instead.** Do not
describe a file export as though it were a push. `Context.md` §1 is the source of
truth for whether a push path exists.

---

## Hard rules

1. **Call `testrail_describe_schema` before generating or pushing any case.**
   Priorities, case types, result statuses, templates and custom fields are all
   per-instance configuration. `priority_id: 4` is not "Critical" everywhere, and
   `status_id: 1` is not universally "Passed". Never send a value you did not
   read from the schema.
2. **Never invent a custom field name.** `custom_fields` keys must exist on the
   instance. If our concept has nowhere to live, fold it into a text field and
   say so — do not silently drop it.
3. **Search before you write.** Run `testrail_search_cases` on the ticket key.
   Duplicated coverage is worse than no coverage: it splits maintenance and makes
   the suite untrustworthy.
4. **A refusal is final.** `REFUSED BY POLICY` means the write targeted a project
   outside the allowlist. Do not retry, do not look for another route, do not
   pick a different section to get around it. Report it and stop.
5. **Never report a dry run as a completed push.** If the response contains
   `"dry_run": true`, nothing reached TestRail.
6. **`WRITE OUTCOME UNKNOWN` means verify, not retry.** The write may have landed.
   Read the state back before re-sending anything.
7. **Every case gets a `refs` value.** Traceability to the ticket is the point.

---

## Concept Mapping

| QA-GenDD concept | TestRail equivalent | Notes |
|---|---|---|
| Test case | Case in a section | |
| Case title | `title` | Behaviour-focused |
| Steps (action + expected) | `custom_steps_separated` | The `steps` argument converts for you — pass `{action, expected}` |
| Preconditions | `custom_preconds` | Via the `preconditions` argument |
| Ticket / story | `refs` | e.g. `ACC-9279` |
| Risk tier (T0–T3) | `priority_id` | **Map via the schema.** Do not assume an ordering |
| Test type | `type_id` | From the schema |
| Coverage split | Test run | `testrail_add_run` |
| Execution evidence | Result `comment` | Attach logs, observations, links |
| Defect | Result `defects` | Ticket key(s) |
| Confidence label, coverage tier, objective | Usually no native field | Check the schema for a custom field; otherwise fold into a text field |
| Feature ID (`Context.md` §2) | Section, or a custom field | Confirm which convention the suite already uses |

`priority_id`, `type_id` and `status_id` are **always** resolved from
`testrail_describe_schema`. There is no default mapping in this document on
purpose — writing one down would invite exactly the guessing that produces
malformed imports.

---

## Reading the suite

The point of reading first is to match the conventions that already exist, rather
than importing a second, differently-shaped suite alongside the real one.

```
testrail_probe                  # posture, and which projects are writable
testrail_list_projects
testrail_list_suites            # note the suite mode
testrail_list_sections          # find where cases belong
testrail_list_cases             # narrow by section or title
testrail_get_case               # read 2-3 in full to learn house style
testrail_describe_schema        # the field map
```

**Read a handful of real cases in full before writing any.** Look for:

- How much detail a step carries, and how many steps a typical case has
- Whether `refs` holds the parent story or the sub-task key
- Whether preconditions are used at all, or folded into step 1
- Section naming and nesting depth — new cases should follow it
- Which custom fields are actually populated, versus merely configured

In a **multiple-suite** project, `suite_id` is required on section and case
reads. The tools will refuse rather than quietly return suite #1.

Keep reads narrow. `testrail_list_cases` on a large project will fill the context
window with case titles and leave no room for the work.

---

## Pushing cases

**Preconditions for a push:**

- [ ] The cases have been human-reviewed
- [ ] `testrail_describe_schema` has been called this session
- [ ] Required fields are populated
- [ ] `testrail_search_cases` shows no existing coverage for the ticket
- [ ] The target `section_id` is confirmed, not guessed
- [ ] Every case has `refs`

```jsonc
// testrail_add_case
{
  "section_id": 500,
  "title": "Order submission creates exactly one charge",
  "refs": "ACC-9279",
  "priority_id": 4,           // from the schema
  "type_id": 1,               // from the schema
  "preconditions": "User logged in, items in cart, gateway in test mode",
  "steps": [
    {"action": "Navigate to checkout", "expected": "Checkout loads with order summary"},
    {"action": "Click Place Order",    "expected": "Loading indicator appears"},
    {"action": "Inspect gateway records", "expected": "Exactly one charge exists"}
  ]
}
```

Use `testrail_add_cases` for a set. It validates every payload and checks the
allowlist **before** the first write, so a batch cannot get halfway into the
wrong project. On a partial failure it returns the ids that were created — those
are authoritative, and re-pushing the whole batch would duplicate them.

**Every step needs an `expected`.** A step with no assertion cannot pass or fail,
which makes the case unrunnable.

---

## Recording execution results

```
testrail_add_run                 # scope with case_ids, or include the whole suite
testrail_add_result_for_case     # one call per case
```

`status_id` comes from `testrail_describe_schema.result_statuses`. Instances
rename and add statuses, so the ids are not portable.

| Outcome | What to record |
|---|---|
| Pass | Status id for Passed. A comment with the evidence — what was observed, not just "worked" |
| Fail | Status id for Failed. Comment with the failure evidence. Defect key in `defects`. Create the defect via `engine/prompts/09-defects.md` |
| Blocked | Status id for Blocked. Comment naming the blocker (environment, dependency, data) |

Record results as they are known. A run left half-untested is indistinguishable
from a run nobody executed.

---

## Traceability

```
Story / requirement (ACC-####)
    └── Case in TestRail (refs = ACC-####)
        └── Test run
            ├── Result (Passed / Failed / Blocked)
            │   └── Evidence in the comment
            └── Defect key in `defects`
                └── Linked back to the story
```

**Checklist**

- [ ] Every generated case has `refs` pointing at its ticket
- [ ] Every case maps to a Feature ID from `Context.md` §2
- [ ] Every result carries evidence in its comment
- [ ] Every failure has a defect key
- [ ] AI-generated cases are marked as such — a custom field if one exists,
      otherwise a consistent note in a text field
- [ ] Risk tier is recorded as `priority_id` per the schema mapping

---

## Integration with the QA workflow

| Workflow step | TestRail action |
|---|---|
| Step 1 (Feature intake) | `testrail_search_cases` — does coverage already exist? |
| Step 2 (Brownfield delta) | `testrail_list_cases` / `testrail_get_case` — what does the suite already assert? |
| Step 4 (Create tests) | Generate locally. Do not push yet |
| Step 5 (Risk + confidence) | Map tiers to `priority_id` from the schema |
| Step 5 Option D (Push) | `testrail_add_cases`, after human review |
| Step 7 (Execution) | `testrail_add_run`, then `testrail_add_result_for_case` |
| Step 8 (Evidence + triage) | Results with evidence comments; defects via prompt 09 |
| Step 11 (Release readiness) | `testrail_list_runs` for pass/fail counts as evidence |

---

## Anti-Patterns

| Avoid | Do instead |
|---|---|
| Guessing `priority_id` / `type_id` / `status_id` | Read them from `testrail_describe_schema` |
| Inventing a custom field name | Check the schema; fold into a text field and say so |
| Pushing generated cases without review | Review first, then push |
| Pushing without `refs` | Always link to the ticket |
| Retrying after `REFUSED BY POLICY` | Report the refusal and stop |
| Re-sending after `WRITE OUTCOME UNKNOWN` | Read the state back, then decide |
| Reporting a `dry_run` response as a push | Say clearly that nothing was sent |
| Dumping a whole suite into context | Narrow by section, title or ticket |
| Creating a case when one already covers the behaviour | Update the existing case |
| Recording Passed with no evidence | Put the observation in the comment |
| Describing a file export as a push | Name it as an export |
| Steps with no expected result | Every step gets an assertion |

---

## Error reference

| Response begins | Meaning | Action |
|---|---|---|
| `REFUSED BY POLICY` | Target project is not allowlisted | Stop. Report it. Do not reroute |
| `WRITE OUTCOME UNKNOWN` | Ambiguous write failure, not retried | Read state back. Do not re-send |
| `Invalid request` | Bad arguments or a nonexistent id | Fix the call |
| `Authentication failed` | Credential, or API disabled | Stop. This is a setup problem |
| `Rate limited` | Survived the retries | Wait, then narrow the query |
| `TestRail unreachable` | Network or server error | May succeed on retry |
| `unknown tool … running read-only` | Write tools not registered | Export to a file instead |

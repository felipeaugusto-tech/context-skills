---
name: test-gap-analyzer
description: >-
  Find where a codebase is untested and rank the gaps by risk using evidence
  rather than intuition — test-file inventory, coverage data where a tool
  exists, git change frequency, past bug-fix churn, dependency fan-in, and
  data-mutation signals. Produces a prioritized gap report where each gap is
  a concrete test scenario with a layer, an effort size, and the reason it
  matters. Also flags tests that exist but cannot fail (no assertions,
  mock-only, snapshot-only, skipped, focused), which coverage tools count as
  covered. Use it whenever someone asks "where are our test gaps," "are we
  confident in our testing," "what tests should we add," "audit our test
  coverage," "we keep shipping regressions in X," "what should QA cover
  before this release," or wants test work scoped for sprint planning or
  after a production incident. Do NOT use for writing the tests themselves,
  generating manual test cases from a story (use qa-test-case-writer), or
  authoring acceptance criteria (use requirements-enhancer).
---

# Test Gap Analyzer

Answer "where are we exposed?" with evidence. The failure mode to design against is
the plausible audit: a tidy report recommending tests for whatever happens to be
visible, ranked by nothing in particular, which reads well and misses the module
that has been quietly patched eleven times this quarter.

Three principles follow:

- **A gap is only a gap if something could break.** Untested code that never
  changes and breaks nothing is not the priority. Untested code that changes every
  sprint and sits on the payment path is.
- **Coverage percentage is not coverage.** A line executed by a test with no
  meaningful assertion is counted covered and protects nothing. These tests are
  worse than missing ones, because they buy false confidence.
- **Recommendations must be scenarios, not areas.** "Improve payment test coverage"
  cannot be picked up. "Assert that a declined card leaves no order row" can.

## Step 0 — Load context and establish what matters

Read the project's own knowledge before forming an opinion:

```bash
ls docs/context/ docs/standards/ 2>/dev/null
find . -maxdepth 3 -iname "testing.md" -o -iname "context.md" -o -iname "architecture.md" \
  2>/dev/null | grep -v node_modules
ls AGENTS.md CLAUDE.md CONTRIBUTING.md 2>/dev/null
```

| Source | Contributes |
|---|---|
| `testing.md` or testing standards | The project's own MUST/SHOULD/MAY levels, layer definitions, naming conventions |
| `context.md` | Critical business flows, personas, tenancy and compliance scope |
| `architecture.md` | Service boundaries and integrations — where contract tests belong |
| Incident or postmortem notes | The most valuable input available: where it has already broken |

If the project defines testing standards, **rank against those rather than generic
best practice.** A team that has decided E2E tests are reserved for three critical
journeys should not receive a report recommending forty.

Then ask what the analysis cannot derive:

- **Critical business flows** — which paths lose money, data, or trust when they
  break. Auth, payments, data sync, and anything with a compliance obligation.
- **Known problem areas** — where bugs recur. Say plainly that git history will
  also be mined for this, so they need only name what history would not show.
- **Integrations** and whether each is mockable or must be hit live.
- **Scope** — whole repo, or one area. A focused analysis of the payment path is
  usually worth more than a shallow pass over everything.

## Step 1 — Inventory what exists

### Step 1a — Check TestRail for existing manual coverage first

Automated tests are only half the inventory. Before inventorying code, check
whether manual/QA coverage already exists in TestRail — a gap that "exists" as
an untested code path but already has a maintained manual case is a different
finding than a true gap.

- **If the `testrail` MCP tools are not visible**, the bridge likely isn't
  registered or the server never started — see `engine/mcp/testrail/README.md`
  and `engine/connectors/testrail.md` for setup. Two setup gotchas found in
  practice:
  - `.mcp.json` at the repo root must use `command: "python"` on Windows, not
    `"python3"` (the config's own comment says this, but it's easy to copy the
    example verbatim and miss it — `python3` is a POSIX-only shim).
  - MCP servers load their tool list at startup. Editing `.mcp.json` or the
    bridge's `.env` requires **restarting the client** before new tools appear
    — there is no hot reload.
  - Confirm which mode you're in: this bridge defaults to read-only, and can
    also run in `TESTRAIL_DRY_RUN=true` even when write tools are exposed.
    Never report a dry-run echo as a completed write.
- **Finding the right project/suite:** `testrail_list_projects` →
  `testrail_list_suites` (required for any multi-suite project) →
  `testrail_list_sections`. There is no cross-project search — you must run
  `testrail_search_cases` once per `(project_id, suite_id)` pair, which for an
  org with several multi-suite projects can mean a dozen-plus calls to cover
  "does any coverage exist for this ticket anywhere."
- **TestRail has no full-text search.** `testrail_search_cases` does a bounded
  client-side scan of titles and `refs` up to `scan_limit` (default 1000). A
  response with `"warning": "Scanned the N-case ceiling..."` means the result
  is **partial** — raise `scan_limit` and re-run before concluding "no
  coverage," especially in large regression suites.
- **Bare ticket numbers produce false positives.** Searching a component like
  `9279` alone will match unrelated tickets that happen to share the digits
  (`ATAP-9279`, `GLOBAL-9279`, etc.) under a different prefix. Search the full
  key (`ACC-9279`) as the primary query, and treat a digits-only match as a
  lead to verify, not a hit.
- **Call `testrail_describe_schema` before interpreting `priority_id` /
  `type_id`** on any case you do find — these are per-instance and not
  portable across projects.
- **Zero results across every project/suite is itself the finding**, not a
  tool failure — say so plainly in the gap report ("no TestRail coverage
  exists for `ACC-9279`; this is a full manual-coverage gap, not a partial
  one") rather than silently falling back to the code-only inventory.
- This bridge is typically read-only — it cannot create the missing cases for
  you. Report the gap and hand off to `engine/connectors/testrail.md` /
  `qa-test-case-writer` for authoring, rather than implying a push happened.

### Step 1b — Inventory the codebase

```bash
python3 scripts/analyze_test_gaps.py . --format table
```

The script inventories test files, maps them to source files by the project's
naming conventions, and reports per source file: whether a test maps to it, size,
git change frequency, bug-fix churn, and dependency fan-in. It also flags weak
tests. Point it at a subdirectory for a focused pass, and pass `--coverage` with a
coverage report to merge real execution data.

**Run the project's coverage tool if one exists** — this is the difference between
measurement and inference:

```bash
npx jest --coverage --coverageReporters=json-summary   # → coverage/coverage-summary.json
pytest --cov --cov-report=json                          # → coverage.json
go test ./... -coverprofile=cover.out
```

If no coverage tooling exists, say so explicitly and note that the analysis is
based on file mapping and risk signals rather than execution data. That is a
weaker but still useful basis — do not imply otherwise, and consider whether
"install a coverage tool" is itself the top recommendation.

## Step 2 — Find the tests that cannot fail

Before looking for missing tests, audit the ones that exist. This category is
invisible to every coverage tool and routinely explains "we had tests for that."

The script flags candidates; confirm by reading them. The taxonomy and what to do
about each is in `references/test-gap-method.md`:

| Pattern | Why it protects nothing |
|---|---|
| No assertions | Executes code, asserts nothing. Passes as long as nothing throws. |
| Asserts only on mocks | Verifies the test's own doubles, not the system. Passes when the real integration is broken. |
| Snapshot-only | Detects change, not correctness. A wrong snapshot committed once is wrong forever. |
| Skipped or focused | `.skip` never runs; `.only` silently disables its whole siblings. |
| Tautological | `expect(true).toBe(true)`, or asserting the value just assigned. |
| No failure path | Only the happy path. The bug will be in the other branch. |

**Report these alongside missing tests, and often above them.** A test suite with
sixty of these at 80% reported coverage is in a worse position than one with honest
40%, because nobody knows to be careful.

## Step 3 — Determine what should exist

For each area in scope, derive the tests that ought to exist from the code and the
context — not from a generic checklist. `references/test-gap-method.md` carries
per-concern heuristics; the shape of the reasoning:

- **Every branch that changes an outcome** deserves a case, especially failure
  branches. Error paths are where coverage is thinnest and incidents come from.
- **Every integration boundary** needs its failure modes exercised: timeout,
  unavailable, malformed response, partial success. A contract test where both
  sides are owned.
- **Every state transition** in a multi-step or resumable flow, including re-entry.
- **Every authorization rule and tenancy boundary**, expressed as a denial test.
  Positive-only auth tests are the most common serious gap, because a broken check
  passes them all.
- **Every past bug**, as a regression test that fails against the old behavior.
  Git history names these for you.

Assign a layer deliberately — unit for logic and branching, integration for
boundaries and persistence, E2E for a handful of journeys. **Do not default to
E2E.** E2E tests are slow, flaky, and expensive to maintain; recommending them
broadly is how a test strategy dies.

## Step 4 — Build the gap matrix

One row per gap. Every row must be actionable on its own:

```markdown
| # | Area | Gap (as a scenario) | Layer | Risk | Effort | Why it matters |
|---|---|---|---|---|---|---|
| 1 | Payments | Declined card leaves no order row and no vault entry | Integration | High | M | `charge()` changed 14× in 6mo, 3 fix commits, no test asserts rollback |
| 2 | Auth | User without AdminWrite receives 403 from POST /api/orders | Unit | High | S | 6 positive auth tests, zero denial tests — a removed check passes all 6 |
| 3 | Sync | Partial batch failure leaves no duplicate rows on retry | Integration | Med | L | Retry path has no test; 2 incidents referenced this file |
```

Risk comes from Step 1's signals, not from feel. State the evidence in the last
column — that is what turns a recommendation into an argument, and it is what
survives contact with a sprint-planning meeting.

## Step 5 — Prioritize honestly

Order by risk-adjusted value, not count. A short list that gets built beats a long
one that gets admired.

- **Top five, named.** If the team does nothing else, these five. Include why each
  outranks the rest.
- **Quick wins** — low effort, real risk reduction. Denial tests for existing auth
  checks are usually the cheapest genuine risk reduction available.
- **Deliberately deferred**, with reasons. A report that recommends everything has
  prioritized nothing.
- **Effort as sizes, not hours** — S/M/L with a stated basis (fixtures needed, is
  the integration mockable, does test infrastructure exist yet). Invented hour
  estimates get treated as commitments.

Where the honest recommendation is infrastructure rather than tests — no test
runner, no way to mock the payment gateway, no CI — say that first. Recommending
forty tests into a repo where tests cannot run is a wasted report.

## Step 6 — Report and hand off

**Default to one report**, `docs/test-gap-analysis-YYYY-MM-DD.md`, containing:
scope and method (including whether coverage data was available **and whether
TestRail was reachable and searched**), the weak-test findings, the gap matrix,
the top five, deferred items with reasons, and open questions. Date it — a gap
analysis is a snapshot and will be wrong in a quarter.

Method section must state explicitly which projects/suites in TestRail were
searched (or that the bridge wasn't configured, if so) — "no manual coverage
found" is a claim about search scope, and the scope should be checkable.

Offer the split into separate inventory, matrix, coverage-map, recommendation, and
roadmap documents only if asked. Five documents mean five things to keep current,
and in practice they diverge; the roadmap outlives the analysis it came from.

Also offer the machine-readable form: `python3 scripts/analyze_test_gaps.py . --format json`
feeds a dashboard or a re-run comparison, and re-running after a sprint shows
whether the gaps actually closed.

Then name the next step rather than doing it: write the top-priority tests, file
the gap rows as tickets (one per row — they are already scoped), or re-run after
the sprint to measure movement. **Never write tests as part of the analysis unless
asked**, and never file tickets without confirmation.

## Hard rules

1. Rank by evidence — coverage, churn, bug-fix history, fan-in, blast radius. Never
   by intuition presented as analysis.
2. State whether coverage data was available. Inference from file mapping is a
   weaker basis and must be labeled as such.
3. Never equate coverage percentage with protection. Audit for tests that cannot
   fail, and report them alongside the missing ones.
4. Every gap is phrased as a concrete scenario, never an area or a percentage target.
5. Assign layers deliberately; never default to E2E.
6. Rank against the project's own testing standards where they exist.
7. Effort as sizes with a stated basis, never invented hours.
8. Prioritize — a report recommending everything has recommended nothing.
9. When test infrastructure is missing, that is the first recommendation.
10. Never write tests or file tickets as part of the analysis without being asked.
11. Date the report and say what would invalidate it.
12. Check TestRail (or the project's test-case-management tool) for existing
    manual coverage before concluding a gap is unaddressed — state which
    projects/suites were searched, and never report a partial or ceiling-limited
    search as an exhaustive "no coverage" finding.

## Bundled files

- `scripts/analyze_test_gaps.py` — test inventory, source-to-test mapping, risk
  signals from git (churn, bug-fix churn, fan-in, size), weak-test detection, and
  optional coverage merging. Table or JSON output. No dependencies.
- `references/test-gap-method.md` — the risk model and its formula, the weak-test
  taxonomy with remedies, per-concern heuristics for what should exist (auth,
  payments, integrations, data sync, migrations, multi-tenancy), layer selection,
  and effort sizing.

Related, not bundled: `engine/mcp/testrail/README.md` (bridge setup) and
`engine/connectors/testrail.md` (agent-facing TestRail usage rules) — read
before Step 1a if TestRail is this project's test-case-management tool.

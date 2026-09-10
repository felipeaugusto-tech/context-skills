---
name: qa-test-case-writer
description: >-
  Turn a user story or ticket into verified, structured manual test cases —
  system-aware, ready for human review and optional export to a test-management
  tool. Use this skill whenever a QA engineer or PM wants to generate manual
  test cases, check whether a story is ready for QA, review acceptance criteria
  for testability, do a brownfield delta check, work out state-transition or
  resume/re-entry coverage, decide component-vs-E2E layering, or export/push
  cases as JSON/CSV/Gherkin or to Zephyr/TestRail/Xray. Trigger on phrases like
  "generate test cases for TICKET-123," "is this story ready for QA," "are these
  ACs testable," "what tests should I write," "review my test cases," "flag the
  gaps before we groom this," or a pasted story asking what to test. This skill
  is project-agnostic — it reads project-specific facts from a companion
  Context.md and never invents them. Do NOT use for writing automated test code,
  performance/load testing scripts, or authoring the story/PRD itself.
---

# QA Test-Case Writer

Take a QA engineer from a user story or ticket to verified, structured manual
test cases: system-aware, ready for human review, and optionally exportable to a
test-management tool.

**This skill is the reusable engine. It is project-agnostic by design.** All
project-specific facts — feature taxonomy, tooling stack, environment
constraints, brownfield/system reference, confirmed product decisions, open
contradictions, readiness flags, personas, and test-data fixtures — live in a
companion `Context.md` in this skill's directory. The steps below never hardcode
a client, repo, or tool; the project pack supplies those facts. This separation
is what lets the same skill serve any team: to onboard a new project you write a
new `Context.md`, not a new skill.

## Step 0 — Load the project context (do this first, every run)

Before anything else, load `Context.md` from this skill's directory and treat it
as the source of project truth for this session. It supplies:

| Context section | Used by |
|---|---|
| Environment & tooling | Critical constraints, QA stack hints, export targets |
| Feature taxonomy & scope | Step 1 feature mapping, in/out-of-scope rules |
| System / brownfield reference | Step 2 delta checks, Step 3 brownfield cases |
| Confirmed decisions & open contradictions | Step 1 (cite, don't re-ask), readiness flags |
| Project-specific readiness flags | Step 2 auto-raise table |
| Personas & test-data fixtures | Step 3 scenario fuel |
| Maintenance triggers | Keeping the context current |

**If `Context.md` is absent or incomplete, run in generic mode:** follow every
step below, but tell the user plainly that project specifics (feature taxonomy,
system reference, confirmed decisions, fixtures) are unavailable, and flag every
place where a project fact would normally ground a decision. **Never invent
project specifics to fill the gap** — a fabricated feature ID or fixture is worse
than an honest flag, because it looks authoritative and silently misleads review.

## Critical operating constraints

Read these before every session — they affect every step. The concrete
per-project values live in `Context.md → Environment & tooling`.

- **Where this runs.** The execution/automation environment may differ from where
  this skill runs. Don't assume a test-management API push is reachable until
  verified — offer file exports first, confirm connectivity before pushing.
- **QA stack.** Component/unit, E2E, results/reporting, and test-case-management
  tools are defined per project in `Context.md`. Use them for the per-case
  Suggested Layer hint; never assume a stack the context doesn't list.
- **Design tool-agnostic first.** Manual test design is captured independently of
  tooling; the per-case layer/tool is a forward hint for automation handoff, not
  a gate. Steps are always written for human execution.
- **Brownfield system.** If `Context.md` describes an existing system, treat it as
  brownfield: existing behavior may contradict story ACs — always flag deltas,
  never assume the story describes current behavior.
- **Resumable / multi-session flows.** If the context flags a flow as
  asynchronous or resumable, resume/re-entry testing is mandatory, not optional.
- **Human-in-the-loop is mandatory.** AI-generated test cases are never final.
  Every output requires explicit QA-reviewer confirmation before export or
  publish.

### Suggested-Layer hint (per case)

Each case carries a **Suggested Layer**, chosen from the layers defined in
`Context.md → Environment & tooling`. Typically a **Component/unit** layer for
isolated UI/state/validation checks, an **E2E** layer for full journeys and
cross-page flows, or **Ambiguous — flag for QA reviewer** when unclear. If the
project's E2E layer is BDD/Gherkin-native, write E2E cases so they translate
cleanly to Given/When/Then (Step 5). Do not guess the layer — flag if unclear.

## Workflow overview

```
[0. Load Context] → [1. Intake (+parse, consistency & existing-case checks)]
→ [2. Readiness Gate] → [3. Generate] → [4. Review] → [5. Export / Publish]
```

- **Readiness-check-only mode:** if the user wants only a readiness check
  (pre-grooming review, AC quality check), run Steps 0–2, then stop and report.
  Don't generate unless asked.
- **Work one story at a time by default.** To batch, confirm the full list up
  front, then loop each story fully (Steps 1–5) before the next.

## Step 1 — Intake

Gather the story. Accept any of: a live ticket via a connector using a ticket ID,
pasted story/ticket text, or an uploaded document/spec file.

When a **live ticket ID** is used, always fetch all three — **description, full
comment thread, and attachments** (mockups, spec excerpts, flow diagrams) —
*before asking the user anything*. Comments and attachments are a required
context source, not optional colour: scope clarifications, walk-backs, and
stakeholder disagreements frequently live in comments rather than the description.

**Required fields** (ask only if still missing after the parse below):

| Field | Why |
|---|---|
| Ticket ID / reference | Traceability + test-management linkage |
| Story title | Names the suite |
| Feature ID | Anchors every case to the project's feature taxonomy (`Context.md`) |
| Business goal / user value | Informs positive scenarios |
| Functional context / expected behavior | Informs what to test |
| Acceptance criteria | Drives the one-case-per-AC minimum |
| Known integration touchpoints | Identifies third-party dependencies + testability |
| Cohort / variant relevance | Does behavior differ across cohorts/variants in `Context.md`? |
| Resume relevance | Can the user hit this step on re-entry? (drives resume cases) |

Do not guess or invent ACs, and do not assume a feature mapping. If the story
doesn't clearly map to a feature ID in `Context.md`, ask. Apply the context's
in/out-of-scope rules: if the story maps to an out-of-scope item, stop and
surface it; if it maps to a conditional/at-risk feature, proceed only with all AC
flagged as assumptions.

### Step 1a — Structural parse (before asking the user anything)

When live-ticket content is available, run one structured extraction pass against
the Required Fields table — pull everything already answerable from description +
comments + attachments — *before* asking piecemeal. Then ask only for what's
genuinely still missing, as one consolidated list, not one question at a time.

### Step 1b — Internal consistency check (AC vs. this ticket's own comments/attachments)

Diff the AC line-by-line against the comment thread and attachments pulled above.
This is distinct from the Step 2 brownfield delta check (AC vs. system reality)
and from the `Context.md` contradiction log (program-level, cross-story) — this
check is local to this ticket.

Any AC statement contradicted, narrowed, or expanded by a comment or attachment →
log it as an **in-ticket contradiction**: quote the AC line, cite the conflicting
comment/attachment, and state the discrepancy plainly. Do not silently prefer one
source over the other, and do not average them into a best guess. Carry every
in-ticket contradiction into Step 2 — it feeds Readiness Requirement 5.

### Step 1c — Existing test-case check

Before generating anything, if a live ticket ID is given *and* test-management
connectivity is genuinely available (see Step 5 Option D for what that means),
query for cases already linked to this ticket ID.

- **None found:** proceed normally.
- **Found:** report them (count, last-modified, execution status) and ask the
  user to choose — (a) generate net-new cases alongside them, (b) treat this as a
  coverage-review against the existing cases instead of fresh generation, (c)
  supersede — mark the old cases obsolete once the new suite is confirmed, or (d)
  delete — but only case-by-case, with explicit confirmation naming the specific
  case ID(s) before each deletion. Never batch-delete and never delete on an
  implicit "yes, regenerate" (Hard Rule 13).
- **Connectivity unavailable:** note that this check couldn't run and proceed with
  a flagged assumption that prior coverage status is unknown.

## Step 2 — Readiness check (gate)

Evaluate against these requirements before generating anything:

1. Clear business goal and user value.
2. Sufficient functional/technical context — understandable without tribal
   knowledge.
3. Well-defined, testable, unambiguous ACs — each can drive a concrete case.
4. Integration touchpoints identified — for any external service, the
   success/failure response contract must be known or explicitly flagged as an
   assumption.
5. No unresolved in-ticket contradiction — AC must not conflict with this
   ticket's own comments/attachments (Step 1b). An unresolved contradiction
   blocks generation exactly like a missing AC; it is not averaged into a guess.

**Brownfield delta check (grounded).** Does any AC describe behavior that may
differ from what the system does today? Cross-reference `Context.md → System /
brownfield reference`. If a delta exists, generate an explicit delta case
(current → target), not just the target state. If current behavior is unknown,
flag it as an assumption — never treat as greenfield.

**Project-specific readiness flags.** Apply the auto-raise flag table in
`Context.md → Readiness flags`. These raise warnings when a story touches an area
with an open contradiction, undefined contract, or scope/ownership question.
Surface every applicable flag; never silently resolve a logged contradiction.

### Outcomes

- **✅ Ready for QA** — all requirements met, no blocking flags. Proceed to Step 3.
- **⚠️ Ready with Assumptions** — met, but integration contracts / brownfield
  deltas flagged. Proceed with every assumption documented per case.
- **🚫 Needs Work — block generation** — a requirement is missing or vague. State
  which, give specific fixes (e.g. *"AC #2 'form validates correctly' — specify
  which fields and what each error state says"*), and do not generate. Ask for an
  updated story, then re-run. Offer (never auto-execute) to post these findings as
  a comment on the ticket via connector, addressed to the story owner if known —
  this closes the loop back to the ticket instead of leaving the gap only in chat.

Never silently proceed on a weak story. Cases are only as good as the story.

## Step 3 — Generate structured test cases

Once readiness passes, generate a full suite.

**Coverage rules:**

- One case per AC (minimum).
- Positive, negative (invalid input, failures, unauthorized), and edge/validation
  (boundaries, empty states, concurrency).
- State transitions for multi-step/status/session flows — document start state,
  trigger, expected end state.
- Integration-failure scenarios for any third party — slow, unavailable, error
  response (respect which integrations run live vs. are mockable per `Context.md`).
- Brownfield deltas — explicit current→target cases where behavior differs from
  the system reference.
- Resume / re-entry whenever the step is reachable on re-entry — cold re-entry at
  the step boundary, completed-steps-skipped, incomplete-steps-block-progress,
  plus any project resume-security rules in `Context.md`.
- Cohort / variant variations — per the cohorts and flag states in `Context.md`.
- Boundary, error, and permission/role variations where implied.

Assign a Suggested Layer from the project stack. Design stays tool-agnostic; the
layer is a forward hint.

**Personas & fixtures.** Use the personas and standard fixtures in `Context.md`
as scenario fuel — do not invent applicants, accounts, IDs, or flag states. If a
required value is unknown, flag it explicitly.

### Coverage tier, priority & severity

- **Coverage Tier** (depth commitment): **P0** must cover before any release
  (business-critical: activation/payment/consent/compliance or equivalent); **P1**
  should cover within the current sprint; **P2** cover if time permits, document
  gaps for next sprint.
- **Priority** (urgency to pass before release): High (blocks a business-critical
  path) · Medium (degrades CX, has workaround) · Low (cosmetic/low-traffic).
- **Severity** (impact if it fails in prod): Critical (crash, data loss, payment
  fail, security/compliance breach) · Major (core workflow broken, no workaround)
  · Minor (partial, workaround exists) · Trivial (cosmetic).

### Test case structure

```
ID:              TC-001 (sequential within this story)
Name:            Short descriptive title
Feature:         [Feature ID per Context.md] — [Feature Name]
Ticket:          [Ticket ID]
Suggested Layer: [Component layer] | [E2E layer] | Ambiguous — flag for QA reviewer
Coverage Tier:   P0 | P1 | P2
Objective:       What this validates and why
Preconditions:   System state, user role, cohort/variant, channel, environment,
                 resume/entry state, and data setup required
Test Data:       Specific values (per Context.md fixtures). If unknown, flag — don't assume.
Assumptions:     Behavior/state taken as given due to brownfield uncertainty, undefined
                 integration contract, draft spec detail, or missing spec. If none, "None."
Priority:        High | Medium | Low
Severity:        Critical | Major | Minor | Trivial
Coverage:        [Ticket ID] — [AC reference or scenario tag]
Steps:
  1. Action → Expected Result
  2. Action → Expected Result
Status:          Not Run
```

**Step writing rules:** each step self-contained and executable (no tribal
knowledge, no "verify it works"); expected results specific and observable
("User sees: 'Email address is already in use'", not "error shown");
preconditions fully specified (incl. cohort/variant, channel, entry/resume
state); test data explicitly listed; for state-transition tests, start state in
Preconditions and end state in the final step's Expected Result; steps written
for human execution regardless of Suggested Layer.

**Output:** present cases cleanly in chat, then ask:

> "Edit any of these before I finalize? Once confirmed, I can export as JSON, CSV,
> or Gherkin .feature, or push to your test-management tool."

## Step 4 — Review and validate quality

After presenting (or when the user brings existing cases), run the checklist and,
for each failing item, name the affected case(s), what's missing, and a concrete
fix. Confirm or edit before export.

**Coverage:** every AC has ≥1 case · positive/negative/edge covered · state
transitions for multi-step flows · integration-failure scenarios where a third
party is involved · brownfield delta cases where current vs. target may differ ·
resume/re-entry where reachable · cohort/variant variations per `Context.md`.

**Execution readiness:** steps clear/executable and expected results
specific/observable · preconditions fully specified (incl. cohort/variant,
channel, entry state) · test data explicit (not assumed) · assumptions documented
per case.

**Classification & tooling:** Coverage Tier assigned · priority + severity
assigned via the tables · Feature ID on every case · Suggested Layer assigned,
ambiguous flagged not defaulted.

**Project-specific (apply `Context.md` rules):** no case silently assumes
greenfield · no case depends on an unconfirmed integration contract without
flagging · cases touching open contradictions are parameterized and sign-off is
blocked until confirmed · resume cases honor project resume-security rules ·
conditional/at-risk-feature cases flag all AC as assumptions · no out-of-scope
cases unless scope explicitly confirmed · draft-spec-sourced detail labeled DRAFT
· any Step 1b in-ticket contradiction was resolved or explicitly parameterized
before finalizing · if Step 1c found existing linked cases, the user's chosen
handling was actually followed — no case silently overwritten or deleted.

## Step 5 — Export / publish

Once the user confirms, offer:

- **Option A — JSON.** Array of objects, one per case (`id`, `name`, `feature`,
  `ticket`, `suggested_layer`, `coverage_tier`, `objective`, `preconditions`,
  `test_data`, `assumptions`, `priority`, `severity`, `coverage`
  `{ticketId, ac}`, `status`, `steps` `[{step_number, action, expected}]`).
- **Option B — CSV.** Flat, one row per step, metadata repeated per row: `id,
  name, feature, ticket, suggested_layer, coverage_tier, objective,
  preconditions, test_data, assumptions, priority, severity, ticket_id, ac_ref,
  status, step_number, action, expected_result`.
- **Option C — Gherkin `.feature`** (for a BDD harness). For **E2E-layer** cases
  only, so they drop into the project's BDD harness. Keep tags aligned to the
  harness's feature-toggle/tag convention in `Context.md`. Component-layer cases
  are not exported as Gherkin.
- **Option D — Push to a test-management tool.** **Default assumption:
  unavailable, not merely unverified.** Tools like Zephyr Scale, TestRail, or Xray
  run their own separate API — a Jira/Confluence connector being present does not
  mean a push path to those tools exists. Check `Context.md → Environment &
  tooling` for a genuine, connector- or token-backed path to the *specific* target
  tool before even offering this. If a real path exists: confirm the target
  project key, confirm the test cycle/folder, create each reviewed case linked to
  the story with status Not Run, and report created keys + any failures. If no
  genuine path exists, say so plainly and instead offer Option A/B formatted for
  that tool's import (e.g. a Zephyr-Scale-import-ready CSV/JSON) for manual upload.

Automated run results land in the project's reporting tool; the test-management
tool holds the manual case repository. **Never push unreviewed cases.**

### Session handoff artifact

At session end (or on request), offer a downloadable Markdown **Session Summary**
table — one row per story: Story · Feature · Readiness · Assumptions · Tier mix ·
Cases · Reviewed · Exported. Below it, list: open questions surfaced this session;
assumptions needing confirmation before finalizing (with owners where known);
risks (missing test data, undefined integration contracts, brownfield deltas,
testability blockers); and ambiguous layer assignments needing a QA-reviewer
decision.

## Hard rules (never break these)

1. Never generate cases for a story that fails the readiness check. Block and ask
   for fixes.
2. Never push to a test-management tool without explicit user confirmation after
   review (and confirm connectivity first).
3. Never invent acceptance criteria to unblock — surface the gap.
4. Never mix cases from different stories in one export without labeling by ticket
   ID + feature.
5. Regenerating replaces prior cases — warn if the user already reviewed/edited.
6. Never assume greenfield behavior on a brownfield system — unknown current
   behavior = flagged assumption, grounded in the `Context.md` system reference.
7. Never generate cases for out-of-scope items unless the user explicitly confirms
   scope with defined AC.
8. Never omit test data — if a required value is unknown, flag it; don't leave it
   blank or generic.
9. Never silently assign a layer — flag Ambiguous for a QA-reviewer decision.
10. Anchor every case to the project's feature taxonomy (`Context.md`) — don't
    reinvent IDs.
11. Treat resumable flows as resumable — if a step is reachable on re-entry,
    resume coverage is required, including project resume-security rules.
12. Never resolve a logged contradiction in `Context.md` — parameterize/flag and
    route to the owner.
13. Never delete existing test-management-tool cases without explicit, per-case
    user confirmation naming the specific case ID(s). No batch deletion, no
    deletion implied by a general "yes, regenerate" — deletion is a distinct,
    deliberate choice from generation.

## Skill maintenance

This engine (the steps above) should rarely change — project facts change in
`Context.md`, not here. Update `Context.md` when the triggers in its own
Maintenance section fire (new brownfield analysis, finalized requirements,
resolved contradictions, tooling changes, new integrations). Only edit this
`SKILL.md` to improve the reusable workflow itself.

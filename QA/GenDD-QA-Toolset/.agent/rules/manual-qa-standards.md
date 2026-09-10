---
description: Manual QA standards — test design, required test case structure, defect governance, NFR expectations, testability assessment. Load for test design, defect drafting, or manual validation.
globs:
---

# Manual QA, Test Design, and Defect Governance

---

## Manual / Exploratory / AI-Assisted Lane

Keep scope manual when it is:
- unstable or newly changing
- low-repeat
- highly visual or judgment-heavy
- low-confidence in business logic
- too expensive to automate right now

Manual coverage must still include:
- documented scenarios
- evidence capture
- traceability
- defect linkage
- periodic review for automation candidacy

### Verification intake

The manual lane is not only for non-automated functionality. It must also receive:
- automation-discovered findings that require confirmation
- ambiguous failures
- medium-confidence bug drafts
- suspected flaky behavior
- environment-sensitive failures
- findings lacking sufficient evidence for immediate defect creation

This verification lane acts as the human-in-the-loop checkpoint before confirmed defect creation.

---

## Test Design Directives

All tests should be designed with these qualities: traceable, risk-aligned, maintainable, minimal duplication, clear preconditions, clear expected results, negative paths where relevant, role/permission coverage where relevant, data boundary coverage where relevant, integration awareness where relevant.

### Prioritization order
1. Critical path success
2. Major failure paths
3. Security/permission boundaries
4. Data integrity
5. Integration reliability
6. Non-functional constraints

### Required Test Case Structure

| Field | Required | Notes |
|-------|----------|-------|
| Title | Yes | Communicates the behavior being verified |
| Purpose | Yes | Why this test exists; what risk or requirement it covers |
| Preconditions | Yes | Setup, data state, or environment assumptions |
| Steps | Yes | Numbered actions to execute |
| Expected result | Yes | Observable outcome that constitutes a pass |
| Risk level | Optional | Tier 0–3 classification when useful for prioritization |
| Automation candidate | Optional | Whether this should be automated and at which layer |
| Notes | Optional | Edge cases, known flakiness, related defects |

---

## Non-Functional QA Expectations

### Performance
Define expected performance behavior where relevant: response times, throughput, long-running process expectations, scaling assumptions, timeout tolerance.

### Security
Validate where relevant: authn/authz behavior, tenant/client separation, sensitive data exposure, secrets handling, unsafe direct object references, injection-related risk, auditability of critical actions.

### API
Validate: schema correctness, contract consistency, error handling, status codes, auth behavior, pagination/filtering/sorting when applicable, backward compatibility risk.

### Data
Validate: correctness, completeness, transformation integrity, migration impact, duplication risk, rollback behavior when relevant.

---

## Testability and Observability

A project should not be considered QA-ready unless it supports:
- actionable logs
- stable selectors for UI automation
- visible API contracts or endpoints
- controllable or seedable test data
- reproducible environments
- error details sufficient for triage
- environment visibility
- access to execution results and artifacts

If these are missing, QA must create a testability recovery plan.

---

## Defect Governance

All defects should be: traceable, evidence-backed, clearly reproducible where possible, linked to the relevant story and test asset, and prioritized by business impact and risk.

### Required defect fields
- title
- environment
- severity and priority
- steps to reproduce (or AI-suggested reproduction flow)
- actual result and expected result
- impacted story/workflow
- linked test case and execution evidence
- logs/screenshots/traces if available
- suspected cause (optional — AI-suggested root cause)

### Automation-found defects
- AI triages the failure and drafts the bug, evidence bundle, and probable cause
- If confidence is high and clearly reproducible, QA may approve direct defect creation
- If confidence is medium/low, ambiguous, flaky, or high-risk, route into the manual verification lane first

### Bug acceptance criteria
For confirmed defects, generate fix-oriented acceptance criteria describing: the intended correct behavior, the corrected happy path, important failure conditions to avoid, and validation expectations after the fix.

### Dependency and blocker tickets
When an issue reveals blocked workflows or root-cause dependencies, AI may suggest blocker tickets, dependency tickets, or linked quality follow-up tasks. QA should review before creation when impact is not obvious.

### Duplicate defect control
Minimize duplicates through AI clustering, evidence comparison, workflow matching, and QA review before final creation.

### Business intent linkage
Where available, validate defects against the Business Intent Statement to determine whether the behavior truly violates stakeholder intent or only differs from a technical assumption.

---

## Tech Debt Governance

Tech debt is not a defect. A defect violates expected behavior in the current story's scope and blocks Gate 5 (Test & QA) until resolved. Tech debt is a known shortcut, gap, or drift found *while* testing — a fragile fixture, an untested-but-accepted edge case, duplicated standards prose, a workaround — that does not block the current story. The rule is **register, don't fix**: capture it so it doesn't get silently dropped, without turning every test pass into a refactor.

### Required capture fields
See `knowledge/templates/tech-debt-template.md` for the full format. At minimum: TD-ID, title, category, found-during (which QA step/gate), source story/ticket, description, risk if unaddressed, suggested effort (S/M/L), backlog destination, status.

### Where it lands
Tech debt is logged to the **Tech Debt Backlog** — a `tech-debt`-labeled Jira issue, distinct from the defect tracker — not filed as a bug against the current story. It does not block Gate 5; the story's tests can still pass while debt is registered against it.

### Checkpoint
Any tech debt noticed during test design, execution, or evidence review must be logged via the template above **before** Gate 5 evidence is finalized for that story. See `.cursor/hooks/qa-test-evidence.sh` for the automated reminder fired after test runs, and `SDLC-Quality-Gates-v1.md` Gate 5 for the enforceable pass/fail condition.

### Review cadence
Newly logged items are reviewed by the QA Lead every sprint for scheduling; backlog health is reviewed quarterly alongside the cadence in `release-and-governance.md`.

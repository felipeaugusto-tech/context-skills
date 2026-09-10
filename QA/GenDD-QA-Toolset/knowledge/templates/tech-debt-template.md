# Tech Debt Capture Template

Standard format for registering technical debt found during QA activity (test design, test execution, evidence review, or rule/standards validation). Tech debt is **registered, not fixed** at the point it's found — this template exists to make that registration a repeatable step instead of a verbal note that evaporates.

Tech debt is not a defect. A defect is a violation of expected behavior in the current story's scope. Tech debt is a known shortcut, gap, or drift that doesn't block the current story but will cost more to fix the longer it's left — see `manual-qa-standards.md` → "Tech Debt Governance" for the full distinction.

---

## Standard Capture Format

```markdown
# {TD-ID}: {Clear, specific title}

**Category:** Code | Test | Architecture/Design | Documentation | Process/Tooling | Data
**Found During:** {SDLC stage or gate, e.g. "Gate 5 — Test & QA", "Step 8 Evidence Review"}
**Source Story/Ticket:** {the ticket being worked when the debt was spotted}
**Reporter:** {who/what found it — human or AI-assisted}
**Date Found:** {date}

## Description
{What the debt is — the shortcut, gap, or drift, and why it wasn't fixed now}

## Risk if Unaddressed
{What gets harder or breaks later, and how urgent this is — not a severity score, a plain statement of consequence}

## Suggested Effort
T-shirt size: S | M | L — a sizing signal for backlog grooming, not a commitment

## Backlog Destination
{Where this lands — see "Where Tech Debt Lands" below}

## Status
New | Backlogged | Scheduled | Remediated | Won't Fix — Accepted
```

---

## Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| TD-ID | Yes | Unique identifier, e.g. `TD-{ticket}-{seq}` |
| Title | Yes | Specific enough to action without re-reading the description |
| Category | Yes | Drives which backlog/owner it routes to |
| Found During | Yes | Which QA step/gate surfaced it — this is what makes the checkpoint auditable |
| Source Story/Ticket | Yes | The story being tested when the debt was noticed, even if the debt itself is unrelated to that story's AC |
| Description | Yes | What it is and why it's being deferred, not fixed inline |
| Risk if Unaddressed | Yes | Forces a "why does this matter" statement instead of a bare complaint |
| Reporter | Yes | Traceability — including when AI-assisted |
| Date Found | Yes | |
| Suggested Effort | Yes | S/M/L sizing only |
| Backlog Destination | Yes | Must be a real, checkable location, not "backlog" as a vague noun |
| Status | Yes | Lifecycle tracking |

---

## Where Tech Debt Lands (Backlog)

Tech debt does **not** go into the defect tracker — it is not a bug against the current story. It lands in the team's **Tech Debt Backlog**:

- Logged as a Jira issue tagged with the `tech-debt` label (or component, per project convention), separate from the defect/bug issue type.
- Linked to the source story/ticket via the "Source Story/Ticket" field, but not blocking that story's Gate 5 (Test & QA) pass — registering debt is the requirement, not resolving it.
- Reviewed at the same cadence as other QA governance items (see `release-and-governance.md` → Review Cadence): at minimum every sprint for newly logged items, quarterly for backlog health.
- Owned by the QA Lead for triage into a scheduled sprint, per the Ownership Model in `release-and-governance.md`; engineering/product own actually resolving it once scheduled.

---

## Worked Example — Demonstration (ACC-9279)

# TD-ACC9279-01: `automation-qa-standards.md` and `core-principles.md` duplicated Rules Repository content with no cross-reference

**Category:** Documentation
**Found During:** Testing-standards rule-domain validation against ACC-9279 (`Testing-Standards-Rule-Domain-Validation-ACC-9279.md`)
**Source Story/Ticket:** ACC-9279 (Identity Verification Results — detailed failure reason)
**Reporter:** QA/AI-assisted validation pass, human-reviewed
**Date Found:** 2026-07-30

## Description
While validating that the `agent-assets` testing-standards rule domain (QA-001…QA-008) correctly governs the tests ACC-9279 will produce, `QA-GenDD/.cursor/rules/automation-qa-standards.md` and `core-principles.md` were found to carry their own informal prose for mocking and AI-generated-test review — duplicating content that now has an enforceable, ID'd home in the Rules Repository (`mocking.md` / QA-007, `ai-generated-test-review.md` / QA-008), with no link between the two. Left as-is, the two copies would drift: someone editing the Rules Repository version would have no signal that QA-GenDD's copy also needed updating, and vice versa.

## Risk if Unaddressed
Silent standards drift — the two docs disagree over time, and whichever one an engineer or agent happens to load first becomes "the rule" by accident rather than by design. Low urgency (no active incident) but compounding: every future edit to either file is a chance to widen the gap.

## Suggested Effort
S — adding a "canonical source" cross-reference is a documentation-only change, not a rework.

## Backlog Destination
Not backlogged — remediated inline during the same validation pass that found it (see Status). Logged here specifically to demonstrate the capture standard end-to-end, per WS2 AC4.

## Status
**Remediated.** Cross-references were added in `automation-qa-standards.md` ("Canonical rule source: ... the enforceable, ID'd rule text lives in the Rules Repository ... When the two disagree, the Rules Repository wins.") and in the mocking/AI-review call-outs. This entry stays on record as the worked example of the capture flow, not as an open backlog item.

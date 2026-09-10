---
description: Release readiness rules, human approval gates, ownership model, review cadence. Load for release decisions or governance reviews.
globs:
---

# Release Readiness and Governance

---

## Required QA Outputs

Every project should maintain, directly or indirectly:
- QA strategy
- Test plan
- Business logic QA context
- Risk matrix
- Traceable test cases
- Automation scope definition
- Test data strategy
- Environment strategy
- Defect triage rules
- Release readiness summary
- Evidence-backed release recommendation

---

## Release Readiness Rules

A release recommendation must be based on evidence, not intuition.

Release decisions should consider:
- risk coverage
- confidence of recovered requirements
- automated results
- manual coverage status
- open critical defects
- flaky test rate
- environment confidence
- stakeholder validation gaps
- security/performance concerns

### Possible release outcomes
- **Release recommended** — evidence supports shipping
- **Release conditionally recommended** — known, documented risks accepted
- **Release not recommended** — unresolved blockers or insufficient coverage
- **Insufficient evidence** — cannot make a confident recommendation

---

## Minimum Human Approval Gates

Human review is required for:
- low-confidence critical requirements
- severe security/privacy issues
- release blockers
- high-impact business logic defects
- AI-drafted severe defects
- automatic actions with tenant/client exposure
- final release recommendation
- automation-detected findings that are ambiguous, flaky, environment-sensitive, or insufficiently evidenced

---

## Ownership Model

| Role | Responsibilities |
|------|-----------------|
| **QA Lead / QA Architect** | Quality strategy, governance, risk, release recommendation |
| **QA Engineer** | Execution oversight, evidence review, manual lane management, triage review |
| **QA Automation Engineer** | Framework design, automated lane coverage, maintenance, reliability |
| **AI Agents / AI Tooling** | Generation, summarization, clustering, drafts, repetitive execution support |
| **Engineering / Product** | Business clarification, testability support, defect resolution, release accountability |

---

## Review Cadence

These standards should be reviewed:
- at project kickoff
- when delivery model changes
- when major risk classes change
- when automation reliability degrades
- at quarterly QA governance review at minimum

---

## Final Directive

QA must operate as a scalable, AI-first, evidence-based quality system.

QA is not a bottleneck. QA enables faster delivery, clearer decisions, and better quality with less rework.

The goal is not to manually test everything. The goal is to have enough evidence for the current level of risk — and to create the fastest and most reliable path to release confidence with:
- clear traceability
- intelligent automation
- managed manual coverage
- AI-assisted triage
- human governance where it matters

Focus on: **risk, evidence, clarity, traceability**.

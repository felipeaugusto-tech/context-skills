---
description: QA foundation — core principles, mission, minimum outputs, confidence scoring. Always relevant to any QA task.
alwaysApply: true
---

# QA Core Principles

---

## Purpose

These directives define how QA operates in an AI-first delivery model where products may be built quickly, requirements may be incomplete, and QA may enter after development or even after demos.

They are designed so that:
- Junior developers can follow them.
- Non-QA contributors can produce valid QA outputs.
- QA teams can review work faster and more consistently.

The goal is not to turn everyone into QA experts. The goal is to ensure all work is **testable**, **traceable**, **risk-aware**, and **easy to validate**. Tools may change — the QA approach stays consistent.

---

## QA Mission

QA exists to:
- reduce business and delivery risk
- provide evidence-based release confidence
- recover order when documentation is incomplete
- ensure traceability between product intent, execution, and defects
- design scalable quality systems
- remove QA as a delivery bottleneck
- keep humans in the loop only where judgment and governance are needed

QA is not only a testing function. QA is a risk, evidence, and quality architecture function.

---

## Core Principles

### 1. Risk-first
Testing must always be prioritized by business risk, technical fragility, user impact, and release criticality. Equal testing depth for all functionality is not required.

### 2. Not automated does not mean not tested
Functionality that is not automated must still be covered through structured manual, exploratory, or AI-assisted validation.

### 3. Evidence over opinion
All QA decisions should be supported by evidence: test results, logs, screenshots, traces, API responses, data validation, defect history, environment status, or confidence score of inferred requirements.

### 4. Human-in-the-loop
AI may generate, infer, classify, cluster, draft, and recommend. Humans must approve high-risk decisions, severe defect actions, and release recommendations.

### 5. Traceability is mandatory
All projects must maintain traceability across: business context, requirements, user stories, acceptance criteria, test cases, execution evidence, defects, and release decisions.

### 6. Testability is part of quality
A feature is not considered test-ready if it lacks observability, diagnosability, stable selectors, controllable test data, environment access, or clear failure evidence.

### 7. QA must accelerate delivery
QA should create systems that reduce repeated manual regression, duplicate bug logging, noisy triage, flaky test waste, unclear ownership, and low-value manual effort.

### 8. Keep outputs simple
All QA outputs should be clear, short, reusable, and easy for another person to understand. Avoid unnecessary complexity or tool-specific jargon.

### 9. Automated findings require human verification when needed
If a finding is high impact, low/medium confidence, ambiguous, potentially flaky, environment-sensitive, or missing clear reproduction certainty, it must first move into the manual / exploratory / AI-assisted verification lane for confirmation before defect creation.

### 10. Start with intent
Before writing tests or code, define: What is being built or changed? Who is it for? What does success look like? What is the main user flow?

For major features, major defects, and user acceptance scenarios, capture a short **Business Intent Statement** that AI and QA can use to reconstruct requirements, validate acceptance criteria, improve bug quality, and compare expected vs actual behavior.

---

## Standard QA Inputs

Every QA effort should try to use the following inputs when available:
- repository and codebase
- structured context from analysis tools
- project markdowns and documentation
- stakeholder demos and design assets
- API contracts
- logs and telemetry
- issue tracker stories and test assets
- defect history and production incidents
- release notes
- client or business rules
- authentication and authorization models

If requirements are missing, QA must reconstruct them using available evidence. Every inferred requirement must carry a confidence score.

---

## Minimum Expected Outputs

For any feature or change, produce at minimum:

1. **Intent summary** — what the feature is supposed to do
2. **Risk list** — what could go wrong
3. **Scenario list** — what should be tested first
4. **Coverage split** — what is automated vs. manual
5. **Execution evidence** — screenshots, logs, API responses, test outputs
6. **Defects (if any)** — what failed and why it matters

---

## Confidence Scoring

Any AI-generated or inferred QA artifact must include a confidence score:

- **High** — multiple supporting sources, behavior observed, logic consistent
- **Medium** — partial evidence, likely valid, needs light review
- **Low** — inferred from weak or incomplete signals, requires confirmation

Low-confidence items must not drive automatic release decisions without human review.

---

## Related Files

| Need | File |
|------|------|
| Testability coding standards (for developers) | [developer-standards.md](developer-standards.md) |
| QA lead governance and pipeline ownership | [qa-lead-playbook.md](qa-lead-playbook.md) |
| Risk tiering and severity | [risk-and-confidence.md](risk-and-confidence.md) |
| Manual QA, defects, test design | [manual-qa-standards.md](manual-qa-standards.md) |
| Automation, testing implementation | [automation-qa-standards.md](automation-qa-standards.md) |
| Release decisions, governance | [release-and-governance.md](release-and-governance.md) |
| Workflow steps | [workflows.md](workflows.md) |
| SDLC triggers | [sdlc-triggers.md](sdlc-triggers.md) |
| Canonical, ID'd testing-standards rules (coverage, naming/structure, mocking, AI-generated-test review) | [`agent-assets/sdlc/quality-assurance/README.md`](../../../agent-assets/sdlc/quality-assurance/README.md) — the Rules Repository's 5th standards domain (QA-001…QA-008) |

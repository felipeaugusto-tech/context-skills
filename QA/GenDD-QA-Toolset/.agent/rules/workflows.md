---
description: Greenfield and brownfield QA workflows — 11-step pipeline, dual validation model, shared architecture. Load when planning or executing a QA workflow.
globs:
---

# QA Workflows
## Brownfield vs Greenfield Operating Models

---

## Overview

Two QA operating models exist based on system context:

- **Brownfield QA Workflow** — for existing systems with unclear or missing requirements
- **Greenfield QA Workflow** — for new systems with defined intent

Both workflows share the same **core QA control system**, but differ in how **context and truth are established**.

> **This workflow is tool-agnostic.** Teams use whatever tools fit their project — the methodology stays the same.

---

## Core Principle

> QA is not execution.
> QA is a **decision system governed by risk, confidence, and evidence**.

All workflows converge to:

**Risk + Confidence → Validation → Evidence → QA Decision → Confirmed Defects**

---

# Greenfield QA Workflow

## Definition

Used when:
- No system exists yet
- Requirements are defined upfront
- Behavior is intentionally designed

---

## Workflow

Steps 5-11 are shared — see Shared Steps below.

| Step | What happens | Subtitle |
|------|-------------|----------|
| **1. Product intent defined** | Business goals, user needs, and success criteria are captured | business goals, user needs, success criteria |
| **2. Validate and structure context** | Validate expected architecture, flows, and assumptions against intent | expected architecture, flows, assumptions |
| **3. Build scope and QA structure** | Stories, QA structure, and requirements are defined | stories, QA structure, requirements definition |
| **3a. QA Planning** | Define test data strategy, environment strategy, automation scope, and CI pipeline shape. Effort proportional to risk and novelty. | proactive investment in future readiness |
| **4. Create structured, traceable test cases** | Structured, traceable test cases are created and stored in the test management system, informed by the QA plan | structured, traceable test cases |

### Key Characteristics

- Forward-designed system
- Context is **defined upfront**
- Lower initial uncertainty
- QA acts as **validation + governance layer**

---

# Brownfield QA Workflow

## Definition

Used when:
- A system or MVP already exists
- Requirements are incomplete or unclear
- Behavior must be **reverse-engineered**

---

## Workflow

Steps 5-11 are shared — see Shared Steps below.

| Step | What happens | Subtitle |
|------|-------------|----------|
| **1. MVP exists** | An AI-generated or legacy system is the brownfield application | Brownfield application ready |
| **2. Recover and structure context** | Infer existing architecture, flows, risks, and assumptions from the codebase | existing architecture, flows, assumptions |
| **3. Build scope and QA structure** | Stories, QA structure, and requirements are defined from recovered context | stories, QA structure, requirements definition |
| **3a. QA Planning** | Define test data strategy, environment strategy, automation scope, and CI pipeline shape. Effort proportional to risk and novelty. | proactive investment in future readiness |
| **4. Create structured, traceable test cases** | Structured, traceable test cases with confidence annotations, informed by the QA plan | structured, traceable test cases |

### Story Update Behavior

When a story is updated:

> Re-enter at **Step 2: Recover and structure context**

This ensures:
- Context is revalidated
- Scope is recalculated
- Tests are updated
- Validation is re-executed

### Key Characteristics

- Reverse-engineered system
- Context is **recovered from the existing system**
- High initial uncertainty
- QA acts as **reconstruction + control layer**

---

## Shared Steps (5-11)

| Step | What happens | Subtitle |
|------|-------------|----------|
| **5. Risk + Confidence** | QA decision engine classifies risk tiers (T0–T3) and assigns confidence scores | QA decision engine |
| **6A. Automation** | Deterministic validation with planned coverage for stable, repeatable scenarios | deterministic validation, planned coverage |
| **6B. Manual + AI** | Exploratory validation for edge cases, unknowns, and uncertainty resolution | exploratory validation, edge cases, unknowns |
| **7A. Automated execution** | Continuous validation producing strong, repeatable evidence | continuous validation, strong evidence |
| **7B. Exploratory execution** | Human + AI validation for judgment-heavy and ambiguous scenarios | human + AI validation |
| **8. Evidence + AI Triage** | Evidence-weighted clustering; AI drafts defects, identifies duplicates, suggests root cause | evidence-weighted clustering |
| **9. QA Decision** | Human-in-the-loop control; QA reviews findings, approves or rejects | human-in-the-loop control |
| **10. Confirmed defects** | Only validated, traceable defects are created in the issue tracker | validated + traceable |
| **11. Release readiness** | Evidence-based release recommendation | release recommended / conditional / not recommended / insufficient evidence |

---

# Brownfield vs Greenfield Comparison

| Dimension | Brownfield | Greenfield |
|----------|-----------|-----------|
| Starting point | Existing system (MVP) | Defined intent |
| Context source | Recovered from system | Validated against intent |
| Requirements | Inferred from code behavior | Designed upfront |
| QA role | Reconstruction + control | Validation + control |
| Initial uncertainty | High | Managed upfront |
| Change handling | Re-enter at context recovery | Managed through design |
| Test confidence | Annotated with confidence levels | Generally higher |

---

# Shared Architecture

Both workflows share:

- **Decision Engine (Step 5):** Risk tiers T0–T3 and confidence scoring drive testing depth. See [risk-and-confidence.md](risk-and-confidence.md).
- **Dual Validation (Steps 6–7):** Automation lane for stable scenarios; Manual + AI lane for exploratory and ambiguous findings. See [automation-qa-standards.md](automation-qa-standards.md) and [manual-qa-standards.md](manual-qa-standards.md).
- **Evidence Flow (Step 8):** AI clusters findings, drafts defects, identifies duplicates; QA reviews meaningful outputs.
- **Output Control (Steps 9–10):** Only validated defects reach the issue tracker. AI drafts, humans decide. See [manual-qa-standards.md](manual-qa-standards.md) for defect field requirements.
- **Tech Debt Capture (Steps 6–8, ongoing):** Anything found during dual validation or evidence review that isn't a defect against this story — a shortcut, gap, or drift — is registered, not fixed, via [manual-qa-standards.md](manual-qa-standards.md) → Tech Debt Governance. This runs alongside every story, not as its own numbered step.

---

# Strategic Insight

The difference between workflows is not in the steps — it is in **where truth comes from**:

- **Brownfield** → Truth is **discovered** from system behavior
- **Greenfield** → Truth is **defined** from intent

---

# Final Takeaway

QA is not about test execution, tooling, or coverage metrics.

It is a **system for controlling correctness under uncertainty**.

> QA governs release decisions through **risk, confidence, and evidence** — not assumptions.

## Related Documents

- [QA Core Principles](core-principles.md) — Foundation principles loaded every session
- [Manual QA Standards](manual-qa-standards.md) — Test design, defects, manual validation
- [Automation QA Standards](automation-qa-standards.md) — Testing implementation, CI/CD
- [Release and Governance](release-and-governance.md) — Release readiness, human gates
- [QA Planner](qa-planner.md) — Routing table, checklists, and prompts for executing these workflows
- [SDLC Triggers](sdlc-triggers.md) — When each SDLC phase feeds information into the QA process

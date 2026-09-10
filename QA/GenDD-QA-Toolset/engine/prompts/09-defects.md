# Defect Generation

## When to Use
Use this prompt when:
- a failure is detected during testing (manual or automated)
- analyzing logs, outputs, or evidence
- converting findings into **structured, high-quality defects**

This step transforms:
→ observations and failures  
into  
→ **actionable, traceable bug reports**

---

## Instructions

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

---

## Input

Analyze the following failure, evidence, or test result:

[PASTE FAILURE DETAILS / LOGS / OUTPUT / NOTES HERE]

---

## Output Format

---

### Title
Short, clear summary of the issue

---

### Environment
- environment (dev, QA, staging, prod)
- relevant configuration (if known)

---

### Linked Context
- Feature / Story (if known)
- Scenario or Test Case (if available)

---

### Preconditions (if applicable)
State required setup:
- user role
- data setup
- system state

---

### Steps to Reproduce
Provide clear, minimal steps:

1. Step
2. Step
3. Step

Must be:
- reproducible
- sequential
- unambiguous

---

### Expected Result
What should happen based on:
- requirements
- intent
- system behavior

---

### Actual Result
What actually happened:
- error messages
- incorrect behavior
- unexpected output

---

### Evidence

Include or reference:
- logs
- API responses
- screenshots
- recordings
- system outputs

---

### Impact

Explain why this matters:

- Blocks critical workflow?
- Affects data integrity?
- Security concern?
- Degrades user experience?

---

### Severity (Suggested)

- Critical → blocks release, security/data risk
- High → major functionality broken
- Medium → important issue, workaround exists
- Low → minor or cosmetic

---

### Priority (Suggested)

Based on:
- business urgency
- release impact
- user exposure

---

### Risk Category

- Security
- Data Integrity
- Core Workflow
- Integration
- UI / UX
- Other

---

### Confidence Level

- High → clearly reproducible and validated
- Medium → likely valid but needs confirmation
- Low → unclear or inconsistent, needs review

---

### Reproducibility

- Always
- Intermittent
- Unable to reproduce consistently

---

### Suspected Cause (Optional)

If possible, suggest:
- probable root cause
- related system behavior
- impacted component

---

### Fix Validation Criteria (Recommended)

Define what must be true after fix:

- expected correct behavior
- validation conditions
- regression areas to check

---

### Human Review Required

- Yes → high-risk, low-confidence, unclear issue
- No → clear, reproducible, well-evidenced issue

---

## Output Expectations

- Clear and concise
- Fully reproducible
- Evidence-backed
- Actionable by developers
- Traceable to context

---

## Do Not

- Create vague or incomplete defects
- Skip reproduction steps
- Ignore evidence
- Over-report low-value issues
- Assume behavior without validation

---

## Goal

Produce **high-quality, developer-ready defects** that:

- reduce back-and-forth
- improve fix speed
- maintain QA signal quality
- align with GenDD traceability and governance
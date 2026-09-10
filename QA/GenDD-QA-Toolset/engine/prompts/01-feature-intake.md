# Feature Intake

## When to Use
Use this prompt when starting work on a **new feature, story, or change request**.

This is the **first step of QA in GenDD**, where we:
- understand intent
- identify risks
- define validation scope

---

## Instructions

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

---

## Prompt

Analyze the following feature, story, or requirement:

[PASTE FEATURE / STORY / DESCRIPTION HERE]

---

## Output Format

### 1. Intent Summary
- What is being built or changed?
- Who is the user?
- What is the expected outcome?
- What does success look like?

---

### 2. Main User Flow
Describe the primary (happy path) workflow step-by-step.

---

### 3. Risk Identification (Risk-First)

Identify and categorize risks:

#### High Risk (Tier 0 / Tier 1)
- Security, authentication, data integrity, core workflows

#### Medium Risk (Tier 2)
- Integrations, background processes, reporting

#### Low Risk (Tier 3)
- UI, cosmetic, low-impact behavior

---

### 4. Key Scenarios (Prioritized)

List validation scenarios grouped by priority:

#### High Priority
- Critical path success
- Major failure paths
- Permission/security checks
- Data integrity validation

#### Medium Priority
- Secondary workflows
- Integration behavior
- Edge cases with moderate impact

#### Low Priority
- UI behavior
- Non-critical variations

---

### 5. Acceptance Criteria (Gherkin Format)

Generate structured acceptance criteria in Gherkin syntax for each key scenario:

```
GIVEN [precondition]
WHEN [action]
THEN [expected outcome]
AND [additional assertion]
```

Requirements:
- ACs describe **expected behavior**, not implementation steps
- Cover the happy path, at least one error condition, and at least one edge case per T0/T1 area
- Each AC must be testable and unambiguous
- Include at least 5 edge cases (multi-tenant isolation, integration failures, null/empty inputs, concurrency, accessibility)

---

### 6. Definition of Ready Checklist

Verify the feature meets the following before it enters development:

| Criterion | Status |
|-----------|--------|
| Clear problem statement | Met / Not Met / Partial |
| ACs describe expected behavior (not implementation) | Met / Not Met / Partial |
| Scope boundaries defined (in/out of scope) | Met / Not Met / Partial |
| Integration impact identified | Met / Not Met / Partial |
| Security/compliance review flagged (if applicable) | Met / Not Met / Partial |
| Environment/data dependencies documented | Met / Not Met / Partial |
| Unknowns explicitly listed (not implicit) | Met / Not Met / Partial |

> "Unknown" is acceptable. "Implicit" is not.

---

### 7. Coverage Recommendation

For each scenario group, indicate:

- Automate → stable, repeatable, high-value
- Manual → exploratory, new, uncertain, visual
- Either → flexible based on context

---

### 8. Evidence Requirements

What evidence should be captured during validation?

Examples:
- logs
- API responses
- screenshots
- execution results
- system outputs

---

### 9. Assumptions and Unknowns

List:
- missing requirements
- unclear behavior
- dependencies not defined
- potential gaps in logic

---

### 10. Confidence Levels

For inferred elements, classify:

- High → strong evidence or clear requirement
- Medium → likely correct but needs validation
- Low → assumption or unclear, requires confirmation

---

## Output Expectations

The result must be:
- clear and structured
- easy to execute
- aligned with risk-first QA
- usable without additional interpretation

Do NOT:
- overcomplicate
- assume perfect requirements
- skip risk prioritization

---

## AC Anti-Patterns to Prevent

| Anti-Pattern | Problem | What to Do Instead |
|--------------|---------|-------------------|
| ACs in description field only | Not visible, not tracked | Generate ACs as a distinct section |
| "See STR" patterns | Expected behavior undefined | Explicitly document expected behavior |
| Missing edge cases | QA discovers issues via bugs | Generate 5+ edge cases per feature |
| Implicit integration impact | Late discovery of downstream effects | Surface integration questions explicitly |
| Vague scope boundaries | Scope creep | Define in-scope and out-of-scope |

---

## Goal

Produce a **QA-ready feature understanding** that:
- aligns with GenDD (intent-first)
- includes testable Gherkin acceptance criteria
- meets Definition of Ready before entering development
- enables scenario creation
- accelerates validation
- reduces ambiguity for QA and development
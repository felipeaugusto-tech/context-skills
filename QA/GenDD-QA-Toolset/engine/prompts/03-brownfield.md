# Brownfield QA Strategy

## When to Use

Use this prompt when defining how to **establish and govern quality in an existing system (Brownfield)** where an MVP or codebase already exists, requirements may be missing or inconsistent, behavior must be understood and reconstructed, or AI may have generated part of the system.

This is NOT about writing test cases — this is about defining a **quality recovery and control system**.

---

## Prompt

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

You are acting as an AI-native QA Architect operating within the **HatchWorks QA methodology**.

Given an existing system, feature, or MVP, define how to **recover context, reconstruct understanding, and establish quality governance** using the Brownfield QA workflow.

---

## Brownfield QA Flow (Reference Model)

Use this structure as the foundation:

1. MVP exists  
2. Recover and structure context  
3. Build scope and QA structure  
4. Create test baseline  
5. Risk + Confidence classification  
6. Dual validation paths  
7. Execution  
8. Evidence + AI triage  
9. QA decision  
10. Confirmed defects  

---

## Output Requirements

Produce a structured QA strategy that explains:

---

### 1. Context Recovery Strategy

- How to infer architecture from the existing codebase and system behavior
- How to reconstruct workflows by analyzing code paths, data flows, and integration points
- How to identify dependencies across modules, services, and external systems
- How to detect implicit business logic that is not captured in documentation

- What signals to use for context recovery:
  - codebase structure and patterns
  - commit history and evolution
  - observable system behavior
  - integration contracts and data flows

---

### 2. Understanding Reconstruction

- How QA identifies:
  - inferred requirements
  - missing requirements
  - conflicting logic

- How assumptions are documented with **confidence levels**

---

### 3. Scope and QA Structure

- How recovered understanding becomes:
  - stories
  - acceptance criteria
  - QA structure

- How traceability is rebuilt from incomplete inputs

---

### 4. Test Baseline Strategy

- How test cases are:
  - generated from inferred behavior
  - structured for traceability
  - annotated with confidence levels

---

### 5. Risk + Confidence Model

- How risk tiers are defined (T0–T3)
- How confidence is assigned to:
  - inferred requirements
  - system behavior
  - test scenarios

- How this model drives validation priorities

---

### 6. Validation Strategy (Dual Lane)

Define:

#### Automation (Deterministic Validation)
- What can be safely automated
- What is stable enough to be repeatable
- Regression coverage strategy

#### Manual + AI (Uncertainty Resolution)
- What requires exploration
- What is ambiguous or low-confidence
- How AI assists investigation and validation

---

### 7. Execution Model

- How testing is executed:
  - automated (repeatable validation)
  - exploratory (behavior discovery)

- How findings are captured with context

---

### 8. Evidence Model

Define levels of evidence:

- Strong → deterministic results, logs, data validation  
- Medium → UI behavior, integration responses  
- Weak → inferred or AI-generated assumptions  

Explain how evidence quality impacts decisions

---

### 9. QA Decision Framework

- How QA evaluates:
  - risk coverage
  - evidence strength
  - confidence levels
  - defect impact

- How release readiness is determined in uncertain environments

---

### 10. Defect Governance

- How AI contributes to:
  - clustering findings
  - drafting defects

- How QA:
  - validates accuracy
  - assigns severity
  - ensures reproducibility

---

## Special Behavior: Story Update Re-entry

When a preexisting story is updated:

- Re-enter at **Step 2: Recover and structure context**

Explain:

- Why context must be revalidated
- How scope, tests, and validation may change
- How the system reuses the same workflow instead of creating a new one

---

## Constraints

Do NOT:
- assume clean or complete requirements
- rely on documentation as source of truth
- jump directly into test execution
- treat QA as a final step

---

## Goal

Produce a QA operating model that ensures:

> An existing system can be understood, validated, and governed,  
> even under uncertainty and incomplete information.

This should reflect **Brownfield QA as a reverse-engineered quality system**, not a traditional testing phase.

---

## Recommended Next Steps

After establishing the brownfield QA strategy:

1. **Identify test coverage gaps** — use `engine/prompts/15-test-gap-analysis.md` to map what tests exist vs. what should exist, prioritized by risk tier
2. **QA planning** — use `engine/prompts/14-qa-planning.md` to define test data, environments, and automation scope
3. **Generate scenarios** — use `engine/prompts/05-scenarios.md` to create risk-prioritized test scenarios from recovered context
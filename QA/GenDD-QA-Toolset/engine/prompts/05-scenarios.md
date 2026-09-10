# Test Scenario Generation

## When to Use

Use this prompt when you need to generate **general, tool-agnostic test scenarios** based on a feature, workflow, or system description. Focus on behavior, risk, and validation intent — not execution or implementation details.

---

## Prompt

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

You are acting as an AI-native QA Architect working within a GenDD-aligned workflow.

Generate **general, tool-agnostic test scenarios** for the provided input. Do NOT assume any specific programming language, framework, tool (e.g., Selenium, Playwright), or implementation details.

---

## Input

Provide:
- Feature description
- User flow or system behavior
- (Optional) business rules or constraints

---

## Output Requirements

Generate a structured list of **test scenarios** using the following format:

### For each scenario include:

- **Scenario Title**
- **Description**
- **Preconditions**
- **Test Steps (high-level)**
- **Expected Result**
- **Risk Level** (T0 / T1 / T2 / T3)
- **Confidence Level** (High / Medium / Low)
- **Suggested Validation Type**
  - Deterministic (automation candidate)
  - Exploratory (manual + AI-assisted)

---

## Behavior-Focused Scenario Design

### Behavior-Driven (Not Implementation-Driven)
Focus on:
- What the system should do  
- What could go wrong  
- Edge cases and failure modes  

Avoid:
- UI selectors  
- API endpoints  
- code-level instructions  

---

## Scenario Coverage Expectations

Ensure scenarios cover:

- **Happy path (core flow)**
- **Negative cases (invalid inputs, failures)**
- **Edge cases (boundary conditions)**
- **State transitions**
- **Data validation**
- **Error handling**
- **Permissions / access control (if applicable)**

---

## Output Style

- Clear, concise, and structured
- No redundancy
- No tool-specific instructions
- Professional, QA-architect level

---

## Goal

Produce a set of scenarios that:

> Can be used across any technology,  
> support both greenfield and brownfield QA workflows,  
> and enable risk-based, evidence-driven validation.
# Scenario to Test Case Conversion

## When to Use
Use this prompt when you already have a **list of scenarios** and need to convert them into **structured, executable test cases**.

This step transforms:
→ understanding (scenarios)  
into  
→ execution-ready validation (test cases)

---

## Instructions

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

---

## Input

Convert the following scenarios into structured test cases:

[PASTE SCENARIOS HERE]

---

## Output Format

For each scenario, generate a test case using the following structure:

---

### Test Case ID
Unique identifier (e.g., TC-LOGIN-001)

---

### Title
Short, clear description of what is being validated

---

### Linked Scenario
Reference the original scenario

---

### Purpose
Why this test exists (what risk or behavior it validates)

---

### Priority
- High (critical path, security, data integrity)
- Medium (important but not blocking)
- Low (cosmetic or minor behavior)

---

### Preconditions
What must be true before executing the test:
- system state
- user role
- data setup
- environment conditions

---

### Steps
Step-by-step instructions:
1. Action
2. Action
3. Action

Keep steps:
- clear
- minimal
- reproducible

---

### Expected Result
What should happen if the system behaves correctly

---

### Negative / Failure Conditions (if applicable)
- invalid inputs
- error handling
- boundary conditions

---

### Test Type
- Functional
- Integration
- API
- UI
- Data
- Security (if relevant)

---

### Automation Candidate
- Yes → stable, repeatable, deterministic
- No → exploratory, unstable, unclear
- Partial → some steps automatable

---

### Evidence Required
What should be captured during execution:
- logs
- API responses
- screenshots
- system outputs

---

### Confidence Level
- High → clearly defined behavior
- Medium → some assumptions
- Low → unclear or inferred logic

---

## Output Requirements

- One test case per scenario (or split if scenario is too broad)
- Maintain **clear traceability** to original scenarios
- Ensure all test cases are:
  - executable
  - unambiguous
  - reproducible

---

## Do Not

- Combine unrelated scenarios into one test case
- Leave expected results vague
- Skip preconditions
- Ignore risk priority
- Overcomplicate language

---

## Goal

Produce **high-quality, execution-ready test cases** that:

- align with GenDD structured outputs
- support both manual and automated execution
- improve QA speed and clarity
- enable consistent validation across teams
# Automation Decision

## When to Use
Use this prompt after:
- scenarios are defined, OR
- test cases are created

This step determines:
→ what should be automated  
→ what should remain manual or exploratory  

---

## Instructions

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

---

## Input

Analyze the following scenarios or test cases:

[PASTE SCENARIOS OR TEST CASES HERE]

---

## Output Format

For each item, provide:

---

### Item Name
(Scenario or Test Case Title)

---

### Risk Level
- High (critical path, security, data integrity)
- Medium (important workflows, integrations)
- Low (cosmetic, low impact)

---

### Classification
- Automate Now
- Keep Manual
- Hybrid (partial automation)
- Needs Clarification

---

### Reasoning

Explain clearly based on:

- **Risk** → how critical is this?
- **Repeatability** → how often will this run?
- **Stability** → is behavior consistent?
- **Complexity** → how hard is it to automate?
- **Maintenance Cost** → will it break often?
- **Execution Cost** → is manual expensive?

---

### Automation Recommendation

If **Automate Now**:
- Suggested level:
  - API
  - Integration
  - UI
  - Data validation
- Key validations to automate

If **Hybrid**:
- Which parts to automate
- Which parts remain manual

If **Manual**:
- Why automation is not recommended
- What type of manual validation is required:
  - exploratory
  - visual
  - judgment-based

---

### Evidence Requirements

What evidence should be captured:
- logs
- API responses
- screenshots
- execution outputs

---

### Risks of Automation (if applicable)

- flakiness risk
- environment dependency
- unclear expected behavior
- data dependency issues

---

### Confidence Level

- High → clear decision based on stable behavior
- Medium → some uncertainty
- Low → insufficient information, needs clarification

---

## Output Expectations

- Be **practical and realistic**
- Avoid recommending automation for everything
- Focus on **high-value scenarios first**
- Keep explanations **short and actionable**

---

## Do Not

- Recommend UI automation for unstable features
- Ignore maintenance cost
- Over-automate low-value scenarios
- Skip reasoning
- Assume all scenarios are automation-ready

---

## Goal

Produce a **balanced automation strategy** that:

- maximizes value and efficiency
- minimizes maintenance and flakiness
- aligns with GenDD delivery speed
- supports both AI and human execution models
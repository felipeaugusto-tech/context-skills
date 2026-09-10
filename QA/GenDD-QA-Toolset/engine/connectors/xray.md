# Xray Test Management Connector

> **Purpose:** Agent-consumable instructions for integrating AI-generated QA artifacts with Xray test management.
> **When to load:** The agent needs to create test cases in Xray format, push execution results, or maintain traceability between tests and stories.

---

## When to Use

Use this connector when:
- The project uses Xray for test management within an issue tracker
- Test cases need to be stored with formal traceability to stories/requirements
- Execution results need to be recorded for audit trails
- The team requires structured test plans with coverage reporting

Do NOT use for:
- Projects without an Xray instance
- Lightweight/informal QA (use markdown test cases instead)
- Exploratory testing (capture evidence directly, no Xray test plan needed)

---

## Concept Mapping

| HatchWorks QA Concept | Xray Equivalent |
|----------------------|-----------------|
| Test scenario | Test (issue type) |
| Test case (with steps) | Test with Steps |
| Test execution evidence | Test Execution + Test Run |
| Coverage split | Test Plan |
| Defect linked to test | Defect linked to Test Run |
| Risk tier (T0-T3) | Priority / Label on Test |
| Confidence label | Custom field or label |

---

## Creating Test Cases for Xray

When generating test cases, structure them so they can be imported into Xray:

### Required Fields

| Field | Maps to Xray | Notes |
|-------|-------------|-------|
| Title | Test summary | Clear, behavior-focused |
| Steps | Test Steps (action + expected result) | Numbered, specific |
| Preconditions | Precondition (linked or inline) | Data state, environment |
| Priority | Priority field | Map T0→Critical, T1→High, T2→Medium, T3→Low |
| Type | Test Type | Manual or Automated |
| Labels | Labels field | Add risk tier, automation candidate, confidence |

### Output Format for Import

```markdown
**Summary:** Verify order submission creates exactly one charge
**Type:** Manual
**Priority:** Critical (T0)
**Labels:** payment, risk-t0, automation-candidate
**Precondition:** User logged in, items in cart, payment gateway in test mode

| # | Action | Expected Result |
|---|--------|-----------------|
| 1 | Navigate to checkout page | Checkout loads with order summary |
| 2 | Click "Place Order" | Loading indicator appears |
| 3 | Check payment gateway | Exactly one charge record created |
| 4 | Check order confirmation page | Confirmation with order ID displayed |
```

---

## Recording Execution Results

After test execution (manual or automated), push results to Xray:

### Pass
- Mark Test Run as PASS
- Attach evidence: screenshots, logs, API responses
- Link to the Test Execution

### Fail
- Mark Test Run as FAIL
- Attach failure evidence
- Create linked defect using `engine/prompts/09-defects.md`
- Link defect to the Test Run and the original story

### Blocked
- Mark Test Run as BLOCKED
- Document the blocker (environment, dependency, data issue)
- Create blocker ticket if needed

---

## Maintaining Traceability

```
Story/Requirement
    └── Test (in Xray)
        └── Test Execution
            ├── Test Run (PASS/FAIL/BLOCKED)
            │   └── Evidence (screenshots, logs)
            └── Defect (if FAIL)
                └── Linked back to Story
```

### Checklist
- [ ] Every test is linked to a story or requirement
- [ ] Every test execution has a Test Execution container
- [ ] Every failure has a linked defect with evidence
- [ ] Risk tier is recorded as a label on each test
- [ ] Confidence labels are recorded for AI-generated tests

---

## Integration with QA Workflow

| Workflow Step | Xray Action |
|--------------|-------------|
| Step 4 (Create tests) | Create Tests in Xray, link to stories |
| Step 5 (Risk + Confidence) | Set priority and labels on Tests |
| Step 7 (Execution) | Create Test Execution, record Test Runs |
| Step 8 (Evidence + Triage) | Attach evidence to Test Runs, create defects |
| Step 10 (Confirmed defects) | Link defects to Test Runs and stories |
| Step 11 (Release readiness) | Use Xray coverage report as evidence |

---

## Anti-Patterns

| Avoid | Do Instead |
|-------|-----------|
| Create Xray tests without linking to stories | Always link to the requirement/story |
| Push AI-generated tests without review | Review and set confidence label first |
| Record PASS without evidence | Attach at least one screenshot or log excerpt |
| Create defects directly from low-confidence failures | Route to manual verification first |
| Skip the Test Execution container | Always group runs under an execution |

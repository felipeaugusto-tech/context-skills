# Xray Integration with AI

This guide teaches you how to use Xray test management alongside the HatchWorks QA Operating Model to maintain traceable, structured QA.

---

## What Is Xray?

Xray is a test management tool that runs inside your issue tracker. It stores test cases, tracks execution results, and maintains traceability between requirements, tests, and defects.

---

## Why Use Xray with AI?

| Without Xray | With Xray |
|---|---|
| Test cases live in markdown files | Test cases are stored with formal traceability |
| Evidence is in screenshots/logs | Evidence is linked to specific test runs |
| Coverage is estimated | Coverage is measured and reported |
| Defects are loosely linked | Defects are traceable to the exact test that found them |

---

## The Workflow

### 1. Generate test cases with AI

Use the QA workflow to generate structured test cases:
```text
Generate test cases for the payment flow. Format them for Xray import
with summary, steps, expected results, priority, and labels.
```

### 2. Review and refine

AI-generated test cases are **drafts**. Review them:
- Are preconditions correct?
- Are steps specific enough to reproduce?
- Is the risk tier accurate?
- Tag AI-generated tests with a confidence label

### 3. Import into Xray

Take the structured output and import it into Xray:
- Create Tests linked to the relevant stories/requirements
- Set priority based on risk tier (T0→Critical, T1→High, T2→Medium, T3→Low)
- Add labels for risk tier, automation candidate, confidence level

### 4. Execute and record

Run tests (manual or automated) and record results in Xray:
- Create a Test Execution
- Mark each Test Run as PASS, FAIL, or BLOCKED
- Attach evidence (screenshots, logs, traces) to each run

### 5. Handle failures

For failures:
- Use the AI defect drafting prompt to create a structured bug report
- Create the defect in your issue tracker
- Link the defect to the Test Run and the original story
- This creates full traceability: Story → Test → Execution → Defect

### 6. Assess release readiness

Xray's coverage reports become input for release readiness:
```text
Assess release readiness based on this Xray coverage data:
- Total tests: 45
- Passed: 40
- Failed: 3 (all Medium severity, workarounds documented)
- Blocked: 2 (environment issue)
- Coverage: T0 100%, T1 95%, T2 80%, T3 40%
```

---

## Tips

1. **Keep the AI as drafter, Xray as record** — AI generates, Xray stores
2. **Always link tests to stories** — traceability is the main value of Xray
3. **Tag confidence levels** — so reviewers know which tests were AI-inferred
4. **Use Xray coverage reports for release decisions** — they provide the evidence
5. **Don't over-formalize exploratory testing** — capture findings directly as defects, not as Xray test plans
6. **Review before import** — AI-generated tests are drafts until a human approves them

# Brownfield QA Workflow — End-to-End Walkthrough

This guide walks through the complete 11-step brownfield QA workflow. Use this when an existing system or MVP needs quality governance established.

---

## The Scenario

> You are assigned QA for an existing e-commerce application. It was built quickly, requirements are incomplete, and there are no existing test suites. You need to recover context, understand the system, and establish quality governance.

---

## Step 1: MVP Exists

**Starting point:** The existing system is your brownfield application. You have access to the codebase, maybe some documentation, and the running application.

---

## Step 2: Recover and Structure Context

**What you do:** Use the AI to analyze the existing system and reconstruct understanding.

**Ask the AI:**
```text
Using the brownfield QA strategy, analyze this existing system and establish quality
governance. Here is what I know:
- Tech stack: [describe]
- Key features: [list them]
- Known issues: [any you know about]
- Available documentation: [what exists]
```

**What you get:** Context recovery strategy, understanding reconstruction, inferred requirements with confidence levels.

**Prompt used:** `engine/prompts/03-brownfield.md`

---

## Step 2b: Identify Test Coverage Gaps

**What you do:** After recovering context, analyze what test coverage already exists and where the gaps are.

**Ask the AI:**
```text
Analyze this codebase and identify test coverage gaps. Focus on T0/T1 risk areas first.
What tests should exist but don't? Prioritize by business risk.
```

**What you get:** Test inventory, coverage gap matrix, risk heat map, prioritized remediation recommendations.

**Prompt used:** `engine/prompts/15-test-gap-analysis.md`

This step gives you visibility into existing test coverage before you start building new scope. It ensures you are not duplicating effort or missing critical gaps.

---

## Step 3: Build Scope and QA Structure

**What you do:** Turn recovered context into stories, acceptance criteria, and QA structure.

The AI produces inferred requirements. Review each one — pay attention to **confidence levels**. Low-confidence items need validation with stakeholders before test design.

---

## Step 3a: QA Planning

```text
Create a QA planning strategy for this brownfield e-commerce system.
There are no existing tests, and the requirement documentation is incomplete.
```

**Prompt used:** `engine/prompts/14-qa-planning.md`

---

## Step 4: Create Test Cases

**Ask the AI:**
```text
Generate prioritized test scenarios for the order management flow.
This is a brownfield system — annotate each scenario with confidence level
based on how certain we are about the expected behavior.
```

Then convert to test cases:
```text
Convert these scenarios into structured test cases. Flag any that depend on
inferred requirements (medium/low confidence).
```

**Prompts used:** `engine/prompts/05-scenarios.md`, `engine/prompts/06-testcases.md`

---

## Steps 5-11: Same as Greenfield

From this point forward, the workflow follows the same shared steps:

5. **Risk + Confidence** — classify risk tiers and confidence levels
6. **Dual validation** — split automation vs. manual (use `engine/prompts/07-automation.md`)
7. **Execution** — run tests, capture evidence
8. **Evidence + AI Triage** — review results (use `engine/prompts/11-evidence.md`, `engine/prompts/10-triage.md`)
9. **QA Decision** — human review of findings
10. **Confirmed defects** — draft structured defects (use `engine/prompts/09-defects.md`)
11. **Release readiness** — assess ship/no-ship (use `engine/prompts/12-release.md`)

See [greenfield-walkthrough.md](greenfield-walkthrough.md) steps 5-11 for detailed examples.

---

## Brownfield-Specific Considerations

### Confidence is lower
In brownfield, many requirements are inferred. Every AI-generated artifact carries a confidence label. Low-confidence items must be validated with the team before they drive decisions.

### Story Update Loop
When a story changes, re-enter at Step 2 (context recovery). Use `engine/prompts/04-story-update.md` with both original and updated context.

### Expect gaps
Missing requirements are normal. The methodology is designed to handle uncertainty. Focus on T0/T1 risks first, then expand coverage iteratively.

---

## Key Takeaways

1. Brownfield starts with context RECOVERY, not context DEFINITION
2. Confidence levels are critical — everything inferred needs a label
3. The same 11-step workflow applies, just with higher uncertainty at the start
4. Focus on T0/T1 risks first; expand coverage as understanding grows

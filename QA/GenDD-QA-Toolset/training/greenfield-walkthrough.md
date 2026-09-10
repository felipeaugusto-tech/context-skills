# Greenfield QA Workflow — End-to-End Walkthrough

This guide walks through the complete 11-step greenfield QA workflow with a real example. Follow along in your IDE with the AI assistant.

---

## The Story

> **Feature:** User Registration with Email Verification
> Users can create an account by providing email, password, and name. After submission, they receive a verification email and must click the link to activate their account.

---

## Step 1: Product Intent Defined

**What you do:** Capture business goals, user needs, and success criteria.

**Ask the AI:**
```text
Run QA intake for this user story:
"Users can create an account by providing email, password, and name. After submission,
they receive a verification email and must click the link to activate their account.
Unverified accounts cannot access protected resources."
```

**What you get:** Intent summary, risk list, priority scenarios, coverage split, evidence needed, open questions.

**Prompt used:** `engine/prompts/01-feature-intake.md`

---

## Step 2: Validate and Structure Context

**What you do:** Validate the requirements, identify gaps, structure assumptions.

**Ask the AI:**
```text
Using the greenfield QA strategy, define how to build quality into this registration
feature from the start. Here is the feature context: [paste intake output]
```

**What you get:** A quality-first development strategy: context design, scope, test design approach, risk model, validation strategy.

**Prompt used:** `engine/prompts/02-greenfield.md`

---

## Step 3: Build Scope and QA Structure

**What you do:** Define stories, acceptance criteria, and QA structure.

This step uses the intake and strategy outputs to break the feature into testable units.

---

## Step 3a: QA Planning (if justified)

**What you do:** For new projects or high-risk features, define test data, environment, automation scope, and CI pipeline shape.

**Ask the AI:**
```text
Create a QA planning strategy for the registration feature. This is a new project
with no existing test infrastructure.
```

**Prompt used:** `engine/prompts/14-qa-planning.md`

---

## Step 4: Create Structured, Traceable Test Cases

**What you do:** Generate test scenarios, then convert to structured test cases.

**Ask the AI (scenarios):**
```text
Generate prioritized test scenarios for user registration with email verification.
Include risk tiers for each scenario.
```

**Ask the AI (test cases):**
```text
Convert these scenarios into structured test cases with preconditions, steps,
and expected results.
```

**Prompts used:** `engine/prompts/05-scenarios.md`, `engine/prompts/06-testcases.md`

---

## Step 5: Risk + Confidence Classification

**What you get:** Each scenario and test case is tagged with:
- Risk tier (T0-T3)
- Confidence level (High/Medium/Low)
- Automation candidate flag

This was done during scenario generation. Review the classification now.

---

## Step 6: Dual Validation — Automation vs Manual

**Ask the AI:**
```text
Classify which of these test cases should be automated vs. kept manual.
Provide rationale for each.
```

**Prompt used:** `engine/prompts/07-automation.md`

**Result:** Clear split — automate stable/repeatable cases, keep manual for exploratory/judgment-heavy cases.

---

## Step 7: Execution

**Automated lane:** Run the automated tests using your test framework (or Playwright MCP for E2E).

**Manual lane:** Execute exploratory and manual test cases, capturing evidence at each step.

---

## Step 8: Evidence + AI Triage

**After tests run, ask the AI:**
```text
Review this test evidence and assess what passed, what failed, and what is unclear:
[paste test output]
```

**For failures:**
```text
Triage these test failures. Classify each as: valid defect, needs verification,
duplicate, test issue, environment issue, or low value.
```

**Prompts used:** `engine/prompts/11-evidence.md`, `engine/prompts/10-triage.md`

---

## Step 9: QA Decision

Human-in-the-loop review. You decide:
- Which findings become confirmed defects
- Which need more investigation
- Which are false positives to discard

---

## Step 10: Confirmed Defects

**For valid findings, ask the AI:**
```text
Draft a structured defect report for this failure: [paste evidence]
```

**Prompt used:** `engine/prompts/09-defects.md`

**Output:** Structured defect with severity, steps to reproduce, evidence, fix-oriented acceptance criteria.

---

## Step 11: Release Readiness

**Ask the AI:**
```text
Assess release readiness for the registration feature based on this evidence:
- [paste test results summary]
- [paste open defects]
- [paste coverage status]
```

**Prompt used:** `engine/prompts/12-release.md`

**Output:** One of four outcomes — recommended, conditionally recommended, not recommended, insufficient evidence.

---

## Key Takeaways

1. Every step has a specific prompt — you never need to write QA instructions from scratch
2. The AI handles generation; you handle decisions (human-in-the-loop)
3. Evidence is captured at every step — nothing is "trust me, it works"
4. The workflow works with any tools — Cursor, VS Code, CLI, or anything that can run prompts

# Manual QA with AI — How to Create Test Cases

This guide teaches you how to instruct an AI assistant to generate structured manual test cases following the HatchWorks QA standards.

---

## What You Need

1. **A user story or feature description** — the context
2. **The QA standards loaded** — the AI needs `.cursor/rules/core-principles.md` at minimum
3. **The right prompt** — specific to what you want to produce

---

## Step 1: Feature Intake

Start by giving the AI the full context of what you are testing.

```text
Run QA intake for this user story:
[paste your user story, acceptance criteria, and any relevant context]
```

**What happens:** The AI produces an intent summary, risk list, priority scenarios, and coverage split. This is your foundation.

**Review checklist:**
- Is the intent statement specific (not generic)?
- Are risks ranked by tier (T0 > T1 > T2 > T3)?
- Are scenarios actionable (not just category names)?

---

## Step 2: Generate Scenarios

```text
Generate prioritized test scenarios for [feature name].
Group by risk tier. Include happy path, failure paths, and edge cases.
```

**What happens:** The AI produces a prioritized scenario list grouped by T0-T3.

**Review checklist:**
- Happy path included?
- At least one negative path per T0/T1 area?
- Each scenario has title, purpose, and expected behavior?

---

## Step 3: Convert to Test Cases

```text
Convert these scenarios into structured test cases with:
- Title and purpose
- Preconditions (data state, environment, user)
- Numbered steps with expected results
- Risk level and automation candidate flag
```

**What happens:** The AI produces structured test cases following the format in `knowledge/templates/test-case-templates.md`.

**Review checklist:**
- Every test case has preconditions?
- Steps are numbered and specific (not "test the feature")?
- Expected results are observable (not "it should work")?
- Each case is linked to a scenario or risk?

---

## Step 4: Classify Automation vs Manual

```text
Classify which test cases should be automated and which should stay manual.
Provide rationale for each.
```

**What happens:** The AI classifies each case with reasoning.

**Rule of thumb:**
- Automate: stable, repeatable, high-value, deterministic
- Keep manual: changing, exploratory, visual, judgment-heavy

---

## Step 5: Execute and Capture Evidence

For manual test cases, execute them and capture evidence at each step:
- Screenshots of key states
- API responses (if applicable)
- Error messages
- Any unexpected behavior

---

## Step 6: Report Results

For **passing tests:** Summarize evidence, link to the test case.

For **failures:** Use the defect drafting prompt:
```text
Draft a structured defect report for this failure:
[paste evidence — what happened, what was expected, screenshots/logs]
```

---

## Tips for Better Results

1. **Be specific with context** — the more detail in your story, the better the scenarios
2. **Review risk classification** — the AI may under/over-rate risks you know about
3. **Refine iteratively** — first pass is a draft; review and ask for adjustments
4. **Always check confidence labels** — low-confidence items need human validation
5. **Use the checklists** — they catch gaps the AI misses

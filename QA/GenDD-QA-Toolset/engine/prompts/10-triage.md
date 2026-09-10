# Defect Triage

## When to Use
Use this prompt when:
- multiple issues, failures, or defects have been identified
- reviewing outputs from automated runs
- cleaning up noisy AI-generated bugs
- preparing defects for issue tracking systems

This step ensures:
→ only meaningful issues move forward  
→ defects are correctly prioritized  
→ QA signal remains high  

---

## Instructions

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

---

## Input

Analyze the following issues, failures, or defect drafts:

[PASTE ISSUE LIST / DEFECT DRAFTS / TEST OUTPUT HERE]

---

## Output Format

For each issue, provide:

---

### Issue Title
Short, clear description

---

### Summary
Brief explanation of the issue

---

### Classification

- Valid Defect → clear issue, actionable
- Needs Verification → requires manual confirmation
- Likely Duplicate → similar to existing issue
- Test Issue → caused by test, not product
- Environment Issue → infra/config problem
- Low Value → not worth tracking

---

### Risk Level

- High → security, data integrity, critical workflows
- Medium → important workflows, integrations
- Low → cosmetic or minor

---

### Severity (Suggested)

- Critical
- High
- Medium
- Low

---

### Priority (Suggested)

Based on:
- business urgency
- release impact
- user exposure

---

### Confidence Level

- High → strong evidence, reproducible
- Medium → likely valid, needs confirmation
- Low → unclear, inconsistent, weak evidence

---

### Reproducibility

- Always
- Intermittent
- Unknown

---

### Evidence Quality

- Strong → logs, steps, reproducible
- Medium → partial evidence
- Weak → unclear or missing

---

### Recommended Action

- Create Defect
- Send to Manual Verification
- Merge with Existing Issue
- Discard
- Investigate Further

---

### Notes

Include:
- duplicate references (if any)
- possible root cause hints
- dependencies or blockers
- impacted areas

---

### Human Review Required

- Yes → high-risk, low-confidence, ambiguous
- No → clear and validated issue

---

## Output Expectations

- Be concise and decisive
- Reduce unnecessary defects
- Focus on high-impact issues
- Ensure all promoted defects are:
  - clear
  - evidence-backed
  - actionable

---

## Do Not

- Promote low-confidence issues without flagging
- Ignore duplicate detection
- Treat all issues equally
- Skip evidence validation
- Over-prioritize low-impact issues

---

## Goal

Produce a **clean, prioritized defect list** that:

- improves QA signal quality
- reduces noise in tracking systems
- accelerates developer action
- aligns with GenDD risk-first decision making
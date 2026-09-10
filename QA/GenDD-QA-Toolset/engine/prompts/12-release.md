# Release Readiness

## When to Use
Use this prompt when you need to evaluate whether a:

- feature
- story set
- sprint increment
- milestone
- release candidate

is ready to move forward.

This step determines:

→ whether there is enough evidence to support release  
→ what risks remain open  
→ what gaps still block confidence  

---

## Instructions

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

---

## Input

Evaluate release readiness based on the following information:

[PASTE TEST RESULTS / DEFECT STATUS / EVIDENCE / RISKS / CONTEXT HERE]

---

## Output Format

---

### 1. Release Status

Choose one:

- **Ready**
- **Ready with Known Risks**
- **Not Ready**
- **Insufficient Evidence**

---

### 2. Executive Summary

Provide a short summary of:

- current readiness state
- why this status was selected
- most important risk signals

---

### 3. Scope Evaluated

List what is included in this readiness decision:

- features
- workflows
- integrations
- environments
- user roles
- test coverage areas

---

### 4. Risk Coverage Assessment

Assess whether critical risks were covered.

Group by:

#### High Risk
- security
- authentication
- data integrity
- critical workflows
- release blockers

#### Medium Risk
- integrations
- secondary workflows
- operational behavior

#### Low Risk
- cosmetic
- low-impact usability
- non-critical variations

For each group, state:
- covered
- partially covered
- not covered

---

### 5. Validation Summary

Summarize what validation exists:

- automated results
- manual / exploratory results
- evidence quality
- confidence of requirements or assumptions
- regression coverage
- edge case coverage

---

### 6. Open Defects / Known Issues

Summarize current open issues:

- critical defects
- high-severity defects
- medium/low issues
- environment or test-related blockers

Indicate whether any issue is:
- release blocking
- acceptable with mitigation
- needs further review

---

### 7. Evidence Quality

Classify overall release evidence as:

- Strong → broad, clear, reproducible evidence exists
- Medium → good coverage but some gaps remain
- Weak → insufficient, fragmented, or unclear evidence

Explain why.

---

### 8. Gaps and Concerns

List what is still missing or uncertain:

- untested flows
- missing evidence
- unclear requirements
- unstable environments
- flaky automation
- unresolved risk areas

---

### 9. Recommended Next Actions

List the minimum actions needed before release, if any.

Examples:
- validate critical workflow manually
- resolve blocking defect
- capture missing evidence
- re-run failed regression
- clarify requirement
- complete security check

---

### 10. Human Review Required

State whether final human review is required.

Examples:
- Yes → high-risk issues remain, evidence gaps exist, or release is conditional
- No → evidence is strong and no major blockers remain

---

### 11. Confidence Level

Rate the confidence in this release recommendation:

- High → strong evidence, clear conclusion
- Medium → generally supported, some uncertainty
- Low → insufficient evidence or unclear risk posture

---

## Output Expectations

- Be concise but complete
- Focus on release risk, not just defect counts
- Make reasoning clear and decision-ready
- Use evidence and impact, not intuition
- Keep the output suitable for:
  - QA leads
  - engineering leads
  - product stakeholders
  - executive summaries

---

## Do Not

- Approve release based only on test completion
- Ignore missing evidence
- Understate high-risk gaps
- Treat low-severity issue count as the main signal
- Assume readiness when critical workflows are not validated

---

## Goal

Produce a **clear, evidence-based release recommendation** that:

- reflects actual risk coverage
- highlights open concerns
- supports leadership decision making
- strengthens release confidence
- aligns with GenDD’s AI-native, human-governed delivery model
# Evidence Analysis

## When to Use
Use this prompt when you have:
- logs
- screenshots
- API responses
- system outputs
- test execution results
- traces or recordings

and need to determine:
- what is actually happening
- whether there is enough evidence to support a finding
- whether the issue is product, test, data, or environment related

This step helps transform:
→ raw execution artifacts  
into  
→ meaningful QA conclusions

---

## Instructions

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

---

## Input

Analyze the following evidence:

[PASTE LOGS / SCREENSHOTS / OUTPUT / API RESPONSES / NOTES HERE]

---

## Output Format

---

### 1. Evidence Summary
Briefly describe:
- what type of evidence was reviewed
- what system behavior it appears to show

---

### 2. Confirmed Observations
List only what is directly supported by evidence.

Examples:
- response returned HTTP 500
- expected field was missing
- error message displayed after submission
- duplicate record was created

---

### 3. Likely Interpretation
Explain what the evidence most likely means.

Examples:
- likely product defect
- likely data issue
- likely environment instability
- likely automation/test failure
- insufficient evidence to conclude

---

### 4. Impact Assessment
Describe possible impact:

- blocks critical flow
- affects data integrity
- impacts user experience
- low business impact
- unknown impact

---

### 5. Evidence Quality

Classify the quality of the evidence:

- Strong → reproducible, clear logs/outputs, direct proof
- Medium → partial support, some uncertainty
- Weak → incomplete, ambiguous, or missing supporting detail

Explain why.

---

### 6. Missing Evidence
Identify what is still needed to reach a stronger conclusion.

Examples:
- reproduction steps
- screenshots
- API payloads
- timestamps
- role/user context
- environment details
- system logs

---

### 7. Recommended Next Action

Choose one:

- Create Defect
- Send to Triage
- Request More Evidence
- Reproduce Manually
- Investigate Test Stability
- Investigate Environment
- No Action Needed

Explain why.

---

### 8. Confidence Level

- High → evidence clearly supports conclusion
- Medium → likely conclusion, some uncertainty
- Low → insufficient evidence, needs validation

---

### 9. Human Review Required

- Yes → if impact is high, evidence is weak, or interpretation is uncertain
- No → if issue is well supported and low ambiguity

---

## Output Expectations

- Be objective
- Distinguish clearly between:
  - observed facts
  - likely interpretation
  - assumptions
- Keep language concise and actionable
- Make the result usable for:
  - QA review
  - triage
  - defect generation
  - release decisions

---

## Do Not

- Overstate certainty
- Treat assumptions as facts
- Ignore evidence gaps
- Jump directly to root cause without support
- Create conclusions without impact analysis

---

## Goal

Produce a **clear evidence-based analysis** that:

- improves QA signal quality
- supports better triage decisions
- prevents weak defects
- strengthens release confidence
- aligns with GenDD evidence-first delivery
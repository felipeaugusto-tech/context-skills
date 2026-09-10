# QA Output Review

## When to Use
Use this prompt when reviewing:

- AI-generated QA outputs
- scenarios
- test cases
- automation decisions
- exploratory checklists
- defects
- release assessments

This step ensures:
→ outputs meet HatchWorks QA standards  
→ quality is consistent and usable  
→ weak or incomplete work is corrected early  

---

## Instructions

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

---

## Input

Review the following QA output:

[PASTE QA OUTPUT HERE]

---

## Output Format

---

### 1. Overall Assessment

Provide a high-level evaluation:

- Strong → ready to use
- Acceptable → minor improvements needed
- Weak → requires significant rework

---

### 2. Intent Alignment

- Is the feature intent clearly understood?
- Is the user goal reflected correctly?

Result:
- Clear
- Partially Clear
- Unclear

---

### 3. Risk Coverage

Evaluate whether risks are:

- identified
- prioritized
- aligned with business impact

Result:
- Strong
- Partial
- Weak

---

### 4. Traceability

Check whether outputs are connected:

- intent → scenarios
- scenarios → test cases
- test cases → evidence
- defects linked to context

Result:
- Complete
- Partial
- Missing

---

### 5. Clarity and Usability

Assess whether the output is:

- easy to understand
- executable by a junior contributor
- free of ambiguity

Result:
- Clear
- Some ambiguity
- Unclear

---

### 6. Testability

Evaluate:

- are steps reproducible?
- are expected results explicit?
- are preconditions defined?

Result:
- Strong
- Partial
- Weak

---

### 7. Evidence Awareness

Check whether the output:

- defines evidence requirements
- supports validation with proof

Result:
- Strong
- Partial
- Missing

---

### 8. Automation vs Manual Balance

Assess whether:

- automation decisions are appropriate
- manual/exploratory coverage is considered

Result:
- Balanced
- Needs Adjustment
- Incorrect

---

### 9. Confidence Awareness

Check if:

- assumptions are clearly identified
- confidence levels are used appropriately

Result:
- Strong
- Partial
- Missing

---

### 10. Issues Identified

List specific problems:

- missing scenarios
- unclear steps
- weak expected results
- lack of risk prioritization
- missing evidence requirements
- overcomplicated or vague outputs

---

### 11. Recommendations

Provide actionable improvements:

- what to fix
- what to add
- what to simplify
- what to remove

---

### 12. Revised Output (Optional but Recommended)

Provide a corrected or improved version of the QA output if needed.

---

### 13. Human Review Required

- Yes → high-risk or unclear outputs
- No → acceptable for execution

---

## Output Expectations

- Be constructive and actionable
- Focus on improving usability and quality
- Avoid generic feedback
- Ensure recommendations are practical

---

## Do Not

- Approve weak or unclear outputs
- Ignore missing risk coverage
- Skip traceability checks
- Provide vague feedback without corrections

---

## Goal

Produce a **high-quality QA review** that:

- ensures alignment with HatchWorks QA standards
- improves output quality before execution
- reduces downstream errors and rework
- enables consistent QA practices across teams
- supports GenDD’s structured, AI-assisted delivery model
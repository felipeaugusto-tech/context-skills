# Exploratory & Manual Testing

## When to Use
Use this prompt when:

- a scenario or feature is **not suitable for automation**
- behavior is **unclear, evolving, or unstable**
- validation requires **human judgment**
- performing **exploratory testing**

This step focuses on:
→ uncovering unknown risks  
→ validating real user behavior  
→ identifying unexpected issues  

---

## Instructions

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

---

## Input

Analyze the following feature, scenario, or test cases:

[PASTE FEATURE / SCENARIOS / TEST CASES HERE]

---

## Output Format

---

### 1. Intent Reminder
Summarize:
- what the feature is supposed to do
- expected user outcome

---

### 2. Key Risk Areas

Identify areas to explore:

- critical workflows
- data handling
- permissions / roles
- integrations
- error handling
- edge cases

Group into:
- High Risk
- Medium Risk
- Low Risk

---

### 3. Exploratory Checklist

Provide a structured checklist of actions to perform:

#### Core Flow Validation
- Validate happy path behavior
- Try variations of normal usage

#### Negative Testing
- Invalid inputs
- Missing data
- Incorrect sequences
- Boundary values

#### Edge Cases
- extreme values
- unusual user behavior
- concurrency or repeated actions

#### Permissions / Roles (if applicable)
- different user roles
- unauthorized actions

#### Data Validation (if applicable)
- data persistence
- duplication
- corruption scenarios

#### Integration Behavior (if applicable)
- external dependencies
- failure handling

#### UI / UX (if applicable)
- layout consistency
- usability issues
- responsiveness

---

### 4. Exploration Ideas

Suggest additional ways to test beyond defined cases:

- “What happens if…”
- “Try breaking the flow by…”
- “Simulate real-world misuse…”

---

### 5. Evidence to Capture

Define what must be recorded:

- screenshots
- logs
- API responses
- timestamps
- reproduction steps
- system outputs

---

### 6. Bug Detection Signals

List indicators that should trigger a defect:

- unexpected behavior
- inconsistent results
- unclear error messages
- system crashes
- incorrect data handling

---

### 7. Follow-up Recommendations

Identify:

- areas that should later be automated
- scenarios needing clearer requirements
- risks that require deeper validation

---

### 8. Confidence Level

- High → well understood feature
- Medium → some ambiguity
- Low → unclear behavior, high exploration needed

---

## Output Expectations

- Keep checklist **clear and actionable**
- Focus on **real user behavior**
- Prioritize **high-risk exploration**
- Make it usable by **non-QA contributors**

---

## Do Not

- turn this into rigid test cases
- over-structure exploratory work
- ignore risk prioritization
- skip evidence requirements

---

## Goal

Produce a **practical exploratory testing checklist** that:

- uncovers hidden issues
- complements automated testing
- strengthens QA coverage
- aligns with GenDD iterative validation
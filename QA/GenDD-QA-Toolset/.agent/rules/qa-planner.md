---
description: QA Planner — routing table, verification checklists, anti-patterns for all QA tasks. This is the execution entry point for the HatchWorks QA Operating Model. Standards are loaded automatically as sibling rules in this directory.
alwaysApply: true
---

# QA Planner

## How to Execute

- **Prompts:** `engine/prompts/` — the skill routing table below maps tasks to specific prompt files.
- **Templates:** `knowledge/templates/` — worked examples of test cases, defects, release assessments.
- **Stack guidance:** `knowledge/stacks/` — language-specific tooling and CI profiles.
- **Connectors (optional):** `engine/connectors/playwright-mcp.md` (browser automation), `engine/connectors/xray.md` (test management).
- **CI automation:** `engine/ci/qa-orchestrator.py` runs automated pipeline triage in this order: **11-evidence → 10-triage → 09-defects → 12-release** (not numeric order). It does **not** run **13-review** — that prompt is for IDE/human quality review of AI-generated QA artifacts. See [engine/ci/README.md](../../engine/ci/README.md).

**Rules:** Always use prompts from `engine/prompts/`. Include confidence labels (High/Medium/Low) on every inferred item. Run the verification checklists below AFTER generating any output.

---

## Quick Start

**Feature intake:**
```text
"Run QA intake for this user story: [paste story]"
```

**Generate test scenarios:**
```text
"Generate prioritized test scenarios for the checkout flow"
```

**Create test cases:**
```text
"Convert these scenarios into structured test cases"
```

**Triage failures:**
```text
"Triage these test failures from the CI run: [paste results]"
```

**Assess release readiness:**
```text
"Assess release readiness for v2.1 based on this evidence"
```

**Identify test gaps:**
```text
"Analyze this codebase and identify test coverage gaps prioritized by risk tier"
```

---

## Quick Reference

| Task | What You Get | Prompt File |
|------|-------------|-------------|
| Feature/story intake | Intent, risks, scenarios, coverage split | `engine/prompts/01-feature-intake.md` |
| Greenfield QA strategy | Quality-first development workflow | `engine/prompts/02-greenfield.md` |
| Brownfield QA strategy | Quality recovery and control system | `engine/prompts/03-brownfield.md` |
| Story update | Refreshed coverage after scope change | `engine/prompts/04-story-update.md` |
| Scenario generation | Prioritized test scenarios by risk tier | `engine/prompts/05-scenarios.md` |
| Test case generation | Structured, traceable test cases | `engine/prompts/06-testcases.md` |
| Automation assessment | Automation vs. manual classification | `engine/prompts/07-automation.md` |
| Manual/exploratory | Exploratory validation checklists | `engine/prompts/08-manual.md` |
| Defect drafting | Structured bug reports from failures | `engine/prompts/09-defects.md` |
| Defect triage | Categorized, prioritized issue list | `engine/prompts/10-triage.md` |
| Evidence review | Interpretation of test results and logs | `engine/prompts/11-evidence.md` |
| Release readiness | Ship/no-ship recommendation with evidence | `engine/prompts/12-release.md` |
| AI output review | Quality-check AI-generated QA artifacts | `engine/prompts/13-review.md` |
| QA planning | Test data, environment, automation, CI strategy | `engine/prompts/14-qa-planning.md` |
| Test gap analysis | Coverage gaps, risk heat map, remediation roadmap | `engine/prompts/15-test-gap-analysis.md` |

---

## How It Works

```text
User Request
    |
    v
+-------------------------------------------------------+
| 1. LOAD CONTEXT                                       |
|    - Always load: .cursor/rules/core-principles.md               |
|    - Load by task:                                    |
|      Risk/triage? -> .cursor/rules/risk-and-confidence.md        |
|      Test design/defects? -> .cursor/rules/manual-qa-standards.md|
|      Writing tests? -> .cursor/rules/automation-qa-standards.md  |
|      Test gaps? -> .cursor/rules/automation-qa-standards.md      |
|      Release? -> .cursor/rules/release-and-governance.md         |
+-------------------------------------------------------+
    |
    v
+-------------------------------------------------------+
| 2. SELECT PROMPT                                      |
|    - Use the routing table above                      |
|    - Load the task-specific prompt from engine/prompts/      |
+-------------------------------------------------------+
    |
    v
+-------------------------------------------------------+
| 3. GENERATE OUTPUT                                    |
|    - Follow the prompt structure                      |
|    - Use templates from knowledge/templates/          |
|    - Include confidence labels on all inferred items  |
+-------------------------------------------------------+
    |
    v
+-------------------------------------------------------+
| 4. VALIDATE (run checklists below)                    |
|    - Check output against verification checklist      |
|    - Fix any gaps before presenting to user           |
+-------------------------------------------------------+
    |
    v
QA Deliverable Ready
```

---

## Recommended Usage Order

### Greenfield (new system)
1. `engine/prompts/01-feature-intake.md` — capture intent, risks, and Gherkin ACs
2. `engine/prompts/02-greenfield.md` — define quality-first strategy
3. `engine/prompts/14-qa-planning.md` — proactive planning (once per project/feature area)
4. `engine/prompts/05-scenarios.md` — generate scenarios
5. `engine/prompts/06-testcases.md` — create test cases
6. `engine/prompts/07-automation.md` — classify automation vs. manual
7. `engine/prompts/15-test-gap-analysis.md` — identify coverage gaps before release
8. `engine/prompts/09-defects.md` — draft defects from failures
9. `engine/prompts/12-release.md` — assess release readiness

### Brownfield (existing system)
1. `engine/prompts/03-brownfield.md` — recover context and establish governance
2. `engine/prompts/15-test-gap-analysis.md` — identify existing coverage gaps
3. `engine/prompts/14-qa-planning.md` — proactive planning (once per project/feature area)
4. `engine/prompts/05-scenarios.md` — generate scenarios
5. `engine/prompts/06-testcases.md` — structured cases from scenarios (before or in parallel with deep exploratory work)
6. `engine/prompts/08-manual.md` — exploratory validation checklists
7. `engine/prompts/07-automation.md` — classify automation vs. manual
8. `engine/prompts/11-evidence.md` — review evidence
9. `engine/prompts/10-triage.md` — triage findings
10. `engine/prompts/12-release.md` — assess release readiness

### Story change
1. `engine/prompts/04-story-update.md` — refresh coverage
2. `engine/prompts/05-scenarios.md` — regenerate scenarios
3. `engine/prompts/06-testcases.md` — update test cases
4. `engine/prompts/12-release.md` — reassess readiness

---

## Verification Checklists

Run these AFTER generating output. Fix any failures before presenting to the user.

### Intent and Risk
- [ ] Intent statement is specific (not generic "improve quality")
- [ ] Risks are ranked by tier (T0 > T1 > T2 > T3)
- [ ] At least one T0/T1 risk is identified if the feature touches auth, payments, or data
- [ ] Each risk has a concrete scenario, not just a category name

### Test Scenarios
- [ ] Scenarios are grouped by risk tier
- [ ] Happy path is included
- [ ] At least one negative/failure path per T0/T1 area
- [ ] Each scenario has: title, purpose, and expected behavior
- [ ] No duplicate scenarios

### Test Cases
- [ ] Every test case has: title, purpose, preconditions, steps, expected result
- [ ] Steps are numbered and specific (not "test the feature")
- [ ] Preconditions include data state and environment assumptions
- [ ] Each test case is linked to a scenario or risk
- [ ] Automation candidate is flagged (yes/no with rationale)

### Defect Reports
- [ ] Title is specific (not "bug found")
- [ ] Steps to reproduce are numbered and repeatable
- [ ] Expected vs. actual result are both stated
- [ ] Evidence is attached or referenced (logs, screenshots, traces)
- [ ] Severity and priority are assigned
- [ ] Confidence level is stated (High/Medium/Low)

### Triage
- [ ] Each finding is classified: valid defect, needs verification, likely duplicate, test issue, environment issue, or low value
- [ ] Duplicates are identified and linked
- [ ] Human review is flagged for high-risk or low-confidence items
- [ ] Recommended action is stated for each finding

### Test Gap Analysis
- [ ] Test inventory covers all test layers (unit, integration, E2E)
- [ ] Critical business logic areas are identified and mapped to risk tiers
- [ ] Gap matrix compares should-have vs. currently-has for each component
- [ ] Every inferred coverage assessment has a confidence label
- [ ] Recommendations are prioritized by risk tier (T0/T1 gaps first)
- [ ] Each recommendation includes business impact and estimated effort
- [ ] Implementation roadmap has concrete sprint assignments
- [ ] Manual-only test coverage is documented (not just automated)

### Release Readiness
- [ ] All T0 and T1 areas have evidence
- [ ] Open critical defects are listed
- [ ] Flaky test rate is noted
- [ ] One of four outcomes is stated: recommended, conditional, not recommended, insufficient evidence
- [ ] Items requiring human approval are flagged

### All Outputs
- [ ] Confidence labels (High/Medium/Low) on every inferred item
- [ ] Traceability: output links back to intent, story, or requirement
- [ ] Language is clear enough for a junior developer
- [ ] No tool-specific jargon (no Jira, Xray, Mori references)

---

## Anti-Patterns

| Avoid | Why | Do Instead |
|-------|-----|-----------|
| Skip risk assessment | You test the wrong things first | Always classify risks by tier before generating scenarios |
| Test everything equally | Wastes effort on low-impact areas | Focus depth on T0/T1, lighter coverage on T2/T3 |
| Create defects without evidence | Pollutes the issue tracker | Attach logs, screenshots, or traces to every defect |
| Promote low-confidence findings | Creates noise and erodes trust | Flag for manual verification instead |
| Use vague test steps | Tests are unreproducible | Write numbered, specific actions with expected results |
| Ignore flaky tests | Flake erodes CI signal | Quarantine, investigate, fix or remove |
| Generate freeform QA outputs | Inconsistent quality | Always use the prompt library in `engine/prompts/` |
| Treat AI output as final | AI may hallucinate or miss context | Run verification checklists, flag for human review |
| Skip story update loop | Outdated tests give false confidence | Re-enter at Step 2 when stories change |
| Skip test gap analysis | Unknown coverage gaps persist to release | Run gap analysis before major releases or after brownfield recovery |

---

## References

Templates and worked examples live in `knowledge/templates/`:

| Template | Purpose |
|----------|---------|
| [test-case-templates.md](../../knowledge/templates/test-case-templates.md) | Standard test case format with worked examples |
| [defect-templates.md](../../knowledge/templates/defect-templates.md) | Defect report format with worked examples |
| [release-templates.md](../../knowledge/templates/release-templates.md) | Release readiness format with worked examples |
| [testing-standards.md](../../knowledge/templates/testing-standards.md) | Customizable per-repo testing standards (MUST/SHOULD/MAY) |


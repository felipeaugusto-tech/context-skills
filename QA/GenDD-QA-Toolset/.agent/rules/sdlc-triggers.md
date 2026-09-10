---
description: SDLC phase triggers (T1-T8) — when requirements, design, development, testing, CI/CD, release, operations, and iteration phases feed QA activity. Load when mapping SDLC events to QA actions.
globs:
---

# SDLC Triggers for the QA Process

## Purpose

Each phase of the Software Development Life Cycle produces **augmentative information** — data that enriches, supplements, or triggers QA activity. This document defines **8 triggers**, one per SDLC phase, that describe exactly when and how that information flows into the GenDD QA pipeline.

QA leads use this document to ensure no phase operates in isolation from quality. Every trigger specifies:

- **When it fires** — the trigger condition
- **What data flows** — the specific augmentative information
- **Where it enters the QA workflow** — step numbers from [workflows.md](workflows.md)
- **What QA should do** — action and which prompt to run
- **What QA artifact is produced** — expected output
- **Confidence treatment** — whether AI outputs need human review at this trigger

## Quick reference

| Trigger | SDLC Phase | Condition | QA Workflow Steps Fed | Primary Prompt |
|---------|-----------|-----------|----------------------|----------------|
| T1 | Requirements | Story/requirement created or updated | Steps 1–2 (Intent + Context validation) | `engine/prompts/01-feature-intake.md` |
| T2 | Design | Architecture, API contracts, data models change | Steps 2–3 (Context + Scope) | `engine/prompts/02-greenfield.md` / `engine/prompts/03-brownfield.md` |
| T3 | Development | Code committed, PR opened | Steps 4–5 (Test design + Risk + Confidence) | `engine/prompts/05-scenarios.md`, `engine/prompts/06-testcases.md`, `engine/prompts/07-automation.md` |
| T4 | Testing | Test execution completes | Steps 7A–8 (Execution + Evidence + Triage) | `engine/prompts/11-evidence.md`, `engine/prompts/09-defects.md` |
| T5 | CI/CD | Pipeline completes | Steps 8–9 (Evidence + Triage, QA Decision) | `engine/prompts/10-triage.md` |
| T6 | Release | Release candidate tagged, deploy initiated | Step 11 (Release readiness) | `engine/prompts/12-release.md` |
| T7 | Operations | Production incident, alert, user feedback | Feeds back to Step 5 (Risk + Confidence) + Defect Governance | `engine/prompts/03-brownfield.md`, `engine/prompts/09-defects.md` |
| T8 | Iteration | Existing story updated, scope changed | Story update loop (re-enter at Step 2) | `engine/prompts/04-story-update.md` |

---

## T1 — Requirements Phase

### When it fires

A new user story, requirement, or acceptance criteria document is created or materially updated in an issue tracker, documentation platform, or project file.

### What data flows

- Business intent statement (what, who, success criteria, main flow)
- Acceptance criteria (Given/When/Then or equivalent)
- User flow descriptions
- Stakeholder needs and constraints
- Non-functional expectations mentioned in the story

### Where it enters the QA workflow

- **Greenfield step 1–2:** Product intent defined, context validated and structured
- **Brownfield step 2–3:** Context recovered, requirements reconstructed

### What QA should do

1. Run the **Feature Intake Prompt** (`engine/prompts/01-feature-intake.md`) with the story/requirement pasted as context.
2. Capture the intent summary, top risks, priority scenarios, and suggested coverage split.
3. Validate the structured context (greenfield) or reconcile with existing knowledge (brownfield).

### What QA artifact is produced

- Intent summary
- Risk list
- Initial scenario list
- Open questions or unclear assumptions

### Confidence treatment

AI-generated intent summaries and risk lists are **drafts**. QA or product owner must review the intent statement for accuracy. Low-confidence inferred requirements must be flagged and validated with stakeholders before test design begins.

---

## T2 — Design Phase

### When it fires

Architecture documents, API contracts (OpenAPI/Swagger), database schemas, data models, or system design artifacts are created or changed.

### What data flows

- System architecture diagrams and component boundaries
- API schemas and endpoint contracts
- Data models, ERDs, migration plans
- Integration points and third-party dependencies
- Non-functional requirements (performance targets, security constraints, SLAs)

### Where it enters the QA workflow

- **Greenfield steps 2–3:** Context validated and structured, scope defined
- **Brownfield steps 2–4:** Context recovered, requirements reconstructed, scope defined

### What QA should do

1. Run the **Greenfield QA Prompt** (`engine/prompts/02-greenfield.md`) or **Brownfield QA Prompt** (`engine/prompts/03-brownfield.md`) with the design artifacts as input.
2. Identify testability gaps: are there stable selectors? Visible API contracts? Controllable test data? (per Testability and Observability in manual-qa-standards.md).
3. Map API contracts to integration test expectations.
4. Capture NFR expectations that will become non-functional test triggers later (Non-Functional QA Expectations in manual-qa-standards.md).
5. **If this is a new project, new stack, or Tier 0/1 area:** Run the **QA Planning Strategy Prompt** (`engine/prompts/14-qa-planning.md`) to produce proactive planning deliverables (test data strategy, environment strategy, automation scope, CI pipeline shape). This corresponds to workflow Step 3a and QA Readiness — Proactive Planning in risk-and-confidence.md.

### What QA artifact is produced

- Updated QA strategy reflecting design decisions
- Testability assessment (gaps and recovery plan if needed)
- API contract test expectations
- NFR test thresholds (response times, throughput, security boundaries)
- **When justified:** Test data strategy, environment strategy, automation scope definition, CI pipeline shape (see QA Readiness — Proactive Planning in risk-and-confidence.md for proportionality guidance)

### Confidence treatment

Design-derived test expectations are generally **high confidence** when contracts are formal (OpenAPI specs). Inferred integration behavior from informal diagrams is **medium confidence** and needs developer confirmation.

---

## T3 — Development Phase

### When it fires

Code is committed to a feature branch, a pull request is opened or updated, or a code review surfaces testability-relevant changes.

### What data flows

- Code diffs (new files, changed logic, deleted tests)
- New dependencies introduced
- Testability signals: data-testid attributes, API error handling, logging, observable contracts
- Changed business logic paths
- Developer notes or PR descriptions

### Where it enters the QA workflow

- **Steps 4–6:** Test case creation, Risk + Confidence, Coverage split

### What QA should do

1. Run the **Scenario Generation Prompt** (`engine/prompts/05-scenarios.md`) with the PR diff or feature description.
2. Run the **Test Case Generation Prompt** (`engine/prompts/06-testcases.md`) to convert scenarios into structured test cases.
3. Run the **Automation Candidate Prompt** (`engine/prompts/07-automation.md`) to classify what should be automated vs. manual.
4. Verify that new code preserves testability (stable selectors, contracts, error detail).

### What QA artifact is produced

- Prioritized scenario list (grouped by risk tier)
- Structured test cases (per Required Test Case Structure in manual-qa-standards.md)
- Automation vs. manual classification with rationale

### Confidence treatment

AI-generated scenarios from code diffs are **medium confidence** — the AI sees what changed but may miss why. Human review is required to validate business relevance. Automation classification is **medium confidence** and needs QA approval before committing automation effort.

---

## T4 — Testing Phase

### When it fires

A test suite execution completes (automated or manual), producing results, coverage reports, failure logs, screenshots, or traces.

### What data flows

- Test pass/fail results (JUnit XML, TRX, coverage reports)
- Failure logs, stack traces, error messages
- Screenshots, Playwright traces, recordings
- Coverage deltas (lines, branches, new vs. regression)
- Flaky test indicators

### Where it enters the QA workflow

- **Steps 7A–8:** Automated execution, Exploratory execution, Evidence + AI Triage

### What QA should do

1. Run the **Evidence Review Prompt** (`engine/prompts/11-evidence.md`) with test output pasted as context.
2. For failures, run the **Defect Drafting Prompt** (`engine/prompts/09-defects.md`) to produce structured defect drafts.
3. Assess whether findings are strong enough for defect creation (per principle 9 — Automated findings require human verification when needed in core-principles.md).
4. Quarantine suspected flaky tests per Automation Governance in automation-qa-standards.md.

### What QA artifact is produced

- Evidence summary (what passed, what failed, what is unclear)
- Defect drafts with evidence bundles
- Flaky test quarantine list
- Follow-up actions (manual verification needed, additional evidence required)

### Confidence treatment

Automated test results are **high confidence** for deterministic pass/fail. AI-drafted defects from failures are **medium confidence** — they must not become confirmed defects without human confirmation when the finding is ambiguous, environment-sensitive, or potentially flaky.

---

## T5 — CI/CD Phase

### When it fires

A CI/CD pipeline run completes (success or failure), producing aggregated build and test results.

### What data flows

- Build success/failure status
- Aggregated test results across suites (unit, integration, E2E)
- Deployment logs and environment state
- Security scan results (dependency audit, SAST)
- Performance benchmark results (if run in CI)

### Where it enters the QA workflow

- **Steps 8–9:** Evidence + AI Triage, QA Decision

### What QA should do

**Manual:**
1. Run the **Defect Triage Prompt** (`engine/prompts/10-triage.md`) with the aggregated pipeline results.

2. Separate product bugs from test bugs, environment issues, and flake.
3. Identify probable duplicates and blockers.
4. Determine which findings route to the manual verification lane vs. direct defect creation.

**Automated (in CI/CD):**
Use `engine/ci/qa-orchestrator.py` to automate the entire triage chain. The orchestrator reads test results (JUnit XML or TRX), coverage, and logs from the pipeline, then chains four QA-GenDD prompts through an LLM API: evidence review → defect triage → defect drafting → release readiness.

Pass `--stack` (python, typescript, java, go, cpp, dotnet) to load a stack profile from `knowledge/stacks/` that injects framework-specific context into the LLM prompts and selects the correct artifact parser. See [engine/ci/README.md](../../engine/ci/README.md) for setup, per-stack CI examples, and usage.

### What QA artifact is produced

- Triage summary (categorized findings)
- Recommended actions per finding (create bug, verify manually, gather evidence, ignore)
- Pipeline health assessment
- Blockers and dependency tickets if needed
- **When using the CI orchestrator:** `qa-summary.md`, `defects.json`, and `release-assessment.json` are written to the output directory

### Confidence treatment

CI results are **high confidence** for build pass/fail. AI triage of aggregated failures is **medium confidence** — particularly for multi-failure runs where root cause may be shared. QA must review the triage before acting on recommendations.

---

## T6 — Release Phase

### When it fires

A release candidate is tagged, deployment to staging or production is initiated, or a release decision is requested.

### What data flows

- Release notes and changelog
- Environment health status (staging or production)
- Open defect summary (critical, high, medium, low counts)
- Evidence gap analysis (what has not been tested)
- Stakeholder sign-off status
- Security and performance validation status

### Where it enters the QA workflow

- **Step 11:** Release readiness (both greenfield and brownfield)

### What QA should do

1. Run the **Release Readiness Prompt** (`engine/prompts/12-release.md`) with the release context.
2. Evaluate against the release readiness checklist (Release Readiness Rules in release-and-governance.md): risk coverage, requirement confidence, automated results, manual coverage, open defects, flaky rate, environment confidence, stakeholder validation, NFR concerns.
3. Produce one of four outcomes: Ready, Ready with known risks, Not ready, Insufficient evidence.

### What QA artifact is produced

- Release readiness assessment with status
- Key risks and coverage gaps
- Required next steps before release
- Human review items flagged for approval

### Confidence treatment

Release recommendations are **always human-approved**. AI may draft the assessment, but the final release recommendation is a mandatory human gate (Minimum Human Approval Gates in release-and-governance.md). No release proceeds on AI recommendation alone.

---

## T7 — Operations Phase

### When it fires

A production incident occurs, a monitoring alert fires, user feedback or support tickets surface quality issues, or production telemetry reveals anomalies.

### What data flows

- Incident reports and severity classification
- Production error logs and telemetry
- User feedback and support ticket patterns
- Performance degradation signals
- Security alerts

### Where it enters the QA workflow

- Feeds back to **Risk Tiering** (Risk Tiering Standard (T0–T3) in risk-and-confidence.md) — production incidents may elevate risk tiers
- Feeds into **Defect Governance** (Defect Governance in manual-qa-standards.md) — production bugs follow the same defect structure
- May trigger **Brownfield context recovery** if the incident reveals undocumented behavior

### What QA should do

1. Run the **Brownfield QA Prompt** (`engine/prompts/03-brownfield.md`) if the incident reveals behavior not captured in existing test coverage.
2. Run the **Defect Drafting Prompt** (`engine/prompts/09-defects.md`) for confirmed production bugs.
3. Update risk tier classifications if the incident changes the risk profile of a component.
4. Assess whether existing test coverage would have caught the issue and create gap-filling scenarios if not.

### What QA artifact is produced

- Production defect report (linked to incident)
- Risk tier adjustment recommendations
- Test coverage gap analysis
- Regression test additions for the affected area

### Confidence treatment

Production incidents are **high confidence** — they represent real user impact. However, AI-inferred root cause from logs is **medium confidence** and needs engineering confirmation. Risk tier adjustments based on a single incident are **medium confidence** — patterns across incidents are stronger signals.

---

## T8 — Iteration Phase

### When it fires

An existing story or requirement is updated, scope is changed, a bug fix alters acceptance criteria, or a feature pivot changes expected behavior.

### What data flows

- Updated requirements and changed acceptance criteria
- Diff between original and updated story
- Fix-oriented acceptance criteria from resolved defects
- Changed scope boundaries
- New risks introduced by the change

### Where it enters the QA workflow

- **Story update loop:** Re-enter at Step 2 (Context validation)

### What QA should do

1. Run the **Story Update Loop Prompt** (`engine/prompts/04-story-update.md`) with both original and updated context.
2. Re-enter the workflow at context recovery (brownfield) or validation (greenfield).
3. Identify which existing scenarios remain valid, which must be updated, and which are now obsolete.
4. Update or regenerate affected tests.
5. Re-run impacted test suites and review evidence.

### What QA artifact is produced

- Updated intent summary reflecting the change
- Scenario delta (valid, updated, obsolete)
- Updated test cases
- Re-execution evidence
- Defect updates (closed, updated, or new)

### Confidence treatment

The change itself is **high confidence** (it came from product/engineering). AI-generated scenario deltas are **medium confidence** — the AI may miss implicit dependencies between the changed story and other features. QA must review the delta for completeness, especially for Tier 0 and Tier 1 areas.

---

## Cursor IDE automation

Five of these triggers are automated via Cursor IDE hooks in `.cursor/hooks.json`. See `.cursor/hooks/` for the implementation scripts.

| Cursor Hook | Event | Maps to SDLC Trigger | Behavior |
|-------------|-------|---------------------|----------|
| Session init | `sessionStart` | All (T1–T8) | Injects QA standards context at session start |
| Test file edit | `afterFileEdit` | T3, T4 | Reminds agent of test structure rules when test files are edited |
| Test evidence | `afterShellExecution` | T4, T5 | Prompts evidence review after test commands complete |
| Story update | `afterFileEdit` | T8 | Triggers story update loop check when requirement files change |
| Release gate | `beforeShellExecution` | T6 | Asks for release readiness confirmation before deploy commands |

---

## Related documents

- [QA Core Principles](core-principles.md) — Foundation principles referenced by trigger definitions
- [QA Workflows](workflows.md) — Greenfield and brownfield step numbers referenced above
- [QA Planner](qa-planner.md) — Routing table and prompts invoked at each trigger
- [Artifact templates](../../knowledge/templates/) — Worked examples of QA outputs

# Getting Started with the HatchWorks QA Operating Model

## What Is This?

The HatchWorks QA Operating Model is a methodology for running QA with AI assistance. It works with any tools your team has available — the methodology stays the same whether you use Cursor, Claude, Playwright, Xray, or something else entirely.

**Three things you need to do QA with AI:**
1. **Context** — what is the system, what changed, what are the requirements
2. **Standards** — what are the QA rules (risk tiers, evidence requirements, test structure)
3. **Prompts** — how to instruct the AI to produce specific QA outputs

---

## Core Principles

The foundation for every QA activity lives in `.cursor/rules/core-principles.md` (loaded automatically). Ten principles govern all work:

1. **Risk-first** — prioritize testing by business risk, not by feature count
2. **Not automated does not mean not tested** — manual and exploratory validation count
3. **Evidence over opinion** — all decisions backed by logs, screenshots, traces, or test outputs
4. **Human-in-the-loop** — AI generates and recommends; humans approve high-risk decisions
5. **Traceability is mandatory** — link intent to requirements to tests to evidence to defects
6. **Testability is part of quality** — no selectors, no logging, no contracts = not test-ready
7. **QA must accelerate delivery** — reduce regression, duplicate bugs, flaky noise, and manual waste
8. **Keep outputs simple** — clear, short, reusable, understandable by a junior developer
9. **Automated findings require human verification when needed** — ambiguous or low-confidence findings go to manual verification before defect creation
10. **Start with intent** — before writing tests, define what is being built, for whom, and what success looks like

Every AI-generated or inferred artifact must carry a **confidence score** (High / Medium / Low). Low-confidence items must not drive release decisions without human review.

---

## The 11-Step Workflow

Both greenfield and brownfield projects follow the same 11-step pipeline. The first four steps differ based on whether you are building new (greenfield) or recovering context from an existing system (brownfield). Steps 5-11 are shared.

```
Steps 1-4 (differ by type)         Steps 5-11 (shared)
─────────────────────────           ───────────────────────────────────
Greenfield:                         5. Risk + Confidence
  1. Product intent defined         6. Dual validation (auto vs manual)
  2. Validate and structure         7. Execution
  3. Build scope + QA structure     8. Evidence + AI Triage
  3a. QA Planning (if justified)    9. QA Decision (human gate)
  4. Create test cases             10. Confirmed defects
                                   11. Release readiness
Brownfield:
  1. MVP exists
  2. Recover and structure context
  2b. Identify test coverage gaps
  3. Build scope + QA structure
  3a. QA Planning
  4. Create test cases
```

The key insight: **greenfield defines truth from intent; brownfield discovers truth from the existing system.** Both converge to the same risk-driven decision engine.

See `.cursor/rules/workflows.md` for the canonical step tables and comparison matrix.

---

## How the Repository Is Organized

```
Layer 1: INTERFACE (.cursor/rules/)   Planner & standards-creator rules
Layer 2: ENGINE (engine/)             What executes the work + automation
Agent Store: KNOWLEDGE (knowledge/)   Standards the AI reads at runtime
Human Store: TRAINING (training/)     Guides for humans to learn the methodology
```

### Layer 1: Interface (`.cursor/rules/`)

The entry point for all QA tasks. Two rule files drive task routing and project setup:
- **QA Planner** (`.cursor/rules/qa-planner.md`) — routes any QA task to the right prompt, with verification checklists and anti-patterns. Always loaded.
- **QA Standards Creator** (`.cursor/rules/qa-standards-creator.md`) — generates stack-specific QA files for your project

Supporting rules loaded by task:

| Rule | When to Load | Audience |
|------|-------------|----------|
| `core-principles.md` | Every QA session (always) | Everyone |
| `developer-standards.md` | Writing/reviewing code, PRs | Developers |
| `qa-lead-playbook.md` | Pipeline governance, triage, release | QA leads |
| `risk-and-confidence.md` | Risk assessment, triage, planning | QA leads, reviewers |
| `manual-qa-standards.md` | Test design, defects, manual validation | QA engineers |
| `automation-qa-standards.md` | Writing tests, automation, CI/CD | Developers, QA automation |
| `release-and-governance.md` | Release decisions, governance | Leads, stakeholders |
| `workflows.md` | Planning or executing a QA workflow | Everyone |
| `sdlc-triggers.md` | Mapping SDLC phases to QA actions | QA leads |

### Layer 2: Engine (`engine/`)

What actually does the work when triggered by Layer 1:
- **Prompts** (`engine/prompts/`) — 15 task-specific prompts (see the full table below)
- **Connectors** (`engine/connectors/`) — optional tool integrations (Playwright MCP, Xray)
- **CI** (`engine/ci/`) — automated AI triage pipeline for CI/CD

### Knowledge (`knowledge/`)

Reference data the AI loads at runtime:

**Stack profiles** (`knowledge/stacks/`) — 6 languages, each with a `.yml` CI profile and a `-testing-guidance.md` companion:

| Stack | Files |
|-------|-------|
| Python | `python.yml`, `python-testing-guidance.md` |
| TypeScript | `typescript.yml`, `typescript-testing-guidance.md` |
| Java | `java.yml`, `java-testing-guidance.md` |
| Go | `go.yml`, `go-testing-guidance.md` |
| C++ | `cpp.yml`, `cpp-testing-guidance.md` |
| .NET | `dotnet.yml`, `dotnet-testing-guidance.md` |

**Templates** (`knowledge/templates/`) — output format templates with worked examples:

| Template | Purpose |
|----------|---------|
| `test-case-templates.md` | Standard test case format |
| `defect-templates.md` | Defect report format |
| `release-templates.md` | Release readiness format |
| `testing-standards.md` | Customizable per-repo testing standards (MUST/SHOULD/MAY) |

### Training (`training/`)

Human-readable guides for learning the methodology — you are reading one now.

---

## The Prompt Library

All QA execution goes through the 15 prompts in `engine/prompts/`. Never generate freeform QA outputs — always use the prompt library.

| Prompt | What You Get |
|--------|-------------|
| `01-feature-intake.md` | Intent summary, risks, scenarios, coverage split |
| `02-greenfield.md` | Quality-first development strategy |
| `03-brownfield.md` | Context recovery and governance system |
| `04-story-update.md` | Refreshed coverage after scope change |
| `05-scenarios.md` | Prioritized test scenarios by risk tier |
| `06-testcases.md` | Structured, traceable test cases |
| `07-automation.md` | Automation vs. manual classification with rationale |
| `08-manual.md` | Exploratory validation checklists |
| `09-defects.md` | Structured bug reports from failures |
| `10-triage.md` | Categorized, prioritized issue list |
| `11-evidence.md` | Interpretation of test results and logs |
| `12-release.md` | Ship/no-ship recommendation with evidence |
| `13-review.md` | Quality-check AI-generated QA artifacts |
| `14-qa-planning.md` | Test data, environment, automation, CI strategy |
| `15-test-gap-analysis.md` | Coverage gaps, risk heat map, remediation roadmap |

**Recommended order for greenfield:** 01 → 02 → 14 → 05 → 06 → 07 → 15 → 09 → 12

**Recommended order for brownfield:** 03 → 15 → 14 → 05 → 06 → 08 → 07 → 11 → 10 → 12

Structured test cases (`06`) ground scenarios before heavy exploratory passes (`08`). If you prefer exploratory-first on a legacy UI, run `08` before `06` and treat `06` as formalization afterward.

**Story change:** 04 → 05 → 06 → 12

---

## SDLC Triggers (T1-T8)

QA does not operate in isolation. Eight triggers map SDLC phases to QA workflow steps and prompts. This answers the question: **"When does QA kick in?"**

| Trigger | SDLC Phase | What Happens | Primary Prompt |
|---------|-----------|--------------|----------------|
| T1 | Requirements | Story created or updated | `01-feature-intake.md` |
| T2 | Design | Architecture, API contracts change | `02-greenfield.md` / `03-brownfield.md` |
| T3 | Development | Code committed, PR opened | `05-scenarios.md`, `06-testcases.md` |
| T4 | Testing | Test execution completes | `11-evidence.md`, `09-defects.md` |
| T5 | CI/CD | Pipeline completes | `10-triage.md` |
| T6 | Release | Release candidate tagged | `12-release.md` |
| T7 | Operations | Production incident or alert | `03-brownfield.md`, `09-defects.md` |
| T8 | Iteration | Story updated, scope changed | `04-story-update.md` |

See `.cursor/rules/sdlc-triggers.md` for full detail on each trigger, including what data flows, what artifacts are produced, and confidence treatment.

---

## Cursor Hooks (IDE Automation)

If you use Cursor, five hooks in `.cursor/hooks.json` automate QA guardrails without manual intervention:

| Hook | When It Fires | What It Does |
|------|--------------|-------------|
| **Session init** | Session starts | Loads QA standards context automatically |
| **Test file edit** | You write to a test file | Reminds the agent of test structure rules from `manual-qa-standards.md` |
| **Story update** | You edit a story/requirement file | Triggers the story-update loop and points to `04-story-update.md` |
| **Test evidence** | A test command completes (pytest, jest, go test, etc.) | Prompts evidence review; routes to `11-evidence.md`, `09-defects.md`, or `10-triage.md` |
| **Release gate** | You run a deploy/release/publish command | Asks for release readiness confirmation; points to `12-release.md` |

These hooks are optional — the methodology works without them, but they prevent common oversights.

---

## CI Orchestrator (Headless Pipeline)

For teams running QA in CI/CD without an IDE, `engine/ci/qa-orchestrator.py` chains **four prompts** through an LLM API (always in this order):

```
Test results (JUnit/TRX) → Evidence review (11) → Defect triage (10)
→ Defect drafting (09) → Release readiness (12)
```

**Outputs:** `qa-summary.md`, `defects.json`, `release-assessment.json`

Pass `--stack` (python, typescript, java, go, cpp, dotnet) to load `knowledge/stacks/{stack}.yml` — the profile’s `stack_context` and optional `guidance:` markdown file are appended to the system prompt for framework-specific analysis.

See `engine/ci/README.md` for setup, environment variables, and per-stack CI examples (GitHub Actions, GitLab).

---

## Verification Checklists

After generating any QA output, run the verification checklists from `.cursor/rules/qa-planner.md`. These catch gaps before you present results:

- **Intent and Risk** — is the intent specific? Are risks ranked T0-T3? At least one T0/T1 for auth/payments/data?
- **Test Scenarios** — grouped by risk tier? Happy path included? Negative paths for T0/T1?
- **Test Cases** — preconditions, numbered steps, expected results, automation flag?
- **Defect Reports** — specific title, numbered repro steps, expected vs actual, evidence, severity, confidence?
- **Triage** — classified (valid defect, duplicate, test issue, env issue)? Human review flagged for high-risk?
- **Test Gap Analysis** — all layers covered? Gap matrix? Confidence labels? Prioritized by risk tier?
- **Release Readiness** — T0/T1 evidence? Open criticals listed? Flaky rate noted? One of four outcomes stated?
- **All Outputs** — confidence labels on every inferred item? Traceability to intent? Clear language?

---

## Anti-Patterns to Avoid

| Avoid | Do Instead |
|-------|-----------|
| Skip risk assessment | Always classify risks by tier before generating scenarios |
| Test everything equally | Focus depth on T0/T1, lighter coverage on T2/T3 |
| Create defects without evidence | Attach logs, screenshots, or traces to every defect |
| Promote low-confidence findings | Flag for manual verification instead |
| Use vague test steps | Write numbered, specific actions with expected results |
| Ignore flaky tests | Quarantine, investigate, fix or remove |
| Generate freeform QA outputs | Always use the prompt library in `engine/prompts/` |
| Treat AI output as final | Run verification checklists, flag for human review |
| Skip story update loop | Re-enter at Step 2 when stories change |
| Skip test gap analysis | Run gap analysis before major releases or after brownfield recovery |

---

## First Steps

### 1. Add the repo to your workspace
Add this repository alongside your target project in your IDE (Cursor, VS Code, etc.).

### 2. Identify your role

| Role | Start Here | Load These Rules |
|------|-----------|-----------------|
| **Developer** | `.cursor/rules/developer-standards.md` | `core-principles.md` + `automation-qa-standards.md` |
| **QA Lead** | `.cursor/rules/qa-lead-playbook.md` | `core-principles.md` + `manual-qa-standards.md` + `risk-and-confidence.md` |
| **Scrum Master** | `training/getting-started.md` (this file) | `core-principles.md` + `release-and-governance.md` |

### 3. Choose your workflow

- **New system (greenfield)?** Start with `engine/prompts/01-feature-intake.md` then `02-greenfield.md`
- **Existing system (brownfield)?** Start with `engine/prompts/03-brownfield.md` then `15-test-gap-analysis.md`

### 4. Run a feature intake
Take a user story from your project and ask the AI:
```text
"Run QA intake for this user story: [paste your story here]"
```
The AI will produce: intent summary, risk list, priority scenarios, coverage split, and evidence needed.

### 5. Generate test scenarios
```text
"Generate prioritized test scenarios for the [feature name]"
```

### 6. Create test cases
```text
"Convert these scenarios into structured test cases"
```

### 7. Run verification checklists
Check the AI output against the verification checklists in `.cursor/rules/qa-planner.md`. Refine as needed.

---

## What to Read Next

### Walkthroughs (step-by-step examples)

| Goal | Read |
|------|------|
| Run a full greenfield workflow E2E | [greenfield-walkthrough.md](greenfield-walkthrough.md) |
| Run a full brownfield workflow E2E | [brownfield-walkthrough.md](brownfield-walkthrough.md) |

### Skill-specific guides

| Goal | Read |
|------|------|
| Learn manual QA with AI | [manual-qa-with-ai.md](manual-qa-with-ai.md) |
| Learn automation with Playwright | [automation-with-playwright.md](automation-with-playwright.md) |
| Learn Xray integration | [xray-with-ai.md](xray-with-ai.md) |

### Rules and standards (for deeper understanding)

| Goal | Read |
|------|------|
| Understand the 11-step workflow in detail | `.cursor/rules/workflows.md` |
| Understand risk tiers and confidence scoring | `.cursor/rules/risk-and-confidence.md` |
| See the full prompt routing table | `.cursor/rules/qa-planner.md` |
| Learn SDLC trigger mappings | `.cursor/rules/sdlc-triggers.md` |
| Review QA lead governance model | `.cursor/rules/qa-lead-playbook.md` |
| Review developer testability standards | `.cursor/rules/developer-standards.md` |
| Set up the CI orchestrator | `engine/ci/README.md` |

# HatchWorks QA Operating Model

A tool-agnostic, AI-first methodology for running QA across all HatchWorks projects. The methodology stays the same — the tools are up to you.

**Three things you need to do QA with AI:**
1. **Context** — what is the system, what changed, what are the requirements
2. **Standards** — what are the QA rules (risk tiers, evidence, test structure)
3. **Prompts** — how to instruct the AI to produce specific QA outputs

---

## Architecture

```
Layer 1: INTERFACE (.agent/rules/)   Planner & standards-creator rules
Layer 2: ENGINE (engine/)            What executes the work + automation
Agent Store: KNOWLEDGE (knowledge/)  Standards the AI reads at runtime
Human Store: TRAINING (training/)    Guides for humans to learn the methodology
```

### Migrating from the legacy layout (`main` branch)

If you linked or scripted against the older repo shape, paths moved as follows:

| Legacy path | This branch |
|-------------|-------------|
| `prompts/` | `engine/prompts/` |
| `prompts/01-master.md` (routing) | `.agent/rules/qa-planner.md` |
| `qa/*.md` (standards, workflows, hooks narrative) | `.agent/rules/*.md` plus `knowledge/templates/` for output shapes |
| `ci/` | `engine/ci/` |
| `stack-profiles/` | `knowledge/stacks/` (`*.yml` profiles + `*-testing-guidance.md`) |
| `artifact-templates/` | `knowledge/templates/` |
| `QA.md` (operator quick sheet) | [QA.md](QA.md) (short index; detail in `training/`) |

### Layer 1: Interface (`.agent/rules/`)

The entry point for all QA tasks. The QA planner and standards-creator rules route requests, enforce checklists, and prevent anti-patterns.

| Rule | Purpose |
|------|---------|
| [qa-planner.md](.agent/rules/qa-planner.md) | Routes any QA task to the right prompt, validates output |
| [qa-standards-creator.md](.agent/rules/qa-standards-creator.md) | Generates stack-specific QA files for any project |

### Layer 2: Engine (`engine/`)

What actually does the work when triggered by Layer 1.

| Component | Purpose |
|-----------|---------|
| [engine/prompts/](engine/prompts/) | 15 task-specific prompts (scenarios, test cases, defects, triage, test gaps, release...) |
| [engine/connectors/](engine/connectors/) | Optional tool integrations (Playwright MCP, Xray) |
| [engine/ci/](engine/ci/) | CI/CD orchestrator — automated AI triage pipeline |

### Knowledge: Standards rules (`.agent/rules/`)

QA standards optimized for AI consumption. Small, focused files loaded selectively to keep the context window lean.

| File | When to Load | Audience |
|------|-------------|----------|
| [core-principles.md](.agent/rules/core-principles.md) | Every QA session (always) | Everyone |
| [developer-standards.md](.agent/rules/developer-standards.md) | Writing/reviewing code, PRs | Developers, engineers |
| [qa-lead-playbook.md](.agent/rules/qa-lead-playbook.md) | Pipeline governance, triage, release | QA leads |
| [risk-and-confidence.md](.agent/rules/risk-and-confidence.md) | Risk assessment, triage, planning | QA leads, reviewers |
| [manual-qa-standards.md](.agent/rules/manual-qa-standards.md) | Test design, defects, manual validation | QA engineers |
| [automation-qa-standards.md](.agent/rules/automation-qa-standards.md) | Writing tests, automation, CI/CD | Developers, QA automation |
| [release-and-governance.md](.agent/rules/release-and-governance.md) | Release decisions, governance | Leads, stakeholders |
| [workflows.md](.agent/rules/workflows.md) | Greenfield/brownfield workflow steps | QA leads, engineers |
| [sdlc-triggers.md](.agent/rules/sdlc-triggers.md) | When SDLC phases trigger QA | QA leads, engineers |

### Knowledge: Stacks and templates (`knowledge/`)

Runtime reference data the agent (or orchestrator) loads alongside rules.

| Location | What it is | Audience |
|----------|------------|----------|
| [knowledge/stacks/](knowledge/stacks/) | Per-language testing guidance + CI stack profiles (`.yml`) | Developers, automation, QA |
| [knowledge/templates/](knowledge/templates/) | Output format templates (test cases, defects, releases, testing standards) | QA engineers, leads |

### Training (`training/`)

Human-readable guides for learning and workshops (separate from the agent-facing `knowledge/` store).

| Guide | Purpose |
|-------|---------|
| [getting-started.md](training/getting-started.md) | Onboarding: what is this, how to use it |
| [greenfield-walkthrough.md](training/greenfield-walkthrough.md) | E2E greenfield workflow with examples |
| [brownfield-walkthrough.md](training/brownfield-walkthrough.md) | E2E brownfield workflow with examples |
| [manual-qa-with-ai.md](training/manual-qa-with-ai.md) | How to instruct the AI for manual test cases |
| [automation-with-playwright.md](training/automation-with-playwright.md) | How to use Playwright MCP for E2E automation |
| [xray-with-ai.md](training/xray-with-ai.md) | How to use Xray to augment the QA process |

---

## Two Pipelines, One Methodology

### Developer Pipeline (all engineers)

Developers follow testability standards set by the QA team, write testable code, and get feedback through CI.

```
Developer writes code → Follows developer-standards.md → PR review (testability checklist)
→ CI runs tests → AI triage → QA lead reviews → Defect/fix loop
```

**Start here:** [.agent/rules/developer-standards.md](.agent/rules/developer-standards.md) — coding standards for testability (selectors, logging, error handling, contracts, test data).

### QA Lead Pipeline (QA leads and architects)

QA leads govern the full 11-step workflow, own risk classification, triage authority, and release decisions.

```
Feature intake → Context → Scope → Test cases → Risk + Confidence → Dual validation
→ Evidence + Triage → QA Decision → Confirmed defects → Release readiness
```

**Start here:** [.agent/rules/qa-lead-playbook.md](.agent/rules/qa-lead-playbook.md) — what you own, when you intervene, how you run the pipeline.

---

## Quick Start

### For developers
1. Read `.agent/rules/developer-standards.md` — testability rules you must follow
2. Load `.agent/rules/core-principles.md` + `.agent/rules/automation-qa-standards.md`
3. Use `.agent/rules/qa-planner.md` for guided test generation
4. Consult `knowledge/stacks/` for your language

### For QA leads
1. Read `.agent/rules/qa-lead-playbook.md` — your governance playbook
2. Load `.agent/rules/core-principles.md` + `.agent/rules/manual-qa-standards.md`
3. Use `.agent/rules/qa-planner.md` for triage, defect drafting, release readiness
4. Enforce `.agent/rules/developer-standards.md` across teams

### For scrum masters / engineering leads
1. Read `training/getting-started.md` for the overview
2. Load `.agent/rules/core-principles.md` + `.agent/rules/release-and-governance.md`
3. Use `.agent/rules/qa-planner.md` for release readiness assessment

### For training / workshops
1. Start with `training/getting-started.md`
2. Walk through `training/greenfield-walkthrough.md` or `training/brownfield-walkthrough.md` end-to-end
3. Demonstrate manual QA, Playwright automation, and Xray integration

### For AI agents (Cursor, etc.)
1. `.agent/rules/qa-planner.md` has routing, checklists, anti-patterns — loaded automatically
2. `.agent/rules/core-principles.md` is always loaded as the foundation
3. `engine/prompts/` is the execution library

**One-page path index:** [QA.md](QA.md)

---

## Repository Structure

```
QA-GenDD/
├── README.md
├── QA.md                              Operator quick index (links into training + rules)
├── .agent/                           LAYER 1: RULES + STANDARDS
│   ├── rules/
│   │   ├── qa-planner.md              Routing, checklists, anti-patterns (always loaded)
│   │   ├── qa-standards-creator.md    Generate stack-specific QA files
│   │   ├── core-principles.md         Foundation (always loaded)
│   │   ├── developer-standards.md     Testability coding standards (for devs)
│   │   ├── qa-lead-playbook.md        QA lead governance playbook
│   │   ├── risk-and-confidence.md     Risk tiers, severity, planning
│   │   ├── manual-qa-standards.md     Test design, defects, manual QA
│   │   ├── automation-qa-standards.md Testing implementation, CI/CD
│   │   ├── release-and-governance.md  Release readiness, human gates
│   │   ├── workflows.md              Greenfield/brownfield steps
│   │   └── sdlc-triggers.md          SDLC phase triggers (T1-T8)
│   ├── hooks.json                     IDE event automation (5 hooks)
│   └── hooks/
├── engine/                            LAYER 2: EXECUTION
│   ├── prompts/                       15 task-specific prompts (01-15)
│   ├── connectors/
│   │   ├── playwright-mcp.md          Playwright browser automation
│   │   └── xray.md                    Xray test management
│   └── ci/
│       ├── qa-orchestrator.py         Automated AI triage pipeline
│       ├── requirements.txt
│       └── README.md
├── knowledge/                         REFERENCE DATA
│   ├── stacks/                        Per-language guidance + CI profiles
│   └── templates/                     Output format templates
├── training/                          HUMAN STORE
│   ├── getting-started.md
│   ├── greenfield-walkthrough.md
│   ├── brownfield-walkthrough.md
│   ├── manual-qa-with-ai.md
│   ├── automation-with-playwright.md
│   └── xray-with-ai.md
```

---

## Workflows

Both greenfield and brownfield paths follow 11 steps:

**Intent/Context -> Validate/Recover Context -> Build Scope -> Create Tests -> Risk + Confidence -> Dual Validation -> Evidence + AI Triage -> QA Decision -> Confirmed Defects -> Release Readiness**

See [.agent/rules/workflows.md](.agent/rules/workflows.md) for the canonical step tables.

---

## Connectors (Optional)

| Connector | What it does | When to use it |
|-----------|----------------|----------------|
| [Playwright MCP](engine/connectors/playwright-mcp.md) | Drive a real browser for E2E checks via MCP | You want AI-assisted UI flows, screenshots, and DOM-backed assertions (see `training/automation-with-playwright.md`). |
| [Xray](engine/connectors/xray.md) | Align tests and defects with Xray for traceability | Your org uses Jira/Xray as the test system of record (see `training/xray-with-ai.md`). |

Connectors are optional. The core methodology works without them.

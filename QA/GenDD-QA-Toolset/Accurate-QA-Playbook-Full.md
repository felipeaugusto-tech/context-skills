# Accurate QA Playbook — Full-Text Edition

**Owner:** QA / Quality Engineering
**Status:** v2.0 — Companion to [`Accurate-QA-Playbook.md`](Accurate-QA-Playbook.md)
**Purpose:** This document reproduces the **complete, verbatim text** (including YAML frontmatter) of every rule, prompt, template, and connector file that the condensed playbook distills. Use the condensed playbook for day-to-day reference; use this document when the full original wording, an edge case, or an exact MUST/SHOULD clause is needed.

**Source of truth on conflict:** the original files inside [`QA-GenDD/`](QA-GenDD/) and, for the testing-standards rule domain (§11), `agent-assets/sdlc/quality-assurance/`. If this document and the original diverge, the original file wins — that divergence is a defect in this document.

One deliberate departure from verbatim reproduction: the worked example in `knowledge/templates/tech-debt-template.md` (§19) that referenced a specific internal ticket has been replaced below with a generic, structurally identical example, to keep this playbook fully general-purpose. This is flagged inline where it occurs.

---

## Table of Contents

1. [Operating Model Overview](#1-operating-model-overview)
2. [Core Principles](#2-core-principles)
3. [Roles & Ownership](#3-roles--ownership)
4. [The 11-Step Workflow](#4-the-11-step-workflow)
5. [Risk Tiering, Severity & Confidence](#5-risk-tiering-severity--confidence)
6. [Developer Testability Standards](#6-developer-testability-standards)
7. [Manual QA & Test Design Standards](#7-manual-qa--test-design-standards)
8. [Defect Governance](#8-defect-governance)
9. [Tech Debt Governance](#9-tech-debt-governance)
10. [Automation, Testing Implementation & AI Usage](#10-automation-testing-implementation--ai-usage)
11. [Testing-Standards Rules Repository Cross-Reference](#11-testing-standards-rules-repository-cross-reference)
12. [Release Readiness & Governance](#12-release-readiness--governance)
13. [SDLC Triggers (T1–T8)](#13-sdlc-triggers-t1t8)
14. [QA Planner — Routing, Checklists & Anti-Patterns](#14-qa-planner--routing-checklists--anti-patterns)
15. [Onboarding a New Tech Stack](#15-onboarding-a-new-tech-stack)
16. [Prompt Library](#16-prompt-library)
17. [Connectors (Optional Tooling)](#17-connectors-optional-tooling)
18. [CI/CD Orchestrator (Headless Pipeline)](#18-cicd-orchestrator-headless-pipeline)
19. [Templates Library](#19-templates-library)
20. [Agent Skills (`.agent/skills/`)](#20-agent-skills-agentskills)

---

## 1. Operating Model Overview

Condensed version: [Accurate-QA-Playbook.md §1](Accurate-QA-Playbook.md#1-operating-model-overview) · Source: [`QA-GenDD/README.md`](QA-GenDD/README.md), [`QA-GenDD/QA.md`](QA-GenDD/QA.md)

### `QA-GenDD/README.md` (verbatim)

> # HatchWorks QA Operating Model
>
> A tool-agnostic, AI-first methodology for running QA across all HatchWorks projects. The methodology stays the same — the tools are up to you.
>
> **Three things you need to do QA with AI:**
> 1. **Context** — what is the system, what changed, what are the requirements
> 2. **Standards** — what are the QA rules (risk tiers, evidence, test structure)
> 3. **Prompts** — how to instruct the AI to produce specific QA outputs
>
> ## Architecture
>
> ```
> Layer 1: INTERFACE (.agent/rules/)   Planner & standards-creator rules
> Layer 2: ENGINE (engine/)            What executes the work + automation
> Agent Store: KNOWLEDGE (knowledge/)  Standards the AI reads at runtime
> Human Store: TRAINING (training/)    Guides for humans to learn the methodology
> ```
>
> ### Migrating from the legacy layout (`main` branch)
>
> If you linked or scripted against the older repo shape, paths moved as follows:
>
> | Legacy path | This branch |
> |-------------|-------------|
> | `prompts/` | `engine/prompts/` |
> | `prompts/01-master.md` (routing) | `.agent/rules/qa-planner.md` |
> | `qa/*.md` (standards, workflows, hooks narrative) | `.agent/rules/*.md` plus `knowledge/templates/` for output shapes |
> | `ci/` | `engine/ci/` |
> | `stack-profiles/` | `knowledge/stacks/` (`*.yml` profiles + `*-testing-guidance.md`) |
> | `artifact-templates/` | `knowledge/templates/` |
> | `QA.md` (operator quick sheet) | `QA.md` (short index; detail in `training/`) |
>
> ### Layer 1: Interface (`.agent/rules/`)
>
> The entry point for all QA tasks. The QA planner and standards-creator rules route requests, enforce checklists, and prevent anti-patterns.
>
> | Rule | Purpose |
> |------|---------|
> | qa-planner.md | Routes any QA task to the right prompt, validates output |
> | qa-standards-creator.md | Generates stack-specific QA files for any project |
>
> ### Layer 2: Engine (`engine/`)
>
> What actually does the work when triggered by Layer 1.
>
> | Component | Purpose |
> |-----------|---------|
> | engine/prompts/ | 15 task-specific prompts (scenarios, test cases, defects, triage, test gaps, release...) |
> | engine/connectors/ | Optional tool integrations (Playwright MCP, Xray) |
> | engine/ci/ | CI/CD orchestrator — automated AI triage pipeline |
>
> ### Knowledge: Standards rules (`.agent/rules/`)
>
> QA standards optimized for AI consumption. Small, focused files loaded selectively to keep the context window lean.
>
> | File | When to Load | Audience |
> |------|-------------|----------|
> | core-principles.md | Every QA session (always) | Everyone |
> | developer-standards.md | Writing/reviewing code, PRs | Developers, engineers |
> | qa-lead-playbook.md | Pipeline governance, triage, release | QA leads |
> | risk-and-confidence.md | Risk assessment, triage, planning | QA leads, reviewers |
> | manual-qa-standards.md | Test design, defects, manual validation | QA engineers |
> | automation-qa-standards.md | Writing tests, automation, CI/CD | Developers, QA automation |
> | release-and-governance.md | Release decisions, governance | Leads, stakeholders |
> | workflows.md | Greenfield/brownfield workflow steps | QA leads, engineers |
> | sdlc-triggers.md | When SDLC phases trigger QA | QA leads, engineers |
>
> ### Knowledge: Stacks and templates (`knowledge/`)
>
> Runtime reference data the agent (or orchestrator) loads alongside rules.
>
> | Location | What it is | Audience |
> |----------|------------|----------|
> | knowledge/stacks/ | Per-language testing guidance + CI stack profiles (`.yml`) | Developers, automation, QA |
> | knowledge/templates/ | Output format templates (test cases, defects, releases, testing standards) | QA engineers, leads |
>
> ### Training (`training/`)
>
> Human-readable guides for learning and workshops (separate from the agent-facing `knowledge/` store).
>
> | Guide | Purpose |
> |-------|---------|
> | getting-started.md | Onboarding: what is this, how to use it |
> | greenfield-walkthrough.md | E2E greenfield workflow with examples |
> | brownfield-walkthrough.md | E2E brownfield workflow with examples |
> | manual-qa-with-ai.md | How to instruct the AI for manual test cases |
> | automation-with-playwright.md | How to use Playwright MCP for E2E automation |
> | xray-with-ai.md | How to use Xray to augment the QA process |
>
> ## Two Pipelines, One Methodology
>
> ### Developer Pipeline (all engineers)
>
> Developers follow testability standards set by the QA team, write testable code, and get feedback through CI.
>
> ```
> Developer writes code → Follows developer-standards.md → PR review (testability checklist)
> → CI runs tests → AI triage → QA lead reviews → Defect/fix loop
> ```
>
> **Start here:** `.agent/rules/developer-standards.md` — coding standards for testability (selectors, logging, error handling, contracts, test data).
>
> ### QA Lead Pipeline (QA leads and architects)
>
> QA leads govern the full 11-step workflow, own risk classification, triage authority, and release decisions.
>
> ```
> Feature intake → Context → Scope → Test cases → Risk + Confidence → Dual validation
> → Evidence + Triage → QA Decision → Confirmed defects → Release readiness
> ```
>
> **Start here:** `.agent/rules/qa-lead-playbook.md` — what you own, when you intervene, how you run the pipeline.
>
> ## Quick Start
>
> ### For developers
> 1. Read `.agent/rules/developer-standards.md` — testability rules you must follow
> 2. Load `.agent/rules/core-principles.md` + `.agent/rules/automation-qa-standards.md`
> 3. Use `.agent/rules/qa-planner.md` for guided test generation
> 4. Consult `knowledge/stacks/` for your language
>
> ### For QA leads
> 1. Read `.agent/rules/qa-lead-playbook.md` — your governance playbook
> 2. Load `.agent/rules/core-principles.md` + `.agent/rules/manual-qa-standards.md`
> 3. Use `.agent/rules/qa-planner.md` for triage, defect drafting, release readiness
> 4. Enforce `.agent/rules/developer-standards.md` across teams
>
> ### For scrum masters / engineering leads
> 1. Read `training/getting-started.md` for the overview
> 2. Load `.agent/rules/core-principles.md` + `.agent/rules/release-and-governance.md`
> 3. Use `.agent/rules/qa-planner.md` for release readiness assessment
>
> ### For training / workshops
> 1. Start with `training/getting-started.md`
> 2. Walk through `training/greenfield-walkthrough.md` or `training/brownfield-walkthrough.md` end-to-end
> 3. Demonstrate manual QA, Playwright automation, and Xray integration
>
> ### For AI agents (Cursor, etc.)
> 1. `.agent/rules/qa-planner.md` has routing, checklists, anti-patterns — loaded automatically
> 2. `.agent/rules/core-principles.md` is always loaded as the foundation
> 3. `engine/prompts/` is the execution library
>
> **One-page path index:** `QA.md`
>
> ## Repository Structure
>
> ```
> QA-GenDD/
> ├── README.md
> ├── QA.md                              Operator quick index (links into training + rules)
> ├── .agent/                           LAYER 1: RULES + STANDARDS
> │   ├── rules/
> │   │   ├── qa-planner.md              Routing, checklists, anti-patterns (always loaded)
> │   │   ├── qa-standards-creator.md    Generate stack-specific QA files
> │   │   ├── core-principles.md         Foundation (always loaded)
> │   │   ├── developer-standards.md     Testability coding standards (for devs)
> │   │   ├── qa-lead-playbook.md        QA lead governance playbook
> │   │   ├── risk-and-confidence.md     Risk tiers, severity, planning
> │   │   ├── manual-qa-standards.md     Test design, defects, manual QA
> │   │   ├── automation-qa-standards.md Testing implementation, CI/CD
> │   │   ├── release-and-governance.md  Release readiness, human gates
> │   │   ├── workflows.md              Greenfield/brownfield steps
> │   │   └── sdlc-triggers.md          SDLC phase triggers (T1-T8)
> │   ├── hooks.json                     IDE event automation (5 hooks)
> │   └── hooks/
> ├── engine/                            LAYER 2: EXECUTION
> │   ├── prompts/                       15 task-specific prompts (01-15)
> │   ├── connectors/
> │   │   ├── playwright-mcp.md          Playwright browser automation
> │   │   └── xray.md                    Xray test management
> │   └── ci/
> │       ├── qa-orchestrator.py         Automated AI triage pipeline
> │       ├── requirements.txt
> │       └── README.md
> ├── knowledge/                         REFERENCE DATA
> │   ├── stacks/                        Per-language guidance + CI profiles
> │   └── templates/                     Output format templates
> ├── training/                          HUMAN STORE
> │   ├── getting-started.md
> │   ├── greenfield-walkthrough.md
> │   ├── brownfield-walkthrough.md
> │   ├── manual-qa-with-ai.md
> │   ├── automation-with-playwright.md
> │   └── xray-with-ai.md
> ```
>
> ## Workflows
>
> Both greenfield and brownfield paths follow 11 steps:
>
> **Intent/Context -> Validate/Recover Context -> Build Scope -> Create Tests -> Risk + Confidence -> Dual Validation -> Evidence + AI Triage -> QA Decision -> Confirmed Defects -> Release Readiness**
>
> See `.agent/rules/workflows.md` for the canonical step tables.
>
> ## Connectors (Optional)
>
> | Connector | What it does | When to use it |
> |-----------|----------------|----------------|
> | Playwright MCP | Drive a real browser for E2E checks via MCP | You want AI-assisted UI flows, screenshots, and DOM-backed assertions (see `training/automation-with-playwright.md`). |
> | Xray | Align tests and defects with Xray for traceability | Your org uses Jira/Xray as the test system of record (see `training/xray-with-ai.md`). |
>
> Connectors are optional. The core methodology works without them.

### `QA-GenDD/QA.md` (verbatim)

> # QA operator quick index
>
> Use this page to jump into the methodology without reading the full README.
>
> ## What to do
>
> 1. Define intent and risk for the change.
> 2. Run the right **prompt** from `engine/prompts/` (never freeform QA blobs).
> 3. Validate outputs using the checklists in `.agent/rules/qa-planner.md`.
>
> ## Where things live
>
> | Need | Path |
> |------|------|
> | Routing, checklists, anti-patterns | `.agent/rules/qa-planner.md` |
> | Foundation rules | `.agent/rules/core-principles.md` |
> | Prompt library (execution) | `engine/prompts/` |
> | Stack + CI profiles | `knowledge/stacks/` |
> | Output templates | `knowledge/templates/` |
> | CI orchestrator (no IDE) | `engine/ci/README.md` |
> | Onboarding and walkthroughs | `training/getting-started.md` |
>
> ## Full map
>
> See `README.md` for architecture, pipelines, connectors, and migration notes from the legacy `main` layout.

---

## 2. Core Principles

Condensed version: [Accurate-QA-Playbook.md §2](Accurate-QA-Playbook.md#2-core-principles) · Source: [`QA-GenDD/.agent/rules/core-principles.md`](QA-GenDD/.agent/rules/core-principles.md)

```markdown
---
description: QA foundation — core principles, mission, minimum outputs, confidence scoring. Always relevant to any QA task.
alwaysApply: true
---

# QA Core Principles

---

## Purpose

These directives define how QA operates in an AI-first delivery model where products may be built quickly, requirements may be incomplete, and QA may enter after development or even after demos.

They are designed so that:
- Junior developers can follow them.
- Non-QA contributors can produce valid QA outputs.
- QA teams can review work faster and more consistently.

The goal is not to turn everyone into QA experts. The goal is to ensure all work is **testable**, **traceable**, **risk-aware**, and **easy to validate**. Tools may change — the QA approach stays consistent.

---

## QA Mission

QA exists to:
- reduce business and delivery risk
- provide evidence-based release confidence
- recover order when documentation is incomplete
- ensure traceability between product intent, execution, and defects
- design scalable quality systems
- remove QA as a delivery bottleneck
- keep humans in the loop only where judgment and governance are needed

QA is not only a testing function. QA is a risk, evidence, and quality architecture function.

---

## Core Principles

### 1. Risk-first
Testing must always be prioritized by business risk, technical fragility, user impact, and release criticality. Equal testing depth for all functionality is not required.

### 2. Not automated does not mean not tested
Functionality that is not automated must still be covered through structured manual, exploratory, or AI-assisted validation.

### 3. Evidence over opinion
All QA decisions should be supported by evidence: test results, logs, screenshots, traces, API responses, data validation, defect history, environment status, or confidence score of inferred requirements.

### 4. Human-in-the-loop
AI may generate, infer, classify, cluster, draft, and recommend. Humans must approve high-risk decisions, severe defect actions, and release recommendations.

### 5. Traceability is mandatory
All projects must maintain traceability across: business context, requirements, user stories, acceptance criteria, test cases, execution evidence, defects, and release decisions.

### 6. Testability is part of quality
A feature is not considered test-ready if it lacks observability, diagnosability, stable selectors, controllable test data, environment access, or clear failure evidence.

### 7. QA must accelerate delivery
QA should create systems that reduce repeated manual regression, duplicate bug logging, noisy triage, flaky test waste, unclear ownership, and low-value manual effort.

### 8. Keep outputs simple
All QA outputs should be clear, short, reusable, and easy for another person to understand. Avoid unnecessary complexity or tool-specific jargon.

### 9. Automated findings require human verification when needed
If a finding is high impact, low/medium confidence, ambiguous, potentially flaky, environment-sensitive, or missing clear reproduction certainty, it must first move into the manual / exploratory / AI-assisted verification lane for confirmation before defect creation.

### 10. Start with intent
Before writing tests or code, define: What is being built or changed? Who is it for? What does success look like? What is the main user flow?

For major features, major defects, and user acceptance scenarios, capture a short **Business Intent Statement** that AI and QA can use to reconstruct requirements, validate acceptance criteria, improve bug quality, and compare expected vs actual behavior.

---

## Standard QA Inputs

Every QA effort should try to use the following inputs when available:
- repository and codebase
- structured context from analysis tools
- project markdowns and documentation
- stakeholder demos and design assets
- API contracts
- logs and telemetry
- issue tracker stories and test assets
- defect history and production incidents
- release notes
- client or business rules
- authentication and authorization models

If requirements are missing, QA must reconstruct them using available evidence. Every inferred requirement must carry a confidence score.

---

## Minimum Expected Outputs

For any feature or change, produce at minimum:

1. **Intent summary** — what the feature is supposed to do
2. **Risk list** — what could go wrong
3. **Scenario list** — what should be tested first
4. **Coverage split** — what is automated vs. manual
5. **Execution evidence** — screenshots, logs, API responses, test outputs
6. **Defects (if any)** — what failed and why it matters

---

## Confidence Scoring

Any AI-generated or inferred QA artifact must include a confidence score:

- **High** — multiple supporting sources, behavior observed, logic consistent
- **Medium** — partial evidence, likely valid, needs light review
- **Low** — inferred from weak or incomplete signals, requires confirmation

Low-confidence items must not drive automatic release decisions without human review.

---

## Related Files

| Need | File |
|------|------|
| Testability coding standards (for developers) | developer-standards.md |
| QA lead governance and pipeline ownership | qa-lead-playbook.md |
| Risk tiering and severity | risk-and-confidence.md |
| Manual QA, defects, test design | manual-qa-standards.md |
| Automation, testing implementation | automation-qa-standards.md |
| Release decisions, governance | release-and-governance.md |
| Workflow steps | workflows.md |
| SDLC triggers | sdlc-triggers.md |
| Canonical, ID'd testing-standards rules (coverage, naming/structure, mocking, AI-generated-test review) | `agent-assets/sdlc/quality-assurance/README.md` — the Rules Repository's 5th standards domain (QA-001…QA-008) |
```

---

## 3. Roles & Ownership

Condensed version: [Accurate-QA-Playbook.md §3](Accurate-QA-Playbook.md#3-roles--ownership) · Source: [`QA-GenDD/.agent/rules/qa-lead-playbook.md`](QA-GenDD/.agent/rules/qa-lead-playbook.md) (the Ownership Model table in `release-and-governance.md` is reproduced in §12)

```markdown
---
description: QA lead governance playbook — pipeline ownership, triage authority, release decisions, testability enforcement. Load when governing QA or making pipeline decisions.
globs:
---

# QA Lead Playbook

This playbook defines what you own, when you intervene, and how you run the QA pipeline end-to-end. General developers follow `developer-standards.md`; you govern the full system.

---

## What You Own

| Area | Your Responsibility |
|------|-------------------|
| **Quality strategy** | Define risk tiers, coverage targets, automation scope for each project |
| **Pipeline governance** | Ensure the 11-step workflow is followed (greenfield or brownfield) |
| **Risk classification** | Approve T0/T1 risk assignments; validate that testing depth matches risk |
| **Triage authority** | Final decision on whether a finding becomes a confirmed defect |
| **Release recommendation** | Produce evidence-based release assessment; flag items requiring stakeholder approval |
| **Testability enforcement** | Set and enforce `developer-standards.md` across teams |
| **Automation ownership** | Define what gets automated, assign maintenance owners, manage flaky test quarantine |
| **AI governance** | Review AI-generated artifacts; ensure confidence labels are accurate; approve high-risk AI outputs |
| **Tech debt backlog** | Own the tech-debt backlog: confirm items found during testing are logged with required fields, triage into a sprint at the review cadence |
| **Team coordination** | Bridge between development, product, and stakeholders on quality decisions |

---

## The Pipeline You Run

### For Every Feature/Story

Follow the 11-step pipeline defined in workflows.md. Your decision points within that pipeline:

### Your Decision Points

| Step | What You Decide | Criteria |
|------|----------------|----------|
| **Step 3a** | Whether full QA planning is needed | New project, new stack, T0/T1 area, no existing infrastructure |
| **Step 5** | Whether risk classification is accurate | Business context, stakeholder input, historical defect patterns |
| **Step 6** | Whether automation/manual split is correct | Stability of UI, repeatability, ROI of automation |
| **Step 8** | Whether AI triage is accurate | Review findings classified as "valid defect" — do they have evidence? |
| **Step 9** | Whether findings become defects | High-confidence + evidence = approve. Low-confidence = route to manual verification |
| **Step 11** | Whether the release ships | All T0/T1 covered, no critical defects, stakeholders informed |

---

## When Developers Use the Pipeline

Developers interact with the pipeline through `developer-standards.md` and automated checks:

1. **Before coding:** Read testability standards (selectors, logging, error handling, contracts)
2. **During PR:** Run the PR review checklist from `developer-standards.md`
3. **CI feedback:** Automated tests run; failures are triaged by the AI pipeline
4. **Your review:** You review AI triage output; developers fix confirmed defects

The developer pipeline is: **Write testable code → PR review → CI tests → AI triage → Your review → Defect/Fix loop**

---

## Triage Governance

### What AI Does
- Clusters failures by probable root cause
- Drafts defect reports with evidence bundles
- Classifies findings: valid defect, needs verification, duplicate, test issue, environment issue
- Assigns confidence levels

### What You Do
- Review all "valid defect" classifications before they become tracked defects
- Route low-confidence findings to manual verification
- Approve or reject AI-drafted defect severity
- Identify false positives and feed back to improve triage quality
- Manage the flaky test quarantine list

### Escalation Rules

| Finding | Action |
|---------|--------|
| T0 failure with high confidence | Create defect immediately; escalate to stakeholders |
| T0 failure with low confidence | Route to manual verification; do NOT auto-create defect |
| T1 failure with high confidence | Create defect; schedule for current sprint |
| T1 failure with low confidence | Route to manual verification |
| T2/T3 failure | Create defect if evidence is clear; otherwise backlog |
| Flaky test (any tier) | Quarantine; investigate root cause; do not treat as product bug |
| Tech debt observed (any tier) | Log to Tech Debt Backlog via `tech-debt-template.md`; never treat as a defect or block Gate 5 on it |

---

## Release Governance

Apply the release readiness checklist and outcomes defined in release-and-governance.md.

### What Requires Your Signature

- Final release recommendation
- AI-drafted severe defects (Critical/High)
- Automation-detected findings that are ambiguous or environment-sensitive
- Any defect that impacts multiple tenants or has security/privacy implications
- Risk tier changes based on production incidents

---

## Testability Enforcement

You are responsible for ensuring development teams follow `developer-standards.md`:

1. **At project kickoff:** Review testability standards with the development team
2. **During sprints:** Check PRs for `data-testid` attributes, structured logging, error handling
3. **When gaps appear:** Create a testability recovery plan (see `manual-qa-standards.md`)
4. **At retrospectives:** Report on testability health — are teams making code easier or harder to test?

---

## Review Cadence

| Frequency | What to Review |
|-----------|---------------|
| **Every PR** | Testability checklist (delegate to QA engineers for T2/T3) |
| **Every sprint** | Risk tier accuracy, coverage gaps, flaky test health |
| **Every release** | Release readiness assessment, open defect status |
| **Monthly** | Automation ROI, triage accuracy, pipeline health |
| **Quarterly** | Standards review — update `developer-standards.md` and QA standards as needed |

---

## Related Files

| Need | File |
|------|------|
| Coding standards you enforce on developers | developer-standards.md |
| Risk tiering model you use for classification | risk-and-confidence.md |
| Test design rules your team follows | manual-qa-standards.md |
| Tech debt capture standard and required fields | `../../knowledge/templates/tech-debt-template.md` |
| Automation governance you oversee | automation-qa-standards.md |
| Release rules you apply | release-and-governance.md |
| Workflow steps you govern | workflows.md |
| Full prompt routing | qa-planner.md |
```

---

## 4. The 11-Step Workflow

Condensed version: [Accurate-QA-Playbook.md §4](Accurate-QA-Playbook.md#4-the-11-step-workflow) · Source: [`QA-GenDD/.agent/rules/workflows.md`](QA-GenDD/.agent/rules/workflows.md)

```markdown
---
description: Greenfield and brownfield QA workflows — 11-step pipeline, dual validation model, shared architecture. Load when planning or executing a QA workflow.
globs:
---

# QA Workflows
## Brownfield vs Greenfield Operating Models

---

## Overview

Two QA operating models exist based on system context:

- **Brownfield QA Workflow** — for existing systems with unclear or missing requirements
- **Greenfield QA Workflow** — for new systems with defined intent

Both workflows share the same **core QA control system**, but differ in how **context and truth are established**.

> **This workflow is tool-agnostic.** Teams use whatever tools fit their project — the methodology stays the same.

---

## Core Principle

> QA is not execution.
> QA is a **decision system governed by risk, confidence, and evidence**.

All workflows converge to:

**Risk + Confidence → Validation → Evidence → QA Decision → Confirmed Defects**

---

# Greenfield QA Workflow

## Definition

Used when:
- No system exists yet
- Requirements are defined upfront
- Behavior is intentionally designed

---

## Workflow

Steps 5-11 are shared — see Shared Steps below.

| Step | What happens | Subtitle |
|------|-------------|----------|
| **1. Product intent defined** | Business goals, user needs, and success criteria are captured | business goals, user needs, success criteria |
| **2. Validate and structure context** | Validate expected architecture, flows, and assumptions against intent | expected architecture, flows, assumptions |
| **3. Build scope and QA structure** | Stories, QA structure, and requirements are defined | stories, QA structure, requirements definition |
| **3a. QA Planning** | Define test data strategy, environment strategy, automation scope, and CI pipeline shape. Effort proportional to risk and novelty. | proactive investment in future readiness |
| **4. Create structured, traceable test cases** | Structured, traceable test cases are created and stored in the test management system, informed by the QA plan | structured, traceable test cases |

### Key Characteristics

- Forward-designed system
- Context is **defined upfront**
- Lower initial uncertainty
- QA acts as **validation + governance layer**

---

# Brownfield QA Workflow

## Definition

Used when:
- A system or MVP already exists
- Requirements are incomplete or unclear
- Behavior must be **reverse-engineered**

---

## Workflow

Steps 5-11 are shared — see Shared Steps below.

| Step | What happens | Subtitle |
|------|-------------|----------|
| **1. MVP exists** | An AI-generated or legacy system is the brownfield application | Brownfield application ready |
| **2. Recover and structure context** | Infer existing architecture, flows, risks, and assumptions from the codebase | existing architecture, flows, assumptions |
| **3. Build scope and QA structure** | Stories, QA structure, and requirements are defined from recovered context | stories, QA structure, requirements definition |
| **3a. QA Planning** | Define test data strategy, environment strategy, automation scope, and CI pipeline shape. Effort proportional to risk and novelty. | proactive investment in future readiness |
| **4. Create structured, traceable test cases** | Structured, traceable test cases with confidence annotations, informed by the QA plan | structured, traceable test cases |

### Story Update Behavior

When a story is updated:

> Re-enter at **Step 2: Recover and structure context**

This ensures:
- Context is revalidated
- Scope is recalculated
- Tests are updated
- Validation is re-executed

### Key Characteristics

- Reverse-engineered system
- Context is **recovered from the existing system**
- High initial uncertainty
- QA acts as **reconstruction + control layer**

---

## Shared Steps (5-11)

| Step | What happens | Subtitle |
|------|-------------|----------|
| **5. Risk + Confidence** | QA decision engine classifies risk tiers (T0–T3) and assigns confidence scores | QA decision engine |
| **6A. Automation** | Deterministic validation with planned coverage for stable, repeatable scenarios | deterministic validation, planned coverage |
| **6B. Manual + AI** | Exploratory validation for edge cases, unknowns, and uncertainty resolution | exploratory validation, edge cases, unknowns |
| **7A. Automated execution** | Continuous validation producing strong, repeatable evidence | continuous validation, strong evidence |
| **7B. Exploratory execution** | Human + AI validation for judgment-heavy and ambiguous scenarios | human + AI validation |
| **8. Evidence + AI Triage** | Evidence-weighted clustering; AI drafts defects, identifies duplicates, suggests root cause | evidence-weighted clustering |
| **9. QA Decision** | Human-in-the-loop control; QA reviews findings, approves or rejects | human-in-the-loop control |
| **10. Confirmed defects** | Only validated, traceable defects are created in the issue tracker | validated + traceable |
| **11. Release readiness** | Evidence-based release recommendation | release recommended / conditional / not recommended / insufficient evidence |

---

# Brownfield vs Greenfield Comparison

| Dimension | Brownfield | Greenfield |
|----------|-----------|-----------|
| Starting point | Existing system (MVP) | Defined intent |
| Context source | Recovered from system | Validated against intent |
| Requirements | Inferred from code behavior | Designed upfront |
| QA role | Reconstruction + control | Validation + control |
| Initial uncertainty | High | Managed upfront |
| Change handling | Re-enter at context recovery | Managed through design |
| Test confidence | Annotated with confidence levels | Generally higher |

---

# Shared Architecture

Both workflows share:

- **Decision Engine (Step 5):** Risk tiers T0–T3 and confidence scoring drive testing depth. See risk-and-confidence.md.
- **Dual Validation (Steps 6–7):** Automation lane for stable scenarios; Manual + AI lane for exploratory and ambiguous findings. See automation-qa-standards.md and manual-qa-standards.md.
- **Evidence Flow (Step 8):** AI clusters findings, drafts defects, identifies duplicates; QA reviews meaningful outputs.
- **Output Control (Steps 9–10):** Only validated defects reach the issue tracker. AI drafts, humans decide. See manual-qa-standards.md for defect field requirements.
- **Tech Debt Capture (Steps 6–8, ongoing):** Anything found during dual validation or evidence review that isn't a defect against this story — a shortcut, gap, or drift — is registered, not fixed, via manual-qa-standards.md → Tech Debt Governance. This runs alongside every story, not as its own numbered step.

---

# Strategic Insight

The difference between workflows is not in the steps — it is in **where truth comes from**:

- **Brownfield** → Truth is **discovered** from system behavior
- **Greenfield** → Truth is **defined** from intent

---

# Final Takeaway

QA is not about test execution, tooling, or coverage metrics.

It is a **system for controlling correctness under uncertainty**.

> QA governs release decisions through **risk, confidence, and evidence** — not assumptions.

## Related Documents

- QA Core Principles (core-principles.md) — Foundation principles loaded every session
- Manual QA Standards (manual-qa-standards.md) — Test design, defects, manual validation
- Automation QA Standards (automation-qa-standards.md) — Testing implementation, CI/CD
- Release and Governance (release-and-governance.md) — Release readiness, human gates
- QA Planner (qa-planner.md) — Routing table, checklists, and prompts for executing these workflows
- SDLC Triggers (sdlc-triggers.md) — When each SDLC phase feeds information into the QA process
```

---

## 5. Risk Tiering, Severity & Confidence

Condensed version: [Accurate-QA-Playbook.md §5](Accurate-QA-Playbook.md#5-risk-tiering-severity--confidence) · Source: [`QA-GenDD/.agent/rules/risk-and-confidence.md`](QA-GenDD/.agent/rules/risk-and-confidence.md)

```markdown
---
description: Risk tiering (T0-T3), severity model, QA planning criteria, story update loop. Load for risk assessment, triage, or QA planning.
globs:
---

# Risk, Severity, and QA Planning

---

## Risk Tiering Standard (T0–T3)

### Tier 0 — Release blockers and critical risks
- Auth failures
- Client/tenant separation issues
- Data integrity loss
- Privacy or legal exposure
- Payment or financial calculation failures
- Severe security issues
- Production availability blockers

### Tier 1 — Core business workflows
- Primary user journeys
- Business-critical calculations
- Critical CRUD flows
- Workflow continuity

### Tier 2 — Secondary operational value
- Integrations
- Reporting
- Asynchronous processing
- Notifications
- Admin functions

### Tier 3 — Low-criticality scope
- Cosmetic defects
- Convenience features
- Low-impact usability issues

Risk tier must determine: testing priority, automation priority, evidence depth, stakeholder escalation needs, and release impact.

---

## Severity and Priority Model

### Severity
- **Critical** — blocks release, major security/data/client impact
- **High** — major workflow broken, no acceptable workaround
- **Medium** — important issue, workaround exists
- **Low** — minor issue, cosmetic or low-impact behavior

### Priority
Priority must reflect business urgency, customer exposure, and release timing. Severity and priority are not always the same.

---

## Reverse QA Operating Model

When QA engages after an MVP already exists, follow the brownfield workflow in workflows.md: recover context, reconstruct requirements, build test coverage, and establish quality governance through the standard 11-step pipeline.

---

## QA Readiness — Proactive Planning

### When full planning is justified
- Starting a new project or major feature area
- Introducing a new tech stack, framework, or integration
- Working on Tier 0 or Tier 1 risk areas (auth, payments, data integrity)
- NFR-heavy features (performance targets, security constraints, compliance)
- The project has no existing test infrastructure

### When lightweight intake suffices
- Small bug fixes in well-understood, well-tested domains
- Cosmetic or Tier 3 changes
- Incremental additions to an already-planned feature area
- The project already has established test data, environments, and automation

### What QA Planning must cover
1. **Test data strategy** — what data is needed, how it is sourced or generated, how PII is handled, how data is cleaned between runs
2. **Environment strategy** — which environments exist, how they are provisioned, parity with production, access controls
3. **Automation scope** — which layers to automate, which framework/tooling, who owns maintenance, what coverage targets apply
4. **CI pipeline shape** — which suites run at PR vs. merge vs. nightly, parallelism, caching, artifact retention

These outputs are **living documents** that evolve with the story update loop.

### Proportionality principle
Planning effort must be proportional to risk and novelty. A Tier 0 payment integration on a new stack justifies a full test data plan and automation framework decision. A Tier 3 tooltip fix does not.

---

## Story Update Loop

When a story or requirement changes mid-cycle, re-enter the workflow at **Step 2 (context validation)**:

1. Re-check intent and context against the updated story.
2. Update affected test scenarios and acceptance criteria.
3. Update or regenerate affected tests.
4. Re-run the impacted test suites.
5. Review evidence from the new execution.
6. Update or close defects that no longer apply.

Do not test using outdated assumptions.
```

---

## 6. Developer Testability Standards

Condensed version: [Accurate-QA-Playbook.md §6](Accurate-QA-Playbook.md#6-developer-testability-standards) · Source: [`QA-GenDD/.agent/rules/developer-standards.md`](QA-GenDD/.agent/rules/developer-standards.md)

```markdown
---
description: Testability coding standards for developers — UI selectors, API error handling, structured logging, test data, environment requirements. Load when writing or reviewing code.
globs:
---

# Developer Testability Standards

---

## Why This Exists

If code is not testable, QA cannot validate it efficiently. These standards exist so that:
- Automated tests can run reliably against your code
- Manual testers can observe and verify behavior
- AI-assisted QA can generate meaningful test cases
- Defects can be triaged quickly with clear evidence
- The QA pipeline does not become a bottleneck waiting for testability fixes

**Rule: Testability is a quality attribute of code, not a QA afterthought.**

---

## UI Testability

### Stable Selectors (MUST)

Every interactive UI element must have a `data-testid` attribute.

| Do | Don't |
|----|-------|
| `<button data-testid="submit-order">` | `<button class="btn-primary">` |
| `<input data-testid="email-input">` | `<input id="field_3">` |
| `<div data-testid="error-message">` | `<div class="text-red-500">` |

- Selectors must be **stable** — they do not change when styles, layout, or text changes
- Selectors must be **semantic** — they describe what the element does, not how it looks
- Never rely on CSS classes, XPath, or text content for test targeting

### State Visibility (SHOULD)

UI state should be inspectable:
- Loading states should be detectable (spinner, skeleton, aria-busy)
- Error states should display specific error codes or messages, not just "Something went wrong"
- Success states should confirm the action taken (order ID, confirmation number)

---

## API Testability

### Error Responses (MUST)

Every API error response must include:

```json
{
  "error": {
    "code": "DUPLICATE_EMAIL",
    "message": "An account with this email already exists",
    "field": "email"
  }
}
```

- Use specific error codes, not generic "Bad Request"
- Include the field that caused the error (for validation failures)
- Return appropriate HTTP status codes (400, 401, 403, 404, 409, 422, 500)

### Contract Consistency (MUST)

- API endpoints must return consistent response shapes (same fields in success and error cases)
- Breaking changes to API contracts must be versioned or flagged
- Nullable fields must be documented in the contract

### Idempotency (SHOULD for write operations)

- POST/PUT operations that create resources should support idempotency keys
- Duplicate requests with the same idempotency key should return the same result, not create duplicates

---

## Logging and Observability

### Structured Logging (MUST)

All logs must be structured (JSON or key-value), not freeform strings.

```json
{"level": "error", "event": "payment_failed", "user_id": "u_123", "amount": 2000, "reason": "card_declined", "trace_id": "abc-def"}
```

Not:
```
ERROR: Payment failed for user 123
```

### What to Log (MUST)

| Event Type | What to Include |
|-----------|----------------|
| User actions | Action name, user ID, resource ID, timestamp |
| Errors | Error code, message, stack trace, request context |
| External calls | Service name, endpoint, response status, latency |
| State changes | Before/after values for critical business data |
| Auth events | Login/logout, permission checks, failed attempts |

### Trace IDs (SHOULD)

- Every request should carry a trace ID through all service calls
- Include the trace ID in error responses so QA can correlate logs to failures

---

## Test Data

### Seedable State (MUST)

- The application must support a known starting state for tests (seed data, fixtures, or factories)
- Test users, tenants, and data must be createable without manual setup
- Test data must be isolatable — tests should not depend on or corrupt shared data

### Data Cleanup (SHOULD)

- Provide a mechanism to reset test data between runs
- Use transactions or dedicated test tenants to prevent accumulation

### Sensitive Data (MUST)

- Test environments must never contain real PII
- Use synthetic or anonymized data for all testing
- Clearly label test accounts and data

---

## Environment

### Reproducibility (MUST)

- The application must be runnable locally or in a test environment that mirrors production behavior
- Environment configuration must be documented (env vars, services, dependencies)
- External dependencies should be mockable or have sandbox/test modes

### Health Checks (SHOULD)

- Expose a health endpoint that reports service status
- Include dependency health (database, cache, external APIs) in the check

---

## Error Handling

### Fail Clearly (MUST)

- Errors must produce actionable messages, not silent failures
- Business rule violations must be distinguishable from system errors
- Timeouts must be explicit (not just hanging connections)

### Boundary Validation (MUST)

- All inputs must be validated at the boundary (API layer, form submission)
- Validation errors must list all failing fields, not just the first one
- Null/empty handling must be explicit

---

## Multi-Tenancy (when applicable)

### Tenant Isolation (MUST)

- Data from one tenant must never be visible to another
- Test with at least two tenants to verify isolation
- Include tenant context in all log entries

---

## PR Review Checklist (for developers)

Before submitting a PR, verify:

- [ ] Interactive UI elements have `data-testid` attributes
- [ ] API error responses include error codes and affected fields
- [ ] Logs are structured with event type, context, and trace IDs
- [ ] New features have seed data or factories for test setup
- [ ] Breaking API changes are documented
- [ ] Environment configuration changes are documented
- [ ] Error messages are specific enough to triage without debugging

---

## For QA Teams

If a project does not meet these standards, the QA team should:
1. Document the gaps in a **testability recovery plan**
2. Prioritize gaps by risk tier (T0/T1 gaps block QA; T2/T3 gaps are tracked)
3. Work with the development team to schedule fixes
4. Re-assess testability after fixes are applied

See manual-qa-standards.md for the full testability assessment framework.
```

---

## 7. Manual QA & Test Design Standards

Condensed version: [Accurate-QA-Playbook.md §7](Accurate-QA-Playbook.md#7-manual-qa--test-design-standards) · Source: [`QA-GenDD/.agent/rules/manual-qa-standards.md`](QA-GenDD/.agent/rules/manual-qa-standards.md)

```markdown
---
description: Manual QA standards — test design, required test case structure, defect governance, NFR expectations, testability assessment. Load for test design, defect drafting, or manual validation.
globs:
---

# Manual QA, Test Design, and Defect Governance

---

## Manual / Exploratory / AI-Assisted Lane

Keep scope manual when it is:
- unstable or newly changing
- low-repeat
- highly visual or judgment-heavy
- low-confidence in business logic
- too expensive to automate right now

Manual coverage must still include:
- documented scenarios
- evidence capture
- traceability
- defect linkage
- periodic review for automation candidacy

### Verification intake

The manual lane is not only for non-automated functionality. It must also receive:
- automation-discovered findings that require confirmation
- ambiguous failures
- medium-confidence bug drafts
- suspected flaky behavior
- environment-sensitive failures
- findings lacking sufficient evidence for immediate defect creation

This verification lane acts as the human-in-the-loop checkpoint before confirmed defect creation.

---

## Test Design Directives

All tests should be designed with these qualities: traceable, risk-aligned, maintainable, minimal duplication, clear preconditions, clear expected results, negative paths where relevant, role/permission coverage where relevant, data boundary coverage where relevant, integration awareness where relevant.

### Prioritization order
1. Critical path success
2. Major failure paths
3. Security/permission boundaries
4. Data integrity
5. Integration reliability
6. Non-functional constraints

### Required Test Case Structure

| Field | Required | Notes |
|-------|----------|-------|
| Title | Yes | Communicates the behavior being verified |
| Purpose | Yes | Why this test exists; what risk or requirement it covers |
| Preconditions | Yes | Setup, data state, or environment assumptions |
| Steps | Yes | Numbered actions to execute |
| Expected result | Yes | Observable outcome that constitutes a pass |
| Risk level | Optional | Tier 0–3 classification when useful for prioritization |
| Automation candidate | Optional | Whether this should be automated and at which layer |
| Notes | Optional | Edge cases, known flakiness, related defects |

---

## Non-Functional QA Expectations

### Performance
Define expected performance behavior where relevant: response times, throughput, long-running process expectations, scaling assumptions, timeout tolerance.

### Security
Validate where relevant: authn/authz behavior, tenant/client separation, sensitive data exposure, secrets handling, unsafe direct object references, injection-related risk, auditability of critical actions.

### API
Validate: schema correctness, contract consistency, error handling, status codes, auth behavior, pagination/filtering/sorting when applicable, backward compatibility risk.

### Data
Validate: correctness, completeness, transformation integrity, migration impact, duplication risk, rollback behavior when relevant.

---

## Testability and Observability

A project should not be considered QA-ready unless it supports:
- actionable logs
- stable selectors for UI automation
- visible API contracts or endpoints
- controllable or seedable test data
- reproducible environments
- error details sufficient for triage
- environment visibility
- access to execution results and artifacts

If these are missing, QA must create a testability recovery plan.

---

## Defect Governance

All defects should be: traceable, evidence-backed, clearly reproducible where possible, linked to the relevant story and test asset, and prioritized by business impact and risk.

### Required defect fields
- title
- environment
- severity and priority
- steps to reproduce (or AI-suggested reproduction flow)
- actual result and expected result
- impacted story/workflow
- linked test case and execution evidence
- logs/screenshots/traces if available
- suspected cause (optional — AI-suggested root cause)

### Automation-found defects
- AI triages the failure and drafts the bug, evidence bundle, and probable cause
- If confidence is high and clearly reproducible, QA may approve direct defect creation
- If confidence is medium/low, ambiguous, flaky, or high-risk, route into the manual verification lane first

### Bug acceptance criteria
For confirmed defects, generate fix-oriented acceptance criteria describing: the intended correct behavior, the corrected happy path, important failure conditions to avoid, and validation expectations after the fix.

### Dependency and blocker tickets
When an issue reveals blocked workflows or root-cause dependencies, AI may suggest blocker tickets, dependency tickets, or linked quality follow-up tasks. QA should review before creation when impact is not obvious.

### Duplicate defect control
Minimize duplicates through AI clustering, evidence comparison, workflow matching, and QA review before final creation.

### Business intent linkage
Where available, validate defects against the Business Intent Statement to determine whether the behavior truly violates stakeholder intent or only differs from a technical assumption.

---

## Tech Debt Governance

Tech debt is not a defect. A defect violates expected behavior in the current story's scope and blocks Gate 5 (Test & QA) until resolved. Tech debt is a known shortcut, gap, or drift found *while* testing — a fragile fixture, an untested-but-accepted edge case, duplicated standards prose, a workaround — that does not block the current story. The rule is **register, don't fix**: capture it so it doesn't get silently dropped, without turning every test pass into a refactor.

### Required capture fields
See `knowledge/templates/tech-debt-template.md` for the full format. At minimum: TD-ID, title, category, found-during (which QA step/gate), source story/ticket, description, risk if unaddressed, suggested effort (S/M/L), backlog destination, status.

### Where it lands
Tech debt is logged to the **Tech Debt Backlog** — a `tech-debt`-labeled Jira issue, distinct from the defect tracker — not filed as a bug against the current story. It does not block Gate 5; the story's tests can still pass while debt is registered against it.

### Checkpoint
Any tech debt noticed during test design, execution, or evidence review must be logged via the template above **before** Gate 5 evidence is finalized for that story. See `.agent/hooks/qa-test-evidence.sh` for the automated reminder fired after test runs, and `SDLC-Quality-Gates-v1.md` Gate 5 for the enforceable pass/fail condition.

### Review cadence
Newly logged items are reviewed by the QA Lead every sprint for scheduling; backlog health is reviewed quarterly alongside the cadence in `release-and-governance.md`.
```

> **Note on cited external file:** `manual-qa-standards.md` references `SDLC-Quality-Gates-v1.md` as the source of the enforceable Gate 5 pass/fail condition and `.agent/hooks/qa-test-evidence.sh` as the automated post-test reminder. Neither file was present in the local `QA-GenDD` checkout at the time this playbook was written — they are referenced here for fidelity to the source, not reproduced.

---

## 8. Defect Governance

Condensed version: [Accurate-QA-Playbook.md §8](Accurate-QA-Playbook.md#8-defect-governance) · Source: the "Defect Governance" section of `manual-qa-standards.md` (reproduced in full in §7 above) plus the defect template below.

### `QA-GenDD/knowledge/templates/defect-templates.md` (verbatim)

```markdown
# Defect Report Templates

Standard format for defect reports, whether drafted by AI or written by a human. Fields align with the Defect Governance standards.

---

## Standard Defect Format

​```markdown
# {BUG-ID}: {Clear, specific title}

**Severity:** Critical | High | Medium | Low
**Priority:** P0 | P1 | P2 | P3
**Confidence:** High | Medium | Low
**Human Review Required:** Yes | No

## Environment
- OS: {operating system}
- Browser: {browser and version}
- Build: {version or commit}
- Environment: {staging, production, local}

## Steps to Reproduce
1. {Specific action}
2. {Specific action}
3. {Specific action}

## Expected Result
{What should happen}

## Actual Result
{What actually happens}

## Evidence
- {Screenshot, log snippet, API trace, recording}

## Impact
- Risk tier: T0/T1/T2/T3
- Impacted story/workflow: {link or reference}
- Linked test case: {TC-ID}
- User impact: {scope of affected users}

## Suspected Cause
{Optional — AI-suggested root cause or area of code}

## Fix-Oriented Acceptance Criteria
After the fix:
- {Expected correct behavior}
- {Corrected happy path}
- {Failure conditions to avoid}
- {Retest scenarios}
​```

---

## Worked Example

# BUG-234: Order confirmation sends duplicate charges on double-click

**Severity:** Critical
**Priority:** P1 — release blocker for payment flow
**Confidence:** High — fully reproducible in staging with clear evidence
**Human Review Required:** No — clearly reproducible with strong evidence

## Environment
- OS: macOS 14, Chrome 124
- Build: v2.4.1
- Environment: Staging

## Steps to Reproduce
1. Log in as test user (admin/test-tenant-1)
2. Add item to cart
3. Navigate to checkout
4. Double-click the "Place Order" button within 500ms
5. Observe two charge records in the payment gateway dashboard

## Expected Result
A single charge is created; duplicate clicks are debounced or idempotent.

## Actual Result
Two separate charges of the same amount are created in the payment gateway test mode.

## Evidence
- Payment gateway dashboard screenshot showing two charge records with identical amounts and 0.4s delta
- Server logs showing two `/api/orders` POST requests with different idempotency keys

## Impact
- Risk tier: T0 (payment/financial calculation)
- Impacted story: "User can submit an order and receive confirmation"
- Linked test case: TC-0045 (order submission idempotency)
- User impact: All users making purchases — financial risk

## Suspected Cause
Submit button handler does not disable on first click; API endpoint does not enforce idempotency key uniqueness.

## Fix-Oriented Acceptance Criteria
After the fix:
- Submitting an order must result in exactly one charge, regardless of click count
- The API must reject duplicate submissions with the same idempotency key (HTTP 409 or silent dedup)
- The submit button must be disabled after the first click until response is received
- Retest must include: single click, double click, rapid triple click, and browser back + resubmit

---

## Severity Definitions

| Level | Criteria | Examples |
|-------|----------|---------|
| **Critical** | Blocks release, data loss, security breach | Payment fails, auth bypass, data corruption |
| **High** | Major feature broken, no workaround | Search not working, checkout stuck |
| **Medium** | Feature impaired, workaround exists | Filter missing one option, display rounding |
| **Low** | Cosmetic, rare edge cases | Typo, minor alignment, tooltip content |

---

## Triage Classification

When triaging multiple findings, classify each as:

| Classification | Action |
|---------------|--------|
| Valid Defect | Create defect with full evidence |
| Needs Verification | Route to manual verification lane |
| Likely Duplicate | Link to existing issue |
| Test Issue | Fix the test, not a product bug |
| Environment Issue | Infrastructure/config problem |
| Low Value | Not worth tracking |
```

---

## 9. Tech Debt Governance

Condensed version: [Accurate-QA-Playbook.md §9](Accurate-QA-Playbook.md#9-tech-debt-governance) · Source: the "Tech Debt Governance" section of `manual-qa-standards.md` (reproduced in full in §7 above) plus the capture template below.

### `QA-GenDD/knowledge/templates/tech-debt-template.md` (verbatim, worked example generalized — see note below)

```markdown
# Tech Debt Capture Template

Standard format for registering technical debt found during QA activity (test design, test execution, evidence review, or rule/standards validation). Tech debt is **registered, not fixed** at the point it's found — this template exists to make that registration a repeatable step instead of a verbal note that evaporates.

Tech debt is not a defect. A defect is a violation of expected behavior in the current story's scope. Tech debt is a known shortcut, gap, or drift that doesn't block the current story but will cost more to fix the longer it's left — see `manual-qa-standards.md` → "Tech Debt Governance" for the full distinction.

---

## Standard Capture Format

​```markdown
# {TD-ID}: {Clear, specific title}

**Category:** Code | Test | Architecture/Design | Documentation | Process/Tooling | Data
**Found During:** {SDLC stage or gate, e.g. "Gate 5 — Test & QA", "Step 8 Evidence Review"}
**Source Story/Ticket:** {the ticket being worked when the debt was spotted}
**Reporter:** {who/what found it — human or AI-assisted}
**Date Found:** {date}

## Description
{What the debt is — the shortcut, gap, or drift, and why it wasn't fixed now}

## Risk if Unaddressed
{What gets harder or breaks later, and how urgent this is — not a severity score, a plain statement of consequence}

## Suggested Effort
T-shirt size: S | M | L — a sizing signal for backlog grooming, not a commitment

## Backlog Destination
{Where this lands — see "Where Tech Debt Lands" below}

## Status
New | Backlogged | Scheduled | Remediated | Won't Fix — Accepted
​```

---

## Required Fields

| Field | Required | Notes |
|-------|----------|-------|
| TD-ID | Yes | Unique identifier, e.g. `TD-{ticket}-{seq}` |
| Title | Yes | Specific enough to action without re-reading the description |
| Category | Yes | Drives which backlog/owner it routes to |
| Found During | Yes | Which QA step/gate surfaced it — this is what makes the checkpoint auditable |
| Source Story/Ticket | Yes | The story being tested when the debt was noticed, even if the debt itself is unrelated to that story's AC |
| Description | Yes | What it is and why it's being deferred, not fixed inline |
| Risk if Unaddressed | Yes | Forces a "why does this matter" statement instead of a bare complaint |
| Reporter | Yes | Traceability — including when AI-assisted |
| Date Found | Yes | |
| Suggested Effort | Yes | S/M/L sizing only |
| Backlog Destination | Yes | Must be a real, checkable location, not "backlog" as a vague noun |
| Status | Yes | Lifecycle tracking |

---

## Where Tech Debt Lands (Backlog)

Tech debt does **not** go into the defect tracker — it is not a bug against the current story. It lands in the team's **Tech Debt Backlog**:

- Logged as a Jira issue tagged with the `tech-debt` label (or component, per project convention), separate from the defect/bug issue type.
- Linked to the source story/ticket via the "Source Story/Ticket" field, but not blocking that story's Gate 5 (Test & QA) pass — registering debt is the requirement, not resolving it.
- Reviewed at the same cadence as other QA governance items (see `release-and-governance.md` → Review Cadence): at minimum every sprint for newly logged items, quarterly for backlog health.
- Owned by the QA Lead for triage into a scheduled sprint, per the Ownership Model in `release-and-governance.md`; engineering/product own actually resolving it once scheduled.

---

## Worked Example — Demonstration

> **Editorial note:** the source template's worked example demonstrates this capture flow using a specific internal story as the "Source Story/Ticket." The example below is a generalized, structurally identical substitute, kept general-purpose for this playbook.

# TD-EXAMPLE-01: `automation-qa-standards.md` and `core-principles.md` carried duplicated Rules Repository content with no cross-reference

**Category:** Documentation
**Found During:** Testing-standards rule-domain validation against a feature under test
**Source Story/Ticket:** {the story being tested when the debt was spotted}
**Reporter:** QA/AI-assisted validation pass, human-reviewed
**Date Found:** {date}

## Description
While validating that the `agent-assets` testing-standards rule domain (QA-001…QA-008) correctly governs the tests a story will produce, `QA-GenDD/.agent/rules/automation-qa-standards.md` and `core-principles.md` were found to carry their own informal prose for mocking and AI-generated-test review — duplicating content that now has an enforceable, ID'd home in the Rules Repository (`mocking.md` / QA-007, `ai-generated-test-review.md` / QA-008), with no link between the two. Left as-is, the two copies would drift: someone editing the Rules Repository version would have no signal that QA-GenDD's copy also needed updating, and vice versa.

## Risk if Unaddressed
Silent standards drift — the two docs disagree over time, and whichever one an engineer or agent happens to load first becomes "the rule" by accident rather than by design. Low urgency (no active incident) but compounding: every future edit to either file is a chance to widen the gap.

## Suggested Effort
S — adding a "canonical source" cross-reference is a documentation-only change, not a rework.

## Backlog Destination
Not backlogged — remediated inline during the same validation pass that found it (see Status). Logged here specifically to demonstrate the capture standard end-to-end.

## Status
**Remediated.** Cross-references were added in `automation-qa-standards.md` ("Canonical rule source: ... the enforceable, ID'd rule text lives in the Rules Repository ... When the two disagree, the Rules Repository wins.") and in the mocking/AI-review call-outs. This entry stays on record as the worked example of the capture flow, not as an open backlog item.
```

---

## 10. Automation, Testing Implementation & AI Usage

Condensed version: [Accurate-QA-Playbook.md §10](Accurate-QA-Playbook.md#10-automation-testing-implementation--ai-usage) · Source: [`QA-GenDD/.agent/rules/automation-qa-standards.md`](QA-GenDD/.agent/rules/automation-qa-standards.md)

```markdown
---
description: Automation standards — testing implementation (unit, integration, E2E), automation governance, AI usage rules, CI/CD integration. Load when writing tests or making automation decisions.
globs:
---

# Automation, Testing Implementation, and AI Usage

---

## Automated Lane

Automate first where scope is: high-value, repeatable, stable, deterministic enough, expensive to repeat manually.

Examples: smoke, sanity, regression, API validation, contract validation, integration checks, stable critical UI flows, data integrity checks.

---

## Automation Governance

Automation must be treated as a product asset, not a side activity.

- Automate high-value repeatable scenarios first
- Avoid fragile low-value UI automation
- Prefer API or integration-level validation when possible
- Define ownership for automation maintenance
- Review flaky tests regularly
- Quarantine and investigate chronic flakiness
- Remove or redesign low-signal automation
- Generate automation with AI only when maintainability is preserved

Automation is successful only if it improves signal, speed, and confidence.

> **Canonical rule source:** the directives in this file are the operator-facing summary. The enforceable, ID'd rule text lives in the Rules Repository (`agent-assets/sdlc/quality-assurance/`) as the testing-standards domain — see `mocking.md` (QA-007) for the full mocking rules and `ai-generated-test-review.md` (QA-008) for the full AI-generated-test review rules referenced below. When the two disagree, the Rules Repository wins.

---

## Overnight Execution Model

Where automation exists, use an overnight quality model:
- Run automated suites overnight
- Collect evidence automatically
- Use AI to cluster failures and separate product bugs from test bugs and flake
- Draft defects, reproduction steps, and summaries
- Identify probable duplicates, blockers, and dependencies
- Route ambiguous findings into the manual verification lane
- Only confirmed or QA-approved findings become tracked defects
- QA reviews only the meaningful outputs in the morning

---

## AI Usage Rules in QA

AI may be used to: reconstruct requirements, summarize repo context, generate markdown files, propose test cases, draft automation, cluster failures, draft bugs, suggest severity and root cause, create evidence summaries, suggest reproduction steps, identify probable duplicates, propose impacted workflows, suggest blocker or dependency tickets, generate fix-oriented acceptance criteria, and compare current behavior against the Business Intent Statement.

AI may not be trusted blindly. Any AI-generated artifact must include:
- source basis
- confidence level
- validation status
- human approval needs where applicable

For high-risk items, AI may draft but not finalize without review.

Full rule set for reviewing AI-generated tests specifically (fail-first check, traceability to AC/ticket, prohibition on self-approval, high-risk review parity): `agent-assets/sdlc/quality-assurance/ai-generated-test-review.md` (QA-008).

---

## Requirement Levels

| Level | Meaning | Enforcement |
|-------|---------|-------------|
| **MUST** | Mandatory, non-negotiable | CI/CD blocks on failure |
| **SHOULD** | Recommended best practice | PR review feedback |
| **MAY** | Optional enhancement | Team discretion |

---

## Foundational Testing Standards

- **Test Naming:** Test names must communicate intent. Common patterns: `{Method}_{Scenario}_{ExpectedResult}`, descriptive strings, or fixture-based grouping.
- **Test Structure:** Arrange-Act-Assert (AAA) pattern — every test has setup, execution, and verification sections.
- **Test Independence:** No shared mutable state, no order dependency, isolated side effects, independent setup.
- **Required Scenarios:** Happy path, invalid input, not found (always). Authorization, authentication, external failure, multi-tenant isolation (when applicable). Domain-specific scenarios only when the code handles that domain.
- **Mocking Guidelines:** Mock at boundaries (external APIs, databases in unit tests, file system, time/randomness). Do NOT mock the code under test, simple value objects, pure functions, or internal implementation. Full rule set: `agent-assets/sdlc/quality-assurance/mocking.md` (QA-007).
- **Coverage:** Priority-based (critical business logic > public APIs > data access > infrastructure). Set numeric targets per repository based on maturity and risk.

---

## Unit Testing

### Coverage Requirements (MUST)

| Area | Minimum | Rationale |
|------|---------|-----------|
| Payment/Financial code | 100% | Money-handling risk |
| Authentication/Authorization | 95% | Security risk |
| Business logic | 80% | Core functionality |
| Utilities/Helpers | 70% | Lower risk |

### Example (Python)

​```python
def test_process_payment_valid_token_returns_success():
    # Arrange
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.charge.return_value = ChargeResult(success=True)
    service = PaymentService(gateway=mock_gateway)

    # Act
    result = service.process_payment("tok_valid", 2000)

    # Assert
    assert result.success is True
    mock_gateway.charge.assert_called_once_with(amount=2000, token="tok_valid")
​```

### Example (TypeScript)

​```typescript
it('processPayment with valid token returns success', async () => {
    // Arrange
    const mockGateway = { charge: vi.fn().mockResolvedValue({ success: true }) };
    const service = new PaymentService(mockGateway);

    // Act
    const result = await service.processPayment('tok_valid', 2000);

    // Assert
    expect(result.success).toBe(true);
    expect(mockGateway.charge).toHaveBeenCalledWith({ amount: 2000, token: 'tok_valid' });
});
​```

### SHOULD (Recommended)
- Use test data builders for complex objects
- Group related tests in nested classes or describe blocks
- Include performance assertions for critical paths

---

## Integration Testing

### MUST (Enforced)

| Rule | Rationale |
|------|-----------|
| Start from clean database state | Prevents test pollution |
| No test order dependency | Tests run in any order |
| Clean up data after tests | Prevents accumulation |
| Use transactions where possible | Fast rollback |
| Isolate test tenants | Multi-tenant safety |

### Database Lifecycle Example (Python)

​```python
class TestPaymentIntegration:
    def setup_method(self):
        self.db = TestDatabase()
        self.db.reset()
        self.db.seed_test_data()

    def teardown_method(self):
        self.db.cleanup_test_data()
​```

### Database Lifecycle Example (TypeScript)

​```typescript
describe('PaymentIntegration', () => {
    let db: TestDatabase;

    beforeEach(async () => {
        db = new TestDatabase();
        await db.reset();
        await db.seedTestData();
    });

    afterEach(async () => {
        await db.cleanupTestData();
    });
});
​```

---

## E2E Testing

### Selector Rules (MUST)

| Do | Don't |
|----|-------|
| `[data-testid="submit-button"]` | `button:has-text("Submit")` |
| `[data-testid="email-input"]` | `.btn-primary`, `#submit` |
| Explicit data attributes | XPath, text selectors, CSS classes |

### Waiting Rules (MUST)

| Do | Don't |
|----|-------|
| `waitForSelector('[data-testid="..."]')` | `waitForTimeout(3000)` |
| `waitForResponse(...)` | `sleep(5000)` |
| `expect(...).toBeVisible()` | Arbitrary delays |

---

## Domain-Specific Test Scenarios

| Domain | Key Scenarios |
|--------|---------------|
| **Payment / Financial** | Card validation, AVS, PIN masking, idempotency, anomaly detection |
| **Email / Notifications** | Delivery triggers, template data, receipt accuracy, deduplication |
| **Security / Auth** | Account lockout, password policy, session expiry |
| **Regression / Sanity** | Health endpoint, critical-path smoke, full regression suite |
| **UI / Accessibility** | Responsive breakpoints, WCAG 2.1 AA, keyboard navigation |

---

## Test Data Management

### Data Patterns

​```typescript
const testUser = TestDataFactory.createUser({
    role: 'admin',
    tenant: 'test-tenant-1'
});
​```

---

## CI/CD Integration

| Stage | Tests Run | Blocking |
|-------|-----------|----------|
| PR | Unit + Fast Integration | Yes |
| Merge to main | Full Integration | Yes |
| Nightly | E2E + Load | No (alerts) |

See `knowledge/stacks/` for language-specific tooling recommendations and CI examples.

---

## Usage

1. Copy relevant sections to your repository's `testing.md`
2. Replace framework examples with your specific frameworks
3. Customize coverage requirements for your risk profile
4. Review with QA team
5. Integrate into CI/CD pipeline
6. See `knowledge/stacks/` for language-specific tooling guidance
```

---

## 11. Testing-Standards Rules Repository Cross-Reference

Condensed version: [Accurate-QA-Playbook.md §11](Accurate-QA-Playbook.md#11-testing-standards-rules-repository-cross-reference) · Source: `agent-assets/sdlc/quality-assurance/*.md` (QA-001–QA-008), cross-referenced by `QA-GenDD/.agent/rules/automation-qa-standards.md`

### QA-001 — Test Strategy Standards (verbatim)

```markdown
---
id: QA-001
title: Test Strategy Standards
phase: quality-assurance
extends: null
tech: null
summary: Rules for the test pyramid and what to test at each level.
tags: [qa, test-strategy, test-pyramid, unit, integration, e2e]
applies_to: ["**/*"]
version: "2.0.0"
last_reviewed: "2026-07-13"
---

# Test Strategy Standards (QA-001)

## Purpose

An unplanned test strategy results in brittle, expensive test suites or dangerously low coverage. The test pyramid provides a principled approach to allocating test effort across levels.

---

## MUST

- **QA-001-01** Every service has a documented test strategy before production release, describing: the test pyramid levels applied, coverage targets per level, which layers are covered by automated vs manual tests, and the tooling at each level.
- **QA-001-02** The test suite follows the test pyramid: unit tests (test individual functions/classes in isolation) form the majority; integration tests (test collaboration including real or in-memory dependencies) are significantly fewer; end-to-end tests (complete user flows through the full stack) cover only a small set of critical path scenarios.

## MUST NOT

- **QA-001-03** Rely solely on end-to-end tests as the primary quality gate.

## SHOULD

- **QA-001-04** Before writing an integration or end-to-end test, evaluate whether a unit test can adequately verify the same behaviour. Only escalate to a higher level when the lower level cannot verify the interaction in question.
```

### QA-002 — Test Automation Standards (verbatim)

```markdown
---
id: QA-002
title: Test Automation Standards
phase: quality-assurance
extends: null
tech: null
summary: Rules for automation structure, test naming, determinism, and maintainability.
tags: [qa, test-automation, naming, determinism, aaa, structure]
applies_to: ["**/*.test.*", "**/*.spec.*", "**/test/**", "**/tests/**", "**/__tests__/**"]
version: "2.0.0"
last_reviewed: "2026-07-13"
---

# Test Automation Standards (QA-002)

## Purpose

Test suites that are hard to read, flaky, or order-dependent lose the trust of the team and are gradually disabled. These standards make automated tests reliable, understandable, and maintainable.

---

## MUST

- **QA-002-01** Test names describe the unit under test, the scenario, and the expected outcome. Format: `[unit]_[scenario]_[expected outcome]` or plain English sentence. Acceptable: `"createUser when email already exists throws DuplicateEmailException"`. Not acceptable: `"testCreateUser"`, `"test1"`, `"should work"`.
- **QA-002-02** Every test follows Arrange/Act/Assert: Arrange (set up the system and inputs), Act (invoke the single action being tested), Assert (verify the expected outcome). Each section is separated by a blank line or comment. A test contains only one Act section.
- **QA-002-03** Tests are deterministic: no dependency on current time without an injectable clock, no random data without a fixed seed or controlled input, no real external network calls in unit tests (use mocks/stubs), no shared mutable state between tests.

## MUST NOT

- **QA-002-04** Write tests that depend on each other's execution order. Each test sets up its own state and cleans up after itself.

## SHOULD

- **QA-002-05** Each test verifies a single, focused behaviour. Tests verifying multiple unrelated outcomes are split.

---

## Tech-Specific Standards

| Technology | Overlay file | Applies to |
|---|---|---|
| JUnit | `junit/test-automation.md` | `**/*Test.java` |
```

### QA-003 — Test Coverage Standards (verbatim)

```markdown
---
id: QA-003
title: Test Coverage Standards
phase: quality-assurance
extends: null
tech: null
summary: Coverage expectations, how they are measured, and what they do and do not guarantee.
tags: [qa, coverage, metrics, branch-coverage, line-coverage]
applies_to: ["**/*"]
version: "2.0.0"
last_reviewed: "2026-07-13"
---

# Test Coverage Standards (QA-003)

## Purpose

Coverage metrics are useful signals but imperfect guarantees. These standards establish meaningful targets while preventing the common failure mode of "gaming" coverage with low-quality tests.

---

## MUST

- **QA-003-01** Coverage is measured and reported in the CI pipeline for every pull request. CI blocks merge if coverage falls below the minimum thresholds.
- **QA-003-02** Production application code maintains a minimum of 80% line coverage. Auto-generated code, configuration files, framework boilerplate, and data transfer objects may be excluded from coverage calculation via the project's coverage tool configuration.

## MUST NOT

- **QA-003-03** Write tests that increase coverage without making meaningful assertions about the behaviour. Tests that call a method and assert only that no exception was thrown, without asserting the result, are not an acceptable coverage strategy.

## SHOULD

- **QA-003-04** Branch coverage of at least 70% is targeted in addition to line coverage.
```

### QA-004 — Test Data Management Standards (verbatim)

```markdown
---
id: QA-004
title: Test Data Management Standards
phase: quality-assurance
extends: null
tech: null
summary: Rules for fixtures, factories, and the prohibition of production data in tests.
tags: [qa, test-data, fixtures, factories, pii, production-data]
applies_to: ["**/*.test.*", "**/*.spec.*", "**/test/**", "**/fixtures/**"]
version: "2.0.0"
last_reviewed: "2026-07-13"
---

# Test Data Management Standards (QA-004)

## Purpose

Test data that is hardcoded, shared, or sourced from production creates brittle, insecure, and non-reproducible tests. These standards ensure test data is safe, isolated, and maintainable.

---

## MUST

- **QA-004-01** Test data is created using factory functions, builder objects, or data-generation libraries rather than hardcoded fixture files. Each factory provides sensible defaults that produce a valid object with the ability to override specific fields for the scenario under test.

## MUST NOT

- **QA-004-02** Use data extracted from production systems in tests. Test databases are populated with synthetic or anonymised data only. See `sdlc/database/pii-handling.md`.
- **QA-004-03** Commit test fixture files containing real PII (real names, email addresses, phone numbers, national IDs, financial data). Use obviously synthetic values (e.g. `test@example.com`, `John Test`, `555-0100`) or randomised fake data libraries.

## SHOULD

- **QA-004-04** Each test creates only the data it needs in a scoped context (e.g. within a transaction that is rolled back, or in a freshly created test scope). Shared test data sets are avoided in favour of per-test data setup.
```

### QA-005 — Flaky Test Policy (verbatim)

```markdown
---
id: QA-005
title: Flaky Test Policy
phase: quality-assurance
extends: null
tech: null
summary: Rules for detecting, quarantining, and fixing flaky tests with SLAs.
tags: [qa, flaky-tests, quarantine, reliability, ci]
applies_to: ["**/*.test.*", "**/*.spec.*", "**/test/**"]
version: "2.0.0"
last_reviewed: "2026-07-13"
---

# Flaky Test Policy (QA-005)

## Purpose

Flaky tests erode trust in the test suite. When developers cannot trust CI to give reliable signal, they start ignoring failures — including real ones. These standards treat flaky tests as defects that must be resolved on a schedule.

---

## MUST

- **QA-005-01** A test that fails intermittently without a code change is moved to a quarantine category within 24 hours of identification. Quarantined tests do not block the CI pipeline. A ticket is created to track the fix.
- **QA-005-02** Quarantined tests are fixed or deleted within 14 calendar days of quarantine. If the underlying behaviour cannot be tested reliably within 14 days, the test is deleted and a tracking ticket is created for a better-designed replacement.

## MUST NOT

- **QA-005-03** Permanently disable tests (using `@Ignore`, `@Skip`, `xit`, or equivalent) without a linked, active ticket. Disabled tests that have been in the repository for more than 30 days with no active remediation are removed.

## SHOULD

- **QA-005-04** Flaky tests are tracked in the team's bug backlog with the same severity as production bugs, with the root cause documented in the fix ticket.
```

### QA-006 — Non-Functional Testing Standards (verbatim)

```markdown
---
id: QA-006
title: Non-Functional Testing Standards
phase: quality-assurance
extends: null
tech: null
summary: Rules for performance, load, security, and accessibility testing.
tags: [qa, performance-testing, load-testing, security-testing, accessibility, non-functional]
applies_to: ["**/*"]
version: "2.0.0"
last_reviewed: "2026-07-13"
---

# Non-Functional Testing Standards (QA-006)

## Purpose

Functional tests verify what a system does. Non-functional tests verify how it performs. Systems without non-functional testing frequently fail their NFRs only after reaching production.

---

## MUST

- **QA-006-01** For any service with defined NFRs (see `sdlc/architecture/non-functional-requirements.md`), at least one automated test validates each NFR before the first production deployment. NFRs that cannot be validated by an automated test have a documented manual verification procedure.
- **QA-006-02** Load and performance tests run against a staging environment, never against production. Staging matches production in data volume, configuration, and hardware tier for results to be valid.

## SHOULD

- **QA-006-03** CI pipelines include SAST scanning against source code. DAST runs against the staging environment on a scheduled basis or before major releases. Security test results are reviewed and tracked with the same SLA as vulnerability findings in `sdlc/security/vulnerability-management.md`.
- **QA-006-04** User-facing UI features are tested for WCAG 2.1 Level AA conformance using automated scanning (e.g. axe-core, Lighthouse) in the UI test suite, with manual keyboard navigation and screen reader testing for critical user flows.
```

### QA-007 — Mocking Standards (verbatim)

```markdown
---
id: QA-007
title: Mocking Standards
phase: quality-assurance
extends: null
tech: null
summary: Rules for where mocking belongs, what must never be mocked, and how mocked dependencies stay faithful to the real contract.
tags: [qa, mocking, test-doubles, fakes, boundaries]
applies_to: ["**/*.test.*", "**/*.spec.*", "**/test/**", "**/tests/**", "**/__tests__/**"]
version: "1.0.0"
last_reviewed: "2026-07-30"
---

# Mocking Standards (QA-007)

## Purpose

Mocking is a tool for isolating a unit from dependencies it does not own, not a way to avoid testing behaviour. Mocking the wrong thing hides real integration defects, and asserting on a mock's internals couples tests to implementation rather than behaviour. These standards define where mocking belongs and where it does not.

---

## MUST

- **QA-007-01** Mock only at architectural boundaries the test does not own: external HTTP/API calls, databases in unit tests, the file system, and system clock/randomness sources.
- **QA-007-02** Model a mocked dependency's request and response shape after its real, currently-documented contract, including its documented error responses, so the mock cannot silently diverge from the behaviour it stands in for.
- **QA-007-03** Provide both success and failure/error response fixtures for every mocked external dependency, so failure-handling logic is exercised and not only the happy path.

## MUST NOT

- **QA-007-04** Mock the unit under test itself, pure functions, simple value objects or DTOs, or internal implementation details of the code being verified.
- **QA-007-05** Assert on a mocked collaborator's internal call order or private state when the test's purpose is to verify observable behaviour. Assert on the inputs and outputs of the interaction instead.
- **QA-007-06** Rely on live calls to third-party vendor services in unit tests or automated PR-gating tests. Validate a vendor integration itself through a contract test or a controlled vendor sandbox, not by mocking the vendor away.

## SHOULD

- **QA-007-07** Prefer a fake or in-memory test double over a deep chain of stubbed mock calls when the dependency has meaningful behaviour worth modelling, for example an in-memory repository instead of a mocked data-access object with dozens of stubbed methods.
- **QA-007-08** Update a mocked dependency's stubbed responses whenever the real dependency's contract changes, so the mock does not drift out of sync with production behaviour.

## MAY

- **QA-007-09** Maintain a shared mock or fixture library for a frequently-mocked external dependency, such as a common vendor API, to keep stub definitions consistent across test suites.
```

### QA-008 — AI-Generated Test Review Standards (verbatim)

```markdown
---
id: QA-008
title: AI-Generated Test Review Standards
phase: quality-assurance
extends: null
tech: null
summary: Rules for validating AI-authored or AI-assisted tests before they are trusted as a quality gate.
tags: [qa, ai-generated-tests, review, gendd, validation]
applies_to: ["**/*.test.*", "**/*.spec.*", "**/test/**", "**/tests/**", "**/__tests__/**"]
version: "1.0.0"
last_reviewed: "2026-07-30"
---

# AI-Generated Test Review Standards (QA-008)

## Purpose

An AI agent can produce a test suite that reaches a target coverage number while asserting nothing meaningful, or that encodes the current, possibly buggy, behaviour of the code as the expected result. These standards ensure a human validates AI-authored or AI-assisted tests before they are trusted as regression protection or release evidence.

## Scope

Applies to any test file authored, substantially drafted, or substantially modified by an AI coding agent, regardless of language or stack. Does not replace the directives in `test-automation.md` (QA-002) or `coverage.md` (QA-003) — an AI-generated test is still subject to those standards in full; this file adds the review obligations specific to AI authorship.

---

## MUST

- **QA-008-01** A human reviewer reads and approves every AI-generated test file before it is merged. An AI agent's own summary or self-report of passing tests is not sufficient sign-off.
- **QA-008-02** Before an AI-generated test is trusted as a regression guard, confirm that it fails when the code under test is reverted to its pre-fix or pre-feature state and passes only against the correct behaviour. Delete or rewrite a test that passes regardless of the implementation it is supposed to verify.
- **QA-008-03** Every AI-generated test carries traceability to the requirement, acceptance criterion, or defect it verifies, for example a reference to the AC ID or ticket number in the test name, display name, or an adjacent comment.
- **QA-008-04** AI-generated test suites for high-risk code — payment, authentication, identity verification, and PII handling — receive the same senior-engineer review required for human-written tests in that risk tier. AI authorship does not lower the review bar.

## MUST NOT

- **QA-008-05** Accept an AI-generated test that only calls the method under test and asserts the absence of an exception, without asserting on the actual result or resulting state, as satisfying coverage or acceptance-criteria requirements.
- **QA-008-06** Treat an AI agent's reported coverage percentage or reported "all tests passing" status as sufficient release evidence without independent human review or a deterministic CI-enforced check.
- **QA-008-07** Allow an AI agent to mark its own generated tests as validated or approved. Validation status is set by a human reviewer or a deterministic CI gate, never by the generating agent.

## SHOULD

- **QA-008-08** Record, alongside each AI-generated test artefact, its source basis (the requirement or spec section it was generated from), a confidence level, and its current validation status, so reviewers can prioritise scrutiny.
- **QA-008-09** Spot-check AI-generated test data and fixtures for realistic-looking PII the model may have fabricated or carried over from its prompt context, in addition to the standing prohibition on real PII in `test-data-management.md` (QA-004).

## MAY

- **QA-008-10** Use a second AI pass to review a first AI pass's generated tests for tautological assertions or missed edge cases, as a pre-filter before human review. This does not replace the human review required by QA-008-01.
```

---

## 12. Release Readiness & Governance

Condensed version: [Accurate-QA-Playbook.md §12](Accurate-QA-Playbook.md#12-release-readiness--governance) · Source: [`QA-GenDD/.agent/rules/release-and-governance.md`](QA-GenDD/.agent/rules/release-and-governance.md)

```markdown
---
description: Release readiness rules, human approval gates, ownership model, review cadence. Load for release decisions or governance reviews.
globs:
---

# Release Readiness and Governance

---

## Required QA Outputs

Every project should maintain, directly or indirectly:
- QA strategy
- Test plan
- Business logic QA context
- Risk matrix
- Traceable test cases
- Automation scope definition
- Test data strategy
- Environment strategy
- Defect triage rules
- Release readiness summary
- Evidence-backed release recommendation

---

## Release Readiness Rules

A release recommendation must be based on evidence, not intuition.

Release decisions should consider:
- risk coverage
- confidence of recovered requirements
- automated results
- manual coverage status
- open critical defects
- flaky test rate
- environment confidence
- stakeholder validation gaps
- security/performance concerns

### Possible release outcomes
- **Release recommended** — evidence supports shipping
- **Release conditionally recommended** — known, documented risks accepted
- **Release not recommended** — unresolved blockers or insufficient coverage
- **Insufficient evidence** — cannot make a confident recommendation

---

## Minimum Human Approval Gates

Human review is required for:
- low-confidence critical requirements
- severe security/privacy issues
- release blockers
- high-impact business logic defects
- AI-drafted severe defects
- automatic actions with tenant/client exposure
- final release recommendation
- automation-detected findings that are ambiguous, flaky, environment-sensitive, or insufficiently evidenced

---

## Ownership Model

| Role | Responsibilities |
|------|-----------------|
| **QA Lead / QA Architect** | Quality strategy, governance, risk, release recommendation |
| **QA Engineer** | Execution oversight, evidence review, manual lane management, triage review |
| **QA Automation Engineer** | Framework design, automated lane coverage, maintenance, reliability |
| **AI Agents / AI Tooling** | Generation, summarization, clustering, drafts, repetitive execution support |
| **Engineering / Product** | Business clarification, testability support, defect resolution, release accountability |

---

## Review Cadence

These standards should be reviewed:
- at project kickoff
- when delivery model changes
- when major risk classes change
- when automation reliability degrades
- at quarterly QA governance review at minimum

---

## Final Directive

QA must operate as a scalable, AI-first, evidence-based quality system.

QA is not a bottleneck. QA enables faster delivery, clearer decisions, and better quality with less rework.

The goal is not to manually test everything. The goal is to have enough evidence for the current level of risk — and to create the fastest and most reliable path to release confidence with:
- clear traceability
- intelligent automation
- managed manual coverage
- AI-assisted triage
- human governance where it matters

Focus on: **risk, evidence, clarity, traceability**.
```

### Release Assessment Format & Worked Example

Source: [`QA-GenDD/knowledge/templates/release-templates.md`](QA-GenDD/knowledge/templates/release-templates.md) (verbatim)

```markdown
# Release Readiness Assessment Templates

Standard format for release readiness assessments. Fields align with the Release Readiness and Governance standards.

---

## Standard Release Assessment Format

​```markdown
# Release Readiness: {Release Name / Version}

## Status: {Recommended | Conditionally Recommended | Not Recommended | Insufficient Evidence}

## Summary
{2-3 sentences: overall status, key strengths, key gaps}

## Risk Coverage

| Area | Tier | Coverage | Evidence |
|------|------|----------|----------|
| {Feature/area} | T0/T1/T2/T3 | Full/Partial/None | {Evidence summary} |

## Requirement Confidence
- {Area}: {High/Medium/Low} — {basis}

## Open Defects

| ID | Severity | Status | Impact |
|----|----------|--------|--------|
| {BUG-ID} | Critical/High/Medium/Low | Open/In Progress | {Brief impact} |

## Automated Results
- Unit: {pass}/{total} passing
- Integration: {pass}/{total} passing
- E2E: {pass}/{total} passing
- Flaky rate: {percentage} ({count}/{total})

## Manual Coverage
- {What was tested manually}
- {Evidence captured}
- {Findings}

## Environment Confidence
- {Environment name}: {confidence level} — {notes}

## Stakeholder Validation
- {Who reviewed what — approved/pending}

## Key Risks Going Forward
1. {Risk and mitigation}

## Required Next Steps
- [ ] {Action item}

## Human Review Items
- {Items requiring human approval before shipping}
​```

---

## Release Outcome Definitions

| Outcome | Meaning | Required Evidence |
|---------|---------|-------------------|
| **Recommended** | Evidence supports shipping | All T0/T1 covered, no critical defects, stakeholder approval |
| **Conditionally Recommended** | Known risks accepted | Risks documented, workarounds in place, product owner sign-off |
| **Not Recommended** | Unresolved blockers | Critical defects open, or T0/T1 areas without coverage |
| **Insufficient Evidence** | Cannot make a confident call | Major coverage gaps, environment issues, missing validation |

## Pass/Fail Criteria

**PASS (recommend release):**
- All T0 areas have evidence
- No open Critical defects
- Flaky rate below threshold
- Stakeholder validation complete

**FAIL (block release):**
- Any T0 area without evidence
- Open Critical defect
- Security vulnerability discovered
- Data loss scenario identified

**CONDITIONAL:**
- T1 gaps with documented workarounds
- Medium defects with product owner acceptance
- Known environment limitations documented
```

---

## 13. SDLC Triggers (T1–T8)

Condensed version: [Accurate-QA-Playbook.md §13](Accurate-QA-Playbook.md#13-sdlc-triggers-t1t8) · Source: [`QA-GenDD/.agent/rules/sdlc-triggers.md`](QA-GenDD/.agent/rules/sdlc-triggers.md)

```markdown
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
- **Where it enters the QA workflow** — step numbers from workflows.md
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

Pass `--stack` (python, typescript, java, go, cpp, dotnet) to load a stack profile from `knowledge/stacks/` that injects framework-specific context into the LLM prompts and selects the correct artifact parser. See `engine/ci/README.md` for setup, per-stack CI examples, and usage.

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

Five of these triggers are automated via Cursor IDE hooks in `.agent/hooks.json`. See `.agent/hooks/` for the implementation scripts.

| Cursor Hook | Event | Maps to SDLC Trigger | Behavior |
|-------------|-------|---------------------|----------|
| Session init | `sessionStart` | All (T1–T8) | Injects QA standards context at session start |
| Test file edit | `afterFileEdit` | T3, T4 | Reminds agent of test structure rules when test files are edited |
| Test evidence | `afterShellExecution` | T4, T5 | Prompts evidence review after test commands complete |
| Story update | `afterFileEdit` | T8 | Triggers story update loop check when requirement files change |
| Release gate | `beforeShellExecution` | T6 | Asks for release readiness confirmation before deploy commands |

---

## Related documents

- QA Core Principles (core-principles.md) — Foundation principles referenced by trigger definitions
- QA Workflows (workflows.md) — Greenfield and brownfield step numbers referenced above
- QA Planner (qa-planner.md) — Routing table and prompts invoked at each trigger
- Artifact templates (`../../knowledge/templates/`) — Worked examples of QA outputs
```

---

## 14. QA Planner — Routing, Checklists & Anti-Patterns

Condensed version: [Accurate-QA-Playbook.md §14](Accurate-QA-Playbook.md#14-qa-planner--routing-checklists--anti-patterns) · Source: [`QA-GenDD/.agent/rules/qa-planner.md`](QA-GenDD/.agent/rules/qa-planner.md)

```markdown
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
- **CI automation:** `engine/ci/qa-orchestrator.py` runs automated pipeline triage in this order: **11-evidence → 10-triage → 09-defects → 12-release** (not numeric order). It does **not** run **13-review** — that prompt is for IDE/human quality review of AI-generated QA artifacts. See `engine/ci/README.md`.

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
| `test-case-templates.md` | Standard test case format with worked examples |
| `defect-templates.md` | Defect report format with worked examples |
| `release-templates.md` | Release readiness format with worked examples |
| `testing-standards.md` | Customizable per-repo testing standards (MUST/SHOULD/MAY) |
```

---

## 15. Onboarding a New Tech Stack

Condensed version: [Accurate-QA-Playbook.md §15](Accurate-QA-Playbook.md#15-onboarding-a-new-tech-stack) · Source: [`QA-GenDD/.agent/rules/qa-standards-creator.md`](QA-GenDD/.agent/rules/qa-standards-creator.md)

```markdown
---
description: QA Standards Creator — generates stack-specific testing guidance and CI profiles for any technology stack. Load when onboarding a new project or creating QA standards for an unsupported stack.
globs:
---

# QA Standards Creator

---

## Quick Start

**Generate from a known stack:**
​```text
"Create QA testing guidance for a Rust project using cargo test"
​```

**Generate from brownfield analysis:**
​```text
"Using this brownfield analysis context, create stack-specific QA standards: [paste analysis]"
​```

**Generate both guidance and CI profile:**
​```text
"Create testing guidance and CI profile for a Ruby on Rails project with RSpec"
​```

---

## What It Produces

For any tech stack, this skill generates two files:

### 1. `{stack}-testing-guidance.md`
A markdown file containing:
- Purpose and audience
- How the stack maps to HatchWorks QA themes (evidence, risk tiering, confidence, coverage, automation governance, defect flow)
- Typical test layers (unit, integration, E2E) with stack-specific tools
- Primary tooling table (runner, assertions, mocks, coverage, orchestration)
- Project layout and common commands
- CI quality gates
- Non-functional testing hooks
- Cross-cutting practices from HatchWorks standards
- Exemplary open-source repository for reference

### 2. `{stack}.yml`
A YAML CI profile containing:
- `name` and `description`
- `test_command` — the default test invocation
- `artifact_format` — `junit_xml`, `trx`, or other
- `coverage_format` — `cobertura_xml`, `lcov`, etc.
- `frameworks` — runner, assertions, mocks, coverage, orchestration
- `common_artifacts` — where test results, coverage, and logs land
- `ci_example` — shell snippet for running tests and the QA orchestrator
- `stack_context` — LLM-injectable context for framework-aware triage
- `guidance` — relative path to the companion `.md` file

---

## How It Works

​```text
Input (stack name, brownfield analysis, or project description)
    |
    v
+-------------------------------------------------------+
| 1. IDENTIFY STACK                                     |
|    - Detect language, framework, test runner           |
|    - Identify CI/CD platform if mentioned              |
+-------------------------------------------------------+
    |
    v
+-------------------------------------------------------+
| 2. LOAD REFERENCES                                    |
|    - Read .agent/rules/core-principles.md for QA themes         |
|    - Read .agent/rules/automation-qa-standards.md for test rules |
|    - Read 1-2 existing knowledge/stacks/ files as format models |
+-------------------------------------------------------+
    |
    v
+-------------------------------------------------------+
| 3. GENERATE                                           |
|    - Create {stack}-testing-guidance.md                |
|    - Create {stack}.yml                               |
|    - Map QA themes to stack-specific tools             |
+-------------------------------------------------------+
    |
    v
+-------------------------------------------------------+
| 4. VALIDATE                                           |
|    - Run checklist below                              |
|    - Ensure all required sections are present          |
+-------------------------------------------------------+
    |
    v
Files ready in knowledge/stacks/
​```

---

## Verification Checklist

Run after generating. Fix any failures.

### Testing Guidance (.md)
- [ ] Has "Purpose and audience" section
- [ ] Has "Inherits from" section referencing `.agent/rules/core-principles.md` and `.agent/rules/automation-qa-standards.md`
- [ ] Has "How this stack supports the Global QA flow" mapping table
- [ ] Has "Typical test layers" table (unit, integration, E2E)
- [ ] Has "Primary tooling" table with real, current tool names
- [ ] Has "Project layout and commands" section
- [ ] Has "CI and quality gates" section
- [ ] Has "Non-functional testing hooks" section
- [ ] Has "Cross-cutting practices" section
- [ ] References an exemplary open-source repository
- [ ] No tool-specific QA jargon (no Jira, Xray, Mori references)
- [ ] All tools mentioned actually exist and are current

### CI Profile (.yml)
- [ ] Has all required fields: name, description, test_command, artifact_format, coverage_format
- [ ] Has frameworks block with at least: runner, assertions, mocks, coverage
- [ ] Has common_artifacts block
- [ ] Has ci_example with working shell commands
- [ ] Has stack_context with framework-specific triage hints
- [ ] Has guidance field pointing to the companion .md file
- [ ] artifact_format matches what the test runner actually produces

---

## Anti-Patterns

| Avoid | Do Instead |
|-------|-----------|
| Invent tool names | Only reference real, actively maintained tools |
| Copy Python guidance for all stacks | Research the idiomatic testing approach for each language |
| Skip the QA theme mapping table | This is what connects stack tooling to HatchWorks methodology |
| Use outdated framework versions | Check current ecosystem conventions |
| Hardcode paths | Use relative paths that work from the repo root |

---

## Reference Examples

Pre-built stack files in `knowledge/stacks/` serve as format models:

| Stack | Guidance | Profile |
|-------|----------|---------|
| Python | `knowledge/stacks/python-testing-guidance.md` | `knowledge/stacks/python.yml` |
| TypeScript | `knowledge/stacks/typescript-testing-guidance.md` | `knowledge/stacks/typescript.yml` |
| Java | `knowledge/stacks/java-testing-guidance.md` | `knowledge/stacks/java.yml` |
| Go | `knowledge/stacks/go-testing-guidance.md` | `knowledge/stacks/go.yml` |
| C++ | `knowledge/stacks/cpp-testing-guidance.md` | `knowledge/stacks/cpp.yml` |
| .NET | `knowledge/stacks/dotnet-testing-guidance.md` | `knowledge/stacks/dotnet.yml` |

When generating for a new stack, read at least one of these as a structural template.
```

---

## 16. Prompt Library

Condensed version: [Accurate-QA-Playbook.md §16](Accurate-QA-Playbook.md#16-prompt-library) · Source: [`QA-GenDD/engine/prompts/`](QA-GenDD/engine/prompts/) (15 files, verbatim below)

### 01 — Feature Intake

```markdown
# Feature Intake

## When to Use
Use this prompt when starting work on a **new feature, story, or change request**.

This is the **first step of QA in GenDD**, where we:
- understand intent
- identify risks
- define validation scope

---

## Instructions

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

---

## Prompt

Analyze the following feature, story, or requirement:

[PASTE FEATURE / STORY / DESCRIPTION HERE]

---

## Output Format

### 1. Intent Summary
- What is being built or changed?
- Who is the user?
- What is the expected outcome?
- What does success look like?

---

### 2. Main User Flow
Describe the primary (happy path) workflow step-by-step.

---

### 3. Risk Identification (Risk-First)

Identify and categorize risks:

#### High Risk (Tier 0 / Tier 1)
- Security, authentication, data integrity, core workflows

#### Medium Risk (Tier 2)
- Integrations, background processes, reporting

#### Low Risk (Tier 3)
- UI, cosmetic, low-impact behavior

---

### 4. Key Scenarios (Prioritized)

List validation scenarios grouped by priority:

#### High Priority
- Critical path success
- Major failure paths
- Permission/security checks
- Data integrity validation

#### Medium Priority
- Secondary workflows
- Integration behavior
- Edge cases with moderate impact

#### Low Priority
- UI behavior
- Non-critical variations

---

### 5. Acceptance Criteria (Gherkin Format)

Generate structured acceptance criteria in Gherkin syntax for each key scenario:

​```
GIVEN [precondition]
WHEN [action]
THEN [expected outcome]
AND [additional assertion]
​```

Requirements:
- ACs describe **expected behavior**, not implementation steps
- Cover the happy path, at least one error condition, and at least one edge case per T0/T1 area
- Each AC must be testable and unambiguous
- Include at least 5 edge cases (multi-tenant isolation, integration failures, null/empty inputs, concurrency, accessibility)

---

### 6. Definition of Ready Checklist

Verify the feature meets the following before it enters development:

| Criterion | Status |
|-----------|--------|
| Clear problem statement | Met / Not Met / Partial |
| ACs describe expected behavior (not implementation) | Met / Not Met / Partial |
| Scope boundaries defined (in/out of scope) | Met / Not Met / Partial |
| Integration impact identified | Met / Not Met / Partial |
| Security/compliance review flagged (if applicable) | Met / Not Met / Partial |
| Environment/data dependencies documented | Met / Not Met / Partial |
| Unknowns explicitly listed (not implicit) | Met / Not Met / Partial |

> "Unknown" is acceptable. "Implicit" is not.

---

### 7. Coverage Recommendation

For each scenario group, indicate:

- Automate → stable, repeatable, high-value
- Manual → exploratory, new, uncertain, visual
- Either → flexible based on context

---

### 8. Evidence Requirements

What evidence should be captured during validation?

Examples:
- logs
- API responses
- screenshots
- execution results
- system outputs

---

### 9. Assumptions and Unknowns

List:
- missing requirements
- unclear behavior
- dependencies not defined
- potential gaps in logic

---

### 10. Confidence Levels

For inferred elements, classify:

- High → strong evidence or clear requirement
- Medium → likely correct but needs validation
- Low → assumption or unclear, requires confirmation

---

## Output Expectations

The result must be:
- clear and structured
- easy to execute
- aligned with risk-first QA
- usable without additional interpretation

Do NOT:
- overcomplicate
- assume perfect requirements
- skip risk prioritization

---

## AC Anti-Patterns to Prevent

| Anti-Pattern | Problem | What to Do Instead |
|--------------|---------|-------------------|
| ACs in description field only | Not visible, not tracked | Generate ACs as a distinct section |
| "See STR" patterns | Expected behavior undefined | Explicitly document expected behavior |
| Missing edge cases | QA discovers issues via bugs | Generate 5+ edge cases per feature |
| Implicit integration impact | Late discovery of downstream effects | Surface integration questions explicitly |
| Vague scope boundaries | Scope creep | Define in-scope and out-of-scope |

---

## Goal

Produce a **QA-ready feature understanding** that:
- aligns with GenDD (intent-first)
- includes testable Gherkin acceptance criteria
- meets Definition of Ready before entering development
- enables scenario creation
- accelerates validation
- reduces ambiguity for QA and development
```

### 02 — Greenfield QA Strategy

```markdown
# Greenfield QA Strategy

## When to Use

Use this prompt when defining how to **develop with quality from the start (Greenfield)** for a new product, feature, or system. The goal is to build with quality embedded from the beginning using context-first development, AI-assisted execution, human-in-the-loop QA governance, and risk/confidence as decision drivers.

This is NOT about writing test cases or diagrams — this is about defining a **quality-driven development workflow**.

---

## Prompt

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

You are acting as an AI-native QA Architect operating within the **HatchWorks QA methodology**.

Given a new product, feature, or system, define how to **build it with quality embedded from the beginning**, using the Greenfield QA workflow.

---

## Greenfield QA Flow (Reference Model)

Use this structure as the foundation:

1. Product intent defined
2. Validate and structure context
3. Build scope and QA structure
4. Create test baseline
5. Risk + Confidence classification
6. Dual validation paths
7. Execution
8. Evidence + AI triage
9. QA decision
10. Confirmed defects

---

## Output Requirements

Produce a structured QA strategy that explains:

### 1. Intent → Quality Translation

- How business intent becomes:
  - requirements
  - acceptance criteria
  - testable behavior

---

### 2. Context Design

- How to structure assumptions around business intent and system behavior
- How to define expected flows and map them to testable outcomes
- How to identify risks early through context analysis and requirement gaps
- What must be validated before coding starts

---

### 3. Scope and QA Structure

- How stories are defined
- How QA is embedded in scope creation
- How traceability is established early

---

### 4. Test Design Strategy

- How test cases are:
  - defined before implementation
  - aligned with business intent
  - structured for traceability

---

### 5. Risk + Confidence Model

- How risk tiers are defined (T0–T3)
- How confidence is assigned to:
  - requirements
  - assumptions
  - flows
- How this influences validation strategy

---

### 6. Validation Strategy (Dual Lane)

Define:

#### Automation (Deterministic Validation)
- What should be automated and why
- What qualifies as stable and repeatable

#### Manual + AI (Uncertainty Resolution)
- What requires human judgment
- How AI assists exploratory validation

---

### 7. Execution Model

- How validation is executed:
  - continuously (automation)
  - iteratively (exploratory)

- How evidence is collected

---

### 8. Evidence Model

Define what counts as:

- Strong evidence (deterministic results, logs, data validation)
- Medium evidence (UI validation, integrations)
- Weak evidence (AI assumptions)

---

### 9. QA Decision Framework

- How QA evaluates:
  - risk coverage
  - evidence quality
  - open defects

- How release readiness is determined

---

### 10. Defect Governance

- How AI contributes to defect creation
- How QA validates and controls defects
- How traceability is maintained

---

## Constraints

Do NOT:
- jump directly into test cases
- assume specific tools or frameworks
- describe UI-level details
- treat QA as a final step

---

## Goal

Produce a QA operating model that ensures:

> The system is built correctly from the start,
> validated continuously,
> and governed through risk, confidence, and evidence.

This should reflect **Greenfield QA as a quality-first development system**, not a testing phase.
```

### 03 — Brownfield QA Strategy

```markdown
# Brownfield QA Strategy

## When to Use

Use this prompt when defining how to **establish and govern quality in an existing system (Brownfield)** where an MVP or codebase already exists, requirements may be missing or inconsistent, behavior must be understood and reconstructed, or AI may have generated part of the system.

This is NOT about writing test cases — this is about defining a **quality recovery and control system**.

---

## Prompt

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

You are acting as an AI-native QA Architect operating within the **HatchWorks QA methodology**.

Given an existing system, feature, or MVP, define how to **recover context, reconstruct understanding, and establish quality governance** using the Brownfield QA workflow.

---

## Brownfield QA Flow (Reference Model)

Use this structure as the foundation:

1. MVP exists
2. Recover and structure context
3. Build scope and QA structure
4. Create test baseline
5. Risk + Confidence classification
6. Dual validation paths
7. Execution
8. Evidence + AI triage
9. QA decision
10. Confirmed defects

---

## Output Requirements

Produce a structured QA strategy that explains:

---

### 1. Context Recovery Strategy

- How to infer architecture from the existing codebase and system behavior
- How to reconstruct workflows by analyzing code paths, data flows, and integration points
- How to identify dependencies across modules, services, and external systems
- How to detect implicit business logic that is not captured in documentation

- What signals to use for context recovery:
  - codebase structure and patterns
  - commit history and evolution
  - observable system behavior
  - integration contracts and data flows

---

### 2. Understanding Reconstruction

- How QA identifies:
  - inferred requirements
  - missing requirements
  - conflicting logic

- How assumptions are documented with **confidence levels**

---

### 3. Scope and QA Structure

- How recovered understanding becomes:
  - stories
  - acceptance criteria
  - QA structure

- How traceability is rebuilt from incomplete inputs

---

### 4. Test Baseline Strategy

- How test cases are:
  - generated from inferred behavior
  - structured for traceability
  - annotated with confidence levels

---

### 5. Risk + Confidence Model

- How risk tiers are defined (T0–T3)
- How confidence is assigned to:
  - inferred requirements
  - system behavior
  - test scenarios

- How this model drives validation priorities

---

### 6. Validation Strategy (Dual Lane)

Define:

#### Automation (Deterministic Validation)
- What can be safely automated
- What is stable enough to be repeatable
- Regression coverage strategy

#### Manual + AI (Uncertainty Resolution)
- What requires exploration
- What is ambiguous or low-confidence
- How AI assists investigation and validation

---

### 7. Execution Model

- How testing is executed:
  - automated (repeatable validation)
  - exploratory (behavior discovery)

- How findings are captured with context

---

### 8. Evidence Model

Define levels of evidence:

- Strong → deterministic results, logs, data validation
- Medium → UI behavior, integration responses
- Weak → inferred or AI-generated assumptions

Explain how evidence quality impacts decisions

---

### 9. QA Decision Framework

- How QA evaluates:
  - risk coverage
  - evidence strength
  - confidence levels
  - defect impact

- How release readiness is determined in uncertain environments

---

### 10. Defect Governance

- How AI contributes to:
  - clustering findings
  - drafting defects

- How QA:
  - validates accuracy
  - assigns severity
  - ensures reproducibility

---

## Special Behavior: Story Update Re-entry

When a preexisting story is updated:

- Re-enter at **Step 2: Recover and structure context**

Explain:

- Why context must be revalidated
- How scope, tests, and validation may change
- How the system reuses the same workflow instead of creating a new one

---

## Constraints

Do NOT:
- assume clean or complete requirements
- rely on documentation as source of truth
- jump directly into test execution
- treat QA as a final step

---

## Goal

Produce a QA operating model that ensures:

> An existing system can be understood, validated, and governed,
> even under uncertainty and incomplete information.

This should reflect **Brownfield QA as a reverse-engineered quality system**, not a traditional testing phase.

---

## Recommended Next Steps

After establishing the brownfield QA strategy:

1. **Identify test coverage gaps** — use `engine/prompts/15-test-gap-analysis.md` to map what tests exist vs. what should exist, prioritized by risk tier
2. **QA planning** — use `engine/prompts/14-qa-planning.md` to define test data, environments, and automation scope
3. **Generate scenarios** — use `engine/prompts/05-scenarios.md` to create risk-prioritized test scenarios from recovered context
```

### 04 — Story Update Loop

```markdown
# Story Update Loop

## When to Use

Use this when a story or feature has changed and QA coverage needs to be refreshed. This aligns with the story update loop defined in `.agent/rules/workflows.md` (re-enter at Step 2).

## Prompt

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

A story or feature has changed. Help me update QA coverage.

Please produce:
1. Updated intent summary
2. What changed (delta between original and updated)
3. What existing scenarios are still valid
4. What scenarios must be updated
5. New risks introduced by the change
6. Automation updates needed
7. Manual validation updates needed
8. Evidence needed for revalidation
9. Any defects likely to be impacted (closed, updated, or new)

Original context:
[PASTE ORIGINAL STORY OR FEATURE]

Updated context:
[PASTE NEW STORY OR CHANGES]

Keep the output simple and focused on what needs to change. Use confidence labels for any inferred items.
```

### 05 — Test Scenario Generation

```markdown
# Test Scenario Generation

## When to Use

Use this prompt when you need to generate **general, tool-agnostic test scenarios** based on a feature, workflow, or system description. Focus on behavior, risk, and validation intent — not execution or implementation details.

---

## Prompt

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

You are acting as an AI-native QA Architect working within a GenDD-aligned workflow.

Generate **general, tool-agnostic test scenarios** for the provided input. Do NOT assume any specific programming language, framework, tool (e.g., Selenium, Playwright), or implementation details.

---

## Input

Provide:
- Feature description
- User flow or system behavior
- (Optional) business rules or constraints

---

## Output Requirements

Generate a structured list of **test scenarios** using the following format:

### For each scenario include:

- **Scenario Title**
- **Description**
- **Preconditions**
- **Test Steps (high-level)**
- **Expected Result**
- **Risk Level** (T0 / T1 / T2 / T3)
- **Confidence Level** (High / Medium / Low)
- **Suggested Validation Type**
  - Deterministic (automation candidate)
  - Exploratory (manual + AI-assisted)

---

## Behavior-Focused Scenario Design

### Behavior-Driven (Not Implementation-Driven)
Focus on:
- What the system should do
- What could go wrong
- Edge cases and failure modes

Avoid:
- UI selectors
- API endpoints
- code-level instructions

---

## Scenario Coverage Expectations

Ensure scenarios cover:

- **Happy path (core flow)**
- **Negative cases (invalid inputs, failures)**
- **Edge cases (boundary conditions)**
- **State transitions**
- **Data validation**
- **Error handling**
- **Permissions / access control (if applicable)**

---

## Output Style

- Clear, concise, and structured
- No redundancy
- No tool-specific instructions
- Professional, QA-architect level

---

## Goal

Produce a set of scenarios that:

> Can be used across any technology,
> support both greenfield and brownfield QA workflows,
> and enable risk-based, evidence-driven validation.
```

### 06 — Scenario to Test Case Conversion

```markdown
# Scenario to Test Case Conversion

## When to Use
Use this prompt when you already have a **list of scenarios** and need to convert them into **structured, executable test cases**.

This step transforms:
→ understanding (scenarios)
into
→ execution-ready validation (test cases)

---

## Instructions

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

---

## Input

Convert the following scenarios into structured test cases:

[PASTE SCENARIOS HERE]

---

## Output Format

For each scenario, generate a test case using the following structure:

---

### Test Case ID
Unique identifier (e.g., TC-LOGIN-001)

---

### Title
Short, clear description of what is being validated

---

### Linked Scenario
Reference the original scenario

---

### Purpose
Why this test exists (what risk or behavior it validates)

---

### Priority
- High (critical path, security, data integrity)
- Medium (important but not blocking)
- Low (cosmetic or minor behavior)

---

### Preconditions
What must be true before executing the test:
- system state
- user role
- data setup
- environment conditions

---

### Steps
Step-by-step instructions:
1. Action
2. Action
3. Action

Keep steps:
- clear
- minimal
- reproducible

---

### Expected Result
What should happen if the system behaves correctly

---

### Negative / Failure Conditions (if applicable)
- invalid inputs
- error handling
- boundary conditions

---

### Test Type
- Functional
- Integration
- API
- UI
- Data
- Security (if relevant)

---

### Automation Candidate
- Yes → stable, repeatable, deterministic
- No → exploratory, unstable, unclear
- Partial → some steps automatable

---

### Evidence Required
What should be captured during execution:
- logs
- API responses
- screenshots
- system outputs

---

### Confidence Level
- High → clearly defined behavior
- Medium → some assumptions
- Low → unclear or inferred logic

---

## Output Requirements

- One test case per scenario (or split if scenario is too broad)
- Maintain **clear traceability** to original scenarios
- Ensure all test cases are:
  - executable
  - unambiguous
  - reproducible

---

## Do Not

- Combine unrelated scenarios into one test case
- Leave expected results vague
- Skip preconditions
- Ignore risk priority
- Overcomplicate language

---

## Goal

Produce **high-quality, execution-ready test cases** that:

- align with GenDD structured outputs
- support both manual and automated execution
- improve QA speed and clarity
- enable consistent validation across teams
```

### 07 — Automation Decision

```markdown
# Automation Decision

## When to Use
Use this prompt after:
- scenarios are defined, OR
- test cases are created

This step determines:
→ what should be automated
→ what should remain manual or exploratory

---

## Instructions

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

---

## Input

Analyze the following scenarios or test cases:

[PASTE SCENARIOS OR TEST CASES HERE]

---

## Output Format

For each item, provide:

---

### Item Name
(Scenario or Test Case Title)

---

### Risk Level
- High (critical path, security, data integrity)
- Medium (important workflows, integrations)
- Low (cosmetic, low impact)

---

### Classification
- Automate Now
- Keep Manual
- Hybrid (partial automation)
- Needs Clarification

---

### Reasoning

Explain clearly based on:

- **Risk** → how critical is this?
- **Repeatability** → how often will this run?
- **Stability** → is behavior consistent?
- **Complexity** → how hard is it to automate?
- **Maintenance Cost** → will it break often?
- **Execution Cost** → is manual expensive?

---

### Automation Recommendation

If **Automate Now**:
- Suggested level:
  - API
  - Integration
  - UI
  - Data validation
- Key validations to automate

If **Hybrid**:
- Which parts to automate
- Which parts remain manual

If **Manual**:
- Why automation is not recommended
- What type of manual validation is required:
  - exploratory
  - visual
  - judgment-based

---

### Evidence Requirements

What evidence should be captured:
- logs
- API responses
- screenshots
- execution outputs

---

### Risks of Automation (if applicable)

- flakiness risk
- environment dependency
- unclear expected behavior
- data dependency issues

---

### Confidence Level

- High → clear decision based on stable behavior
- Medium → some uncertainty
- Low → insufficient information, needs clarification

---

## Output Expectations

- Be **practical and realistic**
- Avoid recommending automation for everything
- Focus on **high-value scenarios first**
- Keep explanations **short and actionable**

---

## Do Not

- Recommend UI automation for unstable features
- Ignore maintenance cost
- Over-automate low-value scenarios
- Skip reasoning
- Assume all scenarios are automation-ready

---

## Goal

Produce a **balanced automation strategy** that:

- maximizes value and efficiency
- minimizes maintenance and flakiness
- aligns with GenDD delivery speed
- supports both AI and human execution models
```

### 08 — Exploratory & Manual Testing

```markdown
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

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

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

- "What happens if…"
- "Try breaking the flow by…"
- "Simulate real-world misuse…"

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
```

### 09 — Defect Generation

```markdown
# Defect Generation

## When to Use
Use this prompt when:
- a failure is detected during testing (manual or automated)
- analyzing logs, outputs, or evidence
- converting findings into **structured, high-quality defects**

This step transforms:
→ observations and failures
into
→ **actionable, traceable bug reports**

---

## Instructions

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

---

## Input

Analyze the following failure, evidence, or test result:

[PASTE FAILURE DETAILS / LOGS / OUTPUT / NOTES HERE]

---

## Output Format

---

### Title
Short, clear summary of the issue

---

### Environment
- environment (dev, QA, staging, prod)
- relevant configuration (if known)

---

### Linked Context
- Feature / Story (if known)
- Scenario or Test Case (if available)

---

### Preconditions (if applicable)
State required setup:
- user role
- data setup
- system state

---

### Steps to Reproduce
Provide clear, minimal steps:

1. Step
2. Step
3. Step

Must be:
- reproducible
- sequential
- unambiguous

---

### Expected Result
What should happen based on:
- requirements
- intent
- system behavior

---

### Actual Result
What actually happened:
- error messages
- incorrect behavior
- unexpected output

---

### Evidence

Include or reference:
- logs
- API responses
- screenshots
- recordings
- system outputs

---

### Impact

Explain why this matters:

- Blocks critical workflow?
- Affects data integrity?
- Security concern?
- Degrades user experience?

---

### Severity (Suggested)

- Critical → blocks release, security/data risk
- High → major functionality broken
- Medium → important issue, workaround exists
- Low → minor or cosmetic

---

### Priority (Suggested)

Based on:
- business urgency
- release impact
- user exposure

---

### Risk Category

- Security
- Data Integrity
- Core Workflow
- Integration
- UI / UX
- Other

---

### Confidence Level

- High → clearly reproducible and validated
- Medium → likely valid but needs confirmation
- Low → unclear or inconsistent, needs review

---

### Reproducibility

- Always
- Intermittent
- Unable to reproduce consistently

---

### Suspected Cause (Optional)

If possible, suggest:
- probable root cause
- related system behavior
- impacted component

---

### Fix Validation Criteria (Recommended)

Define what must be true after fix:

- expected correct behavior
- validation conditions
- regression areas to check

---

### Human Review Required

- Yes → high-risk, low-confidence, unclear issue
- No → clear, reproducible, well-evidenced issue

---

## Output Expectations

- Clear and concise
- Fully reproducible
- Evidence-backed
- Actionable by developers
- Traceable to context

---

## Do Not

- Create vague or incomplete defects
- Skip reproduction steps
- Ignore evidence
- Over-report low-value issues
- Assume behavior without validation

---

## Goal

Produce **high-quality, developer-ready defects** that:

- reduce back-and-forth
- improve fix speed
- maintain QA signal quality
- align with GenDD traceability and governance
```

### 10 — Defect Triage

```markdown
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

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

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
```

### 11 — Evidence Analysis

```markdown
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

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

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
```

### 12 — Release Readiness

```markdown
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

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

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
- aligns with GenDD's AI-native, human-governed delivery model
```

### 13 — QA Output Review

```markdown
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

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

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
- supports GenDD's structured, AI-assisted delivery model
```

### 14 — QA Planning Strategy

```markdown
# QA Planning Strategy

## When to Use

Use this prompt **once per project or major feature area** — at Step 3a of the workflow — to make upfront QA infrastructure decisions before test suites are designed. This is an investment in future readiness, not a per-story activity.

Use it when:
- Starting a new project or major feature area
- Introducing a new tech stack, framework, or integration
- Working on Tier 0 or Tier 1 risk areas
- The project has no existing test infrastructure
- NFR-heavy features require specific performance, security, or compliance validation

Skip it (use the feature intake prompt only) when:
- Small bug fixes in well-understood domains
- Cosmetic or Tier 3 changes
- The project already has established test data, environments, and automation

## Prompt

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

Produce a QA Planning Strategy for this project or feature area.

This plan should make upfront decisions that are expensive to change later. It is a living document that evolves with the project.

### 1. Test Data Strategy

Define:
- What test data is needed (types, volumes, relationships)
- How test data is sourced or generated (factories, seeds, fixtures, synthetic generation)
- How PII and sensitive data is handled in test environments
- How data is cleaned or reset between test runs
- Whether shared or isolated test tenants are used
- Data dependencies between test suites

### 2. Environment Strategy

Define:
- Which environments exist and their purpose (local, CI, staging, pre-prod)
- How environments are provisioned and maintained
- Parity with production (what matches, what differs, and why)
- Access controls and credentials management for test environments
- Data refresh cadence (how often staging data is updated)
- Environment health monitoring approach

### 3. Automation Scope

Define:
- Which test layers to automate (unit, integration, API, E2E) and why
- Which framework and tooling to use (justify the choice for this stack)
- Who owns automation maintenance (by layer)
- Coverage targets by risk tier (Tier 0 targets vs. Tier 3)
- What should explicitly remain manual and why
- How AI-generated tests are reviewed before being committed

### 4. CI Pipeline Shape

Define:
- Which suites run at each stage:
  - PR: fast feedback (unit + fast integration)
  - Merge to main: confidence gate (full integration)
  - Nightly: deep validation (E2E + load + security scans)
- Parallelism and sharding approach
- Caching strategy for dependencies and build artifacts
- Artifact retention (test reports, coverage, traces, screenshots)
- Flaky test handling (quarantine, retry limits, alerting)

### 5. Proportionality Assessment

For each section above, note:
- What level of investment is justified by the risk tier and novelty
- What can be deferred to later sprints without creating technical debt
- What must be in place before the first test suite is designed

Project/feature context:
[PASTE PROJECT DESCRIPTION, TECH STACK, RISK AREAS, AND ANY EXISTING INFRASTRUCTURE HERE]

Keep the plan practical, specific to this project, and actionable. Avoid generic advice — every decision should reference the actual stack, risk profile, and team context.
```

### 15 — Test Gap Analysis

```markdown
# Test Gap Analysis

## When to Use

Use this prompt to systematically identify what tests **should exist** versus what **does exist**, producing coverage maps and actionable recommendations across unit, integration, and end-to-end testing.

Use it when:
- Sprint planning requires visibility into test work needed
- Before major releases to validate coverage
- After production incidents to prevent recurrence
- When onboarding new QA resources to an existing codebase
- During code reviews to identify untested changes
- Leadership asks "are we confident in our testing?"
- After running `engine/prompts/03-brownfield.md` to prioritize test coverage for recovered risk hotspots

Skip it when:
- The system has no existing code or tests yet (use greenfield strategy instead)
- The scope is a single story change (use `engine/prompts/04-story-update.md`)

---

## Instructions

> **Prerequisite:** `.agent/rules/core-principles.md` must be loaded before using this prompt.

---

## Prompt

You are acting as an AI-native QA Architect working within the HatchWorks QA methodology.

Analyze the provided codebase and produce a **test gap analysis** — a structured comparison of what tests should exist versus what currently exists, prioritized by risk tier and annotated with confidence levels.

---

## Input

Provide:
- Codebase access (repository)
- (Optional) Known critical flows or integrations
- (Optional) Recent production incidents or known problem areas
- (Optional) Compliance requirements (PCI, GDPR, HIPAA)

[PASTE CODEBASE CONTEXT, CRITICAL FLOWS, OR KNOWN RISK AREAS HERE]

---

## Output Format

### Phase 1: Test Inventory

#### 1.1 Existing Test Files

Categorize all test files found in the codebase:

| Category | File Path | Test Count | What Is Tested | Notes |
|----------|-----------|------------|----------------|-------|
| Unit | | | | |
| Integration | | | | |
| E2E | | | | |
| Contract | | | | |
| Performance | | | | |

**Confidence:** High / Medium / Low (based on completeness of scan)

#### 1.2 Test Frameworks and Patterns

Identify:
- **Frameworks in use** (by test layer)
- **Patterns observed** (naming, AAA structure, mocking approach, data management)
- **CI/CD integration** (which pipeline stages run which tests)

---

### Phase 2: Required Coverage (What Should Be Tested)

#### 2.1 Critical Business Logic

For each identified area:

| Component | Location | Risk Tier | Risk If Untested | Current Coverage | Confidence |
|-----------|----------|-----------|------------------|------------------|------------|
| | | T0 / T1 / T2 / T3 | | Yes / No / Partial | High / Medium / Low |

Categories to evaluate:
- Payment/Financial logic
- Authentication/Authorization
- Data transformation and calculations
- Integration points (external APIs, webhooks)
- State machines and workflow transitions
- Validation rules and business constraints
- Email and notifications
- UI and frontend (when applicable)

#### 2.2 Key User Journeys

For each journey:

| Journey | Steps | Integrations Touched | Revenue Impact | E2E Test Exists? | Confidence |
|---------|-------|---------------------|----------------|------------------|------------|
| | | | High / Medium / Low | Yes / No | High / Medium / Low |

Prioritize by: revenue impact > user frequency > complexity.

#### 2.3 Integration Points

For each external integration:

| Integration | Type | Methods/Endpoints | Error Scenarios | Test Exists? | Sandbox Available? | Confidence |
|-------------|------|-------------------|-----------------|--------------|-------------------|------------|
| | | | | Yes / No / Partial | Yes / No | High / Medium / Low |

---

### Phase 3: Gap Matrix

Create a coverage gap matrix:

| Component/Feature | Risk Tier | Should Have | Currently Has | Gap | Priority |
|-------------------|-----------|-------------|---------------|-----|----------|
| | T0-T3 | Unit, Integration, E2E | | | High / Medium / Low |

Summary metrics:
- Total gaps by test type (Unit / Integration / E2E)
- Percentage coverage by risk tier
- Count of T0/T1 areas with no coverage

---

### Phase 4: Prioritized Recommendations

For the top gaps, format each as:

**Recommendation N: [Title]**

- **Gap:** What is missing
- **Risk Tier:** T0 / T1 / T2 / T3
- **Business Impact:** What could go wrong without this test
- **Confidence:** High / Medium / Low
- **Recommended Tests:**
  - Type (Unit / Integration / E2E)
  - What it validates
  - Estimated effort
- **Acceptance Criteria:**
  - Covers happy path
  - Covers error conditions
  - Follows existing test patterns
  - Integrated into CI/CD

Prioritize by:
1. T0/T1 areas with no coverage (highest priority)
2. Revenue/payment impact
3. Security/compliance impact
4. User experience impact

---

### Phase 5: Coverage Map

Produce a visual coverage summary:

**By Layer:**

| Layer | Estimated Coverage | Risk Level |
|-------|--------------------|------------|
| UI | | |
| API | | |
| Business Logic | | |
| Data Access | | |
| Integration | | |

**By Test Type:**

| Type | Count | Estimated Coverage |
|------|-------|--------------------|
| Unit | | |
| Integration | | |
| E2E | | |

**Risk Heat Map:**

| Risk Level | Components | Status |
|------------|-----------|--------|
| High (untested T0/T1) | | |
| Medium (partially tested) | | |
| Low (well tested) | | |

---

### Phase 6: Implementation Roadmap

Produce a phased plan:

| Sprint | Tests to Add | Type | Effort | Risk Tier | Status |
|--------|-------------|------|--------|-----------|--------|
| | | | | | Planned |

Include:
- Success metrics (current vs. target coverage per tier)
- Regression checkpoints (smoke post-deploy, full regression pre-release)
- Flaky test quarantine plan

---

## Constraints

Do NOT:
- Chase 100% coverage as a vanity metric — focus on business-critical paths
- Ignore integration tests — unit tests alone do not catch integration failures
- Skip confidence annotations on inferred coverage assessments
- Assume manual-only tests do not exist — document what QA tests manually to avoid duplication
- Produce recommendations without risk tier and business impact

---

## Goal

Produce a **risk-prioritized test gap analysis** that:

> Makes test coverage visible and actionable,
> prioritizes gaps by business risk (T0-T3),
> annotates every inference with confidence,
> and provides a concrete remediation roadmap.
```

---

## 17. Connectors (Optional Tooling)

Condensed version: [Accurate-QA-Playbook.md §17](Accurate-QA-Playbook.md#17-connectors-optional-tooling) · Source: [`QA-GenDD/engine/connectors/`](QA-GenDD/engine/connectors/)

### `xray.md` (verbatim)

```markdown
# Xray Test Management Connector

> **Purpose:** Agent-consumable instructions for integrating AI-generated QA artifacts with Xray test management.
> **When to load:** The agent needs to create test cases in Xray format, push execution results, or maintain traceability between tests and stories.

---

## When to Use

Use this connector when:
- The project uses Xray for test management within an issue tracker
- Test cases need to be stored with formal traceability to stories/requirements
- Execution results need to be recorded for audit trails
- The team requires structured test plans with coverage reporting

Do NOT use for:
- Projects without an Xray instance
- Lightweight/informal QA (use markdown test cases instead)
- Exploratory testing (capture evidence directly, no Xray test plan needed)

---

## Concept Mapping

| HatchWorks QA Concept | Xray Equivalent |
|----------------------|-----------------|
| Test scenario | Test (issue type) |
| Test case (with steps) | Test with Steps |
| Test execution evidence | Test Execution + Test Run |
| Coverage split | Test Plan |
| Defect linked to test | Defect linked to Test Run |
| Risk tier (T0-T3) | Priority / Label on Test |
| Confidence label | Custom field or label |

---

## Creating Test Cases for Xray

When generating test cases, structure them so they can be imported into Xray:

### Required Fields

| Field | Maps to Xray | Notes |
|-------|-------------|-------|
| Title | Test summary | Clear, behavior-focused |
| Steps | Test Steps (action + expected result) | Numbered, specific |
| Preconditions | Precondition (linked or inline) | Data state, environment |
| Priority | Priority field | Map T0→Critical, T1→High, T2→Medium, T3→Low |
| Type | Test Type | Manual or Automated |
| Labels | Labels field | Add risk tier, automation candidate, confidence |

### Output Format for Import

​```markdown
**Summary:** Verify order submission creates exactly one charge
**Type:** Manual
**Priority:** Critical (T0)
**Labels:** payment, risk-t0, automation-candidate
**Precondition:** User logged in, items in cart, payment gateway in test mode

| # | Action | Expected Result |
|---|--------|-----------------|
| 1 | Navigate to checkout page | Checkout loads with order summary |
| 2 | Click "Place Order" | Loading indicator appears |
| 3 | Check payment gateway | Exactly one charge record created |
| 4 | Check order confirmation page | Confirmation with order ID displayed |
​```

---

## Recording Execution Results

After test execution (manual or automated), push results to Xray:

### Pass
- Mark Test Run as PASS
- Attach evidence: screenshots, logs, API responses
- Link to the Test Execution

### Fail
- Mark Test Run as FAIL
- Attach failure evidence
- Create linked defect using `engine/prompts/09-defects.md`
- Link defect to the Test Run and the original story

### Blocked
- Mark Test Run as BLOCKED
- Document the blocker (environment, dependency, data issue)
- Create blocker ticket if needed

---

## Maintaining Traceability

​```
Story/Requirement
    └── Test (in Xray)
        └── Test Execution
            ├── Test Run (PASS/FAIL/BLOCKED)
            │   └── Evidence (screenshots, logs)
            └── Defect (if FAIL)
                └── Linked back to Story
​```

### Checklist
- [ ] Every test is linked to a story or requirement
- [ ] Every test execution has a Test Execution container
- [ ] Every failure has a linked defect with evidence
- [ ] Risk tier is recorded as a label on each test
- [ ] Confidence labels are recorded for AI-generated tests

---

## Integration with QA Workflow

| Workflow Step | Xray Action |
|--------------|-------------|
| Step 4 (Create tests) | Create Tests in Xray, link to stories |
| Step 5 (Risk + Confidence) | Set priority and labels on Tests |
| Step 7 (Execution) | Create Test Execution, record Test Runs |
| Step 8 (Evidence + Triage) | Attach evidence to Test Runs, create defects |
| Step 10 (Confirmed defects) | Link defects to Test Runs and stories |
| Step 11 (Release readiness) | Use Xray coverage report as evidence |

---

## Anti-Patterns

| Avoid | Do Instead |
|-------|-----------|
| Create Xray tests without linking to stories | Always link to the requirement/story |
| Push AI-generated tests without review | Review and set confidence label first |
| Record PASS without evidence | Attach at least one screenshot or log excerpt |
| Create defects directly from low-confidence failures | Route to manual verification first |
| Skip the Test Execution container | Always group runs under an execution |
```

### `playwright-mcp.md` (verbatim)

```markdown
# Playwright MCP Connector

> **Purpose:** Agent-consumable instructions for using the Playwright MCP server to automate E2E testing within the HatchWorks QA workflow.
> **When to load:** The agent is asked to run, write, or verify E2E/UI tests using Playwright.

---

## When to Use

Use this connector when:
- Automating stable, repeatable UI flows (smoke, regression, critical paths)
- Validating UI behavior against acceptance criteria
- Capturing visual evidence (screenshots, page state) for the QA evidence trail
- The project has a Playwright MCP server configured

Do NOT use for:
- Unstable or rapidly changing UI (use manual/exploratory validation instead)
- First-time exploration of unknown features (use manual lane)
- API-only validation (use integration tests directly)

---

## How It Works

The Playwright MCP server exposes browser automation through tool calls. The agent uses these to navigate, interact, and verify web applications.

### Core MCP Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `browser_navigate` | Go to a URL | Start of each test flow |
| `browser_snapshot` | Get page structure (ARIA tree) | Before any interaction, to find element refs |
| `browser_click` | Click an element by ref | User interactions (buttons, links, menus) |
| `browser_fill` | Fill an input field | Form data entry |
| `browser_type` | Type text (append, trigger handlers) | Search fields, typing-sensitive inputs |
| `browser_take_screenshot` | Capture visual evidence | After key actions, for evidence trail |
| `browser_wait` | Wait for page changes | After navigation, form submission, loading |

### Execution Flow

​```
1. browser_navigate → target URL
2. browser_snapshot → understand page structure, get refs
3. For each test step:
   a. browser_click / browser_fill / browser_type → perform action
   b. browser_snapshot → verify page changed as expected
   c. browser_take_screenshot → capture evidence
4. Compare actual state against expected result
5. Report pass/fail with evidence
​```

---

## Connecting to the QA Workflow

### Before Running Tests
- Identify which scenarios to automate (T0/T1 stable flows only)
- Confirm preconditions: test data, environment, user credentials

### After Running Tests
- Capture a screenshot at each major state change
- If tests pass: use `engine/prompts/11-evidence.md` to assess evidence
- If tests fail: use `engine/prompts/09-defects.md` to draft a defect
- If ambiguous: route to manual verification — do NOT auto-create defects

---

## Example: Automating a Login Flow

​```text
Agent instruction:
"Use Playwright to verify the login flow: navigate to /login, enter valid credentials,
submit, and verify the dashboard loads. Capture evidence at each step."

Agent execution:
1. browser_navigate → https://app.example.com/login
2. browser_snapshot → find email input ref, password input ref, submit button ref
3. browser_fill → email input with "test@example.com"
4. browser_fill → password input with "Test123!"
5. browser_take_screenshot → "pre-submit state"
6. browser_click → submit button
7. browser_wait → 2 seconds for navigation
8. browser_snapshot → verify dashboard elements present
9. browser_take_screenshot → "post-login dashboard"
10. Compare: dashboard heading visible? User name displayed? → PASS/FAIL
​```

---

## AC Validation Workflow

Use this workflow to validate Gherkin acceptance criteria against a live application using Playwright MCP. This confirms whether ACs are testable before sprint planning or test automation begins.

### When to Use

- After generating ACs via `engine/prompts/01-feature-intake.md` to verify they are testable against the real UI
- Before sprint planning to validate story feasibility
- When QA questions the testability of requirements
- When developers report AC-to-UI mismatches

### Prerequisites

- Application is running at an accessible URL (staging or local)
- Acceptance criteria are written in Gherkin format (GIVEN-WHEN-THEN)
- Test credentials are available if the feature requires authentication

### Validation Steps

​```
1. Collect Gherkin ACs, application URL, test credentials, feature area name
2. browser_navigate → relevant pages referenced in the ACs
3. browser_take_screenshot → capture baseline state of each page
4. For each WHEN clause:
   a. browser_snapshot → find the referenced element
   b. Verify: Does the element exist? What is its selector (prefer data-testid)?
   c. Verify: Is it visible/enabled in the expected precondition state?
5. For each THEN clause:
   a. browser_snapshot → check if the expected outcome is assertable
   b. Verify: What selector shows success/failure?
   c. Verify: Are error messages accessible?
6. Produce AC Validation Report (see template below)
​```

### AC Validation Report Template

​```markdown
# AC Validation Report

## AC-1: [Scenario Name]
**Status**: Fully Testable / Partially Testable / Not Testable

**GIVEN**: [precondition]
- Verification: [how to set up state]

**WHEN**: [action]
- Element exists: yes/no
- Selector: [data-testid="..."]

**THEN**: [expected outcome]
- Assertable: yes/no
- Assertion selector: [data-testid="..."]

**Issues Found**: [list]
**Recommendations**: [list]
​```

### Bulk AC Validation

For validating multiple ACs at once, produce a summary table:

| AC | Status | Missing Selectors | Action Required |
|----|--------|-------------------|-----------------|
| AC-1 | Fully Testable | None | None |
| AC-2 | Partially Testable | data-testid on submit button | Developer action needed |
| AC-3 | Not Testable | Feature not yet built | Blocked |

### After Validation

- If **Fully Testable**: proceed to test case generation (`engine/prompts/06-testcases.md`)
- If **Partially Testable**: create action items for missing `data-testid` attributes, test data requirements, or API mocks
- If **Not Testable**: route back to feature intake for AC refinement or flag as blocked

---

## Anti-Patterns

| Avoid | Do Instead |
|-------|-----------|
| Automate unstable/changing UI | Flag for manual testing |
| Skip snapshots before clicking | Always snapshot first to get fresh refs |
| Use fixed waits (`sleep(5000)`) | Use `browser_wait` + snapshot verification |
| Ignore console errors | Check and report them as part of evidence |
| Create defects from flaky failures | Route to manual verification first |
| Validate ACs without live application | Always validate against a running instance |
| Skip element verification before writing E2E tests | Always confirm selectors exist first |
```

### `testrail.md` (verbatim) — Source: [`engine/connectors/testrail.md`](engine/connectors/testrail.md)

> # TestRail Connector
>
> **Purpose:** Agent-consumable instructions for reading Accurate's existing test
> suite and pushing AI-generated cases and results to TestRail.
> **When to load:** The agent needs suite context before writing cases, or has
> reviewed cases ready to push.
> **Backed by:** the first-party MCP bridge in `engine/mcp/testrail/`. Setup and
> security posture: [`engine/mcp/testrail/README.md`](engine/mcp/testrail/README.md).
>
> ## When to Use
>
> Use this connector when:
>
> - The project's `Context.md` §1 names TestRail as the test-case-management tool
> - The agent needs to know how the **existing** suite is written before generating new cases (this is the common case, and it is a read-only need)
> - Reviewed cases need to land in TestRail
> - Execution results need recording against a run
>
> Do NOT use for:
>
> - Projects on Xray or Zephyr — see `xray.md`
> - Pushing cases that have not been human-reviewed
> - Lightweight/informal QA where markdown cases are the deliverable
> - Exploratory testing (capture evidence directly; no TestRail run needed)
>
> **If the bridge is not configured, say so and export to a file instead.** Do not describe a file export as though it were a push. `Context.md` §1 is the source of truth for whether a push path exists.
>
> ## Hard rules
>
> 1. **Call `testrail_describe_schema` before generating or pushing any case.** Priorities, case types, result statuses, templates and custom fields are all per-instance configuration. `priority_id: 4` is not "Critical" everywhere, and `status_id: 1` is not universally "Passed". Never send a value you did not read from the schema.
> 2. **Never invent a custom field name.** `custom_fields` keys must exist on the instance. If our concept has nowhere to live, fold it into a text field and say so — do not silently drop it.
> 3. **Search before you write.** Run `testrail_search_cases` on the ticket key. Duplicated coverage is worse than no coverage: it splits maintenance and makes the suite untrustworthy.
> 4. **A refusal is final.** `REFUSED BY POLICY` means the write targeted a project outside the allowlist. Do not retry, do not look for another route, do not pick a different section to get around it. Report it and stop.
> 5. **Never report a dry run as a completed push.** If the response contains `"dry_run": true`, nothing reached TestRail.
> 6. **`WRITE OUTCOME UNKNOWN` means verify, not retry.** The write may have landed. Read the state back before re-sending anything.
> 7. **Every case gets a `refs` value.** Traceability to the ticket is the point.
>
> ## Concept Mapping
>
> | QA-GenDD concept | TestRail equivalent | Notes |
> |---|---|---|
> | Test case | Case in a section | |
> | Case title | `title` | Behaviour-focused |
> | Steps (action + expected) | `custom_steps_separated` | The `steps` argument converts for you — pass `{action, expected}` |
> | Preconditions | `custom_preconds` | Via the `preconditions` argument |
> | Ticket / story | `refs` | e.g. `ACC-9279` |
> | Risk tier (T0–T3) | `priority_id` | **Map via the schema.** Do not assume an ordering |
> | Test type | `type_id` | From the schema |
> | Coverage split | Test run | `testrail_add_run` |
> | Execution evidence | Result `comment` | Attach logs, observations, links |
> | Defect | Result `defects` | Ticket key(s) |
> | Confidence label, coverage tier, objective | Usually no native field | Check the schema for a custom field; otherwise fold into a text field |
> | Feature ID (`Context.md` §2) | Section, or a custom field | Confirm which convention the suite already uses |
>
> `priority_id`, `type_id` and `status_id` are **always** resolved from `testrail_describe_schema`. There is no default mapping in this document on purpose — writing one down would invite exactly the guessing that produces malformed imports.
>
> ## Reading the suite
>
> ```
> testrail_probe                  # posture, and which projects are writable
> testrail_list_projects
> testrail_list_suites            # note the suite mode
> testrail_list_sections          # find where cases belong
> testrail_list_cases             # narrow by section or title
> testrail_get_case               # read 2-3 in full to learn house style
> testrail_describe_schema        # the field map
> ```
>
> **Read a handful of real cases in full before writing any.** In a **multiple-suite** project, `suite_id` is required on section and case reads — the tools refuse rather than quietly return suite #1. Keep reads narrow; `testrail_list_cases` on a large project will fill the context window with case titles and leave no room for the work.
>
> ## Pushing cases
>
> **Preconditions for a push:** cases human-reviewed · `testrail_describe_schema` called this session · required fields populated · `testrail_search_cases` shows no existing coverage · target `section_id` confirmed, not guessed · every case has `refs`.
>
> Use `testrail_add_cases` for a set (up to 100 per call, `stop_on_error: false`). It validates every payload and checks the allowlist **before** the first write, so a batch cannot get halfway into the wrong project. On a partial failure it returns the ids that were created — those are authoritative; re-pushing the whole batch would duplicate them. **Every step needs an `expected`** — a step with no assertion cannot pass or fail.
>
> ## Recording execution results
>
> `testrail_add_run` (scope with `case_ids`, or the whole suite), then `testrail_add_result_for_case` — one call per case. `status_id` comes from `testrail_describe_schema.result_statuses` and is not portable across instances.
>
> ## Integration with the QA workflow
>
> | Workflow step | TestRail action |
> |---|---|
> | Step 1 (Feature intake) | `testrail_search_cases` — does coverage already exist? |
> | Step 2 (Brownfield delta) | `testrail_list_cases` / `testrail_get_case` — what does the suite already assert? |
> | Step 4 (Create tests) | Generate locally. Do not push yet |
> | Step 5 (Risk + confidence) | Map tiers to `priority_id` from the schema |
> | Step 5 Option D (Push) | `testrail_add_cases`, after human review |
> | Step 7 (Execution) | `testrail_add_run`, then `testrail_add_result_for_case` |
> | Step 8 (Evidence + triage) | Results with evidence comments; defects via prompt 09 |
> | Step 11 (Release readiness) | `testrail_list_runs` for pass/fail counts as evidence |
>
> ## Error reference
>
> | Response begins | Meaning | Action |
> |---|---|---|
> | `REFUSED BY POLICY` | Target project is not allowlisted | Stop. Report it. Do not reroute |
> | `WRITE OUTCOME UNKNOWN` | Ambiguous write failure, not retried | Read state back. Do not re-send |
> | `Invalid request` | Bad arguments or a nonexistent id | Fix the call |
> | `Authentication failed` | Credential, or API disabled | Stop. This is a setup problem |
> | `Rate limited` | Survived the retries | Wait, then narrow the query |
> | `TestRail unreachable` | Network or server error | May succeed on retry |
> | `unknown tool … running read-only` | Write tools not registered | Export to a file instead |

---

### TestRail MCP Bridge — Setup & Configuration

Source: [`engine/mcp/testrail/README.md`](engine/mcp/testrail/README.md), [`engine/mcp/testrail/QUICKSTART.md`](engine/mcp/testrail/QUICKSTART.md), [`engine/mcp/testrail/.env.example`](engine/mcp/testrail/.env.example)

The connector above is backed by a first-party, dependency-free MCP server (`engine/mcp/testrail/server.py`) rather than a third-party community package — a community server would run with a credential that inherits *all* of that user's TestRail permissions, which is more risk than writing the ~1,400-line bridge. It talks hand-rolled JSON-RPC 2.0 over stdio, Python 3.10+ standard library only, and defaults to **read-only**.

#### Quickstart (five steps)

1. **Enable the TestRail API instance-wide** — an admin does this once: **Administration → Site Settings → API → Enable API**. If it's off, every request fails with `401` regardless of credential quality.
2. **Mint an API key** — **My Settings → API Keys → Add Key**, in TestRail. Shown once; copy it immediately. The key inherits *your* permissions and every write is attributed to you — for CI or shared use, ask an admin for a service account instead of sharing a personal key.
3. **Configure the bridge:**

   ```bash
   cd engine/mcp/testrail
   cp .env.example .env
   ```

   Fill in the three required lines:

   ```ini
   TESTRAIL_URL=https://accurate.testrail.io
   TESTRAIL_USER=you@accurate.com
   TESTRAIL_API_KEY=paste-your-key-here
   ```

   Confirm the file is actually gitignored before saving a real key:

   ```bash
   git check-ignore -v engine/mcp/testrail/.env    # must print a match
   ```

   Leave everything else as-is — that keeps the bridge in read-only mode, the correct starting posture.
4. **Verify the connection before wiring anything up:**

   ```bash
   python3 server.py --probe        # auth check + visible projects + posture
   python3 server.py --list-tools   # what the agent will actually see
   python3 test_bridge.py           # offline suite, no credentials needed
   ```

   `--probe` distinguishes a disabled API from a bad key from a VPN problem in its error message — debug this here, not through an MCP client's log pane.
5. **Register with the MCP client.** At the repo root, `.mcp.json`:

   ```json
   {
     "mcpServers": {
       "testrail": {
         "command": "python3",
         "args": ["engine/mcp/testrail/server.py"]
       }
     }
   }
   ```

   Cursor uses the same shape in `.cursor/mcp.json`. **On Windows, use `python` instead of `python3`** — the repo's own `.mcp.json` template flags this explicitly and it is the single most common setup mistake (see `test-gap-analyzer`'s Step 1a). No credentials go in this file; the server reads `.env` from its own directory. Restart the MCP client after any change — the tool list is built at startup, so there is no hot reload.

Once registered, the agent can read projects, suites, sections, cases, and results. Writing is a separate, deliberately higher-friction opt-in (below).

#### Enabling writes

Writes stay off until three things are all true — more friction than a single flag, on purpose, because TestRail has no undo and a bad bulk push is expensive to unwind by hand:

```ini
TESTRAIL_MODE=write
TESTRAIL_ALLOWED_PROJECTS=12        # explicit ids, no wildcard
TESTRAIL_DRY_RUN=true               # keep this on for the first run
```

Restart the MCP client afterwards. Suggested sequence: (1) turn on write mode with dry-run against a **sandbox project**, run a real push, and read the echoed payloads — this is where field-mapping mistakes surface for free; (2) same project, `TESTRAIL_DRY_RUN=false`, and inspect what actually landed in the TestRail UI; (3) only then add the real project id to the allowlist.

The allowlist is enforced by *resolving* every write to its project (through the section/case/run, since TestRail's write endpoints don't take a project id directly) and checking that against `TESTRAIL_ALLOWED_PROJECTS` — an unresolvable target is refused, not allowed. Deletes need two independent controls: `TESTRAIL_ALLOW_DELETE=true` at startup **and** the exact string `DELETE PERMANENTLY` in the call's `confirm` argument.

#### Key environment variables (`.env`)

| Variable | Default | Purpose |
|---|---|---|
| `TESTRAIL_URL` | — (required) | Instance root only — no `/index.php`, no `/api/v2` |
| `TESTRAIL_USER` / `TESTRAIL_API_KEY` | — | Standard auth path; key minted per Step 2 above |
| `TESTRAIL_SESSION_COOKIE` | unset | Fallback for SSO-only instances with no mintable API key — see the README's "Session cookie mode" caveats (expires, invalidated by logout, undocumented interface) before relying on it |
| `TESTRAIL_MODE` | `read` | `read` or `write`; write tools are not registered at all in read mode |
| `TESTRAIL_ALLOWED_PROJECTS` | empty | Project ids writes may touch — no wildcard; empty means nothing is writable even in write mode |
| `TESTRAIL_ALLOW_DELETE` | `false` | Registers the delete tool at all (still needs the per-call confirm phrase) |
| `TESTRAIL_DRY_RUN` | `true` | Validates and echoes writes without sending them |
| `TESTRAIL_TIMEOUT` / `TESTRAIL_MAX_RETRIES` / `TESTRAIL_PAGE_SIZE` / `TESTRAIL_MAX_RESPONSE_CHARS` | 30 / 4 / 250 / 60000 | Tuning; defaults are fine for most projects |

#### Troubleshooting

| Symptom | Likely cause |
|---|---|
| `401` on everything | API not enabled instance-wide, or `TESTRAIL_USER` is not the login email |
| `non-JSON body` | An SSO/login interstitial — request wasn't authenticated as an API call, or (cookie mode) the cookie expired |
| `TESTRAIL_URL must be an absolute http(s) URL` (no value shown) | `TESTRAIL_URL` and `TESTRAIL_API_KEY` are likely swapped — the value is withheld on purpose so a misplaced key isn't printed |
| `should be the instance root, not an API URL` | The URL includes `/api/v2` — use just `https://host` |
| `REFUSED BY POLICY … not in TESTRAIL_ALLOWED_PROJECTS` | Working as intended — add the id deliberately if that project really is the target |
| Write tools missing from the tool list | `TESTRAIL_MODE` is `read`, or the client wasn't restarted after the change |
| `suite_id is required` | Multiple-suite project — call `testrail_list_suites` first |
| `WRITE OUTCOME UNKNOWN` | A write failed ambiguously and was not retried — check TestRail before re-sending |
| Client shows no tools at all | Something printed to stdout and corrupted the stream — check the client's stderr log |

#### What the bridge does and does not protect against

It protects against wrong-project writes (allowlist enforced post-resolution), credential leaks into transcripts/logs (redaction at the point text leaves the process, including the Basic Auth blob), credential exfiltration via redirects (`urllib` refuses a cross-host redirect or an HTTPS→HTTP downgrade before following it), silent duplicate writes (an ambiguous POST failure is reported as unknown and not retried, rather than blindly resent), and accidental capability (write/delete tools simply aren't registered unless explicitly enabled).

It does **not** protect against the credential's own read permissions (the allowlist restricts writes only — scope the TestRail account itself if reads need restricting), a compromised developer machine (`.env` is plaintext on disk like any local credential file), or prompt injection via TestRail content (case titles/steps/comments are attacker-influenceable if anyone untrusted can edit the suite, and they flow into the agent's context — the allowlist bounds the *damage*, not the *deception*).

#### Maintenance

- Rotate the API key on the same cadence as any other credential, and immediately if a machine holding `.env` is compromised.
- Re-run `testrail_describe_schema` after any TestRail configuration change — a stale field map is the main way a push starts producing malformed cases.
- Re-run `python3 test_bridge.py` after touching anything in `engine/mcp/testrail/`, especially `guards.py`.
- Record the outcome (push path confirmed, allowlisted project ids, confirmed field mapping) in the project's `Context.md` §1 — until that section confirms a push path exists, `qa-test-case-writer` and `testrail-publisher` correctly keep offering file export only.

---

## 18. CI/CD Orchestrator (Headless Pipeline)

Condensed version: [Accurate-QA-Playbook.md §18](Accurate-QA-Playbook.md#18-cicd-orchestrator-headless-pipeline) · Source: [`QA-GenDD/engine/ci/README.md`](QA-GenDD/engine/ci/README.md)

```markdown
# QA-GenDD CI/CD Orchestrator

Platform-agnostic Python script that chains QA-GenDD prompts through an LLM API to automate the AI testing stream after test execution in any CI/CD pipeline.

## What it does

After your test suites run, the orchestrator:

1. **Parses** test artifacts (JUnit XML, coverage reports, failure logs)
2. **Stack profile (optional)** — when you pass `--stack {name}`, loads `knowledge/stacks/{name}.yml` and appends `stack_context` plus the **`guidance`** markdown file (same directory) into the LLM system prompt when `guidance:` is set in the YAML
3. **Evidence Review** — sends results through `engine/prompts/11-evidence.md` to assess what passed, failed, and is unclear
4. **Defect Triage** — sends failures through `engine/prompts/10-triage.md` to categorize and prioritize
5. **Defect Drafting** — sends actionable failures (high/medium confidence) through `engine/prompts/09-defects.md` to produce structured bug reports
6. **Release Readiness** — sends the full picture through `engine/prompts/12-release.md` for a release recommendation

## Outputs

| File | Contents |
|------|----------|
| `qa-summary.md` | Human-readable summary of all stages |
| `defects.json` | Structured defect drafts (JSON array) for downstream Jira/Xray import |
| `release-assessment.json` | Release status with test metrics and AI assessment |

**Exit code:** 0 = release recommended, 1 = not recommended or insufficient evidence. Use this as a CI gate.

## Setup

​```bash
pip install -r engine/ci/requirements.txt
​```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `QA_LLM_PROVIDER` | Yes | `anthropic` or `openai` |
| `ANTHROPIC_API_KEY` | When provider is anthropic | Anthropic API key |
| `OPENAI_API_KEY` | When provider is openai | OpenAI API key |
| `QA_MODEL` | No | Model override (defaults: `claude-sonnet-4-20250514` for Anthropic, `gpt-4o` for OpenAI) |

## Usage

​```bash
python engine/ci/qa-orchestrator.py \
  --stack python \
  --test-results ./test-output/junit.xml \
  --coverage ./test-output/coverage.xml \
  --logs ./test-output/failures.log \
  --output ./qa-output/
​```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `--test-results` | Yes | Path to test results file (JUnit XML or TRX) |
| `--coverage` | No | Path to coverage report |
| `--logs` | No | Path to failure logs |
| `--output` | No | Output directory (default: `./qa-output`) |
| `--stack` | No | Tech stack profile: `python`, `typescript`, `java`, `go`, `cpp`, `dotnet`. Loads `knowledge/stacks/{stack}.yml` for framework-aware analysis. |

### Stack profiles

When `--stack` is provided, the orchestrator loads a profile from `knowledge/stacks/` that:

1. **Injects stack context** into the LLM system prompt so defect reports, triage, and evidence analysis reference the correct framework (e.g., pytest fixtures for Python, Spring context for Java)
2. **Selects the right artifact parser** (JUnit XML for most stacks, TRX for .NET)
3. **Includes the stack's CI example** in the output summary

When `--stack` is omitted, the orchestrator works in generic mode (backward compatible).

### Per-stack CI examples

**Python:**
​```bash
pytest --junitxml=test-output/junit.xml --cov=src --cov-report=xml:test-output/coverage.xml
python engine/ci/qa-orchestrator.py --stack python --test-results test-output/junit.xml --coverage test-output/coverage.xml
​```

**TypeScript:**
​```bash
vitest run --reporter=junit --outputFile=test-output/junit.xml --coverage
python engine/ci/qa-orchestrator.py --stack typescript --test-results test-output/junit.xml
​```

**Java (Gradle):**
​```bash
./gradlew test jacocoTestReport
python engine/ci/qa-orchestrator.py --stack java --test-results build/test-results/test/ --coverage build/reports/jacoco/test/jacocoTestReport.xml
​```

**Go:**
​```bash
gotestsum --junitfile test-output/junit.xml -- -race -coverprofile=test-output/coverage.out ./...
python engine/ci/qa-orchestrator.py --stack go --test-results test-output/junit.xml --coverage test-output/coverage.out
​```

**C++:**
​```bash
ctest --test-dir build --output-junit test-output/junit.xml --output-on-failure
python engine/ci/qa-orchestrator.py --stack cpp --test-results test-output/junit.xml
​```

**.NET:**
​```bash
dotnet test --logger "trx;LogFileName=results.trx" --collect:"XPlat Code Coverage"
python engine/ci/qa-orchestrator.py --stack dotnet --test-results TestResults/results.trx --coverage TestResults/coverage.cobertura.xml
​```

## Example: GitHub Actions

​```yaml
jobs:
  test-and-qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: pytest --junitxml=test-output/junit.xml --cov --cov-report=xml:test-output/coverage.xml

      - name: Install QA orchestrator deps
        run: pip install -r engine/ci/requirements.txt

      - name: Run QA AI triage
        env:
          QA_LLM_PROVIDER: anthropic
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python engine/ci/qa-orchestrator.py \
            --test-results test-output/junit.xml \
            --coverage test-output/coverage.xml \
            --output qa-output/

      - name: Upload QA summary
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: qa-report
          path: qa-output/
​```

## Example: GitLab CI

​```yaml
qa-triage:
  stage: test
  script:
    - pytest --junitxml=test-output/junit.xml
    - pip install -r engine/ci/requirements.txt
    - python engine/ci/qa-orchestrator.py
        --test-results test-output/junit.xml
        --output qa-output/
  variables:
    QA_LLM_PROVIDER: openai
    OPENAI_API_KEY: $OPENAI_API_KEY
  artifacts:
    paths:
      - qa-output/
    when: always
​```

## Example: Generic (any CI)

​```bash
# After test execution:
export QA_LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-ant-...

pip install -r engine/ci/requirements.txt
python engine/ci/qa-orchestrator.py \
  --test-results ./junit.xml \
  --output ./qa-output/

# Exit code determines CI pass/fail:
echo "Exit code: $?"
​```

## Design principles

- **Reads prompts from the repo** — no hardcoded prompt text; updates to QA-GenDD prompts automatically flow to CI
- **AI drafts, humans decide** — outputs `defects.json` for human review or downstream import; does not auto-create Jira tickets
- **Confidence filtering** — only high/medium confidence findings become defect drafts; low-confidence items are flagged for human review
- **Does not require Cursor** — runs as a standalone Python script with LLM API access

## Related documents

- QA Workflows (`../../.agent/rules/workflows.md`) — Canonical step tables
- SDLC Triggers (`../../.agent/rules/sdlc-triggers.md`) — T5 (CI/CD phase) describes this orchestrator
- Manual QA Standards (`../../.agent/rules/manual-qa-standards.md`) — Defect governance and structure
- Release and Governance (`../../.agent/rules/release-and-governance.md`) — Release readiness rules
```

---

## 19. Templates Library

Condensed version: [Accurate-QA-Playbook.md §19](Accurate-QA-Playbook.md#19-templates-library) · Source: [`QA-GenDD/knowledge/templates/`](QA-GenDD/knowledge/templates/)

The **defect** and **release** templates are reproduced in full in §8 and §12 respectively. The **tech debt** template is reproduced in full (worked example generalized) in §9. The remaining two — **test case templates** and the customizable **testing-standards** starter — are reproduced below.

### `test-case-templates.md` (verbatim)

```markdown
# Test Case Templates

Standard formats for test cases and feature QA starters. Use these as the target output structure when generating QA artifacts.

---

## Standard Test Case Format

​```markdown
## TC-{ID}: {Clear behavior being verified}

**Priority:** P0 | P1 | P2 | P3
**Type:** Functional | UI | Integration | Regression | Security | Performance
**Risk Tier:** T0 | T1 | T2 | T3
**Automation Candidate:** Yes (unit/integration/E2E) | No (reason)

### Purpose
{Why this test exists — what risk or requirement it covers}

### Preconditions
- {Setup requirement}
- {Data state assumption}
- {Environment assumption}

### Steps
1. {Specific action}
   **Expected:** {Observable outcome}

2. {Specific action}
   **Expected:** {Observable outcome}

3. {Specific action}
   **Expected:** {Observable outcome}

### Evidence to Capture
- {What proof looks like for this test — logs, screenshots, API responses}

### Notes
- {Edge cases, known flakiness, related test cases}
​```

---

## Worked Example: Test Case

## TC-0045: Order submission idempotency under double-click

**Priority:** P0
**Type:** Functional
**Risk Tier:** T0 (payment/financial)
**Automation Candidate:** Yes (integration test)

### Purpose
Verify that double-clicking the order submit button does not create duplicate charges. Covers the idempotency requirement for the payment flow.

### Preconditions
- Test user logged in with items in cart
- Payment gateway in sandbox/test mode
- Starting state: zero pending charges for this user

### Steps
1. Navigate to checkout page
   **Expected:** Checkout page loads with order summary and submit button

2. Double-click the "Place Order" button within 500ms
   **Expected:** A single charge is created; second click is debounced or rejected

3. Check payment gateway dashboard
   **Expected:** Exactly one charge record exists for this order

4. Check server logs
   **Expected:** Second request either blocked or returns idempotent response

### Evidence to Capture
- Payment gateway dashboard screenshot showing charge count
- Server logs showing request handling
- API response codes for both requests

### Notes
- Also test: rapid triple-click, browser back + resubmit
- Related: TC-0046 (payment timeout handling)

---

## Feature QA Starter Format

​```markdown
# Feature QA: {Feature Name}

## Intent Summary
{1-2 sentences: what the feature does, who it's for, what success looks like}

## Risk List

| Risk | Tier | Notes |
|------|------|-------|
| {Risk description} | T0/T1/T2/T3 | {Context} |

## Scenario List

| Priority | Scenario | Type |
|----------|----------|------|
| High/Medium/Low | {Scenario description} | Automation / Manual |

## Coverage Split
- **Automate:** {list}
- **Manual:** {list}

## Evidence to Collect
- {What evidence is needed}

## Open Questions
- {Unknowns with confidence levels}

## Confidence
- Intent: High/Medium/Low — {basis}
- Risks: High/Medium/Low — {basis}
​```

---

## Worked Example: Feature QA Starter

# Feature QA: User Registration with Email Verification

## Intent Summary
Users can create an account by providing email, password, and name. After submission, they receive a verification email and must click the link to activate their account. Unverified accounts cannot access protected resources.

## Risk List

| Risk | Tier | Notes |
|------|------|-------|
| Verification link expiry bypass | T0 | Security — expired tokens must not grant access |
| SQL injection via registration fields | T0 | Security — all inputs must be sanitized |
| Password stored in plaintext | T0 | Security — must be hashed (bcrypt/argon2) |
| Duplicate email registration | T1 | Core workflow — must reject duplicates clearly |
| Email delivery failure | T2 | Integration with email provider; may silently fail |
| Registration under load | T2 | Performance — concurrent signups during launch |

## Scenario List

| Priority | Scenario | Type |
|----------|----------|------|
| High | Register with valid email and password | Automation |
| High | Reject duplicate email | Automation |
| High | Verification link activates account | Automation |
| High | Expired verification link is rejected | Automation |
| High | SQL injection in email/name/password fields | Automation |
| Medium | Password complexity enforcement | Automation |
| Medium | Email delivery within 30 seconds | Manual (timing) |
| Medium | Registration rate limiting | Automation |
| Low | UI validation messages clarity | Manual/exploratory |

## Coverage Split
- **Automate:** Happy path, duplicate rejection, link verification, link expiry, injection, password rules, rate limiting.
- **Manual:** Email delivery timing, UI message clarity, exploratory edge cases (special characters, long inputs).

## Evidence to Collect
- API response codes and bodies for each scenario
- Database state (user record, hashed password, verification token)
- Email delivery logs from provider
- Screenshots of error messages

## Open Questions
- What is the verification link expiry duration? (Assumed 24h — **medium confidence**)
- Is there a resend verification flow? (Not in current AC — needs product confirmation)

## Confidence
- Intent: **High** — clear from story AC
- Risk list: **High** — standard auth risks
- Email delivery SLA: **Medium** — assumed 30s, needs provider confirmation

---

## Test Type Reference

| Type | Focus | Example |
|------|-------|---------|
| Functional | Business logic | Login with valid credentials |
| UI/Visual | Appearance, layout | Button matches design spec |
| Integration | Component interaction | API returns data to frontend |
| Regression | Existing functionality | Previous features still work |
| Performance | Speed, load handling | Page loads under 3 seconds |
| Security | Vulnerabilities | SQL injection prevented |

## Priority Definitions

| Priority | Criteria | Must Run |
|----------|----------|----------|
| P0 | Business-critical, security, data integrity | Always |
| P1 | Major features, common flows | Every release |
| P2 | Minor features, edge cases | Periodic |
| P3 | Cosmetic, rare edge cases | When time permits |
```

### `testing-standards.md` (verbatim)

```markdown
# Testing Standards Template

> Use this template to create repository-specific testing standards files. Copy and customize the sections below for your project's frameworks, risk profile, and compliance requirements.
>
> This template complements the always-loaded rule at `.agent/rules/automation-qa-standards.md`. The rule defines the methodology; this template provides a customizable starting point for a target repository.

---

## Requirement Levels

| Level | Meaning | Enforcement |
|-------|---------|-------------|
| **MUST** | Mandatory, non-negotiable | CI/CD blocks on failure |
| **SHOULD** | Recommended best practice | PR review feedback |
| **MAY** | Optional enhancement | Team discretion |

---

## Foundational Standards

These principles apply to all repositories:

- **Test Naming:** Test names must communicate intent. Common patterns: `{Method}_{Scenario}_{ExpectedResult}`, descriptive strings, or fixture-based grouping -- choose what fits the repo's language and framework.
- **Test Structure:** Arrange-Act-Assert (AAA) pattern -- every test has setup, execution, and verification sections.
- **Test Independence:** No shared mutable state, no order dependency, isolated side effects, independent setup.
- **Required Scenarios:** Happy path, invalid input, not found (always). Authorization, authentication, external failure, multi-tenant isolation (when applicable). Domain-specific scenarios only when the code handles that domain.
- **Mocking Guidelines:** Mock at boundaries (external APIs, databases in unit tests, file system, time/randomness). Do NOT mock the code under test, simple value objects, pure functions, or internal implementation.
- **Coverage:** Priority-based (critical business logic > public APIs > data access > infrastructure). Set numeric targets per repository based on maturity and risk.

---

## Unit Testing

### Coverage Requirements (MUST)

| Area | Minimum | Rationale |
|------|---------|-----------|
| Payment/Financial code | 100% | Money-handling risk |
| Authentication/Authorization | 95% | Security risk |
| Business logic | 80% | Core functionality |
| Utilities/Helpers | 70% | Lower risk |

### Example (Python)

​```python
def test_process_payment_valid_token_returns_success():
    # Arrange
    mock_gateway = Mock(spec=PaymentGateway)
    mock_gateway.charge.return_value = ChargeResult(success=True)
    service = PaymentService(gateway=mock_gateway)

    # Act
    result = service.process_payment("tok_valid", 2000)

    # Assert
    assert result.success is True
    mock_gateway.charge.assert_called_once_with(amount=2000, token="tok_valid")
​```

### Example (TypeScript)

​```typescript
it('processPayment with valid token returns success', async () => {
    // Arrange
    const mockGateway = { charge: vi.fn().mockResolvedValue({ success: true }) };
    const service = new PaymentService(mockGateway);

    // Act
    const result = await service.processPayment('tok_valid', 2000);

    // Assert
    expect(result.success).toBe(true);
    expect(mockGateway.charge).toHaveBeenCalledWith({ amount: 2000, token: 'tok_valid' });
});
​```

### SHOULD (Recommended)

- Use test data builders for complex objects
- Group related tests in nested classes or describe blocks
- Include performance assertions for critical paths

---

## Integration Testing

### MUST (Enforced)

| Rule | Rationale |
|------|-----------|
| Start from clean database state | Prevents test pollution |
| No test order dependency | Tests run in any order |
| Clean up data after tests | Prevents accumulation |
| Use transactions where possible | Fast rollback |
| Isolate test tenants | Multi-tenant safety |

### Database Lifecycle Example (Python)

​```python
class TestPaymentIntegration:
    def setup_method(self):
        self.db = TestDatabase()
        self.db.reset()
        self.db.seed_test_data()

    def teardown_method(self):
        self.db.cleanup_test_data()
​```

### Database Lifecycle Example (TypeScript)

​```typescript
describe('PaymentIntegration', () => {
    let db: TestDatabase;

    beforeEach(async () => {
        db = new TestDatabase();
        await db.reset();
        await db.seedTestData();
    });

    afterEach(async () => {
        await db.cleanupTestData();
    });
});
​```

### External Service Testing

​```typescript
it('processPayment integration uses test mode', async () => {
    const config = {
        apiKey: process.env.STRIPE_TEST_KEY,
        isSandbox: true
    };

    const result = await paymentService.charge('tok_visa', 2000);

    await paymentService.void(result.transactionId);
});
​```

---

## E2E Testing

### Selector Rules (MUST)

| Do | Don't |
|----|-------|
| `[data-testid="submit-button"]` | `button:has-text("Submit")` |
| `[data-testid="email-input"]` | `.btn-primary`, `#submit` |
| Explicit data attributes | XPath, text selectors, CSS classes |

### Waiting Rules (MUST)

| Do | Don't |
|----|-------|
| `waitForSelector('[data-testid="..."]')` | `waitForTimeout(3000)` |
| `waitForResponse(...)` | `sleep(5000)` |
| `expect(...).toBeVisible()` | Arbitrary delays |

### Example

​```typescript
describe('Order Creation', () => {
    beforeEach(async () => {
        await resetTestData();
        await loginAsTestUser();
    });

    test('creates order successfully', async () => {
        await page.click('[data-testid="new-order-btn"]');
        await page.fill('[data-testid="amount-input"]', '100');
        await page.click('[data-testid="submit-btn"]');

        await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    });
});
​```

---

## Domain-Specific Test Scenarios

The following scenario checklists apply when your repository touches the relevant domain.

| Domain | Key Scenarios |
|--------|---------------|
| **Payment / Financial** | Card validation (Luhn, length, prefix), AVS, PIN masking, idempotency, anomaly detection |
| **Email / Notifications** | Delivery triggers, template data population, receipt accuracy, deduplication |
| **Security / Auth** | Account lockout, password policy, session expiry |
| **Regression / Sanity** | Health endpoint, critical-path smoke test, full regression suite |
| **UI / Accessibility** | Responsive breakpoints, WCAG 2.1 AA, keyboard navigation |

### Enforcement Levels

When customizing for your repository, assign MUST/SHOULD/MAY levels to each applicable scenario:

- **MUST** -- Payment input validation, email delivery triggers, account lockout, sanity/smoke tests
- **SHOULD** -- Anomaly detection, full regression suite, responsive design, accessibility (WCAG 2.1 AA)
- **MAY** -- Frequency anomaly flagging, usability/user-acceptance testing

---

## Test Data Management

### Test Cards Reference

| Card Number | Scenario |
|-------------|----------|
| 4111111111111111 | Success |
| 4000000000000002 | Declined |
| 4000000000000341 | Insufficient funds |

### Data Patterns

​```typescript
const testUser = TestDataFactory.createUser({
    role: 'admin',
    tenant: 'test-tenant-1'
});
​```

---

## CI/CD Integration

| Stage | Tests Run | Blocking |
|-------|-----------|----------|
| PR | Unit + Fast Integration | Yes |
| Merge to main | Full Integration | Yes |
| Nightly | E2E + Load | No (alerts) |

### Commands (adapt to your framework)

​```bash
# Unit tests (MUST pass for PR):
pytest tests/unit/                     # Python
npm test -- --filter unit              # JavaScript/TypeScript
go test ./... -run Unit                # Go

# Integration tests (MUST pass for merge):
pytest tests/integration/              # Python
npm test -- --filter integration       # JavaScript/TypeScript

# E2E tests (nightly):
npx playwright test                    # Playwright
npx cypress run                        # Cypress
​```

---

## Usage

1. Copy this template to your target repository's `testing.md`
2. Replace framework examples with your specific frameworks
3. Customize coverage requirements for your risk profile
4. Assign MUST/SHOULD/MAY to domain-specific scenarios
5. Review with QA team
6. Integrate into CI/CD pipeline
7. See `knowledge/stacks/` for language-specific tooling guidance

## Related

| Resource | Path | Purpose |
|----------|------|---------|
| Automation QA Standards (rule) | `.agent/rules/automation-qa-standards.md` | Always-loaded methodology standards |
| Test Case Templates | `knowledge/templates/test-case-templates.md` | Worked examples of test case format |
| Test Gap Analysis | `engine/prompts/15-test-gap-analysis.md` | Systematic gap identification workflow |
| Stack Profiles | `knowledge/stacks/` | Language-specific tooling and CI profiles |
```

---

## 20. Agent Skills (`.agent/skills/`)

Source: [`.agent/skills/`](.agent/skills/)

This is a layer not present in the original QA-GenDD architecture described in §1 —
it packages several of the engine's prompt-driven workflows (and some genuinely new
ones) as self-contained, auto-triggering Claude Code skills, each with its own
`SKILL.md` frontmatter description that the agent matches against a user request.
Where a skill supersedes or wraps an `engine/prompts/*.md` file, that's called out
below; where a skill is genuinely new capability (test-gap analysis, document
audit, automation-code generation), it has no engine/prompts equivalent.

| Skill | Triggers on | Does NOT do | Relationship to the engine |
|---|---|---|---|
| `qa-test-case-writer` | "generate test cases for TICKET-123," "is this story ready for QA," "are these ACs testable" | Writing automated test code, performance/load scripts, authoring the story itself | Packages `engine/prompts/06-testcases.md`'s job as a project-agnostic engine driven by a companion `Context.md` (feature taxonomy, brownfield reference, tooling, personas/fixtures) |
| `test-gap-analyzer` | "where are our test gaps," "audit our test coverage," "what should QA cover before this release" | Writing the tests themselves, generating manual cases from a story (→ `qa-test-case-writer`), authoring ACs | New capability — evidence-ranked (coverage data, git churn, bug-fix history, dependency fan-in) rather than intuition-ranked. Also flags tests that exist but cannot fail (no assertions, mock-only, snapshot-only, skipped/focused) — a category invisible to coverage tools |
| `test-automation-implementer` | "automate these test cases," "implement the automation assessment," "turn this into real tests" | Deciding what should be automated (→ `engine/prompts/07-automation.md`), generating the cases (→ `qa-test-case-writer`), finding gaps (→ `test-gap-analyzer`) | Takes `07-automation.md`'s "Automate Now" output plus its linked `06-testcases.md` cases from paper to real, executable test code in the actual target repo/module, using that codebase's real (not assumed) test stack and version |
| `testrail-publisher` | "upload/push/sync test cases to TestRail," "create a TestRail suite/section for these cases," "give me a CSV for manual import" | Generating the cases themselves (→ `06-testcases.md` / `qa-test-case-writer`), recording execution results (→ `engine/connectors/testrail.md`'s run/result tools) | The publishing step for a reviewed `06-testcases.md` output: push live via the TestRail MCP bridge (§17) when write access allows, and always emit a CSV fallback regardless of push outcome |
| `qa-doc-audit` | "audit the playbook," "review this QA doc," "is this still accurate," "find gaps in the standards we shipped" | Finding untested code (→ `test-gap-analyzer`), writing test cases (→ `qa-test-case-writer`), authoring the QA document itself | New capability — audits a delivered QA/testing document (this playbook included) against its source repo, the client's actual tracker state, and current external standards, producing a cited audit, a decidable CSV change log, and a prerequisites checklist |

### Common threads across all five

- **Human-in-the-loop is non-negotiable.** Every skill that can push, delete, or
  finalize something requires explicit confirmation first — `qa-test-case-writer`
  and `testrail-publisher` both refuse to push unreviewed cases; `test-gap-analyzer`
  and `test-automation-implementer` never write tests or file tickets without being
  asked.
- **Never invent what should be verified.** `test-automation-implementer` won't
  assume a mocking library's capability without checking its installed version;
  `qa-doc-audit` requires a citation (line number, file path, or ticket key) for
  every finding; `qa-test-case-writer` won't invent acceptance criteria or fixture
  data to unblock generation.
- **TestRail is read/verify-first, write-second, everywhere it appears.** All four
  skills that can touch TestRail (`qa-test-case-writer`, `test-gap-analyzer`,
  `testrail-publisher`, and indirectly `qa-doc-audit`'s client-context stream) call
  `testrail_describe_schema` before trusting any id, and treat a `dry_run` or
  `writes_possible: false` response as informational, never as a completed write.
  See §17's TestRail MCP Bridge subsection for the underlying setup these skills
  assume is either present or explicitly absent.
- **Confidence and assumption labeling is mandatory**, matching Core Principle 9
  (§2) — every skill above surfaces what it assumed rather than silently filling
  gaps, whether that's an unresolved brownfield delta, a blocked test case, or an
  unverifiable claim in a client-facing document.

---

*End of full-text edition. Return to the condensed [Accurate-QA-Playbook.md](Accurate-QA-Playbook.md) for day-to-day use.*

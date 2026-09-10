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

Follow the 11-step pipeline defined in [workflows.md](workflows.md). Your decision points within that pipeline:

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

Apply the release readiness checklist and outcomes defined in [release-and-governance.md](release-and-governance.md).

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
| Coding standards you enforce on developers | [developer-standards.md](developer-standards.md) |
| Risk tiering model you use for classification | [risk-and-confidence.md](risk-and-confidence.md) |
| Test design rules your team follows | [manual-qa-standards.md](manual-qa-standards.md) |
| Tech debt capture standard and required fields | [../../knowledge/templates/tech-debt-template.md](../../knowledge/templates/tech-debt-template.md) |
| Automation governance you oversee | [automation-qa-standards.md](automation-qa-standards.md) |
| Release rules you apply | [release-and-governance.md](release-and-governance.md) |
| Workflow steps you govern | [workflows.md](workflows.md) |
| Full prompt routing | [QA Planner](qa-planner.md) |

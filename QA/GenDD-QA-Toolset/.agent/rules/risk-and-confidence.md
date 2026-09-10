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

When QA engages after an MVP already exists, follow the brownfield workflow in [workflows.md](workflows.md): recover context, reconstruct requirements, build test coverage, and establish quality governance through the standard 11-step pipeline.

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

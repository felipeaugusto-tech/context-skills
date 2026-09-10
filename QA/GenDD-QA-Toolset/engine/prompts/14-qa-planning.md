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

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

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

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

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

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

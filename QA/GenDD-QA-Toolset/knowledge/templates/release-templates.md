# Release Readiness Assessment Templates

Standard format for release readiness assessments. Fields align with the Release Readiness and Governance standards.

---

## Standard Release Assessment Format

```markdown
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
```

---

## Worked Example

# Release Readiness: Order Management v2.5 (Sprint 12)

## Status: Release conditionally recommended

## Summary
Core order workflows are tested with strong evidence. Two medium-severity defects remain open with workarounds documented. Performance testing is complete. One Tier 2 integration (notification service) has limited coverage due to environment instability.

## Risk Coverage

| Area | Tier | Coverage | Evidence |
|------|------|----------|----------|
| Order creation and payment | T0 | Full — automated + exploratory | 47 tests passing, payment sandbox verified, idempotency confirmed |
| Authentication and authorization | T0 | Full — automated | 23 tests passing, role boundary tests green |
| Order listing and filtering | T1 | Full — automated | 18 tests passing, pagination edge cases covered |
| Email notifications | T2 | Partial — manual only | Staging env intermittent; 3 of 5 scenarios verified manually |
| Admin dashboard | T2 | Happy path only | 6 tests passing; no exploratory coverage yet |
| UI polish (tooltips, alignment) | T3 | Not tested | Deferred to next sprint |

## Requirement Confidence
- All T0/T1 requirements validated from story ACs — **High confidence**
- Notification trigger conditions inferred from code — **Medium confidence**

## Open Defects

| ID | Severity | Status | Impact |
|----|----------|--------|--------|
| BUG-201 | Medium | Open | Order total rounds incorrectly for 3+ decimal currencies (workaround: round on display) |
| BUG-198 | Medium | Open | Email template shows raw HTML when subject > 100 chars (workaround: truncate subject) |

No open Critical or High defects.

## Automated Results
- Unit: 142/142 passing
- Integration: 38/38 passing
- E2E: 22/24 passing (2 flaky — quarantined, not product bugs)
- Flaky rate: 8.3% (2/24) — within tolerance, both under investigation

## Manual Coverage
- Exploratory testing completed for order flow, payment flow, and auth
- Evidence captured: 14 screenshots, 8 API trace logs
- No new defects found in exploratory session

## Environment Confidence
- Staging: representative of production for order/payment/auth
- Notification service staging: unstable (intermittent 503s) — **Low confidence** for email coverage

## Stakeholder Validation
- Product owner reviewed order creation flow on staging — approved
- Finance team verified payment reconciliation report — approved

## Key Risks Going Forward
1. Email notification coverage is incomplete — monitor production delivery rates closely post-release
2. Two medium defects ship with workarounds — schedule fix for Sprint 13

## Required Next Steps
- [ ] Product owner sign-off on known risks (BUG-201, BUG-198)
- [ ] Ops team confirms production environment readiness
- [ ] Release notes updated with known issues section

## Human Review Items
- Final release recommendation requires QA lead approval
- The two open medium defects require product owner acknowledgment before shipping

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

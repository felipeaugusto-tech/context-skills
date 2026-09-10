# Defect Report Templates

Standard format for defect reports, whether drafted by AI or written by a human. Fields align with the Defect Governance standards.

---

## Standard Defect Format

```markdown
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
```

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

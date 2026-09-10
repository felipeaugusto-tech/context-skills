# Test Case Templates

Standard formats for test cases and feature QA starters. Use these as the target output structure when generating QA artifacts.

---

## Standard Test Case Format

```markdown
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
```

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

```markdown
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
```

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

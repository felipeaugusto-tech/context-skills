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

See [manual-qa-standards.md](manual-qa-standards.md) for the full testability assessment framework.

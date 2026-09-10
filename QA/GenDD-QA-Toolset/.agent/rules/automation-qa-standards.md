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

```python
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
```

### Example (TypeScript)

```typescript
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
```

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

```python
class TestPaymentIntegration:
    def setup_method(self):
        self.db = TestDatabase()
        self.db.reset()
        self.db.seed_test_data()

    def teardown_method(self):
        self.db.cleanup_test_data()
```

### Database Lifecycle Example (TypeScript)

```typescript
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
```

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

```typescript
const testUser = TestDataFactory.createUser({
    role: 'admin',
    tenant: 'test-tenant-1'
});
```

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

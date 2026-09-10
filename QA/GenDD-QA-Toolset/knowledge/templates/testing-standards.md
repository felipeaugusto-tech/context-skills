# Testing Standards Template

> Use this template to create repository-specific testing standards files. Copy and customize the sections below for your project's frameworks, risk profile, and compliance requirements.
>
> This template complements the always-loaded rule at `.cursor/rules/automation-qa-standards.md`. The rule defines the methodology; this template provides a customizable starting point for a target repository.

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

### External Service Testing

```typescript
it('processPayment integration uses test mode', async () => {
    const config = {
        apiKey: process.env.STRIPE_TEST_KEY,
        isSandbox: true
    };

    const result = await paymentService.charge('tok_visa', 2000);

    await paymentService.void(result.transactionId);
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

### Example

```typescript
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
```

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

### Commands (adapt to your framework)

```bash
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
```

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
| Automation QA Standards (rule) | `.cursor/rules/automation-qa-standards.md` | Always-loaded methodology standards |
| Test Case Templates | `knowledge/templates/test-case-templates.md` | Worked examples of test case format |
| Test Gap Analysis | `engine/prompts/15-test-gap-analysis.md` | Systematic gap identification workflow |
| Stack Profiles | `knowledge/stacks/` | Language-specific tooling and CI profiles |

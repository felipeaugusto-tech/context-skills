# Automation with Playwright MCP

This guide teaches you how to use the Playwright MCP server to automate E2E testing within the HatchWorks QA workflow.

---

## What Is the Playwright MCP?

The Playwright MCP (Model Context Protocol) server lets an AI assistant control a real browser — navigate pages, click buttons, fill forms, take screenshots, and verify behavior. It turns the AI into an automated tester.

---

## Prerequisites

1. **Playwright MCP server configured** in your IDE (Cursor, etc.)
2. **A running application** to test against (local dev server, staging, etc.)
3. **Test scenarios already defined** — know what you want to automate before you start

---

## When to Automate with Playwright

**Good candidates:**
- Login/logout flows
- Form submissions with validation
- Critical user journeys (checkout, registration, order management)
- Smoke tests after deployment
- Regression tests for stable features

**Bad candidates (keep manual):**
- Features actively being changed
- Highly visual comparisons (layout, design fidelity)
- First-time exploration of unknown features
- Flows requiring human judgment

---

## How to Use It

### 1. Define what to test

Start with your test scenarios (from `engine/prompts/05-scenarios.md`). Pick the ones flagged as automation candidates.

### 2. Instruct the agent

```text
Use Playwright to verify the login flow:
1. Navigate to the login page
2. Enter valid credentials (email: test@example.com, password: Test123!)
3. Submit the form
4. Verify the dashboard loads with the user's name displayed
Capture a screenshot at each step for evidence.
```

### 3. The agent executes

The agent uses the Playwright MCP tools:
- `browser_navigate` to go to the page
- `browser_snapshot` to understand the page structure
- `browser_fill` to enter data
- `browser_click` to submit
- `browser_take_screenshot` to capture evidence

### 4. Review the results

The agent reports pass/fail with evidence. Review:
- Did all steps execute correctly?
- Are the screenshots meaningful (not blank pages)?
- Do the assertions match your expected results?

---

## Connecting Results to the QA Workflow

After Playwright tests run:

**If tests pass:**
```text
Review this test evidence and confirm the login flow is validated:
[paste screenshots and agent output]
```

**If tests fail:**
```text
Triage this test failure — is it a product bug, test issue, or environment problem?
[paste failure evidence]
```

**If failure is confirmed:**
```text
Draft a structured defect report for this Playwright test failure:
[paste evidence]
```

---

## Validating Acceptance Criteria

Before writing full E2E tests, you can use Playwright to validate whether your Gherkin acceptance criteria are testable against the live application. This catches missing selectors, untestable assertions, and AC-to-UI mismatches early.

**Ask the AI:**
```text
Using Playwright, validate these acceptance criteria against [APP_URL]:

[PASTE GHERKIN ACS]

For each AC, check:
1. Do the referenced elements exist?
2. What selectors are available (prefer data-testid)?
3. Can each THEN clause be asserted programmatically?

Produce an AC Validation Report with status per AC (Fully Testable / Partially Testable / Not Testable).
```

See `engine/connectors/playwright-mcp.md` (AC Validation Workflow section) for the full procedure and report template.

---

## Tips

1. **Always snapshot before clicking** — the agent needs element refs from the current page state
2. **Use short waits + re-snapshot** instead of long fixed waits
3. **Capture screenshots at every key state** — they are your evidence trail
4. **Start with happy-path smoke tests** — get simple flows working before complex ones
5. **Review AI-generated assertions** — the agent may miss or misinterpret visual elements
6. **Quarantine flaky tests** — if a test fails intermittently, investigate before trusting it

---

## Example: Full Flow

```text
"Using Playwright, run a smoke test for the checkout flow:
1. Log in as test user
2. Add an item to the cart
3. Go to checkout
4. Fill in shipping details
5. Submit the order
6. Verify the confirmation page shows an order number
Take screenshots at each step. If any step fails, stop and report what happened."
```

The agent will execute each step, capture evidence, and report the result. You review and decide whether to proceed or file a defect.

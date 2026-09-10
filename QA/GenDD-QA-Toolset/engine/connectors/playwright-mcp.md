# Playwright MCP Connector

> **Purpose:** Agent-consumable instructions for using the Playwright MCP server to automate E2E testing within the HatchWorks QA workflow.
> **When to load:** The agent is asked to run, write, or verify E2E/UI tests using Playwright.

---

## When to Use

Use this connector when:
- Automating stable, repeatable UI flows (smoke, regression, critical paths)
- Validating UI behavior against acceptance criteria
- Capturing visual evidence (screenshots, page state) for the QA evidence trail
- The project has a Playwright MCP server configured

Do NOT use for:
- Unstable or rapidly changing UI (use manual/exploratory validation instead)
- First-time exploration of unknown features (use manual lane)
- API-only validation (use integration tests directly)

---

## How It Works

The Playwright MCP server exposes browser automation through tool calls. The agent uses these to navigate, interact, and verify web applications.

### Core MCP Tools

| Tool | Purpose | When to Use |
|------|---------|-------------|
| `browser_navigate` | Go to a URL | Start of each test flow |
| `browser_snapshot` | Get page structure (ARIA tree) | Before any interaction, to find element refs |
| `browser_click` | Click an element by ref | User interactions (buttons, links, menus) |
| `browser_fill` | Fill an input field | Form data entry |
| `browser_type` | Type text (append, trigger handlers) | Search fields, typing-sensitive inputs |
| `browser_take_screenshot` | Capture visual evidence | After key actions, for evidence trail |
| `browser_wait` | Wait for page changes | After navigation, form submission, loading |

### Execution Flow

```
1. browser_navigate → target URL
2. browser_snapshot → understand page structure, get refs
3. For each test step:
   a. browser_click / browser_fill / browser_type → perform action
   b. browser_snapshot → verify page changed as expected
   c. browser_take_screenshot → capture evidence
4. Compare actual state against expected result
5. Report pass/fail with evidence
```

---

## Connecting to the QA Workflow

### Before Running Tests
- Identify which scenarios to automate (T0/T1 stable flows only)
- Confirm preconditions: test data, environment, user credentials

### After Running Tests
- Capture a screenshot at each major state change
- If tests pass: use `engine/prompts/11-evidence.md` to assess evidence
- If tests fail: use `engine/prompts/09-defects.md` to draft a defect
- If ambiguous: route to manual verification — do NOT auto-create defects

---

## Example: Automating a Login Flow

```text
Agent instruction:
"Use Playwright to verify the login flow: navigate to /login, enter valid credentials,
submit, and verify the dashboard loads. Capture evidence at each step."

Agent execution:
1. browser_navigate → https://app.example.com/login
2. browser_snapshot → find email input ref, password input ref, submit button ref
3. browser_fill → email input with "test@example.com"
4. browser_fill → password input with "Test123!"
5. browser_take_screenshot → "pre-submit state"
6. browser_click → submit button
7. browser_wait → 2 seconds for navigation
8. browser_snapshot → verify dashboard elements present
9. browser_take_screenshot → "post-login dashboard"
10. Compare: dashboard heading visible? User name displayed? → PASS/FAIL
```

---

## AC Validation Workflow

Use this workflow to validate Gherkin acceptance criteria against a live application using Playwright MCP. This confirms whether ACs are testable before sprint planning or test automation begins.

### When to Use

- After generating ACs via `engine/prompts/01-feature-intake.md` to verify they are testable against the real UI
- Before sprint planning to validate story feasibility
- When QA questions the testability of requirements
- When developers report AC-to-UI mismatches

### Prerequisites

- Application is running at an accessible URL (staging or local)
- Acceptance criteria are written in Gherkin format (GIVEN-WHEN-THEN)
- Test credentials are available if the feature requires authentication

### Validation Steps

```
1. Collect Gherkin ACs, application URL, test credentials, feature area name
2. browser_navigate → relevant pages referenced in the ACs
3. browser_take_screenshot → capture baseline state of each page
4. For each WHEN clause:
   a. browser_snapshot → find the referenced element
   b. Verify: Does the element exist? What is its selector (prefer data-testid)?
   c. Verify: Is it visible/enabled in the expected precondition state?
5. For each THEN clause:
   a. browser_snapshot → check if the expected outcome is assertable
   b. Verify: What selector shows success/failure?
   c. Verify: Are error messages accessible?
6. Produce AC Validation Report (see template below)
```

### AC Validation Report Template

```markdown
# AC Validation Report

## AC-1: [Scenario Name]
**Status**: Fully Testable / Partially Testable / Not Testable

**GIVEN**: [precondition]
- Verification: [how to set up state]

**WHEN**: [action]
- Element exists: yes/no
- Selector: [data-testid="..."]

**THEN**: [expected outcome]
- Assertable: yes/no
- Assertion selector: [data-testid="..."]

**Issues Found**: [list]
**Recommendations**: [list]
```

### Bulk AC Validation

For validating multiple ACs at once, produce a summary table:

| AC | Status | Missing Selectors | Action Required |
|----|--------|-------------------|-----------------|
| AC-1 | Fully Testable | None | None |
| AC-2 | Partially Testable | data-testid on submit button | Developer action needed |
| AC-3 | Not Testable | Feature not yet built | Blocked |

### After Validation

- If **Fully Testable**: proceed to test case generation (`engine/prompts/06-testcases.md`)
- If **Partially Testable**: create action items for missing `data-testid` attributes, test data requirements, or API mocks
- If **Not Testable**: route back to feature intake for AC refinement or flag as blocked

---

## Anti-Patterns

| Avoid | Do Instead |
|-------|-----------|
| Automate unstable/changing UI | Flag for manual testing |
| Skip snapshots before clicking | Always snapshot first to get fresh refs |
| Use fixed waits (`sleep(5000)`) | Use `browser_wait` + snapshot verification |
| Ignore console errors | Check and report them as part of evidence |
| Create defects from flaky failures | Route to manual verification first |
| Validate ACs without live application | Always validate against a running instance |
| Skip element verification before writing E2E tests | Always confirm selectors exist first |

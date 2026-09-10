# TypeScript — Stack-Specific Testing Guidance

## Purpose and audience

Use this document for **TypeScript** (and typed JavaScript) on **Node.js** and in **browsers** when selecting runners, mocking strategies, and E2E tools. It complements—does not replace—company-wide QA rules.

## Standards Alignment

This file implements the HatchWorks QA methodology for this specific stack. It aligns with the core principles (risk-first, evidence-based, traceable, confidence-scored) and automation standards (MUST/SHOULD/MAY levels, AAA pattern, independence, boundary mocking, priority-based coverage).

This file maps Global QA to **Vitest/Jest/Mocha**, Playwright/Cypress, and typical CI artifacts. Product decisions and defect severity remain under Global QA.

## How this stack supports the Global QA flow

| Global QA theme | How TypeScript practice maps to it |
|-----------------|--------------------------------------|
| **Evidence & traceability** (Core Principles; Standard QA Inputs; Test Design Directives) | Use descriptive `it`/`test` titles; tags or file layout by feature. Publish **JUnit XML** (Vitest/Jest reporters), **coverage** (Istanbul/c8), **Playwright traces** and HTML reports as CI artifacts. |
| **Operating model** (Automated Lane; Manual / Exploratory / AI-Assisted Lane; workflows for greenfield/brownfield) | Automated: unit + component + API + E2E in pipelines. Manual: exploratory UX and edge environments. **Brownfield:** snapshot/component tests to lock UI; contract tests for HTTP clients. |
| **Risk tiering** (Risk Tiering Standard (T0–T3)) | **Tier 0:** auth, payments, PII—E2E for critical paths, API tests with security cases. **Tier 3:** lighter unit tests or smoke only. |
| **Confidence scoring** (Confidence Scoring) | AI-generated specs need review: async mistakes, weak assertions (`toBeTruthy`), and over-mocking are common. Mark speculative tests; require human approval before relying on them for Tier 0. |
| **Coverage & test design** (Automated Lane; Foundational Testing Standards; Test Design Directives) | **Automated lane:** stable unit/API tests; Playwright for repeatable UI paths. **Manual lane:** visual polish, one-off integrations. Order work per the **Test Design Directives** prioritization order. Prefer testing **user-visible behavior** over implementation details. |
| **Non-functional** (Non-Functional QA Expectations) | k6/Artillery for load; OWASP ZAP or dependency audit (npm); axe-core or Playwright accessibility assertions for a11y checks. |
| **Automation governance** (Automation Governance) | Quarantine flakes (retry limits, dedicated jobs); prefer **role-based API tests** over flaky selectors; assign suite owners. |
| **Defect & release flow** (Defect Governance; Release Readiness Rules; Minimum Human Approval Gates) | Failing required checks block merge. Attach Playwright traces/screenshots to defect drafts; human confirms severity per Global QA. |

## Typical test layers

| Layer | What it is in TS | Automated vs manual |
|-------|------------------|---------------------|
| **Unit** | Pure functions, hooks with mocked deps | Automated |
| **Integration** | DB/HTTP with test server, MSW for fetch | Automated |
| **Component** | React/Vue/Svelte testing-library | Automated |
| **E2E** | Playwright/Cypress against real app | Automated for critical paths |

## Primary tooling

| Concern | Common choices |
|---------|----------------|
| **Runners** | Vitest, Jest, Mocha + ts-node/tsx |
| **Assertions** | Vitest/Jest `expect`, Chai (Mocha) |
| **DOM / React** | Testing Library (`@testing-library/react`), jsdom or happy-dom |
| **HTTP mocking** | MSW (Mock Service Worker) |
| **E2E** | Playwright, Cypress |
| **Coverage** | c8, Istanbul via Vitest/Jest |
| **API contract** | Pact, schemathesis (OpenAPI) |

## Project layout and commands

- **Layout:** `*.test.ts`, `*.spec.ts`, or `__tests__/`; mirror `src/` structure.
- **Common commands:**
  - `vitest` / `jest` / `npm test`
  - `vitest run --coverage`
  - `playwright test` — E2E

## CI and quality gates

- Separate **fast** unit job from **slow** E2E; shard Playwright by project/browser.
- Use `CI=1` and deterministic clocks where tests depend on time.
- Upload traces on failure; cap parallel workers if resource-bound (`--runInBand` for Jest when needed).

## Non-functional testing hooks (Non-Functional QA Expectations)

- **Performance:** Lighthouse CI, k6 scripts against staging.
- **Security:** `npm audit`, Snyk, OWASP checks for web apps.
- **API:** contract tests between services; schema validation on responses.

## Cross-cutting practices from HatchWorks standards

The following apply regardless of stack and are defined in the QA core principles:

- **Start with intent:** Before writing any tests, define what is being built, who it is for, what success looks like, and the main user flow (Core Principles — Start with intent).
- **Minimum expected outputs:** Every feature or change should produce an intent summary, risk list, scenario list, coverage split, execution evidence, and defects if any (Minimum Expected Outputs).
- **Story update loop:** When a story changes, re-check intent, update scenarios and tests, re-run, review evidence, and update defects (Story Update Behavior as described in the QA workflows).
- **Keep outputs simple:** All test reports, defect drafts, and QA artifacts should be clear, short, reusable, and free of unnecessary jargon (Core Principles — Keep outputs simple).

## Exemplary open-source repository

**[vitejs/vite](https://github.com/vitejs/vite)** — Large-scale TypeScript with **Vitest** in the same ecosystem; useful for seeing modern TS test configuration, CI integration, and how a complex project keeps tests maintainable.

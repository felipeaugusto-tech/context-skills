# .NET (C#) — Stack-Specific Testing Guidance

## Purpose and audience

Use this document for **.NET** libraries and services (ASP.NET Core, console workers) when choosing test frameworks, WebApplicationFactory patterns, and CI coverage gates. It complements—does not replace—company-wide QA rules.

## Standards Alignment

This file implements the HatchWorks QA methodology for this specific stack. It aligns with the core principles (risk-first, evidence-based, traceable, confidence-scored) and automation standards (MUST/SHOULD/MAY levels, AAA pattern, independence, boundary mocking, priority-based coverage).

.NET integrates tightly with **Visual Studio** and the **`dotnet` CLI**; CI emits **TRX** / xUnit XML and **Coverlet** coverage. Global QA remains authoritative for defects and releases.

## How this stack supports the Global QA flow

| Global QA theme | How .NET practice maps to it |
|-----------------|--------------------------------|
| **Evidence & traceability** (Core Principles; Standard QA Inputs; Test Design Directives) | Use `[Fact]`/`[Theory]` names and traits (`[Trait]`) for filtering. Publish **TRX**, xUnit XML, and **Coverlet** Cobertura/OpenCover output as pipeline artifacts. |
| **Operating model** (Automated Lane; Manual / Exploratory / AI-Assisted Lane; workflows for greenfield/brownfield) | Automated: `dotnet test` in CI; integration with Testcontainers where applicable. Manual: exploratory and UAT. **Brownfield:** golden tests or approval tests for legacy behavior. |
| **Risk tiering** (Risk Tiering Standard (T0–T3)) | **Tier 0:** auth, data protection—security-focused tests, integration against real auth and DB where possible. **Tier 3:** lighter unit tests. |
| **Confidence scoring** (Confidence Scoring) | Review AI-generated tests for misleading `[Theory]` data and missing edge cases; generated tests are drafts until approved. |
| **Coverage & test design** (Automated Lane; Foundational Testing Standards; Test Design Directives) | **Automated:** unit with xUnit/NUnit/MSTest; **WebApplicationFactory** for ASP.NET Core integration. **Manual:** exploratory UX. Follow the **Test Design Directives** prioritization order. |
| **Non-functional** (Non-Functional QA Expectations) | NBomber/BenchmarkDotNet for perf; OWASP dependency-check; Azure Key Vault / auth integration tests in secure environments. |
| **Automation governance** (Automation Governance) | Use collection/fixture patterns to reduce flake; quarantine unstable E2E with explicit ownership. Prefer stable API tests over brittle UI when risk is equivalent. |
| **Defect & release flow** (Defect Governance; Release Readiness Rules; Minimum Human Approval Gates) | Failed `dotnet test` blocks per policy. Attach test output and logs; humans assign severity under Global QA. |

## Typical test layers

| Layer | What it is in .NET | Automated vs manual |
|-------|---------------------|------------------------|
| **Unit** | Classes with mocked `I*` dependencies | Automated |
| **Integration** | WebApplicationFactory, TestServer, real SQL with Testcontainers | Automated |
| **E2E** | Playwright/Selenium against running site | Automated for critical paths |

## Primary tooling

| Concern | Common choices |
|---------|----------------|
| **Frameworks** | xUnit (common in new projects), NUnit, MSTest |
| **Assertions** | FluentAssertions, Shouldly, built-in asserts |
| **Mocking** | Moq, NSubstitute |
| **ASP.NET Core** | WebApplicationFactory, TestServer |
| **Coverage** | Coverlet (`dotnet test --collect:"XPlat Code Coverage"`) |
| **Build** | `dotnet test`, solution-level test projects |

## Project layout and commands

- **Layout:** `*.Tests` / `*.IntegrationTests` projects; mirror folder structure of SUT.
- **Common commands:**
  - `dotnet test`
  - `dotnet test --collect:"XPlat Code Coverage"`
  - `dotnet test --filter Category=Integration`

## CI and quality gates

- Use **`--logger trx`** for Azure DevOps/GitHub integration.
- Run `dotnet format`, analyzers, and `dotnet list package --vulnerable` per policy.
- Separate fast unit jobs from slower integration jobs.

## Non-functional testing hooks (Non-Functional QA Expectations)

- **Performance:** BenchmarkDotNet in dedicated projects; load tests with NBomber or k6 against staging.
- **Security:** dependency scanning, Sonar rules, security headers and authz tests in ASP.NET Core.
- **API:** contract tests for public HTTP APIs; verify ProblemDetails and status codes.

## Cross-cutting practices from HatchWorks standards

The following apply regardless of stack and are defined in the QA core principles:

- **Start with intent:** Before writing any tests, define what is being built, who it is for, what success looks like, and the main user flow (Core Principles — Start with intent).
- **Minimum expected outputs:** Every feature or change should produce an intent summary, risk list, scenario list, coverage split, execution evidence, and defects if any (Minimum Expected Outputs).
- **Story update loop:** When a story changes, re-check intent, update scenarios and tests, re-run, review evidence, and update defects (Story Update Behavior as described in the QA workflows).
- **Keep outputs simple:** All test reports, defect drafts, and QA artifacts should be clear, short, reusable, and free of unnecessary jargon (Core Principles — Keep outputs simple).

## Exemplary open-source repository

**[dotnet/aspnetcore](https://github.com/dotnet/aspnetcore)** — Reference-grade ASP.NET Core codebase with extensive xUnit usage, integration testing patterns, and CI that demonstrates how a large .NET project structures tests and coverage.

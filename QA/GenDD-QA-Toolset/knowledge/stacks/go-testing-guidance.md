# Go — Stack-Specific Testing Guidance

## Purpose and audience

Use this document for **Go** modules and services when applying idiomatic `testing`, table-driven tests, integration patterns, and CI gates (`race`, coverage). It complements—does not replace—company-wide QA rules.

## Standards Alignment

This file implements the HatchWorks QA methodology for this specific stack. It aligns with the core principles (risk-first, evidence-based, traceable, confidence-scored) and automation standards (MUST/SHOULD/MAY levels, AAA pattern, independence, boundary mocking, priority-based coverage).

Go favors **simple packages**, **explicit errors**, and **concurrency discipline**. Global QA still owns release and defect policy; Go tooling provides **race detection**, **benchmarks**, and **coverage profiles** as evidence.

## How this stack supports the Global QA flow

| Global QA theme | How Go practice maps to it |
|-----------------|--------------------------------|
| **Evidence & traceability** (Core Principles; Standard QA Inputs; Test Design Directives) | Table-driven subtests name scenarios; use `t.Run` for structure. Publish **JUnit XML** via `go-junit-report` or native CI parsing, and **coverage** (`cover.out`, `coverprofile`). |
| **Operating model** (Automated Lane; Manual / Exploratory / AI-Assisted Lane; workflows for greenfield/brownfield) | Automated: `go test ./...` in CI; integration with real dependencies via build tags or separate packages. Manual: staging validation. **Brownfield:** characterization tests around exported APIs before refactors. |
| **Risk tiering** (Risk Tiering Standard (T0–T3)) | **Tier 0:** auth, tenancy, financial code—full unit + integration + `race`; fuzzing for parsers. **Tier 3:** narrower tests. |
| **Confidence scoring** (Confidence Scoring) | AI-generated tests need review for goroutine leaks, improper `t.Parallel` use, and weak assertions. |
| **Coverage & test design** (Automated Lane; Foundational Testing Standards; Test Design Directives) | **Automated:** fast unit tests; `httptest` for HTTP handlers; docker-compose or Testcontainers in CI for integration. **Manual:** exploratory checks on deployed services. Follow the **Test Design Directives** prioritization order. |
| **Non-functional** (Non-Functional QA Expectations) | `go test -race`; fuzzing (`go test -fuzz`); benchmarks for perf regressions; `staticcheck`, `govulncheck`. |
| **Automation governance** (Automation Governance) | Flaky tests: fix data races and shared state; avoid sleeping—use synchronization. Quarantine with build tags + issue links. |
| **Defect & release flow** (Defect Governance; Release Readiness Rules; Minimum Human Approval Gates) | Red `go test` or race failures block per policy. Panic stacks and test output feed triage; humans apply Global QA severity. |

## Typical test layers

| Layer | What it is in Go | Automated vs manual |
|-------|-------------------|---------------------|
| **Unit** | Same-package tests, `httptest`, mocks via interfaces | Automated |
| **Integration** | Tests hitting real DB/queue with `-tags=integration` | Automated in dedicated jobs |
| **E2E** | Black-box against running binary or k8s env | Mix; often CI against ephemeral env |

## Primary tooling

| Concern | Common choices |
|---------|----------------|
| **Core** | `testing` package, table-driven tests, `t.Parallel` where safe |
| **Assertions** | `testify/require`, `assert`, or stdlib only |
| **Mocks** | `gomock` + `mockgen`, or hand-written fakes |
| **HTTP** | `net/http/httptest` |
| **Coverage / race** | `go test -cover`, `-race` |
| **Fuzzing** | Native fuzzing (`-fuzz`) |
| **Containers** | Testcontainers-Go |

## Project layout and commands

- **Layout:** `*_test.go` beside sources; `testdata/` for fixtures; `internal/` for test-only helpers when needed.
- **Common commands:**
  - `go test ./...`
  - `go test -race -coverprofile=coverage.out ./...`
  - `go test -fuzz=FuzzName` — fuzz target

## CI and quality gates

- Run **race detector** on CI for concurrent code paths (may use `-short` to limit runtime).
- Use **module caching** (`GOMODCACHE`); pin Go version.
- Fail on `go vet`, `staticcheck`, and `govulncheck` per policy.

## Non-functional testing hooks (Non-Functional QA Expectations)

- **Performance:** `go test -bench` with benchstat comparisons on main.
- **Security:** `govulncheck`, dependency review; fuzz HTTP and parsers.
- **API:** contract tests for public HTTP/gRPC APIs.

## Cross-cutting practices from HatchWorks standards

The following apply regardless of stack and are defined in the QA core principles:

- **Start with intent:** Before writing any tests, define what is being built, who it is for, what success looks like, and the main user flow (Core Principles — Start with intent).
- **Minimum expected outputs:** Every feature or change should produce an intent summary, risk list, scenario list, coverage split, execution evidence, and defects if any (Minimum Expected Outputs).
- **Story update loop:** When a story changes, re-check intent, update scenarios and tests, re-run, review evidence, and update defects (Story Update Behavior as described in the QA workflows).
- **Keep outputs simple:** All test reports, defect drafts, and QA artifacts should be clear, short, reusable, and free of unnecessary jargon (Core Principles — Keep outputs simple).

## Exemplary open-source repository

**[kubernetes/kubernetes](https://github.com/kubernetes/kubernetes)** — Large-scale idiomatic Go: table-driven tests, integration boundaries, and CI discipline—useful for seeing how a complex Go codebase organizes tests and handles scale.

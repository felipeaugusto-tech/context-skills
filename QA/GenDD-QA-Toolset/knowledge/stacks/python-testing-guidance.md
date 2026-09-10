# Python — Stack-Specific Testing Guidance

## Purpose and audience

Use this document when choosing tools, structuring test suites, and wiring CI for **CPython** applications and libraries (CLI, APIs, services, data jobs). It complements—does not replace—company-wide QA rules.

## Standards Alignment

This file implements the HatchWorks QA methodology for this specific stack. It aligns with the core principles (risk-first, evidence-based, traceable, confidence-scored) and automation standards (MUST/SHOULD/MAY levels, AAA pattern, independence, boundary mocking, priority-based coverage).

This file translates those expectations into **Python-specific** runners, libraries, and CI artifacts. Product and release decisions still follow Global QA; Python tooling supplies **technical evidence** and **signals** (pass/fail, coverage, reports).

## How this stack supports the Global QA flow

| Global QA theme | How Python practice maps to it |
|-----------------|--------------------------------|
| **Evidence & traceability** (Core Principles; Standard QA Inputs; Test Design Directives) | Use clear test names and markers (`@pytest.mark`) to tie cases to requirements or risks. Publish **JUnit XML** (`pytest --junitxml`), **coverage** (`coverage.py` HTML/XML), and logs from failed runs as pipeline artifacts. Link issue IDs in test docstrings or markers where your process requires it. |
| **Operating model** (Automated Lane; Manual / Exploratory / AI-Assisted Lane; workflows for greenfield/brownfield) | Automated: `pytest`/`tox`/`nox` in CI. Manual/exploratory: still required for judgment-heavy UX and production-like checks. **Brownfield:** add characterization or golden-file tests to lock observed behavior before refactors. |
| **Risk tiering** (Risk Tiering Standard (T0–T3)) | **Tier 0:** auth, tenancy, money—prioritize targeted unit tests, contract tests, and integration tests with real or containerized dependencies. **Tier 3:** lighter unit coverage; optional smoke only. |
| **Confidence scoring** (Confidence Scoring) | Tests and suites generated or inferred by AI are **drafts** until a human reviews them. Mark speculative tests clearly; do not treat generated coverage alone as proof of correctness. |
| **Coverage & test design** (Automated Lane; Foundational Testing Standards; Test Design Directives) | **Automated lane:** fast unit tests, API tests, stable integration tests. **Manual lane:** exploratory, visual, one-off scenarios. Follow the **Test Design Directives** prioritization order: critical path → major failures → security/permissions → data integrity → integrations → NFR. |
| **Non-functional** (Non-Functional QA Expectations) | Use load tools (e.g. Locust, k6 via subprocess), security scanners, and `hypothesis` for property checks where appropriate; align thresholds with project NFR docs. |
| **Automation governance** (Automation Governance) | Quarantine flaky tests (`pytest` marks, separate jobs); prefer testing **stable boundaries** (HTTP APIs, messages) over brittle full-stack UI when both exist. Every suite has an owner. |
| **Defect & release flow** (Defect Governance; Release Readiness Rules; Minimum Human Approval Gates) | Failing CI blocks merge or release per policy. Defect severity and release approval remain human gates under Global QA; Python CI provides reproducible failure output (tracebacks, fixtures used, seed for randomized tests). |

## Typical test layers

| Layer | What it is in Python | Automated Lane vs Manual / Exploratory / AI-Assisted Lane |
|-------|----------------------|---------------------------|
| **Unit** | Functions/classes with mocks/fakes at I/O boundaries | Usually automated; primary fast feedback |
| **Integration** | Real DB, message broker, or HTTP with TestClient/`httpx` against app in process; Docker services via Testcontainers or compose | Automated when stable; may be nightly for slow suites |
| **End-to-end** | Browser automation (e.g. Playwright) or full black-box HTTP against deployed env | Automated for critical paths; exploratory for edge UX |

## Primary tooling

| Concern | Common choices |
|---------|----------------|
| **Test runner / framework** | `pytest` (dominant), `unittest` (stdlib), `nose2` (legacy) |
| **Assertions / ergonomics** | `pytest` asserts, `unittest` assertions, `hypothesis` for property-based tests |
| **Mocks / doubles** | `unittest.mock`, `pytest-mock`, `responses` / `httpx` mocking for HTTP |
| **Coverage** | `coverage.py` with `pytest-cov` |
| **Multi-env orchestration** | `tox`, `nox` |
| **Async** | `pytest-asyncio` |
| **Django / Flask** | `pytest-django`, Flask test client, factory_boy for data |
| **Performance** | `pytest-benchmark` (micro-benchmarks; not a substitute for load testing) |

## Project layout and commands

- **Layout:** mirror source (`tests/` or `test/` alongside package); use `conftest.py` for shared fixtures.
- **Common commands:**
  - `pytest` — run all tests
  - `pytest tests/unit -q` — scoped run
  - `pytest --cov=packagename --cov-report=xml` — coverage for CI
  - `tox` / `nox -s tests` — matrix across Python versions

## CI and quality gates

- Run **lint + typecheck + tests** as separate steps; fail fast on import errors.
- Upload **JUnit XML** and **coverage** for dashboards and audit trails (**CI/CD Integration**).
- Pin dependencies; use deterministic seeds for randomized/property tests in CI when debugging flakes.
- For parallel runs, avoid shared global state; use isolated temp dirs (`tmp_path`).

## Non-functional testing hooks (Non-Functional QA Expectations)

- **Performance:** Locust, k6, or pytest load against staging; set SLOs in project docs.
- **Security:** Bandit, pip-audit; OWASP checks for web apps.
- **API:** schemathesis or contract tests against OpenAPI where applicable.

## Cross-cutting practices from HatchWorks standards

The following apply regardless of stack and are defined in the QA core principles:

- **Start with intent:** Before writing any tests, define what is being built, who it is for, what success looks like, and the main user flow (Core Principles — Start with intent).
- **Minimum expected outputs:** Every feature or change should produce an intent summary, risk list, scenario list, coverage split, execution evidence, and defects if any (Minimum Expected Outputs).
- **Story update loop:** When a story changes, re-check intent, update scenarios and tests, re-run, review evidence, and update defects (Story Update Behavior as described in the QA workflows).
- **Keep outputs simple:** All test reports, defect drafts, and QA artifacts should be clear, short, reusable, and free of unnecessary jargon (Core Principles — Keep outputs simple).

## Exemplary open-source repository

**[psf/requests](https://github.com/psf/requests)** — Mature `pytest` usage, clear test layout, and CI patterns suitable for learning how a widely used Python library structures tests and keeps them maintainable.

# Java — Stack-Specific Testing Guidance

## Purpose and audience

Use this document for **JVM** applications (Spring, Micronaut, plain Java libraries) when selecting test frameworks, layering tests, and configuring Gradle/Maven CI. It complements—does not replace—company-wide QA rules.

## Standards Alignment

This file implements the HatchWorks QA methodology for this specific stack. It aligns with the core principles (risk-first, evidence-based, traceable, confidence-scored) and automation standards (MUST/SHOULD/MAY levels, AAA pattern, independence, boundary mocking, priority-based coverage).

This file maps Global QA outcomes to **Java ecosystem** tools (JUnit 5, Mockito, build plugins). Release and defect processes remain defined by Global QA; Java pipelines produce **verifiable evidence** (Surefire/Failsafe reports, coverage XML).

## How this stack supports the Global QA flow

| Global QA theme | How Java practice maps to it |
|-----------------|--------------------------------|
| **Evidence & traceability** (Core Principles; Standard QA Inputs; Test Design Directives) | Use `@DisplayName`, `@Tag` (JUnit 5), or suites aligned to requirements. Publish **Surefire** / **Failsafe** XML, JaCoCo coverage reports, and build scan links as CI artifacts. |
| **Operating model** (Automated Lane; Manual / Exploratory / AI-Assisted Lane; workflows for greenfield/brownfield) | Automated: Gradle `test` / Maven `verify`, split unit vs integration. Manual: exploratory and staging validation. **Brownfield:** Spring Boot tests with `@WebMvcTest` / `@DataJpaTest` slices to characterize behavior incrementally. |
| **Risk tiering** (Risk Tiering Standard (T0–T3)) | **Tier 0:** security, multi-tenancy, payments—contract tests, integration tests with Testcontainers, mutation testing where justified. **Tier 3:** lighter unit coverage. |
| **Confidence scoring** (Confidence Scoring) | AI-generated `@Test` methods need human review for assertions and setup. Do not merge generated tests without checking they assert meaningful behavior. |
| **Coverage & test design** (Automated Lane; Foundational Testing Standards; Test Design Directives) | **Automated:** JUnit + Mockito for units; Testcontainers/WireMock for integration; Rest Assured or MockMvc for APIs. **Manual:** exploratory paths and production-only configs. Prioritize the **Test Design Directives** prioritization order. |
| **Non-functional** (Non-Functional QA Expectations) | JMeter/Gatling for load; OWASP Dependency Check; Pact for contracts where services integrate. |
| **Automation governance** (Automation Governance) | Separate flaky retries from real failures; tag slow tests; `@Disabled` with ticket reference only as temporary. Prefer API-level tests over flaky UI when both cover the same risk. |
| **Defect & release flow** (Defect Governance; Release Readiness Rules; Minimum Human Approval Gates) | Failing `verify`/pipeline gates merge/release per policy. Human triage uses Global QA severity; Java stacks attach stack traces and test stdout from Surefire/Failsafe. |

## Typical test layers

| Layer | What it is on the JVM | Automated vs manual |
|-------|------------------------|------------------------|
| **Unit** | Isolated classes with mocks (Mockito) | Automated; default PR gate |
| **Integration** | Spring context, DB, messaging with Testcontainers or embedded brokers | Automated; often parallel "integration" CI job |
| **End-to-end** | Selenium/Playwright/Cypress against running app, or full-stack tests | Automated for key journeys; manual for edge UX |

## Primary tooling

| Concern | Common choices |
|---------|----------------|
| **Unit framework** | JUnit 5 (Jupiter); TestNG in older codebases |
| **Assertions** | AssertJ, Hamcrest |
| **Mocking** | Mockito |
| **Spring** | `@SpringBootTest`, `@WebMvcTest`, `@DataJpaTest`, `MockMvc`, `WebTestClient` |
| **Integration / infra** | Testcontainers, WireMock |
| **Mutation testing** | Pitest |
| **Coverage** | JaCoCo |
| **Build** | Gradle (`test`, `integrationTest`), Maven (Surefire, Failsafe) |
| **BDD (optional)** | Cucumber JVM |

## Project layout and commands

- **Layout:** `src/test/java` mirroring main packages; resources in `src/test/resources`.
- **Common commands:**
  - `./gradlew test` / `mvn test` — unit tests
  - `./gradlew integrationTest` / `mvn verify` — includes integration when configured
  - JaCoCo XML for Sonar or code coverage gates

## CI and quality gates

- Cache Gradle/Maven dependencies; run tests with **consistent JVM** and timezone.
- Split fast unit jobs from slower integration jobs to match the **Automated Lane** and **CI/CD Integration** staging model.
- Fail on flaky retries exceeding policy; surface Surefire reports in UI.

## Non-functional testing hooks (Non-Functional QA Expectations)

- **Performance:** Gatling/JMeter in CI or scheduled pipelines.
- **Security:** OWASP Dependency Check, SpotBugs, Sonar security rules.
- **API:** Contract tests (Pact, Spring Cloud Contract) for consumer/provider alignment.

## Cross-cutting practices from HatchWorks standards

The following apply regardless of stack and are defined in the QA core principles:

- **Start with intent:** Before writing any tests, define what is being built, who it is for, what success looks like, and the main user flow (Core Principles — Start with intent).
- **Minimum expected outputs:** Every feature or change should produce an intent summary, risk list, scenario list, coverage split, execution evidence, and defects if any (Minimum Expected Outputs).
- **Story update loop:** When a story changes, re-check intent, update scenarios and tests, re-run, review evidence, and update defects (Story Update Behavior as described in the QA workflows).
- **Keep outputs simple:** All test reports, defect drafts, and QA artifacts should be clear, short, reusable, and free of unnecessary jargon (Core Principles — Keep outputs simple).

## Exemplary open-source repository

**[spring-projects/spring-boot](https://github.com/spring-projects/spring-boot)** — Large, real-world use of JUnit 5, Spring Test, and modular test slices; useful for studying how a mature Java codebase structures unit vs integration tests and CI.

# C++ — Stack-Specific Testing Guidance

## Purpose and audience

Use this document for **native C++** libraries and applications (CMake, Bazel, or other build systems) when choosing unit test frameworks, sanitizer/fuzzer workflows, and CI gates. It complements—does not replace—company-wide QA rules.

## Standards Alignment

This file implements the HatchWorks QA methodology for this specific stack. It aligns with the core principles (risk-first, evidence-based, traceable, confidence-scored) and automation standards (MUST/SHOULD/MAY levels, AAA pattern, independence, boundary mocking, priority-based coverage).

C++ tooling emphasizes **correctness under UB**, **memory safety**, and **deterministic builds**. Human release gates from Global QA still apply; CI adds **technical signals** (sanitizer failures, test logs, coverage where enabled).

## How this stack supports the Global QA flow

| Global QA theme | How C++ practice maps to it |
|-----------------|--------------------------------|
| **Evidence & traceability** (Core Principles; Standard QA Inputs; Test Design Directives) | Name tests for behavior; group by component. Publish **CTest** / GoogleTest XML or JUnit-compatible output, sanitizer logs, and (if used) **gcov/llvm-cov** reports as artifacts. |
| **Operating model** (Automated Lane; Manual / Exploratory / AI-Assisted Lane; workflows for greenfield/brownfield) | Automated: build + unit tests + sanitizers in CI. Manual: exploratory and hardware-specific checks. **Brownfield:** add tests before refactors; use golden outputs for legacy behavior. |
| **Risk tiering** (Risk Tiering Standard (T0–T3)) | **Tier 0:** security, memory safety, concurrency—ASan/TSan/UBSan, fuzzing, stress tests. **Tier 3:** lighter unit coverage. |
| **Confidence scoring** (Confidence Scoring) | AI-generated tests must be reviewed: undefined behavior and lifetimes are easy to get wrong. Treat generated coverage as insufficient without human review on hot paths. |
| **Coverage & test design** (Automated Lane; Foundational Testing Standards; Test Design Directives) | **Automated:** fast unit tests, component tests. **Manual:** rare edge cases on target hardware. Follow the **Test Design Directives** prioritization order; favor tests that catch UB and API misuse. |
| **Non-functional** (Non-Functional QA Expectations) | Sanitizers, valgrind (where applicable), micro-benchmarks (Google Benchmark), libFuzzer/afl++ for attack surface; perf regressions via benchmark baselines. |
| **Automation governance** (Automation Governance) | Flaky tests often indicate UB or timing assumptions—fix root cause, not retries. Quarantine with explicit tracking. |
| **Defect & release flow** (Defect Governance; Release Readiness Rules; Minimum Human Approval Gates) | Red CI blocks per policy. Sanitizer crashes are release-critical until resolved or waived under process. |

## Typical test layers

| Layer | What it is in C++ | Automated vs manual |
|-------|---------------------|------------------------|
| **Unit** | Functions/classes with mocks or fakes; no I/O or isolated I/O | Automated |
| **Integration** | Multiple translation units, real files/sockets, threaded code | Automated when deterministic |
| **System / E2E** | Full binaries, hardware-in-the-loop | Mix; often manual or specialized lab automation |

## Primary tooling

| Concern | Common choices |
|---------|----------------|
| **Frameworks** | GoogleTest, Catch2, doctest |
| **Build / discovery** | CMake + CTest, Bazel `cc_test`, Meson |
| **Mocks** | GoogleMock, hand-written fakes (common) |
| **Coverage** | gcov/lcov, llvm-cov (Clang) |
| **Sanitizers** | ASan, TSan, UBSan (Clang/GCC) |
| **Fuzzing** | libFuzzer, AFL++ |
| **Benchmarks** | Google Benchmark |

## Project layout and commands

- **Layout:** `tests/` or co-located `*_test.cpp`; CMake `enable_testing()` + `add_test`.
- **Common commands:**
  - `ctest --output-on-failure`
  - `cmake --build build && cmake --build build --target test`
  - Sanitizer builds: separate CMake preset or flags (`-fsanitize=address`, etc.)

## CI and quality gates

- Use **matrix builds**: Debug + Release, multiple compilers (GCC/Clang), sometimes multiple platforms.
- Run **sanitizer** jobs on PR or nightly; fail on leaks/data races/UB reports.
- Pin compiler versions for reproducibility; cache ccache/sccache when possible.

## Non-functional testing hooks (Non-Functional QA Expectations)

- **Performance:** benchmarks with thresholds; compare to baseline in CI where feasible.
- **Security:** fuzzing for parsers/protocols; static analysis (clang-tidy, cppcheck).
- **Concurrency:** TSan on threaded tests; stress tests for locks and queues.

## Cross-cutting practices from HatchWorks standards

The following apply regardless of stack and are defined in the QA core principles:

- **Start with intent:** Before writing any tests, define what is being built, who it is for, what success looks like, and the main user flow (Core Principles — Start with intent).
- **Minimum expected outputs:** Every feature or change should produce an intent summary, risk list, scenario list, coverage split, execution evidence, and defects if any (Minimum Expected Outputs).
- **Story update loop:** When a story changes, re-check intent, update scenarios and tests, re-run, review evidence, and update defects (Story Update Behavior as described in the QA workflows).
- **Keep outputs simple:** All test reports, defect drafts, and QA artifacts should be clear, short, reusable, and free of unnecessary jargon (Core Principles — Keep outputs simple).

## Exemplary open-source repository

**[fmtlib/fmt](https://github.com/fmtlib/fmt)** — Real-world CMake layout, widely used C++ testing patterns, and CI that exercises multiple compilers and configurations—good reference for structuring library tests.

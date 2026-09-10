---
description: QA Standards Creator — generates stack-specific testing guidance and CI profiles for any technology stack. Load when onboarding a new project or creating QA standards for an unsupported stack.
globs:
---

# QA Standards Creator

---

## Quick Start

**Generate from a known stack:**
```text
"Create QA testing guidance for a Rust project using cargo test"
```

**Generate from brownfield analysis:**
```text
"Using this brownfield analysis context, create stack-specific QA standards: [paste analysis]"
```

**Generate both guidance and CI profile:**
```text
"Create testing guidance and CI profile for a Ruby on Rails project with RSpec"
```

---

## What It Produces

For any tech stack, this skill generates two files:

### 1. `{stack}-testing-guidance.md`
A markdown file containing:
- Purpose and audience
- How the stack maps to HatchWorks QA themes (evidence, risk tiering, confidence, coverage, automation governance, defect flow)
- Typical test layers (unit, integration, E2E) with stack-specific tools
- Primary tooling table (runner, assertions, mocks, coverage, orchestration)
- Project layout and common commands
- CI quality gates
- Non-functional testing hooks
- Cross-cutting practices from HatchWorks standards
- Exemplary open-source repository for reference

### 2. `{stack}.yml`
A YAML CI profile containing:
- `name` and `description`
- `test_command` — the default test invocation
- `artifact_format` — `junit_xml`, `trx`, or other
- `coverage_format` — `cobertura_xml`, `lcov`, etc.
- `frameworks` — runner, assertions, mocks, coverage, orchestration
- `common_artifacts` — where test results, coverage, and logs land
- `ci_example` — shell snippet for running tests and the QA orchestrator
- `stack_context` — LLM-injectable context for framework-aware triage
- `guidance` — relative path to the companion `.md` file

---

## How It Works

```text
Input (stack name, brownfield analysis, or project description)
    |
    v
+-------------------------------------------------------+
| 1. IDENTIFY STACK                                     |
|    - Detect language, framework, test runner           |
|    - Identify CI/CD platform if mentioned              |
+-------------------------------------------------------+
    |
    v
+-------------------------------------------------------+
| 2. LOAD REFERENCES                                    |
|    - Read .cursor/rules/core-principles.md for QA themes         |
|    - Read .cursor/rules/automation-qa-standards.md for test rules |
|    - Read 1-2 existing knowledge/stacks/ files as format models |
+-------------------------------------------------------+
    |
    v
+-------------------------------------------------------+
| 3. GENERATE                                           |
|    - Create {stack}-testing-guidance.md                |
|    - Create {stack}.yml                               |
|    - Map QA themes to stack-specific tools             |
+-------------------------------------------------------+
    |
    v
+-------------------------------------------------------+
| 4. VALIDATE                                           |
|    - Run checklist below                              |
|    - Ensure all required sections are present          |
+-------------------------------------------------------+
    |
    v
Files ready in knowledge/stacks/
```

---

## Verification Checklist

Run after generating. Fix any failures.

### Testing Guidance (.md)
- [ ] Has "Purpose and audience" section
- [ ] Has "Inherits from" section referencing `.cursor/rules/core-principles.md` and `.cursor/rules/automation-qa-standards.md`
- [ ] Has "How this stack supports the Global QA flow" mapping table
- [ ] Has "Typical test layers" table (unit, integration, E2E)
- [ ] Has "Primary tooling" table with real, current tool names
- [ ] Has "Project layout and commands" section
- [ ] Has "CI and quality gates" section
- [ ] Has "Non-functional testing hooks" section
- [ ] Has "Cross-cutting practices" section
- [ ] References an exemplary open-source repository
- [ ] No tool-specific QA jargon (no Jira, Xray, Mori references)
- [ ] All tools mentioned actually exist and are current

### CI Profile (.yml)
- [ ] Has all required fields: name, description, test_command, artifact_format, coverage_format
- [ ] Has frameworks block with at least: runner, assertions, mocks, coverage
- [ ] Has common_artifacts block
- [ ] Has ci_example with working shell commands
- [ ] Has stack_context with framework-specific triage hints
- [ ] Has guidance field pointing to the companion .md file
- [ ] artifact_format matches what the test runner actually produces

---

## Anti-Patterns

| Avoid | Do Instead |
|-------|-----------|
| Invent tool names | Only reference real, actively maintained tools |
| Copy Python guidance for all stacks | Research the idiomatic testing approach for each language |
| Skip the QA theme mapping table | This is what connects stack tooling to HatchWorks methodology |
| Use outdated framework versions | Check current ecosystem conventions |
| Hardcode paths | Use relative paths that work from the repo root |

---

## Reference Examples

Pre-built stack files in `knowledge/stacks/` serve as format models:

| Stack | Guidance | Profile |
|-------|----------|---------|
| Python | `knowledge/stacks/python-testing-guidance.md` | `knowledge/stacks/python.yml` |
| TypeScript | `knowledge/stacks/typescript-testing-guidance.md` | `knowledge/stacks/typescript.yml` |
| Java | `knowledge/stacks/java-testing-guidance.md` | `knowledge/stacks/java.yml` |
| Go | `knowledge/stacks/go-testing-guidance.md` | `knowledge/stacks/go.yml` |
| C++ | `knowledge/stacks/cpp-testing-guidance.md` | `knowledge/stacks/cpp.yml` |
| .NET | `knowledge/stacks/dotnet-testing-guidance.md` | `knowledge/stacks/dotnet.yml` |

When generating for a new stack, read at least one of these as a structural template.

# QA-GenDD CI/CD Orchestrator

Platform-agnostic Python script that chains QA-GenDD prompts through an LLM API to automate the AI testing stream after test execution in any CI/CD pipeline.

## What it does

After your test suites run, the orchestrator:

1. **Parses** test artifacts (JUnit XML, coverage reports, failure logs)
2. **Stack profile (optional)** — when you pass `--stack {name}`, loads `knowledge/stacks/{name}.yml` and appends `stack_context` plus the **`guidance`** markdown file (same directory) into the LLM system prompt when `guidance:` is set in the YAML
3. **Evidence Review** — sends results through `engine/prompts/11-evidence.md` to assess what passed, failed, and is unclear
4. **Defect Triage** — sends failures through `engine/prompts/10-triage.md` to categorize and prioritize
5. **Defect Drafting** — sends actionable failures (high/medium confidence) through `engine/prompts/09-defects.md` to produce structured bug reports
6. **Release Readiness** — sends the full picture through `engine/prompts/12-release.md` for a release recommendation

## Outputs

| File | Contents |
|------|----------|
| `qa-summary.md` | Human-readable summary of all stages |
| `defects.json` | Structured defect drafts (JSON array) for downstream Jira/Xray import |
| `release-assessment.json` | Release status with test metrics and AI assessment |

**Exit code:** 0 = release recommended, 1 = not recommended or insufficient evidence. Use this as a CI gate.

## Setup

```bash
pip install -r engine/ci/requirements.txt
```

## Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `QA_LLM_PROVIDER` | Yes | `anthropic` or `openai` |
| `ANTHROPIC_API_KEY` | When provider is anthropic | Anthropic API key |
| `OPENAI_API_KEY` | When provider is openai | OpenAI API key |
| `QA_MODEL` | No | Model override (defaults: `claude-sonnet-4-20250514` for Anthropic, `gpt-4o` for OpenAI) |

## Usage

```bash
python engine/ci/qa-orchestrator.py \
  --stack python \
  --test-results ./test-output/junit.xml \
  --coverage ./test-output/coverage.xml \
  --logs ./test-output/failures.log \
  --output ./qa-output/
```

**Arguments:**

| Argument | Required | Description |
|----------|----------|-------------|
| `--test-results` | Yes | Path to test results file (JUnit XML or TRX) |
| `--coverage` | No | Path to coverage report |
| `--logs` | No | Path to failure logs |
| `--output` | No | Output directory (default: `./qa-output`) |
| `--stack` | No | Tech stack profile: `python`, `typescript`, `java`, `go`, `cpp`, `dotnet`. Loads `knowledge/stacks/{stack}.yml` for framework-aware analysis. |

### Stack profiles

When `--stack` is provided, the orchestrator loads a profile from `knowledge/stacks/` that:

1. **Injects stack context** into the LLM system prompt so defect reports, triage, and evidence analysis reference the correct framework (e.g., pytest fixtures for Python, Spring context for Java)
2. **Selects the right artifact parser** (JUnit XML for most stacks, TRX for .NET)
3. **Includes the stack's CI example** in the output summary

When `--stack` is omitted, the orchestrator works in generic mode (backward compatible).

### Per-stack CI examples

**Python:**
```bash
pytest --junitxml=test-output/junit.xml --cov=src --cov-report=xml:test-output/coverage.xml
python engine/ci/qa-orchestrator.py --stack python --test-results test-output/junit.xml --coverage test-output/coverage.xml
```

**TypeScript:**
```bash
vitest run --reporter=junit --outputFile=test-output/junit.xml --coverage
python engine/ci/qa-orchestrator.py --stack typescript --test-results test-output/junit.xml
```

**Java (Gradle):**
```bash
./gradlew test jacocoTestReport
python engine/ci/qa-orchestrator.py --stack java --test-results build/test-results/test/ --coverage build/reports/jacoco/test/jacocoTestReport.xml
```

**Go:**
```bash
gotestsum --junitfile test-output/junit.xml -- -race -coverprofile=test-output/coverage.out ./...
python engine/ci/qa-orchestrator.py --stack go --test-results test-output/junit.xml --coverage test-output/coverage.out
```

**C++:**
```bash
ctest --test-dir build --output-junit test-output/junit.xml --output-on-failure
python engine/ci/qa-orchestrator.py --stack cpp --test-results test-output/junit.xml
```

**.NET:**
```bash
dotnet test --logger "trx;LogFileName=results.trx" --collect:"XPlat Code Coverage"
python engine/ci/qa-orchestrator.py --stack dotnet --test-results TestResults/results.trx --coverage TestResults/coverage.cobertura.xml
```

## Example: GitHub Actions

```yaml
jobs:
  test-and-qa:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: pytest --junitxml=test-output/junit.xml --cov --cov-report=xml:test-output/coverage.xml

      - name: Install QA orchestrator deps
        run: pip install -r engine/ci/requirements.txt

      - name: Run QA AI triage
        env:
          QA_LLM_PROVIDER: anthropic
          ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        run: |
          python engine/ci/qa-orchestrator.py \
            --test-results test-output/junit.xml \
            --coverage test-output/coverage.xml \
            --output qa-output/

      - name: Upload QA summary
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: qa-report
          path: qa-output/
```

## Example: GitLab CI

```yaml
qa-triage:
  stage: test
  script:
    - pytest --junitxml=test-output/junit.xml
    - pip install -r engine/ci/requirements.txt
    - python engine/ci/qa-orchestrator.py
        --test-results test-output/junit.xml
        --output qa-output/
  variables:
    QA_LLM_PROVIDER: openai
    OPENAI_API_KEY: $OPENAI_API_KEY
  artifacts:
    paths:
      - qa-output/
    when: always
```

## Example: Generic (any CI)

```bash
# After test execution:
export QA_LLM_PROVIDER=anthropic
export ANTHROPIC_API_KEY=sk-ant-...

pip install -r engine/ci/requirements.txt
python engine/ci/qa-orchestrator.py \
  --test-results ./junit.xml \
  --output ./qa-output/

# Exit code determines CI pass/fail:
echo "Exit code: $?"
```

## Design principles

- **Reads prompts from the repo** — no hardcoded prompt text; updates to QA-GenDD prompts automatically flow to CI
- **AI drafts, humans decide** — outputs `defects.json` for human review or downstream import; does not auto-create Jira tickets
- **Confidence filtering** — only high/medium confidence findings become defect drafts; low-confidence items are flagged for human review
- **Does not require Cursor** — runs as a standalone Python script with LLM API access

## Related documents

- [QA Workflows](../../.cursor/rules/workflows.md) — Canonical step tables
- [SDLC Triggers](../../.cursor/rules/sdlc-triggers.md) — T5 (CI/CD phase) describes this orchestrator
- [Manual QA Standards](../../.cursor/rules/manual-qa-standards.md) — Defect governance and structure
- [Release and Governance](../../.cursor/rules/release-and-governance.md) — Release readiness rules

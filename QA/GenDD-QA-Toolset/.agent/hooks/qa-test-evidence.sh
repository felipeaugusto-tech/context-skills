#!/bin/bash
# SDLC Trigger: Post Tool Use (Shell) — trigger evidence review
# Maps to: T4 (Testing), T5 (CI/CD)
# Fires after Shell tool completes; checks if a test command was run.

input=$(cat)

command=$(echo "$input" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/"command"[[:space:]]*:[[:space:]]*"//;s/"$//')

is_test=false
case "$command" in
  *pytest*|*jest*|*vitest*|*"go test"*|*"dotnet test"*|*playwright*|*cypress*)
    is_test=true
    ;;
esac

if [ "$is_test" = false ]; then
  echo '{}'
  exit 0
fi

tool_output=$(echo "$input" | grep -o '"tool_output"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/"tool_output"[[:space:]]*:[[:space:]]*"//;s/"$//')

exit_code="unknown"
case "$tool_output" in
  *exitCode*|*exit_code*)
    extracted=$(echo "$tool_output" | grep -o '"exitCode"[[:space:]]*:[[:space:]]*[0-9]*' | head -1 | grep -o '[0-9]*$')
    if [ -z "$extracted" ]; then
      extracted=$(echo "$tool_output" | grep -o '"exit_code"[[:space:]]*:[[:space:]]*[0-9]*' | head -1 | grep -o '[0-9]*$')
    fi
    if [ -n "$extracted" ]; then
      exit_code="$extracted"
    fi
    ;;
esac

if [ "$exit_code" = "0" ]; then
  cat <<'EOF'
{
  "additional_context": "[SDLC Trigger T4/T5 — Evidence Review (Tests Passed)]\n\nTest execution completed successfully. Per the QA evidence model:\n\n1. Confirm the results count as strong evidence (deterministic pass with full output).\n2. Check coverage: did the tests cover the critical paths for this change?\n3. Consider whether any scenarios are missing per the prioritization order: critical path > failure paths > security > data integrity > integrations > NFRs.\n4. If this was a CI run, note the pipeline status for the release readiness trail.\n5. Tech debt checkpoint: did anything observed while writing or running these tests look like a shortcut, gap, or drift worth registering (fragile fixture, accepted-for-now edge case, duplicated standards prose, etc.)? If so, log it via knowledge/templates/tech-debt-template.md — register it, do not fix it now. Do not let it go unlogged just because tests passed.\n\nUse engine/prompts/11-evidence.md to formally assess the evidence if needed."
}
EOF
else
  cat <<'EOF'
{
  "additional_context": "[SDLC Trigger T4/T5 — Evidence Review (Tests Failed)]\n\nTest execution completed with failures. Per .cursor/rules/core-principles.md (principle 9):\n\n1. Assess whether failures are product bugs, test bugs, environment issues, or flake.\n2. For real failures: use engine/prompts/09-defects.md to draft structured defect reports.\n3. For ambiguous or flaky failures: route to manual verification — do NOT create defects directly.\n4. For each finding, assign confidence: high (clearly reproducible), medium (likely real, needs review), low (uncertain).\n5. Use engine/prompts/10-triage.md if there are multiple failures to categorize.\n6. Tech debt checkpoint: if the failure investigation surfaces something that is not itself the defect — a shortcut, gap, or drift you're choosing not to fix right now — log it via knowledge/templates/tech-debt-template.md instead of letting it disappear once the real defect is filed.\n\nHuman review is required before any finding becomes a tracked defect."
}
EOF
fi
exit 0

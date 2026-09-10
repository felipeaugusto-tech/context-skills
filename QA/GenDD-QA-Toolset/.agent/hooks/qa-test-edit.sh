#!/bin/bash
# SDLC Trigger: Post Tool Use (Write) — validate test structure
# Maps to: T3 (Development), T4 (Testing)
# Fires after Write tool completes; checks if the written file is a test file.

input=$(cat)

filepath=$(echo "$input" | grep -o '"path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/"path"[[:space:]]*:[[:space:]]*"//;s/"$//')

if [ -z "$filepath" ]; then
  echo '{}'
  exit 0
fi

basename_lower=$(basename "$filepath" | tr '[:upper:]' '[:lower:]')

is_test=false
case "$basename_lower" in
  *_test.*|*test_*|*.test.*|*.spec.*|test_*)
    is_test=true
    ;;
esac

if [ "$is_test" = true ]; then
  cat <<'EOF'
{
  "additional_context": "[SDLC Trigger T3/T4 — Test Structure Reminder]\n\nA test file was just edited. Per .cursor/rules/manual-qa-standards.md (Required Test Case Structure), every test case must include:\n- Title: communicates the behavior being verified\n- Purpose: why this test exists and what risk/requirement it covers\n- Preconditions: setup, data state, environment assumptions\n- Steps: numbered actions to execute\n- Expected result: observable outcome that constitutes a pass\n\nOptional: risk level (T0–T3), automation candidate flag, notes.\n\nAlso ensure:\n- Test names communicate intent (AAA pattern: Arrange-Act-Assert)\n- No shared mutable state or order dependency\n- Mocking only at boundaries (external APIs, DB, file system)\n- Required scenarios: happy path, invalid input, not found, plus auth/security when applicable"
}
EOF
else
  echo '{}'
fi
exit 0

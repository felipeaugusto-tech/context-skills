#!/bin/bash
# SDLC Trigger: Post Tool Use (Write) — trigger story update check
# Maps to: T8 (Iteration)
# Fires after Write tool completes; checks if the written file is a requirement/story file.

input=$(cat)

filepath=$(echo "$input" | grep -o '"path"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/"path"[[:space:]]*:[[:space:]]*"//;s/"$//')

if [ -z "$filepath" ]; then
  echo '{}'
  exit 0
fi

filepath_lower=$(echo "$filepath" | tr '[:upper:]' '[:lower:]')

is_story=false
case "$filepath_lower" in
  *requirement*|*stories*|*story*|*acceptance*|*criteria*|*user-stor*|*feature-spec*|*intent*|*prd*|*epic*|*\.feature|*specs*|*/spec/*)
    is_story=true
    ;;
esac

if [ "$is_story" = true ]; then
  cat <<'EOF'
{
  "additional_context": "[SDLC Trigger T8 — Story Update Loop Triggered]\n\nA requirement, story, or acceptance criteria file was just edited. Per .cursor/rules/risk-and-confidence.md (Story Update Loop), the following must be followed:\n\n1. Re-check intent and context against the updated story.\n2. Re-enter the workflow at context recovery (brownfield) or validation (greenfield).\n3. Update affected test scenarios and acceptance criteria.\n4. Update or regenerate affected tests.\n5. Re-run the impacted test suites.\n6. Review evidence from the new execution.\n7. Update or close defects that no longer apply.\n\nDo NOT test using outdated assumptions. Use engine/prompts/04-story-update.md with both original and updated context."
}
EOF
else
  echo '{}'
fi
exit 0

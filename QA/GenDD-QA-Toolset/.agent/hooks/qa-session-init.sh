#!/bin/bash
# SDLC Trigger: Session Start — inject QA context
# Points the agent at qa-planner.md which handles all routing.

cat > /dev/null

cat <<'EOF'
{
  "additional_context": "You are operating under the HatchWorks QA Operating Model.\n\nLoad .cursor/rules/qa-planner.md for the prompt routing table, verification checklists, and anti-patterns.\n\nAlways use prompts from engine/prompts/ rather than generating freeform QA outputs.\nAlways run verification checklists after generating any QA output."
}
EOF
exit 0

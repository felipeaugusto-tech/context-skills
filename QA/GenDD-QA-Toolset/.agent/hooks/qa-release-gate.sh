#!/bin/bash
# SDLC Trigger: Before Shell Execution — release readiness gate
# Maps to: T6 (Release)
# Fires before deploy/release/publish commands.

input=$(cat)

command=$(echo "$input" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | head -1 | sed 's/"command"[[:space:]]*:[[:space:]]*"//;s/"$//')

cat <<EOF
{
  "permission": "ask",
  "user_message": "Release gate: '${command}' appears to be a deployment or release action. Per the HatchWorks QA Operating Model, release readiness must be assessed before proceeding.\n\nHave you completed the release readiness checklist?\n- Risk coverage: all Tier 0 and Tier 1 areas tested with evidence?\n- Open defects: any unresolved Critical or High defects?\n- Automated results: do suites pass?\n- Manual coverage: exploratory findings documented?\n- Stakeholder validation: key workflows reviewed?\n\nUse engine/prompts/12-release.md to assess release readiness if not yet done.",
  "agent_message": "A QA release gate trigger has been activated for the command '${command}'. The user should confirm release readiness has been assessed per .cursor/rules/release-and-governance.md before this deployment or release command proceeds."
}
EOF
exit 0

# Story Update Loop

## When to Use

Use this when a story or feature has changed and QA coverage needs to be refreshed. This aligns with the story update loop defined in `.cursor/rules/workflows.md` (re-enter at Step 2).

## Prompt

> **Prerequisite:** `.cursor/rules/core-principles.md` must be loaded before using this prompt.

A story or feature has changed. Help me update QA coverage.

Please produce:
1. Updated intent summary
2. What changed (delta between original and updated)
3. What existing scenarios are still valid
4. What scenarios must be updated
5. New risks introduced by the change
6. Automation updates needed
7. Manual validation updates needed
8. Evidence needed for revalidation
9. Any defects likely to be impacted (closed, updated, or new)

Original context:
[PASTE ORIGINAL STORY OR FEATURE]

Updated context:
[PASTE NEW STORY OR CHANGES]

Keep the output simple and focused on what needs to change. Use confidence labels for any inferred items.

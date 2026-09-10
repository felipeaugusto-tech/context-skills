# QA operator quick index

Use this page to jump into the methodology without reading the full README.

## What to do

1. Define intent and risk for the change.
2. Run the right **prompt** from `engine/prompts/` (never freeform QA blobs).
3. Validate outputs using the checklists in `.agent/rules/qa-planner.md`.

## Where things live

| Need | Path |
|------|------|
| Routing, checklists, anti-patterns | [.agent/rules/qa-planner.md](.agent/rules/qa-planner.md) |
| Foundation rules | [.agent/rules/core-principles.md](.agent/rules/core-principles.md) |
| Prompt library (execution) | [engine/prompts/](engine/prompts/) |
| Stack + CI profiles | [knowledge/stacks/](knowledge/stacks/) |
| Output templates | [knowledge/templates/](knowledge/templates/) |
| CI orchestrator (no IDE) | [engine/ci/README.md](engine/ci/README.md) |
| Onboarding and walkthroughs | [training/getting-started.md](training/getting-started.md) |

## Full map

See [README.md](README.md) for architecture, pipelines, connectors, and migration notes from the legacy `main` layout.

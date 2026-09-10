# Project Context — TEMPLATE (fill in per project)

> **This file is the project pack.** The `SKILL.md` engine is generic and never
> hardcodes a client, repo, or tool — every project-specific fact lives here.
> To onboard a new project, copy this template and replace the bracketed
> placeholders. Delete sections that genuinely don't apply, but don't leave stale
> placeholders: an unfilled `[...]` reads as a real value and misleads the engine.
>
> If this file is left as a template (placeholders unfilled), the skill will run
> in **generic mode** — it works, but it will flag every place a project fact was
> expected and will not invent one. Filling this in is what makes the output
> project-aware.
>
> **Project:** [Project / client / product name]
> **Repo(s):** [repo or repos in scope — or "N/A"]
> **Context version:** [v1 — date]
> **Maintainer:** [name / team]

---

## 1. Environment & tooling

Defines the QA stack and the hard constraints. Drives the per-case **Suggested
Layer** hint and the export/push options in Step 5.

**Where the skill runs vs. where tests execute:** [Describe the split. Does the
environment running this skill have live connectivity to the test-management
tool, or only to Jira/Confluence? Be explicit — the engine defaults to assuming a
push path is *unavailable* until this section confirms one.]

**QA stack — name the tools for each layer (leave blank if none):**

| Role | Tool | Notes |
|---|---|---|
| Component / unit layer | [e.g. Jest + React Testing Library / none] | Used for the "Component" Suggested Layer hint |
| E2E layer | [e.g. Playwright / Cypress / Cucumber] | Is it BDD/Gherkin-native? [yes/no] — drives Gherkin export |
| Results / reporting | [e.g. Allure / built-in] | Where automated run results land |
| Test-case management | [e.g. Zephyr Scale / TestRail / Xray / none] | The manual case repository |

**Test-management push path (Step 5 Option D):** [Is there a *genuine*
connector- or token-backed path to the test-case-management tool named above?
State it explicitly. "Jira is connected" is NOT a push path to a separate tool
like Zephyr/TestRail/Xray. If there's no real path, say "none — offer
import-ready file export only."]

**Other critical constraints:** [environment access, VPN, data-privacy limits,
regions, feature-flag system, anything that changes how a case is written or run.]

---

## 2. Feature taxonomy & scope

Every generated case anchors to a Feature ID here (Hard Rule 10). Drives Step 1
feature mapping and in/out-of-scope rules.

| Feature ID | Feature name | In scope? | Notes / owner |
|---|---|---|---|
| [F1] | [name] | [in / out / conditional / at-risk] | [notes] |
| [F2] | [name] | [in / out / conditional / at-risk] | [notes] |

**In/out-of-scope rules:**
- Out-of-scope item → the engine stops and surfaces it (Hard Rule 7).
- Conditional / at-risk feature → proceed only with **all AC flagged as
  assumptions**.
- No clear mapping → the engine asks rather than guessing.

---

## 3. System / brownfield reference

If the product is an existing (brownfield) system, describe current behavior so
the engine can run the Step 2 delta check and generate current→target cases.
Leave a clear "greenfield — no existing behavior" note if that's the case.

- **System type:** [greenfield / brownfield]
- **Current behavior of relevant flows:** [Describe the areas stories will touch,
  as they behave *today*. This is what AC gets diffed against. Cite source docs.]
- **Known areas where the system contradicts common assumptions:** [...]

> If current behavior for a touched area is unknown, the engine flags it as an
> assumption — it never assumes greenfield on a brownfield system (Hard Rule 6).

---

## 4. Confirmed product decisions & open contradictions

**Confirmed decisions** (cite these; don't re-ask the user):

| # | Decision | Source | Date |
|---|---|---|---|
| [D1] | [what was decided] | [link/ref] | [date] |

**Open contradictions** (the program-level, cross-story contradiction log). The
engine **parameterizes/flags** cases touching these and routes to the owner — it
never resolves a logged contradiction itself (Hard Rule 12).

| # | Contradiction | Areas/features affected | Owner | Status |
|---|---|---|---|---|
| [C1] | [what conflicts with what] | [F#] | [name] | open |

---

## 5. Project-specific readiness flags (auto-raise table)

Step 2 raises a warning whenever a story touches one of these areas. Surface
every applicable flag; never silently resolve one.

| Flag | Trigger condition | What it warns |
|---|---|---|
| [e.g. UNDEFINED_CONTRACT] | Story touches [integration X] | Success/failure response contract not yet defined |
| [e.g. OPEN_CONTRADICTION] | Story touches [F#] with open contradiction C# | Sign-off blocked until C# resolved |
| [e.g. SCOPE_OWNERSHIP] | Story spans [area] | Ownership/scope boundary unconfirmed |

---

## 6. Personas & test-data fixtures

Scenario fuel for Step 3. The engine uses these and does **not** invent
applicants, accounts, IDs, or flag states (Hard Rule 8). If a needed value isn't
here, it flags it rather than fabricating.

**Personas:**

| Persona | Role / attributes | Use for |
|---|---|---|
| [name] | [role, permissions, cohort] | [scenarios] |

**Standard fixtures:**

| Fixture | Value(s) | Notes |
|---|---|---|
| [e.g. valid test account] | [id / email / state] | [environment] |
| [e.g. cohort/variant flags] | [values] | [when each applies] |

**Cohorts / variants:** [List the cohorts or variants whose behavior can differ,
so Step 3 generates the right variations.]

**Resume / re-entry security rules:** [If any flow is resumable, state the
project's rules for re-entry — token TTL, single-session binding, what must be
re-verified. Drives mandatory resume coverage, Hard Rule 11.]

---

## 7. Maintenance triggers

Update this file (not `SKILL.md`) when any of these fire:

- New brownfield analysis or a change in current system behavior.
- Requirements finalized or a previously open contradiction resolved.
- Tooling change (new test-management tool, new E2E framework, new push path).
- A new third-party integration or a newly defined integration contract.
- New personas, cohorts/variants, or test-data fixtures.
- Feature taxonomy or scope changes.

Bump the **Context version** at the top when you update, so sessions can tell
which pack they ran against.

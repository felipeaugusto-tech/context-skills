---
name: test-automation-implementer
description: >-
  Turn GenDD's "Automate Now" decisions (engine/prompts/07-automation.md
  output, e.g. docs/automation-assessment-*.md) plus their linked test cases
  (engine/prompts/06-testcases.md output, e.g. docs/test-cases-*.md) into
  real, executable test code, written into the actual repo/module the source
  lives in, using that codebase's real test stack and versions — not an
  assumed or preferred one. Use it whenever someone asks to "automate these
  test cases," "write the unit tests for TC-...," "implement the automation
  assessment," "turn this into real tests," or hands over a test-cases/
  automation-assessment doc and a repo path. Do NOT use this to decide what
  should be automated (that's engine/prompts/07-automation.md), to generate
  the test cases themselves (use qa-test-case-writer /
  engine/prompts/06-testcases.md), to find untested code (use
  test-gap-analyzer), or to write manual/exploratory checklists (use
  engine/prompts/08-manual.md).
---

# Test Automation Implementer

Take GenDD's automation decisions from paper to a running test suite. The
failure mode to design against is the plausible-looking test file: it
compiles-in-appearance, references the right TC-IDs, sits in a repo that
*looks* like the automation project — and never actually runs, or runs
without ever reaching the branch it claims to guard, because it was written
against the wrong repo, a mocking library that can't do what the test
assumes, or a method that isn't reachable from a test at all.

Four principles follow, each earned the hard way:

- **The path you were handed may not be the path this case belongs in.** A
  repo named like "the automation project" is very often an E2E/regression
  framework with no access to the internal classes named in a Unit-layer
  test case at all — but that same framework may be exactly the right,
  necessary home for a different case the assessment classified as E2E/UI/
  API. Verify the target *for this case's layer* before writing a single
  test — don't default to "whichever repo I was pointed at" for everything.
- **A dedicated E2E/automation framework repo needs the same validation as
  a source repo, not a pass.** Finding a repo that merely looks like "the
  automation project" is not the same as confirming it can reach the
  screen/endpoint a specific case needs, has the environment/credentials
  the case requires, and will actually execute the new test once written.
- **The installed mocking/test library — with its actual version — decides
  what's testable, not the test case's wording.** "Mock the null return"
  assumes a capability that may not exist in this codebase's Mockito/sinon/
  unittest.mock version. Check before designing, not after writing.
- **A test that can't reach the branch it names is worse than no test.** It
  reads as coverage and protects nothing. If a real blocker exists, surface
  it and ask — never quietly write something adjacent that passes instead.

## Step 0 — Load the inputs

Read, in this order:

1. **The automation assessment** (`docs/automation-assessment-*.md` or
   equivalent 07-automation.md output). This is the authority on *what* to
   automate and at *what layer* (Unit / Integration / API / UI). Take only
   items classified **Automate Now**. Route `Hybrid` items' manual portion
   and any `Manual`/`Needs Clarification` items to
   `engine/prompts/08-manual.md` instead — don't silently absorb them here.
2. **The linked test cases** (`docs/test-cases-*.md`, TC-IDs referenced by
   the assessment). Each TC gives you: purpose, preconditions, steps,
   expected result, and — critically — its **Negative/Failure Conditions**
   section, which often documents that a case is *expected to fail* against
   current code (a fail-first regression/gap-locking test). Preserve that
   intent; do not flatten it into a normal passing assertion.

If no automation assessment exists yet, say so and offer to run
`engine/prompts/07-automation.md` first — don't infer automation
classification yourself from the test cases' "Automation Candidate: Yes"
flag alone; that flag says *should this be automated eventually*, not *is it
safe to write right now at this layer*.

## Step 1 — Find the correct target repo for *this case's layer*

A codebase in this space typically has (at least) two disjoint homes for
tests, and picking the wrong one is the single most common way this skill
produces dead-on-arrival output. Branch on the layer the automation
assessment assigned:

- **Unit / Integration (component-level)** → the production source repo/
  module — where the classes/functions under test actually compile.
- **API / UI / E2E** → a dedicated automation framework repo (often named
  "automation," "*-af," "*-e2e," "*-regression," or similar) that drives the
  running application from outside and has **no compile-time access** to
  its internal classes.

Never assume either is the target just because it's the repo the user
handed over, or because it's the only one you were pointed at. Validate
whichever one this case actually needs — including the one you weren't
handed, if the assessment's layer calls for it and the user hasn't
mentioned it. If a project appears to have only one of the two but the
assessment includes cases needing the other, say so and ask where that
layer's tests should go before writing anything for those cases.

### 1a — Unit / Integration target: confirm the source is actually there

1. Grep for the actual symbols the test cases reference (class names,
   method names, component names) — not just in the path given, but across
   every plausible repo/module in the workspace.
2. If the given path doesn't contain them, **check for nesting** before
   concluding they're missing — a monorepo checkout frequently has the real
   module one level down (`repo/repo/module/...`), or split across sibling
   directories with similar names.
3. Read the candidate repo's manifest (`pom.xml`, `package.json`,
   `build.xml`, `go.mod`, …) and its README *before* writing anything, and
   confirm it is genuinely the production source (compiles the classes
   under test), not the E2E framework from 1b misidentified.
4. **If the given path is the wrong one**, stop and tell the user what you
   found (with evidence: files searched, what's actually in each candidate
   location) and ask them to confirm the real target. Do not silently
   redirect and do not write non-compiling tests into the handed-over path
   to "honor" the original ask.

### 1b — API / UI / E2E target: confirm the automation framework repo is set up for this

An E2E-classified case cannot land in the production source repo, and it
cannot land in an arbitrary "automation" repo without checking that the
repo is actually wired for the kind of case at hand (API vs. browser UI,
which environment/suite, which auth mode). Before writing anything:

1. **Identify the repo.** If the user hasn't named one, search the
   workspace for a framework whose manifest/README describes E2E,
   regression, canary, or smoke automation for the application under test
   (Selenium/Selenide/Playwright/Cypress/RestAssured + TestNG/JUnit/
   pytest are common signatures). Read its README for what it's *for* and
   what it explicitly is not (e.g. "canary and regression testing... not a
   place for internal unit tests").
2. **Confirm it can reach what the case needs.** For a UI case: does a page
   object / component locator already exist for the screen involved, or
   does one need to be added? For an API case: does an existing endpoint
   constants file / client wrapper already define the endpoint, or does
   that need adding? Don't invent a fresh ad hoc HTTP call or raw selector
   when the framework has an established pattern for this — Step 2b covers
   finding that pattern.
3. **Confirm environment and auth prerequisites.** E2E tests usually need a
   live (or test) environment, credentials/config, and possibly test-data
   seeding that unit tests don't. Check for a `BaseTest`/setup class,
   `.env`/config example file, or environment README section that states
   what's required. If a prerequisite is undocumented or you can't confirm
   it's available in the execution environment, say so explicitly rather
   than assuming the test will actually run somewhere.
4. **Confirm how new tests get wired into execution**, not just how they
   compile: suite XML files, TestNG/pytest `groups`/`markers`, a CI job
   filter, or a tag convention (e.g. `smoke`, `regression`, `canary`). A
   new E2E test that isn't added to the right suite/group is invisible to
   whatever actually runs it, exactly like an orphaned unit test the build
   glob never picks up. Ask which suite/group this case belongs in if it
   isn't obvious from the assessment's priority/risk tier.
5. **If this repo turns out not to be the right target** — it's actually a
   unit-test-only project, or it's set up for a different application/
   service than the one in scope — stop and say so, the same as 1a's
   mismatch handling. Do not write UI/API automation into a repo that has
   no path to actually execute it.

## Step 2 — Learn the existing conventions of the confirmed target; don't import a foreign stack

Once the right repo (from 1a or 1b) is confirmed, read its **actual**
conventions before writing anything new. What to read differs by target:

### 2a — Unit / Integration target

- Find the 2–3 existing test files nearest to the code under test (same
  package/directory, or the closest analogous one if this is the module's
  first test). Read them for: test framework (+ major version), mocking/
  stubbing library (+ **exact version** — this gates what's possible),
  assertion style, naming convention, and where test files live relative to
  source (mirrored package path? flat `__tests__` folder? colocated?).
- Confirm the **real dependency version**, not the newest API you know of.
  Check the lockfile/manifest, or the actual jar/package present, for the
  mocking library. An old version (e.g. Mockito 1.x without
  `mockConstruction`, no PowerMock present) forecloses whole classes of test
  that a newer version would make trivial — this changes what's achievable
  in Step 3, not just how you'd write it.
- Confirm how the build actually **discovers** tests (a glob pattern in an
  Ant target, a Maven Surefire default, a Jest/pytest config) so new files
  land somewhere that actually runs.
- If this module has **zero existing tests**, say so explicitly and use the
  closest sibling module's conventions as the pattern, flagging that choice.

### 2b — API / UI / E2E target

- Find the 2–3 existing test files closest in kind to the case at hand (an
  existing API test if writing an API case, a UI regression test in the
  same feature area for a UI case). Read them for: base class/fixture setup
  (`BaseTest` or equivalent), how requests/pages are built (a shared
  `APIUtils`/client wrapper, or page-object classes — not raw framework
  calls scattered per test), assertion style, and any project-mandated
  metadata annotation (e.g. a TestRail-ID tag linking the automated test
  back to its manual case).
- Confirm the project's **E2E selector and waiting rules** if this repo's
  house standards define them (see `automation-qa-standards.md`'s E2E
  section in this project: stable `data-testid`-style selectors only, no
  text/CSS-class/XPath selectors; explicit waits on a condition/response,
  never a fixed sleep). Match them exactly — these rules exist because
  violating them is *the* standard cause of E2E flakiness.
- Confirm test grouping/tagging conventions (`groups`, `markers`, suite XML
  membership) so Step 4's new test is discoverable by the run configuration
  that's supposed to pick it up.
- If this is the framework's **first test for this feature area**, say so
  and follow the closest analogous feature area's structure, flagging the
  choice.

Never introduce a new test framework, assertion library, mocking library,
or selector strategy "because it's better" — match what the confirmed
target already uses, exactly as it exists today.

## Step 3 — Map each case to a concrete unit, and surface blockers before writing

For every TC-ID taken from Step 0:

1. Read the actual source method(s) it targets. Confirm real signatures,
   field names, and control flow — test cases are sometimes written against
   an assumed contract that doesn't match the code precisely; know exactly
   where the assumption and the reality diverge before asserting anything.
2. Identify whether the method under test is reachable from a test at all:
   - **Private with no seam**, and its logic can't be exercised through a
     public entry point without dragging in unrelated, unmockable
     dependencies.
   - **Collaborators constructed inline** (`new Thing()`) rather than
     injected, combined with a mocking library too old to intercept
     construction (no `mockConstruction`, no PowerMock) — the mock can never
     be substituted as the code stands.
   - **Missing test infrastructure** the assessment already flagged as a
     prerequisite (a rendering harness, a fixture builder, a test database) —
     this is an Integration-layer blocker, not something to work around at
     the Unit layer.
   - **Live third-party/network calls** with no double available.
   - **(E2E/UI/API target only)** No page object/locator or endpoint
     definition exists yet for the screen/endpoint involved; no test
     environment or credentials are confirmed reachable; the flow requires
     state (an account, an order, a prior step) that has no seeding
     mechanism in this framework; or the case depends on a third-party
     vendor flow (e.g. a hosted identity/payment provider) that can't be
     driven or stubbed from this repo at all.
3. **When a real blocker exists, stop and ask** — don't quietly write
   something adjacent that passes instead. Lay out concrete options, e.g.:
   - add the smallest possible testability seam (one factory method, one
     visibility widening) so a test subclass can substitute a mock,
   - skip this case for now and log it as a follow-up (infrastructure or
     refactor ticket), or
   - accept partial coverage that exercises only the reachable branches,
     naming exactly which assertion stays unverifiable and why.

   Get an explicit choice before proceeding. If a seam is approved, keep it
   **minimal and behavior-preserving** — it must only add a substitution
   point, never change what the method does. Re-read the diff of any
   production file touched this way before moving on.

## Step 4 — Write the tests

- **One test class per source class/component**, mirroring the source's
  package/module path in the test tree — not one large mixed-purpose file.
- Name test methods for scenario + expected result (e.g.
  `methodUnderTest_condition_expectedResult`), and comment which TC-ID(s)
  each method satisfies. This is the traceability mechanism — don't rely on
  a separate mapping doc that will drift.
- **Fail-first cases stay fail-first.** When a TC-ID's own
  Negative/Failure-Conditions section says the case is expected to fail
  against current code, write the assertion for the *correct/target*
  behavior and say so in a comment — a passing suite obtained by asserting
  the current bug instead defeats the entire point of a regression-locking
  test.
- **Don't write speculative tests against infrastructure that isn't there
  yet.** If Step 0's assessment flagged an Integration-layer item as blocked
  on missing harness/fixtures, leave it out of this pass and report it as
  pending, rather than authoring a test that can't run.
- Match the layer the assessment assigned. Don't promote a Unit-classified
  case to a heavier integration/E2E test (slower, more brittle, contradicts
  the assessment's own reasoning) or the reverse (an Integration case forced
  into a Unit test by mocking away the exact thing it was meant to verify).
- **(E2E/UI/API target only)** Reuse the framework's existing page-object/
  client-wrapper pattern from Step 2b rather than inlining raw selectors or
  HTTP calls; follow its selector/waiting rules exactly; add any required
  TestRail-ID or equivalent traceability annotation; and **wire the new
  test into the run configuration** the case's priority/risk tier implies
  (smoke, canary, regression suite/group) — a test that compiles but was
  never added to a suite/group is functionally the same as not writing it.

## Step 5 — Verify before handing off

- Attempt to actually build/run what you wrote, using the module's own
  tooling (`ant test`, `mvn test`, `npm test`, `pytest`, …), or a scoped
  compiler check against just the touched files if the full build isn't
  runnable here.
- If no toolchain is available in the current environment, **say so
  explicitly** — never report "tests pass" or "verified" without having
  actually run something. A careful manual trace of signatures and imports
  is a reasonable substitute to mention, but label it as exactly that, not
  as verification.
- Cross-check every new or changed production signature (seam methods,
  widened visibility) against every call site the new tests make — a
  mismatch here is the most common self-inflicted compile failure.
- **(E2E/UI/API target only)** Compiling is not the same as running. State
  clearly whether the new test was actually executed against a live/test
  environment, or only compiled/statically checked — and if only the
  latter, name what environment/credentials would be needed to actually run
  it, per Step 1b's prerequisite check. Confirm the new test actually
  appears in the suite/group it was wired into (re-list the suite's
  contents or the tag filter, don't just trust the edit).

## Step 6 — Report

State plainly:

- **TC-ID → test file → test method**, for every case implemented.
- Which cases are **intentionally fail-first** (and why) — don't let these
  read as accidental failures.
- Which cases are **blocked**, with the specific reason and what decision is
  needed to unblock them.
- Which cases were **explicitly deferred** (e.g. Integration cases waiting
  on infrastructure the assessment already flagged) and why they weren't
  forced in.
- Any production file touched to add a testability seam, and confirmation
  it changes no behavior.
- What was and wasn't actually verified to run, and how.
- **Which target repo each case landed in** (production source vs. E2E
  automation framework) and why — this is easy to get wrong silently, so
  say it even when it seems obvious.
- **(E2E/UI/API cases)** which suite/group each new test was wired into,
  and any environment/credential prerequisite that couldn't be confirmed
  available in this session.

## Hard rules

1. Never write tests into a repo/module before confirming — by grepping for
   the actual symbols under test — that the code under test genuinely lives
   there.
2. Never assume a mocking/stubbing capability exists — confirm the installed
   library's actual version before designing a test around it.
3. Never invert or soften a fail-first test's assertion just to make the
   suite green. If a case is documented as expected to fail today, it stays
   asserting the target behavior.
4. Never write a test that cannot reach the branch/condition it claims to
   verify — report the blocker and get a decision instead of writing an
   adjacent test that merely passes.
5. Never introduce a new test framework, assertion library, or mocking
   library when the module already has one — match what exists.
6. Never make a production change beyond the minimum needed to unblock a
   specific, named test case, and never make one without the user's
   explicit go-ahead.
7. Never promote or demote a case's layer from what the automation
   assessment assigned without saying so and why.
8. Never claim a test suite passes, builds, or is verified without having
   actually run it (or explicitly saying you could not, and why).
9. Never silently absorb `Manual`/`Hybrid`/`Needs Clarification` items from
   the automation assessment — route them to `engine/prompts/08-manual.md`.
10. Always report TC-ID-to-test-method traceability; never leave which case
    is covered by which test implicit.
11. Never write an E2E/UI/API test into an automation framework repo before
    confirming that repo is actually set up to reach the screen/endpoint
    involved (page object or endpoint definition exists or is added,
    environment/auth prerequisites are known) — the same discipline Rule 1
    requires for unit tests applies here, not just "found *a* repo that
    looks like automation."
12. Never leave a newly written E2E/UI/API test unwired from the suite/
    group/tag that's supposed to execute it — a test not added to any run
    configuration is not "automated," regardless of whether it compiles.
13. Never treat "the test compiles" as "the test runs" for an E2E/UI/API
    case — state explicitly whether it was actually executed, and against
    what environment.

# Test Gap Method

1. The risk model
2. Weak-test taxonomy and remedies
3. What should exist, by concern
4. Choosing the layer
5. Effort sizing

---

## 1. The risk model

Risk is **likelihood of breaking × cost of it breaking**, and both halves have
evidence available in any git repository. The point of computing it is not
precision; it is defensibility. "This file scored high because it changed fourteen
times in six months, three of those were fix commits, eleven modules import it, and
nothing tests it" is an argument. "Payments feel under-tested" is a feeling.

### Signals for likelihood

| Signal | Where it comes from | Why it predicts breakage |
|---|---|---|
| **Change frequency** | `git log --oneline -- <file>` over a window | Code that changes often breaks often. The single best predictor available. |
| **Bug-fix churn** | commits touching the file whose message matches `fix`, `bug`, `hotfix`, `revert` | Past defects concentrate. A file with repeated fixes will produce more. |
| **Size and complexity** | line count as a proxy; cyclomatic complexity where a tool exists | More branches, more untested paths. |
| **Recency** | last modified date | Code changed last week is riskier than code untouched for two years. |
| **Author spread** | distinct authors touching the file | Many hands, less shared understanding of invariants. |

### Signals for cost

| Signal | Where it comes from | Why it predicts impact |
|---|---|---|
| **Fan-in** | count of modules importing it | A break propagates to every importer. |
| **On a critical flow** | the team's answer plus `context.md` | Auth, payments, data integrity, compliance. Trust is the expensive loss. |
| **Integration boundary** | architecture docs, HTTP and SDK clients | Failures here are the hardest to reproduce and the slowest to diagnose. |
| **Data mutation** | writes, migrations, deletes | Corruption may be unrecoverable; a rendering bug is not. |
| **Blast radius** | tenancy and permission code | One bug affecting all tenants is categorically different from one affecting one page. |

### Combining them

```
exposure   = 1.0 if no test maps to the file
             else (1 - covered_fraction) if coverage data exists
             else 0.4                      # a test exists, but its quality is unverified

likelihood = normalize(change_frequency) + 2 × normalize(bugfix_commits)
             + 0.5 × normalize(size)

cost       = normalize(fan_in) + critical_flow_weight + mutates_data_weight

risk       = exposure × (likelihood + cost)
```

Bug-fix churn is weighted double because it is the only signal that reflects defects
that actually happened rather than conditions that predict them.

The exposure floor of 0.4 for "a test exists but coverage is unknown" is deliberate:
existence is weak evidence of protection, and Step 2 of the skill exists because it
is sometimes no evidence at all. Never treat "has a test file" as covered.

Treat the score as a **sort order, not a measurement.** Report the underlying
signals next to it so anyone can disagree with the ranking on visible grounds.

---

## 2. Weak-test taxonomy and remedies

Every one of these passes CI and reports as coverage.

| Pattern | How to spot it | Remedy |
|---|---|---|
| **No assertions** | Test body with no `expect`, `assert`, `should`, or equivalent | Add the assertion the test's name implies — the name usually states the intent |
| **Mock-only assertions** | Only `expect(mockFn).toHaveBeenCalled()` | Assert the observable result. Call-count assertions verify wiring, not behavior |
| **Snapshot-only** | Body is just `toMatchSnapshot()` | Add explicit assertions for the two or three properties that actually matter |
| **Skipped** | `.skip`, `xit`, `xdescribe`, `@pytest.mark.skip`, `t.Skip()` | Fix or delete. A permanently skipped test is a lie in the file tree |
| **Focused** | `.only`, `fdescribe`, `fit` | Remove immediately — this silently disables sibling tests, so the suite is smaller than it looks |
| **Tautological** | `expect(true).toBe(true)`; asserting a value the test just assigned | Rewrite against the system's output, not the test's own setup |
| **Happy-path only** | No error, boundary, or denial case in the file | Add the failure branch — that is where the defect will be |
| **Over-mocked integration** | Integration test where every collaborator is a double | Use a real dependency or a contract test; otherwise it is a unit test wearing a costume |
| **Non-deterministic** | Real clocks, real network, random data, ordering assumptions | Inject time and randomness; a flaky test gets retried until green, which means it no longer gates |

**Assertion-free and focused tests deserve escalation** over most missing tests. A
missing test is a known unknown. A `.only` left in a committed file means the suite
has been running a fraction of itself, possibly for months.

---

## 3. What should exist, by concern

Heuristics, not a checklist to paste. Apply what the code actually does.

### Authorization and permissions

The highest-value and most consistently missing category, because positive tests
pass even when the check is gone.

- One **denial** test per role that must be refused, asserting the status code and
  that no side effect occurred.
- Escalation attempts: can a user modify the identifier to reach another's resource?
- Absent, expired, and malformed credentials as separate cases.
- Confirm that a denial leaves no partial write behind.

### Multi-tenancy

- Cross-tenant read returns the project's chosen response — often 404 rather than
  403, to avoid disclosing existence. Test the actual convention.
- Cross-tenant write is refused and persists nothing.
- List endpoints return only the caller's tenant, tested with data present in both.
- Any shared cache or index is tenant-scoped.

### Payments and money

- Declined, timeout, and duplicate-submission paths, each asserting the resulting
  system state rather than only the response.
- Idempotency: the same request twice charges once.
- Rounding and currency at boundaries.
- Refund and partial-refund arithmetic.
- Webhook handling: out-of-order delivery, replay, unknown event types.

### Integrations

- Timeout, unavailable, malformed response, and rate-limited, each asserting whether
  the primary flow degrades or fails — the decision itself is often undocumented,
  and the test is where it becomes explicit.
- Retry behavior, including that retries do not duplicate effects.
- A contract test wherever both sides are owned.
- Credential expiry, if the integration authenticates.

### Data sync and background jobs

- Partial failure mid-batch: what is committed, what is retried, no duplicates.
- Re-entry and resume from an interrupted run.
- Concurrent runs of the same job.
- Ordering assumptions, if any exist.

### Migrations and schema

- The rollback actually restores prior state with data intact.
- Backfill correctness on a representative row sample.
- Behavior of code deployed against both old and new schema, if the rollout is
  phased.

### Validation and input handling

- Boundary values, empty, null, and maximum length.
- The exact user-facing message for each rejection, since that is what a support
  ticket will quote.
- Injection-shaped input where the value reaches a query or a template.

---

## 4. Choosing the layer

| Layer | Use for | Avoid for |
|---|---|---|
| **Unit** | Branching logic, calculations, validation, permission decisions, error mapping | Anything whose value is in the wiring between components |
| **Integration** | Persistence, transactions, service boundaries, real error responses, tenancy scoping | Pure logic that a unit test covers faster |
| **Contract** | Boundaries between two owned services | Third parties you cannot coordinate with |
| **E2E** | A small number of critical journeys, end to end | Everything else |

Default toward the lowest layer that can actually observe the behavior. Each level
up costs more to write, more to run, and much more to maintain, and flakiness rises
with it — a flaky suite gets retried until green, at which point it has stopped
gating anything.

**A recommendation of many E2E tests is nearly always a mis-scoped analysis.** Three
to five journeys is a healthy number for most products.

---

## 5. Effort sizing

Sizes, with the basis stated. Invented hours become commitments.

| Size | Means | Typical case |
|---|---|---|
| **S** | Fits the existing harness; no new fixtures | Another case in an existing file; a denial test beside existing auth tests |
| **M** | Needs a fixture, a mock, or a new file, but the infrastructure exists | Integration test against an existing test database |
| **L** | Requires infrastructure that does not exist yet | First integration test in the repo; mocking a gateway with no sandbox |
| **XL** | Blocked on a decision or an external dependency | Needs a vendor sandbox account, or an undefined failure contract settled first |

**XL items are usually not test work.** They are a decision or a procurement task
wearing a test ticket, and calling that out is more useful than estimating it. When
several gaps are L for the same reason, the shared infrastructure is the real
recommendation — say so once rather than repeating the cost across five rows.

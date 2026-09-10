# TestRail Bridge — self-hosted MCP server

> **Purpose:** give agents in this repo authenticated read/write access to
> Accurate's TestRail instance, without installing third-party code.
> **Audience:** whoever sets this up and whoever reviews it. For the *agent-facing*
> usage rules see [`engine/connectors/testrail.md`](../../connectors/testrail.md).

---

## Why this exists

The QA engine can generate test cases, but until now it had no way to read the
existing suite or push anything back. `Context.md` §1 asks a direct question —
*"is there a genuine connector- or token-backed path to the test-case-management
tool?"* — and the honest answer was no.

The obvious fix, a community TestRail MCP server from npm or PyPI, was ruled out
on security grounds. That is a reasonable call: such a server runs on a developer
machine, is handed a credential that inherits **all** of that user's TestRail
permissions, and can write to every project that user can see. Auditing an
unfamiliar dependency tree to that standard is more work than writing the client.

So this is a first-party bridge, built to be reviewable:

| Property | Choice | Why |
|---|---|---|
| Dependencies | **None.** Python 3.10+ standard library only. | Nothing to audit but this directory. No supply chain, no transitive updates, no post-install scripts. |
| Protocol | Hand-rolled JSON-RPC 2.0 over stdio. | ~300 lines in `server.py`. Adding the MCP SDK would restore most of the dependency risk the decision was meant to avoid. |
| Transport | `urllib` with redirect and downgrade blocking. | Prevents the Basic Auth header being forwarded to another host. |
| Default posture | Read-only. | Write access is opt-in per project, never implicit. |
| Secrets | `.env`, gitignored, redacted from all output. | Never on a command line, never in a log, never in an agent transcript. |

Total surface: about 1,400 lines of Python across five files, plus a test suite
that runs with no credentials.

---

## Files

| File | Role |
|---|---|
| `config.py` | `.env` parsing, validation, the redaction registry. |
| `client.py` | HTTP transport: auth, retries, redirect blocking, pagination. |
| `guards.py` | Write authorisation. Resolves every write to a project and checks the allowlist. |
| `tools.py` | Tool schemas and handlers. |
| `server.py` | The JSON-RPC stdio loop. |
| `test_bridge.py` | Offline test suite. No network, no credentials. |
| `.env.example` | Annotated configuration template. |

---

## Setup

### 1. Confirm the API is enabled

An admin must have turned it on: **Administration → Site Settings → API →
Enable API**. Without it every request returns 401 no matter how good the
credential is, which reads exactly like a bad key.

### 2. Mint a credential

**My Settings → API Keys → Add Key.** It is displayed once.

The key inherits *your* permissions, and every write made through it is
attributed to you. For CI or anything shared, ask an admin for a dedicated
service account instead of sharing a personal key — otherwise the audit trail
says you made changes you did not make.

### 3. Configure

```bash
cd engine/mcp/testrail
cp .env.example .env
# edit .env
```

Confirm the file is ignored before you save a real key:

```bash
git check-ignore -v engine/mcp/testrail/.env    # must print a match
```

Minimum viable config:

```ini
TESTRAIL_URL=https://accurate.testrail.io
TESTRAIL_USER=you@accurate.com
TESTRAIL_API_KEY=...
TESTRAIL_MODE=read
```

### 4. Verify before wiring anything up

```bash
python3 server.py --probe        # auth check + visible projects + posture
python3 server.py --list-tools   # what the agent will actually see
python3 test_bridge.py           # offline suite, no credentials needed
```

`--probe` is the fastest way to tell a disabled API from a bad key from a VPN
problem; the error messages name the likely cause in each case. Debugging that
through an MCP client's log pane instead is unpleasant.

### 5. Register with your MCP client

**Claude Code / Cowork** — `.mcp.json` at the repo root:

```json
{
  "mcpServers": {
    "testrail": {
      "command": "python3",
      "args": ["engine/mcp/testrail/server.py"]
    }
  }
}
```

**Cursor** — `.cursor/mcp.json`, same shape. On Windows use `python` rather than
`python3`.

No credentials go in the MCP config. The server reads `.env` from its own
directory, which keeps the secret out of a file that is easy to commit by
accident.

---

## Enabling writes

Writes are off until three things are true. This is deliberately more friction
than a single flag, because TestRail has no undo and a bad bulk push is expensive
to unwind by hand.

```ini
TESTRAIL_MODE=write
TESTRAIL_ALLOWED_PROJECTS=12        # explicit ids, no wildcard
TESTRAIL_DRY_RUN=true               # keep this on for the first run
```

Restart the MCP client afterwards — the tool list is built at startup.

**The suggested sequence:**

1. `TESTRAIL_MODE=write` with `TESTRAIL_DRY_RUN=true`, allowlisting a **sandbox
   project**. Run a real push and read the echoed payloads. This is where field
   mapping mistakes surface, and they surface for free.
2. Same project, `TESTRAIL_DRY_RUN=false`. Inspect what actually landed in the
   TestRail UI.
3. Only then add the real project id.

### How the allowlist is enforced

TestRail's write endpoints do not take a project id — `add_case` takes a
`section_id`, `update_case` takes a `case_id` — and neither the request nor the
response carries one. Trusting a caller-supplied project id would make the
control meaningless, since an agent can simply get it wrong.

So the bridge resolves it, through the suite, which does carry `project_id`:

```
add_case(section_id)     -> get_section -> get_suite -> project_id -> check
update_case(case_id)     -> get_case    -> get_suite -> project_id -> check
add_result(run_id)       -> get_run                  -> project_id -> check
```

That costs up to two extra GETs per write, cached for the process lifetime. If
the chain cannot be completed, the write is **refused rather than allowed** — an
unresolvable target is treated as a failure of the control, not an exception to
it. `add_section` additionally resolves `parent_id`, because a child section
inherits its parent's suite and could otherwise land outside the named project.

### Deletes

Two independent controls, because deletion is the one operation with no recovery
path: `TESTRAIL_ALLOW_DELETE=true` (operator's decision, at startup) **and** the
exact string `DELETE PERMANENTLY` in the call's `confirm` argument (so a caller
cannot delete something while believing it was updating it). Without the env
flag, the tool is not registered at all.

---

## Security posture

**What this design protects against**

- *Wrong-project writes.* The allowlist, enforced after resolution rather than on
  a caller-supplied id.
- *Credential leaks into transcripts and logs.* Every secret is registered at
  load and scrubbed at the single point where text leaves the process — including
  stderr, and including the base64 Basic Auth blob, which is credential-
  equivalent. Redaction runs on the object *before* JSON encoding as well as on
  the encoded text, because `ensure_ascii` escaping would otherwise let a secret
  containing a non-ASCII character or a quote through in readable form.
- *Credential exfiltration via redirects.* `urllib` copies the `Authorization`
  header onto redirects, so a cross-host redirect or an HTTPS→HTTP downgrade is
  refused before it is followed.
- *Silent duplicate writes.* A 5xx or a dropped connection on a POST is
  ambiguous — TestRail may have applied the change and failed on the way back.
  These are **not retried**; the tool reports the outcome as unknown and tells
  the agent to verify rather than re-send. Only 429 is retried on a write, since
  a rate-limited request was refused before it was applied.
- *Context exhaustion.* Read tools project to compact shapes and cap output, and
  truncation is marked in-band so a cut payload is not parsed as complete.
- *Accidental capability.* Write tools are not registered in read mode, and the
  delete tool is not registered unless explicitly enabled.

**What it does not protect against, and you should know**

- **The credential's own permissions.** If the key can see 40 projects, every
  read tool can read all 40. The allowlist restricts *writes* only. Scope the
  TestRail account if reads need restricting.
- **A compromised developer machine.** `.env` sits on disk in plaintext, like
  every other local credential file. Rotate the key if the machine is suspect.
- **Prompt injection via TestRail content.** Case titles, steps and comments are
  attacker-influenceable if anyone untrusted can edit the suite, and they flow
  into the agent's context. The allowlist bounds the damage — an injected
  instruction cannot write outside allowlisted projects — but it does not stop
  the agent being *misled* about what it read.
- **Audit attribution.** Writes appear in TestRail as whoever owns the key. Use
  a service account if "who changed this?" needs a real answer.

### Session cookie mode

`TESTRAIL_SESSION_COOKIE` exists for instances where SSO is the only way in and
no API key can be minted. It works, but understand what you are accepting:

- The cookie expires, and a logout invalidates it immediately. Expect to refresh
  it, mid-task, more often than is comfortable.
- It is not a documented interface. TestRail may answer with an HTML login page
  instead of JSON at any point. The bridge detects that and says so rather than
  parsing garbage, but it cannot prevent it.
- A session cookie is generally *broader* than an API key — it is the same
  credential your browser session uses.

Treat it as a stopgap while a proper key or service account is requested, not a
destination. The `--probe` output always states which auth mode is in use.

---

## Testing

```bash
python3 test_bridge.py
```

~75 tests, no network and no credentials: everything runs against an injected
fake transport. The suite deliberately concentrates on **refusals** — a guardrail
that has never been observed to say no is not a guardrail — along with redaction,
retry and pagination behaviour, and the JSON-RPC handshake.

What it cannot cover: whether *this* instance's field names, required fields and
status ids are what you assumed. That needs `--probe` plus
`testrail_describe_schema` against the real instance, and it is why the connector
doc makes the schema call mandatory before any push.

---

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `401` on everything | API not enabled instance-wide, or `TESTRAIL_USER` is not the login email. |
| `non-JSON body` | An SSO/login interstitial: the request was not authenticated as an API call. In cookie mode, the cookie has expired. |
| `TESTRAIL_URL must be an absolute http(s) URL` (no value shown) | Likely `TESTRAIL_URL` and `TESTRAIL_API_KEY` are swapped. The value is withheld on purpose so a misplaced key is not printed. |
| `should be the instance root, not an API URL` | The URL includes `?/api/v2/`. Use just `https://host`. |
| `REFUSED BY POLICY … not in TESTRAIL_ALLOWED_PROJECTS` | Working as intended. Add the id deliberately if that project is really the target. |
| Write tools missing from the tool list | `TESTRAIL_MODE` is `read`, or the client was not restarted after the change. |
| `suite_id is required` | Multiple-suite project. Call `testrail_list_suites` first. |
| `WRITE OUTCOME UNKNOWN` | A write failed ambiguously and was not retried. Check TestRail before re-sending. |
| Client shows no tools at all | Something printed to stdout and corrupted the stream. Only `server.py`'s `_write` may write there. Check the client's stderr log. |

---

## Maintenance

- **Rotate the API key** on the same cadence as any other credential, and
  immediately if a machine holding a `.env` is compromised.
- **Re-run `testrail_describe_schema`** after any TestRail configuration change.
  A stale field map is the main way a push starts producing malformed cases.
- **Re-run `test_bridge.py`** after touching anything in this directory,
  especially `guards.py`.
- **Record the outcome in `Context.md` §1** — the push path, the allowlisted
  project ids, and the confirmed field mapping. Until that section says a push
  path exists, the case-writer skill will keep offering file export only, which
  is correct behaviour on its part.

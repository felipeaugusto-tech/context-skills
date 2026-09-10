# TestRail Bridge — Quickstart

Five steps to get the connector running. For the full picture (security posture,
write guardrails, troubleshooting), see `README.md` in this folder.

## 1. Turn on the TestRail API

Someone with TestRail admin access needs to enable it once:

**Administration → Site Settings → API → Enable API**

If this is off, every request fails with a 401 no matter how good your key is.

## 2. Get an API key

In TestRail: **My Settings → API Keys → Add Key**

Copy it immediately — TestRail only shows it once.

## 3. Configure the bridge

```bash
cd engine/mcp/testrail
cp .env.example .env
```

Open `.env` and fill in three lines:

```ini
TESTRAIL_URL=https://accurate.testrail.io
TESTRAIL_USER=you@accurate.com
TESTRAIL_API_KEY=paste-your-key-here
```

Leave everything else as-is for now — that leaves the bridge in read-only mode,
which is the right starting point.

## 4. Check the connection

```bash
python3 server.py --probe
```

You should see a list of the TestRail projects visible to your key. If you get
an error instead, it will tell you the likely cause (bad key, API not enabled,
wrong URL) — fix that before moving on.

## 5. Point your MCP client at it

Copy the block from `mcp-config.example.json` into your MCP config:

- **Claude Code / Cowork:** `.mcp.json` at the repo root
- **Cursor:** `.cursor/mcp.json`

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

(On Windows, use `python` instead of `python3`.)

Restart your MCP client. You're done — the agent can now read projects, suites,
sections, cases, and results from TestRail.

---

## Want the agent to write cases too?

By default the bridge only reads. To let it push cases, edit `.env`:

```ini
TESTRAIL_MODE=write
TESTRAIL_ALLOWED_PROJECTS=12        # your project's id — no wildcard allowed
TESTRAIL_DRY_RUN=true               # keep this on for your first test
```

Restart your MCP client again (tools are loaded at startup). With `DRY_RUN` on,
the agent can try a push and you'll see exactly what *would* be sent, without
anything actually reaching TestRail. Once that looks right, set
`TESTRAIL_DRY_RUN=false`.

Only the project id(s) you list in `TESTRAIL_ALLOWED_PROJECTS` can ever be
written to — a write aimed anywhere else is refused automatically.

---

## Something not working?

| Problem | Try this |
|---|---|
| `401` on the probe | Confirm the API is enabled (step 1), and that `TESTRAIL_USER` is your login email |
| MCP client shows no TestRail tools | Restart the client after editing `.env` or the config file |
| Agent says a write was "refused by policy" | The target project isn't in `TESTRAIL_ALLOWED_PROJECTS` — add it deliberately if it should be |

More detail in `README.md`.

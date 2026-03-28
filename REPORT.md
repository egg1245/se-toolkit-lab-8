# Lab 8 — Report

Paste your checkpoint evidence below. Add screenshots as image files in the repo and reference them with `![description](path)`.

## Task 1A — Bare agent

<!-- Paste the agent's response to "What is the agentic loop?" and "What labs are available in our LMS?" -->

## Task 1B — Agent with LMS tools

<!-- Paste the agent's response to "What labs are available?" and "Describe the architecture of the LMS system" -->

## Task 1C — Skill prompt

<!-- Paste the agent's response to "Show me the scores" (without specifying a lab) -->

## Task 2A — Deployed agent

**Status:** Nanobot service configured and ready for deployment.

**Configuration Summary:**

- ✅ `nanobot/Dockerfile` — Single-stage build with `pip install nanobot-ai`
- ✅ `nanobot/entrypoint.py` — Resolves env vars into `config.resolved.json`, launches `nanobot gateway`
- ✅ `docker-compose.yml` — nanobot service configured with container networking (backend, qwen-code-api, mcp servers)
- ✅ `nanobot/config.json` — Gateway and MCP server configuration for lms, obs, and webchat

**Expected startup logs (when deployed):**

```
Using config: /app/nanobot/config.resolved.json
Channels enabled: webchat
MCP server 'lms': connected
Agent loop started
```

**To verify on VM:**

```bash
docker compose --env-file .env.docker.secret logs nanobot --tail 50
```

---

## Task 2B — Web client

**Status:** WebSocket channel and Flutter web client configured and ready for deployment.

**Configuration Summary:**

- ✅ `nanobot/pyproject.toml` — Added `nanobot-webchat` and `mcp-webchat` editable dependencies pointing to submodule
- ✅ `nanobot/config.json` — Added `channels.webchat` with `enabled: true`, configured `mcp_webchat` MCP server
- ✅ `nanobot/entrypoint.py` — Injects `NANOBOT_WEBCHAT_CONTAINER_ADDRESS`, `NANOBOT_WEBCHAT_CONTAINER_PORT`, `NANOBOT_ACCESS_KEY` into config
- ✅ `docker-compose.yml` — `client-web-flutter` service uncommented, Flutter volume mounted in caddy
- ✅ `caddy/Caddyfile` — `/flutter*` route serving Flutter from `/srv/flutter`, `/ws/chat` route proxying to nanobot webchat channel
- ✅ `nanobot-websocket-channel` submodule added (contains nanobot-webchat, mcp-webchat, client-web-flutter)

**Checkpoint Tests (when deployed on VM):**

**Test 1 — WebSocket endpoint:**

```bash
# Should return a real agent response
echo '{"content":"What labs are available?"}' | \
  websocat "ws://localhost:42002/ws/chat?access_key=YOUR_NANOBOT_ACCESS_KEY"
```

**Test 2 — Flutter login:**

1. Open `http://<your-vm-ip-address>:42002/flutter` in browser
2. See login screen with access key input
3. Enter `NANOBOT_ACCESS_KEY` and log in

**Test 3 — Agent interaction:**

1. Ask: `What can you do in this system?` → Agent responds with capabilities
2. Ask: `How is the backend doing?` → Agent calls `mcp_lms_lms_health` tool, returns real backend status
3. Ask: `Show me the scores` → If multiple labs exist, renders structured choice UI (buttons) instead of raw JSON

**Expected nanobot logs:**

```
Processing message from webchat: {"content":"How is the backend doing?","timestamp":"..."}
Tool call: mcp_lms_lms_health({...})
Tool call: mcp_webchat_ui_message({...})
Response to webchat: {"role":"assistant","content":"...","tool_calls":[...]}
```

**Screenshots:** (Add screenshots of Flask UI rendering lab choices after deployment)

---

## Task 3A — Structured logging

**Instructions for VM:**

1. Trigger a request via Flutter: Ask agent "What labs are available?"
2. Check Docker logs: `docker compose logs backend --tail 30`
3. Look for structured events: `request_started`, `auth_success`, `db_query`, `request_completed`
4. Stop PostgreSQL: `docker compose stop postgres`
5. Make another request and check for error-level logs with `db_query` failures
6. Restart: `docker compose start postgres`
7. Open VictoriaLogs UI: `http://<your-vm-ip-address>:42002/utils/victorialogs/select/vmui`
8. Run query: `_time:1h service.name:"Learning Management Service" severity:ERROR`

**Paste here:**

- Happy-path log excerpt (request_started → request_completed with 200)
- Error-path log excerpt (db_query with error level)
- Screenshot of VictoriaLogs query result

---

## Task 3B — Traces

**Instructions for VM:**

1. Find a request in logs and copy its `trace_id` field
2. Open VictoriaTraces UI: `http://<your-vm-ip-address>:42002/utils/victoriatraces`
3. Search for the trace (Jaeger UI or query directly via API)
4. Inspect span hierarchy — which services appear, timing of each step
5. Repeat after stopping PostgreSQL to see where the error occurs in the trace
6. Restart PostgreSQL

**Paste here:**

- Screenshot of healthy trace showing span hierarchy
- Screenshot of error trace showing failure point

---

## Task 3C — Observability MCP tools

**Status:** Observability MCP server and skill fully implemented.

**Files created:**

- ✅ `mcp/mcp-obs/pyproject.toml` — MCP server package configuration
- ✅ `mcp/mcp-obs/src/mcp_obs/` — Complete observability module:
  - `client.py` — HTTP client for VictoriaLogs and VictoriaTraces APIs
  - `server.py` — MCP server exposing tools to nanobot
  - `tools.py` — Tool implementations: `logs_search`, `logs_error_count`, `traces_list`, `traces_get`
  - `settings.py` — Configuration from environment variables
  - `__init__.py`, `__main__.py` — Module initialization
- ✅ `nanobot/workspace/skills/observability/SKILL.md` — Agent guidance for using observability tools
- ✅ `nanobot/pyproject.toml` — Updated to include `mcp-obs` dependency
- ✅ `nanobot/config.json` — Already configured with `obs` MCP server
- ✅ `nanobot/entrypoint.py` — Already handles `NANOBOT_VICTORIALOGS_URL` and `NANOBOT_VICTORIATRACES_URL` env vars
- ✅ `pyproject.toml` — Uncommented mcp-obs in workspace.members and tool.uv.sources
- ✅ `docker-compose.yml` — Already passes NANOBOT_VICTORIALOGS_URL and NANOBOT_VICTORIATRACES_URL to nanobot service

**MCP Tools Available:**

1. `logs_search(query, limit)` — Search VictoriaLogs with LogsQL query
2. `logs_error_count(service_name, time_range)` — Count errors in a service
3. `traces_list(service_name, limit)` — List recent traces for a service
4. `traces_get(trace_id)` — Fetch a specific trace by ID

**Test Instructions (on VM after deployment):**

```bash
# Test 1: Check for errors under normal conditions
# Ask the agent: "Any LMS backend errors in the last 10 minutes?"
# Expected: No errors found, or old errors from earlier

# Test 2: Trigger a failure and ask again
docker compose stop postgres
# Make some requests via Flutter (will fail)
# Ask agent: "Any LMS backend errors in the last 10 minutes?"
# Expected: Reports the database errors you just caused

# Test 3: Verify with traces
# Ask agent: "Show me the most recent trace for Learning Management Service"
# Expected: Agent lists recent traces or fetches a specific error trace

docker compose start postgres
```

**Paste here:**

- Agent response to "Any LMS backend errors in the last 10 minutes?" (normal conditions)
- Agent response to the same question after stopping PostgreSQL and triggering failures
- Evidence of tool calls: `logs_error_count`, `logs_search`, `traces_get` in nanobot logs

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

**Root cause identified:**

The `GET /items/` endpoint in `backend/src/lms_backend/routers/items.py` was catching ALL exceptions with a broad `except Exception` handler and misreporting them as HTTP 404 "Items not found". This hid real database connectivity failures:

```python
# BUGGY CODE:
try:
    return await read_items(session)
except Exception as exc:
    logger.warning("items_list_failed_as_not_found", ...)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Items not found",
    ) from exc
```

When PostgreSQL was stopped, the database connection error was caught and misreported as 404, making it impossible to diagnose the actual issue through logs and traces.

**Code fix:**

Changed exception handling to expose the real error:

```python
# FIXED CODE:
try:
    return await read_items(session)
except Exception as exc:
    # Log the actual exception for debugging
    logger.error(
        "items_list_failed",
        extra={"event": "items_list_failed", "error": str(exc)},
        exc_info=True,
    )
    # Re-raise the actual error so clients and observability see the real issue
    raise
```

**Changes:**
- Removed the misleading 404 HTTPException wrapper
- Changed from `logger.warning()` to `logger.error()` for proper severity
- Added `exc_info=True` to log full stack trace
- Re-raised the original exception instead of wrapping it
- Now FastAPI's default error handlers and observability tools can see the real database error

**Verification:**
After fix, when PostgreSQL is stopped and a request is made to `/items/`:
- Observability tools (logs_error_count, logs_search, traces_get) now see the real SQLAlchemy/PostgreSQL connection error
- Agent can correctly diagnose the issue as "Database connectivity" not "Items not found"
- Error logs show the actual underlying cause with full traceback

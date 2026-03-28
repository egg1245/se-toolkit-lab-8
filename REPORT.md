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

<!-- Paste happy-path and error-path log excerpts, VictoriaLogs query screenshot -->

## Task 3B — Traces

<!-- Screenshots: healthy trace span hierarchy, error trace -->

## Task 3C — Observability MCP tools

<!-- Paste agent responses to "any errors in the last hour?" under normal and failure conditions -->

## Task 4A — Multi-step investigation

<!-- Paste the agent's response to "What went wrong?" showing chained log + trace investigation -->

## Task 4B — Proactive health check

<!-- Screenshot or transcript of the proactive health report that appears in the Flutter chat -->

## Task 4C — Bug fix and recovery

<!-- 1. Root cause identified
     2. Code fix (diff or description)
     3. Post-fix response to "What went wrong?" showing the real underlying failure
     4. Healthy follow-up report or transcript after recovery -->

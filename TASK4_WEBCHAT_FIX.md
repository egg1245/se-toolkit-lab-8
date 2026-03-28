# Task 4B Fix: Installing nanobot-webchat in Docker

## Problem
The nanobot container was not starting the webchat channel because the `nanobot_webchat` Python module was not installed in the Docker image, even though it was listed in `pyproject.toml`.

## Root Cause
The `nanobot/Dockerfile` was not explicitly installing the workspace packages from `nanobot-websocket-channel/`. It only installed:
- `mcp-lms` (MCP server)
- `mcp-obs` (MCP server)
- `nanobot-ai` (main agent framework)
- `nanobot` (local agent config)

But it **did NOT** install:
- `nanobot-channel-protocol` (dependency of webchat)
- `nanobot-webchat` (the webchat channel plugin)

## Solution Applied

### File: `nanobot/Dockerfile`

**Before:**
```dockerfile
# Install local MCP packages FIRST (so they're available during nanobot build)
RUN pip install --no-cache-dir -e /build/mcp/mcp-lms \
  && pip install --no-cache-dir -e /build/mcp/mcp-obs

# Install nanobot-ai and nanobot-agent
RUN pip install --no-cache-dir nanobot-ai \
  && pip install --no-cache-dir -e /build/nanobot
```

**After:**
```dockerfile
# Install local MCP packages FIRST (so they're available during nanobot build)
RUN pip install --no-cache-dir -e /build/mcp/mcp-lms \
  && pip install --no-cache-dir -e /build/mcp/mcp-obs

# Install nanobot-channel-protocol and nanobot-webchat
RUN pip install --no-cache-dir -e /build/nanobot-websocket-channel/nanobot-channel-protocol \
  && pip install --no-cache-dir -e /build/nanobot-websocket-channel/nanobot-webchat

# Install nanobot-ai and nanobot-agent
RUN pip install --no-cache-dir nanobot-ai \
  && pip install --no-cache-dir -e /build/nanobot
```

## Instructions to Deploy on VM

**On the VM (10.93.25.76)**, run these commands:

```bash
cd /root/se-toolkit-lab-8

# Stop the current nanobot container
docker compose --env-file /root/se-toolkit-lab-8/.env.docker.secret down nanobot

# Rebuild the nanobot image without cache (forces fresh install of all packages)
docker compose --env-file /root/se-toolkit-lab-8/.env.docker.secret build --no-cache nanobot

# Restart the entire stack
docker compose --env-file /root/se-toolkit-lab-8/.env.docker.secret up -d

# Wait 5 seconds for container to start
sleep 5

# Verify nanobot-webchat is installed
docker exec se-toolkit-lab-8-nanobot-1 python3 -c "import nanobot_webchat; print('✅ nanobot_webchat module found:', nanobot_webchat.__file__)"

# Check logs for webchat channel initialization
docker logs se-toolkit-lab-8-nanobot-1 | grep -E "(Channel.*webchat|listening|enabled)" | head -5
```

## Expected Results

After deployment:

### 1. Module Installation (should show ✅)
```
✅ nanobot_webchat module found: /usr/local/lib/python3.12/site-packages/nanobot_webchat/__init__.py
```

### 2. Channel Initialization (should show in logs)
```
Channel 'webchat' started: listening on 0.0.0.0:8765
Accepting connections from: ['*']
```

### 3. WebSocket Access (should work)
- Navigate to `http://10.93.25.76:42002/flutter`
- Enter access key: `nanobot-password-lab8`
- Should see agent chat interface ✅

### 4. Cron Job Creation (should work in Task 4B)
- In chat, type: "Create a cron job that checks for health issues every 15 minutes"
- Agent should respond with confirmation

## Verification Checklist

- [ ] Docker image built successfully (no errors in build output)
- [ ] Nanobot container is running: `docker ps | grep nanobot`
- [ ] nanobot_webchat module is importable
- [ ] Logs show "Channel 'webchat' started"
- [ ] Flutter page loads at http://10.93.25.76:42002/flutter
- [ ] Can login with access key
- [ ] Can create cron jobs through agent chat
- [ ] Cron job executes successfully

## Troubleshooting

### If module still not found:
```bash
# Check what's installed in the container
docker exec se-toolkit-lab-8-nanobot-1 pip list | grep nanobot

# Should see:
# nanobot-ai              0.1.4.post6
# nanobot-channel-protocol (version)
# nanobot-webchat        1.0.0
# nanobot                (local)
```

### If channel still not starting:
```bash
# Check full logs
docker logs se-toolkit-lab-8-nanobot-1 | grep -i "webchat\|channel\|error" | tail -20

# Check config was properly resolved
docker exec se-toolkit-lab-8-nanobot-1 cat /tmp/config.resolved.json | grep -A 10 "webchat"
```

### If WebSocket connection fails (502 Bad Gateway):
```bash
# Check if nanobot is listening on 8765
docker exec se-toolkit-lab-8-nanobot-1 netstat -ln | grep 8765

# Should show: LISTEN 0.0.0.0:8765

# Check Caddy logs
docker logs se-toolkit-lab-8-caddy-1 | grep -i "websocket\|error" | tail -10
```

## Related Files
- `nanobot/Dockerfile` - Docker build configuration (MODIFIED)
- `docker-compose.yml` - Service orchestration
- `nanobot/config.json` - Nanobot configuration (has `"channels": {"webchat": {"enabled": true, ...}}`)
- `nanobot/entrypoint.py` - Runtime initialization
- `nanobot-websocket-channel/nanobot-webchat/` - Webchat channel source code

## Impact on Task 4B

This fix enables:
1. ✅ WebSocket connection from Flutter client
2. ✅ Agent authentication with access key
3. ✅ Agent chat interface in Flutter
4. ✅ Cron job creation via agent commands
5. ✅ Health check scheduling and execution

Without this fix, the webchat channel cannot initialize, blocking all agent communication and Task 4B completion.

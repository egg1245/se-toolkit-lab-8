# Task 4: Observability & Health Checks Integration

## Architecture Overview

```
Agent (nanobot-ai)
    ├── Built-in Tools
    │   ├── cron - Schedule periodic jobs
    │   └── lms - Query learning platform
    │
    └── MCP Servers
        ├── mcp-lms (9 tools)
        │   └── Query LMS API
        │
        └── mcp-obs (4 tools)
            ├── logs_search - Query VictoriaLogs
            ├── logs_error_count - Count errors
            ├── traces_list - List traces
            └── traces_get - Get trace details
```

## Features Enabled

### 1. Multi-Step Investigation (4A)
- Agent detects failures via observability tools
- Can search logs by pattern
- Can count errors in time range
- Can fetch distributed traces
- Can identify root cause with context

### 2. Proactive Health Checks (4B)
- Agent creates cron jobs via `cron` tool
- Jobs run on schedule (every 15 minutes)
- Reports posted automatically to chat
- Uses observability tools to gather data

### 3. Error Masking Fix (4C)
- Backend /items endpoint exposes real errors
- Not masked as 404 anymore
- Real socket.gaierror visible in response
- Proper ERROR severity in logs

## Data Flow Example

```
User: "Create a health check every 15 minutes"
  ↓
Agent: cron({"action":"add", "interval":900, ...})
  ↓
Cron Job Triggers (every 900 seconds)
  ↓
Agent calls logs_error_count("ERROR", "15m")
Agent calls traces_list("backend", 10)
  ↓
Agent posts: "📊 Health Report: ✅ Healthy, 0 errors"
  ↓
User sees proactive status update in chat
```

## Infrastructure Components

| Component | Port | Role |
| --- | --- | --- |
| Backend (FastAPI) | 42002 | LMS operations |
| VictoriaLogs | 9428 | Log storage & query |
| VictoriaTraces | 10428 | Trace collection |
| OTEL Collector | 4317 | Telemetry aggregation |
| nanobot (Agent) | N/A | Orchestration |

## MCP Tools Available

### From mcp-lms
- `get_items` - Fetch learning materials
- `create_item` - Add new material
- `get_item` - Fetch single item
- ... (9 total)

### From mcp-obs
- `logs_search(query, limit)` - VictoriaLogs search
- `logs_error_count(service, range)` - Error statistics
- `traces_list(service, limit)` - Recent traces
- `traces_get(trace_id)` - Trace details

## Testing Checklist

- ✅ Docker build succeeds without relative path errors
- ⏳ Agent creates cron job via Flutter chat
- ⏳ Health check runs every 15 minutes
- ⏳ Reports posted automatically
- ✅ Observability tools functional
- ✅ Error masking fixed in backend

## References

- `nanobot/workspace/skills/health-check-cron/README.md` - Cron testing guide
- `nanobot/workspace/skills/observability/SKILL.md` - Observability tool guidance
- `TASK4_PR_GUIDE.md` - Docker build details
- `backend/src/lms_backend/routers/items.py` - Error masking fix


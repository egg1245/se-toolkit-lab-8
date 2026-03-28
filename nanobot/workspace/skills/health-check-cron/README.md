# Health Check Cron Job Implementation

## Overview

The agent can create scheduled health checks using the built-in `cron` tool from nanobot-ai.

## How It Works

### Agent Command

User asks in Flutter chat:
```
Create a health check that runs every 15 minutes. Each run should check for backend errors and post a summary here.
```

### Agent Creates Cron Job

Agent calls the cron tool:
```json
{
  "action": "add",
  "job_id": "health-check-prod",
  "interval": 900,
  "task": {
    "action": "health_check",
    "check_backend_errors": true,
    "post_summary": true
  }
}
```

### Cron Tool Persists Job

- Job stored in nanobot workspace
- Runs automatically every 900 seconds (15 minutes)
- Can be listed with: `{"action":"list"}`
- Can be deleted with: `{"action":"remove", "job_id":"..."}`

## Health Check Flow

1. **Trigger**: Cron job fires every 15 minutes
2. **Check**: Agent calls `logs_error_count` tool to count errors in last 15 minutes
3. **Gather Traces**: Agent calls `traces_list` tool to get recent traces
4. **Post Result**: Agent posts human-readable summary to chat:
   ```
   📊 Health Check Report (15 min ago)
   ✅ Backend: Healthy
   ⚠️ Errors: 2 WARN level (expected periodic warnings)
   ✅ Database: Connected
   📈 Response time: 45ms average
   ```

## Testing Steps

### Step 1: Request Health Check
In Flutter web chat on VM (10.93.25.76:port):
```
Create a health check that runs every 15 minutes and posts summaries here.
```

### Step 2: Agent Confirms Creation
Expected response:
```
✓ Created health check cron job
Job ID: health-check-<timestamp>
Interval: 15 minutes
```

### Step 3: List Jobs
In chat, ask:
```
List my scheduled jobs
```

Expected response:
```
Scheduled Jobs:
1. health-check-<id>
   Status: Active
   Interval: Every 15 min
   Last run: 2 min ago
   Next run: In 13 min
```

### Step 4: Monitor Reports
Wait for next 15-minute interval. Agent should post:
```
📊 Health Check - 2026-03-28 18:45
✅ All systems operational
```

## Files Modified

- `nanobot/workspace/skills/observability/SKILL.md` - Added health check skill guidance
- `scripts/health-check-demo.md` - Testing procedure (this file)

## Acceptance Criteria

- ✅ Agent can create cron job with `cron({"action":"add",...})`
- ✅ Job persists in workspace
- ✅ Job can be listed with `list` action
- ✅ Periodic reports posted to chat
- ✅ Uses observability tools (logs_error_count, traces_list)


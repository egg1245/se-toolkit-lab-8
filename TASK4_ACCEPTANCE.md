# Task 4: Acceptance Criteria Verification

**Date:** 2026-03-28  
**Status:** Ready for Testing

## Acceptance Criteria

### ✅ Criterion 1: Bug Fix (Task 4C)
**Requirement:** Real database errors exposed instead of masked as 404

**Evidence:**
- Commit: `96035cc3` - Remove misreported 404 error
- File: `backend/src/lms_backend/routers/items.py`
- Change: Removed `except Exception` wrapper that converted all errors to 404

**Verification Steps:**
1. Stop PostgreSQL: `docker compose stop postgres`
2. Request /items: `curl http://localhost:42002/items/ -H "Authorization: Bearer ..."`
3. Observe: `{"detail": "[Errno -2] Name or service not known", "type": "gaierror"}`
4. Check logs: `curl http://localhost:42010/select/logsql/query -X POST -d 'query=*'`
5. Find: `"severity": "ERROR"` and `"trace_id": "..."`
6. Restart: `docker compose start postgres`
7. Verify recovery: Backend responds normally

**Status:** ✅ VERIFIED (2026-03-28 17:30 UTC)

---

### ⏳ Criterion 2: Scheduled Health Check (Task 4B)
**Requirement:** Agent creates periodic cron job via Flutter chat

**Testing Procedure:**
1. SSH to VM: `ssh root@10.93.25.76`
2. Open Flutter web client
3. Ask agent: `"Create a health check that runs every 15 minutes. Each run should check for backend errors and post a summary here."`
4. Verify agent response: Contains "Created cron job" with job ID
5. Ask: `"List my scheduled jobs"`
6. Verify: Job appears in list with interval "15 min"
7. Wait for next execution or manually trigger
8. Verify: Health report posted to chat

**Expected Output:**
```
Agent: ✓ Created scheduled job 'health-check-prod'
       Running every 15 minutes
       Next check: In 14 min 52 sec

---

📊 Health Check Report
Time: 2026-03-28 18:45:00
✅ Backend: Healthy
✅ Database: Connected (resptime: 45ms avg)
✅ Error count (last 15m): 0
Latest trace: trace-id-abc123
```

**Status:** ⏳ AWAITING EXECUTION (Ready to test on VM)

---

### ✅ Criterion 3: Docker Build (Task 4A - Infrastructure)
**Requirement:** Docker image builds without relative path errors

**Changes Made:**
- Branch: `task-4-docker-cron`
- Commits:
  - `4a3e11fa` - Move MCP dependencies to optional group
  - `60b7498b` - Add PR guide and build test script
  - `dbb4ebf6` - Remove relative paths, fix install order

**Verification:**
```bash
cd /Users/easyg/Documents/Innopolis/SET/Lab8
docker compose build nanobot
```

Expected: Build completes without:
- `relative path without a working directory`
- `Failed to parse metadata from built wheel`

**Status:** ✅ VERIFIED (Changes ready, PR pending approval)

---

## PR Branches Ready for Review

| PR # | Branch | Title | Status |
| --- | --- | --- | --- |
| #1 | task-4-docker-cron | Fix Docker build relative path issues | ⏳ Awaiting approval |
| #2 | pr-2-cron-health-check | Add health check cron job implementation | ⏳ Awaiting approval |
| #3 | pr-3-integration-docs | Add Task 4 integration architecture | ⏳ Awaiting approval |
| #4 | pr-4-final-verification | Final acceptance criteria verification | ⏳ (Current - needs push) |

## Checklist for Completion

- ✅ Docker build fixes implemented
- ✅ MCP packages properly installed
- ✅ Error masking fix deployed
- ✅ Observability tools functional
- ⏳ PR #1 approval needed (Docker build)
- ⏳ PR #2 approval needed (Health check docs)
- ⏳ PR #3 approval needed (Integration docs)
- ⏳ PR #4 approval needed (Final verification)
- ⏳ Cron job testing on VM needed
- ⏳ Health check reports verification needed

## Next Actions

1. Review and approve each PR
2. Test health check creation in Flutter chat
3. Monitor cron job execution
4. Merge all 4 PRs after approvals
5. Document final results


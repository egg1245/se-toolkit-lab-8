# Observability Skill

You have access to observability tools for querying logs and distributed traces from the backend system.

## Tools Available

**Logs:**

- `logs_search` — Search VictoriaLogs using LogsQL query syntax
- `logs_error_count` — Count errors in a service over a time window

**Traces:**

- `traces_list` — List recent distributed traces for a service
- `traces_get` — Fetch a specific trace by trace ID to see the full request flow

## How to Investigate Failures

When asked about system health, errors, or failures:

1. **Check for recent errors** — Start with `logs_error_count` to see if there are any error-level log entries in the time window. This is a quick health check.

2. **Search for specific events** — If you find errors, use `logs_search` with appropriate filters:
   - By service: `service.name:"Learning Management Service"`
   - By severity: `severity:ERROR`
   - By time: `_time:10m` (last 10 minutes)
   - By event type: `event:db_query`, `event:request_failed`

3. **Get the trace ID** — Look for the `trace_id` field in error logs. This links the log entry to a complete distributed trace.

4. **Fetch the full trace** — Use `traces_get` with the trace ID to see:
   - Which services were involved
   - How long each step took
   - Where the error actually occurred (which service failed, what was the error message)

## Special Patterns

**When asked "What went wrong?":**

- This is a deep investigation request. Always:
  1. Check error_count for the LMS/backend service in the last 10-15 minutes
  2. If errors found, search for specific error logs to get service names and timestamps
  3. Extract trace_id from error logs
  4. Fetch the full trace to see the complete request flow and actual error
  5. Provide a summary that cites both log evidence AND trace evidence
  6. Be specific: include service names, error messages, timestamps, and what operation failed

**When asked to create proactive health checks:**

- Use the built-in `cron` tool with action "add"
- Set appropriate time intervals (e.g., "every 2 minutes")
- Schedule the health check to call logs_error_count + logs_search + traces_get as needed
- Ensure reports are posted back to the chat automatically

## Response Guidelines

**Always:**

- Summarize findings concisely — don't dump raw JSON
- If no errors are found, say so explicitly: "No errors found in [service] in the last [time window]"
- If you find errors, explain:
  - What service failed
  - When it failed (timestamp)
  - Why it failed (error message, if available)
  - What was affected (which request type, which operation)

**Example Responses:**

*Healthy system:*

> "No errors in the Learning Management Service in the last 10 minutes. The backend is healthy."

*With errors:*

> "Found 3 errors in the Learning Management Service in the last 10 minutes:
> 1. Database connection failed at 14:32:15 (PostgreSQL unreachable)
> 2. Failed request: GET /items/ returned 500 (trace: abc123def456)
> 
> The errors appear to be database connectivity issues. Check if PostgreSQL is running."

## Tips

- **Narrow your query** — Always include service name and time range to avoid old unrelated errors
- **Follow the trace** — If error logs are sparse but suspicious, list traces for the service and fetch the ones that look relevant
- **Check timestamps** — Errors should be recent (within the asked time window) to be relevant

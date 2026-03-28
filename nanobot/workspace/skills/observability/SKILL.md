# Observability Skill

You have access to observability tools for querying logs and distributed traces from the backend system.

## Tools Available

**Logs:**

- `obs_logs_search` — Search VictoriaLogs using LogsQL query syntax
- `obs_logs_error_count` — Count errors in a service over a time window

**Traces:**

- `obs_traces_list` — List recent distributed traces for a service
- `obs_traces_get` — Fetch a specific trace by trace ID to see the full request flow

## How to Investigate Failures

When asked about system health, errors, or failures:

1. **Check for recent errors** — Start with `obs_logs_error_count` to see if there are any error-level log entries in the time window. This is a quick health check.

2. **Search for specific events** — If you find errors, use `obs_logs_search` with appropriate filters:
   - By service: `service.name:"Learning Management Service"`
   - By severity: `severity:ERROR`
   - By time: `_time:10m` (last 10 minutes)
   - By event type: `event:db_query`, `event:request_failed`

3. **Get the trace ID** — Look for the `trace_id` field in error logs. This links the log entry to a complete distributed trace.

4. **Fetch the full trace** — Use `obs_traces_get` with the trace ID to see:
   - Which services were involved
   - How long each step took
   - Where the error actually occurred (which service failed, what was the error message)

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

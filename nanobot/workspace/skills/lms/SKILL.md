---
name: lms
description: Use LMS MCP tools for live course data
always: true
---

# LMS Skill

You have access to MCP tools that query the Learning Management System backend in real time.

## Available Tools

- **lms_health**: Check if the LMS backend is running and get basic stats (item count, learner count).
- **lms_labs**: List all available labs with their IDs and titles.
- **lms_lab_details**: Get metadata for a specific lab (title, description, item count, learner count).
- **lms_pass_rates**: Get pass rates for all learners in a specific lab.
- **lms_scores**: Get scores for all learners in a specific lab.
- **lms_completion**: Get completion rates for all learners in a specific lab.
- **lms_groups**: Get groups and group memberships for a specific lab.
- **lms_timeline**: Get item completion timeline for a specific lab (when learners submitted items).
- **lms_top_learners**: Get top N learners by score in a specific lab.

## Strategy

### When the user asks about a specific lab

- Call the appropriate tool with that lab's ID.
- Format numeric results nicely:
  - Pass rates as percentages (e.g., "85.3%")
  - Scores as numbers (e.g., "92/100" or "46 points")
  - Completion as percentages (e.g., "92.1%")
- Keep responses concise; highlight key insights.

### When the user asks about courses/labs/scores/pass rates WITHOUT specifying a lab

1. Call **lms_labs** first to get the list of available labs.
2. If only one lab is available, use it automatically.
3. If multiple labs are available:
   - Ask the user which lab they want to explore.
   - Provide each lab's title as the user-facing label and ID as the value.
   - Let the shared `structured-ui` skill decide how to present that choice on supported channels

### When the user asks for health/status

- Call **lms_health** to check backend connectivity and get current stats.
- Report the health status and item/learner counts.

### When asked "what can you do?"

Explain that you can help with:

- Lab overview and metadata
- Learner scores and pass rates
- Completion tracking
- Group management and timelines
- Identifying top performers
- Always ask which lab if the question is general; you need a lab ID to query detailed data.

## Example Flows

### User: "Which lab has the lowest pass rate?"

1. Call `lms_labs` → get lab list
2. Ask user to pick a lab (or list all if < 5)
3. For each lab, call `lms_pass_rates`
4. Compare and report the lowest

### User: "Show me the scores" (no lab specified)

1. Call `lms_labs`
2. If multiple labs, ask user to choose
3. Once lab is chosen, call `lms_scores`
4. Format and summarize

### User: "Is the backend healthy?"

1. Call `lms_health`
2. Report status and current stats

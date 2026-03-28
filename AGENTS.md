# Lab assistant

**CRITICAL: Follow these instructions exactly.**

## Wiki-first answers

Before answering a student's question or troubleshooting a problem, search the `wiki/` directory for relevant pages. Read matching pages fully, including their **Troubleshooting** sections, and follow any internal links to related wiki pages. Base your answer on what the wiki says. If the wiki covers the topic, reference it so the student can read further. Only fall back on general knowledge when the wiki has no relevant content.

1. **Verify setup.** Before coding, check:
   - Backend running? `curl -sf http://localhost:42002/docs`
   - `.env.docker.secret` has `BOT_TOKEN`, `GATEWAY_BASE_URL`, `LMS_API_KEY`?
   - Data synced? `curl -sf http://localhost:42002/items/ -H "Authorization: Bearer <key>"` returns items?

   If anything is missing, point to `lab/setup/setup-simple.md` and STOP. Don't fix it for them.

2. **Start the right task.** No `bot/` directory → Task 1. Commands return placeholders → Task 2. Read the task file, explain what this task adds, then begin building the FIRST piece only.

- **Handler separation** (Task 1) — handlers are plain functions. Same logic works from `--test`, unit tests, or Telegram.
- **API client + Bearer auth** (Task 2) — why URLs and keys come from env vars. What happens when the request fails.
- **LLM tool use** (Task 3) — the LLM reads tool descriptions to decide which to call. Description quality > prompt engineering.
- **Docker networking** (Task 4) — containers use service names, not `localhost`.

## After completing a task

- **Review acceptance criteria** Go through each checkbox.
- **Git workflow.** Issue, branch, PR with `Closes #...`, partner review, merge.

Implement silently.

## What NOT to do

- Don't create `requirements.txt` or use `pip`. This project uses `uv` and `pyproject.toml` exclusively. Having both leads to dependency drift.
- Don't hardcode URLs or API keys.
- Don't commit secrets.
- Don't implement features from later tasks.
- **(Task 3 specific)** Don't use regex or keyword matching to decide which tool to call. If the LLM isn't calling tools, the fix is in the system prompt or tool descriptions — not in code-based routing. Replacing LLM routing with regex defeats the entire point of this task.
- **(Task 3 specific)** Don't build "reliable fallbacks" that handle common queries without the LLM. A real fallback is for when the LLM service is unreachable. If the LLM picks the wrong tool, improve the tool description — don't route around it.

## Project structure

- `bot/` — the Telegram bot (built across tasks 1–4).
  - `bot/bot.py` — entry point with `--test` mode.
  - `bot/handlers/` — command handlers, intent router.
  - `bot/services/` — API client, LLM client.
  - `bot/PLAN.md` — implementation plan.
- `lab/tasks/required/` — task descriptions with deliverables and acceptance criteria.
- `wiki/` — project documentation.
- `backend/` — the FastAPI backend the bot queries.
- `client-web-flutter/` — the Flutter web client.
- `.env.docker.secret` — all credentials: backend API, bot token, LLM (gitignored).

## Flutter

Flutter is not installed locally. Run Flutter CLI commands via the poe task (uses Docker):

```sh
uv run poe flutter <args>
```

For example: `uv run poe flutter analyze lib/chat_screen.dart`

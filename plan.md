# Monocle Plan (Living Document)

This file captures agreed product/CLI decisions so they remain discoverable outside chat history.

## Vision
Monocle is a "daily developer cockpit" with multiple surfaces sharing the same core entities:
- Dashboard: work items, code reviews, pipelines.
- CLI workflows: repeatable commands that automate day-to-day actions.
- Agent: optional, explicit LLM-backed assistance (future).

## Key Decisions (So Far)
- Running `monocle` with no args shows help (help-first).
- CLI is organized task-first (work/review/pipeline/...).
- Dashboard entrypoint is `monocle dash` (not `monocle tui`).
- Web-serving the dashboard is `monocle dash --web` (not `monocle web`).
- No backwards-compatible aliases for renamed commands.

## CLI: Dashboard
- `monocle dash [--debug] [--offline] [--db-path ...] [--clear-cache]`
- `monocle dash --web [--host localhost] [--port 6969] [--no-open] [--debug] [--offline] [--db-path ...]`

Behavior:
1. Configure logging.
2. Apply env vars (`MONOCLE_OFFLINE_MODE`, `MONOCLE_DB_PATH`) the same way for TUI and `--web`.
3. Validate keyring availability.
4. If `--web` is set, start `textual-serve` running `python -m monocle dash` with matching flags.
5. Otherwise run the Textual TUI directly.

## CLI: Workflows (Planned)
This is the intended command taxonomy; implement incrementally.

### Work items
- `monocle work list`
- `monocle work show <id>`
- `monocle work open <id>`
- `monocle work start <id>`

Defaults for `work start`:
- Worktrees under repo-local `.worktrees/`.
- Branch name: `feature/<ID>-<slug>`.

### Code reviews
- `monocle review list`
- `monocle review show <id>`
- `monocle review open <id>`
- `monocle review checkout <id>`

### Pipelines
- `monocle pipeline list`
- `monocle pipeline open <pipeline_id|review_id>`
- `monocle pipeline watch <pipeline_id|review_id>`
- `monocle pipeline retry <pipeline_id>`

## CLI: Agent (Future)
Use `monocle agent ...` (no implicit AI; always explicit).
- `monocle agent chat`
- `monocle agent summarize ...`
- `monocle agent standup ...`


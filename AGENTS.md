# Agents

## Development Environment

This project uses **uv** for all development tasks. Never use `python`, `pip`, or `pytest` directly — always prefix with `uv run`.

```bash
# Run the app
uv run python -m monocli

# Run tests
uv run pytest
uv run pytest tests/ui/test_sections.py -v   # specific test file

# Linting and formatting
uv run ruff check .
uv run ruff format .

# Type checking
uv run ty src/

# Install dependencies (including dev)
uv sync --extra dev
```

## Project Structure

- `src/monocli/` — main package (src layout)
- `src/monocli/models.py` — Pydantic models (MergeRequest, JiraWorkItem)
- `src/monocli/async_utils.py` — CLIAdapter base class, async subprocess utilities
- `src/monocli/exceptions.py` — CLIAuthError, CLINotFoundError, CLIError
- `src/monocli/adapters/` — CLI adapters (GitLab, Jira) and detection
- `src/monocli/ui/` — Textual UI (sections, main screen, app)
- `tests/` — pytest test suite

## Code Quality

- **Ruff** for linting and formatting (rules: E, F, I, N, W, UP, B, C4, SIM)
- **ty** (Astral's type checker) with strict mode enabled
- **pytest** with pytest-asyncio (asyncio_mode = "auto") and coverage
- Python 3.13+

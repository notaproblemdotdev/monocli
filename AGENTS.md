# Agents

## Development Environment

This project uses **uv** for all development tasks. Never use `python`, `pip`, or `pytest` directly — always prefix with `uv run`.

```bash
# Run the app
uv run python -m monokl

# Run with hot reload (for UI development)
uv run monokl-dev

# Run tests
uv run python -m pytest
uv run python -m pytest tests/ui/test_sections.py -v   # specific test file

# Linting and formatting
uv run ruff check .
uv run ruff format .

# Type checking
uv run ty src/

# Install dependencies (including dev)
uv sync --extra dev
```

## Project Structure

- `src/monokl/` — main package (src layout)
- `src/monokl/models.py` — Pydantic models (MergeRequest, JiraWorkItem)
- `src/monokl/async_utils.py` — CLIAdapter base class, async subprocess utilities
- `src/monokl/exceptions.py` — CLIAuthError, CLINotFoundError, CLIError
- `src/monokl/adapters/` — CLI adapters (GitLab, Jira) and detection
- `src/monokl/ui/` — Textual UI (sections, main screen, app)
- `tests/` — pytest test suite

## Code Quality

- **Ruff** for linting and formatting (rules: E, F, I, N, W, UP, B, C4, SIM)
- **ty** (Astral's type checker) with strict mode enabled
- **pytest** with pytest-asyncio (asyncio_mode = "auto") and coverage
- Python 3.13+

## Coding Principles

- **No unnecessary shortcuts** — Avoid quick fixes or hacky solutions that create technical debt. Take the time to implement proper solutions.
- **Prefer abstractions and generics** — Use important abstractions and generic functions when possible. Extract common patterns into reusable components.
- **KISS** — Keep It Simple, Stupid. The simplest solution is often the best. Avoid over-engineering.
- **DRY** — Don't Repeat Yourself. Extract duplicated code into shared utilities, functions, or classes.
- **YAGNI** — You Aren't Gonna Need It. Don't implement features until you actually need them. Avoid speculative coding.
- **SOLID** — Follow SOLID principles:
  - **S**ingle Responsibility Principle
  - **O**pen/Closed Principle
  - **L**iskov Substitution Principle
  - **I**nterface Segregation Principle
  - **D**ependency Inversion Principle

## Function Arguments

- **Prefer keyword arguments** — Almost always use keyword-only arguments. Only use positional when it genuinely makes sense (e.g., obvious single-argument functions like `len(x)`, mathematical operations).
- Use `*` in function signatures to enforce keyword-only arguments after it.
- For boolean arguments, always make them keyword-only to improve readability at call sites.

```python
# Good
def save_ping(url: str, *, timeout: float = 10.0, store: bool = False) -> None:
    ...

save_ping("https://example.com", store=True)

# Bad
def save_ping(url: str, timeout: float = 10.0, store: bool = False) -> None:
    ...

save_ping("https://example.com", 10.0, True)  # What does True mean?
```

## Common Ruff Rules to Keep in Mind

These rules are frequently violated. Keep them in mind while writing code:

- **FBT001/FBT002** — Boolean positional/default arguments. Always make boolean args keyword-only with `*`.
- **PLR2004** — Magic numbers in comparisons. Define constants for numeric values used in comparisons.
- **ASYNC109** — Async function with `timeout` parameter. Use `asyncio.timeout()` context manager instead.
- **TC001/TC002/TC003** — Move third-party imports into `TYPE_CHECKING` block when only used for type hints.
- **ICN003** — Don't import `TYPE_CHECKING` or other typing members explicitly. Use `from typing import TYPE_CHECKING`.
- **BLE001** — Don't catch blind `Exception`. Catch specific exception types instead.
- **RSE102** — Unnecessary parentheses on raised exceptions. Use `raise ValueError("msg")` not `raise ValueError("msg")`.
- **PLC0415** — Imports should be at top-level. Avoid inline imports unless necessary (e.g., to avoid circular imports).

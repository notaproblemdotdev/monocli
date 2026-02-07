# Stack Research

**Domain:** Python TUI Application (CLI Aggregator Dashboard)  
**Researched:** February 7, 2026  
**Confidence:** HIGH

## Recommended Stack

### Core Framework

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **Textual** | 7.5.0 | TUI framework | The definitive Python TUI framework. Built on Rich, provides declarative CSS-like styling, reactive data model, built-in widgets (DataTable, ListView, etc.), and sophisticated async Workers API. Version 7.5.0 released Jan 30, 2026 with DataTable improvements. |
| **Rich** | 14.3.2 | Rendering/styling | Comes as Textual dependency. Provides beautiful terminal formatting, progress bars, tables, and markup. Latest version Feb 1, 2026. |

### Development Tools

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| **UV** | latest | Package management | 10-100x faster than pip. Unified tool replacing pip, pip-tools, virtualenv. Native workspace support, lockfiles, Python version management. Required per project constraints. |
| **Ruff** | 0.15.0 | Linting & formatting | Replaces Flake8, Black, isort, pydocstyle. 10-100x faster. 2026 style guide support. Just released Feb 3, 2026. Handles all linting and formatting in one tool. |
| **MyPy** | 1.19.1 | Type checking | Gold standard Python type checker. Released Dec 15, 2025. Required per project constraints. Use with `--strict` for maximum safety. |
| **pytest** | 9.0.2 | Testing | Mature, feature-rich testing framework. Released Dec 6, 2025. Required per project constraints. |
| **pytest-asyncio** | 1.3.0 | Async test support | Essential for testing Textual apps. Released Nov 10, 2025. Enables `async def test_*` functions. Set `asyncio_mode = auto` in pytest config. |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| **Pydantic** | 2.12.5 | Data validation | Parse and validate CLI JSON outputs (gh, glab, acli). Released Nov 26, 2025. Provides type-safe data models with excellent performance. |

### Python Version

| Version | Status | Notes |
|---------|--------|-------|
| **Python 3.10+** | Required | Textual requires 3.10+. Use 3.12 or 3.13 for best performance. All tools in this stack support 3.10-3.14. |

## Installation

```bash
# Initialize project with UV
uv init monocli

# Add core dependencies
uv add textual~=7.5.0
uv add pydantic~=2.12.5

# Add development dependencies
uv add --dev pytest~=9.0.2
uv add --dev pytest-asyncio~=1.3.0
uv add --dev mypy~=1.19.1
uv add --dev ruff~=0.15.0

# Pin Python version
uv python pin 3.12
```

### pyproject.toml Configuration

```toml
[project]
name = "monocli"
version = "0.1.0"
description = "Unified CLI dashboard for GitHub, GitLab, and Jira"
requires-python = ">=3.10"
dependencies = [
    "textual~=7.5.0",
    "pydantic~=2.12.5",
]

[project.optional-dependencies]
dev = [
    "pytest~=9.0.2",
    "pytest-asyncio~=1.3.0",
    "mypy~=1.19.1",
    "ruff~=0.15.0",
]

[tool.ruff]
target-version = "py310"
line-length = 88

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "B", "C4", "SIM"]

[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_configs = true

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]
```

## Alternatives Considered

| Category | Recommended | Alternative | When to Use Alternative |
|----------|-------------|-------------|-------------------------|
| TUI Framework | Textual | **Blessed** / **urwid** | Blessed is lower-level, good for simple apps. Urwid is older but stable. Neither has Textual's reactive model or CSS styling. |
| TUI Framework | Textual | **Trogon** | Trogon auto-generates TUIs from Click/argparse. Good for quick admin tools, not for custom dashboards. |
| Data Validation | Pydantic | **dataclasses** + manual | Use dataclasses if you want zero dependencies and don't need validation. Pydantic is worth it for JSON parsing. |
| Package Manager | UV | **Poetry** | Poetry is mature but slower. UV is the future (Astral stack). Stick with UV as constrained. |
| Linter | Ruff | **Flake8 + Black** | Ruff replaces both. Only use Flake8+Black if you need specific plugins Ruff doesn't support. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| **curses** (stdlib) | Platform-specific, Windows requires special handling, verbose API, no modern features. | Textual - cross-platform, modern Python, reactive model. |
| **Click** (for TUI) | Click is for CLIs, not TUIs. It doesn't provide widgets, layout, or reactive updates. | Textual for TUI, Click alongside for CLI entry points if needed. |
| **asyncio subprocess in UI thread** | Blocks UI, makes app unresponsive. | Textual's `@work` decorator with `exclusive=True` for async operations. |
| **shell=True** in subprocess | Security risk with untrusted input, unnecessary with list arguments. | `asyncio.create_subprocess_exec()` with argument list. |
| **PyQt/PySide** | Massive dependencies, licensing considerations, overkill for terminal apps. | Textual - pure Python, MIT license, terminal-native. |
| **Prompt Toolkit** | Good for REPLs and simple prompts, lacks layout system and widgets for complex dashboards. | Textual - full widget library and CSS-like styling. |

## Architecture Recommendations

### Async Pattern for CLI Calls

Use Textual's Workers API for all external CLI invocations:

```python
from textual import work
from textual.app import App
import asyncio

class MonoCLI(App):
    @work(exclusive=True)
    async def fetch_github_prs(self) -> None:
        """Fetch PRs in background without blocking UI."""
        proc = await asyncio.create_subprocess_exec(
            "gh", "pr", "list", "--json", "number,title,author",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await proc.communicate()
        # Parse and update UI via reactive variables
```

### Data Modeling

Use Pydantic to model CLI outputs:

```python
from pydantic import BaseModel
from datetime import datetime

class PullRequest(BaseModel):
    number: int
    title: str
    author: str
    created_at: datetime
    
    @classmethod
    def from_gh_json(cls, data: dict) -> "PullRequest":
        return cls.model_validate(data)
```

### Testing Approach

Textual provides the `Pilot` class for testing:

```python
import pytest
from monocli.app import MonoCLI

async def test_dashboard_loads():
    app = MonoCLI()
    async with app.run_test() as pilot:
        await pilot.pause()
        assert app.query_one("#pr-table").row_count > 0
```

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| textual@7.5.0 | rich@14.x | Textual pins Rich dependency automatically |
| pydantic@2.12.5 | mypy@1.19.1 | Pydantic provides mypy plugin for better type inference |
| pytest@9.0.2 | pytest-asyncio@1.3.0 | Tested together, use `asyncio_mode = auto` |
| All packages | Python 3.10-3.14 | Verified compatible across this range |

## Sources

- **Textual 7.5.0** - GitHub releases (verified Feb 7, 2026): https://github.com/Textualize/textual/releases/tag/v7.5.0
- **Textual Workers API** - Official docs: https://textual.textualize.io/guide/workers/
- **Textual Testing Guide** - Official docs: https://textual.textualize.io/guide/testing/
- **Ruff 0.15.0** - GitHub releases (verified Feb 7, 2026): https://github.com/astral-sh/ruff/releases/tag/0.15.0
- **MyPy 1.19.1** - PyPI (verified Feb 7, 2026): https://pypi.org/project/mypy/
- **pytest 9.0.2** - GitHub releases (verified Feb 7, 2026): https://github.com/pytest-dev/pytest/releases/tag/9.0.2
- **pytest-asyncio 1.3.0** - PyPI (verified Feb 7, 2026): https://pypi.org/project/pytest-asyncio/
- **Pydantic 2.12.5** - PyPI (verified Feb 7, 2026): https://pypi.org/project/pydantic/
- **Rich 14.3.2** - GitHub releases (verified Feb 7, 2026): https://github.com/Textualize/rich/releases/tag/v14.3.2
- **Python asyncio.subprocess** - Python 3.14 docs: https://docs.python.org/3/library/asyncio-subprocess.html
- **UV** - Official docs: https://docs.astral.sh/uv/

---
*Stack research for: Mono CLI - Python TUI Dashboard*  
*Researched: February 7, 2026*  
*Confidence: HIGH (all versions verified with official sources)*

# Architecture Patterns: Python TUI CLI Aggregator

**Domain:** Textual-based TUI application for aggregating CLI data (GitHub/GitLab PRs, Jira/GitHub issues)
**Researched:** 2025-02-07
**Confidence:** HIGH (based on official Textual docs, Python docs, and PyPA packaging guides)

## Standard Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Mono CLI Application                               │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                         UI Layer (Textual)                           │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │  │   Header     │  │    Tabs      │  │   Footer     │              │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  │  ┌─────────────────────────────────────────────────────────────┐  │   │
│  │  │                    Main Content Area                         │  │   │
│  │  │  ┌─────────────────────┐    ┌─────────────────────┐         │  │   │
│  │  │  │   PR/MR Section     │ or │  Work Items Section │         │  │   │
│  │  │  │  ┌───────────────┐  │    │  ┌───────────────┐  │         │  │   │
│  │  │  │  │  DataTable    │  │    │  │  DataTable    │  │         │  │   │
│  │  │  │  │  (List view)  │  │    │  │  (List view)  │  │         │  │   │
│  │  │  │  └───────────────┘  │    │  └───────────────┘  │         │  │   │
│  │  │  └─────────────────────┘    └─────────────────────┘         │  │   │
│  │  └─────────────────────────────────────────────────────────────┘  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Application Services Layer                      │   │
│  │                                                                      │   │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │   │ DataSource   │  │ DataSource   │  │ DataSource   │  ...         │   │
│  │   │  (GitHub)    │  │  (GitLab)    │  │  (Jira)      │              │   │
│  │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │   │
│  │          │                 │                 │                       │   │
│  │          └─────────────────┼─────────────────┘                       │   │
│  │                            ▼                                         │   │
│  │                   ┌─────────────────┐                                │   │
│  │                   │  Data Aggregator │                                │   │
│  │                   │  (Unifies data)  │                                │   │
│  │                   └────────┬────────┘                                │   │
│  │                            ▼                                         │   │
│  │                   ┌─────────────────┐                                │   │
│  │                   │   State Store   │                                │   │
│  │                   │  (Reactive data)│                                │   │
│  │                   └─────────────────┘                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      CLI Adapter Layer                               │   │
│  │                                                                      │   │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │   │  gh adapter  │  │ glab adapter │  │ acli adapter │  ...         │   │
│  │   │  (GitHub)    │  │  (GitLab)    │  │  (Jira)      │              │   │
│  │   └──────┬───────┘  └──────┬───────┘  └──────┬───────┘              │   │
│  │          │                 │                 │                       │   │
│  │          └─────────────────┼─────────────────┘                       │   │
│  │                            ▼                                         │   │
│  │                   ┌─────────────────┐                                │   │
│  │                   │  Async Process   │                                │   │
│  │                   │    Manager       │                                │   │
│  │                   │ (Worker threads) │                                │   │
│  │                   └─────────────────┘                                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                      Plugin/Extension Layer                          │   │
│  │                                                                      │   │
│  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │   │
│  │   │  Entry Point │  │  Entry Point │  │  Entry Point │  ...         │   │
│  │   │  Plugin A    │  │  Plugin B    │  │  Plugin C    │              │   │
│  │   └──────────────┘  └──────────────┘  └──────────────┘              │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| **App** | Entry point, global state, screen management | `textual.app.App` subclass |
| **Screen** | Layout composition, major section containers | `textual.screen.Screen` subclass |
| **Widgets** | UI elements, event handling, display | `textual.widget.Widget` subclasses (DataTable, Static, etc.) |
| **DataSource** | Abstract interface for data providers | Abstract base class defining `fetch_pr()`, `fetch_issues()` |
| **CLI Adapter** | Execute external CLIs, parse output | Async subprocess wrapper per CLI tool |
| **Data Aggregator** | Merge data from multiple sources, unified format | Service class normalizing data structures |
| **State Store** | Reactive application state | Textual reactive variables or custom store |
| **Plugin Registry** | Discover and load plugins | `importlib.metadata.entry_points()` |
| **Worker Manager** | Execute async operations without blocking UI | Textual `@work` decorator or `run_worker()` |

## Recommended Project Structure

```
monocli/
├── src/
│   └── monocli/
│       ├── __init__.py          # Package version, entry point
│       ├── __main__.py          # `python -m monocli` entry
│       ├── app.py               # Main App class (Textual)
│       ├── screens/
│       │   ├── __init__.py
│       │   └── main_screen.py   # Primary dashboard screen
│       ├── widgets/
│       │   ├── __init__.py
│       │   ├── pr_table.py      # DataTable for PRs/MRs
│       │   └── issue_table.py   # DataTable for work items
│       ├── services/
│       │   ├── __init__.py
│       │   ├── aggregator.py    # Data aggregation service
│       │   └── state.py         # Reactive state management
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── base.py          # Abstract CLI adapter base
│       │   ├── github.py        # gh CLI adapter
│       │   ├── gitlab.py        # glab CLI adapter
│       │   └── jira.py          # acli/atlassian CLI adapter
│       ├── datasources/
│       │   ├── __init__.py
│       │   ├── base.py          # Abstract DataSource interface
│       │   ├── pr_source.py     # PR/MR data source interface
│       │   └── issue_source.py  # Work item source interface
│       ├── plugins/
│       │   ├── __init__.py
│       │   ├── registry.py      # Plugin discovery via entry_points
│       │   └── builtin/         # Built-in data sources as plugins
│       │       ├── __init__.py
│       │       ├── github_pr.py
│       │       ├── gitlab_pr.py
│       │       └── jira_issues.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── pr.py            # PR/MR dataclasses
│       │   └── issue.py         # Work item dataclasses
│       └── utils/
│           ├── __init__.py
│           └── async_utils.py   # Async subprocess helpers
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── css/
│   └── app.tcss                 # Textual CSS styles
├── pyproject.toml               # Project config, entry points
└── README.md
```

### Structure Rationale

- **`adapters/`**: Separates external CLI interaction from business logic. Each adapter handles one CLI tool.
- **`datasources/`**: Abstracts data retrieval, allowing plugins to implement new sources.
- **`services/`**: Contains business logic (aggregation, state management) independent of UI.
- **`plugins/`**: Implements plugin discovery. Built-in sources are themselves plugins.
- **`widgets/`**: Custom Textual widgets for specialized display needs.
- **`models/`**: Data classes ensure type safety and consistent data structures.

## Architectural Patterns

### Pattern 1: Worker-Based Async Operations

**What:** Use Textual's Worker API to run CLI commands without blocking the UI.

**When to use:** Any operation that calls external CLIs, makes network requests, or performs I/O that could take >50ms.

**Trade-offs:**
- ✅ UI remains responsive
- ✅ Workers can be cancelled (e.g., for exclusive operations)
- ✅ Automatic error handling and lifecycle management
- ⚠️ Must use `call_from_thread()` for UI updates from thread workers
- ⚠️ Worker results require event-based communication

**Example:**
```python
from textual import work
from textual.app import App
from textual.worker import get_current_worker

class MonoCLIApp(App):
    @work(exclusive=True)  # Cancel previous worker when new one starts
    async def fetch_prs(self, source: str) -> list[PullRequest]:
        """Fetch PRs in background without blocking UI."""
        adapter = self.get_adapter(source)
        return await adapter.fetch_pull_requests()
    
    def on_worker_state_changed(self, event) -> None:
        """Handle worker completion."""
        if event.state == WorkerState.SUCCESS:
            self.update_pr_table(event.worker.result)
```

### Pattern 2: Plugin Architecture via Entry Points

**What:** Use Python's `importlib.metadata.entry_points()` to discover plugins at runtime.

**When to use:** When you want third-party packages to extend Mono CLI with new data sources.

**Trade-offs:**
- ✅ Standard Python packaging mechanism
- ✅ No naming convention constraints
- ✅ Works with any packaging tool (setuptools, hatch, poetry)
- ⚠️ Requires plugin packages to declare entry points in `pyproject.toml`
- ⚠️ Slightly more complex for plugin authors

**Example:**
```python
# Plugin registration in pyproject.toml
# [project.entry-points.'monocli.datasources']
# github-pr = 'monocli.plugins.builtin.github_pr:GitHubPRSource'

# Discovery in registry.py
import sys
if sys.version_info >= (3, 10):
    from importlib.metadata import entry_points
else:
    from importlib_metadata import entry_points

def discover_datasources():
    return entry_points(group='monocli.datasources')
```

### Pattern 3: Adapter Pattern for CLI Wrappers

**What:** Abstract each external CLI tool behind a consistent interface.

**When to use:** Each CLI tool (gh, glab, acli) has different command syntax and output formats.

**Trade-offs:**
- ✅ Easy to add support for new CLI tools
- ✅ Easy to mock for testing
- ✅ Can swap CLI for API later without changing consumers
- ⚠️ Must parse different output formats (JSON preferred)
- ⚠️ Need to handle CLI availability detection

**Example:**
```python
from abc import ABC, abstractmethod
from typing import Optional
import asyncio

class CLIAdapter(ABC):
    """Abstract base for CLI adapters."""
    
    @property
    @abstractmethod
    def cli_name(self) -> str:
        """Name of the CLI binary (e.g., 'gh', 'glab')."""
        pass
    
    @abstractmethod
    async def is_available(self) -> bool:
        """Check if CLI is installed and accessible."""
        pass
    
    async def execute(self, *args: str) -> tuple[str, str, int]:
        """Execute CLI command, return (stdout, stderr, returncode)."""
        proc = await asyncio.create_subprocess_exec(
            self.cli_name, *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return stdout.decode(), stderr.decode(), proc.returncode

class GitHubAdapter(CLIAdapter):
    @property
    def cli_name(self) -> str:
        return 'gh'
    
    async def is_available(self) -> bool:
        stdout, _, code = await self.execute('--version')
        return code == 0
    
    async def fetch_pull_requests(self, repo: Optional[str] = None):
        args = ['pr', 'list', '--json', 'number,title,author,state,url']
        if repo:
            args.extend(['--repo', repo])
        stdout, _, code = await self.execute(*args)
        if code == 0:
            return json.loads(stdout)
        return []
```

### Pattern 4: Reactive State Management

**What:** Use Textual's reactive attributes for automatic UI updates when data changes.

**When to use:** When UI needs to reflect changing application state (loading, data updates, errors).

**Trade-offs:**
- ✅ Automatic UI updates when state changes
- ✅ Declarative, less boilerplate
- ✅ Type-safe with MyPy
- ⚠️ Must understand reactive lifecycle to avoid unnecessary updates
- ⚠️ Complex state graphs can become hard to debug

**Example:**
```python
from textual.reactive import reactive
from textual.widget import Widget

class DashboardState:
    """Reactive application state."""
    prs: reactive[list[PullRequest]] = reactive([], always_update=True)
    issues: reactive[list[Issue]] = reactive([], always_update=True)
    loading: reactive[bool] = reactive(False)
    error: reactive[str | None] = reactive(None)
    
    def watch_prs(self, prs: list[PullRequest]) -> None:
        """Called automatically when PRs change."""
        self.update_table(prs)
```

### Pattern 5: Message-Based Communication

**What:** Use Textual's message passing for loose coupling between components.

**When to use:** When widgets need to communicate without direct references, or when workers need to notify UI of progress.

**Trade-offs:**
- ✅ Loose coupling between components
- ✅ Easy to add new handlers without changing sender
- ✅ Works across thread boundaries (with `post_message`)
- ⚠️ Can be harder to trace than direct method calls
- ⚠️ Message handlers run on main thread

**Example:**
```python
from textual.message import Message

class DataLoaded(Message):
    """Message sent when data is loaded."""
    bubble = True  # Allow parent widgets to handle
    
    def __init__(self, source: str, data: list) -> None:
        self.source = source
        self.data = data
        super().__init__()

# In worker
@work(thread=True)
def fetch_data(self) -> None:
    worker = get_current_worker()
    data = slow_operation()
    if not worker.is_cancelled:
        # post_message is thread-safe
        self.post_message(DataLoaded('github', data))

# In parent widget
def on_data_loaded(self, message: DataLoaded) -> None:
    self.update_display(message.data)
```

## Data Flow

### Request Flow (User Refresh)

```
[User presses 'r']
         ↓
[App.on_key / App.action_refresh]
         ↓
[App.refresh_data] ──► [State.loading = True]
         ↓
[WorkerManager] ──► [Worker.fetch_all_sources] (concurrent)
         ↓
[DataSource.fetch] ──► [CLIAdapter.execute] ──► [asyncio.subprocess]
         ↓
[CLIAdapter.parse_output] ──► [Model instances]
         ↓
[DataAggregator.merge] ──► [Unified data structure]
         ↓
[State.prs/issues = data] (reactive update)
         ↓
[Widgets.watch_prs/issues] ──► [DataTable.update]
         ↓
[UI refreshed]
```

### Key Data Flows

1. **Initial Load Flow:**
   - App mounts → detect available CLIs → load enabled sources → trigger data fetch
   - Show loading indicator → spawn workers → update tables → hide loading indicator

2. **Refresh Flow:**
   - User action → cancel existing workers → spawn new workers → update state → UI refresh
   - Uses `exclusive=True` to prevent stale data from slow sources

3. **Plugin Load Flow:**
   - App start → discover entry points → import plugin modules → register data sources
   - Plugins add their adapters to the available sources pool

4. **Error Handling Flow:**
   - Worker error → Worker.StateChanged(ERROR) → display error toast → log details
   - Individual source errors don't block other sources

## Build Order & Dependencies

### Phase 1: Foundation (No UI)
1. **Models** (`models/pr.py`, `models/issue.py`)
   - Define data structures first
   - No dependencies

2. **CLI Adapters Base** (`adapters/base.py`)
   - Abstract interface
   - Depends on: Models

3. **Async Utilities** (`utils/async_utils.py`)
   - Subprocess helpers
   - No dependencies

### Phase 2: Core Services (Still No UI)
4. **CLI Adapter Implementations** (`adapters/github.py`, etc.)
   - Concrete implementations
   - Depends on: Adapters Base, Async Utils, Models

5. **DataSource Interface** (`datasources/base.py`)
   - Abstract data source
   - Depends on: Models

6. **State Management** (`services/state.py`)
   - Reactive state store
   - Depends on: Models

7. **Data Aggregator** (`services/aggregator.py`)
   - Merges data from sources
   - Depends on: DataSource, Models, State

### Phase 3: UI Layer
8. **Custom Widgets** (`widgets/pr_table.py`, `widgets/issue_table.py`)
   - DataTable subclasses
   - Depends on: Models, State

9. **Main Screen** (`screens/main_screen.py`)
   - Layout composition
   - Depends on: Widgets, State

### Phase 4: Integration
10. **Main App** (`app.py`)
    - App orchestration
    - Depends on: Everything else

11. **Plugin System** (`plugins/registry.py`, `plugins/builtin/`)
    - Entry point discovery
    - Can be built in parallel with App
    - Depends on: DataSource

### Dependency Graph

```
Models
  │
  ├──► Adapters Base
  │      │
  │      ├──► GitHub Adapter ───┐
  │      ├──► GitLab Adapter ───┤
  │      └──► Jira Adapter ─────┤
  │                             │
  ├──► DataSource Base ◄────────┤
  │      │                      │
  │      └──► Built-in Plugins ─┤
  │                             │
  ├──► State ───────────────────┼──► Aggregator
  │                             │
  └──► Widgets ◄────────────────┘
           │
           └──► Main Screen
                    │
                    └──► App
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Blocking the UI Thread

**What:** Calling synchronous subprocess or network code directly in event handlers.

**Why bad:** UI freezes, keystrokes delayed, app feels unresponsive.

**Instead:** Always use `@work` decorator or `run_worker()` for I/O operations.

```python
# BAD - blocks UI
async def on_button_pressed(self):
    result = subprocess.run(['gh', 'pr', 'list'])  # Blocks!
    self.update(result)

# GOOD - non-blocking
@work(exclusive=True)
async def on_button_pressed(self):
    result = await self.adapter.fetch_prs()  # Runs in worker
    self.update(result)
```

### Anti-Pattern 2: Direct UI Updates from Threads

**What:** Calling widget methods from a `thread=True` worker without using `call_from_thread()`.

**Why bad:** Textual widgets are not thread-safe. Race conditions, crashes, or corruption.

**Instead:** Use `call_from_thread()` for UI updates, or post messages.

```python
# BAD - not thread-safe
@work(thread=True)
def fetch_data(self):
    data = slow_operation()
    self.table.update(data)  # CRASH!

# GOOD - thread-safe
@work(thread=True)
def fetch_data(self):
    worker = get_current_worker()
    data = slow_operation()
    if not worker.is_cancelled:
        self.call_from_thread(self.table.update, data)

# ALSO GOOD - messages are thread-safe
@work(thread=True)
def fetch_data(self):
    data = slow_operation()
    self.post_message(DataLoaded(data))
```

### Anti-Pattern 3: Tight Coupling to CLI Tools

**What:** CLI command strings scattered throughout business logic.

**Why bad:** Hard to test, hard to change CLI versions, hard to mock.

**Instead:** Encapsulate in adapter classes with well-defined interfaces.

### Anti-Pattern 4: Synchronous Plugin Loading

**What:** Importing and initializing plugins during app startup without workers.

**Why bad:** Slow plugin discovery blocks UI from appearing.

**Instead:** Load plugins in a worker, show loading state, then initialize UI.

### Anti-Pattern 5: Shared Mutable State Without Reactivity

**What:** Multiple widgets modifying shared state without Textual's reactive system.

**Why bad:** UI gets out of sync, race conditions, hard to debug.

**Instead:** Use `reactive` attributes and `watch_*` methods for state changes.

## Scalability Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| **1-3 data sources** | All adapters in-process, direct CLI calls, simple aggregation |
| **5-10 data sources** | Consider connection pooling for CLI calls, caching layer for data |
| **10+ data sources** | Plugin isolation (subprocess per plugin), rate limiting, background refresh |
| **Large datasets** | Pagination in DataTable, virtual scrolling, lazy loading |

### Performance Priorities

1. **First priority:** Non-blocking UI (Workers API)
2. **Second priority:** Parallel data fetching (`asyncio.gather`)
3. **Third priority:** Caching (TTL cache for CLI responses)
4. **Fourth priority:** Incremental updates (only changed rows)

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| **GitHub CLI (gh)** | Async subprocess via adapter | Parse JSON output with `--json` flag |
| **GitLab CLI (glab)** | Async subprocess via adapter | Similar pattern to gh |
| **Jira CLI (acli)** | Async subprocess via adapter | May need custom parsing |
| **Future: REST APIs** | httpx/aiohttp in workers | Same adapter interface, swap implementation |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| **UI ↔ Services** | Reactive state + Messages | UI watches state, services post messages |
| **Services ↔ Adapters** | Async method calls | Adapters expose async interface |
| **Adapters ↔ CLI** | Async subprocess | Use `asyncio.create_subprocess_exec()` |
| **Core ↔ Plugins** | Entry points + Abstract base | Plugins implement DataSource interface |

## Sources

- Textual Workers API: https://textual.textualize.io/guide/workers/ (HIGH confidence)
- Textual App Basics: https://textual.textualize.io/guide/app/ (HIGH confidence)
- Textual Events: https://textual.textualize.io/guide/events/ (HIGH confidence)
- Textual DataTable: https://textual.textualize.io/widgets/data_table/ (HIGH confidence)
- Python Plugin Discovery: https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/ (HIGH confidence)
- Python Async Subprocess: https://docs.python.org/3/library/asyncio-subprocess.html (HIGH confidence)

---
*Architecture research for: Mono CLI - Python TUI CLI Aggregator*
*Researched: 2025-02-07*

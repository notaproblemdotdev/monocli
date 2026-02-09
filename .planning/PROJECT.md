# Mono CLI

## What This Is

A unified terminal user interface (TUI) that aggregates work items and pull/merge requests from multiple developer platforms into a single dashboard. Built with the Textual framework, it calls existing CLI tools (gh, glab, acli) that are already authenticated, providing a cohesive view of what the user needs to work on across Jira, GitHub, and GitLab.

## Core Value

One dashboard showing all assigned work items and pending PRs/MRs without switching between browser tabs or context switching between platforms.

## Requirements

### Validated (v1.0)

- ✓ TUI framework using Textual renders two-section dashboard — v1.0
- ✓ Auto-detect which CLIs are installed (gh, glab, acli) and show only corresponding sections — v1.0
- ✓ Dashboard displays all sections from start with per-section loading spinners — v1.0
- ✓ Async data fetching without blocking UI — v1.0
- ✓ PRs/MRs section: merge/pull requests assigned to user OR created by user — v1.0
- ✓ Work Items section: issues assigned to user that are not closed — v1.0
- ✓ Display format for each item: Key + Title + Status + Priority — v1.0
- ✓ Press 'o' key to open selected item in default browser — v1.0
- ✓ Structured logging with structlog — v1.0
- ✓ Configurable log levels via LOG_LEVEL env var — v1.0

### Active (v2.0)

- [ ] **GitHub Support** — Add GitHub CLI adapter for PRs and Issues
- [ ] Auto-refresh capability for keeping data current
- [ ] Manual refresh capability (r/F5) for forcing updates
- [ ] Background reload without blocking UI interactions
- [ ] Search/filter functionality (press '/' to filter)
- [ ] Help screen (? key) for keyboard shortcuts
- [ ] Configuration file support (~/.config/monocli/config.yaml)

### Out of Scope

- **In-TUI code review/editing** — Terminal is poor for these tasks; redirect to browser
- **Real-time notifications** — Out of v1 scope; focus on on-demand dashboard view
- **Modifying items from CLI** — View-only in v1, editing via web interface
- **Custom theming** — Standard Textual themes sufficient for MVP
- **Offline mode** — Requires active internet connection to fetch data
- **Caching strategies** — Fresh fetch on load, caching may be added in v2
- **Non-terminal interfaces** — TUI-only, no web or desktop versions

## Context

**Current State:** v1.0 shipped — 4 phases, 15 plans, 6,593 LOC Python

**Tech Stack:**
- Python 3.13+ with Textual 7.x framework
- Pydantic for data validation
- structlog for structured logging
- UV for dependency management
- Ruff for linting/formatting
- MyPy for type checking
- pytest for testing

**Target Users:** Developers working with Jira, GitHub, and/or GitLab who prefer terminal interfaces over browser-based UIs and want a unified view of their work.

**Problem Being Solved:** Context switching between multiple browser tabs (Jira for issues, GitHub/GitLab for PRs) to see what's on the user's plate. This tool provides a single command (`monocli`) that aggregates everything in one view.

**Data Sources:**
- **GitLab:** `glab` CLI for merge requests (✓ implemented)
- **Jira:** `acli` CLI for work items (✓ implemented)
- **GitHub:** `gh` CLI for pull requests (planned for v2.0)

**Authentication:** Relies on existing CLI authentication; no separate auth mechanism needed.

**Architecture Approach:**
- Plugin-style architecture for different data sources (CLI adapters)
- Each source has its own async loader using Textual Workers API
- Loading states per section with spinners
- Non-blocking UI throughout
- asyncio.Semaphore(3) for subprocess concurrency control

## Constraints

- **Tech stack:** Python with Textual framework for TUI
- **Dependencies:** Requires `glab` and/or `acli` CLIs to be installed and authenticated (GitHub support planned)
- **Package management:** UV (from Astral) for dependency management
- **Code quality:** Ruff (from Astral) for linting and formatting
- **Type checking:** MyPy for static type analysis
- **Testing:** pytest for unit and integration tests
- **Async requirement:** Must load data asynchronously without blocking UI
- **UI responsiveness:** Background reloads must not freeze or interrupt user interaction
- **Layout:** Two main sections — PRs/MRs and Work Items

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Use Textual framework | Modern Python TUI library with async support | ✓ Good — excellent async support, reactive properties |
| Shell out to existing CLIs vs APIs | Reuse existing auth, simpler implementation | ✓ Good — zero auth complexity, uses existing tools |
| Per-section loading spinners | Users see dashboard immediately, async feedback | ✓ Good — clear UX pattern, immediate feedback |
| 'o' key for opening browser | Vim-style convention familiar to CLI users | ✓ Good — intuitive for target audience |
| Two-section layout | Logical grouping by task type vs source | ✓ Good — mental model matches user workflow |
| Auto-detect CLIs vs explicit config | Better UX — zero-config experience | ✓ Good — works out of box if CLIs installed |
| UV for dependency management | Fast, modern Python package manager | ✓ Good — fast installs, good lock file |
| Ruff for linting/formatting | Fast, unified Python linter | ✓ Good — single tool covers everything |
| MyPy for type checking | Industry standard for Python | ✓ Good — strict mode catches bugs early |
| pytest for testing | Modern, flexible Python testing | ✓ Good — pytest-asyncio handles async tests well |
| structlog for logging | Structured JSON logging for production | ✓ Good — both human and machine readable |
| asyncio.Semaphore(3) | Limit concurrent subprocess execution | ✓ Good — prevents race conditions |

## Current Milestone: v2.0 Extended Platform Support

**Goal:** Add GitHub and Todoist integrations for comprehensive work item coverage across all major platforms

**Target features:**
- **GitHub CLI adapter** — Fetch PRs and Issues via `gh` CLI
- **Todoist CLI adapter** — Fetch tasks via Todoist CLI or API
- **Unified Tasks section** — Combine Todoist tasks with existing work items
- **Enhanced PRs section** — Add GitHub PRs alongside GitLab MRs
- **Manual refresh capability** — r/F5 key to reload data
- **Help screen** — ? key for keyboard shortcuts reference
- **Configuration file support** — ~/.config/monocli/config.yaml for preferences

---

*Last updated: 2026-02-09 after v1.0 milestone completion*
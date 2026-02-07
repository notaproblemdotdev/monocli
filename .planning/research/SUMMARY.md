# Project Research Summary

**Project:** Mono CLI  
**Domain:** Python TUI Dashboard for GitHub/GitLab PRs and Jira Issues  
**Researched:** February 7, 2026  
**Confidence:** HIGH

## Executive Summary

Mono CLI is a unified terminal dashboard aggregating work items and pull/merge requests from Jira, GitHub, and GitLab. Based on analysis of successful TUI tools (lazygit, k9s) and CLI aggregators, this product fits the **Python TUI CLI aggregator** pattern—using Textual framework to wrap existing platform CLIs rather than implementing custom API integrations.

The recommended approach is a **layered architecture** with Textual 7.5.0 as the TUI framework, implementing worker-based async operations for all external CLI calls. This pattern is well-documented and battle-tested. The core value proposition is **multi-platform aggregation** with a **keyboard-first interface**—showing PRs/MRs and issues from all platforms in a single view with vim-style navigation.

Key risks center on **async/concurrency handling**: blocking the UI thread, race conditions with rapid navigation, and thread-safety violations are the top failure modes. These are mitigated by strict use of Textual's Workers API with `@work(exclusive=True)` and proper `call_from_thread()` usage for UI updates. Platform CLI availability and authentication are secondary risks requiring graceful degradation.

## Key Findings

### Recommended Stack

The stack is built around **Textual 7.5.0** (released Jan 30, 2026), the definitive Python TUI framework with declarative CSS-like styling, reactive data model, and sophisticated async Workers API. All versions have been verified with official sources as of February 7, 2026.

**Core technologies:**
- **Textual 7.5.0**: TUI framework with reactive data model, built-in DataTable widget, and Workers API for async operations — recommended as the modern standard, replacing curses/npyscreen
- **Rich 14.3.2**: Terminal rendering/styling (Textual dependency) — provides beautiful formatting and markup
- **Pydantic 2.12.5**: Data validation and modeling — parse and validate CLI JSON outputs from gh/glab/acli
- **UV (latest)**: Package management — 10-100x faster than pip, required per project constraints
- **Ruff 0.15.0**: Linting and formatting — replaces Flake8, Black, isort in one tool
- **MyPy 1.19.1**: Type checking — gold standard, use with `--strict`
- **pytest 9.0.2 + pytest-asyncio 1.3.0**: Testing — Textual provides `Pilot` class for UI testing

**Python version:** 3.10+ required (Textual minimum), 3.12 or 3.13 recommended for best performance.

### Expected Features

Based on analysis of lazygit (71.9k★), k9s (32.7k★), and gh CLI (42.4k★), successful TUI tools prioritize **keyboard-driven workflows**, **non-blocking async operations**, and **progressive disclosure**.

**Must have (table stakes):**
- Keyboard Navigation — vim-style bindings (j/k, gg/G, / for search) — users expect this from TUI tools
- Real-time Data Loading — async loading without blocking UI with spinner/progress indicator
- Search/Filter — `/` to filter, `n/N` for next/previous match
- Browser Integration — `o` key opens selected item in browser
- Manual Refresh — `r` key refreshes data with last-updated timestamp
- Status Indicators — color coding + icons for open/closed/merged states
- Error Handling — graceful failures when APIs are unreachable
- Help System — `?` shows context-sensitive keybindings

**Should have (competitive):**
- Multi-Platform Aggregation — single view across Jira/GitHub/GitLab (core differentiator)
- Auto-Platform Detection — zero-config startup, detects installed CLIs
- Smart Auto-Refresh — background polling every 5 minutes
- Unified Priority View — cross-platform priority ranking
- Offline Mode — view cached data when disconnected

**Defer (v2+):**
- Contextual Actions — approve PR, transition Jira issue (requires write API)
- Unified Search — fuzzy matching across all platforms
- Plugin System — custom platform adapters

**Anti-features to avoid:** In-TUI code review, full issue editing, custom authentication (delegate to platform CLIs), git operations (separate from lazygit), complex theming.

### Architecture Approach

Recommended architecture uses **5 layers**: UI Layer (Textual widgets/screens), Application Services Layer (DataSource, Data Aggregator, State Store), CLI Adapter Layer (gh/glab/acli adapters), and Plugin/Extension Layer (entry points).

**Major components:**
1. **App/Screens** — Entry point and layout composition using Textual's Screen system
2. **Widgets** — Custom DataTable subclasses for PR/MR and issue display
3. **CLI Adapters** — Abstract base with concrete implementations per platform CLI (gh, glab, acli)
4. **DataSource** — Abstract interface for data providers, implemented as plugins
5. **Data Aggregator** — Service class normalizing and merging platform-specific data
6. **State Store** — Reactive application state using Textual's reactive variables
7. **Plugin Registry** — Entry point discovery via `importlib.metadata.entry_points()`

**Key patterns:**
- Worker-Based Async Operations — `@work(exclusive=True)` for all CLI calls
- Adapter Pattern — Abstract each CLI behind consistent interface
- Reactive State Management — Textual reactive attributes for automatic UI updates
- Message-Based Communication — Loose coupling between components

### Critical Pitfalls

From PITFALLS.md analysis, the following are the most dangerous failure modes:

1. **Blocking the UI Thread with Synchronous Subprocess Calls** — UI freezes, keypresses lost, app appears crashed. **Avoid by:** Always use `asyncio.create_subprocess_exec()` and `@work()` decorator with `exclusive=True`. Never use `subprocess.run()` in event handlers.

2. **Race Conditions with Rapid User Actions** — Stale data overwrites fresh data when responses arrive out of order. **Avoid by:** Use `@work(exclusive=True)` to cancel previous workers, track request IDs, implement debouncing for search-as-you-type.

3. **Thread Safety Violations When Updating UI** — Random crashes, corrupted UI state. **Avoid by:** Use `self.call_from_thread(widget.update, data)` for UI updates from threads, or post messages with `post_message()` (thread-safe).

4. **Inconsistent CLI Output Parsing Across Tools** — Data missing, parser crashes due to different JSON schemas. **Avoid by:** Create abstraction layer normalizing outputs, use `--json` flags, implement defensive parsing with Pydantic defaults.

5. **Orphaned Subprocesses and Resource Leaks** — Zombie processes accumulate. **Avoid by:** Always `await proc.wait()` or use `asyncio.wait_for()` with timeouts, implement cleanup in `on_unmount`.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Foundation (No UI)
**Rationale:** Data models and async infrastructure must be solid before UI. These components have no dependencies and form the base of the dependency graph.
**Delivers:** Data models, CLI adapter base class, async subprocess utilities, one complete adapter implementation (GitHub)
**Addresses:** Platform CLI Detection (table stakes)
**Avoids:** Blocking UI thread, orphaned subprocesses, race conditions
**Research Flag:** Standard patterns, skip research-phase

### Phase 2: Core Services (No UI)
**Rationale:** Services layer implements business logic independent of UI. Can be fully tested before widgets exist.
**Delivers:** DataSource interface, State management, Data Aggregator, GitLab and Jira adapters
**Uses:** Pydantic models, pytest-asyncio
**Implements:** Adapter pattern, reactive state pattern
**Avoids:** Thread safety violations, inconsistent parsing, silent failures
**Research Flag:** CLI-specific parsing quirks may need `/gsd-research-phase` for acli/atlassian CLI

### Phase 3: UI Layer
**Rationale:** UI depends on services layer. Textual patterns are well-documented.
**Delivers:** Custom widgets (PR table, issue table), Main screen layout, Help overlay
**Addresses:** Keyboard navigation, real-time loading, search/filter, browser integration, manual refresh, status indicators
**Uses:** Textual 7.5.0, Textual CSS
**Avoids:** Blocking UI thread (via workers), race conditions (via exclusive workers)
**Research Flag:** Standard patterns, skip research-phase

### Phase 4: Integration & Polish
**Rationale:** Connect all layers, handle edge cases, add caching.
**Delivers:** Main App orchestration, Plugin system, Auto-refresh, Offline cache, Error handling
**Addresses:** Auto-platform detection, auto-refresh, offline mode, error handling
**Avoids:** All critical pitfalls
**Research Flag:** Plugin entry points well-documented; skip research-phase

### Phase Ordering Rationale

The order follows the **dependency graph**: Models → Adapters → Services → Widgets → Screens → App. This architecture-first approach ensures:
- Business logic is testable without UI (Phases 1-2)
- UI is thin layer over services (Phase 3)
- Each layer validates before next builds on it
- Critical async patterns established early (Phase 1)

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 2 (Jira/acli adapter):** Atlassian CLI has sparse documentation and inconsistent JSON output. Recommend `/gsd-research-phase` for acli-specific parsing before implementation.

Phases with standard patterns (skip research-phase):
- **Phase 1:** Async subprocess patterns well-documented in Python/Textual docs
- **Phase 3:** Textual widget patterns established, DataTable extensively documented
- **Phase 4:** Plugin entry points standard Python packaging mechanism

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All versions verified with official sources (GitHub releases, PyPI). Textual 7.5.0 released Jan 30, 2026. |
| Features | HIGH | Well-established patterns from mature tools (lazygit, k9s). MVP scope validated against competitor analysis. |
| Architecture | HIGH | Official Textual docs, Python packaging guides. Patterns verified against lazygit/k9s architecture. |
| Pitfalls | HIGH | Official Textual Workers docs, Python asyncio docs, GitHub Discussions analysis. |

**Overall confidence:** HIGH

All research areas have HIGH confidence based on official documentation and established patterns in production tools. The primary uncertainty is the Atlassian CLI (acli) output format, which should be researched during Phase 2 planning.

### Gaps to Address

| Gap | How to Handle |
|-----|---------------|
| Atlassian CLI (acli) JSON schema | Research during Phase 2 planning; may need manual testing with actual CLI output |
| Platform rate limiting strategy | Implement basic respect in Phase 2; refine during Phase 4 if needed |
| Windows-specific CLI behavior | Cross-platform testing in Phase 4; documented as risk in PITFALLS.md |
| Authentication state detection | Implement per-CLI status checks in Phase 2; patterns documented in PITFALLS.md |

## Sources

### Primary (HIGH confidence)
- **Textual 7.5.0** — GitHub releases (verified Feb 7, 2026): https://github.com/Textualize/textual/releases/tag/v7.5.0
- **Textual Workers API** — Official docs: https://textual.textualize.io/guide/workers/
- **Textual Testing Guide** — Official docs: https://textual.textualize.io/guide/testing/
- **Textual Events** — Official docs: https://textual.textualize.io/guide/events/
- **Ruff 0.15.0** — GitHub releases (verified Feb 7, 2026): https://github.com/astral-sh/ruff/releases/tag/0.15.0
- **MyPy 1.19.1** — PyPI (verified Feb 7, 2026): https://pypi.org/project/mypy/
- **pytest 9.0.2** — GitHub releases (verified Feb 7, 2026): https://github.com/pytest-dev/pytest/releases/tag/9.0.2
- **Python asyncio.subprocess** — Python 3.14 docs: https://docs.python.org/3/library/asyncio-subprocess.html
- **Python Plugin Discovery** — PyPA packaging guide: https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/

### Secondary (MEDIUM confidence - competitor patterns)
- **lazygit** (https://github.com/jesseduffield/lazygit) — TUI patterns, keyboard navigation, async operations
- **k9s** (https://github.com/derailed/k9s) — Dashboard patterns, filtering, real-time updates
- **gh CLI** (https://github.com/cli/cli) — GitHub API integration, authentication patterns

### Tertiary (LOW confidence - needs validation)
- **Atlassian CLI (acli)** — Output format specifications sparse; requires manual testing

---
*Research completed: February 7, 2026*  
*Ready for roadmap: yes*

# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2025-02-07)

**Core value:** One dashboard showing all assigned work items and pending PRs/MRs without switching between browser tabs or context switching between platforms.
**Current focus:** Phase 2 - CLI Adapters

## Current Position

Phase: 3 of 4 (Dashboard UI - Gap Closure)
Plan: 7 of 7 in current phase (Fix keyboard navigation issues)
Status: Phase complete (all gaps closed)
Last activity: 2026-02-09 — Completed 03-07-PLAN.md (Fix keyboard navigation issues)

Progress: [██████████] 100% (14 of 14 total plans)

## Performance Metrics

**Velocity:**
- Total plans completed: 14
- Average duration: 4.6 min
- Total execution time: 1.07 hours

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Foundation | 3/3 | 12m 33s | 4m 11s |
| 2. CLI Adapters | 3/3 | 14m 0s | 4m 40s |
| 3. Dashboard UI | 6/6 | 18m 0s | 3m 0s |
| 4. Add Logging | 1/1 | 8m 0s | 8m 0s |

**Recent Trend:**
- Last 5 plans: 03-05 (auth command), 03-06 (2m - UI fixes), 04-01 (8m), 03-07 (4m - keyboard nav)
- Trend: Gap closure complete - Dashboard UI now fully functional

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Initialization: Use Textual framework for TUI (modern async support)
- Initialization: Shell out to existing CLIs vs APIs (reuse existing auth)
- Initialization: UV for dependency management, Ruff for linting, MyPy for type checking

**New from 01-01:**
- Use src/ layout for better package isolation and testing
- Configure Ruff with comprehensive lint rules (E, F, I, N, W, UP, B, C4, SIM)
- Enable strict MyPy type checking for early error detection
- Use pytest-asyncio for testing async code in future phases

**New from 01-02:**
- Use BeforeValidator for datetime parsing from ISO 8601 JSON strings
- Standardize helper interface: display_key(), display_status(), is_open() on all models
- Pattern validation with regex for Jira keys (PROJECT-123 format)
- Strict mode with ConfigDict for early type error detection

**New from 01-03:**
- Use asyncio.create_subprocess_exec over subprocess.run for true async execution
- Implement @work(exclusive=True) pattern to prevent data fetching race conditions
- Create CLIAdapter base class for consistent CLI interface across platforms
- Use TypeVar for generic model parsing in fetch_and_parse()
- Cache CLI availability check in adapter to avoid repeated which() calls

**New from 02-01:**
- Use TypedDict for DetectionResult to provide clear field names and type safety
- Cache detection results at registry level after first detect_all() call
- Use lightweight auth check commands (e.g., "auth status") rather than data fetching
- Return copies of cached results to prevent external mutation
- Clear cache when new detector registered to ensure freshness
- Registry pattern: register detectors, detect_all returns all results, query methods filter

**New from 02-02:**
- CLI Adapter pattern: Inherit from CLIAdapter, implement fetch_* and check_auth methods
- glab mr list --json with --author and --state filters for targeted fetching
- check_auth() returns boolean (not exception) for detection flow compatibility
- Mock asyncio.create_subprocess_exec for async CLI testing

**New from 02-03:**
- acli whoami for lightweight Jira auth checking
- acli jira issue list --json with --assignee and --status filters
- Bug fix: Add 'not authenticated' to CLIAuthError.AUTH_PATTERNS
- Jira API URL to browser URL transformation in model property

**New from 03-01:**
- Textual reactive properties for data binding in widgets
- SectionState enum for explicit UI state management (LOADING, EMPTY, ERROR, DATA)
- Base class pattern for shared section functionality
- DataTable with zebra_stripes for readability
- Row keys for storing item URLs (for browser integration)
- Title truncation with ellipsis (40 char limit)
- Pilot API with TestApp wrapper for widget testing

**New from 03-02:**
- Nested @work decorator pattern for fire-and-forget async workers
- DetectionRegistry with CLIDetector instances for CLI availability checking
- Reactive active_section property with CSS border highlight
- Fire-and-forget workers with `_ = worker_func()` to silence warnings
- MainScreen.compose() stores section references as instance attributes
- Error handling per section (CLI not found, not authenticated, network errors)

**New from 03-03:**
- Textual BINDINGS with action_* methods for keyboard navigation
- Tab key switches active section with CSS border highlighting
- j/k and arrow keys navigate items within focused section
- 'o' key opens selected item URL in default browser via webbrowser module
- Section-scoped selection (each DataTable maintains independent cursor)
- Row keys store URLs for reliable lookup in get_selected_url()
- on_key() handler for custom key event processing
- Pilot API for integration testing keyboard navigation
- Silent error handling for browser open failures

**New from 03-04 (Gap Closure - Workers API):**
- Migrated from deprecated @work decorator to Textual 7.x run_worker() API
- self.run_worker(self.fetch_method(), exclusive=True) replaces @work(exclusive=True)
- Workers now properly execute and resolve loading spinners to data/empty/error states
- Textual 7.x compatibility achieved, no deprecated APIs used

**New from 03-05 (Gap Closure - Auth Command):**
- acli jira auth status is the correct command for auth checking
- acli whoami doesn't exist and was causing auth check failures
- Consistent auth command between JiraAdapter and CLIDetector

**New from 04-01 (Add Logging):**
- Use structlog for structured JSON logging with processor chain
- Console output: human-readable format (ConsoleRenderer)
- File output: JSON format for production/analysis
- Log directory: ~/.local/share/monocli/logs/monocli_YYYY-MM-DD.log
- Support LOG_LEVEL env variable (DEBUG, INFO, WARNING, ERROR)
- Add --debug CLI flag for verbose logging
- Implement sensitive data filtering processor for security

**New from 04-02 (Fix asyncio subprocess race condition):**
- Use asyncio.Semaphore(3) to limit concurrent subprocess execution
- Keep semaphore locked for entire subprocess lifecycle (creation → communication → cleanup)
- Add await proc.wait() in finally block to ensure proper process cleanup
- Prevents asyncio.exceptions.InvalidStateError from transport cleanup race conditions

**New from 03-07 (Fix keyboard navigation):**
- Handle Textual's RowKey wrapper objects with hasattr(row_key, 'value') check
- Use focus_table() not focus() when targeting DataTable for keyboard navigation
- Add explicit action_quit() to screens for consistent quit behavior

### Roadmap Evolution

- Phase 4 added: Add proper logging with structlog

### Pending Todos

None yet.

### Blockers/Concerns

None yet.

## Session Continuity

Last session: 2026-02-09T20:37:45Z
Stopped at: Completed 03-07-PLAN.md (Fix keyboard navigation issues)
Resume file: None

## Operational Notes

**Log Location:** Application logs are stored at `~/.local/share/monocli/logs/`
- Log files: `monocli_YYYY-MM-DD.log` (JSON format)
- Console output: Human-readable with colors (real-time)
- Debug mode: `uv run monocli --debug` (verbose logging)
- Log levels: Controlled via `LOG_LEVEL` environment variable

## Next Phase

**Phase 3 Dashboard UI - All Gaps Closed!**

All UAT gaps have been resolved:
- Gap 4: 'o' key opens browser ✓ (RowKey.value handling)
- Gap 5: Tab navigation works ✓ (focus_table())
- Gap 6: 'q' key quits ✓ (binding added)

The dashboard is now fully functional with:
- Proper keyboard navigation (Tab, arrows, j/k)
- Browser integration ('o' key)
- Clean quit ('q' key)

**All Phases Complete!**

The project v1 is now fully implemented with:
- **Phase 1: Foundation** - Models, async utils, exceptions
- **Phase 2: CLI Adapters** - GitLab, Jira, detection infrastructure
- **Phase 3: Dashboard UI** - Textual TUI with navigation and browser integration
- **Phase 4: Add Logging** - Structured logging with structlog

**Project v1 is feature complete!**

Future steps could include:
- v2 features: refresh (r/F5), search/filter (/), help (?), GitHub support
- Documentation improvements
- Packaging and distribution

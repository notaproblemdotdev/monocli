---
phase: 03-dashboard-ui
plan: 01
subsystem: ui
tags: [textual, datatable, widgets, tui, reactive]

# Dependency graph
requires:
  - phase: 02-cli-adapters
    provides: GitLabAdapter, JiraAdapter for fetching data
provides:
  - MergeRequestSection widget with DataTable for MR display
  - WorkItemSection widget with DataTable for Jira work items
  - BaseSection base class with loading/empty/error states
  - SectionState enum for state management
affects:
  - 03-02-main-screen (will compose these widgets into main screen)
  - 03-03-keyboard-navigation (will use get_selected_url for browser opening)

# Tech tracking
tech-stack:
  added: []
  patterns:
    - Textual reactive properties for data binding
    - Base class pattern for shared section functionality
    - State machine pattern for UI states (loading/empty/error/data)
    - Pilot API for integration testing

key-files:
  created:
    - src/monocli/ui/__init__.py
    - src/monocli/ui/sections.py
    - tests/ui/__init__.py
    - tests/ui/test_sections.py
  modified: []

key-decisions:
  - "Renamed set_loading() to show_loading() to avoid conflict with Textual Widget base class"
  - "Used zebra_stripes=True on DataTable for better readability"
  - "Stored URLs as row keys for browser integration in later phases"
  - "Used ellipsis truncation for long titles (40 char limit)"

patterns-established:
  - "BaseSection: Abstract common section behavior (title, loading spinner, state management)"
  - "SectionState enum: Explicit states (LOADING, EMPTY, ERROR, DATA)"
  - "Widget composition: Use Vertical/Horizontal containers for layout"
  - "State transitions: show_loading() → update_data() or set_error() → state changes UI"

# Metrics
duration: 4 min
completed: 2026-02-08
---

# Phase 03 Plan 01: Section Widgets Summary

**Textual DataTable section widgets for merge requests and work items with loading, empty, and error states**

## Performance

- **Duration:** 4 min
- **Started:** 2026-02-08T10:13:09Z
- **Completed:** 2026-02-08T10:17:09Z
- **Tasks:** 4 completed
- **Files created:** 4

## Accomplishments

- Created BaseSection base class with shared functionality for loading, empty, and error states
- Implemented MergeRequestSection with columns: Key, Title, Status, Author, Branch, Created
- Implemented WorkItemSection with columns: Key, Title, Status, Priority, Assignee, Created
- Added loading spinner that appears alongside section titles (not replacing content)
- Added empty state messages: "No merge requests found" and "No assigned work items"
- Added error state display in content area
- Implemented title truncation with ellipsis for titles over 40 characters
- Added item count display in section title when data loaded (e.g., "Merge Requests (3)")
- Created 16 integration tests using Textual's Pilot API

## Task Commits

Each task was committed atomically:

1. **Task 1: Create UI package structure** - `002726a` (chore)
2. **Task 2: Create section widgets** - `f2b11c0` (feat)
3. **Task 3: Create integration tests** - `c9e3f2b` (test)
4. **Task 4: Fix set_loading conflict** - `d449fd0` (fix)

**Plan metadata:** [to be committed]

## Files Created/Modified

- `src/monocli/ui/__init__.py` - UI package exports
- `src/monocli/ui/sections.py` - Section widget implementations (381 lines)
  - BaseSection: Base class with state management
  - SectionState: Enum-like class for states
  - MergeRequestSection: MR display widget
  - WorkItemSection: Jira work item display widget
- `tests/ui/__init__.py` - Test package
- `tests/ui/test_sections.py` - Widget integration tests (399 lines)

## Decisions Made

1. **Renamed set_loading() to show_loading()**: The Widget base class already has a set_loading() method with a different signature. Renamed our method to avoid the conflict.

2. **Used zebra_stripes on DataTable**: Improves readability for data-dense tables.

3. **Stored URLs as row keys**: DataTable row keys can store the URL string, making it easy to retrieve for browser opening in the next phase.

4. **40 character title truncation**: Keeps table widths reasonable while showing meaningful title previews.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

1. **Textual Pilot API**: Initially tried to use Pilot directly with widgets, but Pilot requires an App context. Created a TestApp wrapper class to enable testing.

2. **DataTable columns API**: Textual's DataTable uses ColumnKey objects. Fixed tests to use `ordered_columns` property instead of direct column access.

## Next Phase Readiness

Ready for 03-02-PLAN.md (Main Screen):
- Section widgets are complete and tested
- Both widgets expose `update_data()` for async data fetching
- Both widgets expose `get_selected_url()` for browser integration
- State management is solid (loading → data/error/empty transitions work)

---
*Phase: 03-dashboard-ui*
*Completed: 2026-02-08*

---
phase: 03-dashboard-ui
plan: 05
subsystem: cli-adapters
tags: [acli, jira, auth, cli-detection]

# Dependency graph
requires:
  - phase: 02-cli-adapters
    provides: JiraAdapter.check_auth() and CLIDetector registration patterns
provides:
  - Valid acli auth check command in JiraAdapter
  - Consistent auth command in CLIDetector registration
affects:
  - Any code depending on acli authentication checks

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Command consistency: Adapter and Detector use same CLI commands"
key-files:
  created: []
  modified:
    - src/monocli/adapters/jira.py
    - src/monocli/ui/main_screen.py
key-decisions:
  - "acli jira auth status is the correct command for auth checking (whoami doesn't exist)"
patterns-established: []

# Metrics
duration: 2min
completed: 2026-02-08
---

# Phase 3 Plan 5: Fix acli Auth Check Command Summary

**Replaced invalid `acli whoami` command with valid `acli jira auth status` for authentication checking across adapter and detector.**

## Performance

- **Duration:** 2 min
- **Started:** 2026-02-08T11:20:00Z
- **Completed:** 2026-02-08T11:22:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- Fixed JiraAdapter.check_auth() to use valid acli command
- Updated CLIDetector registration to use consistent auth command
- Verified all adapter tests pass

## Task Commits

Each task was committed atomically:

1. **Task 1: Fix acli auth check in JiraAdapter** - `547ef31` (fix)
2. **Task 2: Fix CLIDetector acli command** - `54f0df7` (fix)

**Plan metadata:** `[to be committed]` (docs: complete plan)

## Files Created/Modified

- `src/monocli/adapters/jira.py` - Updated check_auth() to use `["jira", "auth", "status"]` instead of `["whoami"]`
- `src/monocli/ui/main_screen.py` - Updated CLIDetector registration for acli to use `["jira", "auth", "status"]`

## Decisions Made

- **acli jira auth status is the correct command:** The acli CLI doesn't have a `whoami` command. The valid command for checking authentication is `acli jira auth status`, which follows the same pattern as `glab auth status`.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Gap closure complete
- acli authentication now works correctly when user is authenticated
- Ready for manual testing with real acli installation

---

*Phase: 03-dashboard-ui*  
*Plan: 05 (Gap Closure)*  
*Completed: 2026-02-08*

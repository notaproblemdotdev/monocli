---
phase: 02-cli-adapters
verified: 2026-02-07T20:55:00Z
status: passed
score: 6/6 must-haves verified
gaps: []
human_verification: []
---

# Phase 02: CLI Adapters Verification Report

**Phase Goal:** Detect installed CLIs and fetch real data from GitLab and Jira with proper authentication handling  
**Verified:** 2026-02-07  
**Status:** passed  
**Re-verification:** No — initial verification

## Goal Achievement

All 6 must-have criteria have been verified. The phase goal is **ACHIEVED**.

### Observable Truths

| #   | Truth   | Status     | Evidence       |
| --- | ------- | ---------- | -------------- |
| 1   | Application detects presence of glab and acli CLIs on startup | ✓ VERIFIED | CLIDetector.check_availability() uses shutil.which; DetectionRegistry.detect_all() runs multiple detectors concurrently via asyncio.gather |
| 2   | GitLab MRs are fetched via glab --json with required fields | ✓ VERIFIED | GitLabAdapter.fetch_assigned_mrs() uses `glab mr list --json --author=@me --state=opened`; returns list[MergeRequest] with iid, title, state, author, web_url |
| 3   | Jira work items are fetched via acli --json with required fields | ✓ VERIFIED | JiraAdapter.fetch_assigned_items() uses `acli jira issue list --json --assignee=@me`; returns list[JiraWorkItem] with key, summary, status, priority, url |
| 4   | Unauthenticated or missing CLIs result in hidden sections | ✓ VERIFIED | Both adapters have check_auth() methods; DetectionResult has is_authenticated flag; CLIAuthError/CLINotFoundError exceptions raised appropriately |
| 5   | All CLI calls use existing authentication | ✓ VERIFIED | Adapters use glab auth status and acli whoami for auth checks; no custom auth implementation; relies on CLI being already authenticated |
| 6   | Async tests verify adapter behavior | ✓ VERIFIED | 45 total async tests pass: 21 detection + 16 GitLab + 8 Jira tests covering success, auth failure, not installed cases |

**Score:** 6/6 truths verified (100%)

### Required Artifacts

| Artifact | Expected | Status | Details |
| -------- | ----------- | ------ | ------- |
| `src/monocli/adapters/__init__.py` | Package exports | ✓ VERIFIED | Exports CLIDetector, DetectionRegistry, DetectionResult, JiraAdapter (10 lines, HAS_EXPORTS) |
| `src/monocli/adapters/detection.py` | CLIDetector and DetectionRegistry | ✓ VERIFIED | 277 lines, has check_availability(), detect_all(), get_available(), is_available() methods; uses asyncio.gather for concurrency; implements caching |
| `src/monocli/adapters/gitlab.py` | GitLabAdapter | ✓ VERIFIED | 97 lines, inherits from CLIAdapter, has fetch_assigned_mrs() and check_auth() methods |
| `src/monocli/adapters/jira.py` | JiraAdapter | ✓ VERIFIED | 98 lines, inherits from CLIAdapter, has fetch_assigned_items() and check_auth() methods |
| `tests/test_detection.py` | Detection tests | ✓ VERIFIED | 420 lines, 21 tests, covers all cases |
| `tests/test_gitlab_adapter.py` | GitLab adapter tests | ✓ VERIFIED | 453 lines, 16 tests, covers success/empty/auth/not-installed |
| `tests/test_jira_adapter.py` | Jira adapter tests | ✓ VERIFIED | 214 lines, 8 tests, covers success/empty/auth/not-installed |
| `src/monocli/models.py` | MergeRequest and JiraWorkItem models | ✓ VERIFIED | MergeRequest has iid, title, state, author, web_url; JiraWorkItem has key, summary, status, priority, url properties |
| `src/monocli/exceptions.py` | CLI error classes | ✓ VERIFIED | CLIAuthError with AUTH_PATTERNS including "not authenticated"; CLINotFoundError for missing CLI |

### Key Link Verification

| From | To  | Via | Status | Details |
| ---- | --- | --- | ------ | ------- |
| CLIDetector.check_availability() | shutil.which | Installation check | ✓ WIRED | Uses shutil.which(self.cli_name) to check executable existence |
| CLIDetector.check_availability() | run_cli_command | Auth validation | ✓ WIRED | Calls run_cli_command() with test_args for lightweight auth check |
| DetectionRegistry.detect_all() | asyncio.gather | Concurrent execution | ✓ WIRED | Runs all detectors concurrently using asyncio.gather(*coroutines, return_exceptions=True) |
| GitLabAdapter | CLIAdapter | Class inheritance | ✓ WIRED | class GitLabAdapter(CLIAdapter), uses fetch_and_parse() from base class |
| GitLabAdapter.fetch_assigned_mrs() | MergeRequest model | fetch_and_parse() | ✓ WIRED | Returns list[MergeRequest] via fetch_and_parse(args, MergeRequest) |
| JiraAdapter | CLIAdapter | Class inheritance | ✓ WIRED | class JiraAdapter(CLIAdapter), uses fetch_and_parse() from base class |
| JiraAdapter.fetch_assigned_items() | JiraWorkItem model | fetch_and_parse() | ✓ WIRED | Returns list[JiraWorkItem] via fetch_and_parse(args, JiraWorkItem) |
| CLIAdapter.fetch_and_parse() | Pydantic model validation | model_validate() | ✓ WIRED | Uses [model_class.model_validate(item) for item in data] |
| Exception handling | CLIAuthError | raise_for_error() | ✓ WIRED | Auth failures detected via AUTH_PATTERNS and raise CLIAuthError |

### Requirements Coverage

| Requirement | Status | Evidence |
| ----------- | ------ | -------- |
| Detect glab CLI availability | ✓ SATISFIED | CLIDetector with "glab" cli_name and ["auth", "status"] test args |
| Detect acli CLI availability | ✓ SATISFIED | CLIDetector with "acli" cli_name and ["whoami"] test args |
| Fetch GitLab MRs via glab --json | ✓ SATISFIED | GitLabAdapter.fetch_assigned_mrs() uses correct CLI args |
| Fetch Jira work items via acli --json | ✓ SATISFIED | JiraAdapter.fetch_assigned_items() uses correct CLI args |
| Handle authentication failures gracefully | ✓ SATISFIED | check_auth() returns bool, CLIAuthError raised on fetch failure |
| Hide sections for unavailable CLIs | ✓ SATISFIED | DetectionRegistry.get_available() and is_available() methods provide filtering |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
| ---- | ---- | ------- | -------- | ------ |
| None found | - | - | - | - |

**Scan results:** No TODO/FIXME, placeholder patterns, empty implementations, or stub markers found in adapter code.

### Human Verification Required

None — all verifiable criteria pass automated checks. The adapters:
- Correctly use subprocess execution via run_cli_command
- Properly inherit from CLIAdapter base class
- Return validated Pydantic models
- Handle all error cases (not installed, auth failure, network errors)

### Test Results

```
========================== test session starts ==========================
platform darwin -- Python 3.13.10, pytest-9.0.2

Tests passed:
- tests/test_detection.py: 21/21 tests passed
- tests/test_gitlab_adapter.py: 16/16 tests passed  
- tests/test_jira_adapter.py: 8/8 tests passed

Total: 45/45 tests passed (100%)

Coverage:
- src/monocli/adapters/__init__.py: 100%
- src/monocli/adapters/detection.py: 97%
- src/monocli/adapters/gitlab.py: 100%
- src/monocli/adapters/jira.py: 100%
```

### Minor Note

The `__init__.py` exports `JiraAdapter` but not `GitLabAdapter`. Tests import `GitLabAdapter` directly from `monocli.adapters.gitlab`. This is a minor inconsistency but does not affect functionality. If desired, `GitLabAdapter` could be added to `__all__` for API consistency.

### Gaps Summary

No gaps found. All 6 must-have criteria are satisfied.

---
_Verified: 2026-02-07T20:55:00Z_
_Verifier: Claude (gsd-verifier)_

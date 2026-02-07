# Domain Pitfalls: Python TUI CLI Aggregators

**Project:** Mono CLI  
**Domain:** Textual TUI calling external CLIs (gh, glab, acli) asynchronously  
**Researched:** 2026-02-07  
**Confidence:** HIGH

---

## Critical Pitfalls

### Pitfall 1: Blocking the UI Thread with Synchronous Subprocess Calls

**What goes wrong:**
The TUI freezes, becomes unresponsive, and doesn't update while waiting for external CLI commands to complete. Users see frozen screens, keypresses are lost, and the app appears crashed.

**Why it happens:**
Developers often use `subprocess.run()` or `subprocess.Popen()` directly in message handlers or event callbacks. Since these are synchronous/blocking operations, they prevent Textual's event loop from processing UI updates. The documentation explicitly warns: "If you were to run this app, you should see weather information update as you type. But you may find that the input is not as responsive as usual" when making network requests without workers.

**How to avoid:**
- Always use `asyncio.create_subprocess_exec()` or `asyncio.create_subprocess_shell()` for async subprocess handling
- Wrap all external CLI calls in Textual's `@work()` decorator with `exclusive=True` for cancellable operations
- Use `run_worker()` to move blocking operations off the main thread
- Never call synchronous subprocess methods in event handlers

**Warning signs:**
- UI becomes sluggish or freezes during network/cli operations
- Keypresses have noticeable delay before appearing on screen
- Animations (spinners) stop while loading data
- App doesn't respond to Ctrl+C during operations

**Phase to address:** Phase 1 (Core Async Infrastructure)

---

### Pitfall 2: Race Conditions with Rapid User Actions

**What goes wrong:**
Multiple concurrent CLI calls return out of order, causing stale data to overwrite fresh data. For example, user rapidly switches between views - older responses arrive after newer ones, displaying wrong information.

**Why it happens:**
Without exclusive workers or proper cancellation, each user action spawns a new subprocess. Network latency varies, so responses arrive unpredictably. The last response to arrive (not the most recent request) updates the UI.

**How to avoid:**
- Use `@work(exclusive=True)` decorator which "tells Textual to cancel all previous workers before starting the new one"
- Track request IDs and ignore responses for stale requests
- Implement debouncing for rapid-fire actions (e.g., search-as-you-type)
- Check `worker.is_cancelled` in thread workers before updating UI

**Warning signs:**
- UI shows data that doesn't match the current selection
- Flickering between different data sets during rapid navigation
- Dashboard shows results for previously selected item

**Phase to address:** Phase 1 (Core Async Infrastructure)

---

### Pitfall 3: Thread Safety Violations When Updating UI

**What goes wrong:**
Random crashes, corrupted UI state, "RuntimeError: Set changed size during iteration", or widgets appearing in wrong states. These are often intermittent and hard to reproduce.

**Why it happens:**
Textual's UI is not thread-safe. When using `@work(thread=True)` for blocking operations (like synchronous subprocess calls), developers often try to update widgets directly from the worker thread. The FAQ emphasizes: "avoid calling methods on your UI directly from a threaded worker, or setting reactive variables."

**How to avoid:**
- Use `self.call_from_thread(widget.update, data)` to schedule UI updates on main thread
- Post custom messages from thread workers using `post_message()` (which is thread-safe)
- Let message handlers on main thread update UI state
- Prefer async workers (`@work()` without `thread=True`) when possible

**Warning signs:**
- Intermittent crashes during async operations
- Widget state doesn't match expected values
- Error messages about iterators or collection modifications
- UI updates appear to "lag" behind data changes

**Phase to address:** Phase 2 (CLI Integration Layer)

---

### Pitfall 4: Inconsistent CLI Output Parsing Across Tools

**What goes wrong:**
Data appears missing, incorrectly formatted, or the parser crashes when different CLIs return slightly different formats. gh and glab may output similar but not identical JSON structures.

**Why it happens:**
Different CLI tools (gh, glab, acli) have inconsistent JSON schemas, field names, and null handling. Some may use snake_case, others camelCase. Some may omit fields vs return null. Parsing without abstraction leads to fragile code.

**How to avoid:**
- Create an abstraction layer that normalizes all CLI outputs to common data models
- Use `--json` flags where available for structured output
- Implement defensive parsing with `pydantic` or `dataclasses` with defaults
- Handle missing/null fields gracefully - never assume field exists
- Version-pin CLI dependencies and test against actual tool versions

**Warning signs:**
- KeyError or AttributeError when accessing parsed data
- Empty/missing data for some CLIs but not others
- Type errors during data access
- Parser works for gh but fails for glab

**Phase to address:** Phase 2 (CLI Integration Layer)

---

### Pitfall 5: Orphaned Subprocesses and Resource Leaks

**What goes wrong:**
Subprocesses continue running after the TUI exits, consuming resources. On repeated use, system accumulates zombie processes or hits file descriptor limits.

**Why it happens:**
Python docs warn: "If the process object is garbage collected while the process is still running, the child process will be killed" - but this isn't guaranteed. If references are held or cleanup is missed, processes can outlive the parent. Also, `communicate()` can deadlock on large outputs.

**How to avoid:**
- Always `await proc.wait()` or use `asyncio.wait_for()` with timeouts
- Cancel workers properly when widgets are removed (Textual handles this automatically for worker lifecycle)
- Use timeouts on all subprocess operations: `asyncio.wait_for(proc.communicate(), timeout=30)`
- Implement proper cleanup in `on_unmount` or worker cancellation handlers
- Consider using `proc.terminate()` then `proc.kill()` if graceful shutdown fails

**Warning signs:**
- Increasing process count in `ps aux` after app usage
- "Too many open files" errors after extended use
- Hanging on app exit waiting for processes
- Memory usage growing over time

**Phase to address:** Phase 1 (Core Async Infrastructure)

---

### Pitfall 6: Silent Failures When CLIs Not Installed or Authenticated

**What goes wrong:**
The TUI shows empty states or infinite loading spinners without explaining why. Users don't know if they need to install a CLI, login, or if there's a network issue.

**Why it happens:**
External CLI dependencies (gh, glab, acli) may not be installed or authenticated. Without explicit checks, the app attempts to run commands that fail with return code != 0, but errors aren't surfaced to users.

**How to avoid:**
- Check CLI availability on startup: `shutil.which('gh')` 
- Verify authentication status before operations (each CLI has status commands like `gh auth status`)
- Handle non-zero exit codes explicitly and map to user-friendly error messages
- Show setup instructions in UI when CLIs are missing
- Distinguish between "CLI not installed", "not authenticated", and "command failed"

**Warning signs:**
- Empty dashboard with no error message
- Infinite loading spinners
- Commands work in terminal but fail in TUI
- Silent crashes in background workers

**Phase to address:** Phase 2 (CLI Integration Layer)

---

## Moderate Pitfalls

### Pitfall 7: Large Output Buffer Deadlocks

**What goes wrong:**
Subprocess hangs indefinitely when CLI output exceeds OS pipe buffer (typically 64KB). The process appears stuck waiting for I/O.

**Why it happens:**
Python docs explicitly warn: "This method can deadlock when using `stdout=PIPE` or `stderr=PIPE` and the child process generates so much output that it blocks waiting for the OS pipe buffer to accept more data."

**How to avoid:**
- Use `communicate()` method which handles buffering correctly
- Stream large outputs with `readline()` or chunked reading instead of buffering entire output
- Set appropriate limits: `create_subprocess_exec(..., limit=1024*1024)` for larger buffers
- Use `--limit` flags on CLIs when available to reduce output size

**Phase to address:** Phase 2 (CLI Integration Layer)

---

### Pitfall 8: Zombie Worker State After Cancellation

**What goes wrong:**
Workers appear to complete but leave partial state changes. Cancelled operations may have partially updated data structures.

**Why it happens:**
Workers can be cancelled at any point via `Worker.cancel()` which "raises a CancelledError within the coroutine." If cleanup isn't in finally blocks, partial state changes persist.

**How to avoid:**
- Use try/finally blocks in workers for cleanup
- Check `worker.is_cancelled` before making state changes in thread workers
- Implement atomic updates - either complete success or no change
- Handle `CancelledError` explicitly in worker functions

**Phase to address:** Phase 1 (Core Async Infrastructure)

---

### Pitfall 9: Shell Injection in CLI Arguments

**What goes wrong:**
Security vulnerability allowing arbitrary command execution when user input is passed to shell commands.

**Why it happens:**
Using `create_subprocess_shell()` with unsanitized user input. Python docs warn: "It is the application's responsibility to ensure that all whitespace and special characters are quoted appropriately to avoid shell injection vulnerabilities."

**How to avoid:**
- Prefer `create_subprocess_exec()` which takes arguments as list (no shell parsing)
- If shell is required, use `shlex.quote()` on all variable arguments
- Never pass user input directly to shell commands
- Use list form: `['gh', 'issue', 'view', issue_id]` not `f'gh issue view {issue_id}'`

**Phase to address:** Phase 2 (CLI Integration Layer)

---

### Pitfall 10: Missing Error Context for Debugging

**What goes wrong:**
When workers fail, the traceback shows the error but lacks context about which CLI command failed, what arguments were used, and what the CLI stderr contained.

**Why it happens:**
Workers default to `exit_on_error=True` which exits the app immediately. Even with `exit_on_error=False`, the worker's `error` attribute contains the exception but not CLI-specific context.

**How to avoid:**
- Set `exit_on_error=False` on workers for graceful error handling
- Capture both stdout and stderr: `stderr=asyncio.subprocess.PIPE`
- Include command details in custom exception messages
- Log full command context before execution for debugging
- Present CLI stderr output to users in error notifications

**Phase to address:** Phase 2 (CLI Integration Layer)

---

## Minor Pitfalls

### Pitfall 11: WorkerDeclarationError Confusion

**What goes wrong:**
`WorkerDeclarationError` is raised when using `@work` decorator incorrectly.

**Why it happens:**
Since Textual 0.31.0, regular functions must use `@work(thread=True)` while async functions use `@work()`. Mixing these up causes errors. The FAQ notes: "Textual version 0.31.0 requires that you set `thread=True` on the `@work` decorator if you want to run a threaded worker."

**How to avoid:**
- Async functions: `@work()` or `@work(exclusive=True)`
- Sync functions (blocking calls): `@work(thread=True)`
- Always use async workers for asyncio subprocess operations

**Phase to address:** Phase 1 (Core Async Infrastructure)

---

### Pitfall 12: Cross-Platform Path and Shell Issues

**What goes wrong:**
Commands work on macOS/Linux but fail on Windows due to different shell syntax, path separators, or command availability.

**Why it happens:**
Windows uses `cmd.exe` or PowerShell by default, different path separators, and may not have Unix tools available. Textual apps should work cross-platform.

**How to avoid:**
- Use `pathlib.Path` for cross-platform paths
- Avoid shell-specific features in commands
- Test on all target platforms
- Document required CLI installations per platform

**Phase to address:** Phase 4 (Distribution)

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Use sync subprocess calls | Simpler code, no async/await complexity | UI freezes, poor UX | Never in production - only for quick prototypes |
| Parse CLI output with regex/string splitting | Fast implementation | Brittle, breaks on format changes | Only for prototypes; use JSON output for production |
| Skip CLI availability checks | Faster startup | Cryptic errors later | Never - always check dependencies |
| Use `thread=True` for all workers | Works with any code | More complex thread-safety concerns | Only when integrating sync libraries without async support |
| Single error handler for all CLI errors | Less code to write | Poor user experience, hard to debug | Never - different errors need different handling |

---

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| GitHub CLI (gh) | Assuming `gh` is authenticated | Check `gh auth status` before operations, handle unauthenticated error |
| GitLab CLI (glab) | Parsing human-readable output | Use `glab <command> --output json` for structured data |
| AWS CLI (acli) | Not handling AWS credential errors | Catch specific auth errors, guide users to `aws configure` |
| All CLIs | Running commands without checking if installed | Use `shutil.which()` to verify CLI exists before first use |
| Browser opening | Using blocking `webbrowser.open()` | Use `asyncio` compatible approach or run in thread worker |

---

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| Synchronous loading on mount | App startup is slow, shows blank screen | Use workers for initial data load, show loading state | Always - affects first impression |
| Loading all issues/PRs at once | Memory spikes, slow rendering | Implement pagination, lazy loading | >100 items |
| No request caching | Repeated slow CLI calls for same data | Cache results in memory with TTL | Second request for same data |
| Blocking browser open | UI freezes when opening URL | Use `call_from_thread` or non-blocking equivalent | Any browser open action |

---

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| No loading indicators | Users think app is broken | Use `LoadingIndicator` or custom spinners while CLI calls in progress |
| Infinite loading without timeout | Users wait forever for hung operations | Set timeouts on all subprocess calls (30-60s), show error on timeout |
| Error messages with CLI jargon | Users don't understand "exit code 1" | Translate to actionable messages: "GitHub CLI not authenticated. Run: gh auth login" |
| No offline handling | App crashes or hangs without network | Detect offline state, show cached data if available, explain limitations |
| Blocking the entire UI during refresh | Can't navigate while data refreshes | Use workers for refresh, keep UI responsive |

---

## "Looks Done But Isn't" Checklist

- [ ] **Async subprocess handling:** Using `asyncio.create_subprocess_exec`, not `subprocess.run` — verify no blocking calls in event handlers
- [ ] **Worker lifecycle:** All async operations use `@work()` decorator — verify no bare `async def` methods called directly from events
- [ ] **Thread safety:** Thread workers use `call_from_thread` or `post_message` — verify no direct widget updates from thread workers
- [ ] **CLI availability:** App checks for `gh`, `glab`, `acli` on startup — verify graceful degradation when CLIs missing
- [ ] **Error handling:** Each CLI error type has specific user-friendly message — verify no generic "An error occurred" messages
- [ ] **Cancellation handling:** Workers check `is_cancelled` before expensive operations — verify no orphaned subprocesses on rapid navigation
- [ ] **Output parsing:** Defensive parsing with defaults for missing fields — verify no `KeyError` crashes on unexpected CLI output
- [ ] **Timeouts:** All subprocess calls have reasonable timeouts — verify no indefinite hangs on network issues

---

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Blocking UI thread | LOW | Refactor to use `@work()` decorator, test with slow operations |
| Race conditions | MEDIUM | Add `exclusive=True`, implement request ID tracking, test rapid actions |
| Thread safety violations | HIGH | Audit all worker code, add `call_from_thread` wrappers, extensive testing |
| Inconsistent parsing | MEDIUM | Add abstraction layer, implement data models, test against real CLI outputs |
| Orphaned subprocesses | LOW | Add proper `proc.wait()` calls, implement timeouts, add cleanup handlers |
| Missing CLI/auth handling | LOW | Add startup checks, implement error handlers, add setup guidance UI |

---

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Blocking UI thread | Phase 1 | App remains responsive during 10s+ CLI operations, spinner animates |
| Race conditions | Phase 1 | Rapidly switch between items - UI always shows correct selection |
| Thread safety violations | Phase 2 | Run stress test with rapid updates - no crashes or corruption |
| Inconsistent CLI parsing | Phase 2 | Test with each CLI tool (gh, glab, acli) - all display data correctly |
| Orphaned subprocesses | Phase 1 | Check `ps aux` during and after app use - no accumulated processes |
| Silent CLI failures | Phase 2 | Test with uninstalled CLI and unauthenticated state - helpful errors shown |
| Large output deadlocks | Phase 2 | Test with repos having 1000+ issues - no hangs, proper streaming |
| Zombie worker state | Phase 1 | Cancel operations mid-flight - UI returns to clean state |
| Shell injection | Phase 2 | Code review: verify no string interpolation in shell commands |
| Missing error context | Phase 2 | Force CLI errors - verify helpful error messages with context |

---

## Sources

- [Textual Workers Guide](https://textual.textualize.io/guide/workers/) - Official documentation on concurrency and workers
- [Textual FAQ](https://textual.textualize.io/FAQ/) - Common issues including WorkerDeclarationError
- [Python asyncio.subprocess Documentation](https://docs.python.org/3/library/asyncio-subprocess.html) - Official subprocess guidance and warnings
- [Textual API Reference - textual.work](https://textual.textualize.io/api/work/) - Worker decorator parameters
- GitHub Discussions analysis - Common user issues and solutions
- CLI tool manuals (gh, glab) - Output format specifications

---

*Pitfalls research for: Python TUI CLI Aggregators*  
*Researched: 2026-02-07*

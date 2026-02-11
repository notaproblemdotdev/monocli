---
status: resolved
trigger: "q key doesn't quit application (only Ctrl+Q works)"
created: 2026-02-09T10:00:00Z
updated: 2026-02-09T10:10:00Z
---

## Current Focus

hypothesis: CONFIRMED - The 'q' key binding is missing from BINDINGS lists
test: Complete examination of UI files
expecting: Found root cause - no 'q' binding registered anywhere
next_action: Provide structured diagnosis with fix recommendation

## Symptoms

expected: Pressing 'q' key quits the application
actual: Pressing 'q' does nothing; Ctrl+Q quits the application
errors: None (no error, key just doesn't work)
reproduction: Open the app and press 'q' key
started: User reported as broken

## Eliminated

- hypothesis: DataTable is capturing the 'q' key
  evidence: DataTable widget in sections.py has no BINDINGS defined
  timestamp: 2026-02-09T10:08:00Z

- hypothesis: Focus issue preventing key from reaching app
  evidence: 'q' key is not bound anywhere, so focus is irrelevant
  timestamp: 2026-02-09T10:09:00Z

- hypothesis: Binding registered as "ctrl+q" instead of "q"
  evidence: Textual has default "ctrl+q" binding; MonoApp inherits this. The issue is 'q' alone is not bound.
  timestamp: 2026-02-09T10:09:30Z

## Evidence

- timestamp: 2026-02-09T10:02:00Z
  checked: src/monocli/ui/app.py
  found: MonoApp class has action_quit() method (line 45-47) but NO BINDINGS attribute
  implication: The quit action exists but has no key binding registered at app level

- timestamp: 2026-02-09T10:03:00Z
  checked: src/monocli/ui/main_screen.py
  found: MainScreen class has BINDINGS (lines 37-42) with "tab", "o", "j", "k" - NO "q"
  implication: The 'q' binding is not registered at screen level

- timestamp: 2026-02-09T10:07:00Z
  checked: src/monocli/ui/sections.py
  found: No BINDINGS in BaseSection, MergeRequestSection, or WorkItemSection
  implication: DataTable does not have conflicting 'q' binding

- timestamp: 2026-02-09T10:09:00Z
  checked: Textual documentation and app.py inheritance
  found: MonoApp extends App which has default "ctrl+q" binding; action_quit() overrides the handler
  implication: Ctrl+Q works via Textual default; 'q' alone needs explicit binding

## Resolution

root_cause: The 'q' key binding is completely missing from the BINDINGS lists. The MonoApp class has action_quit() method but no BINDINGS attribute. The MainScreen has BINDINGS but doesn't include ("q", "quit", "Quit"). Ctrl+Q works because Textual's App class has a default "ctrl+q" binding.

fix: Add ("q", "quit", "Quit") to the BINDINGS list in src/monocli/ui/main_screen.py at line 42 (after the "k" binding)

verification: NOT VERIFIED (diagnose-only mode)
files_changed: []

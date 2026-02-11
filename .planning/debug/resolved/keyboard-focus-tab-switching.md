---
status: resolved
trigger: "Keyboard navigation doesn't work properly after Tab switching sections"
created: 2026-02-09T10:00:00Z
updated: 2026-02-09T10:10:00Z
---

## Current Focus

hypothesis: WorkItemSection lacks focus_table() call when switching to work section via Tab
test: Examining switch_section() in main_screen.py
expecting: Find that work_section.focus() is called instead of work_section.focus_table()
next_action: Confirm root cause and document fix

## Symptoms

expected: "Keyboard navigation (arrows/j/k) works in the currently focused section after Tab switching"
actual: "When select item in opened by me, click tab twice and work items section is selected, arrows doesnt work in work items but in opened by me"
errors: None - behavioral issue
reproduction: 
  1. Select item in "Opened by me" section
  2. Press Tab twice to navigate to "Work Items" section
  3. Try to use arrow keys in Work Items
  4. Observe that arrows still control "Opened by me" instead
started: "User reported - not working properly"

## Eliminated

- hypothesis: MergeRequestContainer.focus_section not working
  evidence: Code looks correct - it calls section.focus_table() properly
  timestamp: 2026-02-09T10:05:00Z

## Evidence

- timestamp: 2026-02-09T10:05:00Z
  checked: src/monocli/ui/main_screen.py switch_section() method (lines 250-269)
  found: When switching to work section, calls `self.work_section.focus()` (line 264)
  implication: This calls Static.focus() on WorkItemSection, NOT the internal DataTable

- timestamp: 2026-02-09T10:06:00Z
  checked: src/monocli/ui/sections.py WorkItemSection class
  found: WorkItemSection inherits from BaseSection -> Static, has no focus_table() override
  implication: Calling focus() doesn't transfer focus to the internal DataTable

- timestamp: 2026-02-09T10:07:00Z
  checked: src/monocli/ui/sections.py BaseSection.focus_table() (lines 198-205)
  found: BaseSection has focus_table() that calls `self._data_table.focus()`
  implication: This is the correct method to call, but it's not being used for WorkItemSection

- timestamp: 2026-02-09T10:08:00Z
  checked: Compare MR section switching vs Work section switching
  found: MR uses `self.mr_container.focus_section("opened")` which calls `section.focus_table()`
  found: Work uses `self.work_section.focus()` which calls Static.focus()
  implication: INCONSISTENT - MR properly focuses DataTable, Work does not

## Resolution

root_caused: "In main_screen.py line 264, `self.work_section.focus()` is called instead of `self.work_section.focus_table()`. This causes the WorkItemSection widget to receive focus instead of its internal DataTable, so keyboard events still go to the previously focused MR section."
fix: "Change line 264 from `self.work_section.focus()` to `self.work_section.focus_table()`"
verification: "Test Tab navigation from MR 'Opened by me' to Work Items - arrows should control Work Items DataTable"
files_changed: ["src/monocli/ui/main_screen.py"]

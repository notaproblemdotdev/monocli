---
status: investigating
trigger: "Pressing 'o' key doesn't open the selected item in browser"
created: "2026-02-09"
updated: "2026-02-09"
---

## Current Focus

hypothesis: CONFIRMED - get_selected_url() fails type check because DataTable.rows.keys() returns RowKey objects, not strings
test: Tested DataTable behavior with test script to verify RowKey structure
expecting: The isinstance(row_key, str) check fails because row_key is RowKey object
next_action: Fix the type check in get_selected_url() methods to access row_key.value instead

## Symptoms

expected: "Pressing 'o' key opens the selected item in the default browser"
actual: "User reported: o doesnt work. switching with tab works"
errors: None reported
reproduction: "Press 'o' key when an item is selected in the TUI"
started: Unknown

## Eliminated

## Evidence

- timestamp: 2026-02-09
  checked: src/monocli/ui/main_screen.py
  found: "'o' key binding is registered on line 39: ('o', 'open_selected', 'Open in Browser')"
  implication: The binding is correctly registered in BINDINGS

- timestamp: 2026-02-09
  checked: action_open_selected method (lines 275-295)
  found: "Method calls get_selected_url() on mr_container or work_section depending on active_section"
  implication: The logic depends on get_selected_url() returning a valid URL

- timestamp: 2026-02-09
  checked: get_selected_url() implementations in sections.py (lines 311-347 for MR, 603-639 for WorkItem)
  found: "Method uses self._data_table.cursor_row to get selected row index, then looks up row_keys[row_index]"
  implication: cursor_row returns the INDEX of the row (0, 1, 2...), not a coordinate object

- timestamp: 2026-02-09
  checked: DataTable API in Textual
  found: "cursor_row property returns an Optional[int] - the row index starting from 0"
  implication: The code is using cursor_row correctly as an integer index

- timestamp: 2026-02-09
  checked: How rows are added in MergeRequestSection.update_data (line 299-307) and WorkItemSection.update_data (line 591-599)
  found: "Rows are added with key=str(mr.web_url) for MRs and key=item.url for work items"
  implication: The URL is stored as the row key and should be retrievable

- timestamp: 2026-02-09
  checked: DataTable.rows.keys() behavior in Textual
  found: "rows.keys() returns RowKey objects, NOT the original string keys. RowKey has a .value attribute containing the original key"
  implication: The isinstance(row_key, str) check at lines 334 and 626 always fails, causing get_selected_url() to return None

- timestamp: 2026-02-09
  checked: get_selected_url() implementations (lines 311-347 and 603-639)
  found: "Code checks 'if isinstance(row_key, str)' but row_key is always a RowKey object, never a string"
  implication: This is the bug! The URL is never returned because the type check fails

## Resolution

root_caused: "In sections.py, get_selected_url() checks 'if isinstance(row_key, str)' at lines 334 and 626, but DataTable.rows.keys() returns RowKey wrapper objects, not strings. The RowKey objects have a .value attribute containing the original URL string, but the isinstance check always fails, causing the method to return None."
fix: "Change the type check from 'if isinstance(row_key, str)' to 'if hasattr(row_key, 'value')' and return row_key.value, or check if row_key is a RowKey instance and access row_key.value"
verification: ""
files_changed:
  - src/monocli/ui/sections.py (lines 334-335 and 626-627)

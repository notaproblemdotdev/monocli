---
status: investigating
trigger: "Merge Requests section header/label is not visible above the two subsections"
created: "2026-02-09"
updated: "2026-02-09"
---

## Current Focus

hypothesis: The MergeRequestContainer lacks a parent label/header widget - it only contains the two subsections without a "Merge Requests" title above them.
test: Examine compose() methods in sections.py and main_screen.py
expecting: Confirm no Label widget exists for "Merge Requests" header
next_action: Document root cause and provide fix recommendation

## Symptoms

expected: "Dashboard shows 'Merge Requests' section label/header clearly above the two subsections"
actual: "User sees 'Opened by me' and 'Assigned to me' subsections but no parent 'Merge Requests' header above them"
errors: None - this is a UI/layout omission
reproduction: Open the dashboard, observe the MR container area
started: Always been this way (design gap)

## Eliminated

## Evidence

- timestamp: "2026-02-09"
  checked: "src/monocli/ui/sections.py - MergeRequestContainer.compose() method"
  found: "Lines 394-398 only yield the two MergeRequestSection subsections inside a Vertical container, no header Label"
  implication: "The container has no built-in title/label widget"

- timestamp: "2026-02-09"
  checked: "src/monocli/ui/main_screen.py - MainScreen.compose() method"
  found: "Lines 116-118 create mr-container Vertical but only yield the MergeRequestContainer, no Label before it"
  implication: "The main screen doesn't add a 'Merge Requests' header label either"

- timestamp: "2026-02-09"
  checked: "src/monocli/ui/main_screen.py - DEFAULT_CSS"
  found: "Lines 76-79 define .section-label CSS class for bold text styling, but it's never used in compose()"
  implication: "CSS is prepared for section labels but not connected to any widget"

## Resolution

root_cause: "Both MergeRequestContainer.compose() and MainScreen.compose() omit a Label widget for the 'Merge Requests' header. The container only has the two subsections, and the main screen doesn't add a label before yielding the container."
fix: "Add a Label('Merge Requests', classes='section-label') inside the mr-container Vertical in main_screen.py, before the MergeRequestContainer"
verification: ""
files_changed: []

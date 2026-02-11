---
status: investigating
trigger: "MR subsections are in the wrong order - 'Opened by me' appears first instead of 'Assigned to me'"
created: "2026-02-09T00:00:00Z"
updated: "2026-02-09T00:00:00Z"
---

## Current Focus

hypothesis: The compose() method in MergeRequestContainer yields 'opened_by_me' before 'assigned_to_me', causing wrong display order
test: Read sections.py to verify compose() method order
expecting: Confirm that sections are yielded in wrong order
next_action: Document root cause and provide fix

## Symptoms

expected: "Assigned to me" subsection should appear on the left (first), "Opened by me" on the right (second)
actual: "Opened by me" appears first (left), "Assigned to me" appears second (right)
errors: None - visual/layout issue
reproduction: Launch app, look at MR sections - they appear in wrong order
started: Always broken (from initial implementation)

## Eliminated

(No hypotheses eliminated yet)

## Evidence

- timestamp: "2026-02-09T00:00:00Z"
  checked: "src/monocli/ui/sections.py, MergeRequestContainer.compose() method, lines 394-398"
  found: "compose() yields opened_by_me_section BEFORE assigned_to_me_section (lines 397-398)"
  implication: "Textual renders widgets in yield order; first yielded appears first (left in horizontal layout, top in vertical)"

- timestamp: "2026-02-09T00:00:00Z"
  checked: "CSS layout rules in MergeRequestContainer.DEFAULT_CSS, lines 361-381"
  found: "Horizontal layout uses width: 50% for each section; vertical layout uses height: 50%. In both cases, order is determined by DOM order (yield order)"
  implication: "Swapping yield order will fix both horizontal (wide terminal) and vertical (narrow terminal) layouts"

- timestamp: "2026-02-09T00:00:00Z"
  checked: "Initialization order in __init__, lines 386-392"
  found: "Sections are initialized in order: opened_by_me first, then assigned_to_me"
  implication: "This doesn't affect rendering order - only the compose() yield order matters for display"

## Resolution

root_cause: "In MergeRequestContainer.compose() (lines 394-398), the sections are yielded in wrong order: opened_by_me_section is yielded first, causing it to appear first (left/top), but user expects assigned_to_me_section to appear first"
fix: "Swap lines 397 and 398 in compose() method to yield assigned_to_me_section before opened_by_me_section"
verification: "Not yet verified"
files_changed:
  - "src/monocli/ui/sections.py"

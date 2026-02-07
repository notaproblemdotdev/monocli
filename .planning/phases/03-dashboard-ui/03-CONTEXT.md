# Phase 03: Dashboard UI - Context

**Gathered:** 2026-02-07
**Status:** Ready for planning

<domain>
## Phase Boundary

A responsive terminal dashboard using Textual framework displaying work items and merge requests in a two-section layout with keyboard navigation. PRs/MRs on top, Work Items below. Users can navigate with j/k or arrows within sections, Tab to switch sections, and press 'o' to open items in browser.

</domain>

<decisions>
## Implementation Decisions

### Section layout
- 50/50 split between PRs/MRs (top) and Work Items (bottom) sections
- Fixed height sections, not collapsible
- Each section has its own scrollbar when content overflows

### Item presentation format
- **PRs/MRs section columns:** Key/Number, Title, Status, Author, Branch, Created Date
- **Work Items section columns:** Key, Title, Status, Priority, Assignee, Created Date
- **Long titles:** Truncate with ellipsis (...)
- Use DataTable widget for both sections

### Navigation behavior
- Tab key switches active section (top ↔ bottom)
- j/k or arrow keys navigate items within the active section only
- Visual indicator shows which section is currently active (e.g., border highlight, title styling)
- Selection is section-scoped, not global

### Loading & empty states
- Loading spinners appear alongside/beside section titles (not replacing content)
- Spinner design: Minimalist and simple (Textual's default or basic spinner)
- Empty state: Show friendly message like "No merge requests found" or "No assigned work items"
- Error handling: Display error message in place of content (e.g., "Failed to load GitLab MRs")

### Browser integration
- Pressing 'o' immediately opens the selected item in default browser (no confirmation)
- No visual feedback notification (browser opening is sufficient feedback)
- Handle browser open failures gracefully (log error, show brief message)

### Claude's Discretion
- Exact visual styling of the active section indicator
- Spinner animation style (as long as it's simple/minimalist)
- Color scheme and theming
- Exact wording of empty state messages
- Error message display format
- Section title formatting

</decisions>

<specifics>
## Specific Ideas

- Key display format: !42 for GitLab MRs, #123 for GitHub PRs (handled by model's display_key())
- Status and Priority should use the model's display_status() helper
- Overall feel should be clean and information-dense like a terminal-native tool

</specifics>

<deferred>
## Deferred Ideas

- None — discussion stayed within phase scope

</deferred>

---

*Phase: 03-dashboard-ui*
*Context gathered: 2026-02-07*

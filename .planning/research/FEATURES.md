# Feature Landscape

**Domain:** TUI Dashboard for CLI Aggregator (Work Items & PRs/MRs)
**Researched:** 2026-02-07
**Overall Confidence:** HIGH

## Executive Summary

Mono CLI is a unified terminal interface aggregating work items and pull/merge requests from Jira, GitHub, and GitLab. Based on analysis of successful TUI tools (lazygit 71.9k★, k9s 32.7k★, Textual 34.1k★) and CLI aggregators (gh CLI 42.4k★), this document maps the feature landscape for TUI dashboard applications in the developer workflow space.

Key insight: The most successful TUI tools prioritize **keyboard-driven workflows**, **non-blocking async operations**, and **progressive disclosure** (show essential info first, details on demand). Users expect instant feedback, vim-like navigation, and seamless browser integration for deep dives.

---

## Table Stakes

Features users expect from any TUI dashboard app. Missing these = product feels broken.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| **Keyboard Navigation** | TUI users are keyboard-centric; mouse support is secondary | Low | Arrow keys, j/k, gg/G, Ctrl+F for search. Standard vim bindings expected. |
| **Real-time Data Loading** | Users expect async loading without blocking UI | Medium | Spinner/progress indicator while fetching. Textual's worker API handles this well. |
| **Search/Filter** | Essential for navigating large datasets | Medium | `/` to filter, `n/N` for next/previous match. Pattern from k9s, lazygit. |
| **Browser Integration** | Deep links must open in browser for full context | Low | `o` key to open in browser. Universal expectation from TUI tools. |
| **Manual Refresh** | Users need control over when data updates | Low | `r` key to refresh. Shows last-updated timestamp. |
| **Status Indicators** | Visual distinction between states (open/closed/merged) | Low | Color coding + icons. Red/green/yellow semantic colors. |
| **Sortable Columns** | Users want to prioritize by different criteria | Medium | Click header or keybind (e.g., `s` to cycle sort). Status → Priority → Age common default. |
| **Error Handling** | Graceful failures when APIs are unreachable | Medium | Don't crash on network errors. Show cached data with stale indicator. |
| **Help System** | In-app reference for keybindings | Low | `?` to show help. Context-sensitive (different views show different help). |
| **Responsive Layout** | Handle different terminal sizes gracefully | Medium | Collapse columns on narrow screens. Minimum viable at 80x24. |

---

## Differentiators

Features that set Mono CLI apart. Not required, but create competitive advantage.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| **Multi-Platform Aggregation** | Single view across Jira/GitHub/GitLab — unique value | High | Unified data model. Normalize status/priority across platforms. |
| **Auto-Platform Detection** | Zero-config startup — detects installed CLIs | Medium | Check for `gh`, `glab`, `jira` CLI presence. Auto-enable available sources. |
| **Smart Auto-Refresh** | Background updates without user intervention | Medium | Configurable interval (default: 5min). Visual indicator when new data arrives. |
| **Unified Priority View** | Cross-platform priority ranking | Medium | Map Jira priorities + GitHub labels + GitLab labels to common scale. |
| **Contextual Actions** | Act on items directly from TUI | High | Approve PR, transition Jira issue, add comment. Requires write API access. |
| **Customizable Columns** | User chooses what to display | Medium | Config file to show/hide columns. Remember preferences per platform. |
| **Notification Integration** | Alert on new assignments | Medium | Desktop notifications for new PRs/issues. Platform-native or terminal bell. |
| **Offline Mode** | View cached data when disconnected | Medium | Local SQLite cache. Show "offline" indicator with last-sync time. |
| **Quick Actions** | Keyboard shortcuts for common workflows | Medium | `a` to approve, `m` to merge (if checks pass), `c` to comment. |
| **Cross-Platform Search** | Find items across all platforms simultaneously | High | Unified search index. Fuzzy matching on title/description. |

---

## Anti-Features

Features to explicitly NOT build. Common mistakes in this domain.

| Anti-Feature | Why Avoid | What To Do Instead |
|--------------|-----------|-------------------|
| **In-TUI Code Review** | Diff viewing/editing in terminal is poor UX | Open browser with `o` key. Use platform-native review tools. |
| **Full Issue Editing** | Rich text, attachments, mentions are complex | Open browser for editing. TUI is read-only dashboard. |
| **Real-time Collaboration** | Chat/comments in TUI add noise | Integrate with existing notifications. Don't rebuild Slack. |
| **Custom Authentication** | Don't store credentials; use platform CLIs | Delegate auth to `gh`, `glab`, `jira` CLIs. Read their config. |
| **Git Operations** | Stay focused on work items, not git commands | Keep it separate from lazygit. Single responsibility principle. |
| **Complex Theming** | Maintenance burden, accessibility issues | Offer 2-3 curated themes (dark/light/high-contrast). |
| **Mouse-First Interface** | TUI power users prefer keyboard | Mouse support as bonus, not primary interaction mode. |
| **Dashboard Widgets** | Charts/graphs add noise in terminal | Focus on tabular data. Text-first presentation. |

---

## Feature Dependencies

```
Core Data Fetching
    └──requires──> Platform CLI Detection
    └──requires──> Async Loading Framework

Search/Filter
    └──requires──> Data Loading
    └──enhances──> Table Stakes UX

Browser Integration
    └──requires──> Item Selection
    └──uses──> Platform URL Generation

Auto-Refresh
    └──requires──> Background Worker System
    └──conflicts──> Manual Edit Operations (race conditions)

Cross-Platform Aggregation
    └──requires──> Unified Data Model
    └──requires──> Platform Adapters (GitHub/GitLab/Jira)
    └──enables──> Unified Search

Contextual Actions (Advanced)
    └──requires──> Authentication (via platform CLIs)
    └──requires──> Write API Permissions
    └──depends──> Core Data Fetching (need current state)
```

### Dependency Notes

- **Platform CLI Detection → Data Fetching:** Must detect which CLIs are installed before attempting to fetch data. No custom auth.
- **Async Loading → UI Responsiveness:** Data fetching must not block the main thread. Textual's Worker API enables this.
- **Unified Data Model → Cross-Platform Features:** All platform-specific data must be normalized to common schema before aggregation features work.
- **Auto-Refresh conflicts with Manual Actions:** Editing while auto-refresh is active can cause race conditions. Need transaction-like semantics or disable refresh during edits.

---

## MVP Definition

### Launch With (v1)

Minimum viable product — validate that developers want a unified work item view.

- [x] **Platform Detection** — Auto-detect installed CLIs (`gh`, `glab`, `jira`)
- [x] **PR/MR List** — Show assigned + created PRs/MRs from GitHub/GitLab
- [x] **Work Item List** — Show assigned open issues from all platforms
- [x] **Basic Display** — Key + Title + Status + Priority columns
- [x] **Keyboard Navigation** — Vim-style bindings (j/k, gg/G, / for search)
- [x] **Browser Open** — `o` key opens selected item in browser
- [x] **Manual Refresh** — `r` key refreshes all data
- [x] **Async Loading** — Non-blocking data fetch with spinner
- [x] **Help Overlay** — `?` shows available keybindings

### Add After Validation (v1.x)

Features to add once core dashboard is stable and used daily.

- [ ] **Auto-Refresh** — Background polling every 5 minutes
- [ ] **Smart Sorting** — By priority, age, or status
- [ ] **Cross-Platform Priority** — Unified priority view (High/Medium/Low)
- [ ] **Offline Cache** — View last-synced data when disconnected
- [ ] **Column Customization** — Show/hide columns via config
- [ ] **Notification Integration** — Desktop alerts for new assignments

### Future Consideration (v2+)

Defer until product-market fit is established and usage patterns are clear.

- [ ] **Contextual Actions** — Approve/merge/comment from TUI
- [ ] **Unified Search** — Cross-platform fuzzy search
- [ ] **Custom Filters** — Save frequently used filters
- [ ] **Plugin System** — Allow custom platform adapters
- [ ] **Team View** — See items assigned to team members
- [ ] **Sprint/Kanban View** — Board-style visualization (maybe)

---

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Platform CLI Detection | HIGH | LOW | P1 |
| PR/MR Aggregation | HIGH | MEDIUM | P1 |
| Work Item Aggregation | HIGH | MEDIUM | P1 |
| Keyboard Navigation | HIGH | LOW | P1 |
| Browser Integration | HIGH | LOW | P1 |
| Async Loading | HIGH | MEDIUM | P1 |
| Manual Refresh | MEDIUM | LOW | P1 |
| Search/Filter | HIGH | MEDIUM | P1 |
| Auto-Refresh | MEDIUM | MEDIUM | P2 |
| Unified Priority | MEDIUM | MEDIUM | P2 |
| Offline Cache | MEDIUM | MEDIUM | P2 |
| Column Customization | LOW | LOW | P2 |
| Notifications | MEDIUM | MEDIUM | P2 |
| Contextual Actions | HIGH | HIGH | P3 |
| Unified Search | HIGH | HIGH | P3 |
| Plugin System | LOW | HIGH | P3 |

**Priority Key:**
- **P1:** Must have for launch (v1)
- **P2:** Should have, add when core is stable (v1.x)
- **P3:** Nice to have, future consideration (v2+)

---

## Competitor Feature Analysis

| Feature | lazygit | k9s | gh CLI | Our Approach |
|---------|---------|-----|--------|--------------|
| Primary Domain | Git operations | Kubernetes | GitHub | Work item aggregation |
| Multi-Platform | No (git only) | No (k8s only) | No (GitHub only) | **Yes — core differentiator** |
| Keyboard-First | Yes | Yes | N/A (CLI) | Yes — TUI navigation |
| Async Loading | Yes | Yes | Yes | Yes — Textual workers |
| Browser Open | Limited | No | Yes (browse cmd) | Yes — `o` key universal |
| Search/Filter | Yes (`/`) | Yes (`/`) | Partial | Yes — unified filter |
| Auto-Refresh | No | Yes (watch) | No | Yes — background polling |
| Customizable Views | Limited | Yes | N/A | Yes — column selection |
| Help System | Yes (`?`) | Yes (`?`) | `--help` | Yes — context-sensitive |

### Key Insights from Competitors

1. **lazygit (71.9k★):** Proves keyboard-driven git workflows are beloved. Shows importance of discoverable keybindings (`?` help) and undo functionality. Keeps scope focused — doesn't try to be a general terminal app.

2. **k9s (32.7k★):** Demonstrates resource aggregation patterns. The `:resource` command mode for switching views is powerful. Real-time watch mode shows what's possible with async updates.

3. **gh CLI (42.4k★):** Shows GitHub API integration patterns. The `gh pr list` and `gh issue list` commands are the baseline we're improving upon by adding TUI and multi-platform support.

4. **Textual Framework (34.1k★):** Modern Python TUI with reactive patterns, built-in widgets (DataTable, Input), and excellent async support. Reduces complexity vs building on ncurses directly.

---

## Domain-Specific Considerations

### Platform API Constraints

| Platform | Rate Limits | Auth Method | Data Freshness |
|----------|-------------|-------------|----------------|
| GitHub | 5000/hour | `gh auth` token | Real-time |
| GitLab | 2000/min (cloud) | `glab` token | Real-time |
| Jira | 10/sec | OAuth/Token | ~1 min delay typical |

**Implications:**
- Implement request batching/caching to respect rate limits
- Use conditional requests (If-None-Match) where supported
- Show rate limit status in footer when approaching limits

### Data Normalization Challenges

| Concept | GitHub | GitLab | Jira | Unified Model |
|---------|--------|--------|------|---------------|
| Work Unit | Issue/PR | Issue/MR | Issue | `WorkItem` |
| Status | open/closed | opened/closed/merged | To Do/In Progress/Done | `status: open/closed/merged/draft` |
| Priority | Labels | Labels | Priority field | `priority: critical/high/medium/low` |
| Assignment | Assignees | Assignees | Assignee | `assignees: []` |
| Identifier | #123 | #123 | PROJ-123 | `key: platform#id` |

### Terminal Constraints

- **Color support:** Assume 256-color, gracefully degrade to 16-color
- **Width:** Minimum 80 columns, optimal 120+ for all columns
- **Height:** Show at least 10 items visible at once (typical terminal 24+ rows)
- **Unicode:** Use icons if terminal supports, ASCII fallback (e.g., `[o]` vs ``)

---

## Sources

- **lazygit** (https://github.com/jesseduffield/lazygit) — TUI patterns, keyboard navigation, async operations
- **k9s** (https://github.com/derailed/k9s) — Dashboard patterns, filtering, real-time updates, command mode
- **Textual** (https://github.com/Textualize/textual) — Framework capabilities, widget patterns, async architecture
- **gh CLI** (https://github.com/cli/cli) — GitHub API integration, authentication patterns
- **hub** (https://github.com/mislav/hub) — CLI aggregator patterns (though focused on git proxy)

**Confidence Assessment:**
- Table Stakes: HIGH — Well-established patterns across mature tools
- Differentiators: MEDIUM — Based on user pain points, requires validation
- Anti-Features: HIGH — Clear boundaries from domain experience
- Dependencies: HIGH — Logical architecture based on implementation constraints

---

*Feature research for: Mono CLI — TUI Dashboard for Work Item Aggregation*
*Researched: 2026-02-07*

# Requirements: Mono CLI

**Defined:** 2025-02-07
**Core Value:** One dashboard showing all assigned work items and pending MRs without switching between browser tabs or context switching between platforms.

## v1 Requirements

### Dashboard

- [ ] **DASH-01**: Dashboard renders two-section layout (PRs/MRs section + Work Items section)
- [ ] **DASH-02**: User can navigate between items using keyboard (j/k or arrow keys)
- [ ] **DASH-03**: User can press 'o' to open selected item in default browser
- [x] **DASH-04**: Application auto-detects which CLIs are installed (glab, acli) and shows only available sections
- [ ] **DASH-05**: Per-section loading spinners shown while fetching data

### Data Sources

- [x] **DATA-01**: GitLab MRs fetched via glab CLI using --json flag
- [x] **DATA-02**: Jira work items fetched via acli CLI using --json flag
- [x] **DATA-03**: All CLI responses parsed and validated with Pydantic models
- [x] **DATA-04**: GitLab MRs include: MR number, title, status, author, URL
- [x] **DATA-05**: Jira work items include: issue key, title, status, priority, URL
- [ ] **DATA-06**: Display format for each item shows: Key + Title + Status + Priority

### Async & Performance

- [x] **ASYNC-01**: Data fetching uses Textual Workers API with @work decorator
- [x] **ASYNC-02**: Workers use exclusive=True to prevent race conditions
- [x] **ASYNC-03**: UI remains responsive during data fetching (non-blocking)
- [x] **ASYNC-04**: Failed CLI calls handled gracefully with error messages

### Configuration

- [x] **CONFIG-01**: Application uses existing CLI authentication (no separate auth)
- [x] **CONFIG-02**: Missing or unauthenticated CLIs detected and sections hidden

### Testing

- [x] **TEST-01**: Unit tests for Pydantic models using pytest
- [x] **TEST-02**: Async tests for CLI adapters using pytest-asyncio
- [ ] **TEST-03**: Integration tests for Textual widgets

## v2 Requirements

### Dashboard

- **DASH-V2-01**: User can press 'r' or F5 to manually refresh
- **DASH-V2-02**: User can press '?' to show keyboard shortcuts help
- **DASH-V2-03**: Auto-refresh capability with configurable interval
- **DASH-V2-04**: Search/filter functionality (press '/' to filter)

### Data Sources

- **DATA-V2-01**: GitHub PRs fetched via gh CLI using --json flag
- **DATA-V2-02**: GitHub Issues fetched via gh CLI using --json flag
- **DATA-V2-03**: PRs/MRs include both assigned to user AND created by user

### Configuration

- **CONFIG-V2-01**: User can configure which sections to show (override auto-detect)
- **CONFIG-V2-02**: Config file support (~/.config/monocli/config.yaml)

## Out of Scope

| Feature | Reason |
|---------|--------|
| In-TUI code review/editing | Terminal is poor for these tasks; redirect to browser |
| Real-time notifications | Out of v1 scope; focus on on-demand dashboard |
| Custom theming | Standard Textual themes sufficient for MVP |
| Offline mode | Requires active internet to fetch data |
| Caching strategies | Fresh fetch on load; caching may be added in v2 |
| Non-terminal interfaces | TUI-only, no web or desktop versions |
| Modifying items from CLI | View-only in v1; editing via web interface |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| DASH-01 | Phase 3 | Pending |
| DASH-02 | Phase 3 | Pending |
| DASH-03 | Phase 3 | Pending |
| DASH-04 | Phase 2 | Complete |
| DASH-05 | Phase 3 | Pending |
| DATA-01 | Phase 2 | Complete |
| DATA-02 | Phase 2 | Complete |
| DATA-03 | Phase 1 | Complete |
| DATA-04 | Phase 2 | Complete |
| DATA-05 | Phase 2 | Complete |
| DATA-06 | Phase 3 | Pending |
| ASYNC-01 | Phase 1 | Complete |
| ASYNC-02 | Phase 1 | Complete |
| ASYNC-03 | Phase 1 | Complete |
| ASYNC-04 | Phase 1 | Complete |
| CONFIG-01 | Phase 2 | Complete |
| CONFIG-02 | Phase 2 | Complete |
| TEST-01 | Phase 1 | Complete |
| TEST-02 | Phase 2 | Complete |
| TEST-03 | Phase 3 | Pending |

**Coverage:**
- v1 requirements: 20 total
- Mapped to phases: 20
- Unmapped: 0 ✓

**Phase Mapping Summary:**
- **Phase 1 (Foundation):** DATA-03, ASYNC-01, ASYNC-02, ASYNC-03, ASYNC-04, TEST-01 (6 requirements)
- **Phase 2 (CLI Adapters):** DASH-04, DATA-01, DATA-02, DATA-04, DATA-05, CONFIG-01, CONFIG-02, TEST-02 (8 requirements)
- **Phase 3 (Dashboard UI):** DASH-01, DASH-02, DASH-03, DASH-05, DATA-06, TEST-03 (6 requirements)

---
*Requirements defined: 2025-02-07*
*Last updated: 2025-02-07 after Phase 2 completion*

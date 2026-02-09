# Requirements: Mono CLI v2.0

**Defined:** 2026-02-09
**Core Value:** One dashboard showing all assigned work items and pending PRs/MRs without switching between browser tabs or context switching between platforms.
**Milestone:** v2.0 Extended Platform Support

## v2.0 Requirements

### GitHub Integration

- [ ] **GH-01**: GitHub CLI (`gh`) auto-detected and shows PRs section when available
- [ ] **GH-02**: GitHub PRs fetched via `gh pr list --json` with author and state filters
- [ ] **GH-03**: GitHub PRs display: Number + Title + Status + Author
- [ ] **GH-04**: GitHub Issues fetched via `gh issue list --json` 
- [ ] **GH-05**: GitHub Issues display: Number + Title + Status + Labels
- [ ] **GH-06**: GitHub auth status checked via `gh auth status`
- [ ] **GH-07**: GitHub adapter follows same pattern as GitLabAdapter (CLIAdapter base)

### Todoist Integration

- [ ] **TD-01**: Todoist CLI tool auto-detected (or use REST API if no CLI available)
- [ ] **TD-02**: Todoist tasks fetched for today's due date
- [ ] **TD-03**: Todoist tasks display: Content + Priority + Due Date + Project
- [ ] **TD-04**: Todoist auth via API token in environment variable or config file
- [ ] **TD-05**: Todoist tasks appear in Work Items section or new Tasks section
- [ ] **TD-06**: Todoist adapter follows same pattern as existing adapters

### Dashboard Enhancements

- [ ] **DASH-01**: Manual refresh via 'r' key or F5
- [ ] **DASH-02**: Help screen accessible via '?' key showing all keyboard shortcuts
- [ ] **DASH-03**: Configuration file support at ~/.config/monocli/config.yaml
- [ ] **DASH-04**: PRs/MRs section includes both GitHub PRs and GitLab MRs (if both available)
- [ ] **DASH-05**: Work Items section includes Jira issues and Todoist tasks (if both available)
- [ ] **DASH-06**: Section visibility configurable via config file (override auto-detect)

### Data Sources

- [ ] **DATA-01**: GitHub PRs include: number, title, state, author, URL, created_at
- [ ] **DATA-02**: GitHub Issues include: number, title, state, labels, URL, created_at
- [ ] **DATA-03**: Todoist tasks include: content, priority, due_date, project_name, URL
- [ ] **DATA-04**: All new data sources validated with Pydantic models
- [ ] **DATA-05**: Unified display format across all platforms

### Configuration

- [ ] **CONFIG-01**: Config file at ~/.config/monocli/config.yaml
- [ ] **CONFIG-02**: Config supports enabling/disabling specific sections
- [ ] **CONFIG-03**: Config supports section ordering/priority
- [ ] **CONFIG-04**: Environment variables still supported (backward compatible)
- [ ] **CONFIG-05**: Config file is optional (auto-detect remains default)

### Testing

- [ ] **TEST-01**: GitHubAdapter has async tests for success/auth failure/network errors
- [ ] **TEST-02**: TodoistAdapter has async tests for success/auth failure/network errors
- [ ] **TEST-03**: Configuration loading has unit tests
- [ ] **TEST-04**: Integration tests for help screen and refresh functionality

## v3.0+ Requirements (Deferred)

### Dashboard

- **DASH-V3-01**: Auto-refresh capability with configurable interval
- **DASH-V3-02**: Search/filter functionality (press '/' to filter items)
- **DASH-V3-03**: Offline mode with cached data

### Data Sources

- **DATA-V3-01**: Azure DevOps support
- **DATA-V3-02**: Linear support
- **DATA-V3-03**: ClickUp support

## Out of Scope

| Feature | Reason |
|---------|--------|
| In-TUI code review/editing | Terminal is poor for these tasks; redirect to browser |
| Real-time notifications | Out of scope; focus on on-demand dashboard view |
| Custom theming | Standard Textual themes sufficient |
| Caching strategies | Fresh fetch on load; caching in v3 |
| Non-terminal interfaces | TUI-only, no web or desktop versions |
| Modifying items from CLI | View-only; editing via web interface |
| Creating new items | View-only dashboard; creation via native tools |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GH-01 | Phase 5 | Pending |
| GH-02 | Phase 5 | Pending |
| GH-03 | Phase 5 | Pending |
| GH-04 | Phase 5 | Pending |
| GH-05 | Phase 5 | Pending |
| GH-06 | Phase 5 | Pending |
| GH-07 | Phase 5 | Pending |
| TD-01 | Phase 6 | Pending |
| TD-02 | Phase 6 | Pending |
| TD-03 | Phase 6 | Pending |
| TD-04 | Phase 6 | Pending |
| TD-05 | Phase 6 | Pending |
| TD-06 | Phase 6 | Pending |
| DASH-01 | Phase 7 | Pending |
| DASH-02 | Phase 7 | Pending |
| DASH-03 | Phase 7 | Pending |
| DASH-04 | Phase 7 | Pending |
| DASH-05 | Phase 7 | Pending |
| DASH-06 | Phase 7 | Pending |
| DATA-01 | Phase 5 | Pending |
| DATA-02 | Phase 5 | Pending |
| DATA-03 | Phase 6 | Pending |
| DATA-04 | Phase 5-6 | Pending |
| DATA-05 | Phase 7 | Pending |
| CONFIG-01 | Phase 7 | Pending |
| CONFIG-02 | Phase 7 | Pending |
| CONFIG-03 | Phase 7 | Pending |
| CONFIG-04 | Phase 7 | Pending |
| CONFIG-05 | Phase 7 | Pending |
| TEST-01 | Phase 5 | Pending |
| TEST-02 | Phase 6 | Pending |
| TEST-03 | Phase 7 | Pending |
| TEST-04 | Phase 7 | Pending |

**Coverage:**
- v2.0 requirements: 33 total
- Mapped to phases: 33
- Unmapped: 0 ✓

**Phase Mapping Summary:**
- **Phase 5 (GitHub Integration):** GH-01 through GH-07, DATA-01, DATA-02, DATA-04, TEST-01 (11 requirements)
- **Phase 6 (Todoist Integration):** TD-01 through TD-06, DATA-03, DATA-04, TEST-02 (9 requirements)
- **Phase 7 (Dashboard Enhancements):** DASH-01 through DASH-06, DATA-05, CONFIG-01 through CONFIG-05, TEST-03, TEST-04 (13 requirements)

---
*Requirements defined: 2026-02-09*
*Milestone: v2.0 Extended Platform Support*

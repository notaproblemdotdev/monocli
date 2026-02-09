# Roadmap: Mono CLI v2.0

## Overview

This roadmap extends Mono CLI v2.0 with GitHub and Todoist integrations, creating a truly comprehensive work dashboard. We follow the same architecture patterns established in v1.0: CLI adapters for data sources, Textual widgets for UI, and async workers for non-blocking operations.

## Milestones

- ✅ **v1.0 MVP** — Phases 1-4 (shipped 2026-02-09)
- 🚧 **v2.0 Extended Platform Support** — Phases 5-7 (in progress)

## Phases

<details>
<summary>✅ v1.0 MVP (Phases 1-4) — SHIPPED 2026-02-09</summary>

- [x] Phase 1: Foundation (3/3 plans) — completed 2026-02-07
- [x] Phase 2: CLI Adapters (3/3 plans) — completed 2026-02-07
- [x] Phase 3: Dashboard UI (7/7 plans) — completed 2026-02-09
- [x] Phase 4: Add Logging (2/2 plans) — completed 2026-02-09

</details>

### 🚧 v2.0 Extended Platform Support (In Progress)

- [ ] Phase 5: GitHub Integration (4 plans estimated)
- [ ] Phase 6: Todoist Integration (3 plans estimated)
- [ ] Phase 7: Dashboard Enhancements (4 plans estimated)

## Phase Details

### Phase 5: GitHub Integration

**Goal:** Add GitHub CLI adapter to fetch PRs and Issues, completing the Git platform coverage alongside GitLab.

**Depends on:** Phase 4 (Logging infrastructure)

**Requirements:** GH-01 through GH-07, DATA-01, DATA-02, DATA-04, TEST-01 (11 requirements)

**Success Criteria** (what must be TRUE):
1. GitHub CLI (`gh`) is auto-detected on startup
2. GitHub PRs are fetched via `gh pr list --json` with proper filters
3. GitHub Issues are fetched via `gh issue list --json`
4. PRs/MRs section displays both GitHub PRs and GitLab MRs when both available
5. Unauthenticated or missing `gh` results in graceful degradation
6. GitHubAdapter follows CLIAdapter pattern with proper error handling
7. All GitHub adapter functionality is tested

**Plans:** 4 plans in 2 waves

Plans:
- [ ] 05-01-PLAN.md — Create GitHub CLI detection and auth checking
- [ ] 05-02-PLAN.md — Implement GitHubAdapter for PR fetching
- [ ] 05-03-PLAN.md — Implement GitHub Issues fetching
- [ ] 05-04-PLAN.md — Update dashboard to combine GitHub and GitLab PRs

**Details:**
GitHub integration mirrors the GitLab adapter pattern. The `gh` CLI is detected, auth is verified via `gh auth status`, and PRs/Issues are fetched using `--json` output. Pydantic models (GitHubPullRequest, GitHubIssue) validate responses. The PRs section is updated to aggregate from both GitHub and GitLab when both CLIs are available.

---

### Phase 6: Todoist Integration

**Goal:** Add Todoist support for task management, completing the work item coverage alongside Jira.

**Depends on:** Phase 5 (GitHub integration pattern established)

**Requirements:** TD-01 through TD-06, DATA-03, DATA-04, TEST-02 (9 requirements)

**Success Criteria** (what must be TRUE):
1. Todoist CLI tool is auto-detected or REST API is used as fallback
2. Todoist tasks are fetched (today's tasks or specific filter)
3. Tasks display with content, priority, due date, and project name
4. Todoist auth works via API token (env var or config file)
5. Tasks appear in Work Items section alongside Jira issues
6. TodoistAdapter follows CLIAdapter pattern
7. All Todoist adapter functionality is tested

**Plans:** 3 plans in 2 waves

Plans:
- [ ] 06-01-PLAN.md — Research Todoist CLI options and create detection
- [ ] 06-02-PLAN.md — Implement TodoistAdapter for task fetching
- [ ] 06-03-PLAN.md — Update Work Items section to include Todoist tasks

**Details:**
Todoist integration may differ from other adapters if no official CLI exists. Options include: (1) unofficial Todoist CLI tools, (2) direct REST API calls, or (3) Python SDK. The adapter pattern remains consistent regardless of implementation. Tasks are displayed in the Work Items section alongside Jira issues, with priority and due date shown.

**Research Note:** Investigate Todoist CLI options during 06-01 planning phase.

---

### Phase 7: Dashboard Enhancements

**Goal:** Add manual refresh, help screen, and configuration file support for improved UX.

**Depends on:** Phase 6 (All data sources integrated)

**Requirements:** DASH-01 through DASH-06, DATA-05, CONFIG-01 through CONFIG-05, TEST-03, TEST-04 (13 requirements)

**Success Criteria** (what must be TRUE):
1. User can press 'r' or F5 to manually refresh all data
2. User can press '?' to see help screen with all keyboard shortcuts
3. Configuration file at ~/.config/monocli/config.yaml is supported
4. Config allows enabling/disabling specific sections
5. Config allows overriding auto-detection
6. All new features are tested
7. Backward compatibility maintained (works without config file)

**Plans:** 4 plans in 2 waves

Plans:
- [ ] 07-01-PLAN.md — Implement manual refresh (r/F5 key)
- [ ] 07-02-PLAN.md — Create help screen overlay (? key)
- [ ] 07-03-PLAN.md — Implement configuration file loading
- [ ] 07-04-PLAN.md — Add section visibility/priority configuration

**Details:**
Dashboard enhancements improve the daily use experience. Manual refresh allows users to update data on demand. The help screen educates users about available shortcuts. Configuration file support enables customization while maintaining zero-config defaults.

---

## Progress

**Execution Order:**
Phases execute in numeric order: 5 → 6 → 7

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Foundation | v1.0 | 3/3 | ✓ Complete | 2026-02-07 |
| 2. CLI Adapters | v1.0 | 3/3 | ✓ Complete | 2026-02-07 |
| 3. Dashboard UI | v1.0 | 7/7 | ✓ Complete | 2026-02-09 |
| 4. Add Logging | v1.0 | 2/2 | ✓ Complete | 2026-02-09 |
| 5. GitHub Integration | v2.0 | 0/4 | Planned | - |
| 6. Todoist Integration | v2.0 | 0/3 | Planned | - |
| 7. Dashboard Enhancements | v2.0 | 0/4 | Planned | - |

---
*Milestone v2.0 defined: 2026-02-09*

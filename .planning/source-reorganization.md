# Source Module Reorganization Plan

## Goal
Reorganize the source modules to co-locate platform-specific code while supporting multiple transport methods (CLI, API, etc.) and multiple protocol implementations (CodeReviewSource, PieceOfWorkSource).

## Proposed Structure

```
src/monocli/sources/
  __init__.py          # Export public classes: GitLabSource, GitHubSource, etc.
  base.py              # Protocols only (Source, CodeReviewSource, PieceOfWorkSource)
  registry.py          # SourceRegistry

  github/
    __init__.py        # GitHubSource (implements protocols)
    _cli.py            # GitHub CLI adapter
    _api.py            # GitHub REST API adapter (future)

  gitlab/
    __init__.py        # GitLabSource (implements protocols)
    _cli.py            # GitLab CLI adapter (moved from adapters/gitlab.py)
    _api.py            # GitLab API adapter (future)

  jira/
    __init__.py        # JiraSource
    _cli.py            # Jira CLI adapter
    _api.py            # Jira API adapter

  todoist/
    __init__.py        # TodoistSource
    _api.py            # Todoist API adapter (no CLI tool)
```

## Design Decisions

### 1. Detection Module
**Decision:** Move to `sources/_detection.py` (private, shared across sources)

**Rationale:**
- Detection logic is internal infrastructure, not part of public API
- Multiple sources need access to CLI detection
- Keep it private (underscore prefix) to indicate it's not for external use

### 2. CLIAdapter Base Class
**Decision:** Keep in `async_utils.py`

**Rationale:**
- `CLIAdapter` is truly a generic async utility
- Not specific to sources - could be used elsewhere
- Keep infrastructure code separate from business logic

### 3. Naming Convention
**Decision:** Rename to shorter names: `GitLabSource`, `JiraSource`, etc.

**Rationale:**
- One source class per platform
- Each class can implement multiple protocols (CodeReviewSource, PieceOfWorkSource)
- Simpler, more intuitive naming
- Avoids redundancy like "GitLabCodeReviewSource" when it might also handle issues

## Migration Steps

1. **Create new directory structure**
   - Create `github/`, `gitlab/`, `jira/`, `todoist/` directories

2. **Move adapter logic**
   - Move `adapters/gitlab.py` → `sources/gitlab/_cli.py`
   - Move `adapters/jira.py` → `sources/jira/_cli.py`
   - Move `adapters/todoist.py` → `sources/todoist/_api.py`
   - Inline GitHub CLI logic or create `sources/github/_cli.py`

3. **Update source classes**
   - Rename `GitLabCodeReviewSource` → `GitLabSource`
   - Rename `JiraPieceOfWorkSource` → `JiraSource`
   - Rename `TodoistPieceOfWorkSource` → `TodoistSource`
   - Keep `GitHubSource` as-is

4. **Move detection module**
   - Move `adapters/detection.py` → `sources/_detection.py`

5. **Update imports**
   - Update `sources/__init__.py` exports
   - Update all files importing from old locations
   - Update tests

6. **Delete old structure**
   - Remove `adapters/` package entirely
   - Flatten source modules into directories

## Benefits

- **Cohesion:** Everything related to a platform in one place
- **Flexibility:** Easy to add API adapters alongside CLI
- **Clarity:** Clear separation between protocols and implementations
- **Extensibility:** Easy to add new platforms following the same pattern

## Open Questions

- Should we keep backward compatibility aliases during migration?
- Do we need a deprecation period for the old import paths?
- Should we create the `_api.py` files now or only when implementing API support?

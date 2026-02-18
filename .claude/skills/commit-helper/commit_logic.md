# Git Commit Logic

Advanced git workflows and commit management strategies.

## Commit Message Format

### Structure
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New functionality
- `fix`: Bug fix
- `refactor`: Code restructuring (no behavior change)
- `test`: Test additions/changes
- `docs`: Documentation
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `style`: Code style (formatting, no logic change)

### Scope
Common scopes for this project:
- `thermocalc` - ThermoCalc integration
- `auth` - Authentication/authorization
- `scheduler` - Scheduler module
- `transcription` - Transcription service
- `database` - Database layer
- `ui` - Web UI/templates
- `api` - REST API endpoints
- `infra` - Infrastructure (Message Bus, email)

### Examples
```
feat(thermocalc): add chart service for matplotlib integration

- ChartService class for generating reaction/compound charts
- Base64 encoding for HTML embedding
- Support for ΔG, ΔH, ΔS, K, Cp, G, H, S charts

Closes #123
```

```
fix(auth): correct JWT token validation for expired tokens

- Added proper expiration check
- Return 401 instead of 500 on expired token
```

```
refactor(scheduler): extract email logic to infrastructure layer

- Moved EmailService to infrastructure/email/
- Updated scheduler to use generic email commands
```

## Atomic Commits

### Principles
1. **One logical change** per commit
2. **Revertable**: Any commit can be safely reverted
3. **Testable**: Each commit passes tests independently
4. **Readable**: Commit history tells a story

### What NOT to do
❌ Mix unrelated changes
❌ Include debugging code
❌ Leave TODOs in production code
❌ Combine refactoring with feature changes

### What to do
✅ Group related files
✅ Complete features logically
✅ Write clear commit messages
✅ Reference issues/PRs

## Splitting Large Commits

### Strategy 1: By Layer
```
Commit 1: feat(scope): add data models
Commit 2: feat(scope): add database layer
Commit 3: feat(scope): add business logic
Commit 4: feat(scope): add API endpoints
Commit 5: feat(scope): add UI templates
```

### Strategy 2: By Feature
```
Commit 1: feat(scope): add core functionality
Commit 2: feat(scope): add error handling
Commit 3: feat(scope): add validation
Commit 4: test(scope): add unit tests
```

### Strategy 3: By Dependency
```
Commit 1: feat(scope): add base classes and config
Commit 2: feat(scope): add services (depends on base)
Commit 3: feat(scope): add integration (depends on services)
```

## Pre-Commit Workflow

### 1. Check Status
```bash
git status
git diff --stat
```

### 2. Run Tests
```bash
uv run pytest
```

### 3. Stage Files
```bash
# Stage specific files
git add file1.py file2.py

# Or stage by pattern
git add *.py
git add tests/
```

### 4. Create Commit
```bash
git commit -m "type(scope): description"
```

### 5. Verify
```bash
git log -1 --stat
git diff HEAD~1
```

**NOTE:** CHANGELOG.md is updated ONLY during merge to main by merge-helper, not during individual commits.

## Commit History Management

### View History
```bash
# Recent commits
git log --oneline -10

# With stats
git log --stat -5

# Commit graph
git log --graph --oneline --all
```

### Amend Commit
```bash
# Add forgotten file (BEFORE push)
git add forgotten_file.py
git commit --amend --no-edit

# Change message (BEFORE push)
git commit --amend -m "new message"
```

### Squash Commits
```bash
# Interactive rebase
git rebase -i HEAD~3

# Mark commits as 'squash' or 'fixup'
# Save and exit
```

### Revert Commit
```bash
# Revert a commit (creates new commit)
git revert abc1234

# Revert multiple commits
git revert main~2..main
```

## Emergency Recovery

### Undo Last Commit (keep changes)
```bash
git reset --soft HEAD~1
```

### Undo Last Commit (discard changes)
```bash
git reset --hard HEAD~1
```

### Recover Lost Commit
```bash
git reflog
git checkout abc1234
git checkout -b recovery-branch
```

## Project-Specific Rules

### Commit Size Limit
- Maximum: 250 lines changed
- Exclusions: *.lock, alembic/versions/*.py, *.generated.*, .ai/*.md

### CHANGELOG Updates
- **NOT updated during individual commits**
- Updated ONLY once during merge to main by merge-helper
- Format: Relative links from `.ai/` directory
- Sections: Added, Changed, Fixed

### Before Merge
- Restore `.env.production` → `.env`
- Verify `.env` not in staged
- Run all tests
- Request review

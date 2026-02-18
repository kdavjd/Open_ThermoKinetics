---
name: commit-helper
description: >
  INTERNAL: Управление коммитами с Conventional Commits и лимитом ≤250 строк.
  Вызывается из: spec-implementer, merge-helper.
  НЕ вызывается пользователем напрямую.
type: internal
called_by:
  - spec-implementer
  - merge-helper
---

# Commit Helper Skill

**Служебный навык** — управление коммитами с соблюдением качества.

## Usage Context

```yaml
type: internal  # НЕ вызывается пользователем напрямую

called_by:
  - spec-implementer  # коммит после каждого этапа
  - merge-helper      # merge commit
  
responsibility:
  - Conventional Commits format
  - Лимит ≤250 строк (с исключениями)
  - Проверка тестов перед коммитом
```

**IMPORTANT:** CHANGELOG.md is NOT updated during individual commits. It is updated ONLY once during merge to main branch by merge-helper.

## When This Skill Is Invoked

- By spec-implementer after completing a stage
- By merge-helper during final merge
- When changes need to be split into multiple commits

## Pre-Commit Checklist

### Step 1: Check Commit Size

```bash
git diff --stat
```

**Calculate total changes**: Added + Modified lines (excluding deletions)

**If > 250 lines**:
```
Commit Size Exceeds Limit

Current changes: ~450 lines
Limit: 250 lines

Action Required: Split into multiple commits

Suggested breakdown:
1. Commit 1: Core functionality (~200 lines)
   - Files: file1.py, file2.py
2. Commit 2: Tests (~150 lines)
   - Files: test_file.py
3. Commit 3: Documentation (~100 lines)
   - Files: README.md, docs/api.md

Shall I help you split these changes?
```

**Exclusions** (not counted toward limit):
- `*.lock` files (uv.lock, poetry.lock)
- `alembic/versions/*.py` (database migrations)
- `*.generated.*` files (auto-generated)
- `.ai/*.md` (framework documentation)

### Step 2: Verify Tests Pass

```bash
uv run pytest
```

**If tests fail**:
```
Tests Failing

Tests: 5 failed, 42 passed

Action Required: Fix failing tests before committing

Do not commit with failing tests. Fix the issues first.
```

### Step 3: Generate Commit Message

Follow project conventions:

**Types**:
- `feat:` - New functionality
- `fix:` - Bug fix
- `refactor:` - Code restructuring
- `test:` - Test additions/changes
- `docs:` - Documentation
- `chore:` - Maintenance tasks

**Format**:
```
<type>(<scope>): <description>

[Optional detailed body]

[Optional footer]
```

**Examples**:
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

## Commit Creation Workflow

### Workflow for Single Commit (< 250 lines)

1. **Pre-commit checks**:
   ```bash
   git diff --stat
   uv run pytest
   ```

2. **Stage files**:
   ```bash
   git add file1.py file2.py
   ```

3. **Create commit**:
   ```bash
   git commit -m "type(scope): description"
   ```

4. **Verify**:
   ```bash
   git log -1 --stat
   ```

### Workflow for Large Changes (> 250 lines)

1. **Analyze changes**:
   ```bash
   git diff --stat
   ```

2. **Plan atomic commits**:
   - Group related files
   - Ensure logical completeness
   - Order by dependency

3. **Execute commits in sequence**:
   ```bash
   # Commit 1
   git add <files-for-commit-1>
   git commit -m "type(scope): part 1"

   # Commit 2
   git add <files-for-commit-2>
   git commit -m "type(scope): part 2"

   # ... continue until all changes committed
   ```

## Pre-Merge Checklist

Before merging to `main`/`main`:

1. **Verify environment**:
   ```bash
   cat .env
   # Should be production settings, not development
   ```

2. **Check .env status**:
   ```bash
   git status
   # .env should NOT be in staged
   ```

3. **Restore production config** (if needed):
   ```bash
   copy .env.production .env
   ```

4. **Final verification**:
   ```bash
   git diff main --stat
   uv run pytest
   ```

## Output Format

### Successful Commit

```
Commit Created Successfully

Type: feat
Scope: thermocalc
Message: add chart service for matplotlib integration

Files changed: 3
Lines added: 145
Lines deleted: 12

Commit hash: a1b2c3d
```

### Pre-Merge Validation

```
Pre-Merge Validation Passed

Branch: feature/thermocalc-integration
Base branch: main
Commits to merge: 4

Environment: production (.env = .env.production)
Tests: All passing (47 passed)

Ready to merge. Use merge-helper for CHANGELOG update and merge.
```

## Error Conditions

### Tests Failing
```
Cannot Commit: Tests Failing

Run: uv run pytest
Fix: Address failing tests first
```

### .env Would Be Committed
```
Cannot Commit: .env in Staged

Issue: .env contains development secrets
Fix: Remove .env from git add
```

### Commit Too Large
```
Commit Exceeds Size Limit

Current: 450 lines
Limit: 250 lines

Action: Split into multiple atomic commits
```

## References

See [commit_logic.md](commit_logic.md) for advanced git workflows.
See [validators.md](validators.md) for pre-commit validation rules.
See [merge-helper](../merge-helper/SKILL.md) for CHANGELOG update during merge.

**NOTE:** CHANGELOG is updated ONCE during merge to main by merge-helper, not during individual commits.

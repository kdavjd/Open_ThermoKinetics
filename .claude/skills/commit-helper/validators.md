# Pre-Commit Validators

Rules and checks to validate before creating commits.

## Checklist

### 1. Size Validation
```bash
git diff --stat
```

**Rules**:
- Total changes <= 250 lines
- Count: Added + Modified lines
- Exclude: Deletions, *.lock, alembic/versions/*.py, *.generated.*, .ai/*.md

**If > 250 lines**: Split into multiple commits

### 2. Test Validation
```bash
uv run pytest
```

**Rules**:
- All tests must pass
- No failing tests allowed
- Coverage not required but recommended

**If tests fail**: Fix tests before committing

### 3. File Validation

#### .env Check
```bash
git status | grep .env
```

**Rule**: `.env` must NOT be in staged

**Reason**: Contains development secrets

**Fix**: Remove from staging
```bash
git restore --staged .env
```

#### Large Binary Files
```bash
git diff --name-only --staged | grep -E "\.(png|jpg|jpeg|gif|zip|tar)$"
```

**Rule**: Large binaries should be in assets/, not committed directly

### 4. CHANGELOG Validation

**Policy**: `before_each_commit`

**Check**:
- [ ] CHANGELOG.md updated
- [ ] Entry under `[Unreleased]`
- [ ] Proper type (Added/Changed/Fixed)
- [ ] Relative file links
- [ ] Specific details included

### 5. Message Validation

**Format**: `type(scope): description`

**Types**: feat, fix, refactor, test, docs, chore

**Scopes**: thermocalc, auth, scheduler, transcription, database, ui, api, infra

**Rules**:
- Subject line < 72 characters
- Use present tense ("add" not "added")
- Use imperative mood ("add" not "adds")
- No period at end of subject

## Common Issues

### Issue: Commit Too Large

**Symptom**: git diff --stat shows >250 lines

**Solution**:
```bash
# Analyze what changed
git diff --stat

# Plan atomic commits
# Commit 1: Core files
git add core_files.py
# Update CHANGELOG for commit 1
git commit -m "feat(scope): part 1"

# Commit 2: Supporting files
git add supporting_files.py
# Update CHANGELOG for commit 2
git commit -m "feat(scope): part 2"
```

### Issue: Tests Failing

**Symptom**: pytest shows failures

**Solution**:
```bash
# Run tests with verbose output
uv run pytest -v

# Fix the failing tests
# Then commit
```

### Issue: .env in Staged

**Symptom**: git status shows .env in staged

**Solution**:
```bash
# Remove from staging
git restore --staged .env

# Verify it's not committed
git status
```

### Issue: Missing CHANGELOG Entry

**Symptom**: No entry for changes in CHANGELOG.md

**Solution**:
```bash
# Edit CHANGELOG.md
# Add entry under [Unreleased]
# Stage it
git add .ai/CHANGELOG.md
```

## Pre-Merge Validation

Before merging to main/main:

### Environment Check
```bash
cat .env
```

**Verify**: Production settings, not development

**Fix if needed**:
```bash
copy .env.production .env
```

### Status Check
```bash
git status
```

**Verify**:
- `.env` NOT in staged
- All changes committed
- Clean working directory

### Final Tests
```bash
uv run pytest
```

**Verify**: All tests pass

### Diff Check
```bash
git diff main --stat
```

**Verify**: Changes are expected

## Auto-Validation Script

Create `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Check commit size
LINES=$(git diff --cached --stat | tail -n1 | awk '{print $4}')
if [ "$LINES" -gt 250 ]; then
    echo "Commit exceeds 250 lines ($LINES). Please split."
    exit 1
fi

# Run tests
uv run pytest
if [ $? -ne 0 ]; then
    echo "Tests failed. Fix before committing."
    exit 1
fi

# Check .env
if git diff --cached --name-only | grep -q "^\.env$"; then
    echo ".env is staged. Remove it first."
    exit 1
fi
```

Install:
```bash
cp pre-commit .git/hooks/
chmod +x .git/hooks/pre-commit
```

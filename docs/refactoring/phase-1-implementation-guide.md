# Phase 1 Implementation Guide


<!-- TOC START -->
- [v0.10.0 Refactoring - Remove Duplication & Dead Code](#v0100-refactoring-remove-duplication-dead-code)
- [Overview](#overview)
- [Step 4: Delete validator.py ✅](#step-4-delete-validatorpy-)
  - [Verification](#verification)
  - [Actions](#actions)
  - [Validation](#validation)
- [Step 5: Delete auth.py ✅](#step-5-delete-authpy-)
  - [Verification](#verification)
  - [Actions Required](#actions-required)
  - [Modified **init**.py Structure](#modified-initpy-structure)
  - [Validation](#validation)
- [Step 6: Move testing.py to tests/fixtures/ ⏳](#step-6-move-testingpy-to-testsfixtures-)
  - [Verification](#verification)
  - [Actions Required](#actions-required)
  - [Modified **init**.py After This Step](#modified-initpy-after-this-step)
  - [Validation](#validation)
- [Step 7: Remove Unused Imports from core.py ⏳](#step-7-remove-unused-imports-from-corepy-)
  - [Verification](#verification)
  - [Actions Required](#actions-required)
  - [Validation](#validation)
- [Phase 1 Completion Checklist](#phase-1-completion-checklist)
  - [Final Validation](#final-validation)
- [Rollback Plan (If Issues Occur)](#rollback-plan-if-issues-occur)
  - [If you need to rollback](#if-you-need-to-rollback)
- [Summary](#summary)
- [Next Phase](#next-phase)
<!-- TOC END -->

## v0.10.0 Refactoring - Remove Duplication & Dead Code

**Status**: Ready for implementation
**Steps**: 4-7 from IMPLEMENTATION_CHECKLIST.md
**Estimated Time**: 1-2 hours
**Files to Delete**: 2 files
**Files to Move**: 1 file
**Files to Edit**: 1 file

---

## Overview

Phase 1 removes 3 files totaling ~700 lines of unnecessary code:

1. **validator.py** - Empty stub (22 lines)
2. **auth.py** - Duplicate functionality (300 lines)
3. **testing.py** - Move to tests/fixtures/ (362 lines)

---

## Step 4: Delete validator.py ✅

### Verification

```bash
# Check file exists
ls -la src/flext_cli/validator.py

# Verify no production code references (only docs should appear)
grep -r "from flext_cli.validator" . --exclude-dir=docs
grep -r "FlextCliValidator" . --exclude-dir=docs

# Verify not exported
grep "validator" src/flext_cli/__init__.py
```

**Expected**: File exists, no production references, not exported

### Actions

```bash
# Delete the file
rm src/flext_cli/validator.py
```

### Validation

```bash
# Should complete with no errors
make lint
make type-check
```

**Commit**: `refactor: remove empty validator.py stub`

---

## Step 5: Delete auth.py ✅

### Verification

```bash
# Check file exists
ls -la src/flext_cli/auth.py

# Verify functionality exists in api.py
grep -n "def authenticate" src/flext_cli/api.py

# Verify no production code uses FlextCliAuthService
grep -r "FlextCliAuthService" src/ --exclude-dir=__pycache__
# Should only find: src/flext_cli/__init__.py and src/flext_cli/auth.py

# Verify api.py doesn't use it internally
grep "FlextCliAuthService" src/flext_cli/api.py
# Should be empty
```

**Expected**: auth.py exists, api.py has authenticate(), no internal usage

### Actions Required

#### 1. Delete the file

```bash
rm src/flext_cli/auth.py
```

#### 2. Edit `src/flext_cli/__init__.py`

**Remove these 2 lines**:

**Line 170**: Remove entire line

```python
from flext_cli.auth import FlextCliAuthService
```

**Line 195**: Remove entire line from `__all__` list

```python
    "FlextCliAuthService",
```

### Modified **init**.py Structure

**BEFORE** (lines 168-196):

```python
# Phase 2: Advanced Features - Production Ready
# from flext_cli.async_support import FlextCliAsync  # Module not yet implemented
from flext_cli.auth import FlextCliAuthService
from flext_cli.cli import FlextCliCli
...
__all__ = [
    # Core API (alphabetically sorted per FLEXT standards)
    "FlextCli",
    # "FlextCliAsync",  # Module not yet implemented
    "FlextCliAuthService",
    "FlextCliCli",
```

**AFTER** (lines 168-194):

```python
# Phase 2: Advanced Features - Production Ready
# from flext_cli.async_support import FlextCliAsync  # Module not yet implemented
from flext_cli.cli import FlextCliCli
...
__all__ = [
    # Core API (alphabetically sorted per FLEXT standards)
    "FlextCli",
    # "FlextCliAsync",  # Module not yet implemented
    "FlextCliCli",
```

### Validation

```bash
# Should complete with no errors
make lint
make type-check
make test  # Verify tests still pass
```

**Expected**: No import errors, no test failures

**Commit**: `refactor: remove duplicate auth.py module`

---

## Step 6: Move testing.py to tests/fixtures/ ⏳

### Verification

```bash
# Check file exists
ls -la src/flext_cli/testing.py

# Check what's exported
grep "FlextCliTest" src/flext_cli/__init__.py
# Should find: FlextCliTesting, FlextCliTestRunner, FlextCliMockScenarios

# Find test files that import it
grep -r "from flext_cli import.*Test" tests/
grep -r "from flext_cli.testing" tests/
```

### Actions Required

#### 1. Create fixtures directory

```bash
mkdir -p tests/fixtures
```

#### 2. Move the file

```bash
mv src/flext_cli/testing.py tests/fixtures/testing_utilities.py
```

#### 3. Update test imports

**Find all test files with testing imports**:

```bash
find tests -name "*.py" -type f -exec grep -l "from flext_cli import.*Test\|from flext_cli.testing" {} \;
```

**For each test file**, update imports:

**OLD**:

```python
from flext_cli import FlextCliTesting, FlextCliTestRunner, FlextCliMockScenarios
# or
from flext_cli.testing import FlextCliTesting
```

**NEW**:

```python
from tests.fixtures.testing_utilities import (
    FlextCliTesting,
    FlextCliTestRunner,
    FlextCliMockScenarios,
)
```

**Automated sed command** (review before running):

```bash
# Update imports in test files
find tests -name "*.py" -type f -exec sed -i \
  's/from flext_cli import FlextCliTesting/from tests.fixtures.testing_utilities import FlextCliTesting/g' \
  {} +

find tests -name "*.py" -type f -exec sed -i \
  's/from flext_cli import FlextCliTestRunner/from tests.fixtures.testing_utilities import FlextCliTestRunner/g' \
  {} +

find tests -name "*.py" -type f -exec sed -i \
  's/from flext_cli import FlextCliMockScenarios/from tests.fixtures.testing_utilities import FlextCliMockScenarios/g' \
  {} +

find tests -name "*.py" -type f -exec sed -i \
  's/from flext_cli.testing import/from tests.fixtures.testing_utilities import/g' \
  {} +
```

#### 4. Edit `src/flext_cli/__init__.py`

**Remove line 188**:

```python
from flext_cli.testing import FlextCliMockScenarios, FlextCliTesting, FlextCliTestRunner
```

**Remove from `__all__` (lines 208, 214, 215)**:

```python
    "FlextCliMockScenarios",
    ...
    "FlextCliTestRunner",
    "FlextCliTesting",
```

### Modified **init**.py After This Step

**BEFORE**:

```python
from flext_cli.testing import FlextCliMockScenarios, FlextCliTesting, FlextCliTestRunner
...
__all__ = [
    ...
    "FlextCliMockScenarios",
    ...
    "FlextCliTestRunner",
    "FlextCliTesting",
    ...
]
```

**AFTER**:

```python
# Line removed entirely
...
__all__ = [
    # Items removed from list
]
```

### Validation

```bash
# Import should fail (expected)
python -c "from flext_cli import FlextCliTesting" 2>&1 | grep -q "ImportError" && echo "✓ Correctly removed from exports"

# Tests should still work
make test

# Verify tests can import from new location
python -c "from tests.fixtures.testing_utilities import FlextCliTesting; print('✓ Import works')"
```

**Expected**: Can't import from flext_cli anymore, tests pass, can import from tests.fixtures

**Commit**: `refactor: move testing utilities to tests/fixtures/`

---

## Step 7: Remove Unused Imports from core.py ⏳

### Verification

```bash
# Check for unused imports in core.py
grep -n "^import asyncio\|^from concurrent.futures\|^import pluggy\|^from cachetools" src/flext_cli/core.py

# Check if they're actually used
grep -n "asyncio\|ThreadPoolExecutor\|pluggy\|LRUCache\|TTLCache" src/flext_cli/core.py | grep -v "^import\|^from"
```

**Expected**: Import statements found, but possibly not used in code

### Actions Required

**If unused**, remove these imports from `src/flext_cli/core.py`:

- `import asyncio` (if not used)
- `from concurrent.futures import ThreadPoolExecutor` (if not used)
- `import pluggy` (if not used)
- `from cachetools import LRUCache, TTLCache` (if not used)

**Manual review required**: Check each import's usage before removing

### Validation

```bash
make lint
make type-check
make test
```

**Expected**: All checks pass

**Commit**: `refactor: remove unused imports from core.py`

---

## Phase 1 Completion Checklist

After completing all steps, verify:

- [ ] validator.py deleted
- [ ] auth.py deleted
- [ ] testing.py moved to tests/fixtures/testing_utilities.py
- [ ] **init**.py updated (3 imports removed, 4 exports removed)
- [ ] Test imports updated to use tests.fixtures
- [ ] Unused imports removed from core.py
- [ ] `make validate` passes completely
- [ ] All tests passing

### Final Validation

```bash
# Full validation suite
make validate

# Verify file counts
ls src/flext_cli/*.py | wc -l  # Should be 2 fewer (validator, auth deleted)

# Verify new test fixtures location
ls tests/fixtures/testing_utilities.py  # Should exist

# Check no broken imports
python -c "from flext_cli import FlextCli, FlextCliSettings; print('✓ Imports working')"
```

---

## Rollback Plan (If Issues Occur)

### If you need to rollback

```bash
# Restore from git (if committed)
git checkout HEAD~1 src/flext_cli/__init__.py
git checkout HEAD~1 src/flext_cli/validator.py
git checkout HEAD~1 src/flext_cli/auth.py

# Move testing back
mv tests/fixtures/testing_utilities.py src/flext_cli/testing.py

# Restore test imports
find tests -name "*.py" -type f -exec sed -i \
  's/from tests.fixtures.testing_utilities import/from flext_cli.testing import/g' \
  {} +
```

---

## Summary

**Files Deleted**: 2

- src/flext_cli/validator.py
- src/flext_cli/auth.py

**Files Moved**: 1

- src/flext_cli/testing.py → tests/fixtures/testing_utilities.py

**Files Modified**: 1

- src/flext_cli/**init**.py (removed 3 imports, 4 exports)

**Lines Removed**: ~700 lines of unnecessary code

**Impact**: Cleaner codebase, no breaking changes for external users (auth was duplicate, validator was empty, testing was test-only)

---

## Next Phase

After Phase 1 completion, proceed to **Phase 2: Convert Services to Simple Classes**

See `IMPLEMENTATION_CHECKLIST.md` steps 8-23 for Phase 2 details.

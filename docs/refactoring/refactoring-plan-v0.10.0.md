# FLEXT-CLI v0.10.0 Refactoring Plan

<!-- TOC START -->

- [Table of Contents](#table-of-contents)
- [Executive Summary](#executive-summary)
  - [Purpose](#purpose)
  - [Key Metrics](#key-metrics)
  - [Benefits](#benefits)
- [Current State Analysis (v0.9.0)](#current-state-analysis-v090)
  - [What Works Well](#what-works-well)
  - [Over-Engineering Identified](#over-engineering-identified)
- [Target Architecture (v0.10.0)](#target-architecture-v0100)
  - [Design Principles](#design-principles)
  - [Module Classification](#module-classification)
  - [Direct Access Pattern](#direct-access-pattern)
  - [Architecture Diagram](#architecture-diagram)
- [Detailed Changes](#detailed-changes)
  - [Phase 1: Remove Duplication](#phase-1-remove-duplication)
  - [Phase 2: Convert Services to Simple Classes](#phase-2-convert-services-to-simple-classes)
  - [Phase 3: Fix FlextCliContext](#phase-3-fix-flextclicontext)
  - [Phase 4: Remove API Wrappers](#phase-4-remove-api-wrappers)
  - [Phase 5: Remove Unused Infrastructure](#phase-5-remove-unused-infrastructure)
  - [Phase 6: Reorganize Tests](#phase-6-reorganize-tests)
- [Implementation Plan](#implementation-plan)
  - [Timeline Overview](#timeline-overview)
  - [Detailed Steps](#detailed-steps)
- [Risk Assessment](#risk-assessment)
  - [Low Risk (High Confidence)](#low-risk-high-confidence)
  - [Medium Risk (Moderate Confidence)](#medium-risk-moderate-confidence)
  - [High Risk (Careful Attention Required)](#high-risk-careful-attention-required)
  - [Rollback Strategy](#rollback-strategy)
- [Success Criteria](#success-criteria)
  - [Code Quality](#code-quality)
  - [Architecture](#architecture)
  - [Documentation](#documentation)
  - [Testing](#testing)
  - [User Experience](#user-experience)
  - [Ecosystem](#ecosystem)
- [Timeline](#timeline)
  - [Week 1: Documentation & Planning](#week-1-documentation-planning)
  - [Week 2: Core Refactoring](#week-2-core-refactoring)
  - [Week 3: Test Reorganization & Polish](#week-3-test-reorganization-polish)
  - [Week 4: Release & Support](#week-4-release-support)
- [Conclusion](#conclusion)

<!-- TOC END -->

**Version**: 0.10.0
**Date**: 2025-01-24
**Status**: 📝 Planning Phase
**Target Release**: Q1 2025

---

## Table of Contents

1. [Executive Summary](#executive-summary)
1. [Current State Analysis](#current-state-analysis-v090)
1. [Target Architecture](#target-architecture)
1. [Detailed Changes](#detailed-changes)
1. [Implementation Plan](#implementation-plan)
1. [Risk Assessment](#risk-assessment)
1. [Success Criteria](#success-criteria)
1. [Timeline](#timeline)

---

## Executive Summary

### Purpose

This refactoring aims to simplify FLEXT-CLI's architecture by removing over-engineering, reducing unnecessary complexity, and aligning with core design principles.

### Key Metrics

| Metric                   | v0.9.0 (Current) | v0.10.0 (Target) | Change               |
| ------------------------ | ---------------- | ---------------- | -------------------- |
| **Lines of Code**        | ~14,000          | ~9,000-10,000    | **-30-40%**          |
| **Service Classes**      | 18               | 3-4              | **-75-80%**          |
| **Module Count**         | 24               | 20               | **-4 modules**       |
| **Async Infrastructure** | Yes (unused)     | No               | **Removed**          |
| **API Methods**          | ~30              | ~15              | **-50%**             |
| **Test Files**           | 21 flat          | ~40 organized    | **Better structure** |

### Benefits

**For Users**:

- ✅ Simpler, more intuitive API
- ✅ Clearer documentation
- ✅ Faster performance (less indirection)
- ✅ Easier debugging

**For Contributors**:

- ✅ Less code to maintain
- ✅ Clearer architecture
- ✅ Easier to extend
- ✅ Better test organization

**For the Project**:

- ✅ Reduced technical debt
- ✅ Better alignment with SOLID principles
- ✅ Improved code quality
- ✅ Lower maintenance burden

---

## Current State Analysis (v0.9.0)

### What Works Well

1. **Core Abstraction**: Click/Rich abstraction is solid
1. **Type Safety**: Comprehensive type annotations
1. **Railway Pattern**: FlextResult[T] used throughout
1. **Test Coverage**: 95%+ test pass rate
1. **FLEXT Integration**: Good flext-core patterns

### Over-Engineering Identified

#### 1. Excessive Service Classes (18 services)

**Problem**: Nearly every class extends FlextService unnecessarily.

```python
# ❌ CURRENT: Too many services
class FlextCliFileTools(FlextService[dict[str, object]]):
    """File operations as a service - OVERKILL"""
    def __init__(self):
        super().__init__()  # Unnecessary overhead
        self.logger = FlextLogger(__name__)

    def read_json_file(self, path: str) -> FlextResult[dict]:
        # Just reading a file - doesn't need service infrastructure
```

**Impact**:

- Unnecessary initialization overhead
- Confusing architecture (everything is a "service")
- Harder to understand what's actually stateful
- More code to maintain

**Services that shouldn't be services**:

- FlextCliFileTools - Stateless I/O
- FlextCliFormatters - Stateless formatting
- FlextCliTables - Stateless formatting
- FlextCliOutput - Stateless formatting
- FlextCliPrompts - Stateless I/O
- FlextCliDebug - Stateless utilities
- FlextCliCommands - Just a dict wrapper
- FlextCliContext - Should be data model!

#### 2. Unused Async/Threading/Plugin Infrastructure

**Problem**: Imported but never used.

```python
# ❌ CURRENT (core.py): Dead code
import asyncio  # 0 async functions found
from concurrent.futures import ThreadPoolExecutor  # Never instantiated
import pluggy  # Plugin system never used
```

**Impact**:

- Misleading to developers
- Suggests features that don't exist
- Maintenance burden
- Confusing mental model

#### 3. Thin API Wrappers

**Problem**: FlextCli has ~15 wrapper methods that just delegate.

```python
# ❌ CURRENT: Unnecessary indirection
class FlextCli:
    def print(self, message: str, style: str | None = None) -> FlextResult[bool]:
        return self.formatters.print(message, style)

    def create_table(self, data: object) -> FlextResult[str]:
        return self.output.format_data(data, format_type="table")

    def read_json_file(self, path: str) -> FlextResult[dict]:
        return self.file_tools.read_json_file(path)

    # ... 12 more similar wrappers
```

**Impact**:

- Bloated API surface
- Two ways to do everything (confusing)
- Harder to document
- No added value

#### 4. FlextCliContext as Service

**Problem**: Context is a service but should be immutable data.

```python
# ❌ CURRENT: Context with service methods
class FlextCliContext(FlextService[CliDataDict]):
    def activate(self) -> FlextResult[bool]: ...
    def deactivate(self) -> FlextResult[bool]: ...
```

**Impact**:

- Mutable state where immutability is better
- Service overhead for simple data
- Violates value object pattern

#### 5. Duplicate Modules

**Problem**: Three modules with duplicate/empty code.

- `validator.py` - Empty stub (22 lines)
- `auth.py` - Duplicates functionality in api.py (300 lines)
- `testing.py` - Test utilities in production code (362 lines)

**Impact**: -684 lines of unnecessary code

#### 6. Over-Complex Test Structure

**Problem**: Some test files are HUGE (70K lines!), no organization.

```
tests/unit/
├── test_config.py (1,821 lines - 70K bytes!)
├── test_core.py (1,670 lines - 64K bytes!)
├── test_file_tools.py (1,284 lines - 49K bytes!)
└── ... (all flat, no organization)
```

**Impact**:

- Hard to navigate
- Slow to run individual tests
- Difficult to maintain

---

## Target Architecture (v0.10.0)

### Design Principles

1. **Services Only for State** - Use FlextService only when managing state
1. **Simple Classes for Utilities** - Stateless operations use simple classes
1. **Value Objects for Data** - Immutable data models using Pydantic
1. **Direct Access Pattern** - No thin wrappers, direct property access
1. **Zero Unused Infrastructure** - Remove async, threading, plugins

### Module Classification

#### Services (3-4 classes only)

**FlextService should be used when**:

- Class manages mutable state (commands, sessions, configuration)
- Class requires dependency injection
- Class needs lifecycle management
- Class has complex initialization

```python
# ✅ FlextCliCore - Stateful service
class FlextCliCore(FlextService[CliDataDict]):
    """Manages commands, sessions, configuration lifecycle."""
    def __init__(self):
        super().__init__()
        self._commands: dict[str, Command] = {}  # STATE
        self._sessions: dict[str, Session] = {}  # STATE
        self._config: FlextCliSettings = FlextCliSettings()  # STATE
```

**Services in v0.10.0**:

1. **FlextCliCore** - Command/session management ✅
1. **FlextCli** - Main API facade (evaluate if needed) ⚠️
1. **FlextCliCmd** - Command execution (evaluate if needed) ⚠️

#### Simple Classes (10+ utilities)

**Simple classes should be used when**:

- Class is stateless
- Methods could be static
- No dependency injection needed
- Just utility functions grouped together

```python
# ✅ FlextCliFileTools - Simple utility class
class FlextCliFileTools:
    """Stateless file operations."""

    @staticmethod
    def read_json_file(path: str) -> FlextResult[dict]:
        """Read JSON file - no state needed."""
        try:
            with open(path) as f:
                return FlextResult[dict].ok(json.load(f))
        except Exception as e:
            return FlextResult[dict].fail(str(e))
```

**Simple Classes in v0.10.0**:

- FlextCliFileTools - File I/O
- FlextCliFormatters - Rich wrapper (already simple)
- FlextCliTables - Table formatting
- FlextCliOutput - Output formatting
- FlextCliPrompts - User input
- FlextCliDebug - Debug utilities
- FlextCliCommands - Command registry (or just use dict)

#### Data Models (Value Objects)

**Value objects should be used when**:

- Class is immutable data
- Compared by value, not identity
- No behavior, just data validation
- Pydantic model is appropriate

```python
# ✅ FlextCliContext - Value Object
from flext_core import FlextModels

class FlextCliContext(m.Value):
    """Immutable execution context."""
    command: str | None = None
    arguments: list[str] = Field(default_factory=list)
    environment_variables: dict[str, object] = Field(default_factory=dict)
    working_directory: str | None = None

    # No methods - just validated data
```

**Value Objects in v0.10.0**:

- FlextCliContext - Execution context
- All models in FlextCliModels.\*

### Direct Access Pattern

**Old (v0.9.0)**: Wrapper methods

```python
cli = FlextCli()
cli.print("Hello")                    # Wrapper method
cli.create_table(data)                 # Wrapper method
cli.read_json_file("config.json")      # Wrapper method
```

**New (v0.10.0)**: Direct access

```python
cli = FlextCli()
cli.formatters.print("Hello")                  # Direct
cli.output.format_data(data, format_type="table")  # Direct
cli.file_tools.read_json_file("config.json")   # Direct
```

**Benefits**:

- Clear ownership (which service handles what)
- No duplicate API surface
- Easier to document
- Simpler to understand

### Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    FlextCli (Main Facade)                     │
│  - Singleton pattern                                          │
│  - Core initialization                                        │
│  - Authentication (business logic, not simple delegation)     │
│  - CLI execution                                              │
└─────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐
│ FlextCliCore     │  │ FlextCliCmd      │  │ Utility Services  │
│ (Service)        │  │ (Service?)       │  │ (Simple Classes)  │
│                  │  │                  │  │                  │
│ • Commands       │  │ • Execute        │  │ • FileTools      │
│ • Sessions       │  │ • Validate       │  │ • Formatters     │
│ • Config         │  │                  │  │ • Tables         │
│ • Statistics     │  │                  │  │ • Output         │
│                  │  │                  │  │ • Prompts        │
│                  │  │                  │  │ • Debug          │
└──────────────────┘  └──────────────────┘  └──────────────────┘
        │                     │                     │
        └─────────────────────┼─────────────────────┘
                              │
                              ▼
                ┌──────────────────────────┐
                │   Data Models            │
                │   (Value Objects)        │
                │                          │
                │ • FlextCliContext        │
                │ • FlextCliModels.*       │
                │ • FlextCliSettings         │
                └──────────────────────────┘
```

---

## Detailed Changes

### Phase 1: Remove Duplication

#### 1.1 Delete Empty/Duplicate Modules

**Files to Delete**:

1. **validator.py** (22 lines)
   - Status: Already empty stub
   - All validation moved to Pydantic v2
   - No imports to update

1. **auth.py** (300 lines)
   - Duplicate of auth functionality in api.py
   - FlextCliAuthService duplicates FlextCli.authenticate()
   - Remove from `__init__.py` exports
   - No external usage found

1. **testing.py** → Move to tests/fixtures/ (362 lines)
   - FlextCliTesting, FlextCliTestRunner, FlextCliMockScenarios
   - Test utilities don't belong in production code
   - Move to `tests/fixtures/testing_utilities.py`
   - Update test imports

**Total Reduction**: -684 lines

### Phase 2: Convert Services to Simple Classes

#### 2.1 FlextCliFileTools

**Before**:

```python
class FlextCliFileTools(FlextService[dict[str, object]]):
    def __init__(self):
        super().__init__()
        self.logger = FlextLogger(__name__)

    def read_json_file(self, path: str) -> FlextResult[dict]:
        # Implementation
```

**After**:

```python
class FlextCliFileTools:
    """Stateless file operations utility."""

    @staticmethod
    def read_json_file(path: str) -> FlextResult[dict]:
        """Read JSON file."""
        # Same implementation, now static
```

**Changes**:

- Remove FlextService inheritance
- Remove `__init__`
- Make methods static (no self needed)
- Remove logger (can use module-level logger if needed)

**Applies to**:

- FlextCliFileTools ✅
- FlextCliTables ✅
- FlextCliOutput ✅
- FlextCliPrompts ✅
- FlextCliDebug ✅
- FlextCliCommands ✅ (or replace with dict)

#### 2.2 FlextCliFormatters

**Current**: Already a simple class (no change needed) ✅

### Phase 3: Fix FlextCliContext

**Note**: FlextCliContext was later removed from the library. Use `m.Cli.CliContext` for context data where needed. The following is kept for historical reference.

**Before**:

```python
class FlextCliContext(FlextService[CliDataDict]):
    """Context as service with methods."""
    def activate(self) -> FlextResult[bool]: ...
    def deactivate(self) -> FlextResult[bool]: ...
```

**After**:

```python
from flext_core import FlextModels

class FlextCliContext(m.Value):
    """Immutable context value object."""
    command: str | None = None
    arguments: list[str] = Field(default_factory=list)
    environment_variables: dict[str, object] = Field(default_factory=dict)
    working_directory: str | None = None
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())

    # No methods - just validated, immutable data
```

**Benefits**:

- Immutable by default
- Simpler mental model
- No lifecycle management needed
- Follows value object pattern

### Phase 4: Remove API Wrappers

**Methods to Remove from FlextCli**:

```python
# ❌ Remove these wrappers:
def print(self, message, style) -> FlextResult[bool]:
    return self.formatters.print(message, style)

def create_table(self, data, headers, title) -> FlextResult[str]:
    return self.output.format_data(...)

def print_table(self, table) -> FlextResult[bool]:
    return self.formatters.print(table)

def create_tree(self, label) -> FlextResult[Any]:
    return self.formatters.create_tree(label)

def format_output(self, data, format_type) -> FlextResult[str]:
    return self.output.format_data(data, format_type)

def read_json_file(self, path) -> FlextResult[dict]:
    return self.file_tools.read_json_file(path)

def write_json_file(self, path, data) -> FlextResult[bool]:
    return self.file_tools.write_json_file(path, data)

def read_yaml_file(self, path) -> FlextResult[dict]:
    return self.file_tools.read_yaml_file(path)

def write_yaml_file(self, path, data) -> FlextResult[bool]:
    return self.file_tools.write_yaml_file(path, data)

def read_csv_file(self, path) -> FlextResult[list]:
    return self.file_tools.read_csv_file(path)

def write_csv_file(self, path, data) -> FlextResult[bool]:
    return self.file_tools.write_csv_file(path, data)

def prompt_user(self, message) -> FlextResult[str]:
    return self.prompts.prompt(message)

def confirm(self, message) -> FlextResult[bool]:
    return self.prompts.confirm(message)

def select(self, message, choices) -> FlextResult[str]:
    return self.prompts.select(message, choices)
```

**Keep in FlextCli**:

```python
# ✅ Keep these (not simple wrappers):
def __init__(self) -> None:
    """Initialize CLI with all services."""

@classmethod
def get_instance(cls) -> FlextCli:
    """Singleton pattern."""

def authenticate(self, credentials) -> FlextResult[str]:
    """Orchestrates authentication (business logic)."""

def command(self, name, **kwargs):
    """CLI command decorator."""

def group(self, name, **kwargs):
    """CLI group decorator."""

def execute_cli(self) -> FlextResult[bool]:
    """Execute CLI application."""

def execute(self) -> FlextResult[dict]:
    """Execute command."""
```

**Total Reduction**: ~15 methods removed, ~350 lines

### Phase 5: Remove Unused Infrastructure

#### 5.1 Remove from core.py

```python
# ❌ Remove unused imports:
import asyncio  # 0 async functions
from concurrent.futures import ThreadPoolExecutor  # Never used
import pluggy  # Plugin system unused

# Evaluate if needed:
from cachetools import LRUCache, TTLCache  # Check actual usage
```

**Estimated Reduction**: ~200-300 lines

### Phase 6: Reorganize Tests

#### 6.1 New Test Structure

```
tests/
├── unit/
│   ├── core/
│   │   ├── test_api.py (from test_api.py, split)
│   │   ├── test_singleton.py
│   │   └── test_service_base.py (from test_core.py, split)
│   ├── io/
│   │   ├── test_json_operations.py (from test_file_tools.py)
│   │   ├── test_yaml_operations.py (from test_file_tools.py)
│   │   └── test_csv_operations.py (from test_file_tools.py)
│   ├── formatting/
│   │   ├── test_rich_formatters.py (from test_formatters.py)
│   │   ├── test_tables.py
│   │   └── test_output.py
│   ├── cli/
│   │   ├── test_click_wrapper.py (from test_cli.py)
│   │   ├── test_commands.py
│   │   ├── test_params.py
│   │   └── test_execution.py (from test_cmd.py)
│   ├── config/
│   │   ├── test_config_loading.py (from test_config.py, split)
│   │   ├── test_config_validation.py (from test_config.py, split)
│   │   └── test_profiles.py (from test_config.py, split)
│   ├── auth/
│   │   ├── test_token_auth.py (from test_api.py)
│   │   └── test_credential_auth.py (from test_api.py)
│   └── models/
│       ├── test_context.py (from test_context.py)
│       └── test_models.py
│
├── integration/
│   ├── test_full_workflow.py (new)
│   ├── test_command_execution.py (new)
│   └── test_config_persistence.py (new)
│
└── fixtures/
    ├── testing_utilities.py (from src/testing.py)
    ├── sample_configs.py (new)
    └── sample_commands.py (new)
```

#### 6.2 Split Large Test Files

**test_config.py** (1,821 lines) → Split into:

- `config/test_config_loading.py` (~600 lines)
- `config/test_config_validation.py` (~600 lines)
- `config/test_profiles.py` (~400 lines)

**test_core.py** (1,670 lines) → Split into:

- `core/test_service_base.py` (~600 lines)
- `core/test_command_registry.py` (~500 lines)
- `core/test_session_management.py` (~400 lines)

**test_file_tools.py** (1,284 lines) → Split into:

- `io/test_json_operations.py` (~400 lines)
- `io/test_yaml_operations.py` (~400 lines)
- `io/test_csv_operations.py` (~400 lines)

**test_api.py** (986 lines) → Split into:

- `core/test_api.py` (~400 lines)
- `auth/test_token_auth.py` (~300 lines)
- `auth/test_credential_auth.py` (~200 lines)

---

## Implementation Plan

### Timeline Overview

| Phase                              | Duration        | Dependencies | Risk   |
| ---------------------------------- | --------------- | ------------ | ------ |
| **Phase 1**: Documentation         | 13-19 hours     | None         | Low    |
| **Phase 2**: Delete duplicates     | 1-2 hours       | Phase 1      | Low    |
| **Phase 3**: Convert services      | 4-6 hours       | Phase 2      | Medium |
| **Phase 4**: Fix context           | 2-3 hours       | Phase 3      | Medium |
| **Phase 5**: Remove wrappers       | 2-3 hours       | Phase 3      | Medium |
| **Phase 6**: Remove infrastructure | 1-2 hours       | Phase 3      | Low    |
| **Phase 7**: Reorganize tests      | 3-4 hours       | All above    | Medium |
| **Phase 8**: Quality gates         | 2-3 hours       | All above    | Low    |
| **Total**                          | **28-42 hours** | Sequential   | Medium |

### Detailed Steps

#### Phase 1: Documentation (Complete First) ✅

See: [IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)

#### Phase 2: Delete Duplicates

1. Delete `validator.py`
1. Delete `auth.py`
1. Move `testing.py` to `tests/fixtures/testing_utilities.py`
1. Update `__init__.py` exports
1. Update imports in tests
1. Run: `make validate`
1. Commit: "refactor: remove duplicate and empty modules"

#### Phase 3: Convert Services to Simple Classes

For each utility class:

1. Remove FlextService inheritance
1. Remove `__init__` method
1. Convert instance methods to static methods
1. Remove `self` parameter
1. Update all calls (no `.` needed before method)
1. Update tests
1. Run: `make validate` after each conversion

Order:

1. FlextCliFileTools (simplest)
1. FlextCliTables
1. FlextCliOutput
1. FlextCliPrompts
1. FlextCliDebug
1. FlextCliCommands (or replace with dict)

Commit after each: "refactor: convert FlextCliFileTools to simple class"

#### Phase 4: Fix FlextCliContext

1. Change inheritance: `FlextService` → `m.Value`
1. Remove service methods: `activate()`, `deactivate()`
1. Add `model_config = ConfigDict(frozen=True)`
1. Update all usage sites
1. Update tests
1. Run: `make validate`
1. Commit: "refactor: convert context to value object"

#### Phase 5: Remove API Wrappers

1. Remove ~15 wrapper methods from `api.py`
1. Update examples in docs/
1. Update tests
1. Run: `make validate`
1. Commit: "refactor: remove API wrapper methods"

#### Phase 6: Remove Unused Infrastructure

1. Remove asyncio imports
1. Remove threading imports
1. Remove pluggy imports
1. Check cachetools usage
1. Remove any unused code
1. Run: `make validate`
1. Commit: "refactor: remove unused infrastructure"

#### Phase 7: Reorganize Tests

1. Create new test directory structure
1. Split large test files
1. Move testing utilities
1. Simplify conftest.py
1. Run: `make test`
1. Commit: "refactor: reorganize test structure"

#### Phase 8: Quality Gates

1. Run: `make validate` (must pass 100%)
1. Run: `make test` (must maintain 95%+ pass rate)
1. Update `__version__.py` → `0.10.0`
1. Update `CHANGELOG.md`
1. Create PR for review
1. Merge to main after approval
1. Tag: `v0.10.0`

---

## Risk Assessment

### Low Risk (High Confidence)

**1. Delete empty/duplicate modules**

- validator.py is empty
- auth.py is duplicate
- testing.py is test-only
- Minimal external impact

**2. Remove unused imports**

- Not referenced anywhere
- No functionality loss
- Easy to verify with grep

**Mitigation**: None needed, straightforward deletions

### Medium Risk (Moderate Confidence)

**1. Convert services to simple classes**

- Changes instantiation pattern
- May affect dependency injection
- Tests need updates

**Mitigation**:

- Convert one at a time
- Run tests after each
- Keep git history clean for easy rollback

**2. Remove API wrappers**

- Breaking change for users
- Migration guide needed
- Examples need updates

**Mitigation**:

- Comprehensive migration guide
- Version bump (0.9→0.10)
- Deprecation warnings (if time permits)

**3. Reorganize tests**

- Large structural change
- Risk of breaking tests during move
- May miss dependencies

**Mitigation**:

- Full test run before starting
- Move and verify incrementally
- Keep backup of working tests

### High Risk (Careful Attention Required)

**1. Change FlextCliContext from service to value object**

- Architectural pattern change
- Affects all context usage
- May have subtle bugs

**Mitigation**:

- Comprehensive test coverage
- Code review by team
- Staged rollout possible

**2. Remove infrastructure from core.py**

- Core module changes risky
- May have hidden dependencies
- Could break ecosystem projects

**Mitigation**:

- Thorough analysis first
- Test with dependent projects
- Rollback plan ready

### Rollback Strategy

If issues arise:

1. **Per-Phase Rollback**: Each phase is a separate commit

   ```bash
   git revert <commit-hash>
   ```

1. **Full Rollback**: Return to v0.9.0

   ```bash
   git checkout v0.9.0
   git checkout -b hotfix/rollback-v0.10
   ```

1. **Partial Rollback**: Keep safe changes, revert risky ones

   ```bash
   git revert <risky-commit-1> <risky-commit-2>
   ```

---

## Success Criteria

### Code Quality

- ✅ 30-40% code reduction achieved
- ✅ Service classes reduced to 3-4
- ✅ Zero unused imports remain
- ✅ `make validate` passes 100%
- ✅ Test coverage maintained (95%+)

### Architecture

- ✅ Simple classes for utilities
- ✅ Services only for stateful logic
- ✅ Data models are Pydantic value objects
- ✅ Zero duplication with flext-core
- ✅ Clear separation of concerns
- ✅ SOLID principles followed

### Documentation

- ✅ All breaking changes documented
- ✅ Migration guide complete
- ✅ Examples updated
- ✅ API reference accurate
- ✅ Architecture docs current

### Testing

- ✅ All tests passing (95%+ rate maintained)
- ✅ Test structure organized
- ✅ No file > 30K lines
- ✅ Integration tests separated
- ✅ Test utilities in fixtures/

### User Experience

- ✅ API simpler and clearer
- ✅ Migration path clear
- ✅ Breaking changes justified
- ✅ Performance maintained or improved
- ✅ Documentation quality improved

### Ecosystem

- ✅ No dependent project breaks
- ✅ flext-core compatibility maintained
- ✅ FLEXT standards followed
- ✅ Zero tolerance rules upheld
- ✅ Production readiness maintained

---

## Timeline

### Week 1: Documentation & Planning

- **Days 1-3**: Create all refactoring documentation
- **Days 4-5**: Update existing documentation
- **Day 6**: Team review and approval
- **Day 7**: Buffer for feedback incorporation

**Deliverables**: All documentation complete and approved

### Week 2: Core Refactoring

- **Day 1**: Delete duplicates, remove dead code
- **Days 2-3**: Convert services to simple classes
- **Day 4**: Fix FlextCliContext
- **Day 5**: Remove API wrappers
- **Day 6**: Quality gates and fixes
- **Day 7**: Buffer

**Deliverables**: Core refactoring complete, tests passing

### Week 3: Test Reorganization & Polish

- **Days 1-2**: Reorganize test structure
- **Day 3**: Split large test files
- **Day 4**: Update conftest.py
- **Days 5-6**: Final quality gates and polish
- **Day 7**: Prepare release

**Deliverables**: v0.10.0 ready for release

### Week 4: Release & Support

- **Day 1**: Create PR and final review
- **Day 2**: Merge to main
- **Day 3**: Tag v0.10.0 and release
- **Days 4-7**: Monitor issues, provide support

**Deliverables**: v0.10.0 released and stable

---

## Conclusion

This refactoring represents a significant improvement to FLEXT-CLI's architecture by:

1. **Removing over-engineering** (18→3-4 services)
1. **Simplifying the API** (no wrapper methods)
1. **Following SOLID principles** (clear responsibilities)
1. **Reducing code** (30-40% fewer lines)
1. **Improving maintainability** (organized tests, clear docs)

While there are breaking changes, the migration path is clear and the benefits justify the effort. The documentation-first approach ensures all stakeholders understand the changes before implementation begins.

**Status**: Ready for team review and approval to proceed

---

**Document Version**: 1.0
**Last Updated**: 2025-01-24
**Authors**: FLEXT Team
**Reviewers**: [Pending]
**Approval**: [Pending]

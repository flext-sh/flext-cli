# Breaking Changes: v0.9.0 → v0.10.0

<!-- TOC START -->

- [Summary](#summary)
- [1. API Wrapper Methods Removed](#1-api-wrapper-methods-removed)
  - [Removed Methods](#removed-methods)
  - [Migration](#migration)
  - [Automated Migration Script](#automated-migration-script)
- [2. Modules Removed/Moved](#2-modules-removedmoved)
  - [2.1 `flext_cli.validator` - Deleted](#21-flextclivalidator-deleted)
  - [2.2 `flext_cli.auth` - Deleted](#22-flextcliauth-deleted)
  - [2.3 `flext_cli.testing` - Moved to tests/](#23-flextclitesting-moved-to-tests)
- [3. FlextCliContext Removed](#3-flextclicontext-removed)
  - [Removed Methods](#removed-methods)
  - [Migration](#migration)
  - [Why This Change](#why-this-change)
- [4. Service Class Instantiation Changes](#4-service-class-instantiation-changes)
  - [What Changed](#what-changed)
  - [If You Instantiated Directly](#if-you-instantiated-directly)
- [5. Async/Threading Removed](#5-asyncthreading-removed)
  - [What Changed](#what-changed)
  - [Migration](#migration)
- [6. Test Structure Changes](#6-test-structure-changes)
  - [What Changed](#what-changed)
  - [Migration](#migration)
- [7. Import Changes](#7-import-changes)
  - [Removed from `__init__.py`](#removed-from-initpy)
  - [Still Available](#still-available)
- [Migration Checklist](#migration-checklist)
  - [[ ] 1. Update API Calls](#1-update-api-calls)
  - [[ ] 2. Update Imports](#2-update-imports)
  - [[ ] 3. Update Context Usage](#3-update-context-usage)
  - [[ ] 4. Run Tests](#4-run-tests)
  - [[ ] 5. Update Type Hints (if applicable)](#5-update-type-hints-if-applicable)
- [Compatibility Table](#compatibility-table)
- [Deprecation Timeline](#deprecation-timeline)
- [Getting Help](#getting-help)
  - [If Migration Fails](#if-migration-fails)
  - [Support Resources](#support-resources)
- [FAQ](#faq)

<!-- TOC END -->

**Complete list of all breaking changes with fixes**

> ⚠️ **Important**: v0.10.0 contains multiple breaking changes. Review this document carefully before upgrading.

______________________________________________________________________

## Summary

| Category            | Breaking Changes       | Impact Level              |
| ------------------- | ---------------------- | ------------------------- |
| **API Methods**     | 15 methods removed     | **HIGH** - Most common    |
| **Module Removal**  | 3 modules deleted      | **MEDIUM** - If used      |
| **Context**         | Service → Value Object | **MEDIUM** - If activated |
| **Service Classes** | 15 classes simplified  | **LOW** - Internal        |
| **Test Utilities**  | Moved to tests/        | **LOW** - Tests only      |

**Estimated Migration Time**: 30-60 minutes

______________________________________________________________________

## 1. API Wrapper Methods Removed

**Impact**: HIGH - Affects most users

### Removed Methods

All these methods have been removed from `FlextCli`:

```python
# ❌ REMOVED - No longer available
cli.print(message, style)
cli.create_table(data, headers, title)
cli.print_table(table)
cli.create_tree(label)
cli.format_output(data, format_type)
cli.read_json_file(path)
cli.write_json_file(path, data)
cli.read_yaml_file(path)
cli.write_yaml_file(path, data)
cli.read_csv_file(path)
cli.write_csv_file(path, data)
cli.prompt_user(message)
cli.confirm(message)
cli.select(message, choices)
cli.create_live_display()
```

### Migration

Replace with direct access:

```python
# Print operations
cli.print("msg")                 → cli.formatters.print("msg")
cli.print("msg", style="success") → cli.formatters.print("msg", style="success")

# Table operations
cli.create_table(data)           → cli.output.format_data(data, format_type="table")
cli.print_table(table)           → cli.formatters.print(table)

# File operations
cli.read_json_file(path)         → cli.file_tools.read_json_file(path)
cli.write_json_file(path, data)  → cli.file_tools.write_json_file(path, data)
cli.read_yaml_file(path)         → cli.file_tools.read_yaml_file(path)
cli.write_yaml_file(path, data)  → cli.file_tools.write_yaml_file(path, data)
cli.read_csv_file(path)          → cli.file_tools.read_csv_file(path)
cli.write_csv_file(path, data)   → cli.file_tools.write_csv_file(path, data)

# Interactive prompts
cli.prompt_user(msg)             → cli.prompts.prompt(msg)
cli.confirm(msg)                 → cli.prompts.confirm(msg)
cli.select(msg, choices)         → cli.prompts.select(msg, choices)

# Formatting
cli.format_output(data, fmt)     → cli.output.format_data(data, format_type=fmt)
cli.create_tree(label)           → cli.formatters.create_tree(label)
```

### Automated Migration Script

```bash
#!/bin/bash
# save as: migrate_api_calls.sh

# Print methods
find . -name "*.py" -type f -exec sed -i \
  's/cli\.print(/cli.formatters.print(/g' {} +

# File operations
find . -name "*.py" -type f -exec sed -i \
  's/cli\.read_json_file(/cli.file_tools.read_json_file(/g' {} +
find . -name "*.py" -type f -exec sed -i \
  's/cli\.write_json_file(/cli.file_tools.write_json_file(/g' {} +
find . -name "*.py" -type f -exec sed -i \
  's/cli\.read_yaml_file(/cli.file_tools.read_yaml_file(/g' {} +
find . -name "*.py" -type f -exec sed -i \
  's/cli\.write_yaml_file(/cli.file_tools.write_yaml_file(/g' {} +
find . -name "*.py" -type f -exec sed -i \
  's/cli\.read_csv_file(/cli.file_tools.read_csv_file(/g' {} +
find . -name "*.py" -type f -exec sed -i \
  's/cli\.write_csv_file(/cli.file_tools.write_csv_file(/g' {} +

# Prompts
find . -name "*.py" -type f -exec sed -i \
  's/cli\.prompt_user(/cli.prompts.prompt(/g' {} +
find . -name "*.py" -type f -exec sed -i \
  's/cli\.confirm(/cli.prompts.confirm(/g' {} +
find . -name "*.py" -type f -exec sed -i \
  's/cli\.select(/cli.prompts.select(/g' {} +

# Output formatting
find . -name "*.py" -type f -exec sed -i \
  's/cli\.format_output(/cli.output.format_data(/g' {} +

echo "Migration complete! Review changes with: git diff"
```

______________________________________________________________________

## 2. Modules Removed/Moved

**Impact**: MEDIUM - Only if directly imported

### 2.1 `flext_cli.validator` - Deleted

```python
# ❌ REMOVED
from flext_cli import FlextCliValidator
from flext_cli import *

# ✅ FIX: Validation is now in Pydantic models
from flext_cli import FlextCliModels
from pydantic import Field, field_validator
```

**Reason**: Was empty stub, all validation moved to Pydantic v2

### 2.2 `flext_cli.auth` - Deleted

```python
# ❌ REMOVED
from flext_cli import FlextCliAuthService
from flext_cli import FlextCliAuthService

# ✅ FIX: Use FlextCli.authenticate()
from flext_cli import FlextCli
cli = FlextCli()
result = cli.authenticate({"token": "abc123"})
```

**Reason**: Duplicated functionality in `api.py`

### 2.3 `flext_cli.testing` - Moved to tests/

```python
# ❌ REMOVED from production code
from flext_cli import FlextCliTesting, FlextCliTestRunner, FlextCliMockScenarios

# ✅ FIX: Import from test fixtures
from tests.fixtures.testing_utilities import (
    FlextCliTesting,
    FlextCliTestRunner,
    FlextCliMockScenarios
)
```

**Reason**: Test utilities don't belong in production library

______________________________________________________________________

## 3. FlextCliContext Removed

**Impact**: MEDIUM - If you used FlextCliContext or CLI execution context

`FlextCliContext` was removed from the library. Remove any imports and usages. Use `m.Cli.CliContext` (Pydantic Value with `cwd`, `env`, `args`, `output_format`) if you need a simple context data model, or pass command/arguments directly where needed.

______________________________________________________________________

## 4. Service Class Instantiation Changes

**Impact**: LOW - Internal changes, mostly transparent

### What Changed

15 classes changed from services to simple classes:

- FlextCliFileTools
- FlextCliTables
- FlextCliOutput
- FlextCliPrompts
- FlextCliDebug
- FlextCliCommands (or replaced with dict)
- ... and 9 more

### If You Instantiated Directly

```python
# ❌ OLD (if you did this)
file_tools = FlextCliFileTools()  # Was a service
result = file_tools.read_json_file("config.json")

# ✅ NEW - Static methods
result = FlextCliFileTools.read_json_file("config.json")

# ✅ OR - Through main CLI (recommended)
cli = FlextCli()
result = cli.file_tools.read_json_file("config.json")
```

**Note**: Most users access through `FlextCli` instance, so no changes needed

______________________________________________________________________

## 5. Async/Threading Removed

**Impact**: LOW - Was never used

### What Changed

```python
# ❌ REMOVED - Never actually worked
import asyncio  # No longer imported in core.py
from concurrent.futures import ThreadPoolExecutor  # Removed
import pluggy  # Plugin system removed
```

### Migration

**No action needed** - these were never functional, just imported

If you wrote code expecting async:

```python
# ❌ This never worked anyway
await cli.some_async_method()  # Never existed

# ✅ All operations are synchronous
result = cli.formatters.print("message")  # Sync
```

______________________________________________________________________

## 6. Test Structure Changes

**Impact**: LOW - Only affects test code

### What Changed

Tests reorganized into feature-based structure:

```
# ❌ OLD
tests/unit/test_*.py  # All flat

# ✅ NEW
tests/unit/core/test_*.py
tests/unit/io/test_*.py
tests/unit/formatting/test_*.py
tests/unit/cli/test_*.py
tests/unit/config/test_*.py
tests/unit/auth/test_*.py
tests/unit/models/test_*.py
tests/integration/test_*.py
```

### Migration

If you import from test modules:

```python
# ❌ OLD
from tests.unit.test_config import SomeTestHelper

# ✅ NEW
from tests.unit.config.test_config_loading import SomeTestHelper
```

______________________________________________________________________

## 7. Import Changes

**Impact**: LOW - Only if you imported removed modules

### Removed from `__init__.py`

```python
# ❌ REMOVED from flext_cli
FlextCliAuthService  # Use FlextCli.authenticate()
FlextCliTesting  # Move to tests/fixtures/testing_utilities
FlextCliTestRunner  # Move to tests/fixtures/testing_utilities
FlextCliMockScenarios  # Move to tests/fixtures/testing_utilities
```

### Still Available

All other exports remain:

```python
# ✅ Still available
from flext_cli import (
    FlextCli,  # Main API
    FlextCliSettings,  # Configuration
    FlextCliCore,  # Core service
    FlextCliFormatters,  # Formatting
    FlextCliTables,  # Tables
    FlextCliOutput,  # Output
    FlextCliFileTools,  # File operations
    FlextCliPrompts,  # User input
    FlextCliCmd,  # Command execution
    FlextCliCommands,  # Command management
    FlextCliDebug,  # Debug utilities
    FlextCliModels,  # Data models
    FlextCliTypes,  # Type definitions
    FlextCliProtocols,  # Protocols
    FlextCliMixins,  # Mixins
    FlextCliCli,  # CLI framework wrapper
    FlextCliCommonParams,  # CLI parameters
    __version__,  # Version string
)
```

______________________________________________________________________

## Migration Checklist

Use this checklist to ensure complete migration:

### [ ] 1. Update API Calls

- [ ] Replace `cli.print()` with `cli.formatters.print()`
- [ ] Replace `cli.read_json_file()` with `cli.file_tools.read_json_file()`
- [ ] Replace `cli.confirm()` with `cli.prompts.confirm()`
- [ ] Update all other wrapper method calls (see section 1)

### [ ] 2. Update Imports

- [ ] Remove `FlextCliAuthService` imports
- [ ] Update `FlextCliTesting` imports (if used)
- [ ] Remove `FlextCliValidator` imports (if any)

### [ ] 3. Update Context Usage

- [ ] Remove `context.activate()` calls
- [ ] Remove `context.deactivate()` calls
- [ ] Remove any context state mutation
- [ ] Treat context as immutable data

### [ ] 4. Run Tests

- [ ] Run full test suite: `pytest`
- [ ] Fix any import errors
- [ ] Fix any AttributeErrors
- [ ] Verify functionality

### [ ] 5. Update Type Hints (if applicable)

- [ ] Check any explicit type hints for removed methods
- [ ] Update protocol implementations if needed

______________________________________________________________________

## Compatibility Table

| Feature            | v0.9.0      | v0.10.0     | Compatible?     |
| ------------------ | ----------- | ----------- | --------------- |
| Python 3.13+       | ✅ Required | ✅ Required | ✅ Yes          |
| flext-core         | ✅ v0.9.x   | ✅ v0.9.x+  | ✅ Yes          |
| FlextResult[T]     | ✅          | ✅          | ✅ Yes          |
| Railway Pattern    | ✅          | ✅          | ✅ Yes          |
| Type Safety        | ✅          | ✅          | ✅ Yes          |
| API Wrappers       | ✅          | ❌ Removed  | ❌ No           |
| Context.activate() | ✅          | ❌ Removed  | ❌ No           |
| Auth module        | ✅          | ❌ Removed  | ❌ No           |
| Testing in prod    | ✅          | ❌ Moved    | ❌ No           |
| Async/Threading    | ⚠️ Imported | ❌ Removed  | ⚠️ N/A (unused) |

______________________________________________________________________

## Deprecation Timeline

| Version      | Status           | Notes                                            |
| ------------ | ---------------- | ------------------------------------------------ |
| **v0.9.0**   | Maintenance Mode | Security fixes only                              |
| **v0.10.0**  | Current          | Stable, recommended                              |
| **v0.11.0+** | Future           | New features (backwards compatible with v0.10.0) |

**Recommendation**: Migrate to v0.10.0 within 3 months

______________________________________________________________________

## Getting Help

### If Migration Fails

1. **Check Error Message**: Most issues are import or attribute errors
1. **Review This Document**: Find the specific breaking change
1. **Use Migration Script**: Automated find-and-replace helps
1. **Open Issue**: [GitHub Issues](https://github.com/flext-sh/flext-cli/issues)

### Support Resources

- **[Migration Guide](migration-guide-v0.9-to-v0.10.md)** - Step-by-step migration
- **[Architecture Comparison](architecture-comparison.md)** - Before/after comparison
- **[API Reference](../api-reference.md)** - Complete v0.10.0 API
- **[Examples](../../examples/)** - Updated code examples

______________________________________________________________________

## FAQ

**Q: Can I use both v0.9.0 and v0.10.0 patterns?**
A: No, v0.10.0 removes the old patterns completely.

**Q: How long is v0.9.0 supported?**
A: Security fixes only. Migrate to v0.10.0 for new features.

**Q: Will there be more breaking changes?**
A: We aim for stability. Future versions should be backwards compatible with v0.10.0.

**Q: What if I can't migrate immediately?**
A: Stay on v0.9.0 temporarily, but plan migration within 3 months.

**Q: Can I stage the migration?**
A: No, changes must be made together (imports, API calls, context usage).

______________________________________________________________________

**Document Version**: 1.0
**Last Updated**: 2025-01-24
**Applies to**: v0.10.0 only

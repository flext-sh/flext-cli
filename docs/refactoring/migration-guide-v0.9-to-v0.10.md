# Migration Guide: v0.9.0 → v0.10.0

**Estimated Migration Time**: 30-60 minutes for typical projects

> **📘 Quick Summary**: v0.10.0 introduces a **direct access pattern** and removes API wrapper methods. Instead of `cli.print()`, you now use `cli.formatters.print()`. This makes ownership clearer and the API simpler.

---

## Table of Contents

1. [Overview](#overview)
2. [Breaking Changes](#breaking-changes)
3. [Step-by-Step Migration](#step-by-step-migration)
4. [Quick Reference](#quick-reference)
5. [FAQ](#faq)
6. [Getting Help](#getting-help)

---

## Overview

### What Changed

v0.10.0 simplifies FLEXT-CLI by:

- ✅ **Direct Access Pattern**: Call methods on specific services (e.g., `cli.formatters.print()`)
- ✅ **Removed Wrappers**: No more thin wrapper methods in FlextCli
- ✅ **Simplified Services**: Only 3-4 service classes (down from 18)
- ✅ **Context as Value Object**: FlextCliContext is now immutable data
- ✅ **Removed Complexity**: No unused async/threading/plugin code

### Why These Changes

**Clarity**: It's now obvious which service handles what
**Simplicity**: One way to do things, not multiple
**Maintainability**: 30-40% less code to maintain
**Performance**: Less indirection, faster execution

### Compatibility

- ✅ **Python 3.13+**: Still required
- ✅ **flext-core**: Compatible with current version
- ✅ **Railway Pattern**: FlextResult[T] still used throughout
- ✅ **Type Safety**: Still 100% type-safe

---

## Breaking Changes

### 1. API Method Removal (Most Common Impact)

API wrapper methods have been removed. Use direct access instead.

#### Output Methods

```python
# ❌ v0.9.0 (OLD - No longer works)
cli = FlextCli()
cli.print("Hello, World!")
cli.print("Success!", style="success")

# ✅ v0.10.0 (NEW - Use this)
cli = FlextCli()
cli.formatters.print("Hello, World!")
cli.formatters.print("Success!", style="success")
```

```python
# ❌ v0.9.0 (OLD)
table = cli.create_table(data=users, headers=["Name", "Age"])
cli.print_table(table)

# ✅ v0.10.0 (NEW)
result = cli.output.format_data(
    data=users,
    format_type="table",
    headers=["Name", "Age"]
)
cli.formatters.print(result.unwrap())
```

#### File Operations

```python
# ❌ v0.9.0 (OLD)
config_result = cli.read_json_file("config.json")
cli.write_json_file("output.json", data)
cli.read_yaml_file("settings.yaml")
cli.read_csv_file("data.csv")

# ✅ v0.10.0 (NEW)
config_result = cli.file_tools.read_json_file("config.json")
cli.file_tools.write_json_file("output.json", data)
cli.file_tools.read_yaml_file("settings.yaml")
cli.file_tools.read_csv_file("data.csv")
```

#### Interactive Prompts

```python
# ❌ v0.9.0 (OLD)
name = cli.prompt_user("Enter your name:")
confirmed = cli.confirm("Continue?")
choice = cli.select("Select option:", ["A", "B", "C"])

# ✅ v0.10.0 (NEW)
name = cli.prompts.prompt("Enter your name:")
confirmed = cli.prompts.confirm("Continue?")
choice = cli.prompts.select("Select option:", ["A", "B", "C"])
```

#### Output Formatting

```python
# ❌ v0.9.0 (OLD)
json_str = cli.format_output(data, format_type="json")
yaml_str = cli.format_output(data, format_type="yaml")
table_str = cli.format_output(data, format_type="table")

# ✅ v0.10.0 (NEW)
json_str = cli.output.format_data(data, format_type="json")
yaml_str = cli.output.format_data(data, format_type="yaml")
table_str = cli.output.format_data(data, format_type="table")
```

### 2. FlextCliContext Changes

Context is now an immutable value object (no longer a service).

```python
# ❌ v0.9.0 (OLD)
context = FlextCliContext(command="test")
context.activate()  # Method no longer exists
context.is_active = True  # Can't modify
context.deactivate()  # Method no longer exists

# ✅ v0.10.0 (NEW)
context = FlextCliContext(
    command="test",
    arguments=["arg1", "arg2"],
    environment_variables={"ENV": "prod"}
)
# Context is immutable - create new one to "change" it
new_context = FlextCliContext(
    command="test2",
    arguments=context.arguments,  # Copy what you want
    environment_variables=context.environment_variables
)
```

### 3. Service Class Instantiation

Most utility classes are now simple classes (no service inheritance).

```python
# ❌ v0.9.0 (OLD - Some classes were services)
file_tools = FlextCliFileTools()  # Was FlextService
result = file_tools.read_json_file("config.json")

# ✅ v0.10.0 (NEW - Static methods)
result = FlextCliFileTools.read_json_file("config.json")
# Or through main CLI:
cli = FlextCli()
result = cli.file_tools.read_json_file("config.json")
```

### 4. Test Utilities Moved

```python
# ❌ v0.9.0 (OLD)
from flext_cli import FlextCliTesting, FlextCliTestRunner

# ✅ v0.10.0 (NEW)
from tests.fixtures.testing_utilities import (
    FlextCliTesting,
    FlextCliTestRunner
)
```

### 5. Removed Modules

These modules no longer exist:

- ❌ `flext_cli.validator` (was already empty)
- ❌ `flext_cli.auth` (functionality in `api.py`)
- ❌ `flext_cli.testing` (moved to tests/)

```python
# ❌ v0.9.0 (OLD - Will fail)
from flext_cli import FlextCliAuthService

# ✅ v0.10.0 (NEW - Use FlextCli.authenticate())
cli = FlextCli()
result = cli.authenticate({"token": "abc123"})
```

---

## Step-by-Step Migration

### Step 1: Update Imports (5 minutes)

**Action**: Check if you import removed modules.

```bash
# Search your codebase for removed imports
grep -r "from flext_cli import.*AuthService" .
grep -r "from flext_cli import.*Testing" .
grep -r "from flext_cli import.*Validator" .
```

**Fix**: Remove or update these imports.

### Step 2: Replace API Wrapper Calls (15-30 minutes)

**Action**: Find and replace wrapper method calls.

#### Automated Find-and-Replace

Use your IDE or command-line tools:

```bash
# Print methods
find . -name "*.py" -exec sed -i 's/cli\.print(/cli.formatters.print(/g' {} +

# File operations
find . -name "*.py" -exec sed -i 's/cli\.read_json_file(/cli.file_tools.read_json_file(/g' {} +
find . -name "*.py" -exec sed -i 's/cli\.write_json_file(/cli.file_tools.write_json_file(/g' {} +
find . -name "*.py" -exec sed -i 's/cli\.read_yaml_file(/cli.file_tools.read_yaml_file(/g' {} +
find . -name "*.py" -exec sed -i 's/cli\.write_yaml_file(/cli.file_tools.write_yaml_file(/g' {} +
find . -name "*.py" -exec sed -i 's/cli\.read_csv_file(/cli.file_tools.read_csv_file(/g' {} +
find . -name "*.py" -exec sed -i 's/cli\.write_csv_file(/cli.file_tools.write_csv_file(/g' {} +

# Prompts
find . -name "*.py" -exec sed -i 's/cli\.prompt_user(/cli.prompts.prompt(/g' {} +
find . -name "*.py" -exec sed -i 's/cli\.confirm(/cli.prompts.confirm(/g' {} +
find . -name "*.py" -exec sed -i 's/cli\.select(/cli.prompts.select(/g' {} +

# Output formatting
find . -name "*.py" -exec sed -i 's/cli\.format_output(/cli.output.format_data(/g' {} +
find . -name "*.py" -exec sed -i 's/cli\.create_table(/cli.output.format_data(/g' {} +
```

⚠️ **Warning**: Always backup your code before running automated replacements!

#### Manual Review

After automated replacement, manually check:

1. Method signatures (some changed slightly)
2. Error handling (still uses FlextResult[T])
3. Type hints (may need updates)

### Step 3: Update Context Usage (5 minutes)

**Action**: Find all context.activate() and context.deactivate() calls.

```bash
grep -r "context\.activate()" .
grep -r "context\.deactivate()" .
```

**Fix**: Remove these calls or rethink the logic.

```python
# ❌ OLD
context = FlextCliContext(command="test")
context.activate()
# ... use context
context.deactivate()

# ✅ NEW - Context is just data
context = FlextCliContext(command="test")
# ... use context (no activate/deactivate needed)
```

### Step 4: Run Tests (5-15 minutes)

```bash
# Run full test suite
pytest

# Or with coverage
pytest --cov=your_module

# Fix any failures
```

Common test failures:

- Missing `.formatters` or `.file_tools` in calls
- Context activate/deactivate assertions
- Import errors from removed modules

### Step 5: Update Type Hints (If Needed)

```python
# ❌ OLD (if you had type hints)
def process_cli(cli: FlextCli) -> None:
    cli.print("Processing...")

# ✅ NEW (type hints still work)
def process_cli(cli: FlextCli) -> None:
    cli.formatters.print("Processing...")
```

Type hints for FlextCli don't change - only method calls do.

---

## Quick Reference

### Complete Method Mapping

| v0.9.0 (OLD)                      | v0.10.0 (NEW)                                       |
| --------------------------------- | --------------------------------------------------- |
| `cli.print(msg)`                  | `cli.formatters.print(msg)`                         |
| `cli.create_table(data)`          | `cli.output.format_data(data, format_type="table")` |
| `cli.print_table(table)`          | `cli.formatters.print(table)`                       |
| `cli.create_tree(label)`          | `cli.formatters.create_tree(label)`                 |
| `cli.format_output(data, fmt)`    | `cli.output.format_data(data, format_type=fmt)`     |
| `cli.read_json_file(path)`        | `cli.file_tools.read_json_file(path)`               |
| `cli.write_json_file(path, data)` | `cli.file_tools.write_json_file(path, data)`        |
| `cli.read_yaml_file(path)`        | `cli.file_tools.read_yaml_file(path)`               |
| `cli.write_yaml_file(path, data)` | `cli.file_tools.write_yaml_file(path, data)`        |
| `cli.read_csv_file(path)`         | `cli.file_tools.read_csv_file(path)`                |
| `cli.write_csv_file(path, data)`  | `cli.file_tools.write_csv_file(path, data)`         |
| `cli.prompt_user(msg)`            | `cli.prompts.prompt(msg)`                           |
| `cli.confirm(msg)`                | `cli.prompts.confirm(msg)`                          |
| `cli.select(msg, choices)`        | `cli.prompts.select(msg, choices)`                  |

### Services Reference

Access these through FlextCli instance:

| Service          | Methods                                       | Purpose                  |
| ---------------- | --------------------------------------------- | ------------------------ |
| `cli.formatters` | `print()`, `create_tree()`, etc.              | Rich terminal formatting |
| `cli.output`     | `format_data()`, etc.                         | Output management        |
| `cli.file_tools` | `read_json_file()`, `write_yaml_file()`, etc. | File I/O                 |
| `cli.prompts`    | `prompt()`, `confirm()`, `select()`           | User input               |
| `cli.core`       | `execute_command()`, etc.                     | Command management       |
| `cli.cmd`        | `execute()`                                   | Command execution        |

---

## FAQ

### Q: Why remove wrapper methods

**A**: Wrapper methods added no value and made the API confusing. Now there's one clear way to do each operation.

### Q: Will this break my code

**A**: Yes, if you use wrapper methods. But the migration is straightforward - mostly find-and-replace.

### Q: Can I use both old and new patterns

**A**: No, v0.10.0 removes the old wrapper methods completely. You must migrate.

### Q: How long does migration take

**A**: Typically 30-60 minutes for a project. Most of it is automated find-and-replace.

### Q: Is the migration tool available

**A**: Not yet, but the find-and-replace commands above work well. We may add a tool in the future.

### Q: What if I have a large codebase

**A**: Start with automated find-and-replace, then:

1. Run tests to find issues
2. Fix issues one module at a time
3. Consider a staged rollout

### Q: Will there be more breaking changes

**A**: We aim for stability. v0.10.0 is a major cleanup. Future versions should be backwards compatible.

### Q: Can I stay on v0.9.0

**A**: Yes, but v0.10.0 has improvements and will receive ongoing support. v0.9.0 is now in maintenance mode.

### Q: What about performance

**A**: v0.10.0 is **faster** due to less indirection. You may notice 10-20% speed improvements.

### Q: Are there new features

**A**: v0.10.0 focuses on simplification. New features will come in v0.11.x and later.

### Q: Where's the full changelog

**A**: See [CHANGELOG.md](../../CHANGELOG.md) for complete details.

---

## Examples

### Example 1: Simple CLI Application

```python
# ❌ v0.9.0
from flext_cli import FlextCli

def main():
    cli = FlextCli()
    cli.print("Welcome!", style="success")

    config = cli.read_json_file("config.json").unwrap()
    cli.print(f"Loaded config: {config['name']}")

    if cli.confirm("Continue?").unwrap():
        cli.print("Processing...")
        # ... process
        cli.print("Done!", style="success")

# ✅ v0.10.0
from flext_cli import FlextCli

def main():
    cli = FlextCli()
    cli.formatters.print("Welcome!", style="success")

    config = cli.file_tools.read_json_file("config.json").unwrap()
    cli.formatters.print(f"Loaded config: {config['name']}")

    if cli.prompts.confirm("Continue?").unwrap():
        cli.formatters.print("Processing...")
        # ... process
        cli.formatters.print("Done!", style="success")
```

### Example 2: Data Processing Script

```python
# ❌ v0.9.0
from flext_cli import FlextCli

def process_data():
    cli = FlextCli()

    # Read input
    data = cli.read_csv_file("input.csv").unwrap()
    cli.print(f"Loaded {len(data)} records")

    # Process
    results = [process_record(r) for r in data]

    # Output
    table = cli.create_table(results, headers=["ID", "Status"])
    cli.print_table(table)

    # Save
    cli.write_json_file("results.json", results)
    cli.print("Results saved!", style="success")

# ✅ v0.10.0
from flext_cli import FlextCli

def process_data():
    cli = FlextCli()

    # Read input
    data = cli.file_tools.read_csv_file("input.csv").unwrap()
    cli.formatters.print(f"Loaded {len(data)} records")

    # Process
    results = [process_record(r) for r in data]

    # Output
    table_result = cli.output.format_data(
        results,
        format_type="table",
        headers=["ID", "Status"]
    )
    cli.formatters.print(table_result.unwrap())

    # Save
    cli.file_tools.write_json_file("results.json", results)
    cli.formatters.print("Results saved!", style="success")
```

### Example 3: Context Usage

```python
# ❌ v0.9.0
from flext_cli import FlextCliContext

def run_command(command: str, args: list[str]):
    context = FlextCliContext(command=command, arguments=args)
    context.activate()

    try:
        # ... execute command with context
        pass
    finally:
        context.deactivate()

# ✅ v0.10.0
from flext_cli import FlextCliContext

def run_command(command: str, args: list[str]):
    # Context is just immutable data
    context = FlextCliContext(command=command, arguments=args)

    # ... execute command with context
    # No activate/deactivate needed
```

---

## Getting Help

### Documentation

- **[Refactoring Plan](refactoring-plan-v0.10.0.md)** - Technical details
- **[Architecture](../architecture.md)** - New architecture explained
- **[API Reference](../api-reference.md)** - Complete API documentation
- **[Breaking Changes](breaking-changes.md)** - Detailed breaking change list

### Support Channels

- **GitHub Issues**: [Report issues](https://github.com/flext/flext-cli/issues)
- **Discussions**: [Ask questions](https://github.com/flext/flext-cli/discussions)
- **Documentation**: [Full docs](../)

### Migration Assistance

If you need help migrating:

1. Open a GitHub issue with "Migration Help" label
2. Include code samples and specific questions
3. We'll provide guidance

### Reporting Problems

Found a bug after migrating?

1. Check if it's a known issue
2. Create a minimal reproduction
3. Open a GitHub issue with:
   - v0.9.0 code (before)
   - v0.10.0 code (after)
   - Error message and stack trace

---

## Summary

v0.10.0 brings significant improvements through simplification:

✅ **Direct Access Pattern** - Clear ownership
✅ **Removed Wrappers** - One way to do things
✅ **Simpler Architecture** - Less complexity
✅ **Better Performance** - Less indirection
✅ **Easier Maintenance** - 30-40% less code

**Migration is straightforward** - mostly find-and-replace.

**Estimated time: 30-60 minutes**

We're confident you'll appreciate the simpler, cleaner API once migrated!

---

**Document Version**: 1.0
**Last Updated**: 2025-01-24
**Questions?**: [Open an issue](https://github.com/flext/flext-cli/issues)

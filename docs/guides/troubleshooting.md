<!-- Generated from docs/guides/troubleshooting.md for flext-cli. -->

<!-- Source of truth: workspace docs/guides/. -->

# flext-cli - FLEXT Troubleshooting Guide

> Project profile: `flext-cli`

<!-- TOC START -->
- [Quick Diagnosis](#quick-diagnosis)
  - [Health Check Commands](#health-check-commands)
  - [System Status](#system-status)
- [Common Issues](#common-issues)
  - [1. Import Errors](#1-import-errors)
  - [r](#r)
  - [2. Type Checking Errors](#2-type-checking-errors)
  - [3. Test Failures](#3-test-failures)
  - [4. Configuration Issues](#4-configuration-issues)
  - [5. LDIF Processing Issues](#5-ldif-processing-issues)
  - [6. Migration Issues](#6-migration-issues)
  - [7. Performance Issues](#7-performance-issues)
- [Debugging Techniques](#debugging-techniques)
  - [1. Logging Configuration](#1-logging-configuration)
  - [2. Exception Handling](#2-exception-handling)
  - [3. Debug Mode](#3-debug-mode)
  - [4. Step-by-Step Debugging](#4-step-by-step-debugging)
- [Error Codes Reference](#error-codes-reference)
  - [FLEXT Core Errors](#flext-core-errors)
  - [LDIF Processing Errors](#ldif-processing-errors)
  - [API Errors](#api-errors)
- [Performance Troubleshooting](#performance-troubleshooting)
  - [Memory Issues](#memory-issues)
  - [CPU Issues](#cpu-issues)
- [Getting Help](#getting-help)
  - [Self-Service Resources](#self-service-resources)
  - [Community Support](#community-support)
  - [Reporting Issues](#reporting-issues)
  - [Your minimal example here](#your-minimal-example-here)
- [Prevention](#prevention)
  - [Best Practices](#best-practices)
- [Resources](#resources)
<!-- TOC END -->

This guide covers common issues, their solutions, and debugging techniques for FLEXT applications and libraries.

## Quick Diagnosis

### Health Check Commands

```bash
# Check overall system health
make val VALIDATE_SCOPE=workspace

# Check the current project slice
make check PROJECT=flext-cli
make test PROJECT=flext-cli
make scan PROJECT=flext-cli

# Check individual projects
make check PROJECT=flext-core
make check PROJECT=flext-ldif
make check PROJECT=flext-api
```

### System Status

```bash
# Check Python version
python --version  # Should be 3.13+

# Check Poetry environment
poetry env info

# Check dependencies
poetry show --tree

# Check git status
git status
```

## Common Issues

### 1. Import Errors

#### Problem: ModuleNotFoundError

```text
# Error
ModuleNotFoundError: No module named 'flext_core'
```

#### Solutions

**Check PYTHONPATH:**

```bash
source .venv/bin/activate
unset PYTHONPATH
python -c "import flext_core; print(flext_core.__file__)"
```

**Reinstall dependencies:**

```bash
make clean
make boot
```

**Check Poetry environment:**

```bash
poetry env info
poetry install
```

### Import Diagnostics

```python
# Debug import issues
import sys

print("Python path:")
for path in sys.path:
    print(f"  {path}")

print("\nTrying to import flext_core...")
try:
    import flext_core

    print(f"Success: {flext_core.__file__}")
except ImportError as e:
    print(f"Failed: {e}")
```

If the import still fails, activate the workspace `.venv` and rerun the check.

### 2. Type Checking Errors

#### Problem: MyPy errors

```text
# Error
error: Argument 1 to "process" has incompatible type "str"; expected "t.JsonMapping"
```

#### Solutions

**Fix type annotations:**

```text
# ❌ WRONG
def process(data):
    return data


# ✅ CORRECT
def process(data: t.JsonMapping) -> p.Result[ProcessedData]:
    return r.ok(ProcessedData(**data))
```

**Run MyPy with details:**

```bash
make check PROJECT=flext-cli CHECK_GATES=mypy FILES='src/module.py'
```

**Check specific error:**

```bash
make check PROJECT=flext-cli CHECK_GATES=mypy
```

### 3. Test Failures

#### Problem: Tests failing

```text
# Error
AssertionError: Expected success but got failure
```

#### Solutions

**Run with verbose output:**

```bash
pytest tests/unit/test_module.py -vv --tb=long
```

**Debug specific test:**

```bash
pytest tests/unit/test_module.py::TestClass::test_method -v --pdb
```

**Check test data:**

```python
def test_with_debug():
    result = my_function()
    print(f"Result: {result}")
    print(f"Success: {result.success}")
    if result.failure:
        print(f"Error: {result.failure()}")
    assert result.success
```

### 4. Configuration Issues

#### Problem: Configuration not loading

```text
# Error
ValidationError: field required
```

#### Solutions

**Check environment variables:**

```bash
env | grep FLEXT_
```

**Validate configuration:**

```python
from flext_core import FlextSettings

try:
    settings = FlextSettings()
except Exception as error:
    print(f"Configuration error: {error}")
else:
    print("Configuration valid")
    print(f"Log level: {settings.log_level}")
```

**Debug configuration loading:**

```python
import os
from flext_core import FlextSettings

# Print all FLEXT environment variables
for key, value in sorted(os.environ.items()):
    if key.startswith("FLEXT_"):
        print(f"{key}={value}")

# Load and print configuration
settings = FlextSettings()
print(f"Config: {settings.model_dump()}")
```

### 5. LDIF Processing Issues

#### Problem: LDIF parsing fails

```text
# Error
LdifParsingException: Invalid LDIF format
```

#### Solutions

**Check LDIF content:**

```python
from flext_ldif import ldif

content = """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson"""

result = ldif.parse_string(content)
if result.failure:
    print(f"Parse error: {result.error}")
    print(f"Content: {repr(content)}")
else:
    response = result.unwrap()
    print(f"Parsed entries: {len(response.entries)}")
```

**Enable debug logging:**

```python
import logging

logging.basicConfig(level=logging.DEBUG)

# Your LDIF processing code
```

**Validate LDIF format:**

```python
# Check for common LDIF issues
def validate_ldif_content(content: str) -> list[str]:
    issues: list[str] = []

    if not content.strip():
        issues.append("Empty content")

    if not content.startswith("dn:"):
        issues.append("Missing DN line")

    lines = content.split("\n")
    for i, line in enumerate(lines):
        if line and not line.startswith(("dn:", " ", "\t")) and ":" not in line:
            issues.append(f"Invalid line {i + 1}: {line}")

    return issues
```

### 6. Migration Issues

#### Problem: Migration fails

```text
# Error
LdifMigrationException: Server compatibility error
```

#### Solutions

**Check server configuration:**

```python
from flext_ldif import FlextLdifSettings, c

settings = FlextLdifSettings(
    ldif_encoding=c.Ldif.Encoding.UTF8,
    ldif_strict_validation=True,
)

print(f"Config: {settings.model_dump()}")
```

**Build a migration pipeline:**

```python
from flext_ldif import ldif

pipeline = ldif.migration_pipeline(source_server="oid", target_server="oud")
print(type(pipeline).__name__)
```

**Test with sample data:**

```python
from flext_ldif import ldif

# Test migration with small sample
sample_ldif = """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson"""

result = ldif.parse_string(sample_ldif)
if result.success:
    print("Sample parsing successful")
else:
    print(f"Sample parsing failed: {result.error}")
```

### 7. Performance Issues

#### Problem: Slow processing

```text
# Symptoms
# - High memory usage
# - Slow response times
# - Timeout errors
```

#### Solutions

**Profile memory usage:**

```python
import psutil
import os


def profile_memory():
    process = psutil.Process(os.getpid())
    initial_memory = process.memory_info().rss

    # Your processing code here

    final_memory = process.memory_info().rss
    memory_used = final_memory - initial_memory

    print(f"Memory used: {memory_used / 1024 / 1024:.2f} MB")


profile_memory()
```

**Inspect active LDIF settings:**

```python
from flext_ldif import FlextLdifSettings, c

settings = FlextLdifSettings(
    ldif_encoding=c.Ldif.Encoding.UTF8,
    ldif_strict_validation=False,
)

print(settings.model_dump())
```

**Reuse explicit settings in the facade:**

```python
from flext_ldif import FlextLdifSettings, ldif

settings = FlextLdifSettings(ldif_strict_validation=True)
custom_ldif = ldif(settings=settings)

print(type(custom_ldif).__name__)
```

## Debugging Techniques

### 1. Logging Configuration

```python
import logging
from flext_core import FlextLogger

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Use FLEXT logger
logger = FlextLogger.fetch_logger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### 2. Exception Handling

```python
from flext_core import p
from flext_core import FlextLogger, r


logger = FlextLogger.fetch_logger(__name__)


def process_data(data: dict[str, str]) -> p.Result[dict[str, str]]:
    if not data:
        return r[dict[str, str]].fail("Data required")
    return r[dict[str, str]].ok(data)


def safe_operation(data: dict[str, str]) -> p.Result[dict[str, str]]:
    try:
        return process_data(data)
    except ValueError as error:
        logger.error(f"Validation error: {error}")
        return r[dict[str, str]].fail(f"Validation failed: {error}")
    except Exception as error:
        logger.error(f"Unexpected error: {error}", exc_info=True)
        return r[dict[str, str]].fail(f"Operation failed: {error}")
```

### 3. Debug Mode

```python
from flext_core import FlextSettings

# Enable debug mode
settings = FlextSettings(debug=True)

# Debug information will be printed
print(f"Debug mode: {settings.debug}")
print(f"Log level: {settings.log_level}")
```

### 4. Step-by-Step Debugging

```python
from flext_ldif import ldif


def debug_ldif_processing(content: str):
    """Debug LDIF processing step by step."""
    print(f"Input content length: {len(content)}")
    print(f"First 100 chars: {repr(content[:100])}")

    # Step 1: Basic validation
    if not content.strip():
        print("ERROR: Empty content")
        return

    # Step 2: Check DN format
    lines = content.split("\n")
    dn_line = lines[0] if lines else ""
    print(f"DN line: {repr(dn_line)}")

    if not dn_line.startswith("dn:"):
        print("ERROR: Missing or invalid DN line")
        return

    # Step 3: Try parsing
    result = ldif.parse_string(content)
    if result.success:
        response = result.unwrap()
        print(f"SUCCESS: Parsed {len(response.entries)} entries")
    else:
        print(f"ERROR: Parse failed: {result.error}")
```

## Error Codes Reference

### FLEXT Core Errors

| Error Code  | Description                     | Solution                                         |
| ----------- | ------------------------------- | ------------------------------------------------ |
| `FLEXT_001` | Configuration validation failed | Check environment variables and settings files   |
| `FLEXT_002` | Dependency injection failed     | Verify service registration in container         |
| `FLEXT_003` | Type validation failed          | Fix type annotations and data types              |

### LDIF Processing Errors

| Error Code | Description                | Solution                                  |
| ---------- | -------------------------- | ----------------------------------------- |
| `LDIF_001` | Invalid LDIF format        | Check LDIF syntax and structure           |
| `LDIF_002` | Server compatibility error | Enable server quirks or check server type |
| `LDIF_003` | Schema validation failed   | Verify schema definitions and attributes  |

### API Errors

| Error Code | Description           | Solution                           |
| ---------- | --------------------- | ---------------------------------- |
| `API_001`  | HTTP request failed   | Check network connectivity and URL |
| `API_002`  | Authentication failed | Verify API keys and credentials    |
| `API_003`  | Rate limit exceeded   | Implement retry logic with backoff |

## Performance Troubleshooting

### Memory Issues

```python
# Monitor memory usage
import psutil
import os


def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()

    print(f"RSS: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"VMS: {memory_info.vms / 1024 / 1024:.2f} MB")

    # Check for memory leaks
    if memory_info.rss > 500 * 1024 * 1024:  # 500MB
        print("WARNING: High memory usage detected")


monitor_memory()
```

### CPU Issues

```python
# Monitor CPU usage
import psutil
import os
import time


def monitor_cpu():
    process = psutil.Process(os.getpid())

    # Get CPU usage over time
    for i in range(10):
        cpu_percent = process.cpu_percent()
        print(f"CPU usage: {cpu_percent}%")
        time.sleep(1)


monitor_cpu()
```

## Getting Help

### Self-Service Resources

1. **Check Documentation**

   - API Reference
   - Configuration Guide
   - Development Guide

1. **Run Diagnostics**

   ```bash
   # System health check
   make val

   # Project-specific check
   cd flext-core && make val
   ```

1. **Check Logs**

   ```bash
   # Enable debug logging
   export FLEXT_LOG_LEVEL=DEBUG
   python your_script.py
   ```

### Community Support

1. **GitHub Issues**

   - [Create Issue](https://github.com/flext-sh/flext/issues)
   - Search existing issues
   - Check closed issues for solutions

1. **GitHub Discussions**

   - [Ask Question](https://github.com/flext-sh/flext/discussions)
   - Share solutions
   - Discuss best practices

1. **Email Support**

   - <dev@flext.com> for technical issues
   - <support@flext.com> for general questions

### Reporting Issues

When reporting issues, include:

1. **Environment Information**

   ```bash
   python --version
   poetry env info
   make info
   ```

1. **Error Details**

   ```python
   # Full error traceback
   import traceback

   try:
       raise RuntimeError("example failure")
   except Exception:
       traceback.print_exc()
   ```

1. **Minimal Reproduction**

```python
# Minimal code that reproduces the issue
from flext_core import FlextSettings

settings = FlextSettings()
print(settings.log_level)
```

1. **Expected vs Actual Behavior**

- What you expected to happen
- What actually happened
- Steps to reproduce

## Prevention

### Best Practices

1. **Always Use r**

```python
from flext_core import p, r


# ✅ GOOD
def process(data: dict[str, str]) -> p.Result[dict[str, str]]:
    return r[dict[str, str]].ok(data)


# ❌ BAD
def process_without_result(data: dict[str, str]) -> dict[str, str]:
    return data
```

1. **Validate Input Early**

   ```python
   from flext_core import p, r


   def process_data(data: dict[str, str]) -> p.Result[dict[str, str]]:
       if not data:
           return r[dict[str, str]].fail("Data required")

       # Process data
       return r[dict[str, str]].ok(data)
   ```

1. **Use Type Hints**

   ```python
   from collections.abc import Sequence

   from flext_core import p, r


   # ✅ GOOD
   def process(items: Sequence[str]) -> p.Result[list[str]]:
       return r[list[str]].ok([item.upper() for item in items])


   # ❌ BAD
   def process_without_types(items):
       return items
   ```

1. **Test Thoroughly**

   ```python
   def test_process_data():
       # Test success case
       result = process_data({"key": "value"})
       assert result.success

       # Test failure case
       result = process_data(None)
       assert result.failure
   ```

## Resources

- FLEXT Core Documentation
- Configuration Guide
- Development Guide
- Testing Guide
- [GitHub Issues](https://github.com/flext-sh/flext/issues)
- [GitHub Discussions](https://github.com/flext-sh/flext/discussions)

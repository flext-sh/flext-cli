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
  - [Import Diagnostics](#import-diagnostics)
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
# Debug import issues — uses the canonical FLEXT structured logger.
import sys

from flext_core import FlextLogger

logger = FlextLogger.fetch_logger("troubleshoot.imports")
logger.info("python_path", entries=tuple(sys.path))
try:
    import flext_core
except ImportError:
    logger.exception("flext_core_import_failed")
else:
    logger.info("flext_core_import_ok", path=flext_core.__file__)
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
from flext_core import FlextLogger


def test_with_debug() -> None:
    """Use the structured FLEXT logger for in-test diagnostics."""
    logger = FlextLogger.fetch_logger("troubleshoot.test_with_debug")
    result = my_function()
    logger.info(
        "test_result",
        success=bool(result.success),
        error=str(result.error) if result.failure else None,
    )
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
from pydantic import ValidationError

from flext_core import FlextLogger, FlextSettings

logger = FlextLogger.fetch_logger("troubleshoot.config_validate")
try:
    settings = FlextSettings()
except ValidationError:
    logger.exception("flext_settings_invalid")
else:
    logger.info("flext_settings_valid", log_level=str(settings.log_level))
```

**Debug configuration loading:**

```python
import os

from flext_core import FlextLogger, FlextSettings

logger = FlextLogger.fetch_logger("troubleshoot.config_env")

# Log only the FLEXT_ variable NAMES; never log values (may contain secrets).
flext_keys = sorted(name for name in os.environ if name.startswith("FLEXT_"))
logger.info("flext_environment_keys", count=len(flext_keys), keys=tuple(flext_keys))

# Load configuration through the canonical entrypoint and log a non-sensitive view.
settings = FlextSettings.fetch_global()
logger.info("flext_settings_summary", log_level=str(settings.log_level))
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
from flext_core import FlextLogger
from flext_ldif import ldif

logger = FlextLogger.fetch_logger("troubleshoot.ldif_parse")
content = """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson"""

result = ldif.parse_string(content)
if result.failure:
    logger.error(
        "ldif_parse_failed",
        error=str(result.error),
        content_preview=repr(content)[:80],
    )
else:
    response = result.unwrap()
    logger.info("ldif_parse_ok", entries=len(response.entries))
```

**Enable debug logging:**

```python
# FLEXT logging level is configured globally via FlextSettings (FLEXT_LOG_LEVEL env var)
# or by passing log_level= to FlextSettings(). Do NOT call logging.basicConfig.
from flext_core import FlextLogger

logger = FlextLogger.fetch_logger("troubleshoot.ldif_debug")
logger.debug("ldif_processing_start")
# ... your LDIF processing code
logger.debug("ldif_processing_done")
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
from flext_core import FlextLogger
from flext_ldif import FlextLdifSettings, c

logger = FlextLogger.fetch_logger("troubleshoot.ldif_settings")
settings = FlextLdifSettings(
    ldif_encoding=c.Ldif.Encoding.UTF8,
    ldif_strict_validation=True,
)
logger.info(
    "ldif_settings_loaded",
    ldif_encoding=str(settings.ldif_encoding),
    ldif_strict_validation=settings.ldif_strict_validation,
)
```

**Build a migration pipeline:**

```python
from flext_core import FlextLogger
from flext_ldif import ldif

logger = FlextLogger.fetch_logger("troubleshoot.ldif_pipeline")
pipeline = ldif.migration_pipeline(source_server="oid", target_server="oud")
logger.info("migration_pipeline_built", pipeline_type=type(pipeline).__name__)
```

**Test with sample data:**

```python
from flext_core import FlextLogger
from flext_ldif import ldif

logger = FlextLogger.fetch_logger("troubleshoot.ldif_sample")
sample_ldif = """dn: cn=test,dc=example,dc=com
cn: test
objectClass: inetOrgPerson"""

result = ldif.parse_string(sample_ldif)
if result.success:
    logger.info("sample_parse_ok")
else:
    logger.error("sample_parse_failed", error=str(result.error))
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
import os

import psutil

from flext_core import FlextLogger


def profile_memory() -> None:
    """Sample RSS before and after a workload via the FLEXT structured logger."""
    logger = FlextLogger.fetch_logger("troubleshoot.profile_memory")
    process = psutil.Process(os.getpid())
    initial_rss = process.memory_info().rss
    # ... your processing code here ...
    final_rss = process.memory_info().rss
    logger.info(
        "memory_profile",
        used_mb=round((final_rss - initial_rss) / 1024 / 1024, 2),
    )


profile_memory()
```

**Inspect active LDIF settings:**

```python
from flext_core import FlextLogger
from flext_ldif import FlextLdifSettings, c

logger = FlextLogger.fetch_logger("troubleshoot.ldif_settings_inspect")
settings = FlextLdifSettings(
    ldif_encoding=c.Ldif.Encoding.UTF8,
    ldif_strict_validation=False,
)
logger.info(
    "ldif_settings_active",
    ldif_encoding=str(settings.ldif_encoding),
    ldif_strict_validation=settings.ldif_strict_validation,
)
```

**Reuse explicit settings in the facade:**

```python
from flext_core import FlextLogger
from flext_ldif import FlextLdifSettings, ldif

logger = FlextLogger.fetch_logger("troubleshoot.ldif_facade")
settings = FlextLdifSettings(ldif_strict_validation=True)
custom_ldif = ldif(settings=settings)
logger.info("ldif_facade_created", facade_type=type(custom_ldif).__name__)
```

## Debugging Techniques

### 1. Logging Configuration

FLEXT uses **structured logging**. Configuration is global through ``FlextSettings``
(or the ``FLEXT_LOG_LEVEL`` env var) — never call ``logging.basicConfig`` in FLEXT code.

```python
from flext_core import FlextLogger

logger = FlextLogger.fetch_logger(__name__)
logger.debug("debug_event", detail="example")
logger.info("info_event")
logger.warning("warning_event")
logger.error("error_event")
```

### 2. Exception Handling

```python
from flext_core import FlextLogger, p, r

logger = FlextLogger.fetch_logger(__name__)


def process_data(data: dict[str, str]) -> p.Result[dict[str, str]]:
    if not data:
        return r[dict[str, str]].fail("Data required")
    return r[dict[str, str]].ok(data)


def safe_operation(data: dict[str, str]) -> p.Result[dict[str, str]]:
    """Wrap fallible work; log via the structured logger, return ``r``."""
    try:
        return process_data(data)
    except ValueError as error:
        logger.warning("validation_error", error=str(error))
        return r[dict[str, str]].fail(f"Validation failed: {error}")
    except (TypeError, KeyError, AttributeError) as error:
        # ``logger.exception`` emits ERROR + traceback in the structured payload.
        logger.exception("unexpected_error")
        return r[dict[str, str]].fail(f"Operation failed: {error}")
```

### 3. Debug Mode

```python
from flext_core import FlextLogger, FlextSettings

logger = FlextLogger.fetch_logger("troubleshoot.debug_mode")
settings = FlextSettings(debug=True)
logger.info(
    "flext_debug_state",
    debug=settings.debug,
    log_level=str(settings.log_level),
)
```

### 4. Step-by-Step Debugging

```python
from flext_core import FlextLogger
from flext_ldif import ldif


def debug_ldif_processing(content: str) -> None:
    """Debug LDIF processing step-by-step via the structured FLEXT logger."""
    logger = FlextLogger.fetch_logger("troubleshoot.ldif_step")
    logger.info(
        "ldif_input",
        length=len(content),
        first_100=repr(content[:100]),
    )

    if not content.strip():
        logger.error("ldif_empty_content")
        return

    lines = content.split("\n")
    dn_line = lines[0] if lines else ""
    logger.info("ldif_dn_line", dn_line=repr(dn_line))

    if not dn_line.startswith("dn:"):
        logger.error("ldif_missing_dn")
        return

    result = ldif.parse_string(content)
    if result.success:
        response = result.unwrap()
        logger.info("ldif_parse_ok", entries=len(response.entries))
    else:
        logger.error("ldif_parse_failed", error=str(result.error))
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
| `LDIF_002` | Server compatibility error | Enable server servers or check server type |
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
import os

import psutil

from flext_core import FlextLogger

_HIGH_MEMORY_THRESHOLD_MB = 500


def monitor_memory() -> None:
    """Sample current process RSS/VMS via the structured FLEXT logger."""
    logger = FlextLogger.fetch_logger("troubleshoot.monitor_memory")
    info = psutil.Process(os.getpid()).memory_info()
    rss_mb = round(info.rss / 1024 / 1024, 2)
    vms_mb = round(info.vms / 1024 / 1024, 2)
    logger.info("memory_sample", rss_mb=rss_mb, vms_mb=vms_mb)
    if rss_mb > _HIGH_MEMORY_THRESHOLD_MB:
        logger.warning(
            "memory_high",
            rss_mb=rss_mb,
            threshold_mb=_HIGH_MEMORY_THRESHOLD_MB,
        )


monitor_memory()
```

### CPU Issues

```python
import os

import psutil

from flext_core import FlextLogger


def monitor_cpu() -> None:
    """Emit a single CPU sample for the current process via the FLEXT logger.

    For sustained monitoring schedule periodic emits via your runner / SRE
    tooling instead of looping with ``time.sleep`` inside this helper.
    """
    logger = FlextLogger.fetch_logger("troubleshoot.monitor_cpu")
    process = psutil.Process(os.getpid())
    logger.info("cpu_sample", percent=process.cpu_percent(interval=0.1))


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
   from flext_core import FlextLogger

   logger = FlextLogger.fetch_logger("troubleshoot.example_error")
   try:
       raise RuntimeError("example failure")
   except RuntimeError:
       # ``logger.exception`` emits ERROR + the full traceback in structured form.
       logger.exception("example_failure_demo")
   ```

1. **Minimal Reproduction**

```python
# Minimal code that reproduces the issue
from flext_core import FlextLogger, FlextSettings

logger = FlextLogger.fetch_logger("troubleshoot.minimal_repro")
settings = FlextSettings.fetch_global()
logger.info("flext_log_level", value=str(settings.log_level))
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
   def process(items: t.SequenceOf[str]) -> p.Result[list[str]]:
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

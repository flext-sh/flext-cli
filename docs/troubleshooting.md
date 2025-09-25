# Troubleshooting - flext-cli

**Common issues and solutions for flext-cli development and usage.**

**Last Updated**: September 17, 2025 | **Version**: 0.9.9 RC

---

## Installation Issues

### Poetry Installation Problems

**Problem**: Poetry fails to install dependencies

```bash
# Solution: Update Poetry and clear cache
poetry self update
poetry cache clear --all .
poetry install --sync
```

**Problem**: Python version conflicts

```bash
# Solution: Ensure Python 3.13+
python --version
poetry env use python3.13
poetry install
```

---

## Development Issues

### Import Errors

**Problem**: `ImportError: No module named 'flext_cli'`

```bash
# Solution: Install in development mode
poetry install -e .

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:/path/to/flext-cli/src"
```

**Problem**: flext-core import failures

```bash
# Solution: Ensure flext-core is available
cd ../flext-core
poetry install
cd ../flext-cli
poetry run python -c "from flext_core import FlextResult; print('OK')"
```

### Type Checking Issues

**Problem**: MyPy reports errors in strict mode

```bash
# Check specific issues
poetry run mypy src/ --show-error-codes --no-error-summary

# Common solutions:
# 1. Add type annotations
def function(param: str) -> FlextResult[str]:
    pass

# 2. Handle Optional types
from typing import Optional
value: Optional[str] = None

# 3. Use type ignore with specific codes
result = some_operation()
```

### Testing Issues

**Problem**: Tests fail with import errors

```bash
# Solution: Set PYTHONPATH for tests
PYTHONPATH=src pytest tests/

# Or use conftest.py configuration
# tests/conftest.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
```

**Problem**: Coverage reports missing files

```bash
# Solution: Specify source directory
pytest tests/ --cov=src/flext_cli --cov-report=term-missing
```

---

## CLI Runtime Issues

### Command Not Found

**Problem**: `flext: command not found`

```bash
# Solution 1: Install CLI globally
poetry install
poetry run flext --help

# Solution 2: Use full path
poetry run python -m flext_cli --help

# Solution 3: Add to PATH
export PATH="${PATH}:$(poetry env info --path)/bin"
```

### Authentication Issues

**Problem**: Authentication commands fail

```bash
# Debug authentication
flext debug info
flext auth status

# Check configuration
flext config show

# Reset authentication
flext auth logout
flext auth login
```

### Configuration Problems

**Problem**: Configuration not loading correctly

```python
# Debug configuration loading
from Flext_cli import FlextCliConfig
from flext_core import FlextResult

config = FlextCliConfig()
result = config.load_project_config()

if result.is_failure:
    print(f"Config error: {result.error}")
else:
    print(f"Config loaded: {result.unwrap()}")
```

---

## Integration Issues

### flext-core Integration

**Problem**: FlextResult patterns not working

```python
# Verify flext-core integration
from flext_core import FlextResult

# Test basic functionality
result = FlextResult[str].ok("test")
assert result.is_success
assert result.unwrap() == "test"

# Test error handling
error_result = FlextResult[str].fail("error")
assert error_result.is_failure
assert error_result.error == "error"
```

**Problem**: Container registration issues

```python
# Debug container operations
from flext_core import FlextContainer

container = FlextContainer.get_global()

# Test service registration
register_result = container.register("test_service", "test_value")
if register_result.is_failure:
    print(f"Registration failed: {register_result.error}")

# Test service retrieval
get_result = container.get("test_service")
if get_result.is_failure:
    print(f"Retrieval failed: {get_result.error}")
```

### API Client Issues

**Problem**: HTTP requests failing

```python
# Debug API client
from flext_cli import FlextApiClient

client = FlextApiClient()

# Test basic connectivity
try:
    response = client.get("https://httpbin.org/get")
    if response.is_success:
        print("API client working")
    else:
        print(f"API error: {response.error}")
except Exception as e:
    print(f"Network error: {e}")
```

---

## Performance Issues

### Slow Command Execution

**Problem**: CLI commands are slow to start

```bash
# Profile import time
python -X importtime -c "from flext_cli import FlextCliApi"

# Optimize imports
# - Use lazy imports where possible
# - Reduce module-level computations
# - Cache expensive operations
```

**Problem**: Memory usage is high

```python
# Monitor memory usage
import tracemalloc

tracemalloc.start()

# Your CLI operation
from flext_cli import FlextCliApi
api = FlextCliApi()

# Check memory
current, peak = tracemalloc.get_traced_memory()
print(f"Current memory usage: {current / 1024 / 1024:.1f} MB")
print(f"Peak memory usage: {peak / 1024 / 1024:.1f} MB")
tracemalloc.stop()
```

---

## Debug Commands

### System Information

```bash
# Get system info
flext debug info

# Check Python environment
python --version
poetry env info

# Verify dependencies
poetry show
poetry check
```

### Verbose Output

```bash
# Run with verbose output
flext --verbose command

# Enable debug logging
export FLEXT_LOG_LEVEL=DEBUG
flext command

# Python debug mode
python -d -c "from flext_cli import FlextCliApi"
```

### Configuration Debug

```bash
# Show current configuration
flext config show

# Validate configuration
flext config validate

# Reset to defaults
flext config reset
```

---

## Common Error Messages

### "Module not found" errors

**Cause**: Import path issues

```python
# Problem code
from flext_cli.internal import something

# Solution
from Flext_cli import FlextCliApi, FlextCliConfig
```

### "Configuration not found"

**Cause**: Configuration not loaded properly

```python
# Problem
config = FlextCliConfig()
format = config.output_format  # May not exist

# Solution
config = FlextCliConfig()
config.load_project_config()
format = config.get_output_format()
```

### "Click command not found"

**Cause**: Direct Click usage instead of abstraction

```python
# Problem - direct Click usage
import click

# Solution - use flext-cli abstraction
from flext_cli import FlextCliCommands, FlextCliApi
```

---

## Getting Help

### Documentation

- **[API Reference](api-reference.md)** - Complete API documentation
- **[Architecture](architecture.md)** - System design and patterns
- **[Development](development.md)** - Development guidelines

### Debug Resources

```bash
# Internal help
flext --help
flext command --help

# Version information
flext --version

# System diagnostics
flext debug info
```

### Reporting Issues

When reporting issues, include:

1. Python version and environment info
2. Poetry version and dependency list
3. Error messages and stack traces
4. Minimal reproduction steps
5. Expected vs actual behavior

```bash
# Collect diagnostic information
echo "Python: $(python --version)"
echo "Poetry: $(poetry --version)"
echo "flext-cli: $(poetry run flext --version)"
poetry show --tree
flext debug info
```

---

For development patterns, see [development.md](development.md).
For architecture details, see [architecture.md](architecture.md).

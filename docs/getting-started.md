# Getting Started with flext-cli

**Installation and setup guide for the FLEXT ecosystem CLI foundation library.**

**Updated**: September 17, 2025 | **Version**: 0.9.0

---

## Overview

flext-cli serves as the **CLI foundation library** for the FLEXT ecosystem, providing standardized command-line interfaces using **flext-core patterns** with **Click framework integration**.

> **⚠️ STATUS**: Core services work, but CLI commands fail execution due to Click callback signature issues

---

## Prerequisites

### System Requirements

- **Python**: 3.13+ (required for advanced type features)
- **Poetry**: Dependency management
- **Make**: Build automation
- **FLEXT Ecosystem**: Access to flext-core foundation library

### FLEXT Ecosystem Integration

- **[flext-core](../../flext-core/README.md)**: Foundation patterns (FlextResult, FlextService, FlextContainer)
- **CLI Standards**: Provides CLI foundation for all FLEXT project command-line tools

---

## Installation

### Development Setup

```bash
# Clone from FLEXT ecosystem
git clone https://github.com/flext-sh/flext-cli.git
cd flext-cli

# Complete development setup
make setup

# Verify core components load successfully
python -c "from flext_cli import FlextCliService; print('✅ Core service loads')"
python -c "from flext_cli.auth import FlextCliAuth; print('✅ Auth system loads')"
```

### Current Status Verification

# Core service initialization
from flext_cli import FlextCliService
service = FlextCliService()  # ✅ Works

# Authentication system loading
from flext_cli.auth import FlextCliAuth
auth = FlextCliAuth()  # ✅ Works

# Type system verification
from flext_cli.typings import FlextCliTypes
format_types = FlextCliTypes.OutputFormat  # ✅ Works
```

**What's Broken**:
```bash
# CLI command execution fails
python -m flext_cli --version
# Error: print_version() takes 2 positional arguments but 3 were given

# Basic CLI commands crash due to Click callback signature issues
```

---

## Development Workflow

### Quality Gates

```bash
# Code quality validation
make lint                   # ✅ Ruff linting (should pass)
make format                 # Auto-format code

# Type checking
make type-check            # ✅ MyPy strict mode (src/ passes)

# Testing
make test                  # Run test suite
pytest tests/unit/         # Unit tests only
```

### Working Development Pattern

```python
# This development pattern works for extending the library
from flext_cli import FlextCliService
from flext_core import FlextResult

# Initialize service
service = FlextCliService()

# Service operations work correctly
health = service.get_service_health()
assert health.is_success

# Configuration works
config = service.get_config()  # Returns FlextCliConfig | None
```

## Critical Issues

### CLI Command Execution

**Issue**: Click callback signatures are incorrect
**Impact**: No CLI commands execute successfully
**Status**: Requires immediate fix for basic functionality
- Version command crashes with argument errors
- Login commands reference non-existent methods
- Configuration system fails validation

---

## Development Workflow

### Quality Checks

```bash
# These should work for development
make lint          # Code linting
make type-check    # Type checking (may have errors)
make format        # Code formatting

# This may fail due to broken functionality
make test          # Some tests may fail
```

### Working with Broken Code

1. **Focus on Structure**: The architecture and type definitions are solid
2. **Import Testing**: Test individual module imports before using functionality
3. **Fix First**: Prioritize fixing broken core functionality over new features

---

## Troubleshooting

### Import Errors
**Problem**: "Object has no attribute 'model_computed_fields'"
**Solution**: Pydantic configuration issue - requires code fixes

### CLI Crashes
**Problem**: Commands fail with argument errors
**Solution**: Method signature mismatches - requires code fixes

### Configuration Issues
**Problem**: FlextCliConfig fails to initialize
**Solution**: Validation errors - requires default value fixes

---

## Next Steps

**For Development**:
- Focus on fixing broken core functionality first
- Use individual module imports to test specific components
- Refer to TODO.md for specific issues that need fixes

**Not Ready For**:
- Production usage
- Integration with other projects
- Full CLI workflows

---

**Development Status**: Core functionality requires significant fixes before library becomes usable.
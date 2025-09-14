# Getting Started with flext-cli

**Installation and setup guide for flext-cli development.**

**Updated**: September 17, 2025 | **Version**: 0.9.0

---

## ⚠️ Important Notice

**Current Status**: flext-cli has significant functionality gaps and broken core features. This guide covers development setup only - the library is not ready for production use.

---

## Prerequisites

### System Requirements

- **Python**: 3.13+ (required for advanced type features)
- **Poetry**: For dependency management
- **Make**: For build automation

### FLEXT Ecosystem Context

flext-cli is part of the FLEXT ecosystem but has limited working integration:
- **flext-core**: Uses FlextResult patterns (when working)
- **Authentication**: Integration planned but currently broken

---

## Development Setup

### Clone and Setup

```bash
# Clone repository
git clone https://github.com/flext-sh/flext-cli.git
cd flext-cli

# Complete development setup
make setup

# Verify basic imports work (functionality limited)
python -c "import flext_cli; print('Import successful - limited functionality')"
```

### Known Setup Issues

**Authentication Import Fails**:
```bash
# This will fail with Pydantic errors
python -c "from flext_cli import FlextCliAuth; FlextCliAuth()"
```

**CLI Commands Crash**:
```bash
# These commands currently crash
python -m flext_cli.cli --version  # Argument error
python -m flext_cli.cli --help     # May work
```

---

## What Actually Works

### Working Imports
```python
# Basic module imports work
import flext_cli
from flext_cli import __version__

# Some type definitions are accessible
from flext_cli.typings import E, F, P, R, T, U, V
```

### Limited CLI Help
```bash
# Basic help may work
python -c "
import sys
sys.path.insert(0, 'src')
import flext_cli.cli
print('CLI module imported')
"
```

## What Doesn't Work

### Broken Authentication
```python
# This fails with configuration errors
from flext_cli import FlextCliAuth
auth = FlextCliAuth()  # Crashes
```

### Broken CLI Commands
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
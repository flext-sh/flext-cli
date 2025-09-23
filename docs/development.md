# Development Guide - flext-cli

**Contributing guidelines and development workflow for flext-cli.**

**Last Updated**: September 17, 2025 | **Version**: 0.9.9 RC

---

## Development Setup

### Prerequisites

- Python 3.13+
- Poetry for dependency management
- Make for build automation
- Git for version control

### Initial Setup

```bash
# Clone repository
git clone https://github.com/flext-sh/flext-cli.git
cd flext-cli

# Complete development setup
make setup

# Install pre-commit hooks
poetry run pre-commit install
```

---

## Development Workflow

### Essential Commands

```bash
make setup          # Complete development environment setup
make validate       # All quality checks (lint + type + test)
make test          # Run test suite
make lint          # Code linting with Ruff
make type-check    # MyPy type checking
make format        # Auto-format code
make clean         # Clean build artifacts
```

### Code Quality Standards

- **Type Safety**: Complete Python 3.13+ type annotations
- **Linting**: Zero Ruff violations
- **Testing**: Comprehensive test coverage
- **Documentation**: All public APIs documented

---

## Architecture Guidelines

### FLEXT Ecosystem Integration

Follow these patterns when extending flext-cli:

1. **CLI Patterns**: Use flext-cli abstractions
2. **Integration**: Follow flext-core patterns (see flext-core documentation)
3. **Type Safety**: Complete type annotations required
4. **Testing**: Comprehensive test coverage

### Code Organization

```python
# ✅ Correct - Use flext-cli patterns
from flext_cli import FlextCliApi

class ProjectCliService:
    """Project CLI service following FLEXT patterns."""

    def __init__(self):
        self._cli_api = FlextCliApi()

    def process_data(self, data: dict):
        """Process CLI data."""
        if not data:
            return "Data cannot be empty"

        # Business logic
        return {"processed": True, "data": data}

# ❌ Avoid - Direct framework imports
# import click  # Use flext-cli abstractions instead
# import rich   # Use FlextCliFormatters instead
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/              # Unit tests for individual components
├── integration/       # Integration tests
├── conftest.py       # Shared fixtures
└── test_*.py         # Test modules
```

### Testing Patterns

```python
import pytest
from flext_cli import FlextCliApi

def test_cli_api_operation():
    """Test CLI API operations."""
    api = FlextCliApi()

    result = api.process_command("test")

    assert result is not None
    assert "test" in str(result)

def test_error_handling():
    """Test proper error handling."""
    api = FlextCliApi()

    result = api.process_command("")  # Invalid input

    # Test appropriate error handling
    assert result or "error" in str(result)
```

### Test Commands

```bash
# Run all tests
pytest tests/

# Unit tests only
pytest tests/unit/

# With coverage
pytest tests/ --cov=src --cov-report=term-missing

# Specific test file
pytest tests/unit/test_api.py -v
```

---

## Contributing Guidelines

### Code Style

- Follow PEP 8 with 79-character line limit
- Use descriptive variable names
- Add docstrings for all public functions/classes
- Include type hints for all function signatures

### Pull Request Process

1. Create feature branch from main
2. Implement changes with tests
3. Run `make validate` to ensure quality
4. Submit pull request with description
5. Address review feedback
6. Merge after approval

### Commit Messages

Follow conventional commit format:

```
feat: add new CLI command for data export
fix: resolve authentication timeout issue
docs: update API documentation
test: add integration tests for config module
```

---

## Extension Development

### Adding New Commands

1. Create command handler:

```python
from flext_core import FlextResult, FlextService
from flext_cli import FlextCliApi

class DataCommands(FlextService):
    """Data management commands."""

    def handle_export(self, **kwargs) -> FlextResult[None]:
        """Handle data export command."""
        # Implementation
        return FlextResult[None].ok(None)
```

2. Register with CLI:

```python
from flext_cli import FlextCliMain

cli = FlextCliMain()
cli.register_command_group(
    name="data",
    commands={"export": data_handler.handle_export},
    description="Data management"
)
```

3. Add tests:

```python
def test_data_export_command():
    """Test data export functionality."""
    handler = DataCommands()
    result = handler.handle_export(format="json")
    assert result.is_success
```

### Custom Formatters

```python
from flext_cli import FlextCliFormatters

class ProjectFormatters(FlextCliFormatters):
    """Project-specific output formatters."""

    def format_project_data(self, data: dict) -> FlextResult[str]:
        """Format project-specific data."""
        # Custom formatting logic
        return FlextResult[str].ok("formatted_output")
```

---

## Debug and Troubleshooting

### Common Issues

1. **Import Errors**: Ensure proper module structure
2. **Type Errors**: Run `make type-check` for detailed analysis
3. **Test Failures**: Use `pytest -v` for verbose output
4. **Dependency Issues**: Try `poetry install --sync`

### Debug Commands

```bash
# Verbose test output
pytest tests/ -v -s

# Type checking with details
poetry run mypy src/ --show-error-codes

# Dependency tree analysis
poetry show --tree

# Development environment info
flext debug info
```

---

For architectural details, see [architecture.md](architecture.md).
For API usage, see [api-reference.md](api-reference.md).

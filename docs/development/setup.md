# Development Setup Guide

Este guia detalha como configurar o ambiente de desenvolvimento para o FLEXT CLI.

## Prerequisites

### System Requirements

- **Python 3.13+**: Required for modern syntax and type hints
- **Poetry 1.8+**: For dependency management
- **Git**: For version control
- **Make**: For running development commands

### Optional Tools

- **Docker**: For containerized development
- **VS Code** with Python extension
- **PyCharm Professional**: For advanced development

## Installation Steps

### 1. Clone the Repository

```bash
# Clone the FLEXT workspace
git clone https://github.com/your-org/flext.git
cd flext/flext-cli
```

### 2. Verify Python Version

```bash
# Check Python version
python --version  # Should be 3.13+

# If using pyenv
pyenv install 3.13.0
pyenv local 3.13.0
```

### 3. Install Poetry

```bash
# Install Poetry (if not already installed)
curl -sSL https://install.python-poetry.org | python3 -

# Verify installation
poetry --version
```

### 4. Project Setup

```bash
# Complete development setup (recommended)
make setup

# Or manual setup
make install          # Install dependencies
make pre-commit       # Setup pre-commit hooks
```

### 5. Verify Installation

```bash
# Run quality checks
make check

# Run tests
make test

# Test CLI installation
make test-cli
```

## Development Environment

### Virtual Environment

Poetry automatically manages virtual environments:

```bash
# Activate virtual environment
poetry shell

# Install dependencies
poetry install --all-extras --with dev,test,docs,security

# Show environment info
poetry env info
```

### Environment Variables

Create a `.env` file (not committed):

```bash
# CLI Configuration
FLEXT_CLI_DEV_MODE=true
FLEXT_CLI_LOG_LEVEL=debug
FLEXT_CLI_CONFIG_PATH=./config/dev.yaml

# Profile settings
FLX_PROFILE=development
FLX_DEBUG=true

# Testing
PYTEST_CURRENT_TEST=true
```

## IDE Configuration

### VS Code Settings

Create `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.ruffEnabled": true,
  "python.formatting.provider": "none",
  "python.formatting.ruffArgs": ["--line-length=88"],
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"],
  "python.typing.typeCheckingMode": "strict",
  "files.exclude": {
    "**/__pycache__": true,
    "**/.pytest_cache": true,
    "**/.mypy_cache": true,
    "**/.ruff_cache": true
  }
}
```

### VS Code Extensions

Recommended extensions:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.mypy-type-checker",
    "charliermarsh.ruff",
    "ms-python.pytest",
    "tamasfe.even-better-toml",
    "redhat.vscode-yaml"
  ]
}
```

### PyCharm Configuration

1. **Interpreter**: Set to Poetry virtual environment
2. **Code Style**: Use Ruff formatter
3. **Type Checking**: Enable MyPy integration
4. **Testing**: Configure pytest as test runner

## Quality Gates

### Pre-commit Hooks

Automatic quality checks before commits:

```bash
# Install hooks
make pre-commit

# Run manually
poetry run pre-commit run --all-files

# Skip hooks (emergency only)
git commit --no-verify
```

### Make Commands

Essential development commands:

```bash
# Quality validation
make validate         # Complete validation pipeline
make check           # Essential checks (fast)
make lint            # Ruff linting
make type-check      # MyPy type checking
make security        # Security scans
make format          # Format code

# Testing
make test            # Full test suite
make test-unit       # Unit tests only
make test-integration # Integration tests only
make coverage        # Coverage report
make coverage-html   # HTML coverage report

# CLI operations
make install-cli     # Install CLI globally
make test-cli        # Test CLI commands
make cli-smoke-test  # Basic CLI tests

# Maintenance
make clean          # Clean artifacts
make deps-update    # Update dependencies
make deps-audit     # Security audit
```

## Testing Setup

### Test Configuration

Tests are configured in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--cov=src/flext_cli",
    "--cov-report=term-missing",
    "--cov-fail-under=90"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "e2e: End-to-end tests",
    "slow: Slow tests"
]
```

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── unit/                    # Unit tests (fast)
│   ├── test_domain.py
│   ├── test_commands.py
│   └── test_utils.py
├── integration/             # Integration tests
│   ├── test_cli_integration.py
│   └── test_config_integration.py
└── e2e/                     # End-to-end tests
    └── test_full_workflow.py
```

### Running Tests

```bash
# All tests
make test

# Specific test types
pytest -m unit                    # Unit tests only
pytest -m integration             # Integration tests only
pytest -m "not slow"              # Exclude slow tests

# Specific test files
pytest tests/unit/test_domain.py  # Single file
pytest tests/unit/test_domain.py::test_command_lifecycle  # Single test

# With coverage
pytest --cov=src/flext_cli --cov-report=html

# Parallel execution
pytest -n auto                    # Use all CPU cores
```

## Debugging

### CLI Debugging

```bash
# Debug mode
poetry run flext --debug command

# With Python debugger
poetry run python -m pdb -c continue -m flext_cli.cli command

# Verbose output
poetry run flext --debug --verbose command
```

### Test Debugging

```bash
# Debug test failures
pytest --pdb                      # Drop into debugger on failure
pytest --pdb-trace               # Trace all test execution
pytest -s                       # Don't capture output

# Specific test debugging
pytest tests/unit/test_domain.py::test_command_lifecycle --pdb -s
```

### Logging Configuration

```python
# Development logging
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# In CLI commands
from flext_cli.utils.config import get_config
config = get_config()
if config.debug:
    logging.getLogger().setLevel(logging.DEBUG)
```

## Common Issues

### Poetry Issues

```bash
# Clear Poetry cache
poetry cache clear pypi --all

# Recreate virtual environment
poetry env remove python
poetry install

# Fix lock file issues
poetry lock --no-update
```

### Dependency Conflicts

```bash
# Show dependency tree
poetry show --tree

# Check for conflicts
poetry check

# Update dependencies
make deps-update
poetry update
```

### Import Errors

```bash
# Verify PYTHONPATH
echo $PYTHONPATH

# Install in development mode
poetry install -e .

# Check flext-core installation
poetry run python -c "import flext_core; print(flext_core.__version__)"
```

## Performance Optimization

### Development Speed

```bash
# Skip slow tests during development
pytest -m "not slow"

# Use pytest-xdist for parallel tests
pytest -n auto

# Cache test results
pytest --cache-show
```

### Resource Usage

```bash
# Monitor memory usage
poetry run python -m memory_profiler script.py

# Profile execution time
poetry run python -m cProfile -o profile.stats script.py
```

## Advanced Setup

### Docker Development

```dockerfile
# Dockerfile.dev
FROM python:3.13-slim

WORKDIR /app
COPY pyproject.toml poetry.lock ./
RUN pip install poetry && poetry install

COPY . .
CMD ["poetry", "run", "flext", "--help"]
```

```bash
# Build and run
docker build -f Dockerfile.dev -t flext-cli-dev .
docker run --rm -it flext-cli-dev
```

### CI/CD Integration

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.13'
      - run: pip install poetry
      - run: poetry install
      - run: make validate
```

---

**Next**: [Coding Standards](coding-standards.md) | **Previous**: [Development Home](../README.md)

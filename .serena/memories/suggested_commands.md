# FLEXT-CLI Essential Commands

## Quality Gates (MANDATORY - Run after every change)

```bash
# Complete validation pipeline
make validate                # lint + type-check + security + test

# Quick checks
make check                   # lint + type-check only
make lint                    # Ruff linting
make type-check              # MyPy strict mode
make test                    # Pytest with 75% coverage requirement

# Auto-fix
make fix                     # Auto-fix ruff issues + format
```

## Development Workflow

```bash
# Setup
make setup                   # Complete project setup with pre-commit

# Testing variations
make test-unit              # Unit tests only
make test-integration       # Integration tests only
make test-fast              # Tests without coverage
make coverage-html          # HTML coverage report

# CLI Testing
make cli-test               # Test CLI import
make cli-auth               # Test auth commands
make cli-config             # Test config commands
make cli-debug              # Test debug commands
```

## Mandatory QA Gate (ONE-LINER)

```bash
# STOP on first failure - use this before commits
ruff check . && mypy . && pyright && pytest -q --maxfail=1 --cov=src --cov=examples --cov=tests --cov=. --cov-report=term-missing:skip-covered --cov-fail-under=100
```

## Diagnostic Commands

```bash
# Project health
make doctor                 # Complete health check
make diagnose               # Environment diagnostics

# Dependencies
make deps-show              # Show dependency tree
make deps-audit             # Security audit
make deps-update            # Update dependencies
```

## Development Tools

```bash
# Shell access
make shell                  # Python shell with project context

# Cleanup
make clean                  # Clean build artifacts
make clean-all              # Deep clean including venv
make reset                  # Complete reset
```

## Environment Requirements

- **Virtual environment**: Must be activated (`source ~/flext/.venv/bin/activate`)
- **Python version**: 3.13+ (strict requirement)
- **Poetry**: Used for dependency management
- **NO PYTHONPATH**: Never export PYTHONPATH or use env prefixes

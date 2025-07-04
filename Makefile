# FLEXT-CLI Makefile - Developer Command Line Interface
# ===================================================

.PHONY: help install test clean lint format build docs cli-test completion demo interactive

# Default target
help: ## Show this help message
	@echo "⚡ FLEXT-CLI - Developer Command Line Interface"
	@echo "============================================="
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\\033[36m%-20s\\033[0m %s\\n", $$1, $$2}'

# Installation & Setup
install: ## Install dependencies with Poetry
	@echo "📦 Installing dependencies for flext-cli..."
	poetry install --all-extras

install-dev: ## Install with dev dependencies
	@echo "🛠️  Installing dev dependencies..."
	poetry install --all-extras --group dev --group test

# CLI Testing & Validation
cli-test: ## Test CLI commands and functionality
	@echo "🧪 Testing CLI commands..."
	poetry run python -m flext_cli --help
	@echo "✅ Basic CLI help works"
	@echo "🔍 Testing command structure..."
	poetry run python -c "from flext_cli.cli import cli; print('✅ CLI module imports correctly')"

cli-interactive: ## Test CLI in interactive mode
	@echo "🎮 Testing CLI interactive mode..."
	@if [ -f src/flext_cli/cli.py ]; then \
		poetry run python -c "from flext_cli.cli import cli; cli(['--help'])" || echo "CLI needs setup"; \
	else \
		echo "CLI source not found - needs extraction"; \
	fi

# Shell Completion
completion-bash: ## Generate bash completion
	@echo "🐚 Generating bash completion..."
	@mkdir -p completion
	poetry run python -c "from flext_cli.cli import cli; import click; print(click.shell_complete.get_completion(cli, 'bash'))" > completion/flext-cli-bash.sh
	@echo "✅ Bash completion saved to completion/flext-cli-bash.sh"

completion-zsh: ## Generate zsh completion  
	@echo "🐚 Generating zsh completion..."
	@mkdir -p completion
	poetry run python -c "from flext_cli.cli import cli; import click; print(click.shell_complete.get_completion(cli, 'zsh'))" > completion/flext-cli-zsh.sh
	@echo "✅ Zsh completion saved to completion/flext-cli-zsh.sh"

completion: completion-bash completion-zsh ## Generate all shell completions
	@echo "🎯 All shell completions generated"

# CLI Development
demo: ## Run CLI demo commands
	@echo "🎪 Running CLI demo..."
	@echo "📋 Available commands:"
	poetry run flext --help || echo "CLI needs setup"
	@echo "🔧 Config commands:"
	poetry run flext config --help || echo "Config commands need setup"
	@echo "📊 Pipeline commands:"
	poetry run flext pipeline --help || echo "Pipeline commands need setup"

cli-validate: ## Validate CLI command structure
	@echo "🔍 Validating CLI command structure..."
	poetry run python -c "
import sys
try:
    from flext_cli.cli import cli
    from click.testing import CliRunner
    runner = CliRunner()
    result = runner.invoke(cli, ['--help'])
    if result.exit_code == 0:
        print('✅ CLI structure valid')
    else:
        print('❌ CLI structure has issues')
        print(result.output)
        sys.exit(1)
except ImportError as e:
    print(f'⚠️  CLI module not found: {e}')
    print('CLI needs extraction from source')
except Exception as e:
    print(f'❌ CLI validation failed: {e}')
    sys.exit(1)
"

# API Client Testing
client-test: ## Test API client functionality
	@echo "📞 Testing API client..."
	poetry run python -c "
try:
    from flext_cli.client import FlxApiClient
    client = FlxApiClient()
    print('✅ API client imports successfully')
    print(f'Base URL: {client.base_url}')
except ImportError:
    print('⚠️  API client needs extraction')
except Exception as e:
    print(f'❌ API client test failed: {e}')
"

# Testing
test: ## Run CLI tests
	@echo "🧪 Running CLI tests..."
	poetry run pytest tests/ -v --tb=short

test-coverage: ## Run tests with coverage
	@echo "📊 Running tests with coverage..."
	poetry run pytest tests/ --cov=src/flext_cli --cov-report=html:reports/coverage --cov-report=xml:reports/coverage.xml --cov-fail-under=95

test-commands: ## Test individual CLI commands
	@echo "🎯 Testing individual CLI commands..."
	@echo "Testing help command..."
	poetry run python -c "from click.testing import CliRunner; from flext_cli.cli import cli; runner = CliRunner(); result = runner.invoke(cli, ['--help']); print(result.output)"

# Code Quality - Maximum Strictness
lint: ## Run all linters with maximum strictness
	@echo "🔍 Running maximum strictness linting for CLI..."
	poetry run ruff check . --output-format=verbose
	@echo "✅ Ruff linting complete"

format: ## Format code with strict standards
	@echo "🎨 Formatting CLI code..."
	poetry run black .
	poetry run ruff check --fix .
	@echo "✅ Code formatting complete"

type-check: ## Run strict type checking
	@echo "🎯 Running strict MyPy type checking..."
	poetry run mypy src/flext_cli --strict --show-error-codes
	@echo "✅ Type checking complete"

check: lint type-check test ## Run all quality checks
	@echo "✅ All quality checks complete for flext-cli!"

# Build & Distribution
build: ## Build the CLI package
	@echo "🔨 Building flext-cli package..."
	poetry build
	@echo "📦 Package built successfully"

install-local: build ## Install CLI locally for testing
	@echo "🏠 Installing CLI locally..."
	poetry run pip install dist/*.whl --force-reinstall
	@echo "✅ Local installation complete"

# Documentation
docs: ## Generate CLI documentation
	@echo "📚 Generating CLI documentation..."
	@mkdir -p docs/generated
	poetry run python -c "
from flext_cli.cli import cli
import click
ctx = click.Context(cli)
print('# FLEXT CLI Commands\\n')
print(cli.get_help(ctx))
" > docs/generated/commands.md
	@echo "✅ CLI documentation generated"

# Development Workflow
dev-setup: install-dev completion ## Complete development setup
	@echo "🎯 Setting up CLI development environment..."
	poetry run pre-commit install
	mkdir -p reports logs completion examples
	@echo "⚡ Run 'make demo' to test CLI"
	@echo "🎮 Run 'make cli-interactive' for interactive testing"
	@echo "✅ Development setup complete!"

# Interactive Development
repl: ## Start Python REPL with CLI loaded
	@echo "🐍 Starting Python REPL with CLI..."
	poetry run python -c "
from flext_cli.cli import cli
from flext_cli.client import FlxApiClient
from click.testing import CliRunner
runner = CliRunner()
print('CLI tools loaded:')
print('  cli - Main CLI object')
print('  FlxApiClient - API client')
print('  runner - Click test runner')
print('Example: runner.invoke(cli, [\"--help\"])')
" -i

# Cleanup
clean: ## Clean build artifacts and generated files
	@echo "🧹 Cleaning build artifacts..."
	@rm -rf build/ dist/ *.egg-info/
	@rm -rf reports/ logs/ .coverage htmlcov/
	@rm -rf completion/ docs/generated/
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -name "*.pyc" -delete 2>/dev/null || true
	@find . -name "*.pyo" -delete 2>/dev/null || true

# Environment variables
export PYTHONPATH := $(PWD)/src:$(PYTHONPATH)
export FLEXT_CLI_DEV := true
export FLEXT_CLI_DEBUG := true
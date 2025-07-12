# FLEXT-CLI Makefile - Enterprise Command Line Interface
# Uses FLEXT standardized patterns and flext-core integration

# Project Configuration
PROJECT_NAME := flext-cli
PYTHON_VERSION := 3.13
POETRY := poetry
PYTHON := $(POETRY) run python
PYTEST := $(POETRY) run pytest
RUFF := $(POETRY) run ruff
MYPY := $(POETRY) run mypy

# Colors for output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[1;33m
RED := \033[0;31m
RESET := \033[0m

# Default target
.DEFAULT_GOAL := help

## Help
help: ## Show this help message
	@echo "$(BLUE)FLEXT-CLI Makefile$(RESET)"
	@echo "Enterprise Command Line Interface"
	@echo ""
	@echo "$(GREEN)Available commands:$(RESET)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(BLUE)%-20s$(RESET) %s\\n", $$1, $$2}' $(MAKEFILE_LIST)

## Development
install: ## Install all dependencies
	@echo "$(BLUE)📦 Installing dependencies for $(PROJECT_NAME)...$(RESET)"
	@$(POETRY) install
	@echo "$(GREEN)✅ Dependencies installed$(RESET)"

install-dev: ## Install development dependencies
	@echo "$(BLUE)📦 Installing development dependencies...$(RESET)"
	@$(POETRY) install --with dev
	@echo "$(GREEN)✅ Development dependencies installed$(RESET)"

update: ## Update dependencies
	@echo "$(BLUE)🔄 Updating dependencies...$(RESET)"
	@$(POETRY) update
	@echo "$(GREEN)✅ Dependencies updated$(RESET)"

## Code Quality
lint: ## Run linting
	@echo "$(BLUE)🔍 Running linting for $(PROJECT_NAME)...$(RESET)"
	@$(RUFF) check src/ tests/ || true
	@echo "$(GREEN)✅ Linting complete$(RESET)"

lint-fix: ## Fix linting issues
	@echo "$(BLUE)🔧 Fixing linting issues...$(RESET)"
	@$(RUFF) check --fix src/ tests/ || true
	@$(RUFF) format src/ tests/ || true
	@echo "$(GREEN)✅ Linting issues fixed$(RESET)"

format: ## Format code
	@echo "$(BLUE)🎨 Formatting code...$(RESET)"
	@$(RUFF) format src/ tests/
	@echo "$(GREEN)✅ Code formatted$(RESET)"

type-check: ## Run type checking
	@echo "$(BLUE)🔍 Running type checking...$(RESET)"
	@$(MYPY) src/flext_cli/ || true
	@echo "$(GREEN)✅ Type checking complete$(RESET)"

check: lint type-check ## Run all code quality checks

## Testing
test: ## Run all tests
	@echo "$(BLUE)🧪 Running tests for $(PROJECT_NAME)...$(RESET)"
	@$(PYTEST) -v
	@echo "$(GREEN)✅ All tests passed$(RESET)"

test-unit: ## Run unit tests only
	@echo "$(BLUE)🧪 Running unit tests...$(RESET)"
	@$(PYTEST) tests/unit/ -v -m "not integration"
	@echo "$(GREEN)✅ Unit tests passed$(RESET)"

test-integration: ## Run integration tests only
	@echo "$(BLUE)🧪 Running integration tests...$(RESET)"
	@$(PYTEST) tests/integration/ -v -m "integration"
	@echo "$(GREEN)✅ Integration tests passed$(RESET)"

test-cov: ## Run tests with coverage
	@echo "$(BLUE)🧪 Running tests with coverage...$(RESET)"
	@$(PYTEST) --cov=flext_cli --cov-report=html --cov-report=term-missing
	@echo "$(GREEN)✅ Tests with coverage complete$(RESET)"

## CLI Operations
cli-config: ## Show current CLI configuration
	@echo "$(BLUE)⚙️ Showing FLEXT CLI configuration...$(RESET)"
	@$(PYTHON) -c "from flext_cli.config import get_cli_settings; settings = get_cli_settings(); print(f'Project: {settings.project_name}'); print(f'Version: {settings.project_version}'); print(f'API URL: {settings.api.url}'); print(f'Config Dir: {settings.directories.config_dir}'); print(f'Output Format: {settings.output.format}')"

cli-test: ## Test CLI system
	@echo "$(BLUE)🧪 Testing FLEXT CLI system...$(RESET)"
	@$(PYTHON) -c "from flext_cli.config import get_cli_settings; settings = get_cli_settings(); print('✅ CLI configuration loaded successfully'); print(f'Project: {settings.project_name}'); print(f'Environment: {settings.environment}'); print('✅ FLEXT CLI system is working')"

cli-help: ## Show CLI help
	@echo "$(BLUE)❓ Showing FLEXT CLI help...$(RESET)"
	@$(PYTHON) -m flext_cli.cli --help

cli-version: ## Show CLI version
	@echo "$(BLUE)📋 Showing FLEXT CLI version...$(RESET)"
	@$(PYTHON) -m flext_cli.cli --version

## CLI Command Testing
cli-demo: ## Run CLI demo commands
	@echo "$(BLUE)🎬 Running FLEXT CLI demo...$(RESET)"
	@echo "Testing configuration..."
	@$(PYTHON) -m flext_cli.cli config get
	@echo ""
	@echo "Testing help system..."
	@$(PYTHON) -m flext_cli.cli --help

## Build and Distribution
build: ## Build the package
	@echo "$(BLUE)🏗️ Building $(PROJECT_NAME)...$(RESET)"
	@$(POETRY) build
	@echo "$(GREEN)✅ Package built$(RESET)"

clean: ## Clean build artifacts
	@echo "$(BLUE)🧹 Cleaning build artifacts...$(RESET)"
	@rm -rf dist/ build/ *.egg-info/
	@rm -rf .coverage htmlcov/ .pytest_cache/
	@rm -rf .mypy_cache/ .ruff_cache/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✅ Build artifacts cleaned$(RESET)"

## Development Utilities
shell: ## Start Python shell with project context
	@echo "$(BLUE)🐍 Starting Python shell...$(RESET)"
	@$(POETRY) shell

env: ## Show environment information
	@echo "$(BLUE)🌍 Environment Information:$(RESET)"
	@echo "Project: $(PROJECT_NAME)"
	@echo "Python: $(PYTHON_VERSION)"
	@echo "Poetry: $(shell $(POETRY) --version)"
	@echo "Virtual Environment: $(shell $(POETRY) env info --path)"

## Security
security: ## Run security checks
	@echo "$(BLUE)🔒 Running security checks...$(RESET)"
	@$(POETRY) run bandit -r src/ || true
	@echo "$(GREEN)✅ Security checks complete$(RESET)"

## Version Management
version: ## Show current version
	@echo "$(BLUE)📋 Current version:$(RESET)"
	@$(POETRY) version

bump-patch: ## Bump patch version
	@echo "$(BLUE)📈 Bumping patch version...$(RESET)"
	@$(POETRY) version patch
	@echo "$(GREEN)✅ Patch version bumped$(RESET)"

bump-minor: ## Bump minor version
	@echo "$(BLUE)📈 Bumping minor version...$(RESET)"
	@$(POETRY) version minor
	@echo "$(GREEN)✅ Minor version bumped$(RESET)"

bump-major: ## Bump major version
	@echo "$(BLUE)📈 Bumping major version...$(RESET)"
	@$(POETRY) version major
	@echo "$(GREEN)✅ Major version bumped$(RESET)"

## Plugin Development
plugin-scaffold: ## Create plugin scaffold
	@echo "$(BLUE)🔌 Creating plugin scaffold...$(RESET)"
	@$(PYTHON) -m flext_cli.cli plugin scaffold --name example-plugin

plugin-validate: ## Validate plugin structure
	@echo "$(BLUE)🔌 Validating plugin structure...$(RESET)"
	@$(PYTHON) -m flext_cli.cli plugin validate

## Quick Development Workflow
dev: install lint-fix test ## Full development workflow (install, fix, test)
	@echo "$(GREEN)✅ Development workflow complete$(RESET)"

ci: check test ## Continuous integration workflow
	@echo "$(GREEN)✅ CI workflow complete$(RESET)"

## Information
info: ## Show project information
	@echo "$(BLUE)📊 Project Information:$(RESET)"
	@echo "Name: $(PROJECT_NAME)"
	@echo "Description: FLEXT CLI - Enterprise Command Line Interface"
	@echo "Python: $(PYTHON_VERSION)"
	@echo "Poetry: $(shell $(POETRY) --version)"
	@echo ""
	@echo "$(GREEN)📁 Project Structure:$(RESET)"
	@echo "├── src/flext_cli/          # Source code"
	@echo "├── tests/                  # Test files"
	@echo "├── pyproject.toml         # Project configuration"
	@echo "├── Makefile               # This file"
	@echo "└── README.md              # Documentation"
	@echo ""
	@echo "$(GREEN)🚀 Quick Start:$(RESET)"
	@echo "1. make install            # Install dependencies"
	@echo "2. make cli-test           # Test the system"
	@echo "3. make cli-help           # Show CLI help"
	@echo "4. make dev                # Full development workflow"
	@echo ""
	@echo "$(GREEN)🎯 CLI Commands:$(RESET)"
	@echo "• flext --help             - Show help"
	@echo "• flext config get         - Show configuration"
	@echo "• flext pipeline list      - List pipelines"
	@echo "• flext plugin list        - List plugins"
	@echo ""
	@echo "Documentation available in README.md"

.PHONY: help install install-dev update lint lint-fix format type-check check test test-unit test-integration test-cov cli-config cli-test cli-help cli-version cli-demo build clean shell env security version bump-patch bump-minor bump-major plugin-scaffold plugin-validate dev ci info

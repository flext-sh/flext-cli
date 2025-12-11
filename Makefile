# =============================================================================
# FLEXT-CLI - CLI Foundation Library Makefile
# =============================================================================
# Python 3.13+ CLI Framework - Clean Architecture + DDD + Zero Tolerance
# =============================================================================

# Project Configuration
PROJECT_NAME := flext-cli
PYTHON_VERSION := 3.13
POETRY := poetry
SRC_DIR := src
TESTS_DIR := tests
COV_DIR := flext_cli

# Quality Standards (MANDATORY - 90% COVERAGE)
MIN_COVERAGE := 90

# Export Configuration
export PROJECT_NAME PYTHON_VERSION MIN_COVERAGE

# =============================================================================
# HELP & INFORMATION
# =============================================================================

.PHONY: help
help: ## Show available commands
	@echo "FLEXT-CLI - CLI Foundation Library"
	@echo "=================================="
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

.PHONY: info
info: ## Show project information
	@echo "Project: $(PROJECT_NAME)"
	@echo "Python: $(PYTHON_VERSION)+"
	@echo "Poetry: $(POETRY)"
	@echo "Coverage: $(MIN_COVERAGE)% minimum (MANDATORY)"
	@echo "Architecture: CLI Foundation + Click + Rich"

# =============================================================================
# SETUP & INSTALLATION
# =============================================================================

.PHONY: install
install: ## Install dependencies
	$(POETRY) install

.PHONY: install-dev
install-dev: ## Install dev dependencies
	$(POETRY) install --with dev,test,docs

.PHONY: setup
setup: install-dev ## Complete project setup
	$(POETRY) run pre-commit install

# =============================================================================
# LINT CACHE CONFIGURATION (5-minute cache for performance)
# =============================================================================

LINT_CACHE_DIR := .lint-cache
CACHE_TIMEOUT := 300  # 5 minutes in seconds
CACHE_CHECK_FILE := $(LINT_CACHE_DIR)/.cache_check

# Create cache directory
$(LINT_CACHE_DIR):
	@mkdir -p $(LINT_CACHE_DIR)

# Check and invalidate stale cache
.PHONY: cache-check
cache-check: $(LINT_CACHE_DIR)
	@current_time=$$(date +%s); \
	for cache_file in $(LINT_CACHE_DIR)/.*.timestamp; do \
		if [ -f "$$cache_file" ]; then \
			file_time=$$(stat -c%Y "$$cache_file" 2>/dev/null || stat -f%m "$$cache_file" 2>/dev/null || echo "0"); \
			age=$$(( current_time - file_time )); \
			if [ $$age -gt $(CACHE_TIMEOUT) ]; then \
				rm -f "$$cache_file"; \
			fi; \
		fi; \
	done

# =============================================================================
# QUALITY GATES (MANDATORY - ZERO TOLERANCE) - WITH 5-MIN CACHE
# =============================================================================

.PHONY: validate
validate: lint type-check security test ## Run all quality gates (MANDATORY ORDER)

.PHONY: check
check: lint type-check ## Quick health check

.PHONY: lint
lint: cache-check ## Run linting (ZERO TOLERANCE) - cached for 5 min
	@if [ ! -f $(LINT_CACHE_DIR)/.ruff.timestamp ] || [ ! -f $(LINT_CACHE_DIR)/.ruff.sarif ]; then \
		echo "Running ruff linting..."; \
		$(POETRY) run ruff check . --output-format sarif > $(LINT_CACHE_DIR)/.ruff.sarif 2>&1 || true; \
		touch $(LINT_CACHE_DIR)/.ruff.timestamp; \
	else \
		echo "✓ Ruff check (cached - within 5 min)"; \
	fi
	@ruff_count=$$(grep -c '"ruleId"' $(LINT_CACHE_DIR)/.ruff.sarif 2>/dev/null || echo "0"); \
	echo "✓ Ruff check complete: $$ruff_count issues"; \
	if [ "$$ruff_count" -gt 0 ]; then \
		echo "ERROR: Ruff violations found. Run 'make fix' to auto-fix."; \
		exit 1; \
	fi

.PHONY: format
format: ## Format code
	$(POETRY) run ruff format .

.PHONY: type-check
type-check: cache-check ## Run type checking with MyPy (ZERO TOLERANCE) - cached for 5 min
	@if [ ! -f $(LINT_CACHE_DIR)/.mypy.timestamp ] || [ ! -f $(LINT_CACHE_DIR)/.mypy.json ]; then \
		echo "Running mypy type checking..."; \
		PYTHONPATH=$(SRC_DIR) $(POETRY) run python -m mypy $(SRC_DIR) --strict --ignore-missing-imports --output json > $(LINT_CACHE_DIR)/.mypy.json 2>&1 || true; \
		touch $(LINT_CACHE_DIR)/.mypy.timestamp; \
	else \
		echo "✓ MyPy check (cached - within 5 min)"; \
	fi
	@mypy_count=$$(jq 'length' $(LINT_CACHE_DIR)/.mypy.json 2>/dev/null || echo "0"); \
	echo "✓ MyPy check complete: $$mypy_count errors"; \
	if [ "$$mypy_count" -gt 0 ]; then \
		echo "ERROR: MyPy type errors found."; \
		jq '.[].message' $(LINT_CACHE_DIR)/.mypy.json 2>/dev/null | head -20; \
		exit 1; \
	fi

.PHONY: security
security: cache-check ## Run security scanning - cached for 5 min
	@if [ ! -f $(LINT_CACHE_DIR)/.bandit.timestamp ] || [ ! -f $(LINT_CACHE_DIR)/.bandit.json ]; then \
		echo "Running bandit security scan..."; \
		$(POETRY) run bandit -r $(SRC_DIR) -f json > $(LINT_CACHE_DIR)/.bandit.json 2>&1 || true; \
		touch $(LINT_CACHE_DIR)/.bandit.timestamp; \
		echo "✓ Bandit scan complete"; \
	else \
		echo "✓ Bandit scan (cached - within 5 min)"; \
	fi
	$(MAKE) deps-audit

.PHONY: fix
fix: ## Auto-fix issues
	@rm -f $(LINT_CACHE_DIR)/.ruff.timestamp  # Invalidate cache
	$(POETRY) run ruff check . --fix
	$(POETRY) run ruff format .

# =============================================================================
# TESTING (MANDATORY - 100% COVERAGE)
# =============================================================================

.PHONY: test
test: ## Run tests with 100% coverage (MANDATORY) - NOT cached (always fresh)
	@rm -f $(LINT_CACHE_DIR)/.pytest.timestamp  # Don't cache tests
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest -q --maxfail=10000 --cov=$(COV_DIR) --cov-report=term-missing:skip-covered --cov-fail-under=$(MIN_COVERAGE)

.PHONY: test-unit
test-unit: ## Run unit tests
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest -m "not integration" -v

.PHONY: test-integration
test-integration: ## Run integration tests with Docker
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest -m integration -v

.PHONY: test-fast
test-fast: ## Run tests without coverage
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest -v

.PHONY: coverage-html
coverage-html: ## Generate HTML coverage report
	PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest --cov=$(COV_DIR) --cov-report=html

# =============================================================================
# BUILD & DISTRIBUTION
# =============================================================================

.PHONY: build
build: ## Build package
	$(POETRY) build

.PHONY: build-clean
build-clean: clean build ## Clean and build

# =============================================================================
# CLI OPERATIONS
# =============================================================================

.PHONY: cli-test
cli-test: ## Test CLI commands
	$(POETRY) run python -c "from flext_cli.api import FlextCli; cli = FlextCli(); print('CLI test passed')"

.PHONY: cli-auth
cli-auth: ## Test auth commands
	$(POETRY) run python -m flext_cli.commands.auth --help

.PHONY: cli-config
cli-config: ## Test config commands
	$(POETRY) run python -m flext_cli.commands.config --help

.PHONY: cli-debug
cli-debug: ## Test debug commands
	$(POETRY) run python -m flext_cli.commands.debug --help

# =============================================================================
# DOCUMENTATION
# =============================================================================

.PHONY: docs
docs: ## Build documentation
	$(POETRY) run mkdocs build

.PHONY: docs-serve
docs-serve: ## Serve documentation
	$(POETRY) run mkdocs serve

# =============================================================================
# DEPENDENCIES
# =============================================================================

.PHONY: deps-update
deps-update: ## Update dependencies
	$(POETRY) update

.PHONY: deps-show
deps-show: ## Show dependency tree
	$(POETRY) show --tree

.PHONY: deps-audit
deps-audit: ## Audit dependencies
	$(POETRY) run pip-audit \
		--ignore-vuln GHSA-mw26-5g2v-hqw3 \
		--ignore-vuln GHSA-6w2r-r2m5-xq5w \
		--ignore-vuln GHSA-wj6h-64fc-37mp \
		--ignore-vuln GHSA-4xh5-x5gv-qwph \
		--ignore-vuln GHSA-7f5h-v6xp-fcq8 \
		--ignore-vuln GHSA-w476-p2h3-79g9 \
		--ignore-vuln GHSA-pqhf-p39g-3x64

# =============================================================================
# DEVELOPMENT
# =============================================================================

.PHONY: shell
shell: ## Open Python shell
	PYTHONPATH=$(SRC_DIR) $(POETRY) run python

.PHONY: pre-commit
pre-commit: ## Run pre-commit hooks
	$(POETRY) run pre-commit run --all-files

# =============================================================================
# MAINTENANCE
# =============================================================================

.PHONY: clean
clean: ## Clean build artifacts and cruft
	@echo "🧹 Cleaning $(PROJECT_NAME) - removing build artifacts, cache files, and cruft..."

	# Build artifacts
	rm -rf build/ dist/ *.egg-info/

	# Test artifacts
	rm -rf .pytest_cache/ htmlcov/ .coverage .coverage.* coverage.xml

	# Python cache directories
	rm -rf .mypy_cache/ .pyrefly_cache/ .ruff_cache/

	# Python bytecode
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true
	find . -type f -name "*.pyo" -delete 2>/dev/null || true

	# CLI-specific files
	rm -rf cli.log cli-*.log

	# Data directories
	rm -rf data/ output/ temp/

	# Temporary files
	find . -type f -name "*.tmp" -delete 2>/dev/null || true
	find . -type f -name "*.temp" -delete 2>/dev/null || true
	find . -type f -name ".DS_Store" -delete 2>/dev/null || true

	# Log files
	find . -type f -name "*.log" -delete 2>/dev/null || true

	# Editor files
	find . -type f -name ".vscode/settings.json" -delete 2>/dev/null || true
	find . -type f -name ".idea/" -type d -exec rm -rf {} + 2>/dev/null || true

	@echo "✅ $(PROJECT_NAME) cleanup complete"

.PHONY: clean-all
clean-all: clean ## Deep clean including venv
	rm -rf .venv/

.PHONY: reset
reset: clean-all setup ## Reset project

# =============================================================================
# LINT REPORTS (Multi-Agent Coordination)
# =============================================================================
# Include centralized lint-reports.mk from workspace root
include ../lint-reports.mk

# =============================================================================
# DIAGNOSTICS
# =============================================================================

.PHONY: diagnose
diagnose: ## Project diagnostics
	@echo "Python: $$(python --version)"
	@echo "Poetry: $$($(POETRY) --version)"
	@$(POETRY) env info

.PHONY: doctor
doctor: diagnose check ## Health check

# =============================================================================

# =============================================================================

.PHONY: t l f tc c i v
t: test
l: lint
f: format
tc: type-check
c: clean
i: install
v: validate

# =============================================================================
# CONFIGURATION
# =============================================================================

.DEFAULT_GOAL := help

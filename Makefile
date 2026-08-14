# flext-cli - CLI Framework
PROJECT_NAME := flext-cli

Q ?=
POETRY ?= poetry
SRC_DIR ?= src
TESTS_DIR ?= tests

FLEXT_DEFAULT_BRANCH := 0.12.0-dev
FLEXT_BRANCH ?= $(or $(FLEXT_CORE_BRANCH),$(GITHUB_HEAD_REF),$(FLEXT_DEFAULT_BRANCH))
FLEXT_GITHUB_ORG ?= flext-sh
FLEXT_SYNC_PACKAGES := flext-core flext-infra flext-tests

BASE_MK_AVAILABLE := false
ifneq ("$(wildcard ../base.mk)","")
BASE_MK_AVAILABLE := true
include ../base.mk
else ifneq ("$(wildcard base.mk)","")
BASE_MK_AVAILABLE := true
include base.mk
endif

# === PROJECT-SPECIFIC TARGETS ===

setup check test validate: flext-bootstrap-base-mk flext-sync-branch-deps

flext-bootstrap-base-mk: ## Ensure base.mk is present when outside monorepo
ifeq ($(BASE_MK_AVAILABLE),false)
	@branch="$${FLEXT_CORE_BRANCH:-$${GITHUB_HEAD_REF:-$(FLEXT_DEFAULT_BRANCH)}}"; \
	if [ -z "$$branch" ] || [ "$$branch" = "HEAD" ]; then \
		echo "[flext-sync] Unable to detect branch. Set FLEXT_CORE_BRANCH explicitly."; \
		exit 1; \
	fi; \
	echo "[flext-sync] Downloading base.mk from branch '$$branch'"; \
	tmp_dir="$$(mktemp -d)"; \
	trap 'rm -rf "$$tmp_dir"' EXIT; \
	git -C "$$tmp_dir" init -q; \
	git -C "$$tmp_dir" remote add origin "https://github.com/$(FLEXT_GITHUB_ORG)/flext-core.git"; \
	git -C "$$tmp_dir" fetch --depth 1 origin "$$branch"; \
	git -C "$$tmp_dir" show FETCH_HEAD:base.mk > base.mk
else
	@echo "[flext-sync] Using existing base.mk"
endif

flext-sync-branch-deps: ## Sync flext-core/flext-infra/flext-tests from matching git branch
	$(Q)branch="$${FLEXT_CORE_BRANCH:-$${GITHUB_HEAD_REF:-$(FLEXT_DEFAULT_BRANCH)}}"; \
	if [ -z "$$branch" ] || [ "$$branch" = "HEAD" ]; then \
		echo "[flext-sync] Unable to detect branch. Set FLEXT_CORE_BRANCH explicitly."; \
		exit 1; \
	fi; \
	for package in $(FLEXT_SYNC_PACKAGES); do \
		repo_url="https://github.com/$(FLEXT_GITHUB_ORG)/$$package.git"; \
		if ! git ls-remote --exit-code --heads "$$repo_url" "$$branch" >/dev/null 2>&1; then \
			echo "[flext-sync] Branch '$$branch' does not exist in $$package."; \
			exit 1; \
		fi; \
		echo "[flext-sync] Installing $$package from branch '$$branch'"; \
		$(POETRY) run pip install --quiet --no-deps --upgrade "git+$$repo_url@$$branch#egg=$$package"; \
	done

ifeq ($(BASE_MK_AVAILABLE),false)
setup: ## Setup project without base.mk
	poetry install --with dev

check: ## Lint and type check without base.mk
	poetry run ruff check src tests
	poetry run pyrefly check src

test: ## Run tests without base.mk
	PYTHONPATH=src poetry run pytest -v

validate: ## Validate without base.mk
	$(MAKE) check
	$(MAKE) test

help:
	@echo "Available targets: setup check test validate flext-bootstrap-base-mk flext-sync-branch-deps"
endif

.PHONY: cli-test cli-auth cli-config cli-debug test-unit test-integration
.PHONY: build docs-serve shell flext-bootstrap-base-mk flext-sync-branch-deps

cli-test: ## Test CLI commands
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_cli*.py -q

cli-auth: ## Test CLI authentication
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_auth*.py -q

cli-config: ## Test CLI configuration
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_config*.py -q

cli-debug: ## Test CLI debug
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_debug*.py -q

docs-serve: ## Serve documentation
	$(Q)$(POETRY) run mkdocs serve

.DEFAULT_GOAL := help

# flext-cli - CLI Framework
PROJECT_NAME := flext-cli
ifneq ("$(wildcard ../base.mk)", "")
include ../base.mk
else
include base.mk
endif

# === PROJECT-SPECIFIC TARGETS ===
.PHONY: cli-test cli-auth cli-config cli-debug test-unit test-integration
.PHONY: build docs docs-serve shell

cli-test: ## Test CLI commands
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_cli*.py -q

cli-auth: ## Test CLI authentication
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_auth*.py -q

cli-config: ## Test CLI configuration
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_config*.py -q

cli-debug: ## Test CLI debug
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_debug*.py -q

docs: ## Build documentation
	$(Q)$(POETRY) run mkdocs build

docs-serve: ## Serve documentation
	$(Q)$(POETRY) run mkdocs serve

.DEFAULT_GOAL := help

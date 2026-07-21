.PHONY: cli-test cli-auth cli-config cli-debug test-unit test-integration
.PHONY: build shell
cli-test: ## Test CLI commands
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_cli*.py -q
cli-auth: ## Test CLI authentication
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_auth*.py -q
cli-config: ## Test CLI configuration
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_config*.py -q
cli-debug: ## Test CLI debug
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_debug*.py -q
.DEFAULT_GOAL := help

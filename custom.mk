# Private project handlers for flext-cli.
# Strict extension: only `_custom_<verb>_<what>` handlers and `(pre|post)-<verb>[-<what>]`
# hooks. Public targets, toolchain vars, .DEFAULT_GOAL, includes, and help are
# invalid (base.mk owns those). Each handler maps to `make <verb> WHAT=<what>`.
.PHONY: _custom_test_cli _custom_test_auth _custom_test_config _custom_test_debug _custom_test_runtime
_custom_test_cli: ## make test WHAT=cli — CLI command tests
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_cli*.py -q
_custom_test_auth: ## make test WHAT=auth — CLI auth tests
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_auth*.py -q
_custom_test_config: ## make test WHAT=config — CLI config tests
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_config*.py -q
_custom_test_debug: ## make test WHAT=debug — CLI debug tests
	$(Q)PYTHONPATH=$(SRC_DIR) $(POETRY) run pytest $(TESTS_DIR)/unit/test_debug*.py -q
_custom_test_runtime: ## make test WHAT=runtime — portable process-runner tests
	@$(UV_RUN) python -m pytest \
		"$(PROJECT_ROOT)/tests/unit/test_runtime_streamed_process.py" \
		"$(PROJECT_ROOT)/tests/unit/test_runtime_process_containment.py" \
		"$(PROJECT_ROOT)/tests/unit/test_runtime_process_descendants.py"

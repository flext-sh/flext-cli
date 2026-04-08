# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports

_LAZY_IMPORTS = {
    "conftest": "tests.unit.conftest",
    "test_base": "tests.unit.test_base",
    "test_cli_params": "tests.unit.test_cli_params",
    "test_cli_service": "tests.unit.test_cli_service",
    "test_cmd": "tests.unit.test_cmd",
    "test_cmd_cov": "tests.unit.test_cmd_cov",
    "test_commands": "tests.unit.test_commands",
    "test_config": "tests.unit.test_config",
    "test_constants": "tests.unit.test_constants",
    "test_examples_smoke": "tests.unit.test_examples_smoke",
    "test_pipeline": "tests.unit.test_pipeline",
    "test_prompts": "tests.unit.test_prompts",
    "test_prompts_cov": "tests.unit.test_prompts_cov",
    "test_protocols": "tests.unit.test_protocols",
    "test_runtime_utilities_core": "tests.unit.test_runtime_utilities_core",
    "test_runtime_utilities_extra": "tests.unit.test_runtime_utilities_extra",
    "test_tables": "tests.unit.test_tables",
    "test_toml_utilities": "tests.unit.test_toml_utilities",
    "test_typings": "tests.unit.test_typings",
    "test_utilities_cov": "tests.unit.test_utilities_cov",
    "test_version": "tests.unit.test_version",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

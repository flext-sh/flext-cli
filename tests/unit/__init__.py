# AUTO-GENERATED FILE — Regenerate with: make gen
"""Unit package."""

from __future__ import annotations

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".conftest": ("conftest",),
        ".test_base": ("test_base",),
        ".test_cli_params": ("test_cli_params",),
        ".test_cli_service": ("test_cli_service",),
        ".test_cmd": ("test_cmd",),
        ".test_cmd_cov": ("test_cmd_cov",),
        ".test_commands": ("test_commands",),
        ".test_constants": ("test_constants",),
        ".test_examples_smoke": ("test_examples_smoke",),
        ".test_pipeline": ("test_pipeline",),
        ".test_prompts": ("test_prompts",),
        ".test_prompts_cov": ("test_prompts_cov",),
        ".test_protocols": ("test_protocols",),
        ".test_runtime_utilities_core": ("test_runtime_utilities_core",),
        ".test_runtime_utilities_extra": ("test_runtime_utilities_extra",),
        ".test_settings": ("test_settings",),
        ".test_tables": ("test_tables",),
        ".test_toml_utilities": ("test_toml_utilities",),
        ".test_typings": ("test_typings",),
        ".test_utilities_cov": ("test_utilities_cov",),
        ".test_version": ("test_version",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

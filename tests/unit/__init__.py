# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Unit package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import tests.unit.conftest as _tests_unit_conftest

    conftest = _tests_unit_conftest
    import tests.unit.test_base as _tests_unit_test_base

    test_base = _tests_unit_test_base
    import tests.unit.test_cli_params as _tests_unit_test_cli_params

    test_cli_params = _tests_unit_test_cli_params
    import tests.unit.test_cli_service as _tests_unit_test_cli_service

    test_cli_service = _tests_unit_test_cli_service
    import tests.unit.test_cmd as _tests_unit_test_cmd

    test_cmd = _tests_unit_test_cmd
    import tests.unit.test_cmd_cov as _tests_unit_test_cmd_cov

    test_cmd_cov = _tests_unit_test_cmd_cov
    import tests.unit.test_commands as _tests_unit_test_commands

    test_commands = _tests_unit_test_commands
    import tests.unit.test_config as _tests_unit_test_config

    test_config = _tests_unit_test_config
    import tests.unit.test_constants as _tests_unit_test_constants

    test_constants = _tests_unit_test_constants
    import tests.unit.test_examples_smoke as _tests_unit_test_examples_smoke

    test_examples_smoke = _tests_unit_test_examples_smoke
    import tests.unit.test_pipeline as _tests_unit_test_pipeline

    test_pipeline = _tests_unit_test_pipeline
    import tests.unit.test_prompts as _tests_unit_test_prompts

    test_prompts = _tests_unit_test_prompts
    import tests.unit.test_prompts_cov as _tests_unit_test_prompts_cov

    test_prompts_cov = _tests_unit_test_prompts_cov
    import tests.unit.test_protocols as _tests_unit_test_protocols

    test_protocols = _tests_unit_test_protocols
    import tests.unit.test_runtime_utilities_core as _tests_unit_test_runtime_utilities_core

    test_runtime_utilities_core = _tests_unit_test_runtime_utilities_core
    import tests.unit.test_runtime_utilities_extra as _tests_unit_test_runtime_utilities_extra

    test_runtime_utilities_extra = _tests_unit_test_runtime_utilities_extra
    import tests.unit.test_tables as _tests_unit_test_tables

    test_tables = _tests_unit_test_tables
    import tests.unit.test_toml_utilities as _tests_unit_test_toml_utilities

    test_toml_utilities = _tests_unit_test_toml_utilities
    import tests.unit.test_typings as _tests_unit_test_typings

    test_typings = _tests_unit_test_typings
    import tests.unit.test_utilities_cov as _tests_unit_test_utilities_cov

    test_utilities_cov = _tests_unit_test_utilities_cov
    import tests.unit.test_version as _tests_unit_test_version

    test_version = _tests_unit_test_version
    from flext_core.constants import FlextConstants as c
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.models import FlextModels as m
    from flext_core.protocols import FlextProtocols as p
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
    from flext_core.typings import FlextTypes as t
    from flext_core.utilities import FlextUtilities as u
_LAZY_IMPORTS = {
    "c": ("flext_core.constants", "FlextConstants"),
    "conftest": "tests.unit.conftest",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("flext_core.models", "FlextModels"),
    "p": ("flext_core.protocols", "FlextProtocols"),
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("flext_core.typings", "FlextTypes"),
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
    "u": ("flext_core.utilities", "FlextUtilities"),
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "c",
    "conftest",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "test_base",
    "test_cli_params",
    "test_cli_service",
    "test_cmd",
    "test_cmd_cov",
    "test_commands",
    "test_config",
    "test_constants",
    "test_examples_smoke",
    "test_pipeline",
    "test_prompts",
    "test_prompts_cov",
    "test_protocols",
    "test_runtime_utilities_core",
    "test_runtime_utilities_extra",
    "test_tables",
    "test_toml_utilities",
    "test_typings",
    "test_utilities_cov",
    "test_version",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

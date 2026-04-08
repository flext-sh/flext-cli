# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    from examples.constants import (
        ExamplesFlextCliConstants,
        ExamplesFlextCliConstants as c,
    )
    from examples.models import ExamplesFlextCliModels, ExamplesFlextCliModels as m
    from examples.protocols import (
        ExamplesFlextCliProtocols,
        ExamplesFlextCliProtocols as p,
    )
    from examples.typings import ExamplesFlextCliTypes, ExamplesFlextCliTypes as t
    from examples.utilities import (
        ExamplesFlextCliUtilities,
        ExamplesFlextCliUtilities as u,
    )
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
    from flext_core.service import FlextService as s
_LAZY_IMPORTS = {
    "ExamplesFlextCliConstants": ("examples.constants", "ExamplesFlextCliConstants"),
    "ExamplesFlextCliModels": ("examples.models", "ExamplesFlextCliModels"),
    "ExamplesFlextCliProtocols": ("examples.protocols", "ExamplesFlextCliProtocols"),
    "ExamplesFlextCliTypes": ("examples.typings", "ExamplesFlextCliTypes"),
    "ExamplesFlextCliUtilities": ("examples.utilities", "ExamplesFlextCliUtilities"),
    "c": ("examples.constants", "ExamplesFlextCliConstants"),
    "constants": "examples.constants",
    "d": ("flext_core.decorators", "FlextDecorators"),
    "e": ("flext_core.exceptions", "FlextExceptions"),
    "ex_01_getting_started": "examples.ex_01_getting_started",
    "ex_02_output_formatting": "examples.ex_02_output_formatting",
    "ex_03_interactive_prompts": "examples.ex_03_interactive_prompts",
    "ex_04_file_operations": "examples.ex_04_file_operations",
    "ex_05_authentication": "examples.ex_05_authentication",
    "ex_06_configuration": "examples.ex_06_configuration",
    "ex_07_plugin_system": "examples.ex_07_plugin_system",
    "ex_08_shell_interaction": "examples.ex_08_shell_interaction",
    "ex_09_performance_optimization": "examples.ex_09_performance_optimization",
    "ex_10_testing_utilities": "examples.ex_10_testing_utilities",
    "ex_11_complete_integration": "examples.ex_11_complete_integration",
    "ex_12_pydantic_driven_cli": "examples.ex_12_pydantic_driven_cli",
    "ex_14_advanced_file_formats": "examples.ex_14_advanced_file_formats",
    "ex_15_plugin": "examples.ex_15_plugin",
    "h": ("flext_core.handlers", "FlextHandlers"),
    "m": ("examples.models", "ExamplesFlextCliModels"),
    "models": "examples.models",
    "p": ("examples.protocols", "ExamplesFlextCliProtocols"),
    "protocols": "examples.protocols",
    "r": ("flext_core.result", "FlextResult"),
    "s": ("flext_core.service", "FlextService"),
    "t": ("examples.typings", "ExamplesFlextCliTypes"),
    "typings": "examples.typings",
    "u": ("examples.utilities", "ExamplesFlextCliUtilities"),
    "utilities": "examples.utilities",
    "x": ("flext_core.mixins", "FlextMixins"),
}

__all__ = [
    "ExamplesFlextCliConstants",
    "ExamplesFlextCliModels",
    "ExamplesFlextCliProtocols",
    "ExamplesFlextCliTypes",
    "ExamplesFlextCliUtilities",
    "c",
    "constants",
    "d",
    "e",
    "ex_01_getting_started",
    "ex_02_output_formatting",
    "ex_03_interactive_prompts",
    "ex_04_file_operations",
    "ex_05_authentication",
    "ex_06_configuration",
    "ex_07_plugin_system",
    "ex_08_shell_interaction",
    "ex_09_performance_optimization",
    "ex_10_testing_utilities",
    "ex_11_complete_integration",
    "ex_12_pydantic_driven_cli",
    "ex_14_advanced_file_formats",
    "ex_15_plugin",
    "h",
    "m",
    "models",
    "p",
    "protocols",
    "r",
    "s",
    "t",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

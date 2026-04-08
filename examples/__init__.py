# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Examples package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import install_lazy_exports

if _t.TYPE_CHECKING:
    import examples.constants as _examples_constants

    constants = _examples_constants
    import examples.ex_01_getting_started as _examples_ex_01_getting_started
    from examples.constants import (
        ExamplesFlextCliConstants,
        ExamplesFlextCliConstants as c,
    )

    ex_01_getting_started = _examples_ex_01_getting_started
    import examples.ex_02_output_formatting as _examples_ex_02_output_formatting

    ex_02_output_formatting = _examples_ex_02_output_formatting
    import examples.ex_03_interactive_prompts as _examples_ex_03_interactive_prompts

    ex_03_interactive_prompts = _examples_ex_03_interactive_prompts
    import examples.ex_04_file_operations as _examples_ex_04_file_operations

    ex_04_file_operations = _examples_ex_04_file_operations
    import examples.ex_05_authentication as _examples_ex_05_authentication

    ex_05_authentication = _examples_ex_05_authentication
    import examples.ex_06_configuration as _examples_ex_06_configuration

    ex_06_configuration = _examples_ex_06_configuration
    import examples.ex_07_plugin_system as _examples_ex_07_plugin_system

    ex_07_plugin_system = _examples_ex_07_plugin_system
    import examples.ex_08_shell_interaction as _examples_ex_08_shell_interaction

    ex_08_shell_interaction = _examples_ex_08_shell_interaction
    import examples.ex_09_performance_optimization as _examples_ex_09_performance_optimization

    ex_09_performance_optimization = _examples_ex_09_performance_optimization
    import examples.ex_10_testing_utilities as _examples_ex_10_testing_utilities

    ex_10_testing_utilities = _examples_ex_10_testing_utilities
    import examples.ex_11_complete_integration as _examples_ex_11_complete_integration

    ex_11_complete_integration = _examples_ex_11_complete_integration
    import examples.ex_12_pydantic_driven_cli as _examples_ex_12_pydantic_driven_cli

    ex_12_pydantic_driven_cli = _examples_ex_12_pydantic_driven_cli
    import examples.ex_14_advanced_file_formats as _examples_ex_14_advanced_file_formats

    ex_14_advanced_file_formats = _examples_ex_14_advanced_file_formats
    import examples.ex_15_plugin as _examples_ex_15_plugin

    ex_15_plugin = _examples_ex_15_plugin
    import examples.models as _examples_models

    models = _examples_models
    import examples.protocols as _examples_protocols
    from examples.models import ExamplesFlextCliModels, ExamplesFlextCliModels as m

    protocols = _examples_protocols
    import examples.typings as _examples_typings
    from examples.protocols import (
        ExamplesFlextCliProtocols,
        ExamplesFlextCliProtocols as p,
    )

    typings = _examples_typings
    import examples.utilities as _examples_utilities
    from examples.typings import ExamplesFlextCliTypes, ExamplesFlextCliTypes as t

    utilities = _examples_utilities
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

# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Examples package."""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import FlextTypes

    from examples import plugins
    from examples.example_utils import (
        display_config_table,
        display_success_summary,
        display_validation_errors,
        handle_command_result,
        print_demo_completion,
        print_demo_error,
        to_json_dict,
    )
    from examples.models import (
        AdvancedDatabaseConfig,
        AppConfigAdvanced,
        AppConfigNested,
        AppWizardConfig,
        DatabaseConfig,
        DatabaseWizardConfig,
        DeployConfig,
        MyAppConfig,
        NumericPromptResult,
    )
    from examples.plugins.example_plugin import (
        DataProcessorPlugin,
        ExamplePlugin,
        demonstrate_plugin_commands,
    )
    from examples.plugins.protocols import (
        CliMainWithGroups,
        FlextCliProtocols,
        GroupWithCommands,
        p,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "AdvancedDatabaseConfig": ["examples.models", "AdvancedDatabaseConfig"],
    "AppConfigAdvanced": ["examples.models", "AppConfigAdvanced"],
    "AppConfigNested": ["examples.models", "AppConfigNested"],
    "AppWizardConfig": ["examples.models", "AppWizardConfig"],
    "CliMainWithGroups": ["examples.plugins.protocols", "CliMainWithGroups"],
    "DataProcessorPlugin": ["examples.plugins.example_plugin", "DataProcessorPlugin"],
    "DatabaseConfig": ["examples.models", "DatabaseConfig"],
    "DatabaseWizardConfig": ["examples.models", "DatabaseWizardConfig"],
    "DeployConfig": ["examples.models", "DeployConfig"],
    "ExamplePlugin": ["examples.plugins.example_plugin", "ExamplePlugin"],
    "FlextCliProtocols": ["examples.plugins.protocols", "FlextCliProtocols"],
    "GroupWithCommands": ["examples.plugins.protocols", "GroupWithCommands"],
    "MyAppConfig": ["examples.models", "MyAppConfig"],
    "NumericPromptResult": ["examples.models", "NumericPromptResult"],
    "demonstrate_plugin_commands": [
        "examples.plugins.example_plugin",
        "demonstrate_plugin_commands",
    ],
    "display_config_table": ["examples.example_utils", "display_config_table"],
    "display_success_summary": ["examples.example_utils", "display_success_summary"],
    "display_validation_errors": [
        "examples.example_utils",
        "display_validation_errors",
    ],
    "handle_command_result": ["examples.example_utils", "handle_command_result"],
    "p": ["examples.plugins.protocols", "p"],
    "plugins": ["examples.plugins", ""],
    "print_demo_completion": ["examples.example_utils", "print_demo_completion"],
    "print_demo_error": ["examples.example_utils", "print_demo_error"],
    "to_json_dict": ["examples.example_utils", "to_json_dict"],
}

__all__ = [
    "AdvancedDatabaseConfig",
    "AppConfigAdvanced",
    "AppConfigNested",
    "AppWizardConfig",
    "CliMainWithGroups",
    "DataProcessorPlugin",
    "DatabaseConfig",
    "DatabaseWizardConfig",
    "DeployConfig",
    "ExamplePlugin",
    "FlextCliProtocols",
    "GroupWithCommands",
    "MyAppConfig",
    "NumericPromptResult",
    "demonstrate_plugin_commands",
    "display_config_table",
    "display_success_summary",
    "display_validation_errors",
    "handle_command_result",
    "p",
    "plugins",
    "print_demo_completion",
    "print_demo_error",
    "to_json_dict",
]


_LAZY_CACHE: MutableMapping[str, FlextTypes.ModuleExport] = {}


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562).

    A local cache ``_LAZY_CACHE`` persists resolved objects across repeated
    accesses during process lifetime.

    Args:
        name: Attribute name requested by dir()/import.

    Returns:
        Lazy-loaded module export type.

    Raises:
        AttributeError: If attribute not registered.

    """
    if name in _LAZY_CACHE:
        return _LAZY_CACHE[name]

    value = lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)
    _LAZY_CACHE[name] = value
    return value


def __dir__() -> Sequence[str]:
    """Return list of available attributes for dir() and autocomplete.

    Returns:
        List of public names from module exports.

    """
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)

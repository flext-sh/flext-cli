# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Examples package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core.typings import FlextTypes

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
    from examples.plugins import (
        CliMainWithGroups,
        DataProcessorPlugin,
        ExamplePlugin,
        FlextCliProtocols,
        GroupWithCommands,
        demonstrate_plugin_commands,
        p,
    )

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "AdvancedDatabaseConfig": ("examples.models", "AdvancedDatabaseConfig"),
    "AppConfigAdvanced": ("examples.models", "AppConfigAdvanced"),
    "AppConfigNested": ("examples.models", "AppConfigNested"),
    "AppWizardConfig": ("examples.models", "AppWizardConfig"),
    "CliMainWithGroups": ("examples.plugins", "CliMainWithGroups"),
    "DataProcessorPlugin": ("examples.plugins", "DataProcessorPlugin"),
    "DatabaseConfig": ("examples.models", "DatabaseConfig"),
    "DatabaseWizardConfig": ("examples.models", "DatabaseWizardConfig"),
    "DeployConfig": ("examples.models", "DeployConfig"),
    "ExamplePlugin": ("examples.plugins", "ExamplePlugin"),
    "FlextCliProtocols": ("examples.plugins", "FlextCliProtocols"),
    "GroupWithCommands": ("examples.plugins", "GroupWithCommands"),
    "MyAppConfig": ("examples.models", "MyAppConfig"),
    "NumericPromptResult": ("examples.models", "NumericPromptResult"),
    "demonstrate_plugin_commands": ("examples.plugins", "demonstrate_plugin_commands"),
    "display_config_table": ("examples.example_utils", "display_config_table"),
    "display_success_summary": ("examples.example_utils", "display_success_summary"),
    "display_validation_errors": (
        "examples.example_utils",
        "display_validation_errors",
    ),
    "handle_command_result": ("examples.example_utils", "handle_command_result"),
    "p": ("examples.plugins", "p"),
    "plugins": ("examples.plugins", ""),
    "print_demo_completion": ("examples.example_utils", "print_demo_completion"),
    "print_demo_error": ("examples.example_utils", "print_demo_error"),
    "to_json_dict": ("examples.example_utils", "to_json_dict"),
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


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)

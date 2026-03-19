# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Flext cli package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import d, e, h, r
    from flext_core.typings import FlextTypes

    from flext_cli import _models, services
    from flext_cli.__version__ import (
        __all__,
        __author__,
        __author_email__,
        __description__,
        __license__,
        __title__,
        __url__,
        __version__,
        __version_info__,
    )
    from flext_cli._models.cli_models_statistics import FlextCliModelsStatistics
    from flext_cli._models.cli_models_system_context import FlextCliModelsSystemContext
    from flext_cli.api import FlextCli
    from flext_cli.app_base import FlextCliAppBase
    from flext_cli.base import FlextCliServiceBase, s
    from flext_cli.cli import FlextCliCli
    from flext_cli.cli_params import FlextCliCommonParams
    from flext_cli.command_builder import FlextCliCommandBuilder
    from flext_cli.commands import FlextCliCommands
    from flext_cli.constants import FlextCliConstants, c
    from flext_cli.debug import FlextCliDebug
    from flext_cli.file_tools import FlextCliFileTools
    from flext_cli.formatters import FlextCliFormatters
    from flext_cli.middleware import FlextCliLoggingMiddleware
    from flext_cli.mixins import FlextCliMixins, x
    from flext_cli.models import FlextCliModels, m
    from flext_cli.option_groups import FlextCliOptionGroup
    from flext_cli.protocols import FlextCliProtocols, p
    from flext_cli.services.cmd import FlextCliCmd
    from flext_cli.services.core import FlextCliCore
    from flext_cli.services.output import FlextCliOutput
    from flext_cli.services.prompts import FlextCliPrompts
    from flext_cli.services.tables import FlextCliTables
    from flext_cli.settings import FlextCliSettings, logger
    from flext_cli.typings import FlextCliTypes, t
    from flext_cli.utilities import FlextCliUtilities, u

_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextCli": ("flext_cli.api", "FlextCli"),
    "FlextCliAppBase": ("flext_cli.app_base", "FlextCliAppBase"),
    "FlextCliCli": ("flext_cli.cli", "FlextCliCli"),
    "FlextCliCmd": ("flext_cli.services.cmd", "FlextCliCmd"),
    "FlextCliCommandBuilder": ("flext_cli.command_builder", "FlextCliCommandBuilder"),
    "FlextCliCommands": ("flext_cli.commands", "FlextCliCommands"),
    "FlextCliCommonParams": ("flext_cli.cli_params", "FlextCliCommonParams"),
    "FlextCliConstants": ("flext_cli.constants", "FlextCliConstants"),
    "FlextCliCore": ("flext_cli.services.core", "FlextCliCore"),
    "FlextCliDebug": ("flext_cli.debug", "FlextCliDebug"),
    "FlextCliFileTools": ("flext_cli.file_tools", "FlextCliFileTools"),
    "FlextCliFormatters": ("flext_cli.formatters", "FlextCliFormatters"),
    "FlextCliLoggingMiddleware": ("flext_cli.middleware", "FlextCliLoggingMiddleware"),
    "FlextCliMixins": ("flext_cli.mixins", "FlextCliMixins"),
    "FlextCliModels": ("flext_cli.models", "FlextCliModels"),
    "FlextCliModelsStatistics": (
        "flext_cli._models.cli_models_statistics",
        "FlextCliModelsStatistics",
    ),
    "FlextCliModelsSystemContext": (
        "flext_cli._models.cli_models_system_context",
        "FlextCliModelsSystemContext",
    ),
    "FlextCliOptionGroup": ("flext_cli.option_groups", "FlextCliOptionGroup"),
    "FlextCliOutput": ("flext_cli.services.output", "FlextCliOutput"),
    "FlextCliPrompts": ("flext_cli.services.prompts", "FlextCliPrompts"),
    "FlextCliProtocols": ("flext_cli.protocols", "FlextCliProtocols"),
    "FlextCliServiceBase": ("flext_cli.base", "FlextCliServiceBase"),
    "FlextCliSettings": ("flext_cli.settings", "FlextCliSettings"),
    "FlextCliTables": ("flext_cli.services.tables", "FlextCliTables"),
    "FlextCliTypes": ("flext_cli.typings", "FlextCliTypes"),
    "FlextCliUtilities": ("flext_cli.utilities", "FlextCliUtilities"),
    "__all__": ("flext_cli.__version__", "__all__"),
    "__author__": ("flext_cli.__version__", "__author__"),
    "__author_email__": ("flext_cli.__version__", "__author_email__"),
    "__description__": ("flext_cli.__version__", "__description__"),
    "__license__": ("flext_cli.__version__", "__license__"),
    "__title__": ("flext_cli.__version__", "__title__"),
    "__url__": ("flext_cli.__version__", "__url__"),
    "__version__": ("flext_cli.__version__", "__version__"),
    "__version_info__": ("flext_cli.__version__", "__version_info__"),
    "_models": ("flext_cli._models", ""),
    "c": ("flext_cli.constants", "c"),
    "d": ("flext_core", "d"),
    "e": ("flext_core", "e"),
    "h": ("flext_core", "h"),
    "logger": ("flext_cli.settings", "logger"),
    "m": ("flext_cli.models", "m"),
    "p": ("flext_cli.protocols", "p"),
    "r": ("flext_core", "r"),
    "s": ("flext_cli.base", "s"),
    "services": ("flext_cli.services", ""),
    "t": ("flext_cli.typings", "t"),
    "u": ("flext_cli.utilities", "u"),
    "x": ("flext_cli.mixins", "x"),
}

__all__ = [
    "FlextCli",
    "FlextCliAppBase",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommandBuilder",
    "FlextCliCommands",
    "FlextCliCommonParams",
    "FlextCliConstants",
    "FlextCliCore",
    "FlextCliDebug",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliLoggingMiddleware",
    "FlextCliMixins",
    "FlextCliModels",
    "FlextCliModelsStatistics",
    "FlextCliModelsSystemContext",
    "FlextCliOptionGroup",
    "FlextCliOutput",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliServiceBase",
    "FlextCliSettings",
    "FlextCliTables",
    "FlextCliTypes",
    "FlextCliUtilities",
    "__all__",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "_models",
    "c",
    "d",
    "e",
    "h",
    "logger",
    "m",
    "p",
    "r",
    "s",
    "services",
    "t",
    "u",
    "x",
]


def __getattr__(name: str) -> FlextTypes.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)

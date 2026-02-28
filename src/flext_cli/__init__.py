"""Public exports for flext-cli with enforced framework isolation.

Expõe `FlextCli`, os serviços de domínio e utilidades respeitando a regra de
isolamento: Typer/Click permanecem em `cli.py`, enquanto Rich/Tabulate ficam em
`formatters.py` e `services/tables.py`. Utilize esses exports de alto nível
para preservar o comportamento suportado pelo projeto.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from flext_core import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import d, e, h, r, x

    from flext_cli import (
        FlextCli,
        FlextCliAppBase,
        FlextCliCli,
        FlextCliCmd,
        FlextCliCommandBuilder as FlextCommandBuilder,
        FlextCliCommands,
        FlextCliCommonParams,
        FlextCliConstants,
        FlextCliConstants as c,
        FlextCliCore,
        FlextCliDebug,
        FlextCliFileTools,
        FlextCliFormatters,
        FlextCliLoggingMiddleware as LoggingMiddleware,
        FlextCliMiddleware as FlextMiddleware,
        FlextCliMixins,
        FlextCliModels,
        FlextCliModels as m,
        FlextCliOptionGroup as FlextOptionGroup,
        FlextCliOutput,
        FlextCliPrompts,
        FlextCliProtocols,
        FlextCliProtocols as p,
        FlextCliRetryMiddleware as RetryMiddleware,
        FlextCliServiceBase,
        FlextCliSettings,
        FlextCliTables,
        FlextCliTypes,
        FlextCliTypes as t,
        FlextCliUtilities,
        FlextCliUtilities as u,
        FlextCliValidationMiddleware as ValidationMiddleware,
        __version__,
        __version_info__,
    )

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextCli": ("flext_cli.api", "FlextCli"),
    "FlextCliAppBase": ("flext_cli.app_base", "FlextCliAppBase"),
    "FlextCliCli": ("flext_cli.cli", "FlextCliCli"),
    "FlextCliCmd": ("flext_cli.services.cmd", "FlextCliCmd"),
    "FlextCliCommands": ("flext_cli.commands", "FlextCliCommands"),
    "FlextCliCommonParams": ("flext_cli.cli_params", "FlextCliCommonParams"),
    "FlextCliConstants": ("flext_cli.constants", "FlextCliConstants"),
    "FlextCliCore": ("flext_cli.services.core", "FlextCliCore"),
    "FlextCliDebug": ("flext_cli.debug", "FlextCliDebug"),
    "FlextCliFileTools": ("flext_cli.file_tools", "FlextCliFileTools"),
    "FlextCliFormatters": ("flext_cli.formatters", "FlextCliFormatters"),
    "FlextCliMixins": ("flext_cli.mixins", "FlextCliMixins"),
    "FlextCliModels": ("flext_cli.models", "FlextCliModels"),
    "FlextCliOutput": ("flext_cli.services.output", "FlextCliOutput"),
    "FlextCliPrompts": ("flext_cli.services.prompts", "FlextCliPrompts"),
    "FlextCliProtocols": ("flext_cli.protocols", "FlextCliProtocols"),
    "FlextCliServiceBase": ("flext_cli.base", "FlextCliServiceBase"),
    "FlextCliSettings": ("flext_cli.settings", "FlextCliSettings"),
    "FlextCliTables": ("flext_cli.services.tables", "FlextCliTables"),
    "FlextCliTypes": ("flext_cli.typings", "FlextCliTypes"),
    "FlextCliUtilities": ("flext_cli.utilities", "FlextCliUtilities"),
    "FlextCommandBuilder": ("flext_cli.command_builder", "FlextCliCommandBuilder"),
    "FlextMiddleware": ("flext_cli.middleware", "FlextCliMiddleware"),
    "FlextOptionGroup": ("flext_cli.option_groups", "FlextCliOptionGroup"),
    "LoggingMiddleware": ("flext_cli.middleware", "FlextCliLoggingMiddleware"),
    "RetryMiddleware": ("flext_cli.middleware", "FlextCliRetryMiddleware"),
    "ValidationMiddleware": ("flext_cli.middleware", "FlextCliValidationMiddleware"),
    "__version__": ("flext_cli.__version__", "__version__"),
    "__version_info__": ("flext_cli.__version__", "__version_info__"),
    "c": ("flext_cli.constants", "FlextCliConstants"),
    "d": ("flext_core", "d"),
    "e": ("flext_core", "e"),
    "h": ("flext_core", "h"),
    "m": ("flext_cli.models", "FlextCliModels"),
    "p": ("flext_cli.protocols", "FlextCliProtocols"),
    "r": ("flext_core", "r"),
    "t": ("flext_cli.typings", "FlextCliTypes"),
    "u": ("flext_cli.utilities", "FlextCliUtilities"),
    "x": ("flext_core", "x"),
}

__all__ = [
    "FlextCli",
    "FlextCliAppBase",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommands",
    "FlextCliCommonParams",
    "FlextCliConstants",
    "FlextCliCore",
    "FlextCliDebug",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliMixins",
    "FlextCliModels",
    "FlextCliOutput",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliServiceBase",
    "FlextCliSettings",
    "FlextCliTables",
    "FlextCliTypes",
    "FlextCliUtilities",
    "FlextCommandBuilder",
    "FlextMiddleware",
    "FlextOptionGroup",
    "LoggingMiddleware",
    "RetryMiddleware",
    "ValidationMiddleware",
    "__version__",
    "__version_info__",
    "c",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "t",
    "u",
    "x",
]


def __getattr__(name: str) -> Any:  # noqa: ANN401
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)

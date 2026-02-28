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

from flext_core._utilities.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
    from flext_core import d, e, h, r, x

    from flext_cli.__version__ import __version__, __version_info__
    from flext_cli.api import FlextCli
    from flext_cli.app_base import FlextCliAppBase
    from flext_cli.base import FlextCliServiceBase
    from flext_cli.cli import FlextCliCli
    from flext_cli.cli_params import FlextCliCommonParams
    from flext_cli.command_builder import FlextCliCommandBuilder as FlextCommandBuilder
    from flext_cli.commands import FlextCliCommands
    from flext_cli.constants import FlextCliConstants, FlextCliConstants as c
    from flext_cli.debug import FlextCliDebug
    from flext_cli.file_tools import FlextCliFileTools
    from flext_cli.formatters import FlextCliFormatters
    from flext_cli.middleware import (
        FlextCliLoggingMiddleware as LoggingMiddleware,
        FlextCliMiddleware as FlextMiddleware,
        FlextCliRetryMiddleware as RetryMiddleware,
        FlextCliValidationMiddleware as ValidationMiddleware,
    )
    from flext_cli.mixins import FlextCliMixins
    from flext_cli.models import FlextCliModels, FlextCliModels as m
    from flext_cli.option_groups import (
        FlextCliOptionGroup,
        FlextCliOptionGroup as FlextOptionGroup,
    )
    from flext_cli.protocols import FlextCliProtocols, FlextCliProtocols as p
    from flext_cli.services.cmd import FlextCliCmd
    from flext_cli.services.core import FlextCliCore
    from flext_cli.services.output import FlextCliOutput
    from flext_cli.services.prompts import FlextCliPrompts
    from flext_cli.services.tables import FlextCliTables
    from flext_cli.settings import FlextCliSettings
    from flext_cli.typings import FlextCliTypes, FlextCliTypes as t
    from flext_cli.utilities import FlextCliUtilities, FlextCliUtilities as u

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
    "FlextCliOptionGroup": ("flext_cli.option_groups", "FlextCliOptionGroup"),
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
    "FlextCliOptionGroup",
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

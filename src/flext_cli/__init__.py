# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make codegen
#
"""Public exports for flext-cli with enforced framework isolation.

Expõe `FlextCli`, os serviços de domínio e utilidades respeitando a regra de
isolamento: Typer/Click permanecem em `cli.py`, enquanto Rich/Tabulate ficam em
`formatters.py` e `services/tables.py`. Utilize esses exports de alto nível
para preservar o comportamento suportado pelo projeto.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import cleanup_submodule_namespace, lazy_getattr

if TYPE_CHECKING:
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
    from flext_cli.api import FlextCli
    from flext_cli.app_base import FlextCliAppBase
    from flext_cli.base import FlextCliServiceBase, s
    from flext_cli.cli import FlextCliCli, Typer, UsageError
    from flext_cli.cli_params import FlextCliCommonParams
    from flext_cli.command_builder import FlextCliCommandBuilder
    from flext_cli.commands import (
        FlextCliCommandEntryModel,
        FlextCliCommandGroup,
        FlextCliCommands,
    )
    from flext_cli.constants import FlextCliConstants, c
    from flext_cli.debug import FlextCliDebug
    from flext_cli.file_tools import FlextCliFileTools
    from flext_cli.formatters import FlextCliFormatters
    from flext_cli.middleware import (
        FlextCliLoggingMiddleware,
        FlextCliMiddleware,
        FlextCliRetryMiddleware,
        FlextCliValidationMiddleware,
    )
    from flext_cli.mixins import FlextCliMixins, x
    from flext_cli.option_groups import FlextCliOptionGroup
    from flext_cli.protocols import FlextCliProtocols, p
    from flext_cli.services.cmd import FlextCliCmd
    from flext_cli.services.core import FlextCliCore
    from flext_cli.services.prompts import FlextCliPrompts
    from flext_cli.services.tables import FlextCliTables
    from flext_cli.settings import FlextCliSettings, logger
    from flext_cli.typings import FlextCliTypes, t
    from flext_cli.utilities import FlextCliUtilities, u

# Lazy import mapping: export_name -> (module_path, attr_name)
_LAZY_IMPORTS: dict[str, tuple[str, str]] = {
    "FlextCli": ("flext_cli.api", "FlextCli"),
    "FlextCliAppBase": ("flext_cli.app_base", "FlextCliAppBase"),
    "FlextCliCli": ("flext_cli.cli", "FlextCliCli"),
    "FlextCliCmd": ("flext_cli.services.cmd", "FlextCliCmd"),
    "FlextCliCommandBuilder": ("flext_cli.command_builder", "FlextCliCommandBuilder"),
    "FlextCliCommandEntryModel": ("flext_cli.commands", "FlextCliCommandEntryModel"),
    "FlextCliCommandGroup": ("flext_cli.commands", "FlextCliCommandGroup"),
    "FlextCliCommands": ("flext_cli.commands", "FlextCliCommands"),
    "FlextCliCommonParams": ("flext_cli.cli_params", "FlextCliCommonParams"),
    "FlextCliConstants": ("flext_cli.constants", "FlextCliConstants"),
    "FlextCliCore": ("flext_cli.services.core", "FlextCliCore"),
    "FlextCliDebug": ("flext_cli.debug", "FlextCliDebug"),
    "FlextCliFileTools": ("flext_cli.file_tools", "FlextCliFileTools"),
    "FlextCliFormatters": ("flext_cli.formatters", "FlextCliFormatters"),
    "FlextCliLoggingMiddleware": ("flext_cli.middleware", "FlextCliLoggingMiddleware"),
    "FlextCliMiddleware": ("flext_cli.middleware", "FlextCliMiddleware"),
    "FlextCliMixins": ("flext_cli.mixins", "FlextCliMixins"),
    "FlextCliOptionGroup": ("flext_cli.option_groups", "FlextCliOptionGroup"),
    "FlextCliPrompts": ("flext_cli.services.prompts", "FlextCliPrompts"),
    "FlextCliProtocols": ("flext_cli.protocols", "FlextCliProtocols"),
    "FlextCliRetryMiddleware": ("flext_cli.middleware", "FlextCliRetryMiddleware"),
    "FlextCliServiceBase": ("flext_cli.base", "FlextCliServiceBase"),
    "FlextCliSettings": ("flext_cli.settings", "FlextCliSettings"),
    "FlextCliTables": ("flext_cli.services.tables", "FlextCliTables"),
    "FlextCliTypes": ("flext_cli.typings", "FlextCliTypes"),
    "FlextCliUtilities": ("flext_cli.utilities", "FlextCliUtilities"),
    "FlextCliValidationMiddleware": (
        "flext_cli.middleware",
        "FlextCliValidationMiddleware",
    ),
    "Typer": ("flext_cli.cli", "Typer"),
    "UsageError": ("flext_cli.cli", "UsageError"),
    "__all__": ("flext_cli.__version__", "__all__"),
    "__author__": ("flext_cli.__version__", "__author__"),
    "__author_email__": ("flext_cli.__version__", "__author_email__"),
    "__description__": ("flext_cli.__version__", "__description__"),
    "__license__": ("flext_cli.__version__", "__license__"),
    "__title__": ("flext_cli.__version__", "__title__"),
    "__url__": ("flext_cli.__version__", "__url__"),
    "__version__": ("flext_cli.__version__", "__version__"),
    "__version_info__": ("flext_cli.__version__", "__version_info__"),
    "c": ("flext_cli.constants", "c"),
    "logger": ("flext_cli.settings", "logger"),
    "p": ("flext_cli.protocols", "p"),
    "s": ("flext_cli.base", "s"),
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
    "FlextCliCommandEntryModel",
    "FlextCliCommandGroup",
    "FlextCliCommands",
    "FlextCliCommonParams",
    "FlextCliConstants",
    "FlextCliCore",
    "FlextCliDebug",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliLoggingMiddleware",
    "FlextCliMiddleware",
    "FlextCliMixins",
    "FlextCliOptionGroup",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliRetryMiddleware",
    "FlextCliServiceBase",
    "FlextCliSettings",
    "FlextCliTables",
    "FlextCliTypes",
    "FlextCliUtilities",
    "FlextCliValidationMiddleware",
    "Typer",
    "UsageError",
    "__all__",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "c",
    "logger",
    "p",
    "s",
    "t",
    "u",
    "x",
]


def __getattr__(name: str) -> t.ModuleExport:
    """Lazy-load module attributes on first access (PEP 562)."""
    return lazy_getattr(name, _LAZY_IMPORTS, globals(), __name__)


def __dir__() -> list[str]:
    """Return list of available attributes for dir() and autocomplete."""
    return sorted(__all__)


cleanup_submodule_namespace(__name__, _LAZY_IMPORTS)

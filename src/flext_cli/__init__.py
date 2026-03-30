# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext cli package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

from flext_cli.__version__ import (
    __author__ as __author__,
    __author_email__ as __author_email__,
    __description__ as __description__,
    __license__ as __license__,
    __title__ as __title__,
    __url__ as __url__,
    __version__ as __version__,
    __version_info__ as __version_info__,
)

if TYPE_CHECKING:
    from flext_cli import (
        _models as _models,
        api as api,
        base as base,
        constants as constants,
        models as models,
        protocols as protocols,
        services as services,
        settings as settings,
        typings as typings,
        utilities as utilities,
    )
    from flext_cli._models.base import FlextCliModelsBase as FlextCliModelsBase
    from flext_cli.api import FlextCli as FlextCli, cli as cli
    from flext_cli.base import FlextCliServiceBase as FlextCliServiceBase, s as s
    from flext_cli.constants import (
        FlextCliConstants as FlextCliConstants,
        FlextCliConstants as c,
    )
    from flext_cli.models import FlextCliModels as FlextCliModels, FlextCliModels as m
    from flext_cli.protocols import (
        FlextCliProtocols as FlextCliProtocols,
        FlextCliProtocols as p,
    )
    from flext_cli.services import (
        auth as auth,
        cli_params as cli_params,
        cmd as cmd,
        commands as commands,
        file_tools as file_tools,
        formatters as formatters,
        output as output,
        prompts as prompts,
        tables as tables,
    )
    from flext_cli.services.auth import FlextCliAuth as FlextCliAuth
    from flext_cli.services.cli import FlextCliCli as FlextCliCli
    from flext_cli.services.cli_params import (
        FlextCliCommonParams as FlextCliCommonParams,
    )
    from flext_cli.services.cmd import FlextCliCmd as FlextCliCmd
    from flext_cli.services.commands import FlextCliCommands as FlextCliCommands
    from flext_cli.services.file_tools import FlextCliFileTools as FlextCliFileTools
    from flext_cli.services.formatters import FlextCliFormatters as FlextCliFormatters
    from flext_cli.services.output import FlextCliOutput as FlextCliOutput
    from flext_cli.services.prompts import FlextCliPrompts as FlextCliPrompts
    from flext_cli.services.tables import FlextCliTables as FlextCliTables
    from flext_cli.settings import (
        FlextCliSettings as FlextCliSettings,
        logger as logger,
    )
    from flext_cli.typings import FlextCliTypes as FlextCliTypes, FlextCliTypes as t
    from flext_cli.utilities import (
        FlextCliUtilities as FlextCliUtilities,
        FlextCliUtilities as u,
    )

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "FlextCli": ["flext_cli.api", "FlextCli"],
    "FlextCliAuth": ["flext_cli.services.auth", "FlextCliAuth"],
    "FlextCliCli": ["flext_cli.services.cli", "FlextCliCli"],
    "FlextCliCmd": ["flext_cli.services.cmd", "FlextCliCmd"],
    "FlextCliCommands": ["flext_cli.services.commands", "FlextCliCommands"],
    "FlextCliCommonParams": ["flext_cli.services.cli_params", "FlextCliCommonParams"],
    "FlextCliConstants": ["flext_cli.constants", "FlextCliConstants"],
    "FlextCliFileTools": ["flext_cli.services.file_tools", "FlextCliFileTools"],
    "FlextCliFormatters": ["flext_cli.services.formatters", "FlextCliFormatters"],
    "FlextCliModels": ["flext_cli.models", "FlextCliModels"],
    "FlextCliModelsBase": ["flext_cli._models.base", "FlextCliModelsBase"],
    "FlextCliOutput": ["flext_cli.services.output", "FlextCliOutput"],
    "FlextCliPrompts": ["flext_cli.services.prompts", "FlextCliPrompts"],
    "FlextCliProtocols": ["flext_cli.protocols", "FlextCliProtocols"],
    "FlextCliServiceBase": ["flext_cli.base", "FlextCliServiceBase"],
    "FlextCliSettings": ["flext_cli.settings", "FlextCliSettings"],
    "FlextCliTables": ["flext_cli.services.tables", "FlextCliTables"],
    "FlextCliTypes": ["flext_cli.typings", "FlextCliTypes"],
    "FlextCliUtilities": ["flext_cli.utilities", "FlextCliUtilities"],
    "_models": ["flext_cli._models", ""],
    "api": ["flext_cli.api", ""],
    "auth": ["flext_cli.services.auth", ""],
    "base": ["flext_cli.base", ""],
    "c": ["flext_cli.constants", "FlextCliConstants"],
    "cli": ["flext_cli.api", "cli"],
    "cli_params": ["flext_cli.services.cli_params", ""],
    "cmd": ["flext_cli.services.cmd", ""],
    "commands": ["flext_cli.services.commands", ""],
    "constants": ["flext_cli.constants", ""],
    "d": ["flext_core", "d"],
    "e": ["flext_core", "e"],
    "file_tools": ["flext_cli.services.file_tools", ""],
    "formatters": ["flext_cli.services.formatters", ""],
    "h": ["flext_core", "h"],
    "logger": ["flext_cli.settings", "logger"],
    "m": ["flext_cli.models", "FlextCliModels"],
    "models": ["flext_cli.models", ""],
    "output": ["flext_cli.services.output", ""],
    "p": ["flext_cli.protocols", "FlextCliProtocols"],
    "prompts": ["flext_cli.services.prompts", ""],
    "protocols": ["flext_cli.protocols", ""],
    "r": ["flext_core", "r"],
    "s": ["flext_cli.base", "s"],
    "services": ["flext_cli.services", ""],
    "settings": ["flext_cli.settings", ""],
    "t": ["flext_cli.typings", "FlextCliTypes"],
    "tables": ["flext_cli.services.tables", ""],
    "typings": ["flext_cli.typings", ""],
    "u": ["flext_cli.utilities", "FlextCliUtilities"],
    "utilities": ["flext_cli.utilities", ""],
    "x": ["flext_core", "x"],
}

_EXPORTS: Sequence[str] = [
    "FlextCli",
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommands",
    "FlextCliCommonParams",
    "FlextCliConstants",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliModels",
    "FlextCliModelsBase",
    "FlextCliOutput",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliServiceBase",
    "FlextCliSettings",
    "FlextCliTables",
    "FlextCliTypes",
    "FlextCliUtilities",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "_models",
    "api",
    "auth",
    "base",
    "c",
    "cli",
    "cli_params",
    "cmd",
    "commands",
    "constants",
    "d",
    "e",
    "file_tools",
    "formatters",
    "h",
    "logger",
    "m",
    "models",
    "output",
    "p",
    "prompts",
    "protocols",
    "r",
    "s",
    "services",
    "settings",
    "t",
    "tables",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)

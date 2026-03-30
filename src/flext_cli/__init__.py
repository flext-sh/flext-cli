# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext cli package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

from flext_cli.__version__ import (
    __author__,
    __author_email__,
    __description__,
    __license__,
    __title__,
    __url__,
    __version__,
    __version_info__,
)

if TYPE_CHECKING:
    from flext_core import *

    from flext_cli import (
        _models,
        api,
        base,
        constants,
        models,
        protocols,
        services,
        settings,
        typings,
        utilities,
    )
    from flext_cli._models.base import *
    from flext_cli.api import *
    from flext_cli.base import *
    from flext_cli.constants import *
    from flext_cli.models import *
    from flext_cli.protocols import *
    from flext_cli.services import (
        auth,
        cli_params,
        cmd,
        commands,
        file_tools,
        formatters,
        output,
        prompts,
        tables,
    )
    from flext_cli.services.auth import *
    from flext_cli.services.cli import *
    from flext_cli.services.cli_params import *
    from flext_cli.services.cmd import *
    from flext_cli.services.commands import *
    from flext_cli.services.file_tools import *
    from flext_cli.services.formatters import *
    from flext_cli.services.output import *
    from flext_cli.services.prompts import *
    from flext_cli.services.tables import *
    from flext_cli.settings import *
    from flext_cli.typings import *
    from flext_cli.utilities import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextCli": "flext_cli.api",
    "FlextCliAuth": "flext_cli.services.auth",
    "FlextCliCli": "flext_cli.services.cli",
    "FlextCliCmd": "flext_cli.services.cmd",
    "FlextCliCommands": "flext_cli.services.commands",
    "FlextCliCommonParams": "flext_cli.services.cli_params",
    "FlextCliConstants": "flext_cli.constants",
    "FlextCliFileTools": "flext_cli.services.file_tools",
    "FlextCliFormatters": "flext_cli.services.formatters",
    "FlextCliModels": "flext_cli.models",
    "FlextCliModelsBase": "flext_cli._models.base",
    "FlextCliOutput": "flext_cli.services.output",
    "FlextCliPrompts": "flext_cli.services.prompts",
    "FlextCliProtocols": "flext_cli.protocols",
    "FlextCliServiceBase": "flext_cli.base",
    "FlextCliSettings": "flext_cli.settings",
    "FlextCliTables": "flext_cli.services.tables",
    "FlextCliTypes": "flext_cli.typings",
    "FlextCliUtilities": "flext_cli.utilities",
    "_models": "flext_cli._models",
    "api": "flext_cli.api",
    "auth": "flext_cli.services.auth",
    "base": "flext_cli.base",
    "c": ["flext_cli.constants", "FlextCliConstants"],
    "cli": "flext_cli.api",
    "cli_params": "flext_cli.services.cli_params",
    "cmd": "flext_cli.services.cmd",
    "commands": "flext_cli.services.commands",
    "constants": "flext_cli.constants",
    "d": "flext_core",
    "e": "flext_core",
    "file_tools": "flext_cli.services.file_tools",
    "formatters": "flext_cli.services.formatters",
    "h": "flext_core",
    "logger": "flext_cli.settings",
    "m": ["flext_cli.models", "FlextCliModels"],
    "models": "flext_cli.models",
    "output": "flext_cli.services.output",
    "p": ["flext_cli.protocols", "FlextCliProtocols"],
    "prompts": "flext_cli.services.prompts",
    "protocols": "flext_cli.protocols",
    "r": "flext_core",
    "s": "flext_cli.base",
    "services": "flext_cli.services",
    "settings": "flext_cli.settings",
    "t": ["flext_cli.typings", "FlextCliTypes"],
    "tables": "flext_cli.services.tables",
    "typings": "flext_cli.typings",
    "u": ["flext_cli.utilities", "FlextCliUtilities"],
    "utilities": "flext_cli.utilities",
    "x": "flext_core",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))

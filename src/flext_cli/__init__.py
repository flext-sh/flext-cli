# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext cli package."""

from __future__ import annotations

import typing as _t

from flext_cli.__version__ import *
from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    import flext_cli._models as _flext_cli__models
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

    _models = _flext_cli__models
    import flext_cli.api as _flext_cli_api
    from flext_cli._models.base import FlextCliModelsBase

    api = _flext_cli_api
    import flext_cli.base as _flext_cli_base
    from flext_cli.api import FlextCli, cli

    base = _flext_cli_base
    import flext_cli.constants as _flext_cli_constants
    from flext_cli.base import FlextCliServiceBase, FlextCliServiceBase as s

    constants = _flext_cli_constants
    import flext_cli.models as _flext_cli_models
    from flext_cli.constants import FlextCliConstants, FlextCliConstants as c

    models = _flext_cli_models
    import flext_cli.protocols as _flext_cli_protocols
    from flext_cli.models import FlextCliModels, FlextCliModels as m

    protocols = _flext_cli_protocols
    import flext_cli.services as _flext_cli_services
    from flext_cli.protocols import FlextCliProtocols, FlextCliProtocols as p

    services = _flext_cli_services
    import flext_cli.services.auth as _flext_cli_services_auth

    auth = _flext_cli_services_auth
    import flext_cli.services.cli_params as _flext_cli_services_cli_params
    from flext_cli.services.auth import FlextCliAuth
    from flext_cli.services.cli import FlextCliCli

    cli_params = _flext_cli_services_cli_params
    import flext_cli.services.cmd as _flext_cli_services_cmd
    from flext_cli.services.cli_params import FlextCliCommonParams

    cmd = _flext_cli_services_cmd
    import flext_cli.services.commands as _flext_cli_services_commands
    from flext_cli.services.cmd import FlextCliCmd

    commands = _flext_cli_services_commands
    import flext_cli.services.file_tools as _flext_cli_services_file_tools
    from flext_cli.services.commands import FlextCliCommands

    file_tools = _flext_cli_services_file_tools
    import flext_cli.services.formatters as _flext_cli_services_formatters
    from flext_cli.services.file_tools import FlextCliFileTools

    formatters = _flext_cli_services_formatters
    import flext_cli.services.output as _flext_cli_services_output
    from flext_cli.services.formatters import FlextCliFormatters

    output = _flext_cli_services_output
    import flext_cli.services.prompts as _flext_cli_services_prompts
    from flext_cli.services.output import FlextCliOutput

    prompts = _flext_cli_services_prompts
    import flext_cli.services.tables as _flext_cli_services_tables
    from flext_cli.services.prompts import FlextCliPrompts

    tables = _flext_cli_services_tables
    import flext_cli.settings as _flext_cli_settings
    from flext_cli.services.tables import FlextCliTables

    settings = _flext_cli_settings
    import flext_cli.typings as _flext_cli_typings
    from flext_cli.settings import FlextCliSettings, logger

    typings = _flext_cli_typings
    import flext_cli.utilities as _flext_cli_utilities
    from flext_cli.typings import FlextCliTypes, FlextCliTypes as t

    utilities = _flext_cli_utilities
    from flext_cli.utilities import FlextCliUtilities, FlextCliUtilities as u
    from flext_core.decorators import FlextDecorators as d
    from flext_core.exceptions import FlextExceptions as e
    from flext_core.handlers import FlextHandlers as h
    from flext_core.mixins import FlextMixins as x
    from flext_core.result import FlextResult as r
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "flext_cli._models",
        "flext_cli.services",
    ),
    {
        "FlextCli": "flext_cli.api",
        "FlextCliConstants": "flext_cli.constants",
        "FlextCliModels": "flext_cli.models",
        "FlextCliProtocols": "flext_cli.protocols",
        "FlextCliServiceBase": "flext_cli.base",
        "FlextCliSettings": "flext_cli.settings",
        "FlextCliTypes": "flext_cli.typings",
        "FlextCliUtilities": "flext_cli.utilities",
        "__author__": "flext_cli.__version__",
        "__author_email__": "flext_cli.__version__",
        "__description__": "flext_cli.__version__",
        "__license__": "flext_cli.__version__",
        "__title__": "flext_cli.__version__",
        "__url__": "flext_cli.__version__",
        "__version__": "flext_cli.__version__",
        "__version_info__": "flext_cli.__version__",
        "_models": "flext_cli._models",
        "api": "flext_cli.api",
        "base": "flext_cli.base",
        "c": ("flext_cli.constants", "FlextCliConstants"),
        "cli": "flext_cli.api",
        "constants": "flext_cli.constants",
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "logger": "flext_cli.settings",
        "m": ("flext_cli.models", "FlextCliModels"),
        "models": "flext_cli.models",
        "p": ("flext_cli.protocols", "FlextCliProtocols"),
        "protocols": "flext_cli.protocols",
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_cli.base", "FlextCliServiceBase"),
        "services": "flext_cli.services",
        "settings": "flext_cli.settings",
        "t": ("flext_cli.typings", "FlextCliTypes"),
        "typings": "flext_cli.typings",
        "u": ("flext_cli.utilities", "FlextCliUtilities"),
        "utilities": "flext_cli.utilities",
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)

__all__ = [
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


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

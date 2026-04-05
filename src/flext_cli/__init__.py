# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext cli package."""

from __future__ import annotations

import typing as _t

from flext_cli.__version__ import *
from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    import flext_cli._constants as _flext_cli__constants

    _constants = _flext_cli__constants
    import flext_cli._models as _flext_cli__models
    from flext_cli._constants import (
        FlextCliConstantsBase,
        FlextCliConstantsConfig,
        FlextCliConstantsEnums,
        config,
        enums,
    )

    _models = _flext_cli__models
    import flext_cli._protocols as _flext_cli__protocols
    from flext_cli._models import FlextCliModelsBase

    _protocols = _flext_cli__protocols
    import flext_cli._typings as _flext_cli__typings
    from flext_cli._protocols import (
        FlextCliProtocolsBase,
        FlextCliProtocolsDomain,
        domain,
    )

    _typings = _flext_cli__typings
    import flext_cli._utilities as _flext_cli__utilities
    from flext_cli._typings import FlextCliTypesBase, FlextCliTypesDomain

    _utilities = _flext_cli__utilities
    import flext_cli.api as _flext_cli_api
    from flext_cli._utilities import (
        FlextCliUtilitiesBase,
        FlextCliUtilitiesCliModelConverter,
        FlextCliUtilitiesConfiguration,
        FlextCliUtilitiesConversion,
        FlextCliUtilitiesJson,
        FlextCliUtilitiesMatching,
        FlextCliUtilitiesModelCommandBuilder,
        FlextCliUtilitiesModelCommands,
        FlextCliUtilitiesOptionBuilder,
        FlextCliUtilitiesOptions,
        FlextCliUtilitiesToml,
        FlextCliUtilitiesValidation,
        FlextCliUtilitiesYaml,
        configuration,
        conversion,
        json,
        matching,
        model_commands,
        options,
        toml,
        validation,
        yaml,
    )

    api = _flext_cli_api
    import flext_cli.base as _flext_cli_base
    from flext_cli.api import FlextCli, cli

    base = _flext_cli_base
    import flext_cli.constants as _flext_cli_constants
    from flext_cli.base import FlextCliServiceBase, s

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
    import flext_cli.settings as _flext_cli_settings
    from flext_cli.services import (
        FlextCliAuth,
        FlextCliCli,
        FlextCliCmd,
        FlextCliCommands,
        FlextCliCommonParams,
        FlextCliFileTools,
        FlextCliFormatters,
        FlextCliOutput,
        FlextCliPrompts,
        FlextCliTables,
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
        "flext_cli._constants",
        "flext_cli._models",
        "flext_cli._protocols",
        "flext_cli._typings",
        "flext_cli._utilities",
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
        "_constants": "flext_cli._constants",
        "_models": "flext_cli._models",
        "_protocols": "flext_cli._protocols",
        "_typings": "flext_cli._typings",
        "_utilities": "flext_cli._utilities",
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
        "s": "flext_cli.base",
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
    "FlextCliConstantsBase",
    "FlextCliConstantsConfig",
    "FlextCliConstantsEnums",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliModels",
    "FlextCliModelsBase",
    "FlextCliOutput",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliProtocolsBase",
    "FlextCliProtocolsDomain",
    "FlextCliServiceBase",
    "FlextCliSettings",
    "FlextCliTables",
    "FlextCliTypes",
    "FlextCliTypesBase",
    "FlextCliTypesDomain",
    "FlextCliUtilities",
    "FlextCliUtilitiesBase",
    "FlextCliUtilitiesCliModelConverter",
    "FlextCliUtilitiesConfiguration",
    "FlextCliUtilitiesConversion",
    "FlextCliUtilitiesJson",
    "FlextCliUtilitiesMatching",
    "FlextCliUtilitiesModelCommandBuilder",
    "FlextCliUtilitiesModelCommands",
    "FlextCliUtilitiesOptionBuilder",
    "FlextCliUtilitiesOptions",
    "FlextCliUtilitiesToml",
    "FlextCliUtilitiesValidation",
    "FlextCliUtilitiesYaml",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "_constants",
    "_models",
    "_protocols",
    "_typings",
    "_utilities",
    "api",
    "auth",
    "base",
    "c",
    "cli",
    "cli_params",
    "cmd",
    "commands",
    "config",
    "configuration",
    "constants",
    "conversion",
    "d",
    "domain",
    "e",
    "enums",
    "file_tools",
    "formatters",
    "h",
    "json",
    "logger",
    "m",
    "matching",
    "model_commands",
    "models",
    "options",
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
    "toml",
    "typings",
    "u",
    "utilities",
    "validation",
    "x",
    "yaml",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

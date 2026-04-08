# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Flext cli package."""

from __future__ import annotations

import typing as _t

from flext_cli.__version__ import *
from flext_core.lazy import install_lazy_exports, merge_lazy_imports

if _t.TYPE_CHECKING:
    from flext_cli._constants.base import FlextCliConstantsBase
    from flext_cli._constants.config import FlextCliConstantsConfig
    from flext_cli._constants.enums import FlextCliConstantsEnums
    from flext_cli._constants.pipeline import FlextCliConstantsPipeline
    from flext_cli._models.base import FlextCliModelsBase
    from flext_cli._models.pipeline import FlextCliModelsPipeline
    from flext_cli._protocols.base import FlextCliProtocolsBase
    from flext_cli._protocols.domain import FlextCliProtocolsDomain
    from flext_cli._protocols.pipeline import FlextCliProtocolsPipeline
    from flext_cli._typings.base import FlextCliTypesBase
    from flext_cli._typings.domain import FlextCliTypesDomain
    from flext_cli._typings.pipeline import FlextCliTypesPipeline
    from flext_cli._utilities.base import FlextCliUtilitiesBase
    from flext_cli._utilities.configuration import FlextCliUtilitiesConfiguration
    from flext_cli._utilities.conversion import (
        FlextCliUtilitiesCliModelConverter,
        FlextCliUtilitiesConversion,
    )
    from flext_cli._utilities.files import FlextCliUtilitiesFiles
    from flext_cli._utilities.json import FlextCliUtilitiesJson
    from flext_cli._utilities.matching import FlextCliUtilitiesMatching
    from flext_cli._utilities.model_commands import (
        FlextCliUtilitiesModelCommandBuilder,
        FlextCliUtilitiesModelCommands,
    )
    from flext_cli._utilities.options import (
        FlextCliUtilitiesOptionBuilder,
        FlextCliUtilitiesOptions,
    )
    from flext_cli._utilities.pipeline import FlextCliUtilitiesPipeline
    from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime
    from flext_cli._utilities.toml import FlextCliUtilitiesToml
    from flext_cli._utilities.validation import FlextCliUtilitiesValidation
    from flext_cli._utilities.yaml import FlextCliUtilitiesYaml
    from flext_cli.api import FlextCli, cli
    from flext_cli.base import FlextCliServiceBase, s
    from flext_cli.constants import FlextCliConstants, FlextCliConstants as c
    from flext_cli.models import FlextCliModels, FlextCliModels as m
    from flext_cli.protocols import FlextCliProtocols, FlextCliProtocols as p
    from flext_cli.services.auth import FlextCliAuth
    from flext_cli.services.cli import FlextCliCli
    from flext_cli.services.cli_params import FlextCliCommonParams
    from flext_cli.services.cmd import FlextCliCmd
    from flext_cli.services.commands import FlextCliCommands
    from flext_cli.services.file_tools import FlextCliFileTools
    from flext_cli.services.formatters import FlextCliFormatters
    from flext_cli.services.output import FlextCliOutput
    from flext_cli.services.prompts import FlextCliPrompts
    from flext_cli.services.tables import FlextCliTables
    from flext_cli.settings import FlextCliSettings
    from flext_cli.typings import FlextCliTypes, FlextCliTypes as t
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
        "FlextCli": ("flext_cli.api", "FlextCli"),
        "FlextCliConstants": ("flext_cli.constants", "FlextCliConstants"),
        "FlextCliModels": ("flext_cli.models", "FlextCliModels"),
        "FlextCliProtocols": ("flext_cli.protocols", "FlextCliProtocols"),
        "FlextCliServiceBase": ("flext_cli.base", "FlextCliServiceBase"),
        "FlextCliSettings": ("flext_cli.settings", "FlextCliSettings"),
        "FlextCliTypes": ("flext_cli.typings", "FlextCliTypes"),
        "FlextCliUtilities": ("flext_cli.utilities", "FlextCliUtilities"),
        "__author__": ("flext_cli.__version__", "__author__"),
        "__author_email__": ("flext_cli.__version__", "__author_email__"),
        "__description__": ("flext_cli.__version__", "__description__"),
        "__license__": ("flext_cli.__version__", "__license__"),
        "__title__": ("flext_cli.__version__", "__title__"),
        "__url__": ("flext_cli.__version__", "__url__"),
        "__version__": ("flext_cli.__version__", "__version__"),
        "__version_info__": ("flext_cli.__version__", "__version_info__"),
        "c": ("flext_cli.constants", "FlextCliConstants"),
        "cli": ("flext_cli.api", "cli"),
        "d": ("flext_core.decorators", "FlextDecorators"),
        "e": ("flext_core.exceptions", "FlextExceptions"),
        "h": ("flext_core.handlers", "FlextHandlers"),
        "m": ("flext_cli.models", "FlextCliModels"),
        "p": ("flext_cli.protocols", "FlextCliProtocols"),
        "r": ("flext_core.result", "FlextResult"),
        "s": ("flext_cli.base", "s"),
        "t": ("flext_cli.typings", "FlextCliTypes"),
        "u": ("flext_cli.utilities", "FlextCliUtilities"),
        "x": ("flext_core.mixins", "FlextMixins"),
    },
)
_ = _LAZY_IMPORTS.pop("cleanup_submodule_namespace", None)
_ = _LAZY_IMPORTS.pop("install_lazy_exports", None)
_ = _LAZY_IMPORTS.pop("lazy_getattr", None)
_ = _LAZY_IMPORTS.pop("logger", None)
_ = _LAZY_IMPORTS.pop("merge_lazy_imports", None)
_ = _LAZY_IMPORTS.pop("output", None)
_ = _LAZY_IMPORTS.pop("output_reporting", None)

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
    "FlextCliConstantsPipeline",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliModels",
    "FlextCliModelsBase",
    "FlextCliModelsPipeline",
    "FlextCliOutput",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliProtocolsBase",
    "FlextCliProtocolsDomain",
    "FlextCliProtocolsPipeline",
    "FlextCliServiceBase",
    "FlextCliSettings",
    "FlextCliTables",
    "FlextCliTypes",
    "FlextCliTypesBase",
    "FlextCliTypesDomain",
    "FlextCliTypesPipeline",
    "FlextCliUtilities",
    "FlextCliUtilitiesBase",
    "FlextCliUtilitiesCliModelConverter",
    "FlextCliUtilitiesConfiguration",
    "FlextCliUtilitiesConversion",
    "FlextCliUtilitiesFiles",
    "FlextCliUtilitiesJson",
    "FlextCliUtilitiesMatching",
    "FlextCliUtilitiesModelCommandBuilder",
    "FlextCliUtilitiesModelCommands",
    "FlextCliUtilitiesOptionBuilder",
    "FlextCliUtilitiesOptions",
    "FlextCliUtilitiesPipeline",
    "FlextCliUtilitiesRuntime",
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
    "c",
    "cli",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "u",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

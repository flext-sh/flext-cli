# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli package."""

from __future__ import annotations

import typing as _t

from flext_cli.__version__ import *
from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext_cli._constants.base import FlextCliConstantsBase
    from flext_cli._constants.config import FlextCliConstantsSettings
    from flext_cli._constants.enums import FlextCliConstantsEnums
    from flext_cli._constants.errors import FlextCliConstantsErrors
    from flext_cli._constants.output import FlextCliConstantsOutput
    from flext_cli._constants.pipeline import FlextCliConstantsPipeline
    from flext_cli._models.base import FlextCliModelsBase
    from flext_cli._models.pipeline import FlextCliModelsPipeline
    from flext_cli._protocols.base import FlextCliProtocolsBase
    from flext_cli._protocols.domain import FlextCliProtocolsDomain
    from flext_cli._protocols.pipeline import FlextCliProtocolsPipeline
    from flext_cli._typings.base import FlextCliTypesBase
    from flext_cli._typings.domain import FlextCliTypesDomain
    from flext_cli._typings.pipeline import FlextCliTypesPipeline
    from flext_cli._utilities.auth import FlextCliUtilitiesAuth
    from flext_cli._utilities.base import FlextCliUtilitiesBase
    from flext_cli._utilities.cmd import FlextCliUtilitiesCmd
    from flext_cli._utilities.commands import FlextCliUtilitiesCommands
    from flext_cli._utilities.configuration import FlextCliUtilitiesConfiguration
    from flext_cli._utilities.conversion import (
        FlextCliUtilitiesCliModelConverter,
        FlextCliUtilitiesConversion,
    )
    from flext_cli._utilities.files import FlextCliUtilitiesFiles
    from flext_cli._utilities.formatters import FlextCliUtilitiesFormatters
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
    from flext_cli._utilities.output import FlextCliUtilitiesOutput
    from flext_cli._utilities.params import FlextCliUtilitiesParams
    from flext_cli._utilities.pipeline import FlextCliUtilitiesPipeline
    from flext_cli._utilities.prompts import FlextCliUtilitiesPrompts
    from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime
    from flext_cli._utilities.tables import FlextCliUtilitiesTables
    from flext_cli._utilities.toml import FlextCliUtilitiesToml
    from flext_cli._utilities.validation import FlextCliUtilitiesValidation
    from flext_cli._utilities.yaml import FlextCliUtilitiesYaml
    from flext_cli.api import FlextCli, cli
    from flext_cli.base import FlextCliServiceBase, s
    from flext_cli.constants import FlextCliConstants, c
    from flext_cli.models import FlextCliModels, m
    from flext_cli.protocols import FlextCliProtocols, p
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
    from flext_cli.typings import FlextCliTypes, t
    from flext_cli.utilities import FlextCliUtilities, u
    from flext_core import d, e, h, r, x
_LAZY_IMPORTS = merge_lazy_imports(
    (
        "._constants",
        "._models",
        "._protocols",
        "._typings",
        "._utilities",
        ".services",
    ),
    build_lazy_import_map(
        {
            ".__version__": (
                "__author__",
                "__author_email__",
                "__description__",
                "__license__",
                "__title__",
                "__url__",
                "__version__",
                "__version_info__",
            ),
            ".api": (
                "FlextCli",
                "cli",
            ),
            ".base": (
                "FlextCliServiceBase",
                "s",
            ),
            ".constants": (
                "FlextCliConstants",
                "c",
            ),
            ".models": (
                "FlextCliModels",
                "m",
            ),
            ".protocols": (
                "FlextCliProtocols",
                "p",
            ),
            ".settings": ("FlextCliSettings",),
            ".typings": (
                "FlextCliTypes",
                "t",
            ),
            ".utilities": (
                "FlextCliUtilities",
                "u",
            ),
            "flext_core": (
                "d",
                "e",
                "h",
                "r",
                "x",
            ),
        },
    ),
    exclude_names=(
        "cleanup_submodule_namespace",
        "install_lazy_exports",
        "lazy_getattr",
        "logger",
        "merge_lazy_imports",
        "output",
        "output_reporting",
    ),
    module_name=__name__,
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

__all__ = [
    "FlextCli",
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommands",
    "FlextCliCommonParams",
    "FlextCliConstants",
    "FlextCliConstantsBase",
    "FlextCliConstantsEnums",
    "FlextCliConstantsErrors",
    "FlextCliConstantsOutput",
    "FlextCliConstantsPipeline",
    "FlextCliConstantsSettings",
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
    "FlextCliUtilitiesAuth",
    "FlextCliUtilitiesBase",
    "FlextCliUtilitiesCliModelConverter",
    "FlextCliUtilitiesCmd",
    "FlextCliUtilitiesCommands",
    "FlextCliUtilitiesConfiguration",
    "FlextCliUtilitiesConversion",
    "FlextCliUtilitiesFiles",
    "FlextCliUtilitiesFormatters",
    "FlextCliUtilitiesJson",
    "FlextCliUtilitiesMatching",
    "FlextCliUtilitiesModelCommandBuilder",
    "FlextCliUtilitiesModelCommands",
    "FlextCliUtilitiesOptionBuilder",
    "FlextCliUtilitiesOptions",
    "FlextCliUtilitiesOutput",
    "FlextCliUtilitiesParams",
    "FlextCliUtilitiesPipeline",
    "FlextCliUtilitiesPrompts",
    "FlextCliUtilitiesRuntime",
    "FlextCliUtilitiesTables",
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

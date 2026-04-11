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
    from _constants.base import FlextCliConstantsBase
    from _constants.config import FlextCliConstantsSettings
    from _constants.enums import FlextCliConstantsEnums
    from _constants.pipeline import FlextCliConstantsPipeline
    from _models.base import FlextCliModelsBase
    from _models.pipeline import FlextCliModelsPipeline
    from _protocols.base import FlextCliProtocolsBase
    from _protocols.domain import FlextCliProtocolsDomain
    from _protocols.pipeline import FlextCliProtocolsPipeline
    from _typings.base import FlextCliTypesBase
    from _typings.domain import FlextCliTypesDomain
    from _typings.pipeline import FlextCliTypesPipeline
    from _utilities.base import FlextCliUtilitiesBase
    from _utilities.configuration import FlextCliUtilitiesConfiguration
    from _utilities.conversion import (
        FlextCliUtilitiesCliModelConverter,
        FlextCliUtilitiesConversion,
    )
    from _utilities.files import FlextCliUtilitiesFiles
    from _utilities.json import FlextCliUtilitiesJson
    from _utilities.matching import FlextCliUtilitiesMatching
    from _utilities.model_commands import (
        FlextCliUtilitiesModelCommandBuilder,
        FlextCliUtilitiesModelCommands,
    )
    from _utilities.options import (
        FlextCliUtilitiesOptionBuilder,
        FlextCliUtilitiesOptions,
    )
    from _utilities.pipeline import FlextCliUtilitiesPipeline
    from _utilities.runtime import FlextCliUtilitiesRuntime
    from _utilities.toml import FlextCliUtilitiesToml
    from _utilities.validation import FlextCliUtilitiesValidation
    from _utilities.yaml import FlextCliUtilitiesYaml

    from flext_cli.api import FlextCli, cli
    from flext_cli.auth import FlextCliAuth
    from flext_cli.base import FlextCliServiceBase, s
    from flext_cli.cli import FlextCliCli
    from flext_cli.cli_params import FlextCliCommonParams
    from flext_cli.cmd import FlextCliCmd
    from flext_cli.commands import FlextCliCommands
    from flext_cli.constants import FlextCliConstants, c
    from flext_cli.file_tools import FlextCliFileTools
    from flext_cli.formatters import FlextCliFormatters
    from flext_cli.models import FlextCliModels, m
    from flext_cli.output import FlextCliOutput
    from flext_cli.prompts import FlextCliPrompts
    from flext_cli.protocols import FlextCliProtocols, p
    from flext_cli.settings import FlextCliSettings
    from flext_cli.tables import FlextCliTables
    from flext_cli.typings import FlextCliTypes, t
    from flext_cli.utilities import FlextCliUtilities, u
    from flext_core.decorators import d
    from flext_core.exceptions import e
    from flext_core.handlers import h
    from flext_core.mixins import x
    from flext_core.result import r
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
            ".auth": ("FlextCliAuth",),
            ".base": (
                "FlextCliServiceBase",
                "s",
            ),
            ".cli": ("FlextCliCli",),
            ".cli_params": ("FlextCliCommonParams",),
            ".cmd": ("FlextCliCmd",),
            ".commands": ("FlextCliCommands",),
            ".constants": (
                "FlextCliConstants",
                "c",
            ),
            ".file_tools": ("FlextCliFileTools",),
            ".formatters": ("FlextCliFormatters",),
            ".models": (
                "FlextCliModels",
                "m",
            ),
            ".output": ("FlextCliOutput",),
            ".prompts": ("FlextCliPrompts",),
            ".protocols": (
                "FlextCliProtocols",
                "p",
            ),
            ".settings": ("FlextCliSettings",),
            ".tables": ("FlextCliTables",),
            ".typings": (
                "FlextCliTypes",
                "t",
            ),
            ".utilities": (
                "FlextCliUtilities",
                "u",
            ),
            "_constants.base": ("FlextCliConstantsBase",),
            "_constants.config": ("FlextCliConstantsSettings",),
            "_constants.enums": ("FlextCliConstantsEnums",),
            "_constants.pipeline": ("FlextCliConstantsPipeline",),
            "_models.base": ("FlextCliModelsBase",),
            "_models.pipeline": ("FlextCliModelsPipeline",),
            "_protocols.base": ("FlextCliProtocolsBase",),
            "_protocols.domain": ("FlextCliProtocolsDomain",),
            "_protocols.pipeline": ("FlextCliProtocolsPipeline",),
            "_typings.base": ("FlextCliTypesBase",),
            "_typings.domain": ("FlextCliTypesDomain",),
            "_typings.pipeline": ("FlextCliTypesPipeline",),
            "_utilities.base": ("FlextCliUtilitiesBase",),
            "_utilities.configuration": ("FlextCliUtilitiesConfiguration",),
            "_utilities.conversion": (
                "FlextCliUtilitiesCliModelConverter",
                "FlextCliUtilitiesConversion",
            ),
            "_utilities.files": ("FlextCliUtilitiesFiles",),
            "_utilities.json": ("FlextCliUtilitiesJson",),
            "_utilities.matching": ("FlextCliUtilitiesMatching",),
            "_utilities.model_commands": (
                "FlextCliUtilitiesModelCommandBuilder",
                "FlextCliUtilitiesModelCommands",
            ),
            "_utilities.options": (
                "FlextCliUtilitiesOptionBuilder",
                "FlextCliUtilitiesOptions",
            ),
            "_utilities.pipeline": ("FlextCliUtilitiesPipeline",),
            "_utilities.runtime": ("FlextCliUtilitiesRuntime",),
            "_utilities.toml": ("FlextCliUtilitiesToml",),
            "_utilities.validation": ("FlextCliUtilitiesValidation",),
            "_utilities.yaml": ("FlextCliUtilitiesYaml",),
            "flext_core.decorators": ("d",),
            "flext_core.exceptions": ("e",),
            "flext_core.handlers": ("h",),
            "flext_core.mixins": ("x",),
            "flext_core.result": ("r",),
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

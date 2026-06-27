# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli package."""

from __future__ import annotations

import typing as _t

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
from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if _t.TYPE_CHECKING:
    from flext_cli._constants.base import FlextCliConstantsBase as FlextCliConstantsBase
    from flext_cli._constants.enums import (
        FlextCliConstantsEnums as FlextCliConstantsEnums,
    )
    from flext_cli._constants.errors import (
        FlextCliConstantsErrors as FlextCliConstantsErrors,
    )
    from flext_cli._constants.exceptions import (
        FlextCliConstantsExceptions as FlextCliConstantsExceptions,
    )
    from flext_cli._constants.files import (
        FlextCliConstantsFiles as FlextCliConstantsFiles,
    )
    from flext_cli._constants.output import (
        FlextCliConstantsOutput as FlextCliConstantsOutput,
    )
    from flext_cli._constants.pipeline import (
        FlextCliConstantsPipeline as FlextCliConstantsPipeline,
    )
    from flext_cli._constants.settings import (
        FlextCliConstantsSettings as FlextCliConstantsSettings,
    )
    from flext_cli._models.base import FlextCliModelsBase as FlextCliModelsBase
    from flext_cli._models.pipeline import (
        FlextCliModelsPipeline as FlextCliModelsPipeline,
    )
    from flext_cli._models.rules import FlextCliModelsRules as FlextCliModelsRules
    from flext_cli._protocols.base import FlextCliProtocolsBase as FlextCliProtocolsBase
    from flext_cli._protocols.domain import (
        FlextCliProtocolsDomain as FlextCliProtocolsDomain,
    )
    from flext_cli._protocols.pipeline import (
        FlextCliProtocolsPipeline as FlextCliProtocolsPipeline,
    )
    from flext_cli._typings.base import FlextCliTypesBase as FlextCliTypesBase
    from flext_cli._typings.domain import FlextCliTypesDomain as FlextCliTypesDomain
    from flext_cli._typings.pipeline import (
        FlextCliTypesPipeline as FlextCliTypesPipeline,
    )
    from flext_cli._utilities.auth import FlextCliUtilitiesAuth as FlextCliUtilitiesAuth
    from flext_cli._utilities.cmd import FlextCliUtilitiesCmd as FlextCliUtilitiesCmd
    from flext_cli._utilities.commands import (
        FlextCliUtilitiesCommands as FlextCliUtilitiesCommands,
    )
    from flext_cli._utilities.conversion import (
        FlextCliUtilitiesConversion as FlextCliUtilitiesConversion,
    )
    from flext_cli._utilities.files import (
        FlextCliUtilitiesFiles as FlextCliUtilitiesFiles,
    )
    from flext_cli._utilities.formatters import (
        FlextCliUtilitiesFormatters as FlextCliUtilitiesFormatters,
    )
    from flext_cli._utilities.json import FlextCliUtilitiesJson as FlextCliUtilitiesJson
    from flext_cli._utilities.matching import (
        FlextCliUtilitiesMatching as FlextCliUtilitiesMatching,
    )
    from flext_cli._utilities.model_commands import (
        FlextCliUtilitiesModelCommandBuilder as FlextCliUtilitiesModelCommandBuilder,
        FlextCliUtilitiesModelCommands as FlextCliUtilitiesModelCommands,
    )
    from flext_cli._utilities.options import (
        FlextCliUtilitiesOptionBuilder as FlextCliUtilitiesOptionBuilder,
        FlextCliUtilitiesOptions as FlextCliUtilitiesOptions,
    )
    from flext_cli._utilities.output import (
        FlextCliUtilitiesOutput as FlextCliUtilitiesOutput,
    )
    from flext_cli._utilities.params import (
        FlextCliUtilitiesParams as FlextCliUtilitiesParams,
    )
    from flext_cli._utilities.pipeline import (
        FlextCliUtilitiesPipeline as FlextCliUtilitiesPipeline,
    )
    from flext_cli._utilities.prompts import (
        FlextCliUtilitiesPrompts as FlextCliUtilitiesPrompts,
    )
    from flext_cli._utilities.rules import (
        FlextCliUtilitiesRules as FlextCliUtilitiesRules,
    )
    from flext_cli._utilities.runtime import (
        FlextCliUtilitiesRuntime as FlextCliUtilitiesRuntime,
    )
    from flext_cli._utilities.settings import (
        FlextCliUtilitiesSettings as FlextCliUtilitiesSettings,
    )
    from flext_cli._utilities.tables import (
        FlextCliUtilitiesTables as FlextCliUtilitiesTables,
    )
    from flext_cli._utilities.toml import FlextCliUtilitiesToml as FlextCliUtilitiesToml
    from flext_cli._utilities.validation import (
        FlextCliUtilitiesValidation as FlextCliUtilitiesValidation,
    )
    from flext_cli._utilities.yaml import FlextCliUtilitiesYaml as FlextCliUtilitiesYaml
    from flext_cli.api import FlextCli as FlextCli, cli as cli
    from flext_cli.base import FlextCliServiceBase as FlextCliServiceBase, s as s
    from flext_cli.constants import FlextCliConstants as FlextCliConstants, c as c
    from flext_cli.models import FlextCliModels as FlextCliModels, m as m
    from flext_cli.protocols import FlextCliProtocols as FlextCliProtocols, p as p
    from flext_cli.services.auth import FlextCliAuth as FlextCliAuth
    from flext_cli.services.cli import FlextCliCli as FlextCliCli
    from flext_cli.services.cli_params import (
        FlextCliCommonParams as FlextCliCommonParams,
    )
    from flext_cli.services.cmd import FlextCliCmd as FlextCliCmd
    from flext_cli.services.file_tools import FlextCliFileTools as FlextCliFileTools
    from flext_cli.services.formatters import FlextCliFormatters as FlextCliFormatters
    from flext_cli.services.output import FlextCliOutput as FlextCliOutput
    from flext_cli.services.pipeline import FlextCliPipeline as FlextCliPipeline
    from flext_cli.services.prompts import FlextCliPrompts as FlextCliPrompts
    from flext_cli.services.rules import FlextCliRules as FlextCliRules
    from flext_cli.services.runtime import FlextCliRuntime as FlextCliRuntime
    from flext_cli.services.tables import FlextCliTables as FlextCliTables
    from flext_cli.settings import FlextCliSettings as FlextCliSettings
    from flext_cli.typings import FlextCliTypes as FlextCliTypes, t as t
    from flext_cli.utilities import FlextCliUtilities as FlextCliUtilities, u as u
    from flext_core import d as d, e as e, h as h, r as r, x as x
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
            ".services.auth": ("FlextCliAuth",),
            ".services.cli": ("FlextCliCli",),
            ".services.cli_params": ("FlextCliCommonParams",),
            ".services.cmd": ("FlextCliCmd",),
            ".services.file_tools": ("FlextCliFileTools",),
            ".services.formatters": ("FlextCliFormatters",),
            ".services.output": ("FlextCliOutput",),
            ".services.pipeline": ("FlextCliPipeline",),
            ".services.prompts": ("FlextCliPrompts",),
            ".services.rules": ("FlextCliRules",),
            ".services.runtime": ("FlextCliRuntime",),
            ".services.tables": ("FlextCliTables",),
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
        "pytest_addoption",
        "pytest_collect_file",
        "pytest_collection_modifyitems",
        "pytest_configure",
        "pytest_runtest_setup",
        "pytest_runtest_teardown",
        "pytest_sessionfinish",
        "pytest_sessionstart",
        "pytest_terminal_summary",
        "pytest_warning_recorded",
    ),
    module_name=__name__,
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    [
        "__author__",
        "__author_email__",
        "__description__",
        "__license__",
        "__title__",
        "__url__",
        "__version__",
        "__version_info__",
    ],
)

__all__: list[str] = [
    "FlextCli",
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommonParams",
    "FlextCliConstants",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliModels",
    "FlextCliOutput",
    "FlextCliPipeline",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliRules",
    "FlextCliRuntime",
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

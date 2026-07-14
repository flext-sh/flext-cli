# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli package."""

from __future__ import annotations

from typing import TYPE_CHECKING

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
from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d, e, h, r, x

    from ._config import FlextCliConfig, config
    from ._constants.base import FlextCliConstantsBase
    from ._constants.config import FlextCliConstantsConfig
    from ._constants.enums import FlextCliConstantsEnums
    from ._constants.errors import FlextCliConstantsErrors
    from ._constants.exceptions import (
        CliDefinitionError,
        CliValidationError,
        FlextCliConstantsExceptions,
    )
    from ._constants.files import FlextCliConstantsFiles
    from ._constants.output import FlextCliConstantsOutput
    from ._constants.pipeline import FlextCliConstantsPipeline
    from ._constants.settings import FlextCliConstantsSettings
    from ._constants.xlsx import FlextCliConstantsXlsx
    from ._constants.xlsx_future_functions import FlextCliConstantsXlsxFutureFunctions
    from ._models._base_parts.flextclimodelsbase_part_07 import FlextCliModelsBase
    from ._models.config import FlextCliConfigModels
    from ._models.pipeline import FlextCliModelsPipeline
    from ._models.rules import FlextCliModelsRules
    from ._models.template import FlextCliModelsTemplate
    from ._models.xlsx import FlextCliModelsXlsx
    from ._models.xlsx_archive import FlextCliModelsXlsxArchive
    from ._models.xlsx_cells import FlextCliModelsXlsxCells
    from ._models.xlsx_layout import FlextCliModelsXlsxLayout
    from ._models.xlsx_recalc import FlextCliModelsXlsxRecalc
    from ._models.xlsx_rules import FlextCliModelsXlsxRules
    from ._models.xlsx_snapshot import FlextCliModelsXlsxSnapshot
    from ._models.xlsx_style_catalog import FlextCliModelsXlsxStyleCatalog
    from ._models.xlsx_style_fills import FlextCliModelsXlsxStyleFills
    from ._models.xlsx_style_primitives import FlextCliModelsXlsxStylePrimitives
    from ._models.xlsx_styles import FlextCliModelsXlsxStyles
    from ._models.xlsx_tables import FlextCliModelsXlsxTables
    from ._models.xlsx_validation import FlextCliModelsXlsxValidation
    from ._models.xlsx_workbook import FlextCliModelsXlsxWorkbook
    from ._protocols._base_parts.flextcliprotocolsbase_part_05 import (
        FlextCliProtocolsBase,
    )
    from ._protocols.config import FlextCliProtocolsConfig
    from ._protocols.domain import FlextCliProtocolsDomain
    from ._protocols.framework import FlextCliProtocolsFramework
    from ._protocols.pipeline import FlextCliProtocolsPipeline
    from ._protocols.xlsx import FlextCliProtocolsXlsx
    from ._protocols.xlsx_archive import FlextCliProtocolsXlsxArchive
    from ._protocols.xlsx_rules import FlextCliProtocolsXlsxRules
    from ._protocols.xlsx_snapshot import FlextCliProtocolsXlsxSnapshot
    from ._protocols.xlsx_snapshot_structure import (
        FlextCliProtocolsXlsxSnapshotStructure,
    )
    from ._protocols.xlsx_workbook import FlextCliProtocolsXlsxWorkbook
    from ._settings import FlextCliSettings, settings
    from ._typings.base import FlextCliTypesBase
    from ._typings.domain import FlextCliTypesDomain
    from ._typings.pipeline import FlextCliTypesPipeline
    from ._typings.xlsx import FlextCliTypesXlsx
    from ._utilities._cli_namespace import FlextCliUtilitiesCli
    from ._utilities._file_test_helper_parts.flextcliutilitiesfiletesthelpersmixin_part_04 import (
        FlextCliUtilitiesFileTestHelpersMixin,
    )
    from ._utilities._files_parts.flextcliutilitiesfiles_part_04 import (
        FlextCliUtilitiesFiles,
    )
    from ._utilities._json._core import FlextCliUtilitiesJsonCoreMixin
    from ._utilities._json._navigate import FlextCliUtilitiesJsonNavigateMixin
    from ._utilities._options_parts.flextcliutilitiesoptionbuilder_part_01 import (
        FlextCliUtilitiesOptionBuilder,
    )
    from ._utilities._options_parts.flextcliutilitiesoptions_part_02 import (
        FlextCliUtilitiesOptions,
    )
    from ._utilities._rules._loaders import FlextCliUtilitiesRulesLoadersMixin
    from ._utilities._rules._matchers import FlextCliUtilitiesRulesMatchersMixin
    from ._utilities._toml_parts.flextcliutilitiestoml_part_07 import (
        FlextCliUtilitiesToml,
    )
    from ._utilities._xlxx.xlsx_addresses import FlextCliUtilitiesXlsxAddresses
    from ._utilities._xlxx.xlsx_archive import FlextCliUtilitiesXlsxArchive
    from ._utilities._xlxx.xlsx_archive_checks import FlextCliUtilitiesXlsxArchiveChecks
    from ._utilities._xlxx.xlsx_cells import FlextCliUtilitiesXlsxCells
    from ._utilities._xlxx.xlsx_conditional import FlextCliUtilitiesXlsxConditional
    from ._utilities._xlxx.xlsx_formula_codec import FlextCliUtilitiesXlsxFormulaCodec
    from ._utilities._xlxx.xlsx_layout import FlextCliUtilitiesXlsxLayout
    from ._utilities._xlxx.xlsx_protection import FlextCliUtilitiesXlsxProtection
    from ._utilities._xlxx.xlsx_recalc import FlextCliUtilitiesXlsxRecalc
    from ._utilities._xlxx.xlsx_recalc_evidence import (
        FlextCliUtilitiesXlsxRecalcEvidence,
    )
    from ._utilities._xlxx.xlsx_renderer import FlextCliUtilitiesXlsxRenderer
    from ._utilities._xlxx.xlsx_rules import FlextCliUtilitiesXlsxRules
    from ._utilities._xlxx.xlsx_snapshot import FlextCliUtilitiesXlsxSnapshot
    from ._utilities._xlxx.xlsx_snapshot_sheet import FlextCliUtilitiesXlsxSnapshotSheet
    from ._utilities._xlxx.xlsx_snapshot_structure import (
        FlextCliUtilitiesXlsxSnapshotStructure,
    )
    from ._utilities._xlxx.xlsx_snapshot_values import (
        FlextCliUtilitiesXlsxSnapshotValues,
    )
    from ._utilities._xlxx.xlsx_style_builders import FlextCliUtilitiesXlsxStyleBuilders
    from ._utilities._xlxx.xlsx_style_catalog import FlextCliUtilitiesXlsxStyleCatalog
    from ._utilities._xlxx.xlsx_style_codec import FlextCliUtilitiesXlsxStyleCodec
    from ._utilities._xlxx.xlsx_style_readers import FlextCliUtilitiesXlsxStyleReaders
    from ._utilities._xlxx.xlsx_tables import FlextCliUtilitiesXlsxTables
    from ._utilities._xlxx.xlsx_validations import FlextCliUtilitiesXlsxValidations
    from ._utilities._xlxx.xlsx_workbook_io import FlextCliUtilitiesXlsxWorkbookIo
    from ._utilities._xlxx.xlsx_workbook_plan import FlextCliUtilitiesXlsxWorkbookPlan
    from ._utilities._yaml._convert import FlextCliUtilitiesYamlConvertMixin
    from ._utilities._yaml._editing import FlextCliUtilitiesYamlEditingMixin
    from ._utilities._yaml._engine import FlextCliUtilitiesYamlEngineMixin
    from ._utilities.auth import FlextCliUtilitiesAuth
    from ._utilities.cmd import FlextCliUtilitiesCmd
    from ._utilities.commands import FlextCliUtilitiesCommands
    from ._utilities.config import FlextCliUtilitiesConfig
    from ._utilities.conversion import FlextCliUtilitiesConversion
    from ._utilities.formatters import FlextCliUtilitiesFormatters
    from ._utilities.framework import FlextCliUtilitiesFramework
    from ._utilities.json import FlextCliUtilitiesJson
    from ._utilities.matching import FlextCliUtilitiesMatching
    from ._utilities.model_commands import FlextCliUtilitiesModelCommands
    from ._utilities.output import FlextCliUtilitiesOutput
    from ._utilities.params import FlextCliUtilitiesParams
    from ._utilities.pipeline import FlextCliUtilitiesPipeline
    from ._utilities.processes import FlextCliUtilitiesProcesses
    from ._utilities.prompts import FlextCliUtilitiesPrompts
    from ._utilities.rules import FlextCliUtilitiesRules
    from ._utilities.runtime import FlextCliUtilitiesRuntime
    from ._utilities.settings import FlextCliUtilitiesSettings
    from ._utilities.tables import FlextCliUtilitiesTables
    from ._utilities.template import FlextCliUtilitiesTemplate
    from ._utilities.validation import FlextCliUtilitiesValidation
    from ._utilities.xlsx import FlextCliUtilitiesXlsx
    from ._utilities.yaml import FlextCliUtilitiesYaml
    from ._utilities.yaml_model import FlextCliUtilitiesYamlModel
    from .api import FlextCli, cli
    from .base import FlextCliServiceBase, s
    from .constants import FlextCliConstants, FlextCliConstants as c
    from .models import FlextCliModels, FlextCliModels as m
    from .protocols import FlextCliProtocols, FlextCliProtocols as p
    from .services.auth import FlextCliAuth
    from .services.cli import FlextCliCli
    from .services.cli_params import FlextCliCommonParams
    from .services.cmd import FlextCliCmd
    from .services.file_tools import FlextCliFileTools
    from .services.formatters import FlextCliFormatters
    from .services.output import FlextCliOutput
    from .services.pipeline import FlextCliPipeline
    from .services.prompts import FlextCliPrompts
    from .services.rules import FlextCliRules
    from .services.runtime import FlextCliRuntime
    from .services.tables import FlextCliTables
    from .services.xlsx import FlextCliXlsx
    from .services.yaml_model import FlextCliYamlModel
    from .typings import FlextCliTypes, FlextCliTypes as t
    from .utilities import FlextCliUtilities, FlextCliUtilities as u

    _ = (
        c,
        FlextCliConstants,
        t,
        FlextCliTypes,
        p,
        FlextCliProtocols,
        m,
        FlextCliModels,
        u,
        FlextCliUtilities,
        d,
        e,
        h,
        r,
        x,
        s,
        FlextCliServiceBase,
        FlextCliConfig,
        config,
        FlextCliConstantsBase,
        FlextCliConstantsConfig,
        FlextCliConstantsEnums,
        FlextCliConstantsErrors,
        CliDefinitionError,
        CliValidationError,
        FlextCliConstantsExceptions,
        FlextCliConstantsFiles,
        FlextCliConstantsOutput,
        FlextCliConstantsPipeline,
        FlextCliConstantsSettings,
        FlextCliConstantsXlsx,
        FlextCliConstantsXlsxFutureFunctions,
        FlextCliModelsBase,
        FlextCliConfigModels,
        FlextCliModelsPipeline,
        FlextCliModelsRules,
        FlextCliModelsTemplate,
        FlextCliModelsXlsx,
        FlextCliModelsXlsxArchive,
        FlextCliModelsXlsxCells,
        FlextCliModelsXlsxLayout,
        FlextCliModelsXlsxRecalc,
        FlextCliModelsXlsxRules,
        FlextCliModelsXlsxSnapshot,
        FlextCliModelsXlsxStyleCatalog,
        FlextCliModelsXlsxStyleFills,
        FlextCliModelsXlsxStylePrimitives,
        FlextCliModelsXlsxStyles,
        FlextCliModelsXlsxTables,
        FlextCliModelsXlsxValidation,
        FlextCliModelsXlsxWorkbook,
        FlextCliProtocolsBase,
        FlextCliProtocolsConfig,
        FlextCliProtocolsDomain,
        FlextCliProtocolsFramework,
        FlextCliProtocolsPipeline,
        FlextCliProtocolsXlsx,
        FlextCliProtocolsXlsxArchive,
        FlextCliProtocolsXlsxRules,
        FlextCliProtocolsXlsxSnapshot,
        FlextCliProtocolsXlsxSnapshotStructure,
        FlextCliProtocolsXlsxWorkbook,
        FlextCliSettings,
        settings,
        FlextCliTypesBase,
        FlextCliTypesDomain,
        FlextCliTypesPipeline,
        FlextCliTypesXlsx,
        FlextCliUtilitiesCli,
        FlextCliUtilitiesFileTestHelpersMixin,
        FlextCliUtilitiesFiles,
        FlextCliUtilitiesJsonCoreMixin,
        FlextCliUtilitiesJsonNavigateMixin,
        FlextCliUtilitiesOptionBuilder,
        FlextCliUtilitiesOptions,
        FlextCliUtilitiesRulesLoadersMixin,
        FlextCliUtilitiesRulesMatchersMixin,
        FlextCliUtilitiesToml,
        FlextCliUtilitiesXlsxAddresses,
        FlextCliUtilitiesXlsxArchive,
        FlextCliUtilitiesXlsxArchiveChecks,
        FlextCliUtilitiesXlsxCells,
        FlextCliUtilitiesXlsxConditional,
        FlextCliUtilitiesXlsxFormulaCodec,
        FlextCliUtilitiesXlsxLayout,
        FlextCliUtilitiesXlsxProtection,
        FlextCliUtilitiesXlsxRecalc,
        FlextCliUtilitiesXlsxRecalcEvidence,
        FlextCliUtilitiesXlsxRenderer,
        FlextCliUtilitiesXlsxRules,
        FlextCliUtilitiesXlsxSnapshot,
        FlextCliUtilitiesXlsxSnapshotSheet,
        FlextCliUtilitiesXlsxSnapshotStructure,
        FlextCliUtilitiesXlsxSnapshotValues,
        FlextCliUtilitiesXlsxStyleBuilders,
        FlextCliUtilitiesXlsxStyleCatalog,
        FlextCliUtilitiesXlsxStyleCodec,
        FlextCliUtilitiesXlsxStyleReaders,
        FlextCliUtilitiesXlsxTables,
        FlextCliUtilitiesXlsxValidations,
        FlextCliUtilitiesXlsxWorkbookIo,
        FlextCliUtilitiesXlsxWorkbookPlan,
        FlextCliUtilitiesYamlConvertMixin,
        FlextCliUtilitiesYamlEditingMixin,
        FlextCliUtilitiesYamlEngineMixin,
        FlextCliUtilitiesAuth,
        FlextCliUtilitiesCmd,
        FlextCliUtilitiesCommands,
        FlextCliUtilitiesConfig,
        FlextCliUtilitiesConversion,
        FlextCliUtilitiesFormatters,
        FlextCliUtilitiesFramework,
        FlextCliUtilitiesJson,
        FlextCliUtilitiesMatching,
        FlextCliUtilitiesModelCommands,
        FlextCliUtilitiesOutput,
        FlextCliUtilitiesParams,
        FlextCliUtilitiesPipeline,
        FlextCliUtilitiesProcesses,
        FlextCliUtilitiesPrompts,
        FlextCliUtilitiesRules,
        FlextCliUtilitiesRuntime,
        FlextCliUtilitiesSettings,
        FlextCliUtilitiesTables,
        FlextCliUtilitiesTemplate,
        FlextCliUtilitiesValidation,
        FlextCliUtilitiesXlsx,
        FlextCliUtilitiesYaml,
        FlextCliUtilitiesYamlModel,
        FlextCli,
        cli,
        FlextCliAuth,
        FlextCliCli,
        FlextCliCommonParams,
        FlextCliCmd,
        FlextCliFileTools,
        FlextCliFormatters,
        FlextCliOutput,
        FlextCliPipeline,
        FlextCliPrompts,
        FlextCliRules,
        FlextCliRuntime,
        FlextCliTables,
        FlextCliXlsx,
        FlextCliYamlModel,
    )


_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    "._config": ("FlextCliConfig", "config"),
    "._constants.base": ("FlextCliConstantsBase",),
    "._constants.config": ("FlextCliConstantsConfig",),
    "._constants.enums": ("FlextCliConstantsEnums",),
    "._constants.errors": ("FlextCliConstantsErrors",),
    "._constants.exceptions": (
        "CliDefinitionError",
        "CliValidationError",
        "FlextCliConstantsExceptions",
    ),
    "._constants.files": ("FlextCliConstantsFiles",),
    "._constants.output": ("FlextCliConstantsOutput",),
    "._constants.pipeline": ("FlextCliConstantsPipeline",),
    "._constants.settings": ("FlextCliConstantsSettings",),
    "._constants.xlsx": ("FlextCliConstantsXlsx",),
    "._constants.xlsx_future_functions": ("FlextCliConstantsXlsxFutureFunctions",),
    "._models._base_parts.flextclimodelsbase_part_07": ("FlextCliModelsBase",),
    "._models.config": ("FlextCliConfigModels",),
    "._models.pipeline": ("FlextCliModelsPipeline",),
    "._models.rules": ("FlextCliModelsRules",),
    "._models.template": ("FlextCliModelsTemplate",),
    "._models.xlsx": ("FlextCliModelsXlsx",),
    "._models.xlsx_archive": ("FlextCliModelsXlsxArchive",),
    "._models.xlsx_cells": ("FlextCliModelsXlsxCells",),
    "._models.xlsx_layout": ("FlextCliModelsXlsxLayout",),
    "._models.xlsx_recalc": ("FlextCliModelsXlsxRecalc",),
    "._models.xlsx_rules": ("FlextCliModelsXlsxRules",),
    "._models.xlsx_snapshot": ("FlextCliModelsXlsxSnapshot",),
    "._models.xlsx_style_catalog": ("FlextCliModelsXlsxStyleCatalog",),
    "._models.xlsx_style_fills": ("FlextCliModelsXlsxStyleFills",),
    "._models.xlsx_style_primitives": ("FlextCliModelsXlsxStylePrimitives",),
    "._models.xlsx_styles": ("FlextCliModelsXlsxStyles",),
    "._models.xlsx_tables": ("FlextCliModelsXlsxTables",),
    "._models.xlsx_validation": ("FlextCliModelsXlsxValidation",),
    "._models.xlsx_workbook": ("FlextCliModelsXlsxWorkbook",),
    "._protocols._base_parts.flextcliprotocolsbase_part_05": ("FlextCliProtocolsBase",),
    "._protocols.config": ("FlextCliProtocolsConfig",),
    "._protocols.domain": ("FlextCliProtocolsDomain",),
    "._protocols.framework": ("FlextCliProtocolsFramework",),
    "._protocols.pipeline": ("FlextCliProtocolsPipeline",),
    "._protocols.xlsx": ("FlextCliProtocolsXlsx",),
    "._protocols.xlsx_archive": ("FlextCliProtocolsXlsxArchive",),
    "._protocols.xlsx_rules": ("FlextCliProtocolsXlsxRules",),
    "._protocols.xlsx_snapshot": ("FlextCliProtocolsXlsxSnapshot",),
    "._protocols.xlsx_snapshot_structure": ("FlextCliProtocolsXlsxSnapshotStructure",),
    "._protocols.xlsx_workbook": ("FlextCliProtocolsXlsxWorkbook",),
    "._settings": ("FlextCliSettings", "settings"),
    "._typings.base": ("FlextCliTypesBase",),
    "._typings.domain": ("FlextCliTypesDomain",),
    "._typings.pipeline": ("FlextCliTypesPipeline",),
    "._typings.xlsx": ("FlextCliTypesXlsx",),
    "._utilities._cli_namespace": ("FlextCliUtilitiesCli",),
    "._utilities._file_test_helper_parts.flextcliutilitiesfiletesthelpersmixin_part_04": (
        "FlextCliUtilitiesFileTestHelpersMixin",
    ),
    "._utilities._files_parts.flextcliutilitiesfiles_part_04": (
        "FlextCliUtilitiesFiles",
    ),
    "._utilities._json._core": ("FlextCliUtilitiesJsonCoreMixin",),
    "._utilities._json._navigate": ("FlextCliUtilitiesJsonNavigateMixin",),
    "._utilities._options_parts.flextcliutilitiesoptionbuilder_part_01": (
        "FlextCliUtilitiesOptionBuilder",
    ),
    "._utilities._options_parts.flextcliutilitiesoptions_part_02": (
        "FlextCliUtilitiesOptions",
    ),
    "._utilities._rules._loaders": ("FlextCliUtilitiesRulesLoadersMixin",),
    "._utilities._rules._matchers": ("FlextCliUtilitiesRulesMatchersMixin",),
    "._utilities._toml_parts.flextcliutilitiestoml_part_07": ("FlextCliUtilitiesToml",),
    "._utilities._xlxx.xlsx_addresses": ("FlextCliUtilitiesXlsxAddresses",),
    "._utilities._xlxx.xlsx_archive": ("FlextCliUtilitiesXlsxArchive",),
    "._utilities._xlxx.xlsx_archive_checks": ("FlextCliUtilitiesXlsxArchiveChecks",),
    "._utilities._xlxx.xlsx_cells": ("FlextCliUtilitiesXlsxCells",),
    "._utilities._xlxx.xlsx_conditional": ("FlextCliUtilitiesXlsxConditional",),
    "._utilities._xlxx.xlsx_formula_codec": ("FlextCliUtilitiesXlsxFormulaCodec",),
    "._utilities._xlxx.xlsx_layout": ("FlextCliUtilitiesXlsxLayout",),
    "._utilities._xlxx.xlsx_protection": ("FlextCliUtilitiesXlsxProtection",),
    "._utilities._xlxx.xlsx_recalc": ("FlextCliUtilitiesXlsxRecalc",),
    "._utilities._xlxx.xlsx_recalc_evidence": ("FlextCliUtilitiesXlsxRecalcEvidence",),
    "._utilities._xlxx.xlsx_renderer": ("FlextCliUtilitiesXlsxRenderer",),
    "._utilities._xlxx.xlsx_rules": ("FlextCliUtilitiesXlsxRules",),
    "._utilities._xlxx.xlsx_snapshot": ("FlextCliUtilitiesXlsxSnapshot",),
    "._utilities._xlxx.xlsx_snapshot_sheet": ("FlextCliUtilitiesXlsxSnapshotSheet",),
    "._utilities._xlxx.xlsx_snapshot_structure": (
        "FlextCliUtilitiesXlsxSnapshotStructure",
    ),
    "._utilities._xlxx.xlsx_snapshot_values": ("FlextCliUtilitiesXlsxSnapshotValues",),
    "._utilities._xlxx.xlsx_style_builders": ("FlextCliUtilitiesXlsxStyleBuilders",),
    "._utilities._xlxx.xlsx_style_catalog": ("FlextCliUtilitiesXlsxStyleCatalog",),
    "._utilities._xlxx.xlsx_style_codec": ("FlextCliUtilitiesXlsxStyleCodec",),
    "._utilities._xlxx.xlsx_style_readers": ("FlextCliUtilitiesXlsxStyleReaders",),
    "._utilities._xlxx.xlsx_tables": ("FlextCliUtilitiesXlsxTables",),
    "._utilities._xlxx.xlsx_validations": ("FlextCliUtilitiesXlsxValidations",),
    "._utilities._xlxx.xlsx_workbook_io": ("FlextCliUtilitiesXlsxWorkbookIo",),
    "._utilities._xlxx.xlsx_workbook_plan": ("FlextCliUtilitiesXlsxWorkbookPlan",),
    "._utilities._yaml._convert": ("FlextCliUtilitiesYamlConvertMixin",),
    "._utilities._yaml._editing": ("FlextCliUtilitiesYamlEditingMixin",),
    "._utilities._yaml._engine": ("FlextCliUtilitiesYamlEngineMixin",),
    "._utilities.auth": ("FlextCliUtilitiesAuth",),
    "._utilities.cmd": ("FlextCliUtilitiesCmd",),
    "._utilities.commands": ("FlextCliUtilitiesCommands",),
    "._utilities.config": ("FlextCliUtilitiesConfig",),
    "._utilities.conversion": ("FlextCliUtilitiesConversion",),
    "._utilities.formatters": ("FlextCliUtilitiesFormatters",),
    "._utilities.framework": ("FlextCliUtilitiesFramework",),
    "._utilities.json": ("FlextCliUtilitiesJson",),
    "._utilities.matching": ("FlextCliUtilitiesMatching",),
    "._utilities.model_commands": ("FlextCliUtilitiesModelCommands",),
    "._utilities.output": ("FlextCliUtilitiesOutput",),
    "._utilities.params": ("FlextCliUtilitiesParams",),
    "._utilities.pipeline": ("FlextCliUtilitiesPipeline",),
    "._utilities.processes": ("FlextCliUtilitiesProcesses",),
    "._utilities.prompts": ("FlextCliUtilitiesPrompts",),
    "._utilities.rules": ("FlextCliUtilitiesRules",),
    "._utilities.runtime": ("FlextCliUtilitiesRuntime",),
    "._utilities.settings": ("FlextCliUtilitiesSettings",),
    "._utilities.tables": ("FlextCliUtilitiesTables",),
    "._utilities.template": ("FlextCliUtilitiesTemplate",),
    "._utilities.validation": ("FlextCliUtilitiesValidation",),
    "._utilities.xlsx": ("FlextCliUtilitiesXlsx",),
    "._utilities.yaml": ("FlextCliUtilitiesYaml",),
    "._utilities.yaml_model": ("FlextCliUtilitiesYamlModel",),
    ".api": ("FlextCli", "cli"),
    ".base": ("FlextCliServiceBase", "s"),
    ".constants": ("FlextCliConstants", "c"),
    ".models": ("FlextCliModels", "m"),
    ".protocols": ("FlextCliProtocols", "p"),
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
    ".services.xlsx": ("FlextCliXlsx",),
    ".services.yaml_model": ("FlextCliYamlModel",),
    ".typings": ("FlextCliTypes", "t"),
    ".utilities": ("FlextCliUtilities", "u"),
    "flext_core": ("d", "e", "h", "r", "x"),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_DIRECT_IMPORTS: tuple[str, ...] = (
    "CliDefinitionError",
    "CliValidationError",
    "FlextCli",
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommonParams",
    "FlextCliConfig",
    "FlextCliConfigModels",
    "FlextCliConstants",
    "FlextCliConstantsBase",
    "FlextCliConstantsConfig",
    "FlextCliConstantsEnums",
    "FlextCliConstantsErrors",
    "FlextCliConstantsExceptions",
    "FlextCliConstantsFiles",
    "FlextCliConstantsOutput",
    "FlextCliConstantsPipeline",
    "FlextCliConstantsSettings",
    "FlextCliConstantsXlsx",
    "FlextCliConstantsXlsxFutureFunctions",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliModels",
    "FlextCliModelsBase",
    "FlextCliModelsPipeline",
    "FlextCliModelsRules",
    "FlextCliModelsTemplate",
    "FlextCliModelsXlsx",
    "FlextCliModelsXlsxArchive",
    "FlextCliModelsXlsxCells",
    "FlextCliModelsXlsxLayout",
    "FlextCliModelsXlsxRecalc",
    "FlextCliModelsXlsxRules",
    "FlextCliModelsXlsxSnapshot",
    "FlextCliModelsXlsxStyleCatalog",
    "FlextCliModelsXlsxStyleFills",
    "FlextCliModelsXlsxStylePrimitives",
    "FlextCliModelsXlsxStyles",
    "FlextCliModelsXlsxTables",
    "FlextCliModelsXlsxValidation",
    "FlextCliModelsXlsxWorkbook",
    "FlextCliOutput",
    "FlextCliPipeline",
    "FlextCliPrompts",
    "FlextCliProtocols",
    "FlextCliProtocolsBase",
    "FlextCliProtocolsConfig",
    "FlextCliProtocolsDomain",
    "FlextCliProtocolsFramework",
    "FlextCliProtocolsPipeline",
    "FlextCliProtocolsXlsx",
    "FlextCliProtocolsXlsxArchive",
    "FlextCliProtocolsXlsxRules",
    "FlextCliProtocolsXlsxSnapshot",
    "FlextCliProtocolsXlsxSnapshotStructure",
    "FlextCliProtocolsXlsxWorkbook",
    "FlextCliRules",
    "FlextCliRuntime",
    "FlextCliServiceBase",
    "FlextCliSettings",
    "FlextCliTables",
    "FlextCliTypes",
    "FlextCliTypesBase",
    "FlextCliTypesDomain",
    "FlextCliTypesPipeline",
    "FlextCliTypesXlsx",
    "FlextCliUtilities",
    "FlextCliUtilitiesAuth",
    "FlextCliUtilitiesCli",
    "FlextCliUtilitiesCmd",
    "FlextCliUtilitiesCommands",
    "FlextCliUtilitiesConfig",
    "FlextCliUtilitiesConversion",
    "FlextCliUtilitiesFileTestHelpersMixin",
    "FlextCliUtilitiesFiles",
    "FlextCliUtilitiesFormatters",
    "FlextCliUtilitiesFramework",
    "FlextCliUtilitiesJson",
    "FlextCliUtilitiesJsonCoreMixin",
    "FlextCliUtilitiesJsonNavigateMixin",
    "FlextCliUtilitiesMatching",
    "FlextCliUtilitiesModelCommands",
    "FlextCliUtilitiesOptionBuilder",
    "FlextCliUtilitiesOptions",
    "FlextCliUtilitiesOutput",
    "FlextCliUtilitiesParams",
    "FlextCliUtilitiesPipeline",
    "FlextCliUtilitiesProcesses",
    "FlextCliUtilitiesPrompts",
    "FlextCliUtilitiesRules",
    "FlextCliUtilitiesRulesLoadersMixin",
    "FlextCliUtilitiesRulesMatchersMixin",
    "FlextCliUtilitiesRuntime",
    "FlextCliUtilitiesSettings",
    "FlextCliUtilitiesTables",
    "FlextCliUtilitiesTemplate",
    "FlextCliUtilitiesToml",
    "FlextCliUtilitiesValidation",
    "FlextCliUtilitiesXlsx",
    "FlextCliUtilitiesXlsxAddresses",
    "FlextCliUtilitiesXlsxArchive",
    "FlextCliUtilitiesXlsxArchiveChecks",
    "FlextCliUtilitiesXlsxCells",
    "FlextCliUtilitiesXlsxConditional",
    "FlextCliUtilitiesXlsxFormulaCodec",
    "FlextCliUtilitiesXlsxLayout",
    "FlextCliUtilitiesXlsxProtection",
    "FlextCliUtilitiesXlsxRecalc",
    "FlextCliUtilitiesXlsxRecalcEvidence",
    "FlextCliUtilitiesXlsxRenderer",
    "FlextCliUtilitiesXlsxRules",
    "FlextCliUtilitiesXlsxSnapshot",
    "FlextCliUtilitiesXlsxSnapshotSheet",
    "FlextCliUtilitiesXlsxSnapshotStructure",
    "FlextCliUtilitiesXlsxSnapshotValues",
    "FlextCliUtilitiesXlsxStyleBuilders",
    "FlextCliUtilitiesXlsxStyleCatalog",
    "FlextCliUtilitiesXlsxStyleCodec",
    "FlextCliUtilitiesXlsxStyleReaders",
    "FlextCliUtilitiesXlsxTables",
    "FlextCliUtilitiesXlsxValidations",
    "FlextCliUtilitiesXlsxWorkbookIo",
    "FlextCliUtilitiesXlsxWorkbookPlan",
    "FlextCliUtilitiesYaml",
    "FlextCliUtilitiesYamlConvertMixin",
    "FlextCliUtilitiesYamlEditingMixin",
    "FlextCliUtilitiesYamlEngineMixin",
    "FlextCliUtilitiesYamlModel",
    "FlextCliXlsx",
    "FlextCliYamlModel",
    "__author__",
    "__author_email__",
    "__description__",
    "__license__",
    "__title__",
    "__url__",
    "__version__",
    "__version_info__",
    "build_lazy_import_map",
    "c",
    "cli",
    "config",
    "d",
    "e",
    "h",
    "install_lazy_exports",
    "m",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)

__all__: tuple[str, ...] = (
    "FlextCli",
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCmd",
    "FlextCliCommonParams",
    "FlextCliConfig",
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
    "FlextCliXlsx",
    "FlextCliYamlModel",
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
    "config",
    "d",
    "e",
    "h",
    "m",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

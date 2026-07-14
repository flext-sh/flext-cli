# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities package."""

from __future__ import annotations

from typing import TYPE_CHECKING

# mro-i6nq.10: The package consumes its manifest's public-export contract.
from flext_cli._utilities.__unit__ import (
    CHILD_MODULE_PATHS as _CHILD_MODULE_PATHS,
    EXCLUDED_LAZY_NAMES as _EXCLUDED_LAZY_NAMES,
    PUBLIC_EXPORTS as _PUBLIC_EXPORTS,
)
from flext_core.lazy import (
    build_lazy_import_map,
    install_lazy_exports,
    merge_lazy_imports,
)

if TYPE_CHECKING:
    from flext_cli._utilities import (
        _file_test_helper_parts as _file_test_helper_parts,
        _files_parts as _files_parts,
        _json as _json,
        _options_parts as _options_parts,
        _rules as _rules,
        _toml_parts as _toml_parts,
        _yaml as _yaml,
    )
    from flext_cli._utilities._cli_namespace import (
        FlextCliUtilitiesCli as FlextCliUtilitiesCli,
    )
    from flext_cli._utilities._file_test_helper_parts.flextcliutilitiesfiletesthelpersmixin_part_04 import (
        FlextCliUtilitiesFileTestHelpersMixin as FlextCliUtilitiesFileTestHelpersMixin,
    )
    from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_04 import (
        FlextCliUtilitiesFiles as FlextCliUtilitiesFiles,
    )
    from flext_cli._utilities._json._core import (
        FlextCliUtilitiesJsonCoreMixin as FlextCliUtilitiesJsonCoreMixin,
    )
    from flext_cli._utilities._json._navigate import (
        FlextCliUtilitiesJsonNavigateMixin as FlextCliUtilitiesJsonNavigateMixin,
    )
    from flext_cli._utilities._options_parts.flextcliutilitiesoptionbuilder_part_01 import (
        FlextCliUtilitiesOptionBuilder as FlextCliUtilitiesOptionBuilder,
    )
    from flext_cli._utilities._options_parts.flextcliutilitiesoptions_part_02 import (
        FlextCliUtilitiesOptions as FlextCliUtilitiesOptions,
    )
    from flext_cli._utilities._rules._loaders import (
        FlextCliUtilitiesRulesLoadersMixin as FlextCliUtilitiesRulesLoadersMixin,
    )
    from flext_cli._utilities._rules._matchers import (
        FlextCliUtilitiesRulesMatchersMixin as FlextCliUtilitiesRulesMatchersMixin,
    )
    from flext_cli._utilities._toml_parts.flextcliutilitiestoml_part_07 import (
        FlextCliUtilitiesToml as FlextCliUtilitiesToml,
    )
    from flext_cli._utilities._yaml._convert import (
        FlextCliUtilitiesYamlConvertMixin as FlextCliUtilitiesYamlConvertMixin,
    )
    from flext_cli._utilities._yaml._editing import (
        FlextCliUtilitiesYamlEditingMixin as FlextCliUtilitiesYamlEditingMixin,
    )
    from flext_cli._utilities._yaml._engine import (
        FlextCliUtilitiesYamlEngineMixin as FlextCliUtilitiesYamlEngineMixin,
    )
    from flext_cli._utilities.auth import FlextCliUtilitiesAuth as FlextCliUtilitiesAuth
    from flext_cli._utilities.cmd import FlextCliUtilitiesCmd as FlextCliUtilitiesCmd
    from flext_cli._utilities.commands import (
        FlextCliUtilitiesCommands as FlextCliUtilitiesCommands,
    )
    from flext_cli._utilities.config import (
        FlextCliUtilitiesConfig as FlextCliUtilitiesConfig,
    )
    from flext_cli._utilities.conversion import (
        FlextCliUtilitiesConversion as FlextCliUtilitiesConversion,
    )
    from flext_cli._utilities.formatters import (
        FlextCliUtilitiesFormatters as FlextCliUtilitiesFormatters,
    )
    from flext_cli._utilities.framework import (
        FlextCliUtilitiesFramework as FlextCliUtilitiesFramework,
    )
    from flext_cli._utilities.json import FlextCliUtilitiesJson as FlextCliUtilitiesJson
    from flext_cli._utilities.matching import (
        FlextCliUtilitiesMatching as FlextCliUtilitiesMatching,
    )
    from flext_cli._utilities.model_commands import (
        FlextCliUtilitiesModelCommands as FlextCliUtilitiesModelCommands,
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
    from flext_cli._utilities.processes import (
        FlextCliUtilitiesProcesses as FlextCliUtilitiesProcesses,
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
    from flext_cli._utilities.template import (
        FlextCliUtilitiesTemplate as FlextCliUtilitiesTemplate,
    )
    from flext_cli._utilities.validation import (
        FlextCliUtilitiesValidation as FlextCliUtilitiesValidation,
    )
    from flext_cli._utilities.xlsx import FlextCliUtilitiesXlsx as FlextCliUtilitiesXlsx
    from flext_cli._utilities._xlxx.xlsx_addresses import (
        FlextCliUtilitiesXlsxAddresses as FlextCliUtilitiesXlsxAddresses,
    )
    from flext_cli._utilities._xlxx.xlsx_archive import (
        FlextCliUtilitiesXlsxArchive as FlextCliUtilitiesXlsxArchive,
    )
    from flext_cli._utilities._xlxx.xlsx_archive_checks import (
        FlextCliUtilitiesXlsxArchiveChecks as FlextCliUtilitiesXlsxArchiveChecks,
    )
    from flext_cli._utilities._xlxx.xlsx_cells import (
        FlextCliUtilitiesXlsxCells as FlextCliUtilitiesXlsxCells,
    )
    from flext_cli._utilities._xlxx.xlsx_conditional import (
        FlextCliUtilitiesXlsxConditional as FlextCliUtilitiesXlsxConditional,
    )
    from flext_cli._utilities._xlxx.xlsx_formula_codec import (
        FlextCliUtilitiesXlsxFormulaCodec as FlextCliUtilitiesXlsxFormulaCodec,
    )
    from flext_cli._utilities._xlxx.xlsx_layout import (
        FlextCliUtilitiesXlsxLayout as FlextCliUtilitiesXlsxLayout,
    )
    from flext_cli._utilities._xlxx.xlsx_protection import (
        FlextCliUtilitiesXlsxProtection as FlextCliUtilitiesXlsxProtection,
    )
    from flext_cli._utilities._xlxx.xlsx_recalc import (
        FlextCliUtilitiesXlsxRecalc as FlextCliUtilitiesXlsxRecalc,
    )
    from flext_cli._utilities._xlxx.xlsx_recalc_evidence import (
        FlextCliUtilitiesXlsxRecalcEvidence as FlextCliUtilitiesXlsxRecalcEvidence,
    )
    from flext_cli._utilities._xlxx.xlsx_renderer import (
        FlextCliUtilitiesXlsxRenderer as FlextCliUtilitiesXlsxRenderer,
    )
    from flext_cli._utilities._xlxx.xlsx_rules import (
        FlextCliUtilitiesXlsxRules as FlextCliUtilitiesXlsxRules,
    )
    from flext_cli._utilities._xlxx.xlsx_snapshot import (
        FlextCliUtilitiesXlsxSnapshot as FlextCliUtilitiesXlsxSnapshot,
    )
    from flext_cli._utilities._xlxx.xlsx_snapshot_sheet import (
        FlextCliUtilitiesXlsxSnapshotSheet as FlextCliUtilitiesXlsxSnapshotSheet,
    )
    from flext_cli._utilities._xlxx.xlsx_snapshot_structure import (
        FlextCliUtilitiesXlsxSnapshotStructure as FlextCliUtilitiesXlsxSnapshotStructure,
    )
    from flext_cli._utilities._xlxx.xlsx_snapshot_values import (
        FlextCliUtilitiesXlsxSnapshotValues as FlextCliUtilitiesXlsxSnapshotValues,
    )
    from flext_cli._utilities._xlxx.xlsx_style_builders import (
        FlextCliUtilitiesXlsxStyleBuilders as FlextCliUtilitiesXlsxStyleBuilders,
    )
    from flext_cli._utilities._xlxx.xlsx_style_catalog import (
        FlextCliUtilitiesXlsxStyleCatalog as FlextCliUtilitiesXlsxStyleCatalog,
    )
    from flext_cli._utilities._xlxx.xlsx_style_codec import (
        FlextCliUtilitiesXlsxStyleCodec as FlextCliUtilitiesXlsxStyleCodec,
    )
    from flext_cli._utilities._xlxx.xlsx_style_readers import (
        FlextCliUtilitiesXlsxStyleReaders as FlextCliUtilitiesXlsxStyleReaders,
    )
    from flext_cli._utilities._xlxx.xlsx_tables import (
        FlextCliUtilitiesXlsxTables as FlextCliUtilitiesXlsxTables,
    )
    from flext_cli._utilities._xlxx.xlsx_validations import (
        FlextCliUtilitiesXlsxValidations as FlextCliUtilitiesXlsxValidations,
    )
    from flext_cli._utilities._xlxx.xlsx_workbook_io import (
        FlextCliUtilitiesXlsxWorkbookIo as FlextCliUtilitiesXlsxWorkbookIo,
    )
    from flext_cli._utilities._xlxx.xlsx_workbook_plan import (
        FlextCliUtilitiesXlsxWorkbookPlan as FlextCliUtilitiesXlsxWorkbookPlan,
    )
    from flext_cli._utilities.yaml import FlextCliUtilitiesYaml as FlextCliUtilitiesYaml
    from flext_cli._utilities.yaml_model import (
        FlextCliUtilitiesYamlModel as FlextCliUtilitiesYamlModel,
    )

    # mro-i6nq.10: Static declaration mirrors the installer-owned runtime binding.
    __all__: tuple[str, ...]


_LAZY_IMPORTS = merge_lazy_imports(
    _CHILD_MODULE_PATHS,
    build_lazy_import_map(
        _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
    ),
    exclude_names=_EXCLUDED_LAZY_NAMES,
    module_name=__name__,
)


# mro-i6nq.10: The installer publishes __all__ from the manifest's literal ABI.
install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=_PUBLIC_EXPORTS)

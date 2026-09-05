# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from . import (
        _docx as _docx,
        _file_test_helper_parts as _file_test_helper_parts,
        _files_parts as _files_parts,
        _json as _json,
        _options_parts as _options_parts,
        _pptx as _pptx,
        _rules as _rules,
        _toml_parts as _toml_parts,
        _xlxx as _xlxx,
        _yaml as _yaml,
    )
    from ._cli_namespace import FlextCliUtilitiesCli
    from ._docx._reader import FlextCliUtilitiesDocxReader
    from ._docx._renderer import FlextCliUtilitiesDocxRenderer
    from ._json._core import FlextCliUtilitiesJsonCoreMixin
    from ._json._navigate import FlextCliUtilitiesJsonNavigateMixin
    from ._options_parts.flextcliutilitiesoptionbuilder_part_01 import (
        FlextCliUtilitiesOptionBuilder,
    )
    from ._options_parts.flextcliutilitiesoptions_part_02 import (
        FlextCliUtilitiesOptions,
    )
    from ._pptx._reader import FlextCliUtilitiesPptxReader
    from ._pptx._renderer import FlextCliUtilitiesPptxRenderer
    from ._pptx._serializer import FlextCliUtilitiesPptxSerializer
    from ._rules._loaders import FlextCliUtilitiesRulesLoadersMixin
    from ._rules._matchers import FlextCliUtilitiesRulesMatchersMixin
    from ._runtime_commands import FlextCliUtilitiesRuntimeCommandsMixin
    from ._runtime_process_cleanup import FlextCliUtilitiesRuntimeProcessCleanupMixin
    from ._runtime_process_execution import (
        FlextCliUtilitiesRuntimeProcessExecutionMixin,
    )
    from ._runtime_process_group import FlextCliUtilitiesRuntimeProcessGroupMixin
    from ._runtime_process_monitor import FlextCliUtilitiesRuntimeProcessMonitorMixin
    from ._runtime_process_outcome import FlextCliUtilitiesRuntimeProcessOutcomeMixin
    from ._runtime_process_output import FlextCliUtilitiesRuntimeProcessOutputMixin
    from ._runtime_process_resources import (
        FlextCliUtilitiesRuntimeProcessResourcesMixin,
    )
    from ._runtime_process_start import FlextCliUtilitiesRuntimeProcessStartMixin
    from ._runtime_process_stream import FlextCliUtilitiesRuntimeProcessStreamMixin
    from ._runtime_process_threads import FlextCliUtilitiesRuntimeProcessThreadsMixin
    from ._runtime_process_timing import FlextCliUtilitiesRuntimeProcessTimingMixin
    from ._runtime_process_wait import FlextCliUtilitiesRuntimeProcessWaitMixin
    from ._runtime_run_to_file import FlextCliUtilitiesRuntimeRunToFileMixin
    from ._runtime_windows_job_start import FlextCliUtilitiesRuntimeWindowsJobStartMixin
    from ._runtime_windows_job_state import FlextCliUtilitiesRuntimeWindowsJobStateMixin
    from ._xlxx.xlsx_addresses import FlextCliUtilitiesXlsxAddresses
    from ._xlxx.xlsx_archive import FlextCliUtilitiesXlsxArchive
    from ._xlxx.xlsx_archive_checks import FlextCliUtilitiesXlsxArchiveChecks
    from ._xlxx.xlsx_cells import FlextCliUtilitiesXlsxCells
    from ._xlxx.xlsx_conditional import FlextCliUtilitiesXlsxConditional
    from ._xlxx.xlsx_defined_name_values import FlextCliUtilitiesXlsxDefinedNameValues
    from ._xlxx.xlsx_formula_codec import FlextCliUtilitiesXlsxFormulaCodec
    from ._xlxx.xlsx_layout import FlextCliUtilitiesXlsxLayout
    from ._xlxx.xlsx_protection import FlextCliUtilitiesXlsxProtection
    from ._xlxx.xlsx_recalc import FlextCliUtilitiesXlsxRecalc
    from ._xlxx.xlsx_recalc_evidence import FlextCliUtilitiesXlsxRecalcEvidence
    from ._xlxx.xlsx_renderer import FlextCliUtilitiesXlsxRenderer
    from ._xlxx.xlsx_rules import FlextCliUtilitiesXlsxRules
    from ._xlxx.xlsx_snapshot import FlextCliUtilitiesXlsxSnapshot
    from ._xlxx.xlsx_snapshot_sheet import FlextCliUtilitiesXlsxSnapshotSheet
    from ._xlxx.xlsx_snapshot_structure import FlextCliUtilitiesXlsxSnapshotStructure
    from ._xlxx.xlsx_snapshot_values import FlextCliUtilitiesXlsxSnapshotValues
    from ._xlxx.xlsx_style_builders import FlextCliUtilitiesXlsxStyleBuilders
    from ._xlxx.xlsx_style_catalog import FlextCliUtilitiesXlsxStyleCatalog
    from ._xlxx.xlsx_style_codec import FlextCliUtilitiesXlsxStyleCodec
    from ._xlxx.xlsx_style_readers import FlextCliUtilitiesXlsxStyleReaders
    from ._xlxx.xlsx_tables import FlextCliUtilitiesXlsxTables
    from ._xlxx.xlsx_validations import FlextCliUtilitiesXlsxValidations
    from ._xlxx.xlsx_workbook_io import FlextCliUtilitiesXlsxWorkbookIo
    from ._xlxx.xlsx_workbook_plan import FlextCliUtilitiesXlsxWorkbookPlan
    from ._yaml._convert import FlextCliUtilitiesYamlConvertMixin
    from ._yaml._editing import FlextCliUtilitiesYamlEditingMixin
    from ._yaml._engine import FlextCliUtilitiesYamlEngineMixin
    from .atomic_directory_chain import (
        create_guarded_directory_chain,
        plan_directory_chain,
    )
    from .atomic_directory_cleanup import remove_created_directory
    from .atomic_directory_create import create_guarded_empty_directory
    from .atomic_directory_delete import remove_guarded_empty_directory
    from .atomic_directory_descriptor import (
        create_entry,
        remove_entry,
        rename_entry_noreplace,
        require_create_capabilities,
        require_delete_capabilities,
        require_publish_capabilities,
        require_read_capabilities,
    )
    from .atomic_directory_model import (
        DirectoryPhysicalState,
        from_observed,
        physical_state,
        require_absent,
        require_existing,
        require_observed,
        require_parent,
    )
    from .atomic_directory_noreplace import (
        rename_noreplace,
        require_noreplace_capability,
    )
    from .atomic_directory_publish import publish_guarded_staged_empty_directory
    from .atomic_directory_snapshot import read_authenticated_empty_directory
    from .atomic_directory_state import (
        destination_state,
        initialize_empty_state,
        read_empty_state,
        require_identity,
    )
    from .atomic_file import write_atomic_bytes
    from .atomic_file_cleanup import remove_failed_temporary
    from .atomic_file_delete import remove_guarded_file
    from .atomic_file_descriptor import (
        ParentDescriptor,
        assert_parent_unchanged,
        entry_descriptor,
        entry_stat,
        open_entry,
        parent_descriptor,
        replace_entry,
        require_entry,
        unlink_entry,
    )
    from .atomic_file_durability import sync_parent, sync_replacement
    from .atomic_file_mode import (
        NO_MODE_PRECONDITION,
        assert_observed_mode,
        publication_mode,
        validate_guarded_mode_tuple,
        validate_mode,
        validate_mode_precondition,
    )
    from .atomic_file_model import PhysicalState
    from .atomic_file_path import (
        identity,
        is_reparse_point,
        validate_atomic_path,
        validate_directory_path,
        validate_directory_state,
        validate_parent_path,
    )
    from .atomic_file_publish import publish_guarded_staged_file
    from .atomic_file_publish_checks import (
        require_distinct_inode,
        validate_devices,
        validate_identity,
        validate_publication,
    )
    from .atomic_file_read import read_descriptor_bytes, state_key
    from .atomic_file_snapshot import read_authenticated_state
    from .atomic_file_state import (
        assert_destination_unchanged,
        assert_temporary_owned,
        read_authenticated_bytes,
        validate_precondition,
    )
    from .atomic_file_temporary import (
        create_descriptor,
        require_mode_capability,
        temporary_path,
        write_and_sync,
    )
    from .atomic_parent_descriptor import (
        DirectoryChainInspection,
        PhysicalDirectory,
        inspect_directory_chain,
        physical_directory,
        require_traversal_capabilities,
    )
    from .atomic_parent_failure import preserve_recheck_failure
    from .atomic_tree_cleanup import cleanup_physical_tree_guarded
    from .atomic_tree_descriptor import (
        measure_authenticated_file,
        mount_id,
        require_directory_state,
        require_entry_state,
        require_mount,
        require_same_device,
    )
    from .atomic_tree_inventory import inventory_physical_tree
    from .auth import FlextCliUtilitiesAuth
    from .cmd import FlextCliUtilitiesCmd
    from .commands import FlextCliUtilitiesCommands
    from .config import FlextCliUtilitiesConfig
    from .conversion import FlextCliUtilitiesConversion
    from .docx import FlextCliUtilitiesDocx
    from .env import FlextCliUtilitiesEnv
    from .file_test_helpers import FlextCliUtilitiesFileTestHelpersMixin
    from .files import FlextCliUtilitiesFiles
    from .formatters import FlextCliUtilitiesFormatters
    from .framework import FlextCliUtilitiesFramework
    from .json import FlextCliUtilitiesJson
    from .matching import FlextCliUtilitiesMatching
    from .model_commands import FlextCliUtilitiesModelCommands
    from .output import FlextCliUtilitiesOutput
    from .params import FlextCliUtilitiesParams
    from .pipeline import FlextCliUtilitiesPipeline
    from .pptx import FlextCliUtilitiesPptx
    from .processes import FlextCliUtilitiesProcesses
    from .prompts import FlextCliUtilitiesPrompts
    from .rules import FlextCliUtilitiesRules
    from .runtime import FlextCliUtilitiesRuntime
    from .settings import FlextCliUtilitiesSettings
    from .tables import FlextCliUtilitiesTables
    from .template import FlextCliUtilitiesTemplate
    from .toml import FlextCliUtilitiesToml
    from .validation import FlextCliUtilitiesValidation
    from .xlsx import FlextCliUtilitiesXlsx
    from .yaml import FlextCliUtilitiesYaml
    from .yaml_model import FlextCliUtilitiesYamlModel
__all__: tuple[str, ...] = (
    "NO_MODE_PRECONDITION",
    "DirectoryChainInspection",
    "DirectoryPhysicalState",
    "FlextCliUtilitiesAuth",
    "FlextCliUtilitiesCli",
    "FlextCliUtilitiesCmd",
    "FlextCliUtilitiesCommands",
    "FlextCliUtilitiesConfig",
    "FlextCliUtilitiesConversion",
    "FlextCliUtilitiesDocx",
    "FlextCliUtilitiesDocxReader",
    "FlextCliUtilitiesDocxRenderer",
    "FlextCliUtilitiesEnv",
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
    "FlextCliUtilitiesPptx",
    "FlextCliUtilitiesPptxReader",
    "FlextCliUtilitiesPptxRenderer",
    "FlextCliUtilitiesPptxSerializer",
    "FlextCliUtilitiesProcesses",
    "FlextCliUtilitiesPrompts",
    "FlextCliUtilitiesRules",
    "FlextCliUtilitiesRulesLoadersMixin",
    "FlextCliUtilitiesRulesMatchersMixin",
    "FlextCliUtilitiesRuntime",
    "FlextCliUtilitiesRuntimeCommandsMixin",
    "FlextCliUtilitiesRuntimeProcessCleanupMixin",
    "FlextCliUtilitiesRuntimeProcessExecutionMixin",
    "FlextCliUtilitiesRuntimeProcessGroupMixin",
    "FlextCliUtilitiesRuntimeProcessMonitorMixin",
    "FlextCliUtilitiesRuntimeProcessOutcomeMixin",
    "FlextCliUtilitiesRuntimeProcessOutputMixin",
    "FlextCliUtilitiesRuntimeProcessResourcesMixin",
    "FlextCliUtilitiesRuntimeProcessStartMixin",
    "FlextCliUtilitiesRuntimeProcessStreamMixin",
    "FlextCliUtilitiesRuntimeProcessThreadsMixin",
    "FlextCliUtilitiesRuntimeProcessTimingMixin",
    "FlextCliUtilitiesRuntimeProcessWaitMixin",
    "FlextCliUtilitiesRuntimeRunToFileMixin",
    "FlextCliUtilitiesRuntimeWindowsJobStartMixin",
    "FlextCliUtilitiesRuntimeWindowsJobStateMixin",
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
    "FlextCliUtilitiesXlsxDefinedNameValues",
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
    "ParentDescriptor",
    "PhysicalDirectory",
    "PhysicalState",
    "_docx",
    "_file_test_helper_parts",
    "_files_parts",
    "_json",
    "_options_parts",
    "_pptx",
    "_rules",
    "_toml_parts",
    "_xlxx",
    "_yaml",
    "assert_destination_unchanged",
    "assert_observed_mode",
    "assert_parent_unchanged",
    "assert_temporary_owned",
    "cleanup_physical_tree_guarded",
    "create_descriptor",
    "create_entry",
    "create_guarded_directory_chain",
    "create_guarded_empty_directory",
    "destination_state",
    "entry_descriptor",
    "entry_stat",
    "from_observed",
    "identity",
    "initialize_empty_state",
    "inspect_directory_chain",
    "inventory_physical_tree",
    "is_reparse_point",
    "measure_authenticated_file",
    "mount_id",
    "open_entry",
    "parent_descriptor",
    "physical_directory",
    "physical_state",
    "plan_directory_chain",
    "preserve_recheck_failure",
    "publication_mode",
    "publish_guarded_staged_empty_directory",
    "publish_guarded_staged_file",
    "read_authenticated_bytes",
    "read_authenticated_empty_directory",
    "read_authenticated_state",
    "read_descriptor_bytes",
    "read_empty_state",
    "remove_created_directory",
    "remove_entry",
    "remove_failed_temporary",
    "remove_guarded_empty_directory",
    "remove_guarded_file",
    "rename_entry_noreplace",
    "rename_noreplace",
    "replace_entry",
    "require_absent",
    "require_create_capabilities",
    "require_delete_capabilities",
    "require_directory_state",
    "require_distinct_inode",
    "require_entry",
    "require_entry_state",
    "require_existing",
    "require_identity",
    "require_mode_capability",
    "require_mount",
    "require_noreplace_capability",
    "require_observed",
    "require_parent",
    "require_publish_capabilities",
    "require_read_capabilities",
    "require_same_device",
    "require_traversal_capabilities",
    "state_key",
    "sync_parent",
    "sync_replacement",
    "temporary_path",
    "unlink_entry",
    "validate_atomic_path",
    "validate_devices",
    "validate_directory_path",
    "validate_directory_state",
    "validate_guarded_mode_tuple",
    "validate_identity",
    "validate_mode",
    "validate_mode_precondition",
    "validate_parent_path",
    "validate_precondition",
    "validate_publication",
    "write_and_sync",
    "write_atomic_bytes",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            "._cli_namespace": ("FlextCliUtilitiesCli",),
            "._docx": ("_docx",),
            "._docx._reader": ("FlextCliUtilitiesDocxReader",),
            "._docx._renderer": ("FlextCliUtilitiesDocxRenderer",),
            "._file_test_helper_parts": ("_file_test_helper_parts",),
            "._files_parts": ("_files_parts",),
            "._json": ("_json",),
            "._json._core": ("FlextCliUtilitiesJsonCoreMixin",),
            "._json._navigate": ("FlextCliUtilitiesJsonNavigateMixin",),
            "._options_parts": ("_options_parts",),
            "._options_parts.flextcliutilitiesoptionbuilder_part_01": (
                "FlextCliUtilitiesOptionBuilder",
            ),
            "._options_parts.flextcliutilitiesoptions_part_02": (
                "FlextCliUtilitiesOptions",
            ),
            "._pptx": ("_pptx",),
            "._pptx._reader": ("FlextCliUtilitiesPptxReader",),
            "._pptx._renderer": ("FlextCliUtilitiesPptxRenderer",),
            "._pptx._serializer": ("FlextCliUtilitiesPptxSerializer",),
            "._rules": ("_rules",),
            "._rules._loaders": ("FlextCliUtilitiesRulesLoadersMixin",),
            "._rules._matchers": ("FlextCliUtilitiesRulesMatchersMixin",),
            "._runtime_commands": ("FlextCliUtilitiesRuntimeCommandsMixin",),
            "._runtime_process_cleanup": (
                "FlextCliUtilitiesRuntimeProcessCleanupMixin",
            ),
            "._runtime_process_execution": (
                "FlextCliUtilitiesRuntimeProcessExecutionMixin",
            ),
            "._runtime_process_group": ("FlextCliUtilitiesRuntimeProcessGroupMixin",),
            "._runtime_process_monitor": (
                "FlextCliUtilitiesRuntimeProcessMonitorMixin",
            ),
            "._runtime_process_outcome": (
                "FlextCliUtilitiesRuntimeProcessOutcomeMixin",
            ),
            "._runtime_process_output": ("FlextCliUtilitiesRuntimeProcessOutputMixin",),
            "._runtime_process_resources": (
                "FlextCliUtilitiesRuntimeProcessResourcesMixin",
            ),
            "._runtime_process_start": ("FlextCliUtilitiesRuntimeProcessStartMixin",),
            "._runtime_process_stream": ("FlextCliUtilitiesRuntimeProcessStreamMixin",),
            "._runtime_process_threads": (
                "FlextCliUtilitiesRuntimeProcessThreadsMixin",
            ),
            "._runtime_process_timing": ("FlextCliUtilitiesRuntimeProcessTimingMixin",),
            "._runtime_process_wait": ("FlextCliUtilitiesRuntimeProcessWaitMixin",),
            "._runtime_run_to_file": ("FlextCliUtilitiesRuntimeRunToFileMixin",),
            "._runtime_windows_job_start": (
                "FlextCliUtilitiesRuntimeWindowsJobStartMixin",
            ),
            "._runtime_windows_job_state": (
                "FlextCliUtilitiesRuntimeWindowsJobStateMixin",
            ),
            "._toml_parts": ("_toml_parts",),
            "._xlxx": ("_xlxx",),
            "._xlxx.xlsx_addresses": ("FlextCliUtilitiesXlsxAddresses",),
            "._xlxx.xlsx_archive": ("FlextCliUtilitiesXlsxArchive",),
            "._xlxx.xlsx_archive_checks": ("FlextCliUtilitiesXlsxArchiveChecks",),
            "._xlxx.xlsx_cells": ("FlextCliUtilitiesXlsxCells",),
            "._xlxx.xlsx_conditional": ("FlextCliUtilitiesXlsxConditional",),
            "._xlxx.xlsx_defined_name_values": (
                "FlextCliUtilitiesXlsxDefinedNameValues",
            ),
            "._xlxx.xlsx_formula_codec": ("FlextCliUtilitiesXlsxFormulaCodec",),
            "._xlxx.xlsx_layout": ("FlextCliUtilitiesXlsxLayout",),
            "._xlxx.xlsx_protection": ("FlextCliUtilitiesXlsxProtection",),
            "._xlxx.xlsx_recalc": ("FlextCliUtilitiesXlsxRecalc",),
            "._xlxx.xlsx_recalc_evidence": ("FlextCliUtilitiesXlsxRecalcEvidence",),
            "._xlxx.xlsx_renderer": ("FlextCliUtilitiesXlsxRenderer",),
            "._xlxx.xlsx_rules": ("FlextCliUtilitiesXlsxRules",),
            "._xlxx.xlsx_snapshot": ("FlextCliUtilitiesXlsxSnapshot",),
            "._xlxx.xlsx_snapshot_sheet": ("FlextCliUtilitiesXlsxSnapshotSheet",),
            "._xlxx.xlsx_snapshot_structure": (
                "FlextCliUtilitiesXlsxSnapshotStructure",
            ),
            "._xlxx.xlsx_snapshot_values": ("FlextCliUtilitiesXlsxSnapshotValues",),
            "._xlxx.xlsx_style_builders": ("FlextCliUtilitiesXlsxStyleBuilders",),
            "._xlxx.xlsx_style_catalog": ("FlextCliUtilitiesXlsxStyleCatalog",),
            "._xlxx.xlsx_style_codec": ("FlextCliUtilitiesXlsxStyleCodec",),
            "._xlxx.xlsx_style_readers": ("FlextCliUtilitiesXlsxStyleReaders",),
            "._xlxx.xlsx_tables": ("FlextCliUtilitiesXlsxTables",),
            "._xlxx.xlsx_validations": ("FlextCliUtilitiesXlsxValidations",),
            "._xlxx.xlsx_workbook_io": ("FlextCliUtilitiesXlsxWorkbookIo",),
            "._xlxx.xlsx_workbook_plan": ("FlextCliUtilitiesXlsxWorkbookPlan",),
            "._yaml": ("_yaml",),
            "._yaml._convert": ("FlextCliUtilitiesYamlConvertMixin",),
            "._yaml._editing": ("FlextCliUtilitiesYamlEditingMixin",),
            "._yaml._engine": ("FlextCliUtilitiesYamlEngineMixin",),
            ".atomic_directory_chain": (
                "create_guarded_directory_chain",
                "plan_directory_chain",
            ),
            ".atomic_directory_cleanup": ("remove_created_directory",),
            ".atomic_directory_create": ("create_guarded_empty_directory",),
            ".atomic_directory_delete": ("remove_guarded_empty_directory",),
            ".atomic_directory_descriptor": (
                "create_entry",
                "remove_entry",
                "rename_entry_noreplace",
                "require_create_capabilities",
                "require_delete_capabilities",
                "require_publish_capabilities",
                "require_read_capabilities",
            ),
            ".atomic_directory_model": (
                "DirectoryPhysicalState",
                "from_observed",
                "physical_state",
                "require_absent",
                "require_existing",
                "require_observed",
                "require_parent",
            ),
            ".atomic_directory_noreplace": (
                "rename_noreplace",
                "require_noreplace_capability",
            ),
            ".atomic_directory_publish": ("publish_guarded_staged_empty_directory",),
            ".atomic_directory_snapshot": ("read_authenticated_empty_directory",),
            ".atomic_directory_state": (
                "destination_state",
                "initialize_empty_state",
                "read_empty_state",
                "require_identity",
            ),
            ".atomic_file": ("write_atomic_bytes",),
            ".atomic_file_cleanup": ("remove_failed_temporary",),
            ".atomic_file_delete": ("remove_guarded_file",),
            ".atomic_file_descriptor": (
                "ParentDescriptor",
                "assert_parent_unchanged",
                "entry_descriptor",
                "entry_stat",
                "open_entry",
                "parent_descriptor",
                "replace_entry",
                "require_entry",
                "unlink_entry",
            ),
            ".atomic_file_durability": ("sync_parent", "sync_replacement"),
            ".atomic_file_mode": (
                "NO_MODE_PRECONDITION",
                "assert_observed_mode",
                "publication_mode",
                "validate_guarded_mode_tuple",
                "validate_mode",
                "validate_mode_precondition",
            ),
            ".atomic_file_model": ("PhysicalState",),
            ".atomic_file_path": (
                "identity",
                "is_reparse_point",
                "validate_atomic_path",
                "validate_directory_path",
                "validate_directory_state",
                "validate_parent_path",
            ),
            ".atomic_file_publish": ("publish_guarded_staged_file",),
            ".atomic_file_publish_checks": (
                "require_distinct_inode",
                "validate_devices",
                "validate_identity",
                "validate_publication",
            ),
            ".atomic_file_read": ("read_descriptor_bytes", "state_key"),
            ".atomic_file_snapshot": ("read_authenticated_state",),
            ".atomic_file_state": (
                "assert_destination_unchanged",
                "assert_temporary_owned",
                "read_authenticated_bytes",
                "validate_precondition",
            ),
            ".atomic_file_temporary": (
                "create_descriptor",
                "require_mode_capability",
                "temporary_path",
                "write_and_sync",
            ),
            ".atomic_parent_descriptor": (
                "DirectoryChainInspection",
                "PhysicalDirectory",
                "inspect_directory_chain",
                "physical_directory",
                "require_traversal_capabilities",
            ),
            ".atomic_parent_failure": ("preserve_recheck_failure",),
            ".atomic_tree_cleanup": ("cleanup_physical_tree_guarded",),
            ".atomic_tree_descriptor": (
                "measure_authenticated_file",
                "mount_id",
                "require_directory_state",
                "require_entry_state",
                "require_mount",
                "require_same_device",
            ),
            ".atomic_tree_inventory": ("inventory_physical_tree",),
            ".auth": ("FlextCliUtilitiesAuth",),
            ".cmd": ("FlextCliUtilitiesCmd",),
            ".commands": ("FlextCliUtilitiesCommands",),
            ".config": ("FlextCliUtilitiesConfig",),
            ".conversion": ("FlextCliUtilitiesConversion",),
            ".docx": ("FlextCliUtilitiesDocx",),
            ".env": ("FlextCliUtilitiesEnv",),
            ".file_test_helpers": ("FlextCliUtilitiesFileTestHelpersMixin",),
            ".files": ("FlextCliUtilitiesFiles",),
            ".formatters": ("FlextCliUtilitiesFormatters",),
            ".framework": ("FlextCliUtilitiesFramework",),
            ".json": ("FlextCliUtilitiesJson",),
            ".matching": ("FlextCliUtilitiesMatching",),
            ".model_commands": ("FlextCliUtilitiesModelCommands",),
            ".output": ("FlextCliUtilitiesOutput",),
            ".params": ("FlextCliUtilitiesParams",),
            ".pipeline": ("FlextCliUtilitiesPipeline",),
            ".pptx": ("FlextCliUtilitiesPptx",),
            ".processes": ("FlextCliUtilitiesProcesses",),
            ".prompts": ("FlextCliUtilitiesPrompts",),
            ".rules": ("FlextCliUtilitiesRules",),
            ".runtime": ("FlextCliUtilitiesRuntime",),
            ".settings": ("FlextCliUtilitiesSettings",),
            ".tables": ("FlextCliUtilitiesTables",),
            ".template": ("FlextCliUtilitiesTemplate",),
            ".toml": ("FlextCliUtilitiesToml",),
            ".validation": ("FlextCliUtilitiesValidation",),
            ".xlsx": ("FlextCliUtilitiesXlsx",),
            ".yaml": ("FlextCliUtilitiesYaml",),
            ".yaml_model": ("FlextCliUtilitiesYamlModel",),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

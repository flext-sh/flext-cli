# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities import (
        _docx,
        _file_test_helper_parts,
        _files_parts,
        _json,
        _options_parts,
        _pptx,
        _rules,
        _tables_parts,
        _toml_parts,
        _xlxx,
        _yaml,
    )
    from flext_cli._utilities._cli_namespace import FlextCliUtilitiesCli
    from flext_cli._utilities._docx._reader import FlextCliUtilitiesDocxReader
    from flext_cli._utilities._docx._renderer import FlextCliUtilitiesDocxRenderer
    from flext_cli._utilities._json._core import FlextCliUtilitiesJsonCoreMixin
    from flext_cli._utilities._json._navigate import FlextCliUtilitiesJsonNavigateMixin
    from flext_cli._utilities._options_parts.flextcliutilitiesoptionbuilder_part_01 import (
        FlextCliUtilitiesOptionBuilder,
    )
    from flext_cli._utilities._options_parts.flextcliutilitiesoptions_part_02 import (
        FlextCliUtilitiesOptions,
    )
    from flext_cli._utilities._pptx._reader import FlextCliUtilitiesPptxReader
    from flext_cli._utilities._pptx._renderer import FlextCliUtilitiesPptxRenderer
    from flext_cli._utilities._pptx._serializer import FlextCliUtilitiesPptxSerializer
    from flext_cli._utilities._rules._loaders import FlextCliUtilitiesRulesLoadersMixin
    from flext_cli._utilities._rules._matchers import (
        FlextCliUtilitiesRulesMatchersMixin,
    )
    from flext_cli._utilities._runtime_commands import (
        FlextCliUtilitiesRuntimeCommandsMixin,
    )
    from flext_cli._utilities._runtime_darwin_process_group import (
        FlextCliUtilitiesRuntimeDarwinProcessGroupMixin,
    )
    from flext_cli._utilities._runtime_process_cleanup import (
        FlextCliUtilitiesRuntimeProcessCleanupMixin,
    )
    from flext_cli._utilities._runtime_process_execution import (
        FlextCliUtilitiesRuntimeProcessExecutionMixin,
    )
    from flext_cli._utilities._runtime_process_group import (
        FlextCliUtilitiesRuntimeProcessGroupMixin,
    )
    from flext_cli._utilities._runtime_process_monitor import (
        FlextCliUtilitiesRuntimeProcessMonitorMixin,
    )
    from flext_cli._utilities._runtime_process_outcome import (
        FlextCliUtilitiesRuntimeProcessOutcomeMixin,
    )
    from flext_cli._utilities._runtime_process_output import (
        FlextCliUtilitiesRuntimeProcessOutputMixin,
    )
    from flext_cli._utilities._runtime_process_resources import (
        FlextCliUtilitiesRuntimeProcessResourcesMixin,
    )
    from flext_cli._utilities._runtime_process_start import (
        FlextCliUtilitiesRuntimeProcessStartMixin,
    )
    from flext_cli._utilities._runtime_process_stream import (
        FlextCliUtilitiesRuntimeProcessStreamMixin,
    )
    from flext_cli._utilities._runtime_process_threads import (
        FlextCliUtilitiesRuntimeProcessThreadsMixin,
    )
    from flext_cli._utilities._runtime_process_timing import (
        FlextCliUtilitiesRuntimeProcessTimingMixin,
    )
    from flext_cli._utilities._runtime_process_wait import (
        FlextCliUtilitiesRuntimeProcessWaitMixin,
    )
    from flext_cli._utilities._runtime_run_to_file import (
        FlextCliUtilitiesRuntimeRunToFileMixin,
    )
    from flext_cli._utilities._runtime_windows_job_start import (
        FlextCliUtilitiesRuntimeWindowsJobStartMixin,
    )
    from flext_cli._utilities._runtime_windows_job_state import (
        FlextCliUtilitiesRuntimeWindowsJobStateMixin,
    )
    from flext_cli._utilities._tables_parts.flextcliutilitiestablesrenderer_part_01 import (
        FlextCliUtilitiesTablesRenderer,
    )
    from flext_cli._utilities._xlxx.xlsx_addresses import FlextCliUtilitiesXlsxAddresses
    from flext_cli._utilities._xlxx.xlsx_archive import FlextCliUtilitiesXlsxArchive
    from flext_cli._utilities._xlxx.xlsx_archive_checks import (
        FlextCliUtilitiesXlsxArchiveChecks,
    )
    from flext_cli._utilities._xlxx.xlsx_cells import FlextCliUtilitiesXlsxCells
    from flext_cli._utilities._xlxx.xlsx_conditional import (
        FlextCliUtilitiesXlsxConditional,
    )
    from flext_cli._utilities._xlxx.xlsx_defined_name_values import (
        FlextCliUtilitiesXlsxDefinedNameValues,
    )
    from flext_cli._utilities._xlxx.xlsx_formula_codec import (
        FlextCliUtilitiesXlsxFormulaCodec,
    )
    from flext_cli._utilities._xlxx.xlsx_layout import FlextCliUtilitiesXlsxLayout
    from flext_cli._utilities._xlxx.xlsx_protection import (
        FlextCliUtilitiesXlsxProtection,
    )
    from flext_cli._utilities._xlxx.xlsx_recalc import FlextCliUtilitiesXlsxRecalc
    from flext_cli._utilities._xlxx.xlsx_recalc_evidence import (
        FlextCliUtilitiesXlsxRecalcEvidence,
    )
    from flext_cli._utilities._xlxx.xlsx_renderer import FlextCliUtilitiesXlsxRenderer
    from flext_cli._utilities._xlxx.xlsx_rules import FlextCliUtilitiesXlsxRules
    from flext_cli._utilities._xlxx.xlsx_snapshot import FlextCliUtilitiesXlsxSnapshot
    from flext_cli._utilities._xlxx.xlsx_snapshot_sheet import (
        FlextCliUtilitiesXlsxSnapshotSheet,
    )
    from flext_cli._utilities._xlxx.xlsx_snapshot_structure import (
        FlextCliUtilitiesXlsxSnapshotStructure,
    )
    from flext_cli._utilities._xlxx.xlsx_snapshot_values import (
        FlextCliUtilitiesXlsxSnapshotValues,
    )
    from flext_cli._utilities._xlxx.xlsx_style_builders import (
        FlextCliUtilitiesXlsxStyleBuilders,
    )
    from flext_cli._utilities._xlxx.xlsx_style_catalog import (
        FlextCliUtilitiesXlsxStyleCatalog,
    )
    from flext_cli._utilities._xlxx.xlsx_style_codec import (
        FlextCliUtilitiesXlsxStyleCodec,
    )
    from flext_cli._utilities._xlxx.xlsx_style_readers import (
        FlextCliUtilitiesXlsxStyleReaders,
    )
    from flext_cli._utilities._xlxx.xlsx_tables import FlextCliUtilitiesXlsxTables
    from flext_cli._utilities._xlxx.xlsx_validations import (
        FlextCliUtilitiesXlsxValidations,
    )
    from flext_cli._utilities._xlxx.xlsx_workbook_io import (
        FlextCliUtilitiesXlsxWorkbookIo,
    )
    from flext_cli._utilities._xlxx.xlsx_workbook_plan import (
        FlextCliUtilitiesXlsxWorkbookPlan,
    )
    from flext_cli._utilities._yaml._convert import FlextCliUtilitiesYamlConvertMixin
    from flext_cli._utilities._yaml._editing import FlextCliUtilitiesYamlEditingMixin
    from flext_cli._utilities._yaml._engine import FlextCliUtilitiesYamlEngineMixin
    from flext_cli._utilities.atomic_directory_chain import (
        create_guarded_directory_chain,
        plan_directory_chain,
    )
    from flext_cli._utilities.atomic_directory_cleanup import remove_created_directory
    from flext_cli._utilities.atomic_directory_create import (
        create_guarded_empty_directory,
    )
    from flext_cli._utilities.atomic_directory_delete import (
        remove_guarded_empty_directory,
    )
    from flext_cli._utilities.atomic_directory_descriptor import (
        create_entry,
        remove_entry,
        rename_entry_noreplace,
        require_create_capabilities,
        require_delete_capabilities,
        require_publish_capabilities,
        require_read_capabilities,
    )
    from flext_cli._utilities.atomic_directory_model import (
        DirectoryPhysicalState,
        from_observed,
        physical_state,
        require_absent,
        require_existing,
        require_observed,
        require_parent,
    )
    from flext_cli._utilities.atomic_directory_noreplace import (
        rename_noreplace,
        require_noreplace_capability,
    )
    from flext_cli._utilities.atomic_directory_publish import (
        publish_guarded_staged_empty_directory,
    )
    from flext_cli._utilities.atomic_directory_snapshot import (
        read_authenticated_empty_directory,
    )
    from flext_cli._utilities.atomic_directory_state import (
        destination_state,
        initialize_empty_state,
        read_empty_state,
        require_identity,
    )
    from flext_cli._utilities.atomic_file import write_atomic_bytes
    from flext_cli._utilities.atomic_file_cleanup import remove_failed_temporary
    from flext_cli._utilities.atomic_file_delete import remove_guarded_file
    from flext_cli._utilities.atomic_file_descriptor import (
        ParentDescriptor,
        assert_parent_unchanged,
        close_after_failure,
        entry_descriptor,
        entry_stat,
        open_entry,
        parent_descriptor,
        replace_entry,
        require_entry,
        unlink_entry,
    )
    from flext_cli._utilities.atomic_file_durability import (
        sync_parent,
        sync_replacement,
    )
    from flext_cli._utilities.atomic_file_mode import (
        NO_MODE_PRECONDITION,
        assert_observed_mode,
        publication_mode,
        validate_guarded_mode_tuple,
        validate_mode,
        validate_mode_precondition,
    )
    from flext_cli._utilities.atomic_file_model import PhysicalState
    from flext_cli._utilities.atomic_file_path import (
        identity,
        is_reparse_point,
        resolve_parent_path,
        validate_atomic_path,
        validate_directory_path,
        validate_directory_state,
        validate_parent_path,
    )
    from flext_cli._utilities.atomic_file_publish import publish_guarded_staged_file
    from flext_cli._utilities.atomic_file_publish_checks import (
        require_distinct_inode,
        validate_devices,
        validate_identity,
        validate_publication,
    )
    from flext_cli._utilities.atomic_file_read import read_descriptor_bytes, state_key
    from flext_cli._utilities.atomic_file_snapshot import read_authenticated_state
    from flext_cli._utilities.atomic_file_state import (
        assert_destination_unchanged,
        assert_temporary_owned,
        read_authenticated_bytes,
        validate_precondition,
    )
    from flext_cli._utilities.atomic_file_temporary import (
        create_descriptor,
        require_mode_capability,
        temporary_path,
        write_and_sync,
    )
    from flext_cli._utilities.atomic_parent_descriptor import (
        DirectoryChainInspection,
        PhysicalDirectory,
        inspect_directory_chain,
        physical_directory,
        require_traversal_capabilities,
        verify_lineage,
    )
    from flext_cli._utilities.atomic_parent_failure import preserve_recheck_failure
    from flext_cli._utilities.atomic_symlink_publish import (
        delete_guarded_symlink,
        write_guarded_symlink,
    )
    from flext_cli._utilities.atomic_symlink_state import (
        read_symlink_state,
        require_symlink_state,
        symlink_identity,
    )
    from flext_cli._utilities.atomic_tree_cleanup import cleanup_physical_tree_guarded
    from flext_cli._utilities.atomic_tree_darwin import FlextCliAtomicTreeDarwin
    from flext_cli._utilities.atomic_tree_descriptor import (
        measure_authenticated_file,
        mount_id,
        require_directory_state,
        require_entry_state,
        require_mount,
        require_same_device,
    )
    from flext_cli._utilities.atomic_tree_inventory import inventory_physical_tree
    from flext_cli._utilities.auth import FlextCliUtilitiesAuth
    from flext_cli._utilities.cmd import FlextCliUtilitiesCmd
    from flext_cli._utilities.commands import FlextCliUtilitiesCommands
    from flext_cli._utilities.config import FlextCliUtilitiesConfig
    from flext_cli._utilities.conversion import FlextCliUtilitiesConversion
    from flext_cli._utilities.docx import FlextCliUtilitiesDocx
    from flext_cli._utilities.env import FlextCliUtilitiesEnv
    from flext_cli._utilities.file_test_helpers import (
        FlextCliUtilitiesFileTestHelpersMixin,
    )
    from flext_cli._utilities.files import FlextCliUtilitiesFiles
    from flext_cli._utilities.formatters import FlextCliUtilitiesFormatters
    from flext_cli._utilities.framework import FlextCliUtilitiesFramework
    from flext_cli._utilities.json import FlextCliUtilitiesJson
    from flext_cli._utilities.matching import FlextCliUtilitiesMatching
    from flext_cli._utilities.output import FlextCliUtilitiesOutput
    from flext_cli._utilities.params import FlextCliUtilitiesParams
    from flext_cli._utilities.pipeline import FlextCliUtilitiesPipeline
    from flext_cli._utilities.pptx import FlextCliUtilitiesPptx
    from flext_cli._utilities.processes import FlextCliUtilitiesProcesses
    from flext_cli._utilities.prompts import FlextCliUtilitiesPrompts
    from flext_cli._utilities.report import FlextCliUtilitiesReport
    from flext_cli._utilities.rules import FlextCliUtilitiesRules
    from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime
    from flext_cli._utilities.settings import FlextCliUtilitiesSettings
    from flext_cli._utilities.symlink import FlextCliUtilitiesSymlink
    from flext_cli._utilities.tables import FlextCliUtilitiesTables
    from flext_cli._utilities.template import FlextCliUtilitiesTemplate
    from flext_cli._utilities.toml import FlextCliUtilitiesToml
    from flext_cli._utilities.validation import FlextCliUtilitiesValidation
    from flext_cli._utilities.xlsx import FlextCliUtilitiesXlsx
    from flext_cli._utilities.yaml import FlextCliUtilitiesYaml
    from flext_cli._utilities.yaml_model import FlextCliUtilitiesYamlModel


__all__: tuple[str, ...] = (
    "NO_MODE_PRECONDITION",
    "DirectoryChainInspection",
    "DirectoryPhysicalState",
    "FlextCliAtomicTreeDarwin",
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
    "FlextCliUtilitiesReport",
    "FlextCliUtilitiesRules",
    "FlextCliUtilitiesRulesLoadersMixin",
    "FlextCliUtilitiesRulesMatchersMixin",
    "FlextCliUtilitiesRuntime",
    "FlextCliUtilitiesRuntimeCommandsMixin",
    "FlextCliUtilitiesRuntimeDarwinProcessGroupMixin",
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
    "FlextCliUtilitiesSymlink",
    "FlextCliUtilitiesTables",
    "FlextCliUtilitiesTablesRenderer",
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
    "_tables_parts",
    "_toml_parts",
    "_xlxx",
    "_yaml",
    "assert_destination_unchanged",
    "assert_observed_mode",
    "assert_parent_unchanged",
    "assert_temporary_owned",
    "cleanup_physical_tree_guarded",
    "close_after_failure",
    "create_descriptor",
    "create_entry",
    "create_guarded_directory_chain",
    "create_guarded_empty_directory",
    "delete_guarded_symlink",
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
    "read_symlink_state",
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
    "require_symlink_state",
    "require_traversal_capabilities",
    "resolve_parent_path",
    "state_key",
    "symlink_identity",
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
    "verify_lineage",
    "write_and_sync",
    "write_atomic_bytes",
    "write_guarded_symlink",
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
            "._runtime_darwin_process_group": (
                "FlextCliUtilitiesRuntimeDarwinProcessGroupMixin",
            ),
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
            "._tables_parts": ("_tables_parts",),
            "._tables_parts.flextcliutilitiestablesrenderer_part_01": (
                "FlextCliUtilitiesTablesRenderer",
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
                "close_after_failure",
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
                "resolve_parent_path",
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
                "verify_lineage",
            ),
            ".atomic_parent_failure": ("preserve_recheck_failure",),
            ".atomic_symlink_publish": (
                "delete_guarded_symlink",
                "write_guarded_symlink",
            ),
            ".atomic_symlink_state": (
                "read_symlink_state",
                "require_symlink_state",
                "symlink_identity",
            ),
            ".atomic_tree_cleanup": ("cleanup_physical_tree_guarded",),
            ".atomic_tree_darwin": ("FlextCliAtomicTreeDarwin",),
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
            ".output": ("FlextCliUtilitiesOutput",),
            ".params": ("FlextCliUtilitiesParams",),
            ".pipeline": ("FlextCliUtilitiesPipeline",),
            ".pptx": ("FlextCliUtilitiesPptx",),
            ".processes": ("FlextCliUtilitiesProcesses",),
            ".prompts": ("FlextCliUtilitiesPrompts",),
            ".report": ("FlextCliUtilitiesReport",),
            ".rules": ("FlextCliUtilitiesRules",),
            ".runtime": ("FlextCliUtilitiesRuntime",),
            ".settings": ("FlextCliUtilitiesSettings",),
            ".symlink": ("FlextCliUtilitiesSymlink",),
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
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

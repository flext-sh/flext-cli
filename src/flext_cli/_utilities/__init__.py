# AUTO-GENERATED FILE — Regenerate with: make gen
"""Internal package for utilities.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._docx.reader import FlextCliUtilitiesDocxReader
    from flext_cli._utilities._docx.renderer import FlextCliUtilitiesDocxRenderer
    from flext_cli._utilities._file_test_helper.assertions import (
        FlextCliUtilitiesFileTestHelpersAssertions,
    )
    from flext_cli._utilities._file_test_helper.parsing import (
        FlextCliUtilitiesFileTestHelpersParsing,
    )
    from flext_cli._utilities._files.binary_reads import FlextCliUtilitiesFilesPart03
    from flext_cli._utilities._files.flextcliutilitiesfiles_part_05 import (
        FlextCliUtilitiesFilesPart05,
    )
    from flext_cli._utilities._files.flextcliutilitiesfiles_part_06 import (
        FlextCliUtilitiesFilesPart06,
    )
    from flext_cli._utilities._files.formats import FlextCliUtilitiesFilesPart04
    from flext_cli._utilities._files.text_formats import FlextCliUtilitiesFilesPart01
    from flext_cli._utilities._files.writes import FlextCliUtilitiesFilesPart02
    from flext_cli._utilities._json.core import FlextCliUtilitiesJsonCore
    from flext_cli._utilities._json.navigate import FlextCliUtilitiesJsonNavigate
    from flext_cli._utilities._options.annotations import (
        FlextCliUtilitiesOptionsAnnotations,
    )
    from flext_cli._utilities._options.fields import FlextCliUtilitiesOptionsFields
    from flext_cli._utilities._options.option_builder import (
        FlextCliUtilitiesOptionBuilder,
    )
    from flext_cli._utilities._pptx.reader import FlextCliUtilitiesPptxReader
    from flext_cli._utilities._pptx.renderer import FlextCliUtilitiesPptxRenderer
    from flext_cli._utilities._pptx.serializer import FlextCliUtilitiesPptxSerializer
    from flext_cli._utilities._runtime.commands import FlextCliUtilitiesRuntimeCommands
    from flext_cli._utilities._runtime.darwin_process_group import (
        FlextCliUtilitiesRuntimeDarwinProcessGroup,
    )
    from flext_cli._utilities._runtime.process_cleanup import (
        FlextCliUtilitiesRuntimeProcessCleanup,
    )
    from flext_cli._utilities._runtime.process_execution import (
        FlextCliUtilitiesRuntimeProcessExecution,
    )
    from flext_cli._utilities._runtime.process_group import (
        FlextCliUtilitiesRuntimeProcessGroup,
    )
    from flext_cli._utilities._runtime.process_monitor import (
        FlextCliUtilitiesRuntimeProcessMonitor,
    )
    from flext_cli._utilities._runtime.process_outcome import (
        FlextCliUtilitiesRuntimeProcessOutcome,
    )
    from flext_cli._utilities._runtime.process_output import (
        FlextCliUtilitiesRuntimeProcessOutput,
    )
    from flext_cli._utilities._runtime.process_resources import (
        FlextCliUtilitiesRuntimeProcessResources,
    )
    from flext_cli._utilities._runtime.process_start import (
        FlextCliUtilitiesRuntimeProcessStart,
    )
    from flext_cli._utilities._runtime.process_stream import (
        FlextCliUtilitiesRuntimeProcessStream,
    )
    from flext_cli._utilities._runtime.process_threads import (
        FlextCliUtilitiesRuntimeProcessThreads,
    )
    from flext_cli._utilities._runtime.process_timing import (
        FlextCliUtilitiesRuntimeProcessTiming,
    )
    from flext_cli._utilities._runtime.process_wait import (
        FlextCliUtilitiesRuntimeProcessWait,
    )
    from flext_cli._utilities._runtime.run_to_file import (
        FlextCliUtilitiesRuntimeRunToFile,
    )
    from flext_cli._utilities._runtime.windows_job_start import (
        FlextCliUtilitiesRuntimeWindowsJobStart,
    )
    from flext_cli._utilities._runtime.windows_job_state import (
        FlextCliUtilitiesRuntimeWindowsJobState,
    )
    from flext_cli._utilities._tables.renderer import FlextCliUtilitiesTablesRenderer
    from flext_cli._utilities._toml.flextcliutilitiestoml_part_01 import (
        FlextCliUtilitiesTomlPart01,
    )
    from flext_cli._utilities._toml.flextcliutilitiestoml_part_02 import (
        FlextCliUtilitiesTomlPart02,
    )
    from flext_cli._utilities._toml.flextcliutilitiestoml_part_03 import (
        FlextCliUtilitiesTomlPart03,
    )
    from flext_cli._utilities._toml.flextcliutilitiestoml_part_04 import (
        FlextCliUtilitiesTomlPart04,
    )
    from flext_cli._utilities._toml.flextcliutilitiestoml_part_05 import (
        FlextCliUtilitiesTomlPart05,
    )
    from flext_cli._utilities._toml.flextcliutilitiestoml_part_06 import (
        FlextCliUtilitiesTomlPart06,
    )
    from flext_cli._utilities._toml.flextcliutilitiestoml_part_07 import (
        FlextCliUtilitiesTomlPart07,
    )
    from flext_cli._utilities._xlsx.xlsx_addresses import FlextCliUtilitiesXlsxAddresses
    from flext_cli._utilities._xlsx.xlsx_archive import FlextCliUtilitiesXlsxArchive
    from flext_cli._utilities._xlsx.xlsx_archive_checks import (
        FlextCliUtilitiesXlsxArchiveChecks,
    )
    from flext_cli._utilities._xlsx.xlsx_cells import FlextCliUtilitiesXlsxCells
    from flext_cli._utilities._xlsx.xlsx_conditional import (
        FlextCliUtilitiesXlsxConditional,
    )
    from flext_cli._utilities._xlsx.xlsx_defined_name_values import (
        FlextCliUtilitiesXlsxDefinedNameValues,
    )
    from flext_cli._utilities._xlsx.xlsx_formula_codec import (
        FlextCliUtilitiesXlsxFormulaCodec,
    )
    from flext_cli._utilities._xlsx.xlsx_layout import FlextCliUtilitiesXlsxLayout
    from flext_cli._utilities._xlsx.xlsx_protection import (
        FlextCliUtilitiesXlsxProtection,
    )
    from flext_cli._utilities._xlsx.xlsx_recalc import FlextCliUtilitiesXlsxRecalc
    from flext_cli._utilities._xlsx.xlsx_recalc_evidence import (
        FlextCliUtilitiesXlsxRecalcEvidence,
    )
    from flext_cli._utilities._xlsx.xlsx_renderer import FlextCliUtilitiesXlsxRenderer
    from flext_cli._utilities._xlsx.xlsx_rules import FlextCliUtilitiesXlsxRules
    from flext_cli._utilities._xlsx.xlsx_snapshot import FlextCliUtilitiesXlsxSnapshot
    from flext_cli._utilities._xlsx.xlsx_snapshot_sheet import (
        FlextCliUtilitiesXlsxSnapshotSheet,
    )
    from flext_cli._utilities._xlsx.xlsx_snapshot_structure import (
        FlextCliUtilitiesXlsxSnapshotStructure,
    )
    from flext_cli._utilities._xlsx.xlsx_snapshot_values import (
        FlextCliUtilitiesXlsxSnapshotValues,
    )
    from flext_cli._utilities._xlsx.xlsx_style_builders import (
        FlextCliUtilitiesXlsxStyleBuilders,
    )
    from flext_cli._utilities._xlsx.xlsx_style_catalog import (
        FlextCliUtilitiesXlsxStyleCatalog,
    )
    from flext_cli._utilities._xlsx.xlsx_style_codec import (
        FlextCliUtilitiesXlsxStyleCodec,
    )
    from flext_cli._utilities._xlsx.xlsx_style_readers import (
        FlextCliUtilitiesXlsxStyleReaders,
    )
    from flext_cli._utilities._xlsx.xlsx_tables import FlextCliUtilitiesXlsxTables
    from flext_cli._utilities._xlsx.xlsx_validations import (
        FlextCliUtilitiesXlsxValidations,
    )
    from flext_cli._utilities._xlsx.xlsx_workbook_io import (
        FlextCliUtilitiesXlsxWorkbookIo,
    )
    from flext_cli._utilities._xlsx.xlsx_workbook_plan import (
        FlextCliUtilitiesXlsxWorkbookPlan,
    )
    from flext_cli._utilities._yaml.convert import FlextCliUtilitiesYamlConvert
    from flext_cli._utilities._yaml.editing import FlextCliUtilitiesYamlEditing
    from flext_cli._utilities._yaml.engine import FlextCliUtilitiesYamlEngine
    from flext_cli._utilities.atomic_directory_chain import (
        FlextCliUtilitiesAtomicDirectoryChain,
    )
    from flext_cli._utilities.atomic_directory_cleanup import (
        FlextCliUtilitiesAtomicDirectoryCleanup,
    )
    from flext_cli._utilities.atomic_directory_create import (
        FlextCliUtilitiesAtomicDirectoryCreate,
    )
    from flext_cli._utilities.atomic_directory_delete import (
        FlextCliUtilitiesAtomicDirectoryDelete,
    )
    from flext_cli._utilities.atomic_directory_descriptor import (
        FlextCliUtilitiesAtomicDirectoryDescriptor,
    )
    from flext_cli._utilities.atomic_directory_model import (
        FlextCliUtilitiesAtomicDirectoryModel,
    )
    from flext_cli._utilities.atomic_directory_noreplace import (
        FlextCliUtilitiesAtomicDirectoryNoreplace,
    )
    from flext_cli._utilities.atomic_directory_publish import (
        FlextCliUtilitiesAtomicDirectoryPublish,
    )
    from flext_cli._utilities.atomic_directory_snapshot import (
        FlextCliUtilitiesAtomicDirectorySnapshot,
    )
    from flext_cli._utilities.atomic_directory_state import (
        FlextCliUtilitiesAtomicDirectoryState,
    )
    from flext_cli._utilities.atomic_file import FlextCliUtilitiesAtomicFile
    from flext_cli._utilities.atomic_file_cleanup import (
        FlextCliUtilitiesAtomicFileCleanup,
    )
    from flext_cli._utilities.atomic_file_delete import (
        FlextCliUtilitiesAtomicFileDelete,
    )
    from flext_cli._utilities.atomic_file_descriptor import (
        FlextCliUtilitiesAtomicFileDescriptor,
    )
    from flext_cli._utilities.atomic_file_durability import (
        FlextCliUtilitiesAtomicFileDurability,
    )
    from flext_cli._utilities.atomic_file_mode import FlextCliUtilitiesAtomicFileMode
    from flext_cli._utilities.atomic_file_model import FlextCliUtilitiesAtomicFileModel
    from flext_cli._utilities.atomic_file_path import FlextCliUtilitiesAtomicFilePath
    from flext_cli._utilities.atomic_file_publish import (
        FlextCliUtilitiesAtomicFilePublish,
    )
    from flext_cli._utilities.atomic_file_publish_checks import (
        FlextCliUtilitiesAtomicFilePublishChecks,
    )
    from flext_cli._utilities.atomic_file_read import FlextCliUtilitiesAtomicFileRead
    from flext_cli._utilities.atomic_file_snapshot import (
        FlextCliUtilitiesAtomicFileSnapshot,
    )
    from flext_cli._utilities.atomic_file_state import FlextCliUtilitiesAtomicFileState
    from flext_cli._utilities.atomic_file_temporary import (
        FlextCliUtilitiesAtomicFileTemporary,
    )
    from flext_cli._utilities.atomic_parent_descriptor import (
        FlextCliUtilitiesAtomicParentDescriptor,
    )
    from flext_cli._utilities.atomic_parent_failure import (
        FlextCliUtilitiesAtomicParentFailure,
    )
    from flext_cli._utilities.atomic_symlink_publish import (
        FlextCliUtilitiesAtomicSymlinkPublish,
    )
    from flext_cli._utilities.atomic_symlink_state import (
        FlextCliUtilitiesAtomicSymlinkState,
    )
    from flext_cli._utilities.atomic_tree_cleanup import (
        FlextCliUtilitiesAtomicTreeCleanup,
    )
    from flext_cli._utilities.atomic_tree_darwin import FlextCliAtomicTreeDarwin
    from flext_cli._utilities.atomic_tree_descriptor import (
        FlextCliUtilitiesAtomicTreeDescriptor,
    )
    from flext_cli._utilities.atomic_tree_inventory import (
        FlextCliUtilitiesAtomicTreeInventory,
    )
    from flext_cli._utilities.auth import FlextCliUtilitiesAuth
    from flext_cli._utilities.base import FlextCliUtilitiesBase
    from flext_cli._utilities.cli_namespace import FlextCliUtilitiesCli
    from flext_cli._utilities.cmd import FlextCliUtilitiesCmd
    from flext_cli._utilities.commands import FlextCliUtilitiesCommands
    from flext_cli._utilities.config import FlextCliUtilitiesConfig
    from flext_cli._utilities.conversion import FlextCliUtilitiesConversion
    from flext_cli._utilities.dag import FlextCliUtilitiesDag
    from flext_cli._utilities.docx import FlextCliUtilitiesDocx
    from flext_cli._utilities.env import FlextCliUtilitiesEnv
    from flext_cli._utilities.file_changes import FlextCliUtilitiesFileChanges
    from flext_cli._utilities.file_test_helpers import FlextCliUtilitiesFileTestHelpers
    from flext_cli._utilities.files import FlextCliUtilitiesFiles
    from flext_cli._utilities.formatters import FlextCliUtilitiesFormatters
    from flext_cli._utilities.framework import FlextCliUtilitiesFramework
    from flext_cli._utilities.json import FlextCliUtilitiesJson
    from flext_cli._utilities.markdown import FlextCliUtilitiesMarkdown
    from flext_cli._utilities.matching import FlextCliUtilitiesMatching
    from flext_cli._utilities.native_runtime import (
        RuntimeSpawnOptions,
        TimeoutExpired,
        spawn_streamed_process,
        streamed_creation_flags,
    )
    from flext_cli._utilities.output import FlextCliUtilitiesOutput
    from flext_cli._utilities.output_payloads import FlextCliUtilitiesOutputPayloads
    from flext_cli._utilities.params import FlextCliUtilitiesParams
    from flext_cli._utilities.pipeline import FlextCliUtilitiesPipeline
    from flext_cli._utilities.pptx import FlextCliUtilitiesPptx
    from flext_cli._utilities.processes import FlextCliUtilitiesProcesses
    from flext_cli._utilities.prompts import FlextCliUtilitiesPrompts
    from flext_cli._utilities.report import FlextCliUtilitiesReport
    from flext_cli._utilities.runtime import FlextCliUtilitiesRuntime
    from flext_cli._utilities.settings import FlextCliUtilitiesSettings
    from flext_cli._utilities.tables import FlextCliUtilitiesTables
    from flext_cli._utilities.template import FlextCliUtilitiesTemplate
    from flext_cli._utilities.toml import FlextCliUtilitiesToml
    from flext_cli._utilities.validation import FlextCliUtilitiesValidation
    from flext_cli._utilities.xlsx import FlextCliUtilitiesXlsx
    from flext_cli._utilities.yaml import FlextCliUtilitiesYaml


__all__: tuple[str, ...] = (
    "FlextCliAtomicTreeDarwin",
    "FlextCliUtilitiesAtomicDirectoryChain",
    "FlextCliUtilitiesAtomicDirectoryCleanup",
    "FlextCliUtilitiesAtomicDirectoryCreate",
    "FlextCliUtilitiesAtomicDirectoryDelete",
    "FlextCliUtilitiesAtomicDirectoryDescriptor",
    "FlextCliUtilitiesAtomicDirectoryModel",
    "FlextCliUtilitiesAtomicDirectoryNoreplace",
    "FlextCliUtilitiesAtomicDirectoryPublish",
    "FlextCliUtilitiesAtomicDirectorySnapshot",
    "FlextCliUtilitiesAtomicDirectoryState",
    "FlextCliUtilitiesAtomicFile",
    "FlextCliUtilitiesAtomicFileCleanup",
    "FlextCliUtilitiesAtomicFileDelete",
    "FlextCliUtilitiesAtomicFileDescriptor",
    "FlextCliUtilitiesAtomicFileDurability",
    "FlextCliUtilitiesAtomicFileMode",
    "FlextCliUtilitiesAtomicFileModel",
    "FlextCliUtilitiesAtomicFilePath",
    "FlextCliUtilitiesAtomicFilePublish",
    "FlextCliUtilitiesAtomicFilePublishChecks",
    "FlextCliUtilitiesAtomicFileRead",
    "FlextCliUtilitiesAtomicFileSnapshot",
    "FlextCliUtilitiesAtomicFileState",
    "FlextCliUtilitiesAtomicFileTemporary",
    "FlextCliUtilitiesAtomicParentDescriptor",
    "FlextCliUtilitiesAtomicParentFailure",
    "FlextCliUtilitiesAtomicSymlinkPublish",
    "FlextCliUtilitiesAtomicSymlinkState",
    "FlextCliUtilitiesAtomicTreeCleanup",
    "FlextCliUtilitiesAtomicTreeDescriptor",
    "FlextCliUtilitiesAtomicTreeInventory",
    "FlextCliUtilitiesAuth",
    "FlextCliUtilitiesBase",
    "FlextCliUtilitiesCli",
    "FlextCliUtilitiesCmd",
    "FlextCliUtilitiesCommands",
    "FlextCliUtilitiesConfig",
    "FlextCliUtilitiesConversion",
    "FlextCliUtilitiesDag",
    "FlextCliUtilitiesDocx",
    "FlextCliUtilitiesDocxReader",
    "FlextCliUtilitiesDocxRenderer",
    "FlextCliUtilitiesEnv",
    "FlextCliUtilitiesFileChanges",
    "FlextCliUtilitiesFileTestHelpers",
    "FlextCliUtilitiesFileTestHelpersAssertions",
    "FlextCliUtilitiesFileTestHelpersParsing",
    "FlextCliUtilitiesFiles",
    "FlextCliUtilitiesFilesPart01",
    "FlextCliUtilitiesFilesPart02",
    "FlextCliUtilitiesFilesPart03",
    "FlextCliUtilitiesFilesPart04",
    "FlextCliUtilitiesFilesPart05",
    "FlextCliUtilitiesFilesPart06",
    "FlextCliUtilitiesFormatters",
    "FlextCliUtilitiesFramework",
    "FlextCliUtilitiesJson",
    "FlextCliUtilitiesJsonCore",
    "FlextCliUtilitiesJsonNavigate",
    "FlextCliUtilitiesMarkdown",
    "FlextCliUtilitiesMatching",
    "FlextCliUtilitiesOptionBuilder",
    "FlextCliUtilitiesOptionsAnnotations",
    "FlextCliUtilitiesOptionsFields",
    "FlextCliUtilitiesOutput",
    "FlextCliUtilitiesOutputPayloads",
    "FlextCliUtilitiesParams",
    "FlextCliUtilitiesPipeline",
    "FlextCliUtilitiesPptx",
    "FlextCliUtilitiesPptxReader",
    "FlextCliUtilitiesPptxRenderer",
    "FlextCliUtilitiesPptxSerializer",
    "FlextCliUtilitiesProcesses",
    "FlextCliUtilitiesPrompts",
    "FlextCliUtilitiesReport",
    "FlextCliUtilitiesRuntime",
    "FlextCliUtilitiesRuntimeCommands",
    "FlextCliUtilitiesRuntimeDarwinProcessGroup",
    "FlextCliUtilitiesRuntimeProcessCleanup",
    "FlextCliUtilitiesRuntimeProcessExecution",
    "FlextCliUtilitiesRuntimeProcessGroup",
    "FlextCliUtilitiesRuntimeProcessMonitor",
    "FlextCliUtilitiesRuntimeProcessOutcome",
    "FlextCliUtilitiesRuntimeProcessOutput",
    "FlextCliUtilitiesRuntimeProcessResources",
    "FlextCliUtilitiesRuntimeProcessStart",
    "FlextCliUtilitiesRuntimeProcessStream",
    "FlextCliUtilitiesRuntimeProcessThreads",
    "FlextCliUtilitiesRuntimeProcessTiming",
    "FlextCliUtilitiesRuntimeProcessWait",
    "FlextCliUtilitiesRuntimeRunToFile",
    "FlextCliUtilitiesRuntimeWindowsJobStart",
    "FlextCliUtilitiesRuntimeWindowsJobState",
    "FlextCliUtilitiesSettings",
    "FlextCliUtilitiesTables",
    "FlextCliUtilitiesTablesRenderer",
    "FlextCliUtilitiesTemplate",
    "FlextCliUtilitiesToml",
    "FlextCliUtilitiesTomlPart01",
    "FlextCliUtilitiesTomlPart02",
    "FlextCliUtilitiesTomlPart03",
    "FlextCliUtilitiesTomlPart04",
    "FlextCliUtilitiesTomlPart05",
    "FlextCliUtilitiesTomlPart06",
    "FlextCliUtilitiesTomlPart07",
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
    "FlextCliUtilitiesYamlConvert",
    "FlextCliUtilitiesYamlEditing",
    "FlextCliUtilitiesYamlEngine",
    "RuntimeSpawnOptions",
    "TimeoutExpired",
    "spawn_streamed_process",
    "streamed_creation_flags",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliAtomicTreeDarwin": ".atomic_tree_darwin",
        "FlextCliUtilitiesAtomicDirectoryChain": ".atomic_directory_chain",
        "FlextCliUtilitiesAtomicDirectoryCleanup": ".atomic_directory_cleanup",
        "FlextCliUtilitiesAtomicDirectoryCreate": ".atomic_directory_create",
        "FlextCliUtilitiesAtomicDirectoryDelete": ".atomic_directory_delete",
        "FlextCliUtilitiesAtomicDirectoryDescriptor": ".atomic_directory_descriptor",
        "FlextCliUtilitiesAtomicDirectoryModel": ".atomic_directory_model",
        "FlextCliUtilitiesAtomicDirectoryNoreplace": ".atomic_directory_noreplace",
        "FlextCliUtilitiesAtomicDirectoryPublish": ".atomic_directory_publish",
        "FlextCliUtilitiesAtomicDirectorySnapshot": ".atomic_directory_snapshot",
        "FlextCliUtilitiesAtomicDirectoryState": ".atomic_directory_state",
        "FlextCliUtilitiesAtomicFile": ".atomic_file",
        "FlextCliUtilitiesAtomicFileCleanup": ".atomic_file_cleanup",
        "FlextCliUtilitiesAtomicFileDelete": ".atomic_file_delete",
        "FlextCliUtilitiesAtomicFileDescriptor": ".atomic_file_descriptor",
        "FlextCliUtilitiesAtomicFileDurability": ".atomic_file_durability",
        "FlextCliUtilitiesAtomicFileMode": ".atomic_file_mode",
        "FlextCliUtilitiesAtomicFileModel": ".atomic_file_model",
        "FlextCliUtilitiesAtomicFilePath": ".atomic_file_path",
        "FlextCliUtilitiesAtomicFilePublish": ".atomic_file_publish",
        "FlextCliUtilitiesAtomicFilePublishChecks": ".atomic_file_publish_checks",
        "FlextCliUtilitiesAtomicFileRead": ".atomic_file_read",
        "FlextCliUtilitiesAtomicFileSnapshot": ".atomic_file_snapshot",
        "FlextCliUtilitiesAtomicFileState": ".atomic_file_state",
        "FlextCliUtilitiesAtomicFileTemporary": ".atomic_file_temporary",
        "FlextCliUtilitiesAtomicParentDescriptor": ".atomic_parent_descriptor",
        "FlextCliUtilitiesAtomicParentFailure": ".atomic_parent_failure",
        "FlextCliUtilitiesAtomicSymlinkPublish": ".atomic_symlink_publish",
        "FlextCliUtilitiesAtomicSymlinkState": ".atomic_symlink_state",
        "FlextCliUtilitiesAtomicTreeCleanup": ".atomic_tree_cleanup",
        "FlextCliUtilitiesAtomicTreeDescriptor": ".atomic_tree_descriptor",
        "FlextCliUtilitiesAtomicTreeInventory": ".atomic_tree_inventory",
        "FlextCliUtilitiesAuth": ".auth",
        "FlextCliUtilitiesBase": ".base",
        "FlextCliUtilitiesCli": ".cli_namespace",
        "FlextCliUtilitiesCmd": ".cmd",
        "FlextCliUtilitiesCommands": ".commands",
        "FlextCliUtilitiesConfig": ".config",
        "FlextCliUtilitiesConversion": ".conversion",
        "FlextCliUtilitiesDag": ".dag",
        "FlextCliUtilitiesDocx": ".docx",
        "FlextCliUtilitiesDocxReader": "._docx.reader",
        "FlextCliUtilitiesDocxRenderer": "._docx.renderer",
        "FlextCliUtilitiesEnv": ".env",
        "FlextCliUtilitiesFileChanges": ".file_changes",
        "FlextCliUtilitiesFileTestHelpersAssertions": "._file_test_helper.assertions",
        "FlextCliUtilitiesFileTestHelpers": ".file_test_helpers",
        "FlextCliUtilitiesFileTestHelpersParsing": "._file_test_helper.parsing",
        "FlextCliUtilitiesFiles": ".files",
        "FlextCliUtilitiesFilesPart01": "._files.text_formats",
        "FlextCliUtilitiesFilesPart02": "._files.writes",
        "FlextCliUtilitiesFilesPart03": "._files.binary_reads",
        "FlextCliUtilitiesFilesPart04": "._files.formats",
        "FlextCliUtilitiesFilesPart05": "._files.flextcliutilitiesfiles_part_05",
        "FlextCliUtilitiesFilesPart06": "._files.flextcliutilitiesfiles_part_06",
        "FlextCliUtilitiesFormatters": ".formatters",
        "FlextCliUtilitiesFramework": ".framework",
        "FlextCliUtilitiesJson": ".json",
        "FlextCliUtilitiesJsonCore": "._json.core",
        "FlextCliUtilitiesJsonNavigate": "._json.navigate",
        "FlextCliUtilitiesMarkdown": ".markdown",
        "FlextCliUtilitiesMatching": ".matching",
        "FlextCliUtilitiesOptionBuilder": "._options.option_builder",
        "FlextCliUtilitiesOptionsAnnotations": "._options.annotations",
        "FlextCliUtilitiesOptionsFields": "._options.fields",
        "FlextCliUtilitiesOutput": ".output",
        "FlextCliUtilitiesOutputPayloads": ".output_payloads",
        "FlextCliUtilitiesParams": ".params",
        "FlextCliUtilitiesPipeline": ".pipeline",
        "FlextCliUtilitiesPptx": ".pptx",
        "FlextCliUtilitiesPptxReader": "._pptx.reader",
        "FlextCliUtilitiesPptxRenderer": "._pptx.renderer",
        "FlextCliUtilitiesPptxSerializer": "._pptx.serializer",
        "FlextCliUtilitiesProcesses": ".processes",
        "FlextCliUtilitiesPrompts": ".prompts",
        "FlextCliUtilitiesReport": ".report",
        "FlextCliUtilitiesRuntime": ".runtime",
        "FlextCliUtilitiesRuntimeCommands": "._runtime.commands",
        "FlextCliUtilitiesRuntimeDarwinProcessGroup": "._runtime.darwin_process_group",
        "FlextCliUtilitiesRuntimeProcessCleanup": "._runtime.process_cleanup",
        "FlextCliUtilitiesRuntimeProcessExecution": "._runtime.process_execution",
        "FlextCliUtilitiesRuntimeProcessGroup": "._runtime.process_group",
        "FlextCliUtilitiesRuntimeProcessMonitor": "._runtime.process_monitor",
        "FlextCliUtilitiesRuntimeProcessOutcome": "._runtime.process_outcome",
        "FlextCliUtilitiesRuntimeProcessOutput": "._runtime.process_output",
        "FlextCliUtilitiesRuntimeProcessResources": "._runtime.process_resources",
        "FlextCliUtilitiesRuntimeProcessStart": "._runtime.process_start",
        "FlextCliUtilitiesRuntimeProcessStream": "._runtime.process_stream",
        "FlextCliUtilitiesRuntimeProcessThreads": "._runtime.process_threads",
        "FlextCliUtilitiesRuntimeProcessTiming": "._runtime.process_timing",
        "FlextCliUtilitiesRuntimeProcessWait": "._runtime.process_wait",
        "FlextCliUtilitiesRuntimeRunToFile": "._runtime.run_to_file",
        "FlextCliUtilitiesRuntimeWindowsJobStart": "._runtime.windows_job_start",
        "FlextCliUtilitiesRuntimeWindowsJobState": "._runtime.windows_job_state",
        "FlextCliUtilitiesSettings": ".settings",
        "FlextCliUtilitiesTables": ".tables",
        "FlextCliUtilitiesTablesRenderer": "._tables.renderer",
        "FlextCliUtilitiesTemplate": ".template",
        "FlextCliUtilitiesToml": ".toml",
        "FlextCliUtilitiesTomlPart01": "._toml.flextcliutilitiestoml_part_01",
        "FlextCliUtilitiesTomlPart02": "._toml.flextcliutilitiestoml_part_02",
        "FlextCliUtilitiesTomlPart03": "._toml.flextcliutilitiestoml_part_03",
        "FlextCliUtilitiesTomlPart04": "._toml.flextcliutilitiestoml_part_04",
        "FlextCliUtilitiesTomlPart05": "._toml.flextcliutilitiestoml_part_05",
        "FlextCliUtilitiesTomlPart06": "._toml.flextcliutilitiestoml_part_06",
        "FlextCliUtilitiesTomlPart07": "._toml.flextcliutilitiestoml_part_07",
        "FlextCliUtilitiesValidation": ".validation",
        "FlextCliUtilitiesXlsx": ".xlsx",
        "FlextCliUtilitiesXlsxAddresses": "._xlsx.xlsx_addresses",
        "FlextCliUtilitiesXlsxArchive": "._xlsx.xlsx_archive",
        "FlextCliUtilitiesXlsxArchiveChecks": "._xlsx.xlsx_archive_checks",
        "FlextCliUtilitiesXlsxCells": "._xlsx.xlsx_cells",
        "FlextCliUtilitiesXlsxConditional": "._xlsx.xlsx_conditional",
        "FlextCliUtilitiesXlsxDefinedNameValues": "._xlsx.xlsx_defined_name_values",
        "FlextCliUtilitiesXlsxFormulaCodec": "._xlsx.xlsx_formula_codec",
        "FlextCliUtilitiesXlsxLayout": "._xlsx.xlsx_layout",
        "FlextCliUtilitiesXlsxProtection": "._xlsx.xlsx_protection",
        "FlextCliUtilitiesXlsxRecalc": "._xlsx.xlsx_recalc",
        "FlextCliUtilitiesXlsxRecalcEvidence": "._xlsx.xlsx_recalc_evidence",
        "FlextCliUtilitiesXlsxRenderer": "._xlsx.xlsx_renderer",
        "FlextCliUtilitiesXlsxRules": "._xlsx.xlsx_rules",
        "FlextCliUtilitiesXlsxSnapshot": "._xlsx.xlsx_snapshot",
        "FlextCliUtilitiesXlsxSnapshotSheet": "._xlsx.xlsx_snapshot_sheet",
        "FlextCliUtilitiesXlsxSnapshotStructure": "._xlsx.xlsx_snapshot_structure",
        "FlextCliUtilitiesXlsxSnapshotValues": "._xlsx.xlsx_snapshot_values",
        "FlextCliUtilitiesXlsxStyleBuilders": "._xlsx.xlsx_style_builders",
        "FlextCliUtilitiesXlsxStyleCatalog": "._xlsx.xlsx_style_catalog",
        "FlextCliUtilitiesXlsxStyleCodec": "._xlsx.xlsx_style_codec",
        "FlextCliUtilitiesXlsxStyleReaders": "._xlsx.xlsx_style_readers",
        "FlextCliUtilitiesXlsxTables": "._xlsx.xlsx_tables",
        "FlextCliUtilitiesXlsxValidations": "._xlsx.xlsx_validations",
        "FlextCliUtilitiesXlsxWorkbookIo": "._xlsx.xlsx_workbook_io",
        "FlextCliUtilitiesXlsxWorkbookPlan": "._xlsx.xlsx_workbook_plan",
        "FlextCliUtilitiesYaml": ".yaml",
        "FlextCliUtilitiesYamlConvert": "._yaml.convert",
        "FlextCliUtilitiesYamlEditing": "._yaml.editing",
        "FlextCliUtilitiesYamlEngine": "._yaml.engine",
        "RuntimeSpawnOptions": ".native_runtime",
        "TimeoutExpired": ".native_runtime",
        "spawn_streamed_process": ".native_runtime",
        "streamed_creation_flags": ".native_runtime",
    }),
    public_exports=__all__,
)

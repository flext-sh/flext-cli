# AUTO-GENERATED FILE — Regenerate with: make gen
"""Internal package for utilities.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
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
    from flext_cli._utilities.file_test_helpers import (
        FlextCliUtilitiesFileTestHelpersMixin,
    )
    from flext_cli._utilities.files import FlextCliUtilitiesFiles
    from flext_cli._utilities.formatters import FlextCliUtilitiesFormatters
    from flext_cli._utilities.framework import FlextCliUtilitiesFramework
    from flext_cli._utilities.json import FlextCliUtilitiesJson
    from flext_cli._utilities.markdown import FlextCliUtilitiesMarkdown
    from flext_cli._utilities.matching import FlextCliUtilitiesMatching
    from flext_cli._utilities.native_runtime import RuntimeSpawnOptions
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
    "FlextCliUtilitiesEnv",
    "FlextCliUtilitiesFileChanges",
    "FlextCliUtilitiesFileTestHelpersMixin",
    "FlextCliUtilitiesFiles",
    "FlextCliUtilitiesFormatters",
    "FlextCliUtilitiesFramework",
    "FlextCliUtilitiesJson",
    "FlextCliUtilitiesMarkdown",
    "FlextCliUtilitiesMatching",
    "FlextCliUtilitiesOutput",
    "FlextCliUtilitiesOutputPayloads",
    "FlextCliUtilitiesParams",
    "FlextCliUtilitiesPipeline",
    "FlextCliUtilitiesPptx",
    "FlextCliUtilitiesProcesses",
    "FlextCliUtilitiesPrompts",
    "FlextCliUtilitiesReport",
    "FlextCliUtilitiesRuntime",
    "FlextCliUtilitiesSettings",
    "FlextCliUtilitiesTables",
    "FlextCliUtilitiesTemplate",
    "FlextCliUtilitiesToml",
    "FlextCliUtilitiesValidation",
    "FlextCliUtilitiesXlsx",
    "FlextCliUtilitiesYaml",
    "RuntimeSpawnOptions",
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
        "FlextCliUtilitiesEnv": ".env",
        "FlextCliUtilitiesFileChanges": ".file_changes",
        "FlextCliUtilitiesFileTestHelpersMixin": ".file_test_helpers",
        "FlextCliUtilitiesFiles": ".files",
        "FlextCliUtilitiesFormatters": ".formatters",
        "FlextCliUtilitiesFramework": ".framework",
        "FlextCliUtilitiesJson": ".json",
        "FlextCliUtilitiesMarkdown": ".markdown",
        "FlextCliUtilitiesMatching": ".matching",
        "FlextCliUtilitiesOutput": ".output",
        "FlextCliUtilitiesOutputPayloads": ".output_payloads",
        "FlextCliUtilitiesParams": ".params",
        "FlextCliUtilitiesPipeline": ".pipeline",
        "FlextCliUtilitiesPptx": ".pptx",
        "FlextCliUtilitiesProcesses": ".processes",
        "FlextCliUtilitiesPrompts": ".prompts",
        "FlextCliUtilitiesReport": ".report",
        "FlextCliUtilitiesRuntime": ".runtime",
        "FlextCliUtilitiesSettings": ".settings",
        "FlextCliUtilitiesTables": ".tables",
        "FlextCliUtilitiesTemplate": ".template",
        "FlextCliUtilitiesToml": ".toml",
        "FlextCliUtilitiesValidation": ".validation",
        "FlextCliUtilitiesXlsx": ".xlsx",
        "FlextCliUtilitiesYaml": ".yaml",
        "RuntimeSpawnOptions": ".native_runtime",
    }),
    public_exports=__all__,
)

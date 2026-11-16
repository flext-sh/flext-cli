# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import defer_lazy_bases, install_lazy_exports

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
    from flext_cli._utilities.atomic_tree_darwin import (
        FlextCliUtilitiesAtomicTreeDarwin,
    )
    from flext_cli._utilities.atomic_tree_descriptor import (
        FlextCliUtilitiesAtomicTreeDescriptor,
    )
    from flext_cli._utilities.atomic_tree_inventory import (
        FlextCliUtilitiesAtomicTreeInventory,
    )
    from flext_cli._utilities.atomic_tree_physical import (
        FlextCliUtilitiesAtomicTreePhysical,
    )
    from flext_cli._utilities.atomic_tree_query_membership import (
        FlextCliUtilitiesAtomicTreeQueryMembership,
    )
    from flext_cli._utilities.atomic_tree_query_receipts import (
        FlextCliUtilitiesAtomicTreeQueryReceipts,
    )
    from flext_cli._utilities.atomic_tree_query_topology import (
        FlextCliUtilitiesAtomicTreeQueryTopology,
    )
    from flext_cli._utilities.auth import FlextCliUtilitiesAuth
    from flext_cli._utilities.cli_namespace import FlextCliUtilitiesCli
    from flext_cli._utilities.cmd import FlextCliUtilitiesCmd
    from flext_cli._utilities.commands import FlextCliUtilitiesCommands
    from flext_cli._utilities.config import FlextCliUtilitiesConfig
    from flext_cli._utilities.conversion import FlextCliUtilitiesConversion
    from flext_cli._utilities.dag import FlextCliUtilitiesDag
    from flext_cli._utilities.documents import FlextCliUtilitiesDocuments
    from flext_cli._utilities.env import FlextCliUtilitiesEnv
    from flext_cli._utilities.file_changes import FlextCliUtilitiesFileChanges
    from flext_cli._utilities.file_test_helpers import FlextCliUtilitiesFileTestHelpers
    from flext_cli._utilities.files import FlextCliUtilitiesFiles
    from flext_cli._utilities.formatters import FlextCliUtilitiesFormatters
    from flext_cli._utilities.framework import FlextCliUtilitiesFramework
    from flext_cli._utilities.json import FlextCliUtilitiesJson
    from flext_cli._utilities.markdown import FlextCliUtilitiesMarkdown
    from flext_cli._utilities.markdown_links import FlextCliUtilitiesMarkdownLinks
    from flext_cli._utilities.markdown_parsing import FlextCliUtilitiesMarkdownParsing
    from flext_cli._utilities.matching import FlextCliUtilitiesMatching
    from flext_cli._utilities.native_runtime import (
        TimeoutExpired,
        spawn_streamed_process,
        streamed_creation_flags,
    )
    from flext_cli._utilities.option_builder import FlextCliUtilitiesOptionBuilder
    from flext_cli._utilities.options_annotations import (
        FlextCliUtilitiesOptionsAnnotations,
    )
    from flext_cli._utilities.options_fields import FlextCliUtilitiesOptionsFields
    from flext_cli._utilities.output import FlextCliUtilitiesOutput
    from flext_cli._utilities.output_payloads import FlextCliUtilitiesOutputPayloads
    from flext_cli._utilities.params import FlextCliUtilitiesParams
    from flext_cli._utilities.pipeline import FlextCliUtilitiesPipeline
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
    "FlextCliUtilitiesAtomicTreeDarwin",
    "FlextCliUtilitiesAtomicTreeDescriptor",
    "FlextCliUtilitiesAtomicTreeInventory",
    "FlextCliUtilitiesAtomicTreePhysical",
    "FlextCliUtilitiesAtomicTreeQueryMembership",
    "FlextCliUtilitiesAtomicTreeQueryReceipts",
    "FlextCliUtilitiesAtomicTreeQueryTopology",
    "FlextCliUtilitiesAuth",
    "FlextCliUtilitiesCli",
    "FlextCliUtilitiesCmd",
    "FlextCliUtilitiesCommands",
    "FlextCliUtilitiesConfig",
    "FlextCliUtilitiesConversion",
    "FlextCliUtilitiesDag",
    "FlextCliUtilitiesDocuments",
    "FlextCliUtilitiesEnv",
    "FlextCliUtilitiesFileChanges",
    "FlextCliUtilitiesFileTestHelpers",
    "FlextCliUtilitiesFiles",
    "FlextCliUtilitiesFormatters",
    "FlextCliUtilitiesFramework",
    "FlextCliUtilitiesJson",
    "FlextCliUtilitiesMarkdown",
    "FlextCliUtilitiesMarkdownLinks",
    "FlextCliUtilitiesMarkdownParsing",
    "FlextCliUtilitiesMatching",
    "FlextCliUtilitiesOptionBuilder",
    "FlextCliUtilitiesOptionsAnnotations",
    "FlextCliUtilitiesOptionsFields",
    "FlextCliUtilitiesOutput",
    "FlextCliUtilitiesOutputPayloads",
    "FlextCliUtilitiesParams",
    "FlextCliUtilitiesPipeline",
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
    "TimeoutExpired",
    "spawn_streamed_process",
    "streamed_creation_flags",
)

install_lazy_exports(
    __name__,
    globals(),
    {
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
        "FlextCliUtilitiesAtomicTreeDarwin": ".atomic_tree_darwin",
        "FlextCliUtilitiesAtomicTreeDescriptor": ".atomic_tree_descriptor",
        "FlextCliUtilitiesAtomicTreeInventory": ".atomic_tree_inventory",
        "FlextCliUtilitiesAtomicTreePhysical": ".atomic_tree_physical",
        "FlextCliUtilitiesAtomicTreeQueryMembership": ".atomic_tree_query_membership",
        "FlextCliUtilitiesAtomicTreeQueryReceipts": ".atomic_tree_query_receipts",
        "FlextCliUtilitiesAtomicTreeQueryTopology": ".atomic_tree_query_topology",
        "FlextCliUtilitiesAuth": ".auth",
        "FlextCliUtilitiesCli": ".cli_namespace",
        "FlextCliUtilitiesCmd": ".cmd",
        "FlextCliUtilitiesCommands": ".commands",
        "FlextCliUtilitiesConfig": ".config",
        "FlextCliUtilitiesConversion": ".conversion",
        "FlextCliUtilitiesDag": ".dag",
        "FlextCliUtilitiesDocuments": ".documents",
        "FlextCliUtilitiesEnv": ".env",
        "FlextCliUtilitiesFileChanges": ".file_changes",
        "FlextCliUtilitiesFileTestHelpers": ".file_test_helpers",
        "FlextCliUtilitiesFiles": ".files",
        "FlextCliUtilitiesFormatters": ".formatters",
        "FlextCliUtilitiesFramework": ".framework",
        "FlextCliUtilitiesJson": ".json",
        "FlextCliUtilitiesMarkdown": ".markdown",
        "FlextCliUtilitiesMarkdownLinks": ".markdown_links",
        "FlextCliUtilitiesMarkdownParsing": ".markdown_parsing",
        "FlextCliUtilitiesMatching": ".matching",
        "FlextCliUtilitiesOptionBuilder": ".option_builder",
        "FlextCliUtilitiesOptionsAnnotations": ".options_annotations",
        "FlextCliUtilitiesOptionsFields": ".options_fields",
        "FlextCliUtilitiesOutput": ".output",
        "FlextCliUtilitiesOutputPayloads": ".output_payloads",
        "FlextCliUtilitiesParams": ".params",
        "FlextCliUtilitiesPipeline": ".pipeline",
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
        "TimeoutExpired": ".native_runtime",
        "spawn_streamed_process": ".native_runtime",
        "streamed_creation_flags": ".native_runtime",
    },
    public_exports=__all__,
    deferred_members={
        "FlextCliUtilitiesAtomicDirectoryChain": (
            "plan_directory_chain",
            "verify_guarded_directory_chain",
            "create_guarded_directory_chain",
            "_create_chained_directories",
            "require_anchor",
            "require_planned_parent",
            "require_created_identity",
        ),
        "FlextCliUtilitiesAtomicDirectoryCleanup": (
            "remove_created_directory",
            "_remove_created_directory",
            "_require_cleanup_identity",
            "_require_unchanged_cleanup_state",
        ),
        "FlextCliUtilitiesAtomicDirectoryCreate": (
            "create_guarded_empty_directory",
            "_require_created_state",
            "_initialize_created",
        ),
        "FlextCliUtilitiesAtomicDirectoryDelete": ("remove_guarded_empty_directory",),
        "FlextCliUtilitiesAtomicDirectoryDescriptor": (
            "_SECURE_CREATE_MODE",
            "require_read_capabilities",
            "require_directory_create_capabilities",
            "require_delete_capabilities",
            "require_publish_capabilities",
            "create_entry",
            "remove_entry",
            "rename_entry_noreplace",
            "_require_dir_fd",
        ),
        "FlextCliUtilitiesAtomicDirectoryModel": (
            "from_observed",
            "require_absent",
            "require_directory_existing",
            "require_directory_observed",
            "directory_physical_state",
            "_planned_state",
        ),
        "FlextCliUtilitiesAtomicDirectoryNoreplace": (
            "_RENAME_NOREPLACE",
            "_RENAME_EXCL",
            "require_noreplace_capability",
            "rename_noreplace",
            "_runtime_platform",
            "_linux_renameat2",
            "_darwin_renameatx",
            "_load_rename",
            "_encode_name",
        ),
        "FlextCliUtilitiesAtomicDirectoryPublish": (
            "publish_guarded_staged_empty_directory",
            "_require_destination_absent",
            "_authenticated_staged",
            "_require_same_filesystem",
            "_published_state",
            "_raise_post_publication_failure",
        ),
        "FlextCliUtilitiesAtomicDirectorySnapshot": (
            "read_authenticated_empty_directory",
        ),
        "FlextCliUtilitiesAtomicDirectoryState": (
            "_MAX_EMPTY_DIRECTORY_LINK_COUNT",
            "directory_destination_state",
            "_validate_destination",
            "_open_authenticated_empty_entry",
            "read_empty_state",
            "initialize_empty_state",
            "_require_descriptor_state",
            "_require_empty",
            "_require_path_state",
        ),
        "FlextCliUtilitiesAtomicFile": (
            "write_atomic_state",
            "_parse_precondition",
            "_stage_and_publish",
            "_AtomicStage",
            "_validate_replacement",
            "_validate_staged",
        ),
        "FlextCliUtilitiesAtomicFileCleanup": (
            "remove_linked_temporary",
            "remove_failed_temporary",
        ),
        "FlextCliUtilitiesAtomicFileDelete": ("remove_guarded_file",),
        "FlextCliUtilitiesAtomicFileDescriptor": (
            "ParentDescriptor",
            "parent_descriptor",
            "assert_parent_unchanged",
            "destination_state",
            "entry_stat",
            "open_entry",
            "entry_descriptor",
            "unlink_entry",
            "require_file_create_capabilities",
            "link_entry",
            "replace_entry",
            "_require_capabilities",
            "require_entry",
            "close_after_failure",
        ),
        "FlextCliUtilitiesAtomicFileDurability": (
            "sync_parent",
            "sync_replacement",
        ),
        "FlextCliUtilitiesAtomicFileMode": (
            "NoModePrecondition",
            "NO_MODE_PRECONDITION",
            "validate_mode",
            "validate_mode_precondition",
            "validate_guarded_mode_tuple",
            "assert_observed_mode",
            "publication_mode",
        ),
        "FlextCliUtilitiesAtomicFileModel": (
            "require_existing",
            "require_snapshot_presence",
            "require_observed",
            "require_parent",
            "publication_parents",
            "physical_state",
            "planned_physical_state",
        ),
        "FlextCliUtilitiesAtomicFilePath": (
            "validate_atomic_path",
            "validate_directory_path",
            "resolve_parent_path",
            "validate_directory_state",
            "require_identity",
            "path_identity",
            "reparse_point",
        ),
        "FlextCliUtilitiesAtomicFilePublish": (
            "publish_guarded_staged_file",
            "_validated_paths",
            "_resolve_staged",
            "_resolve_destination_payload",
        ),
        "FlextCliUtilitiesAtomicFilePublishChecks": (
            "validate_identity",
            "require_distinct_inode",
            "validate_devices",
            "validate_publication",
            "validate_version",
            "validate_payload",
        ),
        "FlextCliUtilitiesAtomicFileRead": (
            "READ_FLAGS",
            "Reader",
            "read_descriptor_bytes",
            "state_key",
            "descriptor_chunks",
            "raise_changed",
        ),
        "FlextCliUtilitiesAtomicFileSnapshot": (
            "read_receipt",
            "receipt_reader",
        ),
        "FlextCliUtilitiesAtomicFileState": (
            "read_authenticated_state",
            "authenticated_entry",
            "require_owner",
            "_require_size",
            "file_destination_state",
            "validate_precondition",
            "assert_temporary_owned",
            "assert_destination_unchanged",
            "read_authenticated_bytes",
            "_validate_regular_state",
            "_validate_exclusive_link",
        ),
        "FlextCliUtilitiesAtomicFileTemporary": (
            "_SECURE_CREATE_MODE",
            "temporary_path",
            "require_mode_capability",
            "create_descriptor",
            "write_exact",
            "synced_mode",
        ),
        "FlextCliUtilitiesAtomicParentDescriptor": (
            "PhysicalDirectory",
            "physical_directory",
            "verify_lineage",
            "inspect_directory_chain",
            "require_traversal_capabilities",
            "_open_components",
            "_missing_paths",
            "_close_descriptors",
            "_close_after_failure",
        ),
        "FlextCliUtilitiesAtomicParentFailure": (
            "preserve_recheck_failure",
            "raise_combined_failure",
        ),
        "FlextCliUtilitiesAtomicSymlinkPublish": (
            "_validated_target",
            "_stage_verified_link",
            "_discard_staged",
            "_swap_staged_link",
            "_verify_published",
            "write_guarded_symlink",
            "delete_guarded_symlink",
        ),
        "FlextCliUtilitiesAtomicSymlinkState": (
            "read_symlink_state",
            "symlink_identity",
            "require_symlink_state",
        ),
        "FlextCliUtilitiesAtomicTreeCleanup": (
            "cleanup_physical_tree_guarded",
            "_require_cleanup_capabilities",
            "_authenticated_parent",
            "_delete_file",
            "_delete_symlink",
            "_delete_directory",
            "_require_file_state",
            "_require_parent",
            "_deletion_key",
            "_binding_path_key",
            "_raise_cleanup_changed",
        ),
        "FlextCliUtilitiesAtomicTreeDarwin": (
            "Statfs",
            "darwin_mount_id",
        ),
        "FlextCliUtilitiesAtomicTreeDescriptor": (
            "measure_authenticated_file",
            "tree_mount_id",
            "require_mount",
            "require_same_device",
            "require_directory_state",
            "require_entry_state",
            "_tree_runtime_platform",
            "_raise_descriptor_changed",
        ),
        "FlextCliUtilitiesAtomicTreeInventory": (
            "verify_directory_queries",
            "_query_boundary",
            "_verify_inventory_queries",
            "_inventory_unchanged",
            "_verify_inventory_query",
            "_published_query_value",
            "_published_ancestors",
            "_require_membership_policy",
        ),
        "FlextCliUtilitiesAtomicTreePhysical": (
            "_DIRECTORY_FLAGS",
            "_observe_physical_directory",
            "inventory_physical_directory",
            "inventory_physical_tree",
            "_opened_root",
            "_inventory_directory",
            "_file_digest",
            "_entry",
            "_directory_names",
            "_entry_path_key",
            "_raise_inventory_changed",
        ),
        "FlextCliUtilitiesAtomicTreeQueryMembership": (
            "_verify_query_membership",
            "_apply_created_members",
            "_apply_published_members",
            "_published_directory_current",
            "_raise_unpublished_directory",
        ),
        "FlextCliUtilitiesAtomicTreeQueryReceipts": (
            "_SELECTOR_FIELDS",
            "directory_membership_value",
            "directory_query_value",
            "merge_directory_query_receipts",
            "_merge_directory_witnesses",
            "_merge_topology_witnesses",
            "_united_selection",
            "_selection_unchanged",
            "_require_directory_witness_agreement",
            "_require_directory_identity",
        ),
        "FlextCliUtilitiesAtomicTreeQueryTopology": (
            "_verify_query_topology",
            "_require_ancestry_current",
            "_ancestry_gained_by_creation",
            "_created_at",
            "_consumes_selectors",
            "_verify_absent_candidate",
        ),
        "FlextCliUtilitiesAuth": (
            "auth_token_file_path",
            "auth_validate_credentials",
            "auth_extract_token",
        ),
        "FlextCliUtilitiesCli": ("model_config",),
        "FlextCliUtilitiesCmd": ("cmd_status",),
        "FlextCliUtilitiesCommands": (
            "commands_resolve_success_message",
            "commands_emit_success_message",
            "commands_emit_failure_cause",
            "commands_emit_result_error",
        ),
        "FlextCliUtilitiesConfig": (
            "config_decode",
            "_read_by_suffix",
            "config_load",
            "schema_validate",
            "_run_validator",
        ),
        "FlextCliUtilitiesConversion": (
            "_EMPTY_JSON_MAPPING",
            "STR_SEQUENCE_ADAPTER",
            "JSON_VALUE_ADAPTER",
            "JSON_MAPPING_ADAPTER",
            "JSON_LIST_ADAPTER",
            "YAML_DICT_ADAPTER",
            "YAML_SEQ_ADAPTER",
            "CLI_DEFAULT_SOURCE_ADAPTER",
            "default_for_type_kind",
            "resolve_optional_path",
            "normalize_optional_text",
            "normalize_required_text",
        ),
        "FlextCliUtilitiesDag": (
            "dag_waves",
            "dag_order",
            "dag_closure",
            "dag_strongly_connected",
        ),
        "FlextCliUtilitiesDocuments": (
            "docx_read",
            "docx_render",
            "read_presentation",
            "render_presentation",
        ),
        "FlextCliUtilitiesEnv": (
            "_VAR_PATTERN",
            "_STRICT_PATTERN",
            "_ANY_PLACEHOLDER",
            "env_read",
            "env_expand",
            "env_expand_document",
            "_expand_mapping",
            "_expand_sequence",
            "_expand_strict",
        ),
        "FlextCliUtilitiesFileChanges": (
            "file_changes_lock",
            "pending_file_changes",
            "publish_file_changes",
            "_publication_evidence",
            "_publish",
        ),
        "FlextCliUtilitiesFileTestHelpers": (
            "files_assert_exists",
            "files_parse_content",
        ),
        "FlextCliUtilitiesFiles": (),
        "FlextCliUtilitiesFormatters": (
            "_styled",
            "formatters_print",
            "formatters_render_rule",
            "formatters_render_panel",
            "formatters_render_table",
        ),
        "FlextCliUtilitiesFramework": (
            "_TYPER_CLICK_EXCEPTION",
            "_TYPER_CLICK_CONTEXT",
            "TyperApplication",
            "ClickCommand",
            "_active_execution",
            "_active_failure",
            "framework_exit_result",
            "_unwrap",
            "_exit_code_result",
            "framework_create_app",
            "framework_add_group",
            "framework_command_context_annotation",
            "framework_supplied_options",
            "framework_option_spelling",
            "framework_reject_input",
            "framework_report_usage_error",
            "framework_register_callback",
            "framework_register_command",
            "framework_build_parameter",
            "_json_parser",
            "framework_execute",
            "framework_execute_external",
            "framework_external_command",
            "framework_invoke",
            "framework_exit",
            "process_main",
        ),
        "FlextCliUtilitiesJson": (),
        "FlextCliUtilitiesMarkdown": (
            "markdown_fences",
            "markdown_code_spans",
            "markdown_headings",
            "_markdown_wrap_line",
            "markdown_wrap",
            "markdown_rewrite_fences",
        ),
        "FlextCliUtilitiesMarkdownLinks": (
            "markdown_links",
            "_markdown_link_spans",
            "_link_opener",
            "_label_start",
            "markdown_rewrite_link_targets",
            "markdown_unlink",
            "markdown_align_tables",
            "_markdown_realign_tables",
            "_markdown_table_cells",
            "_markdown_aligned_rows",
        ),
        "FlextCliUtilitiesMarkdownParsing": (
            "_VerbatimMarkdownIt",
            "_markdown_parser",
            "_markdown_tokens",
            "_markdown_block_parser",
            "_markdown_inline_walk",
        ),
        "FlextCliUtilitiesMatching": (
            "matches",
            "matches_regex",
            "cli_usage_error",
        ),
        "FlextCliUtilitiesOptionBuilder": ("build",),
        "FlextCliUtilitiesOptionsAnnotations": (
            "unwrap_annotation",
            "json_option",
            "resolve_typer_annotation",
            "string_sequence",
            "normalize_cli_atom",
        ),
        "FlextCliUtilitiesOptionsFields": (
            "field_annotation",
            "field_default",
            "build_option",
            "reorder_prefixed_options",
        ),
        "FlextCliUtilitiesOutput": (
            "_EMIT_LOCK",
            "emit_raw",
            "info",
            "error",
            "warning",
            "debug",
            "header",
            "progress",
            "status",
            "summary",
            "gate_result",
            "resolve_report_dir",
            "resolve_report_path",
        ),
        "FlextCliUtilitiesOutputPayloads": (
            "output_resolve_message_type",
            "output_message_payload",
            "output_progress_line",
            "output_summary_content",
            "output_debug_line",
            "output_table_error",
            "output_status_line",
            "output_gate_line",
        ),
        "FlextCliUtilitiesParams": (
            "params_resolve",
            "params_set_bool",
            "params_set_log_level",
            "params_set_format",
            "params_apply",
        ),
        "FlextCliUtilitiesPipeline": (
            "execute_pipeline",
            "_skip_failed_wave",
            "_execute_ready_wave",
            "_run_stage",
        ),
        "FlextCliUtilitiesProcesses": (
            "ManagedProcess",
            "process_start",
        ),
        "FlextCliUtilitiesPrompts": (
            "prompts_confirmation_text",
            "prompts_display_message",
            "prompts_effective_text",
            "prompts_parse_confirmation",
            "prompts_choice_result",
            "prompts_password_result",
        ),
        "FlextCliUtilitiesReport": ("report_render",),
        "FlextCliUtilitiesRuntime": (
            "_module_logger",
            "process_env",
            "_resolved_env",
            "_spawn_streamed_process",
            "child_communicate",
            "_streamed_creation_flags",
            "run_raw",
            "run_bytes",
        ),
        "FlextCliUtilitiesSettings": (
            "cli_test_env",
            "project_names_from_values",
            "project_numbers_from_values",
            "settings_snapshot_model",
            "validate_settings_structure",
        ),
        "FlextCliUtilitiesTables": (
            "TABLE_DATA_ADAPTER",
            "tables_normalize_mapping_row",
            "tables_normalize_sequence_row",
            "tables_resolve_config",
            "tables_normalize_data",
            "tables_render",
        ),
        "FlextCliUtilitiesTemplate": (
            "_ContentLoader",
            "_AuthenticatedLoader",
            "_environments",
            "template_environment",
            "template_render",
            "template_capture_sources",
            "template_render_authenticated",
            "template_render_to",
            "template_render_dir",
            "_entry_destination",
            "_destination_escape",
            "_write",
        ),
        "FlextCliUtilitiesToml": (),
        "FlextCliUtilitiesValidation": (
            "validate_not_empty",
            "validate_format",
        ),
        "FlextCliUtilitiesXlsx": (
            "xlsx_render",
            "xlsx_snapshot",
            "xlsx_inspect",
            "xlsx_recalc",
            "xlsx_recalc_parity",
            "xlsx_defined_name_values",
            "xlsx_style_catalog",
            "xlsx_style_template",
            "xlsx_parse_range",
            "xlsx_format_reference",
        ),
        "FlextCliUtilitiesYaml": (
            "yaml_safe_load",
            "yaml_load_documents",
            "yaml_parse",
            "yaml_parse_documents",
            "yaml_load_mapping",
            "yaml_dump",
            "yaml_dump_str",
        ),
    },
)

defer_lazy_bases(
    __name__,
    {
        "FlextCliUtilitiesAtomicTreeInventory": (
            (".", "FlextCliUtilitiesAtomicTreeQueryTopology"),
        ),
        "FlextCliUtilitiesAtomicTreeQueryMembership": (
            (".", "FlextCliUtilitiesAtomicTreeQueryReceipts"),
            (".", "FlextCliUtilitiesAtomicTreePhysical"),
        ),
        "FlextCliUtilitiesAtomicTreeQueryTopology": (
            (".", "FlextCliUtilitiesAtomicTreeQueryMembership"),
        ),
        "FlextCliUtilitiesCli": (
            (".", "FlextCliUtilitiesAuth"),
            (".", "FlextCliUtilitiesCmd"),
            (".", "FlextCliUtilitiesCommands"),
            (".", "FlextCliUtilitiesConfig"),
            (".", "FlextCliUtilitiesConversion"),
            (".", "FlextCliUtilitiesDag"),
            (".", "FlextCliUtilitiesEnv"),
            (".", "FlextCliUtilitiesTemplate"),
            (".", "FlextCliUtilitiesFileTestHelpers"),
            (".", "FlextCliUtilitiesFileChanges"),
            (".", "FlextCliUtilitiesFiles"),
            (".", "FlextCliUtilitiesFormatters"),
            (".", "FlextCliUtilitiesFramework"),
            (".", "FlextCliUtilitiesJson"),
            (".", "FlextCliUtilitiesMarkdown"),
            (".", "FlextCliUtilitiesMatching"),
            (".", "FlextCliUtilitiesOptionsFields"),
            (".", "FlextCliUtilitiesOutput"),
            (".", "FlextCliUtilitiesParams"),
            (".", "FlextCliUtilitiesPipeline"),
            (".", "FlextCliUtilitiesPrompts"),
            (".", "FlextCliUtilitiesReport"),
            (".", "FlextCliUtilitiesProcesses"),
            (".", "FlextCliUtilitiesRuntime"),
            (".", "FlextCliUtilitiesSettings"),
            (".", "FlextCliUtilitiesTables"),
            (".", "FlextCliUtilitiesToml"),
            (".", "FlextCliUtilitiesValidation"),
            (".", "FlextCliUtilitiesXlsx"),
            (".", "FlextCliUtilitiesDocuments"),
            (".", "FlextCliUtilitiesYaml"),
        ),
        "FlextCliUtilitiesFiles": (
            ("flext_cli._utilities._files", "FlextCliUtilitiesFilesPart01"),
            ("flext_cli._utilities._files", "FlextCliUtilitiesFilesPart02"),
            ("flext_cli._utilities._files", "FlextCliUtilitiesFilesPart03"),
            ("flext_cli._utilities._files", "FlextCliUtilitiesFilesPart04"),
            ("flext_cli._utilities._files", "FlextCliUtilitiesFilesPart05"),
            ("flext_cli._utilities._files", "FlextCliUtilitiesFilesPart06"),
        ),
        "FlextCliUtilitiesJson": (
            ("flext_cli._utilities._json", "FlextCliUtilitiesJsonNavigate"),
        ),
        "FlextCliUtilitiesMarkdown": ((".", "FlextCliUtilitiesMarkdownLinks"),),
        "FlextCliUtilitiesMarkdownLinks": ((".", "FlextCliUtilitiesMarkdownParsing"),),
        "FlextCliUtilitiesOptionsFields": (
            (".", "FlextCliUtilitiesOptionsAnnotations"),
        ),
        "FlextCliUtilitiesOutput": ((".", "FlextCliUtilitiesOutputPayloads"),),
        "FlextCliUtilitiesProcesses": ((".", "FlextCliUtilitiesRuntime"),),
        "FlextCliUtilitiesRuntime": (
            ("flext_cli._utilities._runtime", "FlextCliUtilitiesRuntimeCommands"),
            ("flext_cli._utilities._runtime", "FlextCliUtilitiesRuntimeRunToFile"),
        ),
        "FlextCliUtilitiesToml": (
            ("flext_cli._utilities._toml", "FlextCliUtilitiesTomlPart01"),
            ("flext_cli._utilities._toml", "FlextCliUtilitiesTomlPart02"),
            ("flext_cli._utilities._toml", "FlextCliUtilitiesTomlPart03"),
            ("flext_cli._utilities._toml", "FlextCliUtilitiesTomlPart04"),
            ("flext_cli._utilities._toml", "FlextCliUtilitiesTomlPart05"),
            ("flext_cli._utilities._toml", "FlextCliUtilitiesTomlPart06"),
            ("flext_cli._utilities._toml", "FlextCliUtilitiesTomlPart07"),
        ),
        "FlextCliUtilitiesYaml": (
            ("flext_cli._utilities._yaml", "FlextCliUtilitiesYamlEditing"),
        ),
    },
)

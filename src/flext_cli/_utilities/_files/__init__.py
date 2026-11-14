# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Files package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._files.binary_reads import FlextCliUtilitiesFilesPart03
    from flext_cli._utilities._files.flextcliutilitiesfiles_part_05 import (
        FlextCliUtilitiesFilesPart05,
    )
    from flext_cli._utilities._files.flextcliutilitiesfiles_part_06 import (
        FlextCliUtilitiesFilesPart06,
    )
    from flext_cli._utilities._files.formats import FlextCliUtilitiesFilesPart04
    from flext_cli._utilities._files.native_results import (
        FlextCliUtilitiesFilesNativeResults,
    )
    from flext_cli._utilities._files.text_formats import FlextCliUtilitiesFilesPart01
    from flext_cli._utilities._files.writes import FlextCliUtilitiesFilesPart02


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesFilesNativeResults",
    "FlextCliUtilitiesFilesPart01",
    "FlextCliUtilitiesFilesPart02",
    "FlextCliUtilitiesFilesPart03",
    "FlextCliUtilitiesFilesPart04",
    "FlextCliUtilitiesFilesPart05",
    "FlextCliUtilitiesFilesPart06",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextCliUtilitiesFilesNativeResults": ".native_results",
        "FlextCliUtilitiesFilesPart01": ".text_formats",
        "FlextCliUtilitiesFilesPart02": ".writes",
        "FlextCliUtilitiesFilesPart03": ".binary_reads",
        "FlextCliUtilitiesFilesPart04": ".formats",
        "FlextCliUtilitiesFilesPart05": ".flextcliutilitiesfiles_part_05",
        "FlextCliUtilitiesFilesPart06": ".flextcliutilitiesfiles_part_06",
    },
    public_exports=__all__,
    deferred_members={
        "FlextCliUtilitiesFilesPart01": (
            "files_delete",
            "files_read_text",
            "files_write_text",
            "files_read_json",
            "files_read_json_model",
            "files_read_yaml",
            "files_read_yaml_model",
            "files_read_yaml_model_chain",
            "files_write_csv",
        ),
        "FlextCliUtilitiesFilesPart02": (
            "files_save_bytes",
            "files_write_binary",
            "atomic_write_text_file",
            "_validated_atomic_write",
            "atomic_write_text_file_guarded",
            "atomic_write_binary_file_guarded",
            "atomic_delete_binary_file_guarded",
            "files_copy",
            "files_execute",
            "files_execute_bool",
            "ensure_dir",
        ),
        "FlextCliUtilitiesFilesPart03": (
            "atomic_read_binary_file_receipt",
            "atomic_binary_file_reader",
            "atomic_read_binary_file_range",
            "atomic_publish_staged_binary_file_receipt_guarded",
            "files_read_csv_with_headers",
            "files_read_binary",
            "atomic_read_binary_file_state",
            "atomic_read_binary_file_capture",
            "atomic_iter_binary_file",
            "atomic_publish_staged_binary_file_guarded",
            "files_list_directory_names",
            "sha256_content",
            "sha256_bytes",
            "sha256_file",
        ),
        "FlextCliUtilitiesFilesPart04": (
            "files_detect_format",
            "files_detect_format_from_content",
            "files_detect_format_from_path",
            "files_load_auto_mapping",
            "csv_loads",
            "csv_dumps",
            "files_copy_directory",
            "files_create_temporary_directory",
            "files_remove_directory",
        ),
        "FlextCliUtilitiesFilesPart05": (
            "atomic_plan_directory_chain",
            "atomic_create_directory_chain_guarded",
            "atomic_read_empty_directory_state",
            "atomic_create_empty_directory_guarded",
            "atomic_delete_empty_directory_guarded",
            "atomic_merge_directory_query_receipts",
            "atomic_directory_membership_value",
            "atomic_directory_query_value",
            "atomic_verify_directory_queries",
            "atomic_inventory_physical_directory",
            "atomic_inventory_physical_tree",
            "atomic_cleanup_physical_tree_guarded",
        ),
        "FlextCliUtilitiesFilesPart06": (
            "atomic_create_binary_file_guarded",
            "atomic_verify_binary_file_states",
            "_same_file_observation",
            "_content_diagnostic",
            "files_matching",
            "_files_candidates",
            "_probed_candidates",
            "_files_git_candidates",
        ),
    },
)

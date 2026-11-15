# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Toml package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
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


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesTomlPart01",
    "FlextCliUtilitiesTomlPart02",
    "FlextCliUtilitiesTomlPart03",
    "FlextCliUtilitiesTomlPart04",
    "FlextCliUtilitiesTomlPart05",
    "FlextCliUtilitiesTomlPart06",
    "FlextCliUtilitiesTomlPart07",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextCliUtilitiesTomlPart01": ".flextcliutilitiestoml_part_01",
        "FlextCliUtilitiesTomlPart02": ".flextcliutilitiestoml_part_02",
        "FlextCliUtilitiesTomlPart03": ".flextcliutilitiestoml_part_03",
        "FlextCliUtilitiesTomlPart04": ".flextcliutilitiestoml_part_04",
        "FlextCliUtilitiesTomlPart05": ".flextcliutilitiestoml_part_05",
        "FlextCliUtilitiesTomlPart06": ".flextcliutilitiestoml_part_06",
        "FlextCliUtilitiesTomlPart07": ".flextcliutilitiestoml_part_07",
    },
    public_exports=__all__,
    deferred_members={
        "FlextCliUtilitiesTomlPart01": (
            "_module_logger",
            "toml_as_mapping",
            "toml_unwrap_item",
            "toml_as_string_list",
            "toml_string_list_change",
            "toml_array",
            "toml_document",
            "toml_table",
            "toml_aot",
            "toml_parse_text",
            "toml_dumps",
            "toml_mapping_from_text",
            "toml_mapping_from_text_result",
            "toml_document_from_mapping",
        ),
        "FlextCliUtilitiesTomlPart02": (
            "toml_item_from_json_value",
            "toml_is_table",
            "_toml_consolidate_proxy",
            "toml_is_item",
            "toml_is_aot",
            "toml_table_child",
            "toml_item_child",
            "toml_array_item_comments",
            "toml_ensure_table",
            "_consolidated_table",
            "toml_ensure_path",
        ),
        "FlextCliUtilitiesTomlPart03": (
            "toml_table_path",
            "toml_ensure_tool_table",
            "toml_value",
            "toml_mapping_child",
            "toml_mapping_ensure_table",
            "toml_mapping_ensure_path",
            "toml_mapping_path",
            "toml_remove_key_if_present",
        ),
        "FlextCliUtilitiesTomlPart04": (
            "toml_sync_value",
            "toml_sync_string_list",
            "toml_mapping_remove_key_if_present",
            "toml_mapping_sync_value",
            "toml_mapping_merge_string_list",
        ),
        "FlextCliUtilitiesTomlPart05": (
            "toml_mapping_sync_string_list",
            "toml_dot_path",
        ),
        "FlextCliUtilitiesTomlPart06": (
            "toml_read",
            "toml_read_document",
            "toml_read_json",
            "_resolve_taplo_config",
            "_format_pyproject",
            "toml_write_document",
        ),
        "FlextCliUtilitiesTomlPart07": ("toml_write_mapping",),
    },
)

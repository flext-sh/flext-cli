# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Json package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._json.core import FlextCliUtilitiesJsonCore
    from flext_cli._utilities._json.navigate import FlextCliUtilitiesJsonNavigate


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesJsonCore",
    "FlextCliUtilitiesJsonNavigate",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextCliUtilitiesJsonCore": ".core",
        "FlextCliUtilitiesJsonNavigate": ".navigate",
    },
    public_exports=__all__,
    deferred_members={
        "FlextCliUtilitiesJsonCore": (
            "_EMPTY_JSON_MAPPING",
            "_EMPTY_JSON_SEQUENCE",
            "_module_logger",
            "json_dumps",
            "json_loads",
            "_parse_json_value",
            "_reject_duplicate_json_keys",
            "json_sort_keys",
            "normalize_json_value",
            "_json_write_content",
            "json_read",
            "json_write",
            "json_parse",
            "json_as_mapping",
            "json_as_sequence",
        ),
        "FlextCliUtilitiesJsonNavigate": (
            "json_as_mapping_list",
            "json_walk_path",
            "json_deep_mapping",
            "json_deep_mapping_list",
            "json_pick_str",
            "json_pick_int",
            "json_pick_bool",
            "json_nested_int",
            "json_get_str_key",
            "_EMPTY_JSON_MAPPING",
            "_EMPTY_JSON_SEQUENCE",
            "_module_logger",
            "json_dumps",
            "json_loads",
            "_parse_json_value",
            "_reject_duplicate_json_keys",
            "json_sort_keys",
            "normalize_json_value",
            "_json_write_content",
            "json_read",
            "json_write",
            "json_parse",
            "json_as_mapping",
            "json_as_sequence",
        ),
    },
)

# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Utilities. Yaml package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._utilities._yaml.convert import FlextCliUtilitiesYamlConvert
    from flext_cli._utilities._yaml.editing import FlextCliUtilitiesYamlEditing
    from flext_cli._utilities._yaml.engine import FlextCliUtilitiesYamlEngine


__all__: tuple[str, ...] = (
    "FlextCliUtilitiesYamlConvert",
    "FlextCliUtilitiesYamlEditing",
    "FlextCliUtilitiesYamlEngine",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "FlextCliUtilitiesYamlConvert": ".convert",
        "FlextCliUtilitiesYamlEditing": ".editing",
        "FlextCliUtilitiesYamlEngine": ".engine",
    },
    public_exports=__all__,
    deferred_members={
        "FlextCliUtilitiesYamlConvert": (
            "_YAML_1_1_IMPLICIT_STRING_VALUES",
            "yaml_to_plain",
            "yaml_deep_to_commented",
            "yaml_is_sequence",
            "yaml_plain_str",
            "yaml_plain_bool",
            "yaml_plain_int",
            "yaml_plain_float",
            "_yaml_coerce_node",
        ),
        "FlextCliUtilitiesYamlEditing": (
            "_module_logger",
            "_yaml_has_anchor",
            "yaml_clear_anchors",
            "yaml_deep_copy_comments",
            "yaml_copy_key_comment",
            "yaml_pre_key_tokens",
            "_yaml_comment_core",
            "yaml_has_key_comment",
            "yaml_add_pre_key_comment",
            "yaml_force_block_style",
            "yaml_update_value_inplace",
            "yaml_overlay_preserving_order",
            "_roundtrip_yaml",
            "yaml_roundtrip_load",
            "_load_node",
            "yaml_roundtrip_load_text",
            "yaml_roundtrip_load_all_text",
            "yaml_roundtrip_load_map_text",
            "yaml_roundtrip_dump",
            "yaml_roundtrip_dump_text",
            "_YAML_1_1_IMPLICIT_STRING_VALUES",
            "yaml_to_plain",
            "yaml_deep_to_commented",
            "yaml_is_sequence",
            "yaml_plain_str",
            "yaml_plain_bool",
            "yaml_plain_int",
            "yaml_plain_float",
            "_yaml_coerce_node",
        ),
        "FlextCliUtilitiesYamlEngine": (
            "_roundtrip_yaml",
            "yaml_roundtrip_load",
            "_load_node",
            "yaml_roundtrip_load_text",
            "yaml_roundtrip_load_all_text",
            "yaml_roundtrip_load_map_text",
            "yaml_roundtrip_dump",
            "yaml_roundtrip_dump_text",
            "_YAML_1_1_IMPLICIT_STRING_VALUES",
            "yaml_to_plain",
            "yaml_deep_to_commented",
            "yaml_is_sequence",
            "yaml_plain_str",
            "yaml_plain_bool",
            "yaml_plain_int",
            "yaml_plain_float",
            "_yaml_coerce_node",
        ),
    },
)

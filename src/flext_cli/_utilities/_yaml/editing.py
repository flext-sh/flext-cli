"""Round-trip YAML tree-editing helpers behind ``u.Cli.yaml_*``.

Comment/anchor-aware editing operations on parsed YAML trees: anchor clearing,
comment copying, pre-key comment insertion, in-place value updates, and
order-preserving overlays.

NOTE (multi-agent): mro-i6nq.13 — extracted from the removed
``_yaml_roundtrip_parts/..._part_02``. Composed into ``FlextCliUtilitiesYaml``
via MRO in ``yaml.py``; consumes the engine + convert mixins through the base
class. Do not duplicate these operations in a leaf module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import ClassVar, cast

from flext_core import u
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.tokens import CommentToken as RuamelCommentToken

from flext_cli import p, t
from flext_cli._utilities._yaml import FlextCliUtilitiesYamlEngine


class FlextCliUtilitiesYamlEditing(FlextCliUtilitiesYamlEngine):
    """Comment/anchor-aware editing operations on parsed YAML trees."""

    _module_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)

    @staticmethod
    def _yaml_has_anchor(value: t.Cli.YamlValue) -> bool:
        """Return True when a value exposes the ruamel anchor API.

        Returns:
            True when a value exposes the ruamel anchor API.

        """
        return hasattr(value, "yaml_set_anchor")

    @staticmethod
    def yaml_clear_anchors(node: t.Cli.YamlValue) -> None:
        """Clear ruamel anchors recursively from a YAML value."""
        if node is None:
            return
        if FlextCliUtilitiesYamlEditing._yaml_has_anchor(node):
            cast("p.Cli.YamlAnchorNode", node).yaml_set_anchor(None)
        if isinstance(node, Mapping):
            for value in node.values():
                FlextCliUtilitiesYamlEditing.yaml_clear_anchors(value)
        elif FlextCliUtilitiesYamlEditing.yaml_is_sequence(node):
            items = cast("Sequence[t.Cli.YamlValue]", node)
            for item in items:
                FlextCliUtilitiesYamlEditing.yaml_clear_anchors(item)

    @staticmethod
    def yaml_deep_copy_comments(src: t.Cli.YamlNode, dst: t.Cli.YamlNode) -> None:
        """Copy ruamel comments from *src* to *dst* for commented containers."""
        if isinstance(src, CommentedMap) and isinstance(dst, CommentedMap):
            src_ca = cast("p.Cli.YamlCommentCarrier", src).ca
            dst_ca = cast("p.Cli.YamlCommentCarrier", dst).ca
            dst_ca.comment = src_ca.comment
            src_map = cast("Mapping[str, t.Cli.YamlNode]", src)
            dst_map = cast("Mapping[str, t.Cli.YamlNode]", dst)
            for key in src_map:
                if key in dst_map:
                    FlextCliUtilitiesYamlEditing.yaml_deep_copy_comments(
                        src_map[key],
                        dst_map[key],
                    )
        elif isinstance(src, CommentedSeq) and isinstance(dst, CommentedSeq):
            src_ca = cast("p.Cli.YamlCommentCarrier", src).ca
            dst_ca = cast("p.Cli.YamlCommentCarrier", dst).ca
            dst_ca.comment = src_ca.comment
            src_seq = cast("Sequence[t.Cli.YamlNode]", src)
            dst_seq = cast("Sequence[t.Cli.YamlNode]", dst)
            for index, item in enumerate(src_seq):
                if index < len(dst_seq):
                    FlextCliUtilitiesYamlEditing.yaml_deep_copy_comments(
                        item,
                        dst_seq[index],
                    )

    @staticmethod
    def yaml_pre_key_tokens(node: CommentedMap, key: str) -> list[RuamelCommentToken]:
        """Return the existing pre-key comment tokens for one key.

        Returns:
            The existing pre-key comment tokens for one key.

        """
        existing = cast("p.Cli.YamlCommentCarrier", node).ca.items.get(key)
        if not existing or not existing[1]:
            return []
        post = existing[1]
        if isinstance(post, RuamelCommentToken):
            return [post]
        if isinstance(post, list):
            tokens = cast("Sequence[object]", post)
            return [token for token in tokens if isinstance(token, RuamelCommentToken)]
        return []

    @staticmethod
    def _yaml_comment_core(text: str) -> str:
        """Reduce a comment to its framing-insensitive core text.

        Returns:
            The resulting ``str``.

        """
        return text.lstrip("#").rstrip("\n").strip()

    @staticmethod
    def yaml_has_key_comment(node: CommentedMap, key: str, text: str) -> bool:
        r"""Return True when a pre-key comment with the same core text exists.

        NOTE (multi-agent): the comparison is framing-insensitive on BOTH
        sides ("# x", "# x\n" and "#x" all match the stored token "# x\n")
        because the write path normalizes through the same helper. This keeps
        ``yaml_add_pre_key_comment`` idempotent for any caller-supplied form;
        charts callers pass the full "# ...\n" token form and behave
        unchanged. Do NOT reintroduce a raw ``token.value == text`` comparison
        — it silently double-inserts for non-canonical input.

        Returns:
            True when a pre-key comment with the same core text exists.

        """
        wanted = FlextCliUtilitiesYamlEditing._yaml_comment_core(text)
        return any(
            FlextCliUtilitiesYamlEditing._yaml_comment_core(token.value) == wanted
            for token in FlextCliUtilitiesYamlEditing.yaml_pre_key_tokens(
                node,
                key,
            )
        )

    @staticmethod
    def yaml_add_pre_key_comment(
        node: CommentedMap,
        key: str,
        text: str,
        path: tuple[str, ...] = (),
    ) -> None:
        """Insert one pre-key comment for a key. Idempotent for any input form."""
        if FlextCliUtilitiesYamlEditing.yaml_has_key_comment(node, key, text):
            return
        comment_text = FlextCliUtilitiesYamlEditing._yaml_comment_core(text)
        indent = max(len(path) - 1, 0) * 2
        setter = cast("p.Cli.YamlCommentKeySetter", node)
        setter.yaml_set_comment_before_after_key(
            key,
            before=comment_text,
            indent=indent,
        )

    @staticmethod
    def yaml_force_block_style(node: t.Cli.YamlNode) -> None:
        """Force block-style rendering for non-empty commented containers."""
        if isinstance(node, CommentedMap):
            if not node:
                return
            cast("p.Cli.YamlFlowStyleCarrier", node).fa.set_block_style()
            values = cast("Mapping[str, t.Cli.YamlNode]", node).values()
            for value in values:
                FlextCliUtilitiesYamlEditing.yaml_force_block_style(value)
        elif isinstance(node, CommentedSeq):
            if not node:
                return
            cast("p.Cli.YamlFlowStyleCarrier", node).fa.set_block_style()
            items = cast("Sequence[t.Cli.YamlNode]", node)
            for item in items:
                FlextCliUtilitiesYamlEditing.yaml_force_block_style(item)

    @staticmethod
    def yaml_update_value_inplace(
        node: CommentedMap,
        key: str,
        value: t.Cli.YamlValue,
    ) -> None:
        """Update one key value, preserving its existing pre-key comments."""
        if isinstance(value, (dict, list)):
            node[key] = FlextCliUtilitiesYamlEditing.yaml_deep_to_commented(value)
        else:
            node[key] = value

    @staticmethod
    def yaml_overlay_preserving_order(
        base: CommentedMap,
        overlay: Mapping[str, t.Cli.YamlValue] | CommentedMap,
    ) -> None:
        """Overwrite *base* with *overlay*, preserving the original key order.

        New keys are appended at the end of the level so the pre-key comments
        of existing keys keep their position.
        """
        new_keys: list[tuple[str, t.Cli.YamlValue]] = []
        overlay_map = cast("Mapping[str, t.Cli.YamlValue]", overlay)
        base_map = cast("Mapping[str, t.Cli.YamlValue]", base)
        for key, value in overlay_map.items():
            if key in base_map:
                current = base_map[key]
                if isinstance(current, CommentedMap) and isinstance(value, dict):
                    FlextCliUtilitiesYamlEditing.yaml_overlay_preserving_order(
                        current,
                        value,
                    )
                else:
                    FlextCliUtilitiesYamlEditing.yaml_update_value_inplace(
                        base,
                        key,
                        value,
                    )
            else:
                new_keys.append((
                    key,
                    FlextCliUtilitiesYamlEditing.yaml_deep_to_commented(value),
                ))
        for key, value in new_keys:
            base[key] = value


__all__: list[str] = ["FlextCliUtilitiesYamlEditing"]

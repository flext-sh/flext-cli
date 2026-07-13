"""Behavioral tests for round-trip YAML helpers exposed via ``u.Cli``.

Covers the comment/quote-preserving round-trip contract (load/dump, plain
conversion, scalar normalization, anchor clearing, comment editing, and
order-preserving overlays) through the published ``u.Cli`` surface. Every
assertion checks observable behavior: ``r[T]`` outcomes, dumped text, and
tree state read back through the public API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from tests import t
from tests import u
from flext_tests import tm

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliYamlRoundtripLoad:
    """Load/dump round-trip contract of ``u.Cli.yaml_roundtrip_*``."""

    def test_round_trip_preserves_comments_quotes_and_order(
        self, tmp_path: Path
    ) -> None:
        source = (
            "# top comment\n"
            "global:\n"
            '  domain: "example.com"  # inline comment\n'
            "  replicas: 2\n"
            "services:\n"
            "  - name: web\n"
        )
        path = tmp_path / "values.yaml"
        path.write_text(source, encoding="utf-8")

        node = u.Cli.yaml_roundtrip_load_map(path).unwrap()
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped, has="# top comment")
        tm.that(dumped, has='domain: "example.com"')
        tm.that(dumped, has="# inline comment")
        assert dumped.index("global:") < dumped.index("services:")

    def test_load_missing_file_fails(self, tmp_path: Path) -> None:
        result = u.Cli.yaml_roundtrip_load(tmp_path / "absent.yaml")

        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="not found")

    def test_load_map_rejects_scalar_root(self, tmp_path: Path) -> None:
        path = tmp_path / "scalar.yaml"
        path.write_text("just-a-string\n", encoding="utf-8")

        result = u.Cli.yaml_roundtrip_load_map(path)

        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="must be a mapping")

    def test_load_map_text_rejects_sequence_root(self) -> None:
        result = u.Cli.yaml_roundtrip_load_map_text("- a\n- b\n")

        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="must be a mapping")

    def test_invalid_yaml_fails_loud(self) -> None:
        result = u.Cli.yaml_roundtrip_load_text("a: [unclosed\n")

        tm.fail(result)
        tm.that(result.error, none=False)


class TestsFlextCliYamlRoundtripConvert:
    """Plain<->commented conversion contract of ``u.Cli``."""

    def test_to_plain_unwraps_commented_tree(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text("a:\n  b: 1\n").unwrap()

        plain = u.Cli.yaml_to_plain(node)

        tm.that(plain, eq={"a": {"b": 1}})
        assert type(plain) is dict

    def test_deep_to_commented_wraps_plain_mapping(self) -> None:
        data: t.Cli.YamlValue = {"a": [1, "x"], "b": {"c": True}}

        node = u.Cli.yaml_deep_to_commented(data)

        tm.that(node, is_=CommentedMap)
        tm.that(node["a"], is_=CommentedSeq)
        tm.that(u.Cli.yaml_to_plain(node), eq={"a": [1, "x"], "b": {"c": True}})

    def test_deep_to_commented_quotes_yaml_11_tokens(self) -> None:
        node = u.Cli.yaml_deep_to_commented({"flag": "yes", "name": "web"})

        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped, has='flag: "yes"')
        tm.that(dumped, has="name: web")

    def test_deep_to_commented_multiline_uses_literal_style(self) -> None:
        node = u.Cli.yaml_deep_to_commented({"script": "line1\nline2\n"})

        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped, has="script: |")
        tm.that(dumped, has="line1")
        tm.that(dumped, has="line2")

    def test_is_sequence_keeps_strings_scalar(self) -> None:
        seq = u.Cli.yaml_roundtrip_load_text("- 1\n").unwrap()
        scalar = u.Cli.yaml_roundtrip_load_text("abc\n").unwrap()

        tm.that(u.Cli.yaml_is_sequence(seq), eq=True)
        tm.that(u.Cli.yaml_is_sequence(CommentedSeq([1])), eq=True)
        tm.that(u.Cli.yaml_is_sequence(scalar), eq=False)
        tm.that(u.Cli.yaml_is_sequence(None), eq=False)


class TestsFlextCliYamlScalars:
    """Scalar normalization contract (ruamel subclasses -> builtins)."""

    def test_plain_str_unwraps_ruamel_subclass(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text('k: "quoted"\n').unwrap()
        value = node["k"]

        plain = u.Cli.yaml_plain_str(value)

        tm.that(value, is_=str)
        assert type(value) is not str
        tm.that(plain, eq="quoted")
        assert type(plain) is str

    def test_plain_int_float_bool_unwrap_subclasses(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text("i: 3\nf: 1.5\nb: true\n").unwrap()

        plain_int = u.Cli.yaml_plain_int(node["i"])
        plain_float = u.Cli.yaml_plain_float(node["f"])
        plain_bool = u.Cli.yaml_plain_bool(node["b"])

        tm.that(plain_int, eq=3)
        assert type(plain_int) is int
        tm.that(plain_float, eq=pytest.approx(1.5))
        tm.that(plain_bool, eq=True)

    def test_normalize_scalar_keeps_containers_untouched(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text("a: 1\n").unwrap()

        assert u.Cli.yaml_normalize_scalar(node) is node
        tm.that(u.Cli.yaml_normalize_scalar(node["a"]), eq=1)


class TestsFlextCliYamlAnchors:
    """Anchor handling contract of ``u.Cli.yaml_clear_anchors``."""

    def test_clear_anchors_strips_anchor_definitions(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text(
            "base: &base\n  a: 1\nuse: *base\n"
        ).unwrap()

        u.Cli.yaml_clear_anchors(node)
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped, lacks="&base")
        tm.that(dumped, lacks="*base")
        tm.that(u.Cli.yaml_to_plain(node), eq={"base": {"a": 1}, "use": {"a": 1}})


class TestsFlextCliYamlComments:
    """Comment transfer and pre-key comment contract."""

    def test_add_pre_key_comment_is_idempotent(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text("a: 1\n").unwrap()

        u.Cli.yaml_add_pre_key_comment(node, "a", "# origin: subchart")
        u.Cli.yaml_add_pre_key_comment(node, "a", "# origin: subchart\n")
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped.count("origin: subchart"), eq=1)

    def test_has_key_comment_matches_inserted_text(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text("a: 1\n").unwrap()

        u.Cli.yaml_add_pre_key_comment(node, "a", "# hello")

        assert u.Cli.yaml_has_key_comment(node, "a", "# hello")
        assert u.Cli.yaml_has_key_comment(node, "a", "# hello\n")
        assert not u.Cli.yaml_has_key_comment(node, "a", "# other")

    def test_copy_key_comment_moves_comment(self) -> None:
        src = u.Cli.yaml_roundtrip_load_map_text("a: 1\nb: 2\n").unwrap()
        u.Cli.yaml_add_pre_key_comment(src, "b", "# keep me")
        target = u.Cli.yaml_deep_to_commented({"b": 0})

        u.Cli.yaml_copy_key_comment(src, "b", target)
        dumped = u.Cli.yaml_roundtrip_dump_text(target).unwrap()

        tm.that(dumped, has="keep me")

    def test_force_block_style_renders_block(self) -> None:
        node = u.Cli.yaml_deep_to_commented({"a": {"b": 1}})

        u.Cli.yaml_force_block_style(node)
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped, has="a:\n")
        tm.that(dumped, has="  b: 1")
        tm.that(dumped, lacks="{b:")

    def test_deep_copy_comments_between_trees(self) -> None:
        src = u.Cli.yaml_roundtrip_load_map_text("# doc\na: 1\n").unwrap()
        dst = u.Cli.yaml_deep_to_commented({"a": 2})

        u.Cli.yaml_deep_copy_comments(src, dst)
        dumped = u.Cli.yaml_roundtrip_dump_text(dst).unwrap()

        tm.that(dumped, has="# doc")


class TestsFlextCliYamlEdit:
    """In-place edit and overlay contract."""

    def test_overlay_preserving_order_keeps_base_order(self) -> None:
        base = u.Cli.yaml_roundtrip_load_map_text("a: 1\nb: 2\n").unwrap()

        u.Cli.yaml_overlay_preserving_order(base, {"b": 20, "c": 30})

        tm.that(list(base.keys()), eq=["a", "b", "c"])
        tm.that(base["b"], eq=20)
        tm.that(base["c"], eq=30)

    def test_update_value_inplace_preserves_comments(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text("# note\na: 1\n").unwrap()

        u.Cli.yaml_update_value_inplace(node, "a", 99)
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped, has="# note")
        tm.that(dumped, has="a: 99")

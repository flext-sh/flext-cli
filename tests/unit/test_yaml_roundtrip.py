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

from tests.typings import t
from tests.utilities import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliYamlRoundtripLoad:
    """Load/dump round-trip contract of ``u.Cli.yaml_roundtrip_*``."""

    def test_round_trip_preserves_comments_quotes_and_order(
        self,
        tmp_path: Path,
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

        assert "# top comment" in dumped
        assert 'domain: "example.com"' in dumped
        assert "# inline comment" in dumped
        assert dumped.index("global:") < dumped.index("services:")

    def test_load_missing_file_fails(self, tmp_path: Path) -> None:
        result = u.Cli.yaml_roundtrip_load(tmp_path / "absent.yaml")

        assert not result.success
        assert result.error is not None
        assert "not found" in result.error

    def test_load_map_rejects_scalar_root(self, tmp_path: Path) -> None:
        path = tmp_path / "scalar.yaml"
        path.write_text("just-a-string\n", encoding="utf-8")

        result = u.Cli.yaml_roundtrip_load_map(path)

        assert not result.success
        assert result.error is not None
        assert "must be a mapping" in result.error

    def test_load_map_text_rejects_sequence_root(self) -> None:
        result = u.Cli.yaml_roundtrip_load_map_text("- a\n- b\n")

        assert not result.success
        assert result.error is not None
        assert "must be a mapping" in result.error

    def test_invalid_yaml_fails_loud(self) -> None:
        result = u.Cli.yaml_roundtrip_load_text("a: [unclosed\n")

        assert not result.success
        assert result.error is not None


class TestsFlextCliYamlRoundtripConvert:
    """Plain<->commented conversion contract of ``u.Cli``."""

    def test_to_plain_unwraps_commented_tree(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text("a:\n  b: 1\n").unwrap()

        plain = u.Cli.yaml_to_plain(node)

        assert plain == {"a": {"b": 1}}
        assert type(plain) is dict

    def test_deep_to_commented_wraps_plain_mapping(self) -> None:
        data: t.Cli.YamlValue = {"a": [1, "x"], "b": {"c": True}}

        node = u.Cli.yaml_deep_to_commented(data)

        assert isinstance(node, CommentedMap)
        assert isinstance(node["a"], CommentedSeq)
        assert u.Cli.yaml_to_plain(node) == {"a": [1, "x"], "b": {"c": True}}

    def test_deep_to_commented_quotes_yaml_11_tokens(self) -> None:
        node = u.Cli.yaml_deep_to_commented({"flag": "yes", "name": "web"})

        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        assert 'flag: "yes"' in dumped
        assert "name: web" in dumped

    def test_deep_to_commented_multiline_uses_literal_style(self) -> None:
        node = u.Cli.yaml_deep_to_commented({"script": "line1\nline2\n"})

        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        assert "script: |" in dumped
        assert "line1" in dumped
        assert "line2" in dumped

    def test_is_sequence_keeps_strings_scalar(self) -> None:
        seq = u.Cli.yaml_roundtrip_load_text("- 1\n").unwrap()
        scalar = u.Cli.yaml_roundtrip_load_text("abc\n").unwrap()

        assert u.Cli.yaml_is_sequence(seq) is True
        assert u.Cli.yaml_is_sequence(CommentedSeq([1])) is True
        assert u.Cli.yaml_is_sequence(scalar) is False
        assert u.Cli.yaml_is_sequence(None) is False


class TestsFlextCliYamlScalars:
    """Scalar normalization contract (ruamel subclasses -> builtins)."""

    def test_plain_str_unwraps_ruamel_subclass(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text('k: "quoted"\n').unwrap()
        value = node["k"]

        plain = u.Cli.yaml_plain_str(value)

        assert isinstance(value, str)
        assert type(value) is not str
        assert plain == "quoted"
        assert type(plain) is str

    def test_plain_int_float_bool_unwrap_subclasses(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text("i: 3\nf: 1.5\nb: true\n").unwrap()

        plain_int = u.Cli.yaml_plain_int(node["i"])
        plain_float = u.Cli.yaml_plain_float(node["f"])
        plain_bool = u.Cli.yaml_plain_bool(node["b"])

        assert plain_int == 3
        assert type(plain_int) is int
        assert plain_float == pytest.approx(1.5)
        assert plain_bool is True

    def test_normalize_scalar_keeps_containers_untouched(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text("a: 1\n").unwrap()

        assert u.Cli.yaml_normalize_scalar(node) is node
        assert u.Cli.yaml_normalize_scalar(node["a"]) == 1


class TestsFlextCliYamlAnchors:
    """Anchor handling contract of ``u.Cli.yaml_clear_anchors``."""

    def test_clear_anchors_strips_anchor_definitions(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text(
            "base: &base\n  a: 1\nuse: *base\n",
        ).unwrap()

        u.Cli.yaml_clear_anchors(node)
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        assert "&base" not in dumped
        assert "*base" not in dumped
        assert u.Cli.yaml_to_plain(node) == {"base": {"a": 1}, "use": {"a": 1}}


class TestsFlextCliYamlComments:
    """Comment transfer and pre-key comment contract."""

    def test_add_pre_key_comment_is_idempotent(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text("a: 1\n").unwrap()

        u.Cli.yaml_add_pre_key_comment(node, "a", "# origin: subchart")
        u.Cli.yaml_add_pre_key_comment(node, "a", "# origin: subchart\n")
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        assert dumped.count("origin: subchart") == 1

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

        assert "keep me" in dumped

    def test_force_block_style_renders_block(self) -> None:
        node = u.Cli.yaml_deep_to_commented({"a": {"b": 1}})

        u.Cli.yaml_force_block_style(node)
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        assert "a:\n" in dumped
        assert "  b: 1" in dumped
        assert "{b:" not in dumped

    def test_deep_copy_comments_between_trees(self) -> None:
        src = u.Cli.yaml_roundtrip_load_map_text("# doc\na: 1\n").unwrap()
        dst = u.Cli.yaml_deep_to_commented({"a": 2})

        u.Cli.yaml_deep_copy_comments(src, dst)
        dumped = u.Cli.yaml_roundtrip_dump_text(dst).unwrap()

        assert "# doc" in dumped


class TestsFlextCliYamlEdit:
    """In-place edit and overlay contract."""

    def test_overlay_preserving_order_keeps_base_order(self) -> None:
        base = u.Cli.yaml_roundtrip_load_map_text("a: 1\nb: 2\n").unwrap()

        u.Cli.yaml_overlay_preserving_order(base, {"b": 20, "c": 30})

        assert list(base.keys()) == ["a", "b", "c"]
        assert base["b"] == 20
        assert base["c"] == 30

    def test_update_value_inplace_preserves_comments(self) -> None:
        node = u.Cli.yaml_roundtrip_load_map_text("# note\na: 1\n").unwrap()

        u.Cli.yaml_update_value_inplace(node, "a", 99)
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        assert "# note" in dumped
        assert "a: 99" in dumped

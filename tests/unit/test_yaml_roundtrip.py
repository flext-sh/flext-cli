"""Behavioral tests for round-trip YAML helpers exposed via ``u.Cli``.

Covers the comment/quote-preserving round-trip contract (load/dump, plain
conversion, scalar normalization, anchor clearing, comment editing, and
order-preserving overlays) through the published ``u.Cli`` surface. Every
assertion checks observable behavior: ``r[T]`` outcomes, dumped text, and
tree state read back through the public API.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from concurrent.futures import ThreadPoolExecutor
from typing import TYPE_CHECKING, cast

import pytest
from ruamel.yaml.comments import CommentedMap, CommentedSeq

from tests import c, t, tm, u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliYamlRoundtripLoad:
    """Load/dump round-trip contract of ``u.Cli.yaml_roundtrip_*``."""

    @staticmethod
    def test_empty_yaml_stream_contains_no_documents() -> None:
        """An empty stream is data, distinct from an explicit null document."""
        tm.that(tm.ok(u.Cli.yaml_parse_documents("# no documents\n")), empty=True)

    @staticmethod
    def test_mapping_document_stream_preserves_order_and_literal_markers() -> None:
        """Document markers inside scalar content never split that content."""
        documents = tm.ok(
            u.Cli.yaml_parse_documents(
                "id: first\ncontent: |\n  ---\n  retained\n"
                '--- # document boundary\nid: second\ncontent: "---"\n'
            )
        )
        tm.that(
            documents,
            eq=(
                {"id": "first", "content": "---\nretained\n"},
                {"id": "second", "content": "---"},
            ),
        )

    @staticmethod
    @pytest.mark.parametrize(
        "suffix",
        ["id: second\nid: contradictory\n", "items: [\n"],
    )
    def test_document_stream_rejects_the_first_bad_document(suffix: str) -> None:
        """A valid prefix never turns a broken stream into partial success."""
        outcome = u.Cli.yaml_parse_documents("id: first\n---\n" + suffix)
        tm.fail(outcome, has="YAML parse error")
        tm.not_none(outcome.exception)

    @staticmethod
    def test_document_stream_requires_each_root_to_be_a_mapping() -> None:
        """A scalar document remains a validation failure after a valid map."""
        outcome = u.Cli.yaml_parse_documents("id: first\n---\n- scalar\n")
        tm.fail(outcome, has="YAML validation error")
        tm.not_none(outcome.exception)

    @staticmethod
    def test_load_missing_file_fails(tmp_path: Path) -> None:
        """Verify that load missing file fails."""
        result = u.Cli.yaml_roundtrip_load(tmp_path / "absent.yaml")

        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="not found")

    @staticmethod
    def test_load_map_text_rejects_sequence_root() -> None:
        """Verify that load map text rejects sequence root."""
        result = u.Cli.yaml_roundtrip_load_map_text("- a\n- b\n")

        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="must be a mapping")

    @staticmethod
    def test_invalid_yaml_fails_loud() -> None:
        """Verify that invalid yaml fails loud."""
        result = u.Cli.yaml_roundtrip_load_text("a: [unclosed\n")

        tm.fail(result)
        tm.that(result.error, none=False)

    @staticmethod
    def test_load_text_empty_document_fails_without_exception() -> None:
        """Verify that load text empty document fails without exception."""
        for text in ("", "# only a comment\n", "---\n", "~\n"):
            result = u.Cli.yaml_roundtrip_load_text(text)

            tm.fail(result)
            tm.that(result.error, none=False)
            tm.that(result.error, has="empty")

    @staticmethod
    def test_load_empty_document_fails_without_exception(tmp_path: Path) -> None:
        """Verify that load empty document fails without exception."""
        path = tmp_path / "comments.yaml"
        path.write_text("# header comment\n# another\n", encoding="utf-8")

        result = u.Cli.yaml_roundtrip_load(path)

        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="empty")

    @staticmethod
    def test_load_map_text_empty_document_fails_without_exception() -> None:
        """Verify that load map text empty document fails without exception."""
        result = u.Cli.yaml_roundtrip_load_map_text("# comment only\n")

        tm.fail(result)
        tm.that(result.error, none=False)

    @staticmethod
    def test_yaml_parse_empty_document_fails_without_exception() -> None:
        """Verify that yaml parse empty document fails without exception."""
        result = u.Cli.yaml_parse("# comment only\n")

        tm.fail(result)
        tm.that(result.error, none=False)

    @staticmethod
    @pytest.mark.slow
    def test_roundtrip_load_text_is_thread_safe() -> None:
        """Verify that roundtrip load text is thread safe."""
        documents = [
            (
                f"# document {index}\n"
                f"root{index}:\n"
                f"  name: service-{index}\n"
                f"  replicas: {index}\n"
                f"  tags:\n"
                f"    - alpha-{index}\n"
                f"    - beta-{index}\n"
            )
            for index in range(8)
        ]
        failures: list[BaseException] = []

        def parse_repeatedly(document: str) -> None:
            for _ in range(250):
                try:
                    result = u.Cli.yaml_roundtrip_load_text(document)
                    if result.failure:
                        failures.append(ValueError(result.error))
                        break
                    result.unwrap()
                except c.CATCHABLE_RUNTIME_EXCEPTIONS as exc:
                    failures.append(exc)
                    break

        with ThreadPoolExecutor(max_workers=len(documents)) as pool:
            list(pool.map(parse_repeatedly, documents))

        tm.that(failures, eq=[])


class TestsFlextCliYamlRoundtripConvert:
    """Plain<->commented conversion contract of ``u.Cli``."""

    @staticmethod
    def test_to_plain_unwraps_commented_tree() -> None:
        """Verify that to plain unwraps commented tree."""
        node = u.Cli.yaml_roundtrip_load_map_text("a:\n  b: 1\n").unwrap()

        plain = u.Cli.yaml_to_plain(node)

        tm.that(plain, eq={"a": {"b": 1}})
        tm.ok(type(plain) is dict)

    @staticmethod
    def test_deep_to_commented_wraps_plain_mapping() -> None:
        """Verify that deep to commented wraps plain mapping."""
        data: t.Cli.YamlValue = {"a": [1, "x"], "b": {"c": True}}

        node = u.Cli.yaml_deep_to_commented(data)

        tm.that(node, is_=CommentedMap)
        node_map = cast("Mapping[str, t.Cli.YamlValue]", node)
        tm.that(node_map["a"], is_=CommentedSeq)
        expected: t.JsonMapping = {"a": [1, "x"], "b": {"c": True}}
        tm.that(
            cast("dict[str, object]", u.Cli.yaml_to_plain(node)),
            eq=cast("dict[str, object]", expected),
        )

    @staticmethod
    def test_deep_to_commented_quotes_yaml_11_tokens() -> None:
        """Verify that deep to commented quotes yaml 11 tokens."""
        node = u.Cli.yaml_deep_to_commented({"flag": "yes", "name": "web"})

        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped, has='flag: "yes"')
        tm.that(dumped, has="name: web")

    @staticmethod
    def test_deep_to_commented_multiline_uses_literal_style() -> None:
        """Verify that deep to commented multiline uses literal style."""
        node = u.Cli.yaml_deep_to_commented({"script": "line1\nline2\n"})

        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped, has="script: |")
        tm.that(dumped, has="line1")
        tm.that(dumped, has="line2")

    @staticmethod
    def test_is_sequence_keeps_strings_scalar() -> None:
        """Verify that is sequence keeps strings scalar."""
        seq = u.Cli.yaml_roundtrip_load_text("- 1\n").unwrap()
        scalar = u.Cli.yaml_roundtrip_load_text("abc\n").unwrap()

        tm.ok(u.Cli.yaml_is_sequence(seq))
        tm.ok(u.Cli.yaml_is_sequence(CommentedSeq([1])))
        tm.fail(u.Cli.yaml_is_sequence(scalar))
        tm.fail(u.Cli.yaml_is_sequence(None))


class TestsFlextCliYamlScalars:
    """Scalar normalization contract (ruamel subclasses -> builtins)."""

    @staticmethod
    def test_plain_str_unwraps_ruamel_subclass() -> None:
        """Verify that plain str unwraps ruamel subclass."""
        node = u.Cli.yaml_roundtrip_load_map_text('k: "quoted"\n').unwrap()
        node_map = cast("Mapping[str, t.Cli.YamlScalar]", node)
        value = node_map["k"]

        plain = u.Cli.yaml_plain_str(value)

        tm.that(value, is_=str)
        tm.ok(type(value) is not str)
        tm.that(plain, eq="quoted")
        tm.ok(type(plain) is str)

    @staticmethod
    def test_plain_int_float_bool_unwrap_subclasses() -> None:
        """Verify that plain int float bool unwrap subclasses."""
        node = u.Cli.yaml_roundtrip_load_map_text("i: 3\nf: 1.5\nb: true\n").unwrap()
        node_map = cast("Mapping[str, t.Cli.YamlScalar]", node)

        plain_int = u.Cli.yaml_plain_int(cast("int", node_map["i"]))
        plain_float = u.Cli.yaml_plain_float(cast("float", node_map["f"]))
        plain_bool = u.Cli.yaml_plain_bool(node_map["b"])

        tm.that(plain_int, eq=3)
        tm.ok(type(plain_int) is int)
        tm.ok(plain_float == pytest.approx(1.5))
        tm.ok(plain_bool)


class TestsFlextCliYamlAnchors:
    """Anchor handling contract of ``u.Cli.yaml_clear_anchors``."""

    @staticmethod
    def test_clear_anchors_strips_anchor_definitions() -> None:
        """Verify that clear anchors strips anchor definitions."""
        node = u.Cli.yaml_roundtrip_load_map_text(
            "base: &base\n  a: 1\nuse: *base\n",
        ).unwrap()

        u.Cli.yaml_clear_anchors(node)
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped, lacks="&base")
        tm.that(dumped, lacks="*base")
        tm.that(u.Cli.yaml_to_plain(node), eq={"base": {"a": 1}, "use": {"a": 1}})


class TestsFlextCliYamlComments:
    """Comment transfer and pre-key comment contract."""

    @staticmethod
    def test_add_pre_key_comment_is_idempotent() -> None:
        """Verify that add pre key comment is idempotent."""
        node = u.Cli.yaml_roundtrip_load_map_text("a: 1\n").unwrap()

        u.Cli.yaml_add_pre_key_comment(node, "a", "# origin: subchart")
        u.Cli.yaml_add_pre_key_comment(node, "a", "# origin: subchart\n")
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped.count("origin: subchart"), eq=1)

    @staticmethod
    def test_has_key_comment_matches_inserted_text() -> None:
        """Verify that has key comment matches inserted text."""
        node = u.Cli.yaml_roundtrip_load_map_text("a: 1\n").unwrap()

        u.Cli.yaml_add_pre_key_comment(node, "a", "# hello")

        tm.ok(u.Cli.yaml_has_key_comment(node, "a", "# hello"))
        tm.ok(u.Cli.yaml_has_key_comment(node, "a", "# hello\n"))
        tm.fail(u.Cli.yaml_has_key_comment(node, "a", "# other"))

    @staticmethod
    def test_force_block_style_renders_block() -> None:
        """Verify that force block style renders block."""
        node = u.Cli.yaml_deep_to_commented({"a": {"b": 1}})

        u.Cli.yaml_force_block_style(node)
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped, has="a:\n")
        tm.that(dumped, has="  b: 1")
        tm.that(dumped, lacks="{b:")

    @staticmethod
    def test_deep_copy_comments_between_trees() -> None:
        """Verify that deep copy comments between trees."""
        src = u.Cli.yaml_roundtrip_load_map_text("# doc\na: 1\n").unwrap()
        dst = u.Cli.yaml_deep_to_commented({"a": 2})

        u.Cli.yaml_deep_copy_comments(src, dst)
        dumped = u.Cli.yaml_roundtrip_dump_text(dst).unwrap()

        tm.that(dumped, has="# doc")


class TestsFlextCliYamlEdit:
    """In-place edit and overlay contract."""

    @staticmethod
    def test_overlay_preserving_order_keeps_base_order() -> None:
        """Verify that overlay preserving order keeps base order."""
        base = u.Cli.yaml_roundtrip_load_map_text("a: 1\nb: 2\n").unwrap()
        base_map = cast("Mapping[str, t.Cli.YamlScalar]", base)

        u.Cli.yaml_overlay_preserving_order(base, {"b": 20, "c": 30})

        tm.that(list(base_map.keys()), eq=["a", "b", "c"])
        tm.that(base_map["b"], eq=20)
        tm.that(base_map["c"], eq=30)

    @staticmethod
    def test_update_value_inplace_preserves_comments() -> None:
        """Verify that update value inplace preserves comments."""
        node = u.Cli.yaml_roundtrip_load_map_text("# note\na: 1\n").unwrap()

        u.Cli.yaml_update_value_inplace(node, "a", 99)
        dumped = u.Cli.yaml_roundtrip_dump_text(node).unwrap()

        tm.that(dumped, has="# note")
        tm.that(dumped, has="a: 99")

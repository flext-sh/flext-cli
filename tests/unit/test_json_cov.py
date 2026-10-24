"""Behavioral tests for the public FlextCli JSON utility contract (``u.Cli.json_*``).

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests import c, m, t, tm, u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliJsonCov:
    """Assert the observable contract of the ``u.Cli`` JSON helpers."""

    # ----- normalize -------------------------------------------------------

    @staticmethod
    def test_normalize_json_value_preserves_mapping() -> None:
        """Verify that normalize json value preserves mapping."""
        tm.that(u.Cli.normalize_json_value({"key": "value"}), eq={"key": "value"})

    @staticmethod
    def test_json_dict_adapter_preserves_validated_nested_payload() -> None:
        """Concrete object admission preserves the mapping adapter's JSON values."""
        source: t.JsonDict = {"active": True, "values": [None, {"name": "native"}]}
        mapping = u.Cli.JSON_MAPPING_ADAPTER.validate_python(source)
        concrete: t.JsonDict = u.json_dict_adapter().validate_python(source)
        tm.that(concrete, eq=mapping)
        tm.that(
            u.normalize_to_json_value({"metadata": concrete}),
            eq={"metadata": source},
        )

    @staticmethod
    @pytest.mark.parametrize("source", [None, "invalid", ["not", "an object"]])
    def test_json_object_adapters_reject_non_mapping_input(source: t.JsonValue) -> None:
        """Object admission does not widen into an arbitrary JSON value schema."""
        with pytest.raises(m.ValidationError):
            u.Cli.JSON_MAPPING_ADAPTER.validate_python(source)
        with pytest.raises(m.ValidationError):
            u.json_dict_adapter().validate_python(source)

    # ----- json_read (fallible, r[JsonMapping]) ----------------------------

    @staticmethod
    def test_json_read_missing_file_fails_loudly(tmp_path: Path) -> None:
        """Verify that json read missing file fails loudly."""
        result = u.Cli.json_read(tmp_path / "missing.json")
        tm.fail(result)
        tm.that(result.error, has="file not found")

    @staticmethod
    def test_json_read_valid_object_returns_parsed_mapping(
        tmp_path: Path,
    ) -> None:
        """Verify that json read valid object returns parsed mapping."""
        path = tmp_path / "data.json"
        path.write_text('{"key": "value"}', encoding="utf-8")
        result = u.Cli.json_read(path)
        tm.ok(result, eq={"key": "value"})

    @staticmethod
    @pytest.mark.parametrize(
        ("content", "reason"),
        [("not json!!", "malformed json"), ("[1, 2, 3]", "non-object root")],
    )
    def test_json_read_rejects_invalid_content(
        tmp_path: Path,
        content: str,
        reason: str,
    ) -> None:
        """Verify that json read rejects invalid content."""
        path = tmp_path / "bad.json"
        path.write_text(content, encoding="utf-8")
        result = u.Cli.json_read(path)
        tm.fail(result, msg=reason)
        tm.that(result.error, none=False)
        tm.that(result.error, has="json_read")

    # ----- json_write roundtrip / options ----------------------------------

    @staticmethod
    def test_json_write_then_read_roundtrips_payload(tmp_path: Path) -> None:
        """Verify that json write then read roundtrips payload."""
        path = tmp_path / "missing" / "nested" / "out.json"
        write_result = u.Cli.json_write(path, {"a": 1, "b": [1, 2]})
        tm.ok(write_result)
        read_result = u.Cli.json_read(path)
        tm.ok(read_result)
        expected: t.JsonMapping = {"a": 1, "b": [1, 2]}
        tm.that(read_result.value, eq=expected)

    @staticmethod
    @pytest.mark.parametrize("path_kind", ["symlink-ancestor", "lexical-traversal"])
    def test_json_write_rejects_path_before_creating_directories(
        tmp_path: Path,
        path_kind: str,
    ) -> None:
        """Reject unsafe destinations without mutating their parent or foreign tree."""
        foreign = tmp_path / "foreign"
        foreign.mkdir()
        sentinel = foreign / "owned.bin"
        sentinel.write_bytes(b"unchanged")
        if path_kind == "symlink-ancestor":
            alias = tmp_path / "alias"
            alias.symlink_to(foreign, target_is_directory=True)
            destination = alias / "missing" / "nested" / "out.json"
        else:
            destination = (
                tmp_path / "missing" / ".." / foreign.name / "nested" / "out.json"
            )
        entries = tuple(sorted(tmp_path.rglob("*")))
        parent_before = tmp_path.stat()
        foreign_before = foreign.stat()
        payload: t.JsonMapping = {"version": 1}

        result = u.Cli.json_write(
            destination,
            payload,
            options=m.Cli.JsonWriteOptions(),
        )

        tm.fail(result, has="json_write")
        tm.that(tuple(sorted(tmp_path.rglob("*"))), eq=entries)
        tm.that(tmp_path.stat().st_mtime_ns, eq=parent_before.st_mtime_ns)
        tm.that(foreign.stat().st_mtime_ns, eq=foreign_before.st_mtime_ns)
        tm.that(sentinel.read_bytes(), eq=b"unchanged")

    @staticmethod
    def test_json_write_sort_keys_orders_nested_keys(tmp_path: Path) -> None:
        """Verify that json write sort keys orders nested keys."""
        path = tmp_path / "sorted.json"
        payload: t.JsonPayload = {
            "z": {"b": 2, "a": 1},
            "a": [{"y": 1, "x": 0}],
        }
        result = u.Cli.json_write(
            path,
            payload,
            options=m.Cli.JsonWriteOptions(sort_keys=True),
        )
        tm.ok(result)
        data_result = u.Cli.json_loads(path.read_text())
        tm.ok(data_result)
        data = u.Cli.json_as_mapping(data_result.value)
        sorted_mapping = u.Cli.JSON_MAPPING_ADAPTER.validate_python(data["z"])
        first_item = u.Cli.JSON_MAPPING_ADAPTER.validate_python(
            u.Cli.JSON_LIST_ADAPTER.validate_python(data["a"])[0],
        )
        tm.that(list(data.keys()), eq=["a", "z"])
        tm.that(list(sorted_mapping.keys()), eq=["a", "b"])
        tm.that(list(first_item.keys()), eq=["x", "y"])

    @staticmethod
    def test_json_write_serializes_pydantic_model_as_object(
        tmp_path: Path,
    ) -> None:
        """Verify that json write serializes pydantic model as object."""
        path = tmp_path / "model.json"
        result = u.Cli.json_write(path, m.Cli.TableConfig())
        tm.ok(result)
        data_result = u.Cli.json_loads(path.read_text())
        tm.ok(data_result)
        tm.that(data_result.value, is_=dict)

    # ----- json_parse (fallible) -------------------------------------------

    @staticmethod
    def test_json_write_replaces_only_destination_and_preserves_mode(
        tmp_path: Path,
    ) -> None:
        """Publishing JSON must not truncate another hardlink to the old document."""
        path = tmp_path / "document.json"
        tm.ok(u.Cli.json_write(path, {"version": 1}))
        path.chmod(0o640)
        sibling = tmp_path / "previous.json"
        sibling.hardlink_to(path)
        before = path.stat()
        tm.ok(u.Cli.json_write(path, {"version": 2}))
        tm.fail(path.stat().st_ino == before.st_ino)
        tm.that(path.stat().st_mode, eq=before.st_mode)
        tm.that(u.Cli.json_read(path).value, eq={"version": 2})
        tm.that(u.Cli.json_read(sibling).value, eq={"version": 1})

    @staticmethod
    def test_json_parse_valid_text_succeeds() -> None:
        """Verify that json parse valid text succeeds."""
        result = u.Cli.json_parse('{"x": 1}')
        tm.ok(result)

    @staticmethod
    def test_json_parse_invalid_text_fails() -> None:
        """Verify that json parse invalid text fails."""
        result = u.Cli.json_parse("not json")
        tm.fail(result)
        tm.that(result.error, none=False)

    # ----- duplicate key rejection (opt-in) ---------------------------------

    @staticmethod
    def test_json_loads_rejects_duplicate_key_when_enabled() -> None:
        """Verify that json loads rejects a repeated key with key and path."""
        result = u.Cli.json_loads('{"a": 1, "a": 2}', reject_duplicate_keys=True)
        tm.fail(result)
        tm.that(result.error, has="duplicate JSON key 'a'")
        tm.that(result.error, has="$.a")

    @staticmethod
    def test_json_loads_rejects_nested_duplicate_key_when_enabled() -> None:
        """Verify that json loads rejects a repeated nested key with its path."""
        result = u.Cli.json_loads(
            '{"outer": {"dup": 1, "dup": 2}}',
            reject_duplicate_keys=True,
        )
        tm.fail(result)
        tm.that(result.error, has="duplicate JSON key 'dup'")
        tm.that(result.error, has="$.outer.dup")

    @staticmethod
    def test_json_loads_accepts_unique_keys_when_enabled() -> None:
        """Verify that json loads keeps parsing unique-key payloads enabled."""
        result = u.Cli.json_loads('{"a": 1, "b": [1, 2]}', reject_duplicate_keys=True)
        tm.ok(result)
        expected: t.JsonValue = {"a": 1, "b": [1, 2]}
        tm.that(result.value, eq=expected)

    @staticmethod
    def test_json_loads_default_keeps_duplicate_tolerance() -> None:
        """Verify that json loads default behavior stays unchanged on duplicates."""
        result = u.Cli.json_loads('{"a": 1, "a": 2}')
        tm.ok(result)
        expected: t.JsonValue = {"a": 2}
        tm.that(result.value, eq=expected)

    @staticmethod
    def test_json_parse_rejects_duplicate_key_when_enabled() -> None:
        """Verify that json parse rejects a repeated key with key and path."""
        result = u.Cli.json_parse(
            '{"dup": {"k": 1, "k": 2}}',
            reject_duplicate_keys=True,
        )
        tm.fail(result)
        tm.that(result.error, has="duplicate JSON key 'k'")
        tm.that(result.error, has="$.dup.k")

    @staticmethod
    def test_json_parse_accepts_unique_keys_when_enabled() -> None:
        """Verify that json parse keeps parsing unique-key payloads enabled."""
        result = u.Cli.json_parse('{"x": 1}', reject_duplicate_keys=True)
        tm.ok(result)
        expected: t.JsonValue = {"x": 1}
        tm.that(result.value, eq=expected)


class TestsFlextCliJsonNavigation:
    """Coercion, navigation and scalar extraction through the public JSON facade."""

    @staticmethod
    @pytest.mark.parametrize(
        ("value", "expected"),
        [(None, {}), ({"a": 1}, {"a": 1}), ([1, 2, 3], {})],
    )
    def test_json_as_mapping_coerces_to_mapping_or_empty(
        value: t.JsonValue | None,
        expected: t.JsonMapping,
    ) -> None:
        """Verify that json as mapping coerces to mapping or empty."""
        tm.that(u.Cli.json_as_mapping(value), eq=expected)

    @staticmethod
    @pytest.mark.parametrize(
        ("value", "expected"),
        [(None, []), ([1, 2, 3], [1, 2, 3]), ({"a": 1}, [])],
    )
    def test_json_as_sequence_coerces_to_list_or_empty(
        value: t.JsonValue | None,
        expected: t.SequenceOf[t.JsonValue],
    ) -> None:
        """Verify that json as sequence coerces to list or empty."""
        tm.that(list(u.Cli.json_as_sequence(value)), eq=expected)

    @staticmethod
    @pytest.mark.parametrize(
        ("value", "expected_len"),
        [([{"a": 1}, {"b": 2}], 2), (None, 0), ("string", 0)],
    )
    def test_json_as_mapping_list_filters_to_mappings(
        value: t.JsonValue | None,
        expected_len: int,
    ) -> None:
        """Verify that json as mapping list filters to mappings."""
        tm.that(len(u.Cli.json_as_mapping_list(value)), eq=expected_len)

    # ----- json_walk_path --------------------------------------------------

    @staticmethod
    def test_json_walk_path_returns_leaf_for_existing_path() -> None:
        """Verify that json walk path returns leaf for existing path."""
        data = u.Cli.json_as_mapping(u.Cli.json_loads('{"a": {"b": {"c": 42}}}').value)
        tm.that(u.Cli.json_walk_path(data, ("a", "b", "c")), eq=42)

    @staticmethod
    @pytest.mark.parametrize(
        ("keys", "raw"),
        [
            (("a", "missing", "c"), '{"a": {}}'),
            (("a", "b"), '{"a": 1}'),
            (("a", "b"), '{"a": {"b": null}}'),
            ((), '{"a": 1}'),
        ],
    )
    def test_json_walk_path_returns_none_when_unreachable(
        keys: t.VariadicTuple[str],
        raw: str,
    ) -> None:
        """Verify that json walk path returns none when unreachable."""
        data = u.Cli.json_as_mapping(u.Cli.json_loads(raw).value)
        tm.that(u.Cli.json_walk_path(data, keys), none=True)

    # ----- deep mapping helpers --------------------------------------------

    @staticmethod
    def test_json_deep_mapping_descends_into_nested_object() -> None:
        """Verify that json deep mapping descends into nested object."""
        data = u.Cli.json_as_mapping(
            u.Cli.json_loads('{"outer": {"inner": {"x": 1}}}').value,
        )
        tm.that(u.Cli.json_deep_mapping(data, "outer", "inner"), eq={"x": 1})

    @staticmethod
    def test_json_deep_mapping_without_keys_returns_same_mapping() -> None:
        """Verify that json deep mapping without keys returns same mapping."""
        tm.that(u.Cli.json_deep_mapping({"a": 1}), eq={"a": 1})

    @staticmethod
    def test_json_deep_mapping_list_returns_nested_list() -> None:
        """Verify that json deep mapping list returns nested list."""
        data = u.Cli.json_as_mapping(
            u.Cli.json_loads('{"items": [{"a": 1}, {"b": 2}]}').value,
        )
        tm.that(len(u.Cli.json_deep_mapping_list(data, "items")), eq=2)

    # ----- typed pickers ---------------------------------------------------

    @staticmethod
    def test_json_pick_str_trims_and_falls_back() -> None:
        """Verify that json pick str trims and falls back."""
        tm.that(u.Cli.json_pick_str({"k": " val "}, "k"), eq="val")
        tm.that(u.Cli.json_pick_str({}, "k", default="default"), eq="default")
        tm.that(u.Cli.json_pick_str({"k": None}, "k", default="fb"), eq="fb")

    @staticmethod
    @pytest.mark.parametrize(
        ("key", "expected"),
        [("n", 5), ("s", 7), ("f", 3), ("b", 1), ("none", 0), ("bad", 0)],
    )
    def test_json_pick_int_coerces_scalar_variants(
        key: str,
        expected: int,
    ) -> None:
        """Verify that json pick int coerces scalar variants."""
        data = u.Cli.json_as_mapping(
            u.Cli.json_loads(
                '{"n": 5, "s": "7", "f": 3.9, "b": true, "none": null, "bad": []}',
            ).value,
        )
        tm.that(u.Cli.json_pick_int(data, key), eq=expected)

    @staticmethod
    @pytest.mark.parametrize(
        ("key", "expected"),
        [
            ("t", True),
            ("f", False),
            ("s_true", True),
            ("s_false", False),
            ("s_yes", True),
            ("s_no", False),
            ("s_1", True),
            ("s_0", False),
            ("s_on", True),
            ("s_off", False),
            ("n", True),
            ("n0", False),
        ],
    )
    def test_json_pick_bool_coerces_truthy_variants(
        key: str,
        *,
        expected: bool,
    ) -> None:
        """Verify that json pick bool coerces truthy variants."""
        source: t.JsonDict = {
            "t": True,
            "f": False,
            "s_true": c.ParserBooleanToken.TRUE,
            "s_false": c.ParserBooleanToken.FALSE,
            "s_yes": c.ParserBooleanToken.YES,
            "s_no": c.ParserBooleanToken.NO,
            "s_1": c.ParserBooleanToken.ONE,
            "s_0": c.ParserBooleanToken.ZERO,
            "s_on": c.ParserBooleanToken.ON,
            "s_off": c.ParserBooleanToken.OFF,
            "n": 1,
            "n0": 0,
            "missing": None,
        }
        data = u.Cli.json_as_mapping(
            u.Cli.json_loads(u.Cli.json_dumps(source).value).value,
        )
        tm.ok(u.Cli.json_pick_bool(data, key) is expected)

    @staticmethod
    def test_json_pick_bool_uses_default_for_missing_key() -> None:
        """Verify that json pick bool uses default for missing key."""
        data = u.Cli.json_as_mapping(u.Cli.json_loads('{"missing": null}').value)
        tm.ok(u.Cli.json_pick_bool(data, "missing", default=True))

    @staticmethod
    def test_json_nested_int_reads_nested_value_or_default() -> None:
        """Verify that json nested int reads nested value or default."""
        data = u.Cli.json_as_mapping(u.Cli.json_loads('{"a": {"b": 42}}').value)
        tm.that(u.Cli.json_nested_int(data, "a", "b"), eq=42)
        tm.that(u.Cli.json_nested_int(data, "a", "missing", default=99), eq=99)

    @staticmethod
    def test_json_get_str_key_trims_value() -> None:
        """Verify that json get str key trims value."""
        tm.that(u.Cli.json_get_str_key({"name": "  Hello  "}, "name"), eq="Hello")

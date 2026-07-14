"""Behavioral tests for the public FlextCli JSON utility contract (``u.Cli.json_*``)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests import m
from tests import t
from tests import u
from flext_tests import tm

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliJsonCov:
    """Assert the observable contract of the ``u.Cli`` JSON helpers."""

    # ----- normalize -------------------------------------------------------

    def test_normalize_json_value_preserves_mapping(self) -> None:
        tm.that(u.Cli.normalize_json_value({"key": "value"}), eq={"key": "value"})

    # ----- json_read (fallible, r[JsonMapping]) ----------------------------

    def test_json_read_missing_file_fails_loudly(self, tmp_path: Path) -> None:
        result = u.Cli.json_read(tmp_path / "missing.json")
        tm.fail(result)
        tm.that(result.error, has="file not found")

    def test_json_read_valid_object_returns_parsed_mapping(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "data.json"
        path.write_text('{"key": "value"}', encoding="utf-8")
        result = u.Cli.json_read(path)
        tm.ok(result)
        tm.that(result.value, eq={"key": "value"})

    @pytest.mark.parametrize(
        ("content", "reason"),
        [("not json!!", "malformed json"), ("[1, 2, 3]", "non-object root")],
    )
    def test_json_read_rejects_invalid_content(
        self, tmp_path: Path, content: str, reason: str
    ) -> None:
        path = tmp_path / "bad.json"
        path.write_text(content, encoding="utf-8")
        result = u.Cli.json_read(path)
        tm.fail(result)
        tm.that(result.error, none=False)
        tm.that(result.error, has="json_read")

    # ----- json_write roundtrip / options ----------------------------------

    def test_json_write_then_read_roundtrips_payload(self, tmp_path: Path) -> None:
        path = tmp_path / "out.json"
        write_result = u.Cli.json_write(path, {"a": 1, "b": [1, 2]})
        tm.ok(write_result)
        read_result = u.Cli.json_read(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq={"a": 1, "b": [1, 2]})

    def test_json_write_sort_keys_orders_nested_keys(self, tmp_path: Path) -> None:
        path = tmp_path / "sorted.json"
        payload: t.JsonPayload = {
            "z": t.Cli.JSON_MAPPING_ADAPTER.validate_python({"b": 2, "a": 1}),
            "a": t.Cli.JSON_LIST_ADAPTER.validate_python([{"y": 1, "x": 0}]),
        }
        result = u.Cli.json_write(
            path, payload, options=m.Cli.JsonWriteOptions(sort_keys=True)
        )
        tm.ok(result)
        data_result = u.Cli.json_loads(path.read_text())
        tm.ok(data_result)
        data = u.Cli.json_as_mapping(data_result.value)
        sorted_mapping = t.Cli.JSON_MAPPING_ADAPTER.validate_python(data["z"])
        first_item = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
            t.Cli.JSON_LIST_ADAPTER.validate_python(data["a"])[0]
        )
        tm.that(list(data.keys()), eq=["a", "z"])
        tm.that(list(sorted_mapping.keys()), eq=["a", "b"])
        tm.that(list(first_item.keys()), eq=["x", "y"])

    def test_json_write_serializes_pydantic_model_as_object(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "model.json"
        result = u.Cli.json_write(path, m.Cli.TableConfig())
        tm.ok(result)
        data_result = u.Cli.json_loads(path.read_text())
        tm.ok(data_result)
        tm.that(data_result.value, is_=dict)

    # ----- json_parse (fallible) -------------------------------------------

    def test_json_parse_valid_text_succeeds(self) -> None:
        result = u.Cli.json_parse('{"x": 1}')
        tm.ok(result)

    def test_json_parse_invalid_text_fails(self) -> None:
        result = u.Cli.json_parse("not json")
        tm.fail(result)
        tm.that(result.error, none=False)

    # ----- coercion helpers: mapping / sequence ----------------------------

    @pytest.mark.parametrize(
        ("value", "expected"), [(None, {}), ({"a": 1}, {"a": 1}), ([1, 2, 3], {})]
    )
    def test_json_as_mapping_coerces_to_mapping_or_empty(
        self, value: t.JsonValue | None, expected: t.JsonMapping
    ) -> None:
        tm.that(u.Cli.json_as_mapping(value), eq=expected)

    @pytest.mark.parametrize(
        ("value", "expected"), [(None, []), ([1, 2, 3], [1, 2, 3]), ({"a": 1}, [])]
    )
    def test_json_as_sequence_coerces_to_list_or_empty(
        self, value: t.JsonValue | None, expected: list[t.JsonValue]
    ) -> None:
        tm.that(list(u.Cli.json_as_sequence(value)), eq=expected)

    @pytest.mark.parametrize(
        ("value", "expected_len"), [([{"a": 1}, {"b": 2}], 2), (None, 0), ("string", 0)]
    )
    def test_json_as_mapping_list_filters_to_mappings(
        self, value: t.JsonValue | None, expected_len: int
    ) -> None:
        tm.that(len(u.Cli.json_as_mapping_list(value)), eq=expected_len)

    # ----- json_walk_path --------------------------------------------------

    def test_json_walk_path_returns_leaf_for_existing_path(self) -> None:
        data = u.Cli.json_as_mapping(u.Cli.json_loads('{"a": {"b": {"c": 42}}}').value)
        tm.that(u.Cli.json_walk_path(data, ("a", "b", "c")), eq=42)

    @pytest.mark.parametrize(
        ("keys", "raw"), [(("a", "missing", "c"), '{"a": {}}'), ((), '{"a": 1}')]
    )
    def test_json_walk_path_returns_none_when_unreachable(
        self, keys: tuple[str, ...], raw: str
    ) -> None:
        data = u.Cli.json_as_mapping(u.Cli.json_loads(raw).value)
        tm.that(u.Cli.json_walk_path(data, keys), none=True)

    # ----- deep mapping helpers --------------------------------------------

    def test_json_deep_mapping_descends_into_nested_object(self) -> None:
        data = u.Cli.json_as_mapping(
            u.Cli.json_loads('{"outer": {"inner": {"x": 1}}}').value
        )
        tm.that(u.Cli.json_deep_mapping(data, "outer", "inner"), eq={"x": 1})

    def test_json_deep_mapping_without_keys_returns_same_mapping(self) -> None:
        tm.that(u.Cli.json_deep_mapping({"a": 1}), eq={"a": 1})

    def test_json_deep_mapping_list_returns_nested_list(self) -> None:
        data = u.Cli.json_as_mapping(
            u.Cli.json_loads('{"items": [{"a": 1}, {"b": 2}]}').value
        )
        tm.that(len(u.Cli.json_deep_mapping_list(data, "items")), eq=2)

    # ----- typed pickers ---------------------------------------------------

    def test_json_pick_str_trims_and_falls_back(self) -> None:
        tm.that(u.Cli.json_pick_str({"k": " val "}, "k"), eq="val")
        tm.that(u.Cli.json_pick_str({}, "k", default="default"), eq="default")
        tm.that(u.Cli.json_pick_str({"k": None}, "k", default="fb"), eq="fb")

    @pytest.mark.parametrize(
        ("key", "expected"),
        [("n", 5), ("s", 7), ("f", 3), ("b", 1), ("none", 0), ("bad", 0)],
    )
    def test_json_pick_int_coerces_scalar_variants(
        self, key: str, expected: int
    ) -> None:
        data = u.Cli.json_as_mapping(
            u.Cli.json_loads(
                '{"n": 5, "s": "7", "f": 3.9, "b": true, "none": null, "bad": []}'
            ).value
        )
        tm.that(u.Cli.json_pick_int(data, key), eq=expected)

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
        self, key: str, expected: bool
    ) -> None:
        data = u.Cli.json_as_mapping(
            u.Cli.json_loads(
                '{"t": true, "f": false, "s_true": "true", "s_false": "false",'
                ' "s_yes": "yes", "s_no": "no", "s_1": "1", "s_0": "0",'
                ' "s_on": "on", "s_off": "off", "n": 1, "n0": 0, "missing": null}'
            ).value
        )
        assert u.Cli.json_pick_bool(data, key) is expected

    def test_json_pick_bool_uses_default_for_missing_key(self) -> None:
        data = u.Cli.json_as_mapping(u.Cli.json_loads('{"missing": null}').value)
        tm.that(u.Cli.json_pick_bool(data, "missing", default=True), eq=True)

    def test_json_nested_int_reads_nested_value_or_default(self) -> None:
        data = u.Cli.json_as_mapping(u.Cli.json_loads('{"a": {"b": 42}}').value)
        tm.that(u.Cli.json_nested_int(data, "a", "b"), eq=42)
        tm.that(u.Cli.json_nested_int(data, "a", "missing", default=99), eq=99)

    def test_json_get_str_key_trims_value(self) -> None:
        tm.that(u.Cli.json_get_str_key({"name": "  Hello  "}, "name"), eq="Hello")


__all__: list[str] = ["TestsFlextCliJsonCov"]

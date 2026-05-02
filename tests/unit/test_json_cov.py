"""Coverage tests for FlextCliUtilitiesJson."""

from __future__ import annotations

import json
from pathlib import Path

from flext_cli import m
from flext_cli._utilities.json import FlextCliUtilitiesJson


class TestsFlextCliJsonCov:
    """Coverage tests for JSON utility methods."""

    def test_normalize_json_value(self) -> None:
        result = FlextCliUtilitiesJson.normalize_json_value({"key": "value"})
        assert result == {"key": "value"}

    def test_json_read_missing_file(self, tmp_path: Path) -> None:
        result = FlextCliUtilitiesJson.json_read(tmp_path / "missing.json")
        assert result.success
        assert result.value == {}

    def test_json_read_valid_file(self, tmp_path: Path) -> None:
        path = tmp_path / "data.json"
        path.write_text('{"key": "value"}', encoding="utf-8")
        result = FlextCliUtilitiesJson.json_read(path)
        assert result.success
        assert result.value == {"key": "value"}

    def test_json_read_invalid_json(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("not json!!", encoding="utf-8")
        result = FlextCliUtilitiesJson.json_read(path)
        assert result.failure

    def test_json_read_non_object_root(self, tmp_path: Path) -> None:
        path = tmp_path / "arr.json"
        path.write_text("[1, 2, 3]", encoding="utf-8")
        result = FlextCliUtilitiesJson.json_read(path)
        assert result.failure

    def test_json_write_and_read_roundtrip(self, tmp_path: Path) -> None:
        path = tmp_path / "out.json"
        result = FlextCliUtilitiesJson.json_write(path, {"a": 1, "b": [1, 2]})
        assert result.success
        read_result = FlextCliUtilitiesJson.json_read(path)
        assert read_result.success
        assert read_result.value == {"a": 1, "b": [1, 2]}

    def test_json_write_with_sort_keys(self, tmp_path: Path) -> None:
        path = tmp_path / "sorted.json"
        opts = m.Cli.JsonWriteOptions(sort_keys=True)
        result = FlextCliUtilitiesJson.json_write(path, {"z": 1, "a": 2}, options=opts)
        assert result.success
        raw = path.read_text()
        data = json.loads(raw)
        assert list(data.keys()) == ["a", "z"]

    def test_json_parse_valid(self) -> None:
        result = FlextCliUtilitiesJson.json_parse('{"x": 1}')
        assert result.success

    def test_json_parse_invalid(self) -> None:
        result = FlextCliUtilitiesJson.json_parse("not json")
        assert result.failure

    def test_json_as_mapping_none(self) -> None:
        result = FlextCliUtilitiesJson.json_as_mapping(None)
        assert result == {}

    def test_json_as_mapping_valid(self) -> None:
        result = FlextCliUtilitiesJson.json_as_mapping({"a": 1})
        assert result == {"a": 1}

    def test_json_as_mapping_non_mapping(self) -> None:
        result = FlextCliUtilitiesJson.json_as_mapping([1, 2, 3])
        assert result == {}

    def test_json_as_sequence_none(self) -> None:
        result = FlextCliUtilitiesJson.json_as_sequence(None)
        assert result == []

    def test_json_as_sequence_valid(self) -> None:
        result = FlextCliUtilitiesJson.json_as_sequence([1, 2, 3])
        assert list(result) == [1, 2, 3]

    def test_json_as_sequence_non_sequence(self) -> None:
        result = FlextCliUtilitiesJson.json_as_sequence({"a": 1})
        assert result == []

    def test_json_as_mapping_list_valid(self) -> None:
        result = FlextCliUtilitiesJson.json_as_mapping_list([{"a": 1}, {"b": 2}])
        assert len(result) == 2

    def test_json_as_mapping_list_none(self) -> None:
        result = FlextCliUtilitiesJson.json_as_mapping_list(None)
        assert result == []

    def test_json_as_mapping_list_non_list(self) -> None:
        result = FlextCliUtilitiesJson.json_as_mapping_list("string")
        assert result == []

    def test_json_walk_path_existing(self) -> None:
        raw = json.loads('{"a": {"b": {"c": 42}}}')
        data = FlextCliUtilitiesJson.json_as_mapping(raw)
        result = FlextCliUtilitiesJson.json_walk_path(data, ("a", "b", "c"))
        assert result == 42

    def test_json_walk_path_missing_intermediate(self) -> None:
        raw = json.loads('{"a": {}}')
        data = FlextCliUtilitiesJson.json_as_mapping(raw)
        result = FlextCliUtilitiesJson.json_walk_path(data, ("a", "missing", "c"))
        assert result is None

    def test_json_walk_path_empty_keys(self) -> None:
        data = {"a": 1}
        result = FlextCliUtilitiesJson.json_walk_path(data, ())
        assert result is None

    def test_json_deep_mapping_valid(self) -> None:
        raw = json.loads('{"outer": {"inner": {"x": 1}}}')
        data = FlextCliUtilitiesJson.json_as_mapping(raw)
        result = FlextCliUtilitiesJson.json_deep_mapping(data, "outer", "inner")
        assert result == {"x": 1}

    def test_json_deep_mapping_no_keys(self) -> None:
        data = {"a": 1}
        result = FlextCliUtilitiesJson.json_deep_mapping(data)
        assert result == {"a": 1}

    def test_json_deep_mapping_list(self) -> None:
        raw = json.loads('{"items": [{"a": 1}, {"b": 2}]}')
        data = FlextCliUtilitiesJson.json_as_mapping(raw)
        result = FlextCliUtilitiesJson.json_deep_mapping_list(data, "items")
        assert len(result) == 2

    def test_json_pick_str(self) -> None:
        assert FlextCliUtilitiesJson.json_pick_str({"k": " val "}, "k") == "val"
        assert (
            FlextCliUtilitiesJson.json_pick_str({}, "k", default="default") == "default"
        )

    def test_json_pick_str_none_value(self) -> None:
        assert (
            FlextCliUtilitiesJson.json_pick_str({"k": None}, "k", default="fb") == "fb"
        )

    def test_json_pick_int_variants(self) -> None:
        raw = json.loads(
            '{"n": 5, "s": "7", "f": 3.9, "b": true, "none": null, "bad": []}'
        )
        data = FlextCliUtilitiesJson.json_as_mapping(raw)
        assert FlextCliUtilitiesJson.json_pick_int(data, "n") == 5
        assert FlextCliUtilitiesJson.json_pick_int(data, "s") == 7
        assert FlextCliUtilitiesJson.json_pick_int(data, "f") == 3
        assert FlextCliUtilitiesJson.json_pick_int(data, "b") == 1
        assert FlextCliUtilitiesJson.json_pick_int(data, "none") == 0
        assert FlextCliUtilitiesJson.json_pick_int(data, "bad") == 0

    def test_json_pick_bool_variants(self) -> None:
        raw = json.loads(
            '{"t": true, "f": false, "s_true": "true", "s_false": "false",'
            ' "s_yes": "yes", "s_no": "no", "s_1": "1", "s_0": "0",'
            ' "s_on": "on", "s_off": "off", "n": 1, "n0": 0, "missing": null}'
        )
        data = FlextCliUtilitiesJson.json_as_mapping(raw)
        assert FlextCliUtilitiesJson.json_pick_bool(data, "t") is True
        assert FlextCliUtilitiesJson.json_pick_bool(data, "f") is False
        assert FlextCliUtilitiesJson.json_pick_bool(data, "s_true") is True
        assert FlextCliUtilitiesJson.json_pick_bool(data, "s_false") is False
        assert FlextCliUtilitiesJson.json_pick_bool(data, "s_yes") is True
        assert FlextCliUtilitiesJson.json_pick_bool(data, "s_no") is False
        assert FlextCliUtilitiesJson.json_pick_bool(data, "s_1") is True
        assert FlextCliUtilitiesJson.json_pick_bool(data, "s_0") is False
        assert FlextCliUtilitiesJson.json_pick_bool(data, "s_on") is True
        assert FlextCliUtilitiesJson.json_pick_bool(data, "s_off") is False
        assert FlextCliUtilitiesJson.json_pick_bool(data, "n") is True
        assert FlextCliUtilitiesJson.json_pick_bool(data, "n0") is False
        assert (
            FlextCliUtilitiesJson.json_pick_bool(data, "missing", default=True) is True
        )

    def test_json_nested_int(self) -> None:
        raw = json.loads('{"a": {"b": 42}}')
        data = FlextCliUtilitiesJson.json_as_mapping(raw)
        assert FlextCliUtilitiesJson.json_nested_int(data, "a", "b") == 42
        assert (
            FlextCliUtilitiesJson.json_nested_int(data, "a", "missing", default=99)
            == 99
        )

    def test_json_get_str_key(self) -> None:
        data = {"name": "  Hello  "}
        assert FlextCliUtilitiesJson.json_get_str_key(data, "name") == "Hello"

    def test_json_sort_keys_recursive(self) -> None:
        sorted_data = FlextCliUtilitiesJson._json_sort_keys(
            dict(json.loads('{"z": {"b": 2, "a": 1}, "a": [{"y": 1, "x": 0}]}'))
        )
        assert isinstance(sorted_data, dict)
        assert list(sorted_data.keys()) == ["a", "z"]

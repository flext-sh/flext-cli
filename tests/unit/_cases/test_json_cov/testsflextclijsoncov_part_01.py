"""Coverage tests for FlextCliUtilitiesJson."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests import m
from tests import p, t
from tests import u
from flext_tests import tm

from pathlib import Path



class TestsFlextCliJsonCov:
    """Implementation part for TestsFlextCliJsonCov."""

    def test_json_normalize_value(self) -> None:
        result = u.Cli.json_normalize_value({"key": "value"})
        tm.that(result, eq={"key": "value"})

    def test_json_read_missing_file(self, tmp_path: Path) -> None:
        result = u.Cli.json_read(tmp_path / "missing.json")
        tm.ok(result)
        tm.that(result.value, eq={})

    def test_json_read_valid_file(self, tmp_path: Path) -> None:
        path = tmp_path / "data.json"
        path.write_text('{"key": "value"}', encoding="utf-8")
        result = u.Cli.json_read(path)
        tm.ok(result)
        tm.that(result.value, eq={"key": "value"})

    def test_json_read_invalid_json(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("not json!!", encoding="utf-8")
        result = u.Cli.json_read(path)
        tm.fail(result)

    def test_json_read_non_object_root(self, tmp_path: Path) -> None:
        path = tmp_path / "arr.json"
        path.write_text("[1, 2, 3]", encoding="utf-8")
        result = u.Cli.json_read(path)
        tm.fail(result)

    def test_json_write_and_read_roundtrip(self, tmp_path: Path) -> None:
        path = tmp_path / "out.json"
        result = u.Cli.json_write(path, {"a": 1, "b": [1, 2]})
        tm.ok(result)
        read_result = u.Cli.json_read(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq={"a": 1, "b": [1, 2]})

    def test_json_write_with_sort_keys(self, tmp_path: Path) -> None:
        path = tmp_path / "sorted.json"
        opts = m.Cli.JsonWriteOptions(sort_keys=True)
        payload: t.JsonPayload = {
            "z": t.Cli.JSON_MAPPING_ADAPTER.validate_python({"b": 2, "a": 1}),
            "a": t.Cli.JSON_LIST_ADAPTER.validate_python([{"y": 1, "x": 0}]),
        }
        result = u.Cli.json_write(path, payload, options=opts)
        tm.ok(result)
        raw = path.read_text()
        data_result = u.Cli.json_loads(raw)
        tm.ok(data_result)
        data = u.Cli.json_as_mapping(data_result.value)
        sorted_mapping = t.Cli.JSON_MAPPING_ADAPTER.validate_python(data["z"])
        sorted_items = t.Cli.JSON_LIST_ADAPTER.validate_python(data["a"])
        first_item = t.Cli.JSON_MAPPING_ADAPTER.validate_python(sorted_items[0])
        tm.that(list(data.keys()), eq=["a", "z"])
        tm.that(list(sorted_mapping.keys()), eq=["a", "b"])
        tm.that(list(first_item.keys()), eq=["x", "y"])

    def test_json_write_pydantic_model(self, tmp_path: Path) -> None:
        path = tmp_path / "model.json"
        result = u.Cli.json_write(path, m.Cli.TableConfig())
        tm.ok(result)
        data_result = u.Cli.json_loads(path.read_text())
        tm.ok(data_result)
        data = data_result.value
        tm.that(data, is_=dict)

    def test_json_parse_valid(self) -> None:
        result = u.Cli.json_parse('{"x": 1}')
        tm.ok(result)

    def test_json_parse_invalid(self) -> None:
        result = u.Cli.json_parse("not json")
        tm.fail(result)

    def test_json_as_mapping_none(self) -> None:
        result = u.Cli.json_as_mapping(None)
        tm.that(result, eq={})

    def test_json_as_mapping_valid(self) -> None:
        result = u.Cli.json_as_mapping({"a": 1})
        tm.that(result, eq={"a": 1})

    def test_json_as_mapping_non_mapping(self) -> None:
        result = u.Cli.json_as_mapping([1, 2, 3])
        tm.that(result, eq={})

    def test_json_as_sequence_none(self) -> None:
        result = u.Cli.json_as_sequence(None)
        tm.that(result, eq=[])

    def test_json_as_sequence_valid(self) -> None:
        result = u.Cli.json_as_sequence([1, 2, 3])
        tm.that(list(result), eq=[1, 2, 3])

    def test_json_as_sequence_non_sequence(self) -> None:
        result = u.Cli.json_as_sequence({"a": 1})
        tm.that(result, eq=[])

    def test_json_as_mapping_list_valid(self) -> None:
        result = u.Cli.json_as_mapping_list([{"a": 1}, {"b": 2}])
        tm.that(len(result), eq=2)

    def test_json_as_mapping_list_none(self) -> None:
        result = u.Cli.json_as_mapping_list(None)
        tm.that(result, eq=[])

    def test_json_as_mapping_list_non_list(self) -> None:
        result = u.Cli.json_as_mapping_list("string")
        tm.that(result, eq=[])

    def test_json_walk_path_existing(self) -> None:
        raw_result = u.Cli.json_loads('{"a": {"b": {"c": 42}}}')
        tm.ok(raw_result)
        data = u.Cli.json_as_mapping(raw_result.value)
        result = u.Cli.json_walk_path(data, ("a", "b", "c"))
        tm.that(result, eq=42)

    def test_json_walk_path_missing_intermediate(self) -> None:
        raw_result = u.Cli.json_loads('{"a": {}}')
        tm.ok(raw_result)
        data = u.Cli.json_as_mapping(raw_result.value)
        result = u.Cli.json_walk_path(data, ("a", "missing", "c"))
        tm.that(result, none=True)

    def test_json_walk_path_empty_keys(self) -> None:
        data = {"a": 1}
        result = u.Cli.json_walk_path(data, ())
        tm.that(result, none=True)


__all__: list[str] = ["TestsFlextCliJsonCov"]

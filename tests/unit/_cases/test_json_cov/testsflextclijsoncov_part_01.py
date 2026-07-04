"""Coverage tests for FlextCliUtilitiesJson."""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.models import m
from tests.typings import t
from tests.utilities import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliJsonCov:
    """Implementation part for TestsFlextCliJsonCov."""

    def test_normalize_json_value(self) -> None:
        result = u.Cli.normalize_json_value({"key": "value"})
        assert result == {"key": "value"}

    def test_json_read_missing_file(self, tmp_path: Path) -> None:
        result = u.Cli.json_read(tmp_path / "missing.json")
        assert result.success
        assert result.value == {}

    def test_json_read_valid_file(self, tmp_path: Path) -> None:
        path = tmp_path / "data.json"
        path.write_text('{"key": "value"}', encoding="utf-8")
        result = u.Cli.json_read(path)
        assert result.success
        assert result.value == {"key": "value"}

    def test_json_read_invalid_json(self, tmp_path: Path) -> None:
        path = tmp_path / "bad.json"
        path.write_text("not json!!", encoding="utf-8")
        result = u.Cli.json_read(path)
        assert result.failure

    def test_json_read_non_object_root(self, tmp_path: Path) -> None:
        path = tmp_path / "arr.json"
        path.write_text("[1, 2, 3]", encoding="utf-8")
        result = u.Cli.json_read(path)
        assert result.failure

    def test_json_write_and_read_roundtrip(self, tmp_path: Path) -> None:
        path = tmp_path / "out.json"
        result = u.Cli.json_write(path, {"a": 1, "b": [1, 2]})
        assert result.success
        read_result = u.Cli.json_read(path)
        assert read_result.success
        assert read_result.value == {"a": 1, "b": [1, 2]}

    def test_json_write_with_sort_keys(self, tmp_path: Path) -> None:
        path = tmp_path / "sorted.json"
        opts = m.Cli.JsonWriteOptions(sort_keys=True)
        payload: t.JsonPayload = {
            "z": t.Cli.JSON_MAPPING_ADAPTER.validate_python({"b": 2, "a": 1}),
            "a": t.Cli.JSON_LIST_ADAPTER.validate_python([{"y": 1, "x": 0}]),
        }
        result = u.Cli.json_write(
            path,
            payload,
            options=opts,
        )
        assert result.success
        raw = path.read_text()
        data_result = u.Cli.json_loads(raw)
        assert data_result.success
        data = u.Cli.json_as_mapping(data_result.value)
        sorted_mapping = t.Cli.JSON_MAPPING_ADAPTER.validate_python(data["z"])
        sorted_items = t.Cli.JSON_LIST_ADAPTER.validate_python(data["a"])
        first_item = t.Cli.JSON_MAPPING_ADAPTER.validate_python(sorted_items[0])
        assert list(data.keys()) == ["a", "z"]
        assert list(sorted_mapping.keys()) == ["a", "b"]
        assert list(first_item.keys()) == ["x", "y"]

    def test_json_write_pydantic_model(self, tmp_path: Path) -> None:
        path = tmp_path / "model.json"
        result = u.Cli.json_write(path, m.Cli.TableConfig())
        assert result.success
        data_result = u.Cli.json_loads(path.read_text())
        assert data_result.success
        data = data_result.value
        assert isinstance(data, dict)

    def test_json_parse_valid(self) -> None:
        result = u.Cli.json_parse('{"x": 1}')
        assert result.success

    def test_json_parse_invalid(self) -> None:
        result = u.Cli.json_parse("not json")
        assert result.failure

    def test_json_as_mapping_none(self) -> None:
        result = u.Cli.json_as_mapping(None)
        assert result == {}

    def test_json_as_mapping_valid(self) -> None:
        result = u.Cli.json_as_mapping({"a": 1})
        assert result == {"a": 1}

    def test_json_as_mapping_non_mapping(self) -> None:
        result = u.Cli.json_as_mapping([1, 2, 3])
        assert result == {}

    def test_json_as_sequence_none(self) -> None:
        result = u.Cli.json_as_sequence(None)
        assert result == []

    def test_json_as_sequence_valid(self) -> None:
        result = u.Cli.json_as_sequence([1, 2, 3])
        assert list(result) == [1, 2, 3]

    def test_json_as_sequence_non_sequence(self) -> None:
        result = u.Cli.json_as_sequence({"a": 1})
        assert result == []

    def test_json_as_mapping_list_valid(self) -> None:
        result = u.Cli.json_as_mapping_list([{"a": 1}, {"b": 2}])
        assert len(result) == 2

    def test_json_as_mapping_list_none(self) -> None:
        result = u.Cli.json_as_mapping_list(None)
        assert result == []

    def test_json_as_mapping_list_non_list(self) -> None:
        result = u.Cli.json_as_mapping_list("string")
        assert result == []

    def test_json_walk_path_existing(self) -> None:
        raw_result = u.Cli.json_loads('{"a": {"b": {"c": 42}}}')
        assert raw_result.success
        data = u.Cli.json_as_mapping(raw_result.value)
        result = u.Cli.json_walk_path(data, ("a", "b", "c"))
        assert result == 42

    def test_json_walk_path_missing_intermediate(self) -> None:
        raw_result = u.Cli.json_loads('{"a": {}}')
        assert raw_result.success
        data = u.Cli.json_as_mapping(raw_result.value)
        result = u.Cli.json_walk_path(data, ("a", "missing", "c"))
        assert result is None

    def test_json_walk_path_empty_keys(self) -> None:
        data = {"a": 1}
        result = u.Cli.json_walk_path(data, ())
        assert result is None


__all__: list[str] = ["TestsFlextCliJsonCov"]

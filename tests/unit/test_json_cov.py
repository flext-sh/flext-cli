"""Behavioral tests for the public FlextCli JSON utility contract (``u.Cli.json_*``)."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.models import m
from tests.typings import t
from tests.utilities import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliJsonCov:
    """Assert the observable contract of the ``u.Cli`` JSON helpers."""

    # ----- normalize -------------------------------------------------------

    def test_normalize_json_value_preserves_mapping(self) -> None:
        assert u.Cli.normalize_json_value({"key": "value"}) == {"key": "value"}

    # ----- json_read (fallible, r[JsonMapping]) ----------------------------

    def test_json_read_missing_file_succeeds_with_empty_mapping(
        self, tmp_path: Path
    ) -> None:
        result = u.Cli.json_read(tmp_path / "missing.json")
        assert result.success
        assert result.value == {}

    def test_json_read_valid_object_returns_parsed_mapping(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "data.json"
        path.write_text('{"key": "value"}', encoding="utf-8")
        result = u.Cli.json_read(path)
        assert result.success
        assert result.value == {"key": "value"}

    @pytest.mark.parametrize(
        ("content", "reason"),
        [
            ("not json!!", "malformed json"),
            ("[1, 2, 3]", "non-object root"),
        ],
    )
    def test_json_read_rejects_invalid_content(
        self, tmp_path: Path, content: str, reason: str
    ) -> None:
        path = tmp_path / "bad.json"
        path.write_text(content, encoding="utf-8")
        result = u.Cli.json_read(path)
        assert result.failure, reason
        assert result.error is not None
        assert "json_read" in result.error

    # ----- json_write roundtrip / options ----------------------------------

    def test_json_write_then_read_roundtrips_payload(self, tmp_path: Path) -> None:
        path = tmp_path / "out.json"
        write_result = u.Cli.json_write(path, {"a": 1, "b": [1, 2]})
        assert write_result.success
        read_result = u.Cli.json_read(path)
        assert read_result.success
        assert read_result.value == {"a": 1, "b": [1, 2]}

    def test_json_write_sort_keys_orders_nested_keys(self, tmp_path: Path) -> None:
        path = tmp_path / "sorted.json"
        payload: t.JsonPayload = {
            "z": t.Cli.JSON_MAPPING_ADAPTER.validate_python({"b": 2, "a": 1}),
            "a": t.Cli.JSON_LIST_ADAPTER.validate_python([{"y": 1, "x": 0}]),
        }
        result = u.Cli.json_write(
            path,
            payload,
            options=m.Cli.JsonWriteOptions(sort_keys=True),
        )
        assert result.success
        data_result = u.Cli.json_loads(path.read_text())
        assert data_result.success
        data = u.Cli.json_as_mapping(data_result.value)
        sorted_mapping = t.Cli.JSON_MAPPING_ADAPTER.validate_python(data["z"])
        first_item = t.Cli.JSON_MAPPING_ADAPTER.validate_python(
            t.Cli.JSON_LIST_ADAPTER.validate_python(data["a"])[0]
        )
        assert list(data.keys()) == ["a", "z"]
        assert list(sorted_mapping.keys()) == ["a", "b"]
        assert list(first_item.keys()) == ["x", "y"]

    def test_json_write_serializes_pydantic_model_as_object(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "model.json"
        result = u.Cli.json_write(path, m.Cli.TableConfig())
        assert result.success
        data_result = u.Cli.json_loads(path.read_text())
        assert data_result.success
        assert isinstance(data_result.value, dict)

    # ----- json_parse (fallible) -------------------------------------------

    def test_json_parse_valid_text_succeeds(self) -> None:
        result = u.Cli.json_parse('{"x": 1}')
        assert result.success

    def test_json_parse_invalid_text_fails(self) -> None:
        result = u.Cli.json_parse("not json")
        assert result.failure
        assert result.error is not None

    # ----- coercion helpers: mapping / sequence ----------------------------

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (None, {}),
            ({"a": 1}, {"a": 1}),
            ([1, 2, 3], {}),
        ],
    )
    def test_json_as_mapping_coerces_to_mapping_or_empty(
        self, value: t.JsonValue | None, expected: t.JsonMapping
    ) -> None:
        assert u.Cli.json_as_mapping(value) == expected

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            (None, []),
            ([1, 2, 3], [1, 2, 3]),
            ({"a": 1}, []),
        ],
    )
    def test_json_as_sequence_coerces_to_list_or_empty(
        self, value: t.JsonValue | None, expected: list[t.JsonValue]
    ) -> None:
        assert list(u.Cli.json_as_sequence(value)) == expected

    @pytest.mark.parametrize(
        ("value", "expected_len"),
        [
            ([{"a": 1}, {"b": 2}], 2),
            (None, 0),
            ("string", 0),
        ],
    )
    def test_json_as_mapping_list_filters_to_mappings(
        self, value: t.JsonValue | None, expected_len: int
    ) -> None:
        assert len(u.Cli.json_as_mapping_list(value)) == expected_len

    # ----- json_walk_path --------------------------------------------------

    def test_json_walk_path_returns_leaf_for_existing_path(self) -> None:
        data = u.Cli.json_as_mapping(
            u.Cli.json_loads('{"a": {"b": {"c": 42}}}').value
        )
        assert u.Cli.json_walk_path(data, ("a", "b", "c")) == 42

    @pytest.mark.parametrize(
        ("keys", "raw"),
        [
            (("a", "missing", "c"), '{"a": {}}'),
            ((), '{"a": 1}'),
        ],
    )
    def test_json_walk_path_returns_none_when_unreachable(
        self, keys: tuple[str, ...], raw: str
    ) -> None:
        data = u.Cli.json_as_mapping(u.Cli.json_loads(raw).value)
        assert u.Cli.json_walk_path(data, keys) is None

    # ----- deep mapping helpers --------------------------------------------

    def test_json_deep_mapping_descends_into_nested_object(self) -> None:
        data = u.Cli.json_as_mapping(
            u.Cli.json_loads('{"outer": {"inner": {"x": 1}}}').value
        )
        assert u.Cli.json_deep_mapping(data, "outer", "inner") == {"x": 1}

    def test_json_deep_mapping_without_keys_returns_same_mapping(self) -> None:
        assert u.Cli.json_deep_mapping({"a": 1}) == {"a": 1}

    def test_json_deep_mapping_list_returns_nested_list(self) -> None:
        data = u.Cli.json_as_mapping(
            u.Cli.json_loads('{"items": [{"a": 1}, {"b": 2}]}').value
        )
        assert len(u.Cli.json_deep_mapping_list(data, "items")) == 2

    # ----- typed pickers ---------------------------------------------------

    def test_json_pick_str_trims_and_falls_back(self) -> None:
        assert u.Cli.json_pick_str({"k": " val "}, "k") == "val"
        assert u.Cli.json_pick_str({}, "k", default="default") == "default"
        assert u.Cli.json_pick_str({"k": None}, "k", default="fb") == "fb"

    @pytest.mark.parametrize(
        ("key", "expected"),
        [
            ("n", 5),
            ("s", 7),
            ("f", 3),
            ("b", 1),
            ("none", 0),
            ("bad", 0),
        ],
    )
    def test_json_pick_int_coerces_scalar_variants(
        self, key: str, expected: int
    ) -> None:
        data = u.Cli.json_as_mapping(
            u.Cli.json_loads(
                '{"n": 5, "s": "7", "f": 3.9, "b": true, "none": null, "bad": []}',
            ).value
        )
        assert u.Cli.json_pick_int(data, key) == expected

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
                ' "s_on": "on", "s_off": "off", "n": 1, "n0": 0, "missing": null}',
            ).value
        )
        assert u.Cli.json_pick_bool(data, key) is expected

    def test_json_pick_bool_uses_default_for_missing_key(self) -> None:
        data = u.Cli.json_as_mapping(u.Cli.json_loads('{"missing": null}').value)
        assert u.Cli.json_pick_bool(data, "missing", default=True) is True

    def test_json_nested_int_reads_nested_value_or_default(self) -> None:
        data = u.Cli.json_as_mapping(u.Cli.json_loads('{"a": {"b": 42}}').value)
        assert u.Cli.json_nested_int(data, "a", "b") == 42
        assert u.Cli.json_nested_int(data, "a", "missing", default=99) == 99

    def test_json_get_str_key_trims_value(self) -> None:
        assert u.Cli.json_get_str_key({"name": "  Hello  "}, "name") == "Hello"


__all__: list[str] = ["TestsFlextCliJsonCov"]

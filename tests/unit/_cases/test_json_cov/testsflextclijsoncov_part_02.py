"""Coverage tests for FlextCliUtilitiesJson."""

from __future__ import annotations

from tests import u


class TestsFlextCliJsonCov:
    """Implementation part for TestsFlextCliJsonCov."""

    def test_json_deep_mapping_valid(self) -> None:
        raw_result = u.Cli.json_loads('{"outer": {"inner": {"x": 1}}}')
        assert raw_result.success
        data = u.Cli.json_as_mapping(raw_result.value)
        result = u.Cli.json_deep_mapping(data, "outer", "inner")
        assert result == {"x": 1}

    def test_json_deep_mapping_no_keys(self) -> None:
        data = {"a": 1}
        result = u.Cli.json_deep_mapping(data)
        assert result == {"a": 1}

    def test_json_deep_mapping_list(self) -> None:
        raw_result = u.Cli.json_loads('{"items": [{"a": 1}, {"b": 2}]}')
        assert raw_result.success
        data = u.Cli.json_as_mapping(raw_result.value)
        result = u.Cli.json_deep_mapping_list(data, "items")
        assert len(result) == 2

    def test_json_pick_str(self) -> None:
        assert u.Cli.json_pick_str({"k": " val "}, "k") == "val"
        assert u.Cli.json_pick_str({}, "k", default="default") == "default"

    def test_json_pick_str_none_value(self) -> None:
        assert u.Cli.json_pick_str({"k": None}, "k", default="fb") == "fb"

    def test_json_pick_int_variants(self) -> None:
        raw_result = u.Cli.json_loads(
            '{"n": 5, "s": "7", "f": 3.9, "b": true, "none": null, "bad": []}'
        )
        assert raw_result.success
        data = u.Cli.json_as_mapping(raw_result.value)
        assert u.Cli.json_pick_int(data, "n") == 5
        assert u.Cli.json_pick_int(data, "s") == 7
        assert u.Cli.json_pick_int(data, "f") == 3
        assert u.Cli.json_pick_int(data, "b") == 1
        assert u.Cli.json_pick_int(data, "none") == 0
        assert u.Cli.json_pick_int(data, "bad") == 0

    def test_json_pick_bool_variants(self) -> None:
        raw_result = u.Cli.json_loads(
            '{"t": true, "f": false, "s_true": "true", "s_false": "false",'
            ' "s_yes": "yes", "s_no": "no", "s_1": "1", "s_0": "0",'
            ' "s_on": "on", "s_off": "off", "n": 1, "n0": 0, "missing": null}'
        )
        assert raw_result.success
        data = u.Cli.json_as_mapping(raw_result.value)
        assert u.Cli.json_pick_bool(data, "t") is True
        assert u.Cli.json_pick_bool(data, "f") is False
        assert u.Cli.json_pick_bool(data, "s_true") is True
        assert u.Cli.json_pick_bool(data, "s_false") is False
        assert u.Cli.json_pick_bool(data, "s_yes") is True
        assert u.Cli.json_pick_bool(data, "s_no") is False
        assert u.Cli.json_pick_bool(data, "s_1") is True
        assert u.Cli.json_pick_bool(data, "s_0") is False
        assert u.Cli.json_pick_bool(data, "s_on") is True
        assert u.Cli.json_pick_bool(data, "s_off") is False
        assert u.Cli.json_pick_bool(data, "n") is True
        assert u.Cli.json_pick_bool(data, "n0") is False
        assert u.Cli.json_pick_bool(data, "missing", default=True) is True

    def test_json_nested_int(self) -> None:
        raw_result = u.Cli.json_loads('{"a": {"b": 42}}')
        assert raw_result.success
        data = u.Cli.json_as_mapping(raw_result.value)
        assert u.Cli.json_nested_int(data, "a", "b") == 42
        assert u.Cli.json_nested_int(data, "a", "missing", default=99) == 99

    def test_json_get_str_key(self) -> None:
        data = {"name": "  Hello  "}
        assert u.Cli.json_get_str_key(data, "name") == "Hello"


__all__: list[str] = ["TestsFlextCliJsonCov"]

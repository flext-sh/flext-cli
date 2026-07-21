"""Coverage tests for FlextCliUtilitiesJson."""

from __future__ import annotations

from flext_tests import tm

from tests import u


class TestsFlextCliJsonCov:
    """Implementation part for TestsFlextCliJsonCov."""

    def test_json_deep_mapping_valid(self) -> None:
        """Verify that json deep mapping valid."""
        raw_result = u.Cli.json_loads('{"outer": {"inner": {"x": 1}}}')
        tm.ok(raw_result)
        data = u.Cli.json_as_mapping(raw_result.value)
        result = u.Cli.json_deep_mapping(data, "outer", "inner")
        tm.that(result, eq={"x": 1})

    def test_json_deep_mapping_no_keys(self) -> None:
        """Verify that json deep mapping no keys."""
        data = {"a": 1}
        result = u.Cli.json_deep_mapping(data)
        tm.that(result, eq={"a": 1})

    def test_json_deep_mapping_list(self) -> None:
        """Verify that json deep mapping list."""
        raw_result = u.Cli.json_loads('{"items": [{"a": 1}, {"b": 2}]}')
        tm.ok(raw_result)
        data = u.Cli.json_as_mapping(raw_result.value)
        result = u.Cli.json_deep_mapping_list(data, "items")
        tm.that(len(result), eq=2)

    def test_json_pick_str(self) -> None:
        """Verify that json pick str."""
        tm.that(u.Cli.json_pick_str({"k": " val "}, "k"), eq="val")
        tm.that(u.Cli.json_pick_str({}, "k", default="default"), eq="default")

    def test_json_pick_str_none_value(self) -> None:
        """Verify that json pick str none value."""
        tm.that(u.Cli.json_pick_str({"k": None}, "k", default="fb"), eq="fb")

    def test_json_pick_int_variants(self) -> None:
        """Verify that json pick int variants."""
        raw_result = u.Cli.json_loads(
            '{"n": 5, "s": "7", "f": 3.9, "b": true, "none": null, "bad": []}'
        )
        tm.ok(raw_result)
        data = u.Cli.json_as_mapping(raw_result.value)
        tm.that(u.Cli.json_pick_int(data, "n"), eq=5)
        tm.that(u.Cli.json_pick_int(data, "s"), eq=7)
        tm.that(u.Cli.json_pick_int(data, "f"), eq=3)
        tm.that(u.Cli.json_pick_int(data, "b"), eq=1)
        tm.that(u.Cli.json_pick_int(data, "none"), eq=0)
        tm.that(u.Cli.json_pick_int(data, "bad"), eq=0)

    def test_json_pick_bool_variants(self) -> None:
        """Verify that json pick bool variants."""
        raw_result = u.Cli.json_loads(
            '{"t": true, "f": false, "s_true": "true", "s_false": "false",'
            ' "s_yes": "yes", "s_no": "no", "s_1": "1", "s_0": "0",'
            ' "s_on": "on", "s_off": "off", "n": 1, "n0": 0, "missing": null}'
        )
        tm.ok(raw_result)
        data = u.Cli.json_as_mapping(raw_result.value)
        tm.that(u.Cli.json_pick_bool(data, "t"), eq=True)
        tm.that(u.Cli.json_pick_bool(data, "f"), eq=False)
        tm.that(u.Cli.json_pick_bool(data, "s_true"), eq=True)
        tm.that(u.Cli.json_pick_bool(data, "s_false"), eq=False)
        tm.that(u.Cli.json_pick_bool(data, "s_yes"), eq=True)
        tm.that(u.Cli.json_pick_bool(data, "s_no"), eq=False)
        tm.that(u.Cli.json_pick_bool(data, "s_1"), eq=True)
        tm.that(u.Cli.json_pick_bool(data, "s_0"), eq=False)
        tm.that(u.Cli.json_pick_bool(data, "s_on"), eq=True)
        tm.that(u.Cli.json_pick_bool(data, "s_off"), eq=False)
        tm.that(u.Cli.json_pick_bool(data, "n"), eq=True)
        tm.that(u.Cli.json_pick_bool(data, "n0"), eq=False)
        tm.that(u.Cli.json_pick_bool(data, "missing", default=True), eq=True)

    def test_json_nested_int(self) -> None:
        """Verify that json nested int."""
        raw_result = u.Cli.json_loads('{"a": {"b": 42}}')
        tm.ok(raw_result)
        data = u.Cli.json_as_mapping(raw_result.value)
        tm.that(u.Cli.json_nested_int(data, "a", "b"), eq=42)
        tm.that(u.Cli.json_nested_int(data, "a", "missing", default=99), eq=99)

    def test_json_get_str_key(self) -> None:
        """Verify that json get str key."""
        data = {"name": "  Hello  "}
        tm.that(u.Cli.json_get_str_key(data, "name"), eq="Hello")


__all__: list[str] = ["TestsFlextCliJsonCov"]

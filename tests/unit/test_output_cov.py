from __future__ import annotations

import json
from collections.abc import Iterable

import pytest
from flext_core import r

from flext_cli.services.output import FlextCliOutput


def test_basic_helper_error_and_fallback_branches(monkeypatch) -> None:
    output = FlextCliOutput()

    monkeypatch.setattr("flext_cli.services.output.u.build", lambda *_a, **_k: 1)
    assert output.get_keys("x") == []

    class StrBoom:
        def __str__(self) -> str:
            raise RuntimeError("str boom")

    assert output.ensure_str(StrBoom(), "d") == "d"

    dict_val = output.get_map_val({"k": {"a": object()}}, "k", "d")
    assert isinstance(dict_val, dict)
    assert output.get_map_val({"k": object()}, "k", "d")

    # cast_if returns default when type doesn't match (no TypeError raised)
    assert output.cast_if("x", int, "not-int") == "not-int"

    monkeypatch.setattr(FlextCliOutput, "cast_if", staticmethod(lambda *_a, **_k: "x"))
    assert FlextCliOutput.to_dict_json({"a": 1}) == {}
    assert FlextCliOutput.to_list_json([1, 2]) == []


def test_formatter_and_dispatch_failure_branches(monkeypatch) -> None:
    output = FlextCliOutput()

    monkeypatch.setattr(
        output,
        "ensure_str",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("ensure boom")),
    )
    create = output.create_formatter("json")
    assert create.is_failure

    monkeypatch.setattr(
        output, "_try_registered_formatter", lambda *_a, **_k: r.fail("no formatter")
    )
    monkeypatch.setattr(
        output,
        "_convert_result_to_formattable",
        lambda *_a, **_k: r.fail("convert fail"),
    )
    converted = output.format_and_display_result({"a": 1}, "json")
    assert converted.is_failure

    called: dict[str, object] = {}

    def formatter(value, fmt) -> None:
        called["value"] = value
        called["fmt"] = fmt

    generic = output._dispatch_registered_formatter("abc", formatter, "table")
    assert generic.is_success
    assert called["value"] == "abc"


def test_registered_result_and_dict_format_branches(monkeypatch) -> None:
    output = FlextCliOutput()
    received: dict[str, object] = {}

    def formatter(value, fmt) -> None:
        received["value"] = value
        received["fmt"] = fmt

    class CustomValue:
        pass

    monkeypatch.setattr(output, "is_json", lambda *_a, **_k: False)
    result = output._format_registered_result(r.ok(CustomValue()), formatter, "json")
    assert result.is_success
    assert isinstance(received["value"], str)

    class Holder:
        def __init__(self) -> None:
            self.a = 1

    dict_result = output._format_dict_object(r.ok(Holder()), "json")
    assert dict_result.is_success


def test_table_creation_and_population_failures(monkeypatch) -> None:
    output = FlextCliOutput()

    monkeypatch.setattr(
        "flext_cli.services.output.u.Cli.process", lambda *_a, **_k: r.fail("keys fail")
    )
    headers_fail = output._validate_headers(["a"], [{"a": 1}])
    assert headers_fail.is_failure

    monkeypatch.setattr(
        "flext_cli.services.output.u.Cli.process", lambda *_a, **_k: r.fail("rows fail")
    )
    rows_fail = output._build_table_rows([{"a": 1}], ["a"])
    assert rows_fail.is_failure

    monkeypatch.setattr(
        "flext_cli.services.output.FlextCliFormatters.create_table",
        lambda *_a, **_k: r.fail("create table fail"),
    )
    init_fail = output._initialize_rich_table(["a"], None)
    assert init_fail.is_failure

    monkeypatch.setattr(
        "flext_cli.services.output.FlextCliFormatters.create_table",
        lambda *_a, **_k: r.ok(object()),
    )
    protocol_fail = output._initialize_rich_table(["a"], None)
    assert protocol_fail.is_failure

    class FakeTable:
        def add_column(self, _name: str) -> None:
            return None

        def add_row(self, *_row: str) -> None:
            return None

    monkeypatch.setattr(
        FlextCliOutput,
        "_build_table_rows",
        staticmethod(lambda *_a, **_k: r.fail("rows boom")),
    )
    populate_fail = output._populate_table_rows(FakeTable(), [{"a": 1}], ["a"])
    assert populate_fail.is_failure


def test_create_rich_table_error_paths(monkeypatch) -> None:
    output = FlextCliOutput()

    monkeypatch.setattr(
        output, "_initialize_rich_table", lambda *_a, **_k: r.fail("init fail")
    )
    init_fail = output.create_rich_table([{"a": 1}])
    assert init_fail.is_failure

    class FakeTable:
        columns: list[str] = []

        def add_column(self, _name: str) -> None:
            return None

        def add_row(self, *_row: str) -> None:
            return None

    monkeypatch.setattr(
        output, "_initialize_rich_table", lambda *_a, **_k: r.ok(FakeTable())
    )
    monkeypatch.setattr(
        output, "_populate_table_rows", lambda *_a, **_k: r.fail("populate fail")
    )
    populate_fail = output.create_rich_table([{"a": 1}])
    assert populate_fail.is_failure

    monkeypatch.setattr(
        output,
        "_prepare_table_headers",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("prepare boom")),
    )
    exc_fail = output.create_rich_table([{"a": 1}])
    assert exc_fail.is_failure


def test_ascii_progress_and_serialization_error_paths(monkeypatch) -> None:
    output = FlextCliOutput()

    marker: dict[str, object] = {}

    def fake_create_table(*_args, **kwargs):
        marker["config"] = kwargs["config"]
        return r.ok("ok")

    monkeypatch.setattr(
        "flext_cli.services.output.FlextCliTables.create_table", fake_create_table
    )
    ascii_result = output.create_ascii_table(data=[{"a": 1}], config=object())
    assert ascii_result.is_success
    assert marker["config"] is not None

    monkeypatch.setattr(
        "flext_cli.services.output.FlextCliFormatters.create_progress",
        lambda *_a, **_k: r.ok(object()),
    )
    with pytest.raises(TypeError):
        output.create_progress_bar()

    monkeypatch.setattr(
        "flext_cli.services.output.FlextCliFormatters.create_progress",
        lambda *_a, **_k: r.fail("no progress"),
    )
    progress_fail = output.create_progress_bar()
    assert progress_fail.is_failure

    monkeypatch.setattr(
        json,
        "dumps",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("json boom")),
    )
    json_fail = output.format_json({"a": 1})
    assert json_fail.is_failure

    monkeypatch.setattr(
        "flext_cli.services.output.yaml.dump",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("yaml boom")),
    )
    yaml_fail = output.format_yaml({"a": 1})
    assert yaml_fail.is_failure


def test_iteration_and_csv_helper_branches(monkeypatch) -> None:
    output = FlextCliOutput()

    assert output._coerce_to_list((1, 2)) == [1, 2]
    assert output._coerce_to_list({"a": 1}) == [("a", 1)]
    assert output._coerce_to_list("abc") == []

    class TinyIterable:
        def __iter__(self):
            return iter(["x"])

    assert output._coerce_to_list(TinyIterable()) == ["x"]

    monkeypatch.setattr(
        output,
        "_try_iterate_items",
        lambda *_a, **_k: (_ for _ in ()).throw(TypeError("iter boom")),
    )
    assert output._coerce_to_list(10) == []

    monkeypatch.setattr(output, "_try_iterate_items", lambda *_a, **_k: [])
    assert output._try_iterate_items(10) == []
    monkeypatch.setattr(
        output,
        "_resolve_iteration_strategy",
        lambda *_a, **_k: None,
    )
    assert output._try_iterate_items(10) == []
    monkeypatch.setattr(
        output,
        "_resolve_iteration_strategy",
        lambda *_a, **_k: lambda _d: (_ for _ in ()).throw(TypeError("strategy boom")),
    )
    assert output._try_iterate_items(10) == []

    output2 = FlextCliOutput()

    assert output2._resolve_iteration_strategy({"a": 1}) is not None
    assert output2._resolve_iteration_strategy([1, 2]) is not None

    class CustomIterable:
        def __iter__(self):
            return iter([1])

    assert output2._resolve_iteration_strategy(CustomIterable()) is not None
    assert output2._resolve_iteration_strategy(10) is None

    assert output2._is_mapping_value({"a": 1}) is True
    assert output2._is_sequence_value((1, 2)) is True
    assert output2._is_custom_iterable_value(CustomIterable()) is True

    assert output2._iterate_mapping({"a": 1}) == [("a", 1)]
    assert output2._iterate_mapping(1) == []
    assert output2._iterate_sequence([1, 2]) == [1, 2]
    assert output2._iterate_sequence(10) == []

    class CustomIterableModel:
        def __iter__(self):
            return iter([1, 2])

    assert output2._iterate_model(CustomIterableModel()) == [1, 2]
    assert output2._iterate_model(10) == []

    class CustomObj:
        pass

    assert isinstance(output2._normalize_iterable_item(CustomObj()), str)
    assert output2._convert_iterable_to_list((1, 2)) == [1, 2]

    class NonSequenceIterable(Iterable[object]):
        def __iter__(self):
            return iter([CustomObj()])

    converted = output2._convert_iterable_to_list(NonSequenceIterable())
    assert len(converted) == 1
    assert isinstance(converted[0], str)

    class BadIterable(Iterable[object]):
        def __iter__(self):
            raise ValueError("bad iter")

    assert output2._convert_iterable_to_list(BadIterable()) == []
    assert output2._format_csv_list("bad").is_failure
    assert output2._replace_none_for_csv("k", None) == ""
    assert output2._replace_none_for_csv("k", object())


def test_try_iterate_items_none_and_exception_branches(monkeypatch) -> None:
    output = FlextCliOutput()

    assert output._try_iterate_items(10) == []

    monkeypatch.setattr(
        output,
        "_resolve_iteration_strategy",
        lambda *_a, **_k: (_ for _ in ()).throw(TypeError("strategy err")),
    )
    assert output._try_iterate_items(10) == []


def test_table_and_tree_remaining_error_paths(monkeypatch) -> None:
    output = FlextCliOutput()

    monkeypatch.setattr(
        output,
        "_prepare_table_data",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("table prep boom")),
    )
    prep_fail = output._prepare_table_data_safe({"a": 1}, None)
    assert prep_fail.is_failure

    data = [{"a": 1}]
    list_fail = output._prepare_list_data(data, ["missing"])
    assert list_fail.is_failure

    monkeypatch.setattr(
        "flext_cli.services.output.m.Cli.TableConfig.model_validate",
        lambda *_a, **_k: (_ for _ in ()).throw(RuntimeError("cfg boom")),
    )
    table_fail = output._create_table_string(data, ["a"])
    assert table_fail.is_failure

    monkeypatch.setattr(
        "flext_cli.services.output.FlextCliFormatters.create_tree",
        lambda *_a, **_k: r.fail("tree fail"),
    )
    tree_fail = output.format_as_tree({"a": 1})
    assert tree_fail.is_failure

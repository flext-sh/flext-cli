from __future__ import annotations

from flext_core import r

from flext_cli.models import m
from flext_cli.services.tables import FlextCliTables


def test_create_table_fails_when_config_build_fails(monkeypatch) -> None:
    import flext_cli.services.tables as tables_module

    monkeypatch.setattr(
        tables_module.u.Configuration,
        "build_options_from_kwargs",
        staticmethod(lambda **_kwargs: r.fail("bad config")),
    )

    result = FlextCliTables.create_table([{"a": 1}])

    assert result.is_failure


def test_create_table_fails_when_prepare_headers_fails(monkeypatch) -> None:
    monkeypatch.setattr(
        FlextCliTables,
        "_prepare_headers",
        staticmethod(lambda _data, _headers: r.fail("bad headers")),
    )

    result = FlextCliTables.create_table([{"a": 1}], table_format="grid")

    assert result.is_failure


def test_create_table_handles_tabulate_exception(monkeypatch) -> None:
    import flext_cli.services.tables as tables_module

    monkeypatch.setattr(
        tables_module,
        "tabulate",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("tab boom")),
    )

    result = FlextCliTables.create_table([{"a": 1}], table_format="grid")

    assert result.is_failure


def test_prepare_headers_dict_and_generic_iterable_paths() -> None:
    from collections import deque

    dict_result = FlextCliTables._prepare_headers({"a": 1}, "keys")
    assert dict_result.is_success

    generic_result = FlextCliTables._prepare_headers(deque([1, 2]), "keys")
    assert generic_result.is_success


def test_calculate_column_count_branches() -> None:
    tables = FlextCliTables()

    assert tables._calculate_column_count([{"a": 1}], ["a"]) == 1
    assert tables._calculate_column_count({"a": 1, "b": 2}, "keys") == 2
    assert tables._calculate_column_count([[1, 2, 3]], "keys") == 3
    assert tables._calculate_column_count([], "keys") == 0


def test_create_table_string_success_and_failure(monkeypatch) -> None:
    import flext_cli.services.tables as tables_module

    tables = FlextCliTables()
    cfg = m.Cli.TableConfig(table_format="grid", colalign=["left", "right", "center"])

    ok_result = tables._create_table_string([[1, 2]], cfg, ["a", "b"])
    assert ok_result.is_success

    monkeypatch.setattr(
        tables_module,
        "tabulate",
        lambda *args, **kwargs: (_ for _ in ()).throw(RuntimeError("create boom")),
    )
    fail_result = tables._create_table_string([[1, 2]], cfg, ["a", "b"])
    assert fail_result.is_failure


def test_print_available_formats_failure_branch(monkeypatch) -> None:
    import flext_cli.services.tables as tables_module

    class FakeGeneric:
        @staticmethod
        def ok(value=True):
            _ = value
            raise RuntimeError("ok boom")

        @staticmethod
        def fail(message: str):
            return r.fail(message)

    class FakeResult:
        def __class_getitem__(cls, _item):
            return FakeGeneric

    monkeypatch.setattr(tables_module, "r", FakeResult)

    result = FlextCliTables.print_available_formats()

    assert result.is_failure


def test_print_available_formats_executes_convert_helper(monkeypatch) -> None:
    import inspect
    import flext_cli.services.tables as tables_module

    called = {"ok": False}

    class FakeGeneric:
        @staticmethod
        def ok(value=True):
            _ = value
            frame = inspect.currentframe()
            assert frame is not None
            caller = frame.f_back
            assert caller is not None
            convert = caller.f_locals["convert_format"]
            converted = convert("grid", "Grid table")
            assert converted == {"format": "grid", "description": "Grid table"}
            called["ok"] = True
            return r.ok(True)

        @staticmethod
        def fail(message: str):
            return r.fail(message)

    class FakeResult:
        def __class_getitem__(cls, _item):
            return FakeGeneric

    monkeypatch.setattr(tables_module, "r", FakeResult)

    result = FlextCliTables.print_available_formats()

    assert result.is_success
    assert called["ok"] is True

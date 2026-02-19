from __future__ import annotations

from flext_core import r

from flext_cli.debug import FlextCliDebug


def test_convert_result_to_json_value_returns_error_fallback() -> None:
    result = r[dict[str, object]].fail("")

    value = FlextCliDebug._convert_result_to_json_value(result)

    assert value == "Unknown error"


def test_collect_info_safely_records_error_key_on_failure(
    flext_cli_debug: FlextCliDebug,
    monkeypatch,
) -> None:
    debug = flext_cli_debug
    info: dict[str, object] = {}

    monkeypatch.setattr(
        FlextCliDebug,
        "get_system_info",
        lambda self: r.fail("failed info"),
    )
    debug._collect_info_safely("get_system_info", "SYSTEM_ERROR", info)

    assert info["SYSTEM_ERROR"] == "failed info"


def test_public_methods_return_failures_when_internal_calls_raise(
    flext_cli_debug: FlextCliDebug,
    monkeypatch,
) -> None:
    debug = flext_cli_debug

    monkeypatch.setattr(
        FlextCliDebug,
        "_get_environment_info",
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("env boom"))),
    )
    assert debug.get_environment_variables().is_failure

    monkeypatch.setattr(
        FlextCliDebug,
        "_validate_filesystem_permissions",
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("validate boom"))),
    )
    assert debug.validate_environment_setup().is_failure

    monkeypatch.setattr(
        FlextCliDebug,
        "_get_system_info",
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("sys boom"))),
    )
    assert debug.get_system_info().is_failure
    assert debug.get_debug_info().is_failure

    monkeypatch.setattr(
        FlextCliDebug,
        "_get_path_info",
        staticmethod(lambda: (_ for _ in ()).throw(RuntimeError("path boom"))),
    )
    assert debug.get_system_paths().is_failure

    monkeypatch.setattr(
        FlextCliDebug,
        "_collect_info_safely",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(RuntimeError("collect boom")),
    )
    assert debug.get_comprehensive_debug_info().is_failure


def test_static_methods_return_failures_when_generate_raises(monkeypatch) -> None:
    import flext_cli.debug as debug_module

    monkeypatch.setattr(
        debug_module.FlextCliUtilities,
        "generate",
        staticmethod(lambda _kind: (_ for _ in ()).throw(RuntimeError("gen boom"))),
    )

    assert FlextCliDebug.test_connectivity().is_failure
    assert FlextCliDebug.execute_health_check().is_failure
    assert FlextCliDebug.execute_trace(["a"]).is_failure


def test_validate_filesystem_permissions_collects_write_error(monkeypatch) -> None:
    import flext_cli.debug as debug_module

    original_write_text = debug_module.pathlib.Path.write_text

    def fail_write(self, data, encoding=None):
        _ = self, data, encoding
        raise OSError("no write")

    monkeypatch.setattr(debug_module.pathlib.Path, "write_text", fail_write)
    errors = FlextCliDebug._validate_filesystem_permissions()
    monkeypatch.setattr(debug_module.pathlib.Path, "write_text", original_write_text)

    assert errors


def test_validate_filesystem_permissions_collects_outer_exception(monkeypatch) -> None:
    import flext_cli.debug as debug_module

    monkeypatch.setattr(
        debug_module.tempfile,
        "NamedTemporaryFile",
        lambda delete=True: (_ for _ in ()).throw(RuntimeError("tmp boom")),
    )

    errors = FlextCliDebug._validate_filesystem_permissions()

    assert errors
    assert "tmp boom" in errors[0]

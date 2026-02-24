from __future__ import annotations

from flext_core import r

from flext_cli.models import FlextCliContext


def test_safe_dict_operation_returns_failure_on_exception() -> None:
    class BadDict(dict):
        def __contains__(self, _key):
            raise RuntimeError("contains failed")

    result = FlextCliContext._safe_dict_operation("get", BadDict(), "x")

    assert result.is_failure
    assert "contains failed" in (result.error or "")


def test_safe_dict_operation_unknown_operation_uses_failed_message() -> None:
    result = FlextCliContext._safe_dict_operation("noop", {}, "x")

    assert result.is_failure
    assert "Operation failed" in (result.error or "")


def test_safe_list_operation_handles_none_after_custom_init_check(monkeypatch) -> None:
    monkeypatch.setattr(
        FlextCliContext,
        "_ensure_initialized",
        staticmethod(lambda _value, _msg: r[bool].ok(True)),
    )

    result = FlextCliContext._safe_list_operation("add", None, "x")

    assert result.is_failure
    assert "initialized" in (result.error or "").lower()


def test_safe_list_operation_unknown_operation_uses_failed_message() -> None:
    result = FlextCliContext._safe_list_operation("noop", [], "x")

    assert result.is_failure
    assert "Operation failed" in (result.error or "")


def test_safe_list_operation_uses_exception_template(monkeypatch) -> None:
    def explode(_list_obj, _value):
        raise RuntimeError("explode")

    monkeypatch.setattr(FlextCliContext, "_perform_add", staticmethod(explode))

    result = FlextCliContext._safe_list_operation(
        "add",
        [],
        "x",
        error_messages={"exception": "add failed: {error}"},
    )

    assert result.is_failure
    assert "explode" in (result.error or "")


def test_set_metadata_returns_failure_on_setitem_exception() -> None:
    ctx = FlextCliContext()
    object.__setattr__(ctx, "context_metadata", None)

    result = ctx.set_metadata("k", "v")

    assert result.is_failure
    assert "metadata" in (result.error or "").lower()

from __future__ import annotations

from pathlib import Path

from flext_core import r

from flext_cli import c
from flext_cli.api import FlextCli
import flext_cli.api as api_module


def test_init_logs_warning_when_container_registration_fails(
    monkeypatch,
) -> None:
    warnings: list[str] = []

    class FakeLogger:
        def warning(self, message: str) -> None:
            warnings.append(message)

    class FakeContainer:
        def has_service(self, _key: str) -> bool:
            return False

        def register(self, _key: str, _value: str) -> r[bool]:
            return r[bool].fail("register failed")

    monkeypatch.setattr(api_module, "logger_core", lambda _name: FakeLogger())
    monkeypatch.setattr(api_module, "container", FakeContainer)

    FlextCli()

    assert warnings
    assert "register failed" in warnings[0]


def test_get_auth_token_falls_back_to_model_validation(flext_cli_api: FlextCli) -> None:
    token_file = flext_cli_api.config.token_file
    token_file.parent.mkdir(parents=True, exist_ok=True)
    token_file.write_text('{"token": ""}', encoding="utf-8")

    result = flext_cli_api.get_auth_token()

    assert result.is_success
    assert result.value == ""


def test_register_cli_entity_rejects_missing_name_or_callback(
    flext_cli_api: FlextCli,
    monkeypatch,
) -> None:
    def passthrough(name=None):
        return lambda _func: lambda: None

    monkeypatch.setattr(flext_cli_api._cli, "create_command_decorator", passthrough)

    with_exception = False
    try:
        flext_cli_api._register_cli_entity("command", "bad", lambda: None)
    except TypeError:
        with_exception = True

    assert with_exception

    class CallableNoCallback:
        name = "x"

        def __call__(self):
            return None

    def without_callback(name=None):
        return lambda _func: CallableNoCallback()

    monkeypatch.setattr(
        flext_cli_api._cli, "create_command_decorator", without_callback
    )

    with_exception = False
    try:
        flext_cli_api._register_cli_entity("command", "bad2", lambda: None)
    except TypeError:
        with_exception = True

    assert with_exception


def test_is_rich_tree_protocol_handles_attribute_errors() -> None:
    class BrokenObject:
        def __getattr__(self, _name: str):
            raise AttributeError("broken")

    assert FlextCli._is_rich_tree_protocol(BrokenObject()) is False
    assert FlextCli._is_rich_tree_protocol(object()) is False


def test_is_rich_tree_protocol_true_with_rich_tree_instance() -> None:
    tree_result = FlextCli().create_tree("root")

    assert tree_result.is_success
    assert FlextCli._is_rich_tree_protocol(tree_result.value) is True


def test_is_rich_tree_protocol_attribute_error_branch(monkeypatch) -> None:
    monkeypatch.setattr(
        api_module,
        "hasattr",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AttributeError("attr boom")),
        raising=False,
    )

    assert FlextCli._is_rich_tree_protocol(object()) is False


def test_is_rich_tree_protocol_attribute_error_via_getattr(monkeypatch) -> None:
    monkeypatch.setattr(
        api_module,
        "getattr",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AttributeError("getattr boom")),
        raising=False,
    )

    assert FlextCli._is_rich_tree_protocol(object()) is False

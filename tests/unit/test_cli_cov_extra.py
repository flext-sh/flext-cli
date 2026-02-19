from __future__ import annotations

import click
import pytest
from pydantic import BaseModel
from typing import ClassVar

from flext_core import r

from flext_cli.cli import FlextCliCli
from flext_cli.cli_params import FlextCliCommonParams


def test_extract_typed_value_branches() -> None:
    cli = FlextCliCli()

    assert cli._extract_typed_value(None, "str", "d") == "d"
    assert isinstance(cli._extract_typed_value(10, "str", ""), str)
    assert cli._extract_typed_value("x", "dict", {}) == {}
    assert cli._extract_typed_value("x", "unknown", None) is None

    result = cli._extract_typed_value({"a": 1, "b": object()}, "dict", {})
    assert isinstance(result, dict)
    assert "a" in result
    assert isinstance(
        cli._extract_typed_value("x", "dict", object()),
        str,
    )


def test_apply_common_params_config_early_returns_and_fail(monkeypatch) -> None:
    cli = FlextCliCli()

    class Cfg:
        model_fields: ClassVar[dict[str, object]] = {}

        def __init__(self) -> None:
            self.debug = False
            self.trace = False

    cfg = Cfg()
    cli._apply_common_params_to_config(cfg)

    Cfg.model_fields = {"debug": object()}
    monkeypatch.setattr(
        FlextCliCommonParams,
        "apply_to_config",
        classmethod(lambda _cls, _config, **_kwargs: r.fail("param fail")),
    )
    cli._apply_common_params_to_config(cfg, debug=True)


def test_create_group_and_build_helpers_error_paths(monkeypatch) -> None:
    cli = FlextCliCli()

    monkeypatch.setattr(
        cli,
        "_create_cli_decorator",
        lambda *_args, **_kwargs: lambda _func: click.Command("x"),
    )
    group_decorator = cli.create_group_decorator("g")
    with pytest.raises(TypeError):
        group_decorator(lambda: None)

    monkeypatch.setattr(cli, "_build_typed_value", lambda *_args, **_kwargs: 1)
    with pytest.raises(TypeError):
        cli._build_str_value({}, "k")

    # Use a fresh instance so _build_typed_value is not monkeypatched.
    cli = FlextCliCli()

    cli2 = FlextCliCli()
    monkeypatch.setattr(
        "flext_cli.cli.u.mapper",
        lambda: type("Mapper", (), {"get": staticmethod(lambda _d, _k: "x")})(),
    )
    monkeypatch.setattr("flext_cli.cli.u.build", lambda *_args, **_kwargs: 1)
    with pytest.raises(TypeError):
        cli2._build_typed_value({"k": "x"}, "k", "str", "")


def test_option_datetime_and_type_factory_errors(monkeypatch) -> None:
    cli = FlextCliCli()

    monkeypatch.setattr(
        cli, "_build_option_config_from_kwargs", lambda _kwargs: object()
    )
    monkeypatch.setattr(cli, "_is_option_config_protocol", lambda _obj: False)
    with pytest.raises(TypeError):
        cli.create_option_decorator("--x")

    monkeypatch.setattr("flext_cli.cli.u.build", lambda *_args, **_kwargs: "bad")
    with pytest.raises(TypeError):
        FlextCliCli._datetime_type()

    assert isinstance(FlextCliCli.type_factory("tuple", tuple_types=None), click.Tuple)
    with pytest.raises(ValueError):
        FlextCliCli.type_factory("unsupported")


def test_type_getters_error_paths(monkeypatch) -> None:
    monkeypatch.setattr(
        FlextCliCli,
        "type_factory",
        classmethod(lambda _cls, _name, **_kwargs: object()),
    )
    with pytest.raises(TypeError):
        FlextCliCli.get_datetime_type()
    with pytest.raises(TypeError):
        FlextCliCli.get_uuid_type()
    with pytest.raises(TypeError):
        FlextCliCli.get_tuple_type([str])
    with pytest.raises(TypeError):
        FlextCliCli.get_bool_type()
    with pytest.raises(TypeError):
        FlextCliCli.get_string_type()
    with pytest.raises(TypeError):
        FlextCliCli.get_int_type()
    with pytest.raises(TypeError):
        FlextCliCli.get_float_type()


def test_pass_context_and_config_getter_error_paths(monkeypatch) -> None:
    monkeypatch.setattr(
        "flext_cli.cli.click.pass_context",
        lambda func: lambda: func(click.Context(click.Command("x"))),
    )
    wrapped = FlextCliCli.create_pass_context_decorator()(lambda _ctx: "ok")
    assert wrapped(click.Context(click.Command("x"))) == "ok"

    get_bool, get_str = FlextCliCli._build_config_getters({"x": "v"})
    monkeypatch.setattr("flext_cli.cli.u.build", lambda *_args, **_kwargs: 1)
    with pytest.raises(TypeError):
        get_bool("x")
    with pytest.raises(TypeError):
        get_str("x")


def test_config_getter_success_and_normalize_hint_paths() -> None:
    cli = FlextCliCli()
    _get_bool, get_str = FlextCliCli._build_config_getters({"x": "v"})
    assert get_str("x") == "v"

    assert cli._normalize_type_hint(None) is None
    assert cli._normalize_type_hint("abc") == "abc"
    assert cli._normalize_type_hint({"a": 1}) == {"a": 1}
    assert isinstance(cli._normalize_type_hint(object()), str)


def test_confirm_and_prompt_error_paths(monkeypatch) -> None:
    monkeypatch.setattr(
        FlextCliCli,
        "_build_confirm_config_from_kwargs",
        staticmethod(lambda _kwargs: object()),
    )
    with pytest.raises(TypeError):
        FlextCliCli.confirm("q")

    monkeypatch.setattr(
        FlextCliCli,
        "_build_prompt_config_from_kwargs",
        staticmethod(lambda _kwargs: object()),
    )
    with pytest.raises(TypeError):
        FlextCliCli.prompt("q")

    class PromptCfg:
        default = None
        hide_input = False
        confirmation_prompt = False
        type_hint = str
        value_proc = None
        prompt_suffix = ": "
        show_default = True
        err = False
        show_choices = True

    monkeypatch.setattr(
        "flext_cli.cli.typer.prompt", lambda **_kwargs: {"a": object(), "b": 1}
    )
    dict_result = FlextCliCli.prompt("q", config=PromptCfg())
    assert dict_result.is_success
    assert dict_result.value == {"b": 1}

    monkeypatch.setattr("flext_cli.cli.typer.prompt", lambda **_kwargs: object())
    str_result = FlextCliCli.prompt("q", config=PromptCfg())
    assert str_result.is_success
    assert isinstance(str_result.value, str)


def test_model_command_failure_result_branch() -> None:
    class DemoModel(BaseModel):
        name: str

    command = FlextCliCli.model_command(
        DemoModel, lambda _model: r.fail("handler fail")
    )

    with pytest.raises(ValueError):
        command(name="x")


def test_apply_common_params_edge_paths(monkeypatch) -> None:
    cli = FlextCliCli()

    class Cfg:
        model_fields: ClassVar[dict[str, object]] = {"other": object()}

        def __init__(self) -> None:
            self.debug = False
            self.trace = False

    cfg = Cfg()
    cli._apply_common_params_to_config(cfg, debug=True)

    Cfg.model_fields = {"log_level": object()}
    monkeypatch.setattr(
        cli,
        "_extract_typed_value",
        lambda _value, kind, _default=None: 123 if kind == "str" else True,
    )
    monkeypatch.setattr(
        FlextCliCommonParams,
        "apply_to_config",
        classmethod(lambda _cls, _config, **_kwargs: r.ok(_config)),
    )
    cli._apply_common_params_to_config(cfg, log_level="info")


def test_confirm_and_prompt_builder_type_errors(monkeypatch) -> None:
    monkeypatch.setattr(
        FlextCliCli,
        "_build_prompt_or_confirm_config",
        staticmethod(lambda _kind, _kwargs: object()),
    )
    with pytest.raises(TypeError):
        FlextCliCli._build_confirm_config_from_kwargs({})
    with pytest.raises(TypeError):
        FlextCliCli._build_prompt_config_from_kwargs({})


def test_model_command_normalized_handler_branches(monkeypatch) -> None:
    class DemoModel(BaseModel):
        name: str

    class OtherModel(BaseModel):
        name: str

    class BuilderStub:
        def __init__(self, _model_class, handler, _config):
            self.handler = handler

        def build(self):
            return self.handler

    monkeypatch.setattr("flext_cli.cli.m.Cli.ModelCommandBuilder", BuilderStub)

    cmd = FlextCliCli.model_command(DemoModel, lambda model: f"ok:{model.name}")
    with pytest.raises(TypeError):
        cmd(object())
    with pytest.raises(TypeError):
        cmd(OtherModel(name="x"))

    cmd_ok = FlextCliCli.model_command(DemoModel, lambda model: r.ok(model.name))
    assert cmd_ok(DemoModel(name="yes")) == "yes"

    cmd_plain = FlextCliCli.model_command(DemoModel, lambda model: model.name.upper())
    assert cmd_plain(DemoModel(name="up")) == "UP"

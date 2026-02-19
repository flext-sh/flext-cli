from __future__ import annotations

import pytest

from flext_cli.cli_params import FlextCliCommonParams
from flext_cli.models import m
from flext_cli.settings import FlextCliSettings


def test_resolve_params_returns_explicit_params_instance() -> None:
    params = m.Cli.CliParamsConfig(verbose=True)

    result = FlextCliCommonParams._resolve_params(params, {})

    assert result is params


def test_apply_to_config_returns_failure_when_resolve_raises(monkeypatch) -> None:
    config = FlextCliSettings()

    monkeypatch.setattr(
        FlextCliCommonParams,
        "_resolve_params",
        classmethod(
            lambda _cls, _params, _kwargs: (_ for _ in ()).throw(
                RuntimeError("bad resolve")
            )
        ),
    )

    result = FlextCliCommonParams.apply_to_config(config)

    assert result.is_failure
    assert "bad resolve" in (result.error or "")


def test_set_format_params_sets_log_format_and_output_format() -> None:
    config = FlextCliSettings()
    params = m.Cli.CliParamsConfig(log_format="compact", output_format="JSON")

    result = FlextCliCommonParams._set_format_params(config, params)

    assert result.is_success
    assert config.log_verbosity == "compact"
    assert result.value.output_format == "json"


def test_configure_logger_fails_for_invalid_log_level() -> None:
    config = FlextCliSettings()
    object.__setattr__(config, "cli_log_level", "INVALID")

    result = FlextCliCommonParams.configure_logger(config)

    assert result.is_failure
    assert "invalid" in (result.error or "").lower()


def test_configure_logger_handles_runtime_exception() -> None:
    class BrokenConfig:
        @property
        def cli_log_level(self):
            raise RuntimeError("read failure")

    result = FlextCliCommonParams.configure_logger(BrokenConfig())

    assert result.is_failure
    assert "read failure" in (result.error or "")


def test_create_decorator_returns_function_when_enabled() -> None:
    FlextCliCommonParams._params_enabled = True
    FlextCliCommonParams.enable_enforcement()

    decorator = FlextCliCommonParams.create_decorator()

    def command_fn() -> str:
        return "ok"

    wrapped = decorator(command_fn)
    assert wrapped is command_fn


def test_create_decorator_exits_when_enforcement_fails() -> None:
    FlextCliCommonParams._params_enabled = False
    FlextCliCommonParams.enable_enforcement()

    decorator = FlextCliCommonParams.create_decorator()

    with pytest.raises(SystemExit):
        decorator(lambda: None)

    FlextCliCommonParams._params_enabled = True

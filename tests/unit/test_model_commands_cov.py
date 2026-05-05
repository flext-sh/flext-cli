"""Coverage tests for the public model-command DSL on ``cli``."""

from __future__ import annotations

import inspect

from flext_cli import cli
from tests import m, p


class _SampleModel(m.BaseModel):
    """Sample model for command tests."""

    name: str
    value: int = 42


class _SampleModelNoDefaults(m.BaseModel):
    """Sample model with all required fields."""

    key: str
    count: int


class TestsFlextCliModelCommandsCov:
    """Coverage tests for public model-command helpers."""

    def test_derive_model_from_mapping(self) -> None:
        result = cli.derive_model(_SampleModel, {"name": "hello", "value": 7})
        assert result.name == "hello"
        assert result.value == 7

    def test_derive_model_from_model_excludes_none(self) -> None:
        class _NullableModel(m.BaseModel):
            name: str
            optional: str | None = None

        source = _NullableModel(name="test", optional=None)
        result = cli.derive_model(_NullableModel, source)
        assert result.name == "test"
        assert result.optional is None

    def test_derive_model_with_overrides(self) -> None:
        result = cli.derive_model(
            _SampleModel,
            {"name": "base", "value": 1},
            overrides={"value": 99},
        )
        assert result.value == 99

    def test_derive_model_multiple_sources(self) -> None:
        result = cli.derive_model(
            _SampleModel,
            {"name": "first"},
            {"name": "second", "value": 5},
        )
        # later source wins
        assert result.name == "second"
        assert result.value == 5

    def test_build_model_command_callable(self) -> None:
        def handler(model: _SampleModel) -> str:
            return f"{model.name}-{model.value}"

        cmd = cli.model_command(_SampleModel, handler)
        assert callable(cmd)

    def test_model_command_with_settings_updates_runtime_values(self) -> None:
        settings = _SampleModel(name="from_settings", value=0)

        def handler(model: _SampleModel) -> str:
            return model.name

        cmd = cli.model_command(_SampleModel, handler, settings=settings)
        result = cmd(name="override", value=1)
        assert result == "override"
        assert settings.name == "override"
        assert settings.value == 1

    def test_model_command_required_fields_use_required_option_defaults(self) -> None:
        def handler(model: _SampleModelNoDefaults) -> str:
            return model.key

        cmd = cli.model_command(_SampleModelNoDefaults, handler)
        sig = inspect.signature(cmd)
        for param in sig.parameters.values():
            if param.name == "key":
                assert isinstance(param.default, p.Cli.CliOptionSpec)
                assert param.default.default is ...
                break

    def test_model_command_signature_keeps_model_default_for_optional_fields(
        self,
    ) -> None:
        settings = _SampleModel(name="default_name")

        def handler(model: _SampleModel) -> str:
            return model.name

        cmd = cli.model_command(_SampleModel, handler, settings=settings)
        option = inspect.signature(cmd).parameters["value"].default
        assert isinstance(option, p.Cli.CliOptionSpec)
        assert option.default == 42

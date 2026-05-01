"""Coverage tests for FlextCliUtilitiesModelCommands and FlextCliUtilitiesModelCommandBuilder."""

from __future__ import annotations

from flext_core import m


class _SampleModel(m.BaseModel):
    """Sample model for command tests."""

    name: str
    value: int = 42


class _SampleModelNoDefaults(m.BaseModel):
    """Sample model with all required fields."""

    key: str
    count: int


class TestsFlextCliModelCommandsCov:
    """Coverage tests for model command utilities."""

    def test_model_source_data_from_mapping(self) -> None:
        from flext_cli._utilities.model_commands import FlextCliUtilitiesModelCommands

        result = FlextCliUtilitiesModelCommands.model_source_data(
            _SampleModel, {"name": "hello", "value": 7, "extra": "ignored"}
        )
        assert result == {"name": "hello", "value": 7}

    def test_model_source_data_from_model(self) -> None:
        from flext_cli._utilities.model_commands import FlextCliUtilitiesModelCommands

        source = _SampleModel(name="world", value=99)
        result = FlextCliUtilitiesModelCommands.model_source_data(_SampleModel, source)
        assert result["name"] == "world"
        assert result["value"] == 99

    def test_model_source_data_excludes_none(self) -> None:
        from flext_cli._utilities.model_commands import FlextCliUtilitiesModelCommands

        class _NullableModel(m.BaseModel):
            name: str
            optional: str | None = None

        source = _NullableModel(name="test", optional=None)
        result = FlextCliUtilitiesModelCommands.model_source_data(
            _NullableModel, source
        )
        assert "optional" not in result

    def test_derive_model_from_mapping(self) -> None:
        from flext_cli._utilities.model_commands import FlextCliUtilitiesModelCommands

        result = FlextCliUtilitiesModelCommands.derive_model(
            _SampleModel, {"name": "a", "value": 1}
        )
        assert result.name == "a"
        assert result.value == 1

    def test_derive_model_with_overrides(self) -> None:
        from flext_cli._utilities.model_commands import FlextCliUtilitiesModelCommands

        result = FlextCliUtilitiesModelCommands.derive_model(
            _SampleModel,
            {"name": "base", "value": 1},
            overrides={"value": 99},
        )
        assert result.value == 99

    def test_derive_model_multiple_sources(self) -> None:
        from flext_cli._utilities.model_commands import FlextCliUtilitiesModelCommands

        result = FlextCliUtilitiesModelCommands.derive_model(
            _SampleModel,
            {"name": "first"},
            {"name": "second", "value": 5},
        )
        # later source wins
        assert result.name == "second"
        assert result.value == 5

    def test_build_model_command_callable(self) -> None:
        from flext_cli._utilities.model_commands import FlextCliUtilitiesModelCommands

        def handler(model: _SampleModel) -> str:
            return f"{model.name}-{model.value}"

        cmd = FlextCliUtilitiesModelCommands.build_model_command(_SampleModel, handler)
        # should be callable
        assert callable(cmd)

    def test_build_model_command_with_settings(self) -> None:
        from flext_cli._utilities.model_commands import FlextCliUtilitiesModelCommands

        class _Settings(m.BaseModel):
            name: str = "from_settings"
            value: int = 0

        settings = _Settings()

        def handler(model: _SampleModel) -> str:
            return model.name

        cmd = FlextCliUtilitiesModelCommands.build_model_command(
            _SampleModel, handler, settings=settings
        )
        assert callable(cmd)

    def test_model_command_builder_required_fields(self) -> None:
        import inspect

        from flext_cli._utilities.model_commands import (
            FlextCliUtilitiesModelCommandBuilder,
        )

        def handler(model: _SampleModelNoDefaults) -> str:
            return model.key

        builder = FlextCliUtilitiesModelCommandBuilder(
            model_class=_SampleModelNoDefaults,
            handler=handler,
        )
        cmd = builder.build()
        sig = inspect.signature(cmd)
        for param in sig.parameters.values():
            # Required fields should have no default (empty)
            if param.name == "key":
                assert param.default is inspect.Parameter.empty
                break

    def test_model_command_builder_with_settings_default(self) -> None:
        from flext_cli._utilities.model_commands import (
            FlextCliUtilitiesModelCommandBuilder,
        )

        class _S(m.BaseModel):
            name: str = "default_name"

        settings = _S()

        def handler(model: _SampleModel) -> str:
            return model.name

        builder = FlextCliUtilitiesModelCommandBuilder(
            model_class=_SampleModel,
            handler=handler,
            settings=settings,
        )
        cmd = builder.build()
        result = cmd(name="override", value=1)
        assert result is not None

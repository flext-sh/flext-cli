"""Behavioral tests for the public model-command DSL on ``cli``.

Covers the observable contract of ``cli.derive_model`` and ``cli.model_command``:
returned/validated model state, handler dispatch, settings-seeded defaults,
default resolution, and error propagation via the Pydantic validation family.
No private attribute access, no internal-collaborator spying, no signature
introspection.
"""

from __future__ import annotations

import pytest

from flext_cli import cli, m


class TestsFlextCliModelCommandsCov:
    """Behavioral contract of the public model-command helpers."""

    class _SampleModel(m.BaseModel):
        """Model with one required and one defaulted field."""

        name: str
        value: int = 42

    class _SampleModelNoDefaults(m.BaseModel):
        """Model whose every field is required."""

        key: str
        count: int

    class _NullableModel(m.BaseModel):
        """Model with an optional field that defaults to ``None``."""

        name: str
        optional: str | None = None

    # ---- derive_model ---------------------------------------------------

    @pytest.mark.parametrize(
        ("payload", "expected_name", "expected_value"),
        [
            ({"name": "hello", "value": 7}, "hello", 7),
            ({"name": "only-required"}, "only-required", 42),
            ({"name": "zero", "value": 0}, "zero", 0),
        ],
    )
    def test_derive_model_from_mapping_validates_and_applies_defaults(
        self,
        payload: dict[str, str | int],
        expected_name: str,
        expected_value: int,
    ) -> None:
        result = cli.derive_model(self._SampleModel, payload)

        assert isinstance(result, self._SampleModel)
        assert result.name == expected_name
        assert result.value == expected_value

    def test_derive_model_from_model_instance_preserves_field_values(self) -> None:
        source = self._NullableModel(name="test", optional=None)

        result = cli.derive_model(self._NullableModel, source)

        assert result.name == "test"
        assert result.optional is None

    def test_derive_model_overrides_take_precedence_over_sources(self) -> None:
        result = cli.derive_model(
            self._SampleModel,
            {"name": "base", "value": 1},
            overrides={"value": 99},
        )

        assert result.name == "base"
        assert result.value == 99

    def test_derive_model_later_source_wins_over_earlier(self) -> None:
        result = cli.derive_model(
            self._SampleModel,
            {"name": "first"},
            {"name": "second", "value": 5},
        )

        assert result.name == "second"
        assert result.value == 5

    def test_derive_model_rejects_invalid_data_with_validation_error(self) -> None:
        with pytest.raises(m.ValidationError):
            cli.derive_model(self._SampleModel, {"value": "not-an-int"})

    def test_derive_model_rejects_missing_required_field(self) -> None:
        with pytest.raises(m.ValidationError):
            cli.derive_model(self._SampleModel, {"value": 1})

    # ---- model_command --------------------------------------------------

    def test_model_command_returns_callable(self) -> None:
        cmd = cli.model_command(self._SampleModel, lambda model: model.name)

        assert callable(cmd)

    def test_model_command_dispatches_to_handler_with_bound_model(self) -> None:
        def handler(model: TestsFlextCliModelCommandsCov._SampleModel) -> str:
            return f"{model.name}-{model.value}"

        cmd = cli.model_command(self._SampleModel, handler)

        assert cmd(name="x", value=3) == "x-3"

    def test_model_command_applies_field_default_for_omitted_optional(self) -> None:
        def handler(model: TestsFlextCliModelCommandsCov._SampleModel) -> int:
            return model.value

        cmd = cli.model_command(self._SampleModel, handler)

        assert cmd(name="y") == 42

    def test_model_command_resolves_values_without_mutating_settings(self) -> None:
        # Invocation no longer writes parsed values back into the settings
        # model (commit f5f83dee): settings seeds option defaults only, and
        # resolved values reach the handler through the validated model.
        settings = self._SampleModel(name="from_settings", value=0)

        def handler(model: TestsFlextCliModelCommandsCov._SampleModel) -> str:
            return model.name

        cmd = cli.model_command(self._SampleModel, handler, settings=settings)
        result = cmd(name="override", value=1)

        assert result == "override"
        assert settings.name == "from_settings"
        assert settings.value == 0

    def test_model_command_raises_validation_error_for_missing_required(self) -> None:
        def handler(model: TestsFlextCliModelCommandsCov._SampleModelNoDefaults) -> str:
            return model.key

        cmd = cli.model_command(self._SampleModelNoDefaults, handler)

        with pytest.raises(m.ValidationError):
            cmd()

    def test_model_command_binds_all_required_fields_to_model(self) -> None:
        def handler(model: TestsFlextCliModelCommandsCov._SampleModelNoDefaults) -> str:
            return f"{model.key}={model.count}"

        cmd = cli.model_command(self._SampleModelNoDefaults, handler)

        assert cmd(key="a", count=5) == "a=5"

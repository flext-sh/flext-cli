"""Behavioral tests for the public model-command DSL on ``cli``.

Covers the observable contract of ``cli.derive_model`` and ``cli.model_command``:
returned/validated model state, handler dispatch, settings-seeded defaults,
default resolution, and error propagation via the Pydantic validation family.
No private attribute access, no internal-collaborator spying, no signature
introspection.
"""

from __future__ import annotations

import pytest

from flext_cli import cli
from tests import m
from flext_tests import tm

# NOTE (multi-agent, mro-wkii.17 / agent: make_ssot_audit): model-command
# coverage consumes the owning field-only test models directly.


class TestsFlextCliModelCommandsCov:
    """Behavioral contract of the public model-command helpers."""

    # ---- derive_model ---------------------------------------------------

    @pytest.mark.parametrize(
        ("payload", "expected_name", "expected_value"),
        [
            (m.Tests.ModelCommandSource(name="hello", value=7), "hello", 7),
            (m.Tests.ModelCommandSource(name="only-required"), "only-required", 42),
            (m.Tests.ModelCommandSource(name="zero", value=0), "zero", 0),
        ],
    )
    def test_derive_model_from_source_model_applies_defaults(
        self,
        payload: m.Tests.ModelCommandSource,
        expected_name: str,
        expected_value: int,
    ) -> None:
        result = cli.derive_model(m.Tests.ModelCommandSample, payload)

        tm.that(result, is_=m.Tests.ModelCommandSample)
        tm.that(result.name, eq=expected_name)
        tm.that(result.value, eq=expected_value)

    def test_derive_model_from_model_instance_preserves_field_values(self) -> None:
        source = m.Tests.ModelCommandNullable(name="test", optional=None)

        result = cli.derive_model(m.Tests.ModelCommandNullable, source)

        tm.that(result.name, eq="test")
        tm.that(result.optional, none=True)

    def test_derive_model_partial_source_takes_precedence(self) -> None:
        result = cli.derive_model(
            m.Tests.ModelCommandSample,
            m.Tests.ModelCommandSource(name="base", value=1),
            m.Tests.ModelCommandSource(value=99),
        )

        tm.that(result.name, eq="base")
        tm.that(result.value, eq=99)

    def test_derive_model_later_source_wins_over_earlier(self) -> None:
        result = cli.derive_model(
            m.Tests.ModelCommandSample,
            m.Tests.ModelCommandSource(name="first"),
            m.Tests.ModelCommandSource(name="second", value=5),
        )

        tm.that(result.name, eq="second")
        tm.that(result.value, eq=5)

    def test_derive_model_rejects_invalid_data_with_validation_error(self) -> None:
        command = cli.model_command(
            m.Tests.ModelCommandSample, lambda model: model.value
        )

        with pytest.raises(m.ValidationError):
            command(name="invalid", value="not-an-int")

    def test_derive_model_rejects_missing_required_field(self) -> None:
        with pytest.raises(m.ValidationError):
            cli.derive_model(
                m.Tests.ModelCommandSample, m.Tests.ModelCommandSource(value=1)
            )

    # ---- model_command --------------------------------------------------

    def test_model_command_returns_callable(self) -> None:
        cmd = cli.model_command(m.Tests.ModelCommandSample, lambda model: model.name)

        tm.that(callable(cmd), eq=True)

    def test_model_command_dispatches_to_handler_with_bound_model(self) -> None:
        def handler(model: m.Tests.ModelCommandSample) -> str:
            return f"{model.name}-{model.value}"

        cmd = cli.model_command(m.Tests.ModelCommandSample, handler)

        tm.that(cmd(name="x", value=3), eq="x-3")

    def test_model_command_applies_field_default_for_omitted_optional(self) -> None:
        def handler(model: m.Tests.ModelCommandSample) -> int:
            return model.value

        cmd = cli.model_command(m.Tests.ModelCommandSample, handler)

        tm.that(cmd(name="y"), eq=42)

    def test_model_command_resolves_values_without_mutating_settings(self) -> None:
        # Invocation no longer writes parsed values back into the settings
        # model (commit f5f83dee): settings seeds option defaults only, and
        # resolved values reach the handler through the validated model.
        settings = m.Tests.ModelCommandSample(name="from_settings", value=0)

        def handler(model: m.Tests.ModelCommandSample) -> str:
            return model.name

        cmd = cli.model_command(m.Tests.ModelCommandSample, handler, settings=settings)
        result = cmd(name="override", value=1)

        tm.that(result, eq="override")
        tm.that(settings.name, eq="from_settings")
        tm.that(settings.value, eq=0)

    def test_model_command_raises_validation_error_for_missing_required(self) -> None:
        def handler(model: m.Tests.ModelCommandRequired) -> str:
            return model.key

        cmd = cli.model_command(m.Tests.ModelCommandRequired, handler)

        with pytest.raises(m.ValidationError):
            cmd()

    def test_model_command_binds_all_required_fields_to_model(self) -> None:
        def handler(model: m.Tests.ModelCommandRequired) -> str:
            return f"{model.key}={model.count}"

        cmd = cli.model_command(m.Tests.ModelCommandRequired, handler)

        tm.that(cmd(key="a", count=5), eq="a=5")

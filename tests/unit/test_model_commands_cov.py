"""Behavioral tests for the public model-command DSL on ``cli``.

Covers the observable contract of ``cli.model_command``:
returned/validated model state, handler dispatch, settings-seeded defaults,
default resolution, and error propagation via the Pydantic validation family.
No private attribute access, no internal-collaborator spying, no signature
introspection.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import cli
from tests import m

# NOTE (multi-agent, mro-wkii.17 / agent: make_ssot_audit): model-command
# coverage consumes the owning field-only test models directly.


class TestsFlextCliModelCommandsCov:
    """Behavioral contract of the public model-command helpers."""

    @staticmethod
    def test_model_command_rejects_invalid_data_with_validation_error() -> None:
        """A plain model command raises the ValidationError of rejected input."""
        command = cli.model_command(
            m.Tests.ModelCommandSample,
            lambda model: model.value,
        )

        with pytest.raises(m.ValidationError):
            command(name="invalid", value="not-an-int")

    # ---- model_command --------------------------------------------------

    @staticmethod
    def test_model_command_dispatches_to_handler_with_bound_model() -> None:
        """Verify that model command dispatches to handler with bound model."""

        def handler(model: m.Tests.ModelCommandSample) -> str:
            return f"{model.name}-{model.value}"

        cmd = cli.model_command(m.Tests.ModelCommandSample, handler)

        tm.that(cmd(name="x", value=3), eq="x-3")

    @staticmethod
    def test_model_command_applies_field_default_for_omitted_optional() -> None:
        """Verify that model command applies field default for omitted optional."""

        def handler(model: m.Tests.ModelCommandSample) -> int:
            return model.value

        cmd = cli.model_command(m.Tests.ModelCommandSample, handler)

        tm.that(cmd(name="y"), eq=42)

    @staticmethod
    def test_model_command_resolves_values_without_mutating_settings() -> None:
        # Invocation no longer writes parsed values back into the settings
        # model (commit f5f83dee): settings seeds option defaults only, and
        # resolved values reach the handler through the validated model.
        """Verify that model command resolves values without mutating settings."""
        settings = m.Tests.ModelCommandSample(name="from_settings", value=0)

        def handler(model: m.Tests.ModelCommandSample) -> str:
            return model.name

        cmd = cli.model_command(m.Tests.ModelCommandSample, handler, settings=settings)
        result = cmd(name="override", value=1)

        tm.that(result, eq="override")
        tm.that(settings.name, eq="from_settings")
        tm.that(settings.value, eq=0)

    @staticmethod
    def test_model_command_raises_validation_error_for_missing_required() -> None:
        """Verify that model command raises validation error for missing required."""

        def handler(model: m.Tests.ModelCommandRequired) -> str:
            return model.key

        cmd = cli.model_command(m.Tests.ModelCommandRequired, handler)

        with pytest.raises(m.ValidationError):
            cmd()

    @staticmethod
    def test_model_command_binds_all_required_fields_to_model() -> None:
        """Verify that model command binds all required fields to model."""

        def handler(model: m.Tests.ModelCommandRequired) -> str:
            return f"{model.key}={model.count}"

        cmd = cli.model_command(m.Tests.ModelCommandRequired, handler)

        tm.that(cmd(key="a", count=5), eq="a=5")

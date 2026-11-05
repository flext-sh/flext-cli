"""Behavioral tests for the public model-command DSL on ``cli``.

Covers the observable contract of ``cli.model_command``:
returned/validated model state, handler dispatch, settings-seeded defaults,
default resolution, and rejection of invalid or missing input. Every command
is registered in a real app and invoked through ``cli.invoke_app`` with
command-line arguments; the handler's result is observed through what it
captured and the invocation outcome. No private attribute access, no
internal-collaborator spying, no signature introspection.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests import c, m, p, tm, u

# NOTE (multi-agent, mro-wkii.17 / agent: make_ssot_audit): model-command
# coverage consumes the owning field-only test models directly.


class TestsFlextCliModelCommandsCov:
    """Behavioral contract of the public model-command helpers."""

    @staticmethod
    def test_model_command_rejects_invalid_data_with_validation_error() -> None:
        """A plain model command rejects invalid input before the handler runs."""
        returned: list[int] = []

        def handler(model: p.Tests.ModelCommandSample) -> int:
            returned.append(model.value)
            return model.value

        outcome = u.Tests.invoke_model_command(
            m.Tests.ModelCommandSample,
            handler,
            ["--name", "invalid", "--value", "not-an-int"],
        )

        tm.fail(u.Cli.process_succeeded(outcome.outcome))
        tm.that(outcome.stderr, has=["--value", "not-an-int"])
        tm.that(returned, empty=True)

    # ---- model_command --------------------------------------------------

    @staticmethod
    def test_model_command_dispatches_to_handler_with_bound_model() -> None:
        """Verify that model command dispatches to handler with bound model."""
        returned: list[str] = []

        def handler(model: p.Tests.ModelCommandSample) -> str:
            result = f"{model.name}-{model.value}"
            returned.append(result)
            return result

        outcome = u.Tests.invoke_model_command(
            m.Tests.ModelCommandSample,
            handler,
            ["--name", "x", "--value", "3"],
        )

        tm.ok(u.Cli.process_succeeded(outcome.outcome))
        tm.that(returned, eq=["x-3"])

    @staticmethod
    def test_model_command_applies_field_default_for_omitted_optional() -> None:
        """Verify that model command applies field default for omitted optional."""
        returned: list[int] = []

        def handler(model: p.Tests.ModelCommandSample) -> int:
            returned.append(model.value)
            return model.value

        outcome = u.Tests.invoke_model_command(
            m.Tests.ModelCommandSample,
            handler,
            ["--name", "y"],
        )

        tm.ok(u.Cli.process_succeeded(outcome.outcome))
        tm.that(returned, eq=[42])

    @staticmethod
    def test_model_command_resolves_values_without_mutating_settings() -> None:
        # Invocation no longer writes parsed values back into the settings
        # model (commit f5f83dee): settings seeds option defaults only, and
        # resolved values reach the handler through the validated model.
        """Verify that model command resolves values without mutating settings."""
        settings = m.Tests.ModelCommandSample(name="from_settings", value=0)
        returned: list[str] = []

        def handler(model: p.Tests.ModelCommandSample) -> str:
            returned.append(model.name)
            return model.name

        outcome = u.Tests.invoke_model_command(
            m.Tests.ModelCommandSample,
            handler,
            ["--name", c.MergeStrategy.OVERRIDE, "--value", "1"],
            settings=settings,
        )

        tm.ok(u.Cli.process_succeeded(outcome.outcome))
        tm.that(returned, eq=[c.MergeStrategy.OVERRIDE])
        tm.that(settings.name, eq="from_settings")
        tm.that(settings.value, eq=0)

    @staticmethod
    def test_model_command_raises_validation_error_for_missing_required() -> None:
        """Verify that model command rejects missing required options."""
        returned: list[str] = []

        def handler(model: p.Tests.ModelCommandRequired) -> str:
            returned.append(model.key)
            return model.key

        outcome = u.Tests.invoke_model_command(
            m.Tests.ModelCommandRequired,
            handler,
            [],
        )

        tm.fail(u.Cli.process_succeeded(outcome.outcome))
        tm.ok(u.Cli.cli_usage_error(outcome.stderr))
        tm.that(outcome.stderr, has="--key")
        tm.that(returned, empty=True)

    @staticmethod
    def test_model_command_binds_all_required_fields_to_model() -> None:
        """Verify that model command binds all required fields to model."""
        returned: list[str] = []

        def handler(model: p.Tests.ModelCommandRequired) -> str:
            result = f"{model.key}={model.count}"
            returned.append(result)
            return result

        outcome = u.Tests.invoke_model_command(
            m.Tests.ModelCommandRequired,
            handler,
            ["--key", "a", "--count", "5"],
        )

        tm.ok(u.Cli.process_succeeded(outcome.outcome))
        tm.that(returned, eq=["a=5"])

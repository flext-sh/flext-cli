"""FLEXT CLI Common Parameters Tests - behavioral contract of FlextCliCommonParams.

Exercises only the observable public contract: return values, ``r[T]`` outcomes,
raised exceptions, applied public model state, and CLI-runner output. No private
attribute/method access, no patching of internal collaborators.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import cli
from tests import c
from tests import p
from tests import t
from tests import u


class TestsFlextCliCliParams:
    """Behavioral tests for FlextCliCommonParams public contract."""

    @pytest.fixture
    def settings(self) -> p.Cli.Settings:
        """Fresh CLI settings instance built through the public factory."""
        result = u.Tests.create_test_settings()
        tm.ok(result)
        return result.value

    # ── create_option ────────────────────────────────────────────────

    @pytest.mark.parametrize("field_name", ["verbose", "quiet", "debug"])
    def test_create_option_returns_option_spec_for_registered_field(
        self, field_name: str
    ) -> None:
        """create_option yields a public CliOptionSpec for each registered field."""
        option = cli.create_option(field_name)
        tm.that(option, is_=p.Cli.CliOptionSpec)

    def test_create_option_raises_valueerror_for_unknown_field(self) -> None:
        """create_option rejects an unregistered field with a descriptive ValueError."""
        with pytest.raises(ValueError, match="not found") as exc_info:
            cli.create_option("nonexistent_field")
        tm.that(str(exc_info.value), has="nonexistent_field")

    # ── apply_to_config: success paths ───────────────────────────────

    def test_apply_to_config_applies_flags_and_log_level(
        self, settings: p.Cli.Settings
    ) -> None:
        """apply_to_config returns updated settings reflecting each applied value."""
        result = cli.apply_to_config(
            settings, verbose=True, debug=True, log_level=c.LogLevel.DEBUG
        )

        tm.ok(result)
        updated = result.value
        tm.that(updated.cli_verbose is True, eq=True)
        tm.that(updated.debug is True, eq=True)
        tm.that(updated.cli_log_level, eq=c.LogLevel.DEBUG)

    def test_apply_to_config_trace_with_debug_enables_trace(
        self, settings: p.Cli.Settings
    ) -> None:
        """Trace is accepted and applied when debug is also enabled."""
        result = cli.apply_to_config(settings, debug=True, trace=True)

        tm.ok(result)
        updated = result.value
        tm.that(updated.debug is True, eq=True)
        tm.that(updated.trace is True, eq=True)

    def test_apply_to_config_is_idempotent_for_same_values(
        self, settings: p.Cli.Settings
    ) -> None:
        """Applying the same values twice yields the same observable state."""
        first = cli.apply_to_config(settings, verbose=True, log_level=c.LogLevel.DEBUG)
        tm.ok(first)
        second = cli.apply_to_config(
            first.value, verbose=True, log_level=c.LogLevel.DEBUG
        )
        tm.ok(second)
        tm.that(second.value.cli_verbose is True, eq=True)
        tm.that(second.value.cli_log_level, eq=c.LogLevel.DEBUG)

    # ── apply_to_config: failure paths ───────────────────────────────

    def test_apply_to_config_trace_without_debug_fails(
        self, settings: p.Cli.Settings
    ) -> None:
        """Trace without debug fails with a message explaining the dependency."""
        result = cli.apply_to_config(settings, trace=True)

        tm.fail(result)
        tm.that((result.error or "").lower(), has="trace mode requires debug mode")

    @pytest.mark.parametrize(
        ("field_name", "expected_fragments"),
        [
            ("log_level", ("invalid", "log level")),
            ("log_format", ("invalid", "log format")),
            ("output_format", ("invalid", "output format")),
        ],
    )
    def test_apply_to_config_rejects_invalid_enum_value(
        self,
        settings: p.Cli.Settings,
        field_name: str,
        expected_fragments: tuple[str, str],
    ) -> None:
        """Each choice-bound field rejects an out-of-domain value with a clear error."""
        match field_name:
            case "log_level":
                result = cli.apply_to_config(settings, log_level="INVALID")
            case "log_format":
                result = cli.apply_to_config(settings, log_format="INVALID")
            case _:
                result = cli.apply_to_config(settings, output_format="INVALID")

        tm.fail(result)
        error_msg = (result.error or "").lower()
        for fragment in expected_fragments:
            tm.that(error_msg, has=fragment)

    # ── decorator wiring: observable CLI behavior ────────────────────

    @pytest.fixture
    def runner_and_app(self) -> tuple[t.Cli.TyperRunner, t.Cli.CliApp]:
        """Build a CLI runner plus an app carrying the common-params decorated command."""
        app_result = u.Tests.create_cli_app()
        tm.ok(app_result)
        app = app_result.value
        tm.ok(u.Tests.create_decorated_command(app, "test"))
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        return runner_result.value, app

    def test_help_exposes_common_options(
        self, runner_and_app: tuple[t.Cli.TyperRunner, t.Cli.CliApp]
    ) -> None:
        """--help lists every common parameter the decorator promises to add."""
        runner, app = runner_and_app
        result = runner.invoke(app, ["test", "--help"])

        tm.that(result.exit_code, eq=0)
        for flag in ("--verbose", "--debug", "--log-level", "--output-format"):
            tm.that(result.stdout, has=flag)

    def test_boolean_flags_toggle_command_behavior(
        self, runner_and_app: tuple[t.Cli.TyperRunner, t.Cli.CliApp]
    ) -> None:
        """Passing --verbose/--debug flips the command's observable output."""
        runner, app = runner_and_app
        result = runner.invoke(app, ["test", "--verbose", "--debug"])

        tm.that(result.exit_code, eq=0)
        tm.that(result.stdout, has="Verbose: enabled")
        tm.that(result.stdout, has="Debug: enabled")

    def test_value_parameters_flow_to_command(
        self, runner_and_app: tuple[t.Cli.TyperRunner, t.Cli.CliApp]
    ) -> None:
        """Choice-valued options are parsed and surfaced in command output."""
        runner, app = runner_and_app
        result = runner.invoke(
            app,
            [
                "test",
                "--log-level",
                c.LogLevel.WARNING,
                "--output-format",
                c.Cli.OutputFormats.JSON,
            ],
        )

        tm.that(result.exit_code, eq=0)
        tm.that(result.stdout, has="Log level: WARNING")
        tm.that(result.stdout, has="Output format: json")

"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tests import tm
from tests import c
from tests import m

from flext_cli import cli

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.
# mro-wkii.17.26 (codex): exercise CLI flows through the public invocation facade.

from collections.abc import MutableSequence

from tests import t



class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    def test_model_command_validates_runtime_settings_fields(self) -> None:
        """Validate runtime CLI parameters through the model command."""
        command_settings = m.Cli.CliParamsConfig()

        def handle(params: m.Cli.CliParamsConfig) -> t.JsonValue:
            return params.debug is True

        command = cli.model_command(
            m.Cli.CliParamsConfig, handle, settings=command_settings
        )
        result = command(debug=True)

        tm.that(result, eq=True)

    def test_create_app_with_common_params_accepts_debug_flag(self) -> None:
        """Accept the public debug flag through a real CLI invocation."""
        app = cli.create_app_with_common_params(
            name="sample", help_text="Sample application"
        )
        cli.register_command(
            app, name="inspect", help_text="Inspect settings", command=lambda: True
        )

        result = cli.invoke_app(app, args=("--debug", "inspect"))

        tm.ok(result)
        invocation = result.value
        tm.that(invocation.exit_code, eq=0)

    def test_create_app_with_common_params_accepts_log_level_flag(self) -> None:
        """Accept an explicit log level through a real CLI invocation."""
        app = cli.create_app_with_common_params(
            name="sample", help_text="Sample application"
        )
        cli.register_command(
            app, name="inspect", help_text="Inspect settings", command=lambda: True
        )

        result = cli.invoke_app(app, args=("--log-level", c.LogLevel.DEBUG, "inspect"))

        tm.ok(result)
        invocation = result.value
        tm.that(invocation.exit_code, eq=0)

    def test_model_command_generates_real_typer_options(self) -> None:
        """Generate and execute real Typer options from the request model."""
        captured: MutableSequence[p.Tests.SampleInput] = []
        app = cli.create_app_with_common_params(
            name="root", help_text="Root application"
        )
        group = cli.create_group(help_text="Sample group", name="sample")

        def handle(params: m.Tests.SampleInput) -> t.JsonValue:
            captured.append(params)
            return True

        command = cli.model_command(m.Tests.SampleInput, handle)
        cli.register_command(
            group, name="run", help_text="Run sample command", command=command
        )
        cli.add_group(app, name="sample", group=group)
        help_result = cli.invoke_app(app, args=("sample", "run", "--help"))
        exec_result = cli.invoke_app(
            app,
            args=(
                "sample",
                "run",
                "--name",
                "alice",
                "--count",
                "3",
                "--dry-run",
                "--output-format",
                c.Cli.OutputFormats.JSON,
            ),
        )

        tm.ok(help_result)
        tm.ok(exec_result)
        help_invocation = help_result.value
        exec_invocation = exec_result.value
        tm.that(help_invocation.exit_code, eq=0)
        tm.that(help_invocation.stdout, has="Target name")
        tm.that(help_invocation.stdout, has="Dry-run mode")
        tm.that(exec_invocation.exit_code, eq=0)
        tm.that(len(captured), eq=1)
        tm.that(captured[0].name, eq="alice")
        tm.that(captured[0].count, eq=3)
        tm.that(captured[0].dry_run, eq=True)
        tm.that(captured[0].output_format, eq=c.Cli.OutputFormats.JSON)


__all__: list[str] = ["TestsFlextCliService"]

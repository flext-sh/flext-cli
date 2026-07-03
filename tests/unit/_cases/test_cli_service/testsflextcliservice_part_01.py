"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from collections.abc import (
    MutableSequence,
)

from flext_tests import tm
from tests.constants import c
from tests.models import m
from tests.typings import t

from flext_cli import cli


class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    def test_model_command_updates_runtime_settings_fields(self) -> None:
        class RuntimeSettings(m.BaseModel):
            debug: bool = False

        settings = RuntimeSettings()

        def handle(params: m.Cli.CliParamsConfig) -> t.JsonValue:
            return params.debug is True

        command = cli.model_command(m.Cli.CliParamsConfig, handle, settings=settings)
        result = command(debug=True)

        tm.that(result, eq=True)
        tm.that(settings.debug, eq=True)

    def test_create_app_with_common_params_applies_settings(self) -> None:
        app = cli.create_app_with_common_params(
            name="sample",
            help_text="Sample application",
            settings=cli.settings,
        )
        cli.register_command(
            app,
            name="inspect",
            help_text="Inspect settings",
            command=lambda: True,
        )

        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        result = runner_result.value.invoke(app, ["--debug", "inspect"])

        tm.that(result.exit_code, eq=0)
        tm.that(cli.settings.debug, eq=True)

    def test_create_app_with_common_params_applies_log_level(self) -> None:
        app = cli.create_app_with_common_params(
            name="sample",
            help_text="Sample application",
            settings=cli.settings,
        )
        cli.register_command(
            app,
            name="inspect",
            help_text="Inspect settings",
            command=lambda: True,
        )

        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        result = runner_result.value.invoke(
            app,
            ["--log-level", c.LogLevel.DEBUG, "inspect"],
        )

        tm.that(result.exit_code, eq=0)
        tm.that(cli.settings.Cli.cli_log_level, eq=c.LogLevel.DEBUG)

    def test_model_command_generates_real_typer_options(self) -> None:
        captured: MutableSequence[m.Tests.SampleInput] = []
        app = cli.create_app_with_common_params(
            name="root",
            help_text="Root application",
            settings=cli.settings,
        )
        group = cli.create_group(help_text="Sample group", name="sample")

        def handle(params: m.Tests.SampleInput) -> t.JsonValue:
            captured.append(params)
            return True

        command = cli.model_command(m.Tests.SampleInput, handle)
        cli.register_command(
            group,
            name="run",
            help_text="Run sample command",
            command=command,
        )
        cli.add_group(app, name="sample", group=group)
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        help_result = runner_result.value.invoke(app, ["sample", "run", "--help"])
        exec_result = runner_result.value.invoke(
            app,
            [
                "sample",
                "run",
                "--name",
                "alice",
                "--count",
                "3",
                "--dry-run",
                "--output-format",
                c.Cli.OutputFormats.JSON,
            ],
        )

        tm.that(help_result.exit_code, eq=0)
        tm.that(help_result.stdout, has="Target name")
        tm.that(help_result.stdout, has="Dry-run mode")
        tm.that(exec_result.exit_code, eq=0)
        tm.that(len(captured), eq=1)
        tm.that(captured[0].name, eq="alice")
        tm.that(captured[0].count, eq=3)
        tm.that(captured[0].dry_run, eq=True)
        tm.that(captured[0].output_format, eq=c.Cli.OutputFormats.JSON)


__all__: list[str] = ["TestsFlextCliService"]

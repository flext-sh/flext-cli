"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from typing import Annotated, Literal

from flext_core import r
from flext_tests import tm
from pydantic import BaseModel, Field

from flext_cli import cli


class _SampleInput(BaseModel):
    """Small request model for exercising model-driven CLI generation."""

    name: Annotated[str, Field(description="Target name")]
    count: Annotated[int, Field(default=1, description="How many times")]
    dry_run: Annotated[bool, Field(default=False, description="Dry-run mode")]
    output_format: Annotated[
        Literal["json", "table"],
        Field(default="table", description="Output format"),
    ]


class TestsCliService:
    """Covers the restored Typer-facing public API."""

    def test_create_app_with_common_params_applies_settings(self) -> None:
        app = cli.create_app_with_common_params(
            name="sample",
            help_text="Sample application",
            config=cli.settings,
        )
        cli.register_command(
            app,
            name="inspect",
            help_text="Inspect settings",
            command=lambda: None,
        )

        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        result = runner_result.value.invoke(app, ["--debug", "inspect"])

        tm.that(result.exit_code, eq=0)
        tm.that(cli.settings.debug, eq=True)

    def test_model_command_generates_real_typer_options(self) -> None:
        captured: list[_SampleInput] = []
        app = cli.create_app_with_common_params(
            name="root",
            help_text="Root application",
            config=cli.settings,
        )
        group = cli.create_group(help_text="Sample group", name="sample")

        def handle(params: _SampleInput) -> None:
            captured.append(params)

        command = cli.model_command(_SampleInput, handle)
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
                "json",
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
        tm.that(captured[0].output_format, eq="json")

    def test_execute_app_returns_user_facing_failure_message(self) -> None:
        app = cli.create_group(help_text="Failure group")

        def fail_handler(_params: _SampleInput) -> None:
            cli.exit(code=1)

        cli.register_command(
            app,
            name="fail",
            help_text="Fail intentionally",
            command=cli.model_command(_SampleInput, fail_handler),
        )
        result = cli.execute_app(
            app,
            prog_name="sample",
            args=["fail", "--name", "alice"],
            error_message=lambda: "expected cli failure",
        )

        tm.fail(result)
        tm.that(result.error, eq="expected cli failure")

    def test_register_result_command_renders_success_and_failure(self) -> None:
        app = cli.create_app_with_common_params(
            name="result-app",
            help_text="Result application",
            config=cli.settings,
        )
        remembered: list[tuple[str | None, str]] = []

        def remember_failure(error: str | None, fallback: str) -> None:
            remembered.append((error, fallback))

        def ok_handler(params: _SampleInput) -> r[str]:
            return r[str].ok(f"processed {params.name}")

        def fail_handler(_params: _SampleInput) -> r[str]:
            return r[str].fail("boom")

        cli.register_result_command(
            app,
            name="ok",
            help_text="Successful command",
            model_cls=_SampleInput,
            handler=ok_handler,
            success_formatter=lambda value: value,
            failure_message="ok failed",
            remember_failure=remember_failure,
        )
        cli.register_result_command(
            app,
            name="fail",
            help_text="Failing command",
            model_cls=_SampleInput,
            handler=fail_handler,
            failure_message="failure fallback",
            remember_failure=remember_failure,
        )
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        ok_result = runner_result.value.invoke(app, ["ok", "--name", "alice"])
        fail_result = runner_result.value.invoke(app, ["fail", "--name", "alice"])

        tm.that(ok_result.exit_code, eq=0)
        tm.that(ok_result.stdout, has="processed alice")
        tm.that(fail_result.exit_code, eq=1)
        tm.that(remembered, eq=[("boom", "failure fallback")])

"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from collections.abc import MutableSequence

from flext_tests import tm

from flext_cli import cli
from flext_core import r
from tests import m


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
        captured: MutableSequence[m.Cli.Tests.SampleInput] = []
        app = cli.create_app_with_common_params(
            name="root",
            help_text="Root application",
            config=cli.settings,
        )
        group = cli.create_group(help_text="Sample group", name="sample")

        def handle(params: m.Cli.Tests.SampleInput) -> None:
            captured.append(params)

        command = cli.model_command(m.Cli.Tests.SampleInput, handle)
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

    def test_model_command_accepts_repeatable_list_options(self) -> None:
        captured: MutableSequence[m.Cli.Tests.RepeatableInput] = []
        app = cli.create_app_with_common_params(
            name="root",
            help_text="Root application",
            config=cli.settings,
        )
        group = cli.create_group(help_text="Sample group", name="sample")

        def handle(params: m.Cli.Tests.RepeatableInput) -> None:
            captured.append(params)

        command = cli.model_command(m.Cli.Tests.RepeatableInput, handle)
        cli.register_command(
            group,
            name="repeat",
            help_text="Run repeatable option command",
            command=command,
        )
        cli.add_group(app, name="sample", group=group)
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        exec_result = runner_result.value.invoke(
            app,
            [
                "sample",
                "repeat",
                "--make-arg",
                "FILES=a b c.py",
                "--make-arg",
                "VERBOSE=1",
            ],
        )

        tm.that(exec_result.exit_code, eq=0)
        tm.that(len(captured), eq=1)
        tm.that(captured[0].make_arg, eq=["FILES=a b c.py", "VERBOSE=1"])

    def test_execute_app_returns_user_facing_failure_message(self) -> None:
        app = cli.create_group(help_text="Failure group")

        def fail_handler(_params: m.Cli.Tests.SampleInput) -> None:
            cli.exit(code=1)

        cli.register_command(
            app,
            name="fail",
            help_text="Fail intentionally",
            command=cli.model_command(m.Cli.Tests.SampleInput, fail_handler),
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
        group = cli.create_group(help_text="Grouped commands", name="group")
        remembered: MutableSequence[tuple[str | None, str]] = []

        def remember_failure(error: str | None, fallback: str) -> None:
            remembered.append((error, fallback))

        def ok_handler(params: m.Cli.Tests.SampleInput) -> r[m.Cli.Tests.SampleOutput]:
            return r[m.Cli.Tests.SampleOutput].ok(
                m.Cli.Tests.SampleOutput(message=f"processed {params.name}")
            )

        def fail_handler(
            params: m.Cli.Tests.SampleInput,
        ) -> r[m.Cli.Tests.SampleOutput]:
            _ = params
            return r[m.Cli.Tests.SampleOutput].fail("boom")

        def build_ok_route() -> m.Cli.Tests.SampleRoute:
            return m.Cli.Tests.SampleRoute(
                name="ok",
                help_text="Successful command",
                model_cls=m.Cli.Tests.SampleInput,
                handler=ok_handler,
                failure_message="ok failed",
            )

        def build_fail_route() -> m.Cli.Tests.SampleRoute:
            return m.Cli.Tests.SampleRoute(
                name="fail",
                help_text="Failing command",
                model_cls=m.Cli.Tests.SampleInput,
                handler=fail_handler,
                failure_message="failure fallback",
            )

        cli.register_result_route(
            app,
            route=build_ok_route(),
            remember_failure=remember_failure,
        )
        cli.register_result_route(
            group,
            route=build_fail_route(),
            remember_failure=remember_failure,
        )
        cli.add_group(app, name="group", group=group)
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        ok_result = runner_result.value.invoke(app, ["ok", "--name", "alice"])
        fail_result = runner_result.value.invoke(
            app,
            ["group", "fail", "--name", "alice"],
        )

        tm.that(ok_result.exit_code, eq=0)
        tm.that(ok_result.stdout, has="processed alice")
        tm.that(fail_result.exit_code, eq=1)
        tm.that(fail_result.stdout, has="boom")
        tm.that(remembered, eq=[("boom", "failure fallback")])

    def test_register_result_routes_preserves_failure_metadata(self) -> None:
        app = cli.create_app_with_common_params(
            name="result-app",
            help_text="Result application",
            config=cli.settings,
        )
        remembered: MutableSequence[tuple[str | None, str]] = []

        def remember_failure(error: str | None, fallback: str) -> None:
            remembered.append((error, fallback))

        def fail_handler(
            params: m.Cli.Tests.SampleInput,
        ) -> r[m.Cli.Tests.SampleOutput]:
            _ = params
            return r[m.Cli.Tests.SampleOutput].fail("batched boom")

        cli.register_result_routes(
            app,
            [
                m.Cli.Tests.SampleRoute(
                    name="fail",
                    help_text="Failing command",
                    model_cls=m.Cli.Tests.SampleInput,
                    handler=fail_handler,
                    failure_message="batched failure fallback",
                )
            ],
            remember_failure=remember_failure,
        )
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        fail_result = runner_result.value.invoke(app, ["fail", "--name", "alice"])

        tm.that(fail_result.exit_code, eq=1)
        tm.that(fail_result.stdout, has="batched boom")
        tm.that(remembered, eq=[("batched boom", "batched failure fallback")])

"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from collections.abc import (
    MutableSequence,
)

from flext_tests import tm

from flext_cli import cli
from tests import c, m, p, r, t


class TestsCliService:
    """Covers the restored Typer-facing public API."""

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

    def test_model_command_generates_real_typer_options(self) -> None:
        captured: MutableSequence[m.Cli.Tests.SampleInput] = []
        app = cli.create_app_with_common_params(
            name="root",
            help_text="Root application",
            settings=cli.settings,
        )
        group = cli.create_group(help_text="Sample group", name="sample")

        def handle(params: m.Cli.Tests.SampleInput) -> t.JsonValue:
            captured.append(params)
            return True

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

    def test_model_command_accepts_repeatable_list_options(self) -> None:
        captured: MutableSequence[m.Cli.Tests.RepeatableInput] = []
        app = cli.create_app_with_common_params(
            name="root",
            help_text="Root application",
            settings=cli.settings,
        )
        group = cli.create_group(help_text="Sample group", name="sample")

        def handle(params: m.Cli.Tests.RepeatableInput) -> t.JsonValue:
            captured.append(params)
            return True

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

    def test_model_command_returns_handler_value(self) -> None:
        def handle(params: m.Cli.Tests.SampleInput) -> t.JsonValue:
            return {
                "name": params.name,
                "count": params.count,
                "dry_run": params.dry_run,
                "output_format": params.output_format,
            }

        command = cli.model_command(m.Cli.Tests.SampleInput, handle)
        result = command(
            name="alice",
            count=3,
            dry_run=True,
            output_format=c.Cli.OutputFormats.JSON,
        )

        tm.that(
            result,
            eq={
                "name": "alice",
                "count": 3,
                "dry_run": True,
                "output_format": c.Cli.OutputFormats.JSON,
            },
        )

    def test_execute_app_prefers_real_failure_message(self) -> None:
        app = cli.create_app_with_common_params(
            name="sample",
            help_text="Failure group",
            settings=cli.settings,
        )
        group = cli.create_group(help_text="Grouped failure commands", name="group")

        def fail_handler(_params: m.Cli.Tests.SampleInput) -> t.JsonValue:
            cli.exit(code=1)
            return True

        cli.register_command(
            group,
            name="fail",
            help_text="Fail intentionally",
            command=cli.model_command(m.Cli.Tests.SampleInput, fail_handler),
        )
        cli.add_group(app, name="group", group=group)
        result = cli.execute_app(
            app,
            prog_name="sample",
            args=["group", "fail", "--name", "alice"],
        )

        tm.fail(result)
        tm.that(result.error, has="CLI exited with code 1")

    def test_execute_app_preserves_click_usage_errors(self) -> None:
        app = cli.create_app_with_common_params(
            name="sample",
            help_text="Failure group",
            settings=cli.settings,
        )
        group = cli.create_group(help_text="Grouped failure commands", name="group")

        cli.register_command(
            group,
            name="ok",
            help_text="Successful command",
            command=lambda: True,
        )
        cli.add_group(app, name="group", group=group)

        result = cli.execute_app(
            app,
            prog_name="sample",
            args=["group", "missing-command"],
        )

        tm.fail(result)
        tm.that(result.error, has="No such command 'missing-command'")

    def test_register_result_command_renders_success_and_failure(self) -> None:
        app = cli.create_app_with_common_params(
            name="result-app",
            help_text="Result application",
            settings=cli.settings,
        )
        group = cli.create_group(help_text="Grouped commands", name="group")

        def ok_handler(
            params: m.Cli.Tests.SampleInput,
        ) -> p.Result[m.Cli.Tests.SampleOutput]:
            return r[m.Cli.Tests.SampleOutput].ok(
                m.Cli.Tests.SampleOutput(message=f"processed {params.name}")
            )

        def fail_handler(
            params: m.Cli.Tests.SampleInput,
        ) -> p.Result[m.Cli.Tests.SampleOutput]:
            _ = params
            return r[m.Cli.Tests.SampleOutput].fail("boom")

        def build_ok_route() -> m.Cli.Tests.SampleRoute:
            return m.Cli.Tests.SampleRoute(
                name="ok",
                help_text="Successful command",
                model_cls=m.Cli.Tests.SampleInput,
                handler=ok_handler,
            )

        def build_fail_route() -> m.Cli.Tests.SampleRoute:
            return m.Cli.Tests.SampleRoute(
                name="fail",
                help_text="Failing command",
                model_cls=m.Cli.Tests.SampleInput,
                handler=fail_handler,
            )

        cli.register_result_route(app, route=build_ok_route())
        cli.register_result_route(group, route=build_fail_route())
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

    def test_register_result_routes_propagates_real_failure(self) -> None:
        app = cli.create_app_with_common_params(
            name="result-app",
            help_text="Result application",
            settings=cli.settings,
        )

        def fail_handler(
            params: m.Cli.Tests.SampleInput,
        ) -> p.Result[m.Cli.Tests.SampleOutput]:
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
                )
            ],
        )
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        fail_result = runner_result.value.invoke(app, ["fail", "--name", "alice"])

        tm.that(fail_result.exit_code, eq=1)
        tm.that(fail_result.stdout, has="batched boom")

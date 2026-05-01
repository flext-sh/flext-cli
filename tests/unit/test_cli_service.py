"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from collections.abc import (
    MutableSequence,
)

import pytest
import typer
from flext_tests import tm

import flext_cli.services.cli as cli_module
from flext_cli import FlextCliSettings, cli
from tests import c, m, p, r, t


class TestsFlextCliService:
    """Covers the restored Typer-facing public API."""

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
        tm.that(cli.settings.cli_log_level, eq=c.LogLevel.DEBUG)

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

    def test_model_command_accepts_repeatable_list_options(self) -> None:
        captured: MutableSequence[m.Tests.RepeatableInput] = []
        app = cli.create_app_with_common_params(
            name="root",
            help_text="Root application",
            settings=cli.settings,
        )
        group = cli.create_group(help_text="Sample group", name="sample")

        def handle(params: m.Tests.RepeatableInput) -> t.JsonValue:
            captured.append(params)
            return True

        command = cli.model_command(m.Tests.RepeatableInput, handle)
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
        def handle(params: m.Tests.SampleInput) -> t.JsonValue:
            return {
                "name": params.name,
                "count": params.count,
                "dry_run": params.dry_run,
                "output_format": params.output_format,
            }

        command = cli.model_command(m.Tests.SampleInput, handle)
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

    def test_model_command_uses_custom_param_decls_from_field_extra(self) -> None:
        class CustomDeclModel(m.BaseModel):
            flag: bool = m.Field(
                False,
                validate_default=True,
                description="Custom flag",
                json_schema_extra={"typer_param_decls": ["-f", "--flaggy"]},
            )

        app = cli.create_app_with_common_params(
            name="decl-app",
            help_text="Decl app",
            settings=cli.settings,
        )
        cli.register_command(
            app,
            name="run",
            help_text="Run",
            command=cli.model_command(CustomDeclModel, lambda _params: True),
        )
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        help_result = runner_result.value.invoke(app, ["run", "--help"])

        tm.that(help_result.exit_code, eq=0)
        tm.that(help_result.stdout, has="--flaggy")

    def test_model_command_skips_excluded_fields(self) -> None:
        class ExcludedFieldModel(m.BaseModel):
            visible: str = m.Field(description="Visible")
            hidden: str = m.Field("secret", exclude=True, validate_default=True)

        app = cli.create_app_with_common_params(
            name="exclude-app",
            help_text="Exclude app",
            settings=cli.settings,
        )
        cli.register_command(
            app,
            name="run",
            help_text="Run",
            command=cli.model_command(ExcludedFieldModel, lambda _params: True),
        )
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        help_result = runner_result.value.invoke(app, ["run", "--help"])

        tm.that(help_result.exit_code, eq=0)
        tm.that(help_result.stdout, has="--visible")
        tm.that("--hidden" in help_result.stdout, eq=False)

    def test_create_app_with_common_params_handles_apply_failure(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        warning_records: list[str] = []
        warning_message = "failed to apply cli params"

        monkeypatch.setattr(
            cli_module.FlextCliCommonParams,
            "apply_to_config",
            lambda *_args, **_kwargs: r[FlextCliSettings].fail("apply failure"),
        )
        monkeypatch.setattr(
            cli.logger,
            "warning",
            lambda message, **_kwargs: warning_records.append(message),
        )

        app = cli.create_app_with_common_params(
            name="warn-app",
            help_text="Warn app",
            settings=cli.settings,
        )
        cli.register_command(app, name="ok", help_text="OK", command=lambda: True)

        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        invoke_result = runner_result.value.invoke(app, ["--debug", "ok"])

        tm.that(invoke_result.exit_code, eq=0)
        tm.that(warning_records, has=[warning_message])

    def test_create_app_with_common_params_handles_identity_update(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        monkeypatch.setattr(
            cli_module.FlextCliCommonParams,
            "apply_to_config",
            lambda settings, **_kwargs: r[FlextCliSettings].ok(settings),
        )

        app = cli.create_app_with_common_params(
            name="identity-app",
            help_text="Identity app",
            settings=cli.settings,
        )
        cli.register_command(app, name="ok", help_text="OK", command=lambda: True)

        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        invoke_result = runner_result.value.invoke(app, ["--debug", "ok"])

        tm.that(invoke_result.exit_code, eq=0)

    def test_derive_model_merges_sources_and_overrides(self) -> None:
        model_from_mapping = {"name": "alice", "count": 2}
        model_from_instance = m.Tests.SampleInput(
            name="bob",
            count=7,
            dry_run=True,
            output_format=c.Cli.OutputFormats.JSON,
        )

        derived = cli.derive_model(
            m.Tests.SampleInput,
            model_from_mapping,
            model_from_instance,
            overrides={"name": "carol", "count": 9},
        )

        tm.that(derived.name, eq="carol")
        tm.that(derived.count, eq=9)
        tm.that(derived.dry_run, eq=True)

    def test_execute_app_handles_abort_exception(self) -> None:
        app = cli.create_app_with_common_params(
            name="abort-app",
            help_text="Abort app",
            settings=cli.settings,
        )
        cli.register_command(
            app,
            name="abort",
            help_text="Abort command",
            command=lambda: (_ for _ in ()).throw(typer.Abort()),
        )

        result = cli.execute_app(app, prog_name="abort-app", args=["abort"])

        tm.fail(result)
        tm.that(result.error, has="Abort")

    def test_execute_app_handles_unexpected_exception(self) -> None:
        app = cli.create_app_with_common_params(
            name="error-app",
            help_text="Error app",
            settings=cli.settings,
        )
        cli.register_command(
            app,
            name="boom",
            help_text="Boom command",
            command=lambda: (_ for _ in ()).throw(ValueError("boom")),
        )

        result = cli.execute_app(app, prog_name="error-app", args=["boom"])

        tm.fail(result)
        tm.that(result.error, has="boom")

    def test_execute_app_handles_nonzero_int_result(self) -> None:
        app = cli.create_app_with_common_params(
            name="int-app",
            help_text="Int app",
            settings=cli.settings,
        )
        cli.register_command(
            app, name="return-two", help_text="Return int", command=lambda: 2
        )

        result = cli.execute_app(app, prog_name="int-app", args=["return-two"])

        tm.fail(result)
        tm.that(result.error, has="CLI exited with code 2")

    def test_execute_app_handles_typer_exit_nonzero_branch(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        class ExitCommand:
            @staticmethod
            def main(**_kwargs: object) -> t.JsonValue:
                raise typer.Exit(code=1)

        monkeypatch.setattr(typer.main, "get_command", lambda _app: ExitCommand())
        app = cli.create_app_with_common_params(
            name="exit-app",
            help_text="Exit app",
            settings=cli.settings,
        )

        result = cli.execute_app(app, prog_name="exit-app", args=[])

        tm.fail(result)
        tm.that(result.error, has="CLI exited with code 1")

    def test_execute_app_returns_ok_for_zero_int_result(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        class ZeroCommand:
            @staticmethod
            def main(**_kwargs: object) -> t.JsonValue:
                return 0

        monkeypatch.setattr(typer.main, "get_command", lambda _app: ZeroCommand())
        app = cli.create_app_with_common_params(
            name="zero-app",
            help_text="Zero app",
            settings=cli.settings,
        )

        result = cli.execute_app(app, prog_name="zero-app", args=[])

        tm.ok(result)

    def test_execute_app_prefers_real_failure_message(self) -> None:
        app = cli.create_app_with_common_params(
            name="sample",
            help_text="Failure group",
            settings=cli.settings,
        )
        group = cli.create_group(help_text="Grouped failure commands", name="group")

        def fail_handler(_params: m.Tests.SampleInput) -> t.JsonValue:
            cli.exit(code=1)
            return True

        cli.register_command(
            group,
            name="fail",
            help_text="Fail intentionally",
            command=cli.model_command(m.Tests.SampleInput, fail_handler),
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
            params: m.Tests.SampleInput,
        ) -> p.Result[m.Tests.SampleOutput]:
            return r[m.Tests.SampleOutput].ok(
                m.Tests.SampleOutput(message=f"processed {params.name}")
            )

        def fail_handler(
            params: m.Tests.SampleInput,
        ) -> p.Result[m.Tests.SampleOutput]:
            _ = params
            return r[m.Tests.SampleOutput].fail("boom")

        def build_ok_route() -> m.Tests.SampleRoute:
            return m.Tests.SampleRoute(
                name="ok",
                help_text="Successful command",
                model_cls=m.Tests.SampleInput,
                handler=ok_handler,
            )

        def build_fail_route() -> m.Tests.SampleRoute:
            return m.Tests.SampleRoute(
                name="fail",
                help_text="Failing command",
                model_cls=m.Tests.SampleInput,
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
            params: m.Tests.SampleInput,
        ) -> p.Result[m.Tests.SampleOutput]:
            _ = params
            return r[m.Tests.SampleOutput].fail("batched boom")

        cli.register_result_routes(
            app,
            [
                m.Tests.SampleRoute(
                    name="fail",
                    help_text="Failing command",
                    model_cls=m.Tests.SampleInput,
                    handler=fail_handler,
                )
            ],
        )
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        fail_result = runner_result.value.invoke(app, ["fail", "--name", "alice"])

        tm.that(fail_result.exit_code, eq=1)
        tm.that(fail_result.stdout, has="batched boom")

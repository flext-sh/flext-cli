"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from flext_tests import tm
from tests import c
from tests import m

from flext_cli import cli, settings

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.
# NOTE (multi-agent, mro-wkii.17 / agent: make_ssot_audit): derive_model tests
# compose canonical source models without JSON-shaped intermediaries.


class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    def test_model_command_skips_excluded_fields(self) -> None:
        class ExcludedFieldModel(m.BaseModel):
            visible: str = m.Field(..., description="Visible", validate_default=True)
            hidden: str = m.Field("secret", exclude=True, validate_default=True)

        app = cli.create_app_with_common_params(
            name="exclude-app", help_text="Exclude app"
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

    def test_create_app_with_common_params_handles_invalid_trace_without_debug(
        self,
    ) -> None:
        app = cli.create_app_with_common_params(name="warn-app", help_text="Warn app")
        cli.register_command(app, name="ok", help_text="OK", command=lambda: True)

        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        invoke_result = runner_result.value.invoke(app, ["--trace", "ok"])

        tm.that(invoke_result.exit_code, eq=0)
        tm.that(settings.trace, eq=False)

    def test_create_app_with_common_params_no_flags_keeps_settings(self) -> None:
        app = cli.create_app_with_common_params(
            name="identity-app", help_text="Identity app"
        )
        cli.register_command(app, name="ok", help_text="OK", command=lambda: True)

        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        invoke_result = runner_result.value.invoke(app, ["ok"])

        tm.that(invoke_result.exit_code, eq=0)
        tm.that(settings.debug, eq=False)

    def test_create_cli_runner_fails_loud_for_unsupported_echo_stdin(self) -> None:
        result = cli.create_cli_runner(echo_stdin=True)

        tm.fail(result)
        tm.that(result.error, has=c.Cli.ERR_CLI_RUNNER_ECHO_STDIN_UNSUPPORTED)

    def test_derive_model_merges_canonical_model_sources(self) -> None:
        first_source = m.Tests.SampleInputPatch(name="alice", count=2)
        model_from_instance = m.Tests.SampleInput(
            name="bob", count=7, dry_run=True, output_format=c.Cli.OutputFormats.JSON
        )
        final_source = m.Tests.SampleInputPatch(name="carol", count=9)

        derived = cli.derive_model(
            m.Tests.SampleInput, first_source, model_from_instance, final_source
        )

        tm.that(derived.name, eq="carol")
        tm.that(derived.count, eq=9)
        tm.that(derived.dry_run, eq=True)

    def test_execute_app_handles_abort_exception(self) -> None:
        app = cli.create_app_with_common_params(name="abort-app", help_text="Abort app")
        cli.register_command(
            app,
            name="abort",
            help_text="Abort command",
            command=lambda: (_ for _ in ()).throw(c.Cli.CliAbortError()),
        )

        result = cli.execute_app(app, prog_name="abort-app", args=["abort"])

        tm.fail(result)
        tm.that(result.error, has="Abort")

    def test_execute_app_handles_unexpected_exception(self) -> None:
        app = cli.create_app_with_common_params(name="error-app", help_text="Error app")
        cli.register_command(
            app,
            name="boom",
            help_text="Boom command",
            command=lambda: (_ for _ in ()).throw(ValueError("boom")),
        )

        result = cli.execute_app(app, prog_name="error-app", args=["boom"])

        tm.fail(result)
        tm.that(result.error, has="boom")


__all__: list[str] = ["TestsFlextCliService"]

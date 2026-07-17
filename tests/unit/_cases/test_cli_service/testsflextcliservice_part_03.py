"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from flext_tests import tm
from tests import c, m

from flext_cli import cli, settings

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.
# NOTE (multi-agent, mro-wkii.17 / agent: make_ssot_audit): derive_model tests
# compose canonical source models without JSON-shaped intermediaries.
# mro-wkii.17.26 (codex): exercise CLI flows through the public invocation facade.


class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    def test_model_command_skips_excluded_fields(self) -> None:
        """Exclude hidden model fields from generated CLI options."""
        app = cli.create_app_with_common_params(
            name="exclude-app", help_text="Exclude app"
        )
        cli.register_command(
            app,
            name="run",
            help_text="Run",
            command=cli.model_command(m.Tests.ExcludedFieldInput, lambda _params: True),
        )
        help_result = cli.invoke_app(app, args=("run", "--help"))

        tm.ok(help_result)
        invocation = help_result.value
        tm.that(invocation.exit_code, eq=0)
        tm.that(invocation.stdout, has="--visible")
        tm.that("--hidden" in invocation.stdout, eq=False)

    def test_create_app_with_common_params_handles_invalid_trace_without_debug(
        self,
    ) -> None:
        """Keep trace disabled when debug mode is not active."""
        app = cli.create_app_with_common_params(name="warn-app", help_text="Warn app")
        cli.register_command(app, name="ok", help_text="OK", command=lambda: True)

        invoke_result = cli.invoke_app(app, args=("--trace", "ok"))

        tm.ok(invoke_result)
        invocation = invoke_result.value
        tm.that(invocation.exit_code, eq=0)
        tm.that(settings.trace, eq=False)

    def test_create_app_with_common_params_no_flags_keeps_settings(self) -> None:
        """Preserve shared settings when no global flags are provided."""
        app = cli.create_app_with_common_params(
            name="identity-app", help_text="Identity app"
        )
        cli.register_command(app, name="ok", help_text="OK", command=lambda: True)

        invoke_result = cli.invoke_app(app, args=("ok",))

        tm.ok(invoke_result)
        invocation = invoke_result.value
        tm.that(invocation.exit_code, eq=0)
        tm.that(settings.debug, eq=False)

    def test_derive_model_merges_canonical_model_sources(self) -> None:
        """Merge canonical model sources in declaration order."""
        first_source = m.Tests.SampleInputPatch(name="alice", count=2)
        model_from_instance = m.Tests.SampleInput(
            name="bob", count=7, dry_run=True, output_format=c.Cli.OutputFormats.JSON
        )
        final_source = m.Tests.SampleInput(
            name="carol", count=9, dry_run=True, output_format=c.Cli.OutputFormats.JSON
        )

        derived = cli.derive_model(
            m.Tests.SampleInput, first_source, model_from_instance, final_source
        )

        tm.that(derived.name, eq="carol")
        tm.that(derived.count, eq=9)
        tm.that(derived.dry_run, eq=True)

    def test_execute_app_handles_unexpected_exception(self) -> None:
        """Propagate an unexpected application exception with context."""
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

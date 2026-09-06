"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

import pytest

from flext_cli import cli, settings
from flext_tests import tm
from tests import c, m, u

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.
# NOTE (multi-agent, mro-wkii.17 / agent: make_ssot_audit): derive_model tests
# compose canonical source models without JSON-shaped intermediaries.


class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    def test_model_command_skips_excluded_fields(self) -> None:
        """Exclude model fields marked private from the generated CLI surface."""

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
        help_result = cli.invoke_app(app, args=["run", "--help"])

        tm.ok(help_result)
        tm.that(u.Cli.process_succeeded(help_result.value.outcome), eq=True)
        tm.that(help_result.value.stdout, has="--visible")
        tm.that("--hidden" in help_result.value.stdout, eq=False)

    def test_create_app_with_common_params_handles_invalid_trace_without_debug(
        self,
    ) -> None:
        """Keep trace disabled when debug is not enabled at the public boundary."""
        app = cli.create_app_with_common_params(name="warn-app", help_text="Warn app")
        cli.register_command(app, name="ok", help_text="OK", command=lambda: True)

        invoke_result = cli.invoke_app(app, args=["--trace", "ok"])

        tm.ok(invoke_result)
        tm.that(u.Cli.process_succeeded(invoke_result.value.outcome), eq=True)
        tm.that(settings.trace, eq=False)

    def test_create_app_with_common_params_no_flags_keeps_settings(self) -> None:
        """Preserve settings when the invocation supplies no shared flags."""
        app = cli.create_app_with_common_params(
            name="identity-app", help_text="Identity app"
        )
        cli.register_command(app, name="ok", help_text="OK", command=lambda: True)

        invoke_result = cli.invoke_app(app, args=["ok"])

        tm.ok(invoke_result)
        tm.that(u.Cli.process_succeeded(invoke_result.value.outcome), eq=True)
        tm.that(settings.debug, eq=False)

    def test_derive_model_merges_canonical_model_sources(self) -> None:
        """Merge ordered canonical model sources without model-less payloads."""
        first_source = m.Tests.SampleInput(name="alice", count=2)
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

    def test_execute_app_propagates_unexpected_exception(self) -> None:
        """Propagate unexpected command defects with their original cause."""
        app = cli.create_app_with_common_params(name="error-app", help_text="Error app")
        cli.register_command(
            app,
            name="boom",
            help_text="Boom command",
            command=lambda: (_ for _ in ()).throw(ValueError("boom")),
        )

        with pytest.raises(ValueError, match="boom"):
            cli.execute_app(app, prog_name="error-app", args=["boom"])


__all__: list[str] = ["TestsFlextCliService"]

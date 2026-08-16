"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import cli
from flext_tests import tm
from tests import m

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    def test_execute_app_handles_nonzero_int_result(self) -> None:
        """Convert a nonzero integer command result into a failed Result."""
        app = cli.create_app_with_common_params(name="int-app", help_text="Int app")
        cli.register_command(
            app, name="return-two", help_text="Return int", command=lambda: 2
        )

        result = cli.execute_app(app, prog_name="int-app", args=["return-two"])

        tm.fail(result)
        tm.that(result.error, has="CLI exited with code 2")

    def test_execute_app_handles_typer_exit_zero_branch(self) -> None:
        """Normalize a real zero Typer exit into successful execution."""
        app = cli.create_app_with_common_params(name="zero-app", help_text="Zero app")
        cli.register_command(
            app,
            name="exit-zero",
            help_text="Exit zero",
            command=lambda: cli.exit(code=0),
        )

        result = cli.execute_app(app, prog_name="zero-app", args=["exit-zero"])

        tm.ok(result)

    def test_execute_app_handles_typer_exit_nonzero_branch_real(self) -> None:
        """Normalize a real nonzero Typer exit into a failed Result."""
        app = cli.create_app_with_common_params(
            name="nonzero-app", help_text="Non-zero app"
        )
        cli.register_command(
            app, name="exit-one", help_text="Exit one", command=lambda: cli.exit(code=1)
        )

        result = cli.execute_app(app, prog_name="nonzero-app", args=["exit-one"])

        tm.fail(result)
        tm.that(result.error, has="CLI exited with code 1")

    def test_execute_app_prefers_real_failure_message(self) -> None:
        """Preserve the real framework failure message at the public boundary."""
        app = cli.create_app_with_common_params(
            name="sample", help_text="Failure group"
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
            app, prog_name="sample", args=["group", "fail", "--name", "alice"]
        )

        tm.fail(result)
        tm.that(result.error, has="CLI exited with code 1")

    def test_execute_app_preserves_click_usage_errors(self) -> None:
        """Preserve Click usage details when a command name is invalid."""
        app = cli.create_app_with_common_params(
            name="sample", help_text="Failure group"
        )
        group = cli.create_group(help_text="Grouped failure commands", name="group")

        cli.register_command(
            group, name="ok", help_text="Successful command", command=lambda: True
        )
        cli.add_group(app, name="group", group=group)

        result = cli.execute_app(
            app, prog_name="sample", args=["group", "missing-command"]
        )

        tm.fail(result)
        tm.that(result.error, has="No such command 'missing-command'")

    def test_execute_external_command_accepts_public_sequence(self) -> None:
        """External commands receive a list at the private framework boundary."""
        app = cli.create_app_with_common_params(
            name="external-app", help_text="External command application"
        )
        cli.register_command(
            app,
            name="ok",
            help_text="Successful external command",
            command=lambda: True,
        )

        result = cli.execute_external_command(
            cli.external_command(app), prog_name="external-app", args=("ok",)
        )

        tm.ok(result)


__all__: list[str] = ["TestsFlextCliService"]

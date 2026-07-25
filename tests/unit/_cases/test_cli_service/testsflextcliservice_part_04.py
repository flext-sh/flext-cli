"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from flext_tests import tm
from tests.models import m
from tests.typings import t

from flext_cli import cli


class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

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

    def test_execute_app_handles_typer_exit_zero_branch(self) -> None:
        app = cli.create_app_with_common_params(
            name="zero-app",
            help_text="Zero app",
            settings=cli.settings,
        )
        cli.register_command(
            app,
            name="exit-zero",
            help_text="Exit zero",
            command=lambda: cli.exit(code=0),
        )

        result = cli.execute_app(app, prog_name="zero-app", args=["exit-zero"])

        tm.ok(result)

    def test_execute_app_handles_typer_exit_nonzero_branch_real(self) -> None:
        app = cli.create_app_with_common_params(
            name="nonzero-app",
            help_text="Non-zero app",
            settings=cli.settings,
        )
        cli.register_command(
            app,
            name="exit-one",
            help_text="Exit one",
            command=lambda: cli.exit(code=1),
        )

        result = cli.execute_app(app, prog_name="nonzero-app", args=["exit-one"])

        tm.fail(result)
        tm.that(result.error, has="CLI exited with code 1")

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


__all__: list[str] = ["TestsFlextCliService"]

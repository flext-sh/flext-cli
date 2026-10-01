"""Behavioral tests for ``cli.service_routes`` through a real Typer app.

Service operations become commands: the valid command renders its result,
rejected input exits non-zero with the validation cause, an input-less
operation runs without options, and ``--help`` never builds the service.
"""

from __future__ import annotations

from typing import override

import pytest
from flext_tests import tm

from flext_cli import cli, r, s
from tests import m, p, t, u


class TestsFlextCliServiceRoutes:
    """Behavioral contract of service-derived CLI routes."""

    class Greeting(m.BaseModel):
        """Request of the greet operation."""

        name: str
        times: int = m.Field(default=1, ge=1)

    class Status(m.BaseModel):
        """Result of the status operation."""

        ready: int

    class Greeter(s[Status]):
        """Service whose public operations are the CLI."""

        @override
        def execute(self) -> p.Result[TestsFlextCliServiceRoutes.Status]:
            """Run the default service action."""
            return r[TestsFlextCliServiceRoutes.Status].ok(
                TestsFlextCliServiceRoutes.Status(ready=1),
            )

        def greet_all(
            self,
            request: TestsFlextCliServiceRoutes.Greeting,
        ) -> p.Result[str]:
            """Greet someone by name."""
            return r[str].ok(" ".join([f"hello {request.name}"] * request.times))

        def report(self) -> p.Result[TestsFlextCliServiceRoutes.Status]:
            """Report the service status."""
            return r[TestsFlextCliServiceRoutes.Status].ok(
                TestsFlextCliServiceRoutes.Status(ready=1),
            )

    @staticmethod
    def _app(
        provide: t.Cli.NullaryOperation[TestsFlextCliServiceRoutes.Greeter],
    ) -> p.Cli.Application:
        app = cli.create_app_with_common_params(name="greeter", help_text="Greeter")
        cli.register_result_routes(
            app,
            cli.service_routes(TestsFlextCliServiceRoutes.Greeter, provide=provide),
        )
        return app

    @staticmethod
    def _unconfigured() -> TestsFlextCliServiceRoutes.Greeter:
        msg = "adapter environment is not configured"
        raise RuntimeError(msg)

    def test_valid_command_renders_result_value(self) -> None:
        """A valid invocation exits zero and renders the operation value."""
        app = self._app(self.Greeter)

        outcome = tm.ok(
            cli.invoke_app(app, args=["greet-all", "--name", "ana", "--times", "2"]),
        )

        tm.that(u.Cli.process_succeeded(outcome.outcome), eq=True)
        tm.that(outcome.stdout, has="hello ana hello ana")

    def test_invalid_input_exits_non_zero_with_validation_cause(self) -> None:
        """Rejected input fails the command with the ValidationError cause."""
        app = self._app(self.Greeter)

        outcome = tm.ok(
            cli.invoke_app(app, args=["greet-all", "--name", "ana", "--times", "0"]),
        )

        tm.that(u.Cli.process_succeeded(outcome.outcome), eq=False)
        tm.that(outcome.stdout, has=["Greeting", "greater than or equal to 1"])

    def test_input_less_operation_renders_json(self) -> None:
        """An operation without a request model runs with no options."""
        app = self._app(self.Greeter)

        outcome = tm.ok(cli.invoke_app(app, args=["report"]))

        tm.that(u.Cli.process_succeeded(outcome.outcome), eq=True)
        tm.that(outcome.stdout, has='{"ready":1}')

    @pytest.mark.parametrize(
        "args",
        [["--help"], ["greet-all", "--help"], ["report", "--help"]],
    )
    def test_help_builds_no_adapter(self, args: list[str]) -> None:
        """Help renders from the class; the unconfigured provider never runs."""
        app = self._app(self._unconfigured)

        outcome = tm.ok(cli.invoke_app(app, args=args))

        tm.that(u.Cli.process_succeeded(outcome.outcome), eq=True)
        tm.that(outcome.stdout, has="Usage")

    def test_execution_reaches_the_provider(self) -> None:
        """Executing a command builds the service through the provider."""
        app = self._app(self._unconfigured)

        with pytest.raises(RuntimeError, match="not configured"):
            cli.execute_app(app, prog_name="greeter", args=["report"])

    def test_required_excluded_request_field_fails_at_build(self) -> None:
        """A required field that no option can supply is a build-time defect."""

        class Hidden(m.BaseModel):
            token: str = m.Field(exclude=True)

        with pytest.raises(TypeError, match="token"):
            cli.model_command(Hidden, lambda _params: True)

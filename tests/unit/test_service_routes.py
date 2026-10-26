"""Behavioral tests for ``cli.service_routes`` through a real Typer app.

Service operations become commands: the valid command renders its result,
rejected input exits non-zero with the validation cause, an input-less
operation runs without options, and ``--help`` never builds the service.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

import pytest

from flext_cli import cli
from tests import c, h, m, p, r, s, t, tm, u


@pytest.mark.usefixtures("preserve_logging")
class TestsFlextCliServiceRoutes:
    """Behavioral contract of service-derived CLI routes."""

    class Greeter(s[p.Tests.ServiceStatus]):
        """Service whose public operations are the CLI.

        The service extends the tests sibling hierarchy, not
        ``FlextCliServiceBase``: ``cli.service_routes`` accepts any core
        ``FlextService`` subclass, so this keeps the contract honest for
        conforming services outside the CLI base.
        """

        greeting: str = "hello"
        ready: int = 1

        def greet_default(self) -> p.Result[p.Tests.ServiceStatus]:
            """Run the default service action.

            Returns:
                The resulting ``p.Result[p.Tests.ServiceStatus]``.

            """
            return self.report()

        @h.handler(command=m.Tests.ServiceGreeting)
        def greet_all(
            self,
            request: p.Tests.ServiceGreeting,
        ) -> p.Result[str]:
            """Greet someone by name.

            Returns:
                The resulting ``p.Result[str]``.

            """
            return r[str].ok(
                " ".join([f"{self.greeting} {request.name}"] * request.times)
            )

        def report(self) -> p.Result[p.Tests.ServiceStatus]:
            """Report the service status.

            Returns:
                The resulting ``p.Result[p.Tests.ServiceStatus]``.

            """
            return r[p.Tests.ServiceStatus].ok(
                m.Tests.ServiceStatus(ready=self.ready),
            )

    class AlternateGreeter(Greeter):
        """A provider cannot replace the function selected by the route catalog."""

        @override
        def greet_all(self, request: p.Tests.ServiceGreeting) -> p.Result[str]:
            """Expose a different implementation under the same method name.

            Returns:
                The resulting ``p.Result[str]``.

            """
            return r[str].ok(f"replacement {request.name}")

    @staticmethod
    def _app(
        provide: t.Cli.NullaryOperation[p.Service[p.Tests.ServiceStatus]],
    ) -> p.Cli.Application:
        app = cli.create_app_with_common_params(name="greeter", help_text="Greeter")
        cli.register_result_routes(
            app,
            cli.service_routes(TestsFlextCliServiceRoutes.Greeter, provide=provide),
        )
        return app

    @staticmethod
    def _unconfigured() -> p.Service[p.Tests.ServiceStatus]:
        msg = "adapter environment is not configured"
        raise RuntimeError(msg)

    def test_valid_command_renders_result_value(self) -> None:
        """A valid invocation exits zero and renders the operation value."""
        app = self._app(self.Greeter)

        outcome = tm.ok(
            cli.invoke_app(app, args=["greet-all", "--name", "ana", "--times", "2"]),
        )

        tm.ok(u.Cli.process_succeeded(outcome.outcome))
        tm.that(outcome.stdout, has="hello ana hello ana")

    @pytest.mark.parametrize(
        "provider_available",
        [
            pytest.param(True, id="configured-provider"),
            pytest.param(False, id="unavailable-provider-never-constructed"),
        ],
    )
    def test_invalid_input_exits_non_zero_with_validation_cause(
        self, *, provider_available: bool
    ) -> None:
        """Reject invalid input before constructing either provider."""
        app = self._app(self.Greeter if provider_available else self._unconfigured)

        outcome = tm.ok(
            cli.invoke_app(
                app,
                args=[
                    "greet-all",
                    "--name",
                    "ana",
                    "--times",
                    c.ParserBooleanToken.ZERO,
                ],
            ),
        )

        tm.fail(u.Cli.process_succeeded(outcome.outcome))
        tm.that(outcome.stdout, eq="")
        tm.that(outcome.stderr, has=["ServiceGreeting", "greater than or equal to 1"])

    def test_input_less_operation_renders_json(self) -> None:
        """An operation without a request model runs with no options."""
        app = self._app(self.Greeter)

        outcome = tm.ok(cli.invoke_app(app, args=["report"]))

        tm.ok(u.Cli.process_succeeded(outcome.outcome))
        tm.that(outcome.stdout, has='{"ready":1}')

    def test_execution_uses_catalogued_function_identity(self) -> None:
        """The provider supplies self, not a late replacement for the operation."""
        app = self._app(self.AlternateGreeter)
        outcome = tm.ok(cli.invoke_app(app, args=["greet-all", "--name", "ana"]))
        tm.ok(u.Cli.process_succeeded(outcome.outcome))
        tm.that(outcome.stdout, has="hello ana")
        tm.ok("replacement" not in outcome.stdout)

    @pytest.mark.parametrize(
        "args",
        [["--help"], ["greet-all", "--help"], ["report", "--help"]],
    )
    def test_help_builds_no_adapter(self, args: list[str]) -> None:
        """Help renders from the class; the unconfigured provider never runs."""
        app = self._app(self._unconfigured)

        outcome = tm.ok(cli.invoke_app(app, args=args))

        tm.ok(u.Cli.process_succeeded(outcome.outcome))
        tm.that(outcome.stdout, has="Usage")

    def test_execution_reaches_the_provider(self) -> None:
        """Executing a command builds the service through the provider."""
        app = self._app(self._unconfigured)

        with pytest.raises(RuntimeError, match="not configured"):
            cli.execute_app(app, prog_name="greeter", args=["report"])

    @staticmethod
    def test_required_excluded_request_field_fails_at_build() -> None:
        """A required field that no option can supply is a build-time defect."""

        class Hidden(m.BaseModel):
            token: str = m.Field(exclude=True)

        with pytest.raises(TypeError, match="token"):
            cli.model_command(Hidden, lambda _params: True)

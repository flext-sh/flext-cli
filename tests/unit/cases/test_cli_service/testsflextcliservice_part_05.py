"""Real Typer integration tests for the public flext-cli CLI facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import cli

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.
from tests import c, m, p, r, t, tm, u


class TestsFlextCliServicePart05:
    """Implementation part for TestsFlextCliServicePart05."""

    @staticmethod
    def test_register_result_command_renders_success_and_failure() -> None:
        """Verify that register result command renders success and failure."""
        app = cli.create_app_with_common_params(
            name="result-app",
            help_text="Result application",
        )
        group = cli.create_group(help_text="Grouped commands", name="group")

        def ok_handler(params: p.Tests.SampleInput) -> p.Result[t.JsonPayload]:
            return cli.execute().map(
                lambda _payload: m.Tests.SampleOutput(
                    message=f"processed {params.name}",
                ),
            )

        def fail_handler(params: p.Tests.SampleInput) -> p.Result[t.JsonPayload]:
            return cli.validate_credentials("", "password").map(
                lambda _value: m.Tests.SampleOutput(message=params.name),
            )

        def build_ok_route() -> p.Cli.ResultCommandRoute:
            return m.Cli.ResultCommandRoute(
                name="ok",
                help_text="Successful command",
                model_cls=m.Tests.SampleInput,
                handler=ok_handler,
            )

        def build_fail_route() -> p.Cli.ResultCommandRoute:
            return m.Cli.ResultCommandRoute(
                name="fail",
                help_text="Failing command",
                model_cls=m.Tests.SampleInput,
                handler=fail_handler,
            )

        cli.register_result_route(app, route=build_ok_route())
        cli.register_result_route(group, route=build_fail_route())
        cli.add_group(app, name="group", group=group)
        ok_invocation = cli.invoke_app(app, args=["ok", "--name", "alice"])
        fail_invocation = cli.invoke_app(app, args=["group", "fail", "--name", "alice"])
        tm.ok(ok_invocation)
        tm.ok(fail_invocation)
        ok_result = ok_invocation.value
        fail_result = fail_invocation.value

        tm.that(ok_result.exit_code, eq=0)
        tm.that(ok_result.stdout, has="processed alice")
        tm.that(fail_result.exit_code, eq=1)
        tm.that(fail_result.stderr, has="Username cannot be empty")
        tm.that(fail_result.stdout, eq="")

    @staticmethod
    def test_result_route_resolves_its_model_only_when_it_parses() -> None:
        """Help lists every route unresolved; only the parsed route resolves."""
        app = cli.create_app_with_common_params(
            name="lazy-app",
            help_text="Lazy application",
        )
        resolved: list[str] = []

        def resolve_first() -> t.ModelClass[m.Tests.SampleInput]:
            resolved.append("first")
            return m.Tests.SampleInput

        def resolve_second() -> t.ModelClass[m.Tests.SampleInput]:
            resolved.append("second")
            return m.Tests.SampleInput

        def handler(params: p.Tests.SampleInput) -> p.Result[t.JsonPayload]:
            return r[t.JsonPayload].ok(
                m.Tests.SampleOutput(message=f"processed {params.name}"),
            )

        cli.register_result_routes(
            app,
            [
                m.Cli.ResultCommandRoute(
                    name="first",
                    help_text="First command",
                    model_cls=resolve_first,
                    handler=handler,
                ),
                m.Cli.ResultCommandRoute(
                    name="second",
                    help_text="Second command",
                    model_cls=resolve_second,
                    handler=handler,
                ),
            ],
        )

        app_help = tm.ok(cli.invoke_app(app, args=["--help"]))
        tm.that(app_help.exit_code, eq=c.Cli.EXIT_CODE_SUCCESS)
        tm.that(app_help.stdout, has=["First command", "Second command"])
        tm.that(resolved, eq=[])

        route_help = tm.ok(cli.invoke_app(app, args=["first", "--help"]))
        tm.that(route_help.exit_code, eq=c.Cli.EXIT_CODE_SUCCESS)
        tm.that(route_help.stdout, has="--name")
        tm.that(resolved, eq=["first"])

        run = tm.ok(cli.invoke_app(app, args=["first", "--name", "alice"]))
        tm.that(run.exit_code, eq=c.Cli.EXIT_CODE_SUCCESS)
        tm.that(run.stdout, has="processed alice")
        tm.that(resolved, eq=["first", "first"])

    @staticmethod
    def test_result_route_resolves_its_model_class_for_consumers() -> None:
        """A class and a resolver both read back as the same input model class."""

        def handler(params: p.Tests.SampleInput) -> p.Result[t.JsonPayload]:
            return r[t.JsonPayload].ok(params.name)

        def resolve() -> t.ModelClass[m.Tests.SampleInput]:
            return m.Tests.SampleInput

        for source in (m.Tests.SampleInput, resolve):
            route = m.Cli.ResultCommandRoute(
                name="sample",
                help_text="Sample command",
                model_cls=source,
                handler=handler,
            )
            tm.that(route.resolved_model_cls, eq=m.Tests.SampleInput)
            tm.that(route.resolved_model_cls.model_fields, has="name")

    @staticmethod
    def test_invoke_app_raises_a_route_model_that_cannot_become_a_command() -> None:
        """A route model defect escapes invoke_app instead of exiting silently."""
        app = cli.create_app_with_common_params(
            name="broken-app",
            help_text="Broken application",
        )

        def handler(_params: p.Tests.ExcludedRequiredInput) -> p.Result[t.JsonPayload]:
            return r[t.JsonPayload].ok("unreachable")

        cli.register_result_routes(
            app,
            [
                m.Cli.ResultCommandRoute(
                    name="broken",
                    help_text="Broken command",
                    model_cls=m.Tests.ExcludedRequiredInput,
                    handler=handler,
                ),
            ],
        )

        app_help = tm.ok(cli.invoke_app(app, args=["--help"]))
        tm.that(app_help.stdout, has="Broken command")
        with u.Tests.raises(TypeError, match="exclude=True"):
            cli.invoke_app(app, args=["broken"])

    @staticmethod
    def test_register_result_routes_propagates_real_failure() -> None:
        """Verify that register result routes propagates real failure."""
        app = cli.create_app_with_common_params(
            name="result-app",
            help_text="Result application",
        )

        def fail_handler(params: p.Tests.SampleInput) -> p.Result[t.JsonPayload]:
            return r[t.JsonPayload].fail(
                "Password cannot be resolved",
                error_code="secret_unavailable",
                error_data={"field": "password", "name": params.name},
                exception=ValueError("secret backend unavailable"),
            )

        cli.register_result_routes(
            app,
            [
                m.Cli.ResultCommandRoute(
                    name="fail",
                    help_text="Failing command",
                    model_cls=m.Tests.SampleInput,
                    handler=fail_handler,
                ),
            ],
        )
        fail_result = cli.execute_app(
            app,
            prog_name="result-app",
            args=["fail", "--name", "alice"],
        )

        tm.fail(fail_result)
        tm.that(fail_result.error, has="Password cannot be resolved")
        tm.that(fail_result.error_code, eq="secret_unavailable")
        tm.ok(fail_result.error_data is not None)
        tm.that(tm.not_none(fail_result.error_data)["field"], eq="password")
        tm.that(fail_result.exception, is_=ValueError)
        tm.that(cli.finalize_result(fail_result), eq=c.Cli.EXIT_CODE_FAILURE)
        tm.that(cli.finalize_result(fail_result, failure_exit_code=2), eq=2)

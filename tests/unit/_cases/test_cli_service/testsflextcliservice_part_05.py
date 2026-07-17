"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations


from flext_tests import tm
from tests import c
from tests import m

from flext_cli import cli, r

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.
# mro-wkii.17.26 (codex): exercise CLI flows through the public invocation facade.

from tests import p


class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    def test_register_result_command_renders_success_and_failure(self) -> None:
        """Render successful and failed result commands through real CLI routes."""
        app = cli.create_app_with_common_params(
            name="result-app", help_text="Result application"
        )
        group = cli.create_group(help_text="Grouped commands", name="group")

        def ok_handler(params: p.Tests.SampleInput) -> p.Result[p.Tests.SampleOutput]:
            return cli.execute().map(
                lambda _payload: m.Tests.SampleOutput(
                    message=f"processed {params.name}"
                )
            )

        def fail_handler(params: p.Tests.SampleInput) -> p.Result[p.Tests.SampleOutput]:
            return cli.validate_credentials("", "password").map(
                lambda _value: m.Tests.SampleOutput(message=params.name)
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

        tm.ok(ok_result)
        tm.ok(fail_result)
        ok_invocation = ok_result.value
        fail_invocation = fail_result.value
        tm.that(ok_invocation.exit_code, eq=0)
        tm.that(ok_invocation.stdout, has="processed alice")
        tm.that(fail_invocation.exit_code, eq=1)
        tm.that(fail_invocation.stdout, has="Username cannot be empty")

    def test_register_result_routes_propagates_real_failure(self) -> None:
        """Preserve structured failures from registered result routes."""
        app = cli.create_app_with_common_params(
            name="result-app", help_text="Result application"
        )

        def fail_handler(params: p.Tests.SampleInput) -> p.Result[p.Tests.SampleOutput]:
            return r[p.Tests.SampleOutput].fail(
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
                )
            ],
        )
        fail_result = cli.execute_app(
            app, prog_name="result-app", args=["fail", "--name", "alice"]
        )

        tm.fail(fail_result)
        tm.that(fail_result.error, has="Password cannot be resolved")
        tm.that(fail_result.error_code, eq="secret_unavailable")
        tm.that(fail_result.error_data, eq={"field": "password", "name": "alice"})
        tm.that(fail_result.exception, is_=ValueError)
        tm.that(cli.finalize_result(fail_result), eq=c.Cli.EXIT_CODE_FAILURE)
        tm.that(cli.finalize_result(fail_result, failure_exit_code=2), eq=2)


__all__: list[str] = ["TestsFlextCliService"]

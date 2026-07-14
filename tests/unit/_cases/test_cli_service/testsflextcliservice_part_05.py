"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tests import tm
from tests import c
from tests import m

from flext_cli import cli, r

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.

if TYPE_CHECKING:
    from tests import p


class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    def test_register_result_command_renders_success_and_failure(self) -> None:
        app = cli.create_app_with_common_params(
            name="result-app", help_text="Result application"
        )
        group = cli.create_group(help_text="Grouped commands", name="group")

        def ok_handler(params: m.Tests.SampleInput) -> p.Result[m.Tests.SampleOutput]:
            return cli.execute().map(
                lambda _payload: m.Tests.SampleOutput(
                    message=f"processed {params.name}"
                )
            )

        def fail_handler(params: m.Tests.SampleInput) -> p.Result[m.Tests.SampleOutput]:
            return cli.validate_credentials("", "password").map(
                lambda _value: m.Tests.SampleOutput(message=params.name)
            )

        def build_ok_route() -> m.Cli.ResultCommandRoute:
            return m.Cli.ResultCommandRoute(
                name="ok",
                help_text="Successful command",
                model_cls=m.Tests.SampleInput,
                handler=ok_handler,
            )

        def build_fail_route() -> m.Cli.ResultCommandRoute:
            return m.Cli.ResultCommandRoute(
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
            app, ["group", "fail", "--name", "alice"]
        )

        tm.that(ok_result.exit_code, eq=0)
        tm.that(ok_result.stdout, has="processed alice")
        tm.that(fail_result.exit_code, eq=1)
        tm.that(fail_result.stdout, has="Username cannot be empty")

    def test_register_result_routes_propagates_real_failure(self) -> None:
        app = cli.create_app_with_common_params(
            name="result-app", help_text="Result application"
        )

        def fail_handler(params: m.Tests.SampleInput) -> p.Result[m.Tests.SampleOutput]:
            return r[m.Tests.SampleOutput].fail(
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
        assert fail_result.error_data is not None
        tm.that(fail_result.error_data["field"], eq="password")
        tm.that(fail_result.exception, is_=ValueError)
        tm.that(cli.finalize_result(fail_result), eq=c.Cli.EXIT_CODE_FAILURE)


__all__: list[str] = ["TestsFlextCliService"]

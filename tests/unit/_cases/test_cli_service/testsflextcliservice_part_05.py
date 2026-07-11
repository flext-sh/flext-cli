"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tests import tm
from tests.models import m

from flext_cli import cli

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.

if TYPE_CHECKING:
    from tests.protocols import p


class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    def test_register_result_command_renders_success_and_failure(self) -> None:
        app = cli.create_app_with_common_params(
            name="result-app",
            help_text="Result application",
        )
        group = cli.create_group(help_text="Grouped commands", name="group")

        def ok_handler(
            params: m.Tests.SampleInput,
        ) -> p.Result[m.Tests.SampleOutput]:
            return cli.execute().map(
                lambda _payload: m.Tests.SampleOutput(
                    message=f"processed {params.name}",
                ),
            )

        def fail_handler(
            params: m.Tests.SampleInput,
        ) -> p.Result[m.Tests.SampleOutput]:
            return cli.validate_credentials("", "password").map(
                lambda _value: m.Tests.SampleOutput(message=params.name),
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
            app,
            ["group", "fail", "--name", "alice"],
        )

        tm.that(ok_result.exit_code, eq=0)
        tm.that(ok_result.stdout, has="processed alice")
        tm.that(fail_result.exit_code, eq=1)
        tm.that(fail_result.stdout, has="Username cannot be empty")

    def test_register_result_routes_propagates_real_failure(self) -> None:
        app = cli.create_app_with_common_params(
            name="result-app",
            help_text="Result application",
        )

        def fail_handler(
            params: m.Tests.SampleInput,
        ) -> p.Result[m.Tests.SampleOutput]:
            return cli.validate_credentials(params.name, "").map(
                lambda _value: m.Tests.SampleOutput(message=params.name),
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
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        fail_result = runner_result.value.invoke(app, ["fail", "--name", "alice"])

        tm.that(fail_result.exit_code, eq=1)
        tm.that(fail_result.stdout, has="Password cannot be empty")


__all__: list[str] = ["TestsFlextCliService"]

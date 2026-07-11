"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tests import tm
from tests.constants import c
from tests.models import m

from flext_cli import cli

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.

if TYPE_CHECKING:
    from collections.abc import (
        MutableSequence,
    )

    from tests.typings import t


class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    def test_model_command_accepts_repeatable_list_options(self) -> None:
        captured: MutableSequence[m.Tests.RepeatableInput] = []
        app = cli.create_app_with_common_params(
            name="root",
            help_text="Root application",
        )
        group = cli.create_group(help_text="Sample group", name="sample")

        def handle(params: m.Tests.RepeatableInput) -> t.JsonValue:
            captured.append(params)
            return True

        command = cli.model_command(m.Tests.RepeatableInput, handle)
        cli.register_command(
            group,
            name="repeat",
            help_text="Run repeatable option command",
            command=command,
        )
        cli.add_group(app, name="sample", group=group)
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        exec_result = runner_result.value.invoke(
            app,
            [
                "sample",
                "repeat",
                "--make-arg",
                "FILES=a b c.py",
                "--make-arg",
                "VERBOSE=1",
            ],
        )

        tm.that(exec_result.exit_code, eq=0)
        tm.that(len(captured), eq=1)
        tm.that(captured[0].make_arg, eq=["FILES=a b c.py", "VERBOSE=1"])

    def test_model_command_returns_handler_value(self) -> None:
        def handle(params: m.Tests.SampleInput) -> t.JsonValue:
            return {
                "name": params.name,
                "count": params.count,
                "dry_run": params.dry_run,
                "output_format": params.output_format,
            }

        command = cli.model_command(m.Tests.SampleInput, handle)
        result = command(
            name="alice",
            count=3,
            dry_run=True,
            output_format=c.Cli.OutputFormats.JSON,
        )

        tm.that(
            result,
            eq={
                "name": "alice",
                "count": 3,
                "dry_run": True,
                "output_format": c.Cli.OutputFormats.JSON,
            },
        )

    def test_model_command_uses_custom_param_decls_from_field_extra(self) -> None:
        class CustomDeclModel(m.BaseModel):
            flag: bool = m.Field(
                False,
                validate_default=True,
                description="Custom flag",
                json_schema_extra={"typer_param_decls": ["-f", "--flaggy"]},
            )

        app = cli.create_app_with_common_params(
            name="decl-app",
            help_text="Decl app",
        )
        cli.register_command(
            app,
            name="run",
            help_text="Run",
            command=cli.model_command(CustomDeclModel, lambda _params: True),
        )
        runner_result = cli.create_cli_runner()
        tm.ok(runner_result)
        help_result = runner_result.value.invoke(app, ["run", "--help"])

        tm.that(help_result.exit_code, eq=0)
        tm.that(help_result.stdout, has="--flaggy")


__all__: list[str] = ["TestsFlextCliService"]

"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import cli
from flext_tests import tm
from tests import c, m

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.

if TYPE_CHECKING:
    from collections.abc import MutableSequence

    from tests import t


class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    def test_model_command_accepts_repeatable_list_options(self) -> None:
        """Accept repeated model-derived options through the public invocation facade."""
        captured: MutableSequence[m.Tests.RepeatableInput] = []
        app = cli.create_app_with_common_params(
            name="root", help_text="Root application"
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
        exec_result = cli.invoke_app(
            app,
            args=[
                "sample",
                "repeat",
                "--make-arg",
                "FILES=a b c.py",
                "--make-arg",
                "VERBOSE=1",
            ],
        )

        tm.ok(exec_result)
        tm.that(u.Cli.process_succeeded(exec_result.value.outcome), eq=True)
        tm.that(len(captured), eq=1)
        tm.that(captured[0].make_arg, eq=["FILES=a b c.py", "VERBOSE=1"])

    def test_model_command_returns_handler_value(self) -> None:
        """Return the observable value produced by a model command handler."""

        def handle(params: m.Tests.SampleInput) -> t.JsonValue:
            return {
                "name": params.name,
                "count": params.count,
                "dry_run": params.dry_run,
                "output_format": params.output_format,
            }

        command = cli.model_command(m.Tests.SampleInput, handle)
        result = command(
            name="alice", count=3, dry_run=True, output_format=c.Cli.OutputFormats.JSON
        )

        expected: t.JsonMapping = {
            "name": "alice",
            "count": 3,
            "dry_run": True,
            "output_format": c.Cli.OutputFormats.JSON,
        }
        tm.that(result, eq=expected)

    def test_model_command_uses_custom_param_decls_from_field_extra(self) -> None:
        """Expose custom option declarations from validated field metadata."""

        class CustomDeclModel(m.BaseModel):
            flag: bool = m.Field(
                False,
                validate_default=True,
                description="Custom flag",
                json_schema_extra={"typer_param_decls": ["-f", "--flaggy"]},
            )

        app = cli.create_app_with_common_params(name="decl-app", help_text="Decl app")
        cli.register_command(
            app,
            name="run",
            help_text="Run",
            command=cli.model_command(CustomDeclModel, lambda _params: True),
        )
        help_result = cli.invoke_app(app, args=["run", "--help"])

        tm.ok(help_result)
        tm.that(u.Cli.process_succeeded(help_result.value.outcome), eq=True)
        tm.that(help_result.value.stdout, has="--flaggy")


__all__: list[str] = ["TestsFlextCliService"]

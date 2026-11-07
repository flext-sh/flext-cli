"""Real Typer integration tests for the public flext-cli CLI facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import cli
from tests import c, m, p, t, tm, u


class TestsFlextCliServicePart02:
    """Implementation part for TestsFlextCliServicePart02."""

    @staticmethod
    def test_model_command_accepts_repeatable_list_options() -> None:
        """Accept repeated model-derived options through the public invocation.

        facade.
        """
        app, captured = u.Tests.sample_group_app(
            m.Tests.RepeatableInput,
            command_name="repeat",
        )
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
        tm.ok(u.Cli.process_succeeded(exec_result.value.outcome))
        tm.that(len(captured), eq=1)
        tm.that(captured[0].make_arg, eq=["FILES=a b c.py", "VERBOSE=1"])

    @staticmethod
    def test_model_command_returns_handler_value() -> None:
        """Return the observable value produced by a model command handler."""
        returned: list[t.JsonValue] = []

        def handle(params: p.Tests.SampleInput) -> t.JsonValue:
            value: t.JsonValue = {
                "name": params.name,
                c.Aggregation.COUNT: params.count,
                "dry_run": params.dry_run,
                "output_format": params.output_format,
            }
            returned.append(value)
            return value

        app = cli.create_app_with_common_params(
            name="handler-app",
            help_text="Handler app",
        )
        cli.register_command(
            app,
            name="run",
            help_text="Run",
            command=cli.model_command(m.Tests.SampleInput, handle),
        )
        invocation = cli.invoke_app(
            app,
            args=[
                "run",
                "--name",
                "alice",
                "--count",
                "3",
                "--dry-run",
                "--output-format",
                c.Cli.OutputFormats.JSON,
            ],
        )

        expected: t.JsonMapping = {
            "name": "alice",
            c.Aggregation.COUNT: 3,
            "dry_run": True,
            "output_format": c.Cli.OutputFormats.JSON,
        }
        tm.ok(invocation)
        tm.ok(u.Cli.process_succeeded(invocation.value.outcome))
        tm.that(returned, eq=[expected])

    @staticmethod
    def test_model_command_uses_custom_param_decls_from_field_extra() -> None:
        """Expose custom option declarations from validated field metadata."""

        class CustomDeclModel(m.BaseModel):
            flag: bool = m.Field(
                default=False,
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
        tm.ok(u.Cli.process_succeeded(help_result.value.outcome))
        tm.that(help_result.value.stdout, has="--flaggy")

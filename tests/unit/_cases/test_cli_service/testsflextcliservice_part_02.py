"""Real Typer integration tests for the public flext-cli CLI facade."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_tests import tm
from tests import c
from tests import m

from flext_cli import cli

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.
# mro-wkii.17.26 (codex): exercise CLI flows through the public invocation facade.

from collections.abc import MutableSequence

from tests import t



class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    def test_model_command_accepts_repeatable_list_options(self) -> None:
        """Parse repeatable CLI options into one validated model."""
        captured: MutableSequence[p.Tests.RepeatableInput] = []
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
            args=(
                "sample",
                "repeat",
                "--make-arg",
                "FILES=a b c.py",
                "--make-arg",
                "VERBOSE=1",
            ),
        )

        tm.ok(exec_result)
        invocation = exec_result.value
        tm.that(invocation.exit_code, eq=0)
        tm.that(len(captured), eq=1)
        tm.that(captured[0].make_arg, eq=["FILES=a b c.py", "VERBOSE=1"])

    def test_model_command_returns_handler_value(self) -> None:
        """Return the handler value from the model-generated command."""

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
        """Expose custom option declarations from validated field metadata."""
        app = cli.create_app_with_common_params(name="decl-app", help_text="Decl app")
        cli.register_command(
            app,
            name="run",
            help_text="Run",
            command=cli.model_command(
                m.Tests.CustomDeclarationInput, lambda _params: True
            ),
        )
        help_result = cli.invoke_app(app, args=("run", "--help"))

        tm.ok(help_result)
        invocation = help_result.value
        tm.that(invocation.exit_code, eq=0)
        tm.that(invocation.stdout, has="--flaggy")


__all__: list[str] = ["TestsFlextCliService"]

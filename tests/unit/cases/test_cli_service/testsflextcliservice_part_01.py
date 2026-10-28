"""Real Typer integration tests for the public flext-cli CLI facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableSequence, Sequence

from flext_cli import FlextCli, cli
from tests import c, m, p, t, tm, u


class TestsFlextCliServicePart01:
    """Implementation part for TestsFlextCliServicePart01."""

    @staticmethod
    def test_model_command_updates_runtime_settings_fields() -> None:
        """Apply model command values to the validated runtime settings model."""

        class RuntimeSettings(m.BaseModel):
            debug: bool = False

        settings = RuntimeSettings()

        def handle(params: m.Cli.CliParamsConfig) -> bool:
            return params.debug is True

        command = cli.model_command(m.Cli.CliParamsConfig, handle, settings=settings)
        result = command(debug=True)

        tm.ok(result)

    @staticmethod
    def _invoke_common_app(args: Sequence[str]) -> p.Result[m.Cli.InvocationResult]:
        """Register one inspect command and invoke the shared application.

        Returns:
            The resulting ``p.Result[m.Cli.InvocationResult]``.

        """
        service = FlextCli.with_settings(cli.settings.clone())
        app = service.create_app_with_common_params(
            name="sample",
            help_text="Sample application",
        )
        service.register_command(
            app,
            name="inspect",
            help_text="Inspect settings",
            command=lambda: True,
        )
        return service.invoke_app(app, args=args)

    @staticmethod
    def test_create_app_with_common_params_applies_settings() -> None:
        """Apply the shared debug option through the public invocation facade."""
        result = TestsFlextCliServicePart01._invoke_common_app(["--debug", "inspect"])

        tm.ok(result)
        tm.ok(u.Cli.process_succeeded(result.value.outcome))

    @staticmethod
    def test_create_app_with_common_params_applies_log_level() -> None:
        """Apply the shared log-level option through the public invocation facade."""
        result = TestsFlextCliServicePart01._invoke_common_app(
            ["--log-level", c.LogLevel.DEBUG, "inspect"],
        )

        tm.ok(result)
        tm.ok(u.Cli.process_succeeded(result.value.outcome))

    @staticmethod
    def test_model_command_generates_real_typer_options() -> None:
        """Generate and execute real options from a canonical request model."""
        captured: MutableSequence[m.Tests.SampleInput] = []
        app = cli.create_app_with_common_params(
            name="root",
            help_text="Root application",
        )
        group = cli.create_group(help_text="Sample group", name="sample")

        def handle(params: m.Tests.SampleInput) -> t.JsonValue:
            captured.append(params)
            return True

        command = cli.model_command(m.Tests.SampleInput, handle)
        cli.register_command(
            group,
            name="run",
            help_text="Run sample command",
            command=command,
        )
        cli.add_group(app, name="sample", group=group)
        help_result = cli.invoke_app(app, args=["sample", "run", "--help"])
        exec_result = cli.invoke_app(
            app,
            args=[
                "sample",
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

        tm.ok(help_result)
        tm.ok(exec_result)
        tm.ok(u.Cli.process_succeeded(help_result.value.outcome))
        tm.that(help_result.value.stdout, has="Target name")
        tm.that(help_result.value.stdout, has="Dry-run mode")
        tm.ok(u.Cli.process_succeeded(exec_result.value.outcome))
        tm.that(len(captured), eq=1)
        tm.that(captured[0].name, eq="alice")
        tm.that(captured[0].count, eq=3)
        tm.ok(captured[0].dry_run)
        tm.that(captured[0].output_format, eq=c.Cli.OutputFormats.JSON)

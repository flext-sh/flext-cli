"""Real Typer integration tests for the public flext-cli CLI facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Annotated

import pytest

from flext_cli import FlextCli, cli
from tests import m, tm, u


class TestsFlextCliServicePart03:
    """Implementation part for TestsFlextCliServicePart03."""

    @staticmethod
    def test_model_command_skips_excluded_fields() -> None:
        """Exclude model fields marked private from the generated CLI surface."""

        class ExcludedFieldModel(m.BaseModel):
            visible: Annotated[
                str, m.Field(..., description="Visible", validate_default=True)
            ]
            hidden: str = m.Field("secret", exclude=True, validate_default=True)

        app = cli.create_app_with_common_params(
            name="exclude-app",
            help_text="Exclude app",
        )
        cli.register_command(
            app,
            name="run",
            help_text="Run",
            command=cli.model_command(ExcludedFieldModel, lambda _params: True),
        )
        help_result = cli.invoke_app(app, args=["run", "--help"])

        tm.ok(help_result)
        tm.ok(u.Cli.process_succeeded(help_result.value.outcome))
        tm.that(help_result.value.stdout, has="--visible")
        tm.fail("--hidden" in help_result.value.stdout)

    @staticmethod
    def test_create_app_with_common_params_accepts_trace_without_debug() -> None:
        """Trace adds diagnostic detail without requiring debug mode."""
        service = FlextCli.with_settings(cli.settings.clone(debug=False))
        app = service.create_app_with_common_params(
            name="trace-app", help_text="Trace app"
        )
        service.register_command(app, name="ok", help_text="OK", command=lambda: True)

        invoke_result = service.invoke_app(app, args=["--trace", "ok"])

        tm.ok(invoke_result)
        tm.ok(u.Cli.process_succeeded(invoke_result.value.outcome))
        tm.ok(service.settings.trace)
        tm.fail(service.settings.debug)

    @staticmethod
    def test_create_app_with_common_params_no_flags_keeps_settings() -> None:
        """Preserve settings when the invocation supplies no shared flags."""
        app = cli.create_app_with_common_params(
            name="identity-app",
            help_text="Identity app",
        )
        cli.register_command(app, name="ok", help_text="OK", command=lambda: True)
        shared_flags = ("debug", "trace", "cli_verbose", "cli_quiet", "log_level")
        flags_before = {
            name: value
            for name, value in cli.settings.model_dump().items()
            if name in shared_flags
        }

        invoke_result = cli.invoke_app(app, args=["ok"])

        tm.ok(invoke_result)
        tm.ok(u.Cli.process_succeeded(invoke_result.value.outcome))
        tm.that(
            {
                name: value
                for name, value in cli.settings.model_dump().items()
                if name in shared_flags
            },
            eq=flags_before,
        )

    @staticmethod
    def test_execute_app_propagates_unexpected_exception() -> None:
        """Propagate unexpected command defects with their original cause."""
        app = cli.create_app_with_common_params(name="error-app", help_text="Error app")
        cli.register_command(
            app,
            name="boom",
            help_text="Boom command",
            command=lambda: (_ for _ in ()).throw(ValueError("boom")),
        )

        with pytest.raises(ValueError, match="boom"):
            cli.execute_app(app, prog_name="error-app", args=["boom"])

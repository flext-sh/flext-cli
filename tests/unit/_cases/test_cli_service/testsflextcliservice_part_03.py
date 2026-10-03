"""Real Typer integration tests for the public flext-cli CLI facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import cli, settings
from tests import m
from tests.utilities import u

# NOTE (multi-agent, mro-wkii.19.4): app creation owns the settings singleton.


class TestsFlextCliService:
    """Implementation part for TestsFlextCliService."""

    @staticmethod
    def test_model_command_skips_excluded_fields() -> None:
        """Exclude model fields marked private from the generated CLI surface."""

        class ExcludedFieldModel(m.BaseModel):
            visible: str = m.Field(..., description="Visible", validate_default=True)
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
        tm.that(u.Cli.process_succeeded(help_result.value.outcome), eq=True)
        tm.that(help_result.value.stdout, has="--visible")
        tm.that("--hidden" in help_result.value.stdout, eq=False)

    @staticmethod
    def test_create_app_with_common_params_rejects_trace_without_debug() -> None:
        """Fail the invocation when shared flags cannot apply to the settings."""
        app = cli.create_app_with_common_params(name="warn-app", help_text="Warn app")
        cli.register_command(app, name="ok", help_text="OK", command=lambda: True)
        trace_before = settings.trace

        invoke_result = cli.invoke_app(app, args=["--trace", "ok"])

        tm.ok(invoke_result)
        tm.that(u.Cli.process_succeeded(invoke_result.value.outcome), eq=False)
        tm.that(invoke_result.value.stderr, has="debug")
        tm.that(settings.trace, eq=trace_before)

    @staticmethod
    def test_create_app_with_common_params_no_flags_keeps_settings() -> None:
        """Preserve settings when the invocation supplies no shared flags."""
        app = cli.create_app_with_common_params(
            name="identity-app",
            help_text="Identity app",
        )
        cli.register_command(app, name="ok", help_text="OK", command=lambda: True)
        shared_flags = {"debug", "trace", "verbose", "quiet", "log_level"}
        flags_before = settings.model_dump(include=shared_flags)

        invoke_result = cli.invoke_app(app, args=["ok"])

        tm.ok(invoke_result)
        tm.that(u.Cli.process_succeeded(invoke_result.value.outcome), eq=True)
        tm.that(settings.model_dump(include=shared_flags), eq=flags_before)

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

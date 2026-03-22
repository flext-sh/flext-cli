"""FLEXT CLI Extended Coverage Tests.

Tests specifically targeting uncovered lines in flext_cli.cli.FlextCliCli.
Focuses on global callbacks, helper functions, and edge cases.
"""

from __future__ import annotations

import logging
from unittest.mock import patch

import click
import typer
from flext_core import FlextRuntime
from flext_tests import tm
from typer.testing import CliRunner

from flext_cli import FlextCliCli, FlextCliSettings
from tests import m, t


class TestsCliCliExtended:
    """Extended test suite for FlextCliCli coverage."""

    def test_global_callback_logic(self) -> None:
        """Test global callback logic in create_app_with_common_params."""
        cli = FlextCliCli()
        mock_config_instance = FlextCliSettings.get_global()
        app = cli.create_app_with_common_params(
            "test_app", "Test App", config=mock_config_instance
        )

        @app.command()
        def hello() -> None:
            click.echo("Hello")

        runner = CliRunner()
        with patch.t.NormalizedValue(
            FlextRuntime, "reconfigure_structlog"
        ) as mock_reconfigure:
            with patch.t.NormalizedValue(
                FlextCliSettings, "get_global"
            ) as mock_get_config:
                mock_get_config.return_value = mock_config_instance
                result = runner.invoke(app, ["--debug", "hello"])
                tm.that(result.exit_code, eq=0)
                tm.that("Hello" in result.stdout, eq=True)
                mock_reconfigure.assert_called()
                call_args = mock_reconfigure.call_args[1]
                tm.that(call_args["log_level"], eq=logging.DEBUG)

    def test_global_callback_quiet(self) -> None:
        """Test global callback with quiet flag."""
        cli = FlextCliCli()
        mock_config_instance = FlextCliSettings.get_global()
        app = cli.create_app_with_common_params(
            "test_app", "Test App", config=mock_config_instance
        )

        @app.command()
        def hello() -> None:
            click.echo("Hello")

        runner = CliRunner()
        with patch.t.NormalizedValue(
            FlextRuntime, "reconfigure_structlog"
        ) as mock_reconfigure:
            result = runner.invoke(app, ["--quiet", "hello"])
            tm.that(result.exit_code, eq=0)
            mock_reconfigure.assert_called()

    def test_param_types_extended(self) -> None:
        """Test remaining parameter types."""
        cli = FlextCliCli()
        uuid_type = cli.get_uuid_type()
        tm.that(isinstance(uuid_type, type(click.UUID)), eq=True)
        tuple_type = cli.get_tuple_type([str, int])
        tm.that(isinstance(tuple_type, click.Tuple), eq=True)
        tm.that(len(tuple_type.types), eq=2)
        tm.that(cli.get_bool_type() is bool, eq=True)
        tm.that(cli.get_string_type() is str, eq=True)
        tm.that(cli.get_int_type() is int, eq=True)
        tm.that(cli.get_float_type() is float, eq=True)

    def test_confirm_logic_extended(self) -> None:
        """Test confirm logic with various scenarios."""
        cli = FlextCliCli()
        config = m.Cli.ConfirmConfig.model_construct(default=True, prompt_suffix="?")
        with patch("typer.confirm") as mock_confirm:
            mock_confirm.return_value = True
            result = cli.confirm("Continue?", config=config)
            tm.ok(result)
            tm.that(result.value is True, eq=True)
            mock_confirm.assert_called_with(
                text="Continue?",
                default=True,
                abort=False,
                prompt_suffix="?",
                show_default=True,
                err=False,
            )
            mock_confirm.side_effect = typer.Abort()
            result = cli.confirm("Continue?", abort=True)
            tm.fail(result)
            tm.that("User aborted" in str(result.error), eq=True)

    def test_prompt_logic_extended(self) -> None:
        """Test prompt logic with various scenarios."""
        cli = FlextCliCli()
        with patch("typer.prompt") as mock_prompt:
            mock_prompt.return_value = "user_input"
            result = cli.prompt("Name", default="guest")
            tm.ok(result)
            tm.that(result.value, eq="user_input")
            mock_prompt.side_effect = typer.Abort()
            result = cli.prompt("Name")
            tm.fail(result)
            tm.that("User aborted" in str(result.error), eq=True)

    def test_utility_wrappers(self) -> None:
        """Test simple utility wrappers."""
        cli = FlextCliCli()
        with patch("click.clear") as mock_clear:
            result = cli.clear_screen()
            tm.ok(result)
            mock_clear.assert_called_once()
        with patch("click.pause") as mock_pause:
            result = cli.pause(info="Press any key")
            tm.ok(result)
            mock_pause.assert_called_with(info="Press any key")

    def test_create_option_decorator_helpers(self) -> None:
        """Test helper functions inside create_option_decorator via execution."""
        cli = FlextCliCli()
        deco = cli.create_option_decorator(
            "--flag", required=True, default=False, help_text="A flag"
        )

        def cmd_impl(*args: t.Scalar, **kwargs: t.Scalar) -> str:
            _ = (args, kwargs)
            return "ok"

        cmd = deco(cmd_impl)
        click_params = getattr(cmd, "__click_params__", None)
        if isinstance(click_params, list):
            tm.that(len(click_params) > 0, eq=True)
            click_info = click_params[0]
            tm.that(click_info.required is True, eq=True)
            tm.that(click_info.default is False, eq=True)
            tm.that(click_info.help, eq="A flag")
        else:
            msg = "cmd should have __click_params__ attribute"
            raise AssertionError(msg)

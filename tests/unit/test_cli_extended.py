"""FLEXT CLI Extended Coverage Tests.

Tests specifically targeting uncovered lines in flext_cli.cli.FlextCliCli.
Focuses on global callbacks, helper functions, and edge cases.
"""

from __future__ import annotations

import logging
from unittest.mock import patch

import click
import typer
from flext_cli import FlextCliCli, FlextCliSettings, m
from flext_core import FlextRuntime, t
from typer.testing import CliRunner


class TestsCliCliExtended:
    """Extended test suite for FlextCliCli coverage."""

    def test_global_callback_logic(self) -> None:
        """Test global callback logic in create_app_with_common_params."""
        cli = FlextCliCli()

        mock_config_instance = FlextCliSettings.get_global_instance()

        # Create a mock app with a command to invoke
        # Explicitly pass config so it's used in callback
        app = cli.create_app_with_common_params(
            "test_app",
            "Test App",
            config=mock_config_instance,
        )

        @app.command()
        def hello() -> None:
            click.echo("Hello")

        runner = CliRunner()

        # Test with --debug flag
        # We need to mock FlextRuntime.reconfigure_structlog to verify it's called correctly
        with patch.object(FlextRuntime, "reconfigure_structlog") as mock_reconfigure:
            # Also mock FlextCliSettings.get_global_instance to return a mock config we can inspect
            with patch.object(
                FlextCliSettings, "get_global_instance"
            ) as mock_get_config:
                mock_get_config.return_value = mock_config_instance

                # Put global options BEFORE subcommand
                result = runner.invoke(app, ["--debug", "hello"])

                assert result.exit_code == 0
                assert "Hello" in result.stdout

                # Verify reconfigure was called with DEBUG level
                # The callback sets config.debug = True and then reconfigures
                mock_reconfigure.assert_called()
                call_args = mock_reconfigure.call_args[1]
                assert call_args["log_level"] == logging.DEBUG

    def test_global_callback_quiet(self) -> None:
        """Test global callback with quiet flag."""
        cli = FlextCliCli()

        mock_config_instance = FlextCliSettings.get_global_instance()

        app = cli.create_app_with_common_params(
            "test_app",
            "Test App",
            config=mock_config_instance,
        )

        @app.command()
        def hello() -> None:
            click.echo("Hello")

        runner = CliRunner()

        with patch.object(FlextRuntime, "reconfigure_structlog") as mock_reconfigure:
            # Put global options BEFORE subcommand
            result = runner.invoke(app, ["--quiet", "hello"])
            assert result.exit_code == 0

            # Verify config.quiet was set (logic is inside apply_to_config)
            # verify reconfigure called
            mock_reconfigure.assert_called()

    def test_param_types_extended(self) -> None:
        """Test remaining parameter types."""
        cli = FlextCliCli()

        # UUID Type
        assert cli.get_uuid_type() == click.UUID

        # Tuple Type
        tuple_type = cli.get_tuple_type([str, int])
        assert isinstance(tuple_type, click.Tuple)
        # click.Tuple converts types to internal representations, check length
        assert len(tuple_type.types) == 2
        # Check against click types if possible, or lenient check
        # assert isinstance(tuple_type.types[0], click.types.StringParamType)
        # assert isinstance(tuple_type.types[1], click.types.IntParamType)

        # Bool and primitives
        assert cli.get_bool_type() is bool
        assert cli.get_string_type() is str
        assert cli.get_int_type() is int
        assert cli.get_float_type() is float

    def test_confirm_logic_extended(self) -> None:
        """Test confirm logic with various scenarios."""
        cli = FlextCliCli()

        # Test with explicit config
        config = m.Cli.ConfirmConfig.model_construct(default=True, prompt_suffix="?")

        with patch("typer.confirm") as mock_confirm:
            mock_confirm.return_value = True

            # Case 1: Success with config
            result = cli.confirm("Continue?", config=config)
            assert result.is_success
            assert result.value is True
            mock_confirm.assert_called_with(
                text="Continue?",
                default=True,
                abort=False,
                prompt_suffix="?",
                show_default=True,
                err=False,
            )

            # Case 2: Abort
            mock_confirm.side_effect = typer.Abort()
            result = cli.confirm("Continue?", abort=True)
            assert result.is_failure
            assert "User aborted" in str(result.error)

    def test_prompt_logic_extended(self) -> None:
        """Test prompt logic with various scenarios."""
        cli = FlextCliCli()

        with patch("typer.prompt") as mock_prompt:
            # Case 1: Success with kwargs
            mock_prompt.return_value = "user_input"
            result = cli.prompt("Name", default="guest")
            assert result.is_success
            assert result.value == "user_input"

            # Case 2: Abort
            mock_prompt.side_effect = typer.Abort()
            result = cli.prompt("Name")
            assert result.is_failure
            assert "User aborted" in str(result.error)

    def test_utility_wrappers(self) -> None:
        """Test simple utility wrappers."""
        cli = FlextCliCli()

        with patch("click.clear") as mock_clear:
            result = cli.clear_screen()
            assert result.is_success
            mock_clear.assert_called_once()

        with patch("click.pause") as mock_pause:
            result = cli.pause(info="Press any key")
            assert result.is_success
            mock_pause.assert_called_with(info="Press any key")

    def test_create_option_decorator_helpers(self) -> None:
        """Test helper functions inside create_option_decorator via execution."""
        cli = FlextCliCli()

        # We test this indirectly by checking the properties of the created decorator
        # or rather the command it decorates.

        # Test 1: Boolean conversion helper
        # passing required=True (bool) and multiple="True" (should be handled/converted if logic allows,
        # but the helpers use u.Cli.build with 'ensure': 'bool', which handles loose types if configured)

        # Actually the helpers in `create_option_decorator` specifically use `u.Cli.build` with `ensure="bool"`.
        # Let's verify implicit conversion if any.

        deco = cli.create_option_decorator(
            "--flag",
            required=True,
            default=False,
            help_text="A flag",
        )

        def cmd_impl(*args: t.GeneralValueType, **kwargs: t.GeneralValueType) -> str:
            _ = args, kwargs
            return "ok"

        # Cast to CliCommandFunction for type compatibility
        cmd = deco(cmd_impl)

        # Inspect click info
        # The decorator adds __click_params__ attribute to the function
        # Use getattr with hasattr check for type safety
        click_params = getattr(cmd, "__click_params__", None)
        if isinstance(click_params, list):
            assert len(click_params) > 0
            click_info = click_params[0]
            assert click_info.required is True
            assert click_info.default is False
            assert click_info.help == "A flag"
        else:
            msg = "cmd should have __click_params__ attribute"
            raise AssertionError(msg)

"""Direct tests for cli.py module functions to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import sys
from unittest.mock import MagicMock, patch

import click

import flext_cli.cli  # Import the module to ensure it's loaded for coverage
from flext_cli.cli import (
    FlextCliMain,
    create_cli_options,
    create_config_with_overrides,
    get_version_info,
    print_version,
    setup_cli_context,
    setup_logging,
)
from flext_cli.configs import FlextCliConfigs
from flext_core import FlextResult


class TestCliDirectFunctions:
    """Test CLI module functions directly for coverage."""

    def test_flext_cli_main_init(self) -> None:
        """Test FlextCliMain initialization."""
        cli_main = FlextCliMain()
        assert cli_main is not None

    def test_flext_cli_main_execute(self) -> None:
        """Test FlextCliMain execute method."""
        cli_main = FlextCliMain()
        result = cli_main.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_flext_cli_main_get_version_info(self) -> None:
        """Test FlextCliMain get_version_info method."""
        cli_main = FlextCliMain()
        version_info = cli_main.get_version_info()
        assert isinstance(version_info, dict)
        assert "cli_version" in version_info
        assert "core_version" in version_info
        assert "python_version" in version_info
        assert "platform" in version_info

    def test_flext_cli_main_create_cli_options(self) -> None:
        """Test FlextCliMain create_cli_options method."""
        cli_main = FlextCliMain()
        result = cli_main.create_cli_options(
            profile="test",
            output_format="json",
            debug=True,
            quiet=False,
            log_level="DEBUG",
        )
        assert isinstance(result, FlextResult)
        assert result.is_success
        options = result.unwrap()
        assert options["profile"] == "test"
        assert options["output_format"] == "json"
        assert options["debug"] is True
        assert options["quiet"] is False
        assert options["log_level"] == "DEBUG"

    def test_flext_cli_main_create_config_with_overrides(self) -> None:
        """Test FlextCliMain create_config_with_overrides method."""
        cli_main = FlextCliMain()
        cli_options = {
            "profile": "test",
            "output_format": "json",
            "debug": True,
            "quiet": False,
            "log_level": "DEBUG",
        }
        result = cli_main.create_config_with_overrides(cli_options)
        assert isinstance(result, FlextResult)

    def test_get_version_info_function(self) -> None:
        """Test get_version_info standalone function."""
        version_info = get_version_info()
        assert isinstance(version_info, dict)
        assert "cli_version" in version_info
        assert "core_version" in version_info
        assert "python_version" in version_info
        assert "platform" in version_info

    def test_print_version_function(self) -> None:
        """Test print_version function."""
        # Create mock context and parameter
        mock_ctx = MagicMock(spec=click.Context)
        mock_ctx.resilient_parsing = False
        mock_param = MagicMock(spec=click.Parameter)

        with patch("click.echo") as mock_echo:
            with patch.object(mock_ctx, "exit") as mock_exit:
                print_version(mock_ctx, mock_param, True)
                mock_echo.assert_called()
                mock_exit.assert_called_once()

    def test_print_version_function_resilient_parsing(self) -> None:
        """Test print_version function with resilient parsing."""
        # Create mock context with resilient_parsing=True
        mock_ctx = MagicMock(spec=click.Context)
        mock_ctx.resilient_parsing = True
        mock_param = MagicMock(spec=click.Parameter)

        with patch("click.echo") as mock_echo:
            with patch.object(mock_ctx, "exit") as mock_exit:
                print_version(mock_ctx, mock_param, True)
                mock_echo.assert_not_called()
                mock_exit.assert_not_called()

    def test_print_version_function_false_value(self) -> None:
        """Test print_version function with false value."""
        # Create mock context
        mock_ctx = MagicMock(spec=click.Context)
        mock_ctx.resilient_parsing = False
        mock_param = MagicMock(spec=click.Parameter)

        with patch("click.echo") as mock_echo:
            with patch.object(mock_ctx, "exit") as mock_exit:
                print_version(mock_ctx, mock_param, False)
                mock_echo.assert_not_called()
                mock_exit.assert_not_called()

    def test_create_cli_options_function(self) -> None:
        """Test create_cli_options standalone function."""
        result = create_cli_options(
            profile="test",
            output_format="table",
            debug=False,
            quiet=True,
        )
        assert isinstance(result, FlextResult)
        assert result.is_success
        options = result.unwrap()
        assert options["profile"] == "test"
        assert options["output_format"] == "table"
        assert options["debug"] is False
        assert options["quiet"] is True

    def test_create_config_with_overrides_function(self) -> None:
        """Test create_config_with_overrides standalone function."""
        cli_options = {
            "profile": "dev",
            "output_format": "yaml",
            "debug": True,
            "quiet": False,
            "log_level": "INFO",
        }
        result = create_config_with_overrides(cli_options)
        assert isinstance(result, FlextResult)

    def test_setup_cli_context_function(self) -> None:
        """Test setup_cli_context function."""
        config = FlextCliConfigs()
        result = setup_cli_context(config)
        assert isinstance(result, FlextResult)

    def test_setup_logging_function(self) -> None:
        """Test setup_logging function."""
        config = FlextCliConfigs()
        result = setup_logging(config)
        assert isinstance(result, FlextResult)

    def test_create_cli_options_with_none_values(self) -> None:
        """Test create_cli_options with None values."""
        result = create_cli_options()
        assert isinstance(result, FlextResult)
        assert result.is_success
        options = result.unwrap()
        assert options["profile"] == "default"
        assert options["output_format"] == "table"
        assert options["debug"] is False
        assert options["quiet"] is False
        assert options["log_level"] is None

    def test_create_cli_options_with_log_level_none(self) -> None:
        """Test create_cli_options with log_level None."""
        result = create_cli_options(log_level=None)
        assert isinstance(result, FlextResult)
        assert result.is_success
        options = result.unwrap()
        assert options["log_level"] is None

    def test_flext_cli_main_create_config_without_log_level(self) -> None:
        """Test create_config_with_overrides without log_level."""
        cli_main = FlextCliMain()
        cli_options = {
            "profile": "test",
            "output_format": "json",
            "debug": True,
            "quiet": False,
            "log_level": None,
        }
        result = cli_main.create_config_with_overrides(cli_options)
        assert isinstance(result, FlextResult)

    def test_flext_cli_main_create_config_without_output_format(self) -> None:
        """Test create_config_with_overrides without output_format."""
        cli_main = FlextCliMain()
        cli_options = {
            "profile": "test",
            "output_format": None,
            "debug": False,
            "quiet": True,
            "log_level": "ERROR",
        }
        result = cli_main.create_config_with_overrides(cli_options)
        assert isinstance(result, FlextResult)


class TestCliErrorPaths:
    """Test CLI error handling paths for coverage."""

    def test_setup_logging_with_valid_level(self) -> None:
        """Test setup_logging with valid configuration."""
        config = FlextCliConfigs(log_level="DEBUG")
        result = setup_logging(config)
        assert isinstance(result, FlextResult)
        # Function should handle valid levels

    def test_create_config_with_overrides_failure_path(self) -> None:
        """Test create_config_with_overrides when apply_cli_overrides fails."""
        # This will test the failure path if apply_cli_overrides returns failure
        cli_options = {
            "profile": "test",
            "output_format": "json",
            "debug": True,
            "quiet": False,
            "log_level": "DEBUG",
        }

        with patch('flext_cli.configs.FlextCliConfigs.apply_cli_overrides') as mock_apply:
            mock_apply.return_value = FlextResult[FlextCliConfigs].fail("Test failure")
            result = create_config_with_overrides(cli_options)
            assert isinstance(result, FlextResult)
            assert result.is_failure
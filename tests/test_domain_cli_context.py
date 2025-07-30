"""Tests for domain CLI context in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import io
from unittest.mock import Mock

import pytest
from flext_cli.core.base import CLIContext
from flext_cli.utils.config import CLIConfig, CLISettings
from rich.console import Console


class TestCLIContext:
    """Test cases for CLIContext domain class."""

    @pytest.fixture
    def mock_console(self) -> Console:
        """Create a mock console for testing."""
        return Console(file=io.StringIO(), width=80)

    @pytest.fixture
    def cli_config(self) -> CLIConfig:
        """Create a CLI config for testing."""
        return CLIConfig(
            debug=True,
            verbose=True,
            quiet=False,
            profile="test",
            output_format="json",
        )

    @pytest.fixture
    def cli_settings(self) -> CLISettings:
        """Create CLI settings for testing."""
        return CLISettings(
            debug=True,
            log_level="DEBUG",
            project_name="test-project",
        )

    @pytest.fixture
    def cli_context(
        self,
        cli_config: CLIConfig,
        cli_settings: CLISettings,
        mock_console: Console,
    ) -> CLIContext:
        """Create a CLI context for testing."""
        return CLIContext(
            config=cli_config,
            settings=cli_settings,
            console=mock_console,
        )

    def test_context_initialization(
        self,
        cli_config: CLIConfig,
        cli_settings: CLISettings,
        mock_console: Console,
    ) -> None:
        """Test CLI context initialization."""
        context = CLIContext(
            config=cli_config,
            settings=cli_settings,
            console=mock_console,
        )

        assert context.config is cli_config
        assert context.settings is cli_settings
        assert context.console is mock_console

    def test_is_debug_property(self, cli_context: CLIContext) -> None:
        """Test is_debug property."""
        # Should return True because config.verbose is True
        if not (cli_context.is_debug):
            raise AssertionError(f"Expected True, got {cli_context.is_debug}")

    def test_is_debug_property_false(
        self,
        cli_settings: CLISettings,
        mock_console: Console,
    ) -> None:
        """Test is_debug property when verbose is False."""
        config = CLIConfig(verbose=False)
        context = CLIContext(
            config=config,
            settings=cli_settings,
            console=mock_console,
        )

        if context.is_debug:
            raise AssertionError(f"Expected False, got {context.is_debug}")

    def test_is_quiet_property(self, cli_context: CLIContext) -> None:
        """Test is_quiet property."""
        # Should return False because config.quiet is False
        if cli_context.is_quiet:
            raise AssertionError(f"Expected False, got {cli_context.is_quiet}")

    def test_is_quiet_property_true(
        self,
        cli_settings: CLISettings,
        mock_console: Console,
    ) -> None:
        """Test is_quiet property when quiet is True."""
        config = CLIConfig(quiet=True)
        context = CLIContext(
            config=config,
            settings=cli_settings,
            console=mock_console,
        )

        if not (context.is_quiet):
            raise AssertionError(f"Expected True, got {context.is_quiet}")

    def test_is_verbose_property(self, cli_context: CLIContext) -> None:
        """Test is_verbose property."""
        # Should return True because config.verbose is True
        if not (cli_context.is_verbose):
            raise AssertionError(f"Expected True, got {cli_context.is_verbose}")

    def test_is_verbose_property_false(
        self,
        cli_settings: CLISettings,
        mock_console: Console,
    ) -> None:
        """Test is_verbose property when verbose is False."""
        config = CLIConfig(verbose=False)
        context = CLIContext(
            config=config,
            settings=cli_settings,
            console=mock_console,
        )

        if context.is_verbose:
            raise AssertionError(f"Expected False, got {context.is_verbose}")

    def test_print_debug_when_debug_enabled(self, cli_context: CLIContext) -> None:
        """Test print_debug when debug mode is enabled."""
        # Mock the console print method
        cli_context.console.print = Mock()

        cli_context.print_debug("Test debug message")

        cli_context.console.print.assert_called_once_with(
            "[dim][DEBUG][/dim] Test debug message"
        )

    def test_print_debug_when_debug_disabled(
        self,
        cli_settings: CLISettings,
        mock_console: Console,
    ) -> None:
        """Test print_debug when debug mode is disabled."""
        config = CLIConfig(verbose=False)
        context = CLIContext(
            config=config,
            settings=cli_settings,
            console=mock_console,
        )

        # Mock the console print method
        context.console.print = Mock()

        context.print_debug("Test debug message")

        # Should not be called because debug is disabled
        context.console.print.assert_not_called()

    def test_print_info_when_not_quiet(self, cli_context: CLIContext) -> None:
        """Test print_info when not in quiet mode."""
        # Mock the console print method
        cli_context.console.print = Mock()

        cli_context.print_info("Test info message")

        cli_context.console.print.assert_called_once_with(
            "[blue][INFO][/blue] Test info message"
        )

    def test_print_info_when_quiet(
        self,
        cli_settings: CLISettings,
        mock_console: Console,
    ) -> None:
        """Test print_info when in quiet mode."""
        config = CLIConfig(quiet=True)
        context = CLIContext(
            config=config,
            settings=cli_settings,
            console=mock_console,
        )

        # Mock the console print method
        context.console.print = Mock()

        context.print_info("Test info message")

        # Should not be called because quiet mode is enabled
        context.console.print.assert_not_called()

    def test_print_success(self, cli_context: CLIContext) -> None:
        """Test print_success method."""
        # Mock the console print method
        cli_context.console.print = Mock()

        cli_context.print_success("Test success message")

        cli_context.console.print.assert_called_once_with(
            "[green][SUCCESS][/green] Test success message"
        )

    def test_print_warning(self, cli_context: CLIContext) -> None:
        """Test print_warning method."""
        # Mock the console print method
        cli_context.console.print = Mock()

        cli_context.print_warning("Test warning message")

        cli_context.console.print.assert_called_once_with(
            "[yellow][WARNING][/yellow] Test warning message"
        )

    def test_print_error(self, cli_context: CLIContext) -> None:
        """Test print_error method."""
        # Mock the console print method
        cli_context.console.print = Mock()

        cli_context.print_error("Test error message")

        cli_context.console.print.assert_called_once_with(
            "[red][ERROR][/red] Test error message"
        )

    def test_print_verbose_when_verbose_enabled(self, cli_context: CLIContext) -> None:
        """Test print_verbose when verbose mode is enabled."""
        # Mock the console print method
        cli_context.console.print = Mock()

        cli_context.print_verbose("Test verbose message")

        cli_context.console.print.assert_called_once_with(
            "[dim][VERBOSE][/dim] Test verbose message"
        )

    def test_print_verbose_when_verbose_disabled(
        self,
        cli_settings: CLISettings,
        mock_console: Console,
    ) -> None:
        """Test print_verbose when verbose mode is disabled."""
        config = CLIConfig(verbose=False)
        context = CLIContext(
            config=config,
            settings=cli_settings,
            console=mock_console,
        )

        # Mock the console print method
        context.console.print = Mock()

        context.print_verbose("Test verbose message")

        # Should not be called because verbose mode is disabled
        context.console.print.assert_not_called()

    def test_all_print_methods_with_different_messages(
        self, cli_context: CLIContext
    ) -> None:
        """Test all print methods with different message content."""
        # Mock the console print method
        cli_context.console.print = Mock()

        # Test different message types
        cli_context.print_debug("Debug: Operation started")
        cli_context.print_info("Info: Processing data")
        cli_context.print_success("Success: Operation completed")
        cli_context.print_warning("Warning: Deprecated feature used")
        cli_context.print_error("Error: Invalid input")
        cli_context.print_verbose("Verbose: Detailed operation info")

        # Verify all calls were made
        if cli_context.console.print.call_count != 6:
            raise AssertionError(
                f"Expected {6}, got {cli_context.console.print.call_count}"
            )

        # Verify specific calls
        expected_calls = [
            "[dim][DEBUG][/dim] Debug: Operation started",
            "[blue][INFO][/blue] Info: Processing data",
            "[green][SUCCESS][/green] Success: Operation completed",
            "[yellow][WARNING][/yellow] Warning: Deprecated feature used",
            "[red][ERROR][/red] Error: Invalid input",
            "[dim][VERBOSE][/dim] Verbose: Detailed operation info",
        ]

        actual_calls = [call[0][0] for call in cli_context.console.print.call_args_list]
        if actual_calls != expected_calls:
            raise AssertionError(f"Expected {expected_calls}, got {actual_calls}")

    def test_context_with_real_console_output(
        self,
        cli_config: CLIConfig,
        cli_settings: CLISettings,
    ) -> None:
        """Test context with real console output."""
        output = io.StringIO()
        console = Console(file=output, width=80)

        context = CLIContext(
            config=cli_config,
            settings=cli_settings,
            console=console,
        )

        # Test that messages are actually written to output
        context.print_success("Test message")
        output_content = output.getvalue()

        if "Test message" not in output_content:
            raise AssertionError(f"Expected {'Test message'} in {output_content}")
        assert "SUCCESS" in output_content

    def test_context_model_validation(self, mock_console: Console) -> None:
        """Test that context validates required fields."""
        # Should raise validation error if required fields are missing
        with pytest.raises(ValueError, match="validation error"):
            CLIContext()

        # Should work with all required fields
        config = CLIConfig()
        settings = CLISettings()

        context = CLIContext(
            config=config,
            settings=settings,
            console=mock_console,
        )

        assert isinstance(context, CLIContext)

    def test_context_arbitrary_types_allowed(
        self,
        cli_config: CLIConfig,
        cli_settings: CLISettings,
        mock_console: Console,
    ) -> None:
        """Test that context allows arbitrary types like Console."""
        # This should not raise validation error for Console type
        context = CLIContext(
            config=cli_config,
            settings=cli_settings,
            console=mock_console,
        )

        assert isinstance(context.console, Console)
        if not (context.model_config["arbitrary_types_allowed"]):
            raise AssertionError(
                f"Expected True, got {context.model_config['arbitrary_types_allowed']}"
            )

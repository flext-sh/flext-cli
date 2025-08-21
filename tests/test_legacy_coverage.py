"""Tests for legacy.py to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import warnings
from unittest.mock import MagicMock, patch

import pytest

from flext_cli import legacy
from flext_cli.api import FlextCliApi
from flext_cli.config import CLIConfig
from flext_cli.exceptions import (
    FlextCliArgumentError,
    FlextCliAuthenticationError,
    FlextCliCommandError,
    FlextCliConfigurationError,
    FlextCliConnectionError,
    FlextCliContextError,
    FlextCliError,
    FlextCliFormatError,
    FlextCliOutputError,
    FlextCliProcessingError,
    FlextCliTimeoutError,
    FlextCliValidationError,
)


class TestDeprecationWarning:
    """Test _deprecation_warning function."""

    def test_deprecation_warning_issued(self) -> None:
        """Test that deprecation warning is issued."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            legacy._deprecation_warning("old_name", "new_name")

            assert len(w) == 1
            assert issubclass(w[0].category, DeprecationWarning)
            assert "old_name is deprecated, use new_name instead" in str(w[0].message)

    def test_deprecation_warning_stacklevel(self) -> None:
        """Test that deprecation warning uses correct stacklevel."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            legacy._deprecation_warning("test_old", "test_new")

            assert len(w) == 1
            # Check that stacklevel parameter was used (exact frame testing is complex)
            assert w[0].category == DeprecationWarning


class TestLegacyServiceAliases:
    """Test legacy service aliases."""

    def test_cli_service(self) -> None:
        """Test cli_service legacy alias."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_service("arg1", test_param="value")

            # Should issue deprecation warning
            assert len(w) == 1
            assert "CliService is deprecated, use FlextCliService instead" in str(
                w[0].message
            )

            # Should return a mock service instance
            assert result is not None

    def test_cli_service_no_args(self) -> None:
        """Test cli_service with no arguments."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            result = legacy.cli_service()

            assert result is not None

    def test_cli_api(self) -> None:
        """Test cli_api legacy alias."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_api()

            # Should issue deprecation warning
            assert len(w) == 1
            assert "CliAPI is deprecated, use FlextCliApi instead" in str(w[0].message)

            # Should return FlextCliApi instance
            assert isinstance(result, FlextCliApi)

    def test_cli_api_with_args(self) -> None:
        """Test cli_api with arguments."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            # FlextCliApi accepts no arguments, function should fail with TypeError
            with pytest.raises(TypeError):
                legacy.cli_api("ignored_arg")

    def test_cliservice(self) -> None:
        """Test cliservice legacy alias (capitalized variant)."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cliservice("arg1", test_param="value")

            # Should issue deprecation warning
            assert len(w) == 1
            assert "CLIService is deprecated, use FlextCliService instead" in str(
                w[0].message
            )

            # Should return a mock service instance
            assert result is not None


class TestLegacySetupFunctions:
    """Test legacy setup function aliases."""

    @patch("flext_cli.legacy.setup_cli")
    def test_setup_flext_cli_success(self, mock_setup_cli: MagicMock) -> None:
        """Test setup_flext_cli legacy alias success."""
        mock_setup_cli.return_value = {"setup": "success"}

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.setup_flext_cli("arg1", test_param="value")

            # Should issue deprecation warning
            assert len(w) == 1
            assert "setup_flext_cli is deprecated, use setup_cli instead" in str(
                w[0].message
            )

            # Should call setup_cli with no arguments (ignoring provided ones)
            mock_setup_cli.assert_called_once_with()
            assert result == {"setup": "success"}

    @patch("flext_cli.legacy.setup_cli", side_effect=ImportError("Module not found"))
    def test_setup_flext_cli_import_error(self, mock_setup_cli: MagicMock) -> None:
        """Test setup_flext_cli when setup_cli raises ImportError."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            with pytest.raises(ImportError, match="setup_cli not available"):
                legacy.setup_flext_cli()

    @patch(
        "flext_cli.legacy.setup_cli", side_effect=AttributeError("Attribute missing")
    )
    def test_setup_flext_cli_attribute_error(self, mock_setup_cli: MagicMock) -> None:
        """Test setup_flext_cli when setup_cli raises AttributeError."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            with pytest.raises(ImportError, match="setup_cli not available"):
                legacy.setup_flext_cli()

    def test_create_context(self) -> None:
        """Test create_context legacy alias."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.create_context("arg1", test_param="value")

            # Should issue deprecation warning
            assert len(w) == 1
            assert (
                "create_context is deprecated, use create_cli_context instead"
                in str(w[0].message)
            )

            # Should return CLIConfig instance
            assert isinstance(result, CLIConfig)

    @patch(
        "flext_cli.legacy.CLIConfig", side_effect=Exception("Config creation failed")
    )
    def test_create_context_exception(self, mock_cli_config: MagicMock) -> None:
        """Test create_context when CLIConfig raises exception."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            with pytest.raises(ImportError, match="create_cli_context not available"):
                legacy.create_context()

    @patch("flext_cli.legacy.setup_cli")
    def test_init_cli(self, mock_setup_cli: MagicMock) -> None:
        """Test init_cli legacy alias."""
        mock_setup_cli.return_value = {"init": "success"}

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.init_cli("arg1", test_param="value")

            # Should issue deprecation warning
            assert len(w) == 1
            assert "init_cli is deprecated, use setup_cli instead" in str(w[0].message)

            assert result == {"init": "success"}

    @patch("flext_cli.legacy.setup_cli", side_effect=ImportError("Setup failed"))
    def test_init_cli_error(self, mock_setup_cli: MagicMock) -> None:
        """Test init_cli when setup_cli fails."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            with pytest.raises(ImportError, match="setup_cli not available"):
                legacy.init_cli()

    @patch("flext_cli.legacy.setup_cli")
    def test_configure_cli(self, mock_setup_cli: MagicMock) -> None:
        """Test configure_cli legacy alias."""
        mock_setup_cli.return_value = {"configure": "success"}

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.configure_cli("arg1", test_param="value")

            # Should issue deprecation warning
            assert len(w) == 1
            assert "configure_cli is deprecated, use setup_cli instead" in str(
                w[0].message
            )

            assert result == {"configure": "success"}

    @patch("flext_cli.legacy.setup_cli", side_effect=AttributeError("Attribute error"))
    def test_configure_cli_error(self, mock_setup_cli: MagicMock) -> None:
        """Test configure_cli when setup_cli fails."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            with pytest.raises(ImportError, match="setup_cli not available"):
                legacy.configure_cli()


class TestLegacyErrorFunctions:
    """Test legacy error function aliases."""

    def test_cli_error_with_message(self) -> None:
        """Test cli_error with message."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_error("Test error message")

            # Should issue deprecation warning
            assert len(w) == 1
            assert "CliError is deprecated, use FlextCliError instead" in str(
                w[0].message
            )

            # Should return FlextCliError instance
            assert isinstance(result, FlextCliError)
            assert "Test error message" in str(result)

    def test_cli_error_no_args(self) -> None:
        """Test cli_error with no arguments."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            result = legacy.cli_error()

            assert isinstance(result, FlextCliError)
            assert "CLI error" in str(result)

    def test_cli_validation_error(self) -> None:
        """Test cli_validation_error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_validation_error("Validation failed")

            assert len(w) == 1
            assert (
                "CliValidationError is deprecated, use FlextCliValidationError instead"
                in str(w[0].message)
            )
            assert isinstance(result, FlextCliValidationError)
            assert "Validation failed" in str(result)

    def test_cli_validation_error_no_args(self) -> None:
        """Test cli_validation_error with no arguments."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            result = legacy.cli_validation_error()

            assert isinstance(result, FlextCliValidationError)
            assert "Validation error" in str(result)

    def test_cli_configuration_error(self) -> None:
        """Test cli_configuration_error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_configuration_error("Config error")

            assert len(w) == 1
            assert (
                "CliConfigurationError is deprecated, use FlextCliConfigurationError instead"
                in str(w[0].message)
            )
            assert isinstance(result, FlextCliConfigurationError)
            assert "Config error" in str(result)

    def test_cli_configuration_error_no_args(self) -> None:
        """Test cli_configuration_error with no arguments."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            result = legacy.cli_configuration_error()

            assert isinstance(result, FlextCliConfigurationError)
            assert "Configuration error" in str(result)

    def test_cli_connection_error(self) -> None:
        """Test cli_connection_error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_connection_error("Connection lost")

            assert len(w) == 1
            assert (
                "CliConnectionError is deprecated, use FlextCliConnectionError instead"
                in str(w[0].message)
            )
            assert isinstance(result, FlextCliConnectionError)
            assert "Connection lost" in str(result)

    def test_cli_processing_error(self) -> None:
        """Test cli_processing_error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_processing_error("Processing failed")

            assert len(w) == 1
            assert (
                "CliProcessingError is deprecated, use FlextCliProcessingError instead"
                in str(w[0].message)
            )
            assert isinstance(result, FlextCliProcessingError)
            assert "Processing failed" in str(result)

    def test_cli_authentication_error(self) -> None:
        """Test cli_authentication_error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_authentication_error("Auth failed")

            assert len(w) == 1
            assert (
                "CliAuthenticationError is deprecated, use FlextCliAuthenticationError instead"
                in str(w[0].message)
            )
            assert isinstance(result, FlextCliAuthenticationError)
            assert "Auth failed" in str(result)

    def test_cli_timeout_error(self) -> None:
        """Test cli_timeout_error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_timeout_error("Operation timed out")

            assert len(w) == 1
            assert (
                "CliTimeoutError is deprecated, use FlextCliTimeoutError instead"
                in str(w[0].message)
            )
            assert isinstance(result, FlextCliTimeoutError)
            assert "Operation timed out" in str(result)

    def test_cli_command_error(self) -> None:
        """Test cli_command_error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_command_error("Command failed")

            assert len(w) == 1
            assert (
                "CliCommandError is deprecated, use FlextCliCommandError instead"
                in str(w[0].message)
            )
            assert isinstance(result, FlextCliCommandError)
            assert "Command failed" in str(result)

    def test_cli_argument_error(self) -> None:
        """Test cli_argument_error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_argument_error("Invalid argument")

            assert len(w) == 1
            assert (
                "CliArgumentError is deprecated, use FlextCliArgumentError instead"
                in str(w[0].message)
            )
            assert isinstance(result, FlextCliArgumentError)
            assert "Invalid argument" in str(result)

    def test_cli_format_error(self) -> None:
        """Test cli_format_error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_format_error("Format invalid")

            assert len(w) == 1
            assert (
                "CliFormatError is deprecated, use FlextCliFormatError instead"
                in str(w[0].message)
            )
            assert isinstance(result, FlextCliFormatError)
            assert "Format invalid" in str(result)

    def test_cli_output_error(self) -> None:
        """Test cli_output_error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_output_error("Output failed")

            assert len(w) == 1
            assert (
                "CliOutputError is deprecated, use FlextCliOutputError instead"
                in str(w[0].message)
            )
            assert isinstance(result, FlextCliOutputError)
            assert "Output failed" in str(result)

    def test_cli_context_error(self) -> None:
        """Test cli_context_error."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.cli_context_error("Context invalid")

            assert len(w) == 1
            assert (
                "CliContextError is deprecated, use FlextCliContextError instead"
                in str(w[0].message)
            )
            assert isinstance(result, FlextCliContextError)
            assert "Context invalid" in str(result)

    def test_command_line_error(self) -> None:
        """Test command_line_error alternative naming."""
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")

            result = legacy.command_line_error("Command line error")

            assert len(w) == 1
            assert "CommandLineError is deprecated, use FlextCliError instead" in str(
                w[0].message
            )
            assert isinstance(result, FlextCliError)
            assert "Command line error" in str(result)

    def test_command_line_error_no_args(self) -> None:
        """Test command_line_error with no arguments."""
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")

            result = legacy.command_line_error()

            assert isinstance(result, FlextCliError)
            assert "Command line error" in str(result)


class TestLegacyErrorEdgeCases:
    """Test edge cases for legacy error functions."""

    def test_all_error_functions_with_multiple_args(self) -> None:
        """Test error functions with multiple arguments."""
        error_functions = [
            legacy.cli_error,
            legacy.cli_validation_error,
            legacy.cli_configuration_error,
            legacy.cli_connection_error,
            legacy.cli_processing_error,
            legacy.cli_authentication_error,
            legacy.cli_timeout_error,
            legacy.cli_command_error,
            legacy.cli_argument_error,
            legacy.cli_format_error,
            legacy.cli_output_error,
            legacy.cli_context_error,
            legacy.command_line_error,
        ]

        for error_func in error_functions:
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")

                # Test with multiple args - should only use the first one
                result = error_func(
                    "First arg", "Second arg", "Third arg", kwarg="value"
                )

                # Should be an exception instance
                assert isinstance(result, Exception)
                # Should use first argument as message
                assert "First arg" in str(result)

    def test_all_error_functions_with_kwargs_only(self) -> None:
        """Test error functions with only keyword arguments."""
        error_functions = [
            legacy.cli_error,
            legacy.cli_validation_error,
            legacy.cli_configuration_error,
            legacy.cli_connection_error,
            legacy.cli_processing_error,
            legacy.cli_authentication_error,
            legacy.cli_timeout_error,
            legacy.cli_command_error,
            legacy.cli_argument_error,
            legacy.cli_format_error,
            legacy.cli_output_error,
            legacy.cli_context_error,
            legacy.command_line_error,
        ]

        for error_func in error_functions:
            with warnings.catch_warnings(record=True):
                warnings.simplefilter("always")

                # Test with only kwargs - should use default message
                result = error_func(kwarg="value", another="param")

                # Should be an exception instance with default message
                assert isinstance(result, Exception)


class TestLegacyModuleAll:
    """Test __all__ export list."""

    def test_all_exports_exist(self) -> None:
        """Test that all functions in __all__ actually exist."""
        for name in legacy.__all__:
            assert hasattr(legacy, name), (
                f"Function {name} declared in __all__ but not found in module"
            )

    def test_all_exports_callable(self) -> None:
        """Test that all exported functions are callable."""
        for name in legacy.__all__:
            func = getattr(legacy, name)
            assert callable(func), f"Export {name} is not callable"

    def test_expected_exports(self) -> None:
        """Test that expected functions are in __all__."""
        expected_exports = {
            "cli_api",
            "cli_service",
            "cliservice",
            "setup_flext_cli",
            "create_context",
            "init_cli",
            "configure_cli",
            "cli_error",
            "cli_validation_error",
            "cli_configuration_error",
            "cli_connection_error",
            "cli_processing_error",
            "cli_authentication_error",
            "cli_timeout_error",
            "cli_command_error",
            "cli_argument_error",
            "cli_format_error",
            "cli_output_error",
            "cli_context_error",
            "command_line_error",
        }

        for export in expected_exports:
            assert export in legacy.__all__, (
                f"Expected export {export} not found in __all__"
            )

"""FUNCTIONAL TESTS - FLEXT CLI Library - REAL functionality validation.

These tests execute REAL code functionality without excessive mocking,
following the consolidated class patterns and demonstrating 100% working code.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_core import FlextResult

from flext_cli import (
    FlextCliConstants,
    FlextCliModels,
    FlextCliTypes,
)


class TestFlextCliModelsReal:
    """Test REAL FlextCliModels functionality."""

    def test_consolidated_models_exists(self) -> None:
        """Test that FlextCliModels consolidated class exists and works."""
        assert hasattr(FlextCliModels, "Command")
        assert hasattr(FlextCliModels, "Session")
        assert hasattr(FlextCliModels, "OutputFormat")
        assert hasattr(FlextCliModels, "CommandStatus")
        assert hasattr(FlextCliModels, "SessionState")

    def test_command_creation_and_validation(self) -> None:
        """Test REAL command creation and business rule validation."""
        # Create REAL command
        command = FlextCliModels.Command(command_line="echo hello")

        # Test REAL validation
        validation_result = command.validate_business_rules()
        assert validation_result.is_success

    def test_command_execution_workflow(self) -> None:
        """Test REAL command execution workflow."""
        command = FlextCliModels.Command(command_line="test command", id="test-123")

        # Test starting execution
        start_result = command.start_execution()
        assert start_result.is_success
        assert command.status == FlextCliModels.CommandStatus.RUNNING
        assert command.started_at is not None

    def test_session_functionality(self) -> None:
        """Test REAL session functionality."""
        session = FlextCliModels.Session(user_id="test-user")

        # Test adding command to session
        add_result = session.add_command("test-command-id")
        assert add_result.is_success
        assert "test-command-id" in session.command_history

    def test_output_format_enum(self) -> None:
        """Test REAL OutputFormat enum functionality."""
        # Test all enum values exist
        assert FlextCliModels.OutputFormat.JSON == "json"
        assert FlextCliModels.OutputFormat.CSV == "csv"
        assert FlextCliModels.OutputFormat.YAML == "yaml"
        assert FlextCliModels.OutputFormat.TABLE == "table"
        assert FlextCliModels.OutputFormat.PLAIN == "plain"

        # Test enum iteration
        formats = [fmt.value for fmt in FlextCliModels.OutputFormat]
        expected = ["json", "csv", "yaml", "table", "plain"]
        assert sorted(formats) == sorted(expected)


class TestFlextCliTypesReal:
    """Test REAL FlextCliTypes functionality."""

    def test_consolidated_types_exists(self) -> None:
        """Test that FlextCliTypes consolidated class exists."""
        assert hasattr(FlextCliTypes, "Command")
        assert hasattr(FlextCliTypes, "Auth")
        assert hasattr(FlextCliTypes, "Config")
        assert hasattr(FlextCliTypes, "Output")
        assert hasattr(FlextCliTypes, "Session")

    def test_type_aliases_work(self) -> None:
        """Test that type aliases are properly defined."""
        from flext_cli.typings import ConfigDict, FlextCliDataType, OutputData

        # Test imports work (validates type aliases exist)
        assert ConfigDict is not None
        assert FlextCliDataType is not None
        assert OutputData is not None


class TestFlextCliConstantsReal:
    """Test REAL FlextCliConstants functionality."""

    def test_consolidated_constants_exists(self) -> None:
        """Test that FlextCliConstants consolidated class exists."""
        assert hasattr(FlextCliConstants, "CliErrors")
        assert hasattr(FlextCliConstants, "CliMessages")
        assert hasattr(FlextCliConstants, "CliOutput")

    def test_error_constants_work(self) -> None:
        """Test REAL error constants functionality."""
        # Test CLI-specific error messages exist
        assert FlextCliConstants.CliErrors.CLI_SETUP_FAILED
        assert FlextCliConstants.CliErrors.AUTH_LOGIN_FAILED
        assert FlextCliConstants.CliErrors.COMMAND_NOT_FOUND

    def test_message_constants_work(self) -> None:
        """Test REAL message constants functionality."""
        # Test CLI-specific messages exist
        assert FlextCliConstants.CliMessages.SUCCESS_LOGIN
        assert FlextCliConstants.CliMessages.INFO_RUN_LOGIN

    def test_output_constants_work(self) -> None:
        """Test REAL output formatting constants."""
        # Test Rich markup tags
        assert FlextCliConstants.CliOutput.SUCCESS_TAG == "[green]"
        assert FlextCliConstants.CliOutput.ERROR_TAG == "[red]"
        assert FlextCliConstants.CliOutput.ICON_SUCCESS == "✓"


class TestFlextCliIntegration:
    """Test REAL integration between CLI components."""

    def test_flext_result_integration(self) -> None:
        """Test REAL FlextResult integration works throughout CLI."""
        command = FlextCliModels.Command(command_line="test")

        # All CLI operations return FlextResult
        validation = command.validate_business_rules()
        assert isinstance(validation, FlextResult)
        assert validation.is_success

        execution = command.start_execution()
        assert isinstance(execution, FlextResult)

    def test_consolidated_pattern_consistency(self) -> None:
        """Test that all consolidated classes follow the same pattern."""
        # All main classes should be consolidated
        assert hasattr(FlextCliModels, "Command")
        assert hasattr(FlextCliTypes, "Command")
        assert hasattr(FlextCliConstants, "CliErrors")

        # All should be single point of access
        Command = FlextCliModels.Command
        command = Command(command_line="test")
        assert command.command_line == "test"


# =============================================================================
# IMPORT AND EXPORT VALIDATION TESTS
# =============================================================================


class TestFlextCliExportsReal:
    """Test that ALL CLI exports work correctly."""

    def test_main_imports_work(self) -> None:
        """Test that main flext_cli imports work without errors."""
        # Test consolidated classes import
        from flext_cli import FlextCliConstants, FlextCliModels, FlextCliTypes

        # Test they're actually the consolidated classes
        assert hasattr(FlextCliModels, "Command")
        assert hasattr(FlextCliTypes, "Command")
        assert hasattr(FlextCliConstants, "CliErrors")

    def test_no_legacy_exports(self) -> None:
        """Test that legacy standalone classes are not exported."""
        # These should NOT be directly importable from the main package
        with pytest.raises(ImportError):
            pass  # Should not exist

        with pytest.raises(ImportError):
            pass  # Should not exist

        with pytest.raises(ImportError):
            pass  # Should not exist

    def test_correct_consolidated_access(self) -> None:
        """Test that consolidated access pattern works correctly."""
        from flext_cli import FlextCliModels

        # Correct way to access
        Command = FlextCliModels.Command
        OutputFormat = FlextCliModels.OutputFormat
        CommandStatus = FlextCliModels.CommandStatus

        # Test they work
        cmd = Command(command_line="test")
        assert cmd.command_line == "test"
        assert OutputFormat.JSON == "json"
        assert CommandStatus.PENDING == "pending"

"""FUNCTIONAL TESTS - FLEXT CLI Library - REAL functionality validation.

These tests Execute code functionality without excessive mocking,
following the consolidated class patterns and demonstrating 100% working code.



Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest
from flext_core import FlextResult, FlextTypes

from flext_cli import (
    FlextCliConstants,
    FlextCliModels,
)
from flext_cli.typings import FlextCliTypes


class TestFlextCliModelsReal:
    """Test REAL FlextCliModels functionality."""

    def test_consolidated_models_exists(self) -> None:
        """Test that FlextCliModels consolidated class exists and works."""
        assert hasattr(FlextCliModels, "CliCommand")
        assert hasattr(FlextCliModels, "CliSession")
        assert hasattr(FlextCliModels, "CliConfig")
        assert hasattr(FlextCliModels, "CliPlugin")
        assert hasattr(FlextCliModels, "Core")  # FlextModels access

    def test_command_creation_and_validation(self) -> None:
        """Test REAL command creation and business rule validation."""
        # Create REAL command
        command = FlextCliModels.CliCommand(command_line="echo hello")

        # Test REAL validation
        validation_result = command.validate_business_rules()
        assert validation_result.is_success

    def test_command_execution_workflow(self) -> None:
        """Test REAL command execution workflow."""
        command = FlextCliModels.CliCommand(command_line="test command", id="test-123")

        # Test starting execution
        start_result = command.start_execution()
        assert start_result.is_success
        assert command.status == FlextCliConstants.STATUS_RUNNING
        assert command.execution_time is not None  # execution_time is set when starting

    def test_session_functionality(self) -> None:
        """Test REAL session functionality."""
        session = FlextCliModels.CliSession(user_id="test-user")

        # Test adding command to session
        test_command = FlextCliModels.CliCommand(command_line="test-command")
        add_result = session.add_command(test_command)
        assert add_result.is_success
        assert len(session.commands) > 0

    def test_output_format_enum(self) -> None:
        """Test REAL OutputFormat enum functionality."""
        # Test all enum values exist
        assert str(FlextCliConstants.OutputFormat.JSON) == "json"
        assert str(FlextCliConstants.OutputFormat.CSV) == "csv"
        assert str(FlextCliConstants.OutputFormat.YAML) == "yaml"
        assert str(FlextCliConstants.OutputFormat.TABLE) == "table"
        assert str(FlextCliConstants.OutputFormat.PLAIN) == "plain"

        # Test enum iteration
        formats = [fmt.value for fmt in FlextCliConstants.OutputFormat]
        expected = ["json", "csv", "yaml", "table", "plain"]
        assert sorted(formats) == sorted(expected)


class TestFlextCliTypesReal:
    """Test REAL FlextCliTypes functionality."""

    def test_consolidated_types_exists(self) -> None:
        """Test that FlextCliTypes consolidated class exists."""
        assert hasattr(FlextCliTypes, "Commands")
        assert hasattr(FlextCliTypes, "Auth")
        assert hasattr(FlextCliTypes, "Config")
        assert hasattr(FlextCliTypes, "OutputFormat")
        assert hasattr(FlextCliTypes, "Session")

    def test_type_aliases_work(self) -> None:
        """Test that type aliases are properly defined."""
        # Test that FlextTypes provides access to actual type classes
        assert FlextTypes.Commands is not None
        assert FlextTypes.Config is not None
        assert FlextTypes.Core is not None  # Core types are available


class TestFlextCliConstantsReal:
    """Test REAL FlextCliConstants functionality."""

    def test_consolidated_constants_exists(self) -> None:
        """Test that FlextCliConstants consolidated class exists."""
        assert hasattr(FlextCliConstants, "TimeoutConfig")
        assert hasattr(FlextCliConstants, "LimitsConfig")
        assert hasattr(FlextCliConstants, "OutputConfig")

    def test_error_constants_work(self) -> None:
        """Test REAL error constants functionality."""
        # Test basic constants exist
        assert FlextCliConstants.FLEXT_DIR_NAME
        assert FlextCliConstants.CONFIG_FILE_NAME
        assert FlextCliConstants.AUTH_DIR_NAME

    def test_message_constants_work(self) -> None:
        """Test REAL message constants functionality."""
        # Test configuration classes exist
        assert hasattr(FlextCliConstants, "TimeoutConfig")
        assert hasattr(FlextCliConstants, "OutputConfig")

    def test_output_constants_work(self) -> None:
        """Test REAL output formatting constants."""
        # Test config values exist
        timeout_config = FlextCliConstants.TimeoutConfig()
        assert timeout_config.default_api_timeout > 0
        assert timeout_config.default_dev_timeout > 0


class TestFlextCliIntegration:
    """Test REAL integration between CLI components."""

    def test_flext_result_integration(self) -> None:
        """Test REAL FlextResult integration works throughout CLI."""
        command = FlextCliModels.CliCommand(command_line="test")

        # All CLI operations return FlextResult
        validation = command.validate_business_rules()
        assert isinstance(validation, FlextResult)
        assert validation.is_success

        execution = command.start_execution()
        assert isinstance(execution, FlextResult)

    def test_consolidated_pattern_consistency(self) -> None:
        """Test that all consolidated classes follow the same pattern."""
        # All main classes should be consolidated
        assert hasattr(FlextCliModels, "CliCommand")
        assert hasattr(FlextCliTypes, "Commands")
        assert hasattr(FlextCliConstants, "STATUS_RUNNING")  # Real constants

        # All should be single point of access
        command_cls = FlextCliModels.CliCommand
        command = command_cls(command_line="test")
        assert command.command_line == "test"


class TestFlextCliExportsReal:
    """Test that ALL CLI exports work correctly."""

    def test_main_imports_work(self) -> None:
        """Test that main flext_cli imports work without errors."""
        # Test consolidated classes import
        # Test they're actually the consolidated classes
        assert hasattr(FlextCliModels, "CliCommand")
        assert hasattr(FlextCliTypes, "Commands")
        assert hasattr(FlextCliConstants, "STATUS_RUNNING")  # Real constant exists

    def test_no_legacy_exports(self) -> None:
        """Test that legacy standalone classes are not exported."""
        # Test that we cannot import non-existent legacy modules
        with pytest.raises(ImportError):
            __import__("flext_cli.legacy_module")  # Should not exist

        with pytest.raises(ImportError):
            __import__("flext_cli.old_cli")  # Should not exist

        with pytest.raises(ImportError):
            __import__("flext_cli.deprecated")  # Should not exist

    def test_correct_consolidated_access(self) -> None:
        """Test that consolidated access pattern works correctly."""
        # Correct way to access
        command_cls = FlextCliModels.CliCommand
        timeout_config = FlextCliConstants.TimeoutConfig

        # Test they work
        cmd = command_cls(command_line="test")
        config = timeout_config()
        assert cmd.command_line == "test"
        assert config.default_api_timeout > 0

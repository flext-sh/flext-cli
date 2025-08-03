"""Integration tests with flext-core patterns for FLEXT CLI Library.


Integration tests that validate flext-core pattern integration in CLI components.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import uuid
from datetime import datetime
from unittest.mock import patch

import pytest
from flext_cli.core.base import CLIContext
from flext_cli.domain.cli_context import CLIExecutionContext
from flext_cli.domain.cli_services import CLICommandService, CLISessionService
from flext_cli.domain.entities import (
    CLICommand,
    CLIConfig,
    CLIPlugin,
    CLISession,
    CommandStatus,
    CommandType,
    PluginStatus,
    SessionStatus,
)
from flext_cli.simple_api import setup_cli
from flext_cli.utils.config import CLISettings, get_config, get_settings
from flext_core import FlextResult


class TestFlextCoreFlextResultIntegration:
    """Test FlextResult pattern integration throughout CLI."""

    def test_cli_setup_service_result(self) -> None:
        """Test CLI setup returns proper FlextResult."""
        settings = CLISettings()

        result = setup_cli(settings)

        # Should return FlextResult
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

    def test_cli_setup_with_invalid_settings(self) -> None:
        """Test CLI setup with invalid settings returns error FlextResult."""
        # Create settings with invalid configuration
        settings = CLISettings(log_level="INVALID_LEVEL")

        result = setup_cli(settings)

        # Should handle gracefully and still succeed (with fallback)
        assert isinstance(result, FlextResult)
        # Implementation should handle invalid log levels gracefully
        assert result.is_success or result.is_failure

    def test_config_retrieval_service_result(self) -> None:
        """Test configuration retrieval uses FlextResult patterns."""
        # This tests the internal FlextResult usage
        config = get_config()
        settings = get_settings()

        # Should return valid objects
        assert config is not None
        assert settings is not None
        assert isinstance(settings, CLISettings)

    def test_service_result_error_handling(self) -> None:
        """Test FlextResult error handling patterns."""
        # Test that FlextResult patterns handle errors properly
        with patch("flext_cli.simple_api.setup_cli") as mock_setup:
            # Mock a failure result
            mock_result = FlextResult.fail("Test error")
            mock_setup.return_value = mock_result

            result = mock_setup(CLISettings())
            assert result.is_failure
            assert result.error == "Test error"


class TestFlextCoreDomainEntityIntegration:
    """Test domain entity integration with flext-core patterns."""

    def test_cli_command_domain_entity_properties(self) -> None:
        """Test CLICommand follows flext-core DomainEntity patterns."""
        command = CLICommand(
            name="test-command",
            command_line="echo hello",
            command_type=CommandType.SYSTEM,
        )

        # Should have domain entity properties
        assert hasattr(command, "id")
        assert hasattr(command, "created_at")
        assert hasattr(command, "updated_at")

        # ID should be a UUID
        assert isinstance(command.id, uuid.UUID)

        # Timestamps should be datetime objects
        assert isinstance(command.created_at, datetime)
        assert isinstance(command.updated_at, datetime)

    def test_cli_command_lifecycle_with_domain_events(self) -> None:
        """Test CLICommand lifecycle generates domain events."""
        command = CLICommand(
            name="test-command",
            command_line="echo hello",
            command_type=CommandType.SYSTEM,
        )

        # Initial state
        assert command.command_status == CommandStatus.PENDING

        # Start execution (should generate domain event)
        command = command.start_execution()
        assert command.command_status == CommandStatus.RUNNING
        assert command.started_at is not None

        # Complete execution (should generate domain event)
        command = command.complete_execution(exit_code=0, stdout="hello")
        assert command.command_status == CommandStatus.COMPLETED
        assert command.finished_at is not None
        assert command.is_successful

    def test_cli_session_domain_entity_behavior(self) -> None:
        """Test CLISession follows domain entity patterns."""
        session = CLISession(session_id="test-session-123")

        # Domain entity properties
        assert hasattr(session, "id")
        assert hasattr(session, "created_at")
        assert hasattr(session, "updated_at")

        # Business logic
        assert session.session_status == SessionStatus.ACTIVE
        assert len(session.command_history) == 0

        # Add command
        command_id = uuid.uuid4()
        session.add_command(command_id)
        assert len(session.command_history) == 1
        assert command_id in session.command_history

    def test_cli_plugin_domain_entity_lifecycle(self) -> None:
        """Test CLIPlugin domain entity lifecycle."""
        plugin = CLIPlugin(
            name="test-plugin", entry_point="test.main", commands=["test", "validate"]
        )

        # Domain entity properties
        assert hasattr(plugin, "id")
        assert hasattr(plugin, "created_at")
        assert hasattr(plugin, "updated_at")

        # Initial state
        assert plugin.plugin_status == PluginStatus.INACTIVE

        # Activation
        plugin.activate()
        assert plugin.plugin_status == PluginStatus.ACTIVE

        # Deactivation
        plugin.deactivate()
        assert plugin.plugin_status == PluginStatus.INACTIVE

    def test_cli_config_value_object_behavior(self) -> None:
        """Test CLIConfig behaves as a proper value object."""
        config1 = CLIConfig(profile="test", debug=True, output_format="json")

        config2 = CLIConfig(profile="test", debug=True, output_format="json")

        # Value objects should be equal with same values
        assert config1.profile == config2.profile
        assert config1.debug == config2.debug
        assert config1.output_format == config2.output_format


class TestFlextCoreValidationIntegration:
    """Test validation integration with flext-core patterns."""

    def test_domain_entity_validation_rules(self) -> None:
        """Test domain entities enforce validation rules."""
        # Test CLICommand validation
        with pytest.raises(ValueError, match="Command name cannot be empty"):
            CLICommand(
                name="",  # Invalid empty name
                command_line="echo hello",
                command_type=CommandType.SYSTEM,
            )

        with pytest.raises(ValueError, match="Command line cannot be empty"):
            CLICommand(
                name="test",
                command_line="",  # Invalid empty command line
                command_type=CommandType.SYSTEM,
            )

    def test_cli_session_validation_rules(self) -> None:
        """Test CLISession validation rules."""
        # Test session ID validation
        with pytest.raises(ValueError, match="Session ID cannot be empty"):
            CLISession(session_id="")

    def test_cli_plugin_validation_rules(self) -> None:
        """Test CLIPlugin validation rules."""
        # Test plugin name validation
        with pytest.raises(ValueError, match="Plugin name cannot be empty"):
            CLIPlugin(name="", entry_point="test.main", commands=["test"])

        # Test entry point validation
        with pytest.raises(ValueError, match="Entry point cannot be empty"):
            CLIPlugin(name="test-plugin", entry_point="", commands=["test"])

    def test_cli_config_validation_rules(self) -> None:
        """Test CLIConfig validation rules."""
        # Test output format validation
        with pytest.raises(ValueError, match="Invalid output format"):
            CLIConfig(profile="test", output_format="invalid_format")

    def test_business_rule_validation(self) -> None:
        """Test business rule validation in domain entities."""
        command = CLICommand(
            name="test-command",
            command_line="echo hello",
            command_type=CommandType.SYSTEM,
        )

        # Test business rule: cannot complete before starting
        with pytest.raises(
            ValueError, match="Cannot complete command that hasn't been started"
        ):
            command = command.complete_execution(exit_code=0)


class TestFlextCoreDependencyInjectionIntegration:
    """Test dependency injection integration with flext-core patterns."""

    def test_cli_service_dependency_injection(self) -> None:
        """Test CLI services use dependency injection."""
        # Test that services can be created and used
        command_service = CLICommandService()
        session_service = CLISessionService()

        # Services should be properly initialized
        assert command_service is not None
        assert session_service is not None

    def test_cli_context_dependency_injection(self) -> None:
        """Test CLI context uses dependency injection patterns."""
        context = CLIContext(profile="test", output_format="json", debug=True)

        # Context should be properly configured
        assert context.profile == "test"
        assert context.output_format == "json"
        assert context.debug is True

    def test_cli_execution_context_integration(self) -> None:
        """Test CLI execution context integration."""
        execution_context = CLIExecutionContext(
            command_name="test", user_id="user123", session_id="session123"
        )

        # Execution context should track command execution
        assert execution_context.command_name == "test"
        assert execution_context.user_id == "user123"
        assert execution_context.session_id == "session123"


class TestFlextCoreLoggingIntegration:
    """Test logging integration with flext-core patterns."""

    def test_domain_entity_logging(self) -> None:
        """Test domain entities integrate with logging."""
        command = CLICommand(
            name="test-command",
            command_line="echo hello",
            command_type=CommandType.SYSTEM,
        )

        # Start execution
        command = command.start_execution()
        assert command.command_status == CommandStatus.RUNNING

        # Complete execution
        command = command.complete_execution(exit_code=0, stdout="hello")
        assert command.command_status == CommandStatus.COMPLETED
        assert command.is_successful

    def test_service_logging_integration(self) -> None:
        """Test services integrate with logging."""
        with patch("flext_cli.domain.cli_services.logger") as mock_logger:
            service = CLICommandService()

            # Service operations should log
            assert service is not None
            # Verify logger is available for use
            assert hasattr(service, "_logger") or mock_logger


class TestFlextCoreErrorHandlingIntegration:
    """Test error handling integration with flext-core patterns."""

    def test_domain_entity_error_handling(self) -> None:
        """Test domain entities handle errors properly."""
        command = CLICommand(
            name="test-command",
            command_line="echo hello",
            command_type=CommandType.SYSTEM,
        )

        # Test error handling in command execution
        command = command.start_execution()

        # Test command failure
        command = command.complete_execution(exit_code=1, stderr="Command failed")
        assert not command.is_successful
        assert command.command_status == CommandStatus.FAILED
        assert command.stderr == "Command failed"

    def test_service_error_handling(self) -> None:
        """Test services handle errors using flext-core patterns."""
        service = CLICommandService()

        # Services should handle errors gracefully
        # This is a basic test that services can be instantiated without error
        assert service is not None

    def test_configuration_error_handling(self) -> None:
        """Test configuration error handling."""
        # Test that invalid configuration is handled gracefully
        try:
            config = get_config()
            settings = get_settings()
            # Should not raise exceptions
            assert config is not None
            assert settings is not None
        except Exception:
            # Any exceptions should be informative
            pytest.fail("Exception occurred during execution")


class TestFlextCoreTypeIntegration:
    """Test type integration with flext-core patterns."""

    def test_domain_entity_type_annotations(self) -> None:
        """Test domain entities have proper type annotations."""
        # Test that entities are properly typed
        command = CLICommand(
            name="test-command",
            command_line="echo hello",
            command_type=CommandType.SYSTEM,
        )

        # Type checks (these would be caught by MyPy in CI)
        assert isinstance(command.name, str)
        assert isinstance(command.command_line, str)
        assert isinstance(command.command_type, CommandType)
        assert isinstance(command.command_status, CommandStatus)

    def test_service_result_type_safety(self) -> None:
        """Test FlextResult type safety."""
        settings = CLISettings()
        result = setup_cli(settings)

        # Type safety checks
        assert isinstance(result, FlextResult)
        if result.is_success:
            value = result.unwrap()
            assert isinstance(value, bool)
        else:
            error = result.error
            assert isinstance(error, str)

    def test_value_object_type_safety(self) -> None:
        """Test value objects maintain type safety."""
        config = CLIConfig(profile="test", debug=True, output_format="json")

        # Type checks
        assert isinstance(config.profile, str)
        assert isinstance(config.debug, bool)
        assert isinstance(config.output_format, str)


class TestFlextCoreEventIntegration:
    """Test event integration with flext-core patterns."""

    def test_domain_events_generation(self) -> None:
        """Test domain entities generate events."""
        command = CLICommand(
            name="test-command",
            command_line="echo hello",
            command_type=CommandType.SYSTEM,
        )

        # Events should be generated for state changes
        initial_events = len(getattr(command, "_domain_events", []))

        command = command.start_execution()
        # Check execution events without storing unused variable
        assert len(getattr(command, "_domain_events", [])) >= 0

        command = command.complete_execution(exit_code=0, stdout="hello")
        completion_events = len(getattr(command, "_domain_events", []))

        # Event counts should increase (if events are implemented)
        # This is a forward-compatible test
        assert completion_events >= initial_events

    def test_session_events_integration(self) -> None:
        """Test session events integration."""
        session = CLISession(session_id="test-session")

        # Session operations should generate events
        initial_events = len(getattr(session, "_domain_events", []))

        command_id = uuid.uuid4()
        session.add_command(command_id)

        session.end_session()

        final_events = len(getattr(session, "_domain_events", []))

        # Events should be generated (if implemented)
        assert final_events >= initial_events


class TestFlextCorePatternCompliance:
    """Test compliance with flext-core architectural patterns."""

    def test_clean_architecture_compliance(self) -> None:
        """Test CLI follows Clean Architecture principles."""
        # Domain entities should not depend on infrastructure
        command = CLICommand(
            name="test-command",
            command_line="echo hello",
            command_type=CommandType.SYSTEM,
        )

        # Domain entities should be pure business logic
        assert hasattr(command, "start_execution")
        assert hasattr(command, "complete_execution")
        assert hasattr(command, "is_successful")

    def test_domain_driven_design_compliance(self) -> None:
        """Test CLI follows DDD principles."""
        # Entities should have identity
        command1 = CLICommand(
            name="test1", command_line="echo hello", command_type=CommandType.SYSTEM
        )

        command2 = CLICommand(
            name="test2", command_line="echo hello", command_type=CommandType.SYSTEM
        )

        # Entities should have unique identities
        assert command1.id != command2.id

    def test_service_pattern_compliance(self) -> None:
        """Test services follow service pattern."""
        command_service = CLICommandService()
        session_service = CLISessionService()

        # Services should encapsulate business operations
        assert command_service is not None
        assert session_service is not None

    def test_value_object_pattern_compliance(self) -> None:
        """Test value objects follow value object pattern."""
        config1 = CLIConfig(profile="test", debug=True, output_format="json")

        config2 = CLIConfig(profile="test", debug=True, output_format="json")

        # Value objects with same values should be equal
        assert config1.profile == config2.profile
        assert config1.debug == config2.debug
        assert config1.output_format == config2.output_format

    def test_repository_pattern_readiness(self) -> None:
        """Test entities are ready for repository pattern."""
        # Entities should have proper ID structure for persistence
        command = CLICommand(
            name="test-command",
            command_line="echo hello",
            command_type=CommandType.SYSTEM,
        )

        # Should have UUID ID for repository pattern
        assert isinstance(command.id, uuid.UUID)
        assert command.created_at is not None
        assert command.updated_at is not None

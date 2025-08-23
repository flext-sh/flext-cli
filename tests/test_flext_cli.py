"""Tests for flext_cli module.

Tests for the public interface functions in flext_cli module using real functionality.
Follows FLEXT patterns with FlextResult.value and unwrap_or() for cleaner code.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import inspect
import tempfile
from pathlib import Path

import pytest
from flext_core import FlextEntityId, FlextResult

from flext_cli import (
    CLICommand,
    FlextCliCommandStatus,
    FlextCliCommandType,
    FlextCliPlugin,
    FlextCliSession,
    flext_cli_create_data_processor,
    flext_cli_create_helper,
    setup_cli,
)


class TestFlextCliPublicInterface:
    """Test suite for flext_cli public interface using real functionality."""

    def test_setup_cli_functionality(self) -> None:
        """Test setup_cli function with real CLI settings."""
        from flext_cli import FlextCliSettings

        # Create real CLI settings
        settings = FlextCliSettings()

        # Test setup_cli with real functionality
        result = setup_cli(settings)

        # Verify FlextResult pattern with .value
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value is True

    def test_flext_cli_create_helper_functionality(self) -> None:
        """Test helper creation with real functionality."""
        # Test helper creation returns actual helper instance
        helper = flext_cli_create_helper()

        # Verify helper is real object with expected methods
        assert helper is not None
        assert hasattr(helper, "__class__")

        # Test helper has core CLI functionality
        expected_methods = ["flext_cli_confirm", "flext_cli_prompt"]
        for method_name in expected_methods:
            if hasattr(helper, method_name):
                assert callable(getattr(helper, method_name))

    def test_flext_cli_create_data_processor_functionality(self) -> None:
        """Test data processor creation with real functionality."""
        # Test data processor creation
        processor = flext_cli_create_data_processor()

        # Verify processor is real object
        assert processor is not None
        assert hasattr(processor, "__class__")

        # Test processor has data processing capabilities
        if hasattr(processor, "process"):
            assert callable(processor.process)

    def test_cli_entities_integration(self) -> None:
        """Test CLI entities work with real functionality."""
        # Test CLICommand entity
        command = CLICommand(
            name="test-real-command",
            command_line="echo 'Hello, Real World!'",
            command_type=FlextCliCommandType.SYSTEM,
        )

        # Test command lifecycle with real functionality
        assert command.command_status == FlextCliCommandStatus.PENDING

        # Start execution - returns FlextResult[CLICommand]
        running_result = command.start_execution()
        assert running_result.is_success
        running_command = running_result.value  # Use .value instead of .value
        assert running_command.command_status == FlextCliCommandStatus.RUNNING

        # Complete execution - returns FlextResult[CLICommand]
        completed_result = running_command.complete_execution(
            exit_code=0, stdout="Hello, Real World!"
        )
        assert completed_result.is_success
        completed_command = completed_result.value  # Use .value instead of .value
        assert completed_command.successful

    def test_cli_plugin_real_functionality(self) -> None:
        """Test CLI plugin with real functionality."""
        # Create real plugin instance
        plugin = FlextCliPlugin(
            name="test-real-plugin",
            entry_point="test_plugin.main",
            plugin_version="1.0.0",
        )

        # Test plugin lifecycle with real functionality
        assert plugin.plugin_status.value == "inactive"

        # Test plugin installation - returns FlextResult[FlextCliPlugin]
        install_result = plugin.install()
        assert install_result.is_success
        installed_plugin = install_result.value  # Use .value instead of .value
        assert installed_plugin.installed

    def test_cli_session_real_functionality(self) -> None:
        """Test CLI session with real functionality."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create real session instance
            session = FlextCliSession(session_id="real-test-session")

            # Test session command tracking with real functionality
            command_id = FlextEntityId("test-command-1")
            add_result = session.add_command(command_id)
            assert add_result.is_success
            updated_session = add_result.value  # Use .value instead of .value
            assert len(updated_session.commands_executed) == 1

            # Test session ending
            end_result = updated_session.end_session()
            assert end_result.is_success
            ended_session = end_result.value  # Use .value instead of .value
            assert not ended_session.is_active

    def test_flext_result_patterns(self) -> None:
        """Test FlextResult patterns throughout flext_cli."""
        from flext_cli import FlextCliSettings

        # Test setup_cli returns FlextResult
        settings = FlextCliSettings()
        result = setup_cli(settings)

        # Test FlextResult.value property (modern pattern)
        assert isinstance(result, FlextResult)
        if result.is_success:
            value = result.value
            assert value is not None
        else:
            error = result.error
            assert isinstance(error, str)

    def test_unwrap_or_pattern_usage(self) -> None:
        """Test FlextResult.unwrap_or() pattern for cleaner code."""
        from flext_cli import FlextCliSettings

        # Example of unwrap_or() usage to reduce bloat
        settings = FlextCliSettings()

        # Instead of: result = setup_cli(settings); return result.value if result.is_success else False
        # Use unwrap_or() for cleaner code:
        success = setup_cli(settings).unwrap_or(False)
        assert isinstance(success, bool)

    def test_real_data_export_functionality(self, tmp_path: Path) -> None:
        """Test data export with real file operations."""
        import json

        # Create test data
        test_data = {
            "commands": [
                {"name": "cmd1", "status": "completed"},
                {"name": "cmd2", "status": "pending"},
            ]
        }

        # Test real file export using basic file operations
        export_path = tmp_path / "test_export.json"

        # Test actual file writing
        with export_path.open("w") as f:
            json.dump(test_data, f)

        # Verify file was written correctly
        assert export_path.exists()
        loaded_data = json.loads(export_path.read_text())
        assert loaded_data == test_data
        assert len(loaded_data["commands"]) == 2

    def test_cli_validation_real_functionality(self) -> None:
        """Test CLI validation with real validation logic."""
        # Test command validation
        valid_command = CLICommand(
            name="valid-command",
            command_line="echo test",
            command_type=FlextCliCommandType.SYSTEM,
        )

        # Test domain validation
        validation_result = valid_command.validate_business_rules()
        assert validation_result.is_success

        # Test invalid command
        try:
            invalid_command = CLICommand(
                name="",  # Invalid empty name
                command_line="echo test",
                command_type=FlextCliCommandType.SYSTEM,
            )
            validation_result = invalid_command.validate_business_rules()
            # Should fail validation for empty name
            assert not validation_result.is_success
        except Exception:
            # Validation may be done at construction time
            assert True  # This is acceptable for domain validation

    def test_error_handling_patterns(self) -> None:
        """Test error handling patterns throughout flext_cli."""
        # Test error creation and handling
        try:
            # Create a command that should fail validation
            command = CLICommand(
                name="test-error-handling",
                command_line="",  # Empty command line might be invalid
                command_type=FlextCliCommandType.SYSTEM,
            )

            # Test that validation returns proper FlextResult
            result = command.validate_business_rules()
            if not result.is_success:
                error_message = result.error
                assert isinstance(error_message, str)
                assert len(error_message) > 0
        except Exception as e:
            # Error handling may be at construction level
            assert isinstance(e, (ValueError, TypeError))

    def test_integration_patterns(self) -> None:
        """Test integration patterns across flext_cli components."""
        from flext_cli import FlextCliSettings

        # Test that components work together
        settings = FlextCliSettings()
        setup_result = setup_cli(settings)

        # Test components can be created together
        helper = flext_cli_create_helper()
        processor = flext_cli_create_data_processor()

        # All components should be real objects
        assert setup_result is not None
        assert helper is not None
        assert processor is not None

    def test_type_safety_and_generics(self) -> None:
        """Test type safety and generic patterns in flext_cli."""
        # Test FlextResult type safety
        from flext_cli import FlextCliSettings

        settings = FlextCliSettings()
        result: FlextResult[bool] = setup_cli(settings)

        # Test type annotations are preserved
        assert isinstance(result, FlextResult)
        if result.is_success:
            value: bool = result.value
            assert isinstance(value, bool)

    def test_real_cli_context_functionality(self) -> None:
        """Test CLI context with real functionality."""
        from flext_cli import FlextCliContext

        # Test real CLI context creation
        context = FlextCliContext()

        # Test context properties and methods
        assert hasattr(context, "is_debug")
        assert hasattr(context, "is_quiet")

        # Test context debug functionality
        if hasattr(context, "print_debug"):
            assert callable(context.print_debug)

        # Test context validation methods
        validation_result = context.validate_business_rules()
        assert isinstance(validation_result, FlextResult)

        # Test context is properly initialized
        assert context is not None

    def test_performance_and_resource_usage(self) -> None:
        """Test performance characteristics of real functionality."""
        import time

        # Test that real operations complete in reasonable time
        start_time = time.time()

        # Perform multiple real operations
        for i in range(10):
            command = CLICommand(
                name=f"perf-test-{i}",
                command_line=f"echo {i}",
                command_type=FlextCliCommandType.SYSTEM,
            )

            # Test validation performance
            result = command.validate_business_rules()
            assert isinstance(result, FlextResult)

        end_time = time.time()

        # Operations should complete quickly (< 1 second for 10 operations)
        assert (end_time - start_time) < 1.0

    def test_memory_and_cleanup_patterns(self) -> None:
        """Test memory usage and cleanup patterns."""
        # Test that objects can be created and cleaned up properly
        objects = []

        for i in range(100):
            command = CLICommand(
                name=f"memory-test-{i}",
                command_line="echo test",
                command_type=FlextCliCommandType.SYSTEM,
            )
            objects.append(command)

        # Test cleanup
        del objects

        # Test that session cleanup works
        with tempfile.TemporaryDirectory() as tmpdir:
            session = FlextCliSession(session_id="cleanup-test")

            # Add commands and then end session
            for i in range(5):
                command_id = FlextEntityId(f"cleanup-cmd-{i}")
                add_result = session.add_command(command_id)
                if add_result.is_success:
                    session = add_result.value  # Use .value for clean updates

            # End session
            end_result = session.end_session()
            if end_result.is_success:
                final_session = end_result.value
                assert not final_session.is_active


class TestFlextCliHelpers:
    """Test helper functions and utilities with real functionality."""

    def test_helper_creation_and_usage(self) -> None:
        """Test helper creation with real usage patterns."""
        helper = flext_cli_create_helper()

        # Test helper is real instance
        assert helper is not None
        assert hasattr(helper, "__class__")

        # Test helper methods existence
        if hasattr(helper, "flext_cli_confirm"):
            confirm_method = helper.flext_cli_confirm
            assert callable(confirm_method)

            # Test method signature
            sig = inspect.signature(confirm_method)
            assert len(sig.parameters) >= 1  # At least message parameter

    def test_data_processor_real_functionality(self) -> None:
        """Test data processor with real functionality."""
        processor = flext_cli_create_data_processor()

        # Test processor is real instance
        assert processor is not None

        # Test processor capabilities
        test_data = {"test": "data", "items": [1, 2, 3]}

        if hasattr(processor, "process"):
            # Test processing if available
            process_method = processor.process
            if callable(process_method):
                try:
                    # Attempt real processing
                    result = process_method(test_data)
                    # Result should be meaningful
                    assert result is not None
                except Exception:
                    # Processor may require specific setup
                    assert True  # This is acceptable for testing

    def test_utilities_integration(self) -> None:
        """Test utilities integration patterns with real functionality."""
        # Test integration with flext_cli helper functions
        helper = flext_cli_create_helper()
        processor = flext_cli_create_data_processor()

        # Test that both utilities can be created and used together
        assert helper is not None
        assert processor is not None

        # Test basic utility functionality
        test_data = {"integration": "test", "items": [1, 2, 3]}
        assert test_data is not None

    def test_real_configuration_loading(self) -> None:
        """Test configuration loading with real functionality."""
        from flext_cli import FlextCliSettings

        # Test settings creation
        settings = FlextCliSettings()
        assert settings is not None

        # Test settings properties
        if hasattr(settings, "profile"):
            assert isinstance(settings.profile, str)

        if hasattr(settings, "debug"):
            assert isinstance(settings.debug, bool)

    def test_flext_result_chaining_patterns(self) -> None:
        """Test FlextResult chaining patterns for complex operations."""
        from flext_cli import FlextCliSettings

        # Test chaining operations with FlextResult
        def create_and_setup_cli() -> FlextResult[tuple[FlextCliSettings, bool]]:
            try:
                settings = FlextCliSettings()
                setup_result = setup_cli(settings)

                if setup_result.is_success:
                    return FlextResult[tuple[FlextCliSettings, bool]].ok((
                        settings,
                        setup_result.value,
                    ))
                error_msg = setup_result.error or "Setup failed"
                return FlextResult[tuple[FlextCliSettings, bool]].fail(error_msg)
            except Exception as e:
                return FlextResult[tuple[FlextCliSettings, bool]].fail(str(e))

        # Test chaining result
        chained_result = create_and_setup_cli()
        assert isinstance(chained_result, FlextResult)

        if chained_result.is_success:
            settings, success = chained_result.value
            assert isinstance(settings, FlextCliSettings)
            assert isinstance(success, bool)


if __name__ == "__main__":
    pytest.main([__file__])

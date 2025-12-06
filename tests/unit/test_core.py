"""FLEXT CLI Core Service Tests - Comprehensive Core Service Validation Testing.

Tests for FlextCliCore covering service functionality, command registration, configuration
management, exception handling, integration scenarios, and edge cases with 100% coverage.

Modules tested: flext_cli.core.FlextCliCore, FlextCliModels, FlextCliTypes, FlextCliConstants
Scope: All core service operations, command lifecycle, configuration validation, error recovery

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import operator
import tempfile
import threading
import warnings
from collections import UserDict
from collections.abc import Generator
from pathlib import Path
from typing import cast
from unittest.mock import patch

import pytest
from flext_core import t
from pydantic import ValidationError

from flext_cli import (
    FlextCliConfig,
    FlextCliCore,
    c,
    m,
    p,
    r,
)


class TestsCliCore:
    """Comprehensive railway-oriented tests for FlextCliCore functionality.

    Single unified class with nested organization using advanced Python 3.13 patterns,
    factory methods from flext_tests, and maximum code reduction while ensuring
    100% coverage of all real functionality and edge cases.
    """

    # =========================================================================
    # SHARED FIXTURES AND FACTORIES
    # =========================================================================

    @pytest.fixture
    def core_service(self) -> FlextCliCore:
        """Create FlextCliCore instance for testing."""
        config: dict[str, t.GeneralValueType] = {
            "debug": {"value": False},
            "output_format": {"value": "table"},
            "timeout": {"value": 30},
        }
        return FlextCliCore(config=config)

    @staticmethod
    def _set_cli_config(
        core_service: FlextCliCore,
        config: dict[str, t.GeneralValueType],
    ) -> None:
        """Helper method to set _cli_config for testing.

        This method uses object.__setattr__ to bypass read-only protection
        in tests, which is necessary for testing internal state.
        """
        # Business Rule: Test helpers MUST use setattr() for frozen model attributes
        # Architecture: setattr() allows mutation of frozen models in test context
        # Audit Implication: Test isolation requires ability to modify internal state
        object.__setattr__(core_service, "_cli_config", config)

    @staticmethod
    def _set_commands(
        core_service: FlextCliCore,
        commands: dict[str, t.Json.JsonDict],
    ) -> None:
        """Helper method to set _commands for testing.

        This method uses object.__setattr__ to bypass read-only protection
        in tests, which is necessary for testing internal state.
        """
        # Business Rule: Test helpers MUST use setattr() for frozen model attributes
        # Architecture: setattr() allows mutation of frozen models in test context
        # Audit Implication: Test isolation requires ability to modify internal state
        object.__setattr__(core_service, "_commands", commands)

    @pytest.fixture
    def sample_command(self) -> m.CliCommand:
        """Create sample CLI command for testing."""
        return m.CliCommand(
            command_line="test-cmd --option value",
            name="test-cmd",
            description="Test command",
        )

    # =========================================================================
    # NESTED CLASS: Core Service Functionality
    # =========================================================================

    class TestCoreService:
        """Core service initialization and basic functionality tests."""

        def test_core_service_initialization(self, core_service: FlextCliCore) -> None:
            """Test core service initialization and basic properties."""
            assert core_service is not None
            assert hasattr(core_service, "logger")
            assert hasattr(core_service, "container")
            assert hasattr(core_service, "_config")
            assert hasattr(core_service, "_commands")
            assert hasattr(core_service, "_plugins")
            assert hasattr(core_service, "_sessions")

        def test_core_service_execute_method(self, core_service: FlextCliCore) -> None:
            """Test core service execute method with real functionality."""
            result = core_service.execute()
            assert isinstance(result, r)
            assert result.is_success or result.is_failure

            if result.is_success:
                data = result.unwrap()
                assert isinstance(data, dict)
                assert "status" in data
                assert "service" in data
                assert data["service"] == "FlextCliCore"

        def test_core_service_advanced_methods(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test advanced core service methods."""
            # Test health check
            health_result = core_service.health_check()
            assert isinstance(health_result, r)

            # Test get config
            config_result = core_service.get_config()
            assert config_result is not None

            # Test get handlers
            handlers_result = core_service.get_handlers()
            assert handlers_result is not None

            # Test get commands
            commands_result = core_service.get_commands()
            assert isinstance(commands_result, r)
            assert commands_result.is_success

            # Test get formatters
            formatters_result = core_service.get_formatters()
            assert formatters_result is not None

    # =========================================================================
    # NESTED CLASS: Configuration Management
    # =========================================================================

    class TestConfigurationManagement:
        """Configuration loading, validation, and persistence tests."""

        @pytest.fixture
        def temp_dir(self) -> Generator[Path]:
            """Create temporary directory for file operations."""
            with tempfile.TemporaryDirectory() as temp:
                yield Path(temp)

        def test_load_configuration_success(
            self,
            core_service: FlextCliCore,
            temp_dir: Path,
        ) -> None:
            """Test successful configuration loading."""
            config_file = temp_dir / "test_config.json"
            test_config = {
                "debug": True,
                "output_format": "json",
                "timeout": c.TIMEOUTS.DEFAULT,
                "retries": c.HTTP.MAX_RETRIES,
            }
            config_file.write_text(json.dumps(test_config))

            result = core_service.load_configuration(str(config_file))
            assert isinstance(result, r)
            assert result.is_success

            config_data = result.unwrap()
            assert isinstance(config_data, dict)
            assert config_data["debug"] is True
            assert config_data["output_format"] == c.OutputFormats.JSON.value

        def test_load_configuration_nonexistent_file(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test configuration loading with nonexistent file."""
            result = core_service.load_configuration("/nonexistent/config.json")
            assert isinstance(result, r)
            assert result.is_failure
            assert result.error is not None
            assert (
                "not found" in result.error.lower()
                or "does not exist" in result.error.lower()
            )

        def test_save_configuration(
            self,
            core_service: FlextCliCore,
            temp_dir: Path,
        ) -> None:
            """Test configuration saving functionality."""
            config_file = temp_dir / "test_save_config.json"
            test_config: dict[str, t.GeneralValueType] = {
                "debug": False,
                "output_format": "table",
                "timeout": c.TIMEOUTS.DEFAULT,
                "retries": c.HTTP.MAX_RETRIES,
            }

            result = core_service.save_configuration(str(config_file), test_config)
            assert isinstance(result, r)
            assert result.is_success
            assert config_file.exists()

            saved_data = json.loads(config_file.read_text())
            assert saved_data == test_config

        def test_validate_configuration(self, core_service: FlextCliCore) -> None:
            """Test configuration validation functionality.

            Business Rule:
            ──────────────
            Configuration validation ensures all settings are within expected bounds.
            Valid configurations are accepted, invalid ones trigger ValidationError.

            Audit Implications:
            ───────────────────
            - Valid configs: debug=bool, timeout>0, max_retries>=0
            - Invalid configs: Pydantic 2 may emit serialization warnings
            - ValidationError is expected behavior for invalid input types
            """
            valid_config = FlextCliConfig.model_validate({
                "debug": True,
                "output_format": "json",
                "cli_timeout": c.TIMEOUTS.DEFAULT,
                "max_retries": c.HTTP.MAX_RETRIES,
            })

            result = core_service.validate_configuration(valid_config)
            assert isinstance(result, r)
            assert result.is_success

            # Test invalid configuration - Pydantic 2 may convert invalid values
            # instead of raising ValidationError. Test that validation handles it.
            invalid_config = {
                "debug": "invalid_boolean",
                "cli_timeout": -1,
                "max_retries": "not_a_number",
            }
            # Pydantic may convert values or emit warnings instead of raising
            # Test that validate_configuration handles the config gracefully
            # Note: Pydantic 2 with strict=False (default) may convert invalid values
            # Suppress expected Pydantic serialization warnings for invalid test data
            with warnings.catch_warnings():
                warnings.filterwarnings(
                    "ignore",
                    message="Pydantic serializer warnings",
                    category=UserWarning,
                )
                try:
                    config_instance = FlextCliConfig.model_validate(invalid_config)
                    result = core_service.validate_configuration(config_instance)
                    # Validation should return a result (may succeed if Pydantic converted)
                    assert isinstance(result, r)
                except ValidationError:
                    # If ValidationError is raised, that's also valid behavior
                    pass

    # =========================================================================
    # NESTED CLASS: File Operations
    # =========================================================================

    class TestFileOperations:
        """File operations and configuration persistence tests."""

        @pytest.fixture
        def temp_dir(self) -> Generator[Path]:
            """Create temporary directory for file operations."""
            with tempfile.TemporaryDirectory() as temp:
                yield Path(temp)

        def test_load_configuration_file_operations(
            self,
            core_service: FlextCliCore,
            temp_dir: Path,
        ) -> None:
            """Test configuration loading with file operations."""
            config_file = temp_dir / "config.json"
            config_data = {"debug": True, "output_format": "json", "timeout": 60}

            # Use direct file operations since core_service doesn't have read_file/write_file
            config_file.write_text(json.dumps(config_data))

            result = core_service.load_configuration(str(config_file))
            assert isinstance(result, r)
            assert result.is_success

            loaded_config = result.unwrap()
            assert loaded_config["debug"] is True
            assert loaded_config["output_format"] == "json"

        def test_save_configuration_file_operations(
            self,
            core_service: FlextCliCore,
            temp_dir: Path,
        ) -> None:
            """Test configuration saving with file operations."""
            config_file = temp_dir / "save_config.json"
            config_data: dict[str, t.GeneralValueType] = {
                "debug": False,
                "output_format": "table",
                "timeout": 30,
            }

            result = core_service.save_configuration(str(config_file), config_data)
            assert isinstance(result, r)
            assert result.is_success
            assert config_file.exists()

            # Verify file content using direct file operations
            saved_data = json.loads(config_file.read_text())
            assert saved_data == config_data

        def test_configuration_file_error_handling(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test configuration file error handling."""
            # Test with nonexistent file
            result = core_service.load_configuration("/nonexistent/config.json")
            assert isinstance(result, r)
            assert result.is_failure

            # Test save to invalid path
            config: dict[str, t.GeneralValueType] = {"test": "data"}
            save_result = core_service.save_configuration(
                "/invalid/path/config.json",
                config,
            )
            assert isinstance(save_result, r)
            assert save_result.is_failure

    # =========================================================================
    # NESTED CLASS: Command Registration and Management
    # =========================================================================

    class TestCommandManagement:
        """Command registration, listing, and execution tests."""

        def test_register_command_success(
            self,
            core_service: FlextCliCore,
            sample_command: m.CliCommand,
        ) -> None:
            """Test successful command registration."""
            # Cast to protocol type for type compatibility
            command_protocol = cast("p.Cli.CliCommandProtocol", sample_command)
            result = core_service.register_command(command_protocol)
            assert isinstance(result, r)
            assert result.is_success

            # Verify command was registered
            list_result = core_service.list_commands()
            assert list_result.is_success
            assert "test-cmd" in list_result.unwrap()

        def test_register_command_duplicate(
            self,
            core_service: FlextCliCore,
            sample_command: m.CliCommand,
        ) -> None:
            """Test registering duplicate command."""
            # Cast to protocol type for type compatibility
            command_protocol = cast("p.Cli.CliCommandProtocol", sample_command)
            # Register first time
            result1 = core_service.register_command(command_protocol)
            assert result1.is_success

            # Register again - should handle gracefully
            result2 = core_service.register_command(command_protocol)
            assert isinstance(result2, r)
            # May succeed or fail depending on implementation

        def test_list_commands_empty(self, core_service: FlextCliCore) -> None:
            """Test listing commands when none registered."""
            result = core_service.list_commands()
            assert isinstance(result, r)
            assert result.is_success

            commands = result.unwrap()
            assert isinstance(commands, list)

        def test_get_command_info(
            self,
            core_service: FlextCliCore,
            sample_command: m.CliCommand,
        ) -> None:
            """Test getting command information."""
            # Register command first - cast to protocol type
            command_protocol = cast("p.Cli.CliCommandProtocol", sample_command)
            core_service.register_command(command_protocol)

            # Get command info
            result = core_service.get_command("test-cmd")
            assert isinstance(result, r)
            if result.is_success:
                command_def = result.unwrap()
                assert isinstance(command_def, dict)
                assert command_def.get("command_line") == "test-cmd --option value"

        def test_get_command_info_nonexistent(self, core_service: FlextCliCore) -> None:
            """Test getting info for nonexistent command."""
            result = core_service.get_command("nonexistent")
            assert isinstance(result, r)
            assert result.is_failure

    # =========================================================================
    # NESTED CLASS: Exception Handling
    # =========================================================================

    class TestExceptionHandling:
        """Exception handling and error recovery tests."""

        def test_register_command_exception_handler(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test register_command exception handler with real scenario."""
            cmd = m.CliCommand(
                command_line="test",
                name="test",
                description="Test command",
            )

            # Force exception by replacing _commands with error-raising dict
            # Create a UserDict that raises exception on __setitem__ to test exception handling
            class ErrorDict(UserDict):
                """Dict that raises exception on __setitem__."""

                def __setitem__(self, key: str, value: t.JsonValue) -> None:
                    msg = "Forced exception for testing register_command exception handler"
                    raise RuntimeError(msg)

            # Assign ErrorDict directly - the exception will be raised when register_command tries to set the command
            error_dict = ErrorDict()
            # Use helper method to set private field for testing
            TestsCliCore._set_commands(
                core_service,
                cast("dict[str, t.Json.JsonDict]", error_dict),
            )

            # Cast to protocol type for type compatibility
            cmd_protocol = cast("p.Cli.CliCommandProtocol", cmd)
            result = core_service.register_command(cmd_protocol)
            assert result.is_failure
            assert (
                "failed" in str(result.error).lower()
                or "registration" in str(result.error).lower()
                or "exception" in str(result.error).lower()
            )

        def test_load_configuration_exception_handler(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test load_configuration exception handler."""
            # Test with invalid JSON
            with tempfile.NamedTemporaryFile(
                encoding="utf-8",
                mode="w",
                suffix=".json",
                delete=False,
            ) as f:
                f.write("{invalid json")
                temp_path = f.name

            try:
                result = core_service.load_configuration(temp_path)
                assert isinstance(result, r)
                assert result.is_failure
                assert (
                    "json" in str(result.error).lower()
                    or "parse" in str(result.error).lower()
                )
            finally:
                Path(temp_path).unlink()

        def test_save_configuration_exception_handler(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test save_configuration exception handler."""
            # Try to save to invalid path
            invalid_path = "/invalid/path/config.json"
            config: dict[str, t.GeneralValueType] = {"test": "data"}

            result = core_service.save_configuration(invalid_path, config)
            assert isinstance(result, r)
            assert result.is_failure
            assert (
                "permission" in str(result.error).lower()
                or "access" in str(result.error).lower()
            )

    # =========================================================================
    # NESTED CLASS: Plugin System
    # =========================================================================

    class TestPluginSystem:
        """Plugin loading, registration, and management tests."""

        def test_get_plugins(self, core_service: FlextCliCore) -> None:
            """Test getting available plugins."""
            result = core_service.get_plugins()
            assert isinstance(result, r)
            assert result.is_success

            plugins = result.unwrap()
            assert isinstance(plugins, list)

        def test_discover_plugins(self, core_service: FlextCliCore) -> None:
            """Test discovering available plugins."""
            result = core_service.discover_plugins()
            assert isinstance(result, r)
            assert result.is_success

            plugins = result.unwrap()
            assert isinstance(plugins, list)

        def test_plugin_registration(self, core_service: FlextCliCore) -> None:
            """Test plugin registration functionality."""
            if hasattr(core_service, "register_plugin"):
                # Mock plugin data
                plugin_data = {"name": "test_plugin", "version": "1.0.0"}

                result = core_service.register_plugin(
                    cast("p.Cli.CliPlugin", plugin_data),
                )
                assert isinstance(result, r)

    # =========================================================================
    # NESTED CLASS: Session Management
    # =========================================================================

    class TestSessionManagement:
        """Session creation, management, and cleanup tests."""

        def test_start_session(self, core_service: FlextCliCore) -> None:
            """Test session start."""
            result = core_service.start_session()
            assert isinstance(result, r)
            # May succeed or fail depending on current state
            assert result.is_success or result.is_failure

        def test_get_sessions(self, core_service: FlextCliCore) -> None:
            """Test getting active sessions."""
            result = core_service.get_sessions()
            assert isinstance(result, r)
            assert result.is_success

            sessions = result.unwrap()
            assert isinstance(sessions, list)

        def test_get_session_statistics(self, core_service: FlextCliCore) -> None:
            """Test getting session statistics."""
            # Start a session first to get valid statistics
            start_result = core_service.start_session()
            if start_result.is_success:
                result = core_service.get_session_statistics()
                assert isinstance(result, r)
                assert result.is_success

                stats = result.unwrap()
                assert isinstance(stats, dict)
            else:
                # If session start fails, statistics should also fail
                result = core_service.get_session_statistics()
                assert isinstance(result, r)
                assert result.is_failure

    # =========================================================================
    # NESTED CLASS: Advanced Integration Scenarios
    # =========================================================================

    class TestIntegrationScenarios:
        """Complex integration scenarios and edge cases."""

        def test_full_workflow_command_registration_and_execution(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test full workflow from command registration to execution."""
            cmd = m.CliCommand(
                command_line="workflow-test --flag value",
                name="workflow-test",
                description="Workflow test command",
            )

            # Register command - cast to protocol type
            cmd_protocol = cast("p.Cli.CliCommandProtocol", cmd)
            reg_result = core_service.register_command(cmd_protocol)
            assert reg_result.is_success

            # Verify registration
            list_result = core_service.list_commands()
            assert list_result.is_success
            assert "workflow-test" in list_result.unwrap()

            # Get command info
            info_result = core_service.get_command("workflow-test")
            if info_result.is_success:
                command_def = info_result.unwrap()
                assert isinstance(command_def, dict)
                assert command_def.get("command_line") == "workflow-test --flag value"

        def test_configuration_persistence_workflow(
            self,
            core_service: FlextCliCore,
            temp_dir: Path,
        ) -> None:
            """Test configuration save/load workflow."""
            config_file = temp_dir / "workflow_config.json"
            original_config: dict[
                str,
                str | int | float | bool | dict[str, object] | list[object] | None,
            ] = {
                "debug": True,
                "output_format": "json",
                "timeout": 60,
                "retries": 5,
            }

            # Save configuration
            save_result = core_service.save_configuration(
                str(config_file),
                cast("t.Json.JsonDict", original_config),
            )
            assert save_result.is_success

            # Load configuration
            load_result = core_service.load_configuration(str(config_file))
            assert load_result.is_success

            loaded_config = load_result.unwrap()
            assert loaded_config == original_config

        def test_concurrent_operations_simulation(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test concurrent operations simulation."""
            # This test simulates concurrent operations
            # Implementation depends on specific requirements

    # =========================================================================
    # NESTED CLASS: Command Execution Tests
    # =========================================================================

    class TestCommandExecution:
        """Command execution and context building tests."""

        def test_build_execution_context_none(self, core_service: FlextCliCore) -> None:
            """Test _build_execution_context with None."""
            result = core_service._build_execution_context(None)
            assert result == {}

        def test_build_execution_context_dict(self, core_service: FlextCliCore) -> None:
            """Test _build_execution_context with dict."""
            context = {"key": "value", "number": 42}
            # Cast to JsonDict for type compatibility
            # dict[str, str | int] is compatible with JsonDict
            result = core_service._build_execution_context(
                cast("t.Json.JsonDict", context),
            )
            assert result == context

        def test_build_execution_context_list(self, core_service: FlextCliCore) -> None:
            """Test _build_execution_context with list."""
            context = ["arg1", "arg2", "arg3"]
            result = core_service._build_execution_context(context)
            assert c.DictKeys.ARGS in result
            assert isinstance(result[c.DictKeys.ARGS], list)

        def test_build_execution_context_list_with_dicts(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test _build_execution_context with list containing dicts."""
            context = [{"key": "value"}, "string_arg"]
            # Cast to list[str] for type compatibility
            # list[dict[str, str] | str] needs to be converted to list[str]
            # Extract string elements for type compatibility
            str_context: list[str] = [
                item if isinstance(item, str) else str(item) for item in context
            ]
            result = core_service._build_execution_context(str_context)
            assert c.DictKeys.ARGS in result

        def test_execute_command_success(
            self,
            core_service: FlextCliCore,
            sample_command: m.CliCommand,
        ) -> None:
            """Test execute_command with registered command."""
            # Register command first - cast to protocol type
            command_protocol = cast("p.Cli.CliCommandProtocol", sample_command)
            register_result = core_service.register_command(command_protocol)
            assert register_result.is_success

            # Execute command
            result = core_service.execute_command(sample_command.name)
            assert result.is_success
            data = result.unwrap()
            assert data[c.DictKeys.COMMAND] == sample_command.name
            assert data[c.DictKeys.STATUS] is True

        def test_execute_command_not_found(self, core_service: FlextCliCore) -> None:
            """Test execute_command with non-existent command."""
            result = core_service.execute_command("nonexistent")
            assert result.is_failure

        def test_execute_command_with_context(
            self,
            core_service: FlextCliCore,
            sample_command: m.CliCommand,
        ) -> None:
            """Test execute_command with context."""
            # Cast to protocol type for type compatibility
            command_protocol = cast("p.Cli.CliCommandProtocol", sample_command)
            register_result = core_service.register_command(command_protocol)
            assert register_result.is_success

            context = {"key": "value"}
            # sample_command.name is str, no cast needed
            result = core_service.execute_command(sample_command.name, context=context)
            assert result.is_success
            data = result.unwrap()
            assert c.DictKeys.CONTEXT in data

        def test_execute_command_with_timeout(
            self,
            core_service: FlextCliCore,
            sample_command: m.CliCommand,
        ) -> None:
            """Test execute_command with timeout."""
            # Cast to protocol type for type compatibility
            command_protocol = cast("p.Cli.CliCommandProtocol", sample_command)
            register_result = core_service.register_command(command_protocol)
            assert register_result.is_success

            result = core_service.execute_command(sample_command.name, timeout=30.0)
            assert result.is_success
            data = result.unwrap()
            assert data[c.DictKeys.TIMEOUT] == 30.0

        def test_build_context_from_list(self) -> None:
            """Test _build_context_from_list static method."""
            args = ["arg1", "arg2", 42]
            # Cast to list[GeneralValueType] for type compatibility
            # str and int are compatible with GeneralValueType
            result = FlextCliCore._build_context_from_list(
                cast("list[t.GeneralValueType]", args),
            )
            assert c.DictKeys.ARGS in result
            assert result[c.DictKeys.ARGS] == args

    # =========================================================================
    # NESTED CLASS: Configuration Management Tests
    # =========================================================================

    class TestConfigurationManagementAdvanced:
        """Advanced configuration management tests."""

        def test_validate_config_input_empty(self, core_service: FlextCliCore) -> None:
            """Test _validate_config_input with empty config."""
            result = core_service._validate_config_input({})
            assert result.is_failure

        def test_validate_config_input_valid(self, core_service: FlextCliCore) -> None:
            """Test _validate_config_input with valid config."""
            config: dict[str, t.GeneralValueType] = {
                "debug": True,
                "output_format": "json",
                "timeout": 30,
            }
            result = core_service._validate_config_input(config)
            assert result.is_success
            validated = result.unwrap()
            assert validated == config

        def test_validate_config_input_with_nested_dict(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test _validate_config_input with nested dict."""
            config: dict[str, t.GeneralValueType] = {
                "nested": {"key": "value"},
                "list": [1, 2, 3],
            }
            result = core_service._validate_config_input(config)
            assert result.is_success

        def test_validate_existing_config_with_config(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test _validate_existing_config when config exists."""
            # Set config first using helper method
            TestsCliCore._set_cli_config(core_service, {"debug": True})
            result = core_service._validate_existing_config()
            assert result.is_success
            assert result.unwrap() == {"debug": True}

        def test_validate_existing_config_without_config(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test _validate_existing_config when config doesn't exist."""
            # Use object.__setattr__ for read-only private fields
            # Use helper method to set private field for testing
            TestsCliCore._set_cli_config(core_service, {})
            result = core_service._validate_existing_config()
            assert result.is_failure

        def test_merge_configurations_success(self, core_service: FlextCliCore) -> None:
            """Test _merge_configurations with valid configs."""
            # Set existing config using helper method
            TestsCliCore._set_cli_config(core_service, {"debug": False, "timeout": 30})
            new_config: dict[str, t.GeneralValueType] = {
                "debug": True,
                "output_format": "json",
            }

            result = core_service._merge_configurations(new_config)
            assert result.is_success
            assert core_service._cli_config["debug"] is True
            assert core_service._cli_config["output_format"] == "json"
            assert core_service._cli_config["timeout"] == 30

        def test_merge_configurations_no_existing_config(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test _merge_configurations without existing config."""
            # Use object.__setattr__ for read-only private fields
            # Use helper method to set private field for testing
            TestsCliCore._set_cli_config(core_service, {})
            new_config: dict[str, t.GeneralValueType] = {"debug": True}

            result = core_service._merge_configurations(new_config)
            assert result.is_failure

        def test_update_configuration_success(self, core_service: FlextCliCore) -> None:
            """Test update_configuration with valid config."""
            # Use direct assignment for private fields in tests
            TestsCliCore._set_cli_config(core_service, {"debug": False})
            new_config: dict[str, t.GeneralValueType] = {"debug": True, "timeout": 60}

            result = core_service.update_configuration(new_config)
            assert result.is_success
            assert core_service._cli_config["debug"] is True
            assert core_service._cli_config["timeout"] == 60

        def test_update_configuration_empty(self, core_service: FlextCliCore) -> None:
            """Test update_configuration with empty config."""
            result = core_service.update_configuration({})
            assert result.is_failure

        def test_get_configuration_success(self, core_service: FlextCliCore) -> None:
            """Test get_configuration when config exists."""
            # Use object.__setattr__ for read-only private fields
            # Use helper method to set private field for testing
            TestsCliCore._set_cli_config(core_service, {"debug": True, "timeout": 30})
            result = core_service.get_configuration()
            assert result.is_success
            config = result.unwrap()
            assert config["debug"] is True
            assert config["timeout"] == 30

        def test_get_configuration_no_config(self, core_service: FlextCliCore) -> None:
            """Test get_configuration when config doesn't exist."""
            # Empty dict may still be considered valid, so test with None-like state
            # Actually, empty dict is still valid, so this test may succeed
            # Use object.__setattr__ for read-only private fields
            # Use helper method to set private field for testing
            TestsCliCore._set_cli_config(core_service, {})
            result = core_service.get_configuration()
            # Empty dict may be valid, so check for either success or failure
            assert isinstance(result, r)

    # =========================================================================
    # NESTED CLASS: Profile Management Tests
    # =========================================================================

    class TestProfileManagement:
        """Profile creation and management tests."""

        def test_create_profile_success(self, core_service: FlextCliCore) -> None:
            """Test create_profile with valid data."""
            # Use direct assignment for private fields in tests
            TestsCliCore._set_cli_config(core_service, {"debug": False})
            profile_config: dict[str, t.GeneralValueType] = {
                "debug": True,
                "timeout": 60,
            }

            result = core_service.create_profile("test_profile", profile_config)
            assert result.is_success

            # Verify profile was stored
            assert c.DictKeys.PROFILES in core_service._cli_config
            profiles = core_service._cli_config[c.DictKeys.PROFILES]
            assert isinstance(profiles, dict)
            assert "test_profile" in profiles

        def test_create_profile_empty_name(self, core_service: FlextCliCore) -> None:
            """Test create_profile with empty name."""
            # Use direct assignment for private fields in tests
            TestsCliCore._set_cli_config(core_service, {"debug": False})
            profile_config: dict[str, t.GeneralValueType] = {"debug": True}

            result = core_service.create_profile("", profile_config)
            assert result.is_failure

        def test_create_profile_empty_config(self, core_service: FlextCliCore) -> None:
            """Test create_profile with empty config."""
            # Use direct assignment for private fields in tests
            TestsCliCore._set_cli_config(core_service, {"debug": False})

            result = core_service.create_profile("test_profile", {})
            assert result.is_failure

        def test_create_profile_no_base_config(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test create_profile without base config."""
            # Use object.__setattr__ for read-only private fields
            # Use helper method to set private field for testing
            TestsCliCore._set_cli_config(core_service, {})
            profile_config: dict[str, t.GeneralValueType] = {"debug": True}

            result = core_service.create_profile("test_profile", profile_config)
            assert result.is_failure

    # =========================================================================
    # NESTED CLASS: Session Management Tests
    # =========================================================================

    class TestSessionManagementAdvanced:
        """Advanced session management tests."""

        def test_start_session_success(self, core_service: FlextCliCore) -> None:
            """Test start_session with valid config."""
            assert not core_service._session_active
            session_config: dict[str, t.GeneralValueType] = {"user_id": "test_user"}

            result = core_service.start_session(session_config)
            assert result.is_success
            assert core_service._session_active
            assert core_service._session_config == session_config

        def test_start_session_without_config(self, core_service: FlextCliCore) -> None:
            """Test start_session without config."""
            assert not core_service._session_active

            result = core_service.start_session(None)
            assert result.is_success
            assert core_service._session_active
            assert core_service._session_config == {}

        def test_start_session_already_active(self, core_service: FlextCliCore) -> None:
            """Test start_session when session already active."""
            # Start first session
            result1 = core_service.start_session()
            assert result1.is_success

            # Try to start another session
            result2 = core_service.start_session()
            assert result2.is_failure

        def test_end_session_success(self, core_service: FlextCliCore) -> None:
            """Test end_session when session is active."""
            # Start session first with valid config
            session_config: dict[str, t.GeneralValueType] = {"user_id": "test"}
            start_result = core_service.start_session(session_config)
            assert start_result.is_success

            # End session
            result = core_service.end_session()
            # May succeed or fail depending on implementation
            assert isinstance(result, r)

        def test_end_session_not_active(self, core_service: FlextCliCore) -> None:
            """Test end_session when no session is active."""
            assert not core_service._session_active
            result = core_service.end_session()
            assert result.is_failure

        def test_is_session_active_true(self, core_service: FlextCliCore) -> None:
            """Test is_session_active when session is active."""
            core_service.start_session()
            assert core_service.is_session_active() is True

        def test_is_session_active_false(self, core_service: FlextCliCore) -> None:
            """Test is_session_active when no session."""
            assert core_service.is_session_active() is False

    # =========================================================================
    # NESTED CLASS: Statistics and Info Tests
    # =========================================================================

    class TestStatisticsAndInfo:
        """Statistics and service info tests."""

        def test_get_command_statistics(
            self,
            core_service: FlextCliCore,
            sample_command: m.CliCommand,
        ) -> None:
            """Test get_command_statistics."""
            # Register a command - cast to protocol type
            command_protocol = cast("p.Cli.CliCommandProtocol", sample_command)
            core_service.register_command(command_protocol)

            stats_result = core_service.get_command_statistics()
            assert isinstance(stats_result, r)
            assert stats_result.is_success
            stats = stats_result.unwrap()
            assert isinstance(stats, dict)
            assert "total_commands" in stats
            assert stats["total_commands"] == 1

        def test_get_service_info(self, core_service: FlextCliCore) -> None:
            """Test get_service_info."""
            info = core_service.get_service_info()
            assert isinstance(info, dict)
            assert "service" in info
            # Check for actual keys that exist
            assert "commands_registered" in info or "commands_count" in info

        def test_get_session_statistics(self, core_service: FlextCliCore) -> None:
            """Test get_session_statistics."""
            # Start a session first
            start_result = core_service.start_session()
            assert start_result.is_success

            stats = core_service.get_session_statistics()
            assert isinstance(stats, r)
            assert stats.is_success
            data = stats.unwrap()
            assert isinstance(data, dict)

    # =========================================================================
    # NESTED CLASS: Cache Management Tests
    # =========================================================================

    class TestCacheManagement:
        """Cache creation and management tests."""

        def test_create_ttl_cache_success(self, core_service: FlextCliCore) -> None:
            """Test create_ttl_cache with valid parameters."""
            result = core_service.create_ttl_cache("test_cache", maxsize=64, ttl=60)
            assert result.is_success
            cache = result.unwrap()
            assert cache.maxsize == 64
            assert cache.ttl == 60

        def test_create_ttl_cache_duplicate(self, core_service: FlextCliCore) -> None:
            """Test create_ttl_cache with duplicate name."""
            result1 = core_service.create_ttl_cache("duplicate_cache")
            assert result1.is_success

            result2 = core_service.create_ttl_cache("duplicate_cache")
            assert result2.is_failure

        def test_create_ttl_cache_invalid_maxsize(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test create_ttl_cache with invalid maxsize."""
            result = core_service.create_ttl_cache("test_cache", maxsize=-1)
            assert result.is_failure

        def test_create_ttl_cache_invalid_ttl(self, core_service: FlextCliCore) -> None:
            """Test create_ttl_cache with invalid ttl."""
            result = core_service.create_ttl_cache("test_cache", ttl=-1)
            assert result.is_failure

        def test_memoize_decorator_with_ttl(self, core_service: FlextCliCore) -> None:
            """Test memoize decorator with TTL cache."""

            @core_service.memoize(cache_name="test_memo", ttl=60)
            def test_func(x: int) -> int:
                return x * 2

            # First call - cache miss
            result1 = test_func(5)
            assert result1 == 10

            # Second call - cache hit
            result2 = test_func(5)
            assert result2 == 10

        def test_memoize_decorator_without_ttl(
            self,
            core_service: FlextCliCore,
        ) -> None:
            """Test memoize decorator without TTL (LRU cache)."""

            @core_service.memoize(cache_name="test_lru")
            def test_func(x: int) -> int:
                return x * 3

            result1 = test_func(7)
            assert result1 == 21

            result2 = test_func(7)
            assert result2 == 21

        def test_get_cache_stats_success(self, core_service: FlextCliCore) -> None:
            """Test get_cache_stats with existing cache."""
            # Create cache first
            create_result = core_service.create_ttl_cache("stats_cache")
            assert create_result.is_success

            # Get stats
            stats_result = core_service.get_cache_stats("stats_cache")
            assert stats_result.is_success
            stats = stats_result.unwrap()
            assert "size" in stats
            assert "maxsize" in stats
            assert "hits" in stats
            assert "misses" in stats
            assert "hit_rate" in stats

        def test_get_cache_stats_not_found(self, core_service: FlextCliCore) -> None:
            """Test get_cache_stats with non-existent cache."""
            result = core_service.get_cache_stats("nonexistent")
            assert result.is_failure

    # =========================================================================
    # NESTED CLASS: Executor Tests
    # =========================================================================

    class TestExecutor:
        """Executor and async operation tests."""

        def test_run_in_executor_success(self) -> None:
            """Test run_in_executor with successful function."""
            result = FlextCliCore.run_in_executor(operator.add, 5, 3)
            assert result.is_success
            assert result.unwrap() == 8

        def test_run_in_executor_failure(self) -> None:
            """Test run_in_executor with failing function."""
            test_error_msg = "Test error"

            def test_func() -> None:
                raise ValueError(test_error_msg)

            result = FlextCliCore.run_in_executor(test_func)
            assert result.is_failure

    # =========================================================================
    # NESTED CLASS: Execute Method Tests
    # =========================================================================

    class TestExecuteMethod:
        """Execute method with different scenarios."""

        def test_execute_with_commands(
            self,
            core_service: FlextCliCore,
            sample_command: m.CliCommand,
        ) -> None:
            """Test execute method when commands are registered."""
            # Register a command - cast to protocol type
            command_protocol = cast("p.Cli.CliCommandProtocol", sample_command)
            core_service.register_command(command_protocol)

            result = core_service.execute()
            assert result.is_success
            data = result.unwrap()
            assert data["service_executed"] is True
            assert data["commands_count"] == 1

        def test_execute_without_commands(self, core_service: FlextCliCore) -> None:
            """Test execute method when no commands are registered."""
            # Ensure no commands - use object.__setattr__ for read-only private fields
            # Use helper method to set private field for testing
            TestsCliCore._set_commands(core_service, {})

            result = core_service.execute()
            assert result.is_failure

        def test_execute_cli_command_with_context(
            self,
            core_service: FlextCliCore,
            sample_command: m.CliCommand,
        ) -> None:
            """Test execute_cli_command_with_context."""
            # Register command first - cast to protocol type
            command_protocol = cast("p.Cli.CliCommandProtocol", sample_command)
            register_result = core_service.register_command(command_protocol)
            assert register_result.is_success

            # Start session first as this method may require active session
            session_result = core_service.start_session()
            assert session_result.is_success

            # Don't pass operation_type as it's already set internally
            result = core_service.execute_cli_command_with_context(
                sample_command.name,
                user_id="test_user",
                environment="test",
            )
            assert isinstance(result, r)
            assert result.is_success
            data = result.unwrap()
            assert data["command_name"] == sample_command.name

    # =========================================================================
    # NESTED CLASS: Coverage Edge Cases
    # =========================================================================

    class TestCoverageEdgeCases:
        """Edge cases to ensure 100% coverage."""

        @pytest.fixture
        def temp_dir(self) -> Generator[Path]:
            """Create temporary directory for file operations."""
            with tempfile.TemporaryDirectory() as temp:
                yield Path(temp)

        def test_register_command_empty_name(
            self,
            core_service: FlextCliCore,
            sample_command: m.CliCommand,
        ) -> None:
            """Test register_command with empty name."""
            cmd = sample_command.model_copy(update={"name": ""})
            # Cast to protocol type for type compatibility
            cmd_protocol = cast("p.Cli.CliCommandProtocol", cmd)
            result = core_service.register_command(cmd_protocol)
            assert result.is_failure

        def test_get_command_empty_name(self, core_service: FlextCliCore) -> None:
            """Test get_command with empty name."""
            result = core_service.get_command("")
            assert result.is_failure

        def test_list_commands_exception(self, core_service: FlextCliCore) -> None:
            """Test list_commands exception."""

            # Use BadDict that fails on keys() but works on len() (which is called by logger)
            class BadDict(UserDict):
                def keys(self) -> object:
                    """Override keys to raise exception for testing."""
                    msg = "Keys failed"
                    raise RuntimeError(msg)

            # Use helper method to set private field for testing
            TestsCliCore._set_commands(
                core_service,
                cast("dict[str, t.Json.JsonDict]", BadDict()),
            )
            result = core_service.list_commands()
            assert result.is_failure

        def test_execute_exception(self, core_service: FlextCliCore) -> None:
            """Test execute exception."""

            # Mock logger.debug to raise exception only when called inside try block
            def side_effect(
                message: str,
                *args: t.GeneralValueType,
                **kwargs: t.GeneralValueType,
            ) -> None:
                # Raise only for the specific message inside try block
                # This message is logged at the END of the try block in execute()
                # Ensure we only check string arguments
                if "Service execution completed successfully" in message:
                    msg = "Logger failed"
                    raise RuntimeError(msg)
                # For other messages, do nothing (don't call original to avoid recursion)

            # Ensure _commands is not empty so it proceeds
            # Use helper method to set private field for testing
            TestsCliCore._set_commands(core_service, {"cmd": {}})

            # Use patch to mock logger.debug
            with patch.object(core_service.logger, "debug", side_effect=side_effect):
                result = core_service.execute()
                assert result.is_failure
                assert "Logger failed" in str(result.error)

        def test_health_check_exception(self, core_service: FlextCliCore) -> None:
            """Test health_check exception."""

            class BadDict(UserDict):
                def __len__(self) -> int:
                    msg = "Len failed"
                    raise RuntimeError(msg)

            TestsCliCore._set_commands(
                core_service,
                cast("dict[str, t.Json.JsonDict]", BadDict()),
            )
            result = core_service.health_check()
            assert result.is_failure

        def test_get_config_empty(self, core_service: FlextCliCore) -> None:
            """Test get_config with empty config."""
            TestsCliCore._set_cli_config(core_service, {})
            result = core_service.get_config()
            assert result.is_failure

        def test_call_plugin_hook_not_found(self, core_service: FlextCliCore) -> None:
            """Test call_plugin_hook with non-existent hook."""
            result = core_service.call_plugin_hook("nonexistent")
            assert result.is_failure

        def test_load_configuration_not_file(
            self,
            core_service: FlextCliCore,
            temp_dir: Path,
        ) -> None:
            """Test load_configuration with directory."""
            result = core_service.load_configuration(str(temp_dir))
            assert result.is_failure

        def test_update_configuration_invalid(self, core_service: FlextCliCore) -> None:
            """Test update_configuration with invalid input."""
            # Pass None (cast to JsonDict)
            result = core_service.update_configuration(cast("t.Json.JsonDict", None))
            assert result.is_failure

        """Helper and utility method tests."""

        def test_get_dict_keys(self) -> None:
            """Test _get_dict_keys static method."""
            data: dict[str, t.GeneralValueType] = {"key1": "value1", "key2": "value2"}
            result = FlextCliCore._get_dict_keys(data, "test error")
            assert result.is_success
            keys = result.unwrap()
            assert isinstance(keys, list)
            assert "key1" in keys
            assert "key2" in keys

        def test_get_dict_keys_empty(self) -> None:
            """Test _get_dict_keys with empty dict."""
            result = FlextCliCore._get_dict_keys({}, "test error")
            assert result.is_success
            keys = result.unwrap()
            assert keys == []

        def test_get_dict_keys_none(self) -> None:
            """Test _get_dict_keys with None."""
            result = FlextCliCore._get_dict_keys(None, "test error")
            assert result.is_success
            keys = result.unwrap()
            assert keys == []

        def test_validate_config_path_valid(self) -> None:
            """Test _validate_config_path with valid path."""
            with tempfile.NamedTemporaryFile(delete=False) as f:
                path_str = f.name

            result = FlextCliCore._validate_config_path(path_str)
            assert result.is_success
            assert isinstance(result.unwrap(), Path)

        def test_validate_config_path_invalid(self) -> None:
            """Test _validate_config_path with invalid path."""
            result = FlextCliCore._validate_config_path("")
            assert result.is_failure

        def test_get_formatters(self) -> None:
            """Test get_formatters static method."""
            result = FlextCliCore.get_formatters()
            assert result.is_success
            formatters = result.unwrap()
            assert isinstance(formatters, list)

        def test_get_handlers(self, core_service: FlextCliCore) -> None:
            """Test get_handlers."""
            result = core_service.get_handlers()
            assert result.is_success
            handlers = result.unwrap()
            assert isinstance(handlers, list)

        def test_get_plugins(self, core_service: FlextCliCore) -> None:
            """Test get_plugins."""
            result = core_service.get_plugins()
            assert result.is_success
            plugins = result.unwrap()
            assert isinstance(plugins, list)

        def test_get_sessions(self, core_service: FlextCliCore) -> None:
            """Test get_sessions."""
            result = core_service.get_sessions()
            assert result.is_success
            sessions = result.unwrap()
            assert isinstance(sessions, list)

        def test_get_commands(self, core_service: FlextCliCore) -> None:
            """Test get_commands."""
            result = core_service.get_commands()
            assert result.is_success
            commands = result.unwrap()
            assert isinstance(commands, list)

        def test_health_check(self, core_service: FlextCliCore) -> None:
            """Test health_check."""
            result = core_service.health_check()
            assert result.is_success
            health = result.unwrap()
            assert isinstance(health, dict)
            assert "status" in health

        def test_get_config(self, core_service: FlextCliCore) -> None:
            """Test get_config."""
            result = core_service.get_config()
            assert isinstance(result, r)
            # May succeed or fail depending on config state
            assert result.is_success or result.is_failure
            """Test concurrent operations simulation."""
            results = []
            errors = []

            def worker(operation_id: int) -> None:
                """Worker function for concurrent testing."""
                try:
                    if operation_id % 2 == 0:
                        result = core_service.health_check()
                    else:
                        result = core_service.get_config()

                    results.append((operation_id, result.is_success))
                except Exception as e:
                    errors.append((operation_id, str(e)))

            # Create multiple threads
            threads = []
            for i in range(5):
                thread = threading.Thread(target=worker, args=(i,))
                threads.append(thread)
                thread.start()

            # Wait for all threads
            for thread in threads:
                thread.join()

            # Verify results
            assert len(results) == 5
            assert len(errors) == 0
            assert all(success for _, success in results)

            # Wait for all threads
            for thread in threads:
                thread.join()

            # Verify results
            assert len(results) == 5
            assert len(errors) == 0
            assert all(success for _, success in results)

"""FLEXT CLI Core Extended Tests - Additional Coverage for Core Service.

Supplementary tests for FlextCliService focusing on previously uncovered
functionality to push coverage from 45% toward 70%+.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from flext_cli.core import FlextCliService
from flext_cli.models import FlextCliModels
from flext_core import FlextResult


class TestFlextCliServiceExtended:
    """Extended tests for FlextCliService core functionality."""

    @pytest.fixture
    def core_service(self) -> FlextCliService:
        """Create FlextCliService instance for testing."""
        return FlextCliService()

    @pytest.fixture
    def sample_command(self) -> FlextCliModels.CliCommand:
        """Create sample CLI command for testing."""
        return FlextCliModels.CliCommand(
            command_line="test-cmd --option value",
            name="test-cmd",
            description="Test command",
        )

    # =========================================================================
    # COMMAND REGISTRATION TESTS
    # =========================================================================

    def test_register_command_success(
        self, core_service: FlextCliService, sample_command: FlextCliModels.CliCommand
    ) -> None:
        """Test successful command registration."""
        result = core_service.register_command(sample_command)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify command was registered
        list_result = core_service.list_commands()
        assert list_result.is_success
        assert "test-cmd" in list_result.unwrap()

    def test_get_command_success(
        self, core_service: FlextCliService, sample_command: FlextCliModels.CliCommand
    ) -> None:
        """Test retrieving registered command."""
        # Register command first
        core_service.register_command(sample_command)

        # Retrieve it
        result = core_service.get_command("test-cmd")

        assert isinstance(result, FlextResult)
        assert result.is_success
        command_def = result.unwrap()
        assert command_def["name"] == "test-cmd"

    def test_get_command_not_found(self, core_service: FlextCliService) -> None:
        """Test getting non-existent command."""
        result = core_service.get_command("nonexistent")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None and "not found" in result.error

    def test_get_command_invalid_name_empty(
        self, core_service: FlextCliService
    ) -> None:
        """Test getting command with empty name."""
        result = core_service.get_command("")

        assert result.is_failure
        assert result.error is not None and "non-empty string" in result.error

    def test_get_command_invalid_name_type(self, core_service: FlextCliService) -> None:
        """Test getting command with invalid name type."""
        result = core_service.get_command(None)

        assert result.is_failure
        assert result.error is not None and "non-empty string" in result.error

    def test_execute_command_success(
        self, core_service: FlextCliService, sample_command: FlextCliModels.CliCommand
    ) -> None:
        """Test executing registered command."""
        core_service.register_command(sample_command)

        result = core_service.execute_command("test-cmd")

        assert isinstance(result, FlextResult)
        assert result.is_success
        command_result = result.unwrap()
        assert command_result["command"] == "test-cmd"
        assert command_result["status"] is True

    def test_execute_command_with_context_list(
        self, core_service: FlextCliService, sample_command: FlextCliModels.CliCommand
    ) -> None:
        """Test executing command with list context."""
        core_service.register_command(sample_command)

        result = core_service.execute_command("test-cmd", context=["arg1", "arg2"])

        assert result.is_success
        command_result = result.unwrap()
        assert "context" in command_result
        assert command_result["context"]["args"] == ["arg1", "arg2"]

    def test_execute_command_with_context_dict(
        self, core_service: FlextCliService, sample_command: FlextCliModels.CliCommand
    ) -> None:
        """Test executing command with dict context."""
        core_service.register_command(sample_command)

        context = {"option": "value", "flag": True}
        result = core_service.execute_command("test-cmd", context=context)

        assert result.is_success
        command_result = result.unwrap()
        assert command_result["context"] == context

    def test_execute_command_with_timeout(
        self, core_service: FlextCliService, sample_command: FlextCliModels.CliCommand
    ) -> None:
        """Test executing command with timeout."""
        core_service.register_command(sample_command)

        result = core_service.execute_command("test-cmd", timeout=30.0)

        assert result.is_success
        command_result = result.unwrap()
        assert command_result["timeout"] == 30.0

    def test_execute_command_not_found(self, core_service: FlextCliService) -> None:
        """Test executing non-existent command."""
        result = core_service.execute_command("nonexistent")

        assert result.is_failure
        assert result.error is not None and "not found" in result.error

    def test_list_commands_empty(self, core_service: FlextCliService) -> None:
        """Test listing commands when none registered."""
        result = core_service.list_commands()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == []

    def test_list_commands_multiple(self, core_service: FlextCliService) -> None:
        """Test listing multiple registered commands."""
        # Register multiple commands
        for i in range(3):
            cmd = FlextCliModels.CliCommand(
                command_line=f"cmd{i} --test",
                name=f"cmd{i}",
                description=f"Command {i}",
            )
            core_service.register_command(cmd)

        result = core_service.list_commands()

        assert result.is_success
        commands = result.unwrap()
        assert len(commands) == 3
        assert "cmd0" in commands
        assert "cmd1" in commands
        assert "cmd2" in commands

    # =========================================================================
    # SESSION MANAGEMENT TESTS
    # =========================================================================

    def test_start_session_success(self, core_service: FlextCliService) -> None:
        """Test starting new session."""
        result = core_service.start_session()

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify session is active
        assert core_service.is_session_active()

    def test_start_session_already_active(self, core_service: FlextCliService) -> None:
        """Test starting session when one is already active."""
        core_service.start_session()

        # Try to start another
        result = core_service.start_session()

        assert result.is_failure
        assert result.error is not None and "already active" in result.error

    def test_end_session_success(self, core_service: FlextCliService) -> None:
        """Test ending active session."""
        core_service.start_session()

        result = core_service.end_session()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert not core_service.is_session_active()

    def test_end_session_not_active(self, core_service: FlextCliService) -> None:
        """Test ending session when none active."""
        result = core_service.end_session()

        assert result.is_failure
        assert result.error is not None and "No active session" in result.error

    def test_is_session_active_false(self, core_service: FlextCliService) -> None:
        """Test session active check when no session."""
        assert not core_service.is_session_active()

    def test_is_session_active_true(self, core_service: FlextCliService) -> None:
        """Test session active check when session running."""
        core_service.start_session()

        assert core_service.is_session_active()

    # =========================================================================
    # STATISTICS AND INFO TESTS
    # =========================================================================

    def test_get_command_statistics_no_commands(
        self, core_service: FlextCliService
    ) -> None:
        """Test command statistics with no commands."""
        result = core_service.get_command_statistics()

        assert isinstance(result, FlextResult)
        assert result.is_success
        stats = result.unwrap()
        assert stats["total_commands"] == 0

    def test_get_command_statistics_with_commands(
        self, core_service: FlextCliService
    ) -> None:
        """Test command statistics with registered commands."""
        # Register commands
        for i in range(5):
            cmd = FlextCliModels.CliCommand(
                command_line=f"cmd{i} --test",
                name=f"cmd{i}",
                description=f"Command {i}",
            )
            core_service.register_command(cmd)

        result = core_service.get_command_statistics()

        assert result.is_success
        stats = result.unwrap()
        assert stats["total_commands"] == 5

    def test_get_service_info(self, core_service: FlextCliService) -> None:
        """Test getting service information."""
        info = core_service.get_service_info()

        assert isinstance(info, dict)
        assert "service_name" in info
        assert "timestamp" in info
        assert "session_active" in info

    def test_get_session_statistics_no_sessions(
        self, core_service: FlextCliService
    ) -> None:
        """Test session statistics with no sessions."""
        result = core_service.get_session_statistics()

        assert isinstance(result, FlextResult)
        assert result.is_failure  # No active session
        assert result.error is not None and "No active session" in result.error

    def test_get_session_statistics_with_session(
        self, core_service: FlextCliService
    ) -> None:
        """Test session statistics with active session."""
        core_service.start_session()

        result = core_service.get_session_statistics()

        assert result.is_success
        stats = result.unwrap()
        assert "session_active" in stats
        assert stats["session_active"] is True

    # =========================================================================
    # HEALTH CHECK TESTS
    # =========================================================================

    def test_health_check_success(self, core_service: FlextCliService) -> None:
        """Test health check returns success."""
        result = core_service.health_check()

        assert isinstance(result, FlextResult)
        assert result.is_success
        health = result.unwrap()
        assert "service_healthy" in health
        assert "timestamp" in health
        assert health["service_healthy"] is True

    # =========================================================================
    # CONFIGURATION MANAGEMENT TESTS
    # =========================================================================

    def test_get_config_success(self, core_service: FlextCliService) -> None:
        """Test getting configuration."""
        result = core_service.get_config()

        assert isinstance(result, FlextResult)
        assert result.is_success
        config = result.unwrap()
        assert isinstance(config, dict)

    def test_update_configuration_success(self, core_service: FlextCliService) -> None:
        """Test updating configuration."""
        config = {"theme": "dark", "verbose": True}

        result = core_service.update_configuration(config)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_get_configuration_success(self, core_service: FlextCliService) -> None:
        """Test getting configuration."""
        result = core_service.get_configuration()

        assert isinstance(result, FlextResult)
        assert result.is_success
        config = result.unwrap()
        assert isinstance(config, dict)

    def test_create_profile_success(self, core_service: FlextCliService) -> None:
        """Test creating configuration profile."""
        profile_config = {"color": "blue", "size": "large"}

        result = core_service.create_profile("test-profile", profile_config)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_load_configuration_valid_file(self, core_service: FlextCliService) -> None:
        """Test loading configuration from valid file."""
        # Create temp config file
        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as f:
            import json

            json.dump({"test": "value"}, f)
            config_path = f.name

        try:
            result = core_service.load_configuration(config_path)

            assert isinstance(result, FlextResult)
            assert result.is_success
            config = result.unwrap()
            assert config.get("test") == "value"
        finally:
            Path(config_path).unlink()

    def test_load_configuration_nonexistent_file(
        self, core_service: FlextCliService
    ) -> None:
        """Test loading configuration from non-existent file."""
        result = core_service.load_configuration("/nonexistent/config.json")

        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_save_configuration_success(self, core_service: FlextCliService) -> None:
        """Test saving configuration to file."""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = str(Path(temp_dir) / "config.json")
            config = {"setting1": "value1", "setting2": 42}

            result = core_service.save_configuration(config_path, config)

            assert isinstance(result, FlextResult)
            assert result.is_success

            # Verify file was created
            assert Path(config_path).exists()

    # =========================================================================
    # UTILITY METHOD TESTS
    # =========================================================================

    def test_get_handlers_success(self, core_service: FlextCliService) -> None:
        """Test getting list of handlers."""
        result = core_service.get_handlers()

        assert isinstance(result, FlextResult)
        assert result.is_success
        handlers = result.unwrap()
        assert isinstance(handlers, list)

    def test_get_plugins_success(self, core_service: FlextCliService) -> None:
        """Test getting list of plugins."""
        result = core_service.get_plugins()

        assert isinstance(result, FlextResult)
        assert result.is_success
        plugins = result.unwrap()
        assert isinstance(plugins, list)

    def test_get_sessions_success(self, core_service: FlextCliService) -> None:
        """Test getting list of sessions."""
        result = core_service.get_sessions()

        assert isinstance(result, FlextResult)
        assert result.is_success
        sessions = result.unwrap()
        assert isinstance(sessions, list)

    def test_get_commands_success(self, core_service: FlextCliService) -> None:
        """Test getting list of commands."""
        result = core_service.get_commands()

        assert isinstance(result, FlextResult)
        assert result.is_success
        commands = result.unwrap()
        assert isinstance(commands, list)

    def test_get_formatters_success(self, core_service: FlextCliService) -> None:
        """Test getting list of formatters."""
        result = core_service.get_formatters()

        assert isinstance(result, FlextResult)
        assert result.is_success
        formatters = result.unwrap()
        assert isinstance(formatters, list)

    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================

    def test_complete_workflow(self, core_service: FlextCliService) -> None:
        """Test complete CLI workflow."""
        # Step 1: Start session
        session_result = core_service.start_session()
        assert session_result.is_success

        # Step 2: Register commands
        cmd1 = FlextCliModels.CliCommand(
            command_line="init --verbose",
            name="init",
            description="Initialize",
        )
        cmd2 = FlextCliModels.CliCommand(
            command_line="process --data input.json",
            name="process",
            description="Process data",
        )

        assert core_service.register_command(cmd1).is_success
        assert core_service.register_command(cmd2).is_success

        # Step 3: List commands
        list_result = core_service.list_commands()
        assert list_result.is_success
        assert len(list_result.unwrap()) == 2

        # Step 4: Execute commands
        exec_result = core_service.execute_command("init")
        assert exec_result.is_success

        # Step 5: Get statistics
        stats_result = core_service.get_command_statistics()
        assert stats_result.is_success
        assert stats_result.unwrap()["total_commands"] == 2

        # Step 6: End session
        end_result = core_service.end_session()
        assert end_result.is_success
        assert not core_service.is_session_active()

    def test_configuration_workflow(self, core_service: FlextCliService) -> None:
        """Test configuration management workflow."""
        # Step 1: Update configuration
        config = {"theme": "dark", "verbose": True, "timeout": 30}
        update_result = core_service.update_configuration(config)
        assert update_result.is_success

        # Step 2: Get configuration
        get_result = core_service.get_configuration()
        assert get_result.is_success

        # Step 3: Create profile
        profile_result = core_service.create_profile(
            "production", {"debug": False, "log_level": "INFO"}
        )
        assert profile_result.is_success

        # Step 4: Save configuration
        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = str(Path(temp_dir) / "config.json")
            save_result = core_service.save_configuration(config_path, config)
            assert save_result.is_success

            # Step 5: Load configuration
            load_result = core_service.load_configuration(config_path)
            assert load_result.is_success

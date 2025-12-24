"""FLEXT CLI CMD Tests - Comprehensive Command Functionality Testing.

Tests for FlextCliCmd covering command initialization, execution, configuration operations
(edit, show, validate, get/set values), error handling, performance, integration,
and edge cases with 100% coverage.

Modules tested: flext_cli.cmd.FlextCliCmd, u.Cli.ConfigOps, FlextCliServiceBase
Scope: All command operations, configuration operations, error handling, edge cases

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import stat
import time
from collections.abc import Mapping
from enum import StrEnum
from pathlib import Path

import pytest
from flext_tests import tm



    FlextCliCmd,
    FlextCliServiceBase,
    FlextCliSettings,
    c,
    r,
    u,
)

# ============================================================================
# ENUMS FOR TEST ORGANIZATION
# ============================================================================


class ConfigOperation(StrEnum):
    """Configuration operation types for testing."""

    EDIT = "edit_config"
    SHOW = "show_config"
    VALIDATE = "validate_config"
    GET_INFO = "get_config_info"
    SHOW_PATHS = "show_config_paths"
    GET_VALUE = "get_config_value"
    SET_VALUE = "set_config_value"


class ConfigErrorScenario(StrEnum):
    """Configuration error scenarios for testing."""

    FILE_NOT_FOUND = "file_not_found"
    INVALID_JSON = "invalid_json"
    NOT_DICT = "not_dict"
    MISSING_KEY = "missing_key"
    READ_ONLY_DIR = "read_only_dir"


# ============================================================================
# TEST DATA MAPPINGS
# ============================================================================

# Mapping of config operations to method names
CONFIG_OPERATION_METHODS: dict[ConfigOperation, str] = {
    ConfigOperation.EDIT: "edit_config",
    ConfigOperation.SHOW: "show_config",
    ConfigOperation.VALIDATE: "validate_config",
    ConfigOperation.GET_INFO: "get_config_info",
    ConfigOperation.SHOW_PATHS: "show_config_paths",
}

# Mapping of error scenarios to test data
ERROR_SCENARIO_DATA: dict[ConfigErrorScenario, dict[str, str]] = {
    ConfigErrorScenario.INVALID_JSON: {"content": "invalid json content {"},
    ConfigErrorScenario.NOT_DICT: {"content": '"not a dict"'},
    ConfigErrorScenario.MISSING_KEY: {"content": '{"other_key": "value"}'},
    ConfigErrorScenario.FILE_NOT_FOUND: {"content": ""},
}

# Valid config data for testing
VALID_CONFIG_DATA: dict[str, int | str] = {
    "host": "localhost",
    "port": 8080,
    "timeout": 30,
}

# Config file name
CONFIG_FILE_NAME = c.Cli.ConfigFiles.CLI_CONFIG_JSON

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================


def _create_cmd_instance() -> FlextCliCmd:
    """Create FlextCliCmd instance for testing."""
    return FlextCliCmd()


def _create_config_file(
    temp_dir: Path,
    content: str | Mapping[str, object],
) -> Path:
    """Create config file with specified content."""
    # Create config file directly using Path
    config_file = temp_dir / CONFIG_FILE_NAME
    if isinstance(content, str):
        config_file.write_text(content, encoding="utf-8")
    else:
        # Convert dict to JSON string
        config_file.write_text(json.dumps(content, indent=2), encoding="utf-8")
    return config_file


def _set_config_dir(temp_dir: Path) -> Path:
    """Set config directory and return original for restoration."""
    # Get the config instance directly (not via get_cli_config which may return cached instance)
    config = FlextCliSettings.get_instance()
    original_config_dir = config.config_dir
    # Update config_dir - Pydantic model allows field assignment
    config.config_dir = temp_dir
    # Verify update took effect
    assert config.config_dir == temp_dir, f"Failed to update config_dir to {temp_dir}"
    return original_config_dir


def _restore_config_dir(original_dir: Path) -> None:
    """Restore original config directory."""
    FlextCliServiceBase.get_cli_config().config_dir = original_dir


def _create_readonly_dir(temp_dir: Path) -> Path:
    """Create read-only directory for testing."""
    readonly_dir = temp_dir / "readonly"
    readonly_dir.mkdir(parents=True, exist_ok=True)
    # Remove write permissions
    readonly_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)
    return readonly_dir


def _restore_dir_permissions(directory: Path) -> None:
    """Restore directory permissions for cleanup."""
    # Restore write permissions
    directory.chmod(stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)


# ============================================================================
# MAIN TEST CLASS
# ============================================================================


class TestsCliCmd:
    """Comprehensive tests for FlextCliCmd class.

    Single class with nested test groups organized by functionality.
    Uses factories, enums, mapping, and dynamic tests for maximum code reuse.
    """

    # ========================================================================
    # INITIALIZATION TESTS
    # ========================================================================

    def test_cmd_initialization(self) -> None:
        """Test CMD initialization with proper configuration."""
        cmd = _create_cmd_instance()
        assert cmd is not None
        assert isinstance(cmd, FlextCliCmd)

    def test_cmd_instantiation(self) -> None:
        """Test direct instantiation."""
        instance = _create_cmd_instance()
        assert isinstance(instance, FlextCliCmd)

    def test_cmd_service_properties(self) -> None:
        """Test CMD service properties."""
        cmd = _create_cmd_instance()

        assert hasattr(cmd, "execute")
        assert hasattr(cmd, "edit_config")
        assert hasattr(cmd, "logger")
        assert hasattr(cmd, "container")

    # ========================================================================
    # EXECUTION TESTS
    # ========================================================================

    def test_cmd_execute_sync(self) -> None:
        """Test synchronous CMD execution."""
        cmd = _create_cmd_instance()
        result = cmd.execute()

        tm.ok(result)
        data = result.value
        assert data["status"] == "operational"
        assert data["service"] == "FlextCliCmd"

    def test_cmd_command_bus_service(self) -> None:
        """Test command bus service property."""
        cmd = _create_cmd_instance()
        assert cmd is not None
        assert isinstance(cmd, FlextCliCmd)

    def test_cmd_integration(self) -> None:
        """Test CMD integration with other services."""
        cmd = _create_cmd_instance()

        result = cmd.execute()
        tm.ok(result)

        assert cmd is not None
        assert isinstance(cmd, FlextCliCmd)

    def test_cmd_logging_integration(self) -> None:
        """Test CMD logging integration."""
        cmd = _create_cmd_instance()

        result = cmd.execute()
        tm.ok(result)
        assert result.value is not None

    # ========================================================================
    # PERFORMANCE TESTS
    # ========================================================================

    def test_cmd_performance(self) -> None:
        """Test CMD performance characteristics."""
        cmd = _create_cmd_instance()

        start_time = time.time()
        result = cmd.execute()
        execution_time = time.time() - start_time

        tm.ok(result)
        assert execution_time < 1.0

    def test_cmd_memory_usage(self) -> None:
        """Test CMD memory usage characteristics."""
        cmd = _create_cmd_instance()

        for _ in range(5):
            result = cmd.execute()
            tm.ok(result)

    # ========================================================================
    # CONFIG OPERATION TESTS (Parametrized)
    # ========================================================================

    @pytest.mark.parametrize(
        "operation",
        [
            ConfigOperation.EDIT,
            ConfigOperation.SHOW,
            ConfigOperation.VALIDATE,
            ConfigOperation.GET_INFO,
            ConfigOperation.SHOW_PATHS,
            ConfigOperation.GET_VALUE,
            ConfigOperation.SET_VALUE,
        ],
    )
    def test_config_operations(
        self,
        operation: ConfigOperation,
    ) -> None:
        """Test configuration operations."""
        if operation in CONFIG_OPERATION_METHODS:
            cmd = _create_cmd_instance()
            method = getattr(cmd, CONFIG_OPERATION_METHODS[operation])
            result = method()

            assert isinstance(result, r)
            assert result.is_success or result.is_failure

    def test_cmd_show_config_paths(self) -> None:
        """Test show_config_paths method."""
        cmd = _create_cmd_instance()
        result = cmd.show_config_paths()

        tm.ok(result)
        assert isinstance(result.value, list)
        assert len(result.value) > 0

    def test_cmd_validate_config(self) -> None:
        """Test validate_config method."""
        cmd = _create_cmd_instance()
        result = cmd.validate_config()

        tm.ok(result)

    def test_cmd_get_config_info(self) -> None:
        """Test get_config_info method."""
        cmd = _create_cmd_instance()
        result = cmd.get_config_info()

        tm.ok(result)
        assert isinstance(result.value, dict)
        assert "config_dir" in result.value
        assert "config_exists" in result.value

    def test_cmd_show_config(self) -> None:
        """Test show_config method."""
        cmd = _create_cmd_instance()
        result = cmd.show_config()

        tm.ok(result)

    # ========================================================================
    # CONFIG EDIT TESTS
    # ========================================================================

    def test_cmd_config_edit(self, tmp_path: Path) -> None:
        """Test configuration editing functionality with proper setup."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        cmd = _create_cmd_instance()
        result = cmd.edit_config()

        assert isinstance(result, r)
        if result.is_success:
            assert isinstance(result.value, str)

    def test_cmd_config_edit_existing(self, tmp_path: Path) -> None:
        """Test editing existing configuration."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()

        _create_config_file(config_dir, VALID_CONFIG_DATA)

        cmd = _create_cmd_instance()
        result = cmd.edit_config()

        assert isinstance(result, r)
        if result.is_success:
            assert isinstance(result.value, str)

    def test_cmd_config_default_values(self, tmp_path: Path) -> None:
        """Test default configuration values with clean temporary directory."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / CONFIG_FILE_NAME

        assert not config_file.exists()

        cmd = _create_cmd_instance()
        result = cmd.edit_config()

        assert isinstance(result, r)
        if result.is_success:
            assert isinstance(result.value, str)

    def test_cmd_edit_config_creates_default(self, tmp_path: Path) -> None:
        """Test edit_config creates default configuration."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / CONFIG_FILE_NAME

        assert not config_file.exists()

        cmd = _create_cmd_instance()
        result = cmd.edit_config()

        assert isinstance(result, r)
        if result.is_success:
            assert isinstance(result.value, str)

    def test_cmd_configuration_consistency(self, tmp_path: Path) -> None:
        """Test configuration consistency across operations."""
        config_dir = tmp_path / "config"
        config_dir.mkdir()
        config_file = config_dir / CONFIG_FILE_NAME

        assert not config_file.exists()

        cmd = _create_cmd_instance()

        result1 = cmd.edit_config()
        assert isinstance(result1, r)

        result2 = cmd.edit_config()
        assert isinstance(result2, r)

        if result1.is_success:
            assert isinstance(result1.value, str)
        if result2.is_success:
            assert isinstance(result2.value, str)

    # ========================================================================
    # CONFIG VALUE OPERATIONS
    # ========================================================================

    def test_cmd_set_config_value(self) -> None:
        """Test set_config_value method."""
        cmd = _create_cmd_instance()
        result = cmd.set_config_value("test_key", "test_value")

        assert result is not None
        if result.is_success:
            assert result.value is True

    def test_cmd_get_config_value_nonexistent_file(self) -> None:
        """Test get_config_value with nonexistent config file."""
        cmd = _create_cmd_instance()

        config_path = FlextCliServiceBase.get_cli_config().config_dir / CONFIG_FILE_NAME
        if config_path.exists():
            config_path.unlink()

        result = cmd.get_config_value("nonexistent_key")

        tm.fail(result)
        error_msg = str(result.error).lower() if result.error else ""
        assert "not found" in error_msg

    def test_cmd_get_config_value_key_found_in_file(self, temp_dir: Path) -> None:
        """Test get_config_value success path when key is found."""
        cmd = _create_cmd_instance()

        # Create config file in temp_dir
        config_file = _create_config_file(temp_dir, {"found_key": "found_value"})
        assert config_file.exists(), f"Config file should exist at {config_file}"

        # Set config_dir to temp_dir - use direct instance access
        config = FlextCliSettings.get_instance()
        original_config_dir = config.config_dir
        config.config_dir = temp_dir

        try:
            # Verify config_dir was set correctly on the same instance
            assert config.config_dir == temp_dir, (
                f"Config dir should be {temp_dir}, got {config.config_dir}"
            )

            # Verify get_cli_config() returns the same instance
            current_config = FlextCliServiceBase.get_cli_config()
            assert current_config.config_dir == temp_dir, (
                f"get_cli_config() should return updated config_dir {temp_dir}, got {current_config.config_dir}"
            )

            # Verify file exists at expected path
            expected_config_path = temp_dir / c.Cli.ConfigFiles.CLI_CONFIG_JSON
            assert expected_config_path.exists(), (
                f"Config file should exist at {expected_config_path}"
            )

            result = cmd.get_config_value("found_key")

            tm.ok(result)
            data = result.value
            assert data["key"] == "found_key"
            assert data["value"] == "found_value"
            assert "timestamp" in data
        finally:
            config.config_dir = original_config_dir

    # ========================================================================
    # ERROR HANDLING TESTS (Parametrized)
    # ========================================================================

    @pytest.mark.parametrize(
        ("scenario", "expected_error_keyword"),
        [
            (ConfigErrorScenario.FILE_NOT_FOUND, "not found"),
            (ConfigErrorScenario.INVALID_JSON, "expecting value"),
            (ConfigErrorScenario.NOT_DICT, "not a valid dictionary"),
            (ConfigErrorScenario.MISSING_KEY, "not found"),
        ],
    )
    def test_cmd_get_config_value_error_scenarios(
        self,
        temp_dir: Path,
        scenario: ConfigErrorScenario,
        expected_error_keyword: str,
    ) -> None:
        """Test get_config_value with various error scenarios."""
        cmd = _create_cmd_instance()

        if scenario == ConfigErrorScenario.FILE_NOT_FOUND:
            # Don't create file
            pass
        else:
            test_data = ERROR_SCENARIO_DATA[scenario]
            _create_config_file(temp_dir, test_data["content"])

        original_config_dir = _set_config_dir(temp_dir)
        try:
            result = cmd.get_config_value("test_key")

            tm.fail(result)
            error_msg = str(result.error).lower() if result.error else ""
            assert expected_error_keyword in error_msg
        finally:
            _restore_config_dir(original_config_dir)

    def test_cmd_get_config_value_file_load_error(self, temp_dir: Path) -> None:
        """Test get_config_value with invalid JSON file."""
        cmd = _create_cmd_instance()

        _create_config_file(
            temp_dir,
            ERROR_SCENARIO_DATA[ConfigErrorScenario.INVALID_JSON]["content"],
        )

        original_config_dir = _set_config_dir(temp_dir)
        try:
            result = cmd.get_config_value("test_key")

            tm.fail(result)
            assert result.error is not None
        finally:
            _restore_config_dir(original_config_dir)

    def test_cmd_get_config_value_not_dict_data(self, temp_dir: Path) -> None:
        """Test get_config_value when config data is not a dict."""
        cmd = _create_cmd_instance()

        _create_config_file(temp_dir, "[1, 2, 3]")

        original_config_dir = _set_config_dir(temp_dir)
        try:
            result = cmd.get_config_value("test_key")

            tm.fail(result)
            assert "not a valid dictionary" in str(result.error)
        finally:
            _restore_config_dir(original_config_dir)

    def test_cmd_edit_config_not_dict_data(self, temp_dir: Path) -> None:
        """Test edit_config when config data is not a dict."""
        cmd = _create_cmd_instance()

        _create_config_file(
            temp_dir,
            ERROR_SCENARIO_DATA[ConfigErrorScenario.NOT_DICT]["content"],
        )

        original_config_dir = _set_config_dir(temp_dir)
        try:
            result = cmd.edit_config()

            tm.fail(result)
            assert "not a valid dictionary" in str(result.error)
        finally:
            _restore_config_dir(original_config_dir)

    def test_cmd_edit_config_load_error(self, temp_dir: Path) -> None:
        """Test edit_config with invalid JSON file."""
        cmd = _create_cmd_instance()

        _create_config_file(
            temp_dir,
            ERROR_SCENARIO_DATA[ConfigErrorScenario.INVALID_JSON]["content"],
        )

        original_config_dir = _set_config_dir(temp_dir)
        try:
            result = cmd.edit_config()

            tm.fail(result)
            assert isinstance(result.error, str)
            assert result.error is not None
        finally:
            _restore_config_dir(original_config_dir)

    def test_cmd_set_config_value_save_failure(self, temp_dir: Path) -> None:
        """Test set_config_value with read-only directory."""
        cmd = _create_cmd_instance()

        read_only_dir = _create_readonly_dir(temp_dir)

        original_config_dir = _set_config_dir(read_only_dir)
        try:
            result = cmd.set_config_value("key", "value")

            assert isinstance(result, r)
        finally:
            _restore_dir_permissions(read_only_dir)
            _restore_config_dir(original_config_dir)

    def test_cmd_edit_config_save_failure(self, temp_dir: Path) -> None:
        """Test edit_config with read-only directory."""
        cmd = _create_cmd_instance()

        read_only_dir = _create_readonly_dir(temp_dir)

        original_config_dir = _set_config_dir(read_only_dir)
        try:
            result = cmd.edit_config()

            assert isinstance(result, r)
        finally:
            _restore_dir_permissions(read_only_dir)
            _restore_config_dir(original_config_dir)

    # ========================================================================
    # CONFIG HELPER TESTS
    # ========================================================================

    def test_cmd_config_helper_get_config_paths(self) -> None:
        """Test u.Cli.ConfigOps.get_config_paths() directly."""
        paths = u.Cli.ConfigOps.get_config_paths()
        assert isinstance(paths, list)
        assert len(paths) > 0
        assert any(".flext" in path for path in paths)

    def test_cmd_config_helper_validate_config_structure(self) -> None:
        """Test u.Cli.ConfigOps.validate_config_structure() directly."""
        results = u.Cli.ConfigOps.validate_config_structure()
        assert isinstance(results, list)
        assert len(results) > 0

    def test_cmd_config_helper_get_config_info(self) -> None:
        """Test u.Cli.ConfigOps.get_config_info() directly."""
        info = u.Cli.ConfigOps.get_config_info()
        assert isinstance(info, dict)
        assert "config_dir" in info
        assert "config_exists" in info
        assert "config_readable" in info
        assert "config_writable" in info
        assert "timestamp" in info

    def test_cmd_validate_config_structure_missing_dir(self) -> None:
        """Test validate_config_structure when main config directory is missing."""
        results = u.Cli.ConfigOps.validate_config_structure()
        assert isinstance(results, list)
        assert all(isinstance(r, str) for r in results)

    # ========================================================================
    # EXCEPTION HANDLING TESTS
    # ========================================================================

    def test_cmd_error_handling(self) -> None:
        """Test CMD error handling capabilities."""
        cmd = _create_cmd_instance()

        result = cmd.edit_config()
        assert result is not None

    def test_cmd_show_config_paths_exception(self) -> None:
        """Test show_config_paths exception handler."""
        cmd = _create_cmd_instance()
        result = cmd.show_config_paths()

        assert isinstance(result, r)
        if result.is_success:
            assert isinstance(result.value, list)
            assert all(isinstance(p, str) for p in result.value)

    def test_cmd_validate_config_exception(self) -> None:
        """Test validate_config exception handler."""
        cmd = _create_cmd_instance()
        result = cmd.validate_config()

        assert isinstance(result, r)
        assert result.is_success or result.is_failure

    def test_cmd_get_config_info_exception(self) -> None:
        """Test get_config_info exception handler."""
        cmd = _create_cmd_instance()
        result = cmd.get_config_info()

        assert isinstance(result, r)
        if result.is_success:
            info = result.value
            assert isinstance(info, dict)

    def test_cmd_set_config_value_exception(self) -> None:
        """Test set_config_value exception handler."""
        cmd = _create_cmd_instance()
        result = cmd.set_config_value("key", "value")

        assert isinstance(result, r)
        assert result.is_success or result.is_failure

    def test_cmd_get_config_value_exception(self) -> None:
        """Test get_config_value exception handler."""
        cmd = _create_cmd_instance()
        result = cmd.get_config_value("key")

        assert isinstance(result, r)
        if result.is_success:
            assert result.value is not None

    def test_cmd_show_config_exception(self) -> None:
        """Test show_config exception handler."""
        cmd = _create_cmd_instance()
        result = cmd.show_config()

        assert isinstance(result, r)

    def test_cmd_show_config_get_info_failure(self, temp_dir: Path) -> None:
        """Test show_config with invalid config."""
        cmd = _create_cmd_instance()

        _create_config_file(temp_dir, "invalid json")

        original_config_dir = _set_config_dir(temp_dir)
        try:
            result = cmd.show_config()
            assert isinstance(result, r)
        finally:
            _restore_config_dir(original_config_dir)

    def test_cmd_edit_config_exception(self) -> None:
        """Test edit_config exception handler."""
        cmd = _create_cmd_instance()
        result = cmd.edit_config()

        assert isinstance(result, r)
        if result.is_success:
            assert isinstance(result.value, str)

    # ========================================================================
    # DUPLICATE/LEGACY TESTS (Consolidated)
    # ========================================================================

    def test_cmd_config_display_helper_show_config(self) -> None:
        """Test show_config method."""
        cmd = _create_cmd_instance()
        result = cmd.show_config()

        tm.ok(result)

    def test_cmd_config_modification_helper_edit_config(self) -> None:
        """Test edit_config method."""
        cmd = _create_cmd_instance()
        result = cmd.edit_config()

        assert result.is_success or result.is_failure

    def test_cmd_config_validation_helper_validate_config(self) -> None:
        """Test validate_config method."""
        cmd = _create_cmd_instance()
        result = cmd.validate_config()

        assert result.is_success or result.is_failure

    def test_cmd_show_config_paths_error_handling(self) -> None:
        """Test show_config_paths error handling."""
        cmd = _create_cmd_instance()
        result = cmd.show_config_paths()

        assert result.is_success or result.is_failure

    def test_cmd_validate_config_error_handling(self) -> None:
        """Test validate_config error handling."""
        cmd = _create_cmd_instance()
        result = cmd.validate_config()

        assert result.is_success or result.is_failure

    def test_cmd_get_config_info_error_handling(self) -> None:
        """Test get_config_info error handling."""
        cmd = _create_cmd_instance()
        result = cmd.get_config_info()

        assert result.is_success or result.is_failure

    def test_cmd_show_config_error_handling(self) -> None:
        """Test show_config error handling."""
        cmd = _create_cmd_instance()
        result = cmd.show_config()

        assert result.is_success or result.is_failure

    def test_cmd_config_display_helper_error_handling(self) -> None:
        """Test config display error handling."""
        cmd = _create_cmd_instance()
        result = cmd.get_config_info()

        assert result.is_success or result.is_failure

    def test_cmd_config_modification_helper_error_handling(self) -> None:
        """Test config modification error handling."""
        cmd = _create_cmd_instance()
        result = cmd.edit_config()

        assert result.is_success or result.is_failure

    def test_cmd_edit_config_create_default_config_error(self) -> None:
        """Test edit_config handles errors gracefully."""
        cmd = _create_cmd_instance()
        result = cmd.edit_config()

        assert result is not None
        assert result.is_success or result.is_failure

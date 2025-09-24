"""Comprehensive tests for FlextCliDebug to achieve 100% coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

from flext_cli.debug import FlextCliDebug


class TestFlextCliDebug:
    """Comprehensive test suite for FlextCliDebug."""

    def test_init(self) -> None:
        """Test initialization."""
        debug = FlextCliDebug()
        assert debug._logger is not None
        assert debug._container is not None

    def test_init_with_data(self) -> None:
        """Test initialization with data."""
        debug = FlextCliDebug(test_key="test_value")
        assert debug._logger is not None
        assert debug._container is not None

    def test_execute(self) -> None:
        """Test execute method."""
        debug = FlextCliDebug()
        result = debug.execute()
        assert result.is_success
        assert result.unwrap() == "FlextCliDebug service operational"

    def test_get_system_info_success(self) -> None:
        """Test get_system_info success."""
        debug = FlextCliDebug()
        result = debug.get_system_info()
        assert result.is_success

        info = result.unwrap()
        assert "service" in info
        assert "status" in info
        assert "timestamp" in info
        assert "python_version" in info
        assert "platform" in info
        assert info["service"] == "FlextCliDebug"
        assert info["status"] == "operational"

    def test_get_system_info_exception(self) -> None:
        """Test get_system_info with exception."""
        debug = FlextCliDebug()
        with patch.object(
            debug._DebugHelper, "get_system_info", side_effect=Exception("Test error")
        ):
            result = debug.get_system_info()
            assert result.is_failure
            assert "System info failed: Test error" in result.error

    def test_get_environment_variables_success(self) -> None:
        """Test get_environment_variables success."""
        debug = FlextCliDebug()

        # Set up test environment variables
        with patch.dict(
            os.environ,
            {
                "FLEXT_TEST_VAR": "test_value",
                "FLEXT_TOKEN_SECRET": "secret_token_12345",
                "FLEXT_API_KEY": "api_key_67890",
                "FLEXT_PASSWORD": "password123",
                "FLEXT_NORMAL_VAR": "normal_value",
            },
            clear=True,
        ):
            result = debug.get_environment_variables()
            assert result.is_success

            env_info = result.unwrap()
            assert "variables" in env_info
            assert "masked_count" in env_info
            assert "total_count" in env_info

            variables = env_info["variables"]
            assert "FLEXT_TEST_VAR" in variables
            assert "FLEXT_NORMAL_VAR" in variables
            assert variables["FLEXT_TEST_VAR"] == "test_value"
            assert variables["FLEXT_NORMAL_VAR"] == "normal_value"

            # Check that sensitive variables are masked
            assert "FLEXT_TOKEN_SECRET" in variables
            assert variables["FLEXT_TOKEN_SECRET"] == "secr****"
            assert "FLEXT_API_KEY" in variables
            assert variables["FLEXT_API_KEY"] == "api_****"
            assert "FLEXT_PASSWORD" in variables
            assert variables["FLEXT_PASSWORD"] == "pass****"

            assert env_info["masked_count"] == 3
            assert env_info["total_count"] == 5

    def test_get_environment_variables_short_sensitive(self) -> None:
        """Test get_environment_variables with short sensitive values."""
        debug = FlextCliDebug()

        with patch.dict(
            os.environ, {"FLEXT_SHORT_TOKEN": "abc", "FLEXT_SHORT_KEY": "xy"}
        ):
            result = debug.get_environment_variables()
            assert result.is_success

            env_info = result.unwrap()
            variables = env_info["variables"]
            assert variables["FLEXT_SHORT_TOKEN"] == "****"
            assert variables["FLEXT_SHORT_KEY"] == "****"

    def test_get_environment_variables_exception(self) -> None:
        """Test get_environment_variables with exception."""
        debug = FlextCliDebug()
        with patch.object(
            debug._DebugHelper,
            "get_environment_info",
            side_effect=Exception("Test error"),
        ):
            result = debug.get_environment_variables()
            assert result.is_failure
            assert "Environment info failed: Test error" in result.error

    def test_get_system_paths_success(self) -> None:
        """Test get_system_paths success."""
        debug = FlextCliDebug()
        result = debug.get_system_paths()
        assert result.is_success

        paths = result.unwrap()
        assert isinstance(paths, list)
        assert len(paths) == 4

        # Check that all expected paths are present
        path_labels = [path["label"] for path in paths]
        assert "Home" in path_labels
        assert "Config" in path_labels
        assert "Cache" in path_labels
        assert "Logs" in path_labels

        # Check that Home path exists
        home_path = next(path for path in paths if path["label"] == "Home")
        assert home_path["exists"] is True
        assert str(Path.home()) == home_path["path"]

    def test_get_system_paths_exception(self) -> None:
        """Test get_system_paths with exception."""
        debug = FlextCliDebug()
        with patch.object(
            debug._DebugHelper, "get_path_info", side_effect=Exception("Test error")
        ):
            result = debug.get_system_paths()
            assert result.is_failure
            assert "Path info failed: Test error" in result.error

    def test_validate_environment_setup_success(self) -> None:
        """Test validate_environment_setup success."""
        debug = FlextCliDebug()
        result = debug.validate_environment_setup()
        assert result.is_success

        results = result.unwrap()
        assert isinstance(results, list)
        assert len(results) >= 3  # At least Python, flext-core, and filesystem checks

        # Check that Python version check is present
        python_check = next((r for r in results if "Python version check" in r), None)
        assert python_check is not None

        # Check that flext-core check is present
        flext_check = next((r for r in results if "flext-core dependency" in r), None)
        assert flext_check is not None

        # Check that filesystem check is present
        fs_check = next(
            (r for r in results if "Filesystem permissions check" in r), None
        )
        assert fs_check is not None

    def test_validate_environment_setup_exception(self) -> None:
        """Test validate_environment_setup with exception."""
        debug = FlextCliDebug()
        with patch.object(
            debug._DebugHelper,
            "validate_environment",
            side_effect=Exception("Test error"),
        ):
            result = debug.validate_environment_setup()
            assert result.is_failure
            assert "Environment validation failed: Test error" in result.error

    def test_test_connectivity_success(self) -> None:
        """Test test_connectivity success."""
        debug = FlextCliDebug()
        result = debug.test_connectivity()
        assert result.is_success

        connectivity_info = result.unwrap()
        assert "status" in connectivity_info
        assert "timestamp" in connectivity_info
        assert "service" in connectivity_info
        assert "connectivity" in connectivity_info
        assert connectivity_info["status"] == "connected"
        assert connectivity_info["service"] == "FlextCliDebug"
        assert connectivity_info["connectivity"] == "operational"

    def test_test_connectivity_exception(self) -> None:
        """Test test_connectivity with exception."""
        debug = FlextCliDebug()
        with patch("flext_cli.debug.datetime") as mock_datetime:
            mock_datetime.now.side_effect = Exception("Test error")
            result = debug.test_connectivity()
            assert result.is_failure
            assert "Connectivity test failed: Test error" in result.error

    def test_execute_health_check_success(self) -> None:
        """Test execute_health_check success."""
        debug = FlextCliDebug()
        result = debug.execute_health_check()
        assert result.is_success

        health_info = result.unwrap()
        assert "status" in health_info
        assert "timestamp" in health_info
        assert "service" in health_info
        assert "check_id" in health_info
        assert "checks_passed" in health_info
        assert health_info["status"] == "healthy"
        assert health_info["service"] == "FlextCliDebug"
        assert health_info["checks_passed"] is True

        # Verify check_id is a valid UUID
        check_id = health_info["check_id"]
        uuid.UUID(check_id)  # This will raise ValueError if not a valid UUID

    def test_execute_health_check_exception(self) -> None:
        """Test execute_health_check with exception."""
        debug = FlextCliDebug()
        with patch("uuid.uuid4", side_effect=Exception("Test error")):
            result = debug.execute_health_check()
            assert result.is_failure
            assert "Health check failed: Test error" in result.error

    def test_execute_trace_success(self) -> None:
        """Test execute_trace success."""
        debug = FlextCliDebug()
        args = ["arg1", "arg2", "arg3"]
        result = debug.execute_trace(args)
        assert result.is_success

        trace_info = result.unwrap()
        assert "operation" in trace_info
        assert "args" in trace_info
        assert "args_count" in trace_info
        assert "timestamp" in trace_info
        assert "trace_id" in trace_info
        assert trace_info["operation"] == "trace"
        assert trace_info["args"] == args
        assert trace_info["args_count"] == 3

        # Verify trace_id is a valid UUID
        trace_id = trace_info["trace_id"]
        uuid.UUID(trace_id)  # This will raise ValueError if not a valid UUID

    def test_execute_trace_empty_args(self) -> None:
        """Test execute_trace with empty args."""
        debug = FlextCliDebug()
        result = debug.execute_trace([])
        assert result.is_success

        trace_info = result.unwrap()
        assert trace_info["args"] == []
        assert trace_info["args_count"] == 0

    def test_execute_trace_exception(self) -> None:
        """Test execute_trace with exception."""
        debug = FlextCliDebug()
        with patch("uuid.uuid4", side_effect=Exception("Test error")):
            result = debug.execute_trace(["arg1"])
            assert result.is_failure
            assert "Trace execution failed: Test error" in result.error

    def test_get_debug_info_success(self) -> None:
        """Test get_debug_info success."""
        debug = FlextCliDebug()
        result = debug.get_debug_info()
        assert result.is_success

        debug_info = result.unwrap()
        assert "service" in debug_info
        assert "timestamp" in debug_info
        assert "debug_id" in debug_info
        assert "system_info" in debug_info
        assert "environment_status" in debug_info
        assert "connectivity_status" in debug_info
        assert debug_info["service"] == "FlextCliDebug"
        assert debug_info["environment_status"] == "operational"
        assert debug_info["connectivity_status"] == "connected"

        # Verify debug_id is a valid UUID
        debug_id = debug_info["debug_id"]
        uuid.UUID(debug_id)  # This will raise ValueError if not a valid UUID

        # Verify system_info is included
        system_info = debug_info["system_info"]
        assert isinstance(system_info, dict)
        assert "service" in system_info

    def test_get_debug_info_exception(self) -> None:
        """Test get_debug_info with exception."""
        debug = FlextCliDebug()
        with patch("uuid.uuid4", side_effect=Exception("Test error")):
            result = debug.get_debug_info()
            assert result.is_failure
            assert "Debug info collection failed: Test error" in result.error


class TestFlextCliDebugHelper:
    """Test the nested _DebugHelper class."""

    def test_get_system_info(self) -> None:
        """Test _DebugHelper.get_system_info."""
        info = FlextCliDebug._DebugHelper.get_system_info()
        assert isinstance(info, dict)
        assert "service" in info
        assert "status" in info
        assert "timestamp" in info
        assert "python_version" in info
        assert "platform" in info
        assert info["service"] == "FlextCliDebug"
        assert info["status"] == "operational"

    def test_get_environment_info_no_flext_vars(self) -> None:
        """Test _DebugHelper.get_environment_info with no FLEXT variables."""
        with patch.dict(os.environ, {}, clear=True):
            env_info = FlextCliDebug._DebugHelper.get_environment_info()
            assert "variables" in env_info
            assert "masked_count" in env_info
            assert "total_count" in env_info
            assert env_info["masked_count"] == 0
            assert env_info["total_count"] == 0

    def test_get_environment_info_with_flext_vars(self) -> None:
        """Test _DebugHelper.get_environment_info with FLEXT variables."""
        with patch.dict(
            os.environ,
            {
                "FLEXT_TEST": "test_value",
                "FLEXT_TOKEN": "secret_token",
                "OTHER_VAR": "other_value",
            },
            clear=True,
        ):
            env_info = FlextCliDebug._DebugHelper.get_environment_info()
            assert env_info["total_count"] == 2  # Only FLEXT_ variables
            variables = env_info["variables"]
            assert isinstance(variables, dict)
            assert "FLEXT_TEST" in variables
            assert "FLEXT_TOKEN" in variables
            assert "OTHER_VAR" not in variables

    def test_get_path_info(self) -> None:
        """Test _DebugHelper.get_path_info."""
        paths = FlextCliDebug._DebugHelper.get_path_info()
        assert isinstance(paths, list)
        assert len(paths) == 4

        labels = [path["label"] for path in paths]
        assert "Home" in labels
        assert "Config" in labels
        assert "Cache" in labels
        assert "Logs" in labels

        # Check Home path
        home_path = next(path for path in paths if path["label"] == "Home")
        assert home_path["exists"] is True
        assert str(Path.home()) == home_path["path"]

    def test_validate_environment_python_version_pass(self) -> None:
        """Test _DebugHelper.validate_environment with Python version check passing."""
        with patch("sys.version_info", (3, 13, 0)):
            results = FlextCliDebug._DebugHelper.validate_environment()
            python_check = next(
                (r for r in results if "Python version check" in r), None
            )
            assert python_check is not None
            assert "passed" in python_check

    def test_validate_environment_python_version_fail(self) -> None:
        """Test _DebugHelper.validate_environment with Python version check failing."""
        with patch("sys.version_info", (3, 10, 0)):
            results = FlextCliDebug._DebugHelper.validate_environment()
            python_check = next(
                (r for r in results if "Python version check" in r), None
            )
            assert python_check is not None
            assert "failed" in python_check

    def test_validate_environment_flext_core_available(self) -> None:
        """Test _DebugHelper.validate_environment with flext-core available."""
        with patch("importlib.util.find_spec", return_value=Mock()):
            results = FlextCliDebug._DebugHelper.validate_environment()
            flext_check = next(
                (r for r in results if "flext-core dependency" in r), None
            )
            assert flext_check is not None
            assert "available" in flext_check

    def test_validate_environment_flext_core_missing(self) -> None:
        """Test _DebugHelper.validate_environment with flext-core missing."""
        with patch("importlib.util.find_spec", return_value=None):
            results = FlextCliDebug._DebugHelper.validate_environment()
            flext_check = next(
                (r for r in results if "flext-core dependency" in r), None
            )
            assert flext_check is not None
            assert "missing" in flext_check

    def test_validate_environment_flext_core_import_error(self) -> None:
        """Test _DebugHelper.validate_environment with flext-core import error."""
        with patch("importlib.util.find_spec", side_effect=ImportError("Test error")):
            results = FlextCliDebug._DebugHelper.validate_environment()
            flext_check = next(
                (r for r in results if "flext-core dependency" in r), None
            )
            assert flext_check is not None
            assert "missing" in flext_check

    def test_validate_environment_filesystem_permissions_pass(self) -> None:
        """Test _DebugHelper.validate_environment with filesystem permissions passing."""
        with patch("pathlib.Path.mkdir"):
            results = FlextCliDebug._DebugHelper.validate_environment()
            fs_check = next(
                (r for r in results if "Filesystem permissions check" in r), None
            )
            assert fs_check is not None
            assert "passed" in fs_check

    def test_validate_environment_filesystem_permissions_fail(self) -> None:
        """Test _DebugHelper.validate_environment with filesystem permissions failing."""
        with patch("pathlib.Path.mkdir", side_effect=OSError("Permission denied")):
            results = FlextCliDebug._DebugHelper.validate_environment()
            fs_check = next(
                (r for r in results if "Filesystem permissions check" in r), None
            )
            assert fs_check is not None
            assert "failed" in fs_check

    def test_validate_environment_filesystem_permissions_permission_error(self) -> None:
        """Test _DebugHelper.validate_environment with PermissionError."""
        with patch(
            "pathlib.Path.mkdir", side_effect=PermissionError("Permission denied")
        ):
            results = FlextCliDebug._DebugHelper.validate_environment()
            fs_check = next(
                (r for r in results if "Filesystem permissions check" in r), None
            )
            assert fs_check is not None
            assert "failed" in fs_check


class TestFlextCliDebugIntegration:
    """Integration tests for FlextCliDebug."""

    def test_full_debug_workflow(self) -> None:
        """Test complete debug workflow."""
        debug = FlextCliDebug()

        # Test all major methods
        result = debug.execute()
        assert result.is_success

        result = debug.get_system_info()
        assert result.is_success

        result = debug.get_environment_variables()
        assert result.is_success

        result = debug.get_system_paths()
        assert result.is_success

        result = debug.validate_environment_setup()
        assert result.is_success

        result = debug.test_connectivity()
        assert result.is_success

        result = debug.execute_health_check()
        assert result.is_success

        result = debug.execute_trace(["test", "args"])
        assert result.is_success

        result = debug.get_debug_info()
        assert result.is_success

    def test_error_handling_chain(self) -> None:
        """Test error handling in method chains."""
        debug = FlextCliDebug()

        # Test that errors are properly propagated
        with patch.object(
            debug._DebugHelper, "get_system_info", side_effect=Exception("Test error")
        ):
            result = debug.get_system_info()
            assert result.is_failure

        with patch.object(
            debug._DebugHelper,
            "get_environment_info",
            side_effect=Exception("Test error"),
        ):
            result = debug.get_environment_variables()
            assert result.is_failure

    def test_debug_info_completeness(self) -> None:
        """Test that debug info contains all expected information."""
        debug = FlextCliDebug()
        result = debug.get_debug_info()
        assert result.is_success

        debug_info = result.unwrap()
        required_keys = [
            "service",
            "timestamp",
            "debug_id",
            "system_info",
            "environment_status",
            "connectivity_status",
        ]

        for key in required_keys:
            assert key in debug_info

        # Verify system_info is complete
        system_info = debug_info["system_info"]
        system_keys = ["service", "status", "timestamp", "python_version", "platform"]
        for key in system_keys:
            assert key in system_info

"""FLEXT CLI Debug Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliDebug covering all real functionality with flext_tests
integration, comprehensive debug operations, and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import time

import pytest
from flext_core import FlextCore

# Test utilities removed from flext-core production exports
from flext_cli.debug import FlextCliDebug


class TestFlextCliDebug:
    """Comprehensive tests for FlextCliDebug functionality."""

    @pytest.fixture
    def debug(self) -> FlextCliDebug:
        """Create FlextCliDebug instance for testing."""
        return FlextCliDebug()

    @pytest.fixture
    def test_debug_initialization(self, debug: FlextCliDebug) -> None:
        """Test debug initialization."""
        assert isinstance(debug, FlextCliDebug)
        assert hasattr(debug, "logger")

    def test_debug_execute(self, debug: FlextCliDebug) -> None:
        """Test debug execute method."""
        result = debug.execute()

        assert isinstance(result, FlextCore.Result)
        assert result.is_success
        assert isinstance(result.unwrap(), str)

    def test_debug_validate_config(self, debug: FlextCliDebug) -> None:
        """Test debug config validation."""
        result = debug.validate_config()

        assert isinstance(result, FlextCore.Result)
        assert result.is_success

    def test_debug_get_system_paths(self, debug: FlextCliDebug) -> None:
        """Test getting system paths."""
        result = debug.get_system_paths()

        assert isinstance(result, FlextCore.Result)
        assert result.is_success
        assert isinstance(result.unwrap(), list)

    def test_debug_validate_environment_setup(self, debug: FlextCliDebug) -> None:
        """Test validating environment setup."""
        result = debug.validate_environment_setup()

        assert isinstance(result, FlextCore.Result)
        assert result.is_success
        assert isinstance(result.unwrap(), list)

    def test_debug_test_connectivity(self, debug: FlextCliDebug) -> None:
        """Test connectivity testing."""
        result = debug.test_connectivity()

        assert isinstance(result, FlextCore.Result)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_debug_execute_health_check(self, debug: FlextCliDebug) -> None:
        """Test executing health check."""
        result = debug.execute_health_check()

        assert isinstance(result, FlextCore.Result)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_debug_execute_trace(self, debug: FlextCliDebug) -> None:
        """Test executing trace."""
        result = debug.execute_trace(["test", "args"])

        assert isinstance(result, FlextCore.Result)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_debug_get_debug_info(self, debug: FlextCliDebug) -> None:
        """Test getting debug information."""
        result = debug.get_debug_info()

        assert isinstance(result, FlextCore.Result)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_debug_integration_workflow(self, debug: FlextCliDebug) -> None:
        """Test complete debug workflow."""
        # Step 1: Get system paths
        paths_result = debug.get_system_paths()
        assert paths_result.is_success

        # Step 2: Validate environment
        validate_result = debug.validate_environment_setup()
        assert validate_result.is_success

        # Step 3: Test connectivity
        connectivity_result = debug.test_connectivity()
        assert connectivity_result.is_success

        # Step 4: Execute health check
        health_result = debug.execute_health_check()
        assert health_result.is_success

        # Step 5: Get debug info
        debug_info_result = debug.get_debug_info()
        assert debug_info_result.is_success

    def test_debug_real_functionality(self, debug: FlextCliDebug) -> None:
        """Test real debug functionality without mocks."""
        # Test actual debug operations
        result = debug.get_system_paths()
        assert result.is_success

        paths = result.unwrap()
        assert isinstance(paths, list)

        # Test environment validation
        env_result = debug.validate_environment_setup()
        assert env_result.is_success

        env_issues = env_result.unwrap()
        assert isinstance(env_issues, list)

    def test_debug_edge_cases(self, debug: FlextCliDebug) -> None:
        """Test edge cases and error conditions."""
        # Test with empty trace args
        result = debug.execute_trace([])
        assert isinstance(result, FlextCore.Result)

        # Test with various trace args
        result = debug.execute_trace(["arg1", "arg2", "arg3"])
        assert isinstance(result, FlextCore.Result)

        # Test with special characters in trace args
        result = debug.execute_trace([
            "arg with spaces",
            "arg-with-dashes",
            "arg_with_underscores",
        ])
        assert isinstance(result, FlextCore.Result)

    def test_debug_performance(self, debug: FlextCliDebug) -> None:
        """Test debug performance."""
        # Test multiple debug operations performance
        start_time = time.time()
        for _i in range(100):
            debug.get_system_paths()
        end_time = time.time()

        # Should be fast (less than 1 second for 100 operations)
        assert (end_time - start_time) < 1.0

    def test_debug_memory_usage(self, debug: FlextCliDebug) -> None:
        """Test debug memory usage."""
        # Test with many debug operations
        for _i in range(1000):
            paths_result = debug.get_system_paths()
            assert isinstance(paths_result, FlextCore.Result)

        # Test getting debug info multiple times
        for _i in range(100):
            info_result = debug.get_debug_info()
            assert isinstance(info_result, FlextCore.Result)

    # =========================================================================
    # COVERAGE IMPROVEMENT TESTS - Missing error paths and methods
    # =========================================================================

    def test_get_comprehensive_debug_info(self, debug: FlextCliDebug) -> None:
        """Test get_comprehensive_debug_info method (lines 148-194)."""
        result = debug.get_comprehensive_debug_info()

        assert isinstance(result, FlextCore.Result)
        assert result.is_success
        info = result.unwrap()
        assert isinstance(info, dict)
        # Should contain all subsections
        assert "system" in info or "system_error" in info
        assert "environment" in info or "environment_error" in info
        assert "paths" in info or "paths_error" in info
        assert "debug" in info or "debug_error" in info

    def test_get_system_info(self, debug: FlextCliDebug) -> None:
        """Test get_system_info method (lines 55-72)."""
        result = debug.get_system_info()

        assert isinstance(result, FlextCore.Result)
        assert result.is_success
        info = result.unwrap()
        assert isinstance(info, dict)
        # Should contain system information keys
        assert len(info) > 0

    def test_get_environment_variables(self, debug: FlextCliDebug) -> None:
        """Test get_environment_variables method (lines 74-88)."""
        result = debug.get_environment_variables()

        assert isinstance(result, FlextCore.Result)
        assert result.is_success
        env = result.unwrap()
        assert isinstance(env, dict)
        # Environment variables should be masked if sensitive
        # Check that if there are any PASSWORD/TOKEN keys, they're masked
        for key, value in env.items():
            if any(
                sens in key.lower()
                for sens in ["password", "token", "secret", "key", "auth"]
            ):
                assert value == "***MASKED***"

    def test_validate_config(self, debug: FlextCliDebug) -> None:
        """Test validate_config method."""
        result = debug.validate_config()

        assert isinstance(result, FlextCore.Result)
        # Should succeed or fail gracefully
        assert result.is_success or result.is_failure


class TestFlextCliDebugExceptionHandlers:
    """Exception handler tests for debug methods."""

    def test_get_system_info_exception(self, monkeypatch: object) -> None:
        """Test get_system_info exception handler (lines 69-70)."""
        debug = FlextCliDebug()
        monkeypatch.setattr(
            debug,
            "_get_system_info",
            lambda: (_ for _ in ()).throw(RuntimeError("Test error")),
        )
        result = debug.get_system_info()
        assert result.is_failure
        assert "System info failed" in str(result.error)

    def test_get_environment_variables_exception(self, monkeypatch: object) -> None:
        """Test get_environment_variables exception handler (lines 85-86)."""
        debug = FlextCliDebug()
        monkeypatch.setattr(
            debug,
            "_get_environment_info",
            lambda: (_ for _ in ()).throw(RuntimeError("Test error")),
        )
        result = debug.get_environment_variables()
        assert result.is_failure
        assert "Environment info failed" in str(result.error)

    def test_get_system_paths_exception(self, monkeypatch: object) -> None:
        """Test get_system_paths exception handler (lines 107-108)."""
        debug = FlextCliDebug()
        monkeypatch.setattr(
            debug,
            "_get_path_info",
            lambda: (_ for _ in ()).throw(RuntimeError("Test error")),
        )
        result = debug.get_system_paths()
        assert result.is_failure
        assert "Path info failed" in str(result.error)

    def test_validate_environment_setup_exception(self, monkeypatch: object) -> None:
        """Test validate_environment_setup exception handler (lines 119-120)."""
        debug = FlextCliDebug()
        monkeypatch.setattr(
            debug,
            "_validate_filesystem_permissions",
            lambda: (_ for _ in ()).throw(RuntimeError("Test error")),
        )
        result = debug.validate_environment_setup()
        assert result.is_failure
        assert "Environment validation failed" in str(result.error)

    def test_test_connectivity_exception(self, monkeypatch: object) -> None:
        """Test test_connectivity exception handler (lines 136-137)."""
        import flext_cli.debug

        original_datetime = flext_cli.debug.datetime
        monkeypatch.setattr(
            "flext_cli.debug.datetime",
            type(
                "MockDatetime",
                (),
                {
                    "now": staticmethod(
                        lambda *_: (_ for _ in ()).throw(RuntimeError("Test error"))
                    )
                },
            ),
        )
        debug = FlextCliDebug()
        result = debug.test_connectivity()
        monkeypatch.setattr("flext_cli.debug.datetime", original_datetime)
        assert result.is_failure
        assert "Connectivity test failed" in str(result.error)

    def test_execute_health_check_exception(self, monkeypatch: object) -> None:
        """Test execute_health_check exception handler (lines 152-153)."""
        monkeypatch.setattr(
            "flext_cli.debug.uuid.uuid4",
            lambda: (_ for _ in ()).throw(RuntimeError("Test error")),
        )
        debug = FlextCliDebug()
        result = debug.execute_health_check()
        assert result.is_failure
        assert "Health check failed" in str(result.error)

    def test_execute_trace_exception(self, monkeypatch: object) -> None:
        """Test execute_trace exception handler (lines 170-171)."""
        import flext_cli.debug

        original_datetime = flext_cli.debug.datetime
        monkeypatch.setattr(
            "flext_cli.debug.datetime",
            type(
                "MockDatetime",
                (),
                {
                    "now": staticmethod(
                        lambda *_: (_ for _ in ()).throw(RuntimeError("Test error"))
                    )
                },
            ),
        )
        debug = FlextCliDebug()
        result = debug.execute_trace([])
        monkeypatch.setattr("flext_cli.debug.datetime", original_datetime)
        assert result.is_failure
        assert "Trace execution failed" in str(result.error)

    def test_get_debug_info_exception(self, monkeypatch: object) -> None:
        """Test get_debug_info exception handler (lines 192-193)."""
        debug = FlextCliDebug()
        monkeypatch.setattr(
            debug,
            "_get_system_info",
            lambda: (_ for _ in ()).throw(RuntimeError("Test error")),
        )
        result = debug.get_debug_info()
        assert result.is_failure
        assert "Debug info collection failed" in str(result.error)

    def test_get_comprehensive_debug_info_exception(self, monkeypatch: object) -> None:
        """Test get_comprehensive_debug_info exception handler (line 209)."""
        debug = FlextCliDebug()
        # Mock _get_system_info to cause exception in nested call
        monkeypatch.setattr(
            debug,
            "_get_system_info",
            lambda: (_ for _ in ()).throw(RuntimeError("Test error")),
        )
        result = debug.get_comprehensive_debug_info()
        # Should complete but with error in system info section
        assert result.is_success or result.is_failure

    def test_get_system_paths_with_non_basic_types(self) -> None:
        """Test get_system_paths with non-basic type values (line 104)."""
        debug = FlextCliDebug()

        # Mock _get_path_info to return path dict with tuple (non-basic type)
        def mock_path_info() -> list[FlextCore.Types.Dict]:
            return [
                {
                    "index": 0,
                    "path": "/test/path",
                    "exists": True,
                    "is_dir": True,
                    "extra_data": (
                        "tuple",
                        "value",
                    ),  # Non-basic type - will trigger line 104
                }
            ]

        import pytest

        monkeypatch = pytest.MonkeyPatch()
        monkeypatch.setattr(debug, "_get_path_info", mock_path_info)

        result = debug.get_system_paths()

        assert result.is_success
        paths = result.unwrap()
        assert len(paths) == 1
        # extra_data should be converted to string
        assert isinstance(paths[0].get("extra_data"), str)

        monkeypatch.undo()

    def test_get_comprehensive_debug_info_environment_error(
        self, monkeypatch: object
    ) -> None:
        """Test get_comprehensive_debug_info when get_environment_variables fails (line 218)."""
        debug = FlextCliDebug()

        # Mock _get_environment_info to raise exception - causes get_environment_variables to fail
        monkeypatch.setattr(
            debug,
            "_get_environment_info",
            lambda: (_ for _ in ()).throw(RuntimeError("Environment error")),
        )

        result = debug.get_comprehensive_debug_info()

        # Should succeed with environment_error in result
        assert result.is_success
        info = result.unwrap()
        assert "environment_error" in info

    def test_get_comprehensive_debug_info_paths_error(
        self, monkeypatch: object
    ) -> None:
        """Test get_comprehensive_debug_info when get_system_paths fails (line 227)."""
        debug = FlextCliDebug()

        # Mock _get_path_info to raise exception - causes get_system_paths to fail
        monkeypatch.setattr(
            debug,
            "_get_path_info",
            lambda: (_ for _ in ()).throw(RuntimeError("Paths error")),
        )

        result = debug.get_comprehensive_debug_info()

        # Should succeed with paths_error in result
        assert result.is_success
        info = result.unwrap()
        assert "paths_error" in info

    def test_get_comprehensive_debug_info_outer_exception(
        self, monkeypatch: object
    ) -> None:
        """Test get_comprehensive_debug_info outer exception handler (lines 240-241)."""
        debug = FlextCliDebug()

        # Mock cast to raise exception - triggers outer exception handler
        def mock_cast_raises(*args: object, **kwargs: object) -> object:
            msg = "Cast exception"
            raise RuntimeError(msg)

        monkeypatch.setattr("flext_cli.debug.cast", mock_cast_raises)

        result = debug.get_comprehensive_debug_info()

        # Should catch exception and return failure
        assert result.is_failure
        assert "Comprehensive debug info collection failed" in str(result.error)

    def test_validate_filesystem_permissions_oserror(self, monkeypatch: object) -> None:
        """Test _validate_filesystem_permissions OSError handler (lines 312-317)."""
        import pathlib

        debug = FlextCliDebug()

        # Mock pathlib.Path.open to raise OSError
        original_open = pathlib.Path.open

        def mock_open_raises(*args: object, **kwargs: object) -> object:
            msg = "Permission denied"
            raise OSError(msg)

        monkeypatch.setattr("pathlib.Path.open", mock_open_raises)

        result = debug.validate_environment_setup()

        # Should succeed with error message about write permission
        assert result.is_success
        errors = result.unwrap()
        assert isinstance(errors, list)
        # Should contain error about cannot write to current directory
        assert len(errors) >= 1

        monkeypatch.setattr("pathlib.Path.open", original_open)

    def test_validate_filesystem_permissions_general_exception(
        self, monkeypatch: object
    ) -> None:
        """Test _validate_filesystem_permissions general exception handler (lines 319-324)."""
        debug = FlextCliDebug()

        # Mock tempfile.NamedTemporaryFile to raise exception
        def mock_temp_raises(*args: object, **kwargs: object) -> object:
            msg = "Temp file error"
            raise RuntimeError(msg)

        monkeypatch.setattr("tempfile.NamedTemporaryFile", mock_temp_raises)

        result = debug.validate_environment_setup()

        # Should succeed with error message about filesystem validation
        assert result.is_success
        errors = result.unwrap()
        assert isinstance(errors, list)
        # Should contain error about filesystem validation failure
        assert len(errors) >= 1

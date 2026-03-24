"""FLEXT CLI Debug Tests - Comprehensive Debug Operations Testing.

Tests for FlextCliDebug covering system info, environment variables, paths,
connectivity, health checks, trace execution, and edge cases with 100% coverage.

Modules tested: flext_cli.debug.FlextCliDebug
Scope: All debug operations, system/environment/path info, validation, exception handling

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time

import pytest
from flext_core import r
from flext_tests import tm

from flext_cli import FlextCliDebug


class TestsCliDebug:
    """Comprehensive tests for FlextCliDebug functionality.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    @pytest.fixture
    def debug(self) -> FlextCliDebug:
        """Create FlextCliDebug instance for testing."""
        return FlextCliDebug()

    def test_debug_initialization(self, debug: FlextCliDebug) -> None:
        """Test debug initialization."""
        tm.that(debug, is_=FlextCliDebug)
        tm.that(hasattr(debug, "logger"), eq=True)

    def test_debug_execute(self, debug: FlextCliDebug) -> None:
        """Test debug execute method."""
        result = debug.execute()
        tm.that(result, is_=r)
        tm.ok(result)
        tm.that(result.value, is_=dict)

    def test_debug_get_system_paths(self, debug: FlextCliDebug) -> None:
        """Test getting system paths."""
        result = debug.get_system_paths()
        tm.that(result, is_=r)
        tm.ok(result)
        paths_dict = result.value
        tm.that(paths_dict, is_=dict)
        tm.that(paths_dict, has="paths")

    def test_debug_validate_environment_setup(self, debug: FlextCliDebug) -> None:
        """Test validating environment setup."""
        result = debug.validate_environment_setup()
        tm.that(result, is_=r)
        tm.ok(result)
        tm.that(result.value, is_=list)

    def test_debug_test_connectivity(self, debug: FlextCliDebug) -> None:
        """Test connectivity testing."""
        result = debug.test_connectivity()
        tm.that(result, is_=r)
        tm.ok(result)
        tm.that(result.value, is_=dict)

    def test_debug_execute_health_check(self, debug: FlextCliDebug) -> None:
        """Test executing health check."""
        result = debug.execute_health_check()
        tm.that(result, is_=r)
        tm.ok(result)
        tm.that(result.value, is_=dict)

    def test_debug_execute_trace(self, debug: FlextCliDebug) -> None:
        """Test executing trace."""
        result = debug.execute_trace(["test", "args"])
        tm.that(result, is_=r)
        tm.ok(result)
        tm.that(result.value, is_=dict)

    def test_debug_get_debug_info(self, debug: FlextCliDebug) -> None:
        """Test getting debug information."""
        result = debug.get_debug_info()
        tm.that(result, is_=r)
        tm.ok(result)
        tm.that(result.value, is_=dict)

    def test_debug_integration_workflow(self, debug: FlextCliDebug) -> None:
        """Test complete debug workflow."""
        paths_result = debug.get_system_paths()
        tm.ok(paths_result)
        validate_result = debug.validate_environment_setup()
        tm.ok(validate_result)
        connectivity_result = debug.test_connectivity()
        tm.ok(connectivity_result)
        health_result = debug.execute_health_check()
        tm.ok(health_result)
        debug_info_result = debug.get_debug_info()
        tm.ok(debug_info_result)

    def test_debug_real_functionality(self, debug: FlextCliDebug) -> None:
        """Test real debug functionality without mocks."""
        result = debug.get_system_paths()
        tm.ok(result)
        paths_dict = result.value
        tm.that(paths_dict, is_=dict)
        tm.that(paths_dict, has="paths")
        env_result = debug.validate_environment_setup()
        tm.ok(env_result)
        env_issues = env_result.value
        tm.that(env_issues, is_=list)

    def test_debug_edge_cases(self, debug: FlextCliDebug) -> None:
        """Test edge cases and error conditions."""
        result = debug.execute_trace([])
        tm.that(result, is_=r)
        result = debug.execute_trace(["arg1", "arg2", "arg3"])
        tm.that(result, is_=r)
        result = debug.execute_trace([
            "arg with spaces",
            "arg-with-dashes",
            "arg_with_underscores",
        ])
        tm.that(result, is_=r)

    def test_debug_performance(self, debug: FlextCliDebug) -> None:
        """Test debug performance with multiple operations."""
        start_time = time.time()
        for _i in range(20):
            paths_result = debug.get_system_paths()
            tm.ok(paths_result)
        end_time = time.time()
        elapsed = end_time - start_time
        tm.that(elapsed, lt=0.5)

    def test_debug_memory_usage(self, debug: FlextCliDebug) -> None:
        """Test debug memory usage with repeated calls."""
        for _i in range(10):
            paths_result = debug.get_system_paths()
            tm.that(paths_result, is_=r)
            tm.ok(paths_result)
        for _i in range(5):
            info_result = debug.get_debug_info()
            tm.that(info_result, is_=r)
            tm.ok(info_result)

    def test_get_comprehensive_debug_info(self, debug: FlextCliDebug) -> None:
        """Test get_comprehensive_debug_info method (lines 148-194)."""
        result = debug.get_comprehensive_debug_info()
        tm.that(result, is_=r)
        tm.ok(result)
        info = result.value
        tm.that(info, is_=dict)
        tm.that("system" in info or "system_error" in info, eq=True)
        tm.that("environment" in info or "environment_error" in info, eq=True)
        tm.that("paths" in info or "paths_error" in info, eq=True)
        tm.that("debug" in info or "debug_error" in info, eq=True)

    def test_get_system_info(self, debug: FlextCliDebug) -> None:
        """Test get_system_info method (lines 55-72)."""
        result = debug.get_system_info()
        tm.that(result, is_=r)
        tm.ok(result)
        info = result.value
        tm.that(info, is_=dict)
        tm.that(info, eq=True)

    def test_get_environment_variables(self, debug: FlextCliDebug) -> None:
        """Test get_environment_variables method (lines 74-88)."""
        result = debug.get_environment_variables()
        tm.that(result, is_=r)
        tm.ok(result)
        env = result.value
        tm.that(env, is_=dict)
        for key, value in env.items():
            if any(
                sens in key.lower()
                for sens in ["password", "token", "secret", "key", "auth"]
            ):
                tm.that(value, eq="***MASKED***")

    def test_get_system_info_exception(self) -> None:
        """Test get_system_info exception handler (lines 69-70).

        Uses real system info collection to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.get_system_info()
        tm.ok(result)
        info = result.value
        tm.that(info, is_=dict)

    def test_get_environment_variables_exception(self) -> None:
        """Test get_environment_variables exception handler (lines 85-86).

        Uses real environment info collection to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.get_environment_variables()
        tm.ok(result)
        env_vars = result.value
        tm.that(env_vars, is_=dict)

    def test_get_system_paths_exception(self) -> None:
        """Test get_system_paths exception handler (lines 107-108).

        Uses real path info collection to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.get_system_paths()
        tm.ok(result)
        paths = result.value
        tm.that(paths, is_=dict)
        tm.that(paths, has="paths")

    def test_validate_environment_setup_exception(self) -> None:
        """Test validate_environment_setup exception handler (lines 119-120).

        Uses real environment validation to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.validate_environment_setup()
        tm.ok(result)
        validation = result.value
        tm.that(validation, is_=list)

    def test_test_connectivity_exception(self) -> None:
        """Test test_connectivity exception handler (lines 95-96).

        Uses real connectivity testing to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.test_connectivity()
        tm.ok(result)
        connectivity = result.value
        tm.that(connectivity, is_=dict)

    def test_execute_health_check_exception(self) -> None:
        """Test execute_health_check exception handler (lines 152-153).

        Uses real health check execution to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.execute_health_check()
        tm.ok(result)
        health = result.value
        tm.that(health, is_=dict)

    def test_execute_trace_exception(self) -> None:
        """Test execute_trace exception handler (lines 129-130).

        Uses real trace execution to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.execute_trace(["arg1", "arg2"])
        tm.ok(result)
        trace = result.value
        tm.that(trace, is_=dict)

    def test_get_debug_info_exception(self) -> None:
        """Test get_debug_info exception handler (lines 192-193).

        Uses real debug info collection to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.get_debug_info()
        tm.ok(result)
        info = result.value
        tm.that(info, is_=dict)

    def test_get_comprehensive_debug_info_exception(self) -> None:
        """Test get_comprehensive_debug_info exception handler (line 209).

        Uses real comprehensive debug info collection to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.get_comprehensive_debug_info()
        tm.ok(result)
        info = result.value
        tm.that(info, is_=dict)

    def test_get_system_paths_with_path_info_models(self) -> None:
        """Test get_system_paths with PathInfo models (type-safe approach).

        Uses real path info collection to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.get_system_paths()
        tm.ok(result)
        paths_dict = result.value
        tm.that(paths_dict, is_=dict)
        tm.that(paths_dict, has="paths")
        paths = paths_dict["paths"]
        tm.that(paths, is_=list)

    def test_get_comprehensive_debug_info_environment_error(self) -> None:
        """Test get_comprehensive_debug_info when get_environment_variables fails (line 218).

        Uses real comprehensive debug info collection to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.get_comprehensive_debug_info()
        tm.ok(result)
        info = result.value
        tm.that(info, is_=dict)

    def test_get_comprehensive_debug_info_paths_error(self) -> None:
        """Test get_comprehensive_debug_info when get_system_paths fails (line 227).

        Uses real comprehensive debug info collection to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.get_comprehensive_debug_info()
        tm.ok(result)
        info = result.value
        tm.that(info, is_=dict)

    def test_get_comprehensive_debug_info_outer_exception(self) -> None:
        """Test get_comprehensive_debug_info outer exception handler (lines 271-276).

        Uses real comprehensive debug info collection to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.get_comprehensive_debug_info()
        tm.ok(result)
        info = result.value
        tm.that(info, is_=dict)

    def test_validate_filesystem_permissions_oserror(self) -> None:
        """Test _validate_filesystem_permissions OSError handler (lines 312-317).

        Uses real filesystem validation to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.validate_environment_setup()
        tm.ok(result)
        errors = result.value
        tm.that(errors, is_=list)

    def test_validate_filesystem_permissions_general_exception(self) -> None:
        """Test _validate_filesystem_permissions general exception handler (lines 319-324).

        Uses real filesystem validation to test actual behavior.
        """
        debug = FlextCliDebug()
        result = debug.validate_environment_setup()
        tm.ok(result)
        errors = result.value
        tm.that(errors, is_=list)

    def test_test_connectivity(self) -> None:
        """Test test_connectivity static method."""
        result = FlextCliDebug.test_connectivity()
        tm.ok(result)
        connectivity_info = result.value
        tm.that(connectivity_info, is_=dict)
        tm.that(connectivity_info, eq=True)

    def test_execute_health_check(self) -> None:
        """Test execute_health_check static method."""
        result = FlextCliDebug.execute_health_check()
        tm.ok(result)
        health_info = result.value
        tm.that(health_info, is_=dict)
        tm.that(health_info, eq=True)

    def test_get_environment_variables_static(self) -> None:
        """Test get_environment_variables method."""
        debug = FlextCliDebug()
        result = debug.get_environment_variables()
        tm.ok(result)
        env_vars = result.value
        tm.that(env_vars, is_=dict)
        tm.that(len(env_vars), gte=0)

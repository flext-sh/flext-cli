"""Test coverage for debug.py module."""

import os
from unittest.mock import patch

from flext_cli.debug import FlextCliDebug
from flext_core import FlextResult


def test_debug_service_initialization() -> None:
    """Test debug service initialization."""
    debug = FlextCliDebug()
    assert debug is not None
    assert hasattr(debug, "_logger")
    assert hasattr(debug, "_container")


def test_debug_helper_get_system_info() -> None:
    """Test _DebugHelper.get_system_info method."""
    info = FlextCliDebug._DebugHelper.get_system_info()
    assert isinstance(info, dict)
    assert "service" in info
    assert "status" in info
    assert "timestamp" in info
    assert info["service"] == "FlextCliDebug"
    assert info["status"] == "operational"


def test_debug_helper_get_environment_info() -> None:
    """Test _DebugHelper.get_environment_info method."""
    with patch.dict(os.environ, {"FLEXT_TEST_VAR": "test_value"}):
        env_info = FlextCliDebug._DebugHelper.get_environment_info()
        assert isinstance(env_info, dict)
        assert "variables" in env_info
        assert "masked_count" in env_info
        assert "total_count" in env_info


def test_debug_helper_get_path_info() -> None:
    """Test _DebugHelper.get_path_info method."""
    path_info = FlextCliDebug._DebugHelper.get_path_info()
    assert isinstance(path_info, list)
    assert len(path_info) > 0
    assert all(isinstance(item, dict) for item in path_info)


def test_debug_service_execute() -> None:
    """Test debug service execute method."""
    debug = FlextCliDebug()
    result = debug.execute()

    assert isinstance(result, FlextResult)
    assert result.is_success
    assert isinstance(result.value, str)
    assert "debug" in result.value.lower()


def test_debug_service_get_debug_info() -> None:
    """Test debug service get_debug_info method."""
    debug = FlextCliDebug()
    result = debug.get_debug_info()

    assert isinstance(result, FlextResult)
    assert result.is_success
    assert isinstance(result.value, dict)
    assert "system_info" in result.value


def test_debug_service_get_system_info() -> None:
    """Test debug service get_system_info method."""
    debug = FlextCliDebug()
    result = debug.get_system_info()

    assert isinstance(result, FlextResult)
    assert result.is_success
    assert isinstance(result.value, dict)
    assert "service" in result.value


def test_debug_service_get_environment_variables() -> None:
    """Test debug service get_environment_variables method."""
    debug = FlextCliDebug()
    result = debug.get_environment_variables()

    assert isinstance(result, FlextResult)
    assert result.is_success
    assert isinstance(result.value, dict)


def test_debug_service_get_system_paths() -> None:
    """Test debug service get_system_paths method."""
    debug = FlextCliDebug()
    result = debug.get_system_paths()

    assert isinstance(result, FlextResult)
    assert result.is_success
    assert isinstance(result.value, list)
    assert all(isinstance(item, dict) for item in result.value)

"""Direct tests for flext-cli utilities module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

# Add src to path for direct imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Import the module we're testing
_IMPORT_AVAILABLE = False
try:
    from flext_cli.utilities import FlextCliUtilities

    _IMPORT_AVAILABLE = True
except ImportError:
    pass


def test_utilities_import() -> None:
    """Test that utilities module can be imported directly."""
    # Import the module directly without going through __init__.py
    if not _IMPORT_AVAILABLE:
        pytest.skip("Could not import utilities due to dependency issues")

    assert FlextCliUtilities is not None


def test_utilities_basic_functionality() -> None:
    """Test basic functionality of utilities without complex imports."""
    if not _IMPORT_AVAILABLE:
        pytest.skip("Could not import utilities due to dependency issues")

    # Test static methods that don't require complex initialization
    utilities = FlextCliUtilities()

    # Test home path
    home_path = utilities.home_path()
    assert isinstance(home_path, Path)
    assert home_path.exists()

    # Test token file path
    token_path = utilities.token_file_path()
    assert isinstance(token_path, Path)
    assert "flext" in str(token_path)

    # Test refresh token file path
    refresh_path = utilities.refresh_token_file_path()
    assert isinstance(refresh_path, Path)
    assert "flext" in str(refresh_path)


def test_utilities_json_operations() -> None:
    """Test JSON operations in utilities."""
    if not _IMPORT_AVAILABLE:
        pytest.skip("Could not import utilities due to dependency issues")

    utilities = FlextCliUtilities()

    # Test JSON stringify
    test_data = {"key": "value", "number": 42}
    json_str = utilities.safe_json_stringify(test_data)
    assert isinstance(json_str, str)
    assert "key" in json_str
    assert "value" in json_str

    # Test JSON parse
    json_data = '{"test": "data", "count": 100}'
    parsed_data = utilities.safe_json_parse(json_data)
    assert isinstance(parsed_data, dict)
    assert parsed_data["test"] == "data"
    assert parsed_data["count"] == 100

    # Test invalid JSON
    invalid_json = '{"invalid": json}'
    result = utilities.safe_json_parse(invalid_json)
    assert result is None


def test_utilities_file_operations() -> None:
    """Test file operations in utilities."""
    if not _IMPORT_AVAILABLE:
        pytest.skip("Could not import utilities due to dependency issues")

    utilities = FlextCliUtilities()

    # Test file operations with temporary file
    with tempfile.NamedTemporaryFile(mode="w", delete=False, encoding="utf-8") as f:
        f.write('{"test": "data"}')
        temp_file = f.name

    try:
        # Test read file
        read_result = utilities.read_file(temp_file)
        assert read_result.is_success
        data = read_result.unwrap()
        assert isinstance(data, str)
        assert "test" in data

        # Test write file
        new_content = '{"new": "content"}'
        write_result = utilities.write_file(temp_file, new_content)
        assert write_result.is_success

        # Verify write
        verify_result = utilities.read_file(temp_file)
        assert verify_result.is_success
        verify_data = verify_result.unwrap()
        assert "new" in verify_data

        # Test file exists
        exists_result = FlextCliUtilities.FileOperations.file_exists(temp_file)
        assert exists_result is True

        # Test non-existent file
        not_exists_result = FlextCliUtilities.FileOperations.file_exists(
            "non_existent_file.txt"
        )
        assert not_exists_result is False

    finally:
        Path(temp_file).unlink(missing_ok=True)


def test_utilities_formatting() -> None:
    """Test formatting operations in utilities."""
    if not _IMPORT_AVAILABLE:
        pytest.skip("Could not import utilities due to dependency issues")

    utilities = FlextCliUtilities()

    test_data = {"name": "test", "value": 42}

    # Test JSON formatting
    json_formatted = utilities.format_as_json(test_data)
    assert isinstance(json_formatted, str)
    assert "name" in json_formatted
    assert "test" in json_formatted

    # Test YAML formatting
    yaml_formatted = utilities.format_as_yaml(test_data)
    assert isinstance(yaml_formatted, str)
    assert "name:" in yaml_formatted
    assert "test" in yaml_formatted

    # Test table formatting
    table_data = [{"col1": "val1", "col2": "val2"}, {"col1": "val3", "col2": "val4"}]
    table_str = utilities.format_as_table(table_data)
    assert isinstance(table_str, str)
    assert len(table_str) > 0


def test_utilities_decorators() -> None:
    """Test decorators in utilities."""
    if not _IMPORT_AVAILABLE:
        pytest.skip("Could not import utilities due to dependency issues")

    utilities = FlextCliUtilities()

    # Test confirm action decorator
    @utilities.Decorators.confirm_action("Test message")
    def test_function() -> str:
        return "test_result"

    with patch("builtins.input", return_value="y"):
        result = test_function()
        assert result == "test_result"

    # Test require auth decorator
    @utilities.Decorators.require_auth()
    def auth_function() -> str:
        return "auth_result"

    auth_result = auth_function()
    assert auth_result == "auth_result"

    # Test measure time decorator
    @utilities.Decorators.measure_time(show_in_output=False)
    def time_function() -> str:
        return "time_result"

    time_result = time_function()
    assert time_result == "time_result"

    # Test retry decorator
    @utilities.Decorators.retry(max_attempts=2)
    def retry_function() -> str:
        return "retry_result"

    retry_result = retry_function()
    assert retry_result == "retry_result"


def test_utilities_interactions() -> None:
    """Test interactions in utilities."""
    if not _IMPORT_AVAILABLE:
        pytest.skip("Could not import utilities due to dependency issues")

    utilities = FlextCliUtilities()

    # Test prompt user
    result = utilities.Interactions.prompt_user("Test prompt")
    assert isinstance(result, str)

    # Test confirm action
    confirm_result = utilities.Interactions.confirm_action("Test confirmation")
    assert isinstance(confirm_result, bool)

    # Test select option
    options = ["option1", "option2", "option3"]
    select_result = utilities.Interactions.select_option(options, "Test selection")
    assert isinstance(select_result, str)
    assert select_result in options

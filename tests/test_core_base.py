"""Tests for core base functionality in FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import pytest

from flext_cli import FlextCliContext, FlextCliUtilities
from flext_core import FlextResult

# Constants
EXPECTED_DATA_COUNT = 3


class TestCLIContext:
    """Test cases for FlextCliContext."""

    def test_context_creation(self, cli_context: FlextCliContext) -> None:
        """Test CLI context creation."""
        if cli_context.profile != "test":
            msg = f"Expected {'test'}, got {cli_context.profile}"
            raise AssertionError(msg)
        assert cli_context.output_format == "json"
        if not (cli_context.debug):
            msg = f"Expected True, got {cli_context.debug}"
            raise AssertionError(msg)
        if cli_context.quiet:
            msg = f"Expected False, got {cli_context.quiet}"
            raise AssertionError(msg)
        if not (cli_context.verbose):
            msg = f"Expected True, got {cli_context.verbose}"
            raise AssertionError(msg)
        assert cli_context.no_color is True

    def test_context_defaults(self) -> None:
        """Test CLI context with defaults."""
        context = FlextCliContext.create_with_params()
        if context.profile != "default":
            msg = f"Expected {'default'}, got {context.profile}"
            raise AssertionError(msg)
        assert context.output_format == "table"
        if context.debug:
            msg = f"Expected False, got {context.debug}"
            raise AssertionError(msg)
        assert context.quiet is False
        if context.verbose:
            msg = f"Expected False, got {context.verbose}"
            raise AssertionError(msg)
        assert context.no_color is False

    def test_context_immutability(self, cli_context: FlextCliContext) -> None:
        """Test CLI context immutability (FlextModels pattern)."""
        # Should be immutable as FlextModels - expect ValueError for frozen instance
        with pytest.raises(ValueError, match="Cannot modify immutable FlextCliContext"):
            cli_context.profile = "new-profile"

    def test_context_validation_empty_profile(self) -> None:
        """Test CLI context validation with empty profile."""
        with pytest.raises(ValueError, match="Profile cannot be empty"):
            FlextCliContext.create_with_params(profile="")

    def test_context_validation_invalid_output_format(self) -> None:
        """Test CLI context validation with invalid output format."""
        with pytest.raises(ValueError, match="Output format must be one of"):
            FlextCliContext.create_with_params(output_format="invalid_format")

    def test_context_validation_quiet_and_verbose(self) -> None:
        """Test CLI context validation with both quiet and verbose."""
        with pytest.raises(
            ValueError,
            match="Cannot have both quiet and verbose modes enabled",
        ):
            FlextCliContext.create_with_params(quiet=True, verbose=True)


class TestFlextCliUtilities:
    """Test FlextCliUtilities functionality."""

    def test_utilities_initialization(self) -> None:
        """Test FlextCliUtilities initialization."""
        utilities = FlextCliUtilities()
        assert utilities is not None
        assert hasattr(utilities, "execute")

    def test_utilities_execute_method(self) -> None:
        """Test FlextCliUtilities execute method."""
        utilities = FlextCliUtilities()
        result = utilities.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_formatting_json(self) -> None:
        """Test JSON formatting functionality."""
        utilities = FlextCliUtilities()
        data = {"key": "value", "number": 42}
        result = utilities.Formatting.format_json(data)
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert "key" in result.value

    def test_formatting_yaml(self) -> None:
        """Test YAML formatting functionality."""
        utilities = FlextCliUtilities()
        data = {"key": "value", "list": [1, 2, 3]}
        result = utilities.Formatting.format_yaml(data)
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert "key" in result.value

    def test_formatting_csv(self) -> None:
        """Test CSV formatting functionality."""
        utilities = FlextCliUtilities()
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        result = utilities.Formatting.format_csv(data)
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert "name" in result.value

    def test_formatting_table(self) -> None:
        """Test table formatting functionality."""
        utilities = FlextCliUtilities()
        data = [{"name": "John", "age": 30}, {"name": "Jane", "age": 25}]
        result = utilities.Formatting.format_table(data)
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert "name" in result.value

    def test_validation_helpers(self) -> None:
        """Test validation helper functionality."""
        utilities = FlextCliUtilities()

        # Test data validation
        data = {"key": "value"}
        result = utilities.validate_data(data, lambda x: isinstance(x, dict))
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value is True

        # Test invalid data validation
        result = utilities.validate_data("not a dict", lambda x: isinstance(x, dict))
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value is False

    def test_file_operations(self) -> None:
        """Test file operation functionality."""
        utilities = FlextCliUtilities()

        # Test file existence check
        result = utilities.FileOperations.file_exists("/nonexistent/file.txt")
        assert isinstance(result, bool)
        assert result is False

    def test_data_transformation(self) -> None:
        """Test data transformation functionality."""
        utilities = FlextCliUtilities()

        # Test string normalization
        result = utilities.Transformation.normalize_string("  Test String  ")
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.value == "test string"

        # Test filename sanitization
        result = utilities.Transformation.sanitize_filename("test/file:name")
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert ":" not in result.value

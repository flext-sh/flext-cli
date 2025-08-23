"""Functional tests for utilities.py module.

These tests execute real functionality without mocks to achieve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from flext_cli.utilities import (
    FileInfo,
    FlextCliFileUtilities,
    FlextCliFormattingUtilities,
    FlextCliSystemUtilities,
    FlextCliTimeUtilities,
    FlextCliValidationUtilities,
    JsonObject,
)


class TestFlextCliValidationUtilities:
    """Test FlextCliValidationUtilities class."""

    def test_validate_email_valid(self) -> None:
        """Test email validation with valid emails."""
        result = FlextCliValidationUtilities.validate_email("test@example.com")
        assert result.is_success

    def test_validate_email_invalid(self) -> None:
        """Test email validation with invalid emails."""
        result = FlextCliValidationUtilities.validate_email("invalid-email")
        assert result.is_failure

    def test_validate_email_empty(self) -> None:
        """Test email validation with empty string."""
        result = FlextCliValidationUtilities.validate_email("")
        assert result.is_failure
        assert "empty" in result.error.lower()

    def test_validate_path_valid(self) -> None:
        """Test path validation with valid paths."""
        result = FlextCliValidationUtilities.validate_path("/tmp/test.txt")
        assert result.is_success
        assert isinstance(result.value, Path)

    def test_validate_path_empty(self) -> None:
        """Test path validation with empty path."""
        result = FlextCliValidationUtilities.validate_path("   ")  # Only whitespace
        assert result.is_failure

    def test_validate_config_valid(self) -> None:
        """Test config validation with valid configuration."""
        # Test with a dict that has model_config attribute (like Pydantic models)
        class MockConfig:
            model_config = {}
        
        result = FlextCliValidationUtilities.validate_config(MockConfig())
        assert result.is_success

    def test_validate_config_none(self) -> None:
        """Test config validation with None."""
        result = FlextCliValidationUtilities.validate_config(None)
        assert result.is_failure
        assert "None" in result.error

    def test_validate_json_string_valid(self) -> None:
        """Test JSON string validation with valid JSON."""
        json_str = '{"name": "test", "value": 42}'
        result = FlextCliValidationUtilities.validate_json_string(json_str)
        assert result.is_success
        assert result.value["name"] == "test"

    def test_validate_json_string_invalid(self) -> None:
        """Test JSON string validation with invalid JSON."""
        result = FlextCliValidationUtilities.validate_json_string("invalid json")
        assert result.is_failure
        assert "Invalid JSON" in result.error

    def test_validate_json_string_empty(self) -> None:
        """Test JSON string validation with empty string."""
        result = FlextCliValidationUtilities.validate_json_string("")
        assert result.is_failure
        assert "empty" in result.error.lower()



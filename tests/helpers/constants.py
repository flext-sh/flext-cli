"""Test constants for flext-cli tests.

Centralized constants for test fixtures, factories, and test data.
Does NOT duplicate src/flext_cli/constants.py - only test-specific constants.
Reuses Enums and Literals from FlextCliConstants for consistency.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Final

from flext_cli.constants import FlextCliConstants


class TestConstants:
    """Advanced test constants using Python 3.13+ patterns.

    Centralized test constants following flext-core nested class pattern.
    Uses advanced collections.abc.Mapping for immutable test data.
    Only contains test-specific constants that are NOT in src/constants.py.

    **Advanced Patterns:**
    - collections.abc.Mapping for immutable test data structures
    - StrEnum for test-specific enumerated values
    - Composes with FlextCliConstants for consistency
    - Python 3.13+ discriminated unions for test data validation
    """

    class Paths:
        """Test path constants."""

        TEST_INPUT_DIR: Final[str] = "tests/fixtures/data/input"
        TEST_OUTPUT_DIR: Final[str] = "tests/fixtures/data/output"
        TEST_TEMP_PREFIX: Final[str] = "flext_cli_test_"

    class CLI:
        """CLI test constants."""

        TEST_COMMAND_NAME: Final[str] = "test_command"
        TEST_GROUP_NAME: Final[str] = "test_group"
        TEST_HELP_TEXT: Final[str] = "Test command help text"
        DEFAULT_TIMEOUT: Final[int] = 5

    class Output:
        """Advanced output format test constants.

        Uses collections.abc.Mapping for immutable test data structures.
        Composes with FlextCliConstants StrEnums for runtime validation.
        Python 3.13+ best practice: Immutable mappings prevent test mutations.
        """

        # Immutable test data using collections.abc.Mapping
        TEST_JSON_OUTPUT: Final[Mapping[str, str]] = {
            "status": FlextCliConstants.CommandStatus.COMPLETED.value,
            "data": "test",
        }

        # Immutable table data using tuple of tuples for complete immutability
        TEST_TABLE_DATA: Final[Sequence[Sequence[str]]] = (
            ("header1", "header2"),
            ("value1", "value2"),
        )

        TEST_CSV_DATA: Final[str] = "header1,header2\nvalue1,value2"

        # Test data for different output formats
        TEST_OUTPUT_DATA: Final[Mapping[str, Mapping[str, str | int]]] = {
            "json": {"format": "json", "indent": 2},
            "yaml": {"format": "yaml", "default_flow_style": False},
            "table": {"format": "table", "max_width": 120},
            "csv": {"format": "csv", "delimiter": ","},
        }

    class Commands:
        """Advanced command test constants.

        Uses FlextCliConstants StrEnums for runtime validation and consistency.
        Composes with discriminated unions for better test type safety.
        Python 3.13+ best practice: Immutable mappings for test configurations.
        """

        # Command status constants using StrEnum values
        TEST_COMMAND_STATUS: Final[str] = (
            FlextCliConstants.CommandStatus.COMPLETED.value
        )
        TEST_SESSION_STATUS: Final[str] = FlextCliConstants.SessionStatus.ACTIVE.value
        TEST_SERVICE_STATUS: Final[str] = (
            FlextCliConstants.ServiceStatus.OPERATIONAL.value
        )

        # Test command configurations using immutable mappings
        TEST_COMMAND_CONFIG: Final[Mapping[str, str | bool | int]] = {
            "name": "test_command",
            "description": "Test command for unit tests",
            "enabled": True,
            "timeout": 30,
            "retry_count": 3,
        }

        TEST_COMMAND_ARGS: Final[Sequence[str]] = (
            "--verbose",
            "--debug",
            "--output-format",
            "json",
        )

        TEST_COMMAND_KWARGS: Final[Mapping[str, str | int | bool]] = {
            "verbose": True,
            "debug": True,
            "output_format": "json",
            "timeout": 30,
        }

    class Messages:
        """Advanced message test constants.

        Uses discriminated unions for message type validation.
        Composes with FlextCliConstants.MessageTypes for consistency.
        """

        TEST_INFO_MESSAGE: Final[str] = "Test info message"
        TEST_ERROR_MESSAGE: Final[str] = "Test error message"
        TEST_WARNING_MESSAGE: Final[str] = "Test warning message"
        TEST_SUCCESS_MESSAGE: Final[str] = "Test operation completed successfully"
        TEST_DEBUG_MESSAGE: Final[str] = "Debug information for testing"

        # Message templates using advanced string formatting
        TEST_COMMAND_EXECUTED: Final[str] = "Command '{command}' executed successfully"
        TEST_VALIDATION_FAILED: Final[str] = "Validation failed for {field}: {error}"
        TEST_TIMEOUT_REACHED: Final[str] = "Operation timed out after {timeout} seconds"

    class Configuration:
        """Advanced test configuration constants.

        Uses collections.abc.Mapping for immutable configuration structures.
        Python 3.13+ best practice: Immutable test configurations.
        """

        # Test profile configurations
        TEST_PROFILE_CONFIG: Final[Mapping[str, str | int | bool]] = {
            "name": "test_profile",
            "output_format": "json",
            "verbose": True,
            "debug": False,
            "timeout": 30,
            "max_retries": 3,
        }

        # Test environment configurations
        TEST_ENV_CONFIG: Final[Mapping[str, str]] = {
            "environment": "test",
            "log_level": "DEBUG",
            "api_url": "http://test.example.com",
            "database_url": "sqlite:///test.db",
        }

        # Test CLI arguments mapping
        TEST_CLI_ARGS: Final[Mapping[str, str | int | bool]] = {
            "verbose": True,
            "quiet": False,
            "debug": True,
            "output_format": "table",
            "timeout": 10,
            "max_width": 100,
        }

    class Fixtures:
        """Test fixture constants using advanced patterns.

        Uses discriminated unions and immutable structures.
        Python 3.13+ best practice: Immutable test fixtures.
        """

        # Sample data fixtures
        SAMPLE_USER_DATA: Final[Mapping[str, str | int]] = {
            "id": 123,
            "username": "testuser",
            "email": "test@example.com",
            "role": "admin",
        }

        SAMPLE_COMMAND_DATA: Final[Mapping[str, str | int | bool]] = {
            "name": "sample_command",
            "description": "Sample command for testing",
            "enabled": True,
            "timeout": 60,
            "requires_auth": False,
        }

        # Test data collections using sequences
        SAMPLE_DATA_ROWS: Final[Sequence[Mapping[str, str | int]]] = (
            {"id": 1, "name": "item1", "value": 100},
            {"id": 2, "name": "item2", "value": 200},
            {"id": 3, "name": "item3", "value": 300},
        )

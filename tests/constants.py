"""Constants for flext-cli tests.

Provides TestsFlextCliConstants, extending c with flext-cli-specific
constants using COMPOSITION INHERITANCE.

Inheritance hierarchy:
- c (flext_tests) - Provides .Tests.* namespace
- FlextCliConstants (production) - Provides .Cli.* namespace

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Final

from flext_tests import c
from pydantic import BaseModel, ConfigDict, Field

from flext_cli import FlextCliConstants


class TestsFlextCliConstants(c, FlextCliConstants):
    """Constants for flext-cli tests using COMPOSITION INHERITANCE.

    MANDATORY: Inherits from BOTH:
    1. c - for test infrastructure (.Tests.*)
    2. FlextCliConstants - for domain constants (.Cli.*)

    Access patterns:
    - c.Tests.Docker.* (container testing)
    - c.Tests.Matcher.* (assertion messages)
    - c.Tests.Factory.* (test data generation)
    - c.Cli.* (domain constants from production)
    - c.TestData.* (project-specific test data)

    Rules:
    - NEVER duplicate constants from c or FlextCliConstants
    - Only flext-cli-specific constants allowed (not generic for other projects)
    - All generic constants come from c
    - All production constants come from FlextCliConstants
    """

    ALICE: Final[str] = "Alice"
    VALID_FIELD_NAME: Final[str] = "validField"
    FIELD_NAME: Final[str] = "field"
    WHITESPACE_FIELD_NAME: Final[str] = "field with spaces"
    VALID_STRING: Final[str] = "valid_string"
    STRING: Final[str] = "string"
    WHITESPACE_STRING: Final[str] = "string with spaces"
    NONE_VALUE: Final[None] = None
    TWO: Final[list[str]] = ["item1", "item2"]
    PASSWORD: Final[str] = "secret123"
    LONG: Final[str] = "a" * 1000
    SPECIAL: Final[str] = "!@#$%^&*()"
    UNICODE: Final[str] = "测试字符串"
    PERFORMANCE_THRESHOLD: Final[float] = 0.1
    INFO: Final[str] = "INFO"
    WARNING: Final[str] = "WARNING"
    ALL: Final[list[str]] = ["ALL"]
    NAME_HEADER: Final[str] = "Name"
    GRID: Final[str] = "grid"
    FANCY_GRID: Final[str] = "fancy_grid"
    INVALID: Final[str] = "invalid"
    EXPECTED_ALL: Final[str] = "expected_all"

    class Environment:
        """Test environment constants."""

        PYTEST_CURRENT_TEST: Final[str] = "PYTEST_CURRENT_TEST"
        PYTEST_BINARY: Final[str] = "pytest"
        CI_VALUE: Final[str] = "true"

    SPECIALIZED_CASES: Final[str] = "specialized_cases"

    class Borders:
        """Table border constants."""

        PLUS: Final[str] = "plus"

    Data: Final[str] = "data"
    Config: Final[str] = "config"

    class OutputFormats:
        """Output format constants."""

        INVALID_FORMAT: Final[str] = "invalid_format"

    class Statuses:
        """Test status constants."""

        VALID_STATUSES: Final[list[str]] = ["pending", "running", "completed", "failed"]
        INVALID_STATUS: Final[str] = "invalid_status"

    class FileOps:
        """Test file operations constants."""

        FILE_NOT_FOUND_PATTERNS: Final[tuple[str, ...]] = (
            "not found",
            "no such file",
            "does not exist",
            "errno 2",
            "cannot open",
        )
        NON_FILE_ERRORS: Final[list[str]] = [
            "permission denied",
            "disk full",
            "access denied",
        ]

    Password: Final[str] = "password"

    class PasswordDefaults:
        """Password validation constants."""

        MIN_LENGTH_STRICT: Final[int] = 8
        MIN_LENGTH_DEFAULT: Final[int] = 1

    Progress: Final[str] = "progress"

    class ProgressDefaults:
        """Progress bar constants."""

        SMALL_DATASET_SIZE: Final[int] = 5
        LARGE_DATASET_SIZE: Final[int] = 100

    class TestConfiguration:
        """Test configuration constants."""

        BASIC_CONFIG: Final[dict[str, object]] = {
            "app_name": "test_app",
            "debug": False,
            "log_level": "INFO",
            "output_format": "json",
        }
        "Basic configuration for testing config provider operations."

    class TestData:
        """Test data constants for test modules."""

        CUSTOM: Final[int] = 42
        TWO: Final[int] = 2
        PASSWORD: Final[str] = "test_password_123"
        LONG: Final[str] = (
            "This is a very long message that tests how the system handles extended text input"
        )
        SPECIAL: Final[str] = "!@#$%^&*()"
        UNICODE: Final[str] = "你好世界🌍"
        PERFORMANCE_THRESHOLD: Final[float] = 1.0

    class Strings:
        """Flext-cli-specific test strings organized by complexity."""

        EMPTY: Final[str] = ""
        WHITESPACE_ONLY: Final[str] = "   "
        SINGLE_CHAR: Final[str] = "a"
        BASIC_WORD: Final[str] = "hello"
        BASIC_LIST: Final[str] = "a,b,c"
        NUMERIC_LIST: Final[str] = "1,2,3"
        WITH_SPACES: Final[str] = "a, b, c"
        EXCESSIVE_SPACES: Final[str] = "  a  ,  b  ,  c  "
        LEADING_SPACES: Final[str] = "  hello"
        TRAILING_SPACES: Final[str] = "hello  "
        LEADING_TRAILING: Final[str] = ",a,b,c,"
        WITH_EMPTY: Final[str] = "a,,c"
        ONLY_DELIMITERS: Final[str] = ",,,"
        UNICODE_CHARS: Final[str] = "héllo,wörld"
        VALID_EMAIL: Final[str] = "test@example.com"
        INVALID_EMAIL: Final[str] = "invalid-email"
        USER_ID_VALID: Final[str] = "123"
        USER_ID_INVALID: Final[str] = "invalid"
        USER_ID_EMPTY: Final[str] = ""

    class TestErrors:
        """Flext-cli-specific error message patterns for validation."""

        PROCESSING_ERROR: Final[str] = "Processing error occurred"
        COMMAND_FAILED: Final[str] = "Command failed"
        INVALID_FORMAT: Final[str] = "Invalid format"
        MISSING_ARGUMENT: Final[str] = "Missing required argument"

    class CliTest:
        """CLI-specific test constants."""

        class Commands:
            """Test command names."""

            TEST_CMD: Final[str] = "test-command"
            HELP_CMD: Final[str] = "help"
            VERSION_CMD: Final[str] = "version"

        class Formats:
            """Test output formats."""

            JSON: Final[str] = "json"
            YAML: Final[str] = "yaml"
            TABLE: Final[str] = "table"
            PLAIN: Final[str] = "plain"

        class MixinsFieldNames:
            """Field name constants for validation messages."""

            OUTPUT_FORMAT: Final[str] = "output format"
            LOG_LEVEL: Final[str] = "log level"
            STATUS: Final[str] = "status"
            PIPELINE_STEP_NAME: Final[str] = "name"

        class Status:
            """Test command statuses."""

            SUCCESS: Final[str] = "success"
            FAILURE: Final[str] = "failure"
            PENDING: Final[str] = "pending"
            RUNNING: Final[str] = "running"

        class TestData:
            """Test data constants."""

            ALICE: Final[str] = "alice"
            VALID_FIELD_NAME: Final[str] = "validField"
            FIELD_NAME: Final[str] = "field"
            WHITESPACE_FIELD_NAME: Final[str] = "field with spaces"
            VALID_STRING: Final[str] = "valid_string"
            STRING: Final[str] = "string"
            WHITESPACE_STRING: Final[str] = "string with spaces"
            NONE_VALUE: Final[None] = None

    class Fixtures:
        """Test fixture dataclasses for flext-cli tests."""

        class Identifiers(BaseModel):
            """Test identifiers and IDs."""

            model_config = ConfigDict(frozen=True)

            user_id: str = Field(default="test_user_123", description="Test user id")
            session_id: str = Field(
                default="test_session_123", description="Test session id"
            )
            service_name: str = Field(
                default="test_service", description="Test service name"
            )
            operation_id: str = Field(
                default="test_operation", description="Test operation id"
            )
            request_id: str = Field(
                default="test-request-456", description="Test request id"
            )
            correlation_id: str = Field(
                default="test-corr-123", description="Test correlation id"
            )

        class Names(BaseModel):
            """Test module and component names."""

            model_config = ConfigDict(frozen=True)

            module_name: str = Field(
                default="test_module", description="Test module name"
            )
            handler_name: str = Field(
                default="test_handler", description="Test handler name"
            )
            chain_name: str = Field(default="test_chain", description="Test chain name")
            command_type: str = Field(
                default="test_command", description="Test command type"
            )
            query_type: str = Field(default="test_query", description="Test query type")
            logger_name: str = Field(
                default="test_logger", description="Test logger name"
            )
            app_name: str = Field(default="test-app", description="Test app name")
            validation_app: str = Field(
                default="validation-test", description="Validation app name"
            )
            source_service: str = Field(
                default="test_service", description="Source service name"
            )

        class ErrorData(BaseModel):
            """Test error codes and messages."""

            model_config = ConfigDict(frozen=True)

            error_code: str = Field(
                default="TEST_ERROR_001", description="Test error code"
            )
            validation_error: str = Field(
                default="test_error", description="Validation error text"
            )
            operation_error: str = Field(
                default="Op failed", description="Operation error text"
            )
            config_error: str = Field(
                default="Config failed", description="Config error text"
            )
            timeout_error: str = Field(
                default="Operation timeout", description="Timeout error text"
            )

        class Data(BaseModel):
            """Test field names and data values."""

            model_config = ConfigDict(frozen=True)

            field_name: str = Field(default="test_field", description="Test field name")
            config_key: str = Field(default="test_key", description="Test config key")
            username: str = Field(default="test_user", description="Test username")
            email: str = Field(default="test@example.com", description="Test email")
            password: str = Field(default="test_pass", description="Test password")
            string_value: str = Field(
                default="test_value", description="Test string value"
            )
            input_data: str = Field(default="test_input", description="Test input data")
            request_data: str = Field(
                default="test_request", description="Test request data"
            )
            result_data: str = Field(
                default="test_result", description="Test result data"
            )
            message: str = Field(default="test_message", description="Test message")

    class Table:
        """Table-related test constants."""

        class Borders:
            """Table border constants."""

            PLUS: Final[str] = "+"

        SPECIALIZED_CASES: Final[list[tuple[str, str, list[str]]]] = [
            ("simple", "simple", ["name", "role", "alice"]),
            ("grid", "grid", ["+", "-", "|"]),
            ("fancy_grid", "fancy_grid", ["╒", "═", "│"]),
            ("markdown", "markdown", ["|", "-"]),
            ("html", "html", ["<table>", "<tr>", "<td>"]),
            ("latex", "latex", ["\\begin{tabular}", "\\hline"]),
            ("rst", "rst", ["=", "name", "role"]),
        ]

    class TestAuthentication:
        """Authentication test constants for protocol testing."""

        VALID_TOKEN: Final[str] = "valid_token"
        INVALID_TOKEN: Final[str] = "invalid_token_xyz"
        VALID_CREDS: Final[dict[str, str]] = {
            "username": "testuser",
            "password": "testpass",
        }
        INVALID_CREDS: Final[dict[str, str]] = {
            "username": "invalid",
            "password": "wrong",
        }
        EMPTY_CREDS: Final[dict[str, str]] = {"username": "", "password": ""}


__all__ = ["TestsFlextCliConstants", "c"]

c = TestsFlextCliConstants

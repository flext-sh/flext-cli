"""Constants for flext-cli tests.

Provides TestsFlextCliConstants, extending FlextTestsConstants with flext-cli-specific
constants using COMPOSITION INHERITANCE.

Inheritance hierarchy:
- FlextTestsConstants (flext_tests) - Provides .Tests.* namespace
- FlextCliConstants (production) - Provides .Cli.* namespace

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

from flext_cli.constants import FlextCliConstants
from flext_cli.typings import t
from flext_tests.constants import FlextTestsConstants


class TestsFlextCliConstants(FlextTestsConstants, FlextCliConstants):
    """Constants for flext-cli tests using COMPOSITION INHERITANCE.

    MANDATORY: Inherits from BOTH:
    1. FlextTestsConstants - for test infrastructure (.Tests.*)
    2. FlextCliConstants - for domain constants (.Cli.*)

    Access patterns:
    - c.Tests.Docker.* (container testing)
    - c.Tests.Matcher.* (assertion messages)
    - c.Tests.Factory.* (test data generation)
    - c.Cli.* (domain constants from production)
    - c.TestData.* (project-specific test data)

    Rules:
    - NEVER duplicate constants from FlextTestsConstants or FlextCliConstants
    - Only flext-cli-specific constants allowed (not generic for other projects)
    - All generic constants come from FlextTestsConstants
    - All production constants come from FlextCliConstants
    """

    # =========================================================================
    # TEST DATA CONSTANTS
    # =========================================================================
    # Constantes de dados de teste - valores simples para usar em testes

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

    # Status constants
    INFO: Final[str] = "INFO"
    WARNING: Final[str] = "WARNING"
    ALL: Final[list[str]] = ["ALL"]

    # Format constants
    NAME_HEADER: Final[str] = "Name"
    GRID: Final[str] = "grid"
    FANCY_GRID: Final[str] = "fancy_grid"
    INVALID: Final[str] = "invalid"
    EXPECTED_ALL: Final[str] = "expected_all"

    # Environment constants
    class Environment:
        """Test environment constants."""

        PYTEST_CURRENT_TEST: Final[str] = "PYTEST_CURRENT_TEST"
        PYTEST_BINARY: Final[str] = "pytest"
        CI_VALUE: Final[str] = "true"

    # Table constants
    SPECIALIZED_CASES: Final[str] = "specialized_cases"

    class Borders:
        """Table border constants."""

        PLUS: Final[str] = "plus"

    Data: Final[str] = "data"

    # Config and OutputFormats
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

    class Configuration:
        """Test configuration constants."""

        BASIC_CONFIG: Final[dict[str, t.GeneralValueType]] = {
            "app_name": "test_app",
            "debug": False,
            "log_level": "INFO",
            "output_format": "json",
        }
        """Basic configuration for testing config provider operations."""

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

        @dataclass(frozen=True, slots=True)
        class Identifiers:
            """Test identifiers and IDs."""

            user_id: str = "test_user_123"
            session_id: str = "test_session_123"
            service_name: str = "test_service"
            operation_id: str = "test_operation"
            request_id: str = "test-request-456"
            correlation_id: str = "test-corr-123"

        @dataclass(frozen=True, slots=True)
        class Names:
            """Test module and component names."""

            module_name: str = "test_module"
            handler_name: str = "test_handler"
            chain_name: str = "test_chain"
            command_type: str = "test_command"
            query_type: str = "test_query"
            logger_name: str = "test_logger"
            app_name: str = "test-app"
            validation_app: str = "validation-test"
            source_service: str = "test_service"

        @dataclass(frozen=True, slots=True)
        class ErrorData:
            """Test error codes and messages."""

            error_code: str = "TEST_ERROR_001"
            validation_error: str = "test_error"
            operation_error: str = "Op failed"
            config_error: str = "Config failed"
            timeout_error: str = "Operation timeout"

        @dataclass(frozen=True, slots=True)
        class Data:
            """Test field names and data values."""

            field_name: str = "test_field"
            config_key: str = "test_key"
            username: str = "test_user"
            email: str = "test@example.com"
            password: str = "test_pass"
            string_value: str = "test_value"
            input_data: str = "test_input"
            request_data: str = "test_request"
            result_data: str = "test_result"
            message: str = "test_message"

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

    class Authentication:
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

        EMPTY_CREDS: Final[dict[str, str]] = {
            "username": "",
            "password": "",
        }


# Short alias per FLEXT convention
c = TestsFlextCliConstants

__all__ = [
    "TestsFlextCliConstants",
    "c",
]

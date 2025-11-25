"""FLEXT CLI Test Constants - Organized by domain and reusable across tests.

Provides centralized constants for all flext-cli tests, organized in namespaces
for better maintainability and reusability.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import Final


class TestData:
    """Test data constants organized by domain."""

    class Users:
        """User-related test data."""

        VALID_USERNAME: Final[str] = "testuser"
        VALID_PASSWORD: Final[str] = "testpass123"
        SHORT_USERNAME: Final[str] = "ab"
        SHORT_PASSWORD: Final[str] = "short"
        EMPTY_USERNAME: Final[str] = ""
        EMPTY_PASSWORD: Final[str] = ""
        WHITESPACE_TOKEN: Final[str] = "   "

        # User data dictionaries
        VALID_CREDENTIALS: Final[dict[str, str]] = {
            "username": VALID_USERNAME,
            "password": VALID_PASSWORD,
        }
        SHORT_USERNAME_CREDS: Final[dict[str, str]] = {
            "username": SHORT_USERNAME,
            "password": VALID_PASSWORD,
        }
        SHORT_PASSWORD_CREDS: Final[dict[str, str]] = {
            "username": VALID_USERNAME,
            "password": SHORT_PASSWORD,
        }
        EMPTY_CREDS: Final[dict[str, str]] = {
            "username": EMPTY_USERNAME,
            "password": EMPTY_PASSWORD,
        }

    class Tokens:
        """Token-related test data."""

        VALID_TOKEN: Final[str] = "test_token_abc123"
        REFRESH_TOKEN: Final[str] = "refresh_token_xyz789"
        EMPTY_TOKEN: Final[str] = ""
        NULL_TOKEN: Final[None] = None
        NUMERIC_TOKEN: Final[int] = 12345

        # Token data structures
        VALID_TOKEN_DATA: Final[dict[str, str]] = {"token": VALID_TOKEN}
        EMPTY_TOKEN_DATA: Final[dict[str, str]] = {"token": EMPTY_TOKEN}
        NULL_TOKEN_DATA: Final[dict[str, str | None]] = {"token": NULL_TOKEN}
        NUMERIC_TOKEN_DATA: Final[dict[str, int]] = {"token": NUMERIC_TOKEN}
        MISSING_TOKEN_DATA: Final[dict[str, str]] = {}  # No token key

    class Config:
        """Configuration-related test data."""

        DEBUG_TRUE: Final[bool] = True
        DEBUG_FALSE: Final[bool] = False
        OUTPUT_FORMAT_JSON: Final[str] = "json"
        OUTPUT_FORMAT_TABLE: Final[str] = "table"
        OUTPUT_FORMAT_YAML: Final[str] = "yaml"
        NO_COLOR_TRUE: Final[bool] = True
        NO_COLOR_FALSE: Final[bool] = False
        PROFILE_TEST: Final[str] = "test"
        PROFILE_DEV: Final[str] = "dev"
        TIMEOUT_DEFAULT: Final[int] = 30
        RETRIES_DEFAULT: Final[int] = 3
        ENDPOINT_DEFAULT: Final[str] = "https://api.example.com"

        # Config dictionaries
        VALID_CONFIG: Final[dict[str, bool | str | int]] = {
            "debug": DEBUG_TRUE,
            "output_format": OUTPUT_FORMAT_JSON,
            "no_color": NO_COLOR_FALSE,
            "profile": PROFILE_TEST,
            "timeout": TIMEOUT_DEFAULT,
            "retries": RETRIES_DEFAULT,
            "api_endpoint": ENDPOINT_DEFAULT,
        }

    class Files:
        """File-related test data."""

        TEST_CONTENT: Final[str] = "test content"
        JSON_CONTENT: Final[str] = '{"key": "value", "number": 42}'
        YAML_CONTENT: Final[str] = "key: value\nnumber: 42\n"
        CSV_CONTENT: Final[str] = "name,age\nJohn,30\nJane,25"
        EMPTY_CONTENT: Final[str] = ""

        # File data structures
        VALID_FILE_DATA: Final[dict[str, str | dict[str, str | int] | list[int]]] = {
            "content": TEST_CONTENT,
            "metadata": {
                "created": "2025-01-01T00:00:00Z",
                "modified": "2025-01-01T00:00:00Z",
                "size": 42,
                "type": "text/plain",
            },
            "path": "test_file.txt",
        }

    class Commands:
        """Command-related test data."""

        TEST_COMMAND: Final[str] = "test_command"
        ARGS_VERBOSE: Final[list[str]] = ["--verbose"]
        ARGS_TIMEOUT: Final[list[str]] = ["--timeout", "30"]
        STATUS_PENDING: Final[str] = "pending"
        STATUS_SUCCESS: Final[str] = "success"
        STATUS_FAILED: Final[str] = "failed"

        # Command data structures
        VALID_COMMAND_DATA: Final[
            dict[str, str | list[str] | dict[str, int] | dict[str, str]]
        ] = {
            "command": TEST_COMMAND,
            "args": ARGS_VERBOSE,
            "kwargs": {
                "timeout": 30,  # TIMEOUT_DEFAULT
                "retries": 3,  # RETRIES_DEFAULT
            },
            "expected_result": {"status": STATUS_SUCCESS, "data": "test_output"},
        }

    class Tables:
        """Table-related test data."""

        SIMPLE_DATA: Final[list[dict[str, str | int]]] = [
            {"name": "John", "age": 30},
            {"name": "Jane", "age": 25},
        ]
        COMPLEX_DATA: Final[list[dict[str, str | int | list[int]]]] = [
            {"name": "Alice", "age": 28, "tags": [1, 2, 3]},
            {"name": "Bob", "age": 35, "tags": [4, 5]},
        ]
        EMPTY_DATA: Final[list[dict[str, str]]] = []
        SINGLE_ROW: Final[list[dict[str, str]]] = [{"name": "Single"}]

    class Output:
        """Output-related test data."""

        SUCCESS_MESSAGE: Final[str] = "Operation completed successfully"
        ERROR_MESSAGE: Final[str] = "An error occurred"
        WARNING_MESSAGE: Final[str] = "This is a warning"
        INFO_MESSAGE: Final[str] = "Information message"
        STYLE_GREEN: Final[str] = "green"
        STYLE_RED: Final[str] = "red"
        STYLE_YELLOW: Final[str] = "yellow"


class TestScenarios:
    """Test scenarios organized by functionality."""

    class Authentication:
        """Authentication test scenarios."""

        VALID_LOGIN: Final[str] = "valid_login"
        INVALID_CREDENTIALS: Final[str] = "invalid_credentials"
        EMPTY_CREDENTIALS: Final[str] = "empty_credentials"
        TOKEN_AUTH: Final[str] = "token_auth"
        EXPIRED_TOKEN: Final[str] = "expired_token"

    class FileOperations:
        """File operation test scenarios."""

        READ_EXISTING: Final[str] = "read_existing"
        READ_NONEXISTENT: Final[str] = "read_nonexistent"
        WRITE_NEW: Final[str] = "write_new"
        WRITE_EXISTING: Final[str] = "write_existing"
        DELETE_EXISTING: Final[str] = "delete_existing"
        DELETE_NONEXISTENT: Final[str] = "delete_nonexistent"
        COPY_FILE: Final[str] = "copy_file"
        MOVE_FILE: Final[str] = "move_file"

    class CommandExecution:
        """Command execution test scenarios."""

        SUCCESSFUL_EXEC: Final[str] = "successful_exec"
        FAILED_EXEC: Final[str] = "failed_exec"
        TIMEOUT_EXEC: Final[str] = "timeout_exec"
        INTERRUPTED_EXEC: Final[str] = "interrupted_exec"

    class Configuration:
        """Configuration test scenarios."""

        VALID_CONFIG: Final[str] = "valid_config"
        INVALID_CONFIG: Final[str] = "invalid_config"
        MISSING_CONFIG: Final[str] = "missing_config"
        CORRUPTED_CONFIG: Final[str] = "corrupted_config"


class TestLimits:
    """Test limits and boundaries."""

    class Sizes:
        """Size limits for test data."""

        MAX_USERNAME_LEN: Final[int] = 50
        MAX_PASSWORD_LEN: Final[int] = 100
        MAX_TOKEN_LEN: Final[int] = 500
        MAX_FILE_SIZE: Final[int] = 1024 * 1024  # 1MB
        MAX_COMMAND_ARGS: Final[int] = 100

    class Timeouts:
        """Timeout values for tests."""

        FAST_TIMEOUT: Final[float] = 0.1
        NORMAL_TIMEOUT: Final[float] = 5.0
        SLOW_TIMEOUT: Final[float] = 30.0
        VERY_SLOW_TIMEOUT: Final[float] = 120.0

    class Counts:
        """Count limits for test data."""

        SMALL_BATCH: Final[int] = 5
        MEDIUM_BATCH: Final[int] = 50
        LARGE_BATCH: Final[int] = 500
        CONCURRENT_WORKERS: Final[int] = 10


class TestPaths:
    """Test file and directory paths."""

    class Files:
        """Test file paths."""

        CONFIG_FILE: Final[str] = "test_config.json"
        TOKEN_FILE: Final[str] = "token.json"
        REFRESH_TOKEN_FILE: Final[str] = "refresh_token.json"
        LOG_FILE: Final[str] = "test.log"
        TEMP_FILE: Final[str] = "temp.txt"
        INVALID_PATH: Final[str] = "/invalid/path/file.txt"

    class Directories:
        """Test directory paths."""

        TEMP_DIR: Final[str] = "temp"
        CONFIG_DIR: Final[str] = "config"
        LOGS_DIR: Final[str] = "logs"
        INVALID_DIR: Final[str] = "/invalid/directory"


class TestMessages:
    """Test messages and error strings."""

    class Errors:
        """Error messages."""

        FILE_NOT_FOUND: Final[str] = "File not found"
        PERMISSION_DENIED: Final[str] = "Permission denied"
        INVALID_FORMAT: Final[str] = "Invalid format"
        TIMEOUT_ERROR: Final[str] = "Operation timed out"
        CONNECTION_ERROR: Final[str] = "Connection failed"

    class Success:
        """Success messages."""

        OPERATION_SUCCESSFUL: Final[str] = "Operation completed successfully"
        FILE_CREATED: Final[str] = "File created successfully"
        CONFIG_LOADED: Final[str] = "Configuration loaded successfully"
        AUTH_SUCCESSFUL: Final[str] = "Authentication successful"


class TestUtilities:
    """Utilities-related test constants and data."""

    class Validation:
        """Validation test data."""

        VALID_FIELD_NAME: Final[str] = "test_field"
        EMPTY_FIELD_NAME: Final[str] = ""
        WHITESPACE_FIELD_NAME: Final[str] = "   "
        VALID_STRING: Final[str] = "valid_string"
        EMPTY_STRING: Final[str] = ""
        WHITESPACE_STRING: Final[str] = "   "
        INTEGER_VALUE: Final[int] = 123
        NONE_VALUE: Final[None] = None

        class Statuses:
            """Status validation data."""

            VALID_STATUSES: Final[list[str]] = [
                "pending",
                "running",
                "completed",
                "failed",
            ]
            INVALID_STATUS: Final[str] = "invalid_status"

        class OutputFormats:
            """Output format validation data."""

            VALID_FORMATS: Final[list[str]] = ["json", "yaml", "table"]
            INVALID_FORMAT: Final[str] = "invalid_format"
            UPPERCASE_FORMAT: Final[str] = "JSON"

    class Environment:
        """Environment test data."""

        PYTEST_CURRENT_TEST: Final[str] = "test_utilities.py::test_something"
        CI_VALUE: Final[str] = "true"
        PYTEST_BINARY: Final[str] = "/usr/bin/pytest"
        BASH_BINARY: Final[str] = "/bin/bash"

    class FileOps:
        """File operations test data."""

        FILE_NOT_FOUND_PATTERNS: Final[list[str]] = [
            "File not found: test.txt",
            "No such file or directory",
            "Path does not exist: /tmp/missing",
            "[Errno 2] No such file",
            "FILE NOT FOUND: TEST.TXT",
        ]
        NON_FILE_ERRORS: Final[list[str]] = [
            "Permission denied",
            "Invalid JSON format",
        ]

    class Config:
        """Configuration test data."""

        CONFIG_DIR_PATTERN: Final[str] = ".flext"
        EXPECTED_KEYS: Final[list[str]] = [
            "config_dir",
            "config_exists",
            "config_readable",
            "config_writable",
            "timestamp",
        ]

    class TypeNormalizer:
        """Type normalizer test data."""

        SIMPLE_TYPE: Final[type] = str
        COMPLEX_UNION: Final[str] = "str | int | None"  # For display
        LIST_TYPE: Final[str] = "list[str] | None"  # For display


class TestProtocols:
    """Protocols-related test constants and data."""

    class ProtocolTypes:
        """Protocol type constants."""

        CLI_FORMATTER: Final[str] = "CliFormatter"
        CLI_CONFIG_PROVIDER: Final[str] = "CliConfigProvider"
        CLI_AUTHENTICATOR: Final[str] = "CliAuthenticator"
        CLI_DEBUG_PROVIDER: Final[str] = "CliDebugProvider"
        CLI_PLUGIN: Final[str] = "CliPlugin"
        CLI_COMMAND_HANDLER: Final[str] = "CliCommandHandler"

    class TestData:
        """Test data for protocol scenarios."""

        class Formatting:
            """Formatting test data."""

            SIMPLE_DATA: Final[dict[str, object]] = {"key": "value", "count": 42}
            COMPLEX_DATA: Final[dict[str, object]] = {
                "items": [
                    {"name": "item1", "value": 100},
                    {"name": "item2", "value": 200},
                ],
                "metadata": {"created": "2025-01-01", "version": "1.0"},
            }
            FORMAT_OPTIONS: Final[dict[str, object]] = {"style": "json", "indent": 2}

        class Configuration:
            """Configuration test data."""

            BASIC_CONFIG: Final[dict[str, object]] = {"debug": True, "timeout": 30}
            ADVANCED_CONFIG: Final[dict[str, object]] = {
                "debug": False,
                "timeout": 60,
                "retries": 3,
                "endpoints": ["api1", "api2"],
            }

        class Authentication:
            """Authentication test data."""

            VALID_CREDS: Final[dict[str, object]] = {
                "username": "testuser",
                "password": "testpass",
            }
            VALID_TOKEN: Final[str] = "valid_token_abc123"
            INVALID_TOKEN: Final[str] = "invalid_token"

        class Commands:
            """Command test data."""

            TEST_COMMAND: Final[str] = "test_command"
            COMMAND_ARGS: Final[list[str]] = ["--verbose", "--debug"]
            COMMAND_KWARGS: Final[dict[str, object]] = {"timeout": 30, "retries": 2}

        class Plugins:
            """Plugin test data."""

            PLUGIN_NAME: Final[str] = "test_plugin"
            PLUGIN_VERSION: Final[str] = "1.0.0"
            PLUGIN_COMMANDS: Final[list[str]] = ["cmd1", "cmd2", "cmd3"]

    class Results:
        """Expected results for protocol tests."""

        class Success:
            """Success result data."""

            FORMATTED_OUTPUT: Final[str] = '{"key": "value", "count": 42}'
            CONFIG_SAVED: Final[str] = "Configuration saved successfully"
            AUTH_SUCCESS: Final[str] = "Authentication successful"
            DEBUG_INFO: Final[dict[str, object]] = {"status": "ok", "version": "1.0"}
            COMMAND_RESULT: Final[str] = "Command executed successfully"

        class Errors:
            """Error result data."""

            FORMAT_ERROR: Final[str] = "Formatting failed"
            CONFIG_ERROR: Final[str] = "Configuration error"
            AUTH_ERROR: Final[str] = "Authentication failed"
            INVALID_TOKEN: Final[str] = "Invalid token"
            COMMAND_ERROR: Final[str] = "Command execution failed"

    class TestTypes:
        """Test type categories for protocol comprehensive testing."""

        INITIALIZATION: Final[str] = "initialization"
        STRUCTURAL_TYPING: Final[str] = "structural_typing"
        CLI_FORMATTER: Final[str] = "cli_formatter"
        CLI_CONFIG_PROVIDER: Final[str] = "cli_config_provider"
        CLI_AUTHENTICATOR: Final[str] = "cli_authenticator"
        CLI_DEBUG_PROVIDER: Final[str] = "cli_debug_provider"
        CLI_PLUGIN: Final[str] = "cli_plugin"
        CLI_COMMAND_HANDLER: Final[str] = "cli_command_handler"
        PROTOCOL_INHERITANCE: Final[str] = "protocol_inheritance"
        RUNTIME_CHECKING: Final[str] = "runtime_checking"

    class TestCases:
        """Test case definitions for protocol comprehensive testing."""

        CASES: Final[list[tuple[str, str, bool]]] = [
            ("initialization", "Protocol initialization", True),
            ("structural_typing", "Structural typing", True),
            ("cli_formatter", "CLI formatter protocol", True),
            ("cli_config_provider", "CLI config provider protocol", True),
            ("cli_authenticator", "CLI authenticator protocol", True),
            ("cli_debug_provider", "CLI debug provider protocol", True),
            ("cli_plugin", "CLI plugin protocol", True),
            ("cli_command_handler", "CLI command handler protocol", True),
            ("protocol_inheritance", "Protocol inheritance", True),
            ("runtime_checking", "Runtime checking", True),
        ]


class TestCli:
    """CLI-related test constants and data."""

    class CommandNames:
        """Command names for CLI testing."""

        TEST_CMD: Final[str] = "test_cmd"
        MY_FUNCTION: Final[str] = "my_function"
        TEST_GROUP: Final[str] = "test_group"
        MY_GROUP: Final[str] = "my_group"
        TEST_CONFIRM: Final[str] = "test_confirm"
        TEST_CONFIRM_ABORT: Final[str] = "test_confirm_abort"
        TEST_PROMPT: Final[str] = "test_prompt"
        TEST_PROMPT_ABORT: Final[str] = "test_prompt_abort"
        MYAPP: Final[str] = "myapp"
        HELLO: Final[str] = "hello"
        PROCESS: Final[str] = "process"
        SELECT: Final[str] = "select"
        MULTI: Final[str] = "multi"

    class ClickTypes:
        """Click type names for testing."""

        CHOICE: Final[str] = "Choice"
        PATH: Final[str] = "Path"
        FILE: Final[str] = "File"
        INTRANGE: Final[str] = "IntRange"
        FLOATRANGE: Final[str] = "FloatRange"
        UUID: Final[str] = "UUID"
        DATETIME: Final[str] = "DateTime"
        TUPLE: Final[str] = "Tuple"

    class PrimitiveTypes:
        """Primitive type names for testing."""

        BOOL: Final[str] = "bool"
        STR: Final[str] = "str"
        INT: Final[str] = "int"
        FLOAT: Final[str] = "float"

    class TestData:
        """Test data for CLI scenarios."""

        class ClickTypeData:
            """Click type test data."""

            CHOICE_DATA: Final[dict[str, object]] = {"choices": ["json", "yaml", "csv"]}
            PATH_DATA: Final[dict[str, object]] = {
                "exists": True,
                "file_okay": True,
                "dir_okay": False,
            }
            FILE_DATA: Final[dict[str, object]] = {"mode": "r", "encoding": "utf-8"}
            INT_RANGE_DATA: Final[dict[str, int]] = {"min": 1, "max": 10}
            FLOAT_RANGE_DATA: Final[dict[str, float]] = {"min": 0.0, "max": 1.0}

        class Commands:
            """Command test data."""

            SIMPLE_DATA: Final[dict[str, object]] = {"key": "value", "count": 42}
            COMPLEX_DATA: Final[dict[str, object]] = {
                "items": [
                    {"name": "item1", "value": 100},
                    {"name": "item2", "value": 200},
                ],
                "metadata": {"created": "2025-01-01", "version": "1.0"},
            }
            FORMAT_OPTIONS: Final[dict[str, object]] = {"style": "json", "indent": 2}

        class Models:
            """Model test data."""

            PARAMS_WITH_ALIASES: Final[dict[str, object]] = {
                "input_dir": "/input",
                "output_dir": "/output",
                "max_count": 10,
            }
            STANDARD_PARAMS: Final[dict[str, object]] = {
                "input_path": "/input/file.txt",
                "count": 5,
            }
            BOOL_PARAMS: Final[dict[str, object]] = {
                "enable_sync": True,
                "verbose_mode": False,
            }
            MIXED_PARAMS: Final[dict[str, object]] = {
                "required_field": "required",
                "optional_field": "default_value",
                "optional_int": 42,
            }

    class Mappings:
        """Mapping constants for CLI tests."""

        class PrimitiveTypeGetters:
            """Primitive type getter methods."""

            DATA: Final[dict[str, str]] = {
                "bool": "get_bool_type",
                "str": "get_string_type",
                "int": "get_int_type",
                "float": "get_float_type",
            }

        class PrimitiveTypeReturns:
            """Primitive type return types."""

            DATA: Final[dict[str, type]] = {
                "bool": bool,
                "str": str,
                "int": int,
                "float": float,
            }

    class DatetimeFormats:
        """Datetime format constants."""

        DEFAULT: Final[list[str]] = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ]

    class TestTypes:
        """Test type categories for CLI comprehensive testing."""

        INITIALIZATION: Final[str] = "initialization"
        COMMAND_DECORATORS: Final[str] = "command_decorators"
        GROUP_DECORATORS: Final[str] = "group_decorators"
        OPTION_ARGUMENT_DECORATORS: Final[str] = "option_argument_decorators"
        PARAMETER_TYPES: Final[str] = "parameter_types"
        CONTEXT_MANAGEMENT: Final[str] = "context_management"
        CLI_RUNNER: Final[str] = "cli_runner"
        UTILITY_METHODS: Final[str] = "utility_methods"
        MODEL_COMMANDS: Final[str] = "model_commands"
        INTEGRATION_WORKFLOWS: Final[str] = "integration_workflows"

    class TestCases:
        """Test case definitions for CLI comprehensive testing."""

        CASES: Final[list[tuple[str, str, bool]]] = [
            ("initialization", "CLI initialization", True),
            ("command_decorators", "Command decorators", True),
            ("group_decorators", "Group decorators", True),
            ("option_argument_decorators", "Option/argument decorators", True),
            ("parameter_types", "Parameter types", True),
            ("context_management", "Context management", True),
            ("cli_runner", "CLI runner", True),
            ("utility_methods", "Utility methods", True),
            ("model_commands", "Model commands", True),
            ("integration_workflows", "Integration workflows", True),
        ]


class TestTypings:
    """Typings-related test constants and data."""

    class TypeDefinitions:
        """Type definition constants."""

        SIMPLE_TYPE_VAR: Final[str] = "t"
        COMPLEX_TYPE_VAR: Final[str] = "k"
        VALUE_TYPE_VAR: Final[str] = "v"
        GENERIC_CONTAINER: Final[str] = "Container"
        KEY_VALUE_STORE: Final[str] = "KeyValueStore"

    class TypedDicts:
        """TypedDict examples."""

        class UserData:
            """User data structure."""

            ID: Final[int] = 1
            NAME: Final[str] = "John Doe"
            EMAIL: Final[str] = "john@example.com"
            ACTIVE: Final[bool] = True

        class ApiResponse:
            """API response structure."""

            STATUS: Final[str] = "success"
            MESSAGE: Final[str] = "Operation successful"
            ERROR: Final[str | None] = None

    class TestData:
        """Test data for typing scenarios."""

        class Processing:
            """Data processing test data."""

            STRING_LIST: Final[list[str]] = ["hello", "world", "test"]
            NUMBER_LIST: Final[list[int]] = [1, 2, 3, 4, 5]
            MIXED_DICT: Final[dict[str, object]] = {
                "key1": 123,
                "key2": "value",
                "key3": True,
                "key4": [1, 2, 3],
            }

        class Api:
            """API test data."""

            SINGLE_USER: Final[dict[str, object]] = {
                "id": 1,
                "name": "Alice",
                "email": "alice@example.com",
                "active": True,
            }
            MULTI_USERS: Final[list[dict[str, object]]] = [
                {
                    "id": 1,
                    "name": "Alice",
                    "email": "alice@example.com",
                    "active": True,
                },
                {"id": 2, "name": "Bob", "email": "bob@example.com", "active": False},
            ]

    class Patterns:
        """Common type patterns."""

        OPTIONAL_STR: Final[str] = "str | None"
        UNION_TYPES: Final[str] = "str | int | bool"
        COMPLEX_UNION: Final[str] = "list[dict[str, str | int]] | None"

    class Protocols:
        """Protocol test data."""

        OPERATION_DATA: Final[list[str]] = ["process", "validate", "transform"]
        RESULT_DATA: Final[dict[str, object]] = {
            "processed": ["HELLO", "WORLD", "TEST"],
            "count": 3,
            "timestamp": "2025-01-01T00:00:00Z",
        }


class TestTables:
    """Tables-related test constants and data."""

    class Formats:
        """Table format constants."""

        SIMPLE: Final[str] = "simple"
        GRID: Final[str] = "grid"
        FANCY_GRID: Final[str] = "fancy_grid"
        PIPE: Final[str] = "pipe"
        PLAIN: Final[str] = "plain"
        INVALID: Final[str] = "invalid_format"

        class ExpectedFormats:
            """Expected format lists."""

            ALL: Final[list[str]] = ["simple", "plain", "grid", "fancy_grid", "pipe"]
            BASIC: Final[list[str]] = ["simple", "grid", "pipe", "fancy_grid"]

    class Data:
        """Test data for tables."""

        class Sample:
            """Sample table data."""

            PEOPLE_DICT: Final[list[dict[str, str | int | float]]] = [
                {"name": "Alice", "age": 30, "city": "New York", "salary": 75000.50},
                {"name": "Bob", "age": 25, "city": "London", "salary": 65000.75},
                {"name": "Charlie", "age": 35, "city": "Paris", "salary": 85000.25},
            ]
            PEOPLE_LIST: Final[list[list[str | int | float]]] = [
                ["Alice", 30, "New York", 75000.50],
                ["Bob", 25, "London", 65000.75],
                ["Charlie", 35, "Paris", 85000.25],
            ]
            SINGLE_ROW: Final[list[dict[str, str | int]]] = [
                {"name": "Alice", "age": 30}
            ]
            WITH_NONE: Final[list[dict[str, str | int | None]]] = [
                {"name": "Alice", "age": 30, "city": None},
                {"name": "Bob", "age": None, "city": "London"},
            ]
            EMPTY: Final[list[dict[str, str]]] = []

        class Headers:
            """Header configurations."""

            CUSTOM: Final[list[str]] = ["Name", "Age", "City", "Salary"]
            SHORT: Final[list[str]] = ["Name", "Age"]

    class Config:
        """Table configuration options."""

        class Alignment:
            """Alignment options."""

            CENTER: Final[str] = "center"
            LEFT: Final[str] = "left"
            RIGHT: Final[str] = "right"
            LIST: Final[list[str]] = [LEFT, RIGHT, CENTER, LEFT]

        class FloatFormat:
            """Float formatting options."""

            TWO_DECIMAL: Final[str] = ".2f"
            ONE_DECIMAL: Final[str] = ".1f"

        class Options:
            """Boolean options."""

            SHOW_INDEX_TRUE: Final[bool] = True
            SHOW_INDEX_FALSE: Final[bool] = False

    class Assertions:
        """Expected assertion values."""

        class Content:
            """Content assertions."""

            ALICE: Final[str] = "Alice"
            BOB: Final[str] = "Bob"
            CHARLIE: Final[str] = "Charlie"
            NAME_HEADER: Final[str] = "name"
            AGE_HEADER: Final[str] = "age"

        class Borders:
            """Border character assertions."""

            PLUS: Final[str] = "+"
            PIPE: Final[str] = "|"
            EQUALS: Final[str] = "="
            DASH: Final[str] = "-"

        class Html:
            """HTML assertions."""

            TABLE_TAG: Final[str] = "<table>"

        class Errors:
            """Error message assertions."""

            EMPTY: Final[str] = "empty"
            INVALID: Final[str] = "invalid"
            UNKNOWN: Final[str] = "unknown"

    class TestTypes:
        """Test type categories for table testing."""

        INITIALIZATION: Final[str] = "initialization"
        FORMAT_AVAILABILITY: Final[str] = "format_availability"
        CREATE_TABLE_BASIC: Final[str] = "create_table_basic"
        CREATE_TABLE_ADVANCED: Final[str] = "create_table_advanced"
        SPECIALIZED_FORMATS: Final[str] = "specialized_formats"
        FORMAT_DISCOVERY: Final[str] = "format_discovery"
        EDGE_CASES: Final[str] = "edge_cases"
        ERROR_HANDLING: Final[str] = "error_handling"
        INTEGRATION_WORKFLOW: Final[str] = "integration_workflow"

    class SpecializedFormats:
        """Specialized format test cases."""

        CASES: Final[list[tuple[str, str, list[str]]]] = [
            (
                "simple",
                "simple",
                [
                    "Alice",
                    "name",
                ],
            ),
            (
                "grid",
                "grid",
                [
                    "Alice",
                    "+",
                    "|",
                ],
            ),
            (
                "markdown",
                "pipe",
                [
                    "Alice",
                    "|",
                ],
            ),
            ("html", "html", ["Alice", "table"]),
            ("latex", "latex", ["Alice"]),
            (
                "rst",
                "rst",
                [
                    "Alice",
                    "=",
                ],
            ),
        ]


class TestMixins:
    """Mixins-related test constants and data."""

    class BusinessRules:
        """Business rules mixin test data."""

        class CommandStates:
            """Command execution states."""

            RUNNING: Final[str] = "running"
            STOPPED: Final[str] = "stopped"
            PAUSED: Final[str] = "paused"
            COMPLETED: Final[str] = "completed"
            FAILED: Final[str] = "failed"

        class SessionStates:
            """Session states."""

            ACTIVE: Final[str] = "active"
            IDLE: Final[str] = "idle"
            ERROR: Final[str] = "error"
            CLOSED: Final[str] = "closed"

        class PipelineSteps:
            """Pipeline step data."""

            VALID_STEP: Final[
                dict[
                    str,
                    str | int | float | bool | dict[str, object] | list[object] | None,
                ]
            ] = {"name": "migration", "type": "batch"}
            STEP_NO_NAME: Final[
                dict[
                    str,
                    str | int | float | bool | dict[str, object] | list[object] | None,
                ]
            ] = {"type": "batch", "config": ""}
            STEP_EMPTY_NAME: Final[
                dict[
                    str,
                    str | int | float | bool | dict[str, object] | list[object] | None,
                ]
            ] = {"name": "", "type": "batch"}
            STEP_WHITESPACE_NAME: Final[
                dict[
                    str,
                    str | int | float | bool | dict[str, object] | list[object] | None,
                ]
            ] = {
                "name": "   ",
                "type": "batch",
            }

        class ConfigData:
            """Configuration data."""

            VALID_CONFIG: Final[
                dict[
                    str,
                    str | int | float | bool | dict[str, object] | list[object] | None,
                ]
            ] = {
                "field1": "value1",
                "field2": "value2",
            }
            INCOMPLETE_CONFIG: Final[
                dict[
                    str,
                    str | int | float | bool | dict[str, object] | list[object] | None,
                ]
            ] = {"field1": "value1"}
            REQUIRED_FIELDS_COMPLETE: Final[list[str]] = ["field1", "field2"]
            REQUIRED_FIELDS_INCOMPLETE: Final[list[str]] = [
                "field1",
                "field2",
                "field3",
            ]

    class CliCommand:
        """CLI command mixin test data."""

        OPERATION_NAME: Final[str] = "test_operation"
        TEST_PARAM_KEY: Final[str] = "test_param"
        TEST_PARAM_VALUE: Final[str] = "test_value"
        SUCCESS_RESULT_KEY: Final[str] = "result"
        SUCCESS_RESULT_VALUE: Final[str] = "success"
        TEST_ERROR_MSG: Final[str] = "Test error"


class TestContext:
    """Context-related test constants and data."""

    class Basic:
        """Basic context test data."""

        DEFAULT_COMMAND: Final[str] = "test_command"
        ALTERNATIVE_COMMAND: Final[str] = "alt_command"
        EMPTY_COMMAND: Final[str] = ""
        WHITESPACE_COMMAND: Final[str] = "   "

    class Arguments:
        """Arguments test data."""

        SINGLE_ARG: Final[list[str]] = ["arg1"]
        MULTIPLE_ARGS: Final[list[str]] = ["arg1", "arg2"]
        LONG_ARGS: Final[list[str]] = ["--verbose", "--debug", "--timeout", "30"]
        EMPTY_ARGS: Final[list[str]] = []

    class Environment:
        """Environment variables test data."""

        SINGLE_VAR: Final[dict[str, str]] = {"VAR1": "value1"}
        MULTIPLE_VARS: Final[dict[str, str]] = {"VAR1": "value1", "VAR2": "value2"}
        EMPTY_VARS: Final[dict[str, str]] = {}
        TEST_VAR_NAME: Final[str] = "TEST_KEY"
        TEST_VAR_VALUE: Final[str] = "test_value"

    class Metadata:
        """Metadata test data."""

        SINGLE_METADATA: Final[dict[str, object]] = {"key1": "value1"}
        NESTED_METADATA: Final[dict[str, object]] = {
            "key1": "value1",
            "nested": {"inner_key": "inner_value"},
        }
        EMPTY_METADATA: Final[dict[str, object]] = {}

    class Paths:
        """Working directory paths."""

        TEST_PATH: Final[str] = "/tmp"
        ALT_PATH: Final[str] = "/home"
        NONE_PATH: Final[None] = None

    class Validation:
        """Validation test data for error scenarios."""

        EMPTY_FIELD: Final[str] = ""
        WHITESPACE_FIELD: Final[str] = "   "
        VALID_STRING: Final[str] = "valid_string"


class TestConstants:
    """Constants-related test constants and data."""

    class ExpectedValues:
        """Expected constant values."""

        PROJECT_NAME: Final[str] = "flext-cli"
        FLEXT_DIR_NAME: Final[str] = ".flext"
        TOKEN_FILE_NAME: Final[str] = "token.json"
        REFRESH_TOKEN_FILE_NAME: Final[str] = "refresh_token.json"
        AUTH_DIR_NAME: Final[str] = "auth"
        DEFAULT_PRIORITY: Final[int] = 999
        TERMINAL_WIDTH_NARROW: Final[int] = 80
        TERMINAL_WIDTH_MEDIUM: Final[int] = 120

    class InvalidChars:
        """Invalid characters for file names."""

        WINDOWS_INVALID: Final[list[str]] = [":", "*", "?", '"', "<", ">", "|"]
        UNIX_INVALID: Final[list[str]] = ["/", "\0"]
        COMMON_INVALID: Final[list[str]] = [
            "/",
            "\\",
            ":",
            "*",
            "?",
            '"',
            "<",
            ">",
            "|",
        ]

    class FormatValidation:
        """Format validation rules."""

        PROJECT_NAME_PATTERN: Final[str] = "flext"
        DIR_NAME_MUST_START_WITH: Final[str] = "."
        FILE_NAME_MUST_END_WITH: Final[str] = ".json"
        TOKEN_KEYWORDS: Final[list[str]] = ["token"]
        REFRESH_KEYWORDS: Final[list[str]] = ["refresh"]

    class TestValues:
        """Test values for constants operations."""

        TEST_TOKEN_JSON: Final[str] = '{"token": "test_token"}'
        TEST_REFRESH_TOKEN_JSON: Final[str] = '{"refresh_token": "test_refresh_token"}'
        ITERATION_COUNT: Final[int] = 1000
        PERFORMANCE_THRESHOLD_SECONDS: Final[float] = 0.1


# Convenience exports for common usage
VALID_USER = {
    "username": "testuser",
    "password": "testpass123",
}
VALID_TOKEN = {"token": "test_token_abc123"}
VALID_CONFIG = {
    "debug": True,
    "output_format": "json",
    "no_color": False,
    "profile": "test",
    "timeout": 30,
    "retries": 3,
    "api_endpoint": "https://api.example.com",
}
TEST_FILE_DATA = {
    "content": "test content",
    "metadata": {
        "created": "2025-01-01T00:00:00Z",
        "modified": "2025-01-01T00:00:00Z",
        "size": 42,
        "type": "text/plain",
    },
    "path": "test_file.txt",
}
TEST_COMMAND_DATA = {
    "command": "test_command",
    "args": ["--verbose"],
    "kwargs": {
        "timeout": 30,
        "retries": 3,
    },
    "expected_result": {"status": "success", "data": "test_output"},
}


class TestCommands:
    """Test constants for FlextCliCommands testing."""

    class CommandNames:
        """Command name constants."""

        TEST_COMMAND: Final[str] = "test_command"
        TEST_EXECUTION: Final[str] = "test_execution"
        VALID: Final[str] = "valid"
        TEMP_CMD: Final[str] = "temp_cmd"
        ALPHA: Final[str] = "alpha"
        BETA: Final[str] = "beta"
        NON_EXISTENT: Final[str] = "non_existent_command"
        INVALID_CMD: Final[str] = "invalid_cmd"
        CMD1: Final[str] = "cmd1"
        CMD2: Final[str] = "cmd2"
        WITH_ARGS: Final[str] = "with_args"
        NO_ARGS: Final[str] = "no_args"
        BAD_CMD: Final[str] = "bad_cmd"
        TIMED: Final[str] = "timed"
        FAILING: Final[str] = "failing"
        INTEGRATION_TEST: Final[str] = "integration_test"
        TEST_GROUP: Final[str] = "test_group"

    class TestData:
        """Test data for commands testing."""

        TEST_RESULT: Final[str] = "test"
        EXECUTED: Final[str] = "executed"
        INTEGRATION_OK: Final[str] = "integration_ok"
        RESULT1: Final[str] = "result1"
        RESULT2: Final[str] = "result2"
        NO_ARGS_RESULT: Final[str] = "no args"
        TIMED_RESULT: Final[str] = "done"

        class Args:
            """Argument test data."""

            ARG1: Final[str] = "arg1"
            ARG2: Final[str] = "arg2"
            ARGS_LIST: Final[list[str]] = ["arg1", "arg2"]
            ARGS_EXPECTED: Final[str] = "args: 2"

        class Timeouts:
            """Timeout test data."""

            CUSTOM_TIMEOUT: Final[int] = 60
            EXECUTION_TIME_LIMIT: Final[float] = 1.0

        class Groups:
            """Command group test data."""

            GROUP_NAME: Final[str] = "test_group"
            GROUP_DESCRIPTION: Final[str] = "Test group"

    class TestCases:
        """Parametrized test cases for commands testing."""

        # Test types for match/case dispatch
        INITIALIZATION = "initialization"
        EXECUTION = "execution"
        LIST_COMMANDS = "list_commands"
        REGISTRATION = "registration"
        EXECUTION_WITH_HANDLER = "execution_with_handler"
        ERROR_HANDLING = "error_handling"
        PERFORMANCE = "performance"
        MEMORY_USAGE = "memory_usage"
        INTEGRATION = "integration"
        SERVICE_PROPERTIES = "service_properties"
        LOGGING = "logging"
        CONCURRENT = "concurrent"
        VALIDATION = "validation"
        UNREGISTER = "unregister"
        CREATE_GROUP = "create_group"
        RUN_CLI = "run_cli"
        CLICK_GROUP = "click_group"
        WITH_ARGS = "with_args"
        WITHOUT_ARGS = "without_args"
        INVALID_STRUCTURE = "invalid_structure"
        GET_COMMANDS = "get_commands"
        CLEAR_COMMANDS = "clear_commands"
        LIST_EMPTY = "list_empty"

        CASES: Final[list[tuple[str, str, bool]]] = [
            (INITIALIZATION, "Commands initialization", True),
            (EXECUTION, "Commands execution", True),
            (LIST_COMMANDS, "List commands", True),
            (REGISTRATION, "Command registration", True),
            (EXECUTION_WITH_HANDLER, "Execute with handler", True),
            (ERROR_HANDLING, "Error handling", True),
            (PERFORMANCE, "Performance characteristics", True),
            (MEMORY_USAGE, "Memory usage", True),
            (INTEGRATION, "Integration with services", True),
            (SERVICE_PROPERTIES, "Service properties", True),
            (LOGGING, "Logging integration", True),
            (CONCURRENT, "Concurrent execution", True),
            (VALIDATION, "Command validation", True),
        ]


class ConfigModelIntegration:
    """Constants for config/model integration tests."""

    class Paths:
        """Path constants for config model tests."""

        INPUT: Final[str] = "/input"
        OUTPUT: Final[str] = "/output"
        CONFIG_INPUT: Final[str] = "/config/input"
        CONFIG_OUTPUT: Final[str] = "/config/output"
        ENV_INPUT: Final[str] = "/env/input"
        ENV_OUTPUT: Final[str] = "/env/output"
        ALIAS_INPUT: Final[str] = "/alias/input"
        ALIAS_OUTPUT: Final[str] = "/alias/output"
        CLI_INPUT: Final[str] = "/cli/input"
        APP_INPUT: Final[str] = "/app/input"
        APP_OUTPUT: Final[str] = "/app/output"
        DEFAULT_INPUT: Final[str] = "/default/input"
        DEFAULT_OUTPUT: Final[str] = "/default/output"
        DATA_INPUT: Final[str] = "data/input"
        DATA_OUTPUT: Final[str] = "data/output"
        TEST_INPUT: Final[str] = "/test/input"
        TEST_OUTPUT: Final[str] = "/test/output"

    class Timeouts:
        """Timeout constants for tests."""

        DEFAULT: Final[int] = 30
        CONFIG: Final[int] = 60
        MAX: Final[int] = 300
        MINIMUM: Final[int] = 0

    class Batch:
        """Batch size constants."""

        DEFAULT: Final[int] = 100
        CONFIG: Final[int] = 1000
        SMALL: Final[int] = 5

    class Flags:
        """Boolean flag constants."""

        VERBOSE_TRUE: Final[bool] = True
        VERBOSE_FALSE: Final[bool] = False
        DEBUG_TRUE: Final[bool] = True
        DEBUG_FALSE: Final[bool] = False
        ALLOW_NONE: Final[bool | None] = None

    class EnvVars:
        """Environment variable names for tests."""

        INPUT_DIR: Final[str] = "TEST_APP_INPUT_DIR"
        OUTPUT_DIR: Final[str] = "TEST_APP_OUTPUT_DIR"
        TIMEOUT_SECONDS: Final[str] = "TEST_APP_TIMEOUT_SECONDS"
        VERBOSE: Final[str] = "TEST_APP_VERBOSE"


class RailwayPatternExample:
    """Railway Pattern example test constants."""

    class TestData:
        """Test data for railway pattern examples."""

        # Simple key-value data
        SIMPLE: Final[dict[str, str | int]] = {"name": "test", "value": 42}
        KEY_VALUE: Final[dict[str, str | int]] = {"key": "value", "number": 42}
        STRATEGY: Final[dict[str, str]] = {"strategy": "recovery_test"}

        # Configuration data
        CONFIG: Final[dict[str, bool | int]] = {"debug": True, "timeout": 30}

        # Complex data
        ITEMS: Final[dict[str, list[dict[str, int]]]] = {
            "items": [{"id": 1}, {"id": 2}]
        }

    class FilePaths:
        """File path constants for railway pattern tests."""

        TEST_FILE: Final[str] = "test.json"
        CONFIG_FILE: Final[str] = "config.json"
        DATA_FILE: Final[str] = "data.json"
        OUTPUT_FILE: Final[str] = "output.json"
        VALIDATED_FILE: Final[str] = "validated.json"
        FALLBACK_FILE: Final[str] = "fallback.json"
        INVALID_PATH: Final[str] = "/nonexistent/directory/file.json"

    class Operations:
        """Operation types for railway pattern tests."""

        WRITE_READ: Final[str] = "write_read"
        WRITE_VALIDATE: Final[str] = "write_validate"
        ERROR_RECOVERY: Final[str] = "error_recovery"
        MULTI_STEP: Final[str] = "multi_step"


class TestVersions:
    """Version module test constants."""

    class Formats:
        """Version format constants."""

        MIN_VERSION_LENGTH: Final[int] = 5
        MAX_VERSION_LENGTH: Final[int] = 50
        MAJOR_MINOR_PATCH: Final[int] = 3
        SEMVER_PATTERN: Final[str] = r"^\d+\.\d+\.\d+(?:-[\w\.]+)?(?:\+[\w\.]+)?$"

    class Examples:
        """Example version strings."""

        VALID_SEMVER: Final[str] = "1.0.0"
        VALID_SEMVER_COMPLEX: Final[str] = "2.1.3-alpha"
        INVALID_NO_DOTS: Final[str] = "100"
        INVALID_TOO_FEW_PARTS: Final[str] = "1.2"
        INVALID_NON_NUMERIC: Final[str] = "a.b.c"
        INVALID_EMPTY: Final[str] = ""

    class InfoTuples:
        """Example version info tuples."""

        VALID_TUPLE: Final[tuple[int, int, int]] = (1, 0, 0)
        VALID_COMPLEX_TUPLE: Final[tuple[int, int, str]] = (2, 1, "3-alpha")
        SHORT_TUPLE: Final[tuple[int, int]] = (1, 0)
        EMPTY_TUPLE: Final[tuple[()]] = ()

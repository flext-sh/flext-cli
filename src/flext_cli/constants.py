"""FLEXT CLI constants."""

from __future__ import annotations

import typing
from collections.abc import Callable, Mapping
from enum import StrEnum
from typing import Literal

from flext_core import FlextConstants


class FlextCliConstants(FlextConstants):
    """Constants for Flext CLI."""

    class Cli:
        """CLI related constants."""

        type EntityTypeLiteral = Literal["command", "group"]
        type OutputFormatLiteral = Literal["json", "yaml", "csv", "table", "plain"]

        class Project:
            """Project constants."""

            NAME = "flext-cli"

        class Paths:
            """Path constants."""

            FLEXT_DIR_NAME, AUTH_DIR_NAME, TOKEN_FILE_NAME, REFRESH_TOKEN_FILE_NAME = (
                ".flext",
                "auth",
                "token.json",
                "refresh_token.json",
            )

        class ValidationMappings:
            """Validation mappings."""

            OUTPUT_FORMAT_SET = frozenset({"json", "yaml", "csv", "table", "plain"})
            COMMAND_STATUS_SET = frozenset({
                "pending",
                "running",
                "completed",
                "failed",
                "cancelled",
            })

        class ValidationLists:
            """Validation lists."""

            OUTPUT_FORMATS: typing.ClassVar[list[str]] = [
                "json",
                "yaml",
                "csv",
                "table",
                "plain",
            ]
            COMMAND_STATUSES: typing.ClassVar[list[str]] = [
                "pending",
                "running",
                "completed",
                "failed",
                "cancelled",
            ]
            SESSION_STATUSES: typing.ClassVar[list[str]] = [
                "active",
                "completed",
                "terminated",
            ]
            DEBUG_LEVELS: typing.ClassVar[list[str]] = [
                "DEBUG",
                "INFO",
                "WARNING",
                "ERROR",
                "CRITICAL",
            ]

        OUTPUT_FORMATS_LIST = ValidationLists.OUTPUT_FORMATS
        COMMAND_STATUSES_LIST = ValidationLists.COMMAND_STATUSES
        DEBUG_LEVELS_LIST = ValidationLists.DEBUG_LEVELS

        class CommandStatus(StrEnum):
            """Command status enum."""

            PENDING, RUNNING, COMPLETED, FAILED, CANCELLED = (
                "pending",
                "running",
                "completed",
                "failed",
                "cancelled",
            )

        class SessionStatus(StrEnum):
            """Session status enum."""

            ACTIVE, COMPLETED, TERMINATED = ("active", "completed", "terminated")

        class OutputFormats(StrEnum):
            """Output formats enum."""

            JSON, YAML, CSV, TABLE, PLAIN = ("json", "yaml", "csv", "table", "plain")

        class MessageTypes(StrEnum):
            """Message types enum."""

            INFO, ERROR, WARNING, SUCCESS = ("info", "error", "warning", "success")

        MESSAGE_TYPES_LIST: typing.ClassVar[list[str]] = [
            MessageTypes.INFO.value,
            MessageTypes.ERROR.value,
            MessageTypes.WARNING.value,
            MessageTypes.SUCCESS.value,
        ]

        class LogVerbosity(StrEnum):
            """Log verbosity enum."""

            COMPACT, DETAILED, FULL = ("compact", "detailed", "full")

        class ServerType(StrEnum):
            """Server type enum."""

            RFC = "rfc"

        class EntityType(StrEnum):
            """Entity type enum."""

            COMMAND, GROUP = ("command", "group")

        class ServiceStatus(StrEnum):
            """Service status enum."""

            OPERATIONAL, AVAILABLE, HEALTHY, CONNECTED = (
                "operational",
                "available",
                "healthy",
                "connected",
            )

        class Settings:
            """Settings constants."""

            class LogLevel(StrEnum):
                """Log level enum."""

                DEBUG, INFO, WARNING, ERROR, CRITICAL = (
                    "DEBUG",
                    "INFO",
                    "WARNING",
                    "ERROR",
                    "CRITICAL",
                )

        class Logging:
            """Logging constants."""

            CONSOLE_ENABLED = FlextConstants.Logging.CONSOLE_ENABLED

        class Utilities:
            """Utility constants."""

            DEFAULT_ENCODING = FlextConstants.Utilities.DEFAULT_ENCODING

        class Terminal:
            """Terminal constants."""

            WIDTH_NARROW, WIDTH_MEDIUM = (80, 120)

        class ExitCodes:
            """Exit code constants."""

            FAILURE = 1

        class CliDefaults:
            """Default CLI constants."""

            DEFAULT_PRIORITY, DEFAULT_APP_NAME, DEFAULT_VERSION = (
                999,
                "flext-cli",
                "2.0.0",
            )
            DEFAULT_PROFILE, DEFAULT_MAX_WIDTH = ("default", 120)
            DEFAULT_NO_COLOR, DEFAULT_VERBOSE, DEFAULT_QUIET, DEFAULT_INTERACTIVE = (
                False,
                False,
                False,
                True,
            )

        class CliGlobalDefaults:
            """Global default CLI constants."""

            DEFAULT_VERSION_STRING, DEFAULT_SERVICE_NAME = ("2.0.0", "flext-cli-config")
            DEFAULT_VERBOSITY, QUIET_VERBOSITY, NORMAL_VERBOSITY = (
                "verbose",
                "quiet",
                "normal",
            )

        class Services:
            """Service constants."""

            OUTPUT, FORMATTERS = ("output", "formatters")

        class HTTP:
            """HTTP constants."""

            MAX_RETRIES = 3

        class TIMEOUTS:
            """Timeout constants."""

            DEFAULT = FlextConstants.Network.DEFAULT_TIMEOUT

        FLEXT_CLI, TRACE, CLI_VERSION = ("flext-cli", "trace", "2.0.0")

        class CmdMessages:
            """Command messages."""

            DEFAULT_PAUSE_MESSAGE = "Press Enter to continue..."
            SUBDIR_EXISTS, SUBDIR_MISSING = (
                "{symbol} {subdir} directory exists",
                "{symbol} {subdir} directory missing",
            )
            CONFIG_SAVED, CONFIG_EDIT_COMPLETED_LOG = (
                "Configuration saved: {key} = {value}",
                "Configuration edit completed",
            )

        class ServiceMessages:
            """Service messages."""

            CONFIG_LOADED_SUCCESSFULLY = "Configuration loaded successfully. Use set_config_value to modify specific values."
            FLEXT_CLI_DEBUG_OPERATIONAL = "FlextCliDebug service operational"

        class LogMessages:
            """Log messages."""

            CLI_CONFIG_UPDATED = "CLI configuration updated successfully"
            PROFILE_CREATED = "Profile '{name}' created successfully"
            SESSION_STARTED, SESSION_ENDED = (
                "CLI session started successfully",
                "CLI session ended successfully",
            )
            CONFIG_DISPLAYED = "Configuration displayed"
            CONFIG_VALIDATION_RESULTS = "Config validation results: {results}"
            CONFIG_EDIT_COMPLETED = "Configuration edit completed successfully"

        class ErrorMessages:
            """Error messages."""

            INVALID_CREDENTIALS = (
                "Invalid credentials: missing token or username/password"
            )
            COMMAND_NAME_EMPTY, COMMAND_NOT_FOUND = (
                "Command name must be a non-empty string",
                "Command '{name}' not found",
            )
            INVALID_COMMAND_TYPE = "Invalid command definition type for '{name}'"
            COMMAND_RETRIEVAL_FAILED, COMMAND_EXECUTION_FAILED = (
                "Command retrieval failed: {error}",
                "Command execution failed: {error}",
            )
            COMMAND_LISTING_FAILED, COMMAND_REGISTRATION_FAILED = (
                "Command listing failed: {error}",
                "Command registration failed: {error}",
            )
            CONFIG_NOT_DICT, CONFIG_NOT_INITIALIZED = (
                "Configuration must be a valid dictionary",
                "Internal configuration is not initialized",
            )
            CONFIG_UPDATE_FAILED, CONFIG_RETRIEVAL_FAILED, CONFIG_VALIDATION_FAILED = (
                "Configuration update failed: {error}",
                "Configuration retrieval failed: {error}",
                "Config validation failed: {error}",
            )
            PROFILE_NAME_EMPTY, PROFILE_CONFIG_NOT_DICT, PROFILE_CREATION_FAILED = (
                "Profile name must be a non-empty string",
                "Profile config must be a valid dictionary",
                "Profile creation failed: {error}",
            )
            SESSION_ALREADY_ACTIVE, NO_ACTIVE_SESSION = (
                "Session is already active",
                "No active session to end",
            )
            SESSION_START_FAILED, SESSION_END_FAILED = (
                "Session start failed: {error}",
                "Session end failed: {error}",
            )
            TEXT_FILE_READ_FAILED, TEXT_FILE_WRITE_FAILED, FILE_COPY_FAILED = (
                "Text file read failed: {error}",
                "Text file write failed: {error}",
                "File copy failed: {error}",
            )
            JSON_WRITE_FAILED, YAML_WRITE_FAILED = (
                "JSON write failed: {error}",
                "YAML write failed: {error}",
            )
            TOKEN_SAVE_FAILED, TOKEN_LOAD_FAILED = (
                "Failed to save token: {error}",
                "Failed to load token: {error}",
            )
            TOKEN_FILE_NOT_FOUND, TOKEN_FILE_EMPTY = (
                "Token file does not exist",
                "Token file is empty",
            )
            NO_DATA_PROVIDED = "No data provided for table"
            TABLE_FORMAT_REQUIRED_DICT = (
                "Table format requires dict[str, t.JsonValue] or list of dicts"
            )
            TABLE_HEADERS_MUST_BE_LIST = (
                "Table headers must be a list for list of dicts data"
            )
            UNSUPPORTED_FORMAT_TYPE = "Unsupported format type: {format_type}"
            CREATE_FORMATTER_FAILED, CREATE_RICH_TABLE_FAILED = (
                "Failed to create formatter: {error}",
                "Failed to create Rich table: {error}",
            )
            CANNOT_ACCESS_CONFIG_DIR, INVALID_OUTPUT_FORMAT = (
                "Cannot access config directory {config_dir}: {error}",
                "Invalid output format: {format}",
            )
            CLI_ARGS_UPDATE_FAILED, CONFIG_LOAD_FAILED_MSG, CONFIG_SAVE_FAILED_MSG = (
                "CLI args update failed: {error}",
                "Config load failed: {error}",
                "Config save failed: {error}",
            )
            CLI_EXECUTION_ERROR = "CLI execution error: {error}"
            INTERACTIVE_MODE_DISABLED = (
                "Interactive mode disabled and no default provided"
            )
            INTERACTIVE_MODE_DISABLED_CHOICE = (
                "Interactive mode disabled and no valid default provided"
            )
            INTERACTIVE_MODE_DISABLED_PASSWORD = (
                "Interactive mode disabled for password input"
            )
            DEFAULT_PATTERN_MISMATCH = (
                "Default value does not match required pattern: {pattern}"
            )
            INPUT_PATTERN_MISMATCH = "Input does not match required pattern: {pattern}"
            TEXT_PROMPT_FAILED, CONFIRMATION_PROMPT_FAILED = (
                "Text prompt failed: {error}",
                "Confirmation prompt failed: {error}",
            )
            NO_CHOICES_PROVIDED, INVALID_CHOICE, CHOICE_PROMPT_FAILED = (
                "No choices provided",
                "Invalid choice: {selected}",
                "Choice prompt failed: {error}",
            )
            PASSWORD_PROMPT_FAILED, PASSWORD_TOO_SHORT_MIN, HISTORY_CLEAR_FAILED = (
                "Password prompt failed: {error}",
                "Password must be at least {min_length} characters",
                "History clear failed: {error}",
            )
            (
                CONFIG_PATHS_FAILED,
                CONFIG_INFO_FAILED,
                EDIT_CONFIG_FAILED,
                SET_CONFIG_FAILED,
            ) = (
                "Config paths failed: {error}",
                "Config info failed: {error}",
                "Edit config failed: {error}",
                "Set config failed: {error}",
            )
            UNSUPPORTED_FORMAT, USER_ABORTED_CONFIRMATION, USER_ABORTED_PROMPT = (
                "Unsupported format: {format}",
                "User aborted confirmation: {error}",
                "User aborted prompt: {error}",
            )
            FAILED_CLEAR_CREDENTIALS = "Failed to clear credentials: {error}"
            FILESYSTEM_VALIDATION_FAILED, CANNOT_WRITE_CURRENT_DIR = (
                "Filesystem validation failed: {error}",
                "Cannot write to current directory: {error}",
            )
            FORMAT_DETECTION_FAILED = "Format detection failed"
            CONFIG_FILE_NOT_FOUND = "Configuration file not found: {file}"
            UNSUPPORTED_CONFIG_FORMAT = (
                "Unsupported configuration file format: {suffix}"
            )
            FAILED_LOAD_CONFIG_FROM_FILE = (
                "Failed to load configuration from {file}: {error}"
            )
            INVALID_VALUE_FOR_FIELD, VALIDATION_ERRORS = (
                "Invalid value for {field}: {error}",
                "Validation errors: {errors}",
            )

        class DictKeys:
            """Dictionary keys."""

            ARGS, COMMAND, STATUS, CONTEXT, TIMESTAMP = (
                "args",
                "command",
                "status",
                "context",
                "timestamp",
            )
            SERVICE, MESSAGE, TIMEOUT, KEY, VALUE = (
                "service",
                "message",
                "timeout",
                "key",
                "value",
            )
            TOKEN, USERNAME, PASSWORD = ("token", "username", "password")
            CONFIG, PROFILES, CONFIG_DIR = ("config", "profiles", "config_dir")
            CONFIG_EXISTS, CONFIG_READABLE, CONFIG_WRITABLE = (
                "config_exists",
                "config_readable",
                "config_writable",
            )
            CONFIG_FILE, CONFIG_DATA = ("config_file", "config_data")

        class Subdirectories:
            """Subdirectory constants."""

            CACHE, LOGS, REFRESH_TOKEN = ("cache", "logs", "refresh_token")
            STANDARD_SUBDIRS: typing.ClassVar[list[str]] = [CACHE, LOGS]

        class Symbols:
            """Symbol constants."""

            SUCCESS_MARK, FAILURE_MARK = ("✓", "✗")
            ERROR_PREFIX, SUCCESS_PREFIX = ("❌ Error:", "✅ Success:")

        class Styles:
            """Style constants."""

            BLUE, BOLD_GREEN, BOLD_RED, BOLD_YELLOW = (
                "blue",
                "bold green",
                "bold red",
                "bold yellow",
            )

        class Emojis:
            """Emoji constants."""

            INFO, SUCCESS, ERROR, WARNING = ("i", "✅", "❌", "⚠️")

        class ConfigFiles:
            """Config file constants."""

            CLI_CONFIG_JSON = "cli_config.json"

        class EnvironmentConstants:
            """Environment constants."""

            PYTEST_CURRENT_TEST, PYTEST, UNDERSCORE, CI, CI_TRUE_VALUE = (
                "PYTEST_CURRENT_TEST",
                "pytest",
                "_",
                "CI",
                "true",
            )

        class ValidationLimits:
            """Validation limit constants."""

            MIN_MAX_WIDTH, MAX_MAX_WIDTH = (40, 200)

        class CliParamsRegistry:
            """CLI parameters registry."""

            SHORT_FLAG_VERBOSE, SHORT_FLAG_QUIET, SHORT_FLAG_DEBUG = ("v", "q", "d")
            SHORT_FLAG_TRACE, SHORT_FLAG_LOG_LEVEL = ("t", "L")
            SHORT_FLAG_OUTPUT_FORMAT, SHORT_FLAG_CONFIG_FILE = ("o", "c")
            PRIORITY_VERBOSE, PRIORITY_QUIET, PRIORITY_DEBUG = (1, 2, 3)
            PRIORITY_TRACE, PRIORITY_LOG_LEVEL, PRIORITY_LOG_FORMAT = (4, 5, 6)
            PRIORITY_OUTPUT_FORMAT, PRIORITY_NO_COLOR, PRIORITY_CONFIG_FILE = (7, 8, 9)
            KEY_SHORT, KEY_PRIORITY, KEY_CHOICES = ("short", "priority", "choices")
            KEY_CASE_SENSITIVE, KEY_FIELD_NAME_OVERRIDE = (
                "case_sensitive",
                "field_name_override",
            )
            LOG_FORMAT_OVERRIDE, CASE_INSENSITIVE = ("log-format", False)

        class CliParamsDefaults:
            """CLI parameters defaults."""

            VALID_LOG_FORMATS: typing.ClassVar[list[str]] = [
                "compact",
                "detailed",
                "full",
            ]
            VALID_OUTPUT_FORMATS: typing.ClassVar[list[str]] = [
                "table",
                "json",
                "yaml",
                "csv",
                "plain",
            ]

        class CliParamsErrorMessages:
            """CLI parameters error messages."""

            PARAMS_MANDATORY = "Common CLI parameters are mandatory and cannot be disabled. All CLI commands must support --verbose, --quiet, --debug, --log-level, etc."
            INVALID_LOG_LEVEL, CONFIGURE_LOGGER_FAILED = (
                "Invalid log level: {log_level}. Must be one of: {valid}",
                "Failed to configure logger: {error}",
            )

        class FileIODefaults:
            """File I/O default values."""

            ZIP_WRITE_MODE: Literal["w"] = "w"
            ZIP_READ_MODE: Literal["r"] = "r"
            GLOB_PATTERN_ALL, FORMAT_EXTENSIONS_KEY = ("*", "extensions")

        class FileExtensions:
            """File extension constants."""

            JSON = ".json"

        class FileSupportedFormats:
            """Supported file format constants."""

            JSON, YAML = ("json", "yaml")
            SUPPORTED_FORMATS: typing.ClassVar[list[str]] = [
                "json",
                "yaml",
                "yml",
                "txt",
                "csv",
            ]
            YAML_EXTENSIONS_SET: typing.ClassVar[set[str]] = {".yaml", ".yml"}

        class FileToolsDefaults:
            """File tools defaults."""

            EXTENSION_PREFIX, CHUNK_SIZE = (".", 4096)

        class FileDefaults:
            """File defaults."""

            DEFAULT_DATETIME_FORMATS: typing.ClassVar[list[str]] = [
                "%Y-%m-%d",
                "%Y-%m-%dT%H:%M:%S",
                "%Y-%m-%d %H:%M:%S",
            ]

        class FileErrorMessages:
            """File error messages."""

            BINARY_READ_FAILED, BINARY_WRITE_FAILED = (
                "Binary read failed: {error}",
                "Binary write failed: {error}",
            )
            CSV_READ_FAILED, CSV_WRITE_FAILED = (
                "CSV read failed: {error}",
                "CSV write failed: {error}",
            )
            FILE_DELETION_FAILED, FILE_MOVE_FAILED = (
                "File deletion failed: {error}",
                "File move failed: {error}",
            )
            DIRECTORY_CREATION_FAILED, DIRECTORY_CHECK_FAILED = (
                "Directory creation failed: {error}",
                "Directory check failed: {error}",
            )
            DIRECTORY_DELETION_FAILED, DIRECTORY_LISTING_FAILED = (
                "Directory deletion failed: {error}",
                "Directory listing failed: {error}",
            )
            HASH_CALCULATION_FAILED, HASH_CALCULATION_FAILED_NO_ERROR = (
                "Hash calculation failed: {error}",
                "Hash calculation failed",
            )
            TEMP_FILE_CREATION_FAILED, TEMP_DIR_CREATION_FAILED = (
                "Temp file creation failed: {error}",
                "Temp directory creation failed: {error}",
            )
            ZIP_CREATION_FAILED, ZIP_EXTRACTION_FAILED = (
                "Zip creation failed: {error}",
                "Zip extraction failed: {error}",
            )
            FILE_SEARCH_FAILED, CONTENT_SEARCH_FAILED = (
                "File search failed: {error}",
                "Content search failed: {error}",
            )
            JSON_LOAD_FAILED, YAML_LOAD_FAILED = (
                "JSON load failed: {error}",
                "YAML load failed: {error}",
            )
            UNSUPPORTED_FORMAT_EXTENSION = (
                "Unsupported file format: {extension}. Supported: .json, .yaml, .yml"
            )
            FILE_EXISTENCE_CHECK_FAILED, UNSUPPORTED_FORMAT_GENERIC = (
                "File existence check failed: {error}",
                "Unsupported file format: {extension}",
            )

        FILE_FORMATS: Mapping[str, Mapping[str, tuple[str, ...] | str]] = {
            "json": {"extensions": ("json",), "mime_type": "application/json"},
            "yaml": {"extensions": ("yaml", "yml"), "mime_type": "application/x-yaml"},
            "csv": {"extensions": ("csv",), "mime_type": "text/csv"},
            "tsv": {"extensions": ("tsv",), "mime_type": "text/tab-separated-values"},
            "toml": {"extensions": ("toml",), "mime_type": "application/toml"},
            "xml": {"extensions": ("xml",), "mime_type": "application/xml"},
        }
        FILE_FORMAT_EXTENSIONS: Mapping[str, tuple[str, ...]] = {
            "json": ("json",),
            "yaml": ("yaml", "yml"),
            "csv": ("csv",),
            "tsv": ("tsv",),
            "toml": ("toml",),
            "xml": ("xml",),
        }
        FILE_FORMAT_MIME_TYPES: Mapping[str, str] = {
            "json": "application/json",
            "yaml": "application/x-yaml",
            "csv": "text/csv",
            "tsv": "text/tab-separated-values",
            "toml": "application/toml",
            "xml": "application/xml",
        }
        SUPPORTED_FILE_FORMATS = frozenset({
            "json",
            "yaml",
            "csv",
            "tsv",
            "toml",
            "xml",
        })
        get_file_extensions: Callable[[str], tuple[str, ...] | None] = (
            FILE_FORMAT_EXTENSIONS.get
        )
        get_mime_type: Callable[[str], str | None] = FILE_FORMAT_MIME_TYPES.get
        validate_file_format: Callable[[str], bool] = (
            SUPPORTED_FILE_FORMATS.__contains__
        )

        class ContextDictKeys:
            """Context dictionary keys."""

            ID, CONTEXT_ID, COMMAND = ("id", "context_id", "command")
            CREATED_AT, TIMEOUT_SECONDS = ("created_at", "timeout_seconds")
            ARGUMENTS_COUNT, ARGUMENTS = ("arguments_count", "arguments")
            ENVIRONMENT_VARIABLES, ENVIRONMENT_VARIABLES_COUNT = (
                "environment_variables",
                "environment_variables_count",
            )
            WORKING_DIRECTORY, IS_ACTIVE = ("working_directory", "is_active")
            METADATA_KEYS, METADATA_COUNT, CONTEXT_EXECUTED = (
                "metadata_keys",
                "metadata_count",
                "context_executed",
            )

        class ContextErrorMessages:
            """Context error messages."""

            ARGUMENTS_NOT_INITIALIZED = (
                "Context arguments not initialized - cannot serialize"
            )
            ENV_VARS_NOT_INITIALIZED = (
                "Context environment variables not initialized - cannot serialize"
            )
            ENV_VAR_NOT_FOUND, ENV_VAR_RETRIEVAL_FAILED = (
                "Environment variable '{name}' not found",
                "Environment variable retrieval failed: {error}",
            )
            ENV_VAR_SETTING_FAILED = "Environment variable setting failed: {error}"
            ARGUMENT_ADDITION_FAILED, ARGUMENT_NOT_FOUND, ARGUMENT_REMOVAL_FAILED = (
                "Argument addition failed: {error}",
                "Argument '{argument}' not found",
                "Argument removal failed: {error}",
            )
            METADATA_SETTING_FAILED, METADATA_KEY_NOT_FOUND = (
                "Metadata setting failed: {error}",
                "Metadata key '{key}' not found",
            )

        class DebugDefaults:
            """Debug defaults."""

            SERVICE_NAME, MASKED_SENSITIVE = ("FlextCliDebug", "***MASKED***")
            SENSITIVE_KEYS: typing.ClassVar[set[str]] = {
                "password",
                "token",
                "secret",
                "key",
                "auth",
            }

        class DebugDictKeys:
            """Debug dictionary keys."""

            CONNECTIVITY, CHECK_ID, CHECKS_PASSED = (
                "connectivity",
                "check_id",
                "checks_passed",
            )
            OPERATION, ARGS_COUNT, TRACE_ID, DEBUG_ID = (
                "operation",
                "args_count",
                "trace_id",
                "debug_id",
            )
            SYSTEM_INFO, ENVIRONMENT_INFO, CONNECTIVITY_STATUS = (
                "system_info",
                "environment_info",
                "connectivity_status",
            )
            SYSTEM_ERROR, ENVIRONMENT_ERROR, PATHS_ERROR, DEBUG_ERROR = (
                "system_error",
                "environment_error",
                "paths_error",
                "debug_error",
            )

        class DebugErrorMessages:
            """Debug error messages."""

            ENVIRONMENT_INFO_FAILED = "Environment info failed: {error}"
            ENVIRONMENT_VALIDATION_FAILED = "Environment validation failed: {error}"
            CONNECTIVITY_TEST_FAILED, HEALTH_CHECK_FAILED = (
                "Connectivity test failed: {error}",
                "Health check failed: {error}",
            )
            TRACE_EXECUTION_FAILED, DEBUG_INFO_COLLECTION_FAILED = (
                "Trace execution failed: {error}",
                "Debug info collection failed: {error}",
            )
            SYSTEM_INFO_COLLECTION_FAILED, SYSTEM_PATHS_COLLECTION_FAILED = (
                "System info collection failed: {error}",
                "System paths collection failed: {error}",
            )
            COMPREHENSIVE_DEBUG_INFO_FAILED = (
                "Comprehensive debug info collection failed: {error}"
            )

        class CmdDefaults:
            """Command defaults."""

            SERVICE_NAME = "FlextCliCmd"

        class CmdErrorMessages:
            """Command error messages."""

            CONFIG_SAVE_FAILED, CONFIG_FILE_NOT_FOUND = (
                "Config save failed: {error}",
                "Configuration file not found: {path}",
            )
            CONFIG_LOAD_FAILED, CONFIG_NOT_DICT = (
                "Failed to load config: {error}",
                "Configuration data is not a valid dictionary",
            )
            CONFIG_KEY_NOT_FOUND = "Configuration key not found: {key}"
            GET_CONFIG_FAILED, SHOW_CONFIG_FAILED = (
                "Get config failed: {error}",
                "Show config failed: {error}",
            )
            CREATE_DEFAULT_CONFIG_FAILED = "Failed to create default config: {error}"

        class CoreServiceDefaults:
            """Core service defaults."""

            SESSION_DURATION_INIT, OPERATION_TYPE_CLI_COMMAND, CLI_COMMAND_PREFIX = (
                0,
                "cli_command",
                "cli_command_",
            )

        class PrivateAttributes:
            """Private attribute names."""

            SESSION_CONFIG, SESSION_START_TIME = (
                "_session_config",
                "_session_start_time",
            )

        class CoreServiceDictKeys:
            """Core service dictionary keys."""

            COMMANDS_REGISTERED, CONFIGURATION_SECTIONS = (
                "commands_registered",
                "configuration_sections",
            )
            SERVICE_READY, SESSION_ACTIVE, COMMANDS_COUNT = (
                "service_ready",
                "session_active",
                "commands_count",
            )

        class CoreServiceLogMessages:
            """Core service log messages."""

            SERVICE_INFO_COLLECTION_FAILED = "Service info collection failed"
            SESSION_STATS_COLLECTION_FAILED, SERVICE_EXECUTION_FAILED = (
                "Session statistics collection failed: {error}",
                "Service execution failed: {error}",
            )

        class MixinsFieldNames:
            """Mixin field names."""

            PIPELINE_STEP_NAME = "name"

        class MixinsValidationMessages:
            """Mixin validation messages."""

            FIELD_CANNOT_BE_EMPTY = "{field_name} cannot be empty"
            INVALID_ENUM_VALUE = "Invalid {field_name}. Valid values: {valid_values}"
            COMMAND_STATE_INVALID = "Cannot {operation}: command is in '{current_status}' state, requires '{required_status}'"
            SESSION_STATUS_INVALID = "Invalid session status '{current_status}'. Valid states: {valid_states}"
            PIPELINE_STEP_EMPTY, PIPELINE_STEP_NO_NAME, PIPELINE_STEP_NAME_EMPTY = (
                "Pipeline step must be a non-empty dictionary",
                "Pipeline step must have a 'name' field",
                "Pipeline step name cannot be empty",
            )
            CONFIG_MISSING_FIELDS = (
                "Missing required configuration fields: {missing_fields}"
            )

        class FormattersDefaults:
            """Formatter defaults."""

            (
                DEFAULT_SPINNER,
                DEFAULT_BORDER_STYLE,
                DEFAULT_REFRESH_RATE,
                TABLE_KEY_VALUE_COLUMNS,
            ) = ("dots", "blue", 4.0, 2)

        class FormattersErrorMessages:
            """Formatter error messages."""

            PRINT_FAILED, TABLE_CREATION_FAILED = (
                "Print failed: {error}",
                "Table creation failed: {error}",
            )
            TABLE_RENDERING_FAILED, PROGRESS_CREATION_FAILED = (
                "Table rendering failed: {error}",
                "Progress creation failed: {error}",
            )
            TREE_CREATION_FAILED, TREE_RENDERING_FAILED = (
                "Tree creation failed: {error}",
                "Tree rendering failed: {error}",
            )
            STATUS_CREATION_FAILED, LIVE_CREATION_FAILED = (
                "Status creation failed: {error}",
                "Live creation failed: {error}",
            )
            LAYOUT_CREATION_FAILED, PANEL_CREATION_FAILED = (
                "Layout creation failed: {error}",
                "Panel creation failed: {error}",
            )

        TABLE_FORMATS: typing.ClassVar[Mapping[str, str]] = {
            "plain": "Minimal formatting, no borders",
            "simple": "Simple ASCII borders",
            "grid": "Grid-style ASCII table",
            "fancy_grid": "Fancy grid with double lines",
            "pipe": "Markdown pipe table",
            "orgtbl": "Emacs org-mode table",
            "jira": "Jira markup table",
            "presto": "Presto SQL output",
            "pretty": "Pretty ASCII table",
            "psql": "PostgreSQL psql output",
            "rst": "reStructuredText grid",
            "mediawiki": "MediaWiki markup",
            "moinmoin": "MoinMoin markup",
            "youtrack": "YouTrack markup",
            "html": "HTML table",
            "unsafehtml": "Unsafe HTML table",
            "latex": "LaTeX table",
            "latex_raw": "Raw LaTeX table",
            "latex_booktabs": "LaTeX booktabs table",
            "latex_longtable": "LaTeX longtable",
            "textile": "Textile markup",
            "tsv": "Tab-separated values",
        }

        class TableFormats:
            """Table format constants."""

            KEYS, SIMPLE, GRID = ("keys", "simple", "grid")

        class TablesErrorMessages:
            """Table error messages."""

            TABLE_DATA_EMPTY = "Table data cannot be empty"
            INVALID_TABLE_FORMAT = (
                "Invalid table format: {table_format}. Available: {available_formats}"
            )
            TABLE_CREATION_FAILED = "Failed to create table: {error}"

        class OutputDefaults:
            """Output defaults."""

            JSON_INDENT, YAML_DEFAULT_FLOW_STYLE = (2, False)
            EMPTY_STYLE, DEFAULT_MESSAGE_TYPE, DEFAULT_FORMAT_TYPE = (
                "",
                "info",
                "table",
            )
            DEFAULT_TREE_TITLE, TREE_BRANCH_LIST_SUFFIX = ("Tree", " (list)")
            TEST_INVALID_KEY, WARNING_PREFIX, NEWLINE, TREE_VALUE_SEPARATOR = (
                "invalid",
                "Warning:",
                "\n",
                ": ",
            )

        class OutputFieldNames:
            """Output field names."""

            KEY, VALUE = ("Key", "Value")

        class OutputLogMessages:
            """Output log messages."""

            JSON_FORMAT_FAILED, YAML_FORMAT_FAILED = (
                "JSON formatting failed: {error}",
                "YAML formatting failed: {error}",
            )
            CSV_FORMAT_FAILED, TABLE_FORMAT_FAILED = (
                "CSV formatting failed: {error}",
                "Failed to format table: {error}",
            )

        class APIDefaults:
            """API defaults."""

            TOKEN_GENERATION_BYTES = 32
            TOKEN_DATA_TYPE_ERROR, TOKEN_VALUE_TYPE_ERROR = (
                "Token file must contain a JSON object",
                "Token must be a string",
            )
            APP_DESCRIPTION_SUFFIX, CONTAINER_REGISTRATION_KEY = (" CLI", "flext_cli")

        class UIDefaults:
            """UI defaults."""

            DEFAULT_PROMPT_SUFFIX = ": "

        class CliSessionDefaults:
            """CLI session defaults."""

            DEFAULT_USER_ID = ""

        class FormattingDefaults:
            """Formatting defaults."""

            MIN_FIELD_LENGTH = 1

        class ProgressDefaults:
            """Progress defaults."""

            REPORT_THRESHOLD = 10

        class PromptsDefaults:
            """Prompt defaults."""

            DEFAULT_PROCESSING_DESCRIPTION = "Processing..."
            CHOICE_PROMPT_SEPARATOR, CONFIRMATION_SUFFIX = ("\n", " (y/n)")
            PROMPT_INPUT_SEPARATOR, CONFIRMATION_YES_PROMPT, CONFIRMATION_NO_PROMPT = (
                ": ",
                " [Y/n]: ",
                " [y/N]: ",
            )
            CHOICE_PROMPT_PREFIX = "\nEnter your choice (1-{count}): "
            CHOICE_DISPLAY_FORMAT, SELECTION_PROMPT = (
                "Option {num}: {option}",
                "Selection prompt: {message}",
            )
            STATUS_FORMAT = "[{status}] {message}"
            SUCCESS_FORMAT, ERROR_FORMAT, WARNING_FORMAT, INFO_FORMAT = (
                "SUCCESS: {message}",
                "ERROR: {message}",
                "WARNING: {message}",
                "INFO: {message}",
            )
            PROGRESS_FORMAT = "  Progress: {progress:.1f}% ({current}/{total})"
            PROMPT_DEFAULT_FORMAT, PROMPT_LOG_FORMAT = (
                " (default: {default})",
                "User prompted: {message}, input: {input}",
            )
            CHOICE_LIST_FORMAT, PROMPT_SPACE_SUFFIX = ("{index}. {choice}", " ")
            DEFAULT_CHOICE_MESSAGE, CHOICE_HISTORY_FORMAT = (
                "Choose an option:",
                "{message}{separator}{options}",
            )

        class PromptsMessages:
            """Prompt messages."""

            USER_CANCELLED_CONFIRMATION, INPUT_STREAM_ENDED = (
                "User cancelled confirmation",
                "Input stream ended",
            )
            NO_OPTIONS_PROVIDED, USER_CANCELLED_SELECTION = (
                "No options provided",
                "User cancelled selection",
            )
            PROCESSING = "Processing {count} items: {description}"
            STARTING_PROGRESS, CREATED_PROGRESS = (
                "Starting progress: {description}",
                "Created progress: {description}",
            )
            PROGRESS_OPERATION, PROGRESS_COMPLETED = (
                "Progress operation: {description} ({count} items)",
                "Completed: {description}",
            )
            PROGRESS_COMPLETED_LOG = (
                "Progress completed: {description}, processed: {processed}"
            )
            USER_SELECTION_LOG = "User selected: {message}, choice: {choice}"

        class PromptsErrorMessages:
            """Prompt error messages."""

            PROMPT_FAILED, CONFIRMATION_FAILED, SELECTION_FAILED = (
                "Prompt failed: {error}",
                "Confirmation failed: {error}",
                "Selection failed: {error}",
            )
            CHOICE_REQUIRED = "Choice required. Available choices: {choices}"
            STATISTICS_COLLECTION_FAILED = "Statistics collection failed: {error}"
            PROMPT_SERVICE_EXECUTION_FAILED = "Prompt service execution failed: {error}"
            PRINT_STATUS_FAILED, PRINT_SUCCESS_FAILED = (
                "Print status failed: {error}",
                "Print success failed: {error}",
            )
            PRINT_ERROR_FAILED, PRINT_WARNING_FAILED, PRINT_INFO_FAILED = (
                "Print error failed: {error}",
                "Print warning failed: {error}",
                "Print info failed: {error}",
            )
            PROGRESS_CREATION_FAILED, PROGRESS_PROCESSING_FAILED = (
                "Progress creation failed: {error}",
                "Progress processing failed: {error}",
            )

        class Lists:
            """Lists constants."""

            LOG_LEVELS_LIST: typing.ClassVar[list[str]] = [
                "DEBUG",
                "INFO",
                "WARNING",
                "ERROR",
                "CRITICAL",
            ]


c = FlextCliConstants
__all__ = ["FlextCliConstants", "c"]

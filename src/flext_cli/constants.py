"""FLEXT CLI Constants - Centralized constants, enums, and literals.

Domain-specific constants extending flext-core standardization for CLI operations.
All literals, strings, numbers, enums, and configuration defaults centralized here.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from enum import StrEnum
from typing import Final, Literal

from flext_core import FlextConstants, FlextTypes

# Literal types moved to FlextCliConstants class - CRITICAL VIOLATION FIXED


class FlextCliConstants(FlextConstants):
    """CLI constants extending flext-core standardization for CLI domain.

    Centralizes all CLI-specific constants, enums, literals, and defaults
    without duplication or wrappers, using direct access patterns.
    """

    # Literal types - CRITICAL VIOLATION FIXED: Moved from module level
    CommandResultStatusLiteral = Literal["success", "failure", "error"]
    CliProjectTypeLiteral = Literal[
        "cli-tool",
        "console-app",
        "terminal-ui",
        "command-runner",
        "interactive-cli",
        "batch-processor",
        "cli-wrapper",
    ]

    # Project identification
    PROJECT_NAME: Final[str] = "flext-cli"

    # Directory and file names
    FLEXT_DIR_NAME: Final[str] = ".flext"
    AUTH_DIR_NAME: Final[str] = "auth"
    TOKEN_FILE_NAME: Final[str] = "token.json"
    REFRESH_TOKEN_FILE_NAME: Final[str] = "refresh_token.json"

    # Default paths
    DEFAULT_FLEXT_DIR: Final[str] = f"~/{FLEXT_DIR_NAME}"
    DEFAULT_TOKEN_PATH: Final[str] = f"{DEFAULT_FLEXT_DIR}/{TOKEN_FILE_NAME}"
    DEFAULT_REFRESH_TOKEN_PATH: Final[str] = (
        f"{DEFAULT_FLEXT_DIR}/{REFRESH_TOKEN_FILE_NAME}"
    )

    class CommandStatus(StrEnum):
        """Command execution status enum."""

        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"

    class SessionStatus(StrEnum):
        """Session execution status enum."""

        ACTIVE = "active"
        COMPLETED = "completed"
        TERMINATED = "terminated"

    class DebugLevel(StrEnum):
        """Debug information level enum."""

        DEBUG = "debug"
        INFO = "info"
        WARNING = "warning"
        ERROR = "error"
        CRITICAL = "critical"

    class ServiceStatus(StrEnum):
        """Service operational status enum."""

        OPERATIONAL = "operational"
        AVAILABLE = "available"
        DEGRADED = "degraded"
        ERROR = "error"
        HEALTHY = "healthy"
        CONNECTED = "connected"

    # Service status constants for direct access
    HEALTHY: Final[str] = ServiceStatus.HEALTHY.value
    OPERATIONAL: Final[str] = ServiceStatus.OPERATIONAL.value

    # Output formats - using FlextTypes.Output.OutputFormat Literal type
    # CLI adds "plain" format on top of standard formats
    class OutputFormats(StrEnum):
        """CLI output format enum - extends Flextstandard formats."""

        JSON = "json"  # Standard format
        YAML = "yaml"  # Standard format
        CSV = "csv"  # Standard format
        TABLE = "table"  # Standard format
        PLAIN = "plain"  # CLI-specific format

    # Terminal width thresholds for format selection
    TERMINAL_WIDTH_NARROW: Final[int] = 80
    TERMINAL_WIDTH_MEDIUM: Final[int] = 120

    # Error codes - CLI-specific strings following FlextConstants.Errors pattern
    class ErrorCodes(StrEnum):
        """CLI error codes following FlextConstants.Errors pattern.

        CLI-specific error codes with CLI_ prefix to distinguish from Flext
        Follows same categorization as FlextConstants.Errors without duplication.
        """

        # Standard error categories with CLI prefix
        CLI_ERROR = "CLI_ERROR"
        CLI_VALIDATION_ERROR = "CLI_VALIDATION_ERROR"
        CLI_CONFIGURATION_ERROR = "CLI_CONFIGURATION_ERROR"
        CLI_CONNECTION_ERROR = "CLI_CONNECTION_ERROR"
        CLI_AUTHENTICATION_ERROR = "CLI_AUTHENTICATION_ERROR"
        CLI_TIMEOUT_ERROR = "CLI_TIMEOUT_ERROR"

        # CLI-specific error codes
        COMMAND_ERROR = "CLI_COMMAND_ERROR"
        FORMAT_ERROR = "CLI_FORMAT_ERROR"

    class ExitCodes:
        """CLI exit codes."""

        SUCCESS: Final[int] = 0
        FAILURE: Final[int] = 1
        CONFIG_ERROR: Final[int] = 2
        COMMAND_ERROR: Final[int] = 3
        TIMEOUT_ERROR: Final[int] = 4
        AUTHENTICATION_ERROR: Final[int] = 5

    class CliDefaults:
        """CLI default values."""

        CONFIG_FILE: Final[str] = "config.json"
        MAX_WIDTH: Final[int] = 120
        DEFAULT_MAX_WIDTH: Final[int] = 120
        DEFAULT_PROFILE: Final[str] = "default"
        DEFAULT_OUTPUT_FORMAT: Final[str] = "table"
        DEFAULT_TIMEOUT: Final[int] = 30

        # Application defaults
        DEFAULT_APP_NAME: Final[str] = "flext-cli"
        DEFAULT_VERSION: Final[str] = "2.0.0"

        # Boolean flag defaults
        DEFAULT_NO_COLOR: Final[bool] = False
        DEFAULT_AUTO_REFRESH: Final[bool] = True
        DEFAULT_VERBOSE: Final[bool] = False
        DEFAULT_DEBUG: Final[bool] = False
        DEFAULT_QUIET: Final[bool] = False
        DEFAULT_INTERACTIVE: Final[bool] = True

        # Environment defaults
        DEFAULT_ENVIRONMENT: Final[str] = "development"

        # Log level defaults
        DEFAULT_LOG_LEVEL: Final[str] = "INFO"
        DEFAULT_CLI_LOG_LEVEL: Final[str] = "INFO"

        # Verbosity defaults
        DEFAULT_LOG_VERBOSITY: Final[str] = "detailed"
        DEFAULT_CLI_LOG_VERBOSITY: Final[str] = "detailed"

    class PipelineDefaults:
        """Pipeline and batch processing defaults."""

        MIN_STEP_TIMEOUT_SECONDS: Final[int] = 10
        MAX_BATCH_SIZE_PARALLEL: Final[int] = 100
        STEP_BASELINE_DURATION_SECONDS: Final[int] = 30
        RETRY_OVERHEAD_SECONDS: Final[int] = 10

    class NetworkDefaults:
        """Network-related defaults for CLI operations."""

        DEFAULT_HOST: Final[str] = "localhost"
        DEFAULT_PORT: Final[int] = 8080
        DEFAULT_API_URL: Final[str] = (
            f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}/api"
        )
        DEFAULT_TIMEOUT: Final[int] = 30
        DEFAULT_MAX_RETRIES: Final[int] = 3
        CONNECT_TIMEOUT: Final[int] = 10
        READ_TIMEOUT: Final[int] = 60

    class PhoneValidation:
        """Phone number validation constants."""

        MIN_INTERNATIONAL_DIGITS: Final[int] = 10
        MAX_INTERNATIONAL_DIGITS: Final[int] = 15
        US_PHONE_DIGITS: Final[int] = 10

    # Constant lists for validation and iteration
    OUTPUT_FORMATS_LIST: Final[FlextTypes.StringList] = [
        OutputFormats.JSON.value,
        OutputFormats.YAML.value,
        OutputFormats.CSV.value,
        OutputFormats.TABLE.value,
        OutputFormats.PLAIN.value,
    ]

    LOG_LEVELS_LIST: Final[FlextTypes.StringList] = [
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ]

    COMMAND_STATUSES_LIST: Final[FlextTypes.StringList] = [
        CommandStatus.PENDING.value,
        CommandStatus.RUNNING.value,
        CommandStatus.COMPLETED.value,
        CommandStatus.FAILED.value,
        CommandStatus.CANCELLED.value,
    ]

    SESSION_STATUSES_LIST: Final[FlextTypes.StringList] = [
        SessionStatus.ACTIVE.value,
        SessionStatus.COMPLETED.value,
        SessionStatus.TERMINATED.value,
    ]

    DEBUG_LEVELS_LIST: Final[FlextTypes.StringList] = [
        DebugLevel.DEBUG.value,
        DebugLevel.INFO.value,
        DebugLevel.WARNING.value,
        DebugLevel.ERROR.value,
        DebugLevel.CRITICAL.value,
    ]

    # Critical debug levels that require descriptive messages
    CRITICAL_DEBUG_LEVELS: Final[FlextTypes.StringList] = [
        DebugLevel.ERROR.value,
        DebugLevel.CRITICAL.value,
    ]

    CRITICAL_DEBUG_LEVELS_SET: Final[set[str]] = {
        DebugLevel.ERROR.value,
        DebugLevel.CRITICAL.value,
    }

    SERVICE_STATUSES_LIST: Final[FlextTypes.StringList] = [
        ServiceStatus.OPERATIONAL.value,
        ServiceStatus.AVAILABLE.value,
        ServiceStatus.DEGRADED.value,
        ServiceStatus.ERROR.value,
        ServiceStatus.HEALTHY.value,
        ServiceStatus.CONNECTED.value,
    ]

    ERROR_CODES_LIST: Final[FlextTypes.StringList] = [
        ErrorCodes.CLI_ERROR.value,
        ErrorCodes.CLI_VALIDATION_ERROR.value,
        ErrorCodes.CLI_CONFIGURATION_ERROR.value,
        ErrorCodes.CLI_CONNECTION_ERROR.value,
        ErrorCodes.CLI_AUTHENTICATION_ERROR.value,
        ErrorCodes.COMMAND_ERROR.value,
        ErrorCodes.CLI_TIMEOUT_ERROR.value,
        ErrorCodes.FORMAT_ERROR.value,
    ]

    class Commands:
        """CLI command name constants."""

        AUTH: Final[str] = "auth"
        CONFIG: Final[str] = "config"
        DEBUG: Final[str] = "debug"
        FORMAT: Final[str] = "format"
        EXPORT: Final[str] = "export"

    class CliCommandResult:
        """CLI command result type definitions."""

        # Core command result types
        CommandResultData = dict[str, FlextTypes.JsonValue]
        CommandResultStatus = Literal["success", "failure", "error"]
        CommandResultMetadata = dict[str, str | int | bool]

    class Shell:
        """Shell-specific constants."""

        # Built-in shell commands
        EXIT: Final[str] = "exit"
        QUIT: Final[str] = "quit"
        Q: Final[str] = "q"
        HISTORY: Final[str] = "history"
        CLEAR: Final[str] = "clear"
        HELP: Final[str] = "help"
        COMMANDS: Final[str] = "commands"
        SESSION: Final[str] = "session"

        # Shell command list
        BUILTIN_COMMANDS: Final[FlextTypes.StringList] = [
            EXIT,
            QUIT,
            Q,
            HISTORY,
            CLEAR,
            HELP,
            COMMANDS,
            SESSION,
        ]

        # Default prompt
        DEFAULT_PROMPT: Final[str] = "> "

    class Auth:
        """CLI authentication constants."""

        TOKEN_FILENAME: Final[str] = "token.json"
        CONFIG_FILENAME: Final[str] = "auth.json"
        MIN_USERNAME_LENGTH: Final[int] = 3
        MIN_PASSWORD_LENGTH: Final[int] = 6

    class Session:
        """CLI session constants."""

        DEFAULT_TIMEOUT: Final[int] = 3600
        MAX_COMMANDS: Final[int] = 1000

    class Services:
        """CLI service name constants."""

        API: Final[str] = "api"
        FORMATTER: Final[str] = "formatter"
        FORMATTERS: Final[str] = "formatters"  # Plural form for consistency
        AUTH: Final[str] = "auth"

    class Protocols:
        """CLI protocol constants."""

        HTTP: Final[str] = "http"
        HTTPS: Final[str] = "https"

    class HTTP:
        """HTTP-related constants."""

        DEFAULT_TIMEOUT: Final[int] = 30
        MAX_RETRIES: Final[int] = 3
        RETRY_DELAY: Final[int] = 1
        USER_AGENT: Final[str] = "FlextCLI/1.0"

    class HttpMethods(StrEnum):
        """HTTP method constants."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"

    HTTP_METHODS_LIST: Final[FlextTypes.StringList] = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "HEAD",
        "OPTIONS",
    ]

    class MessageTypes(StrEnum):
        """Message type constants for CLI output."""

        INFO = "info"
        ERROR = "error"
        WARNING = "warning"
        SUCCESS = "success"
        DEBUG = "debug"

    MESSAGE_TYPES_LIST: Final[FlextTypes.StringList] = [
        MessageTypes.INFO.value,
        MessageTypes.ERROR.value,
        MessageTypes.WARNING.value,
        MessageTypes.SUCCESS.value,
        MessageTypes.DEBUG.value,
    ]

    class TIMEOUTS:
        """Timeout constants."""

        DEFAULT: Final[int] = 30
        CONNECTION: Final[int] = 10
        READ: Final[int] = 30
        WRITE: Final[int] = 30
        COMMAND: Final[int] = 300

    # Service names
    FLEXT_CLI: Final[str] = "flext-cli"

    # User IDs for testing
    USER1: Final[str] = "user1"
    USER2: Final[str] = "user2"

    # Table column names
    VALUE: Final[str] = "Value"

    # Additional status constants
    TRACE: Final[str] = "trace"

    # Default values
    DEFAULT: Final[str] = "default"
    TABLE: Final[str] = "table"

    # Directory labels
    HOME: Final[str] = "Home"
    CONFIG: Final[str] = "Config"
    CACHE: Final[str] = "Cache"
    LOGS: Final[str] = "Logs"

    # MIME types
    APPLICATION_JSON: Final[str] = "application/json"
    APPLICATION_YAML: Final[str] = "application/x-yaml"
    TEXT_CSV: Final[str] = "text/csv"
    TEXT_TSV: Final[str] = "text/tab-separated-values"

    # Format names
    TSV: Final[str] = "tsv"

    # File formats configuration
    FILE_FORMATS: Final[dict[str, dict[str, FlextTypes.StringList]]] = {
        "json": {"extensions": ["json"]},
        "yaml": {"extensions": ["yaml", "yml"]},
        "csv": {"extensions": ["csv"]},
        "tsv": {"extensions": ["tsv"]},
        "toml": {"extensions": ["toml"]},
        "xml": {"extensions": ["xml"]},
    }

    # Service names
    FLEXT_CLI_FILE_TOOLS: Final[str] = "flext-cli-file-tools"

    # Version constants
    CLI_VERSION: Final[str] = "2.0.0"

    class ErrorMessages:
        """Centralized error message templates for CLI operations."""

        # Authentication errors
        USERNAME_PASSWORD_REQUIRED: Final[str] = "Username and password are required"
        USERNAME_TOO_SHORT: Final[str] = "Username must be at least 3 characters"
        PASSWORD_TOO_SHORT: Final[str] = "Password must be at least 6 characters"
        TOKEN_EMPTY: Final[str] = "Token cannot be empty"
        TOKEN_FILE_NOT_FOUND: Final[str] = "Token file does not exist"
        TOKEN_FILE_EMPTY: Final[str] = "Token file is empty"
        INVALID_CREDENTIALS: Final[str] = (
            "Invalid credentials: missing token or username/password"
        )

        # Command errors
        COMMAND_NAME_EMPTY: Final[str] = "Command name must be a non-empty string"
        COMMAND_NOT_FOUND: Final[str] = "Command '{name}' not found"
        INVALID_COMMAND_TYPE: Final[str] = (
            "Invalid command definition type for '{name}'"
        )
        COMMAND_RETRIEVAL_FAILED: Final[str] = "Command retrieval failed: {error}"
        COMMAND_EXECUTION_FAILED: Final[str] = "Command execution failed: {error}"
        COMMAND_LISTING_FAILED: Final[str] = "Command listing failed: {error}"

        # Configuration errors
        CONFIG_NOT_DICT: Final[str] = "Configuration must be a valid dictionary"
        CONFIG_NOT_INITIALIZED: Final[str] = "Internal configuration is not initialized"
        CONFIG_UPDATE_FAILED: Final[str] = "Configuration update failed: {error}"
        CONFIG_RETRIEVAL_FAILED: Final[str] = "Configuration retrieval failed: {error}"
        CONFIG_DATA_NONE: Final[str] = "Configuration data cannot be None"
        CONFIG_DATA_NOT_DICT: Final[str] = "Configuration data must be a dictionary"
        CONFIG_VALIDATION_FAILED: Final[str] = "Config validation failed: {error}"
        INVALID_PROFILES_STRUCTURE: Final[str] = (
            "Invalid profiles configuration structure"
        )

        # Profile errors
        PROFILE_NAME_EMPTY: Final[str] = "Profile name must be a non-empty string"
        PROFILE_CONFIG_NOT_DICT: Final[str] = (
            "Profile config must be a valid dictionary"
        )
        PROFILE_CREATION_FAILED: Final[str] = "Profile creation failed: {error}"

        # Session errors
        SESSION_ALREADY_ACTIVE: Final[str] = "Session is already active"
        NO_ACTIVE_SESSION: Final[str] = "No active session to end"
        SESSION_START_FAILED: Final[str] = "Session start failed: {error}"
        SESSION_END_FAILED: Final[str] = "Session end failed: {error}"

        # File operation errors
        TEXT_FILE_READ_FAILED: Final[str] = "Text file read failed: {error}"
        TEXT_FILE_WRITE_FAILED: Final[str] = "Text file write failed: {error}"
        FILE_COPY_FAILED: Final[str] = "File copy failed: {error}"
        JSON_WRITE_FAILED: Final[str] = "JSON write failed: {error}"
        TOKEN_SAVE_FAILED: Final[str] = "Failed to save token: {error}"
        TOKEN_LOAD_FAILED: Final[str] = "Failed to load token: {error}"
        TOKEN_PATHS_FAILED: Final[str] = "Token paths failed: {error}"

        # Validation errors
        NO_DATA_PROVIDED: Final[str] = "No data provided for table"
        TABLE_FORMAT_REQUIRED_DICT: Final[str] = (
            "Table format requires dict[str, object] or list of dicts"
        )
        TABLE_HEADERS_MUST_BE_LIST: Final[str] = (
            "Table headers must be a list for list of dicts data"
        )
        UNSUPPORTED_FORMAT_TYPE: Final[str] = "Unsupported format type: {format_type}"
        CREATE_FORMATTER_FAILED: Final[str] = "Failed to create formatter: {error}"
        CREATE_RICH_TABLE_FAILED: Final[str] = "Failed to create Rich table: {error}"

        # Prompt errors
        NO_CHOICES_PROVIDED: Final[str] = "No choices provided"
        INVALID_CHOICE: Final[str] = "Invalid choice: {selected}"
        TEXT_PROMPT_FAILED: Final[str] = "Text prompt failed: {error}"
        CONFIRMATION_PROMPT_FAILED: Final[str] = "Confirmation prompt failed: {error}"
        CHOICE_PROMPT_FAILED: Final[str] = "Choice prompt failed: {error}"
        PASSWORD_PROMPT_FAILED: Final[str] = "Password prompt failed: {error}"
        INTERACTIVE_MODE_DISABLED: Final[str] = (
            "Interactive mode disabled and no default provided"
        )
        INTERACTIVE_MODE_DISABLED_CHOICE: Final[str] = (
            "Interactive mode disabled and no valid default provided"
        )
        INTERACTIVE_MODE_DISABLED_PASSWORD: Final[str] = (
            "Interactive mode disabled for password input"
        )
        DEFAULT_PATTERN_MISMATCH: Final[str] = (
            "Default value does not match required pattern: {pattern}"
        )
        INPUT_PATTERN_MISMATCH: Final[str] = (
            "Input does not match required pattern: {pattern}"
        )
        PASSWORD_TOO_SHORT_MIN: Final[str] = (
            "Password must be at least {min_length} characters"
        )
        HISTORY_CLEAR_FAILED: Final[str] = "History clear failed: {error}"

        # Config operation errors
        SHOW_CONFIG_FAILED: Final[str] = "Show config failed: {error}"
        EDIT_CONFIG_FAILED: Final[str] = "Edit config failed: {error}"
        CONFIG_PATHS_FAILED: Final[str] = "Config paths failed: {error}"
        CONFIG_INFO_FAILED: Final[str] = "Config info failed: {error}"
        CREATE_DEFAULT_CONFIG_FAILED: Final[str] = (
            "Failed to create default config: {error}"
        )
        LOAD_CONFIG_FAILED: Final[str] = "Failed to load config: {error}"
        SAVE_CONFIG_FAILED: Final[str] = "Save configuration failed: {error}"

        # Additional authentication errors
        API_KEY_EMPTY: Final[str] = "API key cannot be empty"
        CERTIFICATE_NOT_EXIST: Final[str] = "Certificate file does not exist"
        CERTIFICATE_AUTH_FAILED: Final[str] = (
            "Certificate authentication failed: {error}"
        )
        CERTIFICATE_INVALID_FORMAT: Final[str] = (
            "Certificate has invalid format: {error}"
        )
        CERTIFICATE_NOT_YET_VALID: Final[str] = "Certificate is not yet valid"
        CERTIFICATE_EXPIRED: Final[str] = "Certificate has expired"
        CERTIFICATE_MISSING_SUBJECT: Final[str] = (
            "Certificate is missing required subject information"
        )
        HASHED_PASSWORD_EMPTY: Final[str] = "Hashed password cannot be empty"
        PASSWORD_EMPTY: Final[str] = "Password cannot be empty"
        PERMISSION_EMPTY: Final[str] = "Permission cannot be empty"
        SESSION_ID_EMPTY: Final[str] = "Session ID cannot be empty"
        USER_ID_EMPTY: Final[str] = "User ID cannot be empty"
        USER_NOT_FOUND: Final[str] = "User not found"
        INVALID_TOKEN: Final[str] = "Invalid token"
        FAILED_STORE_CREDENTIALS: Final[str] = "Failed to store credentials: {error}"
        FAILED_HASH_PASSWORD: Final[str] = "Failed to hash password: {error}"
        FAILED_GENERATE_TOKEN: Final[str] = "Failed to generate token: {error}"
        FAILED_GENERATE_SALT: Final[str] = "Failed to generate salt: {error}"
        FAILED_CLEAR_CREDENTIALS: Final[str] = "Failed to clear credentials: {error}"
        FAILED_PASSWORD_VERIFICATION: Final[str] = (
            "Password verification failed: {error}"
        )

        # Additional config/CLI errors
        CLI_CONFIG_FAILED: Final[str] = "CLI configuration failed: {error}"
        BUSINESS_RULES_VALIDATION_FAILED: Final[str] = (
            "Business rules validation failed: {error}"
        )
        CANNOT_ACCESS_CONFIG_DIR: Final[str] = (
            "Cannot access config directory {config_dir}: {error}"
        )
        INVALID_OUTPUT_FORMAT: Final[str] = "Invalid output format: {format}"
        PROFILE_NAME_EMPTY_MSG: Final[str] = "Profile name cannot be empty"
        INVALID_API_URL_FORMAT: Final[str] = (
            "Invalid API URL format: {url}. Must start with http:// or https://"
        )
        INVALID_LOG_LEVEL: Final[str] = (
            "Invalid log level: {level}. Must be one of: {valid_levels}"
        )
        INVALID_LOG_VERBOSITY: Final[str] = (
            "Invalid log verbosity: {verbosity}. Must be one of: {valid_verbosity}"
        )
        CLI_ARGS_UPDATE_FAILED: Final[str] = "CLI args update failed: {error}"
        ENV_MERGE_FAILED: Final[str] = "Environment merge failed: {error}"
        UNKNOWN_CONFIG_FIELD: Final[str] = "Unknown config field: {field}"
        INVALID_VALUE_FOR_FIELD: Final[str] = "Invalid value for {field}: {error}"
        VALIDATION_ERRORS: Final[str] = "Validation errors: {errors}"
        CONFIG_LOAD_FAILED_MSG: Final[str] = "Config load failed: {error}"
        CONFIG_SAVE_FAILED_MSG: Final[str] = "Config save failed: {error}"

        # File and path errors
        CONFIG_FILE_NOT_FOUND: Final[str] = "Configuration file not found: {file}"
        UNSUPPORTED_CONFIG_FORMAT: Final[str] = (
            "Unsupported configuration file format: {suffix}"
        )
        FAILED_LOAD_CONFIG_FROM_FILE: Final[str] = (
            "Failed to load configuration from {file}: {error}"
        )
        SAVE_FAILED: Final[str] = "Save failed: {error}"

        # Additional prompt/CLI errors
        USER_ABORTED_CONFIRMATION: Final[str] = "User aborted confirmation: {error}"
        USER_ABORTED_PROMPT: Final[str] = "User aborted prompt: {error}"

        # Command errors (additional)
        SET_CONFIG_FAILED: Final[str] = "Set config failed: {error}"
        COMMAND_REGISTRATION_FAILED: Final[str] = "Command registration failed: {error}"
        COMMAND_UNREGISTRATION_FAILED: Final[str] = (
            "Command unregistration failed: {error}"
        )
        CLI_EXECUTION_FAILED: Final[str] = "CLI execution failed"
        CLI_EXECUTION_ERROR: Final[str] = "CLI execution failed: {error}"
        GROUP_CREATION_FAILED: Final[str] = "Group creation failed: {error}"
        LOAD_FAILED: Final[str] = "Load failed: {error}"
        INITIALIZE_FAILED: Final[str] = "Initialize failed: {error}"

        # Context and model errors
        CONTEXT_VALIDATION_FAILED: Final[str] = "Context validation failed: {error}"
        MODEL_ATTACHMENT_FAILED: Final[str] = "Model attachment failed: {error}"
        MODEL_EXTRACTION_FAILED: Final[str] = "Model extraction failed: {error}"

        # Plugin errors
        PLUGIN_DIR_NOT_EXIST: Final[str] = "Plugin directory does not exist: {dir}"
        PLUGIN_PATH_NOT_DIR: Final[str] = "Plugin path is not a directory: {path}"
        FAILED_DISCOVER_PLUGINS: Final[str] = "Failed to discover plugins: {error}"
        PLUGIN_CLASS_NOT_FOUND: Final[str] = (
            "Plugin class '{class_name}' not found in module"
        )
        NO_PLUGIN_CLASS_FOUND: Final[str] = "No plugin class found in module '{module}'"
        FAILED_LOAD_PLUGIN: Final[str] = "Failed to load plugin '{module}': {error}"
        PLUGIN_INIT_FAILED: Final[str] = "Plugin initialization failed: {error}"
        PLUGIN_REGISTER_FAILED: Final[str] = (
            "Plugin command registration failed: {error}"
        )
        FAILED_INITIALIZE_PLUGIN: Final[str] = "Failed to initialize plugin: {error}"
        FAILED_LOAD_AND_INIT_PLUGIN: Final[str] = (
            "Failed to load and initialize plugin: {error}"
        )
        FAILED_GET_LOADED_PLUGINS: Final[str] = "Failed to get loaded plugins: {error}"
        FAILED_GET_INIT_PLUGINS: Final[str] = (
            "Failed to get initialized plugins: {error}"
        )
        FAILED_UNLOAD_PLUGIN: Final[str] = "Failed to unload plugin: {error}"

        # File tools errors
        YAML_WRITE_FAILED: Final[str] = "YAML write failed: {error}"
        FORMAT_DETECTION_FAILED: Final[str] = "Format detection failed"
        UNSUPPORTED_FORMAT: Final[str] = "Unsupported format: {format}"

        # Debug errors
        FILESYSTEM_VALIDATION_FAILED: Final[str] = (
            "Filesystem validation failed: {error}"
        )
        CANNOT_WRITE_CURRENT_DIR: Final[str] = (
            "Cannot write to current directory: {error}"
        )

    class ServiceMessages:
        """Service operational status messages."""

        FLEXT_CLI_AUTH_OPERATIONAL: Final[str] = "FlextCliAuth service operational"
        CONFIG_LOADED_SUCCESSFULLY: Final[str] = (
            "Configuration loaded successfully. Use set_config_value to modify specific values."
        )
        FLEXT_CLI_DEBUG_OPERATIONAL: Final[str] = "FlextCliDebug service operational"

    class LogMessages:
        """Centralized log message templates for CLI operations."""

        # Command log messages
        COMMAND_REGISTERED: Final[str] = "Command '{name}' registered successfully"
        COMMAND_EXECUTED: Final[str] = "Command '{name}' executed successfully"

        # Configuration log messages
        CLI_CONFIG_UPDATED: Final[str] = "CLI configuration updated successfully"
        PROFILE_CREATED: Final[str] = "Profile '{name}' created successfully"

        # Session log messages
        SESSION_STARTED: Final[str] = "CLI session started successfully"
        SESSION_ENDED: Final[str] = "CLI session ended successfully"

        # Config operation log messages
        CONFIG_DISPLAYED: Final[str] = "Configuration displayed"
        CONFIG_VALIDATION_RESULTS: Final[str] = "Config validation results: {results}"
        CONFIG_EDIT_COMPLETED: Final[str] = "Configuration edit completed successfully"

    class FieldDescriptions:
        """Field description constants for Pydantic models."""

        # CLI configuration field descriptions
        PROFILE: Final[str] = "CLI profile to use for configuration"
        OUTPUT_FORMAT: Final[str] = "Default output format for CLI commands"
        NO_COLOR: Final[str] = "Disable colored output in CLI"
        CONFIG_DIR: Final[str] = "Configuration directory path"
        PROJECT_NAME: Final[str] = "Project name for CLI operations"
        API_URL: Final[str] = "API URL for remote operations"
        CLI_API_KEY: Final[str] = "API key for authentication (sensitive)"
        TOKEN_FILE: Final[str] = "Path to authentication token file"
        REFRESH_TOKEN_FILE: Final[str] = "Path to refresh token file"
        AUTO_REFRESH: Final[str] = "Automatically refresh authentication tokens"
        VERBOSE: Final[str] = "Enable verbose output"
        DEBUG: Final[str] = "Enable debug mode"
        APP_NAME: Final[str] = "Application name"
        VERSION: Final[str] = "Application version"
        QUIET: Final[str] = "Enable quiet mode"
        INTERACTIVE: Final[str] = "Enable interactive mode"
        MAX_WIDTH: Final[str] = "Maximum width for CLI output"
        CONFIG_FILE: Final[str] = "Custom configuration file path"
        TIMEOUT: Final[str] = "Network timeout in seconds"
        MAX_RETRIES: Final[str] = "Maximum number of retry attempts"
        LOG_LEVEL: Final[str] = "Global logging level for FLEXT projects"
        LOG_VERBOSITY: Final[str] = "Logging verbosity (compact, detailed, full)"
        CLI_LOG_LEVEL: Final[str] = "CLI-specific logging level"
        CLI_LOG_VERBOSITY: Final[str] = "CLI-specific logging verbosity"
        LOG_FILE: Final[str] = "Optional log file path for persistent logging"

    class ValidationMessages:
        """Centralized validation message templates."""

        FIELD_NOT_EMPTY: Final[str] = "{field} cannot be empty"
        FIELD_MIN_LENGTH: Final[str] = (
            "{field} must be at least {min_length} characters"
        )
        VALUE_REQUIRED: Final[str] = "{field} is required"
        INVALID_VALUE: Final[str] = "Invalid {field}: {value}"
        VALUE_OUT_OF_RANGE: Final[str] = (
            "{field} must be between {min_val} and {max_val}"
        )
        INVALID_OUTPUT_FORMAT_MUST_BE: Final[str] = (
            "Invalid output format: {format}. Must be one of: {valid_formats}"
        )
        PROFILE_NAME_CANNOT_BE_EMPTY: Final[str] = "Profile name cannot be empty"
        INVALID_API_URL_MUST_START: Final[str] = (
            "Invalid API URL format: {url}. Must start with http:// or https://"
        )
        INVALID_LOG_LEVEL_MUST_BE: Final[str] = (
            "Invalid log level: {level}. Must be one of: {valid_levels}"
        )
        INVALID_LOG_VERBOSITY_MUST_BE: Final[str] = (
            "Invalid log verbosity: {verbosity}. Must be one of: {valid_verbosity}"
        )

    class DictKeys:
        """Centralized dictionary key constants."""

        # Token and auth keys
        TOKEN_FILE: Final[str] = "token_file"
        REFRESH_TOKEN_FILE: Final[str] = "refresh_token_file"
        TOKEN_PATH: Final[str] = "token_path"
        REFRESH_TOKEN_PATH: Final[str] = "refresh_token_path"
        TOKEN: Final[str] = "token"
        USERNAME: Final[str] = "username"
        PASSWORD: Final[str] = "password"
        AUTHENTICATED: Final[str] = "authenticated"
        TOKEN_EXISTS: Final[str] = "token_exists"
        REFRESH_TOKEN_EXISTS: Final[str] = "refresh_token_exists"

        # Configuration keys
        CONFIG_DIR: Final[str] = "config_dir"
        CONFIG_EXISTS: Final[str] = "config_exists"
        CONFIG_READABLE: Final[str] = "config_readable"
        CONFIG_WRITABLE: Final[str] = "config_writable"
        CONFIG: Final[str] = "config"
        PROFILES: Final[str] = "profiles"

        # Command execution keys
        ARGS: Final[str] = "args"
        COMMAND: Final[str] = "command"
        STATUS: Final[str] = "status"
        CONTEXT: Final[str] = "context"
        TIMESTAMP: Final[str] = "timestamp"
        TOTAL_COMMANDS: Final[str] = "total_commands"
        EXECUTION_TIME: Final[str] = "execution_time"

        # Service and system keys
        SERVICE: Final[str] = "service"
        MESSAGE: Final[str] = "message"
        LOGGER_INSTANCE: Final[str] = "logger_instance"
        PROMPTS_EXECUTED: Final[str] = "prompts_executed"
        INTERACTIVE_MODE: Final[str] = "interactive_mode"

        # File and directory keys
        HOST: Final[str] = "host"
        PORT: Final[str] = "port"
        TIMEOUT: Final[str] = "timeout"

        # Data value keys (generic)
        KEY: Final[str] = "key"
        VALUE: Final[str] = "value"

        # Configuration data keys
        PROFILE: Final[str] = "profile"
        DEBUG: Final[str] = "debug"
        VERBOSE: Final[str] = "verbose"
        QUIET: Final[str] = "quiet"
        OUTPUT_FORMAT: Final[str] = "output_format"
        CONFIG_FILE: Final[str] = "config_file"
        CONFIG_DATA: Final[str] = "config_data"

    class StatusValues:
        """Additional status values for CLI operations."""

        SIMULATED_INPUT: Final[str] = "simulated_input"
        PASSWORD_HIDDEN: Final[str] = "[password hidden]"

    class Subdirectories:
        """CLI subdirectory names."""

        CONFIG: Final[str] = "config"
        CACHE: Final[str] = "cache"
        LOGS: Final[str] = "logs"
        TOKEN: Final[str] = "token"
        REFRESH_TOKEN: Final[str] = "refresh_token"

        # List of subdirectories for iteration
        STANDARD_SUBDIRS: Final[FlextTypes.StringList] = [
            CONFIG,
            CACHE,
            LOGS,
        ]

    class Symbols:
        """CLI symbols and markers."""

        SUCCESS_MARK: Final[str] = "✓"
        FAILURE_MARK: Final[str] = "✗"
        ERROR_PREFIX: Final[str] = "❌ Error:"
        SUCCESS_PREFIX: Final[str] = "✅ Success:"

    class YesNo:
        """Yes/No response constants."""

        YES: Final[str] = "y"
        YES_FULL: Final[str] = "yes"
        NO: Final[str] = "n"
        NO_FULL: Final[str] = "no"
        TRUE: Final[str] = "true"
        FALSE: Final[str] = "false"
        ONE: Final[str] = "1"
        ZERO: Final[str] = "0"

        YES_VALUES: Final[FlextTypes.StringList] = ["y", "yes", "true", "1"]
        NO_VALUES: Final[FlextTypes.StringList] = ["n", "no", "false", "0"]

    class Encoding:
        """Encoding constants."""

        UTF8: Final[str] = "utf-8"
        ASCII: Final[str] = "ascii"

    class JsonOptions:
        """JSON serialization option keys."""

        SKIPKEYS: Final[str] = "skipkeys"
        ENSURE_ASCII: Final[str] = "ensure_ascii"
        CHECK_CIRCULAR: Final[str] = "check_circular"
        ALLOW_NAN: Final[str] = "allow_nan"
        CLS: Final[str] = "cls"
        INDENT: Final[str] = "indent"
        SEPARATORS: Final[str] = "separators"
        DEFAULT: Final[str] = "default"
        SORT_KEYS: Final[str] = "sort_keys"

    class YamlOptions:
        """YAML serialization option keys."""

        DEFAULT_STYLE: Final[str] = "default_style"
        DEFAULT_FLOW_STYLE: Final[str] = "default_flow_style"
        CANONICAL: Final[str] = "canonical"
        INDENT: Final[str] = "indent"
        WIDTH: Final[str] = "width"
        ALLOW_UNICODE: Final[str] = "allow_unicode"
        LINE_BREAK: Final[str] = "line_break"
        ENCODING: Final[str] = "encoding"
        EXPLICIT_START: Final[str] = "explicit_start"
        EXPLICIT_END: Final[str] = "explicit_end"
        VERSION: Final[str] = "version"
        TAGS: Final[str] = "tags"
        SORT_KEYS: Final[str] = "sort_keys"

    class EnvironmentConstants:
        """Environment variable and testing constants."""

        PYTEST_CURRENT_TEST: Final[str] = "PYTEST_CURRENT_TEST"
        PYTEST: Final[str] = "pytest"
        UNDERSCORE: Final[str] = "_"

    class ConfigFiles:
        """Configuration file names."""

        CLI_CONFIG_JSON: Final[str] = "cli_config.json"

    class Project:
        """CLI-specific project types extending FlextTypes.Project.

        Adds CLI-specific project types while inheriting generic types from FlextTypes.
        Follows domain separation principle: CLI domain owns CLI-specific types.
        """

        # CLI-specific project types
        CliProjectType = Literal[
            "cli-tool",
            "console-app",
            "terminal-ui",
            "command-runner",
            "interactive-cli",
            "batch-processor",
            "cli-wrapper",
        ]

        # CLI-specific project configurations
        CliProjectConfig = dict[str, FlextTypes.ConfigValue]
        CommandLineConfig = dict[str, str | int | bool | FlextTypes.StringList]
        InteractiveConfig = dict[str, bool | str | dict[str, FlextTypes.ConfigValue]]
        OutputConfig = dict[
            str, FlextTypes.Output.OutputFormat | FlextTypes.ConfigValue
        ]

    class Styles:
        """Rich/Terminal style constants for colored output."""

        BLUE: Final[str] = "blue"
        GREEN: Final[str] = "green"
        RED: Final[str] = "red"
        YELLOW: Final[str] = "yellow"
        BOLD: Final[str] = "bold"
        BOLD_GREEN: Final[str] = "bold green"
        BOLD_RED: Final[str] = "bold red"
        BOLD_YELLOW: Final[str] = "bold yellow"
        BOLD_BLUE: Final[str] = "bold blue"

    class Emojis:
        """Emoji constants for terminal output messages."""

        INFO: Final[str] = "ℹ️"
        SUCCESS: Final[str] = "✅"
        ERROR: Final[str] = "❌"
        WARNING: Final[str] = "⚠️"

    class TableFormats:
        """Table format constants for tabulate integration."""

        KEYS: Final[str] = "keys"
        SIMPLE: Final[str] = "simple"
        GRID: Final[str] = "grid"
        FANCY_GRID: Final[str] = "fancy_grid"
        PIPE: Final[str] = "pipe"

    class TokenDefaults:
        """Token generation and security defaults."""

        URL_SAFE_BYTES: Final[int] = 32

    class TerminalDefaults:
        """Terminal dimension and display defaults."""

        DEFAULT_WIDTH: Final[int] = 80
        DEFAULT_HEIGHT: Final[int] = 24

    class PriorityDefaults:
        """Priority level defaults for task scheduling."""

        DEFAULT_PRIORITY: Final[int] = 999

    class ValidationLimits:
        """Validation boundary limits for CLI parameters."""

        MIN_MAX_WIDTH: Final[int] = 40
        MAX_MAX_WIDTH: Final[int] = 200
        MAX_TIMEOUT_SECONDS: Final[int] = 300
        MAX_RETRIES: Final[int] = 10

    class DebugServiceNames:
        """Debug service name constants for diagnostic operations."""

        DEBUG: Final[str] = "FlextCliDebug"

    class ProgressDefaults:
        """Progress reporting and update defaults."""

        REPORT_THRESHOLD: Final[int] = 10
        UPDATE_INTERVAL_MS: Final[int] = 100

    class FormattingDefaults:
        """Text formatting and display defaults."""

        INDENT_WIDTH: Final[int] = 2
        TAB_WIDTH: Final[int] = 4
        LINE_BUFFER: Final[int] = 100
        MIN_FIELD_LENGTH: Final[int] = 1

    # Table formats for tabulate integration
    TABLE_FORMATS: Final[FlextTypes.StringDict] = {
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


__all__ = [
    "FlextCliConstants",
]

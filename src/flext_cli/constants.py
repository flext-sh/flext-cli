"""FLEXT CLI Constants - Centralized constants, enums, and literals.

Domain-specific constants extending flext-core standardization for CLI operations.
All literals, strings, numbers, enums, and configuration defaults centralized here.

Advanced Python 3.13+ patterns:
- PEP 695 type aliases for modern syntax
- StrEnum for runtime validation with string interoperability
- collections.abc.Mapping for immutable configuration data
- Discriminated unions with Literal types
- Advanced validation helpers with type narrowing

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from enum import StrEnum
from typing import ClassVar, Final, Literal

from flext_core import FlextConstants


class FlextCliConstants(FlextConstants):
    """CLI constants extending flext-core standardization for CLI domain.

    Business Rules:
    ───────────────
    1. All CLI constants MUST be centralized here (no scattered constants)
    2. Use StrEnum for runtime validation with string interoperability
    3. Use Literal types for type hints (compile-time validation)
    4. Use collections.abc.Mapping for immutable configuration data
    5. Use frozenset for O(1) membership testing in validation
    6. NO duplication between domains - reuse from flext-core when available
    7. NO simple aliases - use complex types with proper validation
    8. Constants MUST be immutable (Final, ClassVar, frozenset, Mapping)

    Architecture Implications:
    ───────────────────────────
    - Centralization ensures single source of truth for all CLI constants
    - StrEnum provides runtime validation and IDE autocomplete
    - Literal types enable type narrowing and exhaustiveness checking
    - Immutable constants prevent accidental modification
    - Composition with FlextConstants ensures ecosystem consistency

    Audit Implications:
    ───────────────────
    - Constant values MUST NOT contain sensitive data (passwords, tokens, keys)
    - Default values MUST be safe and secure (no hardcoded credentials)
    - Configuration constants MUST be validated before use
    - Enum values MUST be documented for audit trail
    - Constant changes MUST be reviewed for security implications
    - Default timeouts and retries MUST prevent resource exhaustion
    """

    # =====================================================================
    # LITERAL TYPES - Python 3.13+ Best Practices
    # =====================================================================
    # CRITICAL: All Literals must be in constants (first class)
    # Using Python 3.13+ `type` statement for type aliases (better than TypeAlias)
    # When possible, prefer StrEnum over Literal for runtime validation
    # Literals are kept for type hints, Enums provide runtime validation

    # Command result status - use Literal for simple status strings
    type CommandResultStatusLiteral = Literal["success", "failure", "error"]

    # CLI project types - use Literal for simple string unions
    type CliProjectTypeLiteral = Literal[
        "cli-tool",
        "console-app",
        "terminal-ui",
        "command-runner",
        "interactive-cli",
        "batch-processor",
        "cli-wrapper",
    ]

    # Output format literal - matches OutputFormats StrEnum below
    type OutputFormatLiteral = Literal["json", "yaml", "csv", "table", "plain"]

    # Log level literal - reuse from flext-core (no duplication)
    # PEP 695 type statement works in classes (Python 3.13+)
    type LogLevelLiteral = FlextConstants.Literals.LogLevelLiteral

    # Command status literal - matches CommandStatus StrEnum below
    type CommandStatusLiteral = Literal[
        "pending",
        "running",
        "completed",
        "failed",
        "cancelled",
    ]

    # Session status literal - matches SessionStatus StrEnum below
    type SessionStatusLiteral = Literal["active", "completed", "terminated"]

    # Service status literal - matches ServiceStatus StrEnum below
    type ServiceStatusLiteral = Literal[
        "operational",
        "available",
        "degraded",
        "error",
        "healthy",
        "connected",
    ]

    # Environment literal - reuse from flext-core (no duplication)
    # Use flext-core EnvironmentLiteral directly - includes "testing" (standard value)
    type EnvironmentLiteral = FlextConstants.Literals.EnvironmentLiteral

    # Log verbosity literal - log detail levels
    type LogVerbosityLiteral = Literal["compact", "detailed", "full"]

    # Entity type literal - CLI entity types
    type EntityTypeLiteral = Literal["command", "group"]

    # Range type literal - numeric range types
    type RangeTypeLiteral = Literal["int", "float"]

    # Error code literal - matches ErrorCodes StrEnum below
    type ErrorCodeLiteral = Literal[
        "CLI_ERROR",
        "CLI_VALIDATION_ERROR",
        "CLI_CONFIGURATION_ERROR",
        "CLI_CONNECTION_ERROR",
        "CLI_AUTHENTICATION_ERROR",
        "CLI_TIMEOUT_ERROR",
        "CLI_COMMAND_ERROR",
        "CLI_FORMAT_ERROR",
    ]

    # HTTP method literal - matches FlextWebMethods StrEnum below
    type HttpMethodLiteral = Literal[
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "HEAD",
        "OPTIONS",
    ]

    # Message type literal - matches MessageTypes StrEnum below
    type MessageTypeLiteral = Literal["info", "error", "warning", "success", "debug"]

    # Priority defaults - must be in first class (not nested)
    DEFAULT_PRIORITY: Final[int] = 999

    # Project identification
    PROJECT_NAME: str = "flext-cli"

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

    # =====================================================================
    # ADVANCED VALIDATION HELPERS - Python 3.13+ collections.abc patterns
    # =====================================================================

    class ValidationMappings:
        """Immutable validation mappings using collections.abc.Mapping.

        Python 3.13+ best practice for read-only validation data.
        All mappings are ClassVar and use collections.abc for type safety.
        """

        # Output format validation mapping
        OUTPUT_FORMAT_MAP: ClassVar[Mapping[str, str]] = {
            "json": "json",
            "yaml": "yaml",
            "csv": "csv",
            "table": "table",
            "plain": "plain",
        }

        # Output format validation set using frozenset for O(1) membership testing
        OUTPUT_FORMAT_SET: ClassVar[frozenset[str]] = frozenset({
            "json",
            "yaml",
            "csv",
            "table",
            "plain",
        })

        # Command status validation mapping
        COMMAND_STATUS_MAP: ClassVar[Mapping[str, str]] = {
            "pending": "pending",
            "running": "running",
            "completed": "completed",
            "failed": "failed",
            "cancelled": "cancelled",
        }

        # Command status validation set
        COMMAND_STATUS_SET: ClassVar[frozenset[str]] = frozenset({
            "pending",
            "running",
            "completed",
            "failed",
            "cancelled",
        })

    @classmethod
    def get_valid_output_formats(cls) -> Sequence[str]:
        """Get sequence of all valid output format strings.

        Returns immutable sequence using collections.abc.Sequence.
        Python 3.13+ best practice for read-only iteration.

        Returns:
            Immutable sequence of valid output format strings

        """
        return tuple(sorted(cls.ValidationMappings.OUTPUT_FORMAT_SET))

    @classmethod
    def get_valid_command_statuses(cls) -> Sequence[str]:
        """Get sequence of all valid command status strings.

        Returns immutable sequence for safe iteration.
        Composes with CommandStatus enum values.

        Returns:
            Immutable sequence of valid command status strings

        """
        return tuple(sorted(cls.ValidationMappings.COMMAND_STATUS_SET))

    # =====================================================================
    # STRING ENUMS - Python 3.13+ StrEnum Best Practices
    # =====================================================================
    # Use StrEnum for runtime validation and string interoperability
    # These enums match their corresponding Literal types above

    class CommandStatus(StrEnum):
        """Command execution status enum.

        Python 3.13+ StrEnum provides string-like behavior with enum validation.
        Can be used interchangeably with CommandStatusLiteral in type hints.
        """

        PENDING = "pending"
        RUNNING = "running"
        COMPLETED = "completed"
        FAILED = "failed"
        CANCELLED = "cancelled"

    class SessionStatus(StrEnum):
        """Session execution status enum.

        Python 3.13+ StrEnum provides string-like behavior with enum validation.
        Can be used interchangeably with SessionStatusLiteral in type hints.
        """

        ACTIVE = "active"
        COMPLETED = "completed"
        TERMINATED = "terminated"

    # No DebugLevel class - use FlextConstants.Logging.LogLevel from flext-core

    class ServiceStatus(StrEnum):
        """Service operational status enum.

        Python 3.13+ StrEnum provides string-like behavior with enum validation.
        Can be used interchangeably with ServiceStatusLiteral in type hints.
        """

        OPERATIONAL = "operational"
        AVAILABLE = "available"
        DEGRADED = "degraded"
        ERROR = "error"
        HEALTHY = "healthy"
        CONNECTED = "connected"

    # Service status constants for direct access
    HEALTHY: Final[str] = ServiceStatus.HEALTHY.value
    OPERATIONAL: Final[str] = ServiceStatus.OPERATIONAL.value

    class OutputFormats(StrEnum):
        """CLI output format enum - extends Flext standard formats.

        Python 3.13+ StrEnum provides string-like behavior with enum validation.
        CLI adds "plain" format on top of standard formats.
        Can be used interchangeably with OutputFormatLiteral in type hints.
        """

        JSON = "json"  # Standard format
        YAML = "yaml"  # Standard format
        CSV = "csv"  # Standard format
        TABLE = "table"  # Standard format
        PLAIN = "plain"  # CLI-specific format

    # Environment enum - reuse from flext-core (no duplication)
    # Use FlextConstants.Settings.Environment directly instead of duplicating
    # Note: flext-core uses "testing", not "test" - update references if needed
    Environment = FlextConstants.Settings.Environment

    class LogVerbosity(StrEnum):
        """Log verbosity level enum.

        Python 3.13+ StrEnum provides string-like behavior with enum validation.
        Can be used interchangeably with LogVerbosityLiteral in type hints.
        """

        COMPACT = "compact"
        DETAILED = "detailed"
        FULL = "full"

    class ServerType(StrEnum):
        """Server type enum.

        Python 3.13+ StrEnum provides string-like behavior with enum validation.
        """

        OUD = "oud"
        OID = "oid"
        RFC = "rfc"
        AD = "ad"
        OPENLDAP = "openldap"

    class EntityType(StrEnum):
        """CLI entity type enum.

        Python 3.13+ StrEnum provides string-like behavior with enum validation.
        Can be used interchangeably with EntityTypeLiteral in type hints.
        """

        COMMAND = "command"
        GROUP = "group"

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
        # Matches OutputFormats.TABLE.value
        # Using literal to avoid forward reference issues
        DEFAULT_OUTPUT_FORMAT: Final[str] = "table"
        # Network timeout - reuse from flext-core Network (no duplication)
        DEFAULT_TIMEOUT: Final[int] = FlextConstants.Network.DEFAULT_TIMEOUT

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

        # Environment defaults - reuse from flext-core (no duplication)
        DEFAULT_ENVIRONMENT: Final[str] = (
            FlextConstants.Settings.Environment.DEVELOPMENT.value
        )

        # Log level defaults - reuse from flext-core
        DEFAULT_LOG_LEVEL: Final[str] = FlextConstants.Settings.LogLevel.INFO.value
        DEFAULT_CLI_LOG_LEVEL: Final[str] = FlextConstants.Settings.LogLevel.INFO.value

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

        # Network defaults - reuse from flext-core Platform constants (no duplication)
        DEFAULT_HOST: Final[str] = FlextConstants.Platform.DEFAULT_HOST
        DEFAULT_PORT: Final[int] = (
            8080  # CLI-specific port (different from FLEXT_API_PORT)
        )
        DEFAULT_API_URL: Final[str] = (
            f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}/api"
        )
        # Network timeout - reuse from flext-core Network (no duplication)
        DEFAULT_TIMEOUT: Final[int] = FlextConstants.Network.DEFAULT_TIMEOUT
        DEFAULT_MAX_RETRIES: Final[int] = 3
        CONNECT_TIMEOUT: Final[int] = 10
        READ_TIMEOUT: Final[int] = 60

    class PhoneValidation:
        """Phone number validation constants."""

        MIN_INTERNATIONAL_DIGITS: Final[int] = 10
        MAX_INTERNATIONAL_DIGITS: Final[int] = 15
        US_PHONE_DIGITS: Final[int] = 10

    # Constant lists for validation and iteration
    OUTPUT_FORMATS_LIST: Final[list[str]] = [
        OutputFormats.JSON.value,
        OutputFormats.YAML.value,
        OutputFormats.CSV.value,
        OutputFormats.TABLE.value,
        OutputFormats.PLAIN.value,
    ]

    # Use FlextConstants.Logging.VALID_LEVELS from flext-core (no duplication)
    LOG_LEVELS_LIST: Final[list[str]] = list(FlextConstants.Logging.VALID_LEVELS)

    COMMAND_STATUSES_LIST: Final[list[str]] = [
        CommandStatus.PENDING.value,
        CommandStatus.RUNNING.value,
        CommandStatus.COMPLETED.value,
        CommandStatus.FAILED.value,
        CommandStatus.CANCELLED.value,
    ]

    SESSION_STATUSES_LIST: Final[list[str]] = [
        SessionStatus.ACTIVE.value,
        SessionStatus.COMPLETED.value,
        SessionStatus.TERMINATED.value,
    ]

    # Use same list as LOG_LEVELS_LIST (references flext-core)
    DEBUG_LEVELS_LIST: Final[list[str]] = LOG_LEVELS_LIST

    # Critical debug levels that require descriptive messages
    CRITICAL_DEBUG_LEVELS: Final[list[str]] = [
        FlextConstants.Logging.ERROR,
        FlextConstants.Logging.CRITICAL,
    ]

    CRITICAL_DEBUG_LEVELS_SET: Final[set[str]] = {
        FlextConstants.Logging.ERROR,
        FlextConstants.Logging.CRITICAL,
    }

    SERVICE_STATUSES_LIST: Final[list[str]] = [
        ServiceStatus.OPERATIONAL.value,
        ServiceStatus.AVAILABLE.value,
        ServiceStatus.DEGRADED.value,
        ServiceStatus.ERROR.value,
        ServiceStatus.HEALTHY.value,
        ServiceStatus.CONNECTED.value,
    ]

    ERROR_CODES_LIST: Final[list[str]] = [
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
        BUILTIN_COMMANDS: Final[list[str]] = [
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

        # Network timeout - reuse from flext-core Network (no duplication)
        DEFAULT_TIMEOUT: Final[int] = FlextConstants.Network.DEFAULT_TIMEOUT
        MAX_RETRIES: Final[int] = 3
        RETRY_DELAY: Final[int] = 1
        USER_AGENT: Final[str] = "FlextCLI/1.0"

    class FlextWebMethods(StrEnum):
        """HTTP method constants."""

        GET = "GET"
        POST = "POST"
        PUT = "PUT"
        DELETE = "DELETE"
        PATCH = "PATCH"
        HEAD = "HEAD"
        OPTIONS = "OPTIONS"

    HTTP_METHODS_LIST: Final[list[str]] = [
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

    MESSAGE_TYPES_LIST: Final[list[str]] = [
        MessageTypes.INFO.value,
        MessageTypes.ERROR.value,
        MessageTypes.WARNING.value,
        MessageTypes.SUCCESS.value,
        MessageTypes.DEBUG.value,
    ]

    # =====================================================================
    # ADVANCED ENUM VALIDATION - Python 3.13+ discriminated union patterns
    # =====================================================================

    @classmethod
    def get_enum_values(cls, enum_class: type[StrEnum]) -> Sequence[str]:
        """Get all values from StrEnum class.

        Returns immutable sequence for safe iteration.
        Python 3.13+ collections.abc.Sequence pattern.
        Uses enum.__members__ for compatibility with all type checkers.

        Args:
            enum_class: StrEnum class to extract values from

        Returns:
            Immutable sequence of enum string values

        """
        return tuple(member.value for member in enum_class.__members__.values())

    @classmethod
    def create_cli_discriminated_union(
        cls,
        _discriminator_field: str,
        *enum_classes: type[StrEnum],
    ) -> dict[str, type[StrEnum]]:
        """Create discriminated union mapping for Pydantic models.

        Advanced pattern for discriminated unions with multiple enums.
        Enables efficient validation with Field(discriminator=discriminator_field).
        Python 3.13+ discriminated union best practice.

        CLI-specific helper that extends FlextConstants.create_discriminated_union
        with discriminator field support for Pydantic models.

        Args:
            discriminator_field: Field name used as discriminator
            *enum_classes: StrEnum classes to include in union

        Returns:
            Mapping of discriminator values to enum classes

        """
        union_map = {}
        for enum_class in enum_classes:
            for member in enum_class.__members__.values():
                union_map[member.value] = enum_class
        return union_map

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
    # Matches OutputFormats.TABLE.value
    # Using direct reference since OutputFormats is already defined above
    TABLE: Final[str] = OutputFormats.TABLE.value

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

    # =====================================================================
    # ADVANCED FILE FORMATS CONFIG - Python 3.13+ nested Mapping patterns
    # =====================================================================

    # File formats configuration with advanced typing
    # Uses nested collections.abc.Mapping for immutable hierarchical data
    # Python 3.13+ best practice for complex read-only configurations
    FILE_FORMATS: Final[Mapping[str, Mapping[str, str | tuple[str, ...]]]] = {
        "json": {"extensions": ("json",), "mime_type": "application/json"},
        "yaml": {"extensions": ("yaml", "yml"), "mime_type": "application/x-yaml"},
        "csv": {"extensions": ("csv",), "mime_type": "text/csv"},
        "tsv": {"extensions": ("tsv",), "mime_type": "text/tab-separated-values"},
        "toml": {"extensions": ("toml",), "mime_type": "application/toml"},
        "xml": {"extensions": ("xml",), "mime_type": "application/xml"},
    }

    # Immutable set of supported format names using frozenset
    # Python 3.13+ frozenset for O(1) membership testing
    SUPPORTED_FILE_FORMATS: Final[frozenset[str]] = frozenset(FILE_FORMATS.keys())

    @classmethod
    def get_file_extensions(cls, format_name: str) -> Sequence[str] | None:
        """Get file extensions for a format name.

        Advanced lookup using collections.abc.Mapping.
        Returns immutable sequence for safe iteration.
        Python 3.13+ best practice for format validation.

        Args:
            format_name: Format name to lookup

        Returns:
            Immutable sequence of extensions, or None if format not supported

        """
        format_config = cls.FILE_FORMATS.get(format_name)
        return format_config.get("extensions") if format_config else None

    @classmethod
    def get_mime_type(cls, format_name: str) -> str | None:
        """Get MIME type for a format name.

        Uses advanced Mapping lookup with type safety.
        Composes with FILE_FORMATS configuration.

        Args:
            format_name: Format name to lookup

        Returns:
            MIME type string, or None if format not supported

        """
        format_config = cls.FILE_FORMATS.get(format_name)
        if format_config:
            mime_type = format_config.get("mime_type")
            return mime_type if isinstance(mime_type, str) else None
        return None

    @classmethod
    def validate_file_format(cls, format_name: str) -> bool:
        """Validate if a file format is supported.

        Uses frozenset for optimal O(1) membership testing.
        Python 3.13+ collections.abc.Set best practice.

        Args:
            format_name: Format name to validate

        Returns:
            True if format is supported, False otherwise

        """
        return format_name in cls.SUPPORTED_FILE_FORMATS

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
        COMMAND_REGISTRATION_FAILED: Final[str] = "Command registration failed: {error}"
        COMMAND_UNREGISTRATION_FAILED: Final[str] = (
            "Command unregistration failed: {error}"
        )
        COMMANDS_REQUIRED: Final[str] = (
            "Commands dictionary is required and cannot be None"
        )
        GROUP_CREATION_FAILED: Final[str] = "Group creation failed: {error}"
        CLI_EXECUTION_FAILED: Final[str] = "CLI execution failed"
        CLI_EXECUTION_ERROR: Final[str] = "CLI execution error: {error}"

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
            "Table format requires t.JsonDict or list of dicts"
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
            "Configuration loaded successfully. "
            "Use set_config_value to modify specific values."
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

        # Testing keys
        EXIT_CODE: Final[str] = "exit_code"
        OUTPUT: Final[str] = "output"
        EXCEPTION: Final[str] = "exception"
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
        VERSION: Final[str] = "version"
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
        SECRET: Final[str] = "secret"
        AUTH: Final[str] = "auth"

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
        STANDARD_SUBDIRS: Final[list[str]] = [
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

        YES_VALUES: Final[list[str]] = ["y", "yes", "true", "1"]
        NO_VALUES: Final[list[str]] = ["n", "no", "false", "0"]

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

    class JsonSchemaKeys:
        """JSON Schema property keys for Pydantic field constraints."""

        MINIMUM: Final[str] = "minimum"
        MAXIMUM: Final[str] = "maximum"
        PROPERTIES: Final[str] = "properties"
        TITLE: Final[str] = "title"
        DESCRIPTION: Final[str] = "description"

    class EnvironmentConstants:
        """Environment variable and testing constants."""

        PYTEST_CURRENT_TEST: Final[str] = "PYTEST_CURRENT_TEST"
        PYTEST: Final[str] = "pytest"
        UNDERSCORE: Final[str] = "_"
        CI: Final[str] = "CI"
        CI_TRUE_VALUE: Final[str] = "true"

    class ConfigFiles:
        """Configuration file names."""

        CLI_CONFIG_JSON: Final[str] = "cli_config.json"

    class ConfigParsing:
        """Configuration parsing constants for environment variables."""

        # Boolean parsing values
        BOOL_TRUE_VALUES: Final[set[str]] = {"true", "1", "yes", "on"}
        BOOL_FALSE_VALUES: Final[set[str]] = {"false", "0", "no", "off", ""}

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

        INFO: Final[str] = "i"  # Information icon
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
        GITHUB: Final[str] = "github"
        HTML: Final[str] = "html"
        UNSAFEHTML: Final[str] = "unsafehtml"
        LATEX: Final[str] = "latex"
        LATEX_RAW: Final[str] = "latex_raw"
        LATEX_BOOKTABS: Final[str] = "latex_booktabs"
        LATEX_LONGTABLE: Final[str] = "latex_longtable"
        RST: Final[str] = "rst"

    class TokenDefaults:
        """Token generation and security defaults."""

        URL_SAFE_BYTES: Final[int] = 32

    class TerminalDefaults:
        """Terminal dimension and display defaults."""

        DEFAULT_WIDTH: Final[int] = 80
        DEFAULT_HEIGHT: Final[int] = 24

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

    class ConfigValidation:
        """Configuration field validation constants."""

        LOG_VERBOSITY_VALUES: Final[set[str]] = {"compact", "detailed", "full"}
        # Environment values - reuse from flext-core (no duplication)
        # Use FlextConstants.get_valid_environments() method instead
        ENVIRONMENT_VALUES: Final[set[str]] = set(
            FlextConstants.get_valid_environments(),
        )
        URL_PROTOCOLS: Final[tuple[str, ...]] = ("http://", "https://")
        YAML_EXTENSIONS: Final[set[str]] = {".yml", ".yaml"}
        STDOUT_FD: Final[int] = 1
        CAPABILITIES_TUPLE_MIN_LENGTH: Final[int] = 2
        DEFAULT_TERMINAL_WIDTH: Final[int] = 80

    # CliGlobalDefaults moved to line 2424 to consolidate all defaults

    class ClickTypes:
        """Click type specification constants."""

        STRING: Final[str] = "STRING"
        INT: Final[str] = "INT"
        FLOAT: Final[str] = "FLOAT"
        BOOL: Final[str] = "BOOL"

    class CliParamDefaults:
        """CLI parameter handling defaults."""

        PARAM_NAME_SEPARATOR: Final[str] = "-"
        FIELD_NAME_SEPARATOR: Final[str] = "_"
        OPTION_PREFIX: Final[str] = "--"
        HELP_TEXT_DEFAULT: Final[str] = "{field_name} parameter"
        MASKED_SENSITIVE: Final[str] = "***MASKED***"
        MASK_CHAR: Final[str] = "*"
        MAGIC_ATTR_CLI_MODEL: Final[str] = "__cli_model__"
        MAGIC_ATTR_CLI_COMMAND_NAME: Final[str] = "__cli_command_name__"
        MAGIC_ATTR_CLI_MODELS: Final[str] = "__cli_models__"

    class FileIODefaults:
        """File I/O operation constants."""

        FILE_WRITE_MODE: Final = "w"
        FILE_READ_MODE: Final = "r"
        FILE_READ_BINARY_MODE: Final[str] = "rb"
        ZIP_WRITE_MODE: Final = "w"
        ZIP_READ_MODE: Final = "r"
        JSON_INDENT: Final[int] = 2
        JSON_ENSURE_ASCII: Final[bool] = False
        ENCODING_DEFAULT: Final[str] = "utf-8"
        GLOB_PATTERN_ALL: Final[str] = "*"
        FORMAT_EXTENSIONS_KEY: Final[str] = "extensions"

    class CoreServiceDefaults:
        """Core service constants for operation defaults."""

        SESSION_DURATION_INIT: Final[int] = 0
        UNKNOWN_VALUE: Final[str] = "unknown"
        OPERATION_TYPE_CLI_COMMAND: Final[str] = "cli_command"
        CLI_COMMAND_PREFIX: Final[str] = "cli_command_"

    class PrivateAttributes:
        """Private attribute names for FlextCliCore service."""

        SESSION_CONFIG: Final[str] = "_session_config"
        SESSION_START_TIME: Final[str] = "_session_start_time"

    class CoreServiceDictKeys:
        """Dictionary keys specific to FlextCliCore operations."""

        REGISTERED_COMMANDS: Final[str] = "registered_commands"
        COMMANDS_REGISTERED: Final[str] = "commands_registered"
        CONFIGURATION_SECTIONS: Final[str] = "configuration_sections"
        SERVICE_READY: Final[str] = "service_ready"
        SESSION_ACTIVE: Final[str] = "session_active"
        SESSION_DURATION_SECONDS: Final[str] = "session_duration_seconds"
        COMMANDS_AVAILABLE: Final[str] = "commands_available"
        CONFIGURATION_LOADED: Final[str] = "configuration_loaded"
        SESSION_CONFIG_KEYS: Final[str] = "session_config_keys"
        START_TIME: Final[str] = "start_time"
        CURRENT_TIME: Final[str] = "current_time"
        SERVICE_EXECUTED: Final[str] = "service_executed"
        COMMANDS_COUNT: Final[str] = "commands_count"
        EXECUTION_TIMESTAMP: Final[str] = "execution_timestamp"
        USER_ID: Final[str] = "user_id"
        OPERATION_TYPE: Final[str] = "operation_type"

    class CoreServiceLogMessages:
        """Log messages specific to FlextCliCore operations."""

        SERVICE_INFO_COLLECTION_FAILED: Final[str] = "Service info collection failed"
        SESSION_STATS_COLLECTION_FAILED: Final[str] = (
            "Session statistics collection failed: {error}"
        )
        SERVICE_EXECUTION_FAILED: Final[str] = "Service execution failed: {error}"

    class FileDefaults:
        """File handling defaults for CLI operations."""

        DEFAULT_FILE_MODE: Final[str] = "r"
        DEFAULT_ERROR_HANDLING: Final[str] = "strict"
        DEFAULT_DATETIME_FORMATS: Final[list[str]] = [
            "%Y-%m-%d",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%d %H:%M:%S",
        ]

    class UIDefaults:
        """User interface default values."""

        DEFAULT_PROMPT_SUFFIX: Final[str] = ": "
        DEFAULT_PAUSE_MESSAGE: Final[str] = "Press any key to continue..."

    class APIDefaults:
        """API and core service defaults."""

        TOKEN_GENERATION_BYTES: Final[int] = 32
        PRINT_TABLE_ERROR_PREFIX: Final[str] = "Failed to print table: {error}"
        FILE_ERROR_INDICATOR: Final[str] = "not found"
        TOKEN_DATA_TYPE_ERROR: Final[str] = "Token file must contain a JSON object"
        TOKEN_VALUE_TYPE_ERROR: Final[str] = "Token must be a string"
        APP_DESCRIPTION_SUFFIX: Final[str] = " CLI"
        CONTAINER_REGISTRATION_KEY: Final[str] = "flext_cli"

    class FileToolsDefaults:
        """File tools service defaults."""

        SERVICE_STATUS_READY: Final[str] = "ready"
        EXTENSION_PREFIX: Final[str] = "."
        CHUNK_SIZE: Final[int] = 4096

    class FileErrorMessages:
        """File operation error messages."""

        BINARY_READ_FAILED: Final[str] = "Binary read failed: {error}"
        BINARY_WRITE_FAILED: Final[str] = "Binary write failed: {error}"
        CSV_READ_FAILED: Final[str] = "CSV read failed: {error}"
        CSV_WRITE_FAILED: Final[str] = "CSV write failed: {error}"
        FILE_DELETION_FAILED: Final[str] = "File deletion failed: {error}"
        FILE_MOVE_FAILED: Final[str] = "File move failed: {error}"
        DIRECTORY_CREATION_FAILED: Final[str] = "Directory creation failed: {error}"
        DIRECTORY_CHECK_FAILED: Final[str] = "Directory check failed: {error}"
        DIRECTORY_DELETION_FAILED: Final[str] = "Directory deletion failed: {error}"
        DIRECTORY_LISTING_FAILED: Final[str] = "Directory listing failed: {error}"
        FILE_SIZE_CHECK_FAILED: Final[str] = "File size check failed: {error}"
        FILE_TIME_CHECK_FAILED: Final[str] = "File time check failed: {error}"
        HASH_CALCULATION_FAILED: Final[str] = "Hash calculation failed: {error}"
        HASH_CALCULATION_FAILED_NO_ERROR: Final[str] = "Hash calculation failed"
        PERMISSION_CHECK_FAILED: Final[str] = "Permission check failed: {error}"
        PERMISSION_SET_FAILED: Final[str] = "Permission set failed: {error}"
        TEMP_FILE_CREATION_FAILED: Final[str] = "Temp file creation failed: {error}"
        TEMP_DIR_CREATION_FAILED: Final[str] = "Temp directory creation failed: {error}"
        ZIP_CREATION_FAILED: Final[str] = "Zip creation failed: {error}"
        ZIP_EXTRACTION_FAILED: Final[str] = "Zip extraction failed: {error}"
        FILE_SEARCH_FAILED: Final[str] = "File search failed: {error}"
        CONTENT_SEARCH_FAILED: Final[str] = "Content search failed: {error}"
        JSON_LOAD_FAILED: Final[str] = "JSON load failed: {error}"
        YAML_LOAD_FAILED: Final[str] = "YAML load failed: {error}"
        UNSUPPORTED_FORMAT_EXTENSION: Final[str] = (
            "Unsupported file format: {extension}. Supported: .json, .yaml, .yml"
        )
        FILE_EXISTENCE_CHECK_FAILED: Final[str] = "File existence check failed: {error}"
        UNSUPPORTED_FORMAT_GENERIC: Final[str] = "Unsupported file format: {extension}"

    class FileExtensions:
        """File extension constants."""

        JSON: Final[str] = ".json"
        YAML: Final[str] = ".yaml"
        YML: Final[str] = ".yml"
        CSV: Final[str] = ".csv"
        TXT: Final[str] = ".txt"

    class FileSupportedFormats:
        """Supported file format lists and format name constants."""

        # Format name constants
        JSON: Final[str] = "json"
        YAML: Final[str] = "yaml"
        YML: Final[str] = "yml"
        CSV: Final[str] = "csv"
        TXT: Final[str] = "txt"
        TOML: Final[str] = "toml"
        XML: Final[str] = "xml"
        TSV: Final[str] = "tsv"

        SUPPORTED_FORMATS: Final[list[str]] = [
            "json",
            "yaml",
            "yml",
            "txt",
            "csv",
        ]
        FORMAT_EXTENSIONS_JSON: Final[list[str]] = ["json"]
        FORMAT_EXTENSIONS_YAML: Final[list[str]] = ["yaml", "yml"]
        YAML_EXTENSIONS_SET: Final[set[str]] = {".yaml", ".yml"}

    class ContextDefaults:
        """Context management defaults and constants."""

        CONTEXT_NONE: Final[str] = "none"
        CONTEXT_NOT_SET: Final[str] = "not_set"

    class ContextDictKeys:
        """Dictionary keys specific to CLI context operations."""

        # Context identity and basic info
        ID: Final[str] = "id"
        CONTEXT_ID: Final[str] = "context_id"

        # Testing and exception info
        EXCEPTION_INFO: Final[str] = "exception_info"
        COMMAND: Final[str] = "command"
        CREATED_AT: Final[str] = "created_at"
        TIMEOUT_SECONDS: Final[str] = "timeout_seconds"

        # Arguments and environment
        ARGUMENTS_COUNT: Final[str] = "arguments_count"
        ARGUMENTS: Final[str] = "arguments"
        ENVIRONMENT_VARIABLES: Final[str] = "environment_variables"
        ENVIRONMENT_VARIABLES_COUNT: Final[str] = "environment_variables_count"
        WORKING_DIRECTORY: Final[str] = "working_directory"

        # State and metadata
        IS_ACTIVE: Final[str] = "is_active"
        METADATA_KEYS: Final[str] = "metadata_keys"
        METADATA_COUNT: Final[str] = "metadata_count"
        CONTEXT_EXECUTED: Final[str] = "context_executed"

    class ContextErrorMessages:
        """Error messages for context operations."""

        CONTEXT_ALREADY_ACTIVE: Final[str] = "Context is already active"
        CONTEXT_ACTIVATION_FAILED: Final[str] = "Context activation failed: {error}"
        CONTEXT_NOT_CURRENTLY_ACTIVE: Final[str] = "Context is not currently active"
        CONTEXT_DEACTIVATION_FAILED: Final[str] = "Context deactivation failed: {error}"
        VARIABLE_NAME_MUST_BE_STRING: Final[str] = (
            "Variable name must be a non-empty string"
        )
        ENV_VAR_NOT_FOUND: Final[str] = "Environment variable '{name}' not found"
        ENV_VAR_RETRIEVAL_FAILED: Final[str] = (
            "Environment variable retrieval failed: {error}"
        )
        VARIABLE_VALUE_MUST_BE_STRING: Final[str] = "Variable value must be a string"
        ENV_VAR_SETTING_FAILED: Final[str] = (
            "Environment variable setting failed: {error}"
        )
        ARGUMENT_MUST_BE_STRING: Final[str] = "Argument must be a non-empty string"
        ARGUMENT_ADDITION_FAILED: Final[str] = "Argument addition failed: {error}"
        ARGUMENT_NOT_FOUND: Final[str] = "Argument '{argument}' not found"
        ARGUMENT_REMOVAL_FAILED: Final[str] = "Argument removal failed: {error}"
        METADATA_KEY_MUST_BE_STRING: Final[str] = (
            "Metadata key must be a non-empty string"
        )
        METADATA_SETTING_FAILED: Final[str] = "Metadata setting failed: {error}"
        METADATA_KEY_NOT_FOUND: Final[str] = "Metadata key '{key}' not found"
        METADATA_RETRIEVAL_FAILED: Final[str] = "Metadata retrieval failed: {error}"
        CONTEXT_SUMMARY_GENERATION_FAILED: Final[str] = (
            "Context summary generation failed: {error}"
        )
        CONTEXT_EXECUTION_FAILED: Final[str] = "Context execution failed: {error}"
        ARGUMENTS_NOT_INITIALIZED: Final[str] = (
            "Context arguments not initialized - cannot serialize"
        )
        ENV_VARS_NOT_INITIALIZED: Final[str] = (
            "Context environment variables not initialized - cannot serialize"
        )
        CONTEXT_SERIALIZATION_FAILED: Final[str] = (
            "Context serialization failed: {error}"
        )

    class DebugErrorMessages:
        """Error messages for debug operations."""

        ENVIRONMENT_INFO_FAILED: Final[str] = "Environment info failed: {error}"
        ENVIRONMENT_VALIDATION_FAILED: Final[str] = (
            "Environment validation failed: {error}"
        )
        CONNECTIVITY_TEST_FAILED: Final[str] = "Connectivity test failed: {error}"
        HEALTH_CHECK_FAILED: Final[str] = "Health check failed: {error}"
        TRACE_EXECUTION_FAILED: Final[str] = "Trace execution failed: {error}"
        DEBUG_INFO_COLLECTION_FAILED: Final[str] = (
            "Debug info collection failed: {error}"
        )
        SYSTEM_INFO_COLLECTION_FAILED: Final[str] = (
            "System info collection failed: {error}"
        )
        SYSTEM_PATHS_COLLECTION_FAILED: Final[str] = (
            "System paths collection failed: {error}"
        )
        COMPREHENSIVE_DEBUG_INFO_FAILED: Final[str] = (
            "Comprehensive debug info collection failed: {error}"
        )

    class DebugDictKeys:
        """Dictionary keys for debug operations."""

        SYSTEM: Final[str] = "system"
        SYSTEM_ERROR: Final[str] = "system_error"
        ENVIRONMENT: Final[str] = "environment"
        ENVIRONMENT_ERROR: Final[str] = "environment_error"
        PATHS: Final[str] = "paths"
        PATHS_ERROR: Final[str] = "paths_error"
        DEBUG: Final[str] = "debug"
        DEBUG_ERROR: Final[str] = "debug_error"
        PYTHON_VERSION: Final[str] = "python_version"
        PLATFORM: Final[str] = "platform"
        ARCHITECTURE: Final[str] = "architecture"
        PROCESSOR: Final[str] = "processor"
        HOSTNAME: Final[str] = "hostname"
        INDEX: Final[str] = "index"
        PATH: Final[str] = "path"
        EXISTS: Final[str] = "exists"
        IS_DIR: Final[str] = "is_dir"
        CONNECTIVITY: Final[str] = "connectivity"
        CHECK_ID: Final[str] = "check_id"
        CHECKS_PASSED: Final[str] = "checks_passed"
        OPERATION: Final[str] = "operation"
        ARGS_COUNT: Final[str] = "args_count"
        TRACE_ID: Final[str] = "trace_id"
        DEBUG_ID: Final[str] = "debug_id"
        SYSTEM_INFO: Final[str] = "system_info"
        ENVIRONMENT_STATUS: Final[str] = "environment_status"
        CONNECTIVITY_STATUS: Final[str] = "connectivity_status"

    class CmdDefaults:
        """CMD service defaults and constants."""

        SERVICE_NAME: Final[str] = "FlextCliCmd"

    class CmdMessages:
        """Messages for CMD operations."""

        CONFIG_DIR_EXISTS: Final[str] = " Main config directory exists"
        CONFIG_DIR_MISSING: Final[str] = " Main config directory missing"
        SUBDIR_EXISTS: Final[str] = "{symbol} {subdir} directory exists"
        SUBDIR_MISSING: Final[str] = "{symbol} {subdir} directory missing"
        CONFIG_SAVED: Final[str] = "Configuration saved: {key} = {value}"
        CONFIG_EDIT_COMPLETED_LOG: Final[str] = "Configuration edit completed"
        CONFIG_INFO_LOG: Final[str] = "Configuration edit completed"

    class CmdErrorMessages:
        """Error messages for CMD operations."""

        CONFIG_SAVE_FAILED: Final[str] = "Config save failed: {error}"
        CONFIG_FILE_NOT_FOUND: Final[str] = "Configuration file not found: {path}"
        CONFIG_LOAD_FAILED: Final[str] = "Failed to load config: {error}"
        CONFIG_NOT_DICT: Final[str] = "Configuration data is not a valid dictionary"
        CONFIG_KEY_NOT_FOUND: Final[str] = "Configuration key not found: {key}"
        GET_CONFIG_FAILED: Final[str] = "Get config failed: {error}"
        SHOW_CONFIG_FAILED: Final[str] = "Show config failed: {error}"
        CREATE_DEFAULT_CONFIG_FAILED: Final[str] = (
            "Failed to create default config: {error}"
        )
        CONFIG_CREATION_DEFAULT_FAILED: Final[str] = (
            "Failed to create default config: {error}"
        )

    class CmdDictKeys:
        """Dictionary keys specific to CMD operations."""

        CONFIG_FILE: Final[str] = "config_file"
        CONFIG_DATA: Final[str] = "config_data"
        MESSAGE: Final[str] = "message"

    class DebugDefaults:
        """Debug service defaults and constants."""

        SERVICE_NAME: Final[str] = "FlextCliDebug"
        MASKED_SENSITIVE: Final[str] = "***MASKED***"
        SENSITIVE_KEYS: Final[set[str]] = {
            "password",
            "token",
            "secret",
            "key",
            "auth",
        }

    class PromptsDefaults:
        """Prompts service defaults and constants."""

        DEFAULT_PROCESSING_DESCRIPTION: Final[str] = "Processing..."
        CHOICE_PROMPT_SEPARATOR: Final[str] = "\n"
        CONFIRMATION_SUFFIX: Final[str] = " (y/n)"
        PASSWORD_PROMPT_DISPLAY: Final[str] = "[password hidden]"
        PROMPT_INPUT_SEPARATOR: Final[str] = ": "
        CONFIRMATION_YES_PROMPT: Final[str] = " [Y/n]: "
        CONFIRMATION_NO_PROMPT: Final[str] = " [y/N]: "
        CHOICE_PROMPT_PREFIX: Final[str] = "\nEnter your choice (1-{count}): "
        CHOICE_DISPLAY_FORMAT: Final[str] = "Option {num}: {option}"
        SELECTION_PROMPT: Final[str] = "Selection prompt: {message}"
        STATUS_FORMAT: Final[str] = "[{status}] {message}"
        SUCCESS_FORMAT: Final[str] = "SUCCESS: {message}"
        ERROR_FORMAT: Final[str] = "ERROR: {message}"
        WARNING_FORMAT: Final[str] = "WARNING: {message}"
        INFO_FORMAT: Final[str] = "INFO: {message}"
        PROGRESS_FORMAT: Final[str] = "  Progress: {progress:.1f}% ({current}/{total})"
        PROGRESS_COMPLETED_FORMAT: Final[str] = "Completed: {description}"
        PROGRESS_OPERATION_FORMAT: Final[str] = (
            "Progress operation: {description} ({count} items)"
        )
        PROMPT_DEFAULT_FORMAT: Final[str] = " (default: {default})"
        PROMPT_LOG_FORMAT: Final[str] = "User prompted: {message}, input: {input}"
        CHOICE_LIST_FORMAT: Final[str] = "{index}. {choice}"
        PROMPT_SPACE_SUFFIX: Final[str] = " "
        DEFAULT_CHOICE_MESSAGE: Final[str] = "Choose an option:"
        CHOICE_HISTORY_FORMAT: Final[str] = "{message}{separator}{options}"

    class PromptsMessages:
        """Messages for prompts operations."""

        PLEASE_ENTER_YES_NO: Final[str] = "Please enter 'y', 'yes', 'n', or 'no'."
        USER_CANCELLED_CONFIRMATION: Final[str] = "User cancelled confirmation"
        INPUT_STREAM_ENDED: Final[str] = "Input stream ended"
        NO_OPTIONS_PROVIDED: Final[str] = "No options provided"
        PLEASE_ENTER_NUMBER_RANGE: Final[str] = (
            "Please enter a number between 1 and {count}."
        )
        PLEASE_ENTER_VALID_NUMBER: Final[str] = "Please enter a valid number."
        USER_CANCELLED_SELECTION: Final[str] = "User cancelled selection"
        PROCESSING: Final[str] = "Processing {count} items: {description}"
        PROGRESS_REPORT: Final[str] = (
            "Progress completed: {description}, processed: {count}"
        )
        USER_PROMPTED_LOG: Final[str] = "User prompted: {message}, input: {input}"
        STARTING_PROGRESS: Final[str] = "Starting progress: {description}"
        CREATED_PROGRESS: Final[str] = "Created progress: {description}"
        PROGRESS_OPERATION: Final[str] = (
            "Progress operation: {description} ({count} items)"
        )
        PROGRESS_COMPLETED: Final[str] = "Completed: {description}"
        PROGRESS_COMPLETED_LOG: Final[str] = (
            "Progress completed: {description}, processed: {processed}"
        )
        USER_SELECTION_LOG: Final[str] = "User selected: {message}, choice: {choice}"

    class PromptsErrorMessages:
        """Error messages for prompts operations."""

        PROMPT_FAILED: Final[str] = "Prompt failed: {error}"
        CONFIRMATION_FAILED: Final[str] = "Confirmation failed: {error}"
        SELECTION_FAILED: Final[str] = "Selection failed: {error}"
        CHOICE_REQUIRED: Final[str] = "Choice required. Available choices: {choices}"
        STATISTICS_COLLECTION_FAILED: Final[str] = (
            "Statistics collection failed: {error}"
        )
        PROMPT_SERVICE_EXECUTION_FAILED: Final[str] = (
            "Prompt service execution failed: {error}"
        )
        PRINT_STATUS_FAILED: Final[str] = "Print status failed: {error}"
        PRINT_SUCCESS_FAILED: Final[str] = "Print success failed: {error}"
        PRINT_ERROR_FAILED: Final[str] = "Print error failed: {error}"
        PRINT_WARNING_FAILED: Final[str] = "Print warning failed: {error}"
        PRINT_INFO_FAILED: Final[str] = "Print info failed: {error}"
        PROGRESS_CREATION_FAILED: Final[str] = "Progress creation failed: {error}"
        PROGRESS_PROCESSING_FAILED: Final[str] = "Progress processing failed: {error}"

    class PromptsDictKeys:
        """Dictionary keys specific to prompts operations."""

        DEFAULT_TIMEOUT: Final[str] = "default_timeout"
        HISTORY_SIZE: Final[str] = "history_size"
        TIMESTAMP: Final[str] = "timestamp"

    # Table formats for tabulate integration
    # Python 3.13+ best practice: Use Mapping for immutable read-only mappings
    TABLE_FORMATS: Final[Mapping[str, str]] = {
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

    class MixinsValidationMessages:
        """Validation error messages for mixins."""

        FIELD_CANNOT_BE_EMPTY: Final[str] = "{field_name} cannot be empty"
        INVALID_URL: Final[str] = "{field_name} is not a valid URL"
        VALIDATION_FAILED: Final[str] = "{field_name} validation failed: {error}"
        INVALID_ENUM_VALUE: Final[str] = (
            "Invalid {field_name}. Valid values: {valid_values}"
        )
        MUST_BE_POSITIVE: Final[str] = "{field_name} must be positive"
        CANNOT_BE_NEGATIVE: Final[str] = "{field_name} cannot be negative"
        COMMAND_STATE_INVALID: Final[str] = (
            "Cannot {operation}: command is in '{current_status}' state, "
            "requires '{required_status}'"
        )
        SESSION_STATUS_INVALID: Final[str] = (
            "Invalid session status '{current_status}'. Valid states: {valid_states}"
        )
        PIPELINE_STEP_EMPTY: Final[str] = "Pipeline step must be a non-empty dictionary"
        PIPELINE_STEP_NO_NAME: Final[str] = "Pipeline step must have a 'name' field"
        PIPELINE_STEP_NAME_EMPTY: Final[str] = "Pipeline step name cannot be empty"
        CONFIG_MISSING_FIELDS: Final[str] = (
            "Missing required configuration fields: {missing_fields}"
        )

    class MixinsFieldNames:
        """Field name constants for validation messages."""

        OUTPUT_FORMAT: Final[str] = "output format"
        LOG_LEVEL: Final[str] = "log level"
        STATUS: Final[str] = "status"
        PIPELINE_STEP_NAME: Final[str] = "name"

    class CommandsDefaults:
        """Commands service defaults and constants."""

        DEFAULT_CLI_NAME: Final[str] = "flext"
        DEFAULT_DESCRIPTION: Final[str] = ""
        OPTION_PREFIX: Final[str] = "--"

    class CommandsDictKeys:
        """Dictionary keys for command operations."""

        NAME: Final[str] = "name"
        HANDLER: Final[str] = "handler"
        DESCRIPTION: Final[str] = "description"
        STATUS: Final[str] = "status"
        SERVICE: Final[str] = "service"
        COMMANDS: Final[str] = "commands"

    class CommandsErrorMessages:
        """Error messages for commands operations."""

        COMMAND_NOT_FOUND: Final[str] = "Command '{name}' not found"
        COMMAND_NOT_FOUND_DETAIL: Final[str] = "Command not found: {command_name}"
        HANDLER_NOT_CALLABLE: Final[str] = "Handler is not callable: {command_name}"
        INVALID_COMMAND_STRUCTURE: Final[str] = (
            "Invalid command structure: {command_name}"
        )
        FAILED_LIST_COMMANDS: Final[str] = "Failed to list commands: {error}"

    class CommandsLogMessages:
        """Log messages for command operations."""

        CLI_EXECUTION_MODE: Final[str] = (
            "CLI execution mode: standalone={standalone_mode}, args={args}"
        )
        EXECUTING_COMMAND: Final[str] = (
            "Executing command {command_name} with timeout {timeout}s"
        )

    class FormattersDefaults:
        """Formatters service defaults and constants."""

        DEFAULT_SPINNER: Final[str] = "dots"
        DEFAULT_BORDER_STYLE: Final[str] = "blue"
        DEFAULT_REFRESH_RATE: Final[float] = 4.0
        TABLE_KEY_VALUE_COLUMNS: Final[int] = 2

    class FormattersErrorMessages:
        """Error messages for formatters operations."""

        PRINT_FAILED: Final[str] = "Print failed: {error}"
        TABLE_CREATION_FAILED: Final[str] = "Table creation failed: {error}"
        TABLE_RENDERING_FAILED: Final[str] = "Table rendering failed: {error}"
        PROGRESS_CREATION_FAILED: Final[str] = "Progress creation failed: {error}"
        TREE_CREATION_FAILED: Final[str] = "Tree creation failed: {error}"
        TREE_RENDERING_FAILED: Final[str] = "Tree rendering failed: {error}"
        STATUS_CREATION_FAILED: Final[str] = "Status creation failed: {error}"
        LIVE_CREATION_FAILED: Final[str] = "Live creation failed: {error}"
        LAYOUT_CREATION_FAILED: Final[str] = "Layout creation failed: {error}"
        PANEL_CREATION_FAILED: Final[str] = "Panel creation failed: {error}"

    class TablesDefaults:
        """Tables service defaults and constants."""

        DEFAULT_FLOAT_FORMAT: Final[str] = "g"
        DEFAULT_NUM_ALIGN: Final[str] = "decimal"
        DEFAULT_STR_ALIGN: Final[str] = "left"
        DEFAULT_MISSING_VALUE: Final[str] = ""

    class TablesErrorMessages:
        """Error messages for tables operations."""

        TABLE_DATA_EMPTY: Final[str] = "Table data cannot be empty"
        INVALID_TABLE_FORMAT: Final[str] = (
            "Invalid table format: {table_format}. Available: {available_formats}"
        )
        UNKNOWN_FORMAT: Final[str] = "Unknown format: {format_name}"
        TABLE_CREATION_FAILED: Final[str] = "Failed to create table: {error}"
        PRINT_FORMATS_FAILED: Final[str] = "Failed to print formats: {error}"

    class TablesLogMessages:
        """Log messages for tables operations."""

        TABLE_CREATED: Final[str] = "Created table"
        TABLE_FORMAT_KEY: Final[str] = "table_format"
        ROW_COUNT_KEY: Final[str] = "row_count"

    class CliParamsDefaults:
        """CLI parameters defaults and constants."""

        DEFAULT_HELP_TEXT_FORMAT: Final[str] = "Set {field_name}"
        CHOICES_HELP_SUFFIX: Final[str] = " (choices: {choices_str})"
        RANGE_HELP_SUFFIX: Final[str] = " [range: {minimum}-{maximum}]"
        VALID_LOG_FORMATS: Final[list[str]] = [
            "compact",
            "detailed",
            "full",
        ]
        VALID_OUTPUT_FORMATS: Final[list[str]] = [
            "table",
            "json",
            "yaml",
            "csv",
            "plain",
        ]
        FIELD_NAME_OVERRIDE_KEY: Final[str] = "field_name_override"

    class CliParamsErrorMessages:
        """Error messages for CLI parameters operations."""

        PARAMS_MANDATORY: Final[str] = (
            "Common CLI parameters are mandatory and cannot be disabled. "
            "All CLI commands must support --verbose, --quiet, --debug, "
            "--log-level, etc."
        )
        FIELD_NOT_FOUND: Final[str] = "Field '{field_name}' not found in FlextCliConfig"
        TRACE_REQUIRES_DEBUG: Final[str] = (
            "Trace mode requires debug mode to be enabled. "
            "Use --debug --trace together."
        )
        INVALID_LOG_LEVEL: Final[str] = (
            "Invalid log level: {log_level}. Must be one of: {valid}"
        )
        INVALID_LOG_FORMAT: Final[str] = (
            "Invalid log format: {log_format}. Must be one of: {valid}"
        )
        INVALID_OUTPUT_FORMAT: Final[str] = (
            "Invalid output format: {output_format}. Must be one of: {valid}"
        )
        APPLY_PARAMS_FAILED: Final[str] = (
            "Failed to apply CLI parameters to config: {error}"
        )
        CONFIGURE_LOGGER_FAILED: Final[str] = "Failed to configure logger: {error}"

    class CliParamsRegistry:
        """CLI parameter registry metadata and constants."""

        # Short flag constants for CLI parameters
        SHORT_FLAG_VERBOSE: Final[str] = "v"
        SHORT_FLAG_QUIET: Final[str] = "q"
        SHORT_FLAG_DEBUG: Final[str] = "d"
        SHORT_FLAG_TRACE: Final[str] = "t"
        SHORT_FLAG_LOG_LEVEL: Final[str] = "L"
        SHORT_FLAG_OUTPUT_FORMAT: Final[str] = "o"
        SHORT_FLAG_CONFIG_FILE: Final[str] = "c"

        # Priority constants for CLI parameters
        PRIORITY_VERBOSE: Final[int] = 1
        PRIORITY_QUIET: Final[int] = 2
        PRIORITY_DEBUG: Final[int] = 3
        PRIORITY_TRACE: Final[int] = 4
        PRIORITY_LOG_LEVEL: Final[int] = 5
        PRIORITY_LOG_FORMAT: Final[int] = 6
        PRIORITY_OUTPUT_FORMAT: Final[int] = 7
        PRIORITY_NO_COLOR: Final[int] = 8
        PRIORITY_CONFIG_FILE: Final[int] = 9

        # Registry metadata keys
        KEY_SHORT: Final[str] = "short"
        KEY_PRIORITY: Final[str] = "priority"
        KEY_CHOICES: Final[str] = "choices"
        KEY_CASE_SENSITIVE: Final[str] = "case_sensitive"
        KEY_FIELD_NAME_OVERRIDE: Final[str] = "field_name_override"

        # Field name override value
        LOG_FORMAT_OVERRIDE: Final[str] = "log-format"

        # Boolean values for registry metadata
        CASE_INSENSITIVE: Final[bool] = False
        CASE_SENSITIVE: Final[bool] = True

    class OutputDefaults:
        """Output service defaults and constants."""

        JSON_INDENT: Final[int] = 2
        YAML_DEFAULT_FLOW_STYLE: Final[bool] = False
        EMPTY_STYLE: Final[str] = ""
        DEFAULT_MESSAGE_TYPE: Final[str] = "info"
        DEFAULT_FORMAT_TYPE: Final[str] = "table"
        DEFAULT_TREE_TITLE: Final[str] = "Tree"
        TREE_BRANCH_LIST_SUFFIX: Final[str] = " (list)"
        TEST_INVALID_KEY: Final[str] = "invalid"
        WARNING_PREFIX: Final[str] = "Warning:"
        NEWLINE: Final[str] = "\n"
        TREE_VALUE_SEPARATOR: Final[str] = ": "

    class OutputFieldNames:
        """Field names for output operations."""

        KEY: Final[str] = "Key"
        VALUE: Final[str] = "Value"
        TREE: Final[str] = "Tree"

    class OutputErrorMessages:
        """Error messages for output operations."""

        NO_DATA_PROVIDED: Final[str] = "No data provided for table"
        TABLE_FORMAT_REQUIRED_DICT: Final[str] = (
            "Table format requires t.JsonDict or list of dicts"
        )
        TABLE_HEADERS_MUST_BE_LIST: Final[str] = (
            "Table headers must be a list for list of dicts data"
        )
        UNSUPPORTED_FORMAT_TYPE: Final[str] = "Unsupported format type: {format_type}"
        CREATE_FORMATTER_FAILED: Final[str] = "Failed to create formatter: {error}"
        CREATE_RICH_TABLE_FAILED: Final[str] = "Failed to create Rich table: {error}"

    class OutputLogMessages:
        """Log messages for output operations."""

        JSON_FORMAT_FAILED: Final[str] = "JSON formatting failed: {error}"
        YAML_FORMAT_FAILED: Final[str] = "YAML formatting failed: {error}"
        CSV_FORMAT_FAILED: Final[str] = "CSV formatting failed: {error}"
        TABLE_FORMAT_FAILED: Final[str] = "Failed to format table: {error}"
        TREE_FORMAT_FAILED: Final[str] = "Failed to format as tree: {error}"

    class ModelsDefaults:
        """Models service defaults and constants."""

        EMPTY_STRING: Final[str] = ""
        ZERO_FLOAT: Final[float] = 0.0
        ZERO_INT: Final[int] = 0
        FALSE_BOOL: Final[bool] = False
        DEFAULT_FIELD_DESCRIPTION: Final[str] = "{field_name} parameter"
        SERIALIZATION_VERSION: Final[str] = "2.11"
        MASKED_PATTERN_ASTERISK: Final[str] = "*"
        SESSION_ID_PREFIX: Final[str] = "session_"
        SESSION_DATETIME_FORMAT: Final[str] = "%Y%m%d_%H%M%S_%f"
        TYPE_MAP_DIMENSION: Final[int] = 6

    class ModelsFieldNames:
        """Field names used in models."""

        COMMAND: Final[str] = "command"
        EXECUTION_TIME: Final[str] = "execution_time"
        ID: Final[str] = "id"
        COMMAND_LINE: Final[str] = "command_line"
        STATUS: Final[str] = "status"
        EXIT_CODE: Final[str] = "exit_code"
        CREATED_AT: Final[str] = "created_at"
        SESSION_ID: Final[str] = "session_id"
        START_TIME: Final[str] = "start_time"
        END_TIME: Final[str] = "end_time"
        LAST_ACTIVITY: Final[str] = "last_activity"
        DURATION_SECONDS: Final[str] = "duration_seconds"
        SERVICE: Final[str] = "service"
        LEVEL: Final[str] = "level"
        COMMANDS: Final[str] = "commands"
        PASSWORD: Final[str] = "password"
        TOKEN: Final[str] = "token"
        SECRET: Final[str] = "secret"
        KEY: Final[str] = "key"
        AUTH: Final[str] = "auth"

    class ModelsErrorMessages:
        """Error messages for models operations."""

        REQUIRED_NESTED_CLASS_NOT_FOUND: Final[str] = (
            "Required nested class {class_name} not found"
        )
        FIELD_NO_TYPE_ANNOTATION: Final[str] = (
            "Field {field_name} has no type annotation"
        )
        COMMAND_LINE_CANNOT_BE_EMPTY: Final[str] = "Command line cannot be empty"
        INVALID_STATUS: Final[str] = (
            "Invalid status '{value}'. Must be one of: {allowed}"
        )
        COMMAND_WITH_EXIT_CODE_PENDING: Final[str] = (
            "Command with exit_code cannot have pending status"
        )
        COMMAND_WITH_OUTPUT_PENDING: Final[str] = (
            "Command with output cannot have pending status"
        )
        COMMAND_DATA_MUST_BE_DICT: Final[str] = "Command data must be a dictionary"
        COMMAND_FIELD_REQUIRED: Final[str] = "Command field is required"
        COMMAND_MUST_BE_STRING: Final[str] = "Command must be a string"
        COMMAND_ALREADY_EXISTS: Final[str] = "Command already exists in session"
        DURATION_CANNOT_BE_NEGATIVE: Final[str] = "duration_seconds cannot be negative"
        INVALID_DEBUG_LEVEL: Final[str] = (
            "Invalid debug level '{value}'. Must be one of: {allowed}"
        )
        CRITICAL_DEBUG_REQUIRES_MESSAGE: Final[str] = (
            "Debug level '{level}' requires a descriptive message"
        )
        FAILED_FIELD_CONVERSION: Final[str] = (
            "Failed to convert field {field_name}: {error}"
        )
        FAILED_MODEL_CONVERSION: Final[str] = (
            "Failed to convert model {model_name}: {error}"
        )
        FAILED_CLICK_OPTIONS_GENERATION: Final[str] = (
            "Failed to generate Click options for {model_name}: {error}"
        )
        FAILED_MODEL_CREATION_FROM_CLI: Final[str] = (
            "Failed to create {model_name} from CLI args: {error}"
        )
        INVALID_INPUT: Final[str] = "Invalid input: {error}"
        VALIDATION_FAILED_FOR_MODEL: Final[str] = (
            "Validation failed for {model_name}: {error}"
        )
        USER_ID_EMPTY: Final[str] = "User ID cannot be empty"
        COMMAND_WITH_EXIT_CODE_CANNOT_HAVE_PENDING_STATUS: Final[str] = (
            "Command with exit_code cannot have pending status"
        )
        COMMAND_WITH_OUTPUT_CANNOT_HAVE_PENDING_STATUS: Final[str] = (
            "Command with output cannot have pending status"
        )
        COMMAND_ALREADY_EXISTS_IN_SESSION: Final[str] = (
            "Command already exists in session"
        )
        DEBUG_LEVEL_REQUIRES_MESSAGE: Final[str] = (
            "Debug level '{level}' requires a descriptive message"
        )
        FAILED_TO_CONVERT_FIELD: Final[str] = (
            "Failed to convert field {field_name}: {error}"
        )
        FAILED_TO_CONVERT_MODEL: Final[str] = (
            "Failed to convert model {model_name}: {error}"
        )
        FAILED_TO_GENERATE_CLICK_OPTIONS: Final[str] = (
            "Failed to generate Click options for {model_name}: {error}"
        )
        FAILED_TO_CREATE_MODEL_FROM_CLI_ARGS: Final[str] = (
            "Failed to create {model_name} from CLI args: {error}"
        )

    class ModelsValidationMessages:
        """Validation messages for models."""

        INVALID_DEBUG_LEVEL: Final[str] = (
            "Invalid debug level '{level}'. Must be one of: {valid_levels}"
        )
        INVALID_STATUS_ENUM: Final[str] = (
            "Invalid {field_name}. Valid values: {valid_values}"
        )

    class ModelsJsonSchema:
        """JSON schema metadata for models."""

        TITLE: Final[str] = "FlextCliModels"
        DESCRIPTION: Final[str] = (
            "Comprehensive CLI domain models with enhanced runtime validation "
            "(Phases 7-8)"
        )
        EXAMPLE_COMMAND: Final[str] = "flext validate"
        EXAMPLE_ARGS: Final[str] = "validate"
        EXAMPLE_COMMAND_2: Final[str] = "flext deploy --env production"
        EXAMPLE_ARGS_2: Final[str] = "deploy"
        EXAMPLE_ARGS_3: Final[str] = "--env"
        EXAMPLE_ARGS_4: Final[str] = "production"

    class PydanticTypeNames:
        """Pydantic-specific type name constants."""

        UNDEFINED_TYPE: Final[str] = "PydanticUndefinedType"

    class ModelsTypeMapping:
        """Type mapping for Python to Click type conversion."""

        # Python 3.13+ best practice: Use Mapping for immutable read-only mappings
        TYPE_STR_MAP: Final[Mapping[str, str]] = {
            "str": "STRING",
            "int": "INT",
            "float": "FLOAT",
            "bool": "BOOL",
            "list": "STRING",
            "dict": "STRING",
        }

    class CliCommandDefaults:
        """CLI Command model defaults."""

        DEFAULT_OUTPUT: Final[str] = ""
        DEFAULT_ERROR_OUTPUT: Final[str] = ""
        DEFAULT_NAME: Final[str] = ""
        DEFAULT_DESCRIPTION: Final[str] = ""
        DEFAULT_USAGE: Final[str] = ""
        DEFAULT_ENTRY_POINT: Final[str] = ""
        DEFAULT_PLUGIN_VERSION: Final[str] = "default"

    class CliCommandDescriptions:
        """CLI Command field descriptions."""

        COMMAND_LINE: Final[str] = "Full command line string that was executed"
        ARGS: Final[str] = "Parsed command line arguments as list"
        STATUS: Final[str] = "Current execution status of the command"
        EXIT_CODE: Final[str] = "Process exit code (0 for success, non-zero for errors)"
        OUTPUT: Final[str] = "Standard output captured from command execution"
        ERROR_OUTPUT: Final[str] = (
            "Standard error output captured from command execution"
        )
        EXECUTION_TIME: Final[str] = "Command execution time in seconds"
        RESULT: Final[str] = "Structured result data from command execution"
        KWARGS: Final[str] = "Additional keyword arguments passed to command"
        NAME: Final[str] = "Command name or identifier"
        DESCRIPTION: Final[str] = "Human-readable command description"
        USAGE: Final[str] = "Command usage documentation"
        ENTRY_POINT: Final[str] = "Plugin or module entry point for this command"
        PLUGIN_VERSION: Final[str] = "Version of the plugin providing this command"

    class CliSessionDefaults:
        """CLI Session model defaults."""

        SESSION_ID_PREFIX: Final[str] = "session_"
        DATETIME_FORMAT: Final[str] = "%Y%m%d_%H%M%S_%f"
        ZERO_DURATION: Final[float] = 0.0
        DEFAULT_USER_ID: Final[str] = ""  # Empty string instead of None
        SECONDS_PER_MINUTE: Final[int] = 60

    class CliSessionDescriptions:
        """CLI Session field descriptions."""

        SESSION_ID: Final[str] = "Unique session identifier with timestamp"
        START_TIME: Final[str] = "Session start time in ISO 8601 format"
        END_TIME: Final[str] = "Session end time in ISO 8601 format"
        LAST_ACTIVITY: Final[str] = "Last activity timestamp in ISO 8601 format"
        INTERNAL_DURATION: Final[str] = (
            "Internal duration tracking field (use duration_seconds computed field)"
        )
        COMMANDS_EXECUTED: Final[str] = (
            "Total number of commands executed in this session"
        )
        COMMANDS: Final[str] = "List of commands executed in this session"
        STATUS: Final[str] = "Current session status"
        USER_ID: Final[str] = "User identifier associated with this session"

    class DebugInfoDefaults:
        """Debug Info model defaults."""

        DEFAULT_SERVICE: Final[str] = "FlextCliDebug"
        DEFAULT_STATUS: Final[str] = "operational"
        DEFAULT_LEVEL: Final[str] = "info"
        DEFAULT_MESSAGE: Final[str] = ""

    class DebugInfoDescriptions:
        """Debug Info field descriptions."""

        SERVICE: Final[str] = "Service name generating debug info"
        STATUS: Final[str] = "Current operational status"
        TIMESTAMP: Final[str] = "Timestamp when debug info was captured (UTC)"
        SYSTEM_INFO: Final[str] = "System information and environment details"
        CONFIG_INFO: Final[str] = "Configuration information (sensitive data masked)"
        LEVEL: Final[str] = "Debug information level"
        MESSAGE: Final[str] = "Human-readable debug message"

    class LoggingConfigDescriptions:
        """LoggingConfig field descriptions."""

        LOG_LEVEL: Final[str] = "Logging level for CLI operations"
        LOG_FORMAT: Final[str] = "Log message format string"
        CONSOLE_OUTPUT: Final[str] = "Enable console output for logs"
        LOG_FILE: Final[str] = "Optional file path for persistent logging"

    class CliParameterSpecDescriptions:
        """CliParameterSpec field descriptions."""

        NAME: Final[str] = "CLI parameter name (e.g., '--field-name')"
        FIELD_NAME: Final[str] = "Original Python field name"
        PARAM_TYPE: Final[str] = "Python type for the parameter"
        CLICK_TYPE: Final[str] = "Click type specification"
        REQUIRED: Final[str] = "Whether the parameter is required"
        DEFAULT: Final[str] = "Default value if any"
        HELP: Final[str] = "Help text from field description"
        VALIDATORS: Final[str] = "List of validation functions"
        METADATA: Final[str] = "Additional Pydantic metadata"

    class CliOptionSpecDescriptions:
        """CliOptionSpec field descriptions."""

        OPTION_NAME: Final[str] = "Full option name with dashes"
        PARAM_DECLS: Final[str] = "Parameter declarations"
        TYPE: Final[str] = "Click type object"
        DEFAULT: Final[str] = "Default value"
        HELP: Final[str] = "Help text"
        REQUIRED: Final[str] = "Whether option is required"
        SHOW_DEFAULT: Final[str] = "Whether to show default in help"
        METADATA: Final[str] = "Additional metadata"

    class CliCommandResultDescriptions:
        """CliCommandResult field descriptions."""

        ID: Final[str] = "Command unique identifier"
        COMMAND_LINE: Final[str] = "Full command line executed"
        STATUS: Final[str] = "Command execution status"
        EXIT_CODE: Final[str] = "Process exit code"
        CREATED_AT: Final[str] = "Command creation timestamp"
        EXECUTION_TIME: Final[str] = "Execution time in seconds"

    class CliDebugDataDescriptions:
        """CliDebugData field descriptions."""

        SERVICE: Final[str] = "Service name generating debug info"
        LEVEL: Final[str] = "Debug information level"
        STATUS: Final[str] = "Current operational status"
        HAS_SYSTEM_INFO: Final[str] = "Whether system info is available"
        HAS_CONFIG_INFO: Final[str] = "Whether config info is available"
        TOTAL_STATS: Final[str] = "Total count of diagnostic statistics"
        MESSAGE_LENGTH: Final[str] = "Length of debug message"
        AGE_SECONDS: Final[str] = "Age of debug info in seconds"

    class CliSessionDataDescriptions:
        """CliSessionData field descriptions."""

        SESSION_ID: Final[str] = "Unique session identifier"
        IS_ACTIVE: Final[str] = "Whether session is active"
        COMMANDS_COUNT: Final[str] = "Number of commands executed"
        DURATION_MINUTES: Final[str] = "Session duration in minutes"
        HAS_USER: Final[str] = "Whether session has associated user"
        LAST_ACTIVITY_AGE: Final[str] = "Time since last activity"

    class CliLoggingDataDescriptions:
        """CliLoggingData field descriptions."""

        LEVEL: Final[str] = "Logging level"
        FORMAT: Final[str] = "Log message format"
        CONSOLE_OUTPUT: Final[str] = "Console output enabled"
        LOG_FILE: Final[str] = "Log file path"
        HAS_FILE_OUTPUT: Final[str] = "File logging enabled"

    class ModelsExamples:
        """Example values for Pydantic model fields."""

        COMMAND_LINE_EXAMPLES: Final[list[str]] = [
            "flext validate",
            "flext deploy --env production",
        ]
        ARGS_EXAMPLES: Final[list[list[str]]] = [
            ["validate"],
            ["deploy", "--env", "production"],
        ]
        EXIT_CODE_EXAMPLES: Final[list[int]] = [0, 1, 127]
        EXECUTION_TIME_EXAMPLES: Final[list[float]] = [0.123, 5.678, 120.5]
        COMMAND_NAME_EXAMPLES: Final[list[str]] = ["validate", "deploy", "test"]
        SESSION_ID_EXAMPLES: Final[list[str]] = ["session_20250113_143022_123456"]
        START_TIME_EXAMPLES: Final[list[str]] = ["2025-01-13T14:30:22Z"]
        END_TIME_EXAMPLES: Final[list[str]] = ["2025-01-13T15:45:30Z"]
        LAST_ACTIVITY_EXAMPLES: Final[list[str]] = ["2025-01-13T15:30:00Z"]
        LOG_LEVEL_EXAMPLES: Final[list[str]] = [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]
        LOG_FORMAT_EXAMPLES: Final[list[str]] = [
            "%(levelname)s: %(message)s",
            "json",
            "plain",
        ]
        LOG_FILE_EXAMPLES: Final[list[str]] = [
            "/var/log/flext-cli.log",
            "~/.flext/cli.log",
        ]

    class CliGlobalDefaults:
        """Default values for CLI operations."""

        # Basic defaults
        DEFAULT_PROFILE: Final[str] = "default"
        DEFAULT_APP_NAME: Final[str] = "flext-cli"

        # Verbosity defaults
        DEFAULT_VERBOSITY: Final[str] = "verbose"
        QUIET_VERBOSITY: Final[str] = "quiet"
        NORMAL_VERBOSITY: Final[str] = "normal"

        # Service defaults
        DEFAULT_VERSION_STRING: Final[str] = "2.0.0"
        DEFAULT_SERVICE_NAME: Final[str] = "flext-cli-config"

        # Auto-refresh
        AUTO_REFRESH: Final[bool] = True
        DEFAULT_APP_DESCRIPTION_SUFFIX: Final[str] = " - FLEXT CLI Framework"
        DEFAULT_TIMEOUT: Final[int] = 30
        DEFAULT_LOG_LEVEL: Final[str] = "INFO"
        DEFAULT_VERSION: Final[str] = "2.0.0"

        # UI defaults
        DEFAULT_NO_COLOR: Final[bool] = False
        DEFAULT_AUTO_REFRESH: Final[bool] = True
        DEFAULT_VERBOSE: Final[bool] = False
        DEFAULT_DEBUG: Final[bool] = False
        DEFAULT_QUIET: Final[bool] = False
        DEFAULT_INTERACTIVE: Final[bool] = True
        DEFAULT_MAX_WIDTH: Final[int] = 120
        DEFAULT_ENVIRONMENT: Final[str] = "development"
        DEFAULT_CLI_LOG_LEVEL: Final[str] = "INFO"
        DEFAULT_LOG_VERBOSITY: Final[str] = "detailed"
        DEFAULT_CLI_LOG_VERBOSITY: Final[str] = "detailed"

    class Lists:
        """List constants."""

        LOG_LEVELS_LIST: Final[list[str]] = [
            "DEBUG",
            "INFO",
            "WARNING",
            "ERROR",
            "CRITICAL",
        ]


__all__ = [
    "FlextCliConstants",
]

"""FLEXT CLI Constants."""

from __future__ import annotations

from typing import ClassVar, Final

from flext_core import FlextConstants

# =============================================================================
# CLI-SPECIFIC CONSTANTS
# =============================================================================

# CLI-specific environment configuration
CLI_ENV_PREFIX: Final[str] = "FLEXT_CLI_"
CLI_PROFILE_ENV_VAR: Final[str] = "FLX_PROFILE"
CLI_DEBUG_ENV_VAR: Final[str] = "FLX_DEBUG"

# CLI-specific behavior defaults
DEFAULT_PROFILE: Final[str] = "default"
DEFAULT_CONFIRM_PROMPT: Final[str] = "Are you sure?"
DEFAULT_RICH_THEME: Final[str] = "monokai"

# CLI-specific output formats (extends core)
OUTPUT_FORMAT_RICH: Final[str] = "rich"
OUTPUT_FORMAT_PLAIN: Final[str] = "plain"

# CLI-specific validation (extends core limits)
MAX_COMMAND_LENGTH: Final[int] = 512
MAX_PROMPT_LENGTH: Final[int] = 256

# =============================================================================
# DELEGATE TO FLEXT-CORE CONSTANTS
# =============================================================================

# API defaults - delegate to flext-core Platform constants
DEFAULT_API_URL: str = f"{FlextConstants.Platform.DEFAULT_BASE_URL}:{FlextConstants.Platform.FLEXT_API_PORT}"
DEFAULT_TIMEOUT: int = FlextConstants.Defaults.TIMEOUT
DEFAULT_RETRIES: int = FlextConstants.Defaults.MAX_RETRIES

# Output defaults - delegate to flext-core
DEFAULT_OUTPUT_FORMAT: str = FlextConstants.Cli.DEFAULT_OUTPUT_FORMAT
DEFAULT_LOG_LEVEL: str = FlextConstants.Observability.DEFAULT_LOG_LEVEL

# CLI behavior - delegate to flext-core
DEFAULT_DEBUG: bool = False  # CLI-specific default

# Environment configuration - delegate to flext-core
ENV_PREFIX: str = CLI_ENV_PREFIX  # Use CLI-specific prefix
ENV_FILE: str = FlextConstants.Configuration.DOTENV_FILES[0]

# Validation limits - delegate to flext-core
MAX_TIMEOUT: int = FlextConstants.Limits.MAX_PORT  # Reuse appropriate limit
MIN_TIMEOUT: int = FlextConstants.Defaults.VALIDATION_TIMEOUT
MAX_RETRIES: int = 10  # CLI-specific limit

# Entity limits - delegate to flext-core
MAX_ENTITY_NAME_LENGTH: int = FlextConstants.Platform.MAX_NAME_LENGTH
MAX_ERROR_MESSAGE_LENGTH: int = FlextConstants.Limits.MAX_STRING_LENGTH


class FlextCliConstants:
    """CLI-specific constants that extend FlextConstants.

    This class provides CLI-specific constants while delegating
    to flext_core.FlextConstants for all shared constants.
    """

    # Delegate to core constants
    Core = FlextConstants.Core
    Errors = FlextConstants.Errors
    Messages = FlextConstants.Messages
    Status = FlextConstants.Status
    Patterns = FlextConstants.Patterns
    Defaults = FlextConstants.Defaults
    Limits = FlextConstants.Limits
    Performance = FlextConstants.Performance
    Configuration = FlextConstants.Configuration
    Infrastructure = FlextConstants.Infrastructure
    Models = FlextConstants.Models
    Observability = FlextConstants.Observability
    Platform = FlextConstants.Platform

    class CliErrors:
        """CLI-specific error messages."""

        # General CLI errors
        CLI_SETUP_FAILED: Final[str] = "CLI setup failed"
        CLI_CONTEXT_NOT_AVAILABLE: Final[str] = "CLI context not available"
        OPERATION_CANCELLED: Final[str] = "Operation cancelled by user"
        USER_INTERRUPTED: Final[str] = "User interrupted"

        # Authentication errors
        AUTH_TOKEN_SAVE_FAILED: Final[str] = "Failed to save auth token"
        AUTH_TOKEN_CLEAR_FAILED: Final[str] = "Failed to clear auth tokens"
        AUTH_REFRESH_TOKEN_SAVE_FAILED: Final[str] = "Failed to save refresh token"
        AUTH_NOT_AUTHENTICATED: Final[str] = "Not authenticated"
        AUTH_LOGIN_FAILED: Final[str] = "Login failed"
        AUTH_LOGOUT_FAILED: Final[str] = "Logout failed"
        AUTH_PASSWORD_EMPTY: Final[str] = "Password cannot be empty"
        AUTH_INVALID_RESPONSE: Final[str] = "Login failed: Invalid response"
        AUTH_NETWORK_ERROR: Final[str] = "Network error during login"
        AUTH_CHECK_FAILED: Final[str] = "Authentication check failed"
        AUTH_USER_INFO_FAILED: Final[str] = "Failed to get user info"

        # Command errors
        COMMAND_NOT_FOUND: Final[str] = "Command not found"
        COMMAND_EXECUTION_FAILED: Final[str] = "Command execution failed"
        COMMAND_EMPTY: Final[str] = "Command cannot be empty"
        COMMAND_LINE_EMPTY: Final[str] = "Command line cannot be empty"
        COMMAND_NAME_EMPTY: Final[str] = "Command name cannot be empty"
        HANDLER_NOT_CALLABLE: Final[str] = "Handler is not callable"

        # Session errors
        SESSION_NOT_FOUND: Final[str] = "Session not found"
        SESSION_ALREADY_EXISTS: Final[str] = "Session already exists in workspace"
        SESSION_VALIDATION_FAILED: Final[str] = "Session validation failed"
        SESSION_INACTIVE: Final[str] = "Cannot add commands to inactive session"
        SESSION_ALREADY_TERMINATED: Final[str] = "Session is already terminated"
        SESSION_WRONG_STATE: Final[str] = "Cannot perform operation in current state"

        # Plugin errors
        PLUGIN_NAME_EMPTY: Final[str] = "Plugin name cannot be empty"
        PLUGIN_ENTRY_POINT_EMPTY: Final[str] = "Entry point cannot be empty"
        PLUGIN_ALREADY_REGISTERED: Final[str] = "Plugin already registered"
        PLUGIN_ALREADY_INSTALLED: Final[str] = "Plugin already installed in workspace"
        PLUGIN_WRONG_STATE: Final[str] = "Cannot perform plugin operation in current state"
        PLUGIN_MUST_BE_ACTIVE: Final[str] = "Active plugin must have loaded_at timestamp"
        PLUGIN_UNLOADED: Final[str] = "Plugin is already unloaded"

        # Configuration errors
        CONFIG_FILE_NOT_FOUND: Final[str] = "Config file not found"
        CONFIG_UNSUPPORTED_FORMAT: Final[str] = "Unsupported config format"
        CONFIG_VALIDATION_FAILED: Final[str] = "Configuration validation failed"
        CONFIG_LOAD_FAILED: Final[str] = "Failed to load configuration"
        CONFIG_SAVE_FAILED: Final[str] = "Failed to save configuration"
        CONFIG_CREATION_FAILED: Final[str] = "Failed to create CLI configuration"
        CONFIG_ENV_FAILED: Final[str] = "Failed to create configuration from environment"

        # Validation errors
        VALIDATION_FAILED: Final[str] = "Validation failed"
        VALIDATION_EMAIL_INVALID: Final[str] = "Invalid email"
        VALIDATION_EMAIL_EMPTY: Final[str] = "Email cannot be empty"
        VALIDATION_EMAIL_FORMAT: Final[str] = "Invalid email format"
        VALIDATION_URL_INVALID: Final[str] = "Invalid URL"
        VALIDATION_URL_FORMAT: Final[str] = "Invalid URL format"
        VALIDATION_PATH_EMPTY: Final[str] = "Path cannot be empty"
        VALIDATION_PATH_NOT_EXISTS: Final[str] = "Path does not exist"
        VALIDATION_PATH_NOT_FILE: Final[str] = "Path must be a file"
        VALIDATION_PATH_NOT_DIR: Final[str] = "Path must be a directory"
        VALIDATION_FILENAME_EMPTY: Final[str] = "Filename cannot be empty"
        VALIDATION_INTEGER_INVALID: Final[str] = "Invalid integer"
        VALIDATION_TYPE_UNKNOWN: Final[str] = "Unknown validation type"

        # File operations errors
        FILE_NOT_FOUND: Final[str] = "File not found"
        FILE_UNSUPPORTED_FORMAT: Final[str] = "Unsupported file format"
        FILE_LOAD_FAILED: Final[str] = "Failed to load data file"
        FILE_SAVE_FAILED: Final[str] = "Failed to save data file"
        FILE_WRITE_FAILED: Final[str] = "Failed to write file"
        FILE_READ_FAILED: Final[str] = "Failed to read file"
        FILE_JSON_INVALID: Final[str] = "Invalid JSON"
        FILE_YAML_INVALID: Final[str] = "Invalid YAML"

        # Format errors
        FORMAT_INVALID: Final[str] = "Invalid format"
        FORMAT_UNSUPPORTED: Final[str] = "Unsupported format"
        FORMAT_ERROR: Final[str] = "Format error"
        FORMAT_TABLE_FAILED: Final[str] = "Table creation failed"
        FORMAT_OUTPUT_FAILED: Final[str] = "Output formatting failed"

        # Data errors
        DATA_EMPTY: Final[str] = "No data provided"
        DATA_INVALID: Final[str] = "Invalid data"
        DATA_MUST_BE_LIST: Final[str] = "Data must be a list"
        DATA_MUST_BE_DICT_LIST: Final[str] = "Data must be a list of dictionaries"
        DATA_EMPTY_LIST: Final[str] = "Cannot create table from empty list"

        # Service errors
        SERVICE_NAME_EMPTY: Final[str] = "Service name cannot be empty"
        SERVICE_NOT_IMPLEMENTED: Final[str] = "Service not implemented"
        SERVICE_CREATION_FAILED: Final[str] = "Failed to create service"
        SERVICE_UNHEALTHY: Final[str] = "Service unhealthy"
        SERVICE_CHECK_FAILED: Final[str] = "Service check failed"

        # Workspace errors
        WORKSPACE_NAME_EMPTY: Final[str] = "Workspace name cannot be empty"
        WORKSPACE_VALIDATION_FAILED: Final[str] = "Workspace validation failed"

        # Interactive errors
        USER_CANCELLED: Final[str] = "User cancelled"
        INPUT_CANCELLED: Final[str] = "Input cancelled"
        CONFIRMATION_CANCELLED: Final[str] = "Confirmation cancelled"
        INPUT_ERROR: Final[str] = "Input error"
        CONFIRMATION_ERROR: Final[str] = "Confirmation error"
        PROMPT_ERROR: Final[str] = "Prompt error"

        # API errors
        API_CLIENT_NOT_AVAILABLE: Final[str] = "API client not available"
        API_CLIENT_NOT_INITIALIZED: Final[str] = "API client not initialized"
        CONNECTION_FAILED: Final[str] = "Connection failed"
        HEALTH_CHECK_FAILED: Final[str] = "Health check failed"
        STATUS_REQUEST_FAILED: Final[str] = "Status request failed"
        SYSTEM_STATUS_FAILED: Final[str] = "System status failed"
        SERVICE_LISTING_FAILED: Final[str] = "Service listing failed"
        CLIENT_CREATION_FAILED: Final[str] = "Client creation failed"

        # Execution errors
        EXECUTION_FAILED: Final[str] = "Execution failed"
        PROCESSING_FAILED: Final[str] = "Processing failed"
        OPERATION_FAILED: Final[str] = "Operation failed"
        STEP_FAILED: Final[str] = "Step failed"
        HANDLER_FAILED: Final[str] = "Handler failed"
        TRANSFORMER_FAILED: Final[str] = "Transformer failed"
        SOURCE_FAILED: Final[str] = "Source failed"
        ALL_SOURCES_FAILED: Final[str] = "All sources failed"

        # Time validation errors
        TIME_NEGATIVE: Final[str] = "Time cannot be negative"
        TIME_END_BEFORE_START: Final[str] = "End time cannot be before start time"
        TIME_COMPLETION_BEFORE_START: Final[str] = "Completion time cannot be before start time"
        TIME_ACTIVITY_BEFORE_START: Final[str] = "Last activity cannot be before start time"
        TIME_TIMEOUT_EXCEEDED: Final[str] = "Timeout cannot exceed 24 hours"

        # Exit code validation
        EXIT_CODE_INVALID: Final[str] = "Exit code must be between 0 and 255"

        # State validation
        STATE_INVALID: Final[str] = "Invalid state"
        STATE_RUNNING_MUST_HAVE_START: Final[str] = "Running command must have started_at timestamp"
        STATE_COMMAND_NOT_IN_HISTORY: Final[str] = "Current command must be in command history"
        STATE_ONLY_CANCEL_RUNNING: Final[str] = "Can only cancel running commands"
        STATE_ONLY_SUSPEND_ACTIVE: Final[str] = "Can only suspend active sessions"
        STATE_ONLY_RESUME_SUSPENDED: Final[str] = "Can only resume suspended sessions"

        # Registry errors
        HANDLER_NOT_FOUND: Final[str] = "Handler not found"
        HANDLER_ALREADY_REGISTERED: Final[str] = "Handler already registered"
        REGISTRY_NOT_FOUND: Final[str] = "No handlers registry found"

        # Template errors
        TEMPLATE_PATTERNS_NOT_FOUND: Final[str] = "No template patterns found"
        TEMPLATE_PATTERNS_NOT_DICT: Final[str] = "No template patterns in dict"
        NOT_TEMPLATE_STRING: Final[str] = "Not a template string"
        TEMPLATE_RENDER_FAILED: Final[str] = "Failed to render with context"

        # Domain event errors
        DOMAIN_EVENT_FAILED: Final[str] = "Failed to add domain event"

        # Setup errors
        SETUP_FAILED: Final[str] = "Setup failed"
        SETUP_CANCELLED: Final[str] = "Setup cancelled"
        PROJECT_NAME_EMPTY: Final[str] = "Project name cannot be empty"

        # Sanitization errors
        SANITIZATION_FAILED: Final[str] = "Sanitization failed"
        FILENAME_SANITIZATION_FAILED: Final[str] = "Filename sanitization failed"

    class CliMessages:
        """CLI-specific user interface messages."""

        # Success messages
        SUCCESS_LOGIN: Final[str] = "Login successful!"
        SUCCESS_LOGOUT: Final[str] = "Logged out successfully"
        SUCCESS_OPERATION_COMPLETE: Final[str] = "Operation completed"
        SUCCESS_VALIDATION_PASSED: Final[str] = "Validation passed"
        SUCCESS_CONFIG_SAVED: Final[str] = "Configuration saved"
        SUCCESS_SETUP_COMPLETE: Final[str] = "Setup complete"
        SUCCESS_FILES_PROCESSED: Final[str] = "Files processed"

        # Process messages
        PROCESS_LOGGING_IN: Final[str] = "Logging in as"
        PROCESS_LOGGING_OUT: Final[str] = "Logging out..."
        PROCESS_CHECKING_AUTH: Final[str] = "Checking authentication..."
        PROCESS_TESTING_CONNECTION: Final[str] = "Testing API connectivity"
        PROCESS_CREATING_DIRECTORIES: Final[str] = "Creating directory structure..."
        PROCESS_CREATING_CONFIG: Final[str] = "Creating configuration files..."
        PROCESS_INITIALIZING_GIT: Final[str] = "Initializing git repository..."
        PROCESS_PROCESSING_STEP: Final[str] = "Processing step"

        # Status messages
        STATUS_AUTHENTICATED: Final[str] = "Authenticated"
        STATUS_NOT_AUTHENTICATED: Final[str] = "Not authenticated"
        STATUS_NOT_LOGGED_IN: Final[str] = "Not logged in"
        STATUS_SYSTEM_OK: Final[str] = "System OK"
        STATUS_CONNECTED: Final[str] = "Connected to API at"
        STATUS_VERSION: Final[str] = "version"
        STATUS_UPTIME: Final[str] = "uptime"

        # Info messages
        INFO_RUN_LOGIN: Final[str] = "Run 'flext auth login' to authenticate"
        INFO_RUN_REAUTH: Final[str] = "Run 'flext auth login' to re-authenticate"
        INFO_ANSWER_YN: Final[str] = "Please answer 'y' or 'n'"
        INFO_CONFIG_EDIT_MANUAL: Final[str] = "Edit the configuration file manually at"
        INFO_COMING_SOON: Final[str] = "Interactive mode coming soon!"
        INFO_USE_HELP: Final[str] = "Use 'flext --help' for currently available commands."

        # Warning messages
        WARNING_NO_PLUGINS: Final[str] = "No plugins found"
        WARNING_NO_PIPELINES: Final[str] = "No pipelines found"
        WARNING_GIT_INIT_FAILED: Final[str] = "Git init failed"
        WARNING_FILES_FAILED: Final[str] = "files failed"
        WARNING_NO_FLEXT_ENV: Final[str] = "No FLEXT environment variables found"
        WARNING_STATUS_FAILED: Final[str] = "Could not get system status"
        WARNING_TOKEN_CLEAR_FAILED: Final[str] = "Logged out, but failed to clear tokens"
        WARNING_LOGOUT_LOCAL: Final[str] = "Error during logout, logged out locally"

        # Confirmation prompts
        CONFIRM_SETUP: Final[str] = "Are you sure you want to proceed with setup?"
        CONFIRM_OPERATION: Final[str] = "Are you sure?"

        # Interactive mode info
        INTERACTIVE_COMING: Final[str] = "🚧 Interactive mode coming soon!"
        INTERACTIVE_PLANNED: Final[str] = "📋 Planned for Sprint 8 - will include:"
        INTERACTIVE_FEATURE_REPL: Final[str] = "• Rich REPL with syntax highlighting"
        INTERACTIVE_FEATURE_COMPLETION: Final[str] = "• Tab completion for commands"
        INTERACTIVE_FEATURE_HISTORY: Final[str] = "• Command history and search"
        INTERACTIVE_FEATURE_HELP: Final[str] = "• Context-aware help system"

        # Debug info
        DEBUG_CONFIGURATION: Final[str] = "Configuration"
        DEBUG_PYTHON_EXECUTABLE: Final[str] = "Python executable"
        DEBUG_PLATFORM: Final[str] = "Platform"
        DEBUG_SERVICE_CONNECTIVITY: Final[str] = "Service connectivity: not implemented"
        DEBUG_FLEXT_CORE_NOT_DETECTED: Final[str] = "flext-core version: not detected"
        DEBUG_INFORMATION: Final[str] = "Debug Information:"

        # Labels and headers
        LABEL_PROFILE: Final[str] = "Profile"
        LABEL_OUTPUT_FORMAT: Final[str] = "Output format"
        LABEL_DEBUG_MODE: Final[str] = "Debug mode"
        LABEL_USERNAME: Final[str] = "Username"
        LABEL_FULL_NAME: Final[str] = "Full Name"
        LABEL_EMAIL: Final[str] = "Email"
        LABEL_ROLE: Final[str] = "Role"
        LABEL_ID: Final[str] = "ID"
        LABEL_USER: Final[str] = "User"
        LABEL_TOTAL: Final[str] = "Total"
        LABEL_STATUS: Final[str] = "Status"
        LABEL_CREATED: Final[str] = "Created"
        LABEL_UPDATED: Final[str] = "Updated"
        LABEL_CONFIGURATION: Final[str] = "Configuration"
        LABEL_TAP: Final[str] = "Tap"
        LABEL_TARGET: Final[str] = "Target"
        LABEL_TRANSFORM: Final[str] = "Transform"
        LABEL_SCHEDULE: Final[str] = "Schedule"
        LABEL_CONFIG: Final[str] = "Config"
        LABEL_SET: Final[str] = "Set"
        LABEL_TRACING: Final[str] = "Tracing"

        # Status display
        STATUS_DISPLAY_CONFIG: Final[str] = "config shown"
        STATUS_DISPLAY_VALIDATION_OK: Final[str] = "Validation OK"
        STATUS_DISPLAY_PATHS: Final[str] = "Paths shown"
        STATUS_DISPLAY_CONFIG_READY: Final[str] = "Config file ready at"
        STATUS_DISPLAY_PROCESSED: Final[str] = "Processed"

        # Version info
        VERSION_CLI: Final[str] = "FLEXT CLI version"
        VERSION_PYTHON: Final[str] = "Python"
        VERSION_FLEXT_CORE: Final[str] = "flext-core"

        # Pipeline messages
        PIPELINE_TOTAL: Final[str] = "pipelines"

        # File operation messages
        FILE_DOES_NOT_EXIST: Final[str] = "File does not exist"

        # Generic placeholders
        UNKNOWN: Final[str] = "Unknown"
        NONE: Final[str] = "None"

    class CliOutput:
        """CLI output formatting constants."""

        # Rich markup tags
        SUCCESS_TAG: Final[str] = "[green]"
        ERROR_TAG: Final[str] = "[red]"
        WARNING_TAG: Final[str] = "[yellow]"
        INFO_TAG: Final[str] = "[blue]"
        DEBUG_TAG: Final[str] = "[dim]"
        BOLD_TAG: Final[str] = "[bold]"
        DIM_TAG: Final[str] = "[dim]"
        END_TAG: Final[str] = "[/]"

        # Icons and symbols
        ICON_SUCCESS: Final[str] = "✓"
        ICON_ERROR: Final[str] = "✗"
        ICON_WARNING: Final[str] = "⚠"
        ICON_INFO: Final[str] = "i"
        ICON_GEAR: Final[str] = "🔧"
        ICON_ROCKET: Final[str] = "🚧"
        ICON_CLIPBOARD: Final[str] = "📋"
        ICON_PARTY: Final[str] = "🎉"

        # Rich console prefixes
        PREFIX_SUCCESS: Final[str] = "[green][SUCCESS][/green]"
        PREFIX_ERROR: Final[str] = "[red][ERROR][/red]"
        PREFIX_WARNING: Final[str] = "[yellow][WARNING][/yellow]"
        PREFIX_INFO: Final[str] = "[blue][INFO][/blue]"
        PREFIX_DEBUG: Final[str] = "[dim][DEBUG][/dim]"
        PREFIX_VERBOSE: Final[str] = "[dim][VERBOSE][/dim]"

        # Bold prefixes with icons
        PREFIX_SUCCESS_BOLD: Final[str] = "[bold green]✓[/bold green]"
        PREFIX_ERROR_BOLD: Final[str] = "[bold red]✗[/bold red]"
        PREFIX_WARNING_BOLD: Final[str] = "[bold yellow]⚠[/bold yellow]"
        PREFIX_INFO_BOLD: Final[str] = "[bold blue]i[/bold blue]"

        # Special formatted messages
        SUCCESS_CHECKMARK: Final[str] = "[green]✅[/green]"
        ERROR_X: Final[str] = "[red]❌[/red]"
        WARNING_TRIANGLE: Final[str] = "[yellow]⚠️[/yellow]"

        # Output separators
        SEPARATOR: Final[str] = ": "
        BULLET: Final[str] = "• "
        INDENT: Final[str] = "  "
        DOUBLE_INDENT: Final[str] = "    "

    class Cli:
        """CLI-specific constants extending core CLI constants."""

        # Inherit from core
        HELP_ARGS = FlextConstants.Cli.HELP_ARGS
        VERSION_ARGS = FlextConstants.Cli.VERSION_ARGS
        CONFIG_ARGS = FlextConstants.Cli.CONFIG_ARGS
        VERBOSE_ARGS = FlextConstants.Cli.VERBOSE_ARGS
        OUTPUT_FORMATS = FlextConstants.Cli.OUTPUT_FORMATS
        DEFAULT_OUTPUT_FORMAT = FlextConstants.Cli.DEFAULT_OUTPUT_FORMAT
        SUCCESS_EXIT_CODE = FlextConstants.Cli.SUCCESS_EXIT_CODE
        ERROR_EXIT_CODE = FlextConstants.Cli.ERROR_EXIT_CODE
        INVALID_USAGE_EXIT_CODE = FlextConstants.Cli.INVALID_USAGE_EXIT_CODE

        # CLI-specific additions
        PROFILE_ARGS: ClassVar[list[str]] = ["--profile", "-p"]
        DEBUG_ARGS: ClassVar[list[str]] = ["--debug", "-d"]
        QUIET_ARGS: ClassVar[list[str]] = ["--quiet", "-q"]
        FORCE_ARGS: ClassVar[list[str]] = ["--force", "-f"]

        # Rich output formats
        RICH_FORMATS: ClassVar[list[str]] = ["rich", "table", "tree", "panel"]
        DEFAULT_RICH_FORMAT = "table"

        # Interactive mode
        INTERACTIVE_ARGS: ClassVar[list[str]] = ["--interactive", "-i"]
        INTERACTIVE_PROMPT = "flext> "

        # Command categories
        COMMAND_CATEGORIES: ClassVar[list[str]] = [
            "auth",
            "config",
            "pipeline",
            "service",
            "debug",
            "REDACTED_LDAP_BIND_PASSWORD",
        ]

    class Validation:
        """CLI-specific validation constants."""

        # Command validation
        MIN_COMMAND_LENGTH = 1
        MAX_COMMAND_LENGTH = MAX_COMMAND_LENGTH

        # Input validation
        MIN_INPUT_LENGTH = 1
        MAX_INPUT_LENGTH = FlextConstants.Limits.MAX_STRING_LENGTH

        # Prompt validation
        MIN_PROMPT_LENGTH = 1
        MAX_PROMPT_LENGTH = MAX_PROMPT_LENGTH

        # File path validation
        MAX_PATH_LENGTH = 4096

    class Display:
        """CLI display constants."""

        # Terminal dimensions
        DEFAULT_TERMINAL_WIDTH = 80
        DEFAULT_TERMINAL_HEIGHT = 24
        MIN_TERMINAL_WIDTH = 40

        # Table display
        DEFAULT_TABLE_WIDTH = 120
        MAX_COLUMN_WIDTH = 50

        # Progress indicators
        SPINNER_STYLE = "dots"
        PROGRESS_BAR_WIDTH = 40

        # Colors (Rich color names)
        SUCCESS_COLOR = "green"
        ERROR_COLOR = "red"
        WARNING_COLOR = "yellow"
        INFO_COLOR = "blue"
        DEBUG_COLOR = "magenta"

    class Examples:
        """Constants for examples and demos."""

        # Mock API failure rate (for examples only)
        MOCK_API_FAILURE_RATE = 0.3  # 30% chance of failure for demo purposes

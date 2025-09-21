"""Unified CLI configurations module with single FlextCliConfigs class.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This module consolidates ALL configuration-related functionality into a single
unified class following SOLID principles and flext-core patterns.
"""

from __future__ import annotations

from pathlib import Path
from typing import ClassVar

from flext_core.constants import FlextConstants
from pydantic import BaseModel, Field

from flext_core import FlextResult


class FlextCliLoggingConstants:
    """CLI-specific logging constants for FLEXT CLI module.

    Provides domain-specific logging defaults, levels, and configuration
    options tailored for command-line interface operations, user interactions,
    and CLI-specific performance monitoring.
    """

    # CLI-specific log levels
    DEFAULT_LEVEL = FlextConstants.Config.LogLevel.INFO
    COMMAND_LEVEL = FlextConstants.Config.LogLevel.INFO
    USER_INTERACTION_LEVEL = FlextConstants.Config.LogLevel.INFO
    ERROR_LEVEL = FlextConstants.Config.LogLevel.ERROR
    PERFORMANCE_LEVEL = FlextConstants.Config.LogLevel.WARNING
    DEBUG_LEVEL = FlextConstants.Config.LogLevel.DEBUG

    # Command execution logging
    LOG_COMMAND_EXECUTION = True
    LOG_COMMAND_ARGUMENTS = True
    LOG_COMMAND_OUTPUT = False  # Don't log command output by default
    LOG_COMMAND_ERRORS = True
    LOG_COMMAND_DURATION = True
    LOG_COMMAND_EXIT_CODE = True

    # User interaction logging
    LOG_USER_INPUT = False  # Don't log user input by default (privacy)
    LOG_USER_SELECTIONS = True
    LOG_USER_CONFIRMATIONS = True
    LOG_USER_CANCELLATIONS = True
    LOG_USER_ERRORS = True

    # Performance tracking for CLI operations
    TRACK_CLI_PERFORMANCE = True
    CLI_PERFORMANCE_THRESHOLD_WARNING = (
        FlextConstants.Performance.CLI_PERFORMANCE_WARNING_MS
    )
    CLI_PERFORMANCE_THRESHOLD_CRITICAL = (
        FlextConstants.Performance.CLI_PERFORMANCE_CRITICAL_MS
    )
    TRACK_MEMORY_USAGE = True
    HIGH_MEMORY_THRESHOLD = FlextConstants.Performance.HIGH_MEMORY_THRESHOLD_BYTES

    # Output and formatting logging
    LOG_OUTPUT_FORMATTING = False  # Don't log output formatting by default
    LOG_PROGRESS_UPDATES = True
    LOG_STATUS_UPDATES = True
    LOG_VERBOSE_OUTPUT = False  # Only log verbose output when explicitly enabled

    # Error handling and recovery
    LOG_ERROR_RECOVERY = True
    LOG_RETRY_ATTEMPTS = True
    LOG_FALLBACK_OPERATIONS = True
    LOG_VALIDATION_ERRORS = True
    LOG_CONFIGURATION_ERRORS = True

    # Context information to include
    INCLUDE_COMMAND_NAME = True
    INCLUDE_COMMAND_ARGS = True
    INCLUDE_USER_ID = False  # Don't include user ID by default (privacy)
    INCLUDE_SESSION_ID = True
    INCLUDE_WORKING_DIRECTORY = True
    INCLUDE_ENVIRONMENT_VARS = False  # Don't log env vars by default (security)

    # Interactive mode logging
    LOG_INTERACTIVE_MODE = True
    LOG_PROMPT_DISPLAYS = False  # Don't log prompts by default
    LOG_USER_RESPONSES = False  # Don't log user responses by default
    LOG_MENU_NAVIGATION = True
    LOG_HELP_REQUESTS = True

    # File and I/O operations
    LOG_FILE_OPERATIONS = True
    LOG_FILE_READS = False  # Don't log file reads by default
    LOG_FILE_WRITES = True
    LOG_FILE_DELETIONS = True
    LOG_DIRECTORY_OPERATIONS = True

    # Network operations
    LOG_NETWORK_REQUESTS = True
    LOG_NETWORK_RESPONSES = False  # Don't log network responses by default
    LOG_NETWORK_ERRORS = True
    LOG_CONNECTION_ATTEMPTS = True

    # Message templates for CLI operations
    class Messages:
        """CLI-specific log message templates."""

        # Command execution messages
        COMMAND_STARTED = "CLI command started: {command} with args: {args}"
        COMMAND_COMPLETED = "CLI command completed: {command} exit_code: {exit_code} duration: {duration}ms"
        COMMAND_FAILED = (
            "CLI command failed: {command} error: {error} exit_code: {exit_code}"
        )
        COMMAND_CANCELLED = "CLI command cancelled: {command} by user"

        # User interaction messages
        USER_PROMPT_DISPLAYED = "User prompt displayed: {prompt_type}"
        USER_RESPONSE_RECEIVED = "User response received: {response_type}"
        USER_CONFIRMATION = "User confirmation: {action} confirmed: {confirmed}"
        USER_CANCELLATION = "User cancelled operation: {operation}"

        # Error messages
        COMMAND_ERROR = "CLI command error: {command} {error}"
        VALIDATION_ERROR = "CLI validation error: {field} {error}"
        CONFIGURATION_ERROR = "CLI configuration error: {error}"
        NETWORK_ERROR = "CLI network error: {operation} {error}"
        FILE_ERROR = "CLI file error: {operation} {file_path} {error}"

        # Performance messages
        SLOW_COMMAND = "Slow CLI command: {command} took {duration}ms"
        HIGH_MEMORY_USAGE = "High memory usage for CLI command: {command} {memory}MB"
        LARGE_OUTPUT = "Large CLI output: {command} {size} bytes"

        # Interactive mode messages
        INTERACTIVE_MODE_STARTED = "Interactive mode started"
        INTERACTIVE_MODE_ENDED = "Interactive mode ended"
        MENU_DISPLAYED = "Menu displayed: {menu_name}"
        MENU_SELECTION = "Menu selection: {menu_name} option: {option}"
        HELP_REQUESTED = "Help requested for: {topic}"

        # File operation messages
        FILE_READ = "File read: {file_path} {size} bytes"
        FILE_WRITTEN = "File written: {file_path} {size} bytes"
        FILE_DELETED = "File deleted: {file_path}"
        DIRECTORY_CREATED = "Directory created: {directory_path}"
        DIRECTORY_DELETED = "Directory deleted: {directory_path}"

        # Network operation messages
        NETWORK_REQUEST = "Network request: {method} {url}"
        NETWORK_RESPONSE = "Network response: {status_code} {url} {size} bytes"
        CONNECTION_ESTABLISHED = "Connection established: {host}:{port}"
        CONNECTION_FAILED = "Connection failed: {host}:{port} {error}"

        # Configuration messages
        CONFIG_LOADED = "CLI configuration loaded from: {source}"
        CONFIG_SAVED = "CLI configuration saved to: {destination}"
        CONFIG_VALIDATED = "CLI configuration validated"
        CONFIG_ERROR = "CLI configuration error: {error}"

        # Progress and status messages
        PROGRESS_UPDATE = (
            "Progress update: {operation} {current}/{total} ({percentage}%)"
        )
        STATUS_UPDATE = "Status update: {status} for {operation}"
        TASK_STARTED = "Task started: {task_name}"
        TASK_COMPLETED = "Task completed: {task_name} duration: {duration}ms"
        TASK_FAILED = "Task failed: {task_name} error: {error}"

    # Environment-specific overrides for CLI logging
    class Environment:
        """Environment-specific CLI logging configuration."""

        DEVELOPMENT: ClassVar[dict[str, object]] = {
            "log_command_output": True,  # Log command output in dev
            "log_user_input": True,  # Log user input in dev
            "log_verbose_output": True,  # Log verbose output in dev
            "log_environment_vars": True,  # Log env vars in dev
            "audit_log_level": FlextConstants.Config.LogLevel.DEBUG,
        }

        STAGING: ClassVar[dict[str, object]] = {
            "log_command_output": False,
            "log_user_input": False,
            "log_verbose_output": False,
            "log_environment_vars": False,
            "audit_log_level": FlextConstants.Config.LogLevel.INFO,
        }

        PRODUCTION: ClassVar[dict[str, object]] = {
            "log_command_output": False,
            "log_user_input": False,
            "log_verbose_output": False,
            "log_environment_vars": False,
            "audit_log_level": FlextConstants.Config.LogLevel.WARNING,
        }

        TESTING: ClassVar[dict[str, object]] = {
            "log_command_output": True,
            "log_user_input": True,
            "log_verbose_output": True,
            "log_environment_vars": True,
            "audit_log_level": FlextConstants.Config.LogLevel.DEBUG,
        }


# Simple directory manager for CLI paths
class DirectoryManager:
    """Simple directory manager for CLI paths."""

    @staticmethod
    def base_dir() -> Path:
        """Get base configuration directory.

        Returns:
            Path: Base configuration directory path.

        """
        return Path.home() / ".flext"

    @staticmethod
    def cache_dir() -> Path:
        """Get cache directory.

        Returns:
            Path: Cache directory path.

        """
        return Path.home() / ".flext" / "cache"

    @staticmethod
    def log_dir() -> Path:
        """Get log directory.

        Returns:
            Path: Log directory path.

        """
        return Path.home() / ".flext" / "logs"

    @staticmethod
    def data_dir() -> Path:
        """Get data directory.

        Returns:
            Path: Data directory path.

        """
        return Path.home() / ".flext" / "data"


# Global instance storage
_global_instance: FlextCliConfigs | None = None


class FlextCliConfigs(BaseModel):
    """CLI configuration management - minimal implementation to fix import errors."""

    # Core configuration fields
    profile: str = Field(default="default", description="Configuration profile")
    debug: bool = Field(default=False, description="Enable debug mode")
    output_format: str = Field(default="table", description="Output format")
    project_name: str = Field(default="flext-cli", description="Project name")
    project_description: str = Field(
        default="FLEXT CLI - Developer Command Line Interface",
        description="Project description",
    )
    project_version: str = Field(
        default=FlextConstants.Core.VERSION, description="Project version"
    )

    # API configuration
    api_url: str = Field(default="http://localhost:8000", description="API URL")
    api_timeout: int = Field(default=30, description="API timeout")
    connect_timeout: int = Field(default=30, description="Connection timeout")
    read_timeout: int = Field(default=60, description="Read timeout")
    retries: int = Field(default=3, description="Number of retries")
    verify_ssl: bool = Field(default=True, description="Verify SSL certificates")

    # CLI behavior
    no_color: bool = Field(default=False, description="Disable colored output")
    quiet: bool = Field(default=False, description="Quiet mode")
    verbose: bool = Field(default=False, description="Verbose mode")
    pager: str | None = Field(default=None, description="Pager command")

    # Logging and timeouts
    log_level: str = Field(default="INFO", description="Log level")
    timeout_seconds: int = Field(default=30, description="Timeout in seconds")
    max_command_retries: int = Field(default=5, description="Maximum command retries")
    auto_refresh: bool = Field(default=True, description="Auto refresh tokens")

    # File paths
    token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "token",
        description="Token file path",
    )
    refresh_token_file: Path = Field(
        default_factory=lambda: Path.home() / ".flext" / "refresh_token",
        description="Refresh token file path",
    )
    config_dir: Path = Field(
        default_factory=DirectoryManager.base_dir, description="Config directory"
    )
    cache_dir: Path = Field(
        default_factory=DirectoryManager.cache_dir, description="Cache directory"
    )
    log_dir: Path = Field(
        default_factory=DirectoryManager.log_dir, description="Log directory"
    )
    data_dir: Path = Field(
        default_factory=DirectoryManager.data_dir, description="Data directory"
    )

    @classmethod
    def get_global_instance(cls) -> FlextCliConfigs:
        """Get global instance - simple implementation.

        Returns:
            FlextCliConfigs: Global configuration instance.

        """
        global _global_instance
        if _global_instance is None:
            _global_instance = cls()
        return _global_instance

    @classmethod
    def get_current(cls) -> FlextCliConfigs:
        """Get current instance.

        Returns:
            FlextCliConfigs: Current configuration instance.

        """
        return cls.get_global_instance()

    @classmethod
    def clear_global_instance(cls) -> None:
        """Clear global instance."""
        global _global_instance
        _global_instance = None

    @classmethod
    def set_global_instance(cls, instance: FlextCliConfigs) -> None:
        """Set global instance."""
        global _global_instance
        _global_instance = instance

    @classmethod
    def apply_cli_overrides(
        cls, overrides: dict[str, object]
    ) -> FlextResult[FlextCliConfigs]:
        """Apply CLI overrides.

        Returns:
            FlextResult[FlextCliConfigs]: Result with updated configuration.

        """
        try:
            config = cls.get_global_instance()
            for key, value in overrides.items():
                if hasattr(config, key):
                    setattr(config, key, value)
            return FlextResult[FlextCliConfigs].ok(config)
        except Exception as e:
            return FlextResult[FlextCliConfigs].fail(f"Failed to apply overrides: {e}")

    @classmethod
    def sync_with_flext_config(cls) -> FlextResult[None]:
        """Sync with flext config.

        Returns:
            FlextResult[None]: Success result.

        """
        return FlextResult[None].ok(None)

    @classmethod
    def ensure_flext_config_integration(cls) -> None:
        """Ensure flext config integration."""

    @classmethod
    def create_development_config(cls) -> FlextResult[FlextCliConfigs]:
        """Create development config.

        Returns:
            FlextResult[FlextCliConfigs]: Development configuration.

        """
        return FlextResult[FlextCliConfigs].ok(cls(debug=True, profile="development"))

    @classmethod
    def create_production_config(cls) -> FlextResult[FlextCliConfigs]:
        """Create production config.

        Returns:
            FlextResult[FlextCliConfigs]: Production configuration.

        """
        return FlextResult[FlextCliConfigs].ok(cls(debug=False, profile="production"))

    @classmethod
    def load_from_profile(cls, profile: str) -> FlextResult[FlextCliConfigs]:
        """Load from profile.

        Returns:
            FlextResult[FlextCliConfigs]: Configuration for the profile.

        """
        return FlextResult[FlextCliConfigs].ok(cls(profile=profile))

    @classmethod
    def create_with_directories(
        cls, config_data: dict[str, object]
    ) -> FlextResult[FlextCliConfigs]:
        """Create with directories.

        Returns:
            FlextResult[FlextCliConfigs]: Configuration with custom directories.

        """
        return FlextResult[FlextCliConfigs].ok(cls(**config_data))

    def model_dump(self) -> dict[str, object]:
        """Convert configuration to dictionary for serialization.

        Returns:
            dict[str, object]: Configuration as dictionary.

        """
        return {
            "profile": self.profile,
            "debug": self.debug,
            "output_format": self.output_format,
            "project_name": self.project_name,
            "project_description": self.project_description,
            "project_version": self.project_version,
            "api_url": self.api_url,
            "api_timeout": self.api_timeout,
            "connect_timeout": self.connect_timeout,
            "read_timeout": self.read_timeout,
            "retries": self.retries,
            "verify_ssl": self.verify_ssl,
            "no_color": self.no_color,
            "quiet": self.quiet,
            "verbose": self.verbose,
            "pager": self.pager,
            "timeout_seconds": self.timeout_seconds,
            "auto_refresh": self.auto_refresh,
            "max_command_retries": self.max_command_retries,
        }

    def validate_business_rules(self) -> FlextResult[None]:
        """Validate business rules for configuration.

        Returns:
            FlextResult[None]: Validation result.

        """
        # Basic validation - all required fields should be present
        if not self.profile:
            return FlextResult[None].fail("Profile is required")
        if not self.project_name:
            return FlextResult[None].fail("Project name is required")
        if self.api_timeout <= 0:
            return FlextResult[None].fail("API timeout must be positive")
        if self.retries < 0:
            return FlextResult[None].fail("Retries must be non-negative")

        return FlextResult[None].ok(None)


class FlextCliLoggingConfig:
    """CLI-specific logging configuration using FlextCliLoggingConstants."""

    def __init__(self) -> None:
        """Initialize with default values from FlextCliLoggingConstants."""
        self.log_command_execution = FlextCliLoggingConstants.LOG_COMMAND_EXECUTION
        self.log_command_arguments = FlextCliLoggingConstants.LOG_COMMAND_ARGUMENTS
        self.log_command_output = FlextCliLoggingConstants.LOG_COMMAND_OUTPUT

    log_command_arguments: bool = Field(
        default=FlextCliLoggingConstants.LOG_COMMAND_ARGUMENTS,
        description="Log command arguments",
    )

    log_command_output: bool = Field(
        default=FlextCliLoggingConstants.LOG_COMMAND_OUTPUT,
        description="Log command output",
    )

    log_command_errors: bool = Field(
        default=FlextCliLoggingConstants.LOG_COMMAND_ERRORS,
        description="Log command errors",
    )

    log_command_duration: bool = Field(
        default=FlextCliLoggingConstants.LOG_COMMAND_DURATION,
        description="Log command execution duration",
    )

    log_command_exit_code: bool = Field(
        default=FlextCliLoggingConstants.LOG_COMMAND_EXIT_CODE,
        description="Log command exit codes",
    )

    # User interaction logging
    log_user_input: bool = Field(
        default=FlextCliLoggingConstants.LOG_USER_INPUT,
        description="Log user input (privacy consideration)",
    )

    log_user_selections: bool = Field(
        default=FlextCliLoggingConstants.LOG_USER_SELECTIONS,
        description="Log user selections",
    )

    log_user_confirmations: bool = Field(
        default=FlextCliLoggingConstants.LOG_USER_CONFIRMATIONS,
        description="Log user confirmations",
    )

    log_user_cancellations: bool = Field(
        default=FlextCliLoggingConstants.LOG_USER_CANCELLATIONS,
        description="Log user cancellations",
    )

    log_user_errors: bool = Field(
        default=FlextCliLoggingConstants.LOG_USER_ERRORS,
        description="Log user errors",
    )

    # Performance tracking for CLI operations
    track_cli_performance: bool = Field(
        default=FlextCliLoggingConstants.TRACK_CLI_PERFORMANCE,
        description="Track CLI performance metrics",
    )

    cli_performance_threshold_warning: float = Field(
        default=FlextCliLoggingConstants.CLI_PERFORMANCE_THRESHOLD_WARNING,
        description="CLI performance warning threshold in milliseconds",
    )

    cli_performance_threshold_critical: float = Field(
        default=FlextCliLoggingConstants.CLI_PERFORMANCE_THRESHOLD_CRITICAL,
        description="CLI performance critical threshold in milliseconds",
    )

    track_memory_usage: bool = Field(
        default=FlextCliLoggingConstants.TRACK_MEMORY_USAGE,
        description="Track memory usage",
    )

    high_memory_threshold: int = Field(
        default=FlextCliLoggingConstants.HIGH_MEMORY_THRESHOLD,
        description="High memory usage threshold in bytes",
    )

    # Output and formatting logging
    log_output_formatting: bool = Field(
        default=FlextCliLoggingConstants.LOG_OUTPUT_FORMATTING,
        description="Log output formatting details",
    )

    log_progress_updates: bool = Field(
        default=FlextCliLoggingConstants.LOG_PROGRESS_UPDATES,
        description="Log progress updates",
    )

    log_status_updates: bool = Field(
        default=FlextCliLoggingConstants.LOG_STATUS_UPDATES,
        description="Log status updates",
    )

    log_verbose_output: bool = Field(
        default=FlextCliLoggingConstants.LOG_VERBOSE_OUTPUT,
        description="Log verbose output details",
    )

    # Error handling and recovery
    log_error_recovery: bool = Field(
        default=FlextCliLoggingConstants.LOG_ERROR_RECOVERY,
        description="Log error recovery attempts",
    )

    log_retry_attempts: bool = Field(
        default=FlextCliLoggingConstants.LOG_RETRY_ATTEMPTS,
        description="Log retry attempts",
    )

    log_fallback_operations: bool = Field(
        default=FlextCliLoggingConstants.LOG_FALLBACK_OPERATIONS,
        description="Log fallback operations",
    )

    log_validation_errors: bool = Field(
        default=FlextCliLoggingConstants.LOG_VALIDATION_ERRORS,
        description="Log validation errors",
    )

    log_configuration_errors: bool = Field(
        default=FlextCliLoggingConstants.LOG_CONFIGURATION_ERRORS,
        description="Log configuration errors",
    )

    # Context information to include in logs
    include_command_name: bool = Field(
        default=FlextCliLoggingConstants.INCLUDE_COMMAND_NAME,
        description="Include command name in log messages",
    )

    include_command_args: bool = Field(
        default=FlextCliLoggingConstants.INCLUDE_COMMAND_ARGS,
        description="Include command arguments in log messages",
    )

    include_user_id: bool = Field(
        default=FlextCliLoggingConstants.INCLUDE_USER_ID,
        description="Include user ID in log messages (privacy consideration)",
    )

    include_session_id: bool = Field(
        default=FlextCliLoggingConstants.INCLUDE_SESSION_ID,
        description="Include session ID in log messages",
    )

    include_working_directory: bool = Field(
        default=FlextCliLoggingConstants.INCLUDE_WORKING_DIRECTORY,
        description="Include working directory in log messages",
    )

    include_environment_vars: bool = Field(
        default=FlextCliLoggingConstants.INCLUDE_ENVIRONMENT_VARS,
        description="Include environment variables in log messages (security consideration)",
    )

    # Interactive mode logging
    log_interactive_mode: bool = Field(
        default=FlextCliLoggingConstants.LOG_INTERACTIVE_MODE,
        description="Log interactive mode events",
    )

    log_prompt_displays: bool = Field(
        default=FlextCliLoggingConstants.LOG_PROMPT_DISPLAYS,
        description="Log prompt displays",
    )

    log_user_responses: bool = Field(
        default=FlextCliLoggingConstants.LOG_USER_RESPONSES,
        description="Log user responses (privacy consideration)",
    )

    log_menu_navigation: bool = Field(
        default=FlextCliLoggingConstants.LOG_MENU_NAVIGATION,
        description="Log menu navigation",
    )

    log_help_requests: bool = Field(
        default=FlextCliLoggingConstants.LOG_HELP_REQUESTS,
        description="Log help requests",
    )

    # File and I/O operations
    log_file_operations: bool = Field(
        default=FlextCliLoggingConstants.LOG_FILE_OPERATIONS,
        description="Log file operations",
    )

    log_file_reads: bool = Field(
        default=FlextCliLoggingConstants.LOG_FILE_READS,
        description="Log file read operations",
    )

    log_file_writes: bool = Field(
        default=FlextCliLoggingConstants.LOG_FILE_WRITES,
        description="Log file write operations",
    )

    log_file_deletions: bool = Field(
        default=FlextCliLoggingConstants.LOG_FILE_DELETIONS,
        description="Log file deletion operations",
    )

    log_directory_operations: bool = Field(
        default=FlextCliLoggingConstants.LOG_DIRECTORY_OPERATIONS,
        description="Log directory operations",
    )

    # Network operations
    log_network_requests: bool = Field(
        default=FlextCliLoggingConstants.LOG_NETWORK_REQUESTS,
        description="Log network requests",
    )

    log_network_responses: bool = Field(
        default=FlextCliLoggingConstants.LOG_NETWORK_RESPONSES,
        description="Log network responses",
    )

    log_network_errors: bool = Field(
        default=FlextCliLoggingConstants.LOG_NETWORK_ERRORS,
        description="Log network errors",
    )

    log_connection_attempts: bool = Field(
        default=FlextCliLoggingConstants.LOG_CONNECTION_ATTEMPTS,
        description="Log connection attempts",
    )

    def get_cli_logging_config(self) -> dict[str, object]:
        """Get CLI-specific logging configuration dictionary.

        Returns:
            dict[str, object]: Logging configuration dictionary.

        """
        return {
            "log_command_execution": self.log_command_execution,
            "log_command_arguments": self.log_command_arguments,
            "log_command_output": self.log_command_output,
            "log_command_errors": self.log_command_errors,
            "log_command_duration": self.log_command_duration,
            "log_command_exit_code": self.log_command_exit_code,
            "log_user_input": self.log_user_input,
            "log_user_selections": self.log_user_selections,
            "log_user_confirmations": self.log_user_confirmations,
            "log_user_cancellations": self.log_user_cancellations,
            "log_user_errors": self.log_user_errors,
            "track_cli_performance": self.track_cli_performance,
            "cli_performance_threshold_warning": self.cli_performance_threshold_warning,
            "cli_performance_threshold_critical": self.cli_performance_threshold_critical,
            "track_memory_usage": self.track_memory_usage,
            "high_memory_threshold": self.high_memory_threshold,
            "log_output_formatting": self.log_output_formatting,
            "log_progress_updates": self.log_progress_updates,
            "log_status_updates": self.log_status_updates,
            "log_verbose_output": self.log_verbose_output,
            "log_error_recovery": self.log_error_recovery,
            "log_retry_attempts": self.log_retry_attempts,
            "log_fallback_operations": self.log_fallback_operations,
            "log_validation_errors": self.log_validation_errors,
            "log_configuration_errors": self.log_configuration_errors,
            "include_command_name": self.include_command_name,
            "include_command_args": self.include_command_args,
            "include_user_id": self.include_user_id,
            "include_session_id": self.include_session_id,
            "include_working_directory": self.include_working_directory,
            "include_environment_vars": self.include_environment_vars,
            "log_interactive_mode": self.log_interactive_mode,
            "log_prompt_displays": self.log_prompt_displays,
            "log_user_responses": self.log_user_responses,
            "log_menu_navigation": self.log_menu_navigation,
            "log_help_requests": self.log_help_requests,
            "log_file_operations": self.log_file_operations,
            "log_file_reads": self.log_file_reads,
            "log_file_writes": self.log_file_writes,
            "log_file_deletions": self.log_file_deletions,
            "log_directory_operations": self.log_directory_operations,
            "log_network_requests": self.log_network_requests,
            "log_network_responses": self.log_network_responses,
            "log_network_errors": self.log_network_errors,
            "log_connection_attempts": self.log_connection_attempts,
        }


__all__ = ["FlextCliConfigs"]

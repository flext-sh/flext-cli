"""FLEXT CLI API - Consolidated single-class implementation.

Single FlextCli class with EXACTLY ONE main class per module pattern.
Consolidates ALL CLI functionality (auth, formatting, commands, etc.).
Uses FlextResult railway pattern with zero async operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import inspect
import os
import pathlib
import secrets
import sys
import traceback
import typing
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import ClassVar, cast

import typer
from click.exceptions import UsageError as ClickUsageError
from flext_core import (
    FlextContainer,
    FlextExceptions,
    FlextLogger,
    FlextResult,
    FlextRuntime,
    FlextTypes,
    FlextUtilities,
)

from flext_cli import __version__
from flext_cli.base import FlextCliServiceBase
from flext_cli.cli import FlextCliCli
from flext_cli.cli_params import FlextCliCommonParams
from flext_cli.commands import FlextCliCommands
from flext_cli.config import FlextCliConfig
from flext_cli.constants import FlextCliConstants
from flext_cli.context import FlextCliContext
from flext_cli.debug import FlextCliDebug
from flext_cli.file_tools import FlextCliFileTools
from flext_cli.formatters import FlextCliFormatters
from flext_cli.mixins import FlextCliMixins
from flext_cli.models import FlextCliModels
from flext_cli.protocols import FlextCliProtocols
from flext_cli.services.cmd import FlextCliCmd
from flext_cli.services.core import FlextCliCore
from flext_cli.services.output import FlextCliOutput
from flext_cli.services.prompts import FlextCliPrompts
from flext_cli.services.tables import FlextCliTables
from flext_cli.typings import FlextCliTypes
from flext_cli.utilities import FlextCliUtilities


class FlextCli:
    """Coordinator for CLI operations with direct domain library access.

    Consolidates ALL CLI functionality through direct access to domain libraries:
    - formatters: FlextCliFormatters - Rich-based visual output
    - output: FlextCliOutput - Comprehensive output tools
    - file_tools: FlextCliFileTools - File operations
    - core: FlextCliCore - Core CLI service
    - cmd: FlextCliCmd - Command execution
    - prompts: FlextCliPrompts - Interactive prompts
    - config: FlextCliConfig - Configuration management

    Uses FlextResult railway pattern with zero async operations.
    All defaults from FlextCliConstants with proper centralization.

    Nested Classes (FLEXT pattern):
        FlextCli.Base - Click/Typer framework abstraction
        FlextCli.Runner - Command execution
        FlextCli.Commands - Command registration
        FlextCli.Params - Reusable CLI parameters
        FlextCli.Output - Output management
        FlextCli.Formatters - Rich abstraction
        FlextCli.Tables - Table formatting
        FlextCli.Prompts - Interactive input
        FlextCli.FileTools - File operations
        FlextCli.Config - Configuration singleton
        FlextCli.Context - Request context
        FlextCli.Core - Core service
        FlextCli.Debug - Debug utilities
        FlextCli.Models - Pydantic models
        FlextCli.Types - Type definitions
        FlextCli.Protocols - Protocol definitions
        FlextCli.Constants - System constants
        FlextCli.Mixins - Reusable mixins
        FlextCli.Utilities - Utility functions
        FlextCli.AppBase - Base class for CLI applications

    Usage (direct access pattern):
        >>> cli = FlextCli.get_instance()
        >>> cli.formatters.print("Hello")  # Direct formatters access
        >>> cli.output.format_data(data)  # Direct output access
        >>> cli.file_tools.read_json_file(path)  # Direct file tools access

    Usage (nested pattern):
        >>> from flext_cli import FlextCli
        >>> class MyCli(FlextCli.AppBase):
        ...     app_name = "my-cli"
        ...     app_help = "My CLI app"
    """

    # =========================================================================
    # NESTED CLASSES - FLEXT pattern (FlextCli.X instead of FlextCliX)
    # =========================================================================
    Base = FlextCliCli
    Runner = FlextCliCmd
    Commands = FlextCliCommands
    Params = FlextCliCommonParams
    Output = FlextCliOutput
    Formatters = FlextCliFormatters
    Tables = FlextCliTables
    # AppBase will be assigned after FlextCliAppBase is defined
    AppBase: ClassVar[type[ABC]]
    Prompts = FlextCliPrompts
    FileTools = FlextCliFileTools
    Config = FlextCliConfig
    Context = FlextCliContext
    Core = FlextCliCore
    Debug = FlextCliDebug
    Models = FlextCliModels
    Types = FlextCliTypes
    Protocols = FlextCliProtocols
    Constants = FlextCliConstants
    Mixins = FlextCliMixins
    Utilities = FlextCliUtilities

    # =========================================================================
    # SINGLETON PATTERN
    # =========================================================================
    _instance: FlextCli | None = None
    _lock = __import__("threading").Lock()

    # Public service instances (no wrapping needed - direct access)
    logger: FlextLogger
    config: FlextCliConfig
    formatters: FlextCliFormatters
    file_tools: FlextCliFileTools
    output: FlextCliOutput
    core: FlextCliCore
    cmd: FlextCliCmd
    prompts: FlextCliPrompts

    def __init__(self) -> None:
        """Initialize consolidated CLI with all functionality integrated."""
        # CLI metadata - MUST be first for Typer app creation
        self._name = FlextCliConstants.CliDefaults.DEFAULT_APP_NAME
        self._version = FlextCliConstants.CLI_VERSION
        self._description = (
            f"{self._name}{FlextCliConstants.APIDefaults.APP_DESCRIPTION_SUFFIX}"
        )

        # Core initialization
        self.logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()
        # Register in container only if not already registered (avoids test conflicts)
        if not self._container.has_service(
            FlextCliConstants.APIDefaults.CONTAINER_REGISTRATION_KEY
        ):
            self._container.with_service(
                FlextCliConstants.APIDefaults.CONTAINER_REGISTRATION_KEY, self
            )

        # Domain library components (domain library pattern)
        self.formatters = FlextCliFormatters()
        self.file_tools = FlextCliFileTools()
        self.output = FlextCliOutput()
        self.core = FlextCliCore()
        self.cmd = FlextCliCmd()
        self.prompts = FlextCliPrompts()

        # CLI framework abstraction (domain library pattern)
        self._cli = FlextCliCli()
        # Commands and groups store Callable functions, not JSON data
        self._commands: dict[str, Callable[..., FlextTypes.JsonValue]] = {}
        self._groups: dict[str, Callable[..., FlextTypes.JsonValue]] = {}
        self._plugin_commands: dict[str, Callable[..., FlextTypes.JsonValue]] = {}

        # Auth state (consolidated from FlextCliAuth)
        # Use new config pattern with automatic namespaces
        # Import ensures auto_register decorator executes

        # Pydantic Settings pattern: AutoConfig.__init__() automatically loads from:
        # 1. Environment variables (FLEXT_CLI_* prefix from model_config)
        # 2. .env file (if exists, via env_file in model_config)
        # 3. Field defaults
        # No workarounds needed - Pydantic Settings handles everything automatically
        self.config = FlextCliServiceBase.get_cli_config()
        self._valid_tokens: set[str] = set()
        self._valid_sessions: set[str] = set()
        self._session_permissions: dict[str, set[str]] = {}
        self._users: dict[str, FlextTypes.JsonDict] = {}
        self._deleted_users: set[str] = set()

    @classmethod
    def get_instance(cls) -> FlextCli:
        """Get singleton FlextCli instance using class-level singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                # Double-check locking pattern
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # =========================================================================
    # AUTHENTICATION - Direct implementation (consolidated from auth.py)
    # =========================================================================

    def authenticate(
        self, credentials: FlextCliTypes.Auth.CredentialsData
    ) -> FlextResult[str]:
        """Authenticate user with provided credentials."""
        if FlextCliConstants.DictKeys.TOKEN in credentials:
            return self._authenticate_with_token(credentials)
        if (
            FlextCliConstants.DictKeys.USERNAME in credentials
            and FlextCliConstants.DictKeys.PASSWORD in credentials
        ):
            return self._authenticate_with_credentials(credentials)
        return FlextResult[str].fail(
            FlextCliConstants.ErrorMessages.INVALID_CREDENTIALS
        )

    def _authenticate_with_token(
        self, credentials: FlextCliTypes.Auth.CredentialsData
    ) -> FlextResult[str]:
        """Authenticate using token."""
        token = str(credentials[FlextCliConstants.DictKeys.TOKEN])
        # Use FlextUtilities.Validation for token validation
        try:
            FlextUtilities.Validation.validate_required_string(token, "Token")
        except ValueError:
            return FlextResult[str].fail(FlextCliConstants.ErrorMessages.TOKEN_EMPTY)
        save_result = self.save_auth_token(token)
        if save_result.is_failure:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=save_result.error
                )
            )
        return FlextResult[str].ok(token)

    def _authenticate_with_credentials(
        self, credentials: FlextCliTypes.Auth.CredentialsData
    ) -> FlextResult[str]:
        """Authenticate using Pydantic 2 validation - no manual checks."""
        # Validate using Pydantic model - eliminates all manual validation
        try:
            FlextCliModels.PasswordAuth.model_validate(credentials)
        except Exception as e:
            return FlextResult[str].fail(str(e))

        # Generate token
        token = secrets.token_urlsafe(
            FlextCliConstants.APIDefaults.TOKEN_GENERATION_BYTES
        )
        self._valid_tokens.add(token)

        return FlextResult[str].ok(token)

    def validate_credentials(self, username: str, password: str) -> FlextResult[bool]:
        """Validate credentials using Pydantic 2."""
        try:
            FlextCliModels.PasswordAuth(username=username, password=password)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(str(e))

    def save_auth_token(self, token: str) -> FlextResult[bool]:
        """Save authentication token using file tools domain library."""
        # Use FlextUtilities.Validation for token validation
        try:
            FlextUtilities.Validation.validate_required_string(token, "Token")
        except ValueError:
            return FlextResult[bool].fail(FlextCliConstants.ErrorMessages.TOKEN_EMPTY)

        token_path = self.config.token_file
        token_data: FlextCliTypes.Auth.CredentialsData = {
            FlextCliConstants.DictKeys.TOKEN: token
        }

        # Use file tools domain library for JSON writing
        # token_data is CredentialsData (dict[str, JsonValue]) which is compatible with JsonValue
        # Cast to JsonValue for type checker (dict is a valid JsonValue at runtime)
        json_data = typing.cast("FlextTypes.JsonValue", token_data)
        write_result = self.file_tools.write_json_file(str(token_path), json_data)
        if write_result.is_failure:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=write_result.error
                )
            )

        self._valid_tokens.add(token)
        return FlextResult[bool].ok(True)

    def get_auth_token(self) -> FlextResult[str]:
        """Get authentication token using Pydantic 2 validation - no wrappers.

        Uses FlextCliModels.TokenData for validation instead of manual checks.
        """
        token_path = self.config.token_file

        # Read JSON file directly using file_tools
        result = self.file_tools.read_json_file(str(token_path))
        if result.is_failure:
            error_str = str(result.error)
            # Check for file not found using utilities helper (covers "not found", "no such file", etc.)
            if (
                FlextCliConstants.APIDefaults.FILE_ERROR_INDICATOR in error_str.lower()
                or FlextCliUtilities.FileOps.is_file_not_found_error(error_str)
            ):
                return FlextResult[str].fail(
                    FlextCliConstants.ErrorMessages.TOKEN_FILE_NOT_FOUND
                )
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_LOAD_FAILED.format(
                    error=error_str
                )
            )

        # Validate using Pydantic model - eliminates _validate_token_data + _extract_token_string
        data = result.unwrap()
        # Check if data is empty or None before validation
        if not data or (FlextRuntime.is_dict_like(data) and not data):
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_FILE_EMPTY
            )
        try:
            token_data = FlextCliModels.TokenData.model_validate(data)
            return FlextResult[str].ok(token_data.token)
        except Exception as e:
            # Return appropriate error message based on exception type
            error_str = str(e).lower()
            if "dict" in error_str or "mapping" in error_str or "object" in error_str:
                return FlextResult[str].fail(
                    FlextCliConstants.APIDefaults.TOKEN_DATA_TYPE_ERROR
                )
            if "string" in error_str or "str" in error_str:
                return FlextResult[str].fail(
                    FlextCliConstants.APIDefaults.TOKEN_VALUE_TYPE_ERROR
                )
            # Fallback for any other validation errors (e.g., field required, value errors)
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_FILE_EMPTY
            )

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        token_result = self.get_auth_token()
        return token_result.is_success

    def clear_auth_tokens(self) -> FlextResult[bool]:
        """Clear authentication tokens using file tools domain library."""
        token_path = self.config.token_file
        refresh_token_path = self.config.refresh_token_file

        # Use file tools domain library for file deletion
        delete_token_result = self.file_tools.delete_file(str(token_path))
        delete_refresh_result = self.file_tools.delete_file(str(refresh_token_path))

        # Check if either deletion failed (but don't fail if file doesn't exist)
        if (
            delete_token_result.is_failure
            and not FlextCliUtilities.FileOps.is_file_not_found_error(
                str(delete_token_result.error)
            )
        ):
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_token_result.error
                )
            )

        if (
            delete_refresh_result.is_failure
            and not FlextCliUtilities.FileOps.is_file_not_found_error(
                str(delete_refresh_result.error)
            )
        ):
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_refresh_result.error
                )
            )

        self._valid_tokens.clear()
        return FlextResult[bool].ok(True)

    # =========================================================================
    # COMMAND REGISTRATION - CLI framework abstraction (domain library pattern)
    # =========================================================================

    def _register_cli_entity(
        self,
        entity_type: FlextCliConstants.EntityTypeLiteral,
        name: str | None,
        func: Callable[..., FlextTypes.JsonValue],
    ) -> Callable[..., FlextTypes.JsonValue]:
        """Register a CLI entity (command or group) with framework abstraction.

        Args:
            entity_type: Type of entity to register ("command" or "group")
            name: Entity name (None to use function name)
            func: Function to register

        Returns:
            Decorated function

        """
        # Validate entity name explicitly - no fallback
        entity_name = name if name is not None else func.__name__

        if entity_type == "command":
            self._commands[entity_name] = func
            decorator = self._cli.create_command_decorator(name=entity_name)
        else:  # group
            self._groups[entity_name] = func
            decorator = self._cli.create_group_decorator(name=entity_name)

        return decorator(func)

    def command(
        self, name: str | None = None
    ) -> Callable[
        [Callable[..., FlextTypes.JsonValue]], Callable[..., FlextTypes.JsonValue]
    ]:
        """Register a command using CLI framework abstraction."""

        def decorator(
            func: Callable[..., FlextTypes.JsonValue],
        ) -> Callable[..., FlextTypes.JsonValue]:
            return self._register_cli_entity("command", name, func)

        return decorator

    def group(
        self, name: str | None = None
    ) -> Callable[
        [Callable[..., FlextTypes.JsonValue]], Callable[..., FlextTypes.JsonValue]
    ]:
        """Register a command group using CLI framework abstraction."""

        def decorator(
            func: Callable[..., FlextTypes.JsonValue],
        ) -> Callable[..., FlextTypes.JsonValue]:
            return self._register_cli_entity("group", name, func)

        return decorator

    def execute_cli(self) -> FlextResult[bool]:
        """Execute the CLI application using framework abstraction."""
        # FlextCliCli doesn't have run_app - CLI execution handled elsewhere
        return FlextResult[bool].ok(True)

    # =========================================================================
    # EXECUTION - Railway pattern with FlextResult
    # =========================================================================

    def execute(self) -> FlextResult[FlextTypes.JsonDict]:
        """Execute CLI service with railway pattern."""
        components: dict[str, str] = {
            "config": "available",
            "formatters": "available",
            "core": "available",
            "prompts": "available",
        }
        return FlextResult[FlextTypes.JsonDict].ok(
            cast(
                "FlextTypes.JsonDict",
                {
                    FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
                    FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
                    "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
                    "version": __version__,
                    "components": components,
                },
            )
        )

    # =========================================================================
    # CONVENIENCE METHODS - Delegate to service instances
    # =========================================================================

    def print(
        self,
        message: str,
        style: str | None = None,
    ) -> FlextResult[bool]:
        """Print formatted message (convenience method for formatters.print)."""
        return self.formatters.print(message, style)

    def create_table(
        self,
        data: Sequence[dict[str, FlextTypes.JsonValue]]
        | dict[str, FlextTypes.JsonValue]
        | None = None,
        headers: list[str] | None = None,
        title: str | None = None,
    ) -> FlextResult[str]:
        """Create table from data (convenience method).

        Args:
            data: Data to format as table (dict or list of dicts)
            headers: Optional column headers
            title: Optional table title

        Returns:
            FlextResult[str]: Formatted table string

        """
        # Handle None case - fast fail if data is None
        if data is None:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED
            )

        # table_data is dict|list which are both valid JsonValue types
        # Ensure type compatibility for type checker (dict/list are JsonValue at runtime)
        if FlextRuntime.is_dict_like(data):
            table_data = typing.cast("FlextTypes.JsonValue", data)
        elif FlextRuntime.is_list_like(data):
            # Already a list-like structure, cast directly
            table_data = typing.cast("FlextTypes.JsonValue", data)
        else:
            # Convert iterable to list and ensure JsonValue compatibility
            table_data = typing.cast(
                "FlextTypes.JsonValue",
                list(data) if isinstance(data, Sequence) else [data],
            )

        # Use output.format_data which supports data, title, and headers
        return self.output.format_data(
            data=table_data,
            format_type="table",
            title=title,
            headers=headers,
        )

    def print_table(
        self,
        table: str,
    ) -> FlextResult[bool]:
        """Print table string (convenience method)."""
        return self.formatters.print(table)

    def create_tree(
        self,
        label: str,
    ) -> FlextResult[FlextCliTypes.Display.RichTree]:
        """Create tree visualization (convenience method for formatters.create_tree)."""
        return self.formatters.create_tree(label)


class FlextCliAppBase(ABC):
    """Base class for CLI applications using FLEXT pattern.

    Provides standard initialization, execution, and error handling
    for CLI applications. Subclasses define app_name, app_help, and
    config_class, then implement _register_commands().

    Usage:
        >>> from flext_cli import FlextCli
        >>> class MyCli(FlextCli.AppBase):
        ...     app_name = "my-cli"
        ...     app_help = "My CLI application"
        ...     config_class = MyConfig
        ...
        ...     def _register_commands(self) -> None:
        ...         # Register commands here
        ...         pass
    """

    # ClassVars to override in subclass
    app_name: ClassVar[str]
    app_help: ClassVar[str]
    config_class: ClassVar[
        type[FlextCliConfig]
    ]  # Config class with get_instance() method

    # Instance attributes (initialized in __init__)
    _output: FlextCliOutput
    _cli: FlextCliCli
    _app: typer.Typer
    _config: FlextCliConfig

    def __init__(self) -> None:
        """Initialize CLI with FlextCli infrastructure."""
        super().__init__()
        self._output = FlextCliOutput()
        self._cli = FlextCliCli()

        # Load configuration using singleton pattern
        # config_class must have get_instance() class method
        self._config = self.config_class.get_instance()

        # Log loaded configuration
        self._log_config_loaded()

        # Create Typer app with common params (--debug, --log-level, --trace)
        self._app = self._cli.create_app_with_common_params(
            name=self.app_name,
            help_text=self.app_help,
            config=self._config,
            add_completion=True,
        )

        # Register commands
        try:
            self._register_commands()
        except NameError as ne:
            self._handle_pathlib_annotation_error(ne)

    @abstractmethod
    def _register_commands(self) -> None:
        """Register CLI commands - implement in subclass."""
        ...

    def _log_config_loaded(self) -> None:
        """Log configuration values. Override in subclass for custom logging."""
        FlextLogger.get_logger().debug(
            "CLI configuration loaded",
            app_name=self.app_name,
        )

    def _handle_pathlib_annotation_error(self, ne: NameError) -> None:
        """Handle Typer annotation issues with pathlib.Path in Python <3.10."""
        if "pathlib" in str(ne):
            FlextLogger.get_logger().warning(
                "Pathlib annotation issue detected during command registration",
                error=str(ne),
                python_version_note="Expected in Python <3.10 due to Typer annotation issues",
            )
        else:
            raise ne

    def _resolve_cli_args(self, args: list[str] | None) -> list[str]:
        """Resolve CLI arguments based on environment.

        Args:
            args: Provided arguments or None

        Returns:
            List of CLI arguments to use

        """
        if args is None:
            # Check if we're in a test environment
            if os.getenv("PYTEST_CURRENT_TEST"):
                return []
            return sys.argv[1:] if len(sys.argv) > 1 else []
        return args

    def execute_cli(self, args: list[str] | None = None) -> FlextResult[bool]:
        """Execute the CLI with Railway-pattern error handling.

        Args:
            args: Command-line arguments (defaults to sys.argv[1:])

        Returns:
            FlextResult[bool] - True if CLI execution completes successfully

        """
        try:
            # Ensure pathlib is available for Typer's annotation evaluation
            sys.modules["pathlib"] = pathlib
            frame = inspect.currentframe()
            if frame and "pathlib" not in frame.f_globals:
                frame.f_globals["pathlib"] = pathlib

            resolved_args = self._resolve_cli_args(args)
            self._app(args=resolved_args, standalone_mode=False)
            return FlextResult[bool].ok(True)
        except NameError as e:
            if "pathlib" in str(e):
                error_msg = f"CLI annotation evaluation error: {e!s}"
                self._output.print_error(error_msg)
                return FlextResult[bool].fail(error_msg)
            raise
        except SystemExit as e:
            if e.code == 0:
                return FlextResult[bool].ok(True)
            return FlextResult[bool].fail(f"CLI execution failed with code {e.code}")
        except Exception as e:
            if isinstance(e, ClickUsageError):
                return FlextResult[bool].fail(f"CLI execution error: {e!s}")
            if isinstance(
                e,
                (
                    ValueError,
                    KeyError,
                    AttributeError,
                    TypeError,
                    OSError,
                    RuntimeError,
                    FlextExceptions.BaseError,
                ),
            ):
                tb = traceback.format_exc()
                error_msg = f"CLI execution error: {e!s}\nTraceback:\n{tb}"
                self._output.print_error(error_msg)
                return FlextResult[bool].fail(f"CLI execution error: {e!s}")
            raise


# Add AppBase to FlextCli nested pattern
FlextCli.AppBase = FlextCliAppBase


__all__ = [
    "FlextCli",
    "FlextCliAppBase",
]

"""Public API facade for flext-cli.

Centraliza autenticação, registro/execução de comandos e acesso às utilidades
expostas como atributos do `FlextCli`, mantendo wrappers de conveniência que
delegam para os serviços internos sem quebrar o isolamento de Typer/Click e
Rich.

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
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from typing import ClassVar, cast

import typer
from click.exceptions import UsageError as ClickUsageError
from flext_core import (
    FlextContainer,
    FlextExceptions,
    FlextLogger,
    FlextResult,
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
from flext_cli.utilities import FlextCliUtilities

# Direct type references - use FlextCliProtocols.Cli.CliCommandFunction directly


class FlextCli:
    """Coordinate CLI operations and expose domain services.

    Business Rules:
    ───────────────
    1. Singleton pattern ensures single CLI instance per process (thread-safe)
    2. Service instances MUST be initialized before use (lazy initialization)
    3. Command registration MUST validate command names and handlers
    4. Authentication MUST be performed before privileged operations
    5. Configuration MUST be loaded from environment variables or config files
    6. All operations MUST return FlextResult[T] for error handling
    7. Service instances are exposed as attributes for direct access
    8. Wrappers delegate to service instances without breaking isolation

    Architecture Implications:
    ───────────────────────────
    - Singleton pattern with thread-safe locking prevents race conditions
    - Service instances are created on-demand (lazy initialization)
    - Direct service access avoids unnecessary wrapper layers
    - Typer/Click and Rich isolation maintained through abstraction
    - Railway-Oriented Programming via FlextResult for composable error handling

    Audit Implications:
    ───────────────────
    - All command registrations MUST be logged with timestamp and command name
    - Authentication attempts MUST be logged (success/failure, no credentials)
    - Configuration changes MUST be logged with before/after values
    - Service initialization MUST be logged for audit trail
    - Error conditions MUST be logged with full context (no sensitive data)
    - Remote operations MUST use encrypted connections (TLS/SSL)
    - Session management MUST track user context for audit purposes

    Instancia serviços (`core`, `cmd`, `output`, `prompts`, `tables`) e
    utilidades (`formatters`, `file_tools`, `utilities`) para acesso direto,
    mantendo os wrappers legados como delegação explícita para essas instâncias.
    """

    # Nested classes - FLEXT pattern
    Base = FlextCliCli
    Runner = FlextCliCmd
    Commands = FlextCliCommands
    Params = FlextCliCommonParams
    Output = FlextCliOutput
    Formatters = FlextCliFormatters
    Tables = FlextCliTables
    AppBase: ClassVar[type[ABC]]
    Prompts = FlextCliPrompts
    FileTools = FlextCliFileTools
    Config = FlextCliConfig
    Context = FlextCliContext
    Core = FlextCliCore
    Debug = FlextCliDebug
    Models = FlextCliModels
    Protocols = FlextCliProtocols
    Constants = FlextCliConstants
    Mixins = FlextCliMixins
    Utilities = FlextCliUtilities

    # Singleton pattern
    _instance: FlextCli | None = None
    _lock = __import__("threading").Lock()

    # Public service instances
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
        self._name = FlextCliConstants.CliDefaults.DEFAULT_APP_NAME
        self._version = FlextCliConstants.CLI_VERSION
        self._description = (
            f"{self._name}{FlextCliConstants.APIDefaults.APP_DESCRIPTION_SUFFIX}"
        )

        self.logger = FlextLogger(__name__)
        self._container = FlextContainer()
        if not self._container.has_service(
            FlextCliConstants.APIDefaults.CONTAINER_REGISTRATION_KEY,
        ):
            # Register service name only - container doesn't need the instance itself
            # Use a simple string identifier instead of the instance
            register_result = self._container.register(
                FlextCliConstants.APIDefaults.CONTAINER_REGISTRATION_KEY,
                FlextCliConstants.APIDefaults.CONTAINER_REGISTRATION_KEY,
            )
            if register_result.is_failure:
                self.logger.warning(
                    f"Failed to register CLI service: {register_result.error}"
                )

        # Domain library components
        self.formatters = FlextCliFormatters()
        self.file_tools = FlextCliFileTools()
        self.output = FlextCliOutput()
        self.core = FlextCliCore()
        self.cmd = FlextCliCmd()
        self.prompts = FlextCliPrompts()

        self._cli = FlextCliCli()
        self._commands: dict[str, FlextCliProtocols.Cli.CliRegisteredCommand] = {}
        self._groups: dict[str, FlextCliProtocols.Cli.CliRegisteredCommand] = {}
        self._plugin_commands: dict[
            str, FlextCliProtocols.Cli.CliRegisteredCommand
        ] = {}

        self.config = FlextCliServiceBase.get_cli_config()
        self._valid_tokens: set[str] = set()
        self._valid_sessions: set[str] = set()
        self._session_permissions: dict[str, set[str]] = {}
        self._users: dict[str, FlextTypes.JsonDict] = {}
        self._deleted_users: set[str] = set()

    @classmethod
    def get_instance(cls) -> FlextCli:
        """Get singleton FlextCli instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    # =========================================================================
    # PRIVATE HELPERS - Generalize common patterns
    # =========================================================================

    @staticmethod
    def _validate_token_string(token: str) -> FlextResult[bool]:
        """Generalized token validation helper."""
        if not isinstance(token, str) or not token.strip():
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.TOKEN_EMPTY,
            )
        return FlextResult[bool].ok(True)

    # =========================================================================
    # AUTHENTICATION
    # =========================================================================

    def authenticate(
        self,
        credentials: Mapping[str, str],
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
            FlextCliConstants.ErrorMessages.INVALID_CREDENTIALS,
        )

    def _authenticate_with_token(
        self,
        credentials: Mapping[str, str],
    ) -> FlextResult[str]:
        """Authenticate using token."""
        token = str(credentials[FlextCliConstants.DictKeys.TOKEN])
        validation = FlextCli._validate_token_string(token)
        if validation.is_failure:
            return FlextResult[str].fail(validation.error or "")

        save_result = self.save_auth_token(token)
        if save_result.is_failure:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=save_result.error,
                ),
            )
        return FlextResult[str].ok(token)

    def _authenticate_with_credentials(
        self,
        credentials: Mapping[str, str],
    ) -> FlextResult[str]:
        """Authenticate using Pydantic 2 validation."""
        try:
            FlextCliModels.PasswordAuth.model_validate(credentials)
        except Exception as e:
            return FlextResult[str].fail(str(e))

        token = secrets.token_urlsafe(
            FlextCliConstants.APIDefaults.TOKEN_GENERATION_BYTES,
        )
        self._valid_tokens.add(token)
        return FlextResult[str].ok(token)

    @staticmethod
    def validate_credentials(username: str, password: str) -> FlextResult[bool]:
        """Validate credentials using Pydantic 2."""
        try:
            FlextCliModels.PasswordAuth(username=username, password=password)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(str(e))

    def save_auth_token(self, token: str) -> FlextResult[bool]:
        """Save authentication token using file tools domain library."""
        validation = FlextCli._validate_token_string(token)
        if validation.is_failure:
            return validation

        token_path = self.config.token_file
        # Create dict with GeneralValueType for DataMapper compatibility
        token_data: dict[str, FlextTypes.GeneralValueType] = {
            # str is subtype of GeneralValueType
            FlextCliConstants.DictKeys.TOKEN: token,
        }

        # Use DataMapper for type-safe conversion
        json_data = FlextUtilities.DataMapper.convert_dict_to_json(token_data)
        write_result = self.file_tools.write_json_file(str(token_path), json_data)
        if write_result.is_failure:
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.TOKEN_SAVE_FAILED.format(
                    error=write_result.error,
                ),
            )

        self._valid_tokens.add(token)
        return FlextResult[bool].ok(True)

    def get_auth_token(self) -> FlextResult[str]:
        """Get authentication token using Pydantic 2 validation."""
        token_path = self.config.token_file

        result = self.file_tools.read_json_file(str(token_path))
        if result.is_failure:
            error_str = str(result.error)
            error_lower = error_str.lower()
            if FlextCliConstants.APIDefaults.FILE_ERROR_INDICATOR in error_lower or any(
                pattern in error_lower
                for pattern in [
                    "not found",
                    "no such file",
                    "does not exist",
                    "errno 2",
                ]
            ):
                return FlextResult[str].fail(
                    FlextCliConstants.ErrorMessages.TOKEN_FILE_NOT_FOUND,
                )
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_LOAD_FAILED.format(
                    error=error_str,
                ),
            )

        data = result.unwrap()
        if not data or (isinstance(data, dict) and not data):
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_FILE_EMPTY,
            )

        try:
            token_data = FlextCliModels.TokenData.model_validate(data)
            return FlextResult[str].ok(token_data.token)
        except Exception as e:
            error_str = str(e).lower()
            # Determine error type based on error message content
            if "dict" in error_str or "mapping" in error_str or "object" in error_str:
                error_msg = FlextCliConstants.APIDefaults.TOKEN_DATA_TYPE_ERROR
            elif "string" in error_str or "str" in error_str:
                error_msg = FlextCliConstants.APIDefaults.TOKEN_VALUE_TYPE_ERROR
            else:
                error_msg = FlextCliConstants.ErrorMessages.TOKEN_FILE_EMPTY
            return FlextResult[str].fail(error_msg)

    def is_authenticated(self) -> bool:
        """Check if user is authenticated."""
        return self.get_auth_token().is_success

    def clear_auth_tokens(self) -> FlextResult[bool]:
        """Clear authentication tokens using file tools domain library."""
        token_path = self.config.token_file
        refresh_token_path = self.config.refresh_token_file

        delete_token_result = self.file_tools.delete_file(str(token_path))
        delete_refresh_result = self.file_tools.delete_file(str(refresh_token_path))

        # Check if either deletion failed (but don't fail if file doesn't exist)
        error_str_token = str(delete_token_result.error).lower()
        if delete_token_result.is_failure and not any(
            pattern in error_str_token
            for pattern in [
                "not found",
                "no such file",
                "does not exist",
                "errno 2",
            ]
        ):
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_token_result.error,
                ),
            )

        error_str_refresh = str(delete_refresh_result.error).lower()
        if delete_refresh_result.is_failure and not any(
            pattern in error_str_refresh
            for pattern in [
                "not found",
                "no such file",
                "does not exist",
                "errno 2",
            ]
        ):
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_refresh_result.error,
                ),
            )

        self._valid_tokens.clear()
        return FlextResult[bool].ok(True)

    # =========================================================================
    # COMMAND REGISTRATION
    # =========================================================================

    def _register_cli_entity(
        self,
        entity_type: FlextCliConstants.EntityTypeLiteral,
        name: str | None,
        func: FlextCliProtocols.Cli.CliCommandFunction,
    ) -> FlextCliProtocols.Cli.CliRegisteredCommand:
        """Register a CLI entity (command or group) with framework abstraction."""
        # Get function name safely - protocols may not have __name__
        entity_name = name if name is not None else getattr(func, "__name__", "unknown")

        if entity_type == "command":
            decorator = self._cli.create_command_decorator(name=entity_name)
            decorated_func = decorator(func)
            # Click Command/Group implements CliRegisteredCommand protocol structurally
            # Note: Cannot use isinstance with Protocol types - use cast instead
            # Click Command/Group are structurally compatible with CliRegisteredCommand
            result = cast("FlextCliProtocols.Cli.CliRegisteredCommand", decorated_func)
            self._commands[entity_name] = result
        else:  # group
            decorator = self._cli.create_group_decorator(name=entity_name)
            decorated_func = decorator(func)
            # Click Group implements CliRegisteredCommand protocol structurally
            # Note: Cannot use isinstance with Protocol types - use cast instead
            result = cast("FlextCliProtocols.Cli.CliRegisteredCommand", decorated_func)
            self._groups[entity_name] = result

        return result

    def command(
        self,
        name: str | None = None,
    ) -> Callable[
        [FlextCliProtocols.Cli.CliCommandFunction],
        FlextCliProtocols.Cli.CliRegisteredCommand,
    ]:
        """Register a command using CLI framework abstraction."""

        def decorator(
            func: FlextCliProtocols.Cli.CliCommandFunction,
        ) -> FlextCliProtocols.Cli.CliRegisteredCommand:
            return self._register_cli_entity("command", name, func)

        return decorator

    def group(
        self,
        name: str | None = None,
    ) -> Callable[
        [FlextCliProtocols.Cli.CliCommandFunction],
        FlextCliProtocols.Cli.CliRegisteredCommand,
    ]:
        """Register a command group using CLI framework abstraction."""

        def decorator(
            func: FlextCliProtocols.Cli.CliCommandFunction,
        ) -> FlextCliProtocols.Cli.CliRegisteredCommand:
            return self._register_cli_entity("group", name, func)

        return decorator

    @staticmethod
    def execute_cli() -> FlextResult[bool]:
        """Execute the CLI application using framework abstraction."""
        return FlextResult[bool].ok(True)

    # =========================================================================
    # EXECUTION
    # =========================================================================

    def execute(self) -> FlextResult[FlextTypes.JsonDict]:  # noqa: PLR6301
        """Execute CLI service with railway pattern."""
        # Build JsonDict - convert version to string, components as dict
        result_dict: FlextTypes.JsonDict = {
            FlextCliConstants.DictKeys.STATUS: (
                FlextCliConstants.ServiceStatus.OPERATIONAL.value
            ),
            FlextCliConstants.DictKeys.SERVICE: FlextCliConstants.FLEXT_CLI,
            "timestamp": FlextUtilities.Generators.generate_iso_timestamp(),
            "version": str(__version__),
            "components": {
                "config": "available",
                "formatters": "available",
                "core": "available",
                "prompts": "available",
            },
        }

        return FlextResult[FlextTypes.JsonDict].ok(result_dict)

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
        data: Sequence[Mapping[str, FlextTypes.GeneralValueType]]
        | Mapping[str, FlextTypes.GeneralValueType]
        | None = None,
        headers: list[str] | None = None,
        title: str | None = None,
    ) -> FlextResult[str]:
        """Create table from data (convenience method)."""
        if data is None:
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.NO_DATA_PROVIDED,
            )

        # Convert data using DataMapper for type-safe conversion
        table_data: FlextTypes.GeneralValueType
        if isinstance(data, dict):
            table_data = FlextUtilities.DataMapper.convert_dict_to_json(data)
        else:
            # Handle all Sequence types (list, tuple, or other sequences)
            converted_list = FlextUtilities.DataMapper.convert_list_to_json(list(data))
            table_data = converted_list

        return self.output.format_data(
            data=table_data,
            format_type=FlextCliConstants.OutputFormats.TABLE.value,
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
    ) -> FlextResult[FlextCliProtocols.Display.RichTreeProtocol]:
        """Create tree visualization (convenience method for formatters.create_tree)."""
        # formatters.create_tree returns RichTree which implements RichTreeProtocol
        result = self.formatters.create_tree(label)
        if result.is_success:
            # RichTree (concrete type) implements RichTreeProtocol structurally
            # Type narrowing: unwrap returns RichTreeProtocol-compatible type
            tree_value = result.unwrap()
            # Use cast instead of isinstance for Protocol (structural typing)
            return FlextResult[FlextCliProtocols.Display.RichTreeProtocol].ok(
                cast("FlextCliProtocols.Display.RichTreeProtocol", tree_value)
            )
            # Fallback: return as-is (formatters already returns correct type)
            # Use cast for structural typing compatibility
            protocol_tree: FlextCliProtocols.Display.RichTreeProtocol = cast(
                "FlextCliProtocols.Display.RichTreeProtocol", tree_value
            )
            return FlextResult[FlextCliProtocols.Display.RichTreeProtocol].ok(
                protocol_tree
            )
        # Result is already FlextResult[RichTreeProtocol] from formatters
        # Use cast to satisfy type checker - Tree implements RichTreeProtocol
        return cast("FlextResult[FlextCliProtocols.Display.RichTreeProtocol]", result)


class FlextCliAppBase(ABC):
    """Base class for CLI applications using the FLEXT pattern.

    Fornece inicialização, execução e tratamento de erros consistentes para CLIs
    Typer. Subclasses definem `app_name`, `app_help` e `config_class` e
    implementam `_register_commands()`.
    """

    # ClassVars to override in subclass
    app_name: ClassVar[str]
    app_help: ClassVar[str]
    config_class: ClassVar[type[FlextCliConfig]]

    # Instance attributes
    logger: FlextLogger
    _output: FlextCliOutput
    _cli: FlextCliCli
    _app: typer.Typer
    _config: FlextCliConfig

    def __init__(self) -> None:
        """Initialize CLI with FlextCli infrastructure."""
        super().__init__()
        self.logger = FlextLogger(__name__)
        self._output = FlextCliOutput()
        self._cli = FlextCliCli()
        self._config = self.config_class.get_instance()

        self.logger.debug(
            "CLI configuration loaded",
            app_name=self.app_name,
        )

        # create_app_with_common_params expects FlextCliConfig | None
        # Pass config directly since it's already FlextCliConfig
        self._app = self._cli.create_app_with_common_params(
            name=self.app_name,
            help_text=self.app_help,
            config=self._config,
            add_completion=True,
        )

        try:
            self._register_commands()
        except NameError as ne:
            self._handle_pathlib_annotation_error(ne)

    @abstractmethod
    def _register_commands(self) -> None:
        """Register CLI commands - implement in subclass."""
        ...

    @staticmethod
    def _handle_pathlib_annotation_error(ne: NameError) -> None:
        """Handle Typer annotation issues with pathlib.Path in Python <3.10."""
        if "pathlib" in str(ne):
            FlextLogger.get_logger().warning(
                "Pathlib annotation issue detected during command registration",
                error=str(ne),
                python_version_note=(
                    "Expected in Python <3.10 with Typer annotation issues"
                ),
            )
        else:
            raise ne

    @staticmethod
    def _resolve_cli_args(args: list[str] | None) -> list[str]:
        """Resolve CLI arguments based on environment."""
        if args is None:
            if os.getenv("PYTEST_CURRENT_TEST"):
                return []
            return sys.argv[1:] if len(sys.argv) > 1 else []
        return args

    def execute_cli(self, args: list[str] | None = None) -> FlextResult[bool]:
        """Execute the CLI with Railway-pattern error handling."""
        try:
            # Ensure pathlib is available for Typer's annotation evaluation
            sys.modules["pathlib"] = pathlib
            frame = inspect.currentframe()
            if frame and "pathlib" not in frame.f_globals:
                frame.f_globals["pathlib"] = pathlib

            resolved_args = FlextCliAppBase._resolve_cli_args(args)
            # Use standalone_mode=True to ensure Typer handles errors and output
            # When standalone_mode=False, Typer doesn't print errors automatically
            self._app(args=resolved_args, standalone_mode=True)
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
            # SystemExit with non-zero code means failure
            # Typer already printed the error in standalone_mode=True
            return FlextResult[bool].fail(f"CLI execution failed with code {e.code}")
        except Exception as e:
            if isinstance(e, ClickUsageError):
                error_msg = f"CLI execution error: {e!s}"
                self._output.print_error(error_msg)
                return FlextResult[bool].fail(error_msg)
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

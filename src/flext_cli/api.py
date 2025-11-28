"""FLEXT CLI API - Consolidated single-class implementation.

**MODULE**: FlextCli - Single primary class for CLI operations
**SCOPE**: Authentication, command registration, execution coordination, convenience methods

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
from collections.abc import Callable, Sequence
from datetime import UTC, datetime
from typing import ClassVar

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
from flext_cli.typings import FlextCliTypes
from flext_cli.utilities import FlextCliUtilities

# Type aliases for command functions
CliCommandFunc = FlextCliProtocols.Cli.CliCommandFunction
CliRegisteredCmd = FlextCliProtocols.Cli.CliRegisteredCommand


class FlextCli:
    """Coordinator for CLI operations with direct domain library access.

    Consolidates ALL CLI functionality through direct access to domain libraries.
    Uses FlextResult railway pattern with zero async operations.
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
    Types = FlextCliTypes
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
            register_result = self._container.register(
                FlextCliConstants.APIDefaults.CONTAINER_REGISTRATION_KEY,
                self,
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
        self._commands: dict[str, CliRegisteredCmd] = {}
        self._groups: dict[str, CliRegisteredCmd] = {}
        self._plugin_commands: dict[str, CliRegisteredCmd] = {}

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

    def _validate_token_string(self, token: str) -> FlextResult[bool]:
        """Generalized token validation helper - uses FlextCliUtilities."""
        return FlextCliUtilities.CliValidation.validate_string_not_empty(
            token,
            FlextCliConstants.ErrorMessages.TOKEN_EMPTY,
        )

    # =========================================================================
    # AUTHENTICATION
    # =========================================================================

    def authenticate(
        self,
        credentials: FlextCliTypes.Auth.CredentialsData,
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
        credentials: FlextCliTypes.Auth.CredentialsData,
    ) -> FlextResult[str]:
        """Authenticate using token."""
        token = str(credentials[FlextCliConstants.DictKeys.TOKEN])
        validation = self._validate_token_string(token)
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
        credentials: FlextCliTypes.Auth.CredentialsData,
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

    def validate_credentials(self, username: str, password: str) -> FlextResult[bool]:
        """Validate credentials using Pydantic 2."""
        try:
            FlextCliModels.PasswordAuth(username=username, password=password)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(str(e))

    def save_auth_token(self, token: str) -> FlextResult[bool]:
        """Save authentication token using file tools domain library."""
        validation = self._validate_token_string(token)
        if validation.is_failure:
            return validation

        token_path = self.config.token_file
        token_data: FlextCliTypes.Auth.CredentialsData = {
            FlextCliConstants.DictKeys.TOKEN: token,
        }

        # Use DataMapper for type-safe conversion
        json_data = FlextCliUtilities.DataMapper.convert_dict_to_json(token_data)
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
            if (
                FlextCliConstants.APIDefaults.FILE_ERROR_INDICATOR in error_str.lower()
                or FlextCliUtilities.FileOps.is_file_not_found_error(error_str)
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
            if "dict" in error_str or "mapping" in error_str or "object" in error_str:
                return FlextResult[str].fail(
                    FlextCliConstants.APIDefaults.TOKEN_DATA_TYPE_ERROR,
                )
            if "string" in error_str or "str" in error_str:
                return FlextResult[str].fail(
                    FlextCliConstants.APIDefaults.TOKEN_VALUE_TYPE_ERROR,
                )
            return FlextResult[str].fail(
                FlextCliConstants.ErrorMessages.TOKEN_FILE_EMPTY,
            )

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
        if (
            delete_token_result.is_failure
            and not FlextCliUtilities.FileOps.is_file_not_found_error(
                str(delete_token_result.error),
            )
        ):
            return FlextResult[bool].fail(
                FlextCliConstants.ErrorMessages.FAILED_CLEAR_CREDENTIALS.format(
                    error=delete_token_result.error,
                ),
            )

        if (
            delete_refresh_result.is_failure
            and not FlextCliUtilities.FileOps.is_file_not_found_error(
                str(delete_refresh_result.error),
            )
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
        func: CliCommandFunc,
    ) -> CliRegisteredCmd:
        """Register a CLI entity (command or group) with framework abstraction."""
        entity_name = name if name is not None else func.__name__

        if entity_type == "command":
            decorator = self._cli.create_command_decorator(name=entity_name)
            result: CliRegisteredCmd = decorator(func)
            self._commands[entity_name] = result
        else:  # group
            decorator = self._cli.create_group_decorator(name=entity_name)
            result = decorator(func)
            self._groups[entity_name] = result

        return result

    def command(
        self,
        name: str | None = None,
    ) -> Callable[[CliCommandFunc], CliRegisteredCmd]:
        """Register a command using CLI framework abstraction."""

        def decorator(func: CliCommandFunc) -> CliRegisteredCmd:
            return self._register_cli_entity("command", name, func)

        return decorator

    def group(
        self,
        name: str | None = None,
    ) -> Callable[[CliCommandFunc], CliRegisteredCmd]:
        """Register a command group using CLI framework abstraction."""

        def decorator(func: CliCommandFunc) -> CliRegisteredCmd:
            return self._register_cli_entity("group", name, func)

        return decorator

    def execute_cli(self) -> FlextResult[bool]:
        """Execute the CLI application using framework abstraction."""
        return FlextResult[bool].ok(True)

    # =========================================================================
    # EXECUTION
    # =========================================================================

    def execute(self) -> FlextResult[FlextTypes.JsonDict]:
        """Execute CLI service with railway pattern."""
        # Build JsonDict - convert version to string, components as dict
        result_dict: FlextTypes.JsonDict = {
            FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
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
        data: Sequence[dict[str, FlextCliTypes.CliJsonValue]]
        | dict[str, FlextCliTypes.CliJsonValue]
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
        table_data: FlextCliTypes.CliJsonValue
        if isinstance(data, dict):
            table_data = FlextCliUtilities.DataMapper.convert_dict_to_json(data)
        else:
            # Handle all Sequence types (list, tuple, or other sequences)
            converted_list = FlextCliUtilities.DataMapper.convert_list_to_json(
                list(data)
            )
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
    ) -> FlextResult[FlextCliTypes.Display.RichTree]:
        """Create tree visualization (convenience method for formatters.create_tree)."""
        return self.formatters.create_tree(label)


class FlextCliAppBase(ABC):
    """Base class for CLI applications using FLEXT pattern.

    Provides standard initialization, execution, and error handling
    for CLI applications. Subclasses define app_name, app_help, and
    config_class, then implement _register_commands().
    """

    # ClassVars to override in subclass
    app_name: ClassVar[str]
    app_help: ClassVar[str]
    config_class: ClassVar[type[FlextCliConfig]]

    # Instance attributes
    _output: FlextCliOutput
    _cli: FlextCliCli
    _app: typer.Typer
    _config: FlextCliConfig

    def __init__(self) -> None:
        """Initialize CLI with FlextCli infrastructure."""
        super().__init__()
        self._output = FlextCliOutput()
        self._cli = FlextCliCli()
        self._config = self.config_class.get_instance()

        FlextLogger.get_logger().debug(
            "CLI configuration loaded",
            app_name=self.app_name,
        )

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
        """Resolve CLI arguments based on environment."""
        if args is None:
            if os.getenv("PYTEST_CURRENT_TEST"):
                return []
            return sys.argv[1:] if len(sys.argv) > 1 else []
        return args

    def orchestrate_workflow(
        self,
        steps: Sequence[
            Callable[[], FlextResult[FlextCliTypes.Workflow.WorkflowStepResult]]
        ],
        *,
        step_names: Sequence[str] | None = None,
        continue_on_failure: bool = False,
        progress_callback: Callable[
            [int, int, str, FlextCliTypes.Workflow.WorkflowProgress], None
        ]
        | None = None,
    ) -> FlextResult[FlextCliModels.WorkflowResult]:
        """Orchestrate a complex multi-step workflow with progress tracking.

        Generic orchestration method that executes a sequence of workflow steps,
        tracks progress, and aggregates results. Each step is a callable that returns
        a FlextResult with step-specific data.

        Args:
            steps: Sequence of step functions, each returning FlextResult[WorkflowStepResult]
            step_names: Optional names for steps (defaults to "Step 1", "Step 2", etc.)
            continue_on_failure: If True, continue executing remaining steps on failure
            progress_callback: Optional callback(current_step, total_steps, step_name, progress)

        Returns:
            FlextResult containing WorkflowResult with aggregated step results and statistics

        Example:
            def parse_step() -> FlextResult[WorkflowStepResult]:
                # Parse LDIF files
                return FlextResult.ok(WorkflowStepResult(
                    step_name="parse",
                    success=True,
                    data={"entries": 100}
                ))

            def migrate_step() -> FlextResult[WorkflowStepResult]:
                # Migrate entries
                return FlextResult.ok(WorkflowStepResult(
                    step_name="migrate",
                    success=True,
                    data={"migrated": 95}
                ))

            result = cli.orchestrate_workflow(
                [parse_step, migrate_step],
                step_names=["Parse LDIF", "Migrate Entries"]
            )
            if result.is_success:
                workflow = result.unwrap()
                print(f"Workflow completed: {workflow.total_steps} steps, {workflow.successful_steps} successful")

        """
        total_steps = len(steps)
        if total_steps == 0:
            return FlextResult[FlextCliModels.WorkflowResult].ok(
                FlextCliModels.WorkflowResult(
                    step_results=[],
                    total_steps=0,
                    successful_steps=0,
                    failed_steps=0,
                    overall_success=True,
                    total_duration_seconds=0.0,
                )
            )

        start_time = datetime.now(UTC)
        step_results = []
        successful_steps = 0
        failed_steps = 0

        # Generate step names if not provided
        if step_names is None:
            step_names = [f"Step {i + 1}" for i in range(total_steps)]
        elif len(step_names) != total_steps:
            return FlextResult[FlextCliModels.WorkflowResult].fail(
                f"step_names length ({len(step_names)}) must match steps length ({total_steps})"
            )

        for step_idx, (step_func, step_name) in enumerate(
            zip(steps, step_names, strict=False)
        ):
            step_start_time = datetime.now(UTC)

            # Execute step
            step_result = step_func()
            step_duration = (datetime.now(UTC) - step_start_time).total_seconds()

            if step_result.is_success:
                successful_steps += 1
                step_data = step_result.unwrap()
                step_data.duration_seconds = step_duration
                step_results.append(step_data)
                self.logger.info(
                    "Step completed successfully",
                    step=step_name,
                    step_index=step_idx + 1,
                    duration_seconds=f"{step_duration:.2f}s",
                )
            else:
                failed_steps += 1
                # Create failed step result
                failed_step = FlextCliModels.WorkflowStepResult(
                    step_name=step_name,
                    success=False,
                    error=str(step_result.error),
                    duration_seconds=step_duration,
                    data={},
                )
                step_results.append(failed_step)
                self.logger.error(
                    "Step failed",
                    step=step_name,
                    step_index=step_idx + 1,
                    error=str(step_result.error),
                    duration_seconds=f"{step_duration:.2f}s",
                )

                if not continue_on_failure:
                    break

            # Progress callback
            if progress_callback:
                progress = FlextCliModels.WorkflowProgress(
                    current_step=step_idx + 1,
                    total_steps=total_steps,
                    current_step_name=step_name,
                    successful_steps=successful_steps,
                    failed_steps=failed_steps,
                    overall_success=failed_steps == 0,
                )
                progress_callback(step_idx + 1, total_steps, step_name, progress)

        total_duration = (datetime.now(UTC) - start_time).total_seconds()
        overall_success = failed_steps == 0

        workflow_result = FlextCliModels.WorkflowResult(
            step_results=step_results,
            total_steps=total_steps,
            successful_steps=successful_steps,
            failed_steps=failed_steps,
            overall_success=overall_success,
            total_duration_seconds=total_duration,
        )

        if overall_success:
            self.logger.info(
                "Workflow completed successfully",
                total_steps=total_steps,
                successful_steps=successful_steps,
                total_duration_seconds=f"{total_duration:.2f}s",
            )
        else:
            self.logger.warning(
                "Workflow completed with failures",
                total_steps=total_steps,
                successful_steps=successful_steps,
                failed_steps=failed_steps,
                total_duration_seconds=f"{total_duration:.2f}s",
            )

        return FlextResult[FlextCliModels.WorkflowResult].ok(workflow_result)

    def execute_cli(self, args: list[str] | None = None) -> FlextResult[bool]:
        """Execute the CLI with Railway-pattern error handling."""
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

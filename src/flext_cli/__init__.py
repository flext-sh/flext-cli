"""FLEXT CLI - CLI Foundation Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import get_flext_container

# Version information
from flext_cli.__version__ import __version__

# Normalized version info tuple
__version_info__: tuple[int, ...] = tuple(
    int(x) for x in __version__.split(".") if x.isdigit()
)

# Core configuration
from flext_cli.config import CLIConfig, CLIConfig as TCliConfig
from flext_cli.cli_config import FlextCliConfig
from flext_cli.api import FlextCliApi
from flext_cli.helpers import FlextCliDataProcessor

# Core formatters
from flext_cli.formatters import (
    PlainFormatter,
    OutputFormatter,
    FormatterFactory,
    CSVFormatter,
    JSONFormatter,
    YAMLFormatter,
    TableFormatter,
)

# Core types
from flext_cli.cli_types import (
    CommandArgs,
    CommandArgs as TCliArgs,
    CommandOptions,
    CommandResult,
    CommandStatus,
    ConfigDict,
    ConfigResult,
    EntityId,
    EnvironmentDict,
    ErrorMessage,
    ExitCode,
    FlextCliDataType,
    FlextCliDataType as TCliData,
    FlextCliFileHandler,
    FlextCliFileHandler as TCliHandler,
    OutputData,
    OutputFormat,
    OutputFormat as TCliFormat,
    PathType,
    PathType as TCliPath,
    PluginStatus,
    PositiveIntType,
    ProfileType,
    TUserId,
    URLType,
    ValidationResult,
)

# Configuration utilities
from flext_cli.config import (
    CLIAPIConfig,
    CLIAuthConfig,
    CLIDirectoryConfig,
    CLIOutputConfig,
    CLISettings,
    get_cli_config,
    get_cli_config as get_config,
    get_cli_settings as get_settings,
    get_cli_settings,
)

# Domain models
from flext_cli.models import (
    FlextCliCommand,
    FlextCliCommand as CLICommand,
    FlextCliCommandStatus,
    FlextCliCommandType,
    FlextCliConfiguration,
    FlextCliConfiguration as CLIConfiguration,
    FlextCliContext,
    FlextCliContext as CLIContext,
    FlextCliOutput,
    FlextCliOutputFormat,
    FlextCliPlugin,
    FlextCliPlugin as CLIPlugin,
    FlextCliPluginState,
    FlextCliSession,
    FlextCliSession as CLISession,
    FlextCliSessionState,
    FlextCliWorkspace,
    SessionStatus,
)

# CLI Context and Execution
from flext_cli.context import CLIExecutionContext
from flext_cli.services import (
    CLICommandService,
    CLISessionService,
)

# Service protocols
from flext_cli.protocols import (
    FlextCliCommandProtocol,
    FlextCliServiceProtocol,
    FlextCliValidatorProtocol,
)
from flext_cli.simple_api import (
    create_development_cli_config,
    create_production_cli_config,
    setup_cli,
)

# Base service patterns
from flext_cli.base_service import (
    FlextCliCommandService,
    FlextCliFormatterService,
    FlextCliInteractiveService,
    FlextCliService,
    FlextCliServiceFactory,
    FlextCliValidatorService,
)

# CLI decorators
from flext_cli.decorators import (
    cli_cache_result,
    cli_confirm,
    cli_confirm as confirm_action,  # Alias for test compatibility
    cli_enhanced,
    cli_file_operation,
    cli_handle_keyboard_interrupt,
    cli_inject_config,
    cli_log_execution,
    cli_measure_time,
    cli_measure_time as measure_time,  # Alias for test compatibility
    cli_retry,
    cli_retry as retry,  # Alias for test compatibility
    cli_spinner as with_spinner,  # Alias for test compatibility
    cli_validate_inputs,
)
from flext_cli.base_core import handle_service_result
from flext_cli.helpers import (
    FlextCliHelper as CLIHelper,
    FlextCliHelper,
    FlextCliFileManager,
    flext_cli_batch_validate,
    flext_cli_create_data_processor,
    flext_cli_create_helper,
    flext_cli_create_file_manager,
)
from flext_cli.utils_core import (
    flext_cli_auto_config,
    flext_cli_load_file,
    flext_cli_output_data,
    flext_cli_require_all,
    flext_cli_save_file,
    flext_cli_validate_all,
)
from flext_cli.cli_types import PositiveInt as PositiveInt, URL as URL
from flext_cli.cli_types import (
    ClickPath as ClickPath,
    ExistingDir as ExistingDir,
    ExistingFile as ExistingFile,
    NewFile as NewFile,
)
from flext_cli.decorators import (
    async_command,
    require_auth,
    validate_config,
    validate_config as flext_cli_auto_validate,
)
# All core decorators are now in flext_cli.decorators

# CLI mixins
from flext_cli.cli_mixins import (
    CLICompleteMixin,
    CLIConfigMixin,
    CLIConfigMixin as FlextCliConfigMixin,
    CLIDataMixin,
    CLIExecutionMixin,
    CLIInteractiveMixin,
    CLIInteractiveMixin as FlextCliInteractiveMixin,
    CLILoggingMixin,
    CLIOutputMixin,
    CLIUIMixin,
    CLIValidationMixin,
    CLIValidationMixin as FlextCliValidationMixin,
)
from flext_cli.mixins import (
    FlextCliAdvancedMixin,
    FlextCliBasicMixin,
    FlextCliMixin,
    FlextCliProgressMixin,
    FlextCliResultMixin,
    flext_cli_handle_exceptions,
    flext_cli_require_confirmation,
    flext_cli_with_progress,
    flext_cli_zero_config,
)

# CLI utilities
from flext_cli.cli_utils import (
    cli_batch_process_files,
    cli_create_table,
    cli_create_table as flext_cli_create_table,
    cli_format_output,
    cli_format_output as format_output,
    cli_load_data_file,
    cli_prompt,
    cli_quick_setup,
    cli_quick_setup as flext_cli_quick_setup,
    cli_run_command,
    cli_save_data_file,
)

# Authentication utilities
from flext_cli.cli_auth import (
    clear_auth_tokens,
    get_auth_headers,
    get_auth_token,
    login_command,
    logout_command,
    save_auth_token,
    status_command,
    get_refresh_token,
    get_refresh_token_path,
    get_token_path,
    is_authenticated,
    save_refresh_token,
    should_auto_refresh,
)

# Commands (Click groups/commands) reexports for root-level imports in tests/examples
from flext_cli.cmd_auth import (
    auth as auth,
    login as login,
    logout as logout,
    status as status,
    whoami as whoami,
)
from flext_cli.cmd_debug_alt import (
    debug_cmd as debug_cmd,
    connectivity as connectivity,
    performance as performance,
    trace as trace,
    env as env,
    paths as paths,
    validate as validate,
)
from flext_cli.cmd_config_alt import (
    config as config,
    # print_config_table as _print_config_table,  # Not used
)

# Application commands
from flext_cli.application_commands import (
    CancelCommandCommand,
    CreateConfigCommand,
    DeleteConfigCommand,
    DisablePluginCommand,
    EnablePluginCommand,
    EndSessionCommand,
    ExecuteCommandCommand,
    GetCommandHistoryCommand,
    GetCommandStatusCommand,
    GetSessionInfoCommand,
    InstallPluginCommand,
    ListCommandsCommand,
    ListConfigsCommand,
    ListPluginsCommand,
    StartSessionCommand,
    UninstallPluginCommand,
    UpdateConfigCommand,
    ValidateConfigCommand,
)

# API functions
from flext_cli.api import (
    flext_cli_aggregate_data,
    flext_cli_batch_export,
    flext_cli_batch_export as flext_cli_batch_execute,
    flext_cli_export,
    flext_cli_format,
    flext_cli_table,
    flext_cli_transform_data,
    flext_cli_unwrap_or_default,
    flext_cli_unwrap_or_none,
)

# Client
from flext_cli.client import FlextApiClient

# Domain factory and constants
from flext_cli.entities import CLIEntityFactory, CommandType
from flext_core import FlextConstants as FlextConstants

# Core formatters

# CLI commands
from flext_cli.cli import cli, main


def create_cli_container() -> object:
    """Create or get a FLEXT CLI service container.

    Exposed for tests/examples to import from root package.
    """
    return get_flext_container()


__all__: list[str] = [
    "CLICommand",
    "FlextCliApi",
    "FlextCliDataProcessor",
    "CLICompleteMixin",
    "CLIConfig",
    "CLIConfigMixin",
    "CLIConfiguration",
    "CLIContext",
    "CLIAPIConfig",
    "CLIAuthConfig",
    "CLIDirectoryConfig",
    "CLIOutputConfig",
    "CLISettings",
    "get_cli_config",
    "get_settings",
    "CLICompleteMixin",
    "CLIConfigMixin",
    "CLIDataMixin",
    "CLIExecutionMixin",
    "CLIInteractiveMixin",
    "CLILoggingMixin",
    "CLIOutputMixin",
    "CLIUIMixin",
    "CLIValidationMixin",
    # domain services/context
    "CLICommandService",
    "CLISessionService",
    "CLIExecutionContext",
    "CommandArgs",
    "cli",
    "main",
    "CommandOptions",
    "CLIEntityFactory",
    "CommandResult",
    "CommandStatus",
    "CommandType",
    "ConfigDict",
    "ConfigResult",
    "EntityId",
    "EnvironmentDict",
    "ErrorMessage",
    "ExitCode",
    "FlextCliCommand",
    "FlextCliDataType",
    "FlextCliCommandProtocol",
    "FlextCliCommandService",
    "FlextCliCommandStatus",
    "FlextCliConfiguration",
    "FlextCliContext",
    "FlextCliFormatterService",
    "FlextCliInteractiveService",
    "FlextCliOutput",
    "FlextCliOutputFormat",
    "FlextCliPlugin",
    "FlextCliPluginState",
    "FlextCliService",
    "FlextCliServiceFactory",
    "FlextCliServiceProtocol",
    "FlextCliSession",
    "FlextCliSessionState",
    "FlextCliValidatorProtocol",
    "FlextCliValidatorService",
    "FlextCliWorkspace",
    "FlextApiClient",
    "OutputData",
    "OutputFormat",
    "PathType",
    "PluginStatus",
    "PositiveIntType",
    "ProfileType",
    "SessionStatus",
    "TUserId",
    "URLType",
    "ValidationResult",
    "PlainFormatter",
    "OutputFormatter",
    "FormatterFactory",
    "__version__",
    "__version_info__",
    "clear_auth_tokens",
    "cli_batch_process_files",
    "cli_cache_result",
    "cli_confirm",
    "cli_create_table",
    "cli_enhanced",
    "cli_file_operation",
    "cli_format_output",
    "cli_handle_keyboard_interrupt",
    "cli_inject_config",
    "cli_load_data_file",
    "cli_log_execution",
    "cli_measure_time",
    "cli_prompt",
    "cli_quick_setup",
    "cli_retry",
    "cli_run_command",
    "cli_save_data_file",
    "cli_validate_inputs",
    # Additional top-level compatibility exports
    "handle_service_result",
    "CLIHelper",
    "FlextCliHelper",
    "PositiveInt",
    "URL",
    "ClickPath",
    "ExistingFile",
    "ExistingDir",
    "NewFile",
    "async_command",
    "confirm_action",
    "require_auth",
    "with_spinner",
    "get_auth_headers",
    "get_config",
    "get_settings",
    "get_auth_token",
    "login_command",
    "logout_command",
    "save_auth_token",
    "setup_cli",
    "status_command",
    # API functions
    "flext_cli_aggregate_data",
    "flext_cli_batch_export",
    "flext_cli_export",
    "flext_cli_format",
    "flext_cli_table",
    "flext_cli_transform_data",
    "flext_cli_unwrap_or_default",
    "flext_cli_unwrap_or_none",
    # Root-level helpers for tests/examples
    "create_cli_container",
    # Auth commands
    "auth",
    "login",
    "logout",
    "status",
    "whoami",
    # Debug commands
    "debug_cmd",
    "connectivity",
    "performance",
    "trace",
    "env",
    "paths",
    "validate",
    # Config command
    "config",
    # Measurement aliases
    "measure_time",
    "retry",
    "with_spinner",
    # Missing imports for tests (added back)
    "validate_config",
    "CSVFormatter",
    "JSONFormatter",
    "YAMLFormatter",
    "TableFormatter",
    "CLIPlugin",
    "FlextCliFileManager",
    "FlextCliAdvancedMixin",
    "FlextCliBasicMixin",
    "get_cli_settings",
    "get_refresh_token_path",
    "CLISession",
    "FlextCliCommandType",
    "get_refresh_token",
    "CancelCommandCommand",
    "CreateConfigCommand",
    "DeleteConfigCommand",
    "FlextCliConfig",
    "get_token_path",
    "FlextCliConfigMixin",
    "DisablePluginCommand",
    "is_authenticated",
    "FlextCliInteractiveMixin",
    "format_output",
    "flext_cli_batch_validate",
    "TCliArgs",
    "TCliConfig",
    "save_refresh_token",
    "EnablePluginCommand",
    "FlextCliMixin",
    "should_auto_refresh",
    "TCliData",
    "flext_cli_create_data_processor",
    "flext_cli_create_helper",
    "flext_cli_auto_config",
    "TCliFormat",
    "EndSessionCommand",
    "flext_cli_create_file_manager",
    "FlextCliProgressMixin",
    "ExecuteCommandCommand",
    "FlextCliResultMixin",
    "TCliHandler",
    "flext_cli_batch_execute",
    "FlextCliFileHandler",
    "TCliPath",
    "flext_cli_create_table",
    "GetCommandHistoryCommand",
    "FlextCliValidationMixin",
    "flext_cli_load_file",
    "flext_cli_output_data",
    "flext_cli_quick_setup",
    "GetCommandStatusCommand",
    "GetSessionInfoCommand",
    "InstallPluginCommand",
    "ListCommandsCommand",
    "ListConfigsCommand",
    "ListPluginsCommand",
    "StartSessionCommand",
    "UninstallPluginCommand",
    "UpdateConfigCommand",
    "ValidateConfigCommand",
    "flext_cli_require_all",
    # "flext_cli_auto_retry",  # Not implemented yet, removing from __all__
    "flext_cli_auto_validate",
    "flext_cli_save_file",
    "flext_cli_validate_all",
    "flext_cli_handle_exceptions",
    "flext_cli_require_confirmation",
    "flext_cli_with_progress",
    "flext_cli_zero_config",
    # Simple API exports
    "create_development_cli_config",
    "create_production_cli_config",
    "get_cli_settings",
]

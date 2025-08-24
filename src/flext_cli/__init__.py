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

# API functions
from flext_cli.api import (
    FlextCliApi,
    SessionSummary,
    flext_cli_aggregate_data,
    flext_cli_batch_export,
    flext_cli_export,
    flext_cli_format,
    flext_cli_table,
    flext_cli_transform_data,
    flext_cli_unwrap_or_default,
    flext_cli_unwrap_or_none,
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

# Core formatters
# CLI commands
from flext_cli.cli import cli, main

# Authentication utilities
from flext_cli.cli_auth import (
    clear_auth_tokens,
    get_auth_headers,
    get_auth_token,
    get_refresh_token,
    get_refresh_token_path,
    get_token_path,
    is_authenticated,
    login_command,
    logout_command,
    save_auth_token,
    save_refresh_token,
    should_auto_refresh,
    status_command,
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
    CLILoggingMixin,
    CLIOutputMixin,
    CLIUIMixin,
    CLIValidationMixin,
    CLIValidationMixin as FlextCliValidationMixin,
)

# Core types
from flext_cli.cli_types import (
    URL as URL,
    ClickPath as ClickPath,
    CommandArgs,
    CommandOptions,
    CommandResult,
    CommandStatus,
    ConfigDict,
    ConfigResult,
    EntityId,
    EnvironmentDict,
    ErrorMessage,
    ExistingDir as ExistingDir,
    ExistingFile as ExistingFile,
    ExitCode,
    FlextCliDataType,
    FlextCliFileHandler,
    FlextCliOutputFormat,
    NewFile as NewFile,
    OutputData,
    PathType,
    PathType as TCliPath,
    PluginStatus,
    PositiveInt as PositiveInt,
    PositiveIntType,
    ProfileType,
    TUserId,
    URLType,
    ValidationResult,
)

# CLI utilities
from flext_cli.cli_utils import (
    cli_batch_process_files,
    cli_create_table,
    cli_format_output,
    cli_format_output as format_output,
    cli_load_data_file,
    cli_prompt,
    cli_quick_setup,
    cli_run_command,
    cli_save_data_file,
)

# Client
from flext_cli.client import (
    FlextApiClient,
    Pipeline,
    PipelineConfig,
    PipelineList,
)

# Commands (Click groups/commands) reexports for root-level imports in tests/examples
from flext_cli.commands_auth import (
    auth as auth,
    login as login,
    logout as logout,
    status as status,
    whoami as whoami,
)
from flext_cli.commands_config import (
    config as config,
    # print_config_table as _print_config_table,  # Not used
)
from flext_cli.commands_debug import (
    connectivity as connectivity,
    debug_cmd as debug_cmd,
    env as env,
    paths as paths,
    performance as performance,
    trace as trace,
    validate as validate,
)

# Configuration utilities
from flext_cli.config import (
    FlextCliApiConfig,
    FlextCliAuthConfig,
    FlextCliConfig,
    FlextCliConfig as TCliConfig,
    FlextCliDirectoryConfig,
    FlextCliOutputConfig,
    FlextCliSettings,
    get_cli_config,
    get_cli_config as get_config,
    get_cli_settings,
    get_cli_settings as get_settings,
)
from flext_cli.constants import FlextCliConstants

# CLI Context and Execution
from flext_cli.context import FlextCliExecutionContext
from flext_cli.core_implementations import handle_service_result

# CLI decorators
from flext_cli.decorators import (
    async_command,
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
    require_auth,
    validate_config,
    validate_config as flext_cli_auto_validate,
)

# Domain factory and constants
from flext_cli.entities import CommandType, FlextCliEntityFactory

# Core formatters
from flext_cli.formatters import (
    CSVFormatter,
    FormatterFactory,
    JSONFormatter,
    OutputFormatter,
    PlainFormatter,
    TableFormatter,
    YAMLFormatter,
)

# Foundation patterns
from flext_cli.foundation import (
    FlextCliEntity,
    create_flext_cli_config,
    setup_flext_cli,
)
from flext_cli.helpers import (
    FlextCliDataProcessor,
    FlextCliFileManager,
    FlextCliHelper,
    FlextCliHelper as CLIHelper,
    flext_cli_batch_validate,
    flext_cli_create_data_processor,
    flext_cli_create_file_manager,
    flext_cli_create_helper,
)
from flext_cli.mixins import (
    FlextCliAdvancedMixin,
    FlextCliBasicMixin,
    FlextCliInteractiveMixin,
    FlextCliMixin,
    FlextCliProgressMixin,
    FlextCliResultMixin,
    flext_cli_handle_exceptions,
    flext_cli_require_confirmation,
    flext_cli_with_progress,
    flext_cli_zero_config,
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
    FlextCliOutput,
    FlextCliPlugin,
    FlextCliPluginState,
    FlextCliSession,
    FlextCliSessionState,
    FlextCliWorkspace,
    SessionStatus,
)

# Base service patterns
from flext_cli.service_implementations import (
    FlextCliFormatterService,
    FlextCliInteractiveService,
    FlextCliService,
    FlextCliServiceFactory,
    FlextCliValidatorService,
)

# Service protocols
from flext_cli.service_protocols import (
    FlextCliCommandProtocol,
    FlextCliServiceProtocol,
    FlextCliValidatorProtocol,
)

# Concrete service implementations
from flext_cli.services import (
    FlextCliCommandService,
    FlextCliSessionService,
)
from flext_cli.simple_api import (
    create_development_cli_config,
    create_production_cli_config,
    setup_cli,
)
from flext_cli.utils_core import (
    flext_cli_auto_config,
    flext_cli_batch_execute,
    flext_cli_create_table,
    flext_cli_load_file,
    flext_cli_output_data,
    flext_cli_quick_setup,
    flext_cli_require_all,
    flext_cli_save_file,
    flext_cli_validate_all,
)

# Output formatting utilities
from flext_cli.utils_output import (
    format_json,
    format_pipeline,
    format_pipeline_list,
    format_plugin_list,
    format_yaml,
    print_error,
    print_info,
    print_success,
    print_warning,
)


def create_cli_container() -> object:
    """Create or get a FLEXT CLI service container.

    Exposed for tests/examples to import from root package.
    """
    return get_flext_container()


# Output formatting utilities - moved to top section to fix E402

__all__: list[str] = [
    "URL",
    "CLICommand",
    "CLICompleteMixin",
    "CLICompleteMixin",
    "CLIConfigMixin",
    "CLIConfigMixin",
    "CLIConfiguration",
    "CLIDataMixin",
    "CLIExecutionMixin",
    "CLIHelper",
    "CLIInteractiveMixin",
    "CLILoggingMixin",
    "CLIOutputMixin",
    "CLIUIMixin",
    "CLIValidationMixin",
    "CSVFormatter",
    "CancelCommandCommand",
    "ClickPath",
    "CommandArgs",
    "CommandArgs",
    "CommandOptions",
    "CommandResult",
    "CommandStatus",
    "CommandType",
    "ConfigDict",
    "ConfigResult",
    "CreateConfigCommand",
    "DeleteConfigCommand",
    "DisablePluginCommand",
    "EnablePluginCommand",
    "EndSessionCommand",
    "EntityId",
    "EnvironmentDict",
    "ErrorMessage",
    "ExecuteCommandCommand",
    "ExistingDir",
    "ExistingFile",
    "ExitCode",
    # Client classes
    "FlextApiClient",
    "FlextApiClient",
    "FlextCliAdvancedMixin",
    "FlextCliApi",
    "FlextCliApiConfig",
    "FlextCliAuthConfig",
    "FlextCliBasicMixin",
    "FlextCliCommand",
    "FlextCliCommandProtocol",
    # domain services/context
    "FlextCliCommandService",
    "FlextCliCommandService",
    "FlextCliCommandStatus",
    "FlextCliCommandType",
    "FlextCliConfig",
    "FlextCliConfig",
    "FlextCliConfigMixin",
    "FlextCliConfiguration",
    "FlextCliConstants",
    "FlextCliContext",
    "FlextCliDataProcessor",
    "FlextCliDataType",
    "FlextCliDataType",
    "FlextCliDirectoryConfig",
    "FlextCliEntity",
    "FlextCliEntityFactory",
    "FlextCliExecutionContext",
    "FlextCliFileHandler",
    "FlextCliFileHandler",
    "FlextCliFileManager",
    "FlextCliFormatterService",
    "FlextCliHelper",
    "FlextCliInteractiveMixin",
    "FlextCliInteractiveService",
    "FlextCliMixin",
    "FlextCliOutput",
    "FlextCliOutputConfig",
    "FlextCliOutputFormat",
    "FlextCliOutputFormat",
    "FlextCliPlugin",
    "FlextCliPlugin",
    "FlextCliPluginState",
    "FlextCliProgressMixin",
    "FlextCliResultMixin",
    "FlextCliService",
    "FlextCliServiceFactory",
    "FlextCliServiceProtocol",
    "FlextCliSession",
    "FlextCliSession",
    "FlextCliSessionService",
    "FlextCliSessionState",
    "FlextCliSettings",
    "FlextCliValidationMixin",
    "FlextCliValidatorProtocol",
    "FlextCliValidatorService",
    "FlextCliWorkspace",
    "FormatterFactory",
    "GetCommandHistoryCommand",
    "GetCommandStatusCommand",
    "GetSessionInfoCommand",
    "InstallPluginCommand",
    "JSONFormatter",
    "ListCommandsCommand",
    "ListConfigsCommand",
    "ListPluginsCommand",
    "NewFile",
    "OutputData",
    "OutputFormatter",
    "PathType",
    "Pipeline",
    "PipelineConfig",
    "PipelineList",
    "PlainFormatter",
    "PluginStatus",
    "PositiveInt",
    "PositiveIntType",
    "ProfileType",
    "SessionStatus",
    "SessionSummary",
    "StartSessionCommand",
    "TCliConfig",
    "TCliPath",
    "TUserId",
    "TableFormatter",
    "URLType",
    "UninstallPluginCommand",
    "UpdateConfigCommand",
    "ValidateConfigCommand",
    "ValidationResult",
    "YAMLFormatter",
    "__version__",
    "__version_info__",
    "async_command",
    # Auth commands
    "auth",
    "clear_auth_tokens",
    "cli",
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
    # Config command
    "config",
    "confirm_action",
    "connectivity",
    # Root-level helpers for tests/examples
    "create_cli_container",
    # Simple API exports
    "create_development_cli_config",
    "create_flext_cli_config",
    "create_production_cli_config",
    # Debug commands
    "debug_cmd",
    "env",
    # API functions
    "flext_cli_aggregate_data",
    "flext_cli_auto_config",
    # "flext_cli_auto_retry",  # Not implemented yet, removing from __all__
    "flext_cli_auto_validate",
    "flext_cli_batch_execute",
    "flext_cli_batch_export",
    "flext_cli_batch_validate",
    "flext_cli_create_data_processor",
    "flext_cli_create_file_manager",
    "flext_cli_create_helper",
    "flext_cli_create_table",
    "flext_cli_export",
    "flext_cli_format",
    "flext_cli_handle_exceptions",
    "flext_cli_load_file",
    "flext_cli_output_data",
    "flext_cli_quick_setup",
    "flext_cli_require_all",
    "flext_cli_require_confirmation",
    "flext_cli_save_file",
    "flext_cli_table",
    "flext_cli_transform_data",
    "flext_cli_unwrap_or_default",
    "flext_cli_unwrap_or_none",
    "flext_cli_validate_all",
    "flext_cli_with_progress",
    "flext_cli_zero_config",
    "format_json",
    "format_output",
    "format_pipeline",
    "format_pipeline_list",
    "format_plugin_list",
    "format_yaml",
    "get_auth_headers",
    "get_auth_token",
    "get_cli_config",
    "get_cli_settings",
    "get_cli_settings",
    "get_config",
    "get_refresh_token",
    "get_refresh_token_path",
    "get_settings",
    "get_settings",
    "get_token_path",
    # Additional top-level compatibility exports
    "handle_service_result",
    "is_authenticated",
    "login",
    "login_command",
    "logout",
    "logout_command",
    "main",
    # Measurement aliases
    "measure_time",
    "paths",
    "performance",
    # Output utilities
    "print_error",
    "print_info",
    "print_success",
    "print_warning",
    "require_auth",
    "retry",
    "save_auth_token",
    "save_refresh_token",
    "setup_cli",
    "setup_flext_cli",
    "should_auto_refresh",
    "status",
    "status_command",
    "trace",
    "validate",
    # Missing imports for tests (added back)
    "validate_config",
    "whoami",
    "with_spinner",
    "with_spinner",
]

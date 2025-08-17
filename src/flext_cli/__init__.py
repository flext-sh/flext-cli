"""FLEXT CLI - CLI Foundation Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from flext_core import get_flext_container

# Version information
from flext_cli.__version__ import __version__

# Normalized version info tuple
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# Core configuration
from flext_cli.cli_config import CLIConfig
from flext_cli.api import FlextCliApi
from flext_cli.core.helpers import FlextCliDataProcessor

# Core formatters
from flext_cli.core.formatters import PlainFormatter, OutputFormatter, FormatterFactory

# Core types
from flext_cli.cli_types import (
    CommandArgs,
    CommandOptions,
    CommandResult,
    CommandStatus,
    CommandType,
    ConfigDict,
    ConfigResult,
    EntityId,
    EnvironmentDict,
    ErrorMessage,
    ExitCode,
    OutputData,
    OutputFormat,
    PathType,
    PluginStatus,
    PositiveIntType,
    ProfileType,
    SessionStatus,
    TUserId,
    URLType,
    ValidationResult,
)

# Configuration utilities
from flext_cli.config import (
    CLISettings,
    CLIAPIConfig,
    CLIAuthConfig,
    CLIDirectoryConfig,
    CLIOutputConfig,
    get_cli_config,
    get_cli_config as get_config,
    get_cli_settings as get_settings,
)

# Domain models
from flext_cli.models import (
    FlextCliCommand,
    FlextCliCommand as CLICommand,
    FlextCliCommandStatus,
    FlextCliConfiguration,
    FlextCliConfiguration as CLIConfiguration,
    FlextCliContext,
    FlextCliContext as CLIContext,
    FlextCliOutput,
    FlextCliOutput as CLIOutput,
    FlextCliOutputFormat,
    FlextCliPlugin,
    FlextCliPlugin as CLIPlugin,
    FlextCliPluginState,
    FlextCliSession,
    FlextCliSession as CLISession,
    FlextCliSessionState,
    FlextCliWorkspace,
)

# CLI Context and Execution
from flext_cli.domain.cli_context import CLIExecutionContext
from flext_cli.domain.cli_services import (
    CLICommandService,
    CLISessionService,
)

# Service protocols
from flext_cli.protocols import (
    FlextCliCommandProtocol,
    FlextCliServiceProtocol,
    FlextCliValidatorProtocol,
)
from flext_cli.simple_api import setup_cli

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
from flext_cli.cli_decorators import (
    cli_cache_result,
    cli_confirm,
    cli_enhanced,
    cli_file_operation,
    cli_handle_keyboard_interrupt,
    cli_inject_config,
    cli_log_execution,
    cli_measure_time,
    cli_retry,
    cli_validate_inputs,
)
from flext_cli.core.base import handle_service_result
from flext_cli.core.helpers import FlextCliHelper as CLIHelper
from flext_cli.core.types import PositiveInt as PositiveInt, URL as URL
from flext_cli.core.types import (
    ClickPath as ClickPath,
    ExistingDir as ExistingDir,
    ExistingFile as ExistingFile,
    NewFile as NewFile,
)
from flext_cli.core.decorators import (
    async_command,
    confirm_action,
    measure_time as core_measure_time,
    require_auth,
    retry as core_retry,
    with_spinner,
)
from flext_cli.core.decorators import measure_time as measure_time
from flext_cli.core.decorators import retry as retry

# CLI mixins
from flext_cli.cli_mixins import (
    CLICompleteMixin,
    CLIConfigMixin,
    CLIDataMixin,
    CLIExecutionMixin,
    CLIInteractiveMixin,
    CLILoggingMixin,
    CLIOutputMixin,
    CLIUIMixin,
    CLIValidationMixin,
)

# CLI utilities
from flext_cli.cli_utils import (
    cli_batch_process_files,
    cli_create_table,
    cli_format_output,
    cli_load_data_file,
    cli_prompt,
    cli_quick_setup,
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
)

# Commands (Click groups/commands) reexports for root-level imports in tests/examples
from flext_cli.commands.auth import (
    auth as auth,
    login as login,
    logout as logout,
    status as status,
)
from flext_cli.commands.debug import (
    debug_cmd as debug_cmd,
    connectivity as connectivity,
    performance as performance,
    trace as trace,
    env as env,
    paths as paths,
)
from flext_cli.commands.config import config as config

# API functions
from flext_cli.api import (
    flext_cli_aggregate_data,
    flext_cli_batch_export,
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
from flext_cli.domain.entities import CLIEntityFactory
from flext_cli.constants import FlextConstants as FlextConstants

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
    "get_cli_config",
    "get_cli_settings",
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
    "PositiveInt",
    "URL",
    "ClickPath",
    "ExistingFile",
    "ExistingDir",
    "NewFile",
    "async_command",
    "confirm_action",
    "core_measure_time",
    "require_auth",
    "core_retry",
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
]

"""FLEXT CLI - CLI Foundation Library."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Callable

from flext_core import FlextResult

# Version information
from flext_cli.__version__ import __version__

# Normalized version info tuple
__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

# Core configuration
from flext_cli.cli_config import CLIConfig

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
    validate_config,
    require_auth,
    retry as core_retry,
    validate_config as core_validate_config,
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


__all__: list[str] = [
    "CLICommand",
    "CLICompleteMixin",
    "CLIConfig",
    "CLIConfigMixin",
    "CLIConfiguration",
    "CLIContext",
    "CLIDataMixin",
    "CLIExecutionMixin",
    "CLIInteractiveMixin",
    "CLILoggingMixin",
    "CLIOutput",
    "CLIOutputMixin",
    "CLIPlugin",
    "CLISession",
    "CLISettings",
    "CLIUIMixin",
    "CLIValidationMixin",
    "CommandArgs",
    "CommandOptions",
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
    "core_validate_config",
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
]

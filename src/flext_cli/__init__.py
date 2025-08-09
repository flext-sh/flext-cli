"""FlextCli - Zero-Boilerplate Foundation Library for CLI Applications.

This library provides massive boilerplate reduction for CLI applications
through flext-core integration, FlextResult patterns, and Rich console
integration. All public APIs use FlextCli prefixes for consistency.

Foundation Features:
    - FlextCliEntity: Zero-boilerplate CLI entities with automatic features
    - FlextCliConfig: Configuration management with FlextSettings
    - FlextCliHelper: Comprehensive utility functions for common operations
    - Zero-boilerplate setup functions for immediate productivity

Examples:
    >>> from flext_cli import FlextCliEntity, create_flext_cli_config
    >>>
    >>> # Zero-boilerplate entity
    >>> class MyCommand(FlextCliEntity):
    ...     name: str = "my-command"
    ...
    ...     def execute(self) -> FlextResult[str]:
    ...         return FlextResult.ok("Command executed")
    >>>
    >>> # Railway-oriented configuration
    >>> config = create_flext_cli_config(debug=True, profile="dev").unwrap()

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# Version
from flext_cli.__version__ import __version__

# Advanced Types - Explicit imports to avoid F403
from flext_cli.advanced_types import (
    FlextCliDataDict,
    FlextCliDataList,
    FlextCliFilePath,
    FlextCliOperationResult,
    FlextCliOutputFormat,
    FlextCliPathLike,
    FlextCliValidationResult,
)

# Helper Functions and Classes
from flext_cli.core.helpers import (
    FlextCliHelper,
    flext_cli_create_data_processor,
    flext_cli_create_file_manager,
    flext_cli_create_helper,
    flext_cli_create_progress,
    flext_cli_load_json,
    flext_cli_quick_confirm,
    flext_cli_save_data,
    flext_cli_validate_dir,
    flext_cli_validate_email,
    flext_cli_validate_file,
    flext_cli_validate_path,
    flext_cli_validate_url,
)

# Core Mixins - Interactive patterns
from flext_cli.core.mixins import (
    FlextCliAdvancedMixin,
    FlextCliInteractiveMixin,
    FlextCliProgressMixin,
    FlextCliResultMixin,
    flext_cli_auto_retry,
    flext_cli_auto_validate,
    flext_cli_handle_exceptions,
    flext_cli_require_confirmation,
    flext_cli_with_progress,
    flext_cli_zero_config,
)

# Type Definitions
from flext_cli.core.typedefs import (
    FlextCliCommandStatus,
    FlextCliCommandType,
    FlextCliConfigData,
    FlextCliLogLevel,
    FlextCliResult,
    FlextCliValidationType,
    flext_cli_command_error,
    flext_cli_command_result,
)

# Advanced Decorators - Explicit imports to avoid F403
from flext_cli.decorators import (
    flext_cli_cache_result,
    flext_cli_confirm,
    flext_cli_enhanced,
    flext_cli_file_operation,
    flext_cli_handle_keyboard_interrupt,
    flext_cli_inject_config,
    flext_cli_log_execution,
    flext_cli_measure_time,
    flext_cli_retry,
    flext_cli_validate_inputs,
)

# Domain Entities
from flext_cli.domain.entities import (
    CLICommand,
    CLIPlugin,
    CLISession,
    CommandStatus,
    CommandType,
)

# Foundation Classes (Primary API) - Fixed imports
from flext_cli.foundation import (
    FlextCliConfig,
    FlextCliEntity,
    create_cli_config,  # Deprecated: use create_flext_cli_config
    create_flext_cli_config,
    legacy_setup_cli,  # Deprecated: use setup_flext_cli
    setup_cli,  # Deprecated: use setup_flext_cli
    setup_flext_cli,
)

# Advanced Mixins - Explicit imports to avoid F403
from flext_cli.mixins import (
    FlextCliCompleteMixin,
    FlextCliConfigMixin,
    FlextCliDataMixin,
    FlextCliExecutionMixin,
    FlextCliUIMixin,
    FlextCliValidationMixin,
)

# Foundation Library Public API - Only Root Namespace Access
__all__ = [
    "CLICommand",
    "CLIPlugin",
    "CLISession",
    "CommandStatus",
    "CommandType",
    "FlextCliAdvancedMixin",
    "FlextCliCommandStatus",
    "FlextCliCommandType",
    "FlextCliCompleteMixin",
    "FlextCliConfig",
    "FlextCliConfigData",
    "FlextCliConfigMixin",
    "FlextCliDataDict",
    "FlextCliDataList",
    "FlextCliDataMixin",
    "FlextCliEntity",
    "FlextCliExecutionMixin",
    "FlextCliFilePath",
    "FlextCliHelper",
    "FlextCliInteractiveMixin",
    "FlextCliLogLevel",
    "FlextCliOperationResult",
    "FlextCliOutputFormat",
    "FlextCliPathLike",
    "FlextCliProgressMixin",
    "FlextCliResult",
    "FlextCliResultMixin",
    "FlextCliUIMixin",
    "FlextCliValidationMixin",
    "FlextCliValidationResult",
    "FlextCliValidationType",
    "__version__",
    "create_cli_config",
    "create_flext_cli_config",
    "flext_cli_auto_retry",
    "flext_cli_auto_validate",
    "flext_cli_cache_result",
    "flext_cli_command_error",
    "flext_cli_command_result",
    "flext_cli_confirm",
    "flext_cli_create_data_processor",
    "flext_cli_create_file_manager",
    "flext_cli_create_helper",
    "flext_cli_create_progress",
    "flext_cli_enhanced",
    "flext_cli_file_operation",
    "flext_cli_handle_exceptions",
    "flext_cli_handle_keyboard_interrupt",
    "flext_cli_inject_config",
    "flext_cli_load_json",
    "flext_cli_log_execution",
    "flext_cli_measure_time",
    "flext_cli_quick_confirm",
    "flext_cli_require_confirmation",
    "flext_cli_retry",
    "flext_cli_save_data",
    "flext_cli_validate_dir",
    "flext_cli_validate_email",
    "flext_cli_validate_file",
    "flext_cli_validate_inputs",
    "flext_cli_validate_path",
    "flext_cli_validate_url",
    "flext_cli_with_progress",
    "flext_cli_zero_config",
    "legacy_setup_cli",
    "setup_cli",
    "setup_flext_cli",
]

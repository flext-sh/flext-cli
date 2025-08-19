"""Core primitives for the FLEXT CLI package.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# Note: FlextCliService and FlextService are in the parent core.py file
# They cannot be imported here due to circular import issues

# Base patterns and context
from flext_cli.core.base import CLIContext, handle_service_result

# Decorators
from flext_cli.core.decorators import (
    async_command,
    confirm_action,
    measure_time,
    require_auth,
    retry,
    with_spinner,
)

# Formatters
from flext_cli.core.formatters import (
    CSVFormatter,
    FormatterFactory,
    JSONFormatter,
    OutputFormatter,
    PlainFormatter,
    TableFormatter,
    YAMLFormatter,
)

# Helpers and utilities
from flext_cli.core.helpers import (
    FlextCliDataProcessor,
    FlextCliFileManager,
    FlextCliHelper,
    flext_cli_batch_validate,
    flext_cli_create_data_processor,
    flext_cli_create_file_manager,
    flext_cli_create_helper,
)

# Mixins
from flext_cli.core.mixins import (
    FlextCliAdvancedMixin,
    FlextCliBasicMixin,
    FlextCliConfigMixin,
    FlextCliInteractiveMixin,
    FlextCliMixin,
    FlextCliProgressMixin,
    FlextCliResultMixin,
    FlextCliValidationMixin,
    flext_cli_auto_retry,
    flext_cli_auto_validate,
    flext_cli_handle_exceptions,
    flext_cli_require_confirmation,
    flext_cli_with_progress,
    flext_cli_zero_config,
)

# Types
from flext_cli.core.types import (
    ClickPath,
    ExistingDir,
    ExistingFile,
    NewFile,
    PositiveInt,
    URL,
    URLType,
)

# Utilities
from flext_cli.core.utils import (
    flext_cli_auto_config,
    flext_cli_batch_execute,
    flext_cli_create_table,
    flext_cli_load_file,
    flext_cli_output_data,
    flext_cli_quick_setup,
    flext_cli_require_all,
    flext_cli_save_file,
    flext_cli_validate_all,
    track,
)

__all__ = [
    # Base patterns
    "CLIContext",
    "handle_service_result",
    # Decorators
    "async_command",
    "confirm_action",
    "measure_time",
    "require_auth",
    "retry",
    "with_spinner",
    # Formatters
    "CSVFormatter",
    "FormatterFactory",
    "JSONFormatter",
    "OutputFormatter",
    "PlainFormatter",
    "TableFormatter",
    "YAMLFormatter",
    # Helpers
    "FlextCliDataProcessor",
    "FlextCliFileManager",
    "FlextCliHelper",
    "flext_cli_batch_validate",
    "flext_cli_create_data_processor",
    "flext_cli_create_file_manager",
    "flext_cli_create_helper",
    # Mixins
    "FlextCliAdvancedMixin",
    "FlextCliBasicMixin",
    "FlextCliConfigMixin",
    "FlextCliInteractiveMixin",
    "FlextCliMixin",
    "FlextCliProgressMixin",
    "FlextCliResultMixin",
    "FlextCliValidationMixin",
    "flext_cli_auto_retry",
    "flext_cli_auto_validate",
    "flext_cli_handle_exceptions",
    "flext_cli_require_confirmation",
    "flext_cli_with_progress",
    "flext_cli_zero_config",
    # Types
    "ClickPath",
    "ExistingDir",
    "ExistingFile",
    "NewFile",
    "PositiveInt",
    "URL",
    "URLType",
    # Utilities
    "flext_cli_auto_config",
    "flext_cli_batch_execute",
    "flext_cli_create_table",
    "flext_cli_load_file",
    "flext_cli_output_data",
    "flext_cli_quick_setup",
    "flext_cli_require_all",
    "flext_cli_save_file",
    "flext_cli_validate_all",
    "track",
]

"""FLEXT CLI - Command and context aliases.

This module provides backward compatibility aliases for CLI commands and contexts,
maintaining a clean separation between implementation and public API.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.cli import (
    auth as auth_cmd,
    debug as debug_cmd,
    login as login_cmd,
    logout as logout_cmd,
    status as status_cmd,
)
from flext_cli.config import FlextCliConfig
from flext_cli.context import FlextCliContext
from flext_cli.decorators import FlextCliDecorators

# Command aliases for backward compatibility
auth = auth_cmd
status = status_cmd
login = login_cmd
logout = logout_cmd
debug = debug_cmd
config = FlextCliConfig
handle_service_result = FlextCliDecorators.handle_service_result

# Context aliases
FlextCliExecutionContext = FlextCliContext.ExecutionContext


def get_cli_config() -> FlextCliConfig:
    """Get current CLI configuration.

    Returns:
        Current CLI configuration instance.

    """
    return FlextCliConfig.get_current()

"""CLI configuration module using flext-core as base.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This module provides configuration management for the FLEXT CLI using
the standardized configuration system from flext-core.
"""

from __future__ import annotations

# Re-export from main config module
from flext_cli.config.cli_config import (
    CLIConfig,
    CLISettings,
    get_cli_config,
    get_cli_settings,
)

__all__ = [
    "CLIConfig",
    "CLISettings",
    "get_cli_config",
    "get_cli_settings",
]

"""Application subpackage for CLI tests and examples.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

# Application layer commands
from flext_cli.application.commands import (
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

__all__ = [
    # Command classes
    "CancelCommandCommand",
    "CreateConfigCommand",
    "DeleteConfigCommand",
    "DisablePluginCommand",
    "EnablePluginCommand",
    "EndSessionCommand",
    "ExecuteCommandCommand",
    "GetCommandHistoryCommand",
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
]

"""FLEXT CLI Typings - Single unified class following FLEXT standards.

Provides CLI-specific type definitions using flext-core patterns.
Single FlextCliTypings class with nested type definitions following FLEXT pattern.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypeVar

from flext_core import FlextTypes


class FlextCliTypings(FlextTypes):
    """Single unified CLI typings class following FLEXT standards.

    Contains all type definitions for CLI domain operations.
    Follows FLEXT pattern: one class per module with nested definitions.

    IMPORTANT: This class contains ONLY type definitions and aliases.
    All constants have been moved to FlextCliConstants for proper separation.
    """

    # Type variables for CLI generics
    T = TypeVar("T")
    CommandHandler = TypeVar("CommandHandler")

    # CLI-specific type aliases extending flext-core using Python 3.13+ type keyword
    type CliConfigData = FlextTypes.Core.Dict
    type CliCommandArgs = FlextTypes.Core.Dict
    type CliCommandResult = FlextTypes.Core.Dict
    type CliFormatData = FlextTypes.Core.Dict

    # CLI output format types
    type OutputFormatType = str
    type CliExitCode = int

    # CLI command handler types
    type CommandHandlerFunc = object  # Will be more specific when protocols are defined

    # CLI authentication types
    type AuthTokenData = FlextTypes.Core.Dict
    type AuthConfigData = FlextTypes.Core.Dict

    # CLI debug and logging types
    type DebugInfoData = FlextTypes.Core.Dict
    type LoggingConfigData = FlextTypes.Core.Dict


__all__ = [
    "FlextCliTypings",
]

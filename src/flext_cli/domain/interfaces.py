"""CLI domain interfaces for dependency injection.

Copyright (c) 2025 FLEXT Contributors
SPDX-License-Identifier: MIT

This module defines CLI-specific interfaces that follow Clean Architecture
principles and enable proper dependency injection.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any

# Use direct import for runtime availability

if TYPE_CHECKING:
    from flext_core.domain.shared_types import ServiceResult

class CLICommandProvider(ABC):
    """Abstract CLI command provider interface for dependency injection."""

    @abstractmethod
    def get_command_name(self) -> str:
        """Get the command name this provider handles.

        Returns:
            Command name identifier

        """
        ...

    @abstractmethod
    def get_command_description(self) -> str:
        """Get the command description.

        Returns:
            Human-readable command description

        """
        ...

    @abstractmethod
    async def execute_command(
        self, args: dict[str, Any], options: dict[str, Any],
    ) -> ServiceResult[Any]:
        """Execute the CLI command.

        Args:
            args: Command arguments
            options: Command options

        Returns:
            ServiceResult containing command execution result or error

        """
        ...

    @abstractmethod
    def get_supported_formats(self) -> list[str]:
        """Get supported output formats for this command.

        Returns:
            List of supported output formats (e.g., ['table', 'json', 'yaml'])

        """
        ...


class CLIOutputFormatter(ABC):
    """Abstract CLI output formatter interface."""

    @abstractmethod
    def format_output(self, data: Any, format_type: str = "table") -> str:
        """Format data for CLI output.

        Args:
            data: Data to format
            format_type: Output format type

        Returns:
            Formatted string for display

        """
        ...


class CLIConfigProvider(ABC):
    """Abstract CLI configuration provider interface."""

    @abstractmethod
    def get_config(self) -> dict[str, Any]:
        """Get CLI configuration.

        Returns:
            CLI configuration dictionary

        """
        ...

    @abstractmethod
    def set_config(self, key: str, value: Any) -> None:
        """Set CLI configuration value.

        Args:
            key: Configuration key
            value: Configuration value

        """
        ...


__all__ = [
    "CLICommandProvider",
    "CLIConfigProvider",
    "CLIOutputFormatter",
]

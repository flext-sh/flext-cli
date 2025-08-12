"""FLEXT CLI Protocols - Interface definitions extending flext-core protocols.

This module defines CLI-specific protocols that extend flext-core protocols.
All protocols follow SOLID principles and use Python 3.13+ typing features.

IMPORTANT: This module ONLY defines CLI-specific protocols. Base protocols
are imported from flext-core to avoid duplication.

Quality standards:
- Python 3.13 typing and runtime-checkable protocols
- flext-core FlextResult for all operations that can fail
- No duplication - always extend flext-core protocols
- Import from flext-core root, never from submodules

Copyright (c) 2025 FLEXT Team
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import abstractmethod
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from pathlib import Path

    import click
    from flext_core import FlextResult
    from rich.console import Console


@runtime_checkable
class FlextCliCommandProtocol(Protocol):
    """Protocol for CLI command implementations.

    Extends FlextProtocol from flext-core for CLI-specific commands.
    """

    @abstractmethod
    def execute(
        self,
        context: dict[str, object],
        **kwargs: object,
    ) -> FlextResult[object]:
        """Execute the CLI command."""
        ...

    @abstractmethod
    def validate_args(self, **kwargs: object) -> FlextResult[dict[str, object]]:
        """Validate command arguments."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Command name."""
        ...

    @property
    @abstractmethod
    def description(self) -> str:
        """Command description."""
        ...


@runtime_checkable
class FlextCliFormatterProtocol(Protocol):
    """Protocol for CLI output formatters.

    Extends FlextProtocol for formatting CLI output.
    """

    @abstractmethod
    def format(
        self,
        data: object,
        format_type: str = "table",
        **options: object,
    ) -> FlextResult[str]:
        """Format data for display."""
        ...

    @abstractmethod
    def format_error(self, error: str | Exception, verbose: bool = False) -> str:
        """Format error message."""
        ...

    @property
    @abstractmethod
    def supported_formats(self) -> list[str]:
        """List of supported formats."""
        ...


@runtime_checkable
class FlextCliValidatorProtocol(Protocol):
    """Protocol for CLI input validators.

    Extends FlextValidatorProtocol from flext-core with CLI-specific validation.
    """

    @abstractmethod
    def validate_command(
        self,
        command: str,
        available_commands: list[str],
    ) -> FlextResult[str]:
        """Validate a CLI command."""
        ...

    @abstractmethod
    def validate_path(
        self,
        path: str | Path,
        must_exist: bool = False,
        must_be_file: bool = False,
        must_be_dir: bool = False,
    ) -> FlextResult[Path]:
        """Validate a file system path."""
        ...


@runtime_checkable
class FlextCliServiceProtocol(Protocol):
    """Protocol for CLI services.

    Extends FlextServiceProtocol from flext-core.
    """

    @abstractmethod
    def initialize_console(
        self,
        width: int | None = None,
        theme: str | None = None,
    ) -> FlextResult[Console]:
        """Initialize Rich console."""
        ...

    @abstractmethod
    def load_configuration(
        self,
        profile: str = "default",
        config_file: Path | None = None,
    ) -> FlextResult[dict[str, object]]:
        """Load CLI configuration."""
        ...


@runtime_checkable
class FlextCliPluginProtocol(Protocol):
    """Protocol for CLI plugins.

    Extends FlextProtocol for plugin system.
    """

    @abstractmethod
    def register_commands(self, cli: click.Group) -> FlextResult[None]:
        """Register plugin commands."""
        ...

    @abstractmethod
    def initialize(self, context: dict[str, object]) -> FlextResult[None]:
        """Initialize plugin."""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        ...

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version."""
        ...


@runtime_checkable
class FlextCliInteractiveProtocol(Protocol):
    """Protocol for interactive CLI components.

    Extends FlextProtocol for user interaction.
    """

    @abstractmethod
    def prompt(
        self,
        message: str,
        default: str | None = None,
        password: bool = False,
    ) -> FlextResult[str]:
        """Prompt user for input."""
        ...

    @abstractmethod
    def confirm(self, message: str, default: bool = False) -> FlextResult[bool]:
        """Ask for confirmation."""
        ...

    @abstractmethod
    def select(
        self,
        message: str,
        choices: list[str],
        default: str | None = None,
    ) -> FlextResult[str]:
        """Select from choices."""
        ...


@runtime_checkable
class FlextConfigProvider(Protocol):
    """Protocol for configuration providers.

    Kept for backward compatibility. New code should use
    FlextCliConfigProtocol instead.
    """

    def get_config(
        self,
        key: str,
        default: object | None = None,
    ) -> FlextResult[object]:
        """Get configuration value by key."""
        ...

    def get_priority(self) -> int:
        """Return provider priority."""
        ...

    def get_all(self) -> dict[str, object]:
        """Return all configuration values."""
        ...


@runtime_checkable
class FlextCliConfigProtocol(Protocol):
    """Protocol for CLI configuration management.

    Extends FlextProtocol for configuration hierarchy.
    """

    @abstractmethod
    def get(self, key: str, default: object = None) -> FlextResult[object]:
        """Get configuration value."""
        ...

    @abstractmethod
    def set(self, key: str, value: object) -> FlextResult[None]:
        """Set configuration value."""
        ...

    @abstractmethod
    def load_from_file(self, path: Path) -> FlextResult[None]:
        """Load configuration from file."""
        ...

    @abstractmethod
    def save_to_file(self, path: Path) -> FlextResult[None]:
        """Save configuration to file."""
        ...

    @property
    @abstractmethod
    def providers(self) -> list[FlextConfigProvider]:
        """List of configuration providers."""
        ...


# Type aliases for implementations
FlextCliCommandImpl = FlextCliCommandProtocol
FlextCliFormatterImpl = FlextCliFormatterProtocol
FlextCliValidatorImpl = FlextCliValidatorProtocol
FlextCliServiceImpl = FlextCliServiceProtocol
FlextCliPluginImpl = FlextCliPluginProtocol
FlextCliInteractiveImpl = FlextCliInteractiveProtocol
FlextCliConfigImpl = FlextCliConfigProtocol


__all__ = [
    # Implementation aliases
    "FlextCliCommandImpl",
    # Protocols
    "FlextCliCommandProtocol",
    "FlextCliConfigImpl",
    "FlextCliConfigProtocol",
    "FlextCliFormatterImpl",
    "FlextCliFormatterProtocol",
    "FlextCliInteractiveImpl",
    "FlextCliInteractiveProtocol",
    "FlextCliPluginImpl",
    "FlextCliPluginProtocol",
    "FlextCliServiceImpl",
    "FlextCliServiceProtocol",
    "FlextCliValidatorImpl",
    "FlextCliValidatorProtocol",
    "FlextConfigProvider",  # Backward compatibility
]

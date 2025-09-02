"""FlextCli Protocols - Modern CLI abstraction protocols for FLEXT ecosystem.

Provides abstract contracts for CLI operations, output formatting, command execution,
and session management that other projects can implement.

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import abstractmethod
from typing import Protocol, TypeVar, runtime_checkable

from flext_core import FlextResult

# Type variables for generic protocols
T = TypeVar("T")
TData = TypeVar("TData")


# =============================================================================
# FLEXT CLI PROTOCOLS - Modern CLI abstraction patterns
# =============================================================================

@runtime_checkable
class FlextCliFormatterProtocol(Protocol):
    """Modern CLI formatter protocol for type-safe data formatting.

    Defines the contract for formatting data into various output formats
    with consistent error handling using FlextResult patterns.
    """

    @abstractmethod
    def format_data(
        self,
        data: object,
        format_type: str
    ) -> FlextResult[str]:
        """Format data to specified output format."""
        ...

    @abstractmethod
    def format_table(
        self,
        data: object,
        title: str | None = None
    ) -> FlextResult[object]:
        """Format data as a table representation."""
        ...

    @abstractmethod
    def format_json(
        self,
        data: object,
        indent: int = 2
    ) -> FlextResult[str]:
        """Format data as JSON string."""
        ...

    @abstractmethod
    def format_yaml(
        self,
        data: object
    ) -> FlextResult[str]:
        """Format data as YAML string."""
        ...

    @abstractmethod
    def format_csv(
        self,
        data: object
    ) -> FlextResult[str]:
        """Format data as CSV string."""
        ...


@runtime_checkable
class FlextCliOutputProtocol(Protocol):
    """Modern CLI output protocol for consistent terminal output.

    Defines the contract for CLI output operations including
    printing, styling, and interactive elements.
    """

    @abstractmethod
    def print_data(
        self,
        data: object,
        format_type: str = "table"
    ) -> FlextResult[None]:
        """Print data to terminal in specified format."""
        ...

    @abstractmethod
    def print_success(
        self,
        message: str
    ) -> FlextResult[None]:
        """Print success message with styling."""
        ...

    @abstractmethod
    def print_error(
        self,
        message: str
    ) -> FlextResult[None]:
        """Print error message with styling."""
        ...

    @abstractmethod
    def print_warning(
        self,
        message: str
    ) -> FlextResult[None]:
        """Print warning message with styling."""
        ...

    @abstractmethod
    def print_info(
        self,
        message: str
    ) -> FlextResult[None]:
        """Print info message with styling."""
        ...

    @abstractmethod
    def show_progress(
        self,
        description: str,
        total: int | None = None
    ) -> object:
        """Show progress indicator."""
        ...


@runtime_checkable
class FlextCliCommandProtocol(Protocol):
    """Modern CLI command protocol for command execution.

    Defines the contract for executing CLI commands with
    proper error handling and result management.
    """

    @abstractmethod
    def execute_command(
        self,
        command: str,
        args: list[str] | None = None,
        options: dict[str, object] | None = None
    ) -> FlextResult[str]:
        """Execute CLI command with arguments and options."""
        ...

    @abstractmethod
    def create_command(
        self,
        name: str,
        description: str,
        handler: object
    ) -> FlextResult[object]:
        """Create a new CLI command."""
        ...

    @abstractmethod
    def get_command_history(self) -> list[dict[str, object]]:
        """Get command execution history."""
        ...

    @abstractmethod
    def validate_command(
        self,
        command: str,
        args: list[str] | None = None
    ) -> FlextResult[bool]:
        """Validate command and arguments."""
        ...


@runtime_checkable
class FlextCliSessionProtocol(Protocol):
    """Modern CLI session protocol for session management.

    Defines the contract for managing CLI sessions including
    user authentication, configuration, and state persistence.
    """

    @abstractmethod
    def create_session(
        self,
        user_id: str,
        config: dict[str, object] | None = None
    ) -> FlextResult[str]:
        """Create new CLI session."""
        ...

    @abstractmethod
    def get_session(
        self,
        session_id: str
    ) -> FlextResult[dict[str, object]]:
        """Get session information."""
        ...

    @abstractmethod
    def update_session(
        self,
        session_id: str,
        updates: dict[str, object]
    ) -> FlextResult[None]:
        """Update session data."""
        ...

    @abstractmethod
    def end_session(
        self,
        session_id: str
    ) -> FlextResult[None]:
        """End CLI session."""
        ...

    @abstractmethod
    def is_session_active(
        self,
        session_id: str
    ) -> bool:
        """Check if session is active."""
        ...


@runtime_checkable
class FlextCliDataProcessorProtocol(Protocol):
    """Modern CLI data processing protocol for data operations.

    Defines the contract for data processing operations including
    transformation, aggregation, filtering, and export.
    """

    @abstractmethod
    def transform_data(
        self,
        data: object,
        filters: dict[str, object] | None = None
    ) -> FlextResult[list[object]]:
        """Transform data with optional filters."""
        ...

    @abstractmethod
    def aggregate_data(
        self,
        data: object,
        group_by: str,
        aggregations: dict[str, str] | None = None
    ) -> FlextResult[list[object]]:
        """Aggregate data by field with aggregation functions."""
        ...

    @abstractmethod
    def export_data(
        self,
        data: object,
        output_path: str,
        format_type: str = "json"
    ) -> FlextResult[str]:
        """Export data to file in specified format."""
        ...

    @abstractmethod
    def import_data(
        self,
        input_path: str,
        format_type: str | None = None
    ) -> FlextResult[object]:
        """Import data from file with auto format detection."""
        ...


@runtime_checkable
class FlextCliManagerProtocol(Protocol):
    """Modern CLI manager protocol for CLI orchestration.

    Defines the contract for high-level CLI management including
    configuration, plugin management, and system operations.
    """

    @abstractmethod
    def configure(
        self,
        config: dict[str, object]
    ) -> FlextResult[None]:
        """Configure CLI manager with settings."""
        ...

    @abstractmethod
    def get_configuration(self) -> dict[str, object]:
        """Get current CLI configuration."""
        ...

    @abstractmethod
    def health_check(self) -> dict[str, object]:
        """Perform CLI system health check."""
        ...

    @abstractmethod
    def get_formatter(self) -> FlextCliFormatterProtocol:
        """Get formatter instance."""
        ...

    @abstractmethod
    def get_output_handler(self) -> FlextCliOutputProtocol:
        """Get output handler instance."""
        ...

    @abstractmethod
    def get_command_executor(self) -> FlextCliCommandProtocol:
        """Get command executor instance."""
        ...

    @abstractmethod
    def get_data_processor(self) -> FlextCliDataProcessorProtocol:
        """Get data processor instance."""
        ...


# =============================================================================
# FACTORY FUNCTIONS - Modern CLI creation patterns
# =============================================================================

def create_flext_cli_formatter(
    default_format: str = "table"
) -> FlextResult[FlextCliFormatterProtocol]:
    """Factory function to create FlextCliFormatter implementation.

    Args:
        default_format: Default output format

    Returns:
        FlextResult containing configured CLI formatter

    """
    from typing import cast

    from flext_cli.formatter_adapter import FlextCliFormatterAdapter

    try:
        formatter = FlextCliFormatterAdapter(default_format=default_format)
        return FlextResult[FlextCliFormatterProtocol].ok(
            cast("FlextCliFormatterProtocol", formatter)
        )

    except Exception as e:
        return FlextResult[FlextCliFormatterProtocol].fail(f"Failed to create formatter: {e}")


def create_flext_cli_output_handler() -> FlextResult[FlextCliOutputProtocol]:
    """Factory function to create FlextCliOutput implementation.

    Returns:
        FlextResult containing configured CLI output handler

    """
    from typing import cast

    from flext_cli.output_adapter import FlextCliOutputAdapter

    try:
        output_handler = FlextCliOutputAdapter()
        return FlextResult[FlextCliOutputProtocol].ok(
            cast("FlextCliOutputProtocol", output_handler)
        )

    except Exception as e:
        return FlextResult[FlextCliOutputProtocol].fail(f"Failed to create output handler: {e}")


def create_flext_cli_manager(
    config: dict[str, object] | None = None
) -> FlextResult[FlextCliManagerProtocol]:
    """Factory function to create FlextCliManager implementation.

    Args:
        config: Optional CLI configuration

    Returns:
        FlextResult containing configured CLI manager

    """
    from typing import cast

    from flext_cli.api import FlextCliApi

    try:
        manager = FlextCliApi()
        if config:
            configure_result = manager.configure(config)
            if not configure_result.success:
                return FlextResult[FlextCliManagerProtocol].fail(
                    f"Failed to configure manager: {configure_result.error}"
                )

        return FlextResult[FlextCliManagerProtocol].ok(
            cast("FlextCliManagerProtocol", manager)
        )

    except Exception as e:
        return FlextResult[FlextCliManagerProtocol].fail(f"Failed to create manager: {e}")


def create_flext_cli_data_processor() -> FlextResult[FlextCliDataProcessorProtocol]:
    """Factory function to create FlextCliDataProcessor implementation.

    Returns:
        FlextResult containing configured CLI data processor

    """
    from typing import cast

    from flext_cli.helpers import FlextCliDataProcessor

    try:
        processor = FlextCliDataProcessor()
        return FlextResult[FlextCliDataProcessorProtocol].ok(
            cast("FlextCliDataProcessorProtocol", processor)
        )

    except Exception as e:
        return FlextResult[FlextCliDataProcessorProtocol].fail(f"Failed to create data processor: {e}")


# =============================================================================
# CONVENIENCE FUNCTIONS - Simplified CLI operations
# =============================================================================

def flext_cli_format_data(
    data: object,
    format_type: str = "table"
) -> FlextResult[str]:
    """Convenience function to format data using modern protocols.

    Args:
        data: Data to format
        format_type: Output format type

    Returns:
        FlextResult containing formatted data

    """
    formatter_result = create_flext_cli_formatter()
    if not formatter_result.success:
        return FlextResult[str].fail(f"Failed to create formatter: {formatter_result.error}")

    formatter = formatter_result.value
    return formatter.format_data(data, format_type)


def flext_cli_print_data(
    data: object,
    format_type: str = "table"
) -> FlextResult[None]:
    """Convenience function to print data using modern protocols.

    Args:
        data: Data to print
        format_type: Output format type

    Returns:
        FlextResult indicating success or failure

    """
    output_result = create_flext_cli_output_handler()
    if not output_result.success:
        return FlextResult[None].fail(f"Failed to create output handler: {output_result.error}")

    output_handler = output_result.value
    return output_handler.print_data(data, format_type)


def flext_cli_export_data(
    data: object,
    output_path: str,
    format_type: str = "json"
) -> FlextResult[str]:
    """Convenience function to export data using modern protocols.

    Args:
        data: Data to export
        output_path: Output file path
        format_type: Export format type

    Returns:
        FlextResult containing export path

    """
    processor_result = create_flext_cli_data_processor()
    if not processor_result.success:
        return FlextResult[str].fail(f"Failed to create data processor: {processor_result.error}")

    processor = processor_result.value
    return processor.export_data(data, output_path, format_type)


# =============================================================================
# EXPORTS
# =============================================================================

__all__ = [
    # Protocol definitions
    "FlextCliCommandProtocol",
    "FlextCliDataProcessorProtocol",
    "FlextCliFormatterProtocol",
    "FlextCliManagerProtocol",
    "FlextCliOutputProtocol",
    "FlextCliSessionProtocol",
    # Factory functions
    "create_flext_cli_data_processor",
    "create_flext_cli_formatter",
    "create_flext_cli_manager",
    "create_flext_cli_output_handler",
    # Convenience functions
    "flext_cli_export_data",
    "flext_cli_format_data",
    "flext_cli_print_data",
]

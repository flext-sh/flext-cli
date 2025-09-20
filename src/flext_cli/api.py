"""FLEXT CLI API - Unified single-class implementation.

Uses Python 3.13 cutting-edge patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_cli.unified_service import get_unified_cli_service
from flext_core import (
    FlextDomainService,
    FlextLogger,
    FlextResult,
    FlextTypes,
)


class FlextCliApi(FlextDomainService[FlextTypes.Core.Dict]):
    """Unified CLI API service - simplified through advanced flext-core patterns.

    This class now serves as a lightweight facade over the FlextCliUnifiedService,
    which uses advanced flext-core features for consolidation and complexity reduction.
    """

    def __init__(self) -> None:
        """Initialize FlextCliApi using unified service backend."""
        super().__init__()
        self._logger = FlextLogger(__name__)

        # Use the unified service from flext-core container

        self._unified_service = get_unified_cli_service()

    def execute(self, command: str = "", **kwargs: object) -> FlextResult[FlextTypes.Core.Dict | str]:
        """Execute CLI operation - delegates to unified service."""
        if command == "format":
            # Handle format command for test compatibility
            data = kwargs.get("data")
            format_type = str(kwargs.get("format_type", "table"))
            if data is not None:
                format_result = self._unified_service.format_data(data, format_type)
                if format_result.is_success:
                    return FlextResult[FlextTypes.Core.Dict | str].ok(format_result.unwrap())
                return FlextResult[FlextTypes.Core.Dict | str].fail(format_result.error or "Format failed")

        # Default execution
        result = self._unified_service.execute()
        if result.is_success:
            return FlextResult[FlextTypes.Core.Dict | str].ok(result.unwrap())
        return FlextResult[FlextTypes.Core.Dict | str].fail(result.error or "Execution failed")

    def format_output(
        self,
        data: object,
        format_type: str = "table",
        **options: object,
    ) -> FlextResult[str]:
        """Format data using unified service - reduced complexity."""
        return self._unified_service.format_data(data, format_type, **options)

    def display_output(self, formatted_data: str) -> FlextResult[None]:
        """Display formatted data using unified service."""
        return self._unified_service.display_output(formatted_data)

    def create_command(
        self,
        command_line: str,
        **options: object,
    ) -> FlextResult[dict[str, object]]:
        """Create CLI command using unified service."""
        return self._unified_service.create_command(command_line, **options)

    def get_health_status(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get API health status using unified service."""
        health_result = self._unified_service.get_health_status()
        if health_result.is_failure:
            return FlextResult[FlextTypes.Core.Dict].fail(
                health_result.error or "Health check failed"
            )

        return FlextResult[FlextTypes.Core.Dict].ok(health_result.unwrap())

    def export_data(
        self, data: object, file_path: object, format_type: str = "json"
    ) -> FlextResult[None]:
        """Export data using unified service."""
        if not isinstance(file_path, Path):
            return FlextResult[None].fail("file_path must be a Path object")

        return self._unified_service.export_data(data, file_path, format_type)

    def batch_export(
        self, datasets: object, output_dir: object, format_type: str = "json"
    ) -> FlextResult[None]:
        """Export multiple datasets using unified service."""
        if not isinstance(output_dir, Path):
            return FlextResult[None].fail("output_dir must be a Path object")

        if not isinstance(datasets, dict):
            return FlextResult[None].fail("datasets must be a dictionary")

        return self._unified_service.batch_export(datasets, output_dir, format_type)

    def format_and_display(
        self, data: object, format_type: str = "table", **options: object
    ) -> FlextResult[None]:
        """Format and display data in one operation using unified service."""
        return self._unified_service.format_and_display(data, format_type, **options)

    # Simplified convenience methods (much less code than before)
    def format_data(self, data: object, format_type: str) -> FlextResult[str]:
        """Format data - delegates to unified service."""
        return self._unified_service.format_data(data, format_type)

    def create_table(
        self, data: object, title: str | None = None, **options: object
    ) -> FlextResult[str]:
        """Create table - delegates to unified service."""
        table_options = options.copy()
        if title:
            table_options["title"] = title
        return self._unified_service.format_data(data, "table", **table_options)

    def get_command_history(self) -> FlextResult[list[dict[str, object]]]:
        """Get command history using unified service."""
        return self._unified_service.get_command_history()

    # Legacy compatibility methods (simplified)
    def execute_with_command(
        self, command: str | None = None, **kwargs: object
    ) -> FlextResult[object | str]:
        """Execute CLI operation with command - simplified through unified service."""
        if command is None:
            return FlextResult[object].ok({"status": "operational"})

        if command == "format":
            data = kwargs.get("data")
            format_type = kwargs.get("format_type", "json")
            if data is not None:
                format_result = self._unified_service.format_data(
                    data, str(format_type)
                )
                if format_result.is_failure:
                    return FlextResult[object | str].fail(
                        format_result.error or "Formatting failed"
                    )
                return FlextResult[object | str].ok(format_result.unwrap())
            return FlextResult[object].fail("No data provided for formatting")

        return FlextResult[object].ok({"status": "operational", "command": command})

    def execute_command(
        self, command: str = "status", **kwargs: object
    ) -> FlextResult[object | str]:
        """Execute CLI operation - delegates to execute_with_command."""
        return self.execute_with_command(command, **kwargs)

    # Utility methods
    def unwrap_or_default(self, result: FlextResult[object], default: object) -> object:
        """Unwrap FlextResult or return default value if failed."""
        return result.unwrap() if result.is_success else default

    def unwrap_or_none(self, result: FlextResult[object]) -> object | None:
        """Unwrap FlextResult or return None if failed."""
        return result.unwrap() if result.is_success else None


__all__ = [
    "FlextCliApi",
]

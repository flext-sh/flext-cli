"""FlextCli Protocols - Minimal essential protocols for flext-core integration.

Provides only essential protocol definitions used by actual implementations,
eliminating unused abstractions in favor of direct flext-core usage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import FlextResult

if TYPE_CHECKING:
    from flext_cli.api import FlextCliApi
    from flext_cli.data_processing import FlextCliDataProcessing
    from flext_cli.formatters import FlextCliFormatters

# =============================================================================
# FACTORY FUNCTIONS - Direct implementations using flext-core
# =============================================================================


def create_flext_cli_formatter(
    default_format: str = "table",
) -> FlextResult[FlextCliFormatters]:
    """Create CLI formatter using direct implementation.

    Args:
        default_format: Default output format

    Returns:
        FlextResult containing FlextCliFormatters instance

    """
    from flext_cli.formatters import FlextCliFormatters

    try:
        formatter = FlextCliFormatters(default_format=default_format)
        return FlextResult["FlextCliFormatters"].ok(formatter)
    except Exception as e:
        return FlextResult["FlextCliFormatters"].fail(
            f"Failed to create formatter: {e}"
        )


def create_flext_cli_data_processor() -> FlextResult[FlextCliDataProcessing]:
    """Create CLI data processor using direct implementation.

    Returns:
        FlextResult containing FlextCliDataProcessing instance

    """
    from flext_cli.data_processing import FlextCliDataProcessing

    try:
        processor = FlextCliDataProcessing()
        return FlextResult["FlextCliDataProcessing"].ok(processor)
    except Exception as e:
        return FlextResult["FlextCliDataProcessing"].fail(
            f"Failed to create data processor: {e}"
        )


def create_flext_cli_manager(
    config: dict[str, object] | None = None,
) -> FlextResult[FlextCliApi]:
    """Create CLI manager using direct implementation.

    Args:
        config: Optional CLI configuration

    Returns:
        FlextResult containing FlextCliApi instance

    """
    from flext_cli.api import FlextCliApi

    try:
        manager = FlextCliApi()
        if config:
            configure_result = manager.configure(config)
            if configure_result.is_failure:
                return FlextResult["FlextCliApi"].fail(
                    f"Failed to configure manager: {configure_result.error}"
                )
        return FlextResult["FlextCliApi"].ok(manager)
    except Exception as e:
        return FlextResult["FlextCliApi"].fail(f"Failed to create manager: {e}")


# =============================================================================
# CONVENIENCE FUNCTIONS - Direct operations using implementations
# =============================================================================


def flext_cli_format_data(data: object, format_type: str = "table") -> FlextResult[str]:
    """Format data using FlextCliFormatters directly.

    Args:
        data: Data to format
        format_type: Output format type

    Returns:
        FlextResult containing formatted data

    """
    formatter_result = create_flext_cli_formatter()
    if formatter_result.is_failure:
        return FlextResult[str].fail(
            f"Failed to create formatter: {formatter_result.error}"
        )

    formatter = formatter_result.value
    return formatter.format_data(data, format_type)


def flext_cli_export_data(
    data: object, output_path: str, format_type: str = "json"
) -> FlextResult[str]:
    """Export data using FlextCliDataProcessing directly.

    Args:
        data: Data to export
        output_path: Output file path
        format_type: Export format type

    Returns:
        FlextResult containing export path

    """
    try:
        # Use formatters to convert data to string format first
        formatter_result = flext_cli_format_data(data, format_type)
        if formatter_result.is_failure:
            return FlextResult[str].fail(f"Format failed: {formatter_result.error}")

        # Write formatted data to file
        from pathlib import Path

        output_file = Path(output_path)
        output_file.write_text(formatter_result.value, encoding="utf-8")

        return FlextResult[str].ok(str(output_file))
    except Exception as e:
        return FlextResult[str].fail(f"Export failed: {e}")


# =============================================================================
# EXPORTS - Minimal essential functions only
# =============================================================================

__all__ = [
    "create_flext_cli_data_processor",
    "create_flext_cli_formatter",
    "create_flext_cli_manager",
    "flext_cli_export_data",
    "flext_cli_format_data",
]

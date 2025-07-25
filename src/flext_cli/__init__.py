"""FLEXT CLI - Enterprise Command Line Interface Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Version 0.8.0 - Pure library with massive code reduction:
- Zero-boilerplate CLI creation using flext-core patterns
- All access through root namespace only
- FlextCli/flext_cli_ prefixed public API
- No duplications with flext-core or internal
"""

from __future__ import annotations

import datetime
import importlib.metadata
import warnings
from typing import Any

# Import flext-core foundation (no duplication)
from flext_core import (
    FlextCoreSettings,
    FlextEntity,
    FlextField,
    FlextResult,
    FlextValueObject,
    get_logger,
)

# Import centralized helpers to eliminate duplication
from flext_cli.core._helpers import (
    flext_cli_fail as _fail,
    flext_cli_success as _success,
)

# Core library classes
from flext_cli.core.builder import FlextCliBuilder
from flext_cli.core.data_exporter import ExportChain, FlextCliDataExporter
from flext_cli.core.formatter import FlextCliFormatter
from flext_cli.core.input import FlextCliInput
from flext_cli.core.rich_gui import FlextCliRichGUI
from flext_cli.core.validator import FlextCliValidator

# Advanced decorators
from flext_cli.decorators import (
    flext_cli_auto_export,
    flext_cli_cache_result,
    flext_cli_data_validator,
    flext_cli_pipeline_step,
    flext_cli_quick_cache,
    flext_cli_quick_retry,
    flext_cli_quick_timing,
    flext_cli_result_wrapper,
    flext_cli_retry,
    flext_cli_timing,
)

# Boilerplate reduction helpers
from flext_cli.helpers import (
    FlextCliBuilder as FlextCliFluentBuilder,  # Alias to avoid conflict
    FlextCliDataMixin,
    FlextCliDict,
    FlextCliList,
    FlextCliMixin,
    flext_cli_batch_process,
    flext_cli_chain,
    flext_cli_pipeline_simple,
    flext_cli_quick_builder,
    flext_cli_quick_dict,
    flext_cli_quick_list,
    flext_cli_safe_call,
)

try:
    __version__ = importlib.metadata.version("flext-cli")
except importlib.metadata.PackageNotFoundError:
    __version__ = "0.8.0"

__version_info__ = tuple(int(x) for x in __version__.split(".") if x.isdigit())

logger = get_logger(__name__)

# ============================================================================
# POWERFUL UTILITY FUNCTIONS - MASSIVE CODE REDUCTION
# ============================================================================


def flext_cli_create_builder(name: str = "cli", **kwargs: object) -> FlextCliBuilder:
    """Create CLI builder with zero boilerplate.

    Example:
        cli = flext_cli_create_builder("myapp")
        cli.add_command("hello", lambda: "Hello World!")
        cli.run()

    """
    return FlextCliBuilder(name=name, **kwargs)


def flext_cli_quick_commands(
    commands: dict[str, callable], **kwargs: object,
) -> FlextResult[None]:
    """Ultra-fast CLI from command dictionary.

    Example:
        flext_cli_quick_commands({
            "hello": lambda: print("Hello!"),
            "version": lambda: print("v1.0.0")
        })

    """
    try:
        builder = FlextCliBuilder(**kwargs)
        for name, func in commands.items():
            builder.add_command(name, func)
        builder.run()
        return _success(None)
    except Exception as e:
        logger.exception("Quick CLI execution failed")
        return _fail(f"Quick CLI failed: {e}")


def flext_cli_validate_inputs(**validations: object) -> FlextCliValidator:
    """Create input validator with patterns.

    Example:
        validator = flext_cli_validate_inputs(
            email="email",
            port=lambda x: 1 <= int(x) <= 65535
        )

    """
    return FlextCliValidator(validations)


def flext_cli_format_output(data: object, style: str = "rich") -> FlextResult[str]:
    """Format data with specified style.

    Styles: 'rich', 'json', 'yaml', 'table'

    Example:
        result = flext_cli_format_output({"name": "Alice"}, "json")
        if result.success:
            print(result.data)

    """
    try:
        formatter = FlextCliFormatter(style)
        return _success(formatter.format(data))
    except Exception as e:
        logger.exception("Output formatting failed")
        return _fail(f"Formatting failed: {e}")


def flext_cli_collect_input(schema: dict[str, Any]) -> FlextResult[dict[str, Any]]:
    """Collect user input based on schema.

    Example:
        result = flext_cli_collect_input({
            "name": {"prompt": "Your name", "required": True},
            "email": {"prompt": "Email", "validator": "email"}
        })

    """
    try:
        input_collector = FlextCliInput()
        return _success(input_collector.collect_dict(schema))
    except Exception as e:
        logger.exception("Input collection failed")
        return _fail(f"Input collection failed: {e}")


def flext_cli_export_data(
    data: list[dict[str, Any]] | dict[str, Any],
    filepath: str,
    format_type: str | None = None,
    **options: object,
) -> FlextResult[str]:
    """Export data to multiple formats with zero boilerplate.

    Example:
        result = flext_cli_export_data(
            data=[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}],
            filepath="users.csv"
        )

    """
    try:
        exporter = FlextCliDataExporter()
        return exporter.export_data(data, filepath, format_type, **options)
    except Exception as e:
        logger.exception("Data export failed")
        return _fail(f"Export failed: {e}")


def flext_cli_create_dashboard(
    title: str = "FlextCli Dashboard",
    layout_config: dict[str, Any] | None = None,
) -> FlextResult[Any]:
    """Create Rich GUI dashboard with zero boilerplate.

    Example:
        result = flext_cli_create_dashboard("My App Dashboard")
        if result.success:
            dashboard = result.unwrap()

    """
    try:
        gui = FlextCliRichGUI()
        return gui.create_dashboard(title, layout_config)
    except Exception as e:
        logger.exception("Dashboard creation failed")
        return _fail(f"Dashboard creation failed: {e}")


def flext_cli_format_tabulate(
    data: list[dict[str, Any]],
    title: str | None = None,
    tablefmt: str = "grid",
    **options: object,
) -> FlextResult[str]:
    """Format data with Tabulate for advanced table styling.

    Example:
        result = flext_cli_format_tabulate(
            data=[{"name": "Alice", "age": 30}],
            tablefmt="fancy_grid"
        )

    """
    try:
        formatter = FlextCliFormatter()
        return formatter.format_tabulate_table(data, title, tablefmt, **options)
    except Exception as e:
        logger.exception("Tabulate formatting failed")
        return _fail(f"Tabulate formatting failed: {e}")


def flext_cli_analyze_data(
    data: list[dict[str, Any]],
    title: str = "Data Analysis",
) -> FlextResult[str]:
    """Generate comprehensive data analysis summary.

    Example:
        result = flext_cli_analyze_data(dataset)
        if result.success:
            print(result.unwrap())

    """
    try:
        formatter = FlextCliFormatter()
        return formatter.format_data_summary(data, title)
    except Exception as e:
        logger.exception("Data analysis failed")
        return _fail(f"Data analysis failed: {e}")


def flext_cli_pipeline(
    data: object,
    export_path: str | None = None,
    formats: list[str] | None = None,
    *,
    dashboard: bool = False,
    analysis: bool = False,
) -> FlextResult[dict[str, Any]]:
    """Execute complete data pipeline with massive code reduction.

    Single function call for: format → export → analyze → dashboard

    Example:
        result = flext_cli_pipeline(
            data=users_data,
            export_path="./output/users",
            formats=["csv", "json"],
            dashboard=True,
            analysis=True
        )

    Returns:
        {
            "formatted": "...",  # Formatted output
            "exported": {...},   # Export results
            "analysis": "...",   # Data analysis
            "dashboard": Layout  # Rich dashboard
        }

    """
    try:
        results = {}

        # Format data
        formatter = FlextCliFormatter()
        format_result = formatter.format(data)
        results["formatted"] = format_result

        # Export data if requested
        if export_path and formats:
            exporter = FlextCliDataExporter()
            export_result = exporter.export_multiple_formats(data, export_path, formats)
            results["exported"] = export_result.data if export_result.success else None

        # Generate analysis if requested
        if analysis and isinstance(data, list):
            analysis_result = formatter.format_data_summary(data)
            results["analysis"] = (
                analysis_result.data if analysis_result.success else None
            )

        # Create dashboard if requested
        if dashboard:
            gui = FlextCliRichGUI()
            dashboard_result = gui.create_dashboard("FlextCli Pipeline")
            results["dashboard"] = (
                dashboard_result.data if dashboard_result.success else None
            )

        return _success(results)

    except Exception as e:
        logger.exception("Pipeline execution failed")
        return _fail(f"Pipeline failed: {e}")


def flext_cli_instant_export(
    data: object,
    format_type: str = "csv",
    filename: str | None = None,
) -> FlextResult[str]:
    """Ultra-fast data export with zero configuration.

    Example:
        # Auto-generates filename with timestamp
        result = flext_cli_instant_export(users, "json")
        print(f"Exported to: {result.unwrap()}")

    """
    try:
        if filename is None:
            timestamp = datetime.datetime.now(tz=datetime.UTC).strftime("%Y%m%d_%H%M%S")
            filename = f"flext_export_{timestamp}.{format_type}"

        exporter = FlextCliDataExporter()
        result = exporter.export_data(data, filename, format_type)

        if result.success:
            return _success(filename)
        return result

    except Exception as e:
        logger.exception("Instant export failed")
        return _fail(f"Instant export failed: {e}")


def flext_cli_data_compare(
    before_data: list[dict[str, Any]],
    after_data: list[dict[str, Any]],
    title: str = "Data Comparison",
) -> FlextResult[str]:
    """Compare two datasets and generate diff report.

    Example:
        result = flext_cli_data_compare(old_users, new_users)
        print(result.unwrap())

    """
    try:
        formatter = FlextCliFormatter()
        return formatter.format_comparison_table(before_data, after_data, title)
    except Exception as e:
        logger.exception("Data comparison failed")
        return _fail(f"Data comparison failed: {e}")


def flext_cli_auto_dashboard(
    data: list[dict[str, Any]],
    title: str | None = None,
    metrics: dict[str, Any] | None = None,
) -> FlextResult[Any]:
    """Auto-generate dashboard from data with zero configuration.

    Example:
        result = flext_cli_auto_dashboard(sales_data)
        if result.success:
            dashboard = result.unwrap()

    """
    try:
        gui = FlextCliRichGUI()

        if title is None:
            title = f"Auto Dashboard - {len(data)} records"

        # Create dashboard with data table
        dashboard_result = gui.create_dashboard(title)
        if not dashboard_result.success:
            return dashboard_result

        dashboard = dashboard_result.data

        # Add data table
        table_result = gui.create_data_table(data, "Data Overview")
        if table_result.success:
            # Update dashboard with table content
            gui.update_dashboard_content(dashboard, {
                "body": table_result.data,
                "metrics": metrics or {},
            })

        return _success(dashboard)

    except Exception as e:
        logger.exception("Auto dashboard creation failed")
        return _fail(f"Auto dashboard failed: {e}")


def flext_cli_format_all(
    data: object,
    styles: list[str] | None = None,
) -> FlextResult[dict[str, str]]:
    """Format data in multiple styles simultaneously.

    Example:
        result = flext_cli_format_all(data, ["json", "yaml", "table"])
        outputs = result.unwrap()
        for style, output in outputs.items():
            print(f"=== {style.upper()} ===")
            print(output)

    """
    try:
        if styles is None:
            styles = ["json", "yaml", "table", "rich"]

        formatter = FlextCliFormatter()
        results = {}

        for style in styles:
            formatter.style = style
            output = formatter.format(data)
            results[style] = output

        return _success(results)

    except Exception as e:
        logger.exception("Multi-format formatting failed")
        return _fail(f"Multi-format formatting failed: {e}")


# ============================================================================
# BACKWARD COMPATIBILITY WITH WARNINGS
# ============================================================================


def _deprecated_warning(old_name: str, new_name: str) -> None:
    """Show deprecation warning."""
    warnings.warn(
        f"{old_name} is deprecated. Use {new_name} instead.",
        DeprecationWarning,
        stacklevel=3,
    )


# Legacy aliases with warnings
def create_cli(*args: Any, **kwargs: object) -> FlextCliBuilder:
    """DEPRECATED: Use flext_cli_create_builder instead."""
    _deprecated_warning("create_cli", "flext_cli_create_builder")
    return flext_cli_create_builder(*args, **kwargs)


def quick_cli(*args: Any, **kwargs: object) -> FlextResult[None]:
    """DEPRECATED: Use flext_cli_quick_commands instead."""
    _deprecated_warning("quick_cli", "flext_cli_quick_commands")
    return flext_cli_quick_commands(*args, **kwargs)


# ============================================================================
# PUBLIC API EXPORTS - ROOT NAMESPACE ONLY
# ============================================================================

__all__ = [
    "ExportChain",  # Chainable export operations
    # ========== CORE LIBRARY CLASSES ==========
    "FlextCliBuilder",  # Main CLI builder
    "FlextCliDataExporter",  # Advanced data export (CSV, Parquet, SQLite, etc.)
    "FlextCliDataMixin",  # Mixin for data operations
    "FlextCliDict",  # Enhanced dict with FlextResult operations
    # ========== BOILERPLATE REDUCTION HELPERS ==========
    "FlextCliFluentBuilder",  # Fluent builder for complex operations
    "FlextCliFormatter",  # Output formatting with Tabulate integration
    "FlextCliInput",  # Input collection
    "FlextCliList",  # Enhanced list with FlextResult operations
    "FlextCliMixin",  # Base mixin for FlextResult patterns
    "FlextCliRichGUI",  # Advanced Rich GUI interfaces
    "FlextCliValidator",  # Input validation
    "FlextCoreSettings",
    # ========== FLEXT-CORE FOUNDATION ==========
    "FlextEntity",
    "FlextField",
    "FlextResult",
    "FlextValueObject",
    # ========== METADATA ==========
    "__version__",
    "__version_info__",
    # ========== DEPRECATED (WITH WARNINGS) ==========
    "create_cli",  # Use flext_cli_create_builder
    # ========== UTILITY FUNCTIONS ==========
    "flext_cli_analyze_data",  # Data analysis and statistics
    "flext_cli_auto_dashboard",  # Auto-generate dashboard from data
    "flext_cli_auto_export",  # Automatic result export
    # ========== BATCH PROCESSING ==========
    "flext_cli_batch_process",  # Batch processing with error handling
    "flext_cli_cache_result",  # Result caching with TTL
    "flext_cli_chain",  # Chain FlextResult operations
    "flext_cli_collect_input",  # User input collection
    "flext_cli_create_builder",  # Create CLI with zero boilerplate
    "flext_cli_create_dashboard",  # Rich GUI dashboard creation
    "flext_cli_data_compare",  # Compare datasets and generate diff
    "flext_cli_data_validator",  # Data structure validation
    "flext_cli_export_data",  # Multi-format data export
    "flext_cli_format_all",  # Format data in multiple styles
    "flext_cli_format_output",  # Data formatting
    "flext_cli_format_tabulate",  # Advanced table formatting
    "flext_cli_instant_export",  # Ultra-fast export with auto-naming
    "flext_cli_pipeline",  # Complete data pipeline execution
    "flext_cli_pipeline_simple",  # Simple pipeline processing
    "flext_cli_pipeline_step",  # Pipeline step marking
    "flext_cli_quick_builder",  # Create fluent builder
    "flext_cli_quick_cache",  # Quick cache with defaults
    "flext_cli_quick_commands",  # Ultra-fast CLI from dict
    # ========== QUICK HELPERS ==========
    "flext_cli_quick_dict",  # Create enhanced dict
    "flext_cli_quick_list",  # Create enhanced list
    "flext_cli_quick_retry",  # Quick retry with defaults
    "flext_cli_quick_timing",  # Quick timing decorator
    # ========== ADVANCED DECORATORS ==========
    "flext_cli_result_wrapper",  # Auto-wrap results in FlextResult
    "flext_cli_retry",  # Retry with exponential backoff
    "flext_cli_safe_call",  # Safe function calls with FlextResult
    "flext_cli_timing",  # Execution timing
    "flext_cli_validate_inputs",  # Input validation patterns
]

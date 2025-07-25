"""FlextCliFormatter - Output formatting using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Consolidated formatting eliminating duplications with flext-core and external libs.
"""

from __future__ import annotations

import json
from typing import Any

import yaml
from flext_core import FlextResult, get_logger


# Helper functions for cleaner FlextResult creation
def _success(data: Any = None) -> FlextResult[Any]:
    return FlextResult(success=True, data=data, error=None)

def _fail(error: str) -> FlextResult[Any]:
    return FlextResult(success=False, data=None, error=error)
from rich.console import Console
from rich.pretty import Pretty
from rich.syntax import Syntax
from rich.table import Table

logger = get_logger(__name__)


class FlextCliFormatter:
    """Output formatter with multiple styles built on flext-core patterns.

    Eliminates all duplications - uses flext-core FlextResult for error handling.
    """

    def __init__(self, style: str = "rich") -> None:
        self.style = style
        self.console = Console()

    def format(self, data: Any, title: str | None = None) -> str:
        """Format data with configured style - returns string."""
        try:
            if self.style == "rich":
                return self._format_rich(data, title)
            if self.style == "json":
                return self._format_json(data, title)
            if self.style == "yaml":
                return self._format_yaml(data, title)
            if self.style == "table":
                return self._format_table(data, title)
            return self._format_simple(data, title)
        except Exception as e:
            logger.exception("Formatting failed")
            return f"Formatting error: {e}"

    def output(self, data: Any, title: str | None = None) -> None:
        """Output formatted data to console."""
        formatted = self.format(data, title)
        self.console.print(formatted)

    def success(self, message: Any, title: str | None = None) -> None:
        """Output success message."""
        if title:
            self.console.print(f"[bold green]✓ {title}[/bold green]")
        self.console.print(f"[green]{message}[/green]")

    def error(self, message: Any, title: str | None = None) -> None:
        """Output error message."""
        if title:
            self.console.print(f"[bold red]✗ {title}[/bold red]")
        self.console.print(f"[red]{message}[/red]")

    def warning(self, message: Any, title: str | None = None) -> None:
        """Output warning message."""
        if title:
            self.console.print(f"[bold yellow]⚠ {title}[/bold yellow]")
        self.console.print(f"[yellow]{message}[/yellow]")

    def info(self, message: Any, title: str | None = None) -> None:
        """Output info message."""
        if title:
            self.console.print(f"[bold blue]ℹ {title}[/bold blue]")
        self.console.print(f"[blue]{message}[/blue]")

    def table(self, data: list[dict[str, Any]], title: str | None = None) -> None:
        """Output data as Rich table."""
        if not data:
            return

        table = Table(title=title, show_header=True, header_style="bold cyan")

        # Use dict keys as headers
        headers = list(data[0].keys())
        for header in headers:
            table.add_column(header)

        # Add rows
        for row in data:
            table.add_row(*[str(row.get(h, "")) for h in headers])

        self.console.print(table)

    def code(self, code: str, language: str = "python", title: str | None = None) -> None:
        """Output syntax-highlighted code."""
        syntax = Syntax(code, language, theme="monokai", line_numbers=True)
        if title:
            self.console.print(f"[bold]{title}[/bold]")
        self.console.print(syntax)

    def _format_rich(self, data: Any, title: str | None = None) -> str:
        """Format with Rich styling."""
        if isinstance(data, (dict, list)):
            pretty = Pretty(data)
            with self.console.capture() as capture:
                if title:
                    self.console.print(f"[bold]{title}[/bold]")
                self.console.print(pretty)
            return capture.get()
        return f"{title}: {data}" if title else str(data)

    def _format_json(self, data: Any, title: str | None = None) -> str:
        """Format as JSON."""
        try:
            if isinstance(data, str):
                content = data
            else:
                content = json.dumps(data, indent=2, default=str)

            if title:
                return f"# {title}\n{content}"
            return content
        except (TypeError, ValueError):
            return str(data)

    def _format_yaml(self, data: Any, title: str | None = None) -> str:
        """Format as YAML."""
        try:
            if isinstance(data, str):
                content = data
            else:
                content = yaml.dump(data, default_flow_style=False)

            if title:
                return f"# {title}\n{content}"
            return content
        except yaml.YAMLError:
            return str(data)

    def _format_table(self, data: Any, title: str | None = None) -> str:
        """Format as ASCII table."""
        if isinstance(data, list) and data and isinstance(data[0], dict):
            headers = list(data[0].keys())

            # Calculate column widths
            col_widths = {}
            for col in headers:
                max_width = max(len(str(row.get(col, ""))) for row in data)
                col_widths[col] = max(len(col), max_width)

            # Build table
            lines = []

            if title:
                lines.append(title)
                lines.append("=" * len(title))

            # Header
            header = " | ".join(col.ljust(col_widths[col]) for col in headers)
            lines.append(header)
            lines.append("-" * len(header))

            # Rows
            for row in data:
                row_line = " | ".join(
                    str(row.get(col, "")).ljust(col_widths[col]) for col in headers
                )
                lines.append(row_line)

            return "\n".join(lines)
        if isinstance(data, dict):
            # Convert dict to table format
            table_data = [{"Key": k, "Value": v} for k, v in data.items()]
            return self._format_table(table_data, title)
        return self._format_simple(data, title)

    def _format_simple(self, data: Any, title: str | None = None) -> str:
        """Format as simple text."""
        if title:
            return f"{title}: {data}"
        return str(data)

    def get_available_styles(self) -> list[str]:
        """Get available formatting styles."""
        return ["rich", "json", "yaml", "table", "simple"]

    @classmethod
    def create_json_formatter(cls) -> FlextCliFormatter:
        """Create JSON-specific formatter."""
        return cls(style="json")

    @classmethod
    def create_table_formatter(cls) -> FlextCliFormatter:
        """Create table-specific formatter."""
        return cls(style="table")

    @classmethod
    def create_rich_formatter(cls) -> FlextCliFormatter:
        """Create Rich-specific formatter."""
        return cls(style="rich")

    @classmethod
    def create_tabulate_formatter(cls) -> FlextCliFormatter:
        """Create Tabulate-optimized formatter."""
        return cls(style="table")

    @classmethod
    def create_export_formatter(cls) -> FlextCliFormatter:
        """Create formatter optimized for data export previews."""
        return cls(style="json")

    def format_progress(self, items: list[Any], title: str = "Processing") -> None:
        """Format progress indication for long operations."""
        from rich.progress import Progress, TaskID

        with Progress(console=self.console) as progress:
            task: TaskID = progress.add_task(title, total=len(items))
            for item in items:
                # This would be used in actual processing
                progress.update(task, advance=1)
                yield item

    def format_tree(self, data: dict[str, Any], title: str = "Tree Structure") -> str:
        """Format hierarchical data as a tree."""
        from rich.tree import Tree

        tree = Tree(title)
        self._add_tree_nodes(tree, data)

        with self.console.capture() as capture:
            self.console.print(tree)
        return capture.get()

    def _add_tree_nodes(self, parent: Any, data: dict[str, Any] | list[Any] | Any) -> None:
        """Recursively add nodes to tree."""
        if isinstance(data, dict):
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    branch = parent.add(str(key))
                    self._add_tree_nodes(branch, value)
                else:
                    parent.add(f"{key}: {value}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    branch = parent.add(f"[{i}]")
                    self._add_tree_nodes(branch, item)
                else:
                    parent.add(f"[{i}]: {item}")

    def format_panel(self, content: str, title: str = "", style: str = "blue") -> str:
        """Format content in a styled panel."""
        from rich.panel import Panel

        panel = Panel(content, title=title, border_style=style)
        with self.console.capture() as capture:
            self.console.print(panel)
        return capture.get()

    def format_columns(self, data: list[str], columns: int = 3) -> str:
        """Format list of items in columns."""
        from rich.columns import Columns

        columns_obj = Columns(data, equal=True, expand=True)
        with self.console.capture() as capture:
            self.console.print(columns_obj)
        return capture.get()

    def format_status_table(self, statuses: dict[str, bool], title: str = "Status") -> None:
        """Format status information as a colored table."""
        table = Table(title=title, show_header=True, header_style="bold cyan")
        table.add_column("Item", style="white")
        table.add_column("Status", justify="center")

        for item, status in statuses.items():
            status_text = "[green]✓ PASS[/green]" if status else "[red]✗ FAIL[/red]"
            table.add_row(item, status_text)

        self.console.print(table)

    def format_tabulate_table(
        self,
        data: list[dict[str, Any]],
        title: str | None = None,
        tablefmt: str = "grid",
        headers: str = "keys",
        **options: Any,
    ) -> FlextResult[str]:
        """Format data using tabulate library for advanced table formatting.

        Args:
            data: List of dictionaries to format
            title: Optional table title
            tablefmt: Table format (grid, fancy_grid, pipe, orgtbl, etc.)
            headers: Header mode (keys, firstrow, etc.)
            **options: Additional tabulate options

        Returns:
            FlextResult with formatted table string

        """
        try:
            import tabulate

            if not data:
                return _fail("No data to format as table")

            # Format table using tabulate
            table_str = tabulate.tabulate(
                data,
                headers=headers,
                tablefmt=tablefmt,
                **options,
            )

            # Add title if provided
            if title:
                title_line = f"\n{title}\n{'-' * len(title)}\n"
                table_str = title_line + table_str

            return _success(table_str)

        except ImportError:
            return _fail("tabulate library required for advanced table formatting")
        except Exception as e:
            logger.exception("Tabulate formatting failed")
            return _fail(f"Tabulate formatting failed: {e}")

    def format_data_summary(
        self,
        data: list[dict[str, Any]],
        title: str = "Data Summary",
    ) -> FlextResult[str]:
        """Generate comprehensive data summary with statistics.

        Args:
            data: List of dictionaries to analyze
            title: Summary title

        Returns:
            FlextResult with formatted data summary

        """
        try:
            if not data:
                return _fail("No data to summarize")

            # Basic statistics
            total_records = len(data)
            columns = list(data[0].keys()) if data else []

            # Column analysis
            column_stats = {}
            for col in columns:
                values = [row.get(col) for row in data if row.get(col) is not None]
                non_null_count = len(values)
                null_count = total_records - non_null_count

                # Data type analysis
                types = {type(v).__name__ for v in values}

                # Numeric statistics if applicable
                numeric_stats = {}
                if values and all(isinstance(v, (int, float)) for v in values):
                    numeric_stats = {
                        "min": min(values),
                        "max": max(values),
                        "mean": sum(values) / len(values) if values else 0,
                    }

                column_stats[col] = {
                    "non_null": non_null_count,
                    "null": null_count,
                    "types": list(types),
                    **numeric_stats,
                }

            # Format summary
            summary_lines = [
                f"\n{title}",
                "=" * len(title),
                f"Total Records: {total_records:,}",
                f"Columns: {len(columns)}",
                "",
                "Column Details:",
                "-" * 50,
            ]

            for col, stats in column_stats.items():
                summary_lines.append(f"{col}:")
                summary_lines.append(f"  Non-null: {stats['non_null']:,}")
                summary_lines.append(f"  Null: {stats['null']:,}")
                summary_lines.append(f"  Types: {', '.join(stats['types'])}")

                if "min" in stats:
                    summary_lines.append(f"  Min: {stats['min']}")
                    summary_lines.append(f"  Max: {stats['max']}")
                    summary_lines.append(f"  Mean: {stats['mean']:.2f}")

                summary_lines.append("")

            return _success("\n".join(summary_lines))

        except Exception as e:
            logger.exception("Data summary failed")
            return _fail(f"Data summary failed: {e}")

    def format_export_preview(
        self,
        data: list[dict[str, Any]],
        export_format: str,
        sample_size: int = 3,
    ) -> FlextResult[str]:
        """Show preview of how data will look when exported.

        Args:
            data: Data to preview
            export_format: Target export format
            sample_size: Number of records to show in preview

        Returns:
            FlextResult with export preview

        """
        try:
            if not data:
                return _fail("No data to preview")

            # Get sample data
            sample_data = data[:sample_size]

            if export_format.lower() == "csv":
                import csv
                import io

                output = io.StringIO()
                fieldnames = list(sample_data[0].keys())
                writer = csv.DictWriter(output, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(sample_data)
                preview = output.getvalue()

            elif export_format.lower() == "json":
                preview = json.dumps(sample_data, indent=2, default=str)

            elif export_format.lower() == "yaml":
                preview = yaml.dump(sample_data, default_flow_style=False)

            elif export_format.lower() in ("table", "tabulate"):
                tabulate_result = self.format_tabulate_table(sample_data)
                if not tabulate_result.success:
                    return tabulate_result
                preview = tabulate_result.unwrap()

            else:
                # Fallback to JSON
                preview = json.dumps(sample_data, indent=2, default=str)

            # Add header and footer
            preview_with_header = (
                f"\n{export_format.upper()} Export Preview ({sample_size} records)\n"
                f"{'-' * 50}\n"
                f"{preview}\n"
                f"{'-' * 50}\n"
                f"Total records to export: {len(data):,}\n"
            )

            return _success(preview_with_header)

        except Exception as e:
            logger.exception("Export preview failed")
            return _fail(f"Export preview failed: {e}")

    def format_comparison_table(
        self,
        before_data: list[dict[str, Any]],
        after_data: list[dict[str, Any]],
        title: str = "Data Comparison",
        key_field: str = "id",
    ) -> FlextResult[str]:
        """Create side-by-side comparison of two datasets.

        Args:
            before_data: Original data
            after_data: Modified data
            title: Comparison title
            key_field: Field to use for matching records

        Returns:
            FlextResult with comparison table

        """
        try:
            # Create lookup dictionaries
            before_dict = {str(row.get(key_field, i)): row for i, row in enumerate(before_data)}
            after_dict = {str(row.get(key_field, i)): row for i, row in enumerate(after_data)}

            # Find changes
            all_keys = set(before_dict.keys()) | set(after_dict.keys())
            changes = []

            for key in sorted(all_keys):
                before_row = before_dict.get(key, {})
                after_row = after_dict.get(key, {})

                if key not in before_dict:
                    changes.append({"Key": key, "Status": "ADDED", "Changes": "New record"})
                elif key not in after_dict:
                    changes.append({"Key": key, "Status": "REMOVED", "Changes": "Record deleted"})
                else:
                    # Check for changes in values
                    field_changes = []
                    all_fields = set(before_row.keys()) | set(after_row.keys())

                    for field in all_fields:
                        before_val = before_row.get(field)
                        after_val = after_row.get(field)

                        if before_val != after_val:
                            field_changes.append(f"{field}: {before_val} → {after_val}")

                    if field_changes:
                        changes.append({
                            "Key": key,
                            "Status": "MODIFIED",
                            "Changes": "; ".join(field_changes[:3]),  # Limit to first 3 changes
                        })

            if not changes:
                return _success(f"\n{title}\nNo changes detected.\n")

            # Format as table
            return self.format_tabulate_table(changes, title=title)

        except Exception as e:
            logger.exception("Comparison table failed")
            return _fail(f"Comparison table failed: {e}")

    def get_available_tabulate_formats(self) -> list[str]:
        """Get list of available tabulate table formats."""
        try:
            import tabulate
            return list(tabulate.tabulate_formats)
        except ImportError:
            return ["tabulate library not available"]

    def format_with_data_export_integration(
        self,
        data: list[dict[str, Any]],
        display_format: str = "rich",
        export_options: dict[str, Any] | None = None,
    ) -> FlextResult[dict[str, Any]]:
        """Format data with integrated export capabilities.

        Args:
            data: Data to format and prepare for export
            display_format: How to display the data
            export_options: Options for potential data export

        Returns:
            FlextResult with formatted display and export metadata

        """
        try:
            # Format for display
            display_result = self.format(data, title="Data Display")

            # Generate export metadata
            export_metadata = {
                "record_count": len(data),
                "columns": list(data[0].keys()) if data else [],
                "data_types": self._analyze_data_types(data),
                "recommended_formats": self._recommend_export_formats(data),
                "estimated_sizes": self._estimate_export_sizes(data),
            }

            result = {
                "display": display_result,
                "export_metadata": export_metadata,
                "data_ready_for_export": True,
            }

            return _success(result)

        except Exception as e:
            logger.exception("Integrated formatting failed")
            return _fail(f"Integrated formatting failed: {e}")

    def _analyze_data_types(self, data: list[dict[str, Any]]) -> dict[str, list[str]]:
        """Analyze data types in dataset."""
        if not data:
            return {}

        type_analysis = {}
        for col in data[0]:
            types = {type(row.get(col)).__name__ for row in data if row.get(col) is not None}
            type_analysis[col] = list(types)

        return type_analysis

    def _recommend_export_formats(self, data: list[dict[str, Any]]) -> list[str]:
        """Recommend best export formats based on data characteristics."""
        if not data:
            return []

        recommendations = []

        # Always recommend JSON for flexibility
        recommendations.append("json")

        # Check if data is flat (good for CSV)
        is_flat = all(
            all(not isinstance(v, (dict, list)) for v in row.values())
            for row in data
        )

        if is_flat:
            recommendations.extend(["csv", "tsv", "excel"])

        # Recommend Parquet for large datasets
        if len(data) > 1000:
            recommendations.append("parquet")

        # Recommend SQLite for structured data
        if len(data) > 100:
            recommendations.append("sqlite")

        return recommendations

    def _estimate_export_sizes(self, data: list[dict[str, Any]]) -> dict[str, str]:
        """Estimate file sizes for different export formats."""
        if not data:
            return {}

        # Rough size estimation based on JSON size
        json_str = json.dumps(data, default=str)
        json_size = len(json_str.encode("utf-8"))

        # Estimated size ratios compared to JSON
        size_ratios = {
            "json": 1.0,
            "csv": 0.6,  # Usually smaller due to no field names repetition
            "parquet": 0.3,  # Excellent compression
            "sqlite": 0.8,  # Some overhead for database structure
            "excel": 1.2,  # Some overhead for formatting
        }

        def format_size(size_bytes: float) -> str:
            """Format size in human readable format."""
            for unit in ["B", "KB", "MB", "GB"]:
                if size_bytes < 1024:
                    return f"{size_bytes:.1f} {unit}"
                size_bytes /= 1024
            return f"{size_bytes:.1f} TB"

        estimates = {}
        for format_name, ratio in size_ratios.items():
            estimated_size = json_size * ratio
            estimates[format_name] = format_size(estimated_size)

        return estimates

"""FlextCliRichGUI - Advanced Rich GUI interfaces using flext-core patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Interactive GUI components with Rich for advanced CLI applications.
"""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

from flext_core import FlextResult, get_logger


# Helper functions for cleaner FlextResult creation
def _success(data: Any = None) -> FlextResult[Any]:
    return FlextResult(success=True, data=data, error=None)

def _fail(error: str) -> FlextResult[Any]:
    return FlextResult(success=False, data=None, error=error)
from rich.console import Console
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table

if TYPE_CHECKING:
    from collections.abc import Callable

logger = get_logger(__name__)


class FlextCliRichGUI:
    """Advanced Rich GUI components built on flext-core patterns.

    Provides interactive dashboards, real-time monitoring, and data visualization.
    """

    def __init__(self, console: Console | None = None) -> None:
        self.console = console or Console()
        self._current_layout: Layout | None = None
        self._live_display: Live | None = None

    def create_dashboard(
        self,
        title: str = "FlextCli Dashboard",
        layout_config: dict[str, Any] | None = None,
    ) -> FlextResult[Layout]:
        """Create interactive dashboard layout.

        Args:
            title: Dashboard title
            layout_config: Layout configuration

        Returns:
            FlextResult with Layout object

        """
        try:
            layout = Layout(name="root")

            # Default layout configuration
            config = layout_config or {
                "header_height": 3,
                "footer_height": 3,
                "sidebar_width": 30,
            }

            # Create main sections
            layout.split_column(
                Layout(name="header", size=config.get("header_height", 3)),
                Layout(name="body", ratio=1),
                Layout(name="footer", size=config.get("footer_height", 3)),
            )

            # Split body into sidebar and main content
            layout["body"].split_row(
                Layout(name="sidebar", size=config.get("sidebar_width", 30)),
                Layout(name="main", ratio=1),
            )

            # Set header
            layout["header"].update(
                Panel(
                    f"[bold blue]{title}[/bold blue]",
                    style="blue",
                ),
            )

            # Set footer with timestamp
            layout["footer"].update(
                Panel(
                    f"[dim]FlextCli Dashboard - {time.strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
                    style="dim",
                ),
            )

            self._current_layout = layout
            return _success(layout)

        except Exception as e:
            logger.exception("Dashboard creation failed")
            return _fail(f"Dashboard creation failed: {e}")

    def create_data_table(
        self,
        data: list[dict[str, Any]],
        title: str | None = None,
        show_lines: bool = True,
        expand: bool = True,
        **table_options: Any,
    ) -> FlextResult[Table]:
        """Create Rich table from data using flext-core patterns.

        Args:
            data: List of dictionaries to display
            title: Table title
            show_lines: Show table lines
            expand: Expand table to full width
            **table_options: Additional Rich Table options

        Returns:
            FlextResult with Rich Table

        """
        try:
            if not data:
                return _fail("No data provided for table")

            table = Table(
                title=title,
                show_lines=show_lines,
                expand=expand,
                **table_options,
            )

            # Add columns from first row
            headers = list(data[0].keys())
            for header in headers:
                # Smart column styling based on data type
                style = self._get_column_style(data, header)
                table.add_column(header, style=style)

            # Add rows
            for row in data:
                table.add_row(*[str(row.get(h, "")) for h in headers])

            return _success(table)

        except Exception as e:
            logger.exception("Table creation failed")
            return _fail(f"Table creation failed: {e}")

    def _get_column_style(self, data: list[dict[str, Any]], column: str) -> str:
        """Determine appropriate style for column based on data types."""
        # Sample first few values to determine type
        sample_values = [row.get(column) for row in data[:5] if row.get(column) is not None]

        if not sample_values:
            return "dim"

        # Check if all values are numeric
        if all(isinstance(v, (int, float)) for v in sample_values):
            return "cyan"

        # Check if all values are boolean
        if all(isinstance(v, bool) for v in sample_values):
            return "green" if sample_values[0] else "red"

        # Check for common patterns
        if column.lower() in ("status", "state"):
            return "green"
        if column.lower() in ("error", "failed", "failure"):
            return "red"
        if column.lower() in ("warning", "warn"):
            return "yellow"
        if column.lower() in ("id", "uuid", "key"):
            return "blue"

        return "white"

    def create_progress_dashboard(
        self,
        tasks: dict[str, dict[str, Any]],
        title: str = "Progress Dashboard",
    ) -> FlextResult[Layout]:
        """Create progress tracking dashboard.

        Args:
            tasks: Dictionary of task_id -> task_info
            title: Dashboard title

        Returns:
            FlextResult with dashboard Layout

        """
        try:
            from rich.progress import (
                BarColumn,
                MofNCompleteColumn,
                Progress,
                TaskID,
                TextColumn,
                TimeElapsedColumn,
                TimeRemainingColumn,
            )

            # Create dashboard layout
            dashboard_result = self.create_dashboard(title)
            if not dashboard_result.success:
                return dashboard_result

            layout = dashboard_result.unwrap()

            # Create progress display
            progress = Progress(
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                MofNCompleteColumn(),
                TimeElapsedColumn(),
                TimeRemainingColumn(),
                expand=True,
            )

            # Add tasks to progress
            task_ids: dict[str, TaskID] = {}
            for task_id, task_info in tasks.items():
                progress_task_id = progress.add_task(
                    task_info.get("description", task_id),
                    total=task_info.get("total", 100),
                    completed=task_info.get("completed", 0),
                )
                task_ids[task_id] = progress_task_id

            # Update main area with progress
            layout["main"].update(Panel(progress, title="Tasks Progress", border_style="green"))

            # Store task IDs for updates
            self._progress_task_ids = task_ids
            self._progress_display = progress

            return _success(layout)

        except Exception as e:
            logger.exception("Progress dashboard creation failed")
            return _fail(f"Progress dashboard creation failed: {e}")

    def create_metrics_dashboard(
        self,
        metrics: dict[str, Any],
        title: str = "Metrics Dashboard",
        refresh_rate: float = 1.0,
    ) -> FlextResult[Layout]:
        """Create real-time metrics dashboard.

        Args:
            metrics: Dictionary of metric_name -> metric_value
            title: Dashboard title
            refresh_rate: Refresh rate in seconds

        Returns:
            FlextResult with metrics dashboard

        """
        try:
            from rich.align import Align
            from rich.columns import Columns

            # Create dashboard layout
            dashboard_result = self.create_dashboard(title)
            if not dashboard_result.success:
                return dashboard_result

            layout = dashboard_result.unwrap()

            # Create metrics panels
            metric_panels = []
            for name, value in metrics.items():
                # Format value based on type
                if isinstance(value, float):
                    formatted_value = f"{value:.2f}"
                    color = "green" if value > 0 else "red"
                elif isinstance(value, int):
                    formatted_value = f"{value:,}"
                    color = "cyan"
                else:
                    formatted_value = str(value)
                    color = "white"

                panel = Panel(
                    Align.center(f"[{color}]{formatted_value}[/{color}]", vertical="middle"),
                    title=name,
                    border_style="blue",
                    height=5,
                )
                metric_panels.append(panel)

            # Arrange metrics in columns
            metrics_display = Columns(metric_panels, equal=True, expand=True)
            layout["main"].update(metrics_display)

            # Create sidebar with metric details
            sidebar_content = self._create_metrics_sidebar(metrics)
            layout["sidebar"].update(sidebar_content)

            return _success(layout)

        except Exception as e:
            logger.exception("Metrics dashboard creation failed")
            return _fail(f"Metrics dashboard creation failed: {e}")

    def _create_metrics_sidebar(self, metrics: dict[str, Any]) -> Panel:
        """Create sidebar with metric details."""
        from rich.text import Text

        content = Text()
        content.append("Metrics Details\n\n", style="bold blue")

        for name, value in metrics.items():
            content.append(f"• {name}: ", style="white")
            content.append(f"{value}\n", style="cyan")

        content.append(f"\nLast updated: {time.strftime('%H:%M:%S')}", style="dim")

        return Panel(content, title="Info", border_style="blue")

    def start_live_dashboard(
        self,
        layout: Layout,
        update_callback: Callable[[], None] | None = None,
        refresh_rate: float = 1.0,
    ) -> FlextResult[None]:
        """Start live updating dashboard.

        Args:
            layout: Dashboard layout to display
            update_callback: Function to call for updates
            refresh_rate: Refresh rate in seconds

        Returns:
            FlextResult indicating success/failure

        """
        try:
            with Live(layout, console=self.console, refresh_per_second=1/refresh_rate) as live:
                self._live_display = live

                if update_callback:
                    # In a real application, this would run in a separate thread
                    # For now, just call once
                    update_callback()

                # Keep dashboard running (in real use, this would be event-driven)
                time.sleep(0.1)  # Minimal sleep for demonstration

            return _success(None)

        except KeyboardInterrupt:
            return _success(None)  # Clean exit
        except Exception as e:
            logger.exception("Live dashboard failed")
            return _fail(f"Live dashboard failed: {e}")

    def create_interactive_menu(
        self,
        options: dict[str, str],
        title: str = "Select Option",
        style: str = "blue",
    ) -> FlextResult[Panel]:
        """Create interactive menu panel.

        Args:
            options: Dictionary of key -> description
            title: Menu title
            style: Panel style

        Returns:
            FlextResult with menu Panel

        """
        try:
            from rich.text import Text

            content = Text()

            for key, description in options.items():
                content.append(f"[{key}] ", style="bold cyan")
                content.append(f"{description}\n", style="white")

            content.append("\nPress the corresponding key to select an option.", style="dim")

            menu_panel = Panel(
                content,
                title=title,
                border_style=style,
                expand=False,
            )

            return _success(menu_panel)

        except Exception as e:
            logger.exception("Menu creation failed")
            return _fail(f"Menu creation failed: {e}")

    def create_log_viewer(
        self,
        log_entries: list[dict[str, Any]],
        title: str = "Log Viewer",
        max_entries: int = 50,
    ) -> FlextResult[Panel]:
        """Create scrollable log viewer.

        Args:
            log_entries: List of log entry dictionaries
            title: Viewer title
            max_entries: Maximum entries to display

        Returns:
            FlextResult with log viewer Panel

        """
        try:
            from rich.text import Text

            content = Text()

            # Show latest entries first
            recent_entries = log_entries[-max_entries:] if len(log_entries) > max_entries else log_entries

            for entry in recent_entries:
                timestamp = entry.get("timestamp", "")
                level = entry.get("level", "INFO")
                message = entry.get("message", "")

                # Color code by log level
                level_colors = {
                    "DEBUG": "dim",
                    "INFO": "blue",
                    "WARNING": "yellow",
                    "ERROR": "red",
                    "CRITICAL": "bold red",
                }
                level_color = level_colors.get(level.upper(), "white")

                content.append(f"[{timestamp}] ", style="dim")
                content.append(f"{level} ", style=level_color)
                content.append(f"{message}\n", style="white")

            if len(log_entries) > max_entries:
                content.append(f"\n... showing last {max_entries} of {len(log_entries)} entries", style="dim")

            log_panel = Panel(
                content,
                title=title,
                border_style="green",
                height=20,
            )

            return _success(log_panel)

        except Exception as e:
            logger.exception("Log viewer creation failed")
            return _fail(f"Log viewer creation failed: {e}")

    def update_dashboard_content(
        self,
        section: str,
        content: Any,
    ) -> FlextResult[None]:
        """Update specific dashboard section content.

        Args:
            section: Section name ('header', 'sidebar', 'main', 'footer')
            content: New content for the section

        Returns:
            FlextResult indicating success/failure

        """
        try:
            if not self._current_layout:
                return _fail("No active dashboard layout")

            if section not in ["header", "sidebar", "main", "footer"]:
                return _fail(f"Invalid section: {section}")

            self._current_layout[section].update(content)
            return _success(None)

        except Exception as e:
            logger.exception("Dashboard update failed")
            return _fail(f"Dashboard update failed: {e}")

    @classmethod
    def create_monitoring_gui(cls) -> FlextCliRichGUI:
        """Create GUI optimized for system monitoring."""
        return cls()

    @classmethod
    def create_data_visualization_gui(cls) -> FlextCliRichGUI:
        """Create GUI optimized for data visualization."""
        return cls()

    def get_dashboard_info(self) -> FlextResult[dict[str, Any]]:
        """Get information about current dashboard state."""
        try:
            if not self._current_layout:
                return _fail("No active dashboard")

            info = {
                "has_layout": bool(self._current_layout),
                "is_live": bool(self._live_display),
                "sections": ["header", "sidebar", "main", "footer"],
                "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            }

            return _success(info)

        except Exception as e:
            return _fail(f"Dashboard info failed: {e}")

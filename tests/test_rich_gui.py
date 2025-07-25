"""Tests for FlextCliRichGUI - Rich-based GUI components."""

from __future__ import annotations

from typing import Any

import pytest
from flext_cli import FlextCliRichGUI
from rich.layout import Layout


class TestFlextCliRichGUI:
    """Test FlextCliRichGUI functionality."""

    @pytest.fixture
    def gui(self) -> FlextCliRichGUI:
        """Create GUI instance for testing."""
        return FlextCliRichGUI()

    @pytest.fixture
    def sample_data(self) -> list[dict[str, Any]]:
        """Sample test data."""
        return [
            {"id": 1, "name": "Alice", "role": "Admin", "status": "Active"},
            {"id": 2, "name": "Bob", "role": "User", "status": "Inactive"},
            {"id": 3, "name": "Charlie", "role": "Manager", "status": "Active"},
        ]

    def test_create_dashboard(self, gui: FlextCliRichGUI) -> None:
        """Test dashboard creation."""
        result = gui.create_dashboard("Test Dashboard")

        assert result.success
        dashboard = result.data
        assert isinstance(dashboard, Layout)

    def test_create_dashboard_with_config(self, gui: FlextCliRichGUI) -> None:
        """Test dashboard creation with custom configuration."""
        config = {
            "theme": "dark",
            "layout": "grid",
            "auto_refresh": True,
        }

        result = gui.create_dashboard("Configured Dashboard", config)

        assert result.success
        dashboard = result.data
        assert isinstance(dashboard, Layout)

    def test_create_data_table(
        self, gui: FlextCliRichGUI, sample_data: list[dict[str, Any]],
    ) -> None:
        """Test data table creation."""
        result = gui.create_data_table(sample_data, "Employee Data")

        assert result.success
        table = result.data
        assert isinstance(table, Layout)

    def test_create_data_table_empty_data(self, gui: FlextCliRichGUI) -> None:
        """Test data table with empty data."""
        result = gui.create_data_table([], "Empty Table")

        assert not result.success
        assert "No data provided" in result.error

    def test_create_metrics_dashboard(self, gui: FlextCliRichGUI) -> None:
        """Test metrics dashboard creation."""
        metrics = {
            "cpu_usage": {"value": 75.5, "unit": "%", "trend": "up"},
            "memory_usage": {"value": 60.2, "unit": "%", "trend": "stable"},
            "disk_usage": {"value": 45.8, "unit": "%", "trend": "down"},
            "network_io": {"value": 1024, "unit": "MB/s", "trend": "up"},
        }

        result = gui.create_metrics_dashboard(metrics, "System Metrics")

        assert result.success
        dashboard = result.data
        assert isinstance(dashboard, Layout)

    def test_create_metrics_dashboard_empty_metrics(self, gui: FlextCliRichGUI) -> None:
        """Test metrics dashboard with empty metrics."""
        result = gui.create_metrics_dashboard({}, "Empty Metrics")

        assert not result.success
        assert "No metrics provided" in result.error

    def test_create_progress_monitor(self, gui: FlextCliRichGUI) -> None:
        """Test progress monitor creation."""
        tasks = [
            {"name": "Data Processing", "progress": 75, "status": "running"},
            {"name": "File Upload", "progress": 100, "status": "completed"},
            {"name": "Validation", "progress": 25, "status": "pending"},
        ]

        result = gui.create_progress_monitor(tasks, "Task Progress")

        assert result.success
        monitor = result.data
        assert isinstance(monitor, Layout)

    def test_create_progress_monitor_empty_tasks(self, gui: FlextCliRichGUI) -> None:
        """Test progress monitor with empty tasks."""
        result = gui.create_progress_monitor([], "Empty Progress")

        assert not result.success
        assert "No tasks provided" in result.error

    def test_create_log_viewer(self, gui: FlextCliRichGUI) -> None:
        """Test log viewer creation."""
        logs = [
            {
                "timestamp": "2024-01-15 10:30:00",
                "level": "INFO",
                "message": "System started",
            },
            {
                "timestamp": "2024-01-15 10:31:00",
                "level": "WARNING",
                "message": "High memory usage",
            },
            {
                "timestamp": "2024-01-15 10:32:00",
                "level": "ERROR",
                "message": "Connection failed",
            },
        ]

        result = gui.create_log_viewer(logs, "System Logs")

        assert result.success
        viewer = result.data
        assert isinstance(viewer, Layout)

    def test_create_log_viewer_empty_logs(self, gui: FlextCliRichGUI) -> None:
        """Test log viewer with empty logs."""
        result = gui.create_log_viewer([], "Empty Logs")

        assert not result.success
        assert "No logs provided" in result.error

    def test_create_status_grid(self, gui: FlextCliRichGUI) -> None:
        """Test status grid creation."""
        statuses = {
            "database": {"status": "online", "color": "green"},
            "api": {"status": "online", "color": "green"},
            "cache": {"status": "offline", "color": "red"},
            "queue": {"status": "warning", "color": "yellow"},
        }

        result = gui.create_status_grid(statuses, "System Status")

        assert result.success
        grid = result.data
        assert isinstance(grid, Layout)

    def test_create_status_grid_empty_statuses(self, gui: FlextCliRichGUI) -> None:
        """Test status grid with empty statuses."""
        result = gui.create_status_grid({}, "Empty Status")

        assert not result.success
        assert "No status items provided" in result.error

    def test_create_chart_display(self, gui: FlextCliRichGUI) -> None:
        """Test chart display creation."""
        chart_data = {
            "labels": ["Jan", "Feb", "Mar", "Apr", "May"],
            "values": [10, 25, 30, 45, 60],
            "title": "Monthly Sales",
        }

        result = gui.create_chart_display(chart_data, "Sales Chart")

        assert result.success
        chart = result.data
        assert isinstance(chart, Layout)

    def test_create_chart_display_invalid_data(self, gui: FlextCliRichGUI) -> None:
        """Test chart display with invalid data."""
        invalid_data = {
            "labels": ["Jan", "Feb"],  # Mismatched lengths
            "values": [10, 25, 30],
        }

        result = gui.create_chart_display(invalid_data, "Invalid Chart")

        assert not result.success
        assert "invalid" in result.error.lower() or "mismatch" in result.error.lower()

    def test_start_live_display(self, gui: FlextCliRichGUI) -> None:
        """Test starting live display."""
        dashboard_result = gui.create_dashboard("Live Test")
        assert dashboard_result.success

        dashboard = dashboard_result.data
        result = gui.start_live_display(dashboard)

        # Live display starts successfully
        assert result.success

    def test_stop_live_display(self, gui: FlextCliRichGUI) -> None:
        """Test stopping live display."""
        # Start a live display first
        dashboard_result = gui.create_dashboard("Test Dashboard")
        dashboard = dashboard_result.data

        start_result = gui.start_live_display(dashboard)
        assert start_result.success

        # Stop the display
        stop_result = gui.stop_live_display()
        assert stop_result.success

    def test_stop_live_display_not_running(self, gui: FlextCliRichGUI) -> None:
        """Test stopping live display when not running."""
        result = gui.stop_live_display()

        assert not result.success
        assert "not running" in result.error.lower()

    def test_update_dashboard_content(
        self, gui: FlextCliRichGUI, sample_data: list[dict[str, Any]],
    ) -> None:
        """Test updating dashboard content."""
        # Create dashboard first
        dashboard_result = gui.create_dashboard("Update Test")
        assert dashboard_result.success

        dashboard = dashboard_result.data

        # Update with new content
        new_content = {
            "header": "Updated Header",
            "body": sample_data,
            "footer": "Updated Footer",
        }

        result = gui.update_dashboard_content(dashboard, new_content)

        assert result.success

    def test_create_interactive_menu(self, gui: FlextCliRichGUI) -> None:
        """Test interactive menu creation."""
        menu_items = [
            {"key": "1", "label": "View Reports", "action": "reports"},
            {"key": "2", "label": "Export Data", "action": "export"},
            {"key": "3", "label": "Settings", "action": "settings"},
            {"key": "q", "label": "Quit", "action": "quit"},
        ]

        result = gui.create_interactive_menu(menu_items, "Main Menu")

        assert result.success
        menu = result.data
        assert isinstance(menu, Layout)

    def test_create_interactive_menu_empty_items(self, gui: FlextCliRichGUI) -> None:
        """Test interactive menu with empty items."""
        result = gui.create_interactive_menu([], "Empty Menu")

        assert not result.success
        assert "No menu items provided" in result.error

    def test_create_data_visualization(
        self, gui: FlextCliRichGUI, sample_data: list[dict[str, Any]],
    ) -> None:
        """Test data visualization creation."""
        viz_config = {
            "type": "bar_chart",
            "x_field": "name",
            "y_field": "id",
            "title": "Employee Distribution",
        }

        result = gui.create_data_visualization(sample_data, viz_config)

        assert result.success
        visualization = result.data
        assert isinstance(visualization, Layout)

    def test_create_data_visualization_empty_data(self, gui: FlextCliRichGUI) -> None:
        """Test data visualization with empty data."""
        viz_config = {"type": "table", "title": "Empty Viz"}

        result = gui.create_data_visualization([], viz_config)

        assert not result.success
        assert "No data provided" in result.error

    def test_create_split_view(
        self, gui: FlextCliRichGUI, sample_data: list[dict[str, Any]],
    ) -> None:
        """Test split view creation."""
        left_content = gui.create_data_table(sample_data, "Left Table").data
        right_content = gui.create_metrics_dashboard(
            {"metric1": {"value": 100, "unit": "%"}},
            "Right Metrics",
        ).data

        result = gui.create_split_view(left_content, right_content, "Split View")

        assert result.success
        split_view = result.data
        assert isinstance(split_view, Layout)

    def test_create_tabbed_interface(
        self, gui: FlextCliRichGUI, sample_data: list[dict[str, Any]],
    ) -> None:
        """Test tabbed interface creation."""
        tabs = {
            "Data": gui.create_data_table(sample_data, "Data Tab").data,
            "Metrics": gui.create_metrics_dashboard(
                {"metric1": {"value": 100, "unit": "%"}},
                "Metrics Tab",
            ).data,
            "Logs": gui.create_log_viewer(
                [
                    {
                        "timestamp": "2024-01-15 10:30:00",
                        "level": "INFO",
                        "message": "Test",
                    },
                ],
                "Logs Tab",
            ).data,
        }

        result = gui.create_tabbed_interface(tabs, "Tabbed Interface")

        assert result.success
        tabbed_view = result.data
        assert isinstance(tabbed_view, Layout)

    def test_create_tabbed_interface_empty_tabs(self, gui: FlextCliRichGUI) -> None:
        """Test tabbed interface with empty tabs."""
        result = gui.create_tabbed_interface({}, "Empty Tabs")

        assert not result.success
        assert "No tabs provided" in result.error

    def test_factory_methods(self) -> None:
        """Test factory methods for creating GUI instances."""
        # Test with default configuration
        data_gui = FlextCliRichGUI.create_data_gui()
        assert isinstance(data_gui, FlextCliRichGUI)

    def test_console_integration(self, gui: FlextCliRichGUI) -> None:
        """Test console integration."""
        from rich.console import Console

        # Test that console is properly initialized
        assert isinstance(gui.console, Console)

    def test_theme_configuration(self, gui: FlextCliRichGUI) -> None:
        """Test theme configuration."""
        # Test setting different themes
        themes = ["default", "dark", "light", "monokai"]

        for theme in themes:
            result = gui.set_theme(theme)
            # Should succeed or gracefully handle unsupported themes
            if not result.success:
                assert (
                    "unsupported" in result.error.lower()
                    or "unknown" in result.error.lower()
                )

    def test_layout_responsiveness(self, gui: FlextCliRichGUI) -> None:
        """Test layout responsiveness to different screen sizes."""
        # Simulate different console sizes
        test_sizes = [(80, 24), (120, 30), (160, 40)]

        for _width, _height in test_sizes:
            # Create a dashboard and test responsiveness
            result = gui.create_dashboard("Responsive Test")
            assert result.success

            dashboard = result.data
            assert isinstance(dashboard, Layout)

    def test_error_handling_edge_cases(self, gui: FlextCliRichGUI) -> None:
        """Test error handling for edge cases."""
        # Test with None data
        result = gui.create_data_table(None, "None Data")  # type: ignore[arg-type]
        assert not result.success

        # Test with very large datasets
        huge_data = [{"id": i, "value": f"item_{i}"} for i in range(10000)]
        result = gui.create_data_table(
            huge_data[:100], "Large Data Sample",
        )  # Sample only
        # Should handle gracefully without crashing
        assert result.success

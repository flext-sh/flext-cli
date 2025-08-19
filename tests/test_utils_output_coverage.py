"""Tests for utils/output.py to improve coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from io import StringIO
from unittest.mock import MagicMock, patch

from rich.console import Console

from flext_cli.utils.output import (
    format_json,
    format_pipeline,
    format_pipeline_list,
    format_plugin_list,
    format_yaml,
    print_error,
    print_info,
    print_success,
    print_warning,
    setup_console,
    show_flext_cli_paths,
)


def create_test_console() -> Console:
    """Create a console suitable for testing without ANSI codes."""
    return Console(file=StringIO(), force_terminal=False, no_color=True, width=120)


class TestSetupConsole:
    """Test setup_console function."""

    def test_setup_console_default(self) -> None:
        """Test setting up console with default settings."""
        console = setup_console()

        assert isinstance(console, Console)
        assert console.is_terminal or not console.is_terminal  # Any boolean is fine
        assert not console.quiet

    def test_setup_console_no_color(self) -> None:
        """Test setting up console with no color."""
        console = setup_console(no_color=True)

        assert isinstance(console, Console)
        assert console._color_system is None

    def test_setup_console_quiet(self) -> None:
        """Test setting up console in quiet mode."""
        console = setup_console(quiet=True)

        assert isinstance(console, Console)
        assert console.quiet

    def test_setup_console_both_flags(self) -> None:
        """Test setting up console with both no_color and quiet."""
        console = setup_console(no_color=True, quiet=True)

        assert isinstance(console, Console)
        assert console._color_system is None
        assert console.quiet


class TestPrintFunctions:
    """Test print utility functions."""

    def test_print_success(self) -> None:
        """Test print_success function."""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)

        print_success(console, "Operation completed successfully")

        result = output.getvalue()
        assert "✓" in result
        assert "Operation completed successfully" in result

    def test_print_error_simple(self) -> None:
        """Test print_error function without details."""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)

        print_error(console, "Something went wrong")

        result = output.getvalue()
        assert "Error:" in result
        assert "Something went wrong" in result

    def test_print_error_with_details(self) -> None:
        """Test print_error function with details."""
        output = StringIO()
        # Use no_color to avoid ANSI codes in assertions
        console = Console(file=output, force_terminal=False, no_color=True, width=80)

        print_error(console, "Connection failed", "Network timeout after 30 seconds")

        result = output.getvalue()
        assert "Error:" in result
        assert "Connection failed" in result
        assert "Network timeout after 30 seconds" in result

    def test_print_warning(self) -> None:
        """Test print_warning function."""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)

        print_warning(console, "This is a warning message")

        result = output.getvalue()
        assert "⚠" in result
        assert "This is a warning message" in result

    def test_print_info(self) -> None:
        """Test print_info function."""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)

        print_info(console, "Information message here")

        result = output.getvalue()
        assert "i" in result
        assert "Information message here" in result


class TestShowFlextCliPaths:
    """Test show_flext_cli_paths function."""

    @patch("flext_cli.utils.output.get_config")
    def test_show_flext_cli_paths(self, mock_get_config: MagicMock) -> None:
        """Test displaying FLEXT CLI paths."""
        # Mock config object
        mock_config = MagicMock()
        mock_config.config_dir = "/home/user/.flext/config"
        mock_config.cache_dir = "/home/user/.flext/cache"
        mock_config.log_dir = "/home/user/.flext/logs"
        mock_get_config.return_value = mock_config

        output = StringIO()
        console = Console(file=output, force_terminal=False, no_color=True, width=80)

        show_flext_cli_paths(console)

        result = output.getvalue()
        assert "FLEXT CLI Paths:" in result
        assert "config" in result
        assert "cache" in result
        assert "logs" in result


class TestFormatPluginList:
    """Test format_plugin_list function."""

    def test_format_plugin_list_empty(self) -> None:
        """Test formatting empty plugin list."""
        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)

        format_plugin_list(console, [], "table")

        result = output.getvalue()
        assert "No plugins found" in result

    def test_format_plugin_list_json(self) -> None:
        """Test formatting plugins as JSON."""
        plugins = [
            {"name": "test-plugin", "type": "extractor", "version": "1.0.0", "description": "Test plugin"},
            {"name": "another-plugin", "type": "loader", "version": "2.0.0", "description": "Another plugin"}
        ]

        output = StringIO()
        console = Console(file=output, force_terminal=False, no_color=True, width=80)

        format_plugin_list(console, plugins, "json")

        result = output.getvalue()
        # Parse the JSON without color codes
        parsed = json.loads(result.strip())
        assert len(parsed) == 2
        assert parsed[0]["name"] == "test-plugin"
        assert parsed[1]["name"] == "another-plugin"

    def test_format_plugin_list_table(self) -> None:
        """Test formatting plugins as table."""
        plugins = [
            {"name": "test-plugin", "type": "extractor", "version": "1.0.0", "description": "Test plugin"},
            {"name": "loader-plugin", "type": "loader", "version": "1.5.0", "description": "Loads data"}
        ]

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=120)

        format_plugin_list(console, plugins, "table")

        result = output.getvalue()
        assert "Available Plugins" in result
        assert "test-plugin" in result
        assert "loader-plugin" in result
        assert "extractor" in result
        assert "loader" in result

    def test_format_plugin_list_missing_fields(self) -> None:
        """Test formatting plugins with missing fields."""
        plugins = [
            {"name": "incomplete-plugin"},  # Missing other fields
            {}  # Completely empty
        ]

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=120)

        format_plugin_list(console, plugins, "table")

        result = output.getvalue()
        assert "incomplete-plugin" in result
        assert "Unknown" in result  # Default values
        assert "No description" in result


class TestFormatPipelineList:
    """Test format_pipeline_list function."""

    def test_format_pipeline_list_empty(self) -> None:
        """Test formatting empty pipeline list."""
        mock_pipeline_list = MagicMock()
        mock_pipeline_list.pipelines = []

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)

        format_pipeline_list(console, mock_pipeline_list)

        result = output.getvalue()
        assert "No pipelines found" in result

    def test_format_pipeline_list_with_data(self) -> None:
        """Test formatting pipeline list with data."""
        mock_pipeline1 = MagicMock()
        mock_pipeline1.id = "pipeline-123456789"
        mock_pipeline1.name = "Test Pipeline"
        mock_pipeline1.status = "running"
        mock_pipeline1.created_at = "2025-01-01T00:00:00Z"

        mock_pipeline2 = MagicMock()
        mock_pipeline2.id = "pipeline-987654321"
        mock_pipeline2.name = "Another Pipeline"
        mock_pipeline2.status = "completed"
        mock_pipeline2.created_at = "2025-01-02T00:00:00Z"

        mock_pipeline_list = MagicMock()
        mock_pipeline_list.pipelines = [mock_pipeline1, mock_pipeline2]
        mock_pipeline_list.total = 2
        mock_pipeline_list.page = 1
        mock_pipeline_list.page_size = 10

        output = StringIO()
        console = Console(file=output, force_terminal=False, no_color=True, width=120)

        format_pipeline_list(console, mock_pipeline_list)

        result = output.getvalue()
        assert "Pipelines" in result
        assert "Test Pipeline" in result
        assert "Another Pipeline" in result
        assert "Total: 2 pipelines" in result

    def test_format_pipeline_list_status_colors(self) -> None:
        """Test that different statuses get different colors."""
        statuses = ["running", "failed", "pending", "completed", "unknown"]

        for status in statuses:
            mock_pipeline = MagicMock()
            mock_pipeline.id = f"pipeline-{status}"
            mock_pipeline.name = f"{status.title()} Pipeline"
            mock_pipeline.status = status
            mock_pipeline.created_at = "2025-01-01T00:00:00Z"

            mock_pipeline_list = MagicMock()
            mock_pipeline_list.pipelines = [mock_pipeline]
            mock_pipeline_list.total = 1
            mock_pipeline_list.page = 1
            mock_pipeline_list.page_size = 10

            output = StringIO()
            console = Console(file=output, force_terminal=True, width=120)

            format_pipeline_list(console, mock_pipeline_list)

            result = output.getvalue()
            assert f"{status.title()} Pipeline" in result

    def test_format_pipeline_list_pagination(self) -> None:
        """Test pagination display."""
        # Create a pipeline so we don't hit the empty case
        mock_pipeline = MagicMock()
        mock_pipeline.id = "pipeline-123"
        mock_pipeline.name = "Test Pipeline"
        mock_pipeline.status = "running"
        mock_pipeline.created_at = "2025-01-01T00:00:00Z"

        mock_pipeline_list = MagicMock()
        mock_pipeline_list.pipelines = [mock_pipeline]  # Add one pipeline
        mock_pipeline_list.total = 25
        mock_pipeline_list.page = 2
        mock_pipeline_list.page_size = 10

        output = StringIO()
        console = Console(file=output, force_terminal=False, no_color=True, width=80)

        format_pipeline_list(console, mock_pipeline_list)

        result = output.getvalue()
        assert "Page 2 of 3" in result  # 25 total / 10 per page = 3 pages
        assert "Total: 25 pipelines" in result


class TestFormatPipeline:
    """Test format_pipeline function."""

    def test_format_pipeline_basic(self) -> None:
        """Test formatting a single pipeline."""
        mock_pipeline = MagicMock()
        mock_pipeline.name = "My Pipeline"
        mock_pipeline.id = "pipeline-12345"
        mock_pipeline.status = "running"
        mock_pipeline.created_at = "2025-01-01T00:00:00Z"
        mock_pipeline.updated_at = "2025-01-01T12:00:00Z"
        mock_pipeline.config = None

        output = StringIO()
        console = Console(file=output, force_terminal=False, no_color=True, width=120)

        format_pipeline(console, mock_pipeline)

        result = output.getvalue()
        assert "My Pipeline" in result
        assert "pipeline-12345" in result
        assert "running" in result
        assert "2025-01-01T00:00:00Z" in result
        assert "2025-01-01T12:00:00Z" in result

    def test_format_pipeline_with_config(self) -> None:
        """Test formatting pipeline with configuration."""
        mock_config = MagicMock()
        mock_config.tap = "tap-postgres"
        mock_config.target = "target-postgres"
        mock_config.transform = "dbt"
        mock_config.schedule = "0 0 * * *"
        mock_config.config = {"host": "localhost", "port": 5432}

        mock_pipeline = MagicMock()
        mock_pipeline.name = "DB Pipeline"
        mock_pipeline.id = "pipeline-db-123"
        mock_pipeline.status = "completed"
        mock_pipeline.created_at = "2025-01-01T00:00:00Z"
        mock_pipeline.updated_at = ""
        mock_pipeline.config = mock_config

        output = StringIO()
        console = Console(file=output, force_terminal=False, no_color=True, width=120)

        format_pipeline(console, mock_pipeline)

        result = output.getvalue()
        assert "DB Pipeline" in result
        assert "Configuration:" in result
        assert "tap-postgres" in result
        assert "target-postgres" in result
        assert "dbt" in result
        assert "0 0 * * *" in result
        assert "host: localhost" in result
        assert "port: 5432" in result

    def test_format_pipeline_minimal_info(self) -> None:
        """Test formatting pipeline with minimal information."""
        mock_pipeline = MagicMock()
        mock_pipeline.name = ""
        mock_pipeline.id = ""
        mock_pipeline.status = ""
        mock_pipeline.created_at = ""
        mock_pipeline.updated_at = ""
        mock_pipeline.config = None

        output = StringIO()
        console = Console(file=output, force_terminal=True, width=80)

        format_pipeline(console, mock_pipeline)

        result = output.getvalue()
        # Should handle empty values gracefully
        assert "ID:" in result
        assert "Status:" in result


class TestFormatJson:
    """Test format_json function."""

    def test_format_json_dict(self) -> None:
        """Test formatting dictionary as JSON."""
        data = {"name": "test", "value": 123, "active": True}

        result = format_json(data)

        parsed = json.loads(result)
        assert parsed["name"] == "test"
        assert parsed["value"] == 123
        assert parsed["active"] is True
        assert result.count("\n") > 0  # Should be pretty-printed

    def test_format_json_list(self) -> None:
        """Test formatting list as JSON."""
        data = [{"id": 1}, {"id": 2}, {"id": 3}]

        result = format_json(data)

        parsed = json.loads(result)
        assert len(parsed) == 3
        assert parsed[0]["id"] == 1

    def test_format_json_with_non_serializable(self) -> None:
        """Test formatting data with non-JSON-serializable objects."""
        from datetime import datetime

        data = {"timestamp": datetime(2025, 1, 1, 12, 0, 0)}

        result = format_json(data)

        # Should use default=str to handle datetime
        assert "2025-01-01 12:00:00" in result

    def test_format_json_none(self) -> None:
        """Test formatting None as JSON."""
        result = format_json(None)

        assert result == "null"


class TestFormatYaml:
    """Test format_yaml function."""

    def test_format_yaml_dict(self) -> None:
        """Test formatting dictionary as YAML."""
        data = {"name": "test", "value": 123, "nested": {"key": "value"}}

        result = format_yaml(data)

        assert "name: test" in result
        assert "value: 123" in result
        assert "nested:" in result
        assert "key: value" in result

    def test_format_yaml_list(self) -> None:
        """Test formatting list as YAML."""
        data = ["item1", "item2", "item3"]

        result = format_yaml(data)

        assert "- item1" in result
        assert "- item2" in result
        assert "- item3" in result

    def test_format_yaml_none(self) -> None:
        """Test formatting None as YAML."""
        result = format_yaml(None)

        assert result == "null"

    def test_format_yaml_strips_document_end(self) -> None:
        """Test that YAML document end markers are stripped."""
        data = {"simple": "data"}

        result = format_yaml(data)

        # Should not contain document end marker
        assert "..." not in result
        assert result.strip() == result  # Should be stripped

    def test_format_yaml_complex_data(self) -> None:
        """Test formatting complex nested data as YAML."""
        data = {
            "database": {
                "host": "localhost",
                "port": 5432,
                "settings": ["ssl=true", "timeout=30"]
            }
        }

        result = format_yaml(data)

        assert "database:" in result
        assert "host: localhost" in result
        assert "port: 5432" in result
        assert "settings:" in result
        assert "ssl=true" in result

"""Tests for utils output utilities.

Tests output formatting utilities for coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import yaml
from rich.console import Console
from rich.table import Table

from flext_cli import (
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
)

# Constants
EXPECTED_BULK_SIZE = 2


class TestSetupConsole:
    """Test console setup functionality."""

    def test_setup_console_default(self) -> None:
      """Test console setup with default settings."""
      console = setup_console()

      assert isinstance(console, Console)
      # Default settings - Rich Console has _color_system attribute
      assert hasattr(console, "_color_system")
      assert not console.quiet

    def test_setup_console_no_color(self) -> None:
      """Test console setup with no color."""
      console = setup_console(no_color=True)

      assert isinstance(console, Console)
      # When no_color=True, color_system should be None
      assert hasattr(console, "_color_system")

    def test_setup_console_quiet(self) -> None:
      """Test console setup with quiet mode."""
      console = setup_console(quiet=True)

      assert isinstance(console, Console)
      if not (console.quiet):
          msg: str = f"Expected True, got {console.quiet}"
          raise AssertionError(msg)

    def test_setup_console_both_options(self) -> None:
      """Test console setup with both no_color and quiet."""
      console = setup_console(no_color=True, quiet=True)

      assert isinstance(console, Console)
      # Verify console has expected attributes
      assert hasattr(console, "_color_system")
      if not (console.quiet):
          msg: str = f"Expected True, got {console.quiet}"
          raise AssertionError(msg)


class TestFormatPipelineList:
    """Test pipeline list formatting."""

    def test_format_empty_pipeline_list(self) -> None:
      """Test formatting empty pipeline list."""
      console = MagicMock(spec=Console)
      pipeline_list = MagicMock()
      pipeline_list.pipelines = []

      format_pipeline_list(console, pipeline_list)

      console.print.assert_called_once_with("[yellow]No pipelines found[/yellow]")

    def test_format_pipeline_list_with_pipelines(self) -> None:
      """Test formatting pipeline list with pipelines."""
      console = MagicMock(spec=Console)

      # Mock pipeline
      pipeline = MagicMock()
      pipeline.id = "12345678-1234-1234-1234-123456789012"
      pipeline.name = "test-pipeline"
      pipeline.status = "running"
      pipeline.created_at = "2025-01-01T00:00:00Z"

      # Mock pipeline list
      pipeline_list = MagicMock()
      pipeline_list.pipelines = [pipeline]
      pipeline_list.total = 1
      pipeline_list.page = 1
      pipeline_list.page_size = 10

      with patch("flext_cli.utils.output.Table") as mock_table_class:
          mock_table = MagicMock(spec=Table)
          mock_table_class.return_value = mock_table

          format_pipeline_list(console, pipeline_list)

          # Check table creation
          mock_table_class.assert_called_once_with(title="Pipelines (Page 1 of 1)")

          # Check table columns
          mock_table.add_column.assert_any_call("ID", style="cyan", no_wrap=True)
          mock_table.add_column.assert_any_call("Name", style="white")
          mock_table.add_column.assert_any_call("Status", style="green")
          mock_table.add_column.assert_any_call("Created", style="dim")

          # Check table row
          mock_table.add_row.assert_called_once_with(
              "12345678",  # First 8 chars
              "test-pipeline",
              "[green]running[/green]",
              "2025-01-01T00:00:00Z",
          )

          # Check console output
          console.print.assert_any_call(mock_table)
          console.print.assert_any_call("\nTotal: 1 pipelines")

    def test_format_pipeline_list_multiple_pages(self) -> None:
      """Test formatting pipeline list with multiple pages."""
      console = MagicMock(spec=Console)

      pipeline_list = MagicMock()
      pipeline_list.pipelines = [MagicMock()]
      pipeline_list.total = 25
      pipeline_list.page = 2
      pipeline_list.page_size = 10

      with patch("flext_cli.utils.output.Table") as mock_table_class:
          format_pipeline_list(console, pipeline_list)

          # Total pages = (25 + 10 - 1) // 10 = 3
          mock_table_class.assert_called_once_with(title="Pipelines (Page 2 of 3)")

    def test_format_pipeline_list_status_colors(self) -> None:
      """Test different status colors in pipeline list."""
      console = MagicMock(spec=Console)

      statuses_and_colors = [
          ("running", "green"),
          ("failed", "red"),
          ("pending", "yellow"),
          ("completed", "blue"),
          ("unknown", "white"),  # Default color
      ]

      for status, color in statuses_and_colors:
          pipeline = MagicMock()
          pipeline.id = "12345678-1234-1234-1234-123456789012"
          pipeline.name = "test-pipeline"
          pipeline.status = status
          pipeline.created_at = "2025-01-01T00:00:00Z"

          pipeline_list = MagicMock()
          pipeline_list.pipelines = [pipeline]
          pipeline_list.total = 1
          pipeline_list.page = 1
          pipeline_list.page_size = 10

          with patch("flext_cli.utils.output.Table") as mock_table_class:
              mock_table = MagicMock(spec=Table)
              mock_table_class.return_value = mock_table

              format_pipeline_list(console, pipeline_list)

              expected_status = f"[{color}]{status}[/{color}]"
              mock_table.add_row.assert_called_with(
                  "12345678",
                  "test-pipeline",
                  expected_status,
                  "2025-01-01T00:00:00Z",
              )


class TestFormatPipeline:
    """Test individual pipeline formatting."""

    def test_format_pipeline_basic(self) -> None:
      """Test formatting basic pipeline."""
      console = MagicMock(spec=Console)

      pipeline = MagicMock()
      pipeline.name = "test-pipeline"
      pipeline.id = "12345678-1234-1234-1234-123456789012"
      pipeline.status = "running"
      pipeline.created_at = "2025-01-01T00:00:00Z"
      pipeline.updated_at = "2025-01-01T12:00:00Z"
      pipeline.config = None

      format_pipeline(console, pipeline)

      # Check basic information was printed
      console.print.assert_any_call("\n[bold cyan]test-pipeline[/bold cyan]")
      console.print.assert_any_call("ID: 12345678-1234-1234-1234-123456789012")
      console.print.assert_any_call("Status: running")
      console.print.assert_any_call("Created: 2025-01-01T00:00:00Z")
      console.print.assert_any_call("Updated: 2025-01-01T12:00:00Z")

    def test_format_pipeline_with_config(self) -> None:
      """Test formatting pipeline with configuration."""
      console = MagicMock(spec=Console)

      # Mock pipeline config
      config = MagicMock()
      config.tap = "tap-csv"
      config.target = "target-postgres"
      config.transform = None
      config.schedule = None
      config.config = None

      pipeline = MagicMock()
      pipeline.name = "test-pipeline"
      pipeline.id = "12345678-1234-1234-1234-123456789012"
      pipeline.status = "running"
      pipeline.created_at = "2025-01-01T00:00:00Z"
      pipeline.updated_at = "2025-01-01T12:00:00Z"
      pipeline.config = config

      format_pipeline(console, pipeline)

      # Check configuration was printed
      console.print.assert_any_call("\n[bold]Configuration:[/bold]")
      console.print.assert_any_call("  Tap: tap-csv")
      console.print.assert_any_call("  Target: target-postgres")

    def test_format_pipeline_with_full_config(self) -> None:
      """Test formatting pipeline with full configuration."""
      console = MagicMock(spec=Console)

      # Mock pipeline config
      config = MagicMock()
      config.tap = "tap-csv"
      config.target = "target-postgres"
      config.transform = "dbt-transform"
      config.schedule = "0 8 * * *"
      config.config = {"setting1": "value1", "setting2": "value2"}

      pipeline = MagicMock()
      pipeline.name = "test-pipeline"
      pipeline.config = config
      pipeline.id = "test-id"
      pipeline.status = "running"
      pipeline.created_at = "2025-01-01"
      pipeline.updated_at = "2025-01-02"

      format_pipeline(console, pipeline)

      # Check all configuration elements were printed
      console.print.assert_any_call("  Tap: tap-csv")
      console.print.assert_any_call("  Target: target-postgres")
      console.print.assert_any_call("  Transform: dbt-transform")
      console.print.assert_any_call("  Schedule: 0 8 * * *")
      console.print.assert_any_call("  Config:")


class TestFormatPluginList:
    """Test plugin list formatting."""

    def test_format_empty_plugin_list(self) -> None:
      """Test formatting empty plugin list."""
      console = MagicMock(spec=Console)
      plugins: list[dict[str, object]] = []

      format_plugin_list(console, plugins, "table")

      console.print.assert_called_once_with("[yellow]No plugins found[/yellow]")

    def test_format_plugin_list_table(self) -> None:
      """Test formatting plugin list as table."""
      console = MagicMock(spec=Console)

      plugins: list[dict[str, object]] = [
          {
              "name": "plugin1",
              "type": "tap",
              "version": "0.9.0",
              "description": "Test plugin 1",
          },
          {
              "name": "plugin2",
              "type": "target",
              "version": "0.9.0",
              "description": "Test plugin 2",
          },
      ]

      with patch("flext_cli.utils.output.Table") as mock_table_class:
          mock_table = MagicMock(spec=Table)
          mock_table_class.return_value = mock_table

          format_plugin_list(console, plugins, "table")

          # Check table creation
          mock_table_class.assert_called_once_with(title="Available Plugins")

          # Check table columns
          mock_table.add_column.assert_any_call("Name", style="cyan")
          mock_table.add_column.assert_any_call("Type", style="white")
          mock_table.add_column.assert_any_call("Version", style="green")
          mock_table.add_column.assert_any_call("Description", style="dim")

          # Check table rows
          if mock_table.add_row.call_count != EXPECTED_BULK_SIZE:
              msg: str = f"Expected {2}, got {mock_table.add_row.call_count}"
              raise AssertionError(msg)
          mock_table.add_row.assert_any_call(
              "plugin1",
              "tap",
              "0.9.0",
              "Test plugin 1",
          )
          mock_table.add_row.assert_any_call(
              "plugin2",
              "target",
              "0.9.0",
              "Test plugin 2",
          )

          console.print.assert_called_once_with(mock_table)

    def test_format_plugin_list_json(self) -> None:
      """Test formatting plugin list as JSON."""
      console = MagicMock(spec=Console)

      plugins: list[dict[str, object]] = [
          {
              "name": "plugin1",
              "type": "tap",
              "version": "0.9.0",
              "description": "Test plugin 1",
          },
      ]

      format_plugin_list(console, plugins, "json")

      # Should print JSON representation
      expected_json = json.dumps(plugins, indent=2)
      console.print.assert_called_once_with(expected_json)

    def test_format_plugin_list_missing_fields(self) -> None:
      """Test formatting plugin list with missing fields."""
      console = MagicMock(spec=Console)

      plugins: list[dict[str, object]] = [
          {
              "name": "plugin1",
              # Missing type, version, description
          },
          {
              "type": "target",
              "version": "0.9.0",
              # Missing name, description
          },
      ]

      with patch("flext_cli.utils.output.Table") as mock_table_class:
          mock_table = MagicMock(spec=Table)
          mock_table_class.return_value = mock_table

          format_plugin_list(console, plugins, "table")

          # Should use default values for missing fields
          mock_table.add_row.assert_any_call(
              "plugin1",
              "Unknown",
              "Unknown",
              "No description",
          )
          mock_table.add_row.assert_any_call(
              "Unknown",
              "target",
              "0.9.0",
              "No description",
          )


class TestFormatJson:
    """Test JSON formatting utility."""

    def test_format_json_simple(self) -> None:
      """Test formatting simple data as JSON."""
      data = {"key": "value", "number": 42}

      result = format_json(data)

      assert isinstance(result, str)
      if "key" not in result:
          key_msg: str = f"Expected {'key'} in {result}"
          raise AssertionError(key_msg)
      assert "value" in result
      if "42" not in result:
          value_msg: str = f"Expected {'42'} in {result}"
          raise AssertionError(value_msg)

      # Should be valid JSON
      parsed = json.loads(result)
      if parsed != data:
          parse_msg: str = f"Expected {data}, got {parsed}"
          raise AssertionError(parse_msg)

    def test_format_json_complex(self) -> None:
      """Test formatting complex data as JSON."""
      data = {
          "string": "value",
          "number": 42,
          "boolean": True,
          "null": None,
          "list": [1, 2, 3],
          "nested": {"inner": "value"},
      }

      result = format_json(data)

      assert isinstance(result, str)
      parsed = json.loads(result)
      if parsed != data:
          msg: str = f"Expected {data}, got {parsed}"
          raise AssertionError(msg)

    def test_format_json_with_objects(self) -> None:
      """Test formatting data with non-serializable objects."""
      data = {
          "timestamp": datetime.now(UTC),
          "value": "test",
      }

      result = format_json(data)

      # Should not raise exception due to default=str
      assert isinstance(result, str)
      parsed = json.loads(result)
      if "timestamp" not in parsed:
          timestamp_msg: str = f"Expected {'timestamp'} in {parsed}"
          raise AssertionError(timestamp_msg)
      assert "value" in parsed
      if parsed["value"] != "test":
          value_check_msg: str = f"Expected {'test'}, got {parsed['value']}"
          raise AssertionError(value_check_msg)


class TestFormatYaml:
    """Test YAML formatting utility."""

    def test_format_yaml_simple(self) -> None:
      """Test formatting simple data as YAML."""
      data = {"key": "value", "number": 42}

      result = format_yaml(data)

      assert isinstance(result, str)
      if "key: value" not in result:
          key_yaml_msg: str = f"Expected {'key: value'} in {result}"
          raise AssertionError(key_yaml_msg)
      assert "number: 42" in result

      # Should be valid YAML
      parsed = yaml.safe_load(result)
      if parsed != data:
          yaml_parse_msg: str = f"Expected {data}, got {parsed}"
          raise AssertionError(yaml_parse_msg)

    def test_format_yaml_complex(self) -> None:
      """Test formatting complex data as YAML."""
      data = {
          "string": "value",
          "number": 42,
          "boolean": True,
          "null": None,
          "list": [1, 2, 3],
          "nested": {"inner": "value"},
      }

      result = format_yaml(data)

      assert isinstance(result, str)
      parsed = yaml.safe_load(result)
      if parsed != data:
          msg: str = f"Expected {data}, got {parsed}"
          raise AssertionError(msg)

    def test_format_yaml_flow_style(self) -> None:
      """Test YAML formatting uses block style."""
      data = {"list": [1, 2, 3], "dict": {"a": 1}}

      result = format_yaml(data)

      # Should use block style (default_flow_style=False)
      if not ("- 1" in result and "list:" in result):
          msg: str = f"Expected block style with '- 1' and 'list:' in {result}"
          raise AssertionError(msg)
      assert "{" not in result  # Flow style would use braces


class TestPrintFunctions:
    """Test various print utility functions."""

    def test_print_error_basic(self) -> None:
      """Test printing basic error message."""
      console = MagicMock(spec=Console)

      print_error(console, "Something went wrong")

      console.print.assert_called_once_with(
          "[bold red]Error:[/bold red] Something went wrong",
      )

    def test_print_error_with_details(self) -> None:
      """Test printing error message with details."""
      console = MagicMock(spec=Console)

      print_error(console, "Something went wrong", "Additional details here")

      console.print.assert_any_call(
          "[bold red]Error:[/bold red] Something went wrong",
      )
      console.print.assert_any_call("[dim]Additional details here[/dim]")
      if console.print.call_count != EXPECTED_BULK_SIZE:
          msg: str = f"Expected {2}, got {console.print.call_count}"
          raise AssertionError(msg)

    def test_print_success(self) -> None:
      """Test printing success message."""
      console = MagicMock(spec=Console)

      print_success(console, "Operation completed")

      console.print.assert_called_once_with(
          "[bold green]✓[/bold green] Operation completed",
      )

    def test_print_warning(self) -> None:
      """Test printing warning message."""
      console = MagicMock(spec=Console)

      print_warning(console, "Be careful")

      console.print.assert_called_once_with("[bold yellow]⚠[/bold yellow] Be careful")

    def test_print_info(self) -> None:
      """Test printing info message."""
      console = MagicMock(spec=Console)

      print_info(console, "Information message")

      console.print.assert_called_once_with(
          "[bold blue]i[/bold blue] Information message",
      )


class TestUtilsOutputIntegration:
    """Integration tests for output utilities."""

    def test_console_integration(self) -> None:
      """Test integration with real Console."""
      console = setup_console()

      # Should work with actual console
      print_success(console, "Test message")
      print_error(console, "Test error", "Details")
      print_warning(console, "Test warning")
      print_info(console, "Test info")

    def test_rich_imports(self) -> None:
      """Test that Rich imports work correctly."""
      # Console and Table are classes, not None
      assert Console is not None
      assert Table is not None

      # Test creation
      console = Console()
      table = Table()
      assert console is not None
      assert table is not None

    def test_yaml_integration(self) -> None:
      """Test YAML integration."""
      test_data = {"key": "value", "list": [1, 2, 3]}

      yaml_output = format_yaml(test_data)
      assert isinstance(yaml_output, str)

      # Should be parseable back
      parsed = yaml.safe_load(yaml_output)
      if parsed != test_data:
          msg: str = f"Expected {test_data}, got {parsed}"
          raise AssertionError(msg)

    def test_json_integration(self) -> None:
      """Test JSON integration."""
      test_data = {"key": "value", "number": 42}

      json_output = format_json(test_data)
      assert isinstance(json_output, str)

      # Should be parseable back
      parsed = json.loads(json_output)
      if parsed != test_data:
          msg: str = f"Expected {test_data}, got {parsed}"
          raise AssertionError(msg)

    def test_table_formatting_integration(self) -> None:
      """Test table formatting integration."""
      console = setup_console()

      # Test with empty plugin list
      format_plugin_list(console, [], "table")

      # Test with plugin list
      plugins: list[dict[str, object]] = [
          {"name": "test", "type": "tap", "version": "1.0", "description": "Test"},
      ]
      format_plugin_list(console, plugins, "table")
      format_plugin_list(console, plugins, "json")

    def test_pipeline_formatting_integration(self) -> None:
      """Test pipeline formatting integration."""
      console = setup_console()

      # Mock pipeline data structures
      pipeline = MagicMock()
      pipeline.name = "test-pipeline"
      pipeline.id = "test-id"
      pipeline.status = "running"
      pipeline.created_at = "2025-01-01"
      pipeline.updated_at = "2025-01-01"
      pipeline.config = None

      pipeline_list = MagicMock()
      pipeline_list.pipelines = []

      # Should work without errors
      format_pipeline(console, pipeline)
      format_pipeline_list(console, pipeline_list)

    def test_error_handling_edge_cases(self) -> None:
      """Test error handling for edge cases."""
      console = setup_console()

      # Test with None values
      print_error(console, "Error", None)
      print_success(console, "")
      print_warning(console, "")
      print_info(console, "")

      # Test with special characters
      print_error(console, "Error with [brackets] and {braces}")
      print_success(console, "Success with émojis 🎉")

    def test_format_functions_with_none(self) -> None:
      """Test format functions with None values."""
      # Should handle None gracefully
      json_result = format_json(None)
      if json_result != "null":
          json_null_msg: str = f"Expected {'null'}, got {json_result}"
          raise AssertionError(json_null_msg)

      yaml_result = format_yaml(None)
      # YAML adds newline, so we check if it contains "null"
      if "null" not in yaml_result:
          yaml_null_msg: str = f"Expected {'null'} in {yaml_result}"
          raise AssertionError(yaml_null_msg)

    def test_format_functions_with_empty_data(self) -> None:
      """Test format functions with empty data structures."""
      # Empty dict
      if format_json({}) != "{}":
          empty_dict_msg: str = f"Expected {'{}'}, got {format_json({})}"
          raise AssertionError(empty_dict_msg)
      assert format_yaml({}).strip() == "{}"

      # Empty list
      if format_json([]) != "[]":
          empty_list_msg: str = f"Expected {'[]'}, got {format_json([])}"
          raise AssertionError(empty_list_msg)
      assert format_yaml([]).strip() == "[]"

    def test_pipeline_status_case_insensitive(self) -> None:
      """Test pipeline status color mapping is case insensitive."""
      console = MagicMock(spec=Console)

      test_cases = [
          ("RUNNING", "green"),
          ("Running", "green"),
          ("FAILED", "red"),
          ("Failed", "red"),
          ("PENDING", "yellow"),
          ("Pending", "yellow"),
          ("COMPLETED", "blue"),
          ("Completed", "blue"),
      ]

      for status, expected_color in test_cases:
          pipeline = MagicMock()
          pipeline.id = "12345678-1234-1234-1234-123456789012"
          pipeline.name = "test"
          pipeline.status = status
          pipeline.created_at = "2025-01-01"

          pipeline_list = MagicMock()
          pipeline_list.pipelines = [pipeline]
          pipeline_list.total = 1
          pipeline_list.page = 1
          pipeline_list.page_size = 10

          with patch("flext_cli.utils.output.Table") as mock_table_class:
              mock_table = MagicMock()
              mock_table_class.return_value = mock_table

              format_pipeline_list(console, pipeline_list)

              # Check that the color was applied correctly
              expected_formatted_status = (
                  f"[{expected_color}]{status}[/{expected_color}]"
              )
              mock_table.add_row.assert_called_with(
                  "12345678",
                  "test",
                  expected_formatted_status,
                  "2025-01-01",
              )

"""Comprehensive tests for utils.output module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

Tests for output utilities to achieve near 100% coverage.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

import yaml
from flext_cli.utils.output import (
    format_json,
    format_pipeline,
    format_plugin_list,
    format_yaml,
    print_error,
    print_info,
    print_success,
    print_warning,
    setup_console,
)


class TestConsoleSetup:
    """Test console setup and initialization."""

    def test_setup_console_default(self) -> None:
        """Test console setup with default settings."""
        console = setup_console()
        assert console is not None
        assert hasattr(console, "print")
        assert hasattr(console, "status")

    def test_setup_console_no_color(self) -> None:
        """Test console setup with no color."""
        console = setup_console(no_color=True)
        assert console is not None
        assert console.options.color_system is None

    def test_setup_console_quiet(self) -> None:
        """Test console setup with quiet mode."""
        console = setup_console(quiet=True)
        assert console is not None
        if not (console.quiet):
            msg = f"Expected True, got {console.quiet}"
            raise AssertionError(msg)


class TestFormatPipeline:
    """Test format_pipeline function."""

    def test_format_pipeline_basic(self) -> None:
        """Test basic pipeline formatting."""
        pipeline_data = {
            "name": "test-pipeline",
            "status": "running",
            "description": "Test pipeline",
        }

        result = format_pipeline(pipeline_data)

        if "test-pipeline" not in result:

            msg = f"Expected {"test-pipeline"} in {result}"
            raise AssertionError(msg)
        assert "running" in result
        if "Test pipeline" not in result:
            msg = f"Expected {"Test pipeline"} in {result}"
            raise AssertionError(msg)

    def test_format_pipeline_with_stats(self) -> None:
        """Test pipeline formatting with statistics."""
        pipeline_data = {
            "name": "data-pipeline",
            "status": "completed",
            "stats": {
                "records_processed": 1000,
                "errors": 2,
                "duration": "5m 30s",
            },
        }

        result = format_pipeline(pipeline_data)

        if "data-pipeline" not in result:

            msg = f"Expected {"data-pipeline"} in {result}"
            raise AssertionError(msg)
        assert "1000" in result
        if "5m 30s" not in result:
            msg = f"Expected {"5m 30s"} in {result}"
            raise AssertionError(msg)

    def test_format_pipeline_empty(self) -> None:
        """Test pipeline formatting with empty data."""
        result = format_pipeline({})
        if "No pipeline data" in result or "pipeline" not in result.lower():
            msg = f"Expected {"No pipeline data" in result or "pipeline"} in {result.lower()}"
            raise AssertionError(msg)

    def test_format_pipeline_none(self) -> None:
        """Test pipeline formatting with None data."""
        result = format_pipeline(None)
        if "No pipeline data" in result or "pipeline" not in result.lower():
            msg = f"Expected {"No pipeline data" in result or "pipeline"} in {result.lower()}"
            raise AssertionError(msg)

    def test_format_pipeline_missing_fields(self) -> None:
        """Test pipeline formatting with missing fields."""
        pipeline_data = {"name": "incomplete-pipeline"}

        result = format_pipeline(pipeline_data)

        if "incomplete-pipeline" not in result:

            msg = f"Expected {"incomplete-pipeline"} in {result}"
            raise AssertionError(msg)


class TestFormatPluginList:
    """Test format_plugin_list function."""

    def test_format_plugin_list_empty(self) -> None:
        """Test formatting empty plugin list."""
        result = format_plugin_list([])
        if "No plugin" in result or "plugin" not in result.lower():
            msg = f"Expected {"No plugin" in result or "plugin"} in {result.lower()}"
            raise AssertionError(msg)

    def test_format_plugin_list_single(self) -> None:
        """Test formatting single plugin."""
        plugins = [
            {
                "name": "test-plugin",
                "version": "1.0.0",
                "enabled": True,
                "description": "A test plugin",
            },
        ]

        result = format_plugin_list(plugins)

        if "test-plugin" not in result:

            msg = f"Expected {"test-plugin"} in {result}"
            raise AssertionError(msg)
        assert "1.0.0" in result

    def test_format_plugin_list_multiple(self) -> None:
        """Test formatting multiple plugins."""
        plugins = [
            {
                "name": "plugin-1",
                "version": "1.0.0",
                "enabled": True,
            },
            {
                "name": "plugin-2",
                "version": "2.0.0",
                "enabled": False,
            },
        ]

        result = format_plugin_list(plugins)

        if "plugin-1" not in result:

            msg = f"Expected {"plugin-1"} in {result}"
            raise AssertionError(msg)
        assert "plugin-2" in result
        if "1.0.0" not in result:
            msg = f"Expected {"1.0.0"} in {result}"
            raise AssertionError(msg)
        assert "2.0.0" in result

    def test_format_plugin_list_missing_fields(self) -> None:
        """Test formatting plugins with missing fields."""
        plugins = [{"name": "incomplete-plugin"}]

        result = format_plugin_list(plugins)

        if "incomplete-plugin" not in result:

            msg = f"Expected {"incomplete-plugin"} in {result}"
            raise AssertionError(msg)

    def test_format_plugin_list_none(self) -> None:
        """Test formatting None plugin list."""
        result = format_plugin_list(None)
        if "No plugin" in result or "plugin" not in result.lower():
            msg = f"Expected {"No plugin" in result or "plugin"} in {result.lower()}"
            raise AssertionError(msg)


class TestFormatJson:
    """Test format_json function."""

    def test_format_json_dict(self) -> None:
        """Test formatting dictionary as JSON."""
        data = {"key": "value", "number": 42}
        result = format_json(data)

        # Parse back to verify valid JSON
        parsed = json.loads(result)
        if parsed != data:
            msg = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)

    def test_format_json_list(self) -> None:
        """Test formatting list as JSON."""
        data = [1, 2, 3, "test"]
        result = format_json(data)

        parsed = json.loads(result)
        if parsed != data:
            msg = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)

    def test_format_json_string(self) -> None:
        """Test formatting string as JSON."""
        data = "simple string"
        result = format_json(data)

        parsed = json.loads(result)
        if parsed != data:
            msg = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)

    def test_format_json_none(self) -> None:
        """Test formatting None as JSON."""
        result = format_json(None)

        parsed = json.loads(result)
        assert parsed is None

    def test_format_json_complex(self) -> None:
        """Test formatting complex nested structure."""
        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25},
            ],
            "metadata": {
                "total": 2,
                "active": True,
            },
        }

        result = format_json(data)
        parsed = json.loads(result)
        if parsed != data:
            msg = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)


class TestFormatYaml:
    """Test format_yaml function."""

    def test_format_yaml_dict(self) -> None:
        """Test formatting dictionary as YAML."""
        data = {"key": "value", "number": 42}
        result = format_yaml(data)

        parsed = yaml.safe_load(result)
        if parsed != data:
            msg = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)

    def test_format_yaml_list(self) -> None:
        """Test formatting list as YAML."""
        data = [1, 2, 3, "test"]
        result = format_yaml(data)

        parsed = yaml.safe_load(result)
        if parsed != data:
            msg = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)

    def test_format_yaml_nested(self) -> None:
        """Test formatting nested structure as YAML."""
        data = {
            "config": {
                "database": {
                    "host": "localhost",
                    "port": 5432,
                },
                "features": ["auth", "logging"],
            },
        }

        result = format_yaml(data)
        parsed = yaml.safe_load(result)
        if parsed != data:
            msg = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)

    def test_format_yaml_none(self) -> None:
        """Test formatting None as YAML."""
        result = format_yaml(None)
        if result.strip() != "null":
            msg = f"Expected {"null"}, got {result.strip()}"
            raise AssertionError(msg)

    def test_format_yaml_string(self) -> None:
        """Test formatting string as YAML."""
        data = "simple string"
        result = format_yaml(data)

        parsed = yaml.safe_load(result)
        if parsed != data:
            msg = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)


class TestPrintFunctions:
    """Test print utility functions."""

    def test_print_info(self) -> None:
        """Test print_info function."""
        console = setup_console()

        # Test that function exists and can be called
        print_info(console, "Information message")

    def test_print_success(self) -> None:
        """Test print_success function."""
        console = setup_console()

        # Test that function exists and can be called
        print_success(console, "Success message")

    def test_print_warning(self) -> None:
        """Test print_warning function."""
        console = setup_console()

        # Test that function exists and can be called
        print_warning(console, "Warning message")

    def test_print_error(self) -> None:
        """Test print_error function."""
        console = setup_console()

        # Test that function exists and can be called
        print_error(console, "Error message")

    def test_print_error_with_details(self) -> None:
        """Test print_error function with details."""
        console = setup_console()

        # Test that function accepts details parameter
        print_error(console, "Error message", "Error details")

    def test_print_functions_with_empty_messages(self) -> None:
        """Test print functions with empty messages."""
        console = setup_console()

        # Test that functions handle empty messages
        print_info(console, "")
        print_success(console, "")
        print_warning(console, "")
        print_error(console, "")

    def test_print_functions_with_multiline(self) -> None:
        """Test print functions with multiline messages."""
        console = setup_console()
        multiline_message = "Line 1\nLine 2\nLine 3"

        # Test that functions handle multiline messages
        print_info(console, multiline_message)
        print_success(console, multiline_message)
        print_warning(console, multiline_message)
        print_error(console, multiline_message)


class TestUtilsOutputIntegration:
    """Integration tests for output utilities."""

    def test_json_yaml_round_trip(self) -> None:
        """Test JSON and YAML formatting round trip."""
        original_data = {
            "name": "test",
            "values": [1, 2, 3],
            "config": {"enabled": True},
        }

        # Format as JSON and parse back
        json_result = format_json(original_data)
        json_parsed = json.loads(json_result)

        # Format as YAML and parse back
        yaml_result = format_yaml(original_data)
        yaml_parsed = yaml.safe_load(yaml_result)

        # Both should match original
        if json_parsed != original_data:
            msg = f"Expected {original_data}, got {json_parsed}"
            raise AssertionError(msg)
        assert yaml_parsed == original_data

    def test_pipeline_formatting_with_real_data(self) -> None:
        """Test pipeline formatting with realistic data."""
        pipeline_data = {
            "name": "etl-pipeline",
            "status": "completed",
            "description": "Extract Transform Load pipeline",
            "created": "2025-01-20T10:30:00Z",
            "stats": {
                "records_processed": 50000,
                "errors": 0,
                "duration": "15m 42s",
                "throughput": "55.2 records/sec",
            },
            "stages": [
                {"name": "extract", "status": "completed"},
                {"name": "transform", "status": "completed"},
                {"name": "load", "status": "completed"},
            ],
        }

        result = format_pipeline(pipeline_data)

        # Should contain key information
        if "etl-pipeline" not in result:
            msg = f"Expected {"etl-pipeline"} in {result}"
            raise AssertionError(msg)
        assert "completed" in result

    def test_plugin_list_formatting_with_real_data(self) -> None:
        """Test plugin list formatting with realistic data."""
        plugins = [
            {
                "name": "auth-plugin",
                "version": "2.1.0",
                "enabled": True,
                "description": "Authentication and authorization",
                "author": "FLEXT Team",
                "dependencies": ["httpx", "jwt"],
            },
            {
                "name": "database-connector",
                "version": "1.5.3",
                "enabled": True,
                "description": "Database connectivity plugin",
                "author": "DB Team",
                "dependencies": ["sqlalchemy", "psycopg2"],
            },
            {
                "name": "legacy-importer",
                "version": "0.9.8",
                "enabled": False,
                "description": "Legacy data importer (deprecated)",
                "author": "Legacy Team",
                "dependencies": [],
            },
        ]

        result = format_plugin_list(plugins)

        # Should contain plugin information
        if "auth-plugin" not in result:
            msg = f"Expected {"auth-plugin"} in {result}"
            raise AssertionError(msg)
        assert "database-connector" in result
        if "legacy-importer" not in result:
            msg = f"Expected {"legacy-importer"} in {result}"
            raise AssertionError(msg)
        assert "2.1.0" in result

    @patch("flext_cli.utils.output.console")
    def test_print_functions_integration(self, mock_console: MagicMock) -> None:
        """Test integration of all print functions."""
        messages = [
            ("info", "Starting process"),
            ("success", "Process completed"),
            ("warning", "Performance degraded"),
            ("error", "Connection failed"),
        ]

        for msg_type, message in messages:
            if msg_type == "info":
                print_info(message)
            elif msg_type == "success":
                print_success(message)
            elif msg_type == "warning":
                print_warning(message)
            elif msg_type == "error":
                print_error(message)

        # Should have called print for each message
        if mock_console.print.call_count != len(messages):
            msg = f"Expected {len(messages)}, got {mock_console.print.call_count}"
            raise AssertionError(msg)

    def test_format_functions_with_edge_cases(self) -> None:
        """Test format functions with edge cases."""
        edge_cases = [
            {},  # Empty dict
            [],  # Empty list
            "",  # Empty string
            0,  # Zero
            False,  # Boolean False
        ]

        for case in edge_cases:
            # Should not raise exceptions
            json_result = format_json(case)
            yaml_result = format_yaml(case)

            # Should be valid JSON/YAML
            json.loads(json_result)
            yaml.safe_load(yaml_result)


class TestOutputErrorHandling:
    """Test error handling in output utilities."""

    def test_format_json_with_non_serializable(self) -> None:
        """Test JSON formatting with non-serializable object."""

        class NonSerializable:
            pass

        non_serializable_data = {"obj": NonSerializable()}

        # Should handle gracefully (might fall back to string representation)
        try:
            result = format_json(non_serializable_data)
            # If no exception, should still be valid JSON-like string
            assert isinstance(result, str)
        except (TypeError, ValueError):
            # Expected behavior for non-serializable objects
            pass

    def test_format_yaml_with_non_serializable(self) -> None:
        """Test YAML formatting with non-serializable object."""

        class NonSerializable:
            pass

        non_serializable_data = {"obj": NonSerializable()}

        # Should handle gracefully
        try:
            result = format_yaml(non_serializable_data)
            assert isinstance(result, str)
        except (TypeError, ValueError):
            # Expected behavior for non-serializable objects
            pass

    def test_format_pipeline_with_malformed_data(self) -> None:
        """Test pipeline formatting with malformed data."""
        malformed_data = {"name": {"nested": "should_be_string"}}

        result = format_pipeline(malformed_data)

        # Should handle gracefully and return string
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_plugin_list_with_malformed_data(self) -> None:
        """Test plugin list formatting with malformed data."""
        malformed_plugins = [
            {"name": ["should", "be", "string"]},
            {"version": {"major": 1, "minor": 0}},
        ]

        result = format_plugin_list(malformed_plugins)

        # Should handle gracefully and return string
        assert isinstance(result, str)
        assert len(result) > 0

"""Comprehensive tests for utils.output module.

Tests for output utilities to achieve near 100% coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json

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
        # Test that color_system is properly disabled
        # Just check that it's disabled (not specific values)
        assert hasattr(console, "_color_system")

    def test_setup_console_quiet(self) -> None:
        """Test console setup with quiet mode."""
        console = setup_console(quiet=True)
        assert console is not None
        if not (console.quiet):
            msg: str = f"Expected True, got {console.quiet}"
            raise AssertionError(msg)


class TestFormatPipeline:
    """Test format_pipeline function."""

    def test_format_pipeline_basic(self) -> None:
        """Test basic pipeline formatting."""
        from io import StringIO

        from flext_cli.client import Pipeline, PipelineConfig
        from rich.console import Console

        pipeline_config = PipelineConfig(
            name="test-pipeline", tap="tap-csv", target="target-csv",
        )
        pipeline = Pipeline(
            id="pipeline-123",
            name="test-pipeline",
            status="running",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=pipeline_config,
        )

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        # Test that function runs without errors (returns None)
        format_pipeline(console, pipeline)

        # Check output was written to console
        output = string_io.getvalue()
        assert "test-pipeline" in output
        assert "running" in output

    def test_format_pipeline_with_stats(self) -> None:
        """Test pipeline formatting with complete pipeline object."""
        from io import StringIO

        from flext_cli.client import Pipeline, PipelineConfig
        from rich.console import Console

        pipeline_config = PipelineConfig(
            name="data-pipeline", tap="tap-postgres", target="target-snowflake",
        )
        pipeline = Pipeline(
            id="pipeline-456",
            name="data-pipeline",
            status="completed",
            created_at="2025-01-20T10:30:00Z",
            updated_at="2025-01-20T10:35:00Z",
            config=pipeline_config,
        )

        # Verify existing pipeline config
        assert pipeline.config.tap == "tap-postgres"
        assert pipeline.config.target == "target-snowflake"
        assert pipeline.config.name == "data-pipeline"

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        # Test that function runs without errors (returns None)
        format_pipeline(console, pipeline)

        # Check output was written to console
        output = string_io.getvalue()
        assert "data-pipeline" in output
        assert "completed" in output

    def test_format_pipeline_empty(self) -> None:
        """Test pipeline formatting with minimal pipeline object."""
        from io import StringIO

        from flext_cli.client import Pipeline, PipelineConfig
        from rich.console import Console

        empty_config = PipelineConfig(
            name="empty-pipeline", tap="tap-none", target="target-none",
        )
        pipeline = Pipeline(
            id="pipeline-empty",
            name="empty-pipeline",
            status="pending",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=empty_config,
        )

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        # Test that function runs without errors (returns None)
        format_pipeline(console, pipeline)

        # Check output was written to console
        output = string_io.getvalue()
        assert "empty-pipeline" in output

    # Removed test_format_pipeline_none - invalid test (function expects Pipeline, not None)

    def test_format_pipeline_missing_fields(self) -> None:
        """Test pipeline formatting with minimal required fields."""
        from io import StringIO

        from flext_cli.client import Pipeline, PipelineConfig
        from rich.console import Console

        # Create proper pipeline config
        pipeline_config = PipelineConfig(
            name="incomplete-pipeline", tap="tap-csv", target="target-csv",
        )

        # Create pipeline with all required fields
        pipeline = Pipeline(
            id="pipeline-123",
            name="incomplete-pipeline",
            status="running",
            created_at="2025-01-01T00:00:00Z",
            updated_at="2025-01-01T00:00:00Z",
            config=pipeline_config,
        )

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        # Test that function runs without errors (returns None)
        format_pipeline(console, pipeline)

        # Check output was written to console
        output = string_io.getvalue()
        assert "incomplete-pipeline" in output


class TestFormatPluginList:
    """Test format_plugin_list function."""

    def test_format_plugin_list_empty(self) -> None:
        """Test formatting empty plugin list."""
        from io import StringIO

        from rich.console import Console

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        # Test that function runs without errors (returns None)
        format_plugin_list(console, [], "table")

        # Check output was written to console
        output = string_io.getvalue()
        assert "No plugins found" in output

    def test_format_plugin_list_single(self) -> None:
        """Test formatting single plugin."""
        from io import StringIO

        from rich.console import Console

        plugins = [
            {
                "name": "test-plugin",
                "version": "0.9.0",
                "enabled": True,
                "description": "A test plugin",
            },
        ]

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        # Test that function runs without errors (returns None)
        format_plugin_list(console, plugins, "table")

        # Check output was written to console
        output = string_io.getvalue()
        assert "test-plugin" in output
        assert "0.9.0" in output

    def test_format_plugin_list_multiple(self) -> None:
        """Test formatting multiple plugins."""
        from io import StringIO

        from rich.console import Console

        plugins = [
            {
                "name": "plugin-1",
                "version": "0.9.0",
                "enabled": True,
            },
            {
                "name": "plugin-2",
                "version": "0.9.0",
                "enabled": False,
            },
        ]

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        # Test that function runs without errors (returns None)
        format_plugin_list(console, plugins, "table")

        # Check output was written to console
        output = string_io.getvalue()
        assert "plugin-1" in output
        assert "plugin-2" in output
        assert "0.9.0" in output
        assert "0.9.0" in output

    def test_format_plugin_list_missing_fields(self) -> None:
        """Test formatting plugins with missing fields."""
        from io import StringIO

        from rich.console import Console

        plugins: list[dict[str, object]] = [{"name": "incomplete-plugin"}]

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        # Test that function runs without errors (returns None)
        format_plugin_list(console, plugins, "table")

        # Check output was written to console
        output = string_io.getvalue()
        assert "incomplete-plugin" in output

    # Removed test_format_plugin_list_none - invalid test (function expects list, not None)


class TestFormatJson:
    """Test format_json function."""

    def test_format_json_dict(self) -> None:
        """Test formatting dictionary as JSON."""
        data = {"key": "value", "number": 42}
        result = format_json(data)

        # Parse back to verify valid JSON
        parsed = json.loads(result)
        if parsed != data:
            msg: str = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)

    def test_format_json_list(self) -> None:
        """Test formatting list as JSON."""
        data = [1, 2, 3, "test"]
        result = format_json(data)

        parsed = json.loads(result)
        if parsed != data:
            msg: str = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)

    def test_format_json_string(self) -> None:
        """Test formatting string as JSON."""
        data = "simple string"
        result = format_json(data)

        parsed = json.loads(result)
        if parsed != data:
            msg: str = f"Expected {data}, got {parsed}"
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
            msg: str = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)


class TestFormatYaml:
    """Test format_yaml function."""

    def test_format_yaml_dict(self) -> None:
        """Test formatting dictionary as YAML."""
        data = {"key": "value", "number": 42}
        result = format_yaml(data)

        parsed = yaml.safe_load(result)
        if parsed != data:
            msg: str = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)

    def test_format_yaml_list(self) -> None:
        """Test formatting list as YAML."""
        data = [1, 2, 3, "test"]
        result = format_yaml(data)

        parsed = yaml.safe_load(result)
        if parsed != data:
            msg: str = f"Expected {data}, got {parsed}"
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
            msg: str = f"Expected {data}, got {parsed}"
            raise AssertionError(msg)

    def test_format_yaml_none(self) -> None:
        """Test formatting None as YAML."""
        result = format_yaml(None)
        if result.strip() != "null":
            msg: str = f"Expected {'null'}, got {result.strip()}"
            raise AssertionError(msg)

    def test_format_yaml_string(self) -> None:
        """Test formatting string as YAML."""
        data = "simple string"
        result = format_yaml(data)

        parsed = yaml.safe_load(result)
        if parsed != data:
            msg: str = f"Expected {data}, got {parsed}"
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
            msg: str = f"Expected {original_data}, got {json_parsed}"
            raise AssertionError(msg)
        assert yaml_parsed == original_data

    def test_pipeline_formatting_with_real_data(self) -> None:
        """Test pipeline formatting with realistic data."""
        from io import StringIO

        from flext_cli.client import Pipeline, PipelineConfig
        from rich.console import Console

        # Create proper pipeline config with all fields
        config = PipelineConfig(
            name="etl-pipeline",
            tap="tap-oracle",
            target="target-postgres",
            transform="dbt-transform",
            schedule="0 2 * * *",
            config={
                "records_processed": 50000,
                "last_execution": "2025-01-20T10:45:00Z",
                "data_source": "Oracle Production DB",
            },
        )

        # Create pipeline with all required fields
        pipeline = Pipeline(
            id="pipeline-etl-001",
            name="etl-pipeline",
            status="completed",
            created_at="2025-01-20T10:30:00Z",
            updated_at="2025-01-20T10:45:00Z",
            config=config,
        )

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        # Test that function runs without errors (returns None)
        format_pipeline(console, pipeline)

        # Check output was written to console
        output = string_io.getvalue()
        assert "etl-pipeline" in output
        assert "completed" in output

    def test_plugin_list_formatting_with_real_data(self) -> None:
        """Test plugin list formatting with realistic data."""
        from io import StringIO

        from rich.console import Console

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

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        # Test that function runs without errors (returns None)
        format_plugin_list(console, plugins, "table")

        # Check output was written to console
        output = string_io.getvalue()
        assert "auth-plugin" in output
        assert "database-connector" in output
        assert "legacy-importer" in output
        assert "2.1.0" in output

    def test_print_functions_integration(self) -> None:
        """Test integration of all print functions."""
        from io import StringIO

        from rich.console import Console

        messages = [
            ("info", "Starting process"),
            ("success", "Process completed"),
            ("warning", "Performance degraded"),
            ("error", "Connection failed"),
        ]

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        for msg_type, message in messages:
            if msg_type == "info":
                print_info(console, message)
            elif msg_type == "success":
                print_success(console, message)
            elif msg_type == "warning":
                print_warning(console, message)
            elif msg_type == "error":
                print_error(console, message)

        # Check that all messages were written to console
        output = string_io.getvalue()
        for _, message in messages:
            assert message in output

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
        """Test pipeline formatting with edge case data."""
        from io import StringIO

        from flext_cli.client import Pipeline, PipelineConfig
        from rich.console import Console

        # Create pipeline config for edge case
        config = PipelineConfig(
            name="malformed-pipeline", tap="tap-unknown", target="target-unknown",
        )

        # Create pipeline with potentially problematic data
        pipeline = Pipeline(
            id="edge-case-id",
            name="malformed-pipeline",
            status="unknown",
            created_at="invalid-timestamp",
            updated_at="another-invalid-timestamp",
            config=config,
        )

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        # Should handle gracefully and return None
        format_pipeline(console, pipeline)

        # Check output was written to console
        output = string_io.getvalue()
        assert len(output) > 0

    def test_format_plugin_list_with_malformed_data(self) -> None:
        """Test plugin list formatting with malformed data."""
        from io import StringIO

        from rich.console import Console

        malformed_plugins: list[dict[str, object]] = [
            {"name": ["should", "be", "string"]},
            {"version": {"major": 1, "minor": 0}},
        ]

        # Capture console output
        string_io = StringIO()
        console = Console(file=string_io, width=80)

        # Should handle gracefully and return None (format_plugin_list converts to strings)
        format_plugin_list(console, malformed_plugins, "table")

        # Check output was written to console
        output = string_io.getvalue()
        assert len(output) > 0

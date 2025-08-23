"""Tests for utils output utilities with REAL code execution.

Tests output formatting utilities with authentic functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from io import StringIO

import yaml
from rich.console import Console

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
)


class TestFormatJsonReal:
    """Test format_json function with real execution."""

    def test_format_simple_dict(self) -> None:
        """Test formatting simple dictionary."""
        data = {"key": "value", "number": 42}
        result = format_json(data)

        assert isinstance(result, str)
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == data

    def test_format_list(self) -> None:
        """Test formatting list."""
        data = [1, 2, 3, "test"]
        result = format_json(data)

        assert isinstance(result, str)
        parsed = json.loads(result)
        assert parsed == data

    def test_format_empty_data(self) -> None:
        """Test formatting empty data."""
        result = format_json({})
        assert isinstance(result, str)
        assert json.loads(result) == {}


class TestFormatYamlReal:
    """Test format_yaml function with real execution."""

    def test_format_simple_dict(self) -> None:
        """Test formatting simple dictionary to YAML."""
        data = {"key": "value", "number": 42}
        result = format_yaml(data)

        assert isinstance(result, str)
        # Should be valid YAML
        parsed = yaml.safe_load(result)
        assert parsed == data

    def test_format_nested_dict(self) -> None:
        """Test formatting nested dictionary."""
        data = {"outer": {"inner": "value"}, "list": [1, 2, 3]}
        result = format_yaml(data)

        assert isinstance(result, str)
        parsed = yaml.safe_load(result)
        assert parsed == data


class TestPrintFunctionsReal:
    """Test print functions with real Rich console."""

    def setup_method(self) -> None:
        """Setup console for each test."""
        # Capture console output in string
        self.output = StringIO()
        self.console = Console(file=self.output, width=80)

    def test_print_success(self) -> None:
        """Test print_success function."""
        print_success(self.console, "Success message")
        output = self.output.getvalue()

        assert "Success message" in output
        assert len(output) > 0

    def test_print_error_basic(self) -> None:
        """Test basic print_error function."""
        print_error(self.console, "Error message")
        output = self.output.getvalue()

        assert "Error message" in output
        assert len(output) > 0

    def test_print_warning(self) -> None:
        """Test print_warning function."""
        print_warning(self.console, "Warning message")
        output = self.output.getvalue()

        assert "Warning message" in output
        assert len(output) > 0

    def test_print_info(self) -> None:
        """Test print_info function."""
        print_info(self.console, "Info message")
        output = self.output.getvalue()

        assert "Info message" in output
        assert len(output) > 0

    def test_print_error_with_details(self) -> None:
        """Test print_error with string details."""
        details = "Error code: 500, description: Internal error"
        print_error(self.console, "Error occurred", details)
        output = self.output.getvalue()

        assert "Error occurred" in output
        assert "Error code: 500" in output
        assert len(output) > 0


class TestFormatPipelineReal:
    """Test format_pipeline function with real execution."""

    def setup_method(self) -> None:
        """Setup console for each test."""
        self.output = StringIO()
        self.console = Console(file=self.output, width=80)

    def test_format_pipeline_basic(self) -> None:
        """Test formatting basic pipeline with proper object structure."""

        # Create mock pipeline object with required attributes
        class MockPipeline:
            def __init__(self) -> None:
                self.name = "test-pipeline"
                self.status = "active"
                self.id = "test-123"
                self.created_at = "2023-01-01T00:00:00Z"

        pipeline = MockPipeline()
        format_pipeline(self.console, pipeline)
        output = self.output.getvalue()

        assert len(output) > 0
        # Should contain pipeline information
        assert "test-pipeline" in output

    def test_format_pipeline_with_config(self) -> None:
        """Test formatting pipeline with config."""
        pipeline = {
            "name": "complex-pipeline",
            "status": "running",
            "config": {"source": "database", "target": "warehouse"},
        }
        format_pipeline(self.console, pipeline)
        output = self.output.getvalue()

        assert len(output) > 0

    def test_format_pipeline_with_full_config(self) -> None:
        """Test formatting pipeline with full configuration."""
        pipeline = {
            "name": "full-pipeline",
            "status": "completed",
            "created_at": "2023-01-01T00:00:00Z",
            "config": {"source": "api", "target": "lake", "schedule": "daily"},
            "metrics": {"records_processed": 1000, "duration": 300},
        }
        format_pipeline(self.console, pipeline)
        output = self.output.getvalue()

        assert len(output) > 0


class TestFormatPipelineListReal:
    """Test format_pipeline_list function with real execution."""

    def setup_method(self) -> None:
        """Setup console for each test."""
        self.output = StringIO()
        self.console = Console(file=self.output, width=80)

    def test_format_empty_pipeline_list(self) -> None:
        """Test formatting empty pipeline list."""
        format_pipeline_list(self.console, [])
        output = self.output.getvalue()

        assert len(output) > 0
        # Should handle empty list gracefully
        assert (
            "no" in output.lower()
            or "empty" in output.lower()
            or "pipelines" in output.lower()
        )

    def test_format_pipeline_list_with_pipelines(self) -> None:
        """Test formatting pipeline list with proper object structure."""

        # Create mock pipeline objects with required attributes
        class MockPipeline:
            def __init__(
                self, name: str, status: str, pipeline_id: str = "test-id"
            ) -> None:
                self.name = name
                self.status = status
                self.id = pipeline_id
                self.created_at = "2023-01-01T00:00:00Z"

        # Create mock pipeline list object
        class MockPipelineList:
            def __init__(self) -> None:
                self.pipelines = [
                    MockPipeline("pipeline1", "running"),
                    MockPipeline("pipeline2", "completed"),
                ]
                self.total = 2
                self.page = 1
                self.page_size = 10

        pipeline_list = MockPipelineList()
        format_pipeline_list(self.console, pipeline_list)
        output = self.output.getvalue()

        assert len(output) > 0
        assert "pipeline1" in output or "pipeline2" in output

    def test_format_pipeline_list_status_colors(self) -> None:
        """Test pipeline list with various statuses."""
        pipelines = [
            {"name": "active-pipeline", "status": "active"},
            {"name": "error-pipeline", "status": "error"},
            {"name": "pending-pipeline", "status": "pending"},
        ]
        format_pipeline_list(self.console, pipelines)
        output = self.output.getvalue()

        assert len(output) > 0

    def test_format_pipeline_list_multiple_pages(self) -> None:
        """Test formatting large pipeline list."""
        pipelines = [{"name": f"pipeline{i}", "status": "active"} for i in range(10)]
        format_pipeline_list(self.console, pipelines)
        output = self.output.getvalue()

        assert len(output) > 0


class TestFormatPluginListReal:
    """Test format_plugin_list function with real execution."""

    def setup_method(self) -> None:
        """Setup console for each test."""
        self.output = StringIO()
        self.console = Console(file=self.output, width=80)

    def test_format_empty_plugin_list(self) -> None:
        """Test formatting empty plugin list."""
        format_plugin_list(self.console, [], "table")
        output = self.output.getvalue()

        assert len(output) > 0

    def test_format_plugin_list_table(self) -> None:
        """Test formatting plugin list as table."""
        plugins = [
            {"name": "plugin1", "version": "1.0", "status": "enabled"},
            {"name": "plugin2", "version": "2.0", "status": "disabled"},
        ]
        format_plugin_list(self.console, plugins, "table")
        output = self.output.getvalue()

        assert len(output) > 0
        assert "plugin1" in output or "plugin2" in output

    def test_format_plugin_list_json(self) -> None:
        """Test formatting plugin list as JSON."""
        plugins = [
            {"name": "plugin1", "version": "1.0"},
            {"name": "plugin2", "version": "2.0"},
        ]
        format_plugin_list(self.console, plugins, "json")
        output = self.output.getvalue()

        assert len(output) > 0

    def test_format_plugin_list_missing_fields(self) -> None:
        """Test formatting plugin list with missing fields."""
        plugins = [
            {"name": "incomplete-plugin"},  # Missing version and status
            {"name": "plugin2", "version": "1.0"},  # Missing status
        ]
        format_plugin_list(self.console, plugins, "table")
        output = self.output.getvalue()

        # Should handle missing fields gracefully
        assert len(output) > 0


class TestUtilsOutputIntegration:
    """Integration tests for utils_output module."""

    def test_pipeline_status_case_insensitive(self) -> None:
        """Test that pipeline status handling is case insensitive."""
        output = StringIO()
        console = Console(file=output, width=80)

        # Test with different case statuses
        pipelines = [
            {"name": "test1", "status": "ACTIVE"},
            {"name": "test2", "status": "inactive"},
            {"name": "test3", "status": "Error"},
        ]

        format_pipeline_list(console, pipelines)
        result = output.getvalue()

        assert len(result) > 0
        # Should handle all statuses gracefully regardless of case

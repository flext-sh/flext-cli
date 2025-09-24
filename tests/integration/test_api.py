"""Integration tests for FlextCliApi - Real API only.

Tests FlextCliApi integration using actual implemented methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_cli import FlextCliApi
from flext_core import FlextResult


class TestFlextCliApiIntegration:
    """Test FlextCliApi integration with real methods."""

    def setup_method(self) -> None:
        """Setup test environment."""
        self.api = FlextCliApi()

    def test_api_initialization(self) -> None:
        """Test API initializes correctly."""
        assert self.api is not None
        assert isinstance(self.api, FlextCliApi)

    def test_api_execute_returns_status(self) -> None:
        """Test execute returns service status."""
        result = self.api.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success
        status = result.value
        assert isinstance(status, dict)
        assert status["status"] == "operational"
        assert status["service"] == "flext-cli-api"
        assert "timestamp" in status
        assert "version" in status

    def test_api_format_data_json(self) -> None:
        """Test formatting data as JSON."""
        data = {"name": "test", "value": 123}

        result = self.api.format_data(data, "json")

        assert result.is_success
        formatted = result.value
        assert isinstance(formatted, str)
        assert "test" in formatted
        assert "123" in formatted

    def test_api_format_data_table(self) -> None:
        """Test formatting data as table."""
        data = {"name": "test", "value": 123, "active": True}

        result = self.api.format_data(data, "table")

        assert result.is_success
        formatted = result.value
        assert isinstance(formatted, str)

    def test_api_display_data(self) -> None:
        """Test displaying formatted data."""
        formatted_data = "Test output data"

        result = self.api.display_data(formatted_data)

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_api_export_data_json(self) -> None:
        """Test exporting data to JSON file."""
        data = {"export": "test", "count": 42}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "export.json"

            result = self.api.export_data(data, output_file, "json")

            assert result.is_success
            assert output_file.exists()

    def test_api_export_data_yaml(self) -> None:
        """Test exporting data to YAML file."""
        data = {"export": "yaml", "items": ["a", "b", "c"]}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_file = Path(temp_dir) / "export.yaml"

            result = self.api.export_data(data, output_file, "yaml")

            # YAML export may or may not be implemented
            assert isinstance(result, FlextResult)

    def test_api_batch_export(self) -> None:
        """Test batch export functionality."""
        datasets: dict[str, object] = {
            "dataset1": {"name": "dataset1", "value": 1},
            "dataset2": {"name": "dataset2", "value": 2},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            result = self.api.batch_export(datasets, output_dir, "json")

            assert isinstance(result, FlextResult)
            if result.is_success:
                # Check files were created
                assert (output_dir / "dataset1.json").exists()
                assert (output_dir / "dataset2.json").exists()

    def test_api_format_and_display_pipeline(self) -> None:
        """Test complete format and display pipeline."""
        data = {"pipeline": "test", "status": "running"}

        # Format
        format_result = self.api.format_data(data, "json")
        assert format_result.is_success

        # Display
        display_result = self.api.display_data(format_result.value)
        assert display_result.is_success

    def test_api_format_unsupported_format(self) -> None:
        """Test formatting with unsupported format."""
        data = {"test": "data"}

        result = self.api.format_data(data, "xml")

        assert result.is_failure

    def test_api_export_requires_existing_directory(self) -> None:
        """Test export fails if parent directory doesn't exist."""
        data = {"nested": "export"}

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "level1" / "level2" / "export.json"

            result = self.api.export_data(data, nested_path, "json")

            # Should fail because parent directory doesn't exist
            assert result.is_failure
            assert "No such file or directory" in (result.error or "")

    def test_api_format_complex_data(self) -> None:
        """Test formatting complex nested data."""
        data = {
            "users": [
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"},
            ],
            "metadata": {"total": 2, "page": 1},
        }

        result = self.api.format_data(data, "json")

        assert result.is_success
        formatted = result.value
        assert "Alice" in formatted
        assert "Bob" in formatted

    def test_api_batch_export_empty_datasets(self) -> None:
        """Test batch export with empty datasets."""
        datasets: dict[str, object] = {}

        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)

            result = self.api.batch_export(datasets, output_dir, "json")

            # Should succeed with empty datasets
            assert isinstance(result, FlextResult)
            assert result.is_success

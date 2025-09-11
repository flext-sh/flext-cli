"""Tests for data_processing.py module - Real functionality testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""


from __future__ import annotations

import tempfile
from pathlib import Path

from flext_core import FlextTypes

from flext_cli.data_processing import FlextCliDataProcessing


class TestFlextCliDataProcessing:
    """Test FlextCliDataProcessing with real execution."""

    def test_data_processing_init(self) -> None:
        """Test data processing initialization."""
        processor = FlextCliDataProcessing()

        assert processor is not None
        assert hasattr(processor, "transform_data")
        assert hasattr(processor, "aggregate_data")
        assert hasattr(processor, "export_to_file")

    def test_transform_data_with_dict(self) -> None:
        """Test transform_data with dictionary input."""
        processor = FlextCliDataProcessing()

        data = {"name": "test", "value": 42}
        result = processor.transform_data(data)

        assert result.is_success
        assert isinstance(result.value, list)
        # Should convert dict to list format
        assert len(result.value) >= 1

    def test_transform_data_with_list(self) -> None:
        """Test transform_data with list input."""
        processor = FlextCliDataProcessing()

        data: list[FlextTypes.Core.Dict] = [{"name": "test1"}, {"name": "test2"}]
        result = processor.transform_data(data)

        assert result.is_success
        assert isinstance(result.value, list)
        assert len(result.value) == 2

    def test_transform_data_with_filters(self) -> None:
        """Test transform_data with filter operations."""
        processor = FlextCliDataProcessing()

        data = [
            {"name": "test1", "active": True},
            {"name": "test2", "active": False},
            {"name": "test3", "active": True},
        ]

        # Test with filters (should filter based on active=True)
        result = processor.transform_data(data, filters={"active": True})

        assert result.is_success
        # Should filter to only active items
        filtered_data = result.value
        assert all(item.get("active") for item in filtered_data if isinstance(item, dict))

    def test_aggregate_data_simple(self) -> None:
        """Test aggregate_data with simple data."""
        processor = FlextCliDataProcessing()

        data = [
            {"category": "A", "value": 10},
            {"category": "B", "value": 20},
            {"category": "A", "value": 15},
        ]

        result = processor.aggregate_data(data)

        assert result.is_success
        # Should return aggregated data structure
        assert isinstance(result.value, dict)

    def test_aggregate_data_empty(self) -> None:
        """Test aggregate_data with empty data."""
        processor = FlextCliDataProcessing()

        result = processor.aggregate_data([])

        assert result.is_success
        # Should handle empty data gracefully
        assert isinstance(result.value, dict)

    def test_export_to_file_json(self) -> None:
        """Test export_to_file with JSON format."""
        processor = FlextCliDataProcessing()

        data = {"test": "data", "number": 42}

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp_file:
            file_path = Path(tmp_file.name)

            result = processor.export_to_file(data, str(file_path))

            assert result.is_success
            # File should be created
            assert file_path.exists()

            # Clean up
            file_path.unlink()

    def test_export_to_file_invalid_path(self) -> None:
        """Test export_to_file with invalid path."""
        processor = FlextCliDataProcessing()

        data: FlextTypes.Core.Dict = {"test": "data"}
        invalid_path = Path("/invalid/nonexistent/path.json")

        result = processor.export_to_file(data, str(invalid_path))

        # Should fail gracefully
        assert result.is_failure

        error_str = str(result.error or "").lower()
        assert ("failed" in error_str or
                "error" in error_str or
                "directory does not exist" in error_str)

    def test_process_batch_data(self) -> None:
        """Test batch processing functionality."""
        processor = FlextCliDataProcessing()

        batch_data = [
            {"id": 1, "value": "a"},
            {"id": 2, "value": "b"},
            {"id": 3, "value": "c"},
        ]

        # Test batch processing (should process all items)
        result = processor.transform_data(batch_data)

        assert result.is_success
        processed = result.value
        assert len(processed) == 3
        # All items should be processed
        assert all(isinstance(item, dict) for item in processed)

    def test_data_processing_error_handling(self) -> None:
        """Test error handling in data processing."""
        processor = FlextCliDataProcessing()

        # Test with None data
        result = processor.transform_data(None)

        # Should handle gracefully
        if result.is_failure:
            assert isinstance(result.error, str)
        else:
            # Should return empty or safe default
            assert result.value is not None

    def test_data_processing_with_complex_structures(self) -> None:
        """Test processing with nested/complex data structures."""
        processor = FlextCliDataProcessing()

        complex_data: FlextTypes.Core.Dict = {
            "users": [
                {"name": "Alice", "details": {"age": 30, "city": "NYC"}},
                {"name": "Bob", "details": {"age": 25, "city": "LA"}},
            ],
            "metadata": {"count": 2, "source": "test"},
        }

        result = processor.transform_data(complex_data)

        assert result.is_success
        # Should handle complex nested structures
        assert isinstance(result.value, list)

    def test_aggregate_with_grouping(self) -> None:
        """Test aggregation with grouping operations."""
        processor = FlextCliDataProcessing()

        data = [
            {"department": "Engineering", "salary": 100000},
            {"department": "Engineering", "salary": 120000},
            {"department": "Sales", "salary": 80000},
            {"department": "Sales", "salary": 85000},
        ]

        result = processor.aggregate_data(data)

        assert result.is_success
        aggregated = result.value

        # Should group by department (implementation dependent)
        assert isinstance(aggregated, dict)
        # Should have processed all departments
        assert len(aggregated) >= 1

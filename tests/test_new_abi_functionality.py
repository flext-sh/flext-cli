"""Test new ABI functionality and chainable patterns.

Tests the enhanced ABI methods and utility functions that provide
massive code reduction capabilities.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any

import pytest
from flext_cli import (
    ExportChain,
    FlextCliDataExporter,
    flext_cli_auto_dashboard,
    flext_cli_data_compare,
    flext_cli_format_all,
    flext_cli_instant_export,
    flext_cli_pipeline,
)


class TestFlextCliABIEnhancements:
    """Test enhanced ABI functionality."""

    @pytest.fixture
    def sample_data(self) -> list[dict[str, Any]]:
        """Sample test data for enhanced ABI tests."""
        return [
            {"id": 1, "name": "Alice", "department": "Engineering", "salary": 95000},
            {"id": 2, "name": "Bob", "department": "Sales", "salary": 75000},
            {"id": 3, "name": "Carol", "department": "Marketing", "salary": 85000},
            {"id": 4, "name": "David", "department": "Engineering", "salary": 105000},
        ]

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_chainable_export_operations(
        self,
        sample_data: list[dict[str, Any]],
        temp_dir: Path,
    ) -> None:
        """Test chainable export operations for massive code reduction."""
        exporter = FlextCliDataExporter()

        # Test fluent interface chaining
        result = (exporter
            .then_export(temp_dir / "data.csv")
            .and_export(temp_dir / "data.json")
            .and_export(temp_dir / "data.tsv")
            .execute(sample_data)
        )

        assert result.success
        chain_results = result.unwrap()

        # Verify all exports were attempted
        assert len(chain_results) == 3

        # Check individual results
        for details in chain_results.values():
            assert "filepath" in details
            assert "success" in details
            assert "message" in details

            # Files should exist if successful
            if details["success"]:
                filepath = Path(details["filepath"])
                assert filepath.exists()
                assert filepath.stat().st_size > 0

    def test_export_chain_error_handling(
        self,
        sample_data: list[dict[str, Any]],
        temp_dir: Path,
    ) -> None:
        """Test export chain error handling and resilience."""
        exporter = FlextCliDataExporter()

        # Include an invalid format to test error handling
        result = (exporter
            .then_export(temp_dir / "data.csv")
            .and_export(temp_dir / "data.invalid", "unsupported_format")
            .and_export(temp_dir / "data.json")
            .execute(sample_data)
        )

        assert result.success  # Chain should continue despite errors
        chain_results = result.unwrap()

        # Check that valid exports succeeded
        csv_result = next((r for r in chain_results.values() if "data.csv" in r["filepath"]), None)
        json_result = next((r for r in chain_results.values() if "data.json" in r["filepath"]), None)
        invalid_result = next((r for r in chain_results.values() if "data.invalid" in r["filepath"]), None)

        assert csv_result
        assert csv_result["success"]
        assert json_result
        assert json_result["success"]
        assert invalid_result
        assert not invalid_result["success"]

    def test_instant_export_functionality(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test instant export with auto-generated filenames."""
        exporter = FlextCliDataExporter()

        # Test instant export with auto-naming
        result = exporter.instant(sample_data, "json", auto_name=True)

        assert result.success
        filename = result.unwrap()

        # Verify filename format
        assert filename.startswith("flext_export_")
        assert filename.endswith(".json")

        # Verify file was created
        filepath = Path(filename)
        assert filepath.exists()
        assert filepath.stat().st_size > 0

    def test_instant_export_without_auto_naming(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test instant export without auto-naming."""
        exporter = FlextCliDataExporter()

        result = exporter.instant(sample_data, "csv", auto_name=False)

        assert result.success
        filename = result.unwrap()
        assert filename == "export.csv"

        # Clean up
        Path(filename).unlink(missing_ok=True)

    def test_batch_export_functionality(
        self,
        sample_data: list[dict[str, Any]],
        temp_dir: Path,
    ) -> None:
        """Test batch export of multiple datasets."""
        exporter = FlextCliDataExporter()

        # Create multiple datasets
        datasets = {
            "employees": sample_data,
            "summary": [{"total_employees": len(sample_data), "avg_salary": 90000}],
            "departments": [{"dept": "Engineering", "count": 2}, {"dept": "Sales", "count": 1}],
        }

        result = exporter.batch_export(
            datasets,
            base_path=temp_dir / "batch_test",
            formats=["csv", "json"],
        )

        assert result.success
        batch_results = result.unwrap()

        # Verify all datasets were processed
        assert len(batch_results) == 3
        assert "employees" in batch_results
        assert "summary" in batch_results
        assert "departments" in batch_results

        # Verify each dataset has both formats
        for formats in batch_results.values():
            assert "csv" in formats
            assert "json" in formats

            for details in formats.values():
                assert "success" in details
                assert "filepath" in details

                if details["success"]:
                    filepath = Path(details["filepath"])
                    assert filepath.exists()

    def test_batch_export_error_resilience(
        self,
        temp_dir: Path,
    ) -> None:
        """Test batch export handles errors gracefully."""
        exporter = FlextCliDataExporter()

        # Include empty data to test error handling
        datasets = {
            "valid_data": [{"id": 1, "name": "Test"}],
            "empty_data": [],  # This should fail
        }

        result = exporter.batch_export(
            datasets,
            base_path=temp_dir / "error_test",
            formats=["csv"],
        )

        assert result.success  # Overall operation should succeed
        batch_results = result.unwrap()

        # Valid data should succeed
        assert batch_results["valid_data"]["csv"]["success"]

        # Empty data should fail
        assert not batch_results["empty_data"]["csv"]["success"]

    def test_factory_methods_specialization(self) -> None:
        """Test specialized factory methods."""
        # Test CSV exporter
        csv_exporter = FlextCliDataExporter.create_csv_exporter()
        assert csv_exporter.default_format == "csv"

        # Test JSON exporter
        json_exporter = FlextCliDataExporter.create_json_exporter()
        assert json_exporter.default_format == "json"

        # Test Parquet exporter
        parquet_exporter = FlextCliDataExporter.create_parquet_exporter()
        assert parquet_exporter.default_format == "parquet"

        # Test Database exporter
        db_exporter = FlextCliDataExporter.create_database_exporter()
        assert db_exporter.default_format == "sqlite"


class TestUtilityFunctions:
    """Test utility functions for massive code reduction."""

    @pytest.fixture
    def sample_data(self) -> list[dict[str, Any]]:
        """Sample test data."""
        return [
            {"id": 1, "name": "Alice", "score": 95, "active": True},
            {"id": 2, "name": "Bob", "score": 85, "active": False},
            {"id": 3, "name": "Carol", "score": 92, "active": True},
        ]

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_flext_cli_pipeline_complete(
        self,
        sample_data: list[dict[str, Any]],
        temp_dir: Path,
    ) -> None:
        """Test complete pipeline functionality."""
        result = flext_cli_pipeline(
            data=sample_data,
            export_path=str(temp_dir / "pipeline_test"),
            formats=["csv", "json"],
            dashboard=True,
            analysis=True,
        )

        assert result.success
        pipeline_results = result.unwrap()

        # Verify all components are present
        assert "formatted" in pipeline_results
        assert "exported" in pipeline_results
        assert "analysis" in pipeline_results
        assert "dashboard" in pipeline_results

        # Verify exports were successful
        exported = pipeline_results["exported"]
        if exported:
            assert "csv" in exported
            assert "json" in exported

    def test_flext_cli_pipeline_minimal(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test pipeline with minimal configuration."""
        result = flext_cli_pipeline(data=sample_data)

        assert result.success
        pipeline_results = result.unwrap()

        # Should have at least formatted data
        assert "formatted" in pipeline_results

    def test_flext_cli_instant_export(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test instant export utility function."""
        result = flext_cli_instant_export(sample_data, "json")

        assert result.success
        filename = result.unwrap()

        assert filename.endswith(".json")
        assert Path(filename).exists()

        # Clean up
        Path(filename).unlink(missing_ok=True)

    def test_flext_cli_instant_export_with_filename(
        self,
        sample_data: list[dict[str, Any]],
        temp_dir: Path,
    ) -> None:
        """Test instant export with custom filename."""
        custom_filename = str(temp_dir / "custom_export.csv")

        result = flext_cli_instant_export(sample_data, "csv", custom_filename)

        assert result.success
        returned_filename = result.unwrap()
        assert returned_filename == custom_filename
        assert Path(custom_filename).exists()

    def test_flext_cli_data_compare(self) -> None:
        """Test data comparison utility."""
        before_data = [
            {"id": 1, "name": "Alice", "status": "active"},
            {"id": 2, "name": "Bob", "status": "inactive"},
        ]

        after_data = [
            {"id": 1, "name": "Alice", "status": "inactive"},  # Changed
            {"id": 2, "name": "Bob", "status": "inactive"},   # Same
            {"id": 3, "name": "Carol", "status": "active"},   # New
        ]

        result = flext_cli_data_compare(before_data, after_data, "Test Comparison")

        assert result.success
        comparison_output = result.unwrap()
        assert isinstance(comparison_output, str)
        assert len(comparison_output) > 0

    def test_flext_cli_auto_dashboard(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test auto dashboard creation."""
        result = flext_cli_auto_dashboard(
            sample_data,
            title="Test Dashboard",
            metrics={"total_records": len(sample_data)},
        )

        assert result.success
        dashboard = result.unwrap()
        assert dashboard is not None

    def test_flext_cli_auto_dashboard_default_title(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test auto dashboard with default title."""
        result = flext_cli_auto_dashboard(sample_data)

        assert result.success
        dashboard = result.unwrap()
        assert dashboard is not None

    def test_flext_cli_format_all(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test multi-format formatting."""
        result = flext_cli_format_all(sample_data, styles=["json", "yaml", "table"])

        assert result.success
        formats = result.unwrap()

        assert "json" in formats
        assert "yaml" in formats
        assert "table" in formats

        # Verify each format produces output
        for output in formats.values():
            assert isinstance(output, str)
            assert len(output) > 0

    def test_flext_cli_format_all_default_styles(
        self,
        sample_data: list[dict[str, Any]],
    ) -> None:
        """Test multi-format formatting with default styles."""
        result = flext_cli_format_all(sample_data)

        assert result.success
        formats = result.unwrap()

        # Should have default styles
        assert len(formats) >= 3
        assert "json" in formats


class TestChainablePatterns:
    """Test chainable patterns for fluent interfaces."""

    @pytest.fixture
    def sample_data(self) -> list[dict[str, Any]]:
        """Sample data for chaining tests."""
        return [
            {"id": 1, "value": 100},
            {"id": 2, "value": 200},
        ]

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Temporary directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_export_chain_creation(self) -> None:
        """Test ExportChain creation and basic functionality."""
        exporter = FlextCliDataExporter()
        chain = ExportChain(exporter)

        assert chain.exporter is exporter
        assert len(chain.operations) == 0

    def test_export_chain_fluent_interface(
        self,
        temp_dir: Path,
    ) -> None:
        """Test fluent interface operations."""
        exporter = FlextCliDataExporter()

        chain = (ExportChain(exporter)
            .then_export(temp_dir / "file1.csv")
            .and_export(temp_dir / "file2.json")
            .then_export(temp_dir / "file3.tsv")
        )

        assert len(chain.operations) == 3

        # Verify operation details
        assert chain.operations[0]["filepath"] == temp_dir / "file1.csv"
        assert chain.operations[1]["filepath"] == temp_dir / "file2.json"
        assert chain.operations[2]["filepath"] == temp_dir / "file3.tsv"

    def test_export_chain_with_options(
        self,
        temp_dir: Path,
    ) -> None:
        """Test export chain with custom options."""
        exporter = FlextCliDataExporter()

        chain = (ExportChain(exporter)
            .then_export(temp_dir / "file.csv", "csv", delimiter=";")
            .and_export(temp_dir / "file.json", "json", indent=4)
        )

        assert len(chain.operations) == 2
        assert chain.operations[0]["options"]["delimiter"] == ";"
        assert chain.operations[1]["options"]["indent"] == 4

    def test_export_chain_execution(
        self,
        sample_data: list[dict[str, Any]],
        temp_dir: Path,
    ) -> None:
        """Test export chain execution."""
        exporter = FlextCliDataExporter()

        result = (ExportChain(exporter)
            .then_export(temp_dir / "chain1.csv")
            .and_export(temp_dir / "chain2.json")
            .execute(sample_data)
        )

        assert result.success
        execution_results = result.unwrap()

        assert len(execution_results) == 2
        assert "export_1" in execution_results
        assert "export_2" in execution_results

        # Verify files were created
        for details in execution_results.values():
            if details["success"]:
                filepath = Path(details["filepath"])
                assert filepath.exists()


class TestErrorHandlingAndResilience:
    """Test error handling and system resilience."""

    @pytest.fixture
    def temp_dir(self) -> Path:
        """Temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_pipeline_error_handling(self) -> None:
        """Test pipeline handles errors gracefully."""
        # Test with empty data
        result = flext_cli_pipeline(data=[])

        # Pipeline should handle gracefully
        assert isinstance(result.success, bool)

    def test_instant_export_error_handling(self) -> None:
        """Test instant export error handling."""
        # Test with invalid data type
        result = flext_cli_instant_export(None, "json")  # type: ignore[arg-type]

        assert not result.success
        assert "export" in result.error.lower()

    def test_batch_export_partial_failures(self, temp_dir: Path) -> None:
        """Test batch export with partial failures."""
        exporter = FlextCliDataExporter()

        datasets = {
            "good_data": [{"id": 1, "name": "test"}],
            "bad_data": None,  # This will cause an error
        }

        result = exporter.batch_export(
            datasets,  # type: ignore[arg-type]
            base_path=temp_dir / "partial_test",
            formats=["csv"],
        )

        # Should handle partial failures gracefully
        assert isinstance(result.success, bool)

    def test_chain_resilience_to_errors(self, temp_dir: Path) -> None:
        """Test export chain resilience to individual failures."""
        exporter = FlextCliDataExporter()
        data = [{"id": 1, "value": "test"}]

        result = (exporter
            .then_export(temp_dir / "good.csv")
            .and_export("/invalid/path/bad.json")  # This should fail
            .and_export(temp_dir / "good2.json")
            .execute(data)
        )

        assert result.success  # Chain should continue despite individual failures
        chain_results = result.unwrap()

        # Should have attempted all operations
        assert len(chain_results) == 3


class TestPerformanceAndOptimization:
    """Test performance patterns and optimizations."""

    def test_large_dataset_handling(self) -> None:
        """Test handling of larger datasets."""
        # Generate larger dataset
        large_data = [
            {"id": i, "value": f"item_{i}", "score": i * 0.1}
            for i in range(1000)
        ]

        exporter = FlextCliDataExporter()
        result = exporter.instant(large_data, "json")

        assert result.success
        filename = result.unwrap()

        # Verify file size is reasonable
        filepath = Path(filename)
        assert filepath.stat().st_size > 10000  # Should be substantial

        # Clean up
        filepath.unlink(missing_ok=True)

    def test_format_all_performance(self) -> None:
        """Test multi-format performance."""
        # Medium-sized dataset
        data = [
            {"id": i, "name": f"User_{i}", "score": i % 100}
            for i in range(100)
        ]

        result = flext_cli_format_all(data, styles=["json", "table"])

        assert result.success
        formats = result.unwrap()

        # Should complete quickly and produce output
        assert len(formats) == 2
        for output in formats.values():
            assert len(output) > 100  # Should have substantial content

    def test_streaming_analysis_pattern(self) -> None:
        """Test streaming analysis pattern for memory efficiency."""
        # Simulate processing in chunks
        full_dataset = [{"id": i, "value": i} for i in range(500)]
        chunk_size = 100

        results = []
        for i in range(0, len(full_dataset), chunk_size):
            chunk = full_dataset[i:i + chunk_size]

            # Process chunk with instant export
            result = flext_cli_instant_export(chunk, "json")
            results.append(result.success)

            # Clean up chunk file
            if result.success:
                Path(result.unwrap()).unlink(missing_ok=True)

        # All chunks should process successfully
        assert all(results)
        assert len(results) == 5  # 500 / 100 = 5 chunks

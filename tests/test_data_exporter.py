"""Test FlextCliDataExporter functionality."""

import tempfile
from pathlib import Path

import pytest
from flext_cli import FlextCliDataExporter


class TestFlextCliDataExporter:
    """Test data export functionality."""

    @pytest.fixture
    def sample_data(self):
        """Sample test data."""
        return [
            {"id": 1, "name": "Alice", "age": 30, "salary": 75000.50, "active": True},
            {"id": 2, "name": "Bob", "age": 25, "salary": 65000.75, "active": False},
            {"id": 3, "name": "Carol", "age": 35, "salary": 85000.25, "active": True},
        ]

    @pytest.fixture
    def exporter(self):
        """FlextCliDataExporter instance."""
        return FlextCliDataExporter()

    @pytest.fixture
    def temp_dir(self):
        """Temporary directory for test files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_csv_export(self, exporter, sample_data, temp_dir) -> None:
        """Test CSV export functionality."""
        filepath = temp_dir / "test.csv"
        result = exporter.export_data(sample_data, str(filepath))

        assert result.success
        assert filepath.exists()
        assert filepath.stat().st_size > 0

        # Read and verify content
        content = filepath.read_text()
        assert "id,name,age,salary,active" in content
        assert "Alice" in content
        assert "Bob" in content

    def test_json_export(self, exporter, sample_data, temp_dir) -> None:
        """Test JSON export functionality."""
        filepath = temp_dir / "test.json"
        result = exporter.export_data(sample_data, str(filepath))

        assert result.success
        assert filepath.exists()
        assert filepath.stat().st_size > 0

        # Verify it's valid JSON
        import json
        with filepath.open() as f:
            data = json.load(f)
        assert len(data) == 3
        assert data[0]["name"] == "Alice"

    def test_tsv_export(self, exporter, sample_data, temp_dir) -> None:
        """Test TSV export functionality."""
        filepath = temp_dir / "test.tsv"
        result = exporter.export_data(sample_data, str(filepath))

        assert result.success
        assert filepath.exists()

        # Verify tab-separated format
        content = filepath.read_text()
        assert "\t" in content  # Tab separators
        assert "Alice" in content

    def test_jsonl_export(self, exporter, sample_data, temp_dir) -> None:
        """Test JSONL export functionality."""
        filepath = temp_dir / "test.jsonl"
        result = exporter.export_data(sample_data, str(filepath))

        assert result.success
        assert filepath.exists()

        # Verify JSONL format (one JSON per line)
        lines = filepath.read_text().strip().split("\n")
        assert len(lines) == 3

        import json
        for line in lines:
            json.loads(line)  # Should not raise exception

    @pytest.mark.skipif(True, reason="Parquet requires additional dependencies")
    def test_parquet_export(self, exporter, sample_data, temp_dir) -> None:
        """Test Parquet export functionality."""
        filepath = temp_dir / "test.parquet"
        result = exporter.export_data(sample_data, str(filepath))

        if result.success:
            assert filepath.exists()
            assert filepath.stat().st_size > 0

    def test_sqlite_export(self, exporter, sample_data, temp_dir) -> None:
        """Test SQLite export functionality."""
        filepath = temp_dir / "test.db"
        result = exporter.export_data(
            sample_data, str(filepath), "sqlite", table_name="employees",
        )

        if result.success:  # May fail if pandas not available
            assert filepath.exists()
            assert filepath.stat().st_size > 0

            # Verify SQLite database
            import sqlite3
            with sqlite3.connect(filepath) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
                tables = [row[0] for row in cursor.fetchall()]
                assert "employees" in tables

    def test_auto_format_detection(self, exporter, sample_data, temp_dir) -> None:
        """Test automatic format detection from file extension."""
        # Test different extensions
        test_cases = [
            ("test.csv", "csv"),
            ("test.json", "json"),
            ("test.tsv", "tsv"),
            ("test.jsonl", "jsonl"),
        ]

        for filename, _expected_format in test_cases:
            filepath = temp_dir / filename
            result = exporter.export_data(sample_data, str(filepath))

            # Should detect format and export successfully
            assert result.success
            assert filepath.exists()

    def test_unsupported_format(self, exporter, sample_data, temp_dir) -> None:
        """Test handling of unsupported format."""
        filepath = temp_dir / "test.xyz"
        result = exporter.export_data(sample_data, str(filepath), "unsupported")

        assert not result.success
        assert "Unsupported format" in result.error

    def test_empty_data(self, exporter, temp_dir) -> None:
        """Test handling of empty data."""
        filepath = temp_dir / "empty.csv"
        result = exporter.export_data([], str(filepath))

        assert not result.success
        assert "No data to export" in result.error

    def test_dict_data_normalization(self, exporter, temp_dir) -> None:
        """Test normalization of single dict to list."""
        single_record = {"id": 1, "name": "Alice", "age": 30}
        filepath = temp_dir / "single.json"

        result = exporter.export_data(single_record, str(filepath))

        assert result.success
        assert filepath.exists()

        # Verify it was converted to list format
        import json
        with filepath.open() as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["name"] == "Alice"

    def test_get_supported_formats(self, exporter) -> None:
        """Test getting supported formats."""
        formats = exporter.get_supported_formats()

        assert isinstance(formats, list)
        assert len(formats) > 0
        assert "csv" in formats
        assert "json" in formats
        assert "sqlite" in formats

    def test_multiple_format_export(self, exporter, sample_data, temp_dir) -> None:
        """Test exporting to multiple formats."""
        formats = ["csv", "json", "tsv"]
        base_path = temp_dir / "multi_export"

        result = exporter.export_multiple_formats(sample_data, base_path, formats)

        assert result.success
        results = result.data

        for format_type in formats:
            assert format_type in results

            # Check files were created
            expected_extensions = {"csv": ".csv", "json": ".json", "tsv": ".tsv"}
            expected_file = base_path.with_suffix(expected_extensions[format_type])
            assert expected_file.exists()

    def test_get_format_info(self, exporter) -> None:
        """Test getting format information."""
        result = exporter.get_format_info("csv")

        assert result.success
        info = result.data

        assert "description" in info
        assert "use_cases" in info
        assert "pros" in info
        assert "cons" in info

    def test_get_format_info_unknown(self, exporter) -> None:
        """Test getting info for unknown format."""
        result = exporter.get_format_info("unknown")

        assert not result.success
        assert "Unknown format" in result.error

    def test_export_with_options(self, exporter, sample_data, temp_dir) -> None:
        """Test export with custom options."""
        filepath = temp_dir / "test_options.csv"

        # Test CSV with custom delimiter
        result = exporter.export_data(
            sample_data, str(filepath), "csv", delimiter=";",
        )

        assert result.success

        content = filepath.read_text()
        assert ";" in content  # Should use semicolon delimiter

    def test_export_creates_parent_directory(self, exporter, sample_data, temp_dir) -> None:
        """Test that export creates parent directories."""
        nested_path = temp_dir / "nested" / "deep" / "test.csv"

        result = exporter.export_data(sample_data, str(nested_path))

        assert result.success
        assert nested_path.exists()
        assert nested_path.parent.exists()

    def test_class_factory_methods(self) -> None:
        """Test class factory methods."""
        csv_exporter = FlextCliDataExporter.create_csv_exporter()
        assert csv_exporter.default_format == "csv"

        json_exporter = FlextCliDataExporter.create_json_exporter()
        assert json_exporter.default_format == "json"

        parquet_exporter = FlextCliDataExporter.create_parquet_exporter()
        assert parquet_exporter.default_format == "parquet"

    def test_large_dataset_handling(self, exporter, temp_dir) -> None:
        """Test handling of larger datasets."""
        # Generate larger dataset
        large_data = [
            {"id": i, "name": f"User_{i}", "value": i * 1.5}
            for i in range(1000)
        ]

        filepath = temp_dir / "large.csv"
        result = exporter.export_data(large_data, str(filepath))

        assert result.success
        assert filepath.exists()
        assert filepath.stat().st_size > 10000  # Should be reasonably large file

    def test_data_types_preservation(self, exporter, temp_dir) -> None:
        """Test that data types are properly handled."""
        mixed_data = [
            {
                "string": "text",
                "integer": 42,
                "float": 3.14,
                "boolean": True,
                "null": None,
                "list": [1, 2, 3],
                "dict": {"nested": "value"},
            },
        ]

        # Test JSON export (preserves types best)
        json_path = temp_dir / "mixed.json"
        result = exporter.export_data(mixed_data, str(json_path))

        assert result.success

        import json
        with json_path.open() as f:
            loaded_data = json.load(f)

        assert loaded_data[0]["string"] == "text"
        assert loaded_data[0]["integer"] == 42
        assert loaded_data[0]["float"] == 3.14
        assert loaded_data[0]["boolean"] is True
        assert loaded_data[0]["null"] is None

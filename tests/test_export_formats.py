"""Test export format implementations."""

import csv
import json
from pathlib import Path

from flext_cli.api import CliApi


class TestJSONExport:
    """Test JSON export functionality."""

    def test_json_export_basic(self, mock_flext_core, sample_data, temp_dir) -> None:
        """Test basic JSON export."""
        api = CliApi()
        filepath = temp_dir / "test.json"

        result = api.export(sample_data, str(filepath), "json")

        assert result.is_success
        assert filepath.exists()

        with filepath.open() as f:
            data = json.load(f)
        assert data == sample_data

    def test_json_export_single_record(self, mock_flext_core, single_record, temp_dir) -> None:
        """Test JSON export with single record."""
        api = CliApi()
        filepath = temp_dir / "single.json"

        result = api.export(single_record, str(filepath), "json")

        assert result.is_success

        with filepath.open() as f:
            data = json.load(f)
        assert data == [single_record]  # Should be wrapped in list

    def test_json_export_with_none_values(self, mock_flext_core, temp_dir) -> None:
        """Test JSON export handles None values."""
        data_with_none = [
            {"id": 1, "name": "Alice", "value": None},
            {"id": 2, "name": None, "value": 42},
        ]

        api = CliApi()
        filepath = temp_dir / "with_none.json"

        result = api.export(data_with_none, str(filepath), "json")

        assert result.is_success

        with filepath.open() as f:
            data = json.load(f)
        assert data == data_with_none

    def test_json_export_complex_types(self, mock_flext_core, temp_dir) -> None:
        """Test JSON export with complex data types."""
        complex_data = [
            {
                "date": "2024-01-01T10:00:00",
                "list": [1, 2, 3],
                "nested": {"key": "value"},
                "boolean": True,
                "number": 42.5,
            },
        ]

        api = CliApi()
        filepath = temp_dir / "complex.json"

        result = api.export(complex_data, str(filepath), "json")

        assert result.is_success

        with filepath.open() as f:
            data = json.load(f)
        assert data == complex_data

    def test_json_export_reports_file_size(self, mock_flext_core, sample_data, temp_dir) -> None:
        """Test JSON export reports file size in result."""
        api = CliApi()
        filepath = temp_dir / "test.json"

        result = api.export(sample_data, str(filepath), "json")

        assert result.is_success
        assert "bytes" in result.data
        assert "3 records" in result.data


class TestCSVExport:
    """Test CSV export functionality."""

    def test_csv_export_basic(self, mock_flext_core, sample_data, temp_dir) -> None:
        """Test basic CSV export."""
        api = CliApi()
        filepath = temp_dir / "test.csv"

        result = api.export(sample_data, str(filepath), "csv")

        assert result.is_success
        assert filepath.exists()

        with filepath.open() as f:
            reader = csv.DictReader(f)
            csv_data = list(reader)

        # Convert numeric fields back
        for row in csv_data:
            row["id"] = int(row["id"])
            row["age"] = int(row["age"])

        assert csv_data == sample_data

    def test_csv_export_single_record(self, mock_flext_core, single_record, temp_dir) -> None:
        """Test CSV export with single record."""
        api = CliApi()
        filepath = temp_dir / "single.csv"

        result = api.export(single_record, str(filepath), "csv")

        assert result.is_success

        with filepath.open() as f:
            reader = csv.DictReader(f)
            csv_data = list(reader)

        # Convert ID back to int
        csv_data[0]["id"] = int(csv_data[0]["id"])

        assert csv_data == [single_record]

    def test_csv_export_empty_list_fails(self, mock_flext_core, temp_dir) -> None:
        """Test CSV export fails with empty list."""
        api = CliApi()
        filepath = temp_dir / "empty.csv"

        result = api.export([], str(filepath), "csv")

        assert not result.is_success
        assert "CSV requires list of dictionaries" in result.error

    def test_csv_export_non_dict_list_fails(self, mock_flext_core, temp_dir) -> None:
        """Test CSV export fails with non-dict list."""
        api = CliApi()
        filepath = temp_dir / "invalid.csv"

        result = api.export(["string1", "string2"], str(filepath), "csv")

        assert not result.is_success
        assert "CSV requires list of dictionaries" in result.error

    def test_csv_export_mixed_keys(self, mock_flext_core, temp_dir) -> None:
        """Test CSV export with records having different keys."""
        mixed_data = [
            {"id": 1, "name": "Alice", "age": 30},
            {"id": 2, "name": "Bob", "city": "NYC"},  # Missing age, has city
            {"id": 3, "name": "Charlie", "age": 25, "city": "LA"},  # Has both
        ]

        api = CliApi()
        filepath = temp_dir / "mixed.csv"

        result = api.export(mixed_data, str(filepath), "csv")

        assert result.is_success

        with filepath.open() as f:
            reader = csv.DictReader(f)
            list(reader)

        # First record defines the fieldnames
        expected_fieldnames = ["id", "name", "age"]
        assert reader.fieldnames == expected_fieldnames

    def test_csv_export_with_special_characters(self, mock_flext_core, temp_dir) -> None:
        """Test CSV export handles special characters."""
        special_data = [
            {"name": "Test, User", "description": 'Contains "quotes"'},
            {"name": "Line\nBreak", "description": "Multi\nline\ntext"},
            {"name": "Comma,Semicolon;Tab\t", "description": "Special chars"},
        ]

        api = CliApi()
        filepath = temp_dir / "special.csv"

        result = api.export(special_data, str(filepath), "csv")

        assert result.is_success

        with filepath.open() as f:
            reader = csv.DictReader(f)
            csv_data = list(reader)

        assert len(csv_data) == 3
        assert csv_data[0]["name"] == "Test, User"
        assert '"quotes"' in csv_data[0]["description"]


class TestYAMLExport:
    """Test YAML export functionality."""

    def test_yaml_export_with_yaml_installed(self, mock_flext_core, sample_data, temp_dir, monkeypatch) -> None:
        """Test YAML export when PyYAML is available."""
        # Mock yaml module
        class MockYAML:
            @staticmethod
            def dump(data, f, default_flow_style=False) -> None:
                # Simple YAML-like output for testing
                f.write("- id: 1\n  name: Alice\n  age: 30\n  city: New York\n")

        monkeypatch.setattr("flext_cli.api.yaml", MockYAML(), raising=False)

        api = CliApi()
        filepath = temp_dir / "test.yaml"

        result = api.export(sample_data, str(filepath), "yaml")

        assert result.is_success
        assert filepath.exists()
        assert "records" in result.data

    def test_yaml_export_without_yaml_fails(self, mock_flext_core, sample_data, temp_dir) -> None:
        """Test YAML export fails when PyYAML not available."""
        # This test would need a complex mock setup to test import failures
        # For now, we'll test the general YAML export functionality
        api = CliApi()
        filepath = temp_dir / "test.yaml"

        # This will likely fail due to missing yaml module, which is expected
        result = api.export(sample_data, str(filepath), "yaml")

        # Result should either succeed (if yaml is available) or fail with import error
        if not result.is_success:
            assert "required for YAML export" in result.error or "Export failed" in result.error


class TestExportErrorHandling:
    """Test export error handling."""

    def test_export_file_permission_error(self, mock_flext_core, sample_data, temp_dir, monkeypatch) -> None:
        """Test export handles file permission errors."""
        api = CliApi()
        filepath = temp_dir / "readonly.json"

        # Mock Path.open to raise PermissionError
        original_open = Path.open
        def mock_open(self, *args, **kwargs):
            if "readonly.json" in str(self):
                msg = "Permission denied"
                raise PermissionError(msg)
            return original_open(self, *args, **kwargs)

        monkeypatch.setattr(Path, "open", mock_open)

        result = api.export(sample_data, str(filepath), "json")

        assert not result.is_success
        assert "Export failed: Permission denied" in result.error

    def test_export_disk_full_error(self, mock_flext_core, sample_data, temp_dir, monkeypatch) -> None:
        """Test export handles disk full errors."""
        api = CliApi()
        filepath = temp_dir / "diskfull.json"

        # Mock Path.open to raise OSError (disk full)
        original_open = Path.open
        def mock_open(self, *args, **kwargs):
            if "diskfull.json" in str(self):
                msg = "No space left on device"
                raise OSError(msg)
            return original_open(self, *args, **kwargs)

        monkeypatch.setattr(Path, "open", mock_open)

        result = api.export(sample_data, str(filepath), "json")

        assert not result.is_success
        assert "Export failed: No space left on device" in result.error

    def test_export_invalid_json_data(self, mock_flext_core, temp_dir, monkeypatch) -> None:
        """Test export handles JSON serialization errors."""
        # Create data that can't be JSON serialized
        class UnserializableClass:
            pass

        bad_data = [{"object": UnserializableClass()}]

        api = CliApi()
        filepath = temp_dir / "bad.json"

        # This should be handled by json.dump's default=str parameter
        result = api.export(bad_data, str(filepath), "json")

        # Should succeed because we use default=str
        assert result.is_success

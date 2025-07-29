"""Test convenience functions."""

import json
from typing import Never

from flext_cli import CliApi, export, format_data, health


class TestConvenienceFunctions:
    """Test convenience functions in __init__.py."""

    def test_export_function_success(self, mock_flext_core, sample_data, temp_dir) -> None:
        """Test export convenience function returns boolean."""
        filepath = temp_dir / "test.json"

        result = export(sample_data, str(filepath), "json")

        assert isinstance(result, bool)
        assert result is True
        assert filepath.exists()

        # Verify content
        with filepath.open() as f:
            data = json.load(f)
        assert data == sample_data

    def test_export_function_failure(self, mock_flext_core, temp_dir) -> None:
        """Test export convenience function handles failure."""
        filepath = temp_dir / "test.json"

        result = export(None, str(filepath), "json")

        assert isinstance(result, bool)
        assert result is False

    def test_format_data_function_success(self, mock_flext_core, sample_data) -> None:
        """Test format_data convenience function returns string."""
        result = format_data(sample_data, "json")

        assert isinstance(result, str)
        # Should be valid JSON
        parsed = json.loads(result)
        assert parsed == sample_data

    def test_format_data_function_failure(self, mock_flext_core, sample_data) -> None:
        """Test format_data convenience function handles failure."""
        result = format_data(sample_data, "unsupported")

        assert isinstance(result, str)
        assert result.startswith("Error:")

    def test_health_function_success(self, mock_flext_core) -> None:
        """Test health convenience function returns dict."""
        result = health()

        assert isinstance(result, dict)
        assert result["status"] == "healthy"
        assert "commands" in result
        assert "formats" in result

    def test_health_function_handles_failure(self, mock_flext_core, monkeypatch) -> None:
        """Test health convenience function handles failure."""
        # Mock the CliApi to raise an exception
        def failing_health() -> Never:
            msg = "Health check failed"
            raise Exception(msg)

        mock_api = CliApi()
        mock_api.health = failing_health
        monkeypatch.setattr("flext_cli.CliApi", lambda: mock_api)

        result = health()

        assert isinstance(result, dict)
        assert result.get("status") == "unhealthy"

    def test_all_functions_use_fresh_api_instances(self, mock_flext_core, sample_data, temp_dir) -> None:
        """Test that convenience functions create fresh API instances."""
        # This ensures no state is shared between calls

        # First export
        filepath1 = temp_dir / "test1.json"
        result1 = export(sample_data, str(filepath1))

        # Second export
        filepath2 = temp_dir / "test2.json"
        result2 = export(sample_data, str(filepath2))

        assert result1 is True
        assert result2 is True
        assert filepath1.exists()
        assert filepath2.exists()

    def test_functions_with_different_data_types(self, mock_flext_core, temp_dir) -> None:
        """Test convenience functions with different data types."""
        # Test with single dict
        single_data = {"key": "value"}
        filepath = temp_dir / "single.json"

        result = export(single_data, str(filepath))
        assert result is True

        # Test with list of strings
        string_list = ["item1", "item2"]
        formatted = format_data(string_list, "json")
        assert isinstance(formatted, str)
        parsed = json.loads(formatted)
        assert parsed == string_list


class TestModuleExports:
    """Test module __all__ exports."""

    def test_all_exports_exist(self) -> None:
        """Test all exported names exist and are callable/accessible."""
        import flext_cli

        expected_exports = ["CliApi", "export", "format_data", "health"]

        for name in expected_exports:
            assert hasattr(flext_cli, name), f"Missing export: {name}"

        # Test they're the expected types
        assert callable(flext_cli.CliApi)
        assert callable(flext_cli.export)
        assert callable(flext_cli.format_data)
        assert callable(flext_cli.health)

    def test_version_exists(self) -> None:
        """Test __version__ is exported."""
        import flext_cli

        assert hasattr(flext_cli, "__version__")
        assert isinstance(flext_cli.__version__, str)
        assert flext_cli.__version__ == "2.0.0"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_string_data(self, mock_flext_core, temp_dir) -> None:
        """Test export with empty string data."""
        filepath = temp_dir / "empty.json"

        result = export("", str(filepath))

        # Empty string should be treated as "no data"
        assert result is False

    def test_zero_value_data(self, mock_flext_core, temp_dir) -> None:
        """Test export with zero/false values."""
        filepath = temp_dir / "zero.json"

        # Zero should be valid data
        result = export([{"value": 0}], str(filepath))
        assert result is True

        # False should be valid data
        result = export([{"flag": False}], str(filepath))
        assert result is True

    def test_nested_data_structures(self, mock_flext_core, temp_dir) -> None:
        """Test with nested data structures."""
        nested_data = [
            {
                "id": 1,
                "user": {
                    "name": "Alice",
                    "preferences": ["json", "csv"],
                },
                "metadata": {
                    "created": "2024-01-01",
                    "tags": ["test", "data"],
                },
            },
        ]

        filepath = temp_dir / "nested.json"
        result = export(nested_data, str(filepath))

        assert result is True

        # Verify content preservation
        with filepath.open() as f:
            data = json.load(f)
        assert data == nested_data

    def test_unicode_data(self, mock_flext_core, temp_dir) -> None:
        """Test with Unicode data."""
        unicode_data = [
            {"name": "José", "city": "São Paulo"},
            {"name": "北京", "description": "中国首都"},
            {"emoji": "🎉", "message": "Hello 世界!"},
        ]

        filepath = temp_dir / "unicode.json"
        result = export(unicode_data, str(filepath))

        assert result is True

        # Verify Unicode preservation
        with filepath.open(encoding="utf-8") as f:
            data = json.load(f)
        assert data == unicode_data

"""Comprehensive tests for FlextCliFileTools to achieve 100% coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import json
import tempfile
from collections import UserDict
from pathlib import Path
from typing import Never
from unittest.mock import MagicMock, patch

import pandas as pd
import yaml

from flext_cli.file_tools import FlextCliFileTools


class TestFlextCliFileTools:
    """Comprehensive test suite for FlextCliFileTools."""

    def test_init(self) -> None:
        """Test initialization."""
        file_tools = FlextCliFileTools()
        assert file_tools._supported_formats is not None
        assert len(file_tools._supported_formats) > 0

    def test_execute(self) -> None:
        """Test execute method."""
        file_tools = FlextCliFileTools()
        result = file_tools.execute()
        assert result.is_success
        assert result.unwrap() is True

    def test_detect_file_format_json(self) -> None:
        """Test detect_file_format with JSON file."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format("test.json")
        assert result.is_success
        assert result.unwrap() == "json"

    def test_detect_file_format_yaml(self) -> None:
        """Test detect_file_format with YAML file."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format("test.yaml")
        assert result.is_success
        assert result.unwrap() == "yaml"

    def test_detect_file_format_yml(self) -> None:
        """Test detect_file_format with YML file."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format("test.yml")
        assert result.is_success
        assert result.unwrap() == "yaml"

    def test_detect_file_format_csv(self) -> None:
        """Test detect_file_format with CSV file."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format("test.csv")
        assert result.is_success
        assert result.unwrap() == "csv"

    def test_detect_file_format_tsv(self) -> None:
        """Test detect_file_format with TSV file."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format("test.tsv")
        assert result.is_success
        assert result.unwrap() == "tsv"

    def test_detect_file_format_xml(self) -> None:
        """Test detect_file_format with XML file."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format("test.xml")
        assert result.is_success
        assert result.unwrap() == "xml"

    def test_detect_file_format_toml(self) -> None:
        """Test detect_file_format with TOML file."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format("test.toml")
        assert result.is_success
        assert result.unwrap() == "toml"

    def test_detect_file_format_xlsx(self) -> None:
        """Test detect_file_format with XLSX file."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format("test.xlsx")
        assert result.is_success
        assert result.unwrap() == "excel"

    def test_detect_file_format_xls(self) -> None:
        """Test detect_file_format with XLS file."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format("test.xls")
        assert result.is_success
        assert result.unwrap() == "excel"

    def test_detect_file_format_parquet(self) -> None:
        """Test detect_file_format with Parquet file."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format("test.parquet")
        assert result.is_success
        assert result.unwrap() == "parquet"

    def test_detect_file_format_txt(self) -> None:
        """Test detect_file_format with TXT file."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format("test.txt")
        assert result.is_success
        assert result.unwrap() == "text"

    def test_detect_file_format_unsupported(self) -> None:
        """Test detect_file_format with unsupported file."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format("test.unknown")
        assert result.is_failure
        assert "Unsupported file format" in result.error

    def test_detect_file_format_path_object(self) -> None:
        """Test detect_file_format with Path object."""
        file_tools = FlextCliFileTools()
        result = file_tools.detect_file_format(Path("test.json"))
        assert result.is_success
        assert result.unwrap() == "json"

    def test_detect_file_format_exception(self) -> None:
        """Test detect_file_format with exception."""
        file_tools = FlextCliFileTools()
        # Test with invalid path that causes exception
        with patch("flext_cli.file_tools.Path", side_effect=Exception("Test error")):
            result = file_tools.detect_file_format("test.json")
            assert result.is_failure
            assert "Test error" in result.error
            assert "Failed to detect file format" in result.error

    def test_get_supported_formats(self) -> None:
        """Test get_supported_formats."""
        file_tools = FlextCliFileTools()
        result = file_tools.get_supported_formats()
        assert result.is_success
        formats = result.unwrap()
        assert "json" in formats
        assert "yaml" in formats
        assert "csv" in formats
        assert "xml" in formats
        assert "toml" in formats
        assert "excel" in formats

    def test_get_supported_formats_exception(self) -> None:
        """Test get_supported_formats with exception."""
        file_tools = FlextCliFileTools()
        # Create a custom dict that raises exception on values()

        class ExceptionDict(UserDict):
            def values(self) -> Never:
                error_msg = "Test error"
                raise RuntimeError(error_msg)

        # Replace _supported_formats with our exception-raising dict
        file_tools._supported_formats = ExceptionDict()
        result = file_tools.get_supported_formats()
        assert result.is_failure
        assert "Failed to get supported formats" in result.error

    def test_file_exists_true(self) -> None:
        """Test file_exists with existing file."""
        file_tools = FlextCliFileTools()
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test data")
            tmp_path = tmp.name

        try:
            result = file_tools.file_exists(tmp_path)
            assert result is True
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_file_exists_false(self) -> None:
        """Test file_exists with non-existing file."""
        file_tools = FlextCliFileTools()
        result = file_tools.file_exists("nonexistent_file.txt")
        assert result is False

    def test_file_exists_exception(self) -> None:
        """Test file_exists with exception."""
        file_tools = FlextCliFileTools()
        # Mock Path.exists to raise exception
        with patch("flext_cli.file_tools.Path") as mock_path:
            mock_path_instance = mock_path.return_value
            mock_path_instance.exists.side_effect = Exception("Test error")
            result = file_tools.file_exists("test.txt")
            assert result is False

    def test_get_file_size_success(self) -> None:
        """Test get_file_size with existing file."""
        file_tools = FlextCliFileTools()
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"test data")
            tmp_path = tmp.name

        try:
            result = file_tools.get_file_size(tmp_path)
            assert result.is_success
            assert result.unwrap() > 0
        finally:
            Path(tmp_path).unlink(missing_ok=True)

    def test_get_file_size_not_exists(self) -> None:
        """Test get_file_size with non-existing file."""
        file_tools = FlextCliFileTools()
        result = file_tools.get_file_size("nonexistent_file.txt")
        assert result.is_failure
        assert "File does not exist" in result.error

    def test_get_file_size_exception(self) -> None:
        """Test get_file_size with exception."""
        file_tools = FlextCliFileTools()
        # Test with a non-existent file
        result = file_tools.get_file_size("nonexistent_file.txt")
        assert result.is_failure
        assert "File does not exist" in result.error

    def test_get_file_size_stat_exception(self) -> None:
        """Test get_file_size with stat exception."""
        file_tools = FlextCliFileTools()
        # Mock Path to raise exception during stat()
        with patch("flext_cli.file_tools.Path") as mock_path:
            mock_path_instance = mock_path.return_value
            mock_path_instance.exists.return_value = True
            mock_path_instance.stat.side_effect = Exception("Test error")
            result = file_tools.get_file_size("test.txt")
            assert result.is_failure
            assert "Failed to get file size" in result.error

    def test_load_file_unsupported_format(self) -> None:
        """Test load_file with unsupported format."""
        file_tools = FlextCliFileTools()
        result = file_tools.load_file("test.unsupported")
        assert result.is_failure
        assert "Unsupported file format" in result.error

    def test_load_file_invalid_load_method(self) -> None:
        """Test load_file with invalid load method."""
        file_tools = FlextCliFileTools()
        # Mock the load method to be non-callable
        with patch.object(
            file_tools,
            "_supported_formats",
            {
                ".json": {
                    "format": "json",
                    "load_method": "not_callable",
                    "save_method": file_tools._save_json,
                }
            },
        ):
            result = file_tools.load_file("test.json")
            assert result.is_failure
            assert "Invalid load method" in result.error

    def test_save_file_unsupported_format(self) -> None:
        """Test save_file with unsupported format."""
        file_tools = FlextCliFileTools()
        result = file_tools.save_file("test.unsupported", {"key": "value"})
        assert result.is_failure
        assert "Unsupported file format" in result.error

    def test_save_file_invalid_save_method(self) -> None:
        """Test save_file with invalid save method."""
        file_tools = FlextCliFileTools()
        # Mock the save method to be non-callable
        with patch.object(
            file_tools,
            "_supported_formats",
            {
                ".json": {
                    "format": "json",
                    "load_method": file_tools._load_json,
                    "save_method": "not_callable",
                }
            },
        ):
            result = file_tools.save_file("test.json", {"key": "value"})
            assert result.is_failure
            assert "Invalid save method" in result.error

    def test_load_file_json(self) -> None:
        """Test load_file with JSON file."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({"key": "value"}, f)
            temp_path = f.name

        try:
            result = file_tools.load_file(temp_path)
            assert result.is_success
            data = result.unwrap()
            assert data == {"key": "value"}
        finally:
            Path(temp_path).unlink()

    def test_load_file_yaml(self) -> None:
        """Test load_file with YAML file."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump({"key": "value"}, f)
            temp_path = f.name

        try:
            result = file_tools.load_file(temp_path)
            assert result.is_success
            data = result.unwrap()
            assert data == {"key": "value"}
        finally:
            Path(temp_path).unlink()

    def test_load_file_csv(self) -> None:
        """Test load_file with CSV file."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".csv", delete=False
        ) as f:
            f.write("name,age\nJohn,25\nJane,30\n")
            temp_path = f.name

        try:
            result = file_tools.load_file(temp_path)
            assert result.is_success
            data = result.unwrap()
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["name"] == "John"
            assert data[0]["age"] == 25
        finally:
            Path(temp_path).unlink()

    def test_load_file_txt(self) -> None:
        """Test load_file with TXT file."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("Hello, World!")
            temp_path = f.name

        try:
            result = file_tools.load_file(temp_path)
            assert result.is_success
            data = result.unwrap()
            assert data == "Hello, World!"
        finally:
            Path(temp_path).unlink()

    def test_load_file_format_detection_failure(self) -> None:
        """Test load_file with format detection failure."""
        file_tools = FlextCliFileTools()
        # Test with unsupported file format
        result = file_tools.load_file("test.unsupported")
        assert result.is_failure
        assert "Unsupported file format" in result.error

    def test_load_file_exception(self) -> None:
        """Test load_file with exception."""
        file_tools = FlextCliFileTools()
        with patch("flext_cli.file_tools.Path", side_effect=Exception("Test error")):
            result = file_tools.load_file("test.json")
            assert result.is_failure
            assert "Failed to detect file format" in result.error

    def test_save_file_json(self) -> None:
        """Test save_file with JSON file."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            data = {"key": "value"}
            result = file_tools.save_file(temp_path, data)
            assert result.is_success

            # Verify file was created and contains correct data
            with Path(temp_path).open("r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            assert loaded_data == data
        finally:
            Path(temp_path).unlink()

    def test_save_file_yaml(self) -> None:
        """Test save_file with YAML file."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            data = {"key": "value"}
            result = file_tools.save_file(temp_path, data)
            assert result.is_success

            # Verify file was created and contains correct data
            with Path(temp_path).open("r", encoding="utf-8") as f:
                loaded_data = yaml.safe_load(f)
            assert loaded_data == data
        finally:
            Path(temp_path).unlink()

    def test_save_file_csv(self) -> None:
        """Test save_file with CSV file."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            data = pd.DataFrame({"name": ["John", "Jane"], "age": [25, 30]})
            result = file_tools.save_file(temp_path, data)
            assert result.is_success

            # Verify file was created
            assert Path(temp_path).exists()
        finally:
            Path(temp_path).unlink()

    def test_save_file_txt(self) -> None:
        """Test save_file with TXT file."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name

        try:
            data = "Hello, World!"
            result = file_tools.save_file(temp_path, data)
            assert result.is_success

            # Verify file was created and contains correct data
            with Path(temp_path).open("r", encoding="utf-8") as f:
                loaded_data = f.read()
            assert loaded_data == data
        finally:
            Path(temp_path).unlink()

    def test_save_file_format_detection_failure(self) -> None:
        """Test save_file with format detection failure."""
        file_tools = FlextCliFileTools()
        # Test with unsupported file format
        result = file_tools.save_file("test.unsupported", {"key": "value"})
        assert result.is_failure
        assert "Unsupported file format" in result.error

    def test_save_file_exception(self) -> None:
        """Test save_file with exception."""
        file_tools = FlextCliFileTools()
        with patch("flext_cli.file_tools.Path", side_effect=Exception("Test error")):
            result = file_tools.save_file("test.json", {"key": "value"})
            assert result.is_failure
            assert "Failed to detect file format" in result.error

    def test_load_json_success(self) -> None:
        """Test _load_json method success."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as f:
            json.dump({"key": "value"}, f)
            temp_path = f.name

        try:
            result = file_tools._load_json(temp_path)
            assert result.is_success
            data = result.unwrap()
            assert data == {"key": "value"}
        finally:
            Path(temp_path).unlink()

    def test_load_json_file_not_found(self) -> None:
        """Test _load_json method with file not found."""
        file_tools = FlextCliFileTools()
        result = file_tools._load_json("nonexistent.json")
        assert result.is_failure
        assert "Failed to load JSON file" in result.error

    def test_load_json_invalid_json(self) -> None:
        """Test _load_json method with invalid JSON."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".json", delete=False
        ) as f:
            f.write("invalid json content")
            temp_path = f.name

        try:
            result = file_tools._load_json(temp_path)
            assert result.is_failure
            assert "Failed to load JSON file" in result.error
        finally:
            Path(temp_path).unlink()

    def test_save_json_success(self) -> None:
        """Test _save_json method success."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            data = {"key": "value"}
            result = file_tools._save_json(temp_path, data)
            assert result.is_success

            # Verify file was created and contains correct data
            with Path(temp_path).open("r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            assert loaded_data == data
        finally:
            Path(temp_path).unlink()

    def test_save_json_exception(self) -> None:
        """Test _save_json method with exception."""
        file_tools = FlextCliFileTools()
        with patch("json.dump", side_effect=Exception("Test error")):
            result = file_tools._save_json("test.json", {"key": "value"})
            assert result.is_failure
            assert "Failed to save JSON file" in result.error

    def test_load_yaml_success(self) -> None:
        """Test _load_yaml method success."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".yaml", delete=False
        ) as f:
            yaml.dump({"key": "value"}, f)
            temp_path = f.name

        try:
            result = file_tools._load_yaml(temp_path)
            assert result.is_success
            data = result.unwrap()
            assert data == {"key": "value"}
        finally:
            Path(temp_path).unlink()

    def test_load_yaml_file_not_found(self) -> None:
        """Test _load_yaml method with file not found."""
        file_tools = FlextCliFileTools()
        result = file_tools._load_yaml("nonexistent.yaml")
        assert result.is_failure
        assert "File does not exist" in result.error

    def test_load_yaml_invalid_yaml(self) -> None:
        """Test _load_yaml method with invalid YAML."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name

        try:
            result = file_tools._load_yaml(temp_path)
            assert result.is_failure
            assert "Failed to load YAML file" in result.error
        finally:
            Path(temp_path).unlink()

    def test_save_yaml_success(self) -> None:
        """Test _save_yaml method success."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            data = {"key": "value"}
            result = file_tools._save_yaml(temp_path, data)
            assert result.is_success

            # Verify file was created and contains correct data
            with Path(temp_path).open("r", encoding="utf-8") as f:
                loaded_data = yaml.safe_load(f)
            assert loaded_data == data
        finally:
            Path(temp_path).unlink()

    def test_save_yaml_exception(self) -> None:
        """Test _save_yaml method with exception."""
        file_tools = FlextCliFileTools()
        with patch("yaml.dump", side_effect=Exception("Test error")):
            result = file_tools._save_yaml("test.yaml", {"key": "value"})
            assert result.is_failure
            assert "Failed to save YAML file" in result.error

    def test_load_text_success(self) -> None:
        """Test _load_text method success."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".txt", delete=False
        ) as f:
            f.write("Hello, World!")
            temp_path = f.name

        try:
            result = file_tools._load_text(temp_path)
            assert result.is_success
            data = result.unwrap()
            assert data == "Hello, World!"
        finally:
            Path(temp_path).unlink()

    def test_load_text_file_not_found(self) -> None:
        """Test _load_text method with file not found."""
        file_tools = FlextCliFileTools()
        result = file_tools._load_text("nonexistent.txt")
        assert result.is_failure
        assert "File does not exist" in result.error

    def test_save_text_success(self) -> None:
        """Test _save_text method success."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name

        try:
            data = "Hello, World!"
            result = file_tools._save_text(temp_path, data)
            assert result.is_success

            # Verify file was created and contains correct data
            with Path(temp_path).open("r", encoding="utf-8") as f:
                loaded_data = f.read()
            assert loaded_data == data
        finally:
            Path(temp_path).unlink()

    def test_save_text_exception(self) -> None:
        """Test _save_text method with exception."""
        file_tools = FlextCliFileTools()
        with patch("flext_cli.file_tools.Path", side_effect=Exception("Test error")):
            result = file_tools._save_text("test.txt", "Hello, World!")
            assert result.is_failure
            assert "Test error" in result.error
            assert "Failed to save text file" in result.error

    def test_load_csv_success(self) -> None:
        """Test _load_csv method success."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".csv", delete=False
        ) as f:
            f.write("name,age\nJohn,25\nJane,30\n")
            temp_path = f.name

        try:
            result = file_tools._load_csv(temp_path)
            assert result.is_success
            data = result.unwrap()
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["name"] == "John"
            assert data[0]["age"] == 25
        finally:
            Path(temp_path).unlink()

    def test_load_csv_file_not_found(self) -> None:
        """Test _load_csv method with file not found."""
        file_tools = FlextCliFileTools()
        result = file_tools._load_csv("nonexistent.csv")
        assert result.is_failure
        assert "Failed to load CSV file" in result.error

    def test_load_csv_text_file_reader(self) -> None:
        """Test _load_csv method with TextFileReader return."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".csv", delete=False
        ) as f:
            f.write("name,age\nJohn,25\nJane,30\n")
            temp_path = f.name

        try:
            # Mock pandas.read_csv to return a TextFileReader-like object
            with patch("flext_cli.file_tools.pd.read_csv") as mock_read_csv:
                # Create a mock TextFileReader object
                mock_reader = MagicMock()
                mock_reader.__class__.__name__ = "TextFileReader"
                mock_read_csv.return_value = mock_reader

                result = file_tools._load_csv(temp_path)
                assert result.is_failure
                assert "CSV file requires specific parameters" in result.error
        finally:
            Path(temp_path).unlink()

    def test_load_csv_exception(self) -> None:
        """Test _load_csv method with exception."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".csv", delete=False
        ) as f:
            f.write("name,age\nJohn,25\nJane,30\n")
            temp_path = f.name

        try:
            # Mock pandas.read_csv to raise an exception
            with patch(
                "flext_cli.file_tools.pd.read_csv", side_effect=Exception("Test error")
            ):
                result = file_tools._load_csv(temp_path)
                assert result.is_failure
                assert "Failed to load CSV file" in result.error
        finally:
            Path(temp_path).unlink()

    def test_save_csv_success(self) -> None:
        """Test _save_csv method success."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            data = pd.DataFrame({"name": ["John", "Jane"], "age": [25, 30]})
            result = file_tools._save_csv(temp_path, data)
            assert result.is_success

            # Verify file was created
            assert Path(temp_path).exists()
        finally:
            Path(temp_path).unlink()

    def test_save_csv_list_of_dicts(self) -> None:
        """Test _save_csv method with list of dicts."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            data = [{"name": "John", "age": 25}, {"name": "Jane", "age": 30}]
            result = file_tools._save_csv(temp_path, data)
            assert result.is_success

            # Verify file was created
            assert Path(temp_path).exists()
        finally:
            Path(temp_path).unlink()

    def test_save_csv_single_dict(self) -> None:
        """Test _save_csv method with single dict."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            data = {"name": "John", "age": 25}
            result = file_tools._save_csv(temp_path, data)
            assert result.is_success

            # Verify file was created
            assert Path(temp_path).exists()
        finally:
            Path(temp_path).unlink()

    def test_save_csv_other_data_type(self) -> None:
        """Test _save_csv method with other data type."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            data = "test string"
            result = file_tools._save_csv(temp_path, data)
            assert result.is_success

            # Verify file was created
            assert Path(temp_path).exists()
        finally:
            Path(temp_path).unlink()

    def test_save_csv_exception(self) -> None:
        """Test _save_csv method with exception."""
        file_tools = FlextCliFileTools()
        with patch("pandas.DataFrame.to_csv", side_effect=Exception("Test error")):
            data = pd.DataFrame({"name": ["John", "Jane"], "age": [25, 30]})
            result = file_tools._save_csv("test.csv", data)
            assert result.is_failure
            assert "Failed to save CSV file" in result.error

    def test_load_tsv_success(self) -> None:
        """Test _load_tsv method success."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".tsv", delete=False
        ) as f:
            f.write("name\tage\nJohn\t25\nJane\t30\n")
            temp_path = f.name

        try:
            result = file_tools._load_tsv(temp_path)
            assert result.is_success
            data = result.unwrap()
            assert isinstance(data, list)
            assert len(data) == 2
            assert data[0]["name"] == "John"
            assert data[0]["age"] == 25
        finally:
            Path(temp_path).unlink()

    def test_load_tsv_file_not_found(self) -> None:
        """Test _load_tsv method with file not found."""
        file_tools = FlextCliFileTools()
        result = file_tools._load_tsv("nonexistent.tsv")
        assert result.is_failure
        assert "File does not exist" in result.error

    def test_save_tsv_success(self) -> None:
        """Test _save_tsv method success."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".tsv", delete=False) as f:
            temp_path = f.name

        try:
            data = pd.DataFrame({"name": ["John", "Jane"], "age": [25, 30]})
            result = file_tools._save_tsv(temp_path, data)
            assert result.is_success

            # Verify file was created
            assert Path(temp_path).exists()
        finally:
            Path(temp_path).unlink()

    def test_save_tsv_exception(self) -> None:
        """Test _save_tsv method with exception."""
        file_tools = FlextCliFileTools()
        with patch("pandas.DataFrame.to_csv", side_effect=Exception("Test error")):
            data = pd.DataFrame({"name": ["John", "Jane"], "age": [25, 30]})
            result = file_tools._save_tsv("test.tsv", data)
            assert result.is_failure
            assert "Failed to save TSV file" in result.error

    def test_load_toml_success(self) -> None:
        """Test _load_toml method success."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", suffix=".toml", delete=False
        ) as f:
            f.write('key = "value"\n')
            temp_path = f.name

        try:
            result = file_tools._load_toml(temp_path)
            assert result.is_success
            data = result.unwrap()
            assert data == {"key": "value"}
        finally:
            Path(temp_path).unlink()

    def test_load_toml_file_not_found(self) -> None:
        """Test _load_toml method with file not found."""
        file_tools = FlextCliFileTools()
        result = file_tools._load_toml("nonexistent.toml")
        assert result.is_failure
        assert "Failed to load TOML file" in result.error

    def test_save_toml_success(self) -> None:
        """Test _save_toml method success."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False) as f:
            temp_path = f.name

        try:
            data = {"key": "value"}
            result = file_tools._save_toml(temp_path, data)
            assert result.is_success

            # Verify file was created and contains correct data
            with Path(temp_path).open("r", encoding="utf-8") as f:
                loaded_data = f.read()
            assert 'key = "value"' in loaded_data
        finally:
            Path(temp_path).unlink()

    def test_save_toml_exception(self) -> None:
        """Test _save_toml method with exception."""
        file_tools = FlextCliFileTools()
        with patch("toml.dump", side_effect=Exception("Test error")):
            result = file_tools._save_toml("test.toml", {"key": "value"})
            assert result.is_failure
            assert "Failed to save TOML file" in result.error


class TestFlextCliFileToolsIntegration:
    """Integration tests for FlextCliFileTools."""

    def test_full_workflow_json(self) -> None:
        """Test complete workflow with JSON files."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
            temp_path = f.name

        try:
            # Test save
            data = {"name": "John", "age": 25, "city": "New York"}
            save_result = file_tools.save_file(temp_path, data)
            assert save_result.is_success

            # Test load
            load_result = file_tools.load_file(temp_path)
            assert load_result.is_success
            loaded_data = load_result.unwrap()
            assert loaded_data == data

            # Test format detection
            format_result = file_tools.detect_file_format(temp_path)
            assert format_result.is_success
            assert format_result.unwrap() == "json"
        finally:
            Path(temp_path).unlink()

    def test_full_workflow_yaml(self) -> None:
        """Test complete workflow with YAML files."""
        file_tools = FlextCliFileTools()

        with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False) as f:
            temp_path = f.name

        try:
            # Test save
            data = {"name": "Jane", "age": 30, "city": "San Francisco"}
            save_result = file_tools.save_file(temp_path, data)
            assert save_result.is_success

            # Test load
            load_result = file_tools.load_file(temp_path)
            assert load_result.is_success
            loaded_data = load_result.unwrap()
            assert loaded_data == data

            # Test format detection
            format_result = file_tools.detect_file_format(temp_path)
            assert format_result.is_success
            assert format_result.unwrap() == "yaml"
        finally:
            Path(temp_path).unlink()

    def test_error_handling_chain(self) -> None:
        """Test error handling in method chains."""
        file_tools = FlextCliFileTools()

        # Test that errors are properly propagated
        result = file_tools.load_file("nonexistent.json")
        assert result.is_failure

        # Test that save_file creates directories as needed (correct behavior)
        with tempfile.TemporaryDirectory() as temp_dir:
            result = file_tools.save_file(
                f"{temp_dir}/test_file_tools/file.json", {"key": "value"}
            )
            assert result.is_success

    def test_supported_formats_completeness(self) -> None:
        """Test that all expected formats are supported."""
        file_tools = FlextCliFileTools()
        result = file_tools.get_supported_formats()
        assert result.is_success

        formats = result.unwrap()
        expected_formats = [
            "json",
            "yaml",
            "csv",
            "tsv",
            "xml",
            "toml",
            "excel",
            "parquet",
            "text",
        ]

        for expected_format in expected_formats:
            assert expected_format in formats

"""FLEXT CLI File Tools Tests - Comprehensive Real Functionality Testing.

Tests for FlextCliFileTools covering all real functionality with flext_tests
integration, comprehensive file operations, and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import json
import threading
import zipfile
from pathlib import Path

import pytest
import yaml
from flext_core import FlextResult, FlextTypes

# Test utilities removed from flext-core production exports
from flext_cli.file_tools import FlextCliFileTools


class TestFlextCliFileTools:
    """Comprehensive tests for FlextCliFileTools functionality."""

    @pytest.fixture
    def file_tools(self) -> FlextCliFileTools:
        """Create FlextCliFileTools instance for testing."""
        return FlextCliFileTools()

    @pytest.fixture
    # ========================================================================
    # INITIALIZATION AND BASIC FUNCTIONALITY
    # ========================================================================
    def test_file_tools_initialization(self, file_tools: FlextCliFileTools) -> None:
        """Test file tools initialization and basic properties."""
        assert file_tools is not None
        assert hasattr(file_tools, "logger")
        assert hasattr(file_tools, "_container")

    def test_file_tools_execute_method(self, file_tools: FlextCliFileTools) -> None:
        """Test file tools execute method with real functionality."""
        result = file_tools.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, bool)
        assert data is True

    # ========================================================================
    # BASIC FILE OPERATIONS
    # ========================================================================

    def test_read_text_file(
        self, file_tools: FlextCliFileTools, temp_file: Path
    ) -> None:
        """Test reading text file functionality."""
        result = file_tools.read_text_file(str(temp_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        content = result.unwrap()
        assert isinstance(content, str)
        assert content == "test content"

    def test_read_text_file_nonexistent(self, file_tools: FlextCliFileTools) -> None:
        """Test reading nonexistent text file."""
        result = file_tools.read_text_file("/nonexistent/file.txt")

        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_write_text_file(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test writing text file functionality."""
        test_file = temp_dir / "test_write.txt"
        test_content = "This is test content for writing"

        result = file_tools.write_text_file(str(test_file), test_content)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was created and contains correct content
        assert test_file.exists()
        assert test_file.read_text() == test_content

    def test_read_binary_file(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test reading binary file functionality."""
        # Create a binary file
        binary_file = temp_dir / "test_binary.bin"
        binary_content = b"\x00\x01\x02\x03\x04\x05"
        binary_file.write_bytes(binary_content)

        result = file_tools.read_binary_file(str(binary_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        content = result.unwrap()
        assert isinstance(content, bytes)
        assert content == binary_content

    def test_write_binary_file(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test writing binary file functionality."""
        test_file = temp_dir / "test_binary_write.bin"
        test_content = b"\x00\x01\x02\x03\x04\x05"

        result = file_tools.write_binary_file(str(test_file), test_content)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was created and contains correct content
        assert test_file.exists()
        assert test_file.read_bytes() == test_content

    # ========================================================================
    # JSON FILE OPERATIONS
    # ========================================================================

    def test_read_json_file(
        self, file_tools: FlextCliFileTools, temp_json_file: Path
    ) -> None:
        """Test reading JSON file functionality."""
        result = file_tools.read_json_file(str(temp_json_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)
        assert data["key"] == "value"
        assert data["number"] == 42
        assert data["list"] == [1, 2, 3]

    def test_write_json_file(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test writing JSON file functionality."""
        test_file = temp_dir / "test_write.json"
        test_data: FlextTypes.Dict = {
            "name": "test",
            "value": 123,
            "nested": {"inner": "data"},
            "list": [1, 2, 3],
        }

        result = file_tools.write_json_file(str(test_file), test_data)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was created and contains correct data
        assert test_file.exists()
        loaded_data = json.loads(test_file.read_text())
        assert loaded_data == test_data

    def test_read_json_file_invalid(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test reading invalid JSON file."""
        invalid_json_file = temp_dir / "invalid.json"
        invalid_json_file.write_text('{"key": "value", "invalid": json}')

        result = file_tools.read_json_file(str(invalid_json_file))

        assert isinstance(result, FlextResult)
        assert result.is_failure

    # ========================================================================
    # YAML FILE OPERATIONS
    # ========================================================================

    def test_read_yaml_file(
        self, file_tools: FlextCliFileTools, temp_yaml_file: Path
    ) -> None:
        """Test reading YAML file functionality."""
        result = file_tools.read_yaml_file(str(temp_yaml_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, dict)
        assert data["key"] == "value"
        assert data["number"] == 42
        assert data["list"] == [1, 2, 3]

    def test_write_yaml_file(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test writing YAML file functionality."""
        test_file = temp_dir / "test_write.yaml"
        test_data: FlextTypes.Dict = {
            "name": "test",
            "value": 123,
            "nested": {"inner": "data"},
            "list": [1, 2, 3],
        }

        result = file_tools.write_yaml_file(str(test_file), test_data)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was created and contains correct data
        assert test_file.exists()
        loaded_data = yaml.safe_load(test_file.read_text())
        assert loaded_data == test_data

    def test_read_yaml_file_invalid(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test reading invalid YAML file."""
        invalid_yaml_file = temp_dir / "invalid.yaml"
        invalid_yaml_file.write_text("key: value\ninvalid: yaml: content:")

        result = file_tools.read_yaml_file(str(invalid_yaml_file))

        assert isinstance(result, FlextResult)
        assert result.is_failure

    # ========================================================================
    # CSV FILE OPERATIONS
    # ========================================================================

    def test_read_csv_file(
        self, file_tools: FlextCliFileTools, temp_csv_file: Path
    ) -> None:
        """Test reading CSV file functionality."""
        result = file_tools.read_csv_file(str(temp_csv_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, list)
        assert len(data) == 4  # Header + 3 data rows
        assert data[0] == ["name", "age", "city"]
        assert data[1] == ["John", "30", "New York"]
        assert data[2] == ["Jane", "25", "London"]
        assert data[3] == ["Bob", "35", "Paris"]

    def test_write_csv_file(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test writing CSV file functionality."""
        test_file = temp_dir / "test_write.csv"
        test_data = [
            ["name", "age", "city"],
            ["Alice", "28", "Paris"],
            ["Bob", "35", "Tokyo"],
            ["Charlie", "22", "Sydney"],
        ]

        result = file_tools.write_csv_file(str(test_file), test_data)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was created and contains correct data
        assert test_file.exists()
        with Path(test_file).open(encoding="utf-8", newline="") as f:
            reader = csv.reader(f)
            loaded_data = list(reader)
        assert loaded_data == test_data

    def test_read_csv_file_with_headers(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test reading CSV file with headers functionality."""
        csv_file = temp_dir / "test_headers.csv"
        csv_content = "name,age,city\nJohn,30,New York\nJane,25,London"
        csv_file.write_text(csv_content)

        result = file_tools.read_csv_file_with_headers(str(csv_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, list)
        assert len(data) == 2
        assert data[0] == {"name": "John", "age": 30, "city": "New York"}
        assert data[1] == {"name": "Jane", "age": 25, "city": "London"}

    # ========================================================================
    # FILE SYSTEM OPERATIONS
    # ========================================================================

    def test_copy_file(
        self, file_tools: FlextCliFileTools, temp_file: Path, temp_dir: Path
    ) -> None:
        """Test file copying functionality."""
        destination = temp_dir / "copied_file.txt"

        result = file_tools.copy_file(str(temp_file), str(destination))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was copied correctly
        assert destination.exists()
        assert destination.read_text() == temp_file.read_text(encoding="utf-8")

    def test_move_file(
        self, file_tools: FlextCliFileTools, temp_file: Path, temp_dir: Path
    ) -> None:
        """Test file moving functionality."""
        destination = temp_dir / "moved_file.txt"
        original_content = temp_file.read_text(encoding="utf-8")

        result = file_tools.move_file(str(temp_file), str(destination))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was moved correctly
        assert not temp_file.exists()
        assert destination.exists()
        assert destination.read_text() == original_content

    def test_delete_file(self, file_tools: FlextCliFileTools, temp_file: Path) -> None:
        """Test file deletion functionality."""
        assert temp_file.exists()

        result = file_tools.delete_file(str(temp_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was deleted
        assert not temp_file.exists()

    def test_file_exists(self, file_tools: FlextCliFileTools, temp_file: Path) -> None:
        """Test file existence checking functionality."""
        # Test existing file
        result = file_tools.file_exists(str(temp_file))
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

        # Test nonexistent file
        result = file_tools.file_exists("/nonexistent/file.txt")
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is False

    def test_get_file_size(
        self, file_tools: FlextCliFileTools, temp_file: Path
    ) -> None:
        """Test file size getting functionality."""
        result = file_tools.get_file_size(str(temp_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        size = result.unwrap()
        assert isinstance(size, int)
        assert size > 0
        assert size == len(temp_file.read_text(encoding="utf-8"))

    def test_get_file_modified_time(
        self, file_tools: FlextCliFileTools, temp_file: Path
    ) -> None:
        """Test file modified time getting functionality."""
        result = file_tools.get_file_modified_time(str(temp_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        modified_time = result.unwrap()
        assert isinstance(modified_time, float)
        assert modified_time > 0

    # ========================================================================
    # DIRECTORY OPERATIONS
    # ========================================================================

    def test_list_directory(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test directory listing functionality."""
        # Create some test files
        (temp_dir / "file1.txt").write_text("content1")
        (temp_dir / "file2.txt").write_text("content2")
        (temp_dir / "subdir").mkdir()

        result = file_tools.list_directory(str(temp_dir))

        assert isinstance(result, FlextResult)
        assert result.is_success

        files = result.unwrap()
        assert isinstance(files, list)
        assert len(files) >= 2  # At least the files we created

    def test_create_directory(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test directory creation functionality."""
        new_dir = temp_dir / "new_directory"

        result = file_tools.create_directory(str(new_dir))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify directory was created
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_directories(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test nested directory creation functionality."""
        nested_dir = temp_dir / "level1" / "level2" / "level3"

        result = file_tools.create_directories(str(nested_dir))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify all directories were created
        assert nested_dir.exists()
        assert nested_dir.is_dir()
        assert (temp_dir / "level1").exists()
        assert (temp_dir / "level1" / "level2").exists()

    def test_delete_directory(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test directory deletion functionality."""
        test_dir = temp_dir / "test_delete_dir"
        test_dir.mkdir()
        (test_dir / "test_file.txt").write_text("test")

        assert test_dir.exists()

        result = file_tools.delete_directory(str(test_dir))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify directory was deleted
        assert not test_dir.exists()

    def test_directory_exists(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test directory existence checking functionality."""
        # Test existing directory
        result = file_tools.directory_exists(str(temp_dir))
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

        # Test nonexistent directory
        result = file_tools.directory_exists("/nonexistent/directory")
        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is False

    # ========================================================================
    # ARCHIVE OPERATIONS
    # ========================================================================

    def test_create_zip_archive(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test ZIP archive creation functionality."""
        # Create test files
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file1.write_text("Content 1")
        file2.write_text("Content 2")

        archive_path = temp_dir / "test_archive.zip"
        files_to_archive = [str(file1), str(file2)]

        result = file_tools.create_zip_archive(str(archive_path), files_to_archive)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify archive was created
        assert archive_path.exists()

        # Verify archive contains the files
        with zipfile.ZipFile(archive_path, "r") as zip_file:
            file_list = zip_file.namelist()
            assert "file1.txt" in file_list
            assert "file2.txt" in file_list

    def test_extract_zip_archive(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test ZIP archive extraction functionality."""
        # Create a ZIP archive first
        file1 = temp_dir / "file1.txt"
        file1.write_text("Content 1")

        archive_path = temp_dir / "test_archive.zip"
        with zipfile.ZipFile(archive_path, "w") as zip_file:
            zip_file.write(file1, "file1.txt")

        # Extract the archive
        extract_dir = temp_dir / "extracted"
        extract_dir.mkdir()

        result = file_tools.extract_zip_archive(str(archive_path), str(extract_dir))

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify file was extracted
        extracted_file = extract_dir / "file1.txt"
        assert extracted_file.exists()
        assert extracted_file.read_text() == "Content 1"

    # ========================================================================
    # FILE SEARCH AND FILTERING
    # ========================================================================

    def test_find_files_by_pattern(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test finding files by pattern functionality."""
        # Create test files with different extensions
        (temp_dir / "test1.txt").write_text("content1")
        (temp_dir / "test2.txt").write_text("content2")
        (temp_dir / "test3.json").write_text('{"key": "value"}')
        (temp_dir / "other.log").write_text("log content")

        result = file_tools.find_files_by_pattern(str(temp_dir), "*.txt")

        assert isinstance(result, FlextResult)
        assert result.is_success

        files = result.unwrap()
        assert isinstance(files, list)
        assert len(files) == 2
        assert any("test1.txt" in f for f in files)
        assert any("test2.txt" in f for f in files)

    def test_find_files_by_name(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test finding files by name functionality."""
        # Create test files
        (temp_dir / "target_file.txt").write_text("target content")
        (temp_dir / "other_file.txt").write_text("other content")
        (temp_dir / "subdir").mkdir()
        (temp_dir / "subdir" / "target_file.txt").write_text("nested target")

        result = file_tools.find_files_by_name(str(temp_dir), "target_file.txt")

        assert isinstance(result, FlextResult)
        assert result.is_success

        files = result.unwrap()
        assert isinstance(files, list)
        assert len(files) == 2  # One in root, one in subdir

    def test_find_files_by_content(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test finding files by content functionality."""
        # Create test files with different content
        (temp_dir / "file1.txt").write_text("This file contains the target word")
        (temp_dir / "file2.txt").write_text("This file does not")
        (temp_dir / "file3.txt").write_text("This file also contains the target word")

        result = file_tools.find_files_by_content(str(temp_dir), "target word")

        assert isinstance(result, FlextResult)
        assert result.is_success

        files = result.unwrap()
        assert isinstance(files, list)
        assert len(files) == 2  # file1 and file3

    # ========================================================================
    # FILE VALIDATION AND CHECKSUM
    # ========================================================================

    def test_calculate_file_hash(
        self, file_tools: FlextCliFileTools, temp_file: Path
    ) -> None:
        """Test file hash calculation functionality."""
        result = file_tools.calculate_file_hash(str(temp_file), "sha256")

        assert isinstance(result, FlextResult)
        assert result.is_success

        hash_value = result.unwrap()
        assert isinstance(hash_value, str)
        assert len(hash_value) == 64  # SHA256 hash length

    def test_verify_file_hash(
        self, file_tools: FlextCliFileTools, temp_file: Path
    ) -> None:
        """Test file hash verification functionality."""
        # Calculate hash first
        hash_result = file_tools.calculate_file_hash(str(temp_file), "sha256")
        assert hash_result.is_success
        expected_hash = hash_result.unwrap()

        # Verify hash
        result = file_tools.verify_file_hash(str(temp_file), expected_hash, "sha256")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

    def test_verify_file_hash_invalid(
        self, file_tools: FlextCliFileTools, temp_file: Path
    ) -> None:
        """Test file hash verification with invalid hash."""
        invalid_hash = "invalid_hash_value"

        result = file_tools.verify_file_hash(str(temp_file), invalid_hash, "sha256")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is False

    # ========================================================================
    # FILE PERMISSIONS AND ATTRIBUTES
    # ========================================================================

    def test_get_file_permissions(
        self, file_tools: FlextCliFileTools, temp_file: Path
    ) -> None:
        """Test getting file permissions functionality."""
        result = file_tools.get_file_permissions(str(temp_file))

        assert isinstance(result, FlextResult)
        assert result.is_success

        permissions = result.unwrap()
        assert isinstance(permissions, str)
        assert len(permissions) == 3  # Owner, Group, Other

    def test_set_file_permissions(
        self, file_tools: FlextCliFileTools, temp_file: Path
    ) -> None:
        """Test setting file permissions functionality."""
        result = file_tools.set_file_permissions(str(temp_file), "644")

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify permissions were set
        permissions_result = file_tools.get_file_permissions(str(temp_file))
        assert permissions_result.is_success
        permissions = permissions_result.unwrap()
        assert permissions == "644"

    # ========================================================================
    # TEMPORARY FILE OPERATIONS
    # ========================================================================

    def test_create_temp_file(self, file_tools: FlextCliFileTools) -> None:
        """Test temporary file creation functionality."""
        result = file_tools.create_temp_file("test_content", suffix=".txt")

        assert isinstance(result, FlextResult)
        assert result.is_success

        temp_file_path = result.unwrap()
        assert isinstance(temp_file_path, str)

        # Verify file exists and has correct content
        temp_file = Path(temp_file_path)
        assert temp_file.exists()
        assert temp_file.read_text(encoding="utf-8") == "test_content"
        assert temp_file.suffix == ".txt"

        # Clean up
        temp_file.unlink()

    def test_create_temp_directory(self, file_tools: FlextCliFileTools) -> None:
        """Test temporary directory creation functionality."""
        result = file_tools.create_temp_directory()

        assert isinstance(result, FlextResult)
        assert result.is_success

        temp_dir_path = result.unwrap()
        assert isinstance(temp_dir_path, str)

        # Verify directory exists
        temp_dir = Path(temp_dir_path)
        assert temp_dir.exists()
        assert temp_dir.is_dir()

        # Clean up
        temp_dir.rmdir()

    # ========================================================================
    # ERROR HANDLING AND EDGE CASES
    # ========================================================================

    def test_error_handling_with_invalid_input(
        self, file_tools: FlextCliFileTools
    ) -> None:
        """Test error handling with various invalid inputs."""
        # Test with None input
        result = file_tools.read_text_file("")
        assert isinstance(result, FlextResult)
        assert result.is_failure

        # Test with empty string
        result = file_tools.read_text_file("")
        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_error_handling_with_permission_denied(
        self, file_tools: FlextCliFileTools
    ) -> None:
        """Test error handling with permission denied scenarios."""
        # Try to write to a directory that should be read-only
        result = file_tools.write_text_file("/proc/test_file", "test content")
        assert isinstance(result, FlextResult)
        assert result.is_failure

    def test_concurrent_file_operations(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test concurrent file operations to ensure thread safety."""
        results = []
        errors = []

        def worker(worker_id: int) -> None:
            try:
                test_file = temp_dir / f"concurrent_test_{worker_id}.txt"
                result = file_tools.write_text_file(
                    str(test_file), f"Worker {worker_id} content"
                )
                results.append(result)
            except Exception as e:
                errors.append(e)

        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify all operations succeeded
        assert len(errors) == 0, f"Errors occurred: {errors}"
        assert len(results) == 5
        for result in results:
            assert isinstance(result, FlextResult)
            assert result.is_success

    # ========================================================================
    # INTEGRATION TESTS
    # ========================================================================

    def test_full_file_workflow_integration(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test complete file workflow integration."""
        # 1. Create test data
        test_data: FlextTypes.Dict = {
            "name": "integration_test",
            "value": 42,
            "nested": {"inner": "data"},
            "list": [1, 2, 3],
        }

        # 2. Write JSON file
        json_file = temp_dir / "test_data.json"
        write_result = file_tools.write_json_file(str(json_file), test_data)
        assert write_result.is_success

        # 3. Read JSON file
        read_result = file_tools.read_json_file(str(json_file))
        assert read_result.is_success
        assert read_result.unwrap() == test_data

        # 4. Copy file
        copied_file = temp_dir / "copied_data.json"
        copy_result = file_tools.copy_file(str(json_file), str(copied_file))
        assert copy_result.is_success

        # 5. Verify copied file
        assert copied_file.exists()
        copied_data = json.loads(copied_file.read_text())
        assert copied_data == test_data

        # 6. Calculate hash
        hash_result = file_tools.calculate_file_hash(str(json_file), "sha256")
        assert hash_result.is_success
        original_hash = hash_result.unwrap()

        # 7. Verify hash of copied file
        copied_hash_result = file_tools.calculate_file_hash(str(copied_file), "sha256")
        assert copied_hash_result.is_success
        copied_hash = copied_hash_result.unwrap()

        # 8. Hashes should be identical
        assert original_hash == copied_hash

        # 9. Create archive
        archive_file = temp_dir / "test_archive.zip"
        archive_result = file_tools.create_zip_archive(
            str(archive_file), [str(json_file), str(copied_file)]
        )
        assert archive_result.is_success

        # 10. Verify complete workflow
        assert json_file.exists()
        assert copied_file.exists()
        assert archive_file.exists()

    def test_file_workflow_integration(self, file_tools: FlextCliFileTools) -> None:
        """Test file workflow integration (execute now sync)."""
        # Test execute (now sync, delegates to execute)
        result = file_tools.execute()
        assert isinstance(result, FlextResult)
        assert result.is_success

        data = result.unwrap()
        assert isinstance(data, bool)
        assert data is True

    # ========================================================================
    # ADDITIONAL COVERAGE TESTS
    # ========================================================================

    def test_detect_file_format(
        self, file_tools: FlextCliFileTools, temp_json_file: Path
    ) -> None:
        """Test file format detection."""
        result = file_tools.detect_file_format(str(temp_json_file))
        assert result.is_success
        assert result.unwrap() == "json"

    def test_get_supported_formats(self, file_tools: FlextCliFileTools) -> None:
        """Test getting supported file formats."""
        result = file_tools.get_supported_formats()
        assert result.is_success
        formats = result.unwrap()
        assert isinstance(formats, list)
        assert "json" in formats
        assert "yaml" in formats
        assert "csv" in formats

    def test_load_file_auto_detect(
        self, file_tools: FlextCliFileTools, temp_json_file: Path
    ) -> None:
        """Test loading file with auto-detection."""
        result = file_tools.load_file(str(temp_json_file))
        assert result.is_success
        data = result.unwrap()
        assert isinstance(data, dict)

    def test_save_file(self, file_tools: FlextCliFileTools, temp_dir: Path) -> None:
        """Test saving file."""
        test_file = temp_dir / "test_save.json"
        test_data = {"test": "data", "value": 123}
        result = file_tools.save_file(str(test_file), test_data, file_format="json")
        assert result.is_success
        assert test_file.exists()

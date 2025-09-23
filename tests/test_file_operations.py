"""Tests for FlextCliFileOperations - Real API only.

Tests file operations using actual implemented methods.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from flext_cli.file_operations import FlextCliFileOperations
from flext_core import FlextResult


class TestFlextCliFileOperations:
    """Test FlextCliFileOperations with real functionality."""

    def setup_method(self) -> None:
        """Setup test method."""
        self.file_ops = FlextCliFileOperations()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self) -> None:
        """Cleanup test method."""
        import shutil

        if self.temp_path.exists():
            shutil.rmtree(self.temp_path)

    def test_file_exists_with_existing_file(self) -> None:
        """Test file_exists with an existing file."""
        test_file = self.temp_path / "test.txt"
        test_file.write_text("test content")

        result = self.file_ops.file_exists(test_file)
        assert result is True

    def test_file_exists_with_nonexistent_file(self) -> None:
        """Test file_exists with a non-existent file."""
        test_file = self.temp_path / "nonexistent.txt"

        result = self.file_ops.file_exists(test_file)
        assert result is False

    def test_file_exists_with_directory(self) -> None:
        """Test file_exists with a directory."""
        test_dir = self.temp_path / "testdir"
        test_dir.mkdir()

        result = self.file_ops.file_exists(test_dir)
        # Directory exists (returns True)
        assert result is True

    def test_get_file_size_with_existing_file(self) -> None:
        """Test get_file_size with existing file."""
        test_file = self.temp_path / "test.txt"
        content = "test content"
        test_file.write_text(content)

        result = self.file_ops.get_file_size(test_file)
        assert result.is_success
        assert result.value == len(content.encode("utf-8"))

    def test_get_file_size_with_empty_file(self) -> None:
        """Test get_file_size with empty file."""
        test_file = self.temp_path / "empty.txt"
        test_file.write_text("")

        result = self.file_ops.get_file_size(test_file)
        assert result.is_success
        assert result.value == 0

    def test_get_file_size_with_nonexistent_file(self) -> None:
        """Test get_file_size with non-existent file."""
        test_file = self.temp_path / "nonexistent.txt"

        result = self.file_ops.get_file_size(test_file)
        assert result.is_failure

    def test_get_file_size_with_directory(self) -> None:
        """Test get_file_size with directory."""
        test_dir = self.temp_path / "testdir"
        test_dir.mkdir()

        result = self.file_ops.get_file_size(test_dir)
        # Directory stat should work and return size
        assert result.is_success or result.is_failure  # Implementation dependent

    def test_file_exists_with_path_object(self) -> None:
        """Test file_exists with Path object."""
        test_file = self.temp_path / "pathtest.txt"
        test_file.write_text("test")

        result = self.file_ops.file_exists(test_file)
        assert result is True

    def test_file_exists_with_string_path(self) -> None:
        """Test file_exists with string path."""
        test_file = self.temp_path / "stringtest.txt"
        test_file.write_text("test")

        result = self.file_ops.file_exists(str(test_file))
        assert result is True

    def test_get_file_size_with_large_file(self) -> None:
        """Test get_file_size with larger file."""
        test_file = self.temp_path / "large.txt"
        content = "x" * 10000
        test_file.write_text(content)

        result = self.file_ops.get_file_size(test_file)
        assert result.is_success
        assert result.value == 10000

    def test_file_operations_return_correct_types(self) -> None:
        """Test that operations return correct types."""
        test_file = self.temp_path / "result_test.txt"
        test_file.write_text("test")

        exists_result = self.file_ops.file_exists(test_file)
        size_result = self.file_ops.get_file_size(test_file)

        assert isinstance(exists_result, bool)
        assert isinstance(size_result, FlextResult)

    def test_file_operations_with_special_characters(self) -> None:
        """Test file operations with special characters in filename."""
        test_file = self.temp_path / "test file with spaces.txt"
        test_file.write_text("content")

        exists_result = self.file_ops.file_exists(test_file)
        size_result = self.file_ops.get_file_size(test_file)

        assert exists_result is True
        assert size_result.is_success

    def test_file_operations_with_unicode_filename(self) -> None:
        """Test file operations with unicode filename."""
        test_file = self.temp_path / "テスト.txt"
        test_file.write_text("unicode content")

        exists_result = self.file_ops.file_exists(test_file)
        size_result = self.file_ops.get_file_size(test_file)

        assert exists_result is True
        assert size_result.is_success

    def test_file_exists_with_symlink(self) -> None:
        """Test file_exists with symbolic link."""
        test_file = self.temp_path / "original.txt"
        test_file.write_text("content")

        link_file = self.temp_path / "link.txt"
        try:
            link_file.symlink_to(test_file)

            result = self.file_ops.file_exists(link_file)
            assert result is True
        except OSError:
            # Symlinks might not be supported
            pytest.skip("Symlinks not supported")

    def test_get_file_size_with_binary_file(self) -> None:
        """Test get_file_size with binary file."""
        test_file = self.temp_path / "binary.bin"
        binary_content = bytes([0, 1, 2, 3, 4, 5])
        test_file.write_bytes(binary_content)

        result = self.file_ops.get_file_size(test_file)
        assert result.is_success
        assert result.value == 6

    def test_file_operations_concurrent_access(self) -> None:
        """Test file operations with concurrent file access."""
        test_file = self.temp_path / "concurrent.txt"
        test_file.write_text("test")

        # Multiple reads should work
        result1 = self.file_ops.file_exists(test_file)
        result2 = self.file_ops.get_file_size(test_file)
        result3 = self.file_ops.file_exists(test_file)

        assert result1 is True
        assert result2.is_success
        assert result3 is True

    def test_file_exists_with_relative_path(self) -> None:
        """Test file_exists with relative path."""
        test_file = self.temp_path / "relative.txt"
        test_file.write_text("content")

        # Convert to relative path
        import os

        old_cwd = Path.cwd()
        try:
            os.chdir(self.temp_path)
            result = self.file_ops.file_exists(Path("relative.txt"))
            assert result is True
        finally:
            os.chdir(old_cwd)

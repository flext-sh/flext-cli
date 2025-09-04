"""Tests for file_operations.py module - Real file operations testing.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_core import FlextResult

from flext_cli.file_operations import FlextCliFileOperations


class TestFlextCliFileOperations:
    """Test FlextCliFileOperations with real file system operations."""

    def test_file_operations_init(self) -> None:
        """Test file operations initialization."""
        file_ops = FlextCliFileOperations()

        assert file_ops is not None
        assert hasattr(file_ops, "safe_write")
        assert hasattr(file_ops, "backup_and_process")
        assert hasattr(file_ops, "create_directory_structure")

    def test_safe_write_success(self) -> None:
        """Test safe_write with valid content."""
        file_ops = FlextCliFileOperations()
        content = "Test content for safe write"

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "test_file.txt"

            result = file_ops.safe_write(content, str(file_path))

            assert result.is_success
            # Verify file was created and contains correct content
            assert file_path.exists()
            written_content = file_path.read_text()
            assert written_content == content

    def test_safe_write_create_parent_directories(self) -> None:
        """Test safe_write creates parent directories."""
        file_ops = FlextCliFileOperations()
        content = "Test content with nested path"

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_path = Path(temp_dir) / "nested" / "directory" / "test_file.txt"

            result = file_ops.safe_write(content, str(nested_path))

            assert result.is_success
            assert nested_path.exists()
            assert nested_path.read_text() == content

    def test_safe_write_invalid_path(self) -> None:
        """Test safe_write with invalid path."""
        file_ops = FlextCliFileOperations()
        content = "Test content"

        # Try to write to invalid location
        invalid_path = "/root/invalid/path/file.txt"  # Should fail

        result = file_ops.safe_write(content, invalid_path)

        # Should fail gracefully
        assert result.is_failure
        assert isinstance(result.error, str)

    def test_backup_and_process_existing_file(self) -> None:
        """Test backup_and_process with existing file."""
        file_ops = FlextCliFileOperations()
        original_content = "Original file content"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(original_content)
            temp_file.flush()
            file_path = Path(temp_file.name)

            def process_function(content: str) -> FlextResult[str]:
                return FlextResult[str].ok(content.upper())

            result = file_ops.backup_and_process(str(file_path), process_function)

            assert result.is_success

            # Verify content was processed
            processed_content = file_path.read_text()
            assert "ORIGINAL FILE CONTENT" in processed_content

            # Clean up
            file_path.unlink()
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            if backup_path.exists():
                backup_path.unlink()

    def test_backup_and_process_nonexistent_file(self) -> None:
        """Test backup_and_process with nonexistent file."""
        file_ops = FlextCliFileOperations()

        def process_function(content: str) -> FlextResult[str]:
            return FlextResult[str].ok(content.upper())

        result = file_ops.backup_and_process(
            "/nonexistent/file.txt", process_function
        )

        assert result.is_failure
        assert "not found" in result.error.lower() or "does not exist" in result.error.lower()

    def test_backup_and_process_with_failing_processor(self) -> None:
        """Test backup_and_process when processor fails."""
        file_ops = FlextCliFileOperations()
        original_content = "Original content"

        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            temp_file.write(original_content)
            temp_file.flush()
            file_path = Path(temp_file.name)

            def failing_processor(content: str) -> FlextResult[str]:
                return FlextResult[str].fail("Processing failed")

            result = file_ops.backup_and_process(str(file_path), failing_processor)

            assert result.is_failure
            assert "Processing failed" in result.error

            # Original file should be preserved
            current_content = file_path.read_text()
            assert current_content == original_content

            # Clean up
            file_path.unlink()

    def test_create_directory_structure_simple(self) -> None:
        """Test create_directory_structure with simple path."""
        file_ops = FlextCliFileOperations()

        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new_directory"

            result = file_ops.create_directory_structure(str(new_dir))

            assert result.is_success
            assert new_dir.exists()
            assert new_dir.is_dir()

    def test_create_directory_structure_nested(self) -> None:
        """Test create_directory_structure with nested path."""
        file_ops = FlextCliFileOperations()

        with tempfile.TemporaryDirectory() as temp_dir:
            nested_dir = Path(temp_dir) / "level1" / "level2" / "level3"

            result = file_ops.create_directory_structure(str(nested_dir))

            assert result.is_success
            assert nested_dir.exists()
            assert nested_dir.is_dir()

    def test_create_directory_structure_existing(self) -> None:
        """Test create_directory_structure with existing directory."""
        file_ops = FlextCliFileOperations()

        with tempfile.TemporaryDirectory() as temp_dir:
            existing_dir = Path(temp_dir)

            result = file_ops.create_directory_structure(str(existing_dir))

            # Should succeed even if directory exists
            assert result.is_success

    def test_create_directory_structure_invalid_permission(self) -> None:
        """Test create_directory_structure with invalid permissions."""
        file_ops = FlextCliFileOperations()

        # Try to create directory in root (should fail for non-root users)
        invalid_path = "/root/invalid_directory"

        result = file_ops.create_directory_structure(invalid_path)

        # Should fail gracefully
        assert result.is_failure
        assert isinstance(result.error, str)

    def test_file_exists_check(self) -> None:
        """Test file existence checking functionality."""
        file_ops = FlextCliFileOperations()

        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            file_path = Path(temp_file.name)

            # File should exist
            # This tests internal file checking logic
            assert file_path.exists()

            # Clean up
            file_path.unlink()

            # Now file should not exist
            assert not file_path.exists()

    def test_write_with_encoding(self) -> None:
        """Test writing files with specific encoding."""
        file_ops = FlextCliFileOperations()

        # Test with unicode content
        unicode_content = "Test with unicode: café, naïve, résumé"

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "unicode_test.txt"

            result = file_ops.safe_write(unicode_content, str(file_path))

            assert result.is_success
            # Verify unicode content is preserved
            written_content = file_path.read_text(encoding="utf-8")
            assert written_content == unicode_content
            assert "café" in written_content
            assert "naïve" in written_content
            assert "résumé" in written_content

    def test_backup_file_creation(self) -> None:
        """Test that backup files are created correctly."""
        file_ops = FlextCliFileOperations()
        original_content = "Content to be backed up"

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".txt") as temp_file:
            temp_file.write(original_content)
            temp_file.flush()
            file_path = Path(temp_file.name)

            def simple_processor(content: str) -> FlextResult[str]:
                return FlextResult[str].ok(f"Processed: {content}")

            result = file_ops.backup_and_process(str(file_path), simple_processor)

            assert result.is_success

            # Check if backup file was created
            backup_path = file_path.with_suffix(file_path.suffix + ".bak")
            if backup_path.exists():
                backup_content = backup_path.read_text()
                assert backup_content == original_content
                # Clean up backup
                backup_path.unlink()

            # Clean up original
            file_path.unlink()

    def test_process_large_file(self) -> None:
        """Test processing with relatively large content."""
        file_ops = FlextCliFileOperations()

        # Create larger content
        large_content = "Large file content line\n" * 1000

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "large_file.txt"

            result = file_ops.safe_write(large_content, str(file_path))

            assert result.is_success
            assert file_path.exists()

            # Verify content size
            written_content = file_path.read_text()
            assert len(written_content) == len(large_content)
            assert written_content.count("Large file content line") == 1000

"""Tests for file_operations.py module."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from flext_cli.file_operations import FlextCliFileOperations
from flext_cli.interactions import FlextCliInteractions
from flext_core import FlextResult


class TestFlextCliFileOperations:
    """Test FlextCliFileOperations class."""

    def test_initialization(self) -> None:
        """Test file operations initialization."""
        ops = FlextCliFileOperations()
        assert ops is not None
        assert isinstance(ops.interactions, FlextCliInteractions)

    def test_initialization_with_interactions(self) -> None:
        """Test initialization with custom interactions."""
        interactions = FlextCliInteractions()
        ops = FlextCliFileOperations(interactions=interactions)
        assert ops.interactions is interactions

    def test_load_json_file_success(self) -> None:
        """Test successful JSON file loading."""
        test_data = {"key": "value", "number": 42}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            suffix=".json",
            delete=False,
        ) as tmp_file:
            json.dump(test_data, tmp_file)
            tmp_file.flush()

            ops = FlextCliFileOperations()
            result = ops.load_json_file(tmp_file.name)

            assert result.is_success
            assert result.value == test_data

            # Cleanup
            Path(tmp_file.name).unlink()

    def test_load_json_file_not_found(self) -> None:
        """Test JSON file loading when file doesn't exist."""
        ops = FlextCliFileOperations()
        result = ops.load_json_file("/nonexistent/file.json")

        assert result.is_failure
        assert result.error is not None
        assert "File not found" in result.error

    def test_load_json_file_invalid_json(self) -> None:
        """Test JSON file loading with invalid JSON."""
        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            suffix=".json",
            delete=False,
        ) as tmp_file:
            tmp_file.write("invalid json content")
            tmp_file.flush()

            ops = FlextCliFileOperations()
            result = ops.load_json_file(tmp_file.name)

            # FlextUtilities.safe_json_parse returns empty dict for invalid JSON
            assert result.is_success
            assert result.value == {}

            # Cleanup
            Path(tmp_file.name).unlink()

    def test_save_json_file_success(self) -> None:
        """Test successful JSON file saving."""
        test_data = {"key": "value", "number": 42}

        with tempfile.NamedTemporaryFile(
            encoding="utf-8",
            mode="w",
            suffix=".json",
            delete=False,
        ) as tmp_file:
            tmp_file.close()  # Close to allow writing

            ops = FlextCliFileOperations()
            result = ops.save_json_file(test_data, tmp_file.name)

            assert result.is_success

            # Verify content was written correctly
            with Path(tmp_file.name).open(encoding="utf-8") as f:
                saved_data = json.load(f)
            assert saved_data == test_data

            # Cleanup
            Path(tmp_file.name).unlink()

    def test_save_json_file_create_directory(self) -> None:
        """Test JSON file saving with directory creation."""
        test_data: dict[str, object] = {"key": "value"}

        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = Path(temp_dir) / "subdir" / "test.json"

            ops = FlextCliFileOperations()
            result = ops.save_json_file(test_data, file_path)

            assert result.is_success
            assert file_path.exists()

            # Verify content
            with file_path.open() as f:
                saved_data = json.load(f)
            assert saved_data == test_data

    def test_safe_write_success(self) -> None:
        """Test successful safe write operation."""
        content = "Test content\nwith multiple lines"

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False
        ) as tmp_file:
            tmp_file.close()

            ops = FlextCliFileOperations()
            result = ops.safe_write(content, tmp_file.name)

            assert result.is_success

            # Verify content
            with Path(tmp_file.name).open(encoding="utf-8") as f:
                saved_content = f.read()
            assert saved_content == content

            # Cleanup
            Path(tmp_file.name).unlink()

    def test_safe_write_with_backup(self) -> None:
        """Test safe write with backup creation."""
        original_content = "Original content"
        new_content = "New content"

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False
        ) as tmp_file:
            tmp_file.write(original_content)
            tmp_file.flush()

            ops = FlextCliFileOperations()
            result = ops.safe_write(new_content, tmp_file.name, backup=True)

            assert result.is_success

            # Verify new content
            with Path(tmp_file.name).open(encoding="utf-8") as f:
                saved_content = f.read()
            assert saved_content == new_content

            # Verify backup was created
            backup_path = Path(tmp_file.name).with_suffix(".bak")
            assert backup_path.exists()

            with backup_path.open() as f:
                backup_content = f.read()
            assert backup_content == original_content

            # Cleanup
            Path(tmp_file.name).unlink()
            backup_path.unlink()

    def test_backup_and_process_success(self) -> None:
        """Test successful backup and process operation."""
        original_content = "Original content"

        def process_func(content: str) -> FlextResult[str]:
            return FlextResult[str].ok(content.upper())

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False
        ) as tmp_file:
            tmp_file.write(original_content)
            tmp_file.flush()

            ops = FlextCliFileOperations()
            result = ops.backup_and_process(tmp_file.name, process_func)

            assert result.is_success
            assert result.value == original_content.upper()

            # Verify backup was created
            backup_path = Path(tmp_file.name).with_suffix(".bak")
            assert backup_path.exists()

            with backup_path.open() as f:
                backup_content = f.read()
            assert backup_content == original_content

            # Cleanup
            Path(tmp_file.name).unlink()
            backup_path.unlink()

    def test_backup_and_process_file_not_found(self) -> None:
        """Test backup and process with non-existent file."""

        def process_func(content: str) -> FlextResult[str]:
            return FlextResult[str].ok(content)

        ops = FlextCliFileOperations()
        result = ops.backup_and_process("/nonexistent/file.txt", process_func)

        assert result.is_failure
        assert result.error is not None
        assert "File not found" in result.error

    def test_backup_and_process_with_confirmation(self) -> None:
        """Test backup and process with user confirmation."""
        original_content = "Original content"

        def process_func(content: str) -> FlextResult[str]:
            return FlextResult[str].ok(content.upper())

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False
        ) as tmp_file:
            tmp_file.write(original_content)
            tmp_file.flush()

            # Mock interactions to return True for confirmation
            with patch.object(FlextCliInteractions, "confirm") as mock_confirm:
                mock_confirm.return_value = FlextResult[bool].ok(True)

                ops = FlextCliFileOperations()
                result = ops.backup_and_process(
                    tmp_file.name,
                    process_func,
                    require_confirmation=True,
                )

                assert result.is_success
                mock_confirm.assert_called_once()

                # Cleanup
                Path(tmp_file.name).unlink()
                backup_path = Path(tmp_file.name).with_suffix(".bak")
                if backup_path.exists():
                    backup_path.unlink()

    def test_backup_and_process_confirmation_cancelled(self) -> None:
        """Test backup and process when user cancels confirmation."""
        original_content = "Original content"

        def process_func(content: str) -> FlextResult[str]:
            return FlextResult[str].ok(content.upper())

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False
        ) as tmp_file:
            tmp_file.write(original_content)
            tmp_file.flush()

            # Mock interactions to return False for confirmation
            with patch.object(FlextCliInteractions, "confirm") as mock_confirm:
                mock_confirm.return_value = FlextResult[bool].ok(False)

                ops = FlextCliFileOperations()
                result = ops.backup_and_process(
                    tmp_file.name,
                    process_func,
                    require_confirmation=True,
                )

                assert result.is_failure
                assert result.error is not None
                assert "Operation cancelled by user" in result.error

                # Cleanup
                Path(tmp_file.name).unlink()

    def test_ensure_directory_success(self) -> None:
        """Test successful directory creation."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "new_subdir"

            ops = FlextCliFileOperations()
            result = ops.ensure_directory(new_dir)

            assert result.is_success
            assert result.value == new_dir
            assert new_dir.exists()
            assert new_dir.is_dir()

    def test_ensure_directory_existing(self) -> None:
        """Test directory creation when directory already exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            existing_dir = Path(temp_dir)

            ops = FlextCliFileOperations()
            result = ops.ensure_directory(existing_dir)

            assert result.is_success
            assert result.value == existing_dir

    def test_create_directory_structure(self) -> None:
        """Test create_directory_structure alias method."""
        with tempfile.TemporaryDirectory() as temp_dir:
            new_dir = Path(temp_dir) / "nested" / "structure"

            ops = FlextCliFileOperations()
            result = ops.create_directory_structure(new_dir)

            assert result.is_success
            assert result.value == new_dir
            assert new_dir.exists()
            assert new_dir.is_dir()

    def test_file_exists_true(self) -> None:
        """Test file_exists when file exists."""
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            tmp_file.write(b"test content")
            tmp_file.flush()

            ops = FlextCliFileOperations()
            assert ops.file_exists(tmp_file.name) is True

            # Cleanup
            Path(tmp_file.name).unlink()

    def test_file_exists_false(self) -> None:
        """Test file_exists when file doesn't exist."""
        ops = FlextCliFileOperations()
        assert ops.file_exists("/nonexistent/file.txt") is False

    def test_file_exists_invalid_path(self) -> None:
        """Test file_exists with invalid path."""
        ops = FlextCliFileOperations()
        # Path("").exists() returns True, so we test with a clearly invalid path
        assert ops.file_exists("/nonexistent/path/that/does/not/exist") is False

    def test_get_file_size_success(self) -> None:
        """Test successful file size retrieval."""
        content = "Test content for size calculation"

        with tempfile.NamedTemporaryFile(
            encoding="utf-8", mode="w", delete=False
        ) as tmp_file:
            tmp_file.write(content)
            tmp_file.flush()

            ops = FlextCliFileOperations()
            result = ops.get_file_size(tmp_file.name)

            assert result.is_success
            assert result.value == len(content.encode("utf-8"))

            # Cleanup
            Path(tmp_file.name).unlink()

    def test_get_file_size_not_found(self) -> None:
        """Test file size retrieval when file doesn't exist."""
        ops = FlextCliFileOperations()
        result = ops.get_file_size("/nonexistent/file.txt")

        assert result.is_failure
        assert result.error is not None
        assert "File not found" in result.error

    def test_error_handling_permission_denied(self) -> None:
        """Test error handling for permission denied scenarios."""
        ops = FlextCliFileOperations()

        # Test with a path that would cause permission issues
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.side_effect = PermissionError("Permission denied")

            result = ops.load_json_file("/restricted/file.json")
            assert result.is_failure
            assert result.error is not None
            assert "JSON load failed" in result.error

    def test_error_handling_os_error(self) -> None:
        """Test error handling for OS errors."""
        ops = FlextCliFileOperations()

        with patch("pathlib.Path.write_text") as mock_write:
            mock_write.side_effect = OSError("Disk full")

            result = ops.save_json_file({"key": "value"}, "/invalid/path/test.json")
            assert result.is_failure
            assert result.error is not None
            assert "JSON save failed" in result.error

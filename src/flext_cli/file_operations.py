"""FLEXT CLI File Operations - File management utilities following flext-core patterns.

Provides FlextCliFileOperations class for safe file operations with backup,
JSON handling, and secure write operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

from flext_core import FlextResult

from flext_cli.constants import FlextCliConstants
from flext_cli.interactions import FlextCliInteractions


class FlextCliFileOperations:
    """Consolidated file operations following flext-core patterns.

    Provides comprehensive file management operations including safe writes,
    backup operations, JSON handling, and secure file operations with
    FlextResult error handling throughout.

    Features:
        - Safe file writing with backup support
        - JSON file loading and saving
        - File processing with confirmation
        - Secure directory creation
        - Atomic file operations
    """

    def __init__(self, *, interactions: FlextCliInteractions | None = None) -> None:
        """Initialize file operations manager.

        Args:
            interactions: Optional interactions manager for confirmations

        """
        self.interactions = interactions or FlextCliInteractions()

    def load_json_file(self, path: str | Path) -> FlextResult[dict[str, object]]:
        """Load JSON data from file with error handling.

        Args:
            path: Path to JSON file

        Returns:
            FlextResult containing loaded JSON data as dictionary

        """
        try:
            file_path = Path(path)
            if not file_path.exists():
                return FlextResult[dict[str, object]].fail(f"File not found: {path}")

            content = file_path.read_text(encoding=FlextCliConstants.DEFAULT_ENCODING)
            data = json.loads(content)

            if not isinstance(data, dict):
                return FlextResult[dict[str, object]].fail(
                    f"JSON file must contain object, got {type(data).__name__}"
                )

            return FlextResult[dict[str, object]].ok(data)
        except json.JSONDecodeError as e:
            return FlextResult[dict[str, object]].fail(f"Invalid JSON: {e}")
        except Exception as e:
            return FlextResult[dict[str, object]].fail(f"JSON load failed: {e}")

    def save_json_file(
        self, data: dict[str, object], path: str | Path, *, indent: int = 2
    ) -> FlextResult[None]:
        """Save data to JSON file with proper formatting.

        Args:
            data: Dictionary data to save
            path: Target file path
            indent: JSON indentation level

        Returns:
            FlextResult indicating success or failure

        """
        try:
            file_path = Path(path)
            file_path.parent.mkdir(parents=True, exist_ok=True)

            json_content = json.dumps(data, indent=indent, ensure_ascii=False)
            file_path.write_text(
                json_content, encoding=FlextCliConstants.DEFAULT_ENCODING
            )

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"JSON save failed: {e}")

    def safe_write(
        self, content: str, file_path: str | Path, *, backup: bool = False
    ) -> FlextResult[None]:
        """Write content to file with optional backup.

        Args:
            content: Content to write
            file_path: Target file path
            backup: Whether to create backup of existing file

        Returns:
            FlextResult indicating success or failure

        """
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)

            if backup and path.exists():
                backup_path = path.with_suffix(path.suffix + ".bak")
                existing_content = path.read_text(
                    encoding=FlextCliConstants.DEFAULT_ENCODING
                )
                backup_path.write_text(
                    existing_content, encoding=FlextCliConstants.DEFAULT_ENCODING
                )

            path.write_text(content, encoding=FlextCliConstants.DEFAULT_ENCODING)
            path.chmod(0o600)  # Secure permissions

            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Safe write failed: {e}")

    def backup_and_process(
        self,
        file_path: str | Path,
        process_func: Callable[[str], FlextResult[str]],
        *,
        require_confirmation: bool = False,
    ) -> FlextResult[str]:
        """Process file with backup and optional confirmation.

        Args:
            file_path: Path to file to process
            process_func: Function to process file content
            require_confirmation: Whether to require user confirmation

        Returns:
            FlextResult containing processed content

        """
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[str].fail(f"File not found: {file_path}")

            if require_confirmation:
                confirmation = self.interactions.confirm(
                    f"Process file {path.name}?", default=True
                )
                if confirmation.is_failure:
                    return FlextResult[str].fail(
                        f"Confirmation failed: {confirmation.error}"
                    )
                if not confirmation.value:
                    return FlextResult[str].fail("Operation cancelled by user")

            # Read original content
            original_content = path.read_text(
                encoding=FlextCliConstants.DEFAULT_ENCODING
            )

            # Process content
            process_result = process_func(original_content)
            if process_result.is_failure:
                return FlextResult[str].fail(
                    f"Processing failed: {process_result.error}"
                )

            # Create backup
            backup_path = path.with_suffix(path.suffix + ".bak")
            backup_path.write_text(
                original_content, encoding=FlextCliConstants.DEFAULT_ENCODING
            )

            # Write processed content
            path.write_text(
                process_result.value, encoding=FlextCliConstants.DEFAULT_ENCODING
            )

            return FlextResult[str].ok(process_result.value)
        except Exception as e:
            return FlextResult[str].fail(f"Backup and process failed: {e}")

    def ensure_directory(self, directory_path: str | Path) -> FlextResult[Path]:
        """Ensure directory exists with proper permissions.

        Args:
            directory_path: Directory path to create

        Returns:
            FlextResult containing created directory Path

        """
        try:
            path = Path(directory_path)
            path.mkdir(parents=True, exist_ok=True, mode=0o700)
            return FlextResult[Path].ok(path)
        except Exception as e:
            return FlextResult[Path].fail(f"Directory creation failed: {e}")

    def file_exists(self, file_path: str | Path) -> bool:
        """Check if file exists.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise

        """
        try:
            return Path(file_path).exists()
        except Exception:
            return False

    def get_file_size(self, file_path: str | Path) -> FlextResult[int]:
        """Get file size in bytes.

        Args:
            file_path: Path to file

        Returns:
            FlextResult containing file size in bytes

        """
        try:
            path = Path(file_path)
            if not path.exists():
                return FlextResult[int].fail(f"File not found: {file_path}")

            size = path.stat().st_size
            return FlextResult[int].ok(size)
        except Exception as e:
            return FlextResult[int].fail(f"File size check failed: {e}")


__all__ = ["FlextCliFileOperations"]

"""FLEXT CLI File Operations - File management utilities following flext-core patterns.

Provides FlextCliFileOperations class for safe file operations with backup,
JSON handling, and secure write operations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from pathlib import Path

from flext_cli.constants import FlextCliConstants
from flext_cli.interactions import FlextCliInteractions
from flext_core import FlextResult


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

    def _create_backup_and_write(
        self, path: Path, original_content: str, processed_content: str
    ) -> str:
        """Helper method for backup creation and content writing - used by safe_call.

        Returns:
            str: Description of return value.

        """
        # Create backup
        backup_path = path.with_suffix(path.suffix + ".bak")
        backup_path.write_text(
            original_content,
            encoding=FlextCliConstants.Files.default_encoding,
        )

        # Write processed content
        path.write_text(
            processed_content,
            encoding=FlextCliConstants.Files.default_encoding,
        )

        return processed_content

    def file_exists(self, file_path: str | Path) -> bool:
        """Check if file exists using railway pattern - NO try/except fallbacks.

        Args:
            file_path: Path to check

        Returns:
            True if file exists, False otherwise

        """

        def check_file_existence() -> bool:
            """Check file existence - used by safe_call.

            Returns:
            bool: Description of return value.

            """
            return Path(file_path).exists()

        # Railway pattern - return False for any failure (invalid path, permission denied, etc.)
        result = FlextResult[bool].safe_call(check_file_existence)
        return result.unwrap() if result.is_success else False

    def get_file_size(self, file_path: str | Path) -> FlextResult[int]:
        """Get file size in bytes using railway pattern - NO try/except fallbacks.

        Args:
            file_path: Path to file

        Returns:
            FlextResult containing file size in bytes

        """

        def validate_file_exists(path: Path) -> FlextResult[Path]:
            """Validate file exists.

            Returns:
            FlextResult[Path]: Description of return value.

            """
            if not path.exists():
                return FlextResult[Path].fail(f"File not found: {file_path}")
            return FlextResult[Path].ok(path)

        def get_file_stat(path: Path) -> FlextResult[int]:
            """Get file size from stat - used by safe_call.

            Returns:
            FlextResult[int]: Description of return value.

            """
            size_result = FlextResult[int].safe_call(lambda: path.stat().st_size)
            if size_result.is_failure:
                return FlextResult[int].fail(f"File stat failed: {size_result.error}")
            return size_result

        # Railway pattern composition - NO try/except needed
        path_result = FlextResult[Path].safe_call(lambda: Path(file_path))
        if path_result.is_failure:
            return FlextResult[int].fail(f"Invalid path: {file_path}")

        return path_result.flat_map(validate_file_exists).flat_map(get_file_stat)


__all__ = ["FlextCliFileOperations"]

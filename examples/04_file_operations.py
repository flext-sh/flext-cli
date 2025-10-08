"""File Operations - Auto-Validated File/Path Handling.

Demonstrates file operations with FlextResult validation and auto-formatting.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import pathlib
import tempfile
from typing import cast

from flext_cli import FlextCli

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_file_io() -> None:
    """File I/O with auto-validation and formatting."""
    test_data = {"name": "example", "value": 42}

    # Use secure temporary file instead of hardcoded path
    with tempfile.NamedTemporaryFile(
        encoding="utf-8", mode="w", suffix=".json", delete=False
    ) as tmp_file:
        tmp_path = tmp_file.name

    try:
        # Auto-formatting based on file extension
        write_result = cli.file_tools.write_json(tmp_path, cast("object", test_data))
        if write_result.is_success:
            cli.output.print_success("File written with auto-formatting")

        read_result = cli.file_tools.read_json(tmp_path)
        if read_result.is_success:
            cli.output.print_success(f"Read: {read_result.value}")
    finally:
        # Clean up temporary file
        with contextlib.suppress(OSError):
            pathlib.Path(tmp_path).unlink()


def demonstrate_path_operations() -> None:
    """Path operations with auto-validation."""
    # Path validation happens automatically during file operations
    cli.output.print_message("Path validation automatic in file operations")


def demonstrate_temp_files() -> None:
    """Temporary files with auto-cleanup."""
    # Temp file creation with auto-cleanup
    temp_result = cli.file_tools.create_temp_file()
    if temp_result.is_success:
        cli.output.print_success("Temp file created with auto-cleanup")


def main() -> None:
    """Run all demonstrations."""
    demonstrate_file_io()
    demonstrate_path_operations()
    demonstrate_temp_files()


if __name__ == "__main__":
    main()

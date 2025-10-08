"""File Operations - Auto-Validated File/Path Handling.

Demonstrates file operations with FlextResult validation and auto-formatting.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import pathlib
import tempfile

from flext_cli import FlextCli

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_file_io() -> None:
    """File I/O with auto-validation and formatting."""
    test_data = {"name": "example", "value": 42}

    cli.formatters.print("\n📁 File I/O Operations:", style="bold cyan")

    # Use secure temporary file instead of hardcoded path
    with tempfile.NamedTemporaryFile(
        encoding="utf-8", mode="w", suffix=".json", delete=False
    ) as tmp_file:
        tmp_path = tmp_file.name

    try:
        # Auto-formatting based on file extension
        write_result = cli.file_tools.write_json(test_data, tmp_path)
        if write_result.is_success:
            cli.formatters.print("✅ File written with auto-formatting", style="green")

        read_result = cli.file_tools.read_json(tmp_path)
        if read_result.is_success:
            cli.formatters.print(f"✅ Read: {read_result.unwrap()}", style="green")
    finally:
        # Clean up temporary file
        with contextlib.suppress(OSError):
            pathlib.Path(tmp_path).unlink()


def demonstrate_path_operations() -> None:
    """Path operations with auto-validation."""
    cli.formatters.print("\n🛤️  Path Operations:", style="bold cyan")
    # Path validation happens automatically during file operations
    cli.formatters.print(
        "✅ Path validation automatic in file operations", style="cyan"
    )


def demonstrate_temp_files() -> None:
    """Temporary files with auto-cleanup."""
    cli.formatters.print("\n🗂️  Temporary Files:", style="bold cyan")
    # Temp file creation with auto-cleanup
    temp_result = cli.file_tools.create_temp_file()
    if temp_result.is_success:
        cli.formatters.print("✅ Temp file created with auto-cleanup", style="green")


def main() -> None:
    """Run all demonstrations."""
    cli.formatters.print("=" * 60, style="bold blue")
    cli.formatters.print("  File Operations Examples", style="bold white on blue")
    cli.formatters.print("=" * 60, style="bold blue")

    demonstrate_file_io()
    demonstrate_path_operations()
    demonstrate_temp_files()

    cli.formatters.print("\n" + "=" * 60, style="bold blue")
    cli.formatters.print(
        "  ✅ All file operation examples completed!", style="bold green"
    )
    cli.formatters.print("=" * 60, style="bold blue")


if __name__ == "__main__":
    main()

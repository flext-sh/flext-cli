"""Advanced File Formats - CSV, Binary, Auto-Detection.

Shows file operations beyond JSON/YAML: CSV with headers, binary files, format auto-detection.

WHEN TO USE:
- Need CSV import/export with headers
- Working with binary files (images, PDFs, etc.)
- Want automatic format detection
- Building data export tools
- Processing mixed file formats

FLEXT-CLI PROVIDES:
- CSV with headers (read_csv_file_with_headers, write_csv_file)
- Binary files (read_binary_file, write_binary_file)
- Auto-format detection (detect_file_format, load_file_auto)
- Text files (read_text_file, write_text_file)
- File operations (copy_file)

HOW TO USE IN YOUR CLI:
Handle all file formats with automatic detection and proper encoding.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import hashlib
import shutil
import tempfile
from pathlib import Path
from typing import cast

from flext_cli import FlextCli, FlextCliTables
from flext_cli.typings import FlextCliTypes

cli = FlextCli.get_instance()
tables = FlextCliTables()


# ============================================================================
# PATTERN 1: CSV export/import with headers
# ============================================================================


def export_to_csv(
    data: list[FlextCliTypes.Data.CliDataDict], output_file: Path
) -> None:
    """Export data to CSV with proper headers."""
    if not data:
        cli.print("⚠️  No data to export", style="yellow")
        return

    cli.print(f"\n📊 Exporting to CSV: {output_file.name}", style="bold cyan")

    # Extract headers from first row
    headers = list(data[0].keys())

    # Prepare rows (headers as first row, then data)
    rows = [headers]  # First row is headers
    rows.extend([[str(row.get(header, "")) for header in headers] for row in data])

    # Write CSV (headers included as first row)
    write_result = cli.file_tools.write_csv_file(output_file, rows)

    if write_result.is_success:
        size = output_file.stat().st_size
        cli.print(f"✅ Exported {len(data)} rows to CSV ({size} bytes)", style="green")
    else:
        cli.print(f"❌ Export failed: {write_result.error}", style="bold red")


def import_from_csv(input_file: Path) -> list[FlextCliTypes.Data.CliDataDict] | None:
    """Import data from CSV with headers."""
    cli.print(f"\n📥 Importing from CSV: {input_file.name}", style="bold cyan")

    # Read CSV with headers
    read_result = cli.file_tools.read_csv_file_with_headers(input_file)

    if read_result.is_failure:
        cli.print(f"❌ Import failed: {read_result.error}", style="bold red")
        return []

    rows = read_result.unwrap()
    cli.print(f"✅ Imported {len(rows)} rows from CSV", style="green")

    # Display sample rows
    if rows:
        cli.print("\n📋 Sample Data:", style="yellow")
        # Cast to expected type
        sample_rows: list[FlextCliTypes.Data.CliDataDict] = cast(
            "list[FlextCliTypes.Data.CliDataDict]", rows[:5]
        )
        # Cast to expected type for table creation
        table_result = tables.create_table(sample_rows, table_format="grid")
        if table_result.is_success:
            pass

    # Cast to expected return type (runtime type is compatible)
    return cast("list[FlextCliTypes.Data.CliDataDict]", rows)


# ============================================================================
# PATTERN 2: Binary file operations
# ============================================================================


def process_binary_file(input_file: Path, output_file: Path) -> None:
    """Read, process, and write binary files."""
    cli.print(f"\n🔧 Processing Binary File: {input_file.name}", style="bold cyan")

    # Read binary file
    read_result = cli.file_tools.read_binary_file(input_file)

    if read_result.is_failure:
        cli.print(f"❌ Read failed: {read_result.error}", style="bold red")
        return

    data = read_result.unwrap()
    cli.print(f"✅ Read {len(data)} bytes", style="green")

    # Calculate checksum
    checksum = hashlib.sha256(data).hexdigest()
    cli.print(f"   MD5 checksum: {checksum}", style="cyan")

    # Process data (example: simple transformation)
    # In real usage: compress, encrypt, resize image, etc.
    processed_data = data  # Placeholder for actual processing

    # Write binary file
    write_result = cli.file_tools.write_binary_file(output_file, processed_data)

    if write_result.is_success:
        cli.print(
            f"✅ Wrote {len(processed_data)} bytes to {output_file.name}", style="green"
        )
    else:
        cli.print(f"❌ Write failed: {write_result.error}", style="bold red")


# ============================================================================
# PATTERN 3: Automatic format detection
# ============================================================================


def load_any_format_file(file_path: Path) -> FlextCliTypes.Data.CliDataDict | None:
    """Load config from ANY format - automatically detected."""
    cli.print(f"\n🔍 Auto-Detecting Format: {file_path.name}", style="bold cyan")

    # Detect format from extension
    format_result = cli.file_tools.detect_file_format(file_path)

    if format_result.is_failure:
        cli.print(
            f"❌ Format detection failed: {format_result.error}", style="bold red"
        )
        return None

    detected_format = format_result.unwrap()
    cli.print(f"✅ Detected format: {detected_format.upper()}", style="green")

    # Load with auto-detection
    load_result = cli.file_tools.load_file_auto_detect(file_path)

    if load_result.is_failure:
        cli.print(f"❌ Load failed: {load_result.error}", style="bold red")
        return None

    data = load_result.unwrap()
    cli.print("✅ Loaded data successfully", style="green")

    # Type narrowing: ensure we have a dict
    if not isinstance(data, dict):
        cli.print(
            f"⚠️  Loaded data is not a dict[str, object] (type: {type(data).__name__})",
            style="yellow",
        )
        return None

    # Display loaded data
    # Cast to expected type
    display_data: FlextCliTypes.Data.CliDataDict = cast(
        "FlextCliTypes.Data.CliDataDict", data
    )
    table_result = cli.create_table(
        data=display_data,
        headers=["Key", "Value"],
        title=f"Loaded from {detected_format.upper()}",
    )
    if table_result.is_success:
        cli.print_table(table_result.unwrap())

    # Cast to expected return type (runtime type is compatible)
    return cast("FlextCliTypes.Data.CliDataDict", data)


# ============================================================================
# PATTERN 4: Multi-format export
# ============================================================================


def export_data_multi_format(
    data: FlextCliTypes.Data.CliDataDict | list[FlextCliTypes.Data.CliDataDict],
    base_path: Path,
) -> dict[str, str]:
    """Export same data to multiple formats (JSON, YAML, CSV)."""
    cli.print(f"\n💾 Multi-Format Export: {base_path.stem}", style="bold cyan")

    export_results = {}

    # Export to JSON
    json_path = base_path.with_suffix(".json")
    json_result = cli.file_tools.write_json_file(json_path, data, indent=2)
    if json_result.is_success:
        size = json_path.stat().st_size
        export_results["JSON"] = f"{size} bytes"
        cli.print(f"✅ JSON: {json_path.name} ({size} bytes)", style="green")

    # Export to YAML
    yaml_path = base_path.with_suffix(".yaml")
    yaml_result = cli.file_tools.write_yaml_file(yaml_path, data)
    if yaml_result.is_success:
        size = yaml_path.stat().st_size
        export_results["YAML"] = f"{size} bytes"
        cli.print(f"✅ YAML: {yaml_path.name} ({size} bytes)", style="green")

    # Export to CSV (if data is list of dicts)
    if isinstance(data, list) and data and isinstance(data[0], dict):
        csv_path = base_path.with_suffix(".csv")
        headers = list(data[0].keys())
        # Prepend headers as first row
        rows = [headers]
        rows.extend([[str(row.get(h, "")) for h in headers] for row in data])

        csv_result = cli.file_tools.write_csv_file(csv_path, rows)
        if csv_result.is_success:
            size = csv_path.stat().st_size
            export_results["CSV"] = f"{size} bytes"
            cli.print(f"✅ CSV: {csv_path.name} ({size} bytes)", style="green")

    # Summary
    cli.print(f"\n📊 Exported to {len(export_results)} formats", style="bold green")
    return export_results


# ============================================================================
# PATTERN 5: Text file operations with encoding
# ============================================================================


def process_text_file(input_file: Path, output_file: Path) -> None:
    """Read and write text files with proper encoding."""
    cli.print(f"\n📝 Processing Text File: {input_file.name}", style="bold cyan")

    # Read text file
    read_result = cli.file_tools.read_text_file(input_file)

    if read_result.is_failure:
        cli.print(f"❌ Read failed: {read_result.error}", style="bold red")
        return

    content = read_result.unwrap()
    cli.print(f"✅ Read {len(content)} characters", style="green")
    cli.print(f"   Lines: {content.count(chr(10)) + 1}", style="cyan")
    cli.print(f"   Words: {len(content.split())}", style="cyan")

    # Process content (example: uppercase)
    processed = content.upper()

    # Write text file
    write_result = cli.file_tools.write_text_file(output_file, processed)

    if write_result.is_success:
        cli.print(
            f"✅ Wrote {len(processed)} characters to {output_file.name}", style="green"
        )


# ============================================================================
# PATTERN 6: File copy with verification
# ============================================================================


def copy_file_with_verification(source: Path, destination: Path) -> bool:
    """Copy file and verify integrity."""
    cli.print(
        f"\n📋 Copying File: {source.name} → {destination.name}", style="bold cyan"
    )

    # Calculate source checksum
    source_data = source.read_bytes()
    source_hash = hashlib.sha256(source_data).hexdigest()
    cli.print(f"   Source MD5: {source_hash}", style="cyan")

    # Copy file
    copy_result = cli.file_tools.copy_file(source, destination)

    if copy_result.is_failure:
        cli.print(f"❌ Copy failed: {copy_result.error}", style="bold red")
        return False

    cli.print("✅ File copied successfully", style="green")

    # Verify copy
    dest_data = destination.read_bytes()
    dest_hash = hashlib.sha256(dest_data).hexdigest()
    cli.print(f"   Dest MD5: {dest_hash}", style="cyan")

    if source_hash == dest_hash:
        cli.print("✅ Integrity verified - checksums match!", style="bold green")
        return True
    cli.print("❌ Integrity check failed - checksums differ!", style="bold red")
    return False


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of advanced file format operations in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Advanced File Formats Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")

    # Setup temp directory
    temp_dir = Path(tempfile.gettempdir()) / "flext_advanced_files"
    temp_dir.mkdir(exist_ok=True)

    # Example 1: CSV operations
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("1. CSV Export/Import:", style="bold cyan")

    sample_data = [
        {"id": 1, "name": "Alice", "department": "Engineering", "salary": "100000"},
        {"id": 2, "name": "Bob", "department": "Sales", "salary": "80000"},
        {"id": 3, "name": "Charlie", "department": "Marketing", "salary": "90000"},
    ]

    csv_file = temp_dir / "employees.csv"
    # Cast to expected type for export function
    typed_sample_data = cast("list[FlextCliTypes.Data.CliDataDict]", sample_data)
    export_to_csv(typed_sample_data, csv_file)
    import_from_csv(csv_file)

    # Example 2: Binary files
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("2. Binary File Processing:", style="bold cyan")

    # Create a sample binary file
    binary_input = temp_dir / "input.bin"
    binary_output = temp_dir / "output.bin"
    binary_input.write_bytes(b"Binary data example content" * 100)

    process_binary_file(binary_input, binary_output)

    # Example 3: Auto-format detection
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("3. Auto-Format Detection:", style="bold cyan")

    # Create test files in different formats
    test_config = {"app": "test", "version": "1.0", "debug": True}

    json_file = temp_dir / "config.json"
    yaml_file = temp_dir / "config.yaml"

    cli.file_tools.write_json_file(json_file, test_config)
    cli.file_tools.write_yaml_file(yaml_file, test_config)

    load_any_format_file(json_file)
    load_any_format_file(yaml_file)

    # Example 4: Multi-format export
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("4. Multi-Format Export:", style="bold cyan")

    multi_data: list[FlextCliTypes.Data.CliDataDict] = [
        {"metric": "CPU", "value": "75%", "status": "OK"},
        {"metric": "Memory", "value": "82%", "status": "Warning"},
        {"metric": "Disk", "value": "45%", "status": "OK"},
    ]

    # multi_data is already properly typed
    export_data_multi_format(multi_data, temp_dir / "metrics")

    # Example 5: Text file processing
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("5. Text File Processing:", style="bold cyan")

    text_input = temp_dir / "input.txt"
    text_output = temp_dir / "output.txt"
    text_input.write_text("Hello, World!\nThis is a test file.\nWith multiple lines.")

    process_text_file(text_input, text_output)

    # Example 6: File copy with verification
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("6. File Copy with Verification:", style="bold cyan")

    # Recreate json_file for copy verification demo
    demo_config = {"app": "demo", "version": "2.0", "enabled": True}
    demo_json = temp_dir / "demo_config.json"
    cli.file_tools.write_json_file(demo_json, demo_config)

    copy_file_with_verification(demo_json, temp_dir / "demo_config_backup.json")

    # Cleanup

    shutil.rmtree(temp_dir, ignore_errors=True)

    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Advanced File Format Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")

    # Integration guide
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print(
        "  • CSV: Use read_csv_file_with_headers() for structured data", style="white"
    )
    cli.print(
        "  • Binary: Use read_binary_file() for images, PDFs, etc.", style="white"
    )
    cli.print("  • Auto-detect: Use load_file_auto() for flexible input", style="white")
    cli.print(
        "  • Multi-format: Export to JSON, YAML, CSV simultaneously", style="white"
    )
    cli.print(
        "  • Verification: Calculate checksums for integrity checks", style="white"
    )


if __name__ == "__main__":
    main()

"""Advanced File Formats - CSV, Binary, Auto-Detection.

Shows file operations beyond JSON/YAML: CSV with headers, binary files,
format auto-detection.

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

from flext_cli import FlextCli, FlextCliTables, m, t, u

cli = FlextCli()
tables = FlextCliTables()


# ============================================================================
# PATTERN 1: CSV export/import with headers
# ============================================================================


def export_to_csv(
    data: list[dict[str, t.JsonValue]],
    output_file: Path,
) -> None:
    """Export data to CSV with proper headers."""
    if not data:
        cli.output.print_message("⚠️  No data to export", style="yellow")
        return

    cli.output.print_message(
        f"\n📊 Exporting to CSV: {output_file.name}",
        style="bold cyan",
    )

    # Extract headers from first row
    headers = list(data[0].keys())

    # Prepare rows (headers as first row, then data)
    rows = [headers]  # First row is headers
    rows.extend([[str(row.get(header, "")) for header in headers] for row in data])

    # Write CSV (headers included as first row)
    write_result = cli.file_tools.write_csv_file(output_file, rows)

    if write_result.is_success:
        size = output_file.stat().st_size
        cli.output.print_message(
            f"✅ Exported {len(data)} rows to CSV ({size} bytes)",
            style="green",
        )
    else:
        cli.output.print_message(
            f"❌ Export failed: {write_result.error}",
            style="bold red",
        )


def import_from_csv(input_file: Path) -> list[dict[str, t.JsonValue]] | None:
    """Import data from CSV with headers."""
    cli.output.print_message(
        f"\n📥 Importing from CSV: {input_file.name}",
        style="bold cyan",
    )

    # Read CSV with headers
    read_result = cli.file_tools.read_csv_file_with_headers(input_file)

    if read_result.is_failure:
        cli.output.print_message(
            f"❌ Import failed: {read_result.error}",
            style="bold red",
        )
        return []

    rows = read_result.value
    cli.output.print_message(f"✅ Imported {len(rows)} rows from CSV", style="green")

    # Display sample rows
    if rows:
        cli.output.print_message("\n📋 Sample Data:", style="yellow")
        # Convert to JsonDict-compatible format using u
        sample_rows_raw = rows[:5]
        # Use u.map to convert list items to JSON
        sample_rows: list[dict[str, t.JsonValue]] = list(
            u.Cli.map(
                sample_rows_raw,
                mapper=lambda row: (
                    u.transform(
                        row,
                        to_json=True,
                    ).value
                    if isinstance(row, dict)
                    and u.transform(
                        row,
                        to_json=True,
                    ).is_success
                    else row
                ),
            ),
        )
        # Cast to expected type for table creation - t.Cli.TableData is Sequence[JsonDict] | JsonDict | Sequence[Sequence[t.GeneralValueType]]
        config = m.Cli.TableConfig(table_format="grid")
        # sample_rows is already Sequence[dict[str, t.GeneralValueType]] which is compatible with t.Cli.TableData
        # t.Cli.TableData accepts Sequence[JsonDict] which is compatible with Sequence[dict[str, t.GeneralValueType]]
        table_result = tables.create_table(
            sample_rows,
            config=config,
        )
        if table_result.is_success:
            pass

    # Convert to JsonDict-compatible format using u
    # Use u.map to convert list items to JSON
    converted_rows: list[dict[str, t.JsonValue]] = list(
        u.Cli.map(
            rows,
            mapper=lambda row: (
                u.transform(
                    row,
                    to_json=True,
                ).value
                if isinstance(row, dict)
                and u.transform(
                    row,
                    to_json=True,
                ).is_success
                else row
            ),
        ),
    )
    return converted_rows


# ============================================================================
# PATTERN 2: Binary file operations
# ============================================================================


def process_binary_file(input_file: Path, output_file: Path) -> None:
    """Read, process, and write binary files."""
    cli.output.print_message(
        f"\n🔧 Processing Binary File: {input_file.name}",
        style="bold cyan",
    )

    # Read binary file
    read_result = cli.file_tools.read_binary_file(input_file)

    if read_result.is_failure:
        cli.output.print_message(
            f"❌ Read failed: {read_result.error}",
            style="bold red",
        )
        return

    data = read_result.value
    cli.output.print_message(f"✅ Read {len(data)} bytes", style="green")

    # Calculate checksum
    checksum = hashlib.sha256(data).hexdigest()
    cli.output.print_message(f"   MD5 checksum: {checksum}", style="cyan")

    # Process data (example: simple transformation)
    # In real usage: compress, encrypt, resize image, etc.
    processed_data = data  # Placeholder for actual processing

    # Write binary file
    write_result = cli.file_tools.write_binary_file(output_file, processed_data)

    if write_result.is_success:
        cli.output.print_message(
            f"✅ Wrote {len(processed_data)} bytes to {output_file.name}",
            style="green",
        )
    else:
        cli.output.print_message(
            f"❌ Write failed: {write_result.error}",
            style="bold red",
        )


# ============================================================================
# PATTERN 3: Automatic format detection
# ============================================================================


def load_any_format_file(file_path: Path) -> dict[str, t.JsonValue] | None:
    """Load config from ANY format - automatically detected."""
    cli.output.print_message(
        f"\n🔍 Auto-Detecting Format: {file_path.name}",
        style="bold cyan",
    )

    # Detect format from extension
    format_result = cli.file_tools.detect_file_format(file_path)

    if format_result.is_failure:
        cli.output.print_message(
            f"❌ Format detection failed: {format_result.error}",
            style="bold red",
        )
        return None

    detected_format = format_result.value
    cli.output.print_message(
        f"✅ Detected format: {detected_format.upper()}",
        style="green",
    )

    # Load with auto-detection
    load_result = cli.file_tools.load_file_auto_detect(file_path)

    if load_result.is_failure:
        cli.output.print_message(
            f"❌ Load failed: {load_result.error}",
            style="bold red",
        )
        return None

    data = load_result.value
    cli.output.print_message("✅ Loaded data successfully", style="green")

    # Type narrowing: ensure we have a dict
    if not isinstance(data, dict):
        cli.output.print_message(
            (
                f"⚠️  Loaded data is not a dict[str, t.JsonValue] "
                f"(type: {type(data).__name__})"
            ),
            style="yellow",
        )
        return None

    # Display loaded data
    # Use u.transform for JSON conversion
    transform_result = u.transform(
        data,
        to_json=True,
    )
    display_data: dict[str, t.JsonValue] = transform_result.map_or(data)
    # Cast to dict[str, t.GeneralValueType] for create_table
    table_result = cli.create_table(
        data=display_data,
        headers=["Key", "Value"],
        _title=f"Loaded from {detected_format.upper()}",
    )
    if table_result.is_success:
        cli.print_table(table_result.value)

    # Convert to JsonDict-compatible dict using u
    # Use u.transform for JSON conversion
    transform_result = u.transform(data, to_json=True)
    return transform_result.map_or(data)


# ============================================================================
# PATTERN 4: Multi-format export
# ============================================================================


def export_data_multi_format(
    data: dict[str, t.JsonValue] | list[dict[str, t.JsonValue]],
    base_path: Path,
) -> dict[str, str]:
    """Export same data to multiple formats (JSON, YAML, CSV)."""
    cli.output.print_message(
        f"\n💾 Multi-Format Export: {base_path.stem}",
        style="bold cyan",
    )

    export_results = {}

    # Export to JSON
    json_path = base_path.with_suffix(".json")
    # Handle both single dict and list of dicts - data is already JsonValue-compatible
    json_payload = data
    json_result = cli.file_tools.write_json_file(json_path, json_payload, indent=2)
    if json_result.is_success:
        size = json_path.stat().st_size
        export_results["JSON"] = f"{size} bytes"
        cli.output.print_message(
            f"✅ JSON: {json_path.name} ({size} bytes)",
            style="green",
        )

    # Export to YAML
    yaml_path = base_path.with_suffix(".yaml")
    # Data is already JsonValue-compatible
    yaml_payload = data
    yaml_result = cli.file_tools.write_yaml_file(yaml_path, yaml_payload)
    if yaml_result.is_success:
        size = yaml_path.stat().st_size
        export_results["YAML"] = f"{size} bytes"
        cli.output.print_message(
            f"✅ YAML: {yaml_path.name} ({size} bytes)",
            style="green",
        )

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
            cli.output.print_message(
                f"✅ CSV: {csv_path.name} ({size} bytes)",
                style="green",
            )

    # Summary
    cli.output.print_message(
        f"\n📊 Exported to {len(export_results)} formats",
        style="bold green",
    )
    return export_results


# ============================================================================
# PATTERN 5: Text file operations with encoding
# ============================================================================


def process_text_file(input_file: Path, output_file: Path) -> None:
    """Read and write text files with proper encoding."""
    cli.output.print_message(
        f"\n📝 Processing Text File: {input_file.name}",
        style="bold cyan",
    )

    # Read text file
    read_result = cli.file_tools.read_text_file(input_file)

    if read_result.is_failure:
        cli.output.print_message(
            f"❌ Read failed: {read_result.error}",
            style="bold red",
        )
        return

    content = read_result.value
    cli.output.print_message(f"✅ Read {len(content)} characters", style="green")
    cli.output.print_message(f"   Lines: {content.count(chr(10)) + 1}", style="cyan")
    cli.output.print_message(f"   Words: {len(content.split())}", style="cyan")

    # Process content (example: uppercase)
    processed = content.upper()

    # Write text file
    write_result = cli.file_tools.write_text_file(output_file, processed)

    if write_result.is_success:
        cli.output.print_message(
            f"✅ Wrote {len(processed)} characters to {output_file.name}",
            style="green",
        )


# ============================================================================
# PATTERN 6: File copy with verification
# ============================================================================


def copy_file_with_verification(source: Path, destination: Path) -> bool:
    """Copy file and verify integrity."""
    cli.output.print_message(
        f"\n📋 Copying File: {source.name} → {destination.name}",
        style="bold cyan",
    )

    # Calculate source checksum
    source_data = source.read_bytes()
    source_hash = hashlib.sha256(source_data).hexdigest()
    cli.output.print_message(f"   Source MD5: {source_hash}", style="cyan")

    # Copy file
    copy_result = cli.file_tools.copy_file(source, destination)

    if copy_result.is_failure:
        cli.output.print_message(
            f"❌ Copy failed: {copy_result.error}",
            style="bold red",
        )
        return False

    cli.output.print_message("✅ File copied successfully", style="green")

    # Verify copy
    dest_data = destination.read_bytes()
    dest_hash = hashlib.sha256(dest_data).hexdigest()
    cli.output.print_message(f"   Dest MD5: {dest_hash}", style="cyan")

    if source_hash == dest_hash:
        cli.output.print_message(
            "✅ Integrity verified - checksums match!",
            style="bold green",
        )
        return True
    cli.output.print_message(
        "❌ Integrity check failed - checksums differ!",
        style="bold red",
    )
    return False


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of advanced file format operations in YOUR code."""
    cli.output.print_message("=" * 70, style="bold blue")
    cli.output.print_message(
        "  Advanced File Formats Library Usage",
        style="bold white",
    )
    cli.output.print_message("=" * 70, style="bold blue")

    # Setup temp directory
    temp_dir = Path(tempfile.gettempdir()) / "flext_advanced_files"
    temp_dir.mkdir(exist_ok=True)

    # Example 1: CSV operations
    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    cli.output.print_message("1. CSV Export/Import:", style="bold cyan")

    sample_data = [
        {"id": 1, "name": "Alice", "department": "Engineering", "salary": "100000"},
        {"id": 2, "name": "Bob", "department": "Sales", "salary": "80000"},
        {"id": 3, "name": "Charlie", "department": "Marketing", "salary": "90000"},
    ]

    csv_file = temp_dir / "employees.csv"
    # Convert to JsonDict-compatible format using u
    # Use u.map to convert list items to JSON
    typed_sample_data: list[dict[str, t.JsonValue]] = list(
        u.Cli.map(
            sample_data,
            mapper=lambda row: (
                u.transform(
                    row,
                    to_json=True,
                ).value
                if isinstance(row, dict)
                and u.transform(
                    row,
                    to_json=True,
                ).is_success
                else row
            ),
        ),
    )
    export_to_csv(typed_sample_data, csv_file)
    import_from_csv(csv_file)

    # Example 2: Binary files
    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    cli.output.print_message("2. Binary File Processing:", style="bold cyan")

    # Create a sample binary file
    binary_input = temp_dir / "input.bin"
    binary_output = temp_dir / "output.bin"
    binary_input.write_bytes(b"Binary data example content" * 100)

    process_binary_file(binary_input, binary_output)

    # Example 3: Auto-format detection
    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    cli.output.print_message("3. Auto-Format Detection:", style="bold cyan")

    # Create test files in different formats
    test_config: dict[str, t.JsonValue] = {
        "app": "test",
        "version": "1.0",
        "debug": True,
    }

    json_file = temp_dir / "config.json"
    yaml_file = temp_dir / "config.yaml"

    cli.file_tools.write_json_file(json_file, test_config)
    cli.file_tools.write_yaml_file(yaml_file, test_config)

    load_any_format_file(json_file)
    load_any_format_file(yaml_file)

    # Example 4: Multi-format export
    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    cli.output.print_message("4. Multi-Format Export:", style="bold cyan")

    multi_data: list[dict[str, t.JsonValue]] = [
        {"metric": "CPU", "value": "75%", "status": "OK"},
        {"metric": "Memory", "value": "82%", "status": "Warning"},
        {"metric": "Disk", "value": "45%", "status": "OK"},
    ]

    # multi_data is already properly typed
    export_data_multi_format(multi_data, temp_dir / "metrics")

    # Example 5: Text file processing
    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    cli.output.print_message("5. Text File Processing:", style="bold cyan")

    text_input = temp_dir / "input.txt"
    text_output = temp_dir / "output.txt"
    text_input.write_text("Hello, World!\nThis is a test file.\nWith multiple lines.")

    process_text_file(text_input, text_output)

    # Example 6: File copy with verification
    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    cli.output.print_message("6. File Copy with Verification:", style="bold cyan")

    # Recreate json_file for copy verification demo
    demo_config: dict[str, t.JsonValue] = {
        "app": "demo",
        "version": "2.0",
        "enabled": True,
    }
    demo_json = temp_dir / "demo_config.json"
    cli.file_tools.write_json_file(demo_json, demo_config)

    copy_file_with_verification(demo_json, temp_dir / "demo_config_backup.json")

    # Cleanup

    shutil.rmtree(temp_dir, ignore_errors=True)

    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    cli.output.print_message(
        "  ✅ Advanced File Format Examples Complete",
        style="bold green",
    )
    cli.output.print_message("=" * 70, style="bold blue")

    # Integration guide
    cli.output.print_message("\n💡 Integration Tips:", style="bold cyan")
    cli.output.print_message(
        "  • CSV: Use read_csv_file_with_headers() for structured data",
        style="white",
    )
    cli.output.print_message(
        "  • Binary: Use read_binary_file() for images, PDFs, etc.",
        style="white",
    )
    cli.output.print_message(
        "  • Auto-detect: Use load_file_auto() for flexible input",
        style="white",
    )
    cli.output.print_message(
        "  • Multi-format: Export to JSON, YAML, CSV simultaneously",
        style="white",
    )
    cli.output.print_message(
        "  • Verification: Calculate checksums for integrity checks",
        style="white",
    )


if __name__ == "__main__":
    main()

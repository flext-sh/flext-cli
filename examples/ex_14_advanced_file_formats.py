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
from collections.abc import (
    Sequence,
)
from pathlib import Path

from examples import c, p, t, u
from flext_cli import cli


def export_to_csv(data: Sequence[t.JsonMapping], output_file: Path) -> None:
    """Export data to CSV with proper headers."""
    if not data:
        cli.print("⚠️  No data to export", style=c.Cli.MessageStyles.YELLOW)
        return
    cli.print(
        f"\n📊 Exporting to CSV: {output_file.name}",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    headers = list(data[0].keys())
    rows = [headers]
    rows.extend([[str(row.get(header, "")) for header in headers] for row in data])
    write_result = cli.write_csv_file(output_file, rows)
    if write_result.success:
        size = output_file.stat().st_size
        cli.print(
            f"✅ Exported {len(data)} rows to CSV ({size} bytes)",
            style=c.Cli.MessageStyles.GREEN,
        )
    else:
        cli.print(
            f"❌ Export failed: {write_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )


def import_from_csv(
    input_file: Path,
) -> Sequence[t.JsonMapping] | None:
    """Import data from CSV with headers."""
    cli.print(
        f"\n📥 Importing from CSV: {input_file.name}",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    read_result = cli.read_csv_file_with_headers(input_file)
    if read_result.failure:
        cli.print(
            f"❌ Import failed: {read_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return []
    rows = read_result.value
    cli.print(f"✅ Imported {len(rows)} rows from CSV", style=c.Cli.MessageStyles.GREEN)
    if rows:
        sample_rows = [dict(r) for r in rows[:5]]
        if sample_rows:
            cli.show_table(sample_rows, title="📋 Sample Data")
    return [dict(r) for r in rows]


def process_binary_file(input_file: Path, output_file: Path) -> None:
    """Read, process, and write binary files."""
    cli.print(
        f"\n🔧 Processing Binary File: {input_file.name}",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    read_result = cli.read_binary_file(input_file)
    if read_result.failure:
        cli.print(
            f"❌ Read failed: {read_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return
    data = read_result.value
    cli.print(f"✅ Read {len(data)} bytes", style=c.Cli.MessageStyles.GREEN)
    checksum = hashlib.sha256(data).hexdigest()
    cli.print(f"   MD5 checksum: {checksum}", style=c.Cli.MessageStyles.CYAN)
    processed_data = data
    write_result = cli.write_binary_file(output_file, processed_data)
    if write_result.success:
        cli.print(
            f"✅ Wrote {len(processed_data)} bytes to {output_file.name}",
            style=c.Cli.MessageStyles.GREEN,
        )
    else:
        cli.print(
            f"❌ Write failed: {write_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )


def load_any_format_file(file_path: Path) -> t.JsonMapping | None:
    """Load settings from ANY format - automatically detected."""
    cli.print(
        f"\n🔍 Auto-Detecting Format: {file_path.name}",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    format_result = cli.detect_file_format(file_path)
    if format_result.failure:
        cli.print(
            f"❌ Format detection failed: {format_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return None
    detected_format = format_result.value
    cli.print(
        f"✅ Detected format: {detected_format.upper()}",
        style=c.Cli.MessageStyles.GREEN,
    )
    load_result: p.Result[t.JsonMapping] = cli.load_file_auto_dict(file_path)
    if load_result.failure:
        cli.print(
            f"❌ Load failed: {load_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return None
    data: t.JsonMapping = load_result.value
    cli.print("✅ Loaded data successfully", style=c.Cli.MessageStyles.GREEN)
    display_rows = [{"Key": k, "Value": str(v)} for k, v in data.items()]
    cli.show_table(
        display_rows,
        headers=["Key", "Value"],
        title=f"Loaded from {detected_format.upper()}",
    )
    return data


def export_data_multi_format(
    data: t.JsonMapping | Sequence[t.JsonMapping],
    base_path: Path,
) -> t.StrMapping:
    """Export same data to multiple formats (JSON, YAML, CSV)."""
    cli.print(
        f"\n💾 Multi-Format Export: {base_path.stem}",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )

    export_results: t.MutableStrMapping = {}
    json_path = base_path.with_suffix(".json")
    if isinstance(data, Sequence):
        json_payload = t.json_list_adapter().validate_python(data)
    else:
        json_payload = t.json_mapping_adapter().validate_python(data)
    json_result = cli.write_json_file(json_path, json_payload, indent=2)
    if json_result.success:
        size = json_path.stat().st_size
        export_results["JSON"] = f"{size} bytes"
        cli.print(
            f"✅ JSON: {json_path.name} ({size} bytes)", style=c.Cli.MessageStyles.GREEN
        )

    yaml_path = base_path.with_suffix(".yaml")
    yaml_payload = json_payload
    yaml_result = cli.write_yaml_file(yaml_path, yaml_payload)
    if yaml_result.success:
        size = yaml_path.stat().st_size
        export_results["YAML"] = f"{size} bytes"
        cli.print(
            f"✅ YAML: {yaml_path.name} ({size} bytes)", style=c.Cli.MessageStyles.GREEN
        )

    csv_rows_data = u.Cli.json_as_mapping_list(json_payload)

    if csv_rows_data:
        csv_path = base_path.with_suffix(".csv")
        headers = list(csv_rows_data[0].keys())
        rows = [headers]
        rows.extend([
            [str(row.get(header, "")) for header in headers] for row in csv_rows_data
        ])
        csv_result = cli.write_csv_file(csv_path, rows)
        if csv_result.success:
            size = csv_path.stat().st_size
            export_results["CSV"] = f"{size} bytes"
            cli.print(
                f"✅ CSV: {csv_path.name} ({size} bytes)",
                style=c.Cli.MessageStyles.GREEN,
            )
    cli.print(
        f"\n📊 Exported to {len(export_results)} formats",
        style=c.Cli.MessageStyles.BOLD_GREEN,
    )

    return export_results


def process_text_file(input_file: Path, output_file: Path) -> None:
    """Read and write text files with proper encoding."""
    cli.print(
        f"\n📝 Processing Text File: {input_file.name}",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    read_result = u.Cli.files_read_text(input_file)
    if read_result.failure:
        cli.print(
            f"❌ Read failed: {read_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return
    content = read_result.value
    cli.print(f"✅ Read {len(content)} characters", style=c.Cli.MessageStyles.GREEN)
    cli.print(f"   Lines: {content.count(chr(10)) + 1}", style=c.Cli.MessageStyles.CYAN)
    cli.print(f"   Words: {len(content.split())}", style=c.Cli.MessageStyles.CYAN)
    processed = content.upper()
    write_result = cli.atomic_write_text_file(output_file, processed)
    if write_result.success:
        cli.print(
            f"✅ Wrote {len(processed)} characters to {output_file.name}",
            style=c.Cli.MessageStyles.GREEN,
        )


def copy_file_with_verification(source: Path, destination: Path) -> bool:
    """Copy file and verify integrity."""
    cli.print(
        f"\n📋 Copying File: {source.name} → {destination.name}",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    source_data = source.read_bytes()
    source_hash = hashlib.sha256(source_data).hexdigest()
    cli.print(f"   Source MD5: {source_hash}", style=c.Cli.MessageStyles.CYAN)
    copy_result = cli.copy_file(source, destination)
    if copy_result.failure:
        cli.print(
            f"❌ Copy failed: {copy_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return False
    cli.print("✅ File copied successfully", style=c.Cli.MessageStyles.GREEN)
    dest_data = destination.read_bytes()
    dest_hash = hashlib.sha256(dest_data).hexdigest()
    cli.print(f"   Dest MD5: {dest_hash}", style=c.Cli.MessageStyles.CYAN)
    if source_hash == dest_hash:
        cli.print(
            "✅ Integrity verified - checksums match!",
            style=c.Cli.MessageStyles.BOLD_GREEN,
        )
        return True
    cli.print(
        "❌ Integrity check failed - checksums differ!",
        style=c.Cli.MessageStyles.BOLD_RED,
    )
    return False


def main() -> None:
    """Examples of advanced file format operations in YOUR code."""
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  Advanced File Formats Library Usage", style=c.Cli.MessageStyles.BOLD_WHITE
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    temp_dir = Path(tempfile.gettempdir()) / "flext_advanced_files"
    temp_dir.mkdir(exist_ok=True)
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("1. CSV Export/Import:", style=c.Cli.MessageStyles.BOLD_CYAN)
    sample_data: Sequence[t.JsonMapping] = [
        {"id": 1, "name": "Alice", "department": "Engineering", "salary": "100000"},
        {"id": 2, "name": "Bob", "department": "Sales", "salary": "80000"},
        {"id": 3, "name": "Charlie", "department": "Marketing", "salary": "90000"},
    ]
    csv_file = temp_dir / "employees.csv"
    typed_sample_data: Sequence[t.JsonMapping] = [dict(row) for row in sample_data]
    export_to_csv(typed_sample_data, csv_file)
    import_from_csv(csv_file)
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("2. Binary File Processing:", style=c.Cli.MessageStyles.BOLD_CYAN)
    binary_input = temp_dir / "input.bin"
    binary_output = temp_dir / "output.bin"
    binary_input.write_bytes(b"Binary data example content" * 100)
    process_binary_file(binary_input, binary_output)
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("3. Auto-Format Detection:", style=c.Cli.MessageStyles.BOLD_CYAN)
    test_config = {
        "app": "test",
        "version": "1.0",
        "debug": True,
    }
    json_file = temp_dir / "settings.json"
    yaml_file = temp_dir / "settings.yaml"
    cli.write_json_file(json_file, test_config)
    cli.write_yaml_file(yaml_file, test_config)
    load_any_format_file(json_file)
    load_any_format_file(yaml_file)
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("4. Multi-Format Export:", style=c.Cli.MessageStyles.BOLD_CYAN)
    multi_data: Sequence[t.JsonMapping] = [
        {"metric": "CPU", "value": "75%", "status": "OK"},
        {"metric": "Memory", "value": "82%", "status": "Warning"},
        {"metric": "Disk", "value": "45%", "status": "OK"},
    ]
    export_data_multi_format(multi_data, temp_dir / "metrics")
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("5. Text File Processing:", style=c.Cli.MessageStyles.BOLD_CYAN)
    text_input = temp_dir / "input.txt"
    text_output = temp_dir / "output.txt"
    text_input.write_text("Hello, World!\nThis is a test file.\nWith multiple lines.")
    process_text_file(text_input, text_output)
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("6. File Copy with Verification:", style=c.Cli.MessageStyles.BOLD_CYAN)
    demo_config = {
        "app": "demo",
        "version": "2.0",
        "enabled": True,
    }
    demo_json = temp_dir / "demo_config.json"
    cli.write_json_file(demo_json, demo_config)
    copy_file_with_verification(demo_json, temp_dir / "demo_config_backup.json")
    shutil.rmtree(temp_dir, ignore_errors=True)
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  ✅ Advanced File Format Examples Complete",
        style=c.Cli.MessageStyles.BOLD_GREEN,
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n💡 Integration Tips:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "  • CSV: Use read_csv_file_with_headers() for structured data",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Binary: Use read_binary_file() for images, PDFs, etc.",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Auto-detect: Use load_file_auto() for flexible input",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Multi-format: Export to JSON, YAML, CSV simultaneously",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Verification: Calculate checksums for integrity checks",
        style=c.Cli.MessageStyles.WHITE,
    )


if __name__ == "__main__":
    main()

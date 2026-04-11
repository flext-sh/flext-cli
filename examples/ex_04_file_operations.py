"""File Operations - Using flext-cli for File I/O in YOUR Code.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import hashlib
import platform
import shutil
import tempfile
from collections.abc import Mapping, MutableMapping, MutableSequence, Sequence
from pathlib import Path

from pydantic import TypeAdapter, ValidationError

from examples import c, m, t
from flext_cli import cli, r, u

# ============================================================================
# PATTERN 1: JSON config files in YOUR application
# ============================================================================


def save_user_preferences(
    preferences: t.ContainerMapping,
    config_dir: Path,
) -> bool:
    """Save user preferences to JSON in YOUR app."""
    config_file = config_dir / "preferences.json"

    # Instead of:
    # with open(config_file, 'w') as f:
    #     json.dump(preferences, f)

    write_result = cli.write_json_file(
        config_file,
        u.Cli.normalize_json_value(preferences),
    )

    if write_result.failure:
        cli.print(
            f"❌ Failed to save: {write_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return False

    cli.print(
        f"✅ Saved preferences to {config_file.name}", style=c.Cli.MessageStyles.GREEN
    )
    return True


def load_user_preferences(config_dir: Path) -> r[m.Cli.LoadedConfig]:
    """Load user preferences from JSON in YOUR app. Returns r[LoadedConfig]; no None."""
    config_file = config_dir / "preferences.json"

    read_result = cli.read_json_file(config_file)

    if read_result.failure:
        cli.print(
            f"⚠️  Could not load: {read_result.error}", style=c.Cli.MessageStyles.YELLOW
        )
        return r[m.Cli.LoadedConfig].fail(
            read_result.error or "Could not load preferences",
        )
    if not isinstance(read_result.value, Mapping):
        return r[m.Cli.LoadedConfig].fail("Preferences content must be a mapping")

    cli.print(
        f"✅ Loaded preferences from {config_file.name}",
        style=c.Cli.MessageStyles.GREEN,
    )
    return r[m.Cli.LoadedConfig].ok(
        m.Cli.LoadedConfig(content=dict(read_result.value)),
    )


# ============================================================================
# PATTERN 2: YAML configuration in YOUR deployment tool
# ============================================================================


def save_deployment_config(
    config: t.ContainerMapping,
    config_file: Path,
) -> bool:
    """Save deployment config to YAML in YOUR tool."""
    # Instead of:
    # with open(config_file, 'w') as f:
    #     yaml.dump(config, f)

    # Normalize the mapping into the CLI JSON contract before writing YAML.
    write_result = cli.write_yaml_file(
        config_file,
        u.Cli.normalize_json_value(config),
    )

    if write_result.failure:
        cli.print(
            f"❌ Config save failed: {write_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return False

    cli.print("✅ Saved deployment config", style=c.Cli.MessageStyles.GREEN)
    return True


def load_deployment_config(config_file: Path) -> r[m.Cli.LoadedConfig]:
    """Load deployment config from YAML in YOUR tool. Returns r[LoadedConfig]; no None."""
    load_result = cli.load_file_auto_dict(config_file)

    if load_result.failure:
        cli.print(
            f"❌ Config load failed: {load_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return r[m.Cli.LoadedConfig].fail(load_result.error or "Config load failed")

    cli.print("✅ Loaded deployment config", style=c.Cli.MessageStyles.GREEN)
    return r[m.Cli.LoadedConfig].ok(
        m.Cli.LoadedConfig(content=load_result.value),
    )


# ============================================================================
# PATTERN 3: Export data as tables in YOUR reporting tool
# ============================================================================


def export_database_report(
    records: Sequence[t.ContainerMapping],
    output_file: Path,
    format_type: c.Cli.TabularFormat = c.Cli.TabularFormat.GRID,
) -> bool | None:
    """Export database query results in YOUR reporting tool."""
    table_rows: Sequence[t.Cli.TableMappingRow] = [
        {str(key): u.Cli.normalize_json_value(value) for key, value in record.items()}
        for record in records
    ]
    table_result = cli.format_table(table_rows, table_format=format_type)

    if table_result.failure:
        cli.print(
            f"❌ Table creation failed: {table_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return False

    # Save to file
    ascii_table = table_result.value
    try:
        output_file.write_text(ascii_table, encoding="utf-8")
        cli.print(
            f"✅ Report exported to {output_file}", style=c.Cli.MessageStyles.GREEN
        )
        return True
    except Exception as e:
        cli.print(f"❌ Export failed: {e}", style=c.Cli.MessageStyles.BOLD_RED)
        return False


# ============================================================================
# PATTERN 4: Directory operations in YOUR file manager CLI
# ============================================================================


def list_project_files(project_dir: Path) -> None:
    """List files with metadata in YOUR file manager."""
    if not project_dir.exists():
        cli.print(
            f"❌ Directory not found: {project_dir}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return

    # Collect file metadata
    files_data: Sequence[t.Cli.TableMappingRow] = [
        {
            "Name": item.name[:40],
            "Type": "📂 dir" if item.is_dir() else "📄 file",
            "Size": f"{item.stat().st_size:,}" if item.is_file() else "-",
        }
        for item in sorted(project_dir.iterdir())
    ]

    # Display as table
    if files_data:
        sample_data = files_data[:20]
        cli.print(
            f"\n📁 Directory: {project_dir.name}", style=c.Cli.MessageStyles.BOLD_CYAN
        )
        cli.show_table(sample_data, title="Directory listing")


def show_directory_tree(root_path: Path, max_items: int = 15) -> None:
    """Display directory tree in YOUR file browser."""
    if not root_path.exists():
        cli.print(f"❌ Path not found: {root_path}", style=c.Cli.MessageStyles.BOLD_RED)
        return

    tree_result = cli.create_tree(f"📁 {root_path.name}")

    if tree_result.failure:
        cli.print(
            f"❌ Tree creation failed: {tree_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return

    tree = tree_result.value
    items = list(root_path.iterdir())[:max_items]

    for item in sorted(items):
        if item.is_dir():
            tree.add(f"📂 {item.name}/")
        else:
            size = item.stat().st_size
            tree.add(f"📄 {item.name} ({size:,} bytes)")

    # Print the tree using cli
    cli.print(str(tree))


# ============================================================================
# PATTERN 5: Data validation workflow in YOUR ETL tool
# ============================================================================


def validate_and_import_data(input_file: Path) -> r[m.Cli.LoadedConfig]:
    """Validate and import data in YOUR ETL pipeline. Returns r[LoadedConfig]; no None."""
    read_result = cli.read_json_file(input_file)

    if read_result.failure:
        cli.print(
            f"❌ Read failed: {read_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return r[m.Cli.LoadedConfig].fail(read_result.error or "Read failed")

    data = read_result.value
    if not isinstance(data, Mapping):
        return r[m.Cli.LoadedConfig].fail("Input data must be a mapping")

    required_fields = list(c.EXAMPLE_REQUIRED_DATA_FIELDS)
    for field in required_fields:
        if field not in data:
            return r[m.Cli.LoadedConfig].fail(f"Missing required field: {field}")

    cli.print("✅ Data validated successfully", style=c.Cli.MessageStyles.GREEN)
    return r[m.Cli.LoadedConfig].ok(
        m.Cli.LoadedConfig(content=data),
    )


# ============================================================================
# PATTERN 6: Backup and restore in YOUR backup tool
# ============================================================================


def backup_config_files(source_dir: Path, backup_dir: Path) -> t.StrSequence:
    """Backup configuration files in YOUR backup tool."""
    backup_dir.mkdir(parents=True, exist_ok=True)

    config_files = list(source_dir.glob("*.json")) + list(source_dir.glob("*.yaml"))

    backed_up: MutableSequence[str] = []
    for config_file in config_files:
        # Read original
        if config_file.suffix == ".json":
            read_result = cli.read_json_file(config_file)
        else:
            read_result = cli.read_yaml_file(config_file)

        if read_result.failure:
            cli.print(
                f"⚠️  Skipped {config_file.name}: {read_result.error}",
                style=c.Cli.MessageStyles.YELLOW,
            )
            continue

        # Write backup
        backup_file = backup_dir / config_file.name
        if config_file.suffix == ".json":
            write_result = cli.write_json_file(
                backup_file,
                read_result.value,
            )
        else:
            write_result = cli.write_yaml_file(
                backup_file,
                read_result.value,
            )

        if write_result.success:
            backed_up.append(config_file.name)

    cli.print(
        f"✅ Backed up {len(backed_up)} files to {backup_dir}",
        style=c.Cli.MessageStyles.GREEN,
    )
    return backed_up


# ============================================================================
# PATTERN 7: CSV export/import with headers in YOUR data tool
# ============================================================================


def export_to_csv(
    data: Sequence[t.ContainerMapping],
    output_file: Path,
) -> bool:
    """Export data to CSV with proper headers in YOUR reporting tool."""
    if not data:
        cli.print("⚠️  No data to export", style=c.Cli.MessageStyles.YELLOW)
        return False

    cli.print(
        f"📊 Exporting {len(data)} rows to CSV...", style=c.Cli.MessageStyles.CYAN
    )

    # Extract headers from first row
    headers = list(data[0].keys())

    # Prepare rows (headers as first row, then data)
    rows = [headers]  # First row is headers
    rows.extend([[str(row.get(header, "")) for header in headers] for row in data])

    # Write CSV (headers included as first row)
    write_result = cli.write_csv_file(output_file, rows)

    if write_result.failure:
        cli.print(
            f"❌ CSV export failed: {write_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return False

    size = output_file.stat().st_size
    cli.print(
        f"✅ Exported to {output_file.name} ({size} bytes)",
        style=c.Cli.MessageStyles.GREEN,
    )
    return True


def import_from_csv(input_file: Path) -> Sequence[t.StrMapping] | None:
    """Import data from CSV with headers in YOUR data tool."""
    cli.print(f"📥 Importing from {input_file.name}...", style=c.Cli.MessageStyles.CYAN)

    # Read CSV with headers
    read_result = cli.read_csv_file_with_headers(input_file)

    if read_result.failure:
        cli.print(
            f"❌ CSV import failed: {read_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return None

    rows = read_result.value
    cli.print(f"✅ Imported {len(rows)} rows from CSV", style=c.Cli.MessageStyles.GREEN)

    # Display sample
    if rows:
        sample_rows = [dict(r) for r in rows[:5]]
        tabular_data: Sequence[t.Cli.TableMappingRow] = [
            dict(row) for row in sample_rows
        ]
        cli.show_table(tabular_data, title="📋 Sample Data")
    return [dict(r) for r in rows] if rows else None


# ============================================================================
# PATTERN 8: Binary file operations in YOUR file processor
# ============================================================================


def process_binary_file(input_file: Path, output_file: Path) -> bool:
    """Read and write binary files in YOUR file processor."""
    cli.print(
        f"🔧 Processing binary file: {input_file.name}", style=c.Cli.MessageStyles.CYAN
    )

    # Read binary file
    read_result = cli.read_binary_file(input_file)

    if read_result.failure:
        cli.print(
            f"❌ Read failed: {read_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return False

    data = read_result.value
    cli.print(f"✅ Read {len(data)} bytes", style=c.Cli.MessageStyles.GREEN)

    # Calculate checksum
    checksum = hashlib.sha256(data).hexdigest()
    cli.print(f"   SHA256: {checksum}", style=c.Cli.MessageStyles.CYAN)

    # Process data (example: simple copy)
    processed_data = data

    # Write binary file
    write_result = cli.write_binary_file(output_file, processed_data)

    if write_result.failure:
        cli.print(
            f"❌ Write failed: {write_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return False

    cli.print(
        f"✅ Wrote {len(processed_data)} bytes to {output_file.name}",
        style=c.Cli.MessageStyles.GREEN,
    )
    return True


# ============================================================================
# PATTERN 9: Auto-format detection in YOUR config loader
# ============================================================================


def load_config_auto_detect(config_file: Path) -> r[m.Cli.LoadedConfig]:
    """Load config from ANY format with auto-detection. Returns r[LoadedConfig]; no None."""
    cli.print(
        f"🔍 Auto-detecting format: {config_file.name}", style=c.Cli.MessageStyles.CYAN
    )

    load_result = cli.load_file_auto_dict(config_file)

    if load_result.failure:
        cli.print(
            f"❌ Load failed: {load_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return r[m.Cli.LoadedConfig].fail(load_result.error or "Load failed")

    data = load_result.value
    cli.print("✅ Config loaded successfully", style=c.Cli.MessageStyles.GREEN)

    display_rows = [{"Key": k, "Value": str(v)} for k, v in data.items()]
    cli.show_table(display_rows, headers=["Key", "Value"], title="Loaded config")
    return r[m.Cli.LoadedConfig].ok(
        m.Cli.LoadedConfig(content=data),
    )


# ============================================================================
# PATTERN 10: Multi-format export in YOUR export tool
# ============================================================================


def export_multi_format(
    data: t.ContainerMapping | Sequence[t.ContainerMapping],
    base_path: Path,
) -> t.StrMapping:
    """Export same data to multiple formats (JSON, YAML, CSV)."""
    cli.print(
        f"💾 Multi-format export: {base_path.stem}", style=c.Cli.MessageStyles.CYAN
    )

    export_results: MutableMapping[str, str] = {}

    # Export to JSON
    json_path = base_path.with_suffix(".json")
    # Handle both single dict and list of dicts
    json_payload = u.Cli.normalize_json_value(data)
    json_result = cli.write_json_file(
        json_path,
        json_payload,
        indent=2,
    )
    if json_result.success:
        size = json_path.stat().st_size
        export_results["JSON"] = f"{size} bytes"
        cli.print(
            f"✅ JSON: {json_path.name} ({size} bytes)", style=c.Cli.MessageStyles.GREEN
        )

    # Export to YAML
    yaml_path = base_path.with_suffix(".yaml")
    yaml_payload = u.Cli.normalize_json_value(data)
    yaml_result = cli.write_yaml_file(
        yaml_path,
        yaml_payload,
    )
    if yaml_result.success:
        size = yaml_path.stat().st_size
        export_results["YAML"] = f"{size} bytes"
        cli.print(
            f"✅ YAML: {yaml_path.name} ({size} bytes)", style=c.Cli.MessageStyles.GREEN
        )

    rows_adapter: TypeAdapter[Sequence[t.ContainerMapping]] = TypeAdapter(
        Sequence[t.ContainerMapping]
    )
    csv_rows_data: Sequence[t.ContainerMapping]
    try:
        csv_rows_data = rows_adapter.validate_python(data)
    except ValidationError:
        csv_rows_data = []

    if csv_rows_data:
        csv_path = base_path.with_suffix(".csv")
        headers = list(csv_rows_data[0].keys())
        rows = [headers]
        rows.extend(
            [[str(row.get(header, "")) for header in headers] for row in csv_rows_data],
        )

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


# ============================================================================
# PATTERN 10: Railway Pattern for File Operations Chain
# ============================================================================


def process_file_pipeline(
    input_file: Path,
    output_dir: Path,
) -> r[Mapping[str, t.RecursiveValue]]:
    """Complete file processing pipeline using Railway Pattern.

    Demonstrates chaining multiple file operations with proper error handling.
    Uses single return point pattern for reduced complexity.
    """
    cli.print(
        f"\n🔄 Processing file pipeline: {input_file.name}",
        style=c.Cli.MessageStyles.CYAN,
    )

    # Initialize result
    result: r[Mapping[str, t.RecursiveValue]]

    # Railway pattern: Chain operations with automatic error propagation

    # Step 1: Validate input file exists and is readable
    if not input_file.exists():
        result = r[Mapping[str, t.RecursiveValue]].fail(f"File not found: {input_file}")
    elif not input_file.is_file():
        result = r[Mapping[str, t.RecursiveValue]].fail(f"Not a file: {input_file}")
    else:
        cli.print("✅ Input validation passed", style=c.Cli.MessageStyles.GREEN)

        # Step 2: Read file content (dict-only, no narrowing)
        read_result = cli.read_json_file(input_file)
        if read_result.failure:
            result = r[Mapping[str, t.RecursiveValue]].fail(
                f"File read failed: {read_result.error}",
            )
        else:
            data = read_result.value
            cli.print("✅ File read successfully", style=c.Cli.MessageStyles.GREEN)
            if not isinstance(data, Mapping):
                result = r[Mapping[str, t.RecursiveValue]].fail(
                    "File content must be a mapping",
                )
            else:
                transformed_data = validate_and_transform_data(data)
                cli.print(
                    "✅ Data validation/transform passed",
                    style=c.Cli.MessageStyles.GREEN,
                )

                output_result = generate_output_files(transformed_data, output_dir)
                if output_result.failure:
                    result = r[Mapping[str, t.RecursiveValue]].fail(
                        output_result.error or "Unknown error",
                    )
                else:
                    results = output_result.value
                    cli.print(
                        "✅ Output files generated", style=c.Cli.MessageStyles.GREEN
                    )

                    summary = create_processing_summary(results)
                    cli.print(
                        "✅ Processing summary created", style=c.Cli.MessageStyles.GREEN
                    )
                    cli.print(
                        "🎉 File processing pipeline completed successfully!",
                        style=c.Cli.MessageStyles.BOLD_GREEN,
                    )
                    result = r[Mapping[str, t.RecursiveValue]].ok(summary)

    if result.failure:
        cli.print(
            f"❌ Pipeline failed: {result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )

    return result


def validate_and_transform_data(
    data: t.ContainerMapping,
) -> m.Cli.LoadedConfig:
    """Validate and transform input data."""
    transformed = {
        **data,
        "processed_at": "2025-11-23T10:00:00Z",
        "pipeline_version": "2.0",
        "validated": True,
    }

    return m.Cli.LoadedConfig(content=transformed)


def generate_output_files(
    data: m.Cli.LoadedConfig,
    output_dir: Path,
) -> r[Mapping[str, Path]]:
    """Generate multiple output file formats."""
    output_dir.mkdir(exist_ok=True)
    base_name = "processed_data"

    results: MutableMapping[str, Path] = {}

    # JSON output
    json_file = output_dir / f"{base_name}.json"
    json_result = cli.write_json_file(
        json_file,
        data.content,
    )
    if json_result.failure:
        return r[Mapping[str, Path]].fail(f"JSON export failed: {json_result.error}")
    results["json"] = json_file

    # YAML output
    yaml_file = output_dir / f"{base_name}.yaml"
    yaml_result = cli.write_yaml_file(
        yaml_file,
        data.content,
    )
    if yaml_result.failure:
        return r[Mapping[str, Path]].fail(f"YAML export failed: {yaml_result.error}")
    results["yaml"] = yaml_file

    rows_adapter: TypeAdapter[Sequence[t.ContainerMapping]] = TypeAdapter(
        Sequence[t.ContainerMapping]
    )
    csv_rows_data: Sequence[t.ContainerMapping]
    content_items: t.ValueOrModel = ""
    if isinstance(data.content, dict):
        content_items = data.content.get("items", [])
    else:
        content_items = []
    try:
        csv_rows_data = rows_adapter.validate_python(content_items)
    except ValidationError:
        csv_rows_data = []

    if csv_rows_data:
        csv_file = output_dir / f"{base_name}.csv"
        csv_rows: Sequence[t.StrSequence] = [
            [str(value) for value in item.values()] for item in csv_rows_data
        ]
        csv_result = cli.write_csv_file(csv_file, csv_rows)
        if csv_result.failure:
            return r[Mapping[str, Path]].fail(f"CSV export failed: {csv_result.error}")
        results["csv"] = csv_file

    return r[Mapping[str, Path]].ok(results)


def create_processing_summary(
    results: Mapping[str, Path],
) -> Mapping[str, bool | int | t.StrSequence | str]:
    """Create a summary of the processing pipeline."""
    return {
        "pipeline_completed": True,
        "timestamp": "2025-11-23T10:00:00Z",
        "output_files": [str(p) for p in results.values()],
        "file_count": len(results),
        "formats": list(results.keys()),
    }


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of using file operations in YOUR code."""
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("  File Operations Library Usage", style=c.Cli.MessageStyles.BOLD_WHITE)
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)

    # Setup temp directories
    temp_dir = Path(tempfile.gettempdir()) / "flext_demo"
    temp_dir.mkdir(exist_ok=True)

    # Example 1: JSON preferences
    cli.print(
        "\n1. JSON Config Files (user preferences):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    prefs: t.ContainerMapping = {
        "theme": "dark",
        "font_size": 14,
        "auto_save": True,
    }
    save_user_preferences(prefs, temp_dir)
    prefs_result = load_user_preferences(temp_dir)
    if prefs_result.failure:
        cli.print(
            f"   Load result: {prefs_result.error}", style=c.Cli.MessageStyles.YELLOW
        )

    # Example 2: YAML deployment config
    cli.print(
        "\n2. YAML Configuration (deployment):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    deploy_config: t.ContainerMapping = {
        "environment": "staging",
        "host": "staging.example.com",
        "platform": platform.system(),
    }
    yaml_file = temp_dir / "deploy.yaml"
    save_deployment_config(deploy_config, yaml_file)
    deploy_result = load_deployment_config(yaml_file)
    if deploy_result.failure:
        cli.print(
            f"   Load result: {deploy_result.error}", style=c.Cli.MessageStyles.YELLOW
        )

    # Example 3: Table export
    cli.print("\n3. Data Export (table format):", style=c.Cli.MessageStyles.BOLD_CYAN)
    sample_data: Sequence[t.ContainerMapping] = [
        {"id": 1, "name": "Alice", "status": "active"},
        {"id": 2, "name": "Bob", "status": "inactive"},
    ]
    report_file = temp_dir / "report.txt"
    export_database_report(
        sample_data, report_file, format_type=c.Cli.TabularFormat.GRID
    )

    # Example 4: Directory listing
    cli.print(
        "\n4. Directory Operations (file browser):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    list_project_files(Path.cwd())

    # Example 5: Directory tree
    cli.print(
        "\n5. Directory Tree (structure view):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    show_directory_tree(Path.cwd(), max_items=10)

    # Example 6: Data validation
    cli.print(
        "\n6. Data Validation (ETL pipeline):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    test_data: t.ContainerMapping = {"id": 1, "name": "test", "value": 100}
    test_file = temp_dir / "test_data.json"
    cli.write_json_file(test_file, u.Cli.normalize_json_value(test_data))
    valid_result = validate_and_import_data(test_file)
    if valid_result.failure:
        cli.print(
            f"   Validation: {valid_result.error}", style=c.Cli.MessageStyles.YELLOW
        )

    # Example 7: CSV export/import
    cli.print(
        "\n7. CSV Export/Import (with headers):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    csv_data: Sequence[t.ContainerMapping] = [
        {"employee_id": 101, "name": "Alice Smith", "department": "Engineering"},
        {"employee_id": 102, "name": "Bob Jones", "department": "Sales"},
        {"employee_id": 103, "name": "Carol White", "department": "Marketing"},
    ]
    csv_file = temp_dir / "employees.csv"
    export_to_csv(csv_data, csv_file)
    import_from_csv(csv_file)

    # Example 8: Binary file operations
    cli.print("\n8. Binary File Operations:", style=c.Cli.MessageStyles.BOLD_CYAN)
    binary_input = temp_dir / "input.bin"
    binary_output = temp_dir / "output.bin"
    binary_input.write_bytes(b"Binary data content example" * 50)
    process_binary_file(binary_input, binary_output)

    # Example 9: Auto-format detection
    cli.print("\n9. Auto-Format Detection:", style=c.Cli.MessageStyles.BOLD_CYAN)
    auto_config: t.ContainerMapping = {
        "app": "demo",
        "version": "1.0",
        "enabled": True,
    }
    auto_json = temp_dir / "auto_config.json"
    auto_yaml = temp_dir / "auto_config.yaml"
    cli.write_json_file(auto_json, u.Cli.normalize_json_value(auto_config))
    cli.write_yaml_file(auto_yaml, u.Cli.normalize_json_value(auto_config))
    auto1_result = load_config_auto_detect(auto_json)
    auto2_result = load_config_auto_detect(auto_yaml)
    if auto1_result.failure:
        cli.print(
            f"   Auto load JSON: {auto1_result.error}", style=c.Cli.MessageStyles.YELLOW
        )
    if auto2_result.failure:
        cli.print(
            f"   Auto load YAML: {auto2_result.error}", style=c.Cli.MessageStyles.YELLOW
        )

    # Example 10: Multi-format export
    cli.print("\n10. Multi-Format Export:", style=c.Cli.MessageStyles.BOLD_CYAN)
    multi_data: Sequence[t.ContainerMapping] = [
        {"metric": "CPU", "value": "75%", "status": "OK"},
        {"metric": "Memory", "value": "82%", "status": "Warning"},
    ]
    export_multi_format(multi_data, temp_dir / "metrics")

    # Example 11: Railway Pattern Pipeline
    cli.print(
        "\n11. Railway Pattern Pipeline (complete workflow):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    pipeline_input: t.ContainerMapping = {
        "name": "pipeline_demo",
        "version": "1.0",
        "items": [
            {"id": 1, "name": "task1", "status": "completed"},
            {"id": 2, "name": "task2", "status": "pending"},
        ],
    }
    pipeline_file = temp_dir / "pipeline_input.json"
    cli.write_json_file(pipeline_file, u.Cli.normalize_json_value(pipeline_input))
    pipeline_result = process_file_pipeline(pipeline_file, temp_dir / "pipeline_output")

    if pipeline_result.success:
        summary = pipeline_result.value
        cli.print(f"   📊 Pipeline summary: {summary}", style=c.Cli.MessageStyles.CYAN)

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)

    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("  ✅ File Operations Complete", style=c.Cli.MessageStyles.BOLD_GREEN)
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)

    # Integration guide
    cli.print("\n💡 Integration Tips:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "  • JSON: Use cli.read_json() / write_json()", style=c.Cli.MessageStyles.WHITE
    )
    cli.print(
        "  • YAML: Use cli.read_yaml_file() / write_yaml()",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • CSV: Use read_csv_file_with_headers() for structured data",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Binary: Use read_binary_file() for images, PDFs, etc.",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Auto-detect: Use load_file_auto() for flexible loading",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Tables: Use FlextCliTables for ASCII table export",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • All methods return r for error handling", style=c.Cli.MessageStyles.WHITE
    )


if __name__ == "__main__":
    main()

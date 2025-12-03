"""File Operations - Using flext-cli for File I/O in YOUR Code.

WHEN TO USE THIS:
- Building CLI tools that read/write config files
- Need to save/load data in JSON, YAML, CSV formats
- Want structured error handling for file operations
- Need to validate file contents
- Building data export/import features
- Working with CSV files with proper headers
- Handling binary files (images, PDFs, etc.)
- Auto-detecting file formats

FLEXT-CLI PROVIDES:
- file_tools.read_json() / write_json() - JSON file operations
- file_tools.read_yaml_file() / write_yaml() - YAML config files
- file_tools.read_csv_file_with_headers() / write_csv_file() - CSV with headers
- file_tools.read_binary_file() / write_binary_file() - Binary operations
- file_tools.detect_file_format() / load_file_auto() - Auto-format detection
- FlextResult error handling - No try/except needed
- Automatic path handling with pathlib integration

HOW TO USE IN YOUR CLI:
Replace open() and json.load() with flext-cli file_tools for better error handling
Use CSV operations for structured data with headers
Use binary operations for images, PDFs, etc.
Use auto-detection for flexible file loading

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import hashlib
import platform
import shutil
import tempfile
from pathlib import Path
from typing import cast

from flext_core import FlextResult, FlextTypes, FlextUtilities

from flext_cli import (
    FlextCli,
    FlextCliModels,
    FlextCliTables,
    FlextCliTypes,
)

# Alias for static method calls - use u.* for uds
u = FlextUtilities
r = FlextResult
t = FlextTypes

cli = FlextCli()
tables = FlextCliTables()


# ============================================================================
# PATTERN 1: JSON config files in YOUR application
# ============================================================================


def save_user_preferences(
    preferences: FlextCliTypes.Data.CliDataDict,
    config_dir: Path,
) -> bool:
    """Save user preferences to JSON in YOUR app."""
    config_file = config_dir / "preferences.json"

    # Instead of:
    # with open(config_file, 'w') as f:
    #     json.dump(preferences, f)

    write_result = cli.file_tools.write_json_file(
        config_file,
        preferences,
    )

    if write_result.is_failure:
        cli.print(f"❌ Failed to save: {write_result.error}", style="bold red")
        return False

    cli.print(f"✅ Saved preferences to {config_file.name}", style="green")
    return True


def load_user_preferences(config_dir: Path) -> dict[str, object] | None:
    """Load user preferences from JSON in YOUR app."""
    config_file = config_dir / "preferences.json"

    # Instead of:
    # with open(config_file) as f:
    #     return json.load(f)

    read_result = cli.file_tools.read_json_file(config_file)

    if read_result.is_failure:
        cli.print(f"⚠️  Could not load: {read_result.error}", style="yellow")
        return None

    preferences = read_result.unwrap()
    if not isinstance(preferences, dict):
        return None
    cli.print(f"✅ Loaded preferences from {config_file.name}", style="green")
    # Cast to expected type (runtime type is compatible)
    return cast("dict[str, object] | None", preferences)


# ============================================================================
# PATTERN 2: YAML configuration in YOUR deployment tool
# ============================================================================


def save_deployment_config(
    config: FlextCliTypes.Data.CliDataDict,
    config_file: Path,
) -> bool:
    """Save deployment config to YAML in YOUR tool."""
    # Instead of:
    # with open(config_file, 'w') as f:
    #     yaml.dump(config, f)

    # Cast dict to object (compatible with JsonValue)
    write_result = cli.file_tools.write_yaml_file(
        config_file,
        config,
    )

    if write_result.is_failure:
        cli.print(f"❌ Config save failed: {write_result.error}", style="bold red")
        return False

    cli.print("✅ Saved deployment config", style="green")
    return True


def load_deployment_config(config_file: Path) -> dict[str, object] | None:
    """Load deployment config from YAML in YOUR tool."""
    read_result = cli.file_tools.read_yaml_file(config_file)

    if read_result.is_failure:
        cli.print(f"❌ Config load failed: {read_result.error}", style="bold red")
        return None

    config = read_result.unwrap()
    if not isinstance(config, dict):
        return None
    cli.print("✅ Loaded deployment config", style="green")
    # Cast to expected type (runtime type is compatible)
    return cast("dict[str, object] | None", config)


# ============================================================================
# PATTERN 3: Export data as tables in YOUR reporting tool
# ============================================================================


def export_database_report(
    records: list[FlextCliTypes.Data.CliDataDict],
    output_file: Path,
    format_type: str = "grid",
) -> bool | None:
    """Export database query results in YOUR reporting tool."""
    # Create ASCII table (for logs, emails, markdown docs)
    # Create table config with specified format
    config = FlextCliModels.TableConfig(table_format=format_type)
    table_result = tables.create_table(records, config=config)

    if table_result.is_failure:
        cli.print(f"❌ Table creation failed: {table_result.error}", style="bold red")
        return False

    # Save to file
    ascii_table = table_result.unwrap()
    try:
        output_file.write_text(ascii_table, encoding="utf-8")
        cli.print(f"✅ Report exported to {output_file}", style="green")
        return True
    except Exception as e:
        cli.print(f"❌ Export failed: {e}", style="bold red")
        return False


# ============================================================================
# PATTERN 4: Directory operations in YOUR file manager CLI
# ============================================================================


def list_project_files(project_dir: Path) -> None:
    """List files with metadata in YOUR file manager."""
    if not project_dir.exists():
        cli.print(f"❌ Directory not found: {project_dir}", style="bold red")
        return

    # Collect file metadata
    files_data: list[FlextCliTypes.Data.CliDataDict] = [
        {
            "Name": item.name[:40],
            "Type": "📂 dir" if item.is_dir() else "📄 file",
            "Size": f"{item.stat().st_size:,}" if item.is_file() else "-",
        }
        for item in sorted(project_dir.iterdir())
    ]

    # Display as table
    if files_data:
        # files_data is already properly typed
        sample_data: list[FlextCliTypes.Data.CliDataDict] = files_data[:20]
        # Create table config for grid format
        config = FlextCliModels.TableConfig(table_format="grid")
        table_result = tables.create_table(sample_data, config=config)
        if table_result.is_success:
            cli.print(f"\n📁 Directory: {project_dir.name}", style="bold cyan")
            # tables.create_table returns string, use cli.print
            cli.print(table_result.unwrap())


def show_directory_tree(root_path: Path, max_items: int = 15) -> None:
    """Display directory tree in YOUR file browser."""
    if not root_path.exists():
        cli.print(f"❌ Path not found: {root_path}", style="bold red")
        return

    tree_result = cli.create_tree(f"📁 {root_path.name}")

    if tree_result.is_failure:
        cli.print(f"❌ Tree creation failed: {tree_result.error}", style="bold red")
        return

    tree = tree_result.unwrap()
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


def validate_and_import_data(input_file: Path) -> FlextCliTypes.Data.CliDataDict | None:
    """Validate and import data in YOUR ETL pipeline."""
    # Step 1: Read file
    read_result = cli.file_tools.read_json_file(input_file)

    if read_result.is_failure:
        cli.print(f"❌ Read failed: {read_result.error}", style="bold red")
        return None

    data = read_result.unwrap()

    # Step 2: Validate structure
    def validate_structure(
        data: FlextCliTypes.Data.CliDataDict,
    ) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Your validation logic."""
        required_fields = ["id", "name", "value"]
        for field in required_fields:
            if field not in data:
                return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
                    f"Missing required field: {field}",
                )
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok(data)

    # Chain validation using FlextResult - type narrowing needed
    if not isinstance(data, dict):
        cli.print("❌ Data is not a dictionary", style="bold red")
        return None

    # Convert to JsonDict-compatible dict using u
    # Use u.transform for JSON conversion
    transform_result = u.transform(data, to_json=True)
    json_data: t.JsonDict = (
        transform_result.unwrap()
        if transform_result.is_success
        else cast("t.JsonDict", data)
    )
    validated = validate_structure(json_data)

    if validated.is_failure:
        cli.print(f"❌ Validation failed: {validated.error}", style="bold red")
        return None

    cli.print("✅ Data validated successfully", style="green")
    return validated.unwrap()


# ============================================================================
# PATTERN 6: Backup and restore in YOUR backup tool
# ============================================================================


def backup_config_files(source_dir: Path, backup_dir: Path) -> list[str]:
    """Backup configuration files in YOUR backup tool."""
    backup_dir.mkdir(parents=True, exist_ok=True)

    config_files = list(source_dir.glob("*.json")) + list(source_dir.glob("*.yaml"))

    backed_up = []
    for config_file in config_files:
        # Read original
        if config_file.suffix == ".json":
            read_result = cli.file_tools.read_json_file(config_file)
        else:
            read_result = cli.file_tools.read_yaml_file(config_file)

        if read_result.is_failure:
            cli.print(
                f"⚠️  Skipped {config_file.name}: {read_result.error}",
                style="yellow",
            )
            continue

        # Write backup
        backup_file = backup_dir / config_file.name
        if config_file.suffix == ".json":
            write_result = cli.file_tools.write_json_file(
                backup_file,
                read_result.unwrap(),
            )
        else:
            write_result = cli.file_tools.write_yaml_file(
                backup_file,
                read_result.unwrap(),
            )

        if write_result.is_success:
            backed_up.append(config_file.name)

    cli.print(f"✅ Backed up {len(backed_up)} files to {backup_dir}", style="green")
    return backed_up


# ============================================================================
# PATTERN 7: CSV export/import with headers in YOUR data tool
# ============================================================================


def export_to_csv(
    data: list[FlextCliTypes.Data.CliDataDict],
    output_file: Path,
) -> bool:
    """Export data to CSV with proper headers in YOUR reporting tool."""
    if not data:
        cli.print("⚠️  No data to export", style="yellow")
        return False

    cli.print(f"📊 Exporting {len(data)} rows to CSV...", style="cyan")

    # Extract headers from first row
    headers = list(data[0].keys())

    # Prepare rows (headers as first row, then data)
    rows = [headers]  # First row is headers
    rows.extend([[str(row.get(header, "")) for header in headers] for row in data])

    # Write CSV (headers included as first row)
    write_result = cli.file_tools.write_csv_file(output_file, rows)

    if write_result.is_failure:
        cli.print(f"❌ CSV export failed: {write_result.error}", style="bold red")
        return False

    size = output_file.stat().st_size
    cli.print(f"✅ Exported to {output_file.name} ({size} bytes)", style="green")
    return True


def import_from_csv(input_file: Path) -> list[dict[str, str]] | None:
    """Import data from CSV with headers in YOUR data tool."""
    cli.print(f"📥 Importing from {input_file.name}...", style="cyan")

    # Read CSV with headers
    read_result = cli.file_tools.read_csv_file_with_headers(input_file)

    if read_result.is_failure:
        cli.print(f"❌ CSV import failed: {read_result.error}", style="bold red")
        return None

    rows = read_result.unwrap()
    cli.print(f"✅ Imported {len(rows)} rows from CSV", style="green")

    # Display sample
    if rows:
        sample_rows: list[dict[str, str]] = rows[:5]
        # Create table config for grid format
        config = FlextCliModels.TableConfig(table_format="grid")
        # Convert to JsonDict-compatible format using u
        tabular_data: FlextCliTypes.Data.TabularData = (
            # Use u.map to convert list items to JSON
            list(
                u.map(
                    sample_rows,
                    mapper=lambda row: (
                        u.transform(row, to_json=True).unwrap()
                        if isinstance(row, dict)
                        and u.transform(row, to_json=True).is_success
                        else row
                    ),
                )
            )
        )
        table_result = tables.create_table(tabular_data, config=config)
        if table_result.is_success:
            cli.print("\n📋 Sample Data:", style="yellow")

    # Cast to expected type (runtime type is compatible)
    return rows


# ============================================================================
# PATTERN 8: Binary file operations in YOUR file processor
# ============================================================================


def process_binary_file(input_file: Path, output_file: Path) -> bool:
    """Read and write binary files in YOUR file processor."""
    cli.print(f"🔧 Processing binary file: {input_file.name}", style="cyan")

    # Read binary file
    read_result = cli.file_tools.read_binary_file(input_file)

    if read_result.is_failure:
        cli.print(f"❌ Read failed: {read_result.error}", style="bold red")
        return False

    data = read_result.unwrap()
    cli.print(f"✅ Read {len(data)} bytes", style="green")

    # Calculate checksum
    checksum = hashlib.sha256(data).hexdigest()
    cli.print(f"   SHA256: {checksum}", style="cyan")

    # Process data (example: simple copy)
    processed_data = data

    # Write binary file
    write_result = cli.file_tools.write_binary_file(output_file, processed_data)

    if write_result.is_failure:
        cli.print(f"❌ Write failed: {write_result.error}", style="bold red")
        return False

    cli.print(
        f"✅ Wrote {len(processed_data)} bytes to {output_file.name}",
        style="green",
    )
    return True


# ============================================================================
# PATTERN 9: Auto-format detection in YOUR config loader
# ============================================================================


def load_config_auto_detect(config_file: Path) -> dict[str, object] | None:
    """Load config from ANY format with auto-detection."""
    cli.print(f"🔍 Auto-detecting format: {config_file.name}", style="cyan")

    # Detect format from extension
    format_result = cli.file_tools.detect_file_format(config_file)

    if format_result.is_failure:
        cli.print(
            f"❌ Format detection failed: {format_result.error}",
            style="bold red",
        )
        return None

    detected_format = format_result.unwrap()
    cli.print(f"✅ Detected format: {detected_format.upper()}", style="green")

    # Load with auto-detection
    load_result = cli.file_tools.load_file_auto_detect(config_file)

    if load_result.is_failure:
        cli.print(f"❌ Load failed: {load_result.error}", style="bold red")
        return None

    data = load_result.unwrap()
    cli.print("✅ Config loaded successfully", style="green")

    # Display loaded data
    if isinstance(data, dict):
        # Use u.transform for JSON conversion
        if isinstance(data, dict):
            transform_result = u.transform(data, to_json=True)
            display_data: FlextCliTypes.Data.CliDataDict = (
                transform_result.unwrap()
                if transform_result.is_success
                else cast("FlextCliTypes.Data.CliDataDict", data)
            )
        else:
            display_data = cast("FlextCliTypes.Data.CliDataDict", data)
        table_result = cli.create_table(
            data=display_data,
            headers=["Key", "Value"],
            title=f"Config from {detected_format.upper()}",
        )
        if table_result.is_success:
            cli.print_table(table_result.unwrap())
        # Cast to expected type (runtime type is compatible)
        return cast("dict[str, object] | None", data)

    return None


# ============================================================================
# PATTERN 10: Multi-format export in YOUR export tool
# ============================================================================


def export_multi_format(
    data: FlextCliTypes.Data.CliDataDict | list[FlextCliTypes.Data.CliDataDict],
    base_path: Path,
) -> FlextCliTypes.Data.CliDataDict:
    """Export same data to multiple formats (JSON, YAML, CSV)."""
    cli.print(f"💾 Multi-format export: {base_path.stem}", style="cyan")

    export_results: dict[str, str] = {}

    # Export to JSON
    json_path = base_path.with_suffix(".json")
    # Handle both single dict and list of dicts
    json_payload = data
    json_result = cli.file_tools.write_json_file(
        json_path, cast("t.GeneralValueType", json_payload), indent=2
    )
    if json_result.is_success:
        size = json_path.stat().st_size
        export_results["JSON"] = f"{size} bytes"
        cli.print(f"✅ JSON: {json_path.name} ({size} bytes)", style="green")

    # Export to YAML
    yaml_path = base_path.with_suffix(".yaml")
    yaml_payload = data
    yaml_result = cli.file_tools.write_yaml_file(
        yaml_path,
        cast("t.GeneralValueType", yaml_payload),
    )
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

    cli.print(f"\n📊 Exported to {len(export_results)} formats", style="bold green")
    return export_results


# ============================================================================
# PATTERN 10: Railway Pattern for File Operations Chain
# ============================================================================


def process_file_pipeline(
    input_file: Path, output_dir: Path
) -> FlextResult[dict[str, object]]:
    """Complete file processing pipeline using Railway Pattern.

    Demonstrates chaining multiple file operations with proper error handling.
    Uses single return point pattern for reduced complexity.
    """
    cli.print(f"\n🔄 Processing file pipeline: {input_file.name}", style="cyan")

    # Initialize result
    result: FlextResult[dict[str, object]]

    # Railway pattern: Chain operations with automatic error propagation

    # Step 1: Validate input file exists and is readable
    if not input_file.exists():
        result = FlextResult[dict[str, object]].fail(f"File not found: {input_file}")
    elif not input_file.is_file():
        result = FlextResult[dict[str, object]].fail(f"Not a file: {input_file}")
    else:
        cli.print("✅ Input validation passed", style="green")

        # Step 2: Read file content
        read_result = cli.file_tools.read_json_file(input_file)
        if read_result.is_failure:
            result = FlextResult[dict[str, object]].fail(
                f"File read failed: {read_result.error}"
            )
        else:
            data = read_result.unwrap()
            cli.print("✅ File read successfully", style="green")

            # Step 3: Validate and transform data
            try:
                if not isinstance(data, dict):
                    result = FlextResult[dict[str, object]].fail(
                        "JSON file must contain a dictionary"
                    )
                else:
                    transformed_data = validate_and_transform_data(
                        cast("dict[str, object]", data)
                    )
                    cli.print("✅ Data validation/transform passed", style="green")

                    # Step 4: Generate multiple output formats
                    output_result = generate_output_files(transformed_data, output_dir)
                    if output_result.is_failure:
                        result = FlextResult[dict[str, object]].fail(
                            output_result.error or "Unknown error"
                        )
                    else:
                        results = output_result.unwrap()
                        cli.print("✅ Output files generated", style="green")

                        # Step 5: Create summary report
                        summary = create_processing_summary(results)
                        cli.print("✅ Processing summary created", style="green")
                        cli.print(
                            "🎉 File processing pipeline completed successfully!",
                            style="bold green",
                        )
                        result = FlextResult[dict[str, object]].ok(summary)
            except Exception as e:
                result = FlextResult[dict[str, object]].fail(
                    f"Data validation failed: {e}"
                )

    if result.is_failure:
        cli.print(f"❌ Pipeline failed: {result.error}", style="bold red")

    return result


def validate_and_transform_data(data: dict[str, object]) -> dict[str, object]:
    """Validate and transform input data."""
    # Ensure required fields exist
    if not isinstance(data, dict):
        msg = "Data must be a dictionary"
        raise TypeError(msg)

    # Add processing metadata
    transformed = dict(data)  # Copy
    transformed["processed_at"] = "2025-11-23T10:00:00Z"
    transformed["pipeline_version"] = "2.0"
    transformed["validated"] = True

    return transformed


def generate_output_files(
    data: dict[str, object], output_dir: Path
) -> FlextResult[dict[str, Path]]:
    """Generate multiple output file formats."""
    output_dir.mkdir(exist_ok=True)
    base_name = "processed_data"

    results = {}

    # JSON output
    json_file = output_dir / f"{base_name}.json"
    json_result = cli.file_tools.write_json_file(
        json_file, cast("t.GeneralValueType", data)
    )
    if json_result.is_failure:
        return FlextResult[dict[str, Path]].fail(
            f"JSON export failed: {json_result.error}"
        )
    results["json"] = json_file

    # YAML output
    yaml_file = output_dir / f"{base_name}.yaml"
    yaml_result = cli.file_tools.write_yaml_file(
        yaml_file, cast("t.GeneralValueType", data)
    )
    if yaml_result.is_failure:
        return FlextResult[dict[str, Path]].fail(
            f"YAML export failed: {yaml_result.error}"
        )
    results["yaml"] = yaml_file

    # CSV output (if data contains list)
    if "items" in data and isinstance(data["items"], list):
        csv_file = output_dir / f"{base_name}.csv"
        csv_result = cli.file_tools.write_csv_file(csv_file, data["items"])
        if csv_result.is_failure:
            return FlextResult[dict[str, Path]].fail(
                f"CSV export failed: {csv_result.error}"
            )
        results["csv"] = csv_file

    return FlextResult[dict[str, Path]].ok(results)


def create_processing_summary(results: dict[str, Path]) -> dict[str, object]:
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


def main() -> None:  # noqa: PLR0914, PLR0915
    """Examples of using file operations in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  File Operations Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")

    # Setup temp directories
    temp_dir = Path(tempfile.gettempdir()) / "flext_demo"
    temp_dir.mkdir(exist_ok=True)

    # Example 1: JSON preferences
    cli.print("\n1. JSON Config Files (user preferences):", style="bold cyan")
    prefs: FlextCliTypes.Data.CliDataDict = {
        "theme": "dark",
        "font_size": 14,
        "auto_save": True,
    }
    save_user_preferences(prefs, temp_dir)
    load_user_preferences(temp_dir)

    # Example 2: YAML deployment config
    cli.print("\n2. YAML Configuration (deployment):", style="bold cyan")
    deploy_config: FlextCliTypes.Data.CliDataDict = {
        "environment": "staging",
        "host": "staging.example.com",
        "platform": platform.system(),
    }
    yaml_file = temp_dir / "deploy.yaml"
    save_deployment_config(deploy_config, yaml_file)
    load_deployment_config(yaml_file)

    # Example 3: Table export
    cli.print("\n3. Data Export (table format):", style="bold cyan")
    sample_data: list[FlextCliTypes.Data.CliDataDict] = [
        {"id": 1, "name": "Alice", "status": "active"},
        {"id": 2, "name": "Bob", "status": "inactive"},
    ]
    report_file = temp_dir / "report.txt"
    export_database_report(sample_data, report_file, format_type="grid")

    # Example 4: Directory listing
    cli.print("\n4. Directory Operations (file browser):", style="bold cyan")
    list_project_files(Path.cwd())

    # Example 5: Directory tree
    cli.print("\n5. Directory Tree (structure view):", style="bold cyan")
    show_directory_tree(Path.cwd(), max_items=10)

    # Example 6: Data validation
    cli.print("\n6. Data Validation (ETL pipeline):", style="bold cyan")
    test_data: FlextCliTypes.Data.CliDataDict = {"id": 1, "name": "test", "value": 100}
    test_file = temp_dir / "test_data.json"
    cli.file_tools.write_json_file(test_file, test_data)
    validate_and_import_data(test_file)

    # Example 7: CSV export/import
    cli.print("\n7. CSV Export/Import (with headers):", style="bold cyan")
    csv_data: list[FlextCliTypes.Data.CliDataDict] = [
        {"employee_id": 101, "name": "Alice Smith", "department": "Engineering"},
        {"employee_id": 102, "name": "Bob Jones", "department": "Sales"},
        {"employee_id": 103, "name": "Carol White", "department": "Marketing"},
    ]
    csv_file = temp_dir / "employees.csv"
    export_to_csv(csv_data, csv_file)
    import_from_csv(csv_file)

    # Example 8: Binary file operations
    cli.print("\n8. Binary File Operations:", style="bold cyan")
    binary_input = temp_dir / "input.bin"
    binary_output = temp_dir / "output.bin"
    binary_input.write_bytes(b"Binary data content example" * 50)
    process_binary_file(binary_input, binary_output)

    # Example 9: Auto-format detection
    cli.print("\n9. Auto-Format Detection:", style="bold cyan")
    auto_config: FlextCliTypes.Data.CliDataDict = {
        "app": "demo",
        "version": "1.0",
        "enabled": True,
    }
    auto_json = temp_dir / "auto_config.json"
    auto_yaml = temp_dir / "auto_config.yaml"
    cli.file_tools.write_json_file(auto_json, auto_config)
    cli.file_tools.write_yaml_file(auto_yaml, auto_config)
    load_config_auto_detect(auto_json)
    load_config_auto_detect(auto_yaml)

    # Example 10: Multi-format export
    cli.print("\n10. Multi-Format Export:", style="bold cyan")
    multi_data: list[FlextCliTypes.Data.CliDataDict] = [
        {"metric": "CPU", "value": "75%", "status": "OK"},
        {"metric": "Memory", "value": "82%", "status": "Warning"},
    ]
    export_multi_format(multi_data, temp_dir / "metrics")

    # Example 11: Railway Pattern Pipeline
    cli.print("\n11. Railway Pattern Pipeline (complete workflow):", style="bold cyan")
    pipeline_input: FlextCliTypes.Data.CliDataDict = {
        "name": "pipeline_demo",
        "version": "1.0",
        "items": [
            {"id": 1, "name": "task1", "status": "completed"},
            {"id": 2, "name": "task2", "status": "pending"},
        ],
    }
    pipeline_file = temp_dir / "pipeline_input.json"
    cli.file_tools.write_json_file(pipeline_file, pipeline_input)
    pipeline_result = process_file_pipeline(pipeline_file, temp_dir / "pipeline_output")

    if pipeline_result.is_success:
        summary = pipeline_result.unwrap()
        cli.print(f"   📊 Pipeline summary: {summary}", style="cyan")

    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)

    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ File Operations Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")

    # Integration guide
    cli.print("\n💡 Integration Tips:", style="bold cyan")
    cli.print("  • JSON: Use file_tools.read_json() / write_json()", style="white")
    cli.print("  • YAML: Use file_tools.read_yaml_file() / write_yaml()", style="white")
    cli.print(
        "  • CSV: Use read_csv_file_with_headers() for structured data",
        style="white",
    )
    cli.print(
        "  • Binary: Use read_binary_file() for images, PDFs, etc.",
        style="white",
    )
    cli.print(
        "  • Auto-detect: Use load_file_auto() for flexible loading",
        style="white",
    )
    cli.print("  • Tables: Use FlextCliTables for ASCII table export", style="white")
    cli.print("  • All methods return FlextResult for error handling", style="white")


if __name__ == "__main__":
    main()

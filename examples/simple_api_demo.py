"""Simple API Demo - Quick Reference for flext-cli.

A quick reference showing common flext-cli patterns in one place.

WHEN TO USE flext-cli:
- Building any Python CLI application
- Need styled terminal output (colors, tables, progress)
- Want error handling without exceptions (FlextCore.Result)
- Need file I/O (JSON, YAML) with validation
- Building interactive CLI tools

QUICK START:
```python
from flext_cli import FlextCli, FlextCliTables
from flext_core import FlextCore

cli = FlextCli.get_instance()

# Styled output
cli.print("Hello!", style="green")

# Tables
cli.create_table(data={"key": "value"}, headers=["Field", "Value"])

# File I/O
cli.file_tools.write_json_file(path, data)
```

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
import platform
import tempfile
from pathlib import Path
from typing import cast

from flext_core import FlextCore

from flext_cli import FlextCli, FlextCliTables
from flext_cli.typings import FlextCliTypes

cli = FlextCli.get_instance()


def main() -> None:
    """Quick reference of flext-cli patterns."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  FLEXT-CLI Quick Reference", style="bold white on blue")
    cli.print("=" * 70, style="bold blue")

    # 1. STYLED OUTPUT
    cli.print("\n1️⃣  Styled Output (replace print):", style="bold cyan")
    cli.print("   ✅ Success message", style="green")
    cli.print("   ❌ Error message", style="bold red")
    cli.print("   ⚠️  Warning message", style="yellow")
    cli.print("   ℹ️  Info message", style="cyan")

    # 2. TABLES (Rich)
    cli.print("\n2️⃣  Rich Tables (terminal display):", style="bold cyan")
    system_info: FlextCliTypes.Data.CliDataDict = cast(
        "FlextCliTypes.Data.CliDataDict",
        {
            "Platform": platform.system(),
            "Python": platform.python_version(),
            "Machine": platform.machine(),
        },
    )

    table_result = cli.create_table(
        data=system_info, headers=["Property", "Value"], title="💻 System Info"
    )
    if table_result.is_success:
        cli.print_table(table_result.unwrap())

    # 3. ASCII TABLES (for logs/files)
    cli.print("\n3️⃣  ASCII Tables (logs/files):", style="bold cyan")

    tables = FlextCliTables()

    # Type annotation for table data - list of dicts with object values
    table_data: list[FlextCore.Types.Dict] = cast(
        "list[FlextCore.Types.Dict]",
        [{"metric": "CPU", "value": "85%"}, {"metric": "Memory", "value": "12GB"}],
    )
    ascii_result = tables.create_table(table_data, table_format="grid")
    if ascii_result.is_success:
        cli.print(ascii_result.unwrap(), style="white")

    # 4. FILE I/O
    cli.print("\n4️⃣  File Operations (JSON/YAML):", style="bold cyan")
    temp_file = Path(tempfile.gettempdir()) / "demo.json"

    # Write
    test_data = {
        "app": "demo",
        "user": os.getenv("USER", "unknown"),
        "pid": os.getpid(),
    }
    write_result = cli.file_tools.write_json_file(temp_file, test_data)
    if write_result.is_success:
        size = temp_file.stat().st_size
        cli.print(f"   ✅ Wrote {size} bytes to {temp_file.name}", style="green")

    # Read
    read_result = cli.file_tools.read_json_file(temp_file)
    if read_result.is_success:
        # Narrow type - we know it's a dict from our write operation
        read_data = read_result.unwrap()
        if isinstance(read_data, dict):
            cli.print(
                f"   ✅ Read data back: user={read_data.get('user', 'unknown')}",
                style="green",
            )

    temp_file.unlink(missing_ok=True)

    # 5. DIRECTORY TREE
    cli.print("\n5️⃣  Directory Tree (hierarchical display):", style="bold cyan")
    cwd = Path.cwd()
    tree_result = cli.create_tree(f"📁 {cwd.name}")
    if tree_result.is_success:
        tree = tree_result.unwrap()
        for item in sorted(cwd.iterdir())[:7]:
            if item.is_dir():
                tree.add(f"📂 {item.name}/")
            else:
                tree.add(f"📄 {item.name}")
        cli.formatters.get_console().print(tree)

    # 6. ERROR HANDLING
    cli.print("\n6️⃣  Error Handling (FlextCore.Result pattern):", style="bold cyan")

    # Success case
    result = cli.file_tools.read_json_file(temp_file)
    if result.is_failure:
        # Safe string slicing with None check
        error_msg = result.error or "Unknown error"
        cli.print(f"   ℹ️  File not found (expected): {error_msg[:50]}...", style="cyan")

    # Validation example

    def validate_positive(n: int) -> FlextCore.Result[int]:
        if n < 0:
            return FlextCore.Result[int].fail("Must be positive")
        return FlextCore.Result[int].ok(n * 2)

    valid = validate_positive(10)
    if valid.is_success:
        cli.print(f"   ✅ Valid: {valid.unwrap()}", style="green")

    invalid = validate_positive(-5)
    if invalid.is_failure:
        cli.print(f"   ℹ️  Invalid: {invalid.error}", style="yellow")

    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Quick Reference Complete!", style="bold green")
    cli.print("=" * 70, style="bold blue")

    # Usage summary
    cli.print("\n📚 Common Patterns:", style="bold cyan")
    cli.print(
        """
  # Initialize (once)
  from flext_cli import FlextCli
  cli = FlextCli.get_instance()

  # Styled output
  cli.print("message", style="green")

  # Tables (terminal)
  cli.create_table(data={...}, headers=[...], title="...")

  # Tables (files/logs)
  from flext_cli import FlextCliTables
  tables = FlextCliTables()
  tables.create_table(data=[...], table_format="grid")

  # File I/O
  cli.file_tools.write_json_file(path, data)
  result = cli.file_tools.read_json_file(path)

  # Error handling
  if result.is_success:
      data = result.unwrap()
  else:
      print(result.error)
    """,
        style="white",
    )

    cli.print("\n💡 Next Steps:", style="bold cyan")
    cli.print("  • See examples/01_getting_started.py for basics", style="white")
    cli.print(
        "  • See examples/02_output_formatting.py for output patterns", style="white"
    )
    cli.print(
        "  • See examples/03_interactive_prompts.py for user input", style="white"
    )
    cli.print(
        "  • See examples/11_complete_integration.py for full apps", style="white"
    )


if __name__ == "__main__":
    main()

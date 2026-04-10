"""Testing Utilities - Testing YOUR CLI with flext-.

WHEN TO USE THIS:
- Writing tests for CLI applications
- Need to test command outputs
- Want to mock user interactions
- Testing CLI error scenarios
- Building testable CLI tools

FLEXT-CLI PROVIDES:
- r pattern for testable code
- Output capture via formatters
- Mockable prompt system
- File operation testing utilities
- Integration testing patterns

HOW TO USE IN YOUR CLI:
Write comprehensive tests for YOUR CLI application

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from collections.abc import Mapping, MutableMapping
from pathlib import Path

from examples import t
from flext_cli import cli
from flext_core import r


def _temp_file_path(filename: str, *, base_dir: Path | None = None) -> Path:
    """Resolve an example temp file path."""
    return (
        base_dir if base_dir is not None else Path(tempfile.gettempdir())
    ) / filename


def my_cli_command(name: str) -> r[str]:
    """Example CLI command to test."""
    if not name:
        return r[str].fail("Name cannot be empty")
    result = f"Hello, {name}!"
    cli.print(result, style="green")
    return r[str].ok(result)


def test_cli_command() -> None:
    """Test CLI command in YOUR test suite."""
    cli.print("\n🧪 Testing CLI Command:", style="bold cyan")
    result = my_cli_command("World")
    if not result.is_success:
        cli.print(f"   ❌ Command should succeed: {result.error}", style="red")
        return
    if result.value != "Hello, World!":
        cli.print("   ❌ Unexpected output", style="red")
        return
    cli.print("   ✅ Success case passed", style="green")
    result = my_cli_command("")
    if not result.is_failure:
        cli.print("   ❌ Command should fail with empty name", style="red")
        return
    error_msg = result.error or ""
    if "empty" not in error_msg.lower():
        cli.print("   ❌ Unexpected error message", style="red")
        return
    cli.print("   ✅ Failure case passed", style="green")


def save_config_command(
    config: t.ContainerMapping,
    *,
    base_dir: Path | None = None,
) -> r[bool]:
    """CLI command that saves config."""
    temp_file = _temp_file_path("test_config.json", base_dir=base_dir)
    return (
        cli
        .write_json_file(temp_file, config)
        .map_error(
            lambda error: f"Save failed: {error}",
        )
        .map(
            lambda _: True,
        )
    )


def test_file_operations() -> None:
    """Test file operations in YOUR test suite."""
    cli.print("\n📄 Testing File Operations:", style="bold cyan")
    config_data = {"test": True, "value": 123}
    config: t.ContainerMapping = dict(config_data)
    result = save_config_command(config)
    if not result.is_success:
        cli.print(f"   ❌ Config save should succeed: {result.error}", style="red")
        return
    cli.print("   ✅ File save test passed", style="green")
    temp_file = Path(tempfile.gettempdir()) / "test_config.json"
    read_result = cli.read_json_file(temp_file)
    if not read_result.is_success:
        cli.print("   ❌ Config read should succeed", style="red")
        return
    loaded = read_result.value
    if not isinstance(loaded, Mapping):
        cli.print("   ❌ Config payload should be a mapping", style="red")
        return
    if loaded.get("test") is not True:
        cli.print("   ❌ Config value mismatch", style="red")
        return
    cli.print("   ✅ File read test passed", style="green")
    temp_file.unlink(missing_ok=True)


def interactive_command() -> r[str]:
    """Command with user prompts to test."""
    prompts = cli
    prompts.interactive_mode = False
    name_result = prompts.prompt("Enter name:", default="TestUser")
    if name_result.is_failure:
        return r[str].fail(f"Prompt failed: {name_result.error}")
    name = name_result.value
    return r[str].ok(f"Hello, {name}!")


def test_interactive_command() -> None:
    """Test interactive commands in YOUR test suite."""
    cli.print("\n🎭 Testing Interactive Commands:", style="bold cyan")
    result = interactive_command()
    if not result.is_success:
        cli.print(
            f"   ❌ Interactive command should succeed: {result.error}",
            style="red",
        )
        return
    if "TestUser" not in result.value:
        cli.print("   ❌ Should use default value", style="red")
        return
    cli.print("   ✅ Interactive command test passed", style="green")


def risky_operation(value: int) -> r[int]:
    """Operation that might fail."""
    if value < 0:
        return r[int].fail("Value must be positive")
    if value > 100:
        return r[int].fail("Value too large")
    return r[int].ok(value * 2)


def test_error_scenarios() -> None:
    """Test error handling in YOUR test suite."""
    cli.print("\n❌ Testing Error Scenarios:", style="bold cyan")
    result = risky_operation(-1)
    if not result.is_failure:
        cli.print("   ❌ Should fail with negative value", style="red")
        return
    error_msg = result.error or ""
    if "positive" not in error_msg:
        cli.print("   ❌ Unexpected error message", style="red")
        return
    cli.print("   ✅ Negative value test passed", style="green")
    result = risky_operation(200)
    if not result.is_failure:
        cli.print("   ❌ Should fail with large value", style="red")
        return
    error_msg = result.error or ""
    if "too large" not in error_msg.lower():
        cli.print("   ❌ Unexpected error message", style="red")
        return
    cli.print("   ✅ Large value test passed", style="green")
    result = risky_operation(10)
    if not result.is_success:
        cli.print(f"   ❌ Should succeed with valid value: {result.error}", style="red")
        return
    if result.value != 20:
        cli.print("   ❌ Unexpected result", style="red")
        return
    cli.print("   ✅ Valid value test passed", style="green")


def _finalize_workflow_data(
    temp_file: Path,
    read_data: t.Cli.JsonValue,
) -> r[Mapping[str, t.Cli.JsonValue]]:
    """Validate workflow payload, mark it processed, and clean up the temp file."""
    temp_file.unlink(missing_ok=True)
    if not isinstance(read_data, Mapping):
        return r[Mapping[str, t.Cli.JsonValue]].fail(
            "Workflow payload must be a mapping",
        )
    loaded: MutableMapping[str, t.Cli.JsonValue] = {
        str(key): value for key, value in read_data.items()
    }
    loaded["status"] = "completed"
    loaded["processed"] = True
    return r[Mapping[str, t.Cli.JsonValue]].ok(loaded)


def full_workflow_command(
    *,
    base_dir: Path | None = None,
) -> r[Mapping[str, t.Cli.JsonValue]]:
    """Complete workflow to test."""
    data: t.ContainerMapping = {"status": "processing", "items": [1, 2, 3]}
    temp_file = _temp_file_path("workflow_test.json", base_dir=base_dir)
    result = (
        cli
        .write_json_file(temp_file, data)
        .map_error(
            lambda error: f"Write failed: {error}",
        )
        .flat_map(
            lambda _: cli.read_json_file(temp_file).map_error(
                lambda error: f"Read failed: {error}",
            ),
        )
        .flat_map(
            lambda read_data: _finalize_workflow_data(temp_file, read_data),
        )
    )
    if result.is_failure:
        temp_file.unlink(missing_ok=True)
    return result


def test_integration() -> None:
    """Integration test for YOUR CLI workflow."""
    cli.print("\n🔄 Testing Integration Workflow:", style="bold cyan")
    result = full_workflow_command()
    if not result.is_success:
        cli.print(f"   ❌ Workflow should succeed: {result.error}", style="red")
        return
    data = result.value
    if data["status"] != "completed":
        cli.print("   ❌ Status should be updated", style="red")
        return
    if data["processed"] is not True:
        cli.print("   ❌ Should be marked as processed", style="red")
        return
    cli.print("   ✅ Integration test passed", style="green")


def main() -> None:
    """Examples of testing patterns for YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Testing Utilities Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")
    test_cli_command()
    test_file_operations()
    test_interactive_command()
    test_error_scenarios()
    test_integration()
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ All Tests Passed!", style="bold green")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n💡 Testing Tips:", style="bold cyan")
    cli.print("  • Use r returns for testable commands", style="white")
    cli.print("  • Test both success and failure cases", style="white")
    cli.print("  • Use non-interactive prompts in tests", style="white")
    cli.print("  • Clean up temp files after tests", style="white")
    cli.print("  • Write integration tests for workflows", style="white")
    cli.print("\n📝 pytest Example:", style="bold cyan")
    cli.print(
        '\ndef test_my_command():\n    from flext_cli import cli\n\n    result = my_command(param="test")\n\n    assert result.is_success\n    assert result.value == expected_value\n    ',
        style="cyan",
    )


if __name__ == "__main__":
    main()

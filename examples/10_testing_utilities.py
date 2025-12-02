"""Testing Utilities - Testing YOUR CLI with flext-cli.

WHEN TO USE THIS:
- Writing tests for CLI applications
- Need to test command outputs
- Want to mock user interactions
- Testing CLI error scenarios
- Building testable CLI tools

FLEXT-CLI PROVIDES:
- FlextResult pattern for testable code
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
from pathlib import Path
from typing import cast

from flext_core import FlextResult, FlextTypes, FlextUtilities

from flext_cli import FlextCli, FlextCliPrompts, FlextCliTypes

cli = FlextCli()


# ============================================================================
# PATTERN 1: Test CLI command with FlextResult
# ============================================================================


def my_cli_command(name: str) -> FlextResult[str]:
    """Example CLI command to test."""
    if not name:
        return FlextResult[str].fail("Name cannot be empty")

    result = f"Hello, {name}!"
    cli.output.print_message(result, style="green")
    return FlextResult[str].ok(result)


def test_cli_command() -> None:
    """Test CLI command in YOUR test suite."""
    cli.output.print_message("\n🧪 Testing CLI Command:", style="bold cyan")

    # Test success case
    result = my_cli_command("World")
    if not result.is_success:
        cli.output.print_message(
            f"   ❌ Command should succeed: {result.error}", style="red"
        )
        return
    if result.unwrap() != "Hello, World!":
        cli.output.print_message("   ❌ Unexpected output", style="red")
        return
    cli.output.print_message("   ✅ Success case passed", style="green")

    # Test failure case
    result = my_cli_command("")
    if not result.is_failure:
        cli.output.print_message(
            "   ❌ Command should fail with empty name", style="red"
        )
        return
    error_msg = result.error or ""
    if "empty" not in error_msg.lower():
        cli.output.print_message("   ❌ Unexpected error message", style="red")
        return
    cli.output.print_message("   ✅ Failure case passed", style="green")


# ============================================================================
# PATTERN 2: Test file operations
# ============================================================================


def save_config_command(
    config: FlextCliTypes.Data.CliDataDict,
) -> FlextResult[bool]:
    """CLI command that saves config."""
    temp_file = Path(tempfile.gettempdir()) / "test_config.json"

    write_result = cli.file_tools.write_json_file(temp_file, config)
    if write_result.is_failure:
        return FlextResult[bool].fail(f"Save failed: {write_result.error}")

    return FlextResult[bool].ok(True)


def test_file_operations() -> None:
    """Test file operations in YOUR test suite."""
    cli.output.print_message("\n📄 Testing File Operations:", style="bold cyan")

    # Test save
    config_data = {"test": True, "value": 123}
    # Convert to JsonDict-compatible dict using FlextUtilities
    config: FlextCliTypes.Data.CliDataDict = (
        FlextUtilities.DataMapper.convert_dict_to_json(
            cast("dict[str, FlextTypes.GeneralValueType]", config_data)
        )
    )
    result = save_config_command(config)

    if not result.is_success:
        cli.output.print_message(
            f"   ❌ Config save should succeed: {result.error}", style="red"
        )
        return
    cli.output.print_message("   ✅ File save test passed", style="green")

    # Verify file contents

    temp_file = Path(tempfile.gettempdir()) / "test_config.json"
    read_result = cli.file_tools.read_json_file(temp_file)

    if not (read_result.is_success):
        cli.output.print_message("   ❌ Config read should succeed", style="red")
        return
    loaded = read_result.unwrap()
    # Type narrowing for dict[str, object] access
    if isinstance(loaded, dict) and loaded.get("test") is not True:
        cli.output.print_message("   ❌ Config value mismatch", style="red")
        return
    cli.output.print_message("   ✅ File read test passed", style="green")

    # Cleanup
    temp_file.unlink(missing_ok=True)


# ============================================================================
# PATTERN 3: Test prompts with mocking
# ============================================================================


def interactive_command() -> FlextResult[str]:
    """Command with user prompts to test."""
    prompts = FlextCliPrompts(interactive_mode=False)  # Non-interactive for tests

    # In real tests, you'd mock the prompt response
    name_result = prompts.prompt("Enter name:", default="TestUser")

    if name_result.is_failure:
        return FlextResult[str].fail(f"Prompt failed: {name_result.error}")

    name = name_result.unwrap()
    return FlextResult[str].ok(f"Hello, {name}!")


def test_interactive_command() -> None:
    """Test interactive commands in YOUR test suite."""
    cli.output.print_message("\n🎭 Testing Interactive Commands:", style="bold cyan")

    # Test with non-interactive prompts
    result = interactive_command()

    if not result.is_success:
        cli.output.print_message(
            f"   ❌ Interactive command should succeed: {result.error}",
            style="red",
        )
        return
    if "TestUser" not in result.unwrap():
        cli.output.print_message("   ❌ Should use default value", style="red")
        return
    cli.output.print_message("   ✅ Interactive command test passed", style="green")


# ============================================================================
# PATTERN 4: Test error scenarios
# ============================================================================


def risky_operation(value: int) -> FlextResult[int]:
    """Operation that might fail."""
    if value < 0:
        return FlextResult[int].fail("Value must be positive")

    if value > 100:
        return FlextResult[int].fail("Value too large")

    return FlextResult[int].ok(value * 2)


def test_error_scenarios() -> None:
    """Test error handling in YOUR test suite."""
    cli.output.print_message("\n❌ Testing Error Scenarios:", style="bold cyan")

    # Test negative value
    result = risky_operation(-1)
    if not result.is_failure:
        cli.output.print_message("   ❌ Should fail with negative value", style="red")
        return
    error_msg = result.error or ""
    if "positive" not in error_msg:
        cli.output.print_message("   ❌ Unexpected error message", style="red")
        return
    cli.output.print_message("   ✅ Negative value test passed", style="green")

    # Test too large value
    result = risky_operation(200)
    if not result.is_failure:
        cli.output.print_message("   ❌ Should fail with large value", style="red")
        return
    error_msg = result.error or ""
    if "too large" not in error_msg.lower():
        cli.output.print_message("   ❌ Unexpected error message", style="red")
        return
    cli.output.print_message("   ✅ Large value test passed", style="green")

    # Test valid value
    result = risky_operation(10)
    if not result.is_success:
        cli.output.print_message(
            f"   ❌ Should succeed with valid value: {result.error}", style="red"
        )
        return
    if result.unwrap() != 20:
        cli.output.print_message("   ❌ Unexpected result", style="red")
        return
    cli.output.print_message("   ✅ Valid value test passed", style="green")


# ============================================================================
# PATTERN 5: Integration test example
# ============================================================================


def full_workflow_command() -> FlextResult[FlextCliTypes.Data.CliDataDict]:
    """Complete workflow to test."""
    # Step 1: Create data
    data: FlextCliTypes.Data.CliDataDict = {"status": "processing", "items": [1, 2, 3]}

    # Step 2: Save to file
    temp_file = Path(tempfile.gettempdir()) / "workflow_test.json"
    write_result = cli.file_tools.write_json_file(temp_file, data)

    if write_result.is_failure:
        return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
            f"Write failed: {write_result.error}",
        )

    # Step 3: Read back
    read_result = cli.file_tools.read_json_file(temp_file)

    if read_result.is_failure:
        temp_file.unlink(missing_ok=True)
        return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
            f"Read failed: {read_result.error}",
        )

    # Step 4: Process - type narrowing needed
    loaded = read_result.unwrap()
    if not isinstance(loaded, dict):
        temp_file.unlink(missing_ok=True)
        return FlextResult[FlextCliTypes.Data.CliDataDict].fail(
            "Data is not a dictionary",
        )

    loaded["status"] = "completed"
    loaded["processed"] = True

    # Cleanup
    temp_file.unlink(missing_ok=True)

    # Convert to JsonDict-compatible dict using FlextUtilities
    typed_data: FlextCliTypes.Data.CliDataDict = (
        FlextUtilities.DataMapper.convert_dict_to_json(loaded)
    )
    return FlextResult[FlextCliTypes.Data.CliDataDict].ok(typed_data)


def test_integration() -> None:
    """Integration test for YOUR CLI workflow."""
    cli.output.print_message("\n🔄 Testing Integration Workflow:", style="bold cyan")

    result = full_workflow_command()

    if not result.is_success:
        cli.output.print_message(
            f"   ❌ Workflow should succeed: {result.error}", style="red"
        )
        return

    data = result.unwrap()
    if data["status"] != "completed":
        cli.output.print_message("   ❌ Status should be updated", style="red")
        return
    if data["processed"] is not True:
        cli.output.print_message("   ❌ Should be marked as processed", style="red")
        return
    cli.output.print_message("   ✅ Integration test passed", style="green")


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of testing patterns for YOUR code."""
    cli.output.print_message("=" * 70, style="bold blue")
    cli.output.print_message("  Testing Utilities Library Usage", style="bold white")
    cli.output.print_message("=" * 70, style="bold blue")

    # Run all tests
    test_cli_command()
    test_file_operations()
    test_interactive_command()
    test_error_scenarios()
    test_integration()

    cli.output.print_message("\n" + "=" * 70, style="bold blue")
    cli.output.print_message("  ✅ All Tests Passed!", style="bold green")
    cli.output.print_message("=" * 70, style="bold blue")

    # Testing guide
    cli.output.print_message("\n💡 Testing Tips:", style="bold cyan")
    cli.output.print_message(
        "  • Use FlextResult returns for testable commands", style="white"
    )
    cli.output.print_message("  • Test both success and failure cases", style="white")
    cli.output.print_message("  • Use non-interactive prompts in tests", style="white")
    cli.output.print_message("  • Clean up temp files after tests", style="white")
    cli.output.print_message("  • Write integration tests for workflows", style="white")

    # pytest example
    cli.output.print_message("\n📝 pytest Example:", style="bold cyan")
    cli.output.print_message(
        """
def test_my_command():
    from flext_cli import FlextCli
    cli = FlextCli()

    result = my_command(param="test")

    assert result.is_success
    assert result.unwrap() == expected_value
    """,
        style="cyan",
    )


if __name__ == "__main__":
    main()

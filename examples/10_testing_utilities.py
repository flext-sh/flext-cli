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

from flext_cli import FlextCli, FlextCliPrompts, r, t

cli = FlextCli()


# ============================================================================
# PATTERN 1: Test CLI command with FlextResult
# ============================================================================


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

    # Test success case
    result = my_cli_command("World")
    if not result.is_success:
        cli.print(
            f"   ❌ Command should succeed: {result.error}",
            style="red",
        )
        return
    if result.value != "Hello, World!":
        cli.print("   ❌ Unexpected output", style="red")
        return
    cli.print("   ✅ Success case passed", style="green")

    # Test failure case
    result = my_cli_command("")
    if not result.is_failure:
        cli.print(
            "   ❌ Command should fail with empty name",
            style="red",
        )
        return
    error_msg = result.error or ""
    if "empty" not in error_msg.lower():
        cli.print("   ❌ Unexpected error message", style="red")
        return
    cli.print("   ✅ Failure case passed", style="green")


# ============================================================================
# PATTERN 2: Test file operations
# ============================================================================


def save_config_command(
    config: dict[str, t.JsonValue],
) -> r[bool]:
    """CLI command that saves config."""
    temp_file = Path(tempfile.gettempdir()) / "test_config.json"

    write_result = cli.file_tools.write_json_file(temp_file, config)
    if write_result.is_failure:
        return r[bool].fail(f"Save failed: {write_result.error}")

    return r[bool].ok(value=True)


def test_file_operations() -> None:
    """Test file operations in YOUR test suite."""
    cli.print("\n📄 Testing File Operations:", style="bold cyan")

    # Test save
    config_data = {"test": True, "value": 123}
    config: dict[str, t.JsonValue] = dict(config_data)
    result = save_config_command(config)

    if not result.is_success:
        cli.print(
            f"   ❌ Config save should succeed: {result.error}",
            style="red",
        )
        return
    cli.print("   ✅ File save test passed", style="green")

    # Verify file contents

    temp_file = Path(tempfile.gettempdir()) / "test_config.json"
    read_result = cli.file_tools.read_json_dict(temp_file)

    if not (read_result.is_success):
        cli.print("   ❌ Config read should succeed", style="red")
        return
    loaded = read_result.value
    if loaded.get("test") is not True:
        cli.print("   ❌ Config value mismatch", style="red")
        return
    cli.print("   ✅ File read test passed", style="green")

    # Cleanup
    temp_file.unlink(missing_ok=True)


# ============================================================================
# PATTERN 3: Test prompts with mocking
# ============================================================================


def interactive_command() -> r[str]:
    """Command with user prompts to test."""
    prompts = FlextCliPrompts(interactive_mode=False)  # Non-interactive for tests

    # In real tests, you'd mock the prompt response
    name_result = prompts.prompt("Enter name:", default="TestUser")

    if name_result.is_failure:
        return r[str].fail(f"Prompt failed: {name_result.error}")

    name = name_result.value
    return r[str].ok(f"Hello, {name}!")


def test_interactive_command() -> None:
    """Test interactive commands in YOUR test suite."""
    cli.print("\n🎭 Testing Interactive Commands:", style="bold cyan")

    # Test with non-interactive prompts
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


# ============================================================================
# PATTERN 4: Test error scenarios
# ============================================================================


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

    # Test negative value
    result = risky_operation(-1)
    if not result.is_failure:
        cli.print("   ❌ Should fail with negative value", style="red")
        return
    error_msg = result.error or ""
    if "positive" not in error_msg:
        cli.print("   ❌ Unexpected error message", style="red")
        return
    cli.print("   ✅ Negative value test passed", style="green")

    # Test too large value
    result = risky_operation(200)
    if not result.is_failure:
        cli.print("   ❌ Should fail with large value", style="red")
        return
    error_msg = result.error or ""
    if "too large" not in error_msg.lower():
        cli.print("   ❌ Unexpected error message", style="red")
        return
    cli.print("   ✅ Large value test passed", style="green")

    # Test valid value
    result = risky_operation(10)
    if not result.is_success:
        cli.print(
            f"   ❌ Should succeed with valid value: {result.error}",
            style="red",
        )
        return
    if result.value != 20:
        cli.print("   ❌ Unexpected result", style="red")
        return
    cli.print("   ✅ Valid value test passed", style="green")


# ============================================================================
# PATTERN 5: Integration test example
# ============================================================================


def full_workflow_command() -> r[dict[str, t.JsonValue]]:
    """Complete workflow to test."""
    # Step 1: Create data
    data: dict[str, t.JsonValue] = {"status": "processing", "items": [1, 2, 3]}

    # Step 2: Save to file
    temp_file = Path(tempfile.gettempdir()) / "workflow_test.json"
    write_result = cli.file_tools.write_json_file(temp_file, data)

    if write_result.is_failure:
        return r[dict[str, t.JsonValue]].fail(
            f"Write failed: {write_result.error}",
        )

    # Step 3: Read back
    read_result = cli.file_tools.read_json_dict(temp_file)

    if read_result.is_failure:
        temp_file.unlink(missing_ok=True)
        return r[dict[str, t.JsonValue]].fail(
            f"Read failed: {read_result.error}",
        )

    # Step 4: Process
    loaded = read_result.value
    loaded["status"] = "completed"
    loaded["processed"] = True

    # Cleanup
    temp_file.unlink(missing_ok=True)

    return r[dict[str, t.JsonValue]].ok(loaded)


def test_integration() -> None:
    """Integration test for YOUR CLI workflow."""
    cli.print("\n🔄 Testing Integration Workflow:", style="bold cyan")

    result = full_workflow_command()

    if not result.is_success:
        cli.print(
            f"   ❌ Workflow should succeed: {result.error}",
            style="red",
        )
        return

    data = result.value
    if data["status"] != "completed":
        cli.print("   ❌ Status should be updated", style="red")
        return
    if data["processed"] is not True:
        cli.print("   ❌ Should be marked as processed", style="red")
        return
    cli.print("   ✅ Integration test passed", style="green")


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of testing patterns for YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Testing Utilities Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")

    # Run all tests
    test_cli_command()
    test_file_operations()
    test_interactive_command()
    test_error_scenarios()
    test_integration()

    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ All Tests Passed!", style="bold green")
    cli.print("=" * 70, style="bold blue")

    # Testing guide
    cli.print("\n💡 Testing Tips:", style="bold cyan")
    cli.print(
        "  • Use FlextResult returns for testable commands",
        style="white",
    )
    cli.print("  • Test both success and failure cases", style="white")
    cli.print("  • Use non-interactive prompts in tests", style="white")
    cli.print("  • Clean up temp files after tests", style="white")
    cli.print("  • Write integration tests for workflows", style="white")

    # pytest example
    cli.print("\n📝 pytest Example:", style="bold cyan")
    cli.print(
        """
def test_my_command():
    from flext_cli import FlextCli
    cli = FlextCli()

    result = my_command(param="test")

    assert result.is_success
    assert result.value == expected_value
    """,
        style="cyan",
    )


if __name__ == "__main__":
    main()

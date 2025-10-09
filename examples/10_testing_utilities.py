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

NOTE: This file demonstrates testing patterns for users, hence S101 (assert usage)
is expected and appropriate - showing users how to write assert-based tests.
"""
# ruff: noqa: S101

from __future__ import annotations

import tempfile
from pathlib import Path

from flext_core import FlextResult

from flext_cli import FlextCli, FlextCliPrompts

cli = FlextCli.get_instance()


# ============================================================================
# PATTERN 1: Test CLI command with FlextResult
# ============================================================================


def my_cli_command(name: str) -> FlextResult[str]:
    """Example CLI command to test."""
    if not name:
        return FlextResult[str].fail("Name cannot be empty")

    result = f"Hello, {name}!"
    cli.formatters.print(result, style="green")
    return FlextResult[str].ok(result)


def test_cli_command() -> None:
    """Test CLI command in YOUR test suite."""
    cli.formatters.print("\n🧪 Testing CLI Command:", style="bold cyan")

    # Test success case
    result = my_cli_command("World")
    assert result.is_success, "Command should succeed"
    assert result.unwrap() == "Hello, World!", "Unexpected output"
    cli.formatters.print("   ✅ Success case passed", style="green")

    # Test failure case
    result = my_cli_command("")
    assert result.is_failure, "Command should fail with empty name"
    error_msg = result.error or ""
    assert "empty" in error_msg.lower(), "Unexpected error message"
    cli.formatters.print("   ✅ Failure case passed", style="green")


# ============================================================================
# PATTERN 2: Test file operations
# ============================================================================


def save_config_command(config: dict) -> FlextResult[None]:
    """CLI command that saves config."""
    temp_file = Path(tempfile.gettempdir()) / "test_config.json"

    write_result = cli.file_tools.write_json_file(temp_file, config)
    if write_result.is_failure:
        return FlextResult[None].fail(f"Save failed: {write_result.error}")

    return FlextResult[None].ok(None)


def test_file_operations() -> None:
    """Test file operations in YOUR test suite."""
    cli.formatters.print("\n📄 Testing File Operations:", style="bold cyan")

    # Test save
    config = {"test": True, "value": 123}
    result = save_config_command(config)

    assert result.is_success, "Config save should succeed"
    cli.formatters.print("   ✅ File save test passed", style="green")

    # Verify file contents

    temp_file = Path(tempfile.gettempdir()) / "test_config.json"
    read_result = cli.file_tools.read_json_file(temp_file)

    assert read_result.is_success, "Config read should succeed"
    loaded = read_result.unwrap()
    # Type narrowing for dict access
    if isinstance(loaded, dict):
        assert loaded.get("test") is True, "Config value mismatch"
    cli.formatters.print("   ✅ File read test passed", style="green")

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
    cli.formatters.print("\n🎭 Testing Interactive Commands:", style="bold cyan")

    # Test with non-interactive prompts
    result = interactive_command()

    assert result.is_success, "Interactive command should succeed"
    assert "TestUser" in result.unwrap(), "Should use default value"
    cli.formatters.print("   ✅ Interactive command test passed", style="green")


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
    cli.formatters.print("\n❌ Testing Error Scenarios:", style="bold cyan")

    # Test negative value
    result = risky_operation(-1)
    assert result.is_failure, "Should fail with negative value"
    error_msg = result.error or ""
    assert "positive" in error_msg, "Unexpected error message"
    cli.formatters.print("   ✅ Negative value test passed", style="green")

    # Test too large value
    result = risky_operation(200)
    assert result.is_failure, "Should fail with large value"
    error_msg = result.error or ""
    assert "too large" in error_msg.lower(), "Unexpected error message"
    cli.formatters.print("   ✅ Large value test passed", style="green")

    # Test valid value
    result = risky_operation(10)
    assert result.is_success, "Should succeed with valid value"
    assert result.unwrap() == 20, "Unexpected result"
    cli.formatters.print("   ✅ Valid value test passed", style="green")


# ============================================================================
# PATTERN 5: Integration test example
# ============================================================================


def full_workflow_command() -> FlextResult[dict]:
    """Complete workflow to test."""
    # Step 1: Create data
    data = {"status": "processing", "items": [1, 2, 3]}

    # Step 2: Save to file
    temp_file = Path(tempfile.gettempdir()) / "workflow_test.json"
    write_result = cli.file_tools.write_json_file(temp_file, data)

    if write_result.is_failure:
        return FlextResult[dict].fail(f"Write failed: {write_result.error}")

    # Step 3: Read back
    read_result = cli.file_tools.read_json_file(temp_file)

    if read_result.is_failure:
        temp_file.unlink(missing_ok=True)
        return FlextResult[dict].fail(f"Read failed: {read_result.error}")

    # Step 4: Process - type narrowing needed
    loaded = read_result.unwrap()
    if not isinstance(loaded, dict):
        temp_file.unlink(missing_ok=True)
        return FlextResult[dict].fail("Data is not a dictionary")

    loaded["status"] = "completed"
    loaded["processed"] = True

    # Cleanup
    temp_file.unlink(missing_ok=True)

    return FlextResult[dict].ok(loaded)


def test_integration() -> None:
    """Integration test for YOUR CLI workflow."""
    cli.formatters.print("\n🔄 Testing Integration Workflow:", style="bold cyan")

    result = full_workflow_command()

    assert result.is_success, "Workflow should succeed"

    data = result.unwrap()
    assert data["status"] == "completed", "Status should be updated"
    assert data["processed"] is True, "Should be marked as processed"
    cli.formatters.print("   ✅ Integration test passed", style="green")


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of testing patterns for YOUR code."""
    cli.formatters.print("=" * 70, style="bold blue")
    cli.formatters.print("  Testing Utilities Library Usage", style="bold white")
    cli.formatters.print("=" * 70, style="bold blue")

    # Run all tests
    test_cli_command()
    test_file_operations()
    test_interactive_command()
    test_error_scenarios()
    test_integration()

    cli.formatters.print("\n" + "=" * 70, style="bold blue")
    cli.formatters.print("  ✅ All Tests Passed!", style="bold green")
    cli.formatters.print("=" * 70, style="bold blue")

    # Testing guide
    cli.formatters.print("\n💡 Testing Tips:", style="bold cyan")
    cli.formatters.print(
        "  • Use FlextResult returns for testable commands", style="white"
    )
    cli.formatters.print("  • Test both success and failure cases", style="white")
    cli.formatters.print("  • Use non-interactive prompts in tests", style="white")
    cli.formatters.print("  • Clean up temp files after tests", style="white")
    cli.formatters.print("  • Write integration tests for workflows", style="white")

    # pytest example
    cli.formatters.print("\n📝 pytest Example:", style="bold cyan")
    cli.formatters.print(
        """
def test_my_command():
    from flext_cli import FlextCli
    cli = FlextCli.get_instance()

    result = my_command(param="test")

    assert result.is_success
    assert result.unwrap() == expected_value
    """,
        style="cyan",
    )


if __name__ == "__main__":
    main()

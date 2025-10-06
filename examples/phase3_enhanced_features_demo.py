"""FLEXT-CLI Phase 3 Enhanced Features Demo.

This example demonstrates Phase 3 enhancements:
- Additional Click parameter types (DateTime, UUID, Tuple)
- Advanced Rich features (prompts, confirm dialogs, live displays)
- Testing utilities and patterns
- CLI testing helpers

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import (
    FlextCli,
    FlextCliTesting,
)


def demo_additional_click_types() -> None:
    """Demo 1: Additional Click Parameter Types - DateTime, UUID, Tuple."""
    cli = FlextCli()

    # DateTime parameter type
    cli.click.get_datetime_type(formats=["%Y-%m-%d", "%d/%m/%Y"])

    # UUID parameter type
    cli.click.get_uuid_type()

    # Tuple parameter type
    cli.click.get_tuple_type([int, int, int])

    cli.click.get_tuple_type([str, int])

    # Basic types
    cli.click.get_bool_type()
    cli.click.get_string_type()
    cli.click.get_int_type()
    cli.click.get_float_type()


def demo_advanced_rich_features() -> None:
    """Demo 2: Advanced Rich Features - Prompts, Confirm, Live Displays."""
    cli = FlextCli()

    # Interactive prompts (non-interactive demo - showing API)

    # Live display
    table_result = cli.formatters.create_table(title="Live Data")
    if table_result.is_success:
        table = table_result.unwrap()
        # Rich Table API (returned from create_table)
        table.add_column("Status")
        table.add_column("Value")

        live_result = cli.formatters.create_live_display(table)
        if live_result.is_success:
            pass

    # Example: Non-interactive prompt demonstration


def demo_testing_utilities() -> None:
    """Demo 3: Testing Utilities and Patterns."""
    # Initialize testing utilities
    runner = FlextCliTestRunner()
    scenarios = FlextCliTesting.MockScenarios()

    # Mock scenarios
    config_result = scenarios.mock_user_config(
        profile="test",
        debug_mode=True,
        output_format="json",
        api_key="test-key-12345",
    )
    if config_result.is_success:
        config_result.unwrap()

    context_result = scenarios.mock_cli_context(
        command_name="process",
        params={"input_file": "test.csv", "verbose": True},
    )
    if context_result.is_success:
        context_result.unwrap()

    # CLI testing helpers

    # Isolated runner
    isolated_result = runner.create_isolated_runner(mix_stderr=True)
    if isolated_result.is_success:
        pass


def demo_integration_test_pattern() -> None:
    """Demo 4: Integration Test Pattern Example."""


def demo_complete_phase3_workflow() -> None:
    """Demo 5: Complete Phase 3 Workflow - All Features Together."""
    cli = FlextCli()
    runner = FlextCliTestRunner()
    scenarios = FlextCliTesting.MockScenarios()

    # Create command with advanced parameter types
    cli.click.get_datetime_type()
    cli.click.get_uuid_type()

    # Setup mock configuration
    config_result = scenarios.mock_user_config(
        profile="production",
        debug_mode=False,
        output_format="table",
    )
    if config_result.is_success:
        config_result.unwrap()

    # Create live display for progress
    table_result = cli.formatters.create_table(title="Processing Status")
    if table_result.is_success:
        table = table_result.unwrap()
        # Use Rich Table API directly
        table.add_column("Task")
        table.add_column("Status")
        table.add_row("Data Loading", "✅ Complete")
        table.add_row("Processing", "⏳ In Progress")

    # Test command execution

    @cli.main.command()
    def process(verbose: bool = False) -> None:
        """Process data."""
        if verbose:
            pass

    # Run test
    test_result = runner.invoke_command(
        cli_main=cli.main,
        command_name="process",
        args=["--verbose"],
    )
    if test_result.is_success:
        test_result.unwrap()


def main() -> None:
    """Run all Phase 3 demos."""
    # Run all demos
    demo_additional_click_types()
    demo_advanced_rich_features()
    demo_testing_utilities()
    demo_integration_test_pattern()
    demo_complete_phase3_workflow()

    # Final summary


if __name__ == "__main__":
    main()

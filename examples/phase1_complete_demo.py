"""FLEXT-CLI Phase 1 Complete Demo.

This example demonstrates ALL Phase 1 components:
- FlextCliCli: Click abstraction layer
- FlextCliFormatters: Rich abstraction layer
- FlextCliTables: Tabulate integration
- FlextCliMain: Command registration system
- FlextCli: Unified API facade

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from rich.text import Text

from flext_cli import (
    FlextCli,
    FlextCliCli,
    FlextCliFormatters,
    FlextCliMain,
    FlextCliTables,
)


def demo_click_abstraction() -> None:
    """Demo 1: Click Abstraction Layer - NO direct Click imports needed!."""
    # Initialize Click wrapper
    click_wrapper = FlextCliCli()

    # Create command decorator
    cmd_result = click_wrapper.create_command_decorator(
        name="hello",
        help="Greet someone",
    )

    if cmd_result.is_success:
        pass

    # Create option decorator
    opt_result = click_wrapper.create_option_decorator(
        "--name",
        "-n",
        default="World",
        help="Name to greet",
    )

    if opt_result.is_success:
        pass

    # Get parameter types (NO Click imports!)
    click_wrapper.get_choice_type(["red", "green", "blue"])

    click_wrapper.get_path_type(exists=True, file_okay=True)

    click_wrapper.get_int_range_type(min=1, max=100)


def demo_rich_formatters() -> None:
    """Demo 2: Rich Abstraction Layer - NO direct Rich imports needed!."""
    # Initialize Rich wrapper
    formatters = FlextCliFormatters()

    # 1. Create a panel
    panel_result = formatters.create_panel(
        content="This is a beautiful panel created WITHOUT importing Rich!",
        title="Demo Panel",
        border_style="blue",
    )

    if panel_result.is_success:
        formatters.print_rich(renderable=panel_result.unwrap())

    # 2. Print styled text
    styled_text = Text("Bold Red Text", style="bold red")
    formatters.print_rich(renderable=styled_text)

    # 3. Create a progress bar
    progress_result = formatters.create_progress()
    if progress_result.is_success:
        pass

    # 4. Render markdown
    markdown_result = formatters.render_markdown(
        """
# Markdown Support
- **Bold** and *italic*
- Code: `print('hello')`
- Lists work great!
        """
    )
    if markdown_result.is_success:
        formatters.print_rich(renderable=markdown_result.unwrap())

    # 5. Syntax highlight code
    code_result = formatters.highlight_code(
        code='def hello():\n    print("Hello from highlighted code!")',
        language="python",
        theme="monokai",
    )
    if code_result.is_success:
        formatters.print_rich(renderable=code_result.unwrap())


def demo_tabulate_tables() -> None:
    """Demo 3: Tabulate Integration - Lightweight ASCII tables."""
    # Initialize Tabulate wrapper
    tables = FlextCliTables()

    # Sample data
    data = [
        {"Name": "Alice", "Age": 30, "City": "NYC"},
        {"Name": "Bob", "Age": 25, "City": "LA"},
        {"Name": "Charlie", "Age": 35, "City": "Chicago"},
    ]

    # 1. Simple table
    simple_result = tables.create_simple_table(data)
    if simple_result.is_success:
        pass

    # 2. Grid table
    grid_result = tables.create_grid_table(data, fancy=False)
    if grid_result.is_success:
        pass

    # 3. Fancy grid table
    fancy_result = tables.create_grid_table(data, fancy=True)
    if fancy_result.is_success:
        pass

    # 4. Markdown table
    markdown_result = tables.create_markdown_table(data)
    if markdown_result.is_success:
        pass

    # 5. Available formats
    tables.list_formats()


def demo_command_registration() -> None:
    """Demo 4: Command Registration System."""
    # Initialize command system
    main_cli = FlextCliMain(
        name="demo-app",
        version="1.0.0",
        description="Demo CLI Application",
    )

    # Register a command programmatically
    def hello_command(name: str = "World") -> None:
        """Say hello to someone."""

    register_result = main_cli.register_command(
        hello_command,
        name="hello",
    )

    if register_result.is_success:
        pass

    # Register a command group
    def config_group() -> None:
        """Configuration commands."""

    group_result = main_cli.register_group(
        config_group,
        name="config",
    )

    if group_result.is_success:
        pass

    # List all commands
    commands_result = main_cli.list_commands()
    if commands_result.is_success:
        commands_result.unwrap()

    # List all groups
    groups_result = main_cli.list_groups()
    if groups_result.is_success:
        groups_result.unwrap()


def demo_unified_api() -> None:
    """Demo 5: Unified API Facade - Single entry point for everything!."""
    # Single entry point for ALL CLI functionality
    cli = FlextCli()

    # Access Click abstraction
    cli.click.get_choice_type(["option1", "option2", "option3"])

    # Access Rich formatters
    panel_result = cli.formatters.create_panel(
        content="Using unified API!",
        title="Unified Access",
    )
    if panel_result.is_success:
        pass

    # Access Tabulate tables
    data = [{"col1": "value1", "col2": "value2"}]
    table_result = cli.tables.create_simple_table(data)
    if table_result.is_success:
        pass

    # Access command registration
    commands_result = cli.main.list_commands()
    if commands_result.is_success:
        pass

    # Execute to get component status
    execute_result = cli.execute()
    if execute_result.is_success:
        data = execute_result.unwrap()
        components = data.get("components", {})
        for _name, _status in components.items():
            pass


def demo_complete_cli_example() -> None:
    """Demo 6: Complete CLI Application Example."""
    # Initialize unified API
    cli = FlextCli()

    # Create command with decorator pattern
    @cli.main.command()
    def greet(name: str = "World") -> None:
        """Greet someone with styled output."""
        # Use formatters for output
        panel_result = cli.formatters.create_panel(
            content=f"Hello, {name}!",
            title="Greeting",
            border_style="green",
        )
        if panel_result.is_success:
            cli.formatters.print_rich(renderable=panel_result.unwrap())

    # Create command group
    @cli.main.group()
    def data() -> None:
        """Data management commands."""

    # Add subcommand to group
    # Note: In real usage, you'd use @data.command()
    def list_data() -> None:
        """List data entries."""
        sample_data = [
            {"ID": 1, "Name": "Item 1", "Status": "Active"},
            {"ID": 2, "Name": "Item 2", "Status": "Pending"},
            {"ID": 3, "Name": "Item 3", "Status": "Complete"},
        ]

        # Use tables for output
        table_result = cli.tables.create_grid_table(sample_data, fancy=True)
        if table_result.is_success:
            pass

    # Register the subcommand
    data_group_result = cli.main.get_group("data")
    if data_group_result.is_success:
        pass


def main() -> None:
    """Run all Phase 1 demos."""
    # Run all demos
    demo_click_abstraction()
    demo_rich_formatters()
    demo_tabulate_tables()
    demo_command_registration()
    demo_unified_api()
    demo_complete_cli_example()

    # Final summary


if __name__ == "__main__":
    main()

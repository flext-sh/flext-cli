"""FLEXT CLI Main Tests - Comprehensive Command Registration Testing.

Tests for FlextCliMain command registration system with real Click functionality
testing and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import click
import pytest
from click.testing import CliRunner
from flext_core import FlextResult

from flext_cli.main import FlextCliMain


class TestFlextCliMain:
    """Comprehensive tests for FlextCliMain command registration system."""

    @pytest.fixture
    def cli_main(self) -> FlextCliMain:
        """Create FlextCliMain instance for testing."""
        return FlextCliMain(name="testcli", version="1.0.0", description="Test CLI")

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create CliRunner for testing."""
        return CliRunner()

    # =========================================================================
    # INITIALIZATION TESTS
    # =========================================================================

    def test_main_initialization(self, cli_main: FlextCliMain) -> None:
        """Test CLI main initialization."""
        assert isinstance(cli_main, FlextCliMain)
        assert hasattr(cli_main, "_name")
        assert hasattr(cli_main, "_version")
        assert hasattr(cli_main, "_description")
        assert hasattr(cli_main, "_commands")
        assert hasattr(cli_main, "_groups")
        assert hasattr(cli_main, "_plugin_commands")

    def test_main_initialization_with_defaults(self) -> None:
        """Test initialization with default values."""
        main = FlextCliMain()

        assert isinstance(main, FlextCliMain)
        # Should have default values
        assert main._name == "flext"
        assert main._version == "0.9.0"

    def test_main_initialization_with_custom_values(self) -> None:
        """Test initialization with custom values."""
        main = FlextCliMain(name="mycli", version="2.0.0", description="My awesome CLI")

        assert main._name == "mycli"
        assert main._version == "2.0.0"
        assert main._description == "My awesome CLI"

    def test_main_execute(self, cli_main: FlextCliMain) -> None:
        """Test execute method."""
        result = cli_main.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is None

    # =========================================================================
    # COMMAND REGISTRATION TESTS (DECORATOR API)
    # =========================================================================

    def test_command_decorator_simple(
        self, cli_main: FlextCliMain, runner: CliRunner
    ) -> None:
        """Test registering command with decorator."""

        @cli_main.command()
        def hello() -> None:
            click.echo("Hello, world!")

        # Verify command is registered
        result = cli_main.list_commands()
        assert result.is_success
        assert "hello" in result.unwrap()

        # Test command execution
        main_group = cli_main.get_main_group()
        assert main_group.is_success

        result_cmd = runner.invoke(main_group.unwrap(), ["hello"])
        assert result_cmd.exit_code == 0
        assert "Hello, world!" in result_cmd.output

    def test_command_decorator_with_name(
        self, cli_main: FlextCliMain, runner: CliRunner
    ) -> None:
        """Test registering command with custom name."""

        @cli_main.command(name="greet")
        def greeting_func() -> None:
            click.echo("Greetings!")

        # Should be registered with custom name
        result = cli_main.list_commands()
        assert result.is_success
        assert "greet" in result.unwrap()

        # Test execution
        main_group = cli_main.get_main_group()
        result_cmd = runner.invoke(main_group.unwrap(), ["greet"])
        assert result_cmd.exit_code == 0
        assert "Greetings!" in result_cmd.output

    def test_command_decorator_with_options(
        self, cli_main: FlextCliMain, runner: CliRunner
    ) -> None:
        """Test command with Click options."""

        @cli_main.command()
        @click.option("--name", "-n", default="World", help="Name to greet")
        def hello(name: str) -> None:
            click.echo(f"Hello, {name}!")

        # Test with default
        main_group = cli_main.get_main_group()
        result = runner.invoke(main_group.unwrap(), ["hello"])
        assert result.exit_code == 0
        assert "Hello, World!" in result.output

        # Test with custom name
        result = runner.invoke(main_group.unwrap(), ["hello", "--name", "Alice"])
        assert result.exit_code == 0
        assert "Hello, Alice!" in result.output

    def test_multiple_commands(self, cli_main: FlextCliMain, runner: CliRunner) -> None:
        """Test registering multiple commands."""

        @cli_main.command()
        def cmd1() -> None:
            click.echo("Command 1")

        @cli_main.command()
        def cmd2() -> None:
            click.echo("Command 2")

        @cli_main.command()
        def cmd3() -> None:
            click.echo("Command 3")

        # All should be registered
        result = cli_main.list_commands()
        assert result.is_success
        commands = result.unwrap()
        assert len(commands) == 3
        assert "cmd1" in commands
        assert "cmd2" in commands
        assert "cmd3" in commands

    # =========================================================================
    # COMMAND REGISTRATION TESTS (PROGRAMMATIC API)
    # =========================================================================

    def test_register_command_programmatic(
        self, cli_main: FlextCliMain, runner: CliRunner
    ) -> None:
        """Test registering command programmatically."""

        def my_command() -> None:
            click.echo("Programmatic command")

        result = cli_main.register_command(my_command, name="mycmd")

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify registration
        list_result = cli_main.list_commands()
        assert "mycmd" in list_result.unwrap()

        # Test execution
        main_group = cli_main.get_main_group()
        result_cmd = runner.invoke(main_group.unwrap(), ["mycmd"])
        assert result_cmd.exit_code == 0
        assert "Programmatic command" in result_cmd.output

    def test_register_command_without_name(self, cli_main: FlextCliMain) -> None:
        """Test registering command without explicit name."""

        def auto_named_command() -> None:
            click.echo("Auto-named")

        result = cli_main.register_command(auto_named_command)

        assert result.is_success

        # Should use function name (with hyphens)
        list_result = cli_main.list_commands()
        assert (
            "auto-named-command" in list_result.unwrap()
            or "auto_named_command" in list_result.unwrap()
        )

    # =========================================================================
    # GROUP REGISTRATION TESTS (DECORATOR API)
    # =========================================================================

    def test_group_decorator_simple(
        self, cli_main: FlextCliMain, runner: CliRunner
    ) -> None:
        """Test registering group with decorator."""

        @cli_main.group()
        def database() -> None:
            """Database commands."""

        @database.command()
        def init() -> None:
            click.echo("Initializing database...")

        # Verify group is registered
        result = cli_main.list_groups()
        assert result.is_success
        assert "database" in result.unwrap()

        # Test group command execution
        main_group = cli_main.get_main_group()
        result_cmd = runner.invoke(main_group.unwrap(), ["database", "init"])
        assert result_cmd.exit_code == 0
        assert "Initializing database..." in result_cmd.output

    def test_group_decorator_with_name(
        self, cli_main: FlextCliMain, runner: CliRunner
    ) -> None:
        """Test registering group with custom name."""

        @cli_main.group(name="db")
        def database_funcs() -> None:
            """DB commands."""

        # Should be registered with custom name
        result = cli_main.list_groups()
        assert result.is_success
        assert "db" in result.unwrap()

    def test_multiple_groups(self, cli_main: FlextCliMain) -> None:
        """Test registering multiple groups."""

        @cli_main.group()
        def config() -> None:
            """Config commands."""

        @cli_main.group()
        def database() -> None:
            """DB commands."""

        @cli_main.group()
        def users() -> None:
            """User commands."""

        # All should be registered
        result = cli_main.list_groups()
        assert result.is_success
        groups = result.unwrap()
        assert len(groups) == 3
        assert "config" in groups
        assert "database" in groups
        assert "users" in groups

    def test_group_with_multiple_subcommands(
        self, cli_main: FlextCliMain, runner: CliRunner
    ) -> None:
        """Test group with multiple subcommands."""

        @cli_main.group()
        def config() -> None:
            """Configuration commands."""

        @config.command()
        def show() -> None:
            click.echo("Showing config...")

        @config.command()
        def edit() -> None:
            click.echo("Editing config...")

        @config.command()
        def reset() -> None:
            click.echo("Resetting config...")

        # Test all subcommands
        main_group = cli_main.get_main_group()

        result = runner.invoke(main_group.unwrap(), ["config", "show"])
        assert result.exit_code == 0
        assert "Showing config..." in result.output

        result = runner.invoke(main_group.unwrap(), ["config", "edit"])
        assert result.exit_code == 0
        assert "Editing config..." in result.output

        result = runner.invoke(main_group.unwrap(), ["config", "reset"])
        assert result.exit_code == 0
        assert "Resetting config..." in result.output

    # =========================================================================
    # GROUP REGISTRATION TESTS (PROGRAMMATIC API)
    # =========================================================================

    def test_register_group_programmatic(self, cli_main: FlextCliMain) -> None:
        """Test registering group programmatically."""

        def my_group() -> None:
            """My commands."""

        result = cli_main.register_group(my_group, name="mygroup")

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Verify registration
        list_result = cli_main.list_groups()
        assert "mygroup" in list_result.unwrap()

    # =========================================================================
    # PLUGIN COMMAND TESTS
    # =========================================================================

    def test_register_plugin_command(
        self, cli_main: FlextCliMain, runner: CliRunner
    ) -> None:
        """Test registering plugin command."""

        @click.command()
        def plugin_cmd() -> None:
            click.echo("Plugin command")

        result = cli_main.register_plugin_command("plugin", plugin_cmd)

        assert isinstance(result, FlextResult)
        assert result.is_success

        # Test execution
        main_group = cli_main.get_main_group()
        result_cmd = runner.invoke(main_group.unwrap(), ["plugin"])
        assert result_cmd.exit_code == 0
        assert "Plugin command" in result_cmd.output

    def test_register_plugin_command_duplicate(self, cli_main: FlextCliMain) -> None:
        """Test registering duplicate plugin command."""

        @click.command()
        def cmd1() -> None:
            pass

        # First registration should succeed
        result1 = cli_main.register_plugin_command("duplicate", cmd1)
        assert result1.is_success

        # Second registration with same name should fail
        @click.command()
        def cmd2() -> None:
            pass

        result2 = cli_main.register_plugin_command("duplicate", cmd2)
        assert result2.is_failure
        assert "already registered" in result2.error

    def test_load_plugin_commands_invalid_package(self, cli_main: FlextCliMain) -> None:
        """Test loading plugins from non-existent package."""
        result = cli_main.load_plugin_commands("nonexistent.package")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None and "Failed to import" in result.error

    # =========================================================================
    # COMMAND METADATA TESTS
    # =========================================================================

    def test_list_commands_empty(self, cli_main: FlextCliMain) -> None:
        """Test listing commands when none registered."""
        result = cli_main.list_commands()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == []

    def test_list_commands_with_commands(self, cli_main: FlextCliMain) -> None:
        """Test listing commands after registration."""

        @cli_main.command()
        def cmd1() -> None:
            pass

        @cli_main.command()
        def cmd2() -> None:
            pass

        result = cli_main.list_commands()

        assert result.is_success
        commands = result.unwrap()
        assert len(commands) == 2
        assert "cmd1" in commands
        assert "cmd2" in commands

    def test_list_groups_empty(self, cli_main: FlextCliMain) -> None:
        """Test listing groups when none registered."""
        result = cli_main.list_groups()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == []

    def test_list_groups_with_groups(self, cli_main: FlextCliMain) -> None:
        """Test listing groups after registration."""

        @cli_main.group()
        def group1() -> None:
            pass

        @cli_main.group()
        def group2() -> None:
            pass

        result = cli_main.list_groups()

        assert result.is_success
        groups = result.unwrap()
        assert len(groups) == 2
        assert "group1" in groups
        assert "group2" in groups

    def test_get_command_success(self, cli_main: FlextCliMain) -> None:
        """Test getting registered command."""

        @cli_main.command()
        def mycommand() -> None:
            pass

        result = cli_main.get_command("mycommand")

        assert isinstance(result, FlextResult)
        assert result.is_success
        command = result.unwrap()
        assert hasattr(command, "name")

    def test_get_command_not_found(self, cli_main: FlextCliMain) -> None:
        """Test getting non-existent command."""
        result = cli_main.get_command("nonexistent")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None and "not found" in result.error

    def test_get_group_success(self, cli_main: FlextCliMain) -> None:
        """Test getting registered group."""

        @cli_main.group()
        def mygroup() -> None:
            pass

        result = cli_main.get_group("mygroup")

        assert isinstance(result, FlextResult)
        assert result.is_success
        group = result.unwrap()
        assert hasattr(group, "name")

    def test_get_group_not_found(self, cli_main: FlextCliMain) -> None:
        """Test getting non-existent group."""
        result = cli_main.get_group("nonexistent")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert result.error is not None and "not found" in result.error

    # =========================================================================
    # CLI EXECUTION TESTS
    # =========================================================================

    def test_get_main_group_success(self, cli_main: FlextCliMain) -> None:
        """Test getting main CLI group."""
        result = cli_main.get_main_group()

        assert isinstance(result, FlextResult)
        assert result.is_success
        group = result.unwrap()
        assert isinstance(group, click.Group)

    def test_execute_cli_with_help(self, cli_main: FlextCliMain) -> None:
        """Test executing CLI with --help."""
        result = cli_main.execute_cli(["--help"], standalone_mode=False)

        # Help should work even without commands
        assert isinstance(result, FlextResult)

    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================

    def test_complete_cli_workflow(
        self, cli_main: FlextCliMain, runner: CliRunner
    ) -> None:
        """Test complete CLI workflow with commands and groups."""

        # Step 1: Register commands
        @cli_main.command()
        def version() -> None:
            click.echo("v1.0.0")

        @cli_main.command()
        def info() -> None:
            click.echo("Test CLI")

        # Step 2: Register group with subcommands
        @cli_main.group()
        def config() -> None:
            """Configuration commands."""

        @config.command()
        def show() -> None:
            click.echo("Config: enabled")

        @config.command()
        def reset() -> None:
            click.echo("Config reset")

        # Step 3: Verify registrations
        cmd_result = cli_main.list_commands()
        assert cmd_result.is_success
        assert len(cmd_result.unwrap()) == 2

        grp_result = cli_main.list_groups()
        assert grp_result.is_success
        assert len(grp_result.unwrap()) == 1

        # Step 4: Test command execution
        main_group = cli_main.get_main_group()
        assert main_group.is_success

        result = runner.invoke(main_group.unwrap(), ["version"])
        assert result.exit_code == 0
        assert "v1.0.0" in result.output

        result = runner.invoke(main_group.unwrap(), ["info"])
        assert result.exit_code == 0
        assert "Test CLI" in result.output

        result = runner.invoke(main_group.unwrap(), ["config", "show"])
        assert result.exit_code == 0
        assert "Config: enabled" in result.output

    def test_mixed_decorator_and_programmatic(
        self, cli_main: FlextCliMain, runner: CliRunner
    ) -> None:
        """Test mixing decorator and programmatic registration."""

        # Decorator style
        @cli_main.command()
        def decorated_cmd() -> None:
            click.echo("Decorated")

        # Programmatic style
        def programmatic_cmd() -> None:
            click.echo("Programmatic")

        result = cli_main.register_command(programmatic_cmd, name="prog")
        assert result.is_success

        # Both should work
        main_group = cli_main.get_main_group()

        # Click shows "decorated" (not "decorated-cmd") in command list
        result1 = runner.invoke(main_group.unwrap(), ["decorated"])
        assert result1.exit_code == 0
        assert "Decorated" in result1.output

        result2 = runner.invoke(main_group.unwrap(), ["prog"])
        assert result2.exit_code == 0
        assert "Programmatic" in result2.output

    # =========================================================================
    # EDGE CASES AND ERROR HANDLING
    # =========================================================================

    def test_command_with_complex_options(
        self, cli_main: FlextCliMain, runner: CliRunner
    ) -> None:
        """Test command with multiple complex options."""

        @cli_main.command()
        @click.option("--verbose", "-v", is_flag=True, help="Verbose output")
        @click.option("--count", "-c", default=1, type=int, help="Count")
        @click.option(
            "--format", "-f", type=click.Choice(["json", "yaml"]), default="json"
        )
        @click.argument("filename")
        def process(verbose: bool, count: int, format_type: str, filename: str) -> None:
            if verbose:
                click.echo(f"Processing {filename} {count} times as {format_type}")
            else:
                click.echo(f"Processing {filename}")

        main_group = cli_main.get_main_group()

        # Test with all options
        result = runner.invoke(
            main_group.unwrap(),
            ["process", "--verbose", "--count", "3", "--format", "yaml", "data.txt"],
        )
        assert result.exit_code == 0
        assert "Processing data.txt 3 times as yaml" in result.output

    def test_nested_groups(self, cli_main: FlextCliMain, runner: CliRunner) -> None:
        """Test nested command groups."""

        @cli_main.group()
        def admin() -> None:
            """Admin commands."""

        @admin.group()
        def users() -> None:
            """User management."""

        @users.command()
        def list_users() -> None:
            click.echo("Listing users...")

        main_group = cli_main.get_main_group()

        # Test nested execution
        result = runner.invoke(main_group.unwrap(), ["admin", "users", "list-users"])
        assert result.exit_code == 0
        assert "Listing users..." in result.output

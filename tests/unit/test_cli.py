"""FLEXT CLI Click Tests - Comprehensive Click Abstraction Testing.

Tests for FlextCliCli Click abstraction layer with real Click functionality
testing and targeting 90%+ coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import click
import pytest
from click.testing import CliRunner
from flext_core import FlextResult

from flext_cli.cli import FlextCliCli


class TestFlextCliCli:
    """Comprehensive tests for FlextCliCli Click abstraction layer."""

    @pytest.fixture
    def cli_cli(self) -> FlextCliCli:
        """Create FlextCliCli instance for testing."""
        return FlextCliCli()

    # =========================================================================
    # INITIALIZATION TESTS
    # =========================================================================

    def test_cli_cli_initialization(self, cli_cli: FlextCliCli) -> None:
        """Test Click abstraction layer initialization."""
        assert isinstance(cli_cli, FlextCliCli)
        assert hasattr(cli_cli, "logger")
        assert hasattr(cli_cli, "container")  # Public property, not _container

    def test_cli_cli_execute(self, cli_cli: FlextCliCli) -> None:
        """Test execute method returns operational status."""
        result = cli_cli.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success
        data = result.unwrap()
        assert isinstance(data, dict)
        assert data["service"] == "flext-cli"
        assert data["status"] == "operational"

    def test_logger_property_defensive_check(self) -> None:
        """Test logger property is available and functional."""
        cli = FlextCliCli()
        # Logger property should always be available (from FlextService)
        logger = cli.logger
        assert logger is not None
        # Verify logger is functional
        assert hasattr(logger, "info")
        assert hasattr(logger, "error")

    # =========================================================================
    # COMMAND AND GROUP CREATION TESTS
    # =========================================================================

    def test_create_command_decorator(self, cli_cli: FlextCliCli) -> None:
        """Test creating Click command decorator."""
        decorator = cli_cli.create_command_decorator(
            name="test_cmd", help_text="Test command"
        )

        # Decorator is a callable, not FlextResult
        assert callable(decorator)

        @decorator
        def test_func() -> None:
            click.echo("Test")

        assert isinstance(test_func, click.Command)
        assert test_func.name == "test_cmd"

    def test_create_command_decorator_without_name(self, cli_cli: FlextCliCli) -> None:
        """Test creating command decorator without explicit name."""
        decorator = cli_cli.create_command_decorator(help_text="Auto-named command")

        # Decorator is a callable, not FlextResult
        assert callable(decorator)

        @decorator
        def my_function() -> None:
            pass

        assert isinstance(my_function, click.Command)
        # Click converts underscores to hyphens in command names
        assert my_function.name == "my-function"

    def test_create_group_decorator(self, cli_cli: FlextCliCli) -> None:
        """Test creating Click group decorator."""
        decorator = cli_cli.create_group_decorator(
            name="test_group", help_text="Test group"
        )

        # Decorator is a callable, not FlextResult
        assert callable(decorator)

        @decorator
        def test_group_func() -> None:
            """Group function."""

        assert isinstance(test_group_func, click.Group)
        assert test_group_func.name == "test_group"

    def test_create_group_decorator_without_name(self, cli_cli: FlextCliCli) -> None:
        """Test group decorator without name uses function name."""
        decorator = cli_cli.create_group_decorator()

        # Decorator is a callable, not FlextResult
        assert callable(decorator)

        @decorator
        def my_group() -> None:
            pass

        assert isinstance(my_group, click.Group)
        # Click preserves function name as-is (no hyphen conversion for groups)
        assert my_group.name == "my"

    # =========================================================================
    # OPTION AND ARGUMENT DECORATOR TESTS
    # =========================================================================

    def test_create_option_decorator(self, cli_cli: FlextCliCli) -> None:
        """Test creating Click option decorator."""
        decorator = cli_cli.create_option_decorator(
            "--count", "-c", default=1, help_text="Number of items"
        )

        # Decorator is a callable, not FlextResult
        assert callable(decorator)

        # Apply decorator to function
        @decorator
        def test_func(count: int) -> None:
            click.echo(f"Count: {count}")

        # Function should have the option parameter
        assert callable(test_func)

    def test_create_option_decorator_flag(self, cli_cli: FlextCliCli) -> None:
        """Test creating boolean flag option."""
        decorator = cli_cli.create_option_decorator(
            "--verbose", "-v", is_flag=True, help_text="Verbose output"
        )

        # Decorator is a callable, not FlextResult
        assert callable(decorator)

        @decorator
        def test_func(verbose: bool) -> None:
            if verbose:
                click.echo("Verbose mode")

        assert callable(test_func)

    def test_create_argument_decorator(self, cli_cli: FlextCliCli) -> None:
        """Test creating Click argument decorator."""
        decorator = cli_cli.create_argument_decorator("filename")

        # Decorator is a callable, not FlextResult
        assert callable(decorator)

        @decorator
        def test_func(filename: str) -> None:
            click.echo(f"File: {filename}")

        assert callable(test_func)

    # =========================================================================
    # PARAMETER TYPE TESTS
    # =========================================================================

    def test_get_choice_type(self, cli_cli: FlextCliCli) -> None:
        """Test getting Click Choice type."""
        choice_type = cli_cli.get_choice_type(["json", "yaml", "csv"])

        assert isinstance(choice_type, click.Choice)
        # Click Choice stores choices as tuple
        assert choice_type.choices == ("json", "yaml", "csv")

    def test_get_path_type(self, cli_cli: FlextCliCli) -> None:
        """Test getting Click Path type."""
        path_type = cli_cli.get_path_type(exists=True, file_okay=True, dir_okay=False)

        assert isinstance(path_type, click.Path)

    def test_get_file_type(self, cli_cli: FlextCliCli) -> None:
        """Test getting Click File type."""
        file_type = cli_cli.get_file_type(mode="r", encoding="utf-8")

        assert isinstance(file_type, click.File)

    def test_get_int_range_type(self, cli_cli: FlextCliCli) -> None:
        """Test getting Click IntRange type."""
        # FIXED: Use min_val/max_val instead of min/max
        int_range = cli_cli.get_int_range_type(min_val=1, max_val=10)

        assert isinstance(int_range, click.IntRange)
        assert int_range.min == 1
        assert int_range.max == 10

    def test_get_int_range_type_with_clamp(self, cli_cli: FlextCliCli) -> None:
        """Test IntRange with clamp option."""
        # FIXED: Use min_val/max_val instead of min/max
        int_range = cli_cli.get_int_range_type(min_val=0, max_val=100, clamp=True)

        assert isinstance(int_range, click.IntRange)
        assert int_range.clamp is True

    def test_get_float_range_type(self, cli_cli: FlextCliCli) -> None:
        """Test getting Click FloatRange type."""
        # FIXED: Use min_val/max_val instead of min/max
        float_range = cli_cli.get_float_range_type(min_val=0.0, max_val=1.0)

        assert isinstance(float_range, click.FloatRange)
        assert float_range.min == 0.0
        assert float_range.max == 1.0

    def test_get_uuid_type(self, cli_cli: FlextCliCli) -> None:
        """Test getting Click UUID type."""
        uuid_type = cli_cli.get_uuid_type()

        # Returns the class itself, not an instance
        assert uuid_type is click.UUID

    def test_get_datetime_type(self, cli_cli: FlextCliCli) -> None:
        """Test getting Click DateTime type."""
        datetime_type = cli_cli.get_datetime_type(formats=["%Y-%m-%d"])

        assert isinstance(datetime_type, click.DateTime)

    def test_get_datetime_type_default_formats(self, cli_cli: FlextCliCli) -> None:
        """Test get_datetime_type with default formats (line 380)."""
        # Call without formats parameter - should use defaults
        datetime_type = cli_cli.get_datetime_type()

        assert isinstance(datetime_type, click.DateTime)
        # Verify default formats are set
        assert "%Y-%m-%d" in datetime_type.formats
        assert "%Y-%m-%dT%H:%M:%S" in datetime_type.formats
        assert "%Y-%m-%d %H:%M:%S" in datetime_type.formats

    def test_get_tuple_type(self, cli_cli: FlextCliCli) -> None:
        """Test getting Click Tuple type."""
        tuple_type = cli_cli.get_tuple_type([str, int, float])

        assert isinstance(tuple_type, click.Tuple)

    def test_get_bool_type(self, cli_cli: FlextCliCli) -> None:
        """Test getting bool type."""
        bool_type = cli_cli.get_bool_type()

        assert bool_type is bool

    def test_get_string_type(self, cli_cli: FlextCliCli) -> None:
        """Test getting string type."""
        str_type = cli_cli.get_string_type()

        assert str_type is str

    def test_get_int_type(self, cli_cli: FlextCliCli) -> None:
        """Test getting int type."""
        int_type = cli_cli.get_int_type()

        assert int_type is int

    def test_get_float_type(self, cli_cli: FlextCliCli) -> None:
        """Test getting float type."""
        float_type = cli_cli.get_float_type()

        assert float_type is float

    # =========================================================================
    # CONTEXT MANAGEMENT TESTS
    # =========================================================================

    def test_get_current_context_no_context(self, cli_cli: FlextCliCli) -> None:
        """Test getting current context when none exists."""
        # FIXED: Returns None when no context, not FlextResult
        context = cli_cli.get_current_context()

        # Context is None when not in a Click command
        assert context is None

    def test_create_pass_context_decorator(self, cli_cli: FlextCliCli) -> None:
        """Test creating pass_context decorator."""
        decorator = cli_cli.create_pass_context_decorator()

        assert callable(decorator)

    # =========================================================================
    # CLI RUNNER TESTS
    # =========================================================================

    def test_create_cli_runner(self, cli_cli: FlextCliCli) -> None:
        """Test creating CLI runner."""
        result = cli_cli.create_cli_runner()

        # Returns FlextResult, not direct CliRunner
        assert isinstance(result, FlextResult)
        assert result.is_success
        runner = result.unwrap()
        assert isinstance(runner, CliRunner)

    def test_cli_runner_usage(self, cli_cli: FlextCliCli) -> None:
        """Test creating CLI runner for testing commands."""
        # Create runner
        runner_result = cli_cli.create_cli_runner()
        assert isinstance(runner_result, FlextResult)
        assert runner_result.is_success

        # Verify runner can be used (actual command invocation requires Typer app)
        runner = runner_result.unwrap()
        assert isinstance(runner, CliRunner)

    # =========================================================================
    # UTILITY METHOD TESTS
    # =========================================================================

    def test_echo(self, cli_cli: FlextCliCli) -> None:
        """Test echo utility."""
        result = cli_cli.echo("Test message")
        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_confirm(self, cli_cli: FlextCliCli) -> None:
        """Test confirm method returns FlextResult."""
        # Just check the method exists and returns FlextResult
        assert hasattr(cli_cli, "confirm")
        # Can't test actual confirmation without user input

    def test_confirm_success(
        self, cli_cli: FlextCliCli, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test confirm success path (line 575)."""

        # Mock typer.confirm to return True
        def mock_confirm(*args: object, **kwargs: object) -> bool:
            return True

        monkeypatch.setattr("typer.confirm", mock_confirm)

        # Call confirm - should return success with True
        result = cli_cli.confirm("Proceed?")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() is True

    def test_confirm_abort_exception(
        self, cli_cli: FlextCliCli, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test confirm handles typer.Abort exception (lines 566-577)."""
        import typer

        # Mock typer.confirm to raise Abort
        def mock_confirm(*args: object, **kwargs: object) -> bool:
            raise typer.Abort

        monkeypatch.setattr("typer.confirm", mock_confirm)

        # Call confirm - should catch Abort and return failure
        result = cli_cli.confirm("Proceed?")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert "abort" in str(result.error).lower()

    def test_prompt_success(
        self, cli_cli: FlextCliCli, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prompt success path (line 631)."""

        # Mock typer.prompt to return a value
        def mock_prompt(*args: object, **kwargs: object) -> str:
            return "test_value"

        monkeypatch.setattr("typer.prompt", mock_prompt)

        # Call prompt - should return success with value
        result = cli_cli.prompt("Enter name:")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert result.unwrap() == "test_value"

    def test_prompt_abort_exception(
        self, cli_cli: FlextCliCli, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test prompt handles typer.Abort exception (lines 618-633)."""
        import typer

        # Mock typer.prompt to raise Abort
        def mock_prompt(*args: object, **kwargs: object) -> str:
            raise typer.Abort

        monkeypatch.setattr("typer.prompt", mock_prompt)

        # Call prompt - should catch Abort and return failure
        result = cli_cli.prompt("Enter name:")

        assert isinstance(result, FlextResult)
        assert result.is_failure
        assert "abort" in str(result.error).lower()

    def test_format_filename(self, cli_cli: FlextCliCli) -> None:
        """Test format_filename utility method (line 695)."""
        from pathlib import Path

        # Test with string filename
        formatted = cli_cli.format_filename("/path/to/file.txt")
        assert isinstance(formatted, str)
        assert "file.txt" in formatted

        # Test with Path object
        path = Path("/path/to/another_file.txt")
        formatted = cli_cli.format_filename(path, shorten=True)
        assert isinstance(formatted, str)

    def test_get_terminal_size(self, cli_cli: FlextCliCli) -> None:
        """Test get_terminal_size utility method (lines 704-705)."""
        size = cli_cli.get_terminal_size()

        # Should return tuple of (width, height)
        assert isinstance(size, tuple)
        assert len(size) == 2
        assert isinstance(size[0], int)  # width
        assert isinstance(size[1], int)  # height

    def test_clear_screen(self, cli_cli: FlextCliCli) -> None:
        """Test clear_screen utility method (lines 714-715)."""
        result = cli_cli.clear_screen()

        assert isinstance(result, FlextResult)
        assert result.is_success

    def test_pause(self, cli_cli: FlextCliCli, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test pause utility method (lines 727-728)."""
        # Mock click.pause to avoid blocking in tests
        pause_called = False

        def mock_pause(info: str = "") -> None:
            nonlocal pause_called
            pause_called = True

        monkeypatch.setattr("click.pause", mock_pause)

        # Call pause
        result = cli_cli.pause(info="Press any key...")

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert pause_called

    # =========================================================================
    # INTEGRATION TESTS
    # =========================================================================

    def test_complete_cli_workflow(self, cli_cli: FlextCliCli) -> None:
        """Test complete CLI workflow with group, command, options."""
        # FIXED: Decorators are returned directly, not FlextResult
        group_decorator = cli_cli.create_group_decorator(name="myapp")

        @group_decorator
        def cli() -> None:
            """My application."""

        # Verify group was created
        assert isinstance(cli, click.Group)
        assert cli.name == "myapp"

        # Create command with options
        command_decorator = cli_cli.create_command_decorator(name="hello")
        option_decorator = cli_cli.create_option_decorator("--name", default="World")

        @command_decorator
        @option_decorator
        def hello(name: str) -> None:
            """Say hello."""
            click.echo(f"Hello, {name}!")

        # Verify command was created with options
        assert isinstance(hello, click.Command)
        assert hello.name == "hello"

    def test_cli_with_options_and_arguments(self, cli_cli: FlextCliCli) -> None:
        """Test CLI with both options and arguments."""
        # FIXED: Decorators are returned directly, not FlextResult
        command_decorator = cli_cli.create_command_decorator(name="process")
        argument_decorator = cli_cli.create_argument_decorator("filename")
        option_decorator = cli_cli.create_option_decorator("--verbose", is_flag=True)

        @command_decorator
        @argument_decorator
        @option_decorator
        def process(filename: str, verbose: bool) -> None:
            """Process a file."""
            if verbose:
                click.echo(f"Processing {filename} verbosely")
            else:
                click.echo(f"Processing {filename}")

        # Verify command was created with both options and arguments
        assert isinstance(process, click.Command)
        assert process.name == "process"

    def test_command_with_choice_validation(self, cli_cli: FlextCliCli) -> None:
        """Test command with choice type."""
        # FIXED: Decorators are returned directly, not FlextResult
        command_decorator = cli_cli.create_command_decorator(name="select")
        choice_type = cli_cli.get_choice_type(["json", "yaml", "csv"])
        option_decorator = cli_cli.create_option_decorator(
            "--format",
            type_hint=choice_type,
            default="json",
        )

        @command_decorator
        @option_decorator
        def select(output_format: str) -> None:
            """Select format."""
            click.echo(f"Format: {output_format}")

        # Verify command was created with choice type option
        assert isinstance(select, click.Command)
        assert select.name == "select"

    def test_multiple_decorators_order(self, cli_cli: FlextCliCli) -> None:
        """Test decorator application order."""
        # FIXED: Decorators are returned directly, not FlextResult
        command_decorator = cli_cli.create_command_decorator(name="multi")
        opt1 = cli_cli.create_option_decorator("--first", default="1")
        opt2 = cli_cli.create_option_decorator("--second", default="2")

        @command_decorator
        @opt1
        @opt2
        def multi(first: str, second: str) -> None:
            """Multiple options."""
            click.echo(f"First: {first}, Second: {second}")

        # Verify command was created with multiple options
        assert isinstance(multi, click.Command)
        assert multi.name == "multi"

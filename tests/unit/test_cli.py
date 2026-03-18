"""FLEXT CLI Click Tests - Comprehensive Click Abstraction Validation Testing.

Tests for FlextCliCli covering Click decorators, parameters, context management,
utility methods, model command generation, integration workflows, and edge cases
with 100% coverage.

Modules tested: flext_cli.cli.FlextCliCli
Scope: All Click decorators, parameter types, context management, utility methods

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import click
import pytest
import typer
from click.testing import CliRunner
from flext_core import r
from flext_tests import tm

from flext_cli import FlextCliCli, FlextCliSettings, m

from ..helpers._impl import FlextCliTestHelpers


class TestsCliCli:
    """Comprehensive test suite for flext_cli.FlextCliCli module."""

    def test_cli_initialization(self) -> None:
        """Test CLI class initialization."""
        cli_cli = FlextCliCli()
        tm.that(isinstance(cli_cli, FlextCliCli), eq=True)
        tm.that(hasattr(cli_cli, "logger"), eq=True)
        tm.that(hasattr(cli_cli, "container"), eq=True)

    def test_cli_execute_method(self) -> None:
        """Test CLI execute method returns valid result."""
        cli_cli = FlextCliCli()
        execute_result = cli_cli.execute()
        tm.ok(execute_result)
        data = execute_result.value
        tm.that(isinstance(data, dict), eq=True)
        tm.that(data.get("service"), eq="flext-cli")
        tm.that(data.get("status"), eq="operational")

    def test_command_decorator_creation(self) -> None:
        """Test command decorator creation."""
        cli_cli = FlextCliCli()
        command_result = FlextCliTestHelpers.CliHelpers.create_test_command(
            cli_cli, "test_cmd"
        )
        tm.ok(command_result)
        if command_result.is_success and command_result.value:
            tm.that(isinstance(command_result.value, click.Command), eq=True)
            tm.that(command_result.value.name, eq="test_cmd")

    def test_group_decorator_creation(self) -> None:
        """Test group decorator creation."""
        cli_cli = FlextCliCli()
        group_result = FlextCliTestHelpers.CliHelpers.create_test_group(
            cli_cli, "test_group"
        )
        tm.ok(group_result)
        if group_result.is_success and group_result.value:
            tm.that(isinstance(group_result.value, click.Group), eq=True)
            tm.that(group_result.value.name, eq="test_group")

    def test_option_decorator(self) -> None:
        """Test option decorator creation."""
        cli_cli = FlextCliCli()
        option_config_instance = m.Cli.OptionConfig.model_construct(default=1)
        option_config = option_config_instance
        option_decorator = cli_cli.create_option_decorator(
            "--count", "-c", config=option_config
        )
        tm.that(callable(option_decorator), eq=True)

    def test_argument_decorator(self) -> None:
        """Test argument decorator creation."""
        cli_cli = FlextCliCli()
        argument_decorator = cli_cli.create_argument_decorator("filename")
        tm.that(callable(argument_decorator), eq=True)

    def test_command_with_options(self) -> None:
        """Test command creation with options."""
        cli_cli = FlextCliCli()
        command_result = FlextCliTestHelpers.CliHelpers.create_command_with_options(
            cli_cli, "test_cmd", "--value", "default"
        )
        tm.ok(command_result)

    @pytest.mark.parametrize(
        ("click_type_name", "data_dict"),
        [
            ("choice", {"choices": ["option1", "option2", "option3"]}),
            ("path", {"exists": True, "file_okay": True, "dir_okay": False}),
            ("file", {"exists": True, "file_okay": True, "dir_okay": False}),
            ("intrange", {"min": 0, "max": 100}),
            ("floatrange", {"min": 0.0, "max": 100.0}),
        ],
    )
    def test_click_type_creation(
        self, click_type_name: str, data_dict: dict[str, object]
    ) -> None:
        """Test Click type creation with various parameter types."""
        if click_type_name == "choice":
            choices = data_dict.get("choices")
            tm.that(isinstance(choices, list), eq=True)
            if isinstance(choices, list):
                choice_type = click.Choice(choices)
                tm.that(isinstance(choice_type, click.Choice), eq=True)
                choices_tuple: tuple[str, ...] = choice_type.choices
                tm.that(choices_tuple, eq=tuple(choices))
        elif click_type_name == "path":
            path_type = click.Path(
                exists=bool(data_dict.get("exists")),
                file_okay=bool(data_dict.get("file_okay")),
                dir_okay=bool(data_dict.get("dir_okay")),
            )
            tm.that(isinstance(path_type, click.Path), eq=True)
        elif click_type_name in {"intrange", "floatrange"}:
            tm.that("min" in data_dict, eq=True)
            tm.that("max" in data_dict, eq=True)

    @pytest.mark.parametrize(
        ("primitive_type", "getter_method"),
        {
            "str": "get_string_type",
            "int": "get_int_type",
            "float": "get_float_type",
            "bool": "get_bool_type",
        }.items(),
    )
    def test_primitive_type_getters(
        self, primitive_type: str, getter_method: str
    ) -> None:
        """Test primitive type getter methods."""
        cli_cli = FlextCliCli()
        method = getattr(cli_cli, getter_method)
        result = method()
        expected_type = {"str": str, "int": int, "float": float, "bool": bool}[
            primitive_type
        ]
        tm.that(result is expected_type, eq=True)

    def test_datetime_type(self) -> None:
        """Test DateTime type creation."""
        cli_cli = FlextCliCli()
        datetime_type = cli_cli.get_datetime_type()
        tm.that(isinstance(datetime_type, click.DateTime), eq=True)
        for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
            tm.that(fmt in datetime_type.formats, eq=True)

    def test_cli_runner_invocation(self) -> None:
        """Test CLI runner for command invocation."""
        runner = CliRunner()
        tm.that(isinstance(runner, CliRunner), eq=True)

        @click.command()
        def simple_command() -> None:
            click.echo("hello")

        result = runner.invoke(simple_command, [])
        tm.that(result.exit_code, eq=0)
        tm.that("hello" in result.output, eq=True)

    @pytest.mark.parametrize(
        ("test_type", "description", "should_succeed"),
        [
            ("init", "Initialization test", True),
            ("command", "Command decorator test", True),
            ("group", "Group decorator test", True),
        ],
    )
    def test_cli_comprehensive_scenarios(
        self, test_type: str, description: str, should_succeed: bool
    ) -> None:
        """Comprehensive CLI scenario tests using parametrization."""
        result = self._execute_cli_test(test_type)
        tm.that(should_succeed is True, eq=True)
        tm.ok(result)

    def _execute_cli_test(self, test_type: str) -> r[bool]:
        """Execute specific CLI test by type."""
        try:
            success = False
            match test_type:
                case "init":
                    self.test_cli_initialization()
                    success = True
                case "command":
                    self.test_command_decorator_creation()
                    success = True
                case "group":
                    self.test_group_decorator_creation()
                    success = True
                case "option":
                    self.test_option_decorator()
                    self.test_argument_decorator()
                    success = True
                case "parameter":
                    self.test_datetime_type()
                    success = True
                case "context":
                    cli_cli = FlextCliCli()
                    tm.that(isinstance(cli_cli, FlextCliCli), eq=True)
                    success = True
                case "runner":
                    self.test_cli_runner_invocation()
                    success = True
                case "utility":
                    cli_cli = FlextCliCli()
                    tm.that(hasattr(cli_cli, "logger"), eq=True)
                    success = True
                case "model":
                    cli_cli = FlextCliCli()
                    tm.that(isinstance(cli_cli, FlextCliCli), eq=True)
                    success = True
                case "integration":
                    cli_cli = FlextCliCli()
                    result = cli_cli.execute()
                    tm.ok(result)
                    success = True
                case _:
                    return r[bool].fail(f"Unknown test type: {test_type}")
            return r[bool].ok(success)
        except Exception as e:
            return r[bool].fail(str(e))

    class TestCoverageExtended:
        """Extended tests for 100% coverage."""

        def test_create_app_with_common_params(self) -> None:
            """Test create_app_with_common_params creation only."""
            cli = FlextCliCli()
            app = cli.create_app_with_common_params("test_app", "help")
            tm.that(isinstance(app, typer.Typer), eq=True)

        def test_echo(self) -> None:
            """Test echo."""
            cli = FlextCliCli()
            result = cli.echo("message")
            tm.ok(result)

        def test_utilities(self) -> None:
            """Test utility methods."""
            cli = FlextCliCli()
            tm.that(isinstance(cli.format_filename("test.txt"), str), eq=True)
            tm.that(isinstance(cli.get_terminal_size(), tuple), eq=True)

        def test_model_command_validation(self) -> None:
            """Test model_command input validation."""
            cli = FlextCliCli()
            invalid_model: type = dict

            def handler(_model: object) -> str:
                return "invalid"

            with pytest.raises(Exception):
                cli.model_command(invalid_model, handler)

        def test_create_cli_runner(self) -> None:
            """Test create_cli_runner."""
            cli = FlextCliCli()
            result = cli.create_cli_runner()
            tm.ok(result)
            tm.that(isinstance(result.value, CliRunner), eq=True)

        def test_get_current_context(self) -> None:
            """Test get_current_context."""
            cli = FlextCliCli()
            ctx = cli.get_current_context()
            tm.that(ctx is None, eq=True)

        def test_create_pass_context_decorator(self) -> None:
            """Test create_pass_context_decorator."""
            cli = FlextCliCli()
            decorator = cli.create_pass_context_decorator()
            tm.that(callable(decorator), eq=True)

    def test_get_terminal_size(self) -> None:
        """Test get_terminal_size method."""
        cli = FlextCliCli()
        width, height = cli.get_terminal_size()
        tm.that(isinstance(width, int), eq=True)
        tm.that(isinstance(height, int), eq=True)
        tm.that(width > 0, eq=True)
        tm.that(height > 0, eq=True)

    def test_clear_screen(self) -> None:
        """Test clear_screen method."""
        cli = FlextCliCli()
        result = cli.clear_screen()
        tm.ok(result)
        tm.that(result.value is True, eq=True)

    def test_get_current_context_none(self) -> None:
        """Test get_current_context when not in command."""
        cli = FlextCliCli()
        ctx = cli.get_current_context()
        tm.that(ctx is None, eq=True)

    def test_get_bool_type(self) -> None:
        """Test get_bool_type method."""
        cli = FlextCliCli()
        bool_type = cli.get_bool_type()
        tm.that(bool_type is bool, eq=True)

    def test_get_string_type(self) -> None:
        """Test get_string_type method."""
        cli = FlextCliCli()
        string_type = cli.get_string_type()
        tm.that(string_type is str, eq=True)

    def test_get_int_type(self) -> None:
        """Test get_int_type method."""
        cli = FlextCliCli()
        int_type = cli.get_int_type()
        tm.that(int_type is int, eq=True)

    def test_get_float_type(self) -> None:
        """Test get_float_type method."""
        cli = FlextCliCli()
        float_type = cli.get_float_type()
        tm.that(float_type is float, eq=True)

    def test_get_uuid_type(self) -> None:
        """Test get_uuid_type method."""
        cli = FlextCliCli()
        uuid_type = cli.get_uuid_type()
        tm.that(hasattr(uuid_type, "name"), eq=True)

    def test_get_datetime_type(self) -> None:
        """Test get_datetime_type method."""
        cli = FlextCliCli()
        datetime_type = cli.get_datetime_type()
        tm.that(hasattr(datetime_type, "name"), eq=True)

    def test_get_tuple_type(self) -> None:
        """Test get_tuple_type method."""
        cli = FlextCliCli()
        tuple_type = cli.get_tuple_type([str, int])
        tm.that(hasattr(tuple_type, "name"), eq=True)

    def test_format_filename(self) -> None:
        """Test format_filename method."""
        cli = FlextCliCli()
        result = cli.format_filename("test.py")
        tm.that(isinstance(result, str), eq=True)
        tm.that("test.py" in result, eq=True)

    def test_pause(self) -> None:
        """Test pause method."""
        cli = FlextCliCli()
        result = cli.pause()
        tm.ok(result)
        result = cli.pause("Press Enter to continue...")
        tm.ok(result)

    def test_echo(self) -> None:
        """Test echo method."""
        cli = FlextCliCli()
        result = cli.echo("test message")
        tm.ok(result)
        result = cli.echo("colored message", color=True)
        tm.ok(result)

    def test_execute_method(self) -> None:
        """Test execute method returns valid result."""
        cli = FlextCliCli()
        result = cli.execute()
        tm.ok(result)
        data = result.value
        tm.that(isinstance(data, dict), eq=True)

    def test_create_pass_context_decorator(self) -> None:
        """Test create_pass_context_decorator method."""
        cli = FlextCliCli()
        decorator = cli.create_pass_context_decorator()
        tm.that(callable(decorator), eq=True)

    def test_create_cli_runner(self) -> None:
        """Test create_cli_runner method."""
        cli = FlextCliCli()
        result = cli.create_cli_runner()
        tm.ok(result)
        runner = result.value
        tm.that(hasattr(runner, "invoke"), eq=True)

    def test_format_filename_method(self) -> None:
        """Test format_filename method."""
        cli = FlextCliCli()
        result = cli.format_filename("test.py")
        tm.that(isinstance(result, str), eq=True)
        tm.that("test.py" in result, eq=True)

    def test_create_command_decorator(self) -> None:
        """Test create_command_decorator method."""
        cli = FlextCliCli()
        decorator = cli.create_command_decorator("test_cmd")
        tm.that(callable(decorator), eq=True)

    def test_create_option_decorator(self) -> None:
        """Test create_option_decorator method."""
        cli = FlextCliCli()
        decorator = cli.create_option_decorator("--test-option")
        tm.that(callable(decorator), eq=True)

    def test_create_argument_decorator(self) -> None:
        """Test create_argument_decorator method."""
        cli = FlextCliCli()
        decorator = cli.create_argument_decorator("test_arg")
        tm.that(callable(decorator), eq=True)

    def test_build_bool_value(self) -> None:
        """Test _build_bool_value method."""
        cli = FlextCliCli()
        bool_value = cli._build_bool_value({"test": True}, "test", default=False)
        tm.that(isinstance(bool_value, bool), eq=True)
        tm.that(bool_value is True, eq=True)

    def test_build_str_value(self) -> None:
        """Test _build_str_value method."""
        cli = FlextCliCli()
        str_value = cli._build_str_value({"test": "value"}, "test", default="default")
        tm.that(isinstance(str_value, str), eq=True)
        tm.that(str_value, eq="value")

    def test_get_console_enabled(self) -> None:
        """Test _get_console_enabled method."""
        cli = FlextCliCli()
        config = FlextCliSettings()
        config.no_color = False
        console_enabled = cli._get_console_enabled(config)
        tm.that(isinstance(console_enabled, bool), eq=True)

    def test_apply_common_params_to_config(self) -> None:
        """Test _apply_common_params_to_config method."""
        cli = FlextCliCli()
        config = FlextCliSettings()
        cli._apply_common_params_to_config(config, verbose=True, debug=True)
        tm.that(config.verbose is True, eq=True)
        tm.that(config.debug is True, eq=True)

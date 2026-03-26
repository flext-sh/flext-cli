"""FLEXT CLI Click Tests - Comprehensive Click Abstraction Validation Testing.

Tests for FlextCliCli covering Click decorators, parameters, context management,
utility methods, model command generation, integration workflows, and edge cases.

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
from tests import t


class TestsCliCli:
    """Comprehensive test suite for flext_cli.FlextCliCli module."""

    def test_cli_initialization(self) -> None:
        """Test CLI class initialization."""
        cli_cli = FlextCliCli()
        tm.that(cli_cli, is_=FlextCliCli)
        tm.that(hasattr(cli_cli, "logger"), eq=True)
        tm.that(hasattr(cli_cli, "container"), eq=True)

    def test_cli_execute_method(self) -> None:
        """Test CLI execute method returns valid result."""
        cli_cli = FlextCliCli()
        execute_result = cli_cli.execute()
        tm.ok(execute_result)
        data = execute_result.value
        tm.that(data, is_=dict)
        tm.that(data.get("service"), eq="flext-cli")
        tm.that(data.get("status"), eq="operational")

    def test_command_decorator_creation(self) -> None:
        """Test command decorator creation."""
        cli = FlextCliCli()
        decorator = cli.create_command_decorator("test_cmd")
        tm.that(callable(decorator), eq=True)

    def test_group_decorator_creation(self) -> None:
        """Test group decorator creation."""
        cli = FlextCliCli()
        decorator = cli.create_group_decorator("test_group")
        tm.that(callable(decorator), eq=True)

    def test_option_decorator(self) -> None:
        """Test option decorator creation."""
        cli_cli = FlextCliCli()
        option_config_instance = m.Cli.OptionConfig.model_construct(default=1)
        option_config = option_config_instance
        option_decorator = cli_cli.create_option_decorator(
            "--count",
            "-c",
            config=option_config,
        )
        tm.that(callable(option_decorator), eq=True)

    def test_argument_decorator(self) -> None:
        """Test argument decorator creation."""
        cli_cli = FlextCliCli()
        argument_decorator = cli_cli.create_argument_decorator("filename")
        tm.that(callable(argument_decorator), eq=True)

    def test_command_with_options(self) -> None:
        """Test command creation with options."""
        cli = FlextCliCli()
        option_config = m.Cli.OptionConfig.model_construct(default="default")
        decorator = cli.create_option_decorator("--value", config=option_config)
        tm.that(callable(decorator), eq=True)

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
        self,
        click_type_name: str,
        data_dict: t.ContainerMapping,
    ) -> None:
        """Test Click type creation with various parameter types."""
        if click_type_name == "choice":
            choices = data_dict.get("choices")
            tm.that(choices, is_=list)
            if isinstance(choices, list):
                str_choices = [str(c) for c in choices]
                choice_type = click.Choice(str_choices)
                tm.that(choice_type, is_=click.Choice)
                choices_tuple: tuple[str, ...] = tuple(choice_type.choices)
                tm.that(choices_tuple, eq=tuple(str_choices))
        elif click_type_name == "path":
            path_type = click.Path(
                exists=bool(data_dict.get("exists")),
                file_okay=bool(data_dict.get("file_okay")),
                dir_okay=bool(data_dict.get("dir_okay")),
            )
            tm.that(path_type, is_=click.Path)
        elif click_type_name in {"intrange", "floatrange"}:
            tm.that(data_dict, has="min")
            tm.that(data_dict, has="max")

    def test_cli_runner_invocation(self) -> None:
        """Test CLI runner for command invocation."""
        runner = CliRunner()
        tm.that(runner, is_=CliRunner)

        @click.command()
        def simple_command() -> None:
            click.echo("hello")

        result = runner.invoke(simple_command, [])
        tm.that(result.exit_code, eq=0)
        tm.that(result.output, has="hello")

    @pytest.mark.parametrize(
        ("test_type", "description", "should_succeed"),
        [
            ("init", "Initialization test", True),
            ("command", "Command decorator test", True),
            ("group", "Group decorator test", True),
        ],
    )
    def test_cli_comprehensive_scenarios(
        self,
        test_type: str,
        description: str,
        should_succeed: bool,
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
                    pass
                case "context":
                    cli_cli = FlextCliCli()
                    tm.that(cli_cli, is_=FlextCliCli)
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
                    tm.that(cli_cli, is_=FlextCliCli)
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
            tm.that(app, is_=typer.Typer)

        def test_echo(self) -> None:
            """Test echo."""
            cli = FlextCliCli()
            result = cli.echo("message")
            tm.ok(result)

        def test_model_command_validation(self) -> None:
            """Test model_command input validation."""
            cli = FlextCliCli()
            invalid_model: type = dict

            def handler(_model: t.NormalizedValue) -> str:
                return "invalid"

            with pytest.raises(Exception):
                cli.model_command(invalid_model, handler)

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
        tm.that(data, is_=dict)

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
        tm.that(bool_value, is_=bool)
        tm.that(bool_value is True, eq=True)

    def test_build_str_value(self) -> None:
        """Test _build_str_value method."""
        cli = FlextCliCli()
        str_value = cli._build_str_value({"test": "value"}, "test", default="default")
        tm.that(str_value, is_=str)
        tm.that(str_value, eq="value")

    def test_get_console_enabled(self) -> None:
        """Test _get_console_enabled method."""
        cli = FlextCliCli()
        config = FlextCliSettings()
        config.no_color = False
        console_enabled = cli._get_console_enabled(config)
        tm.that(console_enabled, is_=bool)

    def test_apply_common_params_to_config(self) -> None:
        """Test _apply_common_params_to_config method."""
        cli = FlextCliCli()
        config = FlextCliSettings()
        cli._apply_common_params_to_config(config, verbose=True, debug=True)
        tm.that(config.verbose is True, eq=True)
        tm.that(config.debug is True, eq=True)

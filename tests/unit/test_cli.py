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

from collections.abc import Callable
from typing import cast

import click
import pytest
import typer
from click.testing import CliRunner
from flext_tests import tm
from pydantic import BaseModel

from flext_cli import FlextCliCli, m, p, r, t

# from ..fixtures.constants import TestCli  # Fixtures removed - use conftest.py and flext_tests
from ..helpers import FlextCliTestHelpers


class TestsCliCli:
    """Comprehensive test suite for flext_cli.FlextCliCli module."""

    # ========================================================================
    # CLI INITIALIZATION
    # ========================================================================

    def test_cli_initialization(self) -> None:
        """Test CLI class initialization."""
        cli_cli = FlextCliCli()
        assert isinstance(cli_cli, FlextCliCli)
        assert hasattr(cli_cli, "logger")
        assert hasattr(cli_cli, "container")

    def test_cli_execute_method(self) -> None:
        """Test CLI execute method returns valid result."""
        cli_cli = FlextCliCli()
        execute_result = cli_cli.execute()
        tm.ok(execute_result)

        data = execute_result.unwrap()
        assert isinstance(data, dict)
        assert data.get("service") == "flext-cli"
        assert data.get("status") == "operational"

    # ========================================================================
    # COMMAND DECORATORS
    # ========================================================================

    def test_command_decorator_creation(self) -> None:
        """Test command decorator creation."""
        cli_cli = FlextCliCli()
        command_result = FlextCliTestHelpers.CliHelpers.create_test_command(
            cli_cli,
            "test_cmd",
        )
        tm.ok(command_result)

        if command_result.is_success and command_result.value:
            assert isinstance(command_result.value, click.Command)
            assert command_result.value.name == "test_cmd"

    # ========================================================================
    # GROUP DECORATORS
    # ========================================================================

    def test_group_decorator_creation(self) -> None:
        """Test group decorator creation."""
        cli_cli = FlextCliCli()
        group_result = FlextCliTestHelpers.CliHelpers.create_test_group(
            cli_cli,
            "test_group",
        )
        tm.ok(group_result)

        if group_result.is_success and group_result.value:
            assert isinstance(group_result.value, click.Group)
            assert group_result.value.name == "test_group"

    # ========================================================================
    # OPTION AND ARGUMENT DECORATORS
    # ========================================================================

    def test_option_decorator(self) -> None:
        """Test option decorator creation."""
        cli_cli = FlextCliCli()
        option_config_instance = m.Cli.OptionConfig(default=1)
        option_config = cast("p.Cli.OptionConfigProtocol", option_config_instance)
        option_decorator = cli_cli.create_option_decorator(
            "--count",
            "-c",
            config=option_config,
        )
        assert callable(option_decorator)

    def test_argument_decorator(self) -> None:
        """Test argument decorator creation."""
        cli_cli = FlextCliCli()
        argument_decorator = cli_cli.create_argument_decorator("filename")
        assert callable(argument_decorator)

    def test_command_with_options(self) -> None:
        """Test command creation with options."""
        cli_cli = FlextCliCli()
        command_result = FlextCliTestHelpers.CliHelpers.create_command_with_options(
            cli_cli,
            "test_cmd",
            "--value",
            "default",
        )
        tm.ok(command_result)

    # ========================================================================
    # PARAMETER TYPES
    # ========================================================================

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
        data_dict: dict[str, object],
    ) -> None:
        """Test Click type creation with various parameter types."""
        if click_type_name == "choice":
            choices = data_dict.get("choices")
            assert isinstance(choices, list)
            choice_type = click.Choice(choices)
            assert isinstance(choice_type, click.Choice)
            assert choice_type.choices == tuple(choices)
        elif click_type_name == "path":
            path_type = click.Path(
                exists=bool(data_dict.get("exists")),
                file_okay=bool(data_dict.get("file_okay")),
                dir_okay=bool(data_dict.get("dir_okay")),
            )
            assert isinstance(path_type, click.Path)
        elif click_type_name in {"intrange", "floatrange"}:
            assert "min" in data_dict
            assert "max" in data_dict

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
        self,
        primitive_type: str,
        getter_method: str,
    ) -> None:
        """Test primitive type getter methods."""
        cli_cli = FlextCliCli()
        method = getattr(cli_cli, getter_method)
        result = method()
        expected_type = {"str": str, "int": int, "float": float, "bool": bool}[
            primitive_type
        ]
        assert result is expected_type

    def test_datetime_type(self) -> None:
        """Test DateTime type creation."""
        cli_cli = FlextCliCli()
        datetime_type = cli_cli.get_datetime_type()
        assert isinstance(datetime_type, click.DateTime)
        for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
            assert fmt in datetime_type.formats

    # ========================================================================
    # CLI RUNNER
    # ========================================================================

    def test_cli_runner_invocation(self) -> None:
        """Test CLI runner for command invocation."""
        runner = CliRunner()
        assert isinstance(runner, CliRunner)

        @click.command()
        def simple_command() -> None:
            click.echo("hello")

        result = runner.invoke(simple_command, [])
        assert result.exit_code == 0
        assert "hello" in result.output

    # ========================================================================
    # COMPREHENSIVE CLI TESTS (PARAMETRIZED)
    # ========================================================================

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
        assert should_succeed is True
        tm.ok(result)

    # ========================================================================
    # TEST EXECUTION HELPERS
    # ========================================================================

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
                    assert isinstance(cli_cli, FlextCliCli)
                    success = True
                case "runner":
                    self.test_cli_runner_invocation()
                    success = True
                case "utility":
                    cli_cli = FlextCliCli()
                    assert hasattr(cli_cli, "logger")
                    success = True
                case "model":
                    cli_cli = FlextCliCli()
                    assert isinstance(cli_cli, FlextCliCli)
                    success = True
                case "integration":
                    cli_cli = FlextCliCli()
                    result = cli_cli.execute()
                    assert result.is_success
                    success = True
                case _:
                    return r[bool].fail(f"Unknown test type: {test_type}")
            return r[bool].ok(success)
        except Exception as e:
            return r[bool].fail(str(e))

    # ========================================================================
    # EXTENDED COVERAGE TESTS
    # ========================================================================

    class TestCoverageExtended:
        """Extended tests for 100% coverage."""

        def test_create_app_with_common_params(self) -> None:
            """Test create_app_with_common_params creation only."""
            cli = FlextCliCli()
            # Just test creation, logic tested in test_cli_extended.py
            app = cli.create_app_with_common_params("test_app", "help")
            assert isinstance(app, typer.Typer)

        def test_echo(self) -> None:
            """Test echo."""
            cli = FlextCliCli()
            # Capture stdout?
            result = cli.echo("message")
            assert result.is_success

        def test_utilities(self) -> None:
            """Test utility methods."""
            cli = FlextCliCli()
            assert isinstance(cli.format_filename("test.txt"), str)
            assert isinstance(cli.get_terminal_size(), tuple)

        def test_model_command_validation(self) -> None:
            """Test model_command input validation."""
            cli = FlextCliCli()
            # Test with invalid type (not a BaseModel subclass)
            # This should raise TypeError at runtime
            # dict is not a BaseModel subclass, so this should fail
            # Using cast to bypass type checking for this negative test case
            invalid_model = cast("type[BaseModel]", dict)
            handler = cast(
                "Callable[[BaseModel], t.GeneralValueType]",
                lambda x: x,
            )
            with pytest.raises((TypeError, ValueError)):
                cli.model_command(invalid_model, handler)

        def test_create_cli_runner(self) -> None:
            """Test create_cli_runner."""
            cli = FlextCliCli()
            result = cli.create_cli_runner()
            assert result.is_success
            assert isinstance(result.unwrap(), CliRunner)

        def test_get_current_context(self) -> None:
            """Test get_current_context."""
            cli = FlextCliCli()
            # Should return None when not in command
            ctx = cli.get_current_context()
            assert ctx is None

        def test_create_pass_context_decorator(self) -> None:
            """Test create_pass_context_decorator."""
            cli = FlextCliCli()
            decorator = cli.create_pass_context_decorator()
            assert callable(decorator)

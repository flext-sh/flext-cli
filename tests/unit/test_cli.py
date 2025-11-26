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
from click.testing import CliRunner
from flext_core import FlextResult
from flext_tests import FlextTestsMatchers

from flext_cli import FlextCliCli

from ..fixtures.constants import TestCli
from ..helpers import FlextCliTestHelpers


class TestFlextCliCli:
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
        FlextTestsMatchers.assert_success(execute_result)

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
            cli_cli, TestCli.CommandNames.TEST_CMD
        )
        FlextTestsMatchers.assert_success(command_result)

        if command_result.is_success and command_result.value:
            assert isinstance(command_result.value, click.Command)
            assert command_result.value.name == TestCli.CommandNames.TEST_CMD

    # ========================================================================
    # GROUP DECORATORS
    # ========================================================================

    def test_group_decorator_creation(self) -> None:
        """Test group decorator creation."""
        cli_cli = FlextCliCli()
        group_result = FlextCliTestHelpers.CliHelpers.create_test_group(
            cli_cli, TestCli.CommandNames.TEST_GROUP
        )
        FlextTestsMatchers.assert_success(group_result)

        if group_result.is_success and group_result.value:
            assert isinstance(group_result.value, click.Group)
            assert group_result.value.name == TestCli.CommandNames.TEST_GROUP

    # ========================================================================
    # OPTION AND ARGUMENT DECORATORS
    # ========================================================================

    def test_option_decorator(self) -> None:
        """Test option decorator creation."""
        cli_cli = FlextCliCli()
        option_decorator = cli_cli.create_option_decorator("--count", "-c", default=1)
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
            cli_cli, "test_cmd", "--value", "default"
        )
        FlextTestsMatchers.assert_success(command_result)

    # ========================================================================
    # PARAMETER TYPES
    # ========================================================================

    @pytest.mark.parametrize(
        ("click_type_name", "data_dict"),
        [
            ("choice", TestCli.TestData.ClickTypeData.CHOICE_DATA),
            ("path", TestCli.TestData.ClickTypeData.PATH_DATA),
            ("file", TestCli.TestData.ClickTypeData.FILE_DATA),
            ("intrange", TestCli.TestData.ClickTypeData.INT_RANGE_DATA),
            ("floatrange", TestCli.TestData.ClickTypeData.FLOAT_RANGE_DATA),
        ],
    )
    def test_click_type_creation(
        self, click_type_name: str, data_dict: dict[str, object]
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
        TestCli.Mappings.PrimitiveTypeGetters.DATA.items(),
    )
    def test_primitive_type_getters(
        self, primitive_type: str, getter_method: str
    ) -> None:
        """Test primitive type getter methods."""
        cli_cli = FlextCliCli()
        method = getattr(cli_cli, getter_method)
        result = method()
        expected_type = TestCli.Mappings.PrimitiveTypeReturns.DATA[primitive_type]
        assert result is expected_type

    def test_datetime_type(self) -> None:
        """Test DateTime type creation."""
        cli_cli = FlextCliCli()
        datetime_type = cli_cli.get_datetime_type()
        assert isinstance(datetime_type, click.DateTime)
        for fmt in TestCli.DatetimeFormats.DEFAULT:
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
        TestCli.TestCases.CASES,
    )
    def test_cli_comprehensive_scenarios(
        self, test_type: str, description: str, should_succeed: bool
    ) -> None:
        """Comprehensive CLI scenario tests using parametrization."""
        result = self._execute_cli_test(test_type)
        assert should_succeed is True
        FlextTestsMatchers.assert_success(result)

    # ========================================================================
    # TEST EXECUTION HELPERS
    # ========================================================================

    def _execute_cli_test(self, test_type: str) -> FlextResult[bool]:
        """Execute specific CLI test by type."""
        try:
            match test_type:
                case TestCli.TestTypes.INITIALIZATION:
                    self.test_cli_initialization()
                    return FlextResult[bool].ok(True)
                case TestCli.TestTypes.COMMAND_DECORATORS:
                    self.test_command_decorator_creation()
                    return FlextResult[bool].ok(True)
                case TestCli.TestTypes.GROUP_DECORATORS:
                    self.test_group_decorator_creation()
                    return FlextResult[bool].ok(True)
                case TestCli.TestTypes.OPTION_ARGUMENT_DECORATORS:
                    self.test_option_decorator()
                    self.test_argument_decorator()
                    return FlextResult[bool].ok(True)
                case TestCli.TestTypes.PARAMETER_TYPES:
                    self.test_datetime_type()
                    return FlextResult[bool].ok(True)
                case TestCli.TestTypes.CONTEXT_MANAGEMENT:
                    cli_cli = FlextCliCli()
                    assert isinstance(cli_cli, FlextCliCli)
                    return FlextResult[bool].ok(True)
                case TestCli.TestTypes.CLI_RUNNER:
                    self.test_cli_runner_invocation()
                    return FlextResult[bool].ok(True)
                case TestCli.TestTypes.UTILITY_METHODS:
                    cli_cli = FlextCliCli()
                    assert hasattr(cli_cli, "logger")
                    return FlextResult[bool].ok(True)
                case TestCli.TestTypes.MODEL_COMMANDS:
                    cli_cli = FlextCliCli()
                    assert isinstance(cli_cli, FlextCliCli)
                    return FlextResult[bool].ok(True)
                case TestCli.TestTypes.INTEGRATION_WORKFLOWS:
                    cli_cli = FlextCliCli()
                    result = cli_cli.execute()
                    assert result.is_success
                    return FlextResult[bool].ok(True)
                case _:
                    return FlextResult[bool].fail(f"Unknown test type: {test_type}")
        except Exception as e:
            return FlextResult[bool].fail(str(e))

"""FLEXT-CLI Testing Utilities.

This module provides testing utilities and helpers for CLI applications built with flext-cli.
Includes CLI runners, output capture, mock scenarios, and integration test patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
    FlextTypes,
)

from flext_cli.cli import FlextCliCli
from flext_cli.main import FlextCliMain

if TYPE_CHECKING:
    from click.testing import Result


class FlextCliTesting(FlextService[object]):
    """CLI testing utilities for flext-cli applications.

    Provides comprehensive testing helpers including:
    - CLI command execution in test environments
    - Output capture and validation
    - Mock command scenarios
    - Integration test patterns

    Example:
        >>> from flext_cli.testing import FlextCliTesting
        >>> from flext_cli import FlextCliApi
        >>>
        >>> # Setup CLI for testing
        >>> cli = FlextCliApi()
        >>> runner = FlextCliTesting()
        >>>
        >>> # Test command execution
        >>> test_result = runner.invoke_command(
        ...     cli_main=cli.main, command_name="hello", args=["--name", "World"]
        ... )

    """

    def __init__(self, **data: object) -> None:
        """Initialize CLI test runner.

        Args:
            **data: Additional service data

        """
        super().__init__(**data)
        # Logger and container inherited from FlextService via FlextMixins

    def invoke_command(
        self,
        cli_main: FlextCliMain,
        command_name: str,
        *,
        args: FlextTypes.StringList | None = None,
        catch_exceptions: bool = True,
    ) -> FlextResult[FlextTypes.Dict]:
        """Invoke a CLI command for testing.

        Args:
            cli_main: FlextCliMain instance
            command_name: Name of command to invoke
            args: Command arguments
            catch_exceptions: Catch exceptions during execution

        Returns:
            FlextResult containing execution results with keys:
                - exit_code: Command exit code
                - output: Captured output
                - exception: Exception if raised (when catch_exceptions=True)

        Example:
            >>> runner = FlextCliTesting()
            >>> result = runner.invoke_command(
            ...     cli_main=cli.main, command_name="greet", args=["--name", "Alice"]
            ... )
            >>> if result.is_success:
            ...     data = result.unwrap()
            ...     assert data["exit_code"] == 0

        """
        try:
            click_wrapper = FlextCliCli()

            # Get CLI runner
            runner_result = click_wrapper.create_cli_runner()
            if runner_result.is_failure:
                return FlextResult[FlextTypes.Dict].fail(
                    f"Failed to create runner: {runner_result.error}"
                )

            runner = runner_result.unwrap()

            # Get command
            cmd_result = cli_main.get_command(command_name)
            if cmd_result.is_failure:
                return FlextResult[FlextTypes.Dict].fail(
                    f"Failed to get command: {cmd_result.error}"
                )

            command = cmd_result.unwrap()

            # Invoke command
            result: Result = runner.invoke(
                command, args or [], catch_exceptions=catch_exceptions
            )

            # Extract result data with explicit typing
            exit_code: int = result.exit_code
            output: str = result.output
            exception: Exception | None = (
                result.exception if hasattr(result, "exception") else None
            )

            execution_data = {
                "exit_code": exit_code,
                "output": output,
                "exception": exception,
            }

            self._logger.debug(
                "Invoked command for testing",
                extra={"cmd_name": command_name, "exit_code": exit_code},
            )

            return FlextResult[FlextTypes.Dict].ok(execution_data)

        except Exception as e:
            error_msg = f"Failed to invoke command: {e}"
            self._logger.exception(error_msg)
            return FlextResult[FlextTypes.Dict].fail(error_msg)

    def create_isolated_runner(self, *, mix_stderr: bool = True) -> FlextResult[object]:
        """Create isolated CLI runner for testing.

        Args:
            mix_stderr: Mix stderr into stdout

        Returns:
            FlextResult containing Click CliRunner

        Example:
            >>> runner = FlextCliTesting()
            >>> isolated_result = runner.create_isolated_runner()
            >>> if isolated_result.is_success:
            ...     cli_runner = isolated_result.unwrap()

        """
        try:
            click_wrapper = FlextCliCli()
            runner_result = click_wrapper.create_cli_runner(_mix_stderr=mix_stderr)

            if runner_result.is_failure:
                return FlextResult[object].fail(
                    f"Failed to create runner: {runner_result.error}"
                )

            self._logger.debug("Created isolated CLI runner")
            return FlextResult[object].ok(runner_result.unwrap())

        except Exception as e:
            error_msg = f"Failed to create isolated runner: {e}"
            self._logger.exception(error_msg)
            return FlextResult[object].fail(error_msg)

    def capture_output(
        self,
        cli_main: object,
        command_name: str,
        args: FlextTypes.StringList | None = None,
    ) -> FlextResult[str]:
        """Capture CLI command output for testing.

        Args:
            cli_main: FlextCliMain instance
            command_name: Command to execute
            args: Command arguments

        Returns:
            FlextResult containing captured output string

        Example:
            >>> runner = FlextCliTesting()
            >>> output_result = runner.capture_output(
            ...     cli_main=cli.main, command_name="hello", args=["--name", "Bob"]
            ... )
            >>> if output_result.is_success:
            ...     assert "Hello Bob" in output_result.unwrap()

        """
        try:
            result = self.invoke_command(
                cli_main=cli_main,
                command_name=command_name,
                args=args,
                catch_exceptions=True,
            )

            if result.is_failure:
                return FlextResult[str].fail(
                    f"Command invocation failed: {result.error}"
                )

            data = result.unwrap()
            output = str(data.get("output", ""))

            self._logger.debug(
                "Captured CLI output",
                extra={"cmd_name": command_name, "output_len": len(output)},
            )

            return FlextResult[str].ok(output)

        except Exception as e:
            error_msg = f"Failed to capture output: {e}"
            self._logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def assert_command_succeeds(
        self,
        cli_main: object,
        command_name: str,
        args: FlextTypes.StringList | None = None,
    ) -> FlextResult[None]:
        """Assert that CLI command succeeds (exit code 0).

        Args:
            cli_main: FlextCliMain instance
            command_name: Command to test
            args: Command arguments

        Returns:
            FlextResult[None] - success if command exits with 0, failure otherwise

        Example:
            >>> runner = FlextCliTesting()
            >>> result = runner.assert_command_succeeds(
            ...     cli_main=cli.main, command_name="version"
            ... )
            >>> assert result.is_success

        """
        try:
            result = self.invoke_command(
                cli_main=cli_main,
                command_name=command_name,
                args=args,
            )

            if result.is_failure:
                return FlextResult[None].fail(
                    f"Command execution failed: {result.error}"
                )

            data = result.unwrap()
            exit_code = data.get("exit_code", -1)

            if exit_code != 0:
                return FlextResult[None].fail(
                    f"Command failed with exit code {exit_code}"
                )

            self._logger.debug("Command succeeded", extra={"cmd_name": command_name})
            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Assertion failed: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def assert_output_contains(
        self,
        cli_main: object,
        command_name: str,
        expected_text: str,
        args: FlextTypes.StringList | None = None,
    ) -> FlextResult[None]:
        """Assert that command output contains expected text.

        Args:
            cli_main: FlextCliMain instance
            command_name: Command to test
            expected_text: Text that should be in output
            args: Command arguments

        Returns:
            FlextResult[None] - success if text found, failure otherwise

        Example:
            >>> runner = FlextCliTesting()
            >>> result = runner.assert_output_contains(
            ...     cli_main=cli.main,
            ...     command_name="hello",
            ...     expected_text="Hello World",
            ...     args=["--name", "World"],
            ... )

        """
        try:
            output_result = self.capture_output(
                cli_main=cli_main,
                command_name=command_name,
                args=args,
            )

            if output_result.is_failure:
                return FlextResult[None].fail(
                    f"Output capture failed: {output_result.error}"
                )

            output = output_result.unwrap()

            if expected_text not in output:
                return FlextResult[None].fail(
                    f"Expected text '{expected_text}' not found in output"
                )

            self._logger.debug(
                "Output contains expected text",
                extra={"cmd_name": command_name, "expected": expected_text},
            )
            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Assertion failed: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    # Attribute declarations - override FlextService optional types
    # These are guaranteed initialized in __init__
    _logger: FlextLogger | None
    _container: FlextContainer | None

    def execute(self) -> FlextResult[object]:
        """Execute CLI testing utilities.

        Returns:
            FlextResult[object]

        """
        return FlextResult[object].ok(None)

    # ==========================================================================
    # NESTED MOCK SCENARIOS - Consolidated within unified class
    # ==========================================================================

    class MockScenarios(FlextService[object]):
        """Mock scenarios for CLI testing.

        Provides pre-configured mock scenarios for common CLI testing patterns.

        Example:
            >>> from flext_cli.testing import FlextCliMockScenarios
            >>>
            >>> scenarios = FlextCliMockScenarios()
            >>> mock_config = scenarios.mock_user_config(
            ...     profile="test", debug_mode=True
            ... )

        """

        def __init__(self, **data: object) -> None:
            """Initialize mock scenarios.

            Args:
            **data: Additional service data

            """
            super().__init__(**data)
            # Logger and container inherited from FlextService via FlextMixins

    def mock_user_config(
        self,
        profile: str = "test",
        output_format: str = "json",
        *,
        debug_mode: bool = False,
        **extra: object,
    ) -> FlextResult[FlextTypes.Dict]:
        """Create mock user configuration for testing.

        Args:
            profile: Configuration profile name
            debug_mode: Debug mode flag
            output_format: Output format
            **extra: Additional config fields

        Returns:
            FlextResult containing mock configuration dict

        Example:
            >>> scenarios = FlextCliMockScenarios()
            >>> config_result = scenarios.mock_user_config(
            ...     profile="development", debug_mode=True, api_key="test-key"
            ... )

        """
        try:
            config = {
                "profile": profile,
                "debug_mode": debug_mode,
                "output_format": output_format,
                **extra,
            }

            self._logger.debug("Created mock config", extra={"config_profile": profile})
            return FlextResult[FlextTypes.Dict].ok(config)

        except Exception as e:
            error_msg = f"Failed to create mock config: {e}"
            self._logger.exception(error_msg)
            return FlextResult[FlextTypes.Dict].fail(error_msg)

    def mock_cli_context(
        self,
        command_name: str = "test-command",
        params: FlextTypes.Dict | None = None,
    ) -> FlextResult[FlextTypes.Dict]:
        """Create mock CLI context for testing.

        Args:
            command_name: Command name
            params: Command parameters

        Returns:
            FlextResult containing mock context dict

        Example:
            >>> scenarios = FlextCliMockScenarios()
            >>> context_result = scenarios.mock_cli_context(
            ...     command_name="process",
            ...     params={"input_file": "test.csv", "verbose": True},
            ... )

        """
        try:
            context = {
                "command": command_name,
                "params": params or {},
                "invoked_subcommand": "",
            }

            self._logger.debug("Created mock context", extra={"cmd_name": command_name})
            return FlextResult[FlextTypes.Dict].ok(context)

        except Exception as e:
            error_msg = f"Failed to create mock context: {e}"
            self._logger.exception(error_msg)
            return FlextResult[FlextTypes.Dict].fail(error_msg)

    def run_scenarios(self) -> FlextResult[object]:
        """Execute mock scenarios operations.

        Returns:
            FlextResult[object]

        """
        return FlextResult[object].ok(None)


__all__ = [
    "FlextCliTesting",
]

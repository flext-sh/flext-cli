"""FLEXT CLI Test Helpers - Generic and domain-specific helpers for comprehensive testing.

Provides highly reusable helpers that reduce test code by >5 lines per test.
Organized by functionality with factory patterns and railway-oriented returns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import re
import tempfile
from collections.abc import Callable
from pathlib import Path
from typing import ParamSpec, TypeVar, cast

from click import echo
from flext_core import FlextResult, FlextService, FlextTypes

from flext_cli import (
    FlextCliAppBase,
    FlextCliCli,
    FlextCliCommands,
    FlextCliConfig,
    FlextCliConstants,
    FlextCliContext,
    FlextCliModels,
    FlextCliTables,
    FlextCliTypes,
)
from flext_cli.typings import FlextCliTypes

from .fixtures.constants import (
    TestCli,
    TestConstants,
    TestData,
    TestTables,
    TestTypings,
    TestVersions,
)
from .fixtures.typing import GenericFieldsDict

T = TypeVar("T")
P = ParamSpec("P")

# Type alias for CLI option defaults
DefaultType = str | int | float | bool | GenericFieldsDict | list[object] | None


class CommandsFactory:
    """Factory for creating commands and testing scenarios."""

    @staticmethod
    def create_commands() -> FlextCliCommands:
        """Create a new FlextCliCommands instance."""
        return FlextCliCommands()

    @staticmethod
    def register_simple_command(
        commands: FlextCliCommands, name: str, result: str = "test"
    ) -> FlextResult[bool]:
        """Register a simple command that returns a constant value."""
        try:
            commands.register_command(name, lambda: result)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(str(e))

    @staticmethod
    def register_command_with_args(
        commands: FlextCliCommands, name: str
    ) -> FlextResult[bool]:
        """Register a command that accepts and processes args."""
        try:

            def cmd_with_args(args: list[str]) -> str:
                return f"args: {len(args)}"

            commands.register_command(name, cmd_with_args)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(str(e))

    @staticmethod
    def register_failing_command(
        commands: FlextCliCommands, name: str
    ) -> FlextResult[bool]:
        """Register a command that raises an exception."""
        try:

            def failing_handler() -> None:
                msg = "Handler execution error"
                raise RuntimeError(msg)

            commands.register_command(name, failing_handler)
            return FlextResult[bool].ok(True)
        except Exception as e:
            return FlextResult[bool].fail(str(e))


class FlextCliTestHelpers(FlextService[GenericFieldsDict]):
    """Generic and specialized test helpers for flext-cli following FLEXT patterns.

    Highly reusable helpers that reduce test code by >5 lines per test.
    Single class with nested helper classes organized by functionality.
    All methods return FlextResult[T] for railway-oriented testing.
    """

    # =========================================================================
    # GENERIC HELPERS - Reduce >5 lines per test across multiple test files
    # =========================================================================

    class GenericHelpers:
        """Generic helpers usable across all test types."""

        @staticmethod
        def bulk_validate_results(
            results: list[FlextResult[object]],
            *,
            expected_success: bool = True,
        ) -> FlextResult[list[object]]:
            """Validate multiple results at once - saves 3-5 lines per test.

            Args:
                results: List of FlextResult instances
                expected_success: Whether all should be successful

            Returns:
                FlextResult with extracted data or first error

            """
            try:
                extracted_data = []
                for i, result in enumerate(results):
                    if expected_success and result.is_failure:
                        return FlextResult.fail(f"Result {i} failed: {result.error}")
                    if not expected_success and result.is_success:
                        return FlextResult.fail(f"Result {i} unexpectedly succeeded")
                    if result.is_success:
                        extracted_data.append(result.unwrap())
                return FlextResult.ok(extracted_data)
            except Exception as e:
                return FlextResult.fail(str(e))

        @staticmethod
        def create_parametrized_test_cases(
            base_config: GenericFieldsDict,
            variations: list[GenericFieldsDict],
        ) -> list[GenericFieldsDict]:
            """Generate parametrized test cases from base config - reduces boilerplate.

            Args:
                base_config: Base configuration for all cases
                variations: List of variations to apply

            Returns:
                List of complete test case configurations

            """
            test_cases = []
            for variation in variations:
                case = base_config.copy()
                case.update(variation)
                test_cases.append(case)
            return test_cases

        @staticmethod
        def validate_object_attributes(
            obj: object,
            required_attrs: dict[str, type],
            optional_attrs: dict[str, type] | None = None,
        ) -> FlextResult[bool]:
            """Validate object has required attributes with correct types - saves validation code.

            Args:
                obj: Object to validate
                required_attrs: Required attributes and their expected types
                optional_attrs: Optional attributes and their expected types

            Returns:
                FlextResult indicating validation success

            """
            try:
                # Check required attributes
                for attr_name, expected_type in required_attrs.items():
                    if not hasattr(obj, attr_name):
                        return FlextResult.fail(
                            f"Missing required attribute: {attr_name}"
                        )

                    attr_value = getattr(obj, attr_name)
                    if not isinstance(attr_value, expected_type):
                        return FlextResult.fail(
                            f"Attribute {attr_name} has wrong type: {type(attr_value)} != {expected_type}"
                        )

                # Check optional attributes
                if optional_attrs:
                    for attr_name, expected_type in optional_attrs.items():
                        if hasattr(obj, attr_name):
                            attr_value = getattr(obj, attr_name)
                            if not isinstance(attr_value, expected_type):
                                return FlextResult.fail(
                                    f"Optional attribute {attr_name} has wrong type: {type(attr_value)} != {expected_type}"
                                )

                return FlextResult.ok(True)
            except Exception as e:
                return FlextResult.fail(str(e))

        @staticmethod
        def create_test_context_manager(
            setup_func: Callable[[], object] | None = None,
            teardown_func: Callable[[], object] | None = None,
        ) -> Callable[[Callable[P, T]], Callable[P, T]]:
            """Create a test context manager decorator - reduces context management code.

            Args:
                setup_func: Function to call before test execution
                teardown_func: Function to call after test execution

            Returns:
                Decorator function

            """

            def decorator(test_func: Callable[P, T]) -> Callable[P, T]:
                def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                    try:
                        if setup_func:
                            setup_func()
                        return test_func(*args, **kwargs)
                    finally:
                        if teardown_func:
                            teardown_func()

                return wrapper

            return decorator

        @staticmethod
        def assert_multiple_conditions(
            conditions: list[tuple[Callable[[], bool], str]],
        ) -> FlextResult[bool]:
            """Assert multiple conditions at once - reduces assertion boilerplate.

            Args:
                conditions: List of (condition_func, error_message) tuples

            Returns:
                FlextResult indicating all conditions passed

            """
            try:
                for condition_func, error_msg in conditions:
                    if not condition_func():
                        return FlextResult.fail(error_msg)
                return FlextResult.ok(True)
            except Exception as e:
                return FlextResult.fail(str(e))

    class AppFactory:
        """Factory for creating FlextCliAppBase instances."""

        @staticmethod
        def create_app(
            app_name: str = "test-cli",
            app_help: str = "Test CLI application",
            config_class: type[FlextCliConfig] | None = None,
        ) -> FlextResult[FlextCliAppBase]:
            """Create a FlextCliAppBase instance.

            Args:
                app_name: Name of the CLI application
                app_help: Help text for the CLI application
                config_class: Configuration class for the application

            Returns:
                FlextResult[FlextCliAppBase]: App instance

            """
            try:
                final_config_class = config_class or FlextCliConfig

                class TestCliAppBase(FlextCliAppBase):
                    """Test CLI application base class."""

                    app_name = app_name
                    app_help = app_help
                    config_class = final_config_class

                    def _register_commands(self) -> None:
                        """Register test commands - empty for test purposes."""

                return FlextResult[FlextCliAppBase].ok(TestCliAppBase())
            except Exception as e:
                return FlextResult[FlextCliAppBase].fail(str(e))

    # =========================================================================
    # NESTED HELPER: Context Creation
    # =========================================================================

    class ContextFactory:
        """Factory for creating FlextCliContext instances."""

        @staticmethod
        def create_context(
            command: str | None = None,
            arguments: list[str] | None = None,
            environment_variables: FlextTypes.JsonDict | None = None,
            working_directory: str | None = None,
            **kwargs: FlextTypes.JsonValue,
        ) -> FlextResult[FlextCliContext]:
            """Create a FlextCliContext instance.

            Args:
                command: Command being executed
                arguments: Command line arguments
                environment_variables: Environment variables
                working_directory: Current working directory
                **kwargs: Additional context data

            Returns:
                FlextResult[FlextCliContext]: Context instance

            """
            try:
                context = FlextCliContext(
                    command=command,
                    arguments=arguments,
                    environment_variables=environment_variables,
                    working_directory=working_directory,
                    **kwargs,
                )
                return FlextResult[FlextCliContext].ok(context)
            except Exception as e:
                return FlextResult[FlextCliContext].fail(str(e))

    # =========================================================================
    # NESTED HELPER: Authentication
    # =========================================================================

    class AuthHelpers:
        """Helpers for authentication testing."""

        @staticmethod
        def create_credentials(
            username: str | None = None,
            password: str | None = None,
            **overrides: str,
        ) -> FlextResult[FlextCliTypes.Auth.CredentialsData]:
            """Create test authentication credentials with validation.

            Args:
                username: Username (default: testuser), must be >= 3 chars if provided
                password: Password (default: testpass123), must be >= 8 chars if provided
                **overrides: Additional credential fields

            Returns:
                FlextResult[CredentialsData]: Test credentials or validation error

            """
            try:
                # Validate username if explicitly provided (not None)
                if username is not None:
                    if len(username.strip()) == 0:
                        return FlextResult[FlextCliTypes.Auth.CredentialsData].fail(
                            "Username cannot be empty"
                        )
                    if len(username) < 3:
                        return FlextResult[FlextCliTypes.Auth.CredentialsData].fail(
                            "Username must be at least 3 characters"
                        )
                    final_username = username
                else:
                    final_username = TestData.Users.VALID_USERNAME

                # Validate password if explicitly provided (not None)
                if password is not None:
                    if len(password.strip()) == 0:
                        return FlextResult[FlextCliTypes.Auth.CredentialsData].fail(
                            "Password cannot be empty"
                        )
                    if len(password) < 8:
                        return FlextResult[FlextCliTypes.Auth.CredentialsData].fail(
                            "Password must be at least 8 characters"
                        )
                    final_password = password
                else:
                    final_password = TestData.Users.VALID_PASSWORD

                creds: dict[str, FlextTypes.JsonValue] = {
                    FlextCliConstants.DictKeys.USERNAME: final_username,
                    FlextCliConstants.DictKeys.PASSWORD: final_password,
                    **overrides,
                }
                return FlextResult[FlextCliTypes.Auth.CredentialsData].ok(creds)
            except Exception as e:
                return FlextResult[FlextCliTypes.Auth.CredentialsData].fail(str(e))

        @staticmethod
        def create_token_data(
            token: str | None = None,
            **overrides: str,
        ) -> FlextResult[FlextCliTypes.Auth.CredentialsData]:
            """Create test token data.

            Args:
                token: Token string (default: test_token_abc123)
                **overrides: Additional token fields

            Returns:
                FlextResult[CredentialsData]: Token data

            """
            try:
                token_value = (
                    token if token is not None else TestData.Tokens.VALID_TOKEN
                )
                data: dict[str, FlextTypes.JsonValue] = {
                    "token": token_value,
                    **overrides,
                }
                return FlextResult[FlextCliTypes.Auth.CredentialsData].ok(data)
            except Exception as e:
                return FlextResult[FlextCliTypes.Auth.CredentialsData].fail(str(e))

    # =========================================================================
    # NESTED HELPER: File Operations
    # =========================================================================

    class FileHelpers:
        """Helpers for file operation testing."""

        @staticmethod
        def create_temp_file(
            content: str = TestData.Files.TEST_CONTENT,
            suffix: str = ".txt",
        ) -> FlextResult[Path]:
            """Create a temporary file with content.

            Args:
                content: File content
                suffix: File extension

            Returns:
                FlextResult[Path]: Path to temporary file

            """
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w",
                    suffix=suffix,
                    delete=False,
                    encoding="utf-8",
                ) as f:
                    f.write(content)
                    return FlextResult[Path].ok(Path(f.name))
            except Exception as e:
                return FlextResult[Path].fail(str(e))

        @staticmethod
        def create_temp_json_file(
            data: GenericFieldsDict | None = None,
        ) -> FlextResult[Path]:
            """Create a temporary JSON file.

            Args:
                data: JSON data (default: test data)

            Returns:
                FlextResult[Path]: Path to temporary JSON file

            """
            try:
                content = json.dumps(data or {"test": "data", "number": 42})
                return FlextCliTestHelpers.FileHelpers.create_temp_file(
                    content=content,
                    suffix=".json",
                )
            except Exception as e:
                return FlextResult[Path].fail(str(e))

        @staticmethod
        def create_temp_dir() -> FlextResult[Path]:
            """Create a temporary directory.

            Returns:
                FlextResult[Path]: Path to temporary directory

            """
            try:
                temp_dir = Path(tempfile.mkdtemp())
                return FlextResult[Path].ok(temp_dir)
            except Exception as e:
                return FlextResult[Path].fail(str(e))

    # =========================================================================
    # NESTED HELPER: Command Testing
    # =========================================================================

    class CommandHelpers:
        """Helpers for command testing."""

        @staticmethod
        def create_command_model(
            name: str = TestData.Commands.TEST_COMMAND,
            command_line: str = "test",
            status: FlextCliConstants.CommandStatusLiteral = "pending",
            **overrides: object,
        ) -> FlextResult[FlextCliModels.CliCommand]:
            """Create a CliCommand model instance.

            Args:
                name: Command name
                command_line: Command line
                status: Command status
                **overrides: Additional fields

            Returns:
                FlextResult[CliCommand]: Command model

            """
            try:
                # Extract valid overrides with proper types
                description: str = str(overrides.get("description", ""))
                usage: str = str(overrides.get("usage", ""))
                entry_point: str = str(overrides.get("entry_point", ""))
                plugin_version: str = str(overrides.get("plugin_version", "default"))

                command = FlextCliModels.CliCommand(
                    command_line=command_line,
                    args=[],
                    status=status,
                    exit_code=None,
                    output="",
                    error_output="",
                    execution_time=None,
                    result=None,
                    kwargs={},
                    name=name,
                    description=description,
                    usage=usage,
                    entry_point=entry_point,
                    plugin_version=plugin_version,
                )
                return FlextResult[FlextCliModels.CliCommand].ok(command)
            except Exception as e:
                return FlextResult[FlextCliModels.CliCommand].fail(str(e))

    # =========================================================================
    # NESTED HELPER: Configuration
    # =========================================================================

    class ConfigHelpers:
        """Helpers for configuration testing."""

        @staticmethod
        def create_config_data(
            debug: bool = TestData.Config.DEBUG_TRUE,
            output_format: str = TestData.Config.OUTPUT_FORMAT_JSON,
            **overrides: FlextTypes.JsonValue,
        ) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
            """Create test configuration data.

            Args:
                debug: Debug flag
                output_format: Output format
                **overrides: Additional config fields

            Returns:
                FlextResult[CliDataDict]: Config data

            """
            try:
                base_config: dict[str, FlextTypes.JsonValue] = {
                    "debug": debug,
                    "output_format": output_format,
                    "no_color": False,
                    "profile": TestData.Config.PROFILE_TEST,
                    "timeout": TestData.Config.TIMEOUT_DEFAULT,
                    "retries": TestData.Config.RETRIES_DEFAULT,
                    "api_endpoint": TestData.Config.ENDPOINT_DEFAULT,
                }
                config_data: dict[str, FlextTypes.JsonValue] = {
                    **base_config,
                    **overrides,
                }
                return FlextResult[FlextCliTypes.Data.CliDataDict].ok(config_data)
            except Exception as e:
                return FlextResult[FlextCliTypes.Data.CliDataDict].fail(str(e))

    # =========================================================================
    # NESTED HELPER: Type Testing
    # =========================================================================

    class TypingHelpers:
        """Helpers for type testing scenarios."""

        @staticmethod
        def create_typed_dict_data() -> FlextResult[GenericFieldsDict]:
            """Create TypedDict-compatible test data.

            Returns:
                FlextResult[GenericFieldsDict]: TypedDict test data

            """
            try:
                data = TestTypings.TestData.Processing.MIXED_DICT
                return FlextResult[GenericFieldsDict].ok(
                    cast("GenericFieldsDict", data)
                )
            except Exception as e:
                return FlextResult[GenericFieldsDict].fail(str(e))

        @staticmethod
        def create_api_response_data(
            status: str = TestTypings.TypedDicts.ApiResponse.STATUS,
            *,
            single_user: bool = True,
        ) -> FlextResult[GenericFieldsDict]:
            """Create API response test data.

            Args:
                status: Response status
                single_user: Whether to return single user or list

            Returns:
                FlextResult[GenericFieldsDict]: API response data

            """
            try:
                data: GenericFieldsDict = cast(
                    "GenericFieldsDict",
                    {
                        "status": status,
                        "data": TestTypings.TestData.Api.SINGLE_USER
                        if single_user
                        else TestTypings.TestData.Api.MULTI_USERS,
                        "message": TestTypings.TypedDicts.ApiResponse.MESSAGE,
                        "error": TestTypings.TypedDicts.ApiResponse.ERROR,
                    },
                )
                return FlextResult[GenericFieldsDict].ok(data)
            except Exception as e:
                return FlextResult[GenericFieldsDict].fail(str(e))

        @staticmethod
        def create_processing_test_data() -> FlextResult[
            tuple[list[str], list[int], GenericFieldsDict]
        ]:
            """Create processing test data tuple.

            Returns:
                FlextResult[tuple]: String list, number list, mixed dict

            """
            try:
                data = (
                    TestTypings.TestData.Processing.STRING_LIST,
                    TestTypings.TestData.Processing.NUMBER_LIST,
                    cast(
                        "GenericFieldsDict", TestTypings.TestData.Processing.MIXED_DICT
                    ),
                )
                return FlextResult[tuple[list[str], list[int], GenericFieldsDict]].ok(
                    data
                )
            except Exception as e:
                return FlextResult[tuple[list[str], list[int], GenericFieldsDict]].fail(
                    str(e)
                )

    # =========================================================================
    # NESTED HELPER: Protocol Testing
    # =========================================================================

    class ProtocolHelpers:
        """Helpers for protocol testing scenarios."""

        @staticmethod
        def create_formatter_implementation() -> FlextResult[object]:
            """Create a CliFormatter protocol implementation."""
            try:

                class TestFormatter:
                    def format_data(
                        self, data: GenericFieldsDict, **options: GenericFieldsDict
                    ) -> FlextResult[str]:
                        try:
                            indent_value: int | None = None
                            if "indent" in options:
                                val = options.get("indent", 2)
                                indent_value = (
                                    int(val) if isinstance(val, (int, str)) else 2
                                )
                            formatted = json.dumps(data, indent=indent_value or 2)
                            return FlextResult[str].ok(formatted)
                        except Exception as e:
                            return FlextResult[str].fail(str(e))

                return FlextResult[object].ok(TestFormatter())
            except Exception as e:
                return FlextResult[object].fail(str(e))

        @staticmethod
        def create_config_provider_implementation() -> FlextResult[object]:
            """Create a CliConfigProvider protocol implementation."""
            try:

                class TestConfigProvider:
                    def __init__(self) -> None:
                        self._config: GenericFieldsDict = cast("GenericFieldsDict", {})

                    def load_config(self) -> FlextResult[GenericFieldsDict]:
                        return FlextResult[GenericFieldsDict].ok(
                            cast("GenericFieldsDict", self._config.copy())
                        )

                    def save_config(
                        self, config: GenericFieldsDict
                    ) -> FlextResult[bool]:
                        self._config.update(config)
                        return FlextResult[bool].ok(True)

                return FlextResult[object].ok(TestConfigProvider())
            except Exception as e:
                return FlextResult[object].fail(str(e))

        @staticmethod
        def create_authenticator_implementation() -> FlextResult[object]:
            """Create a CliAuthenticator protocol implementation."""
            try:

                class TestAuthenticator:
                    def authenticate(
                        self, credentials: GenericFieldsDict
                    ) -> FlextResult[GenericFieldsDict]:
                        username = credentials.get("username")
                        password = credentials.get("password")
                        if username == "testuser" and password == "testpass":
                            return FlextResult[GenericFieldsDict].ok(
                                cast(
                                    "GenericFieldsDict",
                                    {
                                        "token": "valid_token",
                                        "user": username,
                                    },
                                )
                            )
                        return FlextResult[GenericFieldsDict].fail(
                            "Invalid credentials"
                        )

                    def validate_token(self, token: str) -> FlextResult[bool]:
                        return FlextResult[bool].ok(token.startswith("valid_"))

                return FlextResult[object].ok(TestAuthenticator())
            except Exception as e:
                return FlextResult[object].fail(str(e))

    # =========================================================================
    # NESTED HELPER: CLI Testing
    # =========================================================================

    class CliHelpers:
        """Helpers for CLI testing scenarios."""

        @staticmethod
        def create_test_command(
            cli_cli: FlextCliCli,
            name: str,
            help_text: str = "Test command",
        ) -> FlextResult[object]:
            """Create a test command using CLI decorator."""
            try:
                decorator = cli_cli.create_command_decorator(
                    name=name, help_text=help_text
                )

                @decorator
                def test_func(
                    *args: object, **kwargs: object
                ) -> FlextCliTypes.CliJsonValue:
                    """Test command function."""
                    echo("Test")
                    return None

                return FlextResult[object].ok(test_func)
            except Exception as e:
                return FlextResult[object].fail(str(e))

        @staticmethod
        def create_test_group(
            cli_cli: FlextCliCli,
            name: str,
            help_text: str = "Test group",
        ) -> FlextResult[object]:
            """Create a test group using CLI decorator."""
            try:
                decorator = cli_cli.create_group_decorator(
                    name=name, help_text=help_text
                )

                @decorator
                def test_group_func(
                    *args: object, **kwargs: object
                ) -> FlextCliTypes.CliJsonValue:
                    """Group function."""
                    return None

                return FlextResult[object].ok(test_group_func)
            except Exception as e:
                return FlextResult[object].fail(str(e))

        @staticmethod
        def create_command_with_options(
            cli_cli: FlextCliCli,
            command_name: str,
            option_name: str,
            option_default: DefaultType = None,
        ) -> FlextResult[object]:
            """Create a command with options."""
            try:
                command_decorator = cli_cli.create_command_decorator(name=command_name)
                option_decorator = cli_cli.create_option_decorator(
                    option_name, default=option_default
                )

                @command_decorator
                @option_decorator
                def test_command(
                    *args: object, **kwargs: object
                ) -> FlextCliTypes.CliJsonValue:
                    """Test command with options."""
                    value = kwargs.get("value") if kwargs else args[0] if args else None
                    echo(f"Value: {value}")
                    return None

                return FlextResult[object].ok(test_command)
            except Exception as e:
                return FlextResult[object].fail(str(e))

        @staticmethod
        def create_model_command_test_data() -> FlextResult[dict[str, object]]:
            """Create test data for model command testing."""
            try:
                data: dict[str, object] = {
                    "params_with_aliases": TestCli.TestData.Models.PARAMS_WITH_ALIASES,
                    "standard_params": TestCli.TestData.Models.STANDARD_PARAMS,
                    "bool_params": TestCli.TestData.Models.BOOL_PARAMS,
                    "mixed_params": TestCli.TestData.Models.MIXED_PARAMS,
                }
                return FlextResult[dict[str, object]].ok(data)
            except Exception as e:
                return FlextResult[dict[str, object]].fail(str(e))

    # =========================================================================
    # NESTED HELPER: Test Assertions
    # =========================================================================

    class AssertHelpers:
        """Enhanced assertion helpers for test validation - reduces 3-5 lines per test."""

        @staticmethod
        def assert_result_success(result: FlextResult[object]) -> None:
            """Assert FlextResult is successful.

            Args:
                result: Result to validate

            Raises:
                AssertionError: If result is not successful

            """
            assert result.is_success, f"Expected success, got: {result.error}"

        @staticmethod
        def assert_result_failure(
            result: FlextResult[object], error_contains: str | None = None
        ) -> None:
            """Assert FlextResult is failure.

            Args:
                result: Result to validate
                error_contains: Optional substring that error must contain

            Raises:
                AssertionError: If result is not failure

            """
            assert result.is_failure, f"Expected failure, got: {result}"
            if error_contains:
                error_msg = str(result.error).lower() if result.error else ""
                assert error_contains.lower() in error_msg, (
                    f"Error should contain '{error_contains}', got: {error_msg}"
                )

        @staticmethod
        def assert_file_operations(
            result: FlextResult[object],
            expected_path: Path | None = None,
            expected_content: str | None = None,
        ) -> None:
            """Assert file operation result and verify file state.

            Args:
                result: File operation result
                expected_path: Path to verify exists
                expected_content: Expected file content

            """
            FlextCliTestHelpers.AssertHelpers.assert_result_success(result)
            if expected_path:
                assert expected_path.exists(), f"File should exist: {expected_path}"
                if expected_content:
                    assert expected_path.read_text() == expected_content

        @staticmethod
        def assert_component_state(
            obj: object,
            component_name: str,
            *,
            expected_exists: bool = True,
            expected_type: type | None = None,
        ) -> None:
            """Assert component state on an object - saves 3-4 lines per component check.

            Args:
                obj: Object to check
                component_name: Name of the component attribute
                expected_exists: Whether component should exist
                expected_type: Expected type of the component

            Raises:
                AssertionError: If component state doesn't match expectations

            """
            if expected_exists:
                assert hasattr(obj, component_name), (
                    f"Component {component_name} should exist"
                )
                component = getattr(obj, component_name)
                assert component is not None, (
                    f"Component {component_name} should not be None"
                )
                if expected_type:
                    assert isinstance(component, expected_type), (
                        f"Component {component_name} should be {expected_type}, got {type(component)}"
                    )
            elif hasattr(obj, component_name):
                component = getattr(obj, component_name)
                assert component is None, f"Component {component_name} should be None"

        @staticmethod
        def assert_method_callable(
            obj: object,
            method_name: str,
            *,
            expected_callable: bool = True,
        ) -> None:
            """Assert method exists and is callable - saves 2-3 lines per method check.

            Args:
                obj: Object to check
                method_name: Name of the method
                expected_callable: Whether method should be callable

            Raises:
                AssertionError: If method state doesn't match expectations

            """
            assert hasattr(obj, method_name), f"Method {method_name} should exist"
            method = getattr(obj, method_name)
            if expected_callable:
                assert callable(method), f"Method {method_name} should be callable"
            else:
                assert not callable(method), (
                    f"Method {method_name} should not be callable"
                )

        @staticmethod
        def assert_dict_structure(
            data: dict[str, object],
            required_keys: list[str],
            optional_keys: list[str] | None = None,
            key_types: dict[str, type] | None = None,
        ) -> None:
            """Assert dictionary has expected structure - saves 5-10 lines per structure check.

            Args:
                data: Dictionary to validate
                required_keys: Keys that must be present
                optional_keys: Keys that may be present
                key_types: Expected types for specific keys

            Raises:
                AssertionError: If structure doesn't match expectations

            """
            # Check required keys
            for key in required_keys:
                assert key in data, f"Required key '{key}' missing from dict"

            # Check key types
            if key_types:
                for key, expected_type in key_types.items():
                    if key in data:
                        assert isinstance(data[key], expected_type), (
                            f"Key '{key}' should be {expected_type}, got {type(data[key])}"
                        )

            # Check no unexpected keys (if optional_keys specified)
            if optional_keys is not None:
                all_allowed_keys = set(required_keys + optional_keys)
                actual_keys = set(data.keys())
                unexpected_keys = actual_keys - all_allowed_keys
                assert not unexpected_keys, f"Unexpected keys found: {unexpected_keys}"

    # =========================================================================
    # NESTED HELPER: Output Formatting
    # =========================================================================

    class OutputHelpers:
        """Helpers for output formatting tests."""

        @staticmethod
        def create_format_test_data() -> FlextCliTypes.Data.CliDataDict:
            """Create standard test data for format tests.

            Returns:
                Test data dictionary

            """
            data: dict[str, FlextTypes.JsonValue] = {
                "key": "value",
                "number": 42,
                "list": [1, 2, 3],
            }
            return data

        @staticmethod
        def create_table_test_data() -> FlextCliTypes.Data.CliDataDict:
            """Create test data for table formatting.

            Returns:
                Test data with table structure

            """
            # Convert table data to JsonValue-compatible format
            users_list: list[object] = [
                dict(row.items()) for row in TestData.Tables.SIMPLE_DATA
            ]
            data: dict[str, FlextTypes.JsonValue] = {"users": users_list}
            return data

    class ConstantsFactory:
        """Factory for FlextCliConstants instance creation and validation."""

        @staticmethod
        def get_constants() -> FlextCliConstants:
            """Get FlextCliConstants instance."""
            return FlextCliConstants()

        @staticmethod
        def validate_constant_value(
            constant_value: str,
            expected_value: str,
        ) -> FlextResult[bool]:
            """Validate that constant matches expected value."""
            if constant_value == expected_value:
                return FlextResult[bool].ok(True)
            return FlextResult[bool].fail(
                f"Constant value '{constant_value}' does not match expected '{expected_value}'",
            )

        @staticmethod
        def validate_constant_format(
            constant_value: str,
            must_start_with: str | None = None,
            must_end_with: str | None = None,
            must_not_contain: list[str] | None = None,
        ) -> FlextResult[bool]:
            """Validate constant format according to rules."""
            if must_start_with and not constant_value.startswith(must_start_with):
                return FlextResult[bool].fail(
                    f"Constant must start with '{must_start_with}', got '{constant_value}'",
                )

            if must_end_with and not constant_value.endswith(must_end_with):
                return FlextResult[bool].fail(
                    f"Constant must end with '{must_end_with}', got '{constant_value}'",
                )

            if must_not_contain:
                for char in must_not_contain:
                    if char in constant_value:
                        return FlextResult[bool].fail(
                            f"Constant must not contain '{char}', got '{constant_value}'",
                        )

            return FlextResult[bool].ok(True)

        @staticmethod
        def validate_all_constants(
            constants: FlextCliConstants,
        ) -> FlextResult[dict[str, bool]]:
            """Validate all constants against expected format and values."""
            validations: dict[str, bool] = {}

            # Validate PROJECT_NAME
            project_name_valid = (
                FlextCliTestHelpers.ConstantsFactory.validate_constant_value(
                    constants.PROJECT_NAME,
                    TestConstants.ExpectedValues.PROJECT_NAME,
                ).is_success
            )
            validations["PROJECT_NAME"] = project_name_valid

            # Validate FLEXT_DIR_NAME
            dir_name_valid = FlextCliTestHelpers.ConstantsFactory.validate_constant_format(
                constants.FLEXT_DIR_NAME,
                must_start_with=TestConstants.FormatValidation.DIR_NAME_MUST_START_WITH,
            ).is_success
            validations["FLEXT_DIR_NAME"] = dir_name_valid

            # Validate TOKEN_FILE_NAME
            token_file_valid = FlextCliTestHelpers.ConstantsFactory.validate_constant_format(
                constants.TOKEN_FILE_NAME,
                must_end_with=TestConstants.FormatValidation.FILE_NAME_MUST_END_WITH,
                must_not_contain=TestConstants.InvalidChars.COMMON_INVALID,
            ).is_success
            validations["TOKEN_FILE_NAME"] = token_file_valid

            # Validate REFRESH_TOKEN_FILE_NAME
            refresh_token_file_valid = FlextCliTestHelpers.ConstantsFactory.validate_constant_format(
                constants.REFRESH_TOKEN_FILE_NAME,
                must_end_with=TestConstants.FormatValidation.FILE_NAME_MUST_END_WITH,
                must_not_contain=TestConstants.InvalidChars.COMMON_INVALID,
            ).is_success
            validations["REFRESH_TOKEN_FILE_NAME"] = refresh_token_file_valid

            if all(validations.values()):
                return FlextResult[dict[str, bool]].ok(validations)

            failed = [key for key, valid in validations.items() if not valid]
            return FlextResult[dict[str, bool]].fail(
                f"Constants validation failed for: {', '.join(failed)}",
            )

    class VersionTestFactory:
        """Factory for version validation testing."""

        @staticmethod
        def validate_version_string(version: str) -> FlextResult[bool]:
            """Validate version string format and constraints."""
            # version is already typed as str, so isinstance check is for runtime safety only

            if len(version) < TestVersions.Formats.MIN_VERSION_LENGTH:
                return FlextResult[bool].fail("Version too short")

            if len(version) > TestVersions.Formats.MAX_VERSION_LENGTH:
                return FlextResult[bool].fail("Version too long")

            if not re.match(TestVersions.Formats.SEMVER_PATTERN, version):
                return FlextResult[bool].fail("Invalid semver format")

            return FlextResult[bool].ok(True)

        @staticmethod
        def validate_version_info(info: tuple[int | str, ...]) -> FlextResult[bool]:
            """Validate version info tuple."""
            # info is already typed as tuple, so isinstance check is for runtime safety only

            if len(info) < TestVersions.Formats.MAJOR_MINOR_PATCH:
                return FlextResult[bool].fail("Version info too short")

            # First three parts should be int or str
            for i in range(min(TestVersions.Formats.MAJOR_MINOR_PATCH, len(info))):
                if not isinstance(info[i], (int, str)):
                    return FlextResult[bool].fail(f"Part {i} has invalid type")

            return FlextResult[bool].ok(True)

        @staticmethod
        def validate_consistency(
            version: str,
            info: tuple[int | str, ...],
        ) -> FlextResult[bool]:
            """Validate consistency between version string and info tuple."""
            # Simulate real __version_info__ creation logic
            expected_info = tuple(
                int(part) if part.isdigit() else part for part in version.split(".")
            )

            if expected_info != info:
                return FlextResult[bool].fail(
                    f"Version info mismatch: expected {expected_info}, got {info}",
                )

            return FlextResult[bool].ok(True)

    # =========================================================================
    # FlextService Protocol Implementation
    # =========================================================================

    def execute(self, **_kwargs: object) -> FlextResult[dict[str, object]]:
        """Execute testing service.

        Args:
            **kwargs: Additional execution parameters

        Returns:
            FlextResult[dict[str, Any]]: Service execution status

        """
        try:
            payload = {
                FlextCliConstants.DictKeys.STATUS: FlextCliConstants.ServiceStatus.OPERATIONAL.value,
                FlextCliConstants.DictKeys.SERVICE: "FlextCliTestHelpers",
                FlextCliConstants.DictKeys.MESSAGE: "Test helpers ready",
            }
            payload_data = cast("dict[str, object]", payload)
            return FlextResult[dict[str, object]].ok(payload_data)
        except Exception as e:
            return FlextResult[dict[str, object]].fail(str(e))

    # =========================================================================
    # NESTED HELPER: Tables Testing
    # =========================================================================

    class TablesFactory:
        """Factory for creating table test data and scenarios."""

        @staticmethod
        def create_tables() -> FlextCliTables:
            """Create a new FlextCliTables instance."""
            return FlextCliTables()

        @staticmethod
        def get_test_data() -> dict[str, object]:
            """Get comprehensive table test data."""
            return {
                "people_dict": TestTables.Data.Sample.PEOPLE_DICT,
                "people_list": TestTables.Data.Sample.PEOPLE_LIST,
                "single_row": TestTables.Data.Sample.SINGLE_ROW,
                "with_none": TestTables.Data.Sample.WITH_NONE,
                "empty": TestTables.Data.Sample.EMPTY,
                "none": None,
            }


# ============================================================================
# CONVENIENCE EXPORTS (for backward compatibility)
# ============================================================================

create_flext_cli_app_base = FlextCliTestHelpers.AppFactory.create_app

# Expose nested classes as module-level for import convenience
OutputHelpers = FlextCliTestHelpers.OutputHelpers
AuthHelpers = FlextCliTestHelpers.AuthHelpers
CommandHelpers = FlextCliTestHelpers.CommandHelpers

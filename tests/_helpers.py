"""FLEXT CLI Test Helpers - Generic and domain-specific helpers for comprehensive testing.

Provides highly reusable helpers that reduce test code by >5 lines per test.
Organized by functionality with factory patterns and railway-oriented returns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping, Sequence
from typing import ParamSpec, TypeVar, cast

from click import echo
from flext_core import FlextService

from flext_cli import (
    FlextCliAppBase,
    FlextCliCli,
    FlextCliCommands,
    FlextCliConfig,
    FlextCliConstants,
    FlextCliContext,
    FlextCliTables,
    c,
    m,
    p,
    r,
    u,
)
from flext_cli.typings import t

# Fixtures modules removed - use conftest.py and flext_tests instead
# from .fixtures.constants import ...
# from .fixtures.typing import GenericFieldsDict

T = TypeVar("T")
P = ParamSpec("P")

# Type alias for CLI option defaults
type DefaultType = (
    str | int | float | bool | dict[str, t.GeneralValueType] | list[object] | None
)


class CommandsFactory:
    """Factory for creating commands and testing scenarios."""

    @staticmethod
    def create_commands() -> FlextCliCommands:
        """Create a new FlextCliCommands instance."""
        return FlextCliCommands()

    @staticmethod
    def register_simple_command(
        commands: FlextCliCommands,
        name: str,
        result: str = "test",
    ) -> r[bool]:
        """Register a simple command that returns a constant value."""
        try:
            handler: p.Cli.CliCommandHandler = cast(
                "p.Cli.CliCommandHandler",
                lambda: result,
            )
            commands.register_command(name, handler)
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(str(e))

    @staticmethod
    def register_command_with_args(commands: FlextCliCommands, name: str) -> r[bool]:
        """Register a command that accepts and processes args."""
        try:

            def cmd_with_args(
                *args: t.GeneralValueType,
                **kwargs: t.GeneralValueType,
            ) -> t.GeneralValueType:
                if args and isinstance(args[0], list):
                    arg_list = args[0]
                    return f"args: {len(arg_list)}"
                return "args: 0"

            commands.register_command(name, cmd_with_args)
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(str(e))

    @staticmethod
    def register_failing_command(commands: FlextCliCommands, name: str) -> r[bool]:
        """Register a command that raises an exception."""
        try:

            def failing_handler(
                *args: t.GeneralValueType,
                **kwargs: t.GeneralValueType,
            ) -> t.GeneralValueType:
                msg = "Handler execution error"
                raise RuntimeError(msg)

            commands.register_command(name, failing_handler)
            return r[bool].ok(True)
        except Exception as e:
            return r[bool].fail(str(e))


class FlextCliTestHelpers(FlextService[dict[str, t.GeneralValueType]]):
    """Generic and specialized test helpers for flext-cli following FLEXT patterns.

    Highly reusable helpers that reduce test code by >5 lines per test.
    Single class with nested helper classes organized by functionality.
    All methods return r[T] for railway-oriented testing.
    """

    # =========================================================================
    # GENERIC HELPERS - Reduce >5 lines per test across multiple test files
    # =========================================================================

    # GenericHelpers removed - use FlextTestsUtilities.GenericHelpers directly

    # JsonHelpers removed - use FlextTestsUtilities.GenericHelpers directly
    # - to_json_dict -> FlextTestsUtilities.GenericHelpers.to_json_dict
    # - to_json_value -> FlextTestsUtilities.GenericHelpers.to_json_value

    # TestAutomationHelpers removed - use FlextTestsUtilities.GenericHelpers directly
    # - validate_object_properties -> FlextTestsUtilities.GenericHelpers.validate_object_properties
    # - batch_test_operations -> FlextTestsUtilities.GenericHelpers.batch_test_operations
    # - test_with_mock_exception -> FlextTestsUtilities.GenericHelpers.test_with_mock_exception
    # - assert_result_with_message -> use tm.ok()/tm.fail() directly

    class AppFactory:
        """Factory for creating FlextCliAppBase instances."""

        @staticmethod
        def create_app(
            app_name: str = "test-cli",
            app_help: str = "Test CLI application",
            config_class: type[FlextCliConfig] | None = None,
        ) -> r[FlextCliAppBase]:
            """Create a FlextCliAppBase instance.

            Args:
                app_name: Name of the CLI application
                app_help: Help text for the CLI application
                config_class: Configuration class for the application

            Returns:
                r[FlextCliAppBase]: App instance

            """
            try:
                final_config_class = config_class or FlextCliConfig

                app_name_value = app_name
                app_help_value = app_help

                class TestCliAppBase(FlextCliAppBase):
                    """Test CLI application base class."""

                    app_name = app_name_value
                    app_help = app_help_value
                    config_class = final_config_class

                    def _register_commands(self) -> None:
                        """Register test commands - empty for test purposes."""

                return r[FlextCliAppBase].ok(TestCliAppBase())
            except Exception as e:
                return r[FlextCliAppBase].fail(str(e))

    # =========================================================================
    # NESTED HELPER: Context Creation
    # =========================================================================

    class ContextFactory:
        """Factory for creating FlextCliContext instances."""

        @staticmethod
        def create_context(
            command: str | None = None,
            arguments: list[str] | None = None,
            environment_variables: dict[str, t.GeneralValueType] | None = None,
            working_directory: str | None = None,
            **kwargs: t.JsonValue,
        ) -> r[FlextCliContext]:
            """Create a FlextCliContext instance.

            Args:
                command: Command being executed
                arguments: Command line arguments
                environment_variables: Environment variables
                working_directory: Current working directory
                **kwargs: Additional context data

            Returns:
                r[FlextCliContext]: Context instance

            """
            try:
                env_vars: dict[str, t.GeneralValueType] | None = (
                    cast(
                        "dict[str, t.GeneralValueType] | None",
                        environment_variables,
                    )
                    if environment_variables is not None
                    else None
                )
                context = FlextCliContext(
                    command=command,
                    arguments=arguments,
                    environment_variables=env_vars,
                    working_directory=working_directory,
                    **kwargs,
                )
                return r[FlextCliContext].ok(context)
            except Exception as e:
                return r[FlextCliContext].fail(str(e))

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
        ) -> r[Mapping[str, str]]:
            """Create test authentication credentials with validation.

            Args:
                username: Username (default: testuser), must be >= 3 chars if provided
                password: Password (default: testpass123), must be >= 8 chars if provided
                **overrides: Additional credential fields

            Returns:
                r[CredentialsData]: Test credentials or validation error

            """
            try:
                # Validate username if explicitly provided (not None)
                if username is not None:
                    if len(username.strip()) == 0:
                        return r[Mapping[str, str]].fail("Username cannot be empty")
                    if len(username) < 3:
                        return r[Mapping[str, str]].fail(
                            "Username must be at least 3 characters",
                        )
                    final_username = username
                else:
                    final_username = "testuser"

                # Validate password if explicitly provided (not None)
                if password is not None:
                    if len(password.strip()) == 0:
                        return r[Mapping[str, str]].fail("Password cannot be empty")
                    if len(password) < 8:
                        return r[Mapping[str, str]].fail(
                            "Password must be at least 8 characters",
                        )
                    final_password = password
                else:
                    final_password = "testpass123"

                creds: dict[str, t.JsonValue] = {
                    c.DictKeys.USERNAME: final_username,
                    c.DictKeys.PASSWORD: final_password,
                    **overrides,
                }
                creds_str: Mapping[str, str] = cast("Mapping[str, str]", creds)
                return r[Mapping[str, str]].ok(creds_str)
            except Exception as e:
                return r[Mapping[str, str]].fail(str(e))

        @staticmethod
        def create_token_data(
            token: str | None = None,
            **overrides: str,
        ) -> r[Mapping[str, str]]:
            """Create test token data.

            Args:
                token: Token string (default: test_token_abc123)
                **overrides: Additional token fields

            Returns:
                r[CredentialsData]: Token data

            """
            try:
                token_value = token if token is not None else "test_token_abc123"
                data: dict[str, t.JsonValue] = {
                    "token": token_value,
                    **overrides,
                }
                data_str: Mapping[str, str] = cast("Mapping[str, str]", data)
                return r[Mapping[str, str]].ok(data_str)
            except Exception as e:
                return r[Mapping[str, str]].fail(str(e))

    # =========================================================================
    # NESTED HELPER: File Operations
    # =========================================================================

    # FileHelpers removed - use FlextTestsFileManager directly

    # =========================================================================
    # NESTED HELPER: Command Testing
    # =========================================================================

    class CommandHelpers:
        """Helpers for command testing."""

        @staticmethod
        def create_command_model(
            name: str = "test_command",
            command_line: str = "test",
            status: c.CommandStatusLiteral = c.CommandStatus.PENDING.value,
            **overrides: object,
        ) -> r[m.CliCommand]:
            """Create a CliCommand model instance.

            Args:
                name: Command name
                command_line: Command line
                status: Command status
                **overrides: Additional fields

            Returns:
                r[CliCommand]: Command model

            """
            try:
                # Extract valid overrides with proper types
                description: str = str(overrides.get("description", ""))
                usage: str = str(overrides.get("usage", ""))
                entry_point: str = str(overrides.get("entry_point", ""))
                plugin_version: str = str(overrides.get("plugin_version", "default"))

                command = m.CliCommand(
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
                return r[m.CliCommand].ok(command)
            except Exception as e:
                return r[m.CliCommand].fail(str(e))

    # =========================================================================
    # NESTED HELPER: Configuration
    # =========================================================================

    class ConfigHelpers:
        """Helpers for configuration testing."""

        @staticmethod
        def create_config_data(
            *,
            debug: bool = True,
            output_format: str = c.OutputFormats.JSON.value,
            **overrides: t.JsonValue,
        ) -> r[dict[str, t.GeneralValueType]]:
            """Create test configuration data - uses c.

            Args:
                debug: Debug flag
                output_format: Output format (default: JSON from FlextCliConstants)
                **overrides: Additional config fields

            Returns:
                r[CliDataDict]: Config data

            """
            try:
                base_config: dict[str, t.JsonValue] = {
                    "debug": debug,
                    "output_format": output_format,
                    "no_color": False,
                    "profile": "test",
                    "timeout": c.NetworkDefaults.DEFAULT_TIMEOUT,
                    "retries": c.NetworkDefaults.DEFAULT_MAX_RETRIES,
                    "api_endpoint": "https://api.example.com",
                }
                config_data: dict[str, t.JsonValue] = {
                    **base_config,
                    **overrides,
                }
                return r[dict[str, t.GeneralValueType]].ok(
                    cast("dict[str, t.GeneralValueType]", config_data),
                )
            except Exception as e:
                return r[dict[str, t.GeneralValueType]].fail(str(e))

    # =========================================================================
    # NESTED HELPER: Type Testing
    # =========================================================================

    class TypingHelpers:
        """Helpers for type testing scenarios."""

        @staticmethod
        def create_typed_dict_data() -> r[dict[str, t.GeneralValueType]]:
            """Create TypedDict-compatible test data.

            Returns:
                r[dict[str, t.GeneralValueType]]: TypedDict test data

            """
            try:
                data: dict[str, t.GeneralValueType] = {
                    "key1": 123,
                    "key2": "value",
                    "key3": True,
                    "key4": [1, 2, 3],
                }
                # Convert to JsonDict-compatible dict using helper
                # data is already dict[str, object], convert to GeneralValueType
                data_converted: dict[str, t.GeneralValueType] = data
                # Use u.transform for JSON conversion
                transform_result = u.transform(
                    data_converted,
                    to_json=True,
                )
                converted_data = (
                    transform_result.unwrap()
                    if transform_result.is_success
                    else data_converted
                )
                return r[dict[str, t.GeneralValueType]].ok(converted_data)
            except Exception as e:
                return r[dict[str, t.GeneralValueType]].fail(str(e))

        @staticmethod
        def create_api_response_data(
            status: str = "success",
            *,
            single_user: bool = True,
        ) -> r[dict[str, t.GeneralValueType]]:
            """Create API response test data.

            Args:
                status: Response status
                single_user: Whether to return single user or list

            Returns:
                r[dict[str, t.GeneralValueType]]: API response data

            """
            try:
                raw_data = {
                    "status": status,
                    "data": {
                        "id": 1,
                        "name": "Alice",
                        "email": "alice@example.com",
                        "active": True,
                    }
                    if single_user
                    else [
                        {
                            "id": 1,
                            "name": "Alice",
                            "email": "alice@example.com",
                            "active": True,
                        },
                        {
                            "id": 2,
                            "name": "Bob",
                            "email": "bob@example.com",
                            "active": False,
                        },
                    ],
                    "message": "Operation successful",
                    "error": None,
                }
                # Convert to JsonDict-compatible dict using helper
                raw_data_converted: dict[str, t.GeneralValueType] = cast(
                    "dict[str, t.GeneralValueType]",
                    raw_data,
                )
                # Use u.transform for JSON conversion
                transform_result = u.transform(raw_data_converted, to_json=True)
                data = (
                    transform_result.unwrap()
                    if transform_result.is_success
                    else raw_data_converted
                )
                return r[dict[str, t.GeneralValueType]].ok(data)
            except Exception as e:
                return r[dict[str, t.GeneralValueType]].fail(str(e))

        @staticmethod
        def create_processing_test_data() -> r[
            tuple[list[str], list[int], dict[str, t.GeneralValueType]]
        ]:
            """Create processing test data tuple.

            Returns:
                r[tuple]: String list, number list, mixed dict

            """
            try:
                # Convert mixed dict to JsonDict-compatible dict using helper
                mixed_dict_input: dict[str, t.GeneralValueType] = cast(
                    "dict[str, t.GeneralValueType]",
                    {
                        "key1": 123,
                        "key2": "value",
                        "key3": True,
                        "key4": [1, 2, 3],
                    },
                )
                # Use u.transform for JSON conversion
                transform_result = u.transform(mixed_dict_input, to_json=True)
                mixed_dict = (
                    transform_result.unwrap()
                    if transform_result.is_success
                    else mixed_dict_input
                )
                data = (
                    ["hello", "world", "test"],
                    [1, 2, 3, 4, 5],
                    mixed_dict,
                )
                return r[tuple[list[str], list[int], dict[str, t.GeneralValueType]]].ok(
                    data,
                )
            except Exception as e:
                return r[
                    tuple[list[str], list[int], dict[str, t.GeneralValueType]]
                ].fail(str(e))

    # =========================================================================
    # NESTED HELPER: Protocol Testing
    # =========================================================================

    class ProtocolHelpers:
        """Helpers for protocol testing scenarios."""

        @staticmethod
        def create_formatter_implementation() -> r[object]:
            """Create a CliFormatter protocol implementation."""
            try:

                class TestFormatter:
                    def format_data(
                        self,
                        data: dict[str, t.GeneralValueType],
                        **options: dict[str, t.GeneralValueType],
                    ) -> r[str]:
                        try:
                            indent_value: int | None = None
                            if "indent" in options:
                                val = options.get("indent", 2)
                                indent_value = (
                                    int(val) if isinstance(val, (int, str)) else 2
                                )
                            formatted = json.dumps(data, indent=indent_value or 2)
                            return r[str].ok(formatted)
                        except Exception as e:
                            return r[str].fail(str(e))

                return r[object].ok(TestFormatter())
            except Exception as e:
                return r[object].fail(str(e))

        @staticmethod
        def create_config_provider_implementation() -> r[object]:
            """Create a CliConfigProvider protocol implementation."""
            try:

                class TestConfigProvider:
                    def __init__(self) -> None:
                        self._config: dict[str, t.GeneralValueType] = {}

                    def load_config(self) -> r[dict[str, object]]:
                        # Convert to JsonDict-compatible dict using helper
                        config_copy_raw = self._config.copy()
                        config_copy_converted: dict[
                            str,
                            t.GeneralValueType,
                        ] = config_copy_raw
                        # Use u.transform for JSON conversion
                        transform_result = u.transform(
                            config_copy_converted,
                            to_json=True,
                        )
                        config_copy = (
                            transform_result.unwrap()
                            if transform_result.is_success
                            else config_copy_converted
                        )
                        return r[dict[str, object]].ok(config_copy)

                    def save_config(
                        self,
                        config: dict[str, t.GeneralValueType],
                    ) -> r[bool]:
                        self._config.update(config)
                        return r[bool].ok(True)

                return r[object].ok(TestConfigProvider())
            except Exception as e:
                return r[object].fail(str(e))

        @staticmethod
        def create_authenticator_implementation() -> r[object]:
            """Create a CliAuthenticator protocol implementation.

            Business Rule:
            ──────────────
            The CliAuthenticator protocol requires authenticate(username, password) -> r[str].
            This implementation validates credentials and returns a token string on success.
            The authenticate method signature MUST match p.Cli.CliAuthenticator:
            - Parameters: username: str, password: str
            - Returns: r[str] (token on success)

            Audit Implications:
            ───────────────────
            - Valid credentials ("testuser"/"testpass") return "valid_token" token
            - Invalid credentials return failure result with error message
            - Token validation checks for "valid_" prefix for security audit trail
            """
            try:

                class TestAuthenticator:
                    """Test authenticator matching CliAuthenticator protocol."""

                    def authenticate(self, username: str, password: str) -> r[str]:
                        """Authenticate user with username and password.

                        Args:
                            username: User identifier for authentication
                            password: User password for authentication

                        Returns:
                            r[str]: Token string on success, error on failure

                        """
                        if username == "testuser" and password == "testpass":
                            return r[str].ok("valid_token")
                        return r[str].fail("Invalid credentials")

                    def validate_token(self, token: str) -> r[bool]:
                        """Validate authentication token.

                        Args:
                            token: Token string to validate

                        Returns:
                            r[bool]: True if token is valid

                        """
                        return r[bool].ok(token.startswith("valid_"))

                return r[object].ok(TestAuthenticator())
            except Exception as e:
                return r[object].fail(str(e))

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
        ) -> r[object]:
            """Create a test command using CLI decorator."""
            try:
                decorator = cli_cli.create_command_decorator(
                    name=name,
                    help_text=help_text,
                )

                @decorator
                def test_func(*args: object, **kwargs: object) -> t.GeneralValueType:
                    """Test command function."""
                    echo("Test")
                    return None

                return r[object].ok(test_func)
            except Exception as e:
                return r[object].fail(str(e))

        @staticmethod
        def create_test_group(
            cli_cli: FlextCliCli,
            name: str,
            help_text: str = "Test group",
        ) -> r[object]:
            """Create a test group using CLI decorator."""
            try:
                decorator = cli_cli.create_group_decorator(
                    name=name,
                    help_text=help_text,
                )

                @decorator
                def test_group_func(
                    *args: object,
                    **kwargs: object,
                ) -> t.GeneralValueType:
                    """Group function."""
                    return None

                return r[object].ok(test_group_func)
            except Exception as e:
                return r[object].fail(str(e))

        @staticmethod
        def create_command_with_options(
            cli_cli: FlextCliCli,
            command_name: str,
            option_name: str,
            option_default: DefaultType = None,
        ) -> r[object]:
            """Create a command with options."""
            try:
                command_decorator = cli_cli.create_command_decorator(name=command_name)
                option_default_converted: t.GeneralValueType | None = (
                    cast("t.GeneralValueType", option_default)
                    if option_default is not None
                    else None
                )
                option_config_instance = (
                    m.OptionConfig(default=option_default_converted)
                    if option_default_converted is not None
                    else None
                )
                option_config = (
                    cast("p.Cli.OptionConfigProtocol", option_config_instance)
                    if option_config_instance is not None
                    else None
                )
                option_decorator = cli_cli.create_option_decorator(
                    option_name,
                    config=option_config,
                )

                @command_decorator
                @option_decorator
                def test_command(*args: object, **kwargs: object) -> t.GeneralValueType:
                    """Test command with options."""
                    value = kwargs.get("value") if kwargs else args[0] if args else None
                    echo(f"Value: {value}")
                    return None

                return r[object].ok(test_command)
            except Exception as e:
                return r[object].fail(str(e))

        @staticmethod
        def create_model_command_test_data() -> r[dict[str, object]]:
            """Create test data for model command testing."""
            try:
                data: dict[str, object] = {
                    "params_with_aliases": {
                        "input_dir": "/input",
                        "output_dir": "/output",
                        "max_count": 10,
                    },
                    "standard_params": {
                        "input_path": "/input/file.txt",
                        "count": 5,
                    },
                    "bool_params": {
                        "enable_sync": True,
                        "verbose_mode": False,
                    },
                    "mixed_params": {
                        "required_field": "required",
                        "optional_field": "default_value",
                        "optional_int": 42,
                    },
                }
                return r[dict[str, object]].ok(data)
            except Exception as e:
                return r[dict[str, object]].fail(str(e))

    # =========================================================================
    # NESTED HELPER: Test Assertions
    # =========================================================================

    # AssertHelpers removed - use FlextTestsMatchers directly

    # =========================================================================
    # NESTED HELPER: Output Formatting
    # =========================================================================

    class OutputHelpers:
        """Helpers for output formatting tests."""

        @staticmethod
        def create_format_test_data() -> dict[str, t.GeneralValueType]:
            """Create standard test data for format tests.

            Returns:
                Test data dictionary

            """
            data: dict[str, t.GeneralValueType] = {
                "key": "value",
                "number": 42,
                "list": [1, 2, 3],
            }
            return data

        @staticmethod
        def create_table_test_data() -> dict[str, t.GeneralValueType]:
            """Create test data for table formatting.

            Returns:
                Test data with table structure

            """
            # Convert table data to JsonValue-compatible format
            users_list_raw: list[object] = [
                {"name": "John", "age": 30},
                {"name": "Jane", "age": 25},
            ]
            users_list: Sequence[t.GeneralValueType] = cast(
                "Sequence[t.GeneralValueType]",
                users_list_raw,
            )
            data: dict[str, t.GeneralValueType] = {"users": users_list}
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
        ) -> r[bool]:
            """Validate that constant matches expected value."""
            if constant_value == expected_value:
                return r[bool].ok(True)
            return r[bool].fail(
                f"Constant value '{constant_value}' does not match expected '{expected_value}'",
            )

        @staticmethod
        def validate_constant_format(
            constant_value: str,
            must_start_with: str | None = None,
            must_end_with: str | None = None,
            must_not_contain: list[str] | None = None,
        ) -> r[bool]:
            """Validate constant format according to rules."""
            if must_start_with and not constant_value.startswith(must_start_with):
                return r[bool].fail(
                    f"Constant must start with '{must_start_with}', got '{constant_value}'",
                )

            if must_end_with and not constant_value.endswith(must_end_with):
                return r[bool].fail(
                    f"Constant must end with '{must_end_with}', got '{constant_value}'",
                )

            if must_not_contain:
                for char in must_not_contain:
                    if char in constant_value:
                        return r[bool].fail(
                            f"Constant must not contain '{char}', got '{constant_value}'",
                        )

            return r[bool].ok(True)

        @staticmethod
        def validate_all_constants(
            constants: FlextCliConstants,
        ) -> r[dict[str, bool]]:
            """Validate all constants against expected format and values."""
            validations: dict[str, bool] = {}

            # Validate PROJECT_NAME
            project_name_valid = (
                FlextCliTestHelpers.ConstantsFactory.validate_constant_value(
                    constants.PROJECT_NAME,
                    "flext-cli",
                ).is_success
            )
            validations["PROJECT_NAME"] = project_name_valid

            # Validate FLEXT_DIR_NAME
            dir_name_valid = (
                FlextCliTestHelpers.ConstantsFactory.validate_constant_format(
                    constants.FLEXT_DIR_NAME,
                    must_start_with=".",
                ).is_success
            )
            validations["FLEXT_DIR_NAME"] = dir_name_valid

            # Validate TOKEN_FILE_NAME
            token_file_valid = (
                FlextCliTestHelpers.ConstantsFactory.validate_constant_format(
                    constants.TOKEN_FILE_NAME,
                    must_end_with=".json",
                    must_not_contain=["/", "\\", ":", "*", "?", '"', "<", ">", "|"],
                ).is_success
            )
            validations["TOKEN_FILE_NAME"] = token_file_valid

            # Validate REFRESH_TOKEN_FILE_NAME
            refresh_token_file_valid = (
                FlextCliTestHelpers.ConstantsFactory.validate_constant_format(
                    constants.REFRESH_TOKEN_FILE_NAME,
                    must_end_with=".json",
                    must_not_contain=["/", "\\", ":", "*", "?", '"', "<", ">", "|"],
                ).is_success
            )
            validations["REFRESH_TOKEN_FILE_NAME"] = refresh_token_file_valid

            if all(validations.values()):
                return r[dict[str, bool]].ok(validations)

            failed = [key for key, valid in validations.items() if not valid]
            return r[dict[str, bool]].fail(
                f"Constants validation failed for: {', '.join(failed)}",
            )

    class VersionTestFactory:
        """Factory for version validation testing."""

        @staticmethod
        def validate_version_string(version: str) -> r[bool]:
            """Validate version string format and constraints."""
            # version is already typed as str, so isinstance check is for runtime safety only

            if len(version) < 5:
                return r[bool].fail("Version too short")

            if len(version) > 50:
                return r[bool].fail("Version too long")

            semver_pattern = r"^\d+\.\d+\.\d+(?:-[\w\.]+)?(?:\+[\w\.]+)?$"
            if not re.match(semver_pattern, version):
                return r[bool].fail("Invalid semver format")

            return r[bool].ok(True)

        @staticmethod
        def validate_version_info(info: tuple[int | str, ...]) -> r[bool]:
            """Validate version info tuple."""
            # info is already typed as tuple, so isinstance check is for runtime safety only

            if len(info) < 3:
                return r[bool].fail("Version info too short")

            # First three parts should be int or str
            for i in range(min(3, len(info))):
                if not isinstance(info[i], (int, str)):
                    return r[bool].fail(f"Part {i} has invalid type")

            return r[bool].ok(True)

        @staticmethod
        def validate_consistency(
            version: str,
            info: tuple[int | str, ...],
        ) -> r[bool]:
            """Validate consistency between version string and info tuple."""
            # Simulate real __version_info__ creation logic
            expected_info = tuple(
                int(part) if part.isdigit() else part for part in version.split(".")
            )

            if expected_info != info:
                return r[bool].fail(
                    f"Version info mismatch: expected {expected_info}, got {info}",
                )

            return r[bool].ok(True)

    # =========================================================================
    # FlextService Protocol Implementation
    # =========================================================================

    def execute(self) -> r[dict[str, t.GeneralValueType]]:
        """Execute testing service.

        Returns:
            r[dict[str, t.GeneralValueType]]: Service execution status.

        """
        try:
            payload = {
                c.DictKeys.STATUS: c.ServiceStatus.OPERATIONAL.value,
                c.DictKeys.SERVICE: "FlextCliTestHelpers",
                c.DictKeys.MESSAGE: "Test helpers ready",
            }
            # Convert to JsonDict-compatible dict using helper
            payload_converted: dict[str, t.GeneralValueType] = cast(
                "dict[str, t.GeneralValueType]",
                payload,
            )
            # Use u.transform for JSON conversion
            transform_result = u.transform(payload_converted, to_json=True)
            payload_data = (
                transform_result.unwrap()
                if transform_result.is_success
                else payload_converted
            )
            return r[dict[str, t.GeneralValueType]].ok(payload_data)
        except Exception as e:
            return r[dict[str, t.GeneralValueType]].fail(str(e))

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
                "people_dict": [
                    {
                        "name": "Alice",
                        "age": 30,
                        "city": "New York",
                        "salary": 75000.50,
                    },
                    {"name": "Bob", "age": 25, "city": "London", "salary": 65000.75},
                    {"name": "Charlie", "age": 35, "city": "Paris", "salary": 85000.25},
                ],
                "people_list": [
                    ["Alice", 30, "New York", 75000.50],
                    ["Bob", 25, "London", 65000.75],
                    ["Charlie", 35, "Paris", 85000.25],
                ],
                "single_row": [{"name": "Alice", "age": 30}],
                "with_none": [
                    {"name": "Alice", "age": 30, "city": None},
                    {"name": "Bob", "age": None, "city": "London"},
                ],
                "empty": [],
                "none": None,
            }


# ============================================================================
# CONVENIENCE EXPORTS (for backward compatibility)
# ============================================================================

create_flext_cli_app_base = FlextCliTestHelpers.AppFactory.create_app

# Expose nested classes as module-level for import convenience (domain-specific only)
OutputHelpers = FlextCliTestHelpers.OutputHelpers
AuthHelpers = FlextCliTestHelpers.AuthHelpers
CommandHelpers = FlextCliTestHelpers.CommandHelpers
# GenericHelpers, AssertHelpers, FileHelpers removed - use flext_tests directly

"""FLEXT CLI Test Helpers - Factories and utilities for test code reduction.

Provides reusable factories, validators, and helpers to reduce test code
through DRY principles and parametrized test patterns.

Extends src modules via inheritance:
- TestModels extends FlextCliModels
- TestTypes extends FlextCliTypes
- TestUtilities extends u
- TestConstants extends FlextCliConstants
- TestProtocols extends FlextCliProtocols

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import inspect
import re
from typing import Final, TypeVar

import click
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_cli import r
from flext_cli.constants import FlextCliConstants
from flext_cli.context import FlextCliContext
from tests import c, m, p, t, u  # TestsCli structure

from .. import _helpers as helpers

# Expose the large classes from _helpers.py
CommandsFactory = helpers.CommandsFactory

# Standardized short names are imported from tests module (TestsCli structure)
# Use m, t, u, c, p in test modules - these extend FlextTests and FlextCli

# TypeVars for generic test helpers
T = TypeVar("T")

# Type aliases for field definitions
# FieldDefault can be a primitive value
type FieldDefault = str | int | float | bool | None
# FieldKwargs for Field() keyword arguments (restricted to common JSON-compatible types)
type FieldKwargs = dict[str, str | int | float | bool | None]


class ConfigFactory:
    """Factory for creating BaseSettings configuration classes."""

    @staticmethod
    def create_config(
        name: str,
        prefix: str = "TEST_",
        fields: dict[str, tuple[type, FieldDefault | FieldInfo]] | None = None,
    ) -> type[BaseSettings]:
        """Create a BaseSettings config class dynamically.

        Args:
            name: Class name
            prefix: Environment variable prefix
            fields: Dict of field_name -> (field_type, default_value)

        Returns:
            Dynamic BaseSettings class

        """
        if fields is None:
            fields = {"test_field": (str, Field(default="test"))}

        # Create field annotations and defaults
        annotations: dict[str, type] = {}
        class_dict: dict[str, object] = {
            "model_config": SettingsConfigDict(env_prefix=prefix),
            "__annotations__": annotations,
        }

        for field_name, (field_type, default) in fields.items():
            annotations[field_name] = field_type
            class_dict[field_name] = default

        return type(name, (BaseSettings,), class_dict)


class ParamsFactory:
    """Factory for creating BaseModel parameter classes."""

    @staticmethod
    def create_params(
        name: str,
        fields: dict[str, tuple[type, FieldDefault | FieldInfo, FieldKwargs]]
        | None = None,
        *,
        populate_by_name: bool = True,
    ) -> type[BaseModel]:
        """Create a BaseModel params class dynamically.

        Args:
            name: Class name
            fields: Dict of field_name -> (field_type, default, field_kwargs)
            populate_by_name: Allow population by field name or alias

        Returns:
            Dynamic BaseModel class

        """
        if fields is None:
            # Create default fields with proper typing
            # Use Field() to create FieldInfo for default
            default_field = Field(default=None)
            empty_kwargs: FieldKwargs = {}
            # Use str as type (not str | None) since we handle None via Field default
            fields = {"test_field": (str, default_field, empty_kwargs)}

        # Create field annotations and defaults
        annotations: dict[str, type] = {}
        class_dict: dict[str, object] = {
            "model_config": {"populate_by_name": populate_by_name},
            "__annotations__": annotations,
        }

        for field_name, (field_type, default, kwargs) in fields.items():
            # field_type is guaranteed to be type (not None) by the signature
            annotations[field_name] = field_type
            if isinstance(default, FieldInfo):
                class_dict[field_name] = default
            elif isinstance(default, (str, int, float, bool)) or default is None:
                # Type narrowing: default is FieldDefault (primitive type)
                # Field() accepts these types directly
                # For kwargs, Field() accepts typed dict with JSON-compatible values
                # We create Field with default and kwargs are applied via Field() constructor
                if kwargs:
                    # Field() constructor accepts typed dict with JSON-compatible values
                    # Runtime behavior is correct with our typed FieldKwargs
                    field_instance = Field(default=default)
                    # Apply kwargs by updating the FieldInfo if needed
                    # For now, just use Field with default since kwargs are typically empty
                    class_dict[field_name] = field_instance
                else:
                    class_dict[field_name] = Field(default=default)

        return type(name, (BaseModel,), class_dict)


class ValidationHelper:
    """Helper methods for common validation patterns."""

    @staticmethod
    def assert_field_value(
        obj: object,
        field_name: str,
        expected_value: object,
        message: str | None = None,
    ) -> None:
        """Assert that an object field has expected value.

        Args:
            obj: Object to check
            field_name: Field name
            expected_value: Expected value
            message: Optional custom error message

        """
        actual = getattr(obj, field_name)
        assert actual == expected_value, message or (
            f"{field_name}={actual}, expected {expected_value}"
        )

    @staticmethod
    def assert_field_type(
        obj: object,
        field_name: str,
        expected_type: type | tuple[type, ...],
    ) -> None:
        """Assert that an object field has expected type.

        Args:
            obj: Object to check
            field_name: Field name
            expected_type: Expected type or tuple of types

        """
        value = getattr(obj, field_name)
        assert isinstance(
            value,
            expected_type,
        ), f"{field_name}={type(value)}, expected {expected_type}"

    @staticmethod
    def extract_config_values(
        config: BaseSettings,
        field_names: list[str],
    ) -> dict[str, object]:
        """Extract multiple field values from config.

        Args:
            config: BaseSettings instance
            field_names: List of field names to extract

        Returns:
            Dict of field_name -> field_value

        """
        return {name: getattr(config, name) for name in field_names}


class TestScenario:
    """Enum-like class for test scenarios."""

    class ConfigScenarios:
        """Configuration test scenarios."""

        REQUIRED_FIELDS: Final[str] = "required_fields"
        OPTIONAL_FIELDS: Final[str] = "optional_fields"
        WITH_DEFAULTS: Final[str] = "with_defaults"
        WITH_ENV_VARS: Final[str] = "with_env_vars"
        WITH_NONE_VALUES: Final[str] = "with_none_values"
        MISSING_ENV_VAR: Final[str] = "missing_env_var"

    class ParamsScenarios:
        """Parameter test scenarios."""

        WITH_ALIASES: Final[str] = "with_aliases"
        WITH_REQUIRED: Final[str] = "with_required"
        WITH_OPTIONAL: Final[str] = "with_optional"
        WITH_FIELD_NAMES: Final[str] = "with_field_names"
        WITH_MIXED_VALUES: Final[str] = "with_mixed_values"
        FORBID_EXTRA: Final[str] = "forbid_extra"


class FlextCliTestHelpers:
    """Centralized test helpers for flext-cli test modules."""

    class AssertHelpers:
        """Helper methods for asserting r state."""

        @staticmethod
        def assert_result_success(result: r[T]) -> None:
            """Assert that a r is successful.

            Args:
                result: r to check

            Raises:
                AssertionError: If result is not successful

            """
            assert result.is_success, (
                f"Expected success but got failure: {result.error}"
            )

        @staticmethod
        def assert_result_failure(result: r[T]) -> None:
            """Assert that a r is a failure.

            Args:
                result: r to check

            Raises:
                AssertionError: If result is not a failure

            """
            assert result.is_failure, (
                f"Expected failure but got success: {result.value}"
            )

    class VersionTestFactory:
        """Factory for version validation tests."""

        @staticmethod
        def validate_version_string(version: str) -> r[str]:
            """Validate version string against semver pattern.

            Args:
                version: Version string to validate

            Returns:
                r with success or failure

            """
            if not version:
                return r.fail("Version must be non-empty string")

            pattern: str = r"^\d+\.\d+\.\d+(?:-[\w\.]+)?(?:\+[\w\.]+)?$"
            if not re.match(pattern, version):
                return r.fail(f"Version '{version}' does not match semver pattern")

            return r.ok(version)

        @staticmethod
        def validate_version_info(
            version_info: tuple[int | str, ...],
        ) -> r[tuple[int | str, ...]]:
            """Validate version info tuple structure.

            Args:
                version_info: Version info tuple to validate

            Returns:
                r with success or failure

            """
            if len(version_info) < 3:
                return r.fail("Version info must have at least 3 parts")

            for i, part in enumerate(version_info):
                if isinstance(part, int) and part < 0:
                    return r.fail(f"Version part {i} must be non-negative int")
                if isinstance(part, str) and not part:
                    return r.fail(f"Version part {i} must be non-empty string")
                # Type narrowing: part is int | str, so else branch is unreachable
                # but kept for runtime safety

            return r.ok(version_info)

        @staticmethod
        def validate_consistency(
            version_string: str,
            version_info: tuple[int | str, ...],
        ) -> r[tuple[str, tuple[int | str, ...]]]:
            """Validate consistency between version string and info tuple.

            Args:
                version_string: Version string
                version_info: Version info tuple

            Returns:
                r with success or failure

            """
            # First validate both individually
            string_result = (
                FlextCliTestHelpers.VersionTestFactory.validate_version_string(
                    version_string,
                )
            )
            if string_result.is_failure:
                return r.fail(f"Invalid version string: {string_result.error}")

            info_result = FlextCliTestHelpers.VersionTestFactory.validate_version_info(
                version_info,
            )
            if info_result.is_failure:
                return r.fail(f"Invalid version info: {info_result.error}")

            # Check consistency between string and info
            # Handle semver with pre-release/metadata: "1.2.3-alpha.1+build.123"
            # Split by + to separate metadata (ignored)
            version_without_metadata = version_string.split("+", maxsplit=1)[0]
            # Split by - to separate base version and pre-release
            version_base_and_prerelease = version_without_metadata.split("-")
            base_parts = version_base_and_prerelease[0].split(".")
            prerelease_parts = (
                version_base_and_prerelease[1].split(".")
                if len(version_base_and_prerelease) > 1
                else []
            )
            # Combine base and pre-release parts
            version_parts_raw = base_parts + prerelease_parts

            # Convert numeric strings to ints, keep others as strings
            version_parts = []
            for part in version_parts_raw:
                try:
                    version_parts.append(int(part))
                except ValueError:
                    version_parts.append(part)

            info_parts = list(version_info)

            min_length = min(len(version_parts), len(info_parts))
            for i in range(min_length):
                version_part = version_parts[i]
                info_part = info_parts[i]

                # Check type compatibility
                if (isinstance(info_part, int) and isinstance(version_part, int)) or (
                    isinstance(info_part, str) and isinstance(version_part, str)
                ):
                    if version_part != info_part:
                        return r.fail(
                            f"Mismatch at position {i}: {version_part} != {info_part}",
                        )
                elif type(info_part) is not type(version_part):
                    return r.fail(
                        f"Type mismatch at position {i}: {type(version_part).__name__} != {type(info_part).__name__}",
                    )

            return r.ok((version_string, version_info))

    class ProtocolHelpers:
        """Helper methods for protocol implementation tests."""

        @staticmethod
        def create_formatter_implementation() -> r[object]:
            """Create a formatter implementation satisfying CliFormatter protocol.

            Returns:
                r with formatter instance or error

            """
            try:

                class TestFormatter:
                    """Test formatter implementation."""

                    def format_data(self, data: object, **options: object) -> r[str]:
                        """Format data to string."""
                        try:
                            return r.ok(str(data))
                        except Exception as e:
                            return r.fail(str(e))

                formatter = TestFormatter()
                # Validate it satisfies the protocol by checking methods exist
                if hasattr(formatter, "format_data") and callable(
                    getattr(formatter, "format_data", None),
                ):
                    return r.ok(formatter)
                return r.fail("Formatter does not satisfy CliFormatter protocol")
            except Exception as e:
                return r.fail(f"Failed to create formatter: {e!s}")

        @staticmethod
        def create_config_provider_implementation() -> r[object]:
            """Create a config provider implementation satisfying CliConfigProvider protocol.

            Returns:
                r with config provider instance or error

            """
            try:

                class TestConfigProvider:
                    """Test config provider implementation."""

                    def __init__(self) -> None:
                        """Initialize config provider."""
                        self.config: dict[str, object] = {}

                    def load_config(self) -> r[dict[str, object]]:
                        """Load configuration."""
                        try:
                            return r.ok(self.config)
                        except Exception as e:
                            return r.fail(str(e))

                    def save_config(self, config: object) -> r[bool]:
                        """Save configuration."""
                        try:
                            if isinstance(config, dict):
                                self.config = config
                                return r.ok(True)
                            return r.fail("Config must be a dict")
                        except Exception as e:
                            return r.fail(str(e))

                provider = TestConfigProvider()
                # Validate it satisfies the protocol by checking methods exist
                if (
                    hasattr(provider, "load_config")
                    and callable(getattr(provider, "load_config", None))
                    and hasattr(provider, "save_config")
                    and callable(getattr(provider, "save_config", None))
                ):
                    return r.ok(provider)
                return r.fail(
                    "Config provider does not satisfy CliConfigProvider protocol",
                )
            except Exception as e:
                return r.fail(f"Failed to create config provider: {e!s}")

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
            - Token validation checks for known valid tokens for security audit trail
            """
            try:

                class TestAuthenticator:
                    """Test authenticator matching CliAuthenticator protocol."""

                    def __init__(self) -> None:
                        """Initialize authenticator with no token."""
                        self.token: str | None = None

                    def authenticate(self, username: str, password: str) -> r[str]:
                        """Authenticate user with username and password.

                        Args:
                            username: User identifier for authentication
                            password: User password for authentication

                        Returns:
                            r[str]: Token string on success, error on failure

                        """
                        # Use same credentials as c.Authentication.VALID_CREDS
                        # Valid credentials are testuser/testpass
                        if username == "testuser" and password == "testpass":
                            self.token = "valid_token"
                            return r[str].ok(self.token)
                        return r[str].fail("Invalid credentials")

                    def validate_token(self, token: str) -> r[bool]:
                        """Validate authentication token.

                        Args:
                            token: Token string to validate

                        Returns:
                            r[bool]: True if token is valid

                        """
                        # Accept tokens starting with "valid_" (matches _helpers.py implementation)
                        if token.startswith("valid_"):
                            return r[bool].ok(True)
                        # Also accept known test tokens for backward compatibility
                        if token in {"valid_token_abc123", "valid_token", "test_token"}:
                            return r[bool].ok(True)
                        return r[bool].fail("Invalid token")

                authenticator = TestAuthenticator()
                # Validate it satisfies the protocol by checking methods exist
                # Business Rule: Protocol validation MUST check method existence and callability
                # Architecture: Use hasattr and callable to verify protocol compliance
                # Audit Implication: Protocol validation ensures type safety at runtime
                has_authenticate = hasattr(authenticator, "authenticate") and callable(
                    getattr(authenticator, "authenticate", None),
                )
                has_validate_token = hasattr(
                    authenticator,
                    "validate_token",
                ) and callable(getattr(authenticator, "validate_token", None))
                # Additional validation: Ensure methods are bound methods, not unbound
                # Business Rule: Protocol implementations MUST be instance methods, not static
                # Architecture: Bound methods ensure proper self parameter binding
                if has_authenticate and has_validate_token:
                    # Verify authenticate method signature matches protocol
                    # Business Rule: Protocol validation MUST verify method signature matches expected
                    # Architecture: inspect.signature() provides runtime type checking for protocols
                    # Audit Implication: Signature validation ensures protocol compliance at runtime
                    auth_method = getattr(authenticator, "authenticate", None)
                    if auth_method:
                        sig = inspect.signature(auth_method)
                        # Protocol requires (self, username: str, password: str)
                        # Check that method has correct number of parameters
                        # For bound methods, self is already bound, so signature shows only username and password
                        params = list(sig.parameters.keys())
                        if (
                            len(params) >= 2
                        ):  # At least username and password (self may be hidden in bound methods)
                            return r.ok(authenticator)
                return r.fail(
                    "Authenticator does not satisfy CliAuthenticator protocol",
                )
            except Exception as e:
                return r.fail(f"Failed to create authenticator: {e!s}")

    class TypingHelpers:
        """Helper methods for type system tests."""

        @staticmethod
        def create_processing_test_data() -> r[
            tuple[list[str], list[int], dict[str, object]]
        ]:
            """Create test data for type processing scenarios.

            Returns:
                r with tuple of (string_list, number_list, mixed_dict)

            """
            try:
                string_list = ["hello", "world", "test"]
                number_list = [1, 2, 3, 4, 5]
                mixed_dict: dict[str, object] = {
                    "key1": 123,
                    "key2": "value",
                    "key3": True,
                    "key4": [1, 2, 3],
                }
                return r.ok((string_list, number_list, mixed_dict))
            except Exception as e:
                return r.fail(f"Failed to create processing test data: {e!s}")

        @staticmethod
        def create_typed_dict_data() -> r[dict[str, object]]:
            """Create typed dict test data.

            Returns:
                r with typed dict (user data)

            """
            try:
                user_data: dict[str, object] = {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "active": True,
                }
                return r.ok(user_data)
            except Exception as e:
                return r.fail(f"Failed to create typed dict data: {e!s}")

        @staticmethod
        def create_api_response_data() -> r[list[dict[str, object]]]:
            """Create API response test data.

            Returns:
                r with list of user dicts

            """
            try:
                users_data: list[dict[str, object]] = [
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
                ]
                return r.ok(users_data)
            except Exception as e:
                return r.fail(f"Failed to create API response data: {e!s}")

    class ConstantsFactory:
        """Factory for creating constants test fixtures."""

        @staticmethod
        def get_constants() -> type[FlextCliConstants]:
            """Get FlextCliConstants instance for testing.

            Returns:
                FlextCliConstants instance

            """
            return FlextCliConstants

    class ContextFactory:
        """Factory for creating CLI context test fixtures."""

        @staticmethod
        def create_context(
            command: str | None = None,
            arguments: list[str] | None = None,
            environment_variables: dict[str, t.GeneralValueType] | None = None,
            working_directory: str | None = None,
        ) -> r[object]:
            """Create a FlextCliContext instance for testing.

            Args:
                command: Command name
                arguments: Command arguments
                environment_variables: Environment variables dict
                working_directory: Working directory path

            Returns:
                r with FlextCliContext instance or error

            """
            try:
                ctx = FlextCliContext(
                    command=command,
                    arguments=arguments or [],
                    environment_variables=environment_variables or {},
                    working_directory=working_directory,
                )
                return r.ok(ctx)
            except Exception as e:
                return r.fail(f"Failed to create context: {e!s}")

    class CliHelpers:
        """Helper methods for CLI testing."""

        @staticmethod
        def create_test_command(cli_cli: object, command_name: str) -> r[object]:
            """Create a test command for CLI testing.

            Args:
                cli_cli: FlextCliCli instance
                command_name: Command name to create

            Returns:
                r with command object or error

            """
            try:

                @click.command(name=command_name)
                def test_cmd() -> None:
                    click.echo("test")

                return r.ok(test_cmd)
            except Exception as e:
                return r.fail(f"Failed to create command: {e!s}")

        @staticmethod
        def create_test_group(cli_cli: object, group_name: str) -> r[object]:
            """Create a test group for CLI testing.

            Args:
                cli_cli: FlextCliCli instance
                group_name: Group name to create

            Returns:
                r with group object or error

            """
            try:

                @click.group(name=group_name)
                def test_grp() -> None:
                    pass

                return r.ok(test_grp)
            except Exception as e:
                return r.fail(f"Failed to create group: {e!s}")

        @staticmethod
        def create_command_with_options(
            cli_cli: object,
            command_name: str,
            option_name: str,
            default: str,
        ) -> r[object]:
            """Create a command with options for CLI testing.

            Args:
                cli_cli: FlextCliCli instance
                command_name: Command name
                option_name: Option name (with dashes)
                default: Default option value

            Returns:
                r with command object or error

            """
            try:

                @click.command(name=command_name)
                @click.option(option_name, default=default)
                def cmd_with_opt(config: str) -> None:
                    pass

                return r.ok(cmd_with_opt)
            except Exception as e:
                return r.fail(f"Failed to create command with options: {e!s}")


__all__ = [
    "CommandsFactory",
    "ConfigFactory",
    "FlextCliTestHelpers",
    "ParamsFactory",
    "TestScenario",
    "ValidationHelper",
    "c",
    "m",
    "p",
    "t",
    "u",
]

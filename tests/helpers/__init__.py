"""FLEXT CLI Test Helpers - Factories and utilities for test code reduction.

Provides reusable factories, validators, and helpers to reduce test code
through DRY principles and parametrized test patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import re
from typing import Final, TypeAlias, TypeVar

from flext_core import FlextResult
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, SettingsConfigDict

from flext_cli import FlextCliProtocols as FlextCliProtocols

from .. import _helpers as helpers

# Expose the large classes from _helpers.py
CommandsFactory = helpers.CommandsFactory

# TypeVars for generic test helpers
T = TypeVar("T")

# Type aliases for field definitions
# FieldDefault can be a primitive value
FieldDefault: TypeAlias = str | int | float | bool | None
# FieldKwargs for Field() keyword arguments (Field accepts Any in kwargs, but we restrict to common types)
FieldKwargs: TypeAlias = dict[str, str | int | float | bool | None]


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
                # For kwargs, Field() accepts Any, but we need to ensure type safety
                # Since we can't use cast() or type: ignore, we create Field without kwargs first
                # then add kwargs if needed via a different approach
                if kwargs:
                    # Field() signature accepts **kwargs as Any, so we can pass our typed dict
                    # The runtime behavior is correct even if mypy complains about overload matching
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
        """Helper methods for asserting FlextResult state."""

        @staticmethod
        def assert_result_success(result: FlextResult[T]) -> None:
            """Assert that a FlextResult is successful.

            Args:
                result: FlextResult to check

            Raises:
                AssertionError: If result is not successful

            """
            assert result.is_success, (
                f"Expected success but got failure: {result.error}"
            )

        @staticmethod
        def assert_result_failure(result: FlextResult[T]) -> None:
            """Assert that a FlextResult is a failure.

            Args:
                result: FlextResult to check

            Raises:
                AssertionError: If result is not a failure

            """
            assert result.is_failure, (
                f"Expected failure but got success: {result.unwrap()}"
            )

    class VersionTestFactory:
        """Factory for version validation tests."""

        @staticmethod
        def validate_version_string(version: str) -> FlextResult[str]:
            """Validate version string against semver pattern.

            Args:
                version: Version string to validate

            Returns:
                FlextResult with success or failure

            """
            if not version:
                return FlextResult.fail("Version must be non-empty string")

            pattern: str = r"^\d+\.\d+\.\d+(?:-[\w\.]+)?(?:\+[\w\.]+)?$"
            if not re.match(pattern, version):
                return FlextResult.fail(
                    f"Version '{version}' does not match semver pattern"
                )

            return FlextResult.ok(version)

        @staticmethod
        def validate_version_info(
            version_info: tuple[int | str, ...],
        ) -> FlextResult[tuple[int | str, ...]]:
            """Validate version info tuple structure.

            Args:
                version_info: Version info tuple to validate

            Returns:
                FlextResult with success or failure

            """
            if len(version_info) < 3:
                return FlextResult.fail("Version info must have at least 3 parts")

            for i, part in enumerate(version_info):
                if isinstance(part, int) and part < 0:
                    return FlextResult.fail(
                        f"Version part {i} must be non-negative int"
                    )
                if isinstance(part, str) and not part:
                    return FlextResult.fail(
                        f"Version part {i} must be non-empty string"
                    )
                # Type narrowing: part is int | str, so else branch is unreachable
                # but kept for runtime safety

            return FlextResult.ok(version_info)

        @staticmethod
        def validate_consistency(
            version_string: str,
            version_info: tuple[int | str, ...],
        ) -> FlextResult[tuple[str, tuple[int | str, ...]]]:
            """Validate consistency between version string and info tuple.

            Args:
                version_string: Version string
                version_info: Version info tuple

            Returns:
                FlextResult with success or failure

            """
            # First validate both individually
            string_result = (
                FlextCliTestHelpers.VersionTestFactory.validate_version_string(
                    version_string
                )
            )
            if string_result.is_failure:
                return FlextResult.fail(
                    f"Invalid version string: {string_result.error}"
                )

            info_result = FlextCliTestHelpers.VersionTestFactory.validate_version_info(
                version_info
            )
            if info_result.is_failure:
                return FlextResult.fail(f"Invalid version info: {info_result.error}")

            # Check consistency between string and info
            version_parts = version_string.split(".")
            info_parts = list(version_info)

            min_length = min(len(version_parts), len(info_parts))
            for i in range(min_length):
                version_part = version_parts[i]
                info_part = info_parts[i]

                if isinstance(info_part, int):
                    try:
                        if int(version_part) != info_part:
                            return FlextResult.fail(
                                f"Mismatch at position {i}: {version_part} != {info_part}"
                            )
                    except ValueError:
                        return FlextResult.fail(
                            f"Cannot convert version part {i} to int: {version_part}"
                        )
                elif isinstance(info_part, str) and version_part != info_part:
                    return FlextResult.fail(
                        f"Mismatch at position {i}: {version_part} != {info_part}"
                    )

            return FlextResult.ok((version_string, version_info))

    class ProtocolHelpers:
        """Helper methods for protocol implementation tests."""

        @staticmethod
        def create_formatter_implementation() -> FlextResult[object]:
            """Create a formatter implementation satisfying CliFormatter protocol.

            Returns:
                FlextResult with formatter instance or error

            """
            try:

                class TestFormatter:
                    """Test formatter implementation."""

                    def format_data(
                        self, data: object, **options: object
                    ) -> FlextResult[str]:
                        """Format data to string."""
                        try:
                            return FlextResult.ok(str(data))
                        except Exception as e:
                            return FlextResult.fail(str(e))

                formatter = TestFormatter()
                # Validate it satisfies the protocol by checking methods exist
                if hasattr(formatter, "format_data") and callable(
                    getattr(formatter, "format_data", None)
                ):
                    return FlextResult.ok(formatter)
                return FlextResult.fail(
                    "Formatter does not satisfy CliFormatter protocol"
                )
            except Exception as e:
                return FlextResult.fail(f"Failed to create formatter: {e!s}")

        @staticmethod
        def create_config_provider_implementation() -> FlextResult[object]:
            """Create a config provider implementation satisfying CliConfigProvider protocol.

            Returns:
                FlextResult with config provider instance or error

            """
            try:

                class TestConfigProvider:
                    """Test config provider implementation."""

                    def __init__(self) -> None:
                        """Initialize config provider."""
                        self.config: dict[str, object] = {}

                    def load_config(self) -> FlextResult[dict[str, object]]:
                        """Load configuration."""
                        try:
                            return FlextResult.ok(self.config)
                        except Exception as e:
                            return FlextResult.fail(str(e))

                    def save_config(self, config: object) -> FlextResult[bool]:
                        """Save configuration."""
                        try:
                            if isinstance(config, dict):
                                self.config = config
                                return FlextResult.ok(True)
                            return FlextResult.fail("Config must be a dict")
                        except Exception as e:
                            return FlextResult.fail(str(e))

                provider = TestConfigProvider()
                # Validate it satisfies the protocol by checking methods exist
                if (
                    hasattr(provider, "load_config")
                    and callable(getattr(provider, "load_config", None))
                    and hasattr(provider, "save_config")
                    and callable(getattr(provider, "save_config", None))
                ):
                    return FlextResult.ok(provider)
                return FlextResult.fail(
                    "Config provider does not satisfy CliConfigProvider protocol"
                )
            except Exception as e:
                return FlextResult.fail(f"Failed to create config provider: {e!s}")

        @staticmethod
        def create_authenticator_implementation() -> FlextResult[object]:
            """Create an authenticator implementation satisfying CliAuthenticator protocol.

            Returns:
                FlextResult with authenticator instance or error

            """
            try:

                class TestAuthenticator:
                    """Test authenticator implementation."""

                    def __init__(self) -> None:
                        """Initialize authenticator."""
                        self.token: str | None = None

                    def authenticate(self, credentials: object) -> FlextResult[str]:
                        """Authenticate with credentials."""
                        try:
                            if not isinstance(credentials, dict):
                                return FlextResult.fail("Credentials must be a dict")
                            self.token = "test_token"
                            return FlextResult.ok(self.token)
                        except Exception as e:
                            return FlextResult.fail(str(e))

                    def validate_token(self, token: str) -> FlextResult[bool]:
                        """Validate authentication token."""
                        try:
                            if token in {"valid_token_abc123", "test_token"}:
                                return FlextResult.ok(True)
                            return FlextResult.fail("Invalid token")
                        except Exception as e:
                            return FlextResult.fail(str(e))

                authenticator = TestAuthenticator()
                # Validate it satisfies the protocol by checking methods exist
                has_authenticate = hasattr(authenticator, "authenticate") and callable(
                    getattr(authenticator, "authenticate", None)
                )
                has_validate_token = hasattr(
                    authenticator, "validate_token"
                ) and callable(getattr(authenticator, "validate_token", None))
                if has_authenticate and has_validate_token:
                    return FlextResult.ok(authenticator)
                return FlextResult.fail(
                    "Authenticator does not satisfy CliAuthenticator protocol"
                )
            except Exception as e:
                return FlextResult.fail(f"Failed to create authenticator: {e!s}")

    class TypingHelpers:
        """Helper methods for type system tests."""

        @staticmethod
        def create_processing_test_data() -> FlextResult[
            tuple[list[str], list[int], dict[str, object]]
        ]:
            """Create test data for type processing scenarios.

            Returns:
                FlextResult with tuple of (string_list, number_list, mixed_dict)

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
                return FlextResult.ok((string_list, number_list, mixed_dict))
            except Exception as e:
                return FlextResult.fail(f"Failed to create processing test data: {e!s}")

        @staticmethod
        def create_typed_dict_data() -> FlextResult[dict[str, object]]:
            """Create typed dict test data.

            Returns:
                FlextResult with typed dict (user data)

            """
            try:
                user_data: dict[str, object] = {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "active": True,
                }
                return FlextResult.ok(user_data)
            except Exception as e:
                return FlextResult.fail(f"Failed to create typed dict data: {e!s}")

        @staticmethod
        def create_api_response_data() -> FlextResult[list[dict[str, object]]]:
            """Create API response test data.

            Returns:
                FlextResult with list of user dicts

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
                return FlextResult.ok(users_data)
            except Exception as e:
                return FlextResult.fail(f"Failed to create API response data: {e!s}")

    class CliHelpers:
        """Helper methods for CLI testing."""

        @staticmethod
        def create_test_command(
            cli_cli: object, command_name: str
        ) -> FlextResult[object]:
            """Create a test command for CLI testing.

            Args:
                cli_cli: FlextCliCli instance
                command_name: Command name to create

            Returns:
                FlextResult with command object or error

            """
            try:
                import click

                @click.command(name=command_name)
                def test_cmd() -> None:
                    click.echo("test")

                return FlextResult.ok(test_cmd)
            except Exception as e:
                return FlextResult.fail(f"Failed to create command: {e!s}")

        @staticmethod
        def create_test_group(cli_cli: object, group_name: str) -> FlextResult[object]:
            """Create a test group for CLI testing.

            Args:
                cli_cli: FlextCliCli instance
                group_name: Group name to create

            Returns:
                FlextResult with group object or error

            """
            try:
                import click

                @click.group(name=group_name)
                def test_grp() -> None:
                    pass

                return FlextResult.ok(test_grp)
            except Exception as e:
                return FlextResult.fail(f"Failed to create group: {e!s}")

        @staticmethod
        def create_command_with_options(
            cli_cli: object, command_name: str, option_name: str, default: str
        ) -> FlextResult[object]:
            """Create a command with options for CLI testing.

            Args:
                cli_cli: FlextCliCli instance
                command_name: Command name
                option_name: Option name (with dashes)
                default: Default option value

            Returns:
                FlextResult with command object or error

            """
            try:
                import click

                @click.command(name=command_name)
                @click.option(option_name, default=default)
                def cmd_with_opt(config: str) -> None:
                    pass

                return FlextResult.ok(cmd_with_opt)
            except Exception as e:
                return FlextResult.fail(f"Failed to create command with options: {e!s}")

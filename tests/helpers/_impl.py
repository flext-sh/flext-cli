"""Implementation of test helpers - factories, validation, scenarios.

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
from tests import t

T = TypeVar("T")
type FieldDefault = str | int | float | bool | None
type FieldKwargs = dict[str, str | int | float | bool | None]


class ConfigFactory:
    """Factory for creating BaseSettings configuration classes."""

    @staticmethod
    def create_config(
        name: str,
        prefix: str = "TEST_",
        fields: dict[str, tuple[type, FieldDefault | FieldInfo]] | None = None,
    ) -> type[BaseSettings]:
        """Create a BaseSettings config class dynamically."""
        if fields is None:
            fields = {"test_field": (str, Field(default="test"))}

        annotations: dict[str, type] = {}
        class_dict: dict[str, t.GeneralValueType] = {
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
        """Create a BaseModel params class dynamically."""
        if fields is None:
            default_field = Field(default=None)
            empty_kwargs: FieldKwargs = {}
            fields = {"test_field": (str, default_field, empty_kwargs)}

        annotations: dict[str, type] = {}
        class_dict: dict[str, t.GeneralValueType] = {
            "model_config": {"populate_by_name": populate_by_name},
            "__annotations__": annotations,
        }

        for field_name, (field_type, default, kwargs) in fields.items():
            annotations[field_name] = field_type
            if isinstance(default, FieldInfo):
                class_dict[field_name] = default
            elif isinstance(default, (str, int, float, bool)) or default is None:
                if kwargs:
                    field_instance = Field(default=default)
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
        """Assert that an object field has expected value."""
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
        """Assert that an object field has expected type."""
        value = getattr(obj, field_name)
        assert isinstance(
            value,
            expected_type,
        ), f"{field_name}={type(value)}, expected {expected_type}"

    @staticmethod
    def extract_config_values(
        config: BaseSettings,
        field_names: list[str],
    ) -> dict[str, t.GeneralValueType]:
        """Extract multiple field values from config."""
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
            """Assert that a r is successful."""
            assert result.is_success, (
                f"Expected success but got failure: {result.error}"
            )

        @staticmethod
        def assert_result_failure(result: r[T]) -> None:
            """Assert that a r is a failure."""
            assert result.is_failure, (
                f"Expected failure but got success: {result.value}"
            )

    class VersionTestFactory:
        """Factory for version validation tests."""

        @staticmethod
        def validate_version_string(version: str) -> r[str]:
            """Validate version string against semver pattern."""
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
            """Validate version info tuple structure."""
            if len(version_info) < 3:
                return r.fail("Version info must have at least 3 parts")

            for i, part in enumerate(version_info):
                if isinstance(part, int) and part < 0:
                    return r.fail(f"Version part {i} must be non-negative int")
                if isinstance(part, str) and not part:
                    return r.fail(f"Version part {i} must be non-empty string")

            return r.ok(version_info)

        @staticmethod
        def validate_consistency(
            version_string: str,
            version_info: tuple[int | str, ...],
        ) -> r[tuple[str, tuple[int | str, ...]]]:
            """Validate consistency between version string and info tuple."""
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

            version_without_metadata = version_string.split("+", maxsplit=1)[0]
            version_base_and_prerelease = version_without_metadata.split("-")
            base_parts = version_base_and_prerelease[0].split(".")
            prerelease_parts = (
                version_base_and_prerelease[1].split(".")
                if len(version_base_and_prerelease) > 1
                else []
            )
            version_parts_raw = base_parts + prerelease_parts

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
            """Create a formatter implementation satisfying CliFormatter protocol."""
            try:

                class TestFormatter:
                    def format_data(self, data: object, **options: object) -> r[str]:
                        try:
                            return r.ok(str(data))
                        except Exception as e:
                            return r.fail(str(e))

                formatter = TestFormatter()
                if hasattr(formatter, "format_data") and callable(
                    getattr(formatter, "format_data", None),
                ):
                    return r.ok(formatter)
                return r.fail("Formatter does not satisfy CliFormatter protocol")
            except Exception as e:
                return r.fail(f"Failed to create formatter: {e!s}")

        @staticmethod
        def create_config_provider_implementation() -> r[object]:
            """Create a config provider implementation satisfying CliConfigProvider protocol."""
            try:

                class TestConfigProvider:
                    def __init__(self) -> None:
                        self.config: dict[str, t.GeneralValueType] = {}

                    def load_config(self) -> r[dict[str, t.GeneralValueType]]:
                        try:
                            return r.ok(self.config)
                        except Exception as e:
                            return r.fail(str(e))

                    def save_config(self, config: object) -> r[bool]:
                        try:
                            if isinstance(config, dict):
                                self.config = config
                                return r.ok(True)
                            return r.fail("Config must be a dict")
                        except Exception as e:
                            return r.fail(str(e))

                provider = TestConfigProvider()
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
            """Create a CliAuthenticator protocol implementation."""
            try:

                class TestAuthenticator:
                    def __init__(self) -> None:
                        self.token: str | None = None

                    def authenticate(self, username: str, password: str) -> r[str]:
                        if username == "testuser" and password == "testpass":
                            self.token = "valid_token"
                            return r[str].ok(self.token)
                        return r[str].fail("Invalid credentials")

                    def validate_token(self, token: str) -> r[bool]:
                        if token.startswith("valid_"):
                            return r[bool].ok(value=True)
                        if token in {"valid_token_abc123", "valid_token", "test_token"}:
                            return r[bool].ok(value=True)
                        return r[bool].fail("Invalid token")

                authenticator = TestAuthenticator()
                has_authenticate = hasattr(authenticator, "authenticate") and callable(
                    getattr(authenticator, "authenticate", None),
                )
                has_validate_token = hasattr(
                    authenticator,
                    "validate_token",
                ) and callable(getattr(authenticator, "validate_token", None))
                if has_authenticate and has_validate_token:
                    auth_method = getattr(authenticator, "authenticate", None)
                    if auth_method:
                        sig = inspect.signature(auth_method)
                        params = list(sig.parameters.keys())
                        if len(params) >= 2:
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
            tuple[list[str], list[int], dict[str, t.GeneralValueType]]
        ]:
            """Create test data for type processing scenarios."""
            try:
                string_list = ["hello", "world", "test"]
                number_list = [1, 2, 3, 4, 5]
                mixed_dict: dict[str, t.GeneralValueType] = {
                    "key1": 123,
                    "key2": "value",
                    "key3": True,
                    "key4": [1, 2, 3],
                }
                return r.ok((string_list, number_list, mixed_dict))
            except Exception as e:
                return r.fail(f"Failed to create processing test data: {e!s}")

        @staticmethod
        def create_typed_dict_data() -> r[dict[str, t.GeneralValueType]]:
            """Create typed dict test data."""
            try:
                user_data: dict[str, t.GeneralValueType] = {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "active": True,
                }
                return r.ok(user_data)
            except Exception as e:
                return r.fail(f"Failed to create typed dict data: {e!s}")

        @staticmethod
        def create_api_response_data() -> r[list[dict[str, t.GeneralValueType]]]:
            """Create API response test data."""
            try:
                users_data: list[dict[str, t.GeneralValueType]] = [
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
            """Get FlextCliConstants instance for testing."""
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
            """Create a FlextCliContext instance for testing."""
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
            """Create a test command for CLI testing."""
            try:

                @click.command(name=command_name)
                def test_cmd() -> None:
                    click.echo("test")

                return r.ok(test_cmd)
            except Exception as e:
                return r.fail(f"Failed to create command: {e!s}")

        @staticmethod
        def create_test_group(cli_cli: object, group_name: str) -> r[object]:
            """Create a test group for CLI testing."""
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
            """Create a command with options for CLI testing."""
            try:

                @click.command(name=command_name)
                @click.option(option_name, default=default)
                def cmd_with_opt(config: str) -> None:
                    pass

                return r.ok(cmd_with_opt)
            except Exception as e:
                return r.fail(f"Failed to create command with options: {e!s}")

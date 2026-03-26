"""Implementation of test helpers - factories, validation, scenarios.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import logging
import re
from collections.abc import Sequence
from typing import Final, TypeIs

from flext_core import r

from flext_cli import t


def _is_json_dict(value: t.NormalizedValue) -> TypeIs[t.ContainerMapping]:
    """TypeGuard: narrow t.NormalizedValue to dict for JSON shape."""
    return isinstance(value, dict)


def _is_json_list(value: t.NormalizedValue) -> TypeIs[t.ContainerList]:
    """TypeGuard: narrow t.NormalizedValue to list for JSON array shape."""
    return isinstance(value, list)


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

    class VersionTestFactory:
        """Factory for version validation tests."""

        @staticmethod
        def validate_version_string(version: str) -> r[str]:
            """Validate version string against semver pattern."""
            if not version:
                return r[str].fail("Version must be non-empty string")
            pattern: str = "^\\d+\\.\\d+\\.\\d+(?:-[\\w\\.]+)?(?:\\+[\\w\\.]+)?$"
            if not re.match(pattern, version):
                return r[str].fail(f"Version '{version}' does not match semver pattern")
            return r[str].ok(version)

        @staticmethod
        def validate_version_info(
            version_info: tuple[int | str, ...],
        ) -> r[tuple[int | str, ...]]:
            """Validate version info tuple structure."""
            if len(version_info) < 3:
                return r[tuple[int | str, ...]].fail(
                    "Version info must have at least 3 parts",
                )
            for i, part in enumerate(version_info):
                if isinstance(part, int) and part < 0:
                    return r[tuple[int | str, ...]].fail(
                        f"Version part {i} must be non-negative int",
                    )
                if isinstance(part, str) and (not part):
                    return r[tuple[int | str, ...]].fail(
                        f"Version part {i} must be non-empty string",
                    )
            return r[tuple[int | str, ...]].ok(version_info)

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
                return r[tuple[str, tuple[int | str, ...]]].fail(
                    f"Invalid version string: {string_result.error}",
                )
            info_result = FlextCliTestHelpers.VersionTestFactory.validate_version_info(
                version_info,
            )
            if info_result.is_failure:
                return r[tuple[str, tuple[int | str, ...]]].fail(
                    f"Invalid version info: {info_result.error}",
                )
            version_without_metadata = version_string.split("+", maxsplit=1)[0]
            version_base_and_prerelease = version_without_metadata.split("-")
            base_parts = version_base_and_prerelease[0].split(".")
            prerelease_parts = (
                version_base_and_prerelease[1].split(".")
                if len(version_base_and_prerelease) > 1
                else []
            )
            version_parts_raw = base_parts + prerelease_parts
            version_parts: list[int | str] = []
            for part in version_parts_raw:
                try:
                    version_parts.append(int(part))
                except ValueError:
                    logging.getLogger(__name__).debug(
                        "version part non-int, keep as str: %s",
                        part,
                    )
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
                        return r[tuple[str, tuple[int | str, ...]]].fail(
                            f"Mismatch at position {i}: {version_part} != {info_part}",
                        )
                else:
                    return r[tuple[str, tuple[int | str, ...]]].fail(
                        f"Type mismatch at position {i}: {type(version_part).__name__} != {type(info_part).__name__}",
                    )
            return r[tuple[str, tuple[int | str, ...]]].ok((
                version_string,
                version_info,
            ))

    class TypingHelpers:
        """Helper methods for type system tests."""

        @staticmethod
        def create_processing_test_data() -> r[
            tuple[t.StrSequence, Sequence[int], t.ContainerMapping]
        ]:
            """Create test data for type processing scenarios."""
            try:
                string_list = ["hello", "world", "test"]
                number_list = [1, 2, 3, 4, 5]
                mixed_dict: t.ContainerMapping = {
                    "key1": 123,
                    "key2": "value",
                    "key3": True,
                    "key4": [1, 2, 3],
                }
                return r[tuple[t.StrSequence, Sequence[int], t.ContainerMapping]].ok((
                    string_list,
                    number_list,
                    mixed_dict,
                ))
            except (ValueError, TypeError) as e:
                return r[tuple[t.StrSequence, Sequence[int], t.ContainerMapping]].fail(
                    f"Failed to create processing test data: {e!s}",
                )

        @staticmethod
        def create_typed_dict_data() -> r[t.ContainerMapping]:
            """Create typed dict test data."""
            try:
                user_data: t.ContainerMapping = {
                    "id": 1,
                    "name": "John Doe",
                    "email": "john@example.com",
                    "active": True,
                }
                return r[t.ContainerMapping].ok(user_data)
            except (ValueError, TypeError) as e:
                return r[t.ContainerMapping].fail(
                    f"Failed to create typed dict data: {e!s}",
                )

        @staticmethod
        def create_api_response_data() -> r[Sequence[t.ContainerMapping]]:
            """Create API response test data."""
            try:
                users_data: Sequence[t.ContainerMapping] = [
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
                return r[Sequence[t.ContainerMapping]].ok(users_data)
            except (ValueError, TypeError) as e:
                return r[Sequence[t.ContainerMapping]].fail(
                    f"Failed to create API response data: {e!s}",
                )


__all__ = [
    "FlextCliTestHelpers",
    "TestScenario",
    "_is_json_dict",
    "_is_json_list",
]

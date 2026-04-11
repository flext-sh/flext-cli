"""Implementation of test helpers - factories, validation, scenarios.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import logging
import re
from collections.abc import MutableSequence

from tests import c

from flext_core import r


class FlextCliTestHelpers:
    """Centralized test helpers for flext-cli test modules."""

    class VersionTestFactory:
        """Factory for version validation tests."""

        @staticmethod
        def validate_version_string(version: str) -> r[str]:
            """Validate version string against semver pattern."""
            if not version:
                return r[str].fail(c.Cli.Tests.VersionErrors.EMPTY_STRING)
            pattern: str = c.Cli.Tests.VersionExamples.SEMVER_PATTERN
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
                    c.Cli.Tests.VersionErrors.INFO_TOO_SHORT,
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
            if string_result.failure:
                return r[tuple[str, tuple[int | str, ...]]].fail(
                    f"Invalid version string: {string_result.error}",
                )
            info_result = FlextCliTestHelpers.VersionTestFactory.validate_version_info(
                version_info,
            )
            if info_result.failure:
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
            version_parts: MutableSequence[int | str] = []
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


__all__ = ["FlextCliTestHelpers"]

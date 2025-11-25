"""Tests for flext_cli.__version__ - Version validation using modern patterns.

**TESTED MODULES**: flext_cli.__version__, flext_cli.__version_info__
**SCOPE**: Version semver compliance, immutability, consistency, edge cases

Uses StrEnum, dataclass, parametrization, and dynamic tests for maximum coverage
with minimal code (DRY principle).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import StrEnum
from typing import Final

import pytest

from flext_cli import __version__, __version_info__
from tests.fixtures.constants import TestVersions
from tests.helpers import FlextCliTestHelpers


class VersionValidationType(StrEnum):
    """Types of version validation."""

    STRING_VALIDATION = "string_validation"
    INFO_VALIDATION = "info_validation"
    CONSISTENCY = "consistency"


@dataclass(frozen=True)
class VersionTestScenario:
    """Version test scenario mapping."""

    name: str
    version_string: str | None = None
    version_info: tuple[int | str, ...] | None = None
    should_pass: bool = True

    @property
    def validation_type(self) -> VersionValidationType:
        """Determine validation type based on data provided."""
        if self.version_string and self.version_info:
            return VersionValidationType.CONSISTENCY
        if self.version_info:
            return VersionValidationType.INFO_VALIDATION
        return VersionValidationType.STRING_VALIDATION


class VersionTestCases:
    """Consolidated version test cases using mapping."""

    STRING_TESTS: Final[dict[str, VersionTestScenario]] = {
        "valid_semver": VersionTestScenario(
            "valid_semver",
            version_string=TestVersions.Examples.VALID_SEMVER,
            should_pass=True,
        ),
        "valid_complex": VersionTestScenario(
            "valid_complex",
            version_string=TestVersions.Examples.VALID_SEMVER_COMPLEX,
            should_pass=True,
        ),
        "invalid_no_dots": VersionTestScenario(
            "invalid_no_dots",
            version_string=TestVersions.Examples.INVALID_NO_DOTS,
            should_pass=False,
        ),
        "invalid_non_numeric": VersionTestScenario(
            "invalid_non_numeric",
            version_string=TestVersions.Examples.INVALID_NON_NUMERIC,
            should_pass=False,
        ),
        "invalid_empty": VersionTestScenario(
            "invalid_empty",
            version_string=TestVersions.Examples.INVALID_EMPTY,
            should_pass=False,
        ),
    }

    INFO_TESTS: Final[dict[str, VersionTestScenario]] = {
        "valid_tuple": VersionTestScenario(
            "valid_tuple",
            version_info=TestVersions.InfoTuples.VALID_TUPLE,
            should_pass=True,
        ),
        "valid_complex_tuple": VersionTestScenario(
            "valid_complex_tuple",
            version_info=TestVersions.InfoTuples.VALID_COMPLEX_TUPLE,
            should_pass=True,
        ),
        "short_tuple": VersionTestScenario(
            "short_tuple",
            version_info=TestVersions.InfoTuples.SHORT_TUPLE,
            should_pass=False,
        ),
        "empty_tuple": VersionTestScenario(
            "empty_tuple",
            version_info=TestVersions.InfoTuples.EMPTY_TUPLE,
            should_pass=False,
        ),
    }

    CONSISTENCY_TESTS: Final[dict[str, VersionTestScenario]] = {
        "valid_match": VersionTestScenario(
            "valid_match",
            version_string=TestVersions.Examples.VALID_SEMVER,
            version_info=TestVersions.InfoTuples.VALID_TUPLE,
            should_pass=True,
        ),
        "valid_complex_match": VersionTestScenario(
            "valid_complex_match",
            version_string=TestVersions.Examples.VALID_SEMVER_COMPLEX,
            version_info=TestVersions.InfoTuples.VALID_COMPLEX_TUPLE,
            should_pass=True,
        ),
        "invalid_mismatch": VersionTestScenario(
            "invalid_mismatch",
            version_string=TestVersions.Examples.INVALID_NO_DOTS,
            version_info=TestVersions.InfoTuples.SHORT_TUPLE,
            should_pass=False,
        ),
    }


class TestFlextCliVersion:
    """Comprehensive version validation test suite."""

    def test_actual_version_string_type(self) -> None:
        """Test __version__ is a non-empty string."""
        assert isinstance(__version__, str)
        assert len(__version__) > 0
        assert __version__ == __version__.strip()

    def test_actual_version_string_semver_compliant(self) -> None:
        """Test __version__ matches semver pattern."""
        pattern: Final[str] = TestVersions.Formats.SEMVER_PATTERN
        assert re.match(pattern, __version__) is not None

    def test_actual_version_info_structure(self) -> None:
        """Test __version_info__ is a valid tuple."""
        assert isinstance(__version_info__, tuple)
        assert len(__version_info__) >= TestVersions.Formats.MAJOR_MINOR_PATCH

        for i, part in enumerate(__version_info__):
            assert isinstance(part, (int, str)), f"Part {i} invalid type: {type(part)}"
            if isinstance(part, int):
                assert part >= 0, f"Part {i} negative: {part}"
            else:
                assert len(part) > 0, f"Part {i} empty string"

    def test_actual_version_consistency(self) -> None:
        """Test __version__ and __version_info__ are consistent."""
        result = FlextCliTestHelpers.VersionTestFactory.validate_consistency(
            __version__, __version_info__
        )
        assert result.is_success

    def test_actual_version_immutability(self) -> None:
        """Test version values are immutable."""
        original_version = __version__
        original_info = __version_info__

        assert __version__ == original_version
        assert __version_info__ == original_info
        assert isinstance(__version_info__, tuple)

    @pytest.mark.parametrize(
        ("scenario"),
        list(VersionTestCases.STRING_TESTS.values()),
        ids=list(VersionTestCases.STRING_TESTS),
    )
    def test_version_string_validation(self, scenario: VersionTestScenario) -> None:
        """Test version string validation with mapped scenarios."""
        assert scenario.version_string is not None
        result = FlextCliTestHelpers.VersionTestFactory.validate_version_string(
            scenario.version_string
        )

        if scenario.should_pass:
            assert result.is_success, f"Failed: {scenario.name}"
        else:
            assert result.is_failure, f"Should fail: {scenario.name}"

    @pytest.mark.parametrize(
        ("scenario"),
        list(VersionTestCases.INFO_TESTS.values()),
        ids=list(VersionTestCases.INFO_TESTS),
    )
    def test_version_info_validation(self, scenario: VersionTestScenario) -> None:
        """Test version info tuple validation with mapped scenarios."""
        assert scenario.version_info is not None
        result = FlextCliTestHelpers.VersionTestFactory.validate_version_info(
            scenario.version_info
        )

        if scenario.should_pass:
            assert result.is_success, f"Failed: {scenario.name}"
        else:
            assert result.is_failure, f"Should fail: {scenario.name}"

    @pytest.mark.parametrize(
        ("scenario"),
        list(VersionTestCases.CONSISTENCY_TESTS.values()),
        ids=list(VersionTestCases.CONSISTENCY_TESTS),
    )
    def test_version_consistency_validation(
        self, scenario: VersionTestScenario
    ) -> None:
        """Test consistency between version string and info with mapped scenarios."""
        assert scenario.version_string is not None
        assert scenario.version_info is not None

        result = FlextCliTestHelpers.VersionTestFactory.validate_consistency(
            scenario.version_string, scenario.version_info
        )

        if scenario.should_pass:
            assert result.is_success, f"Failed: {scenario.name}"
        else:
            assert result.is_failure, f"Should fail: {scenario.name}"

    def test_version_string_length_bounds(self) -> None:
        """Test version string length is within acceptable bounds."""
        min_len: Final[int] = TestVersions.Formats.MIN_VERSION_LENGTH
        max_len: Final[int] = TestVersions.Formats.MAX_VERSION_LENGTH
        assert min_len <= len(__version__) <= max_len

    def test_version_parts_extraction(self) -> None:
        """Test major.minor.patch can be extracted from version."""
        parts: list[str] = __version__.split(".")
        assert len(parts) >= TestVersions.Formats.MAJOR_MINOR_PATCH

        major_str, minor_str, patch_str = parts[0], parts[1], parts[2]
        assert major_str.isdigit()
        assert minor_str.isdigit()
        assert patch_str[0].isdigit()

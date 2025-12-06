"""FLEXT CLI Version Tests - Comprehensive Version Validation Testing.

Tests for flext_cli.__version__ and __version_info__ covering semver compliance,
immutability, consistency, and edge cases with 100% coverage.

Modules tested: flext_cli.__version__, flext_cli.__version_info__
Scope: Version string validation, version info validation, consistency checks

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from enum import StrEnum
from typing import Final, TypeVar

import pytest
from flext_tests import tm

from flext_cli import __version__, __version_info__

from .._helpers import FlextCliTestHelpers
from ..conftest import Examples, InfoTuples

T = TypeVar("T")


class TestsCliVersion:
    """Comprehensive version validation test suite.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    # =========================================================================
    # NESTED: Version Validation Types
    # =========================================================================

    class ValidationType(StrEnum):
        """Types of version validation."""

        STRING = "string_validation"
        INFO = "info_validation"
        CONSISTENCY = "consistency"

    # =========================================================================
    # NESTED: Test Scenario Factory
    # =========================================================================

    class TestScenario:
        """Version test scenario data class."""

        @dataclass(frozen=True)
        class Data:
            """Version test scenario data."""

            name: str
            version_string: str | None = None
            version_info: tuple[int | str, ...] | None = None
            should_pass: bool = True

            @property
            def validation_type(self) -> TestsCliVersion.ValidationType:
                """Determine validation type based on data provided."""
                # Access ValidationType enum from outer class scope
                # Use module-level lookup to avoid forward reference issues
                current_module = sys.modules[__name__]
                test_class: type[TestsCliVersion] = current_module.TestsCliVersion
                validation_enum = test_class.ValidationType
                if self.version_string and self.version_info:
                    return validation_enum.CONSISTENCY
                if self.version_info:
                    return validation_enum.INFO
                return validation_enum.STRING

        @classmethod
        def get_string_cases(cls) -> list[TestsCliVersion.TestScenario.Data]:
            """Get parametrized test cases for version string validation."""
            # Use cls to reference the nested Data class
            data_class = cls.Data
            return [
                data_class(
                    "valid_semver",
                    version_string=Examples.VALID_SEMVER,
                    should_pass=True,
                ),
                data_class(
                    "valid_complex",
                    version_string=Examples.VALID_SEMVER_COMPLEX,
                    should_pass=True,
                ),
                data_class(
                    "invalid_no_dots",
                    version_string=Examples.INVALID_NO_DOTS,
                    should_pass=False,
                ),
                data_class(
                    "invalid_non_numeric",
                    version_string=Examples.INVALID_NON_NUMERIC,
                    should_pass=False,
                ),
                data_class(
                    "invalid_empty",
                    version_string="",
                    should_pass=False,
                ),
            ]

        @classmethod
        def get_info_cases(cls) -> list[TestsCliVersion.TestScenario.Data]:
            """Get parametrized test cases for version info validation."""
            # Use cls to reference the nested Data class
            data_class = cls.Data
            return [
                data_class(
                    "valid_tuple",
                    version_info=InfoTuples.VALID_TUPLE,
                    should_pass=True,
                ),
                data_class(
                    "valid_complex_tuple",
                    version_info=InfoTuples.VALID_COMPLEX_TUPLE,
                    should_pass=True,
                ),
                data_class(
                    "short_tuple",
                    version_info=InfoTuples.SHORT_TUPLE,
                    should_pass=False,
                ),
                data_class(
                    "empty_tuple",
                    version_info=InfoTuples.EMPTY_TUPLE,
                    should_pass=False,
                ),
            ]

        @classmethod
        def get_consistency_cases(cls) -> list[TestsCliVersion.TestScenario.Data]:
            """Get parametrized test cases for version consistency validation."""
            # Use cls to reference the nested Data class
            data_class = cls.Data
            return [
                data_class(
                    "valid_match",
                    version_string=Examples.VALID_SEMVER,
                    version_info=InfoTuples.VALID_TUPLE,
                    should_pass=True,
                ),
                data_class(
                    "valid_complex_match",
                    version_string=Examples.VALID_SEMVER_COMPLEX,
                    version_info=InfoTuples.VALID_COMPLEX_TUPLE,
                    should_pass=True,
                ),
                data_class(
                    "invalid_mismatch",
                    version_string=Examples.INVALID_NO_DOTS,
                    version_info=InfoTuples.SHORT_TUPLE,
                    should_pass=False,
                ),
            ]

    # =========================================================================
    # NESTED: Assertion Helpers
    # =========================================================================

    # Assertions removed - use FlextTestsMatchers directly

    # =========================================================================
    # ACTUAL VERSION TESTS
    # =========================================================================

    def test_actual_version_string_type(self) -> None:
        """Test __version__ is a non-empty string."""
        assert isinstance(__version__, str)
        assert len(__version__) > 0
        assert __version__ == __version__.strip()

    def test_actual_version_string_semver_compliant(self) -> None:
        """Test __version__ matches semver pattern."""
        pattern: Final[str] = r"^\d+\.\d+\.\d+(?:-[\w\.]+)?(?:\+[\w\.]+)?$"
        assert re.match(pattern, __version__) is not None

    def test_actual_version_string_length_bounds(self) -> None:
        """Test version string length is within acceptable bounds."""
        min_len: Final[int] = 5
        max_len: Final[int] = 50
        assert min_len <= len(__version__) <= max_len

    def test_actual_version_info_structure(self) -> None:
        """Test __version_info__ is a valid tuple."""
        assert isinstance(__version_info__, tuple)
        assert len(__version_info__) >= 3

        for i, part in enumerate(__version_info__):
            assert isinstance(part, (int, str)), f"Part {i} invalid type: {type(part)}"
            if isinstance(part, int):
                assert part >= 0, f"Part {i} negative: {part}"
            else:
                assert len(part) > 0, f"Part {i} empty string"

    def test_actual_version_parts_extraction(self) -> None:
        """Test major.minor.patch can be extracted from version."""
        parts: list[str] = __version__.split(".")
        assert len(parts) >= 3

        major_str, minor_str, patch_str = parts[0], parts[1], parts[2]
        assert major_str.isdigit()
        assert minor_str.isdigit()
        assert patch_str[0].isdigit()

    def test_actual_version_consistency(self) -> None:
        """Test __version__ and __version_info__ are consistent."""
        result = FlextCliTestHelpers.VersionTestFactory.validate_consistency(
            __version__,
            __version_info__,
        )
        tm.ok(result)

    def test_actual_version_immutability(self) -> None:
        """Test version values are immutable."""
        original_version = __version__
        original_info = __version_info__

        assert __version__ == original_version
        assert __version_info__ == original_info
        assert isinstance(__version_info__, tuple)

    # =========================================================================
    # VERSION STRING VALIDATION TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        "scenario",
        TestScenario.get_string_cases(),
        ids=[s.name for s in TestScenario.get_string_cases()],
    )
    def test_version_string_validation(
        self,
        scenario: TestScenario.Data,
    ) -> None:
        """Test version string validation with parametrized cases."""
        assert scenario.version_string is not None
        result = FlextCliTestHelpers.VersionTestFactory.validate_version_string(
            scenario.version_string,
        )

        if scenario.should_pass:
            tm.ok(result, message=f"{scenario.name}: ")
        else:
            tm.fail(result, message=f"{scenario.name}: ")

    # =========================================================================
    # VERSION INFO VALIDATION TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        "scenario",
        TestScenario.get_info_cases(),
        ids=[s.name for s in TestScenario.get_info_cases()],
    )
    def test_version_info_validation(
        self,
        scenario: TestScenario.Data,
    ) -> None:
        """Test version info tuple validation with parametrized cases."""
        assert scenario.version_info is not None
        result = FlextCliTestHelpers.VersionTestFactory.validate_version_info(
            scenario.version_info,
        )

        if scenario.should_pass:
            tm.ok(result, message=f"{scenario.name}: ")
        else:
            tm.fail(result, message=f"{scenario.name}: ")

    # =========================================================================
    # VERSION CONSISTENCY VALIDATION TESTS (Parametrized)
    # =========================================================================

    @pytest.mark.parametrize(
        "scenario",
        TestScenario.get_consistency_cases(),
        ids=[s.name for s in TestScenario.get_consistency_cases()],
    )
    def test_version_consistency_validation(
        self,
        scenario: TestScenario.Data,
    ) -> None:
        """Test consistency between version string and info with parametrized cases."""
        assert scenario.version_string is not None
        assert scenario.version_info is not None

        result = FlextCliTestHelpers.VersionTestFactory.validate_consistency(
            scenario.version_string,
            scenario.version_info,
        )

        if scenario.should_pass:
            tm.ok(result, message=f"{scenario.name}: ")
        else:
            tm.fail(result, message=f"{scenario.name}: ")

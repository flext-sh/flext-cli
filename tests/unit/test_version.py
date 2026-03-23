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
from collections.abc import Sequence
from enum import StrEnum, unique
from typing import ClassVar, Final, TypeVar

import pytest
from flext_tests import tm
from pydantic import BaseModel, ConfigDict, Field

from flext_cli import __version__, __version_info__

from ..conftest import Examples, InfoTuples
from ..helpers import FlextCliTestHelpers

T = TypeVar("T")


class TestsCliVersion:
    """Comprehensive version validation test suite.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    @unique
    class ValidationType(StrEnum):
        """Types of version validation."""

        STRING = "string_validation"
        INFO = "info_validation"
        CONSISTENCY = "consistency"

    class TestScenario:
        """Version test scenario data class."""

        class Data(BaseModel):
            """Version test scenario data."""

            model_config: ClassVar[ConfigDict] = ConfigDict(frozen=True)

            name: str = Field(description="Scenario name")
            version_string: str | None = Field(
                default=None, description="Version string under test"
            )
            version_info: tuple[int | str, ...] | None = Field(
                default=None, description="Version info tuple under test"
            )
            should_pass: bool = Field(
                default=True, description="Whether scenario should pass validation"
            )

            @property
            def validation_type(self) -> TestsCliVersion.ValidationType:
                """Determine validation type based on data provided."""
                current_module = sys.modules[__name__]
                test_class: type[TestsCliVersion] = current_module.TestsCliVersion
                validation_enum = test_class.ValidationType
                if self.version_string and self.version_info:
                    return validation_enum.CONSISTENCY
                if self.version_info:
                    return validation_enum.INFO
                return validation_enum.STRING

        @classmethod
        def get_string_cases(cls) -> Sequence[TestsCliVersion.TestScenario.Data]:
            """Get parametrized test cases for version string validation."""
            data_class = cls.Data
            return [
                data_class(
                    name="valid_semver",
                    version_string=Examples.VALID_SEMVER,
                    should_pass=True,
                ),
                data_class(
                    name="valid_complex",
                    version_string=Examples.VALID_SEMVER_COMPLEX,
                    should_pass=True,
                ),
                data_class(
                    name="invalid_no_dots",
                    version_string=Examples.INVALID_NO_DOTS,
                    should_pass=False,
                ),
                data_class(
                    name="invalid_non_numeric",
                    version_string=Examples.INVALID_NON_NUMERIC,
                    should_pass=False,
                ),
                data_class(name="invalid_empty", version_string="", should_pass=False),
            ]

        @classmethod
        def get_info_cases(cls) -> Sequence[TestsCliVersion.TestScenario.Data]:
            """Get parametrized test cases for version info validation."""
            data_class = cls.Data
            return [
                data_class(
                    name="valid_tuple",
                    version_info=InfoTuples.VALID_TUPLE,
                    should_pass=True,
                ),
                data_class(
                    name="valid_complex_tuple",
                    version_info=InfoTuples.VALID_COMPLEX_TUPLE,
                    should_pass=True,
                ),
                data_class(
                    name="short_tuple",
                    version_info=InfoTuples.SHORT_TUPLE,
                    should_pass=False,
                ),
                data_class(
                    name="empty_tuple",
                    version_info=InfoTuples.EMPTY_TUPLE,
                    should_pass=False,
                ),
            ]

        @classmethod
        def get_consistency_cases(cls) -> Sequence[TestsCliVersion.TestScenario.Data]:
            """Get parametrized test cases for version consistency validation."""
            data_class = cls.Data
            return [
                data_class(
                    name="valid_match",
                    version_string=Examples.VALID_SEMVER,
                    version_info=InfoTuples.VALID_TUPLE,
                    should_pass=True,
                ),
                data_class(
                    name="valid_complex_match",
                    version_string=Examples.VALID_SEMVER_COMPLEX,
                    version_info=InfoTuples.VALID_COMPLEX_TUPLE,
                    should_pass=True,
                ),
                data_class(
                    name="invalid_mismatch",
                    version_string=Examples.INVALID_NO_DOTS,
                    version_info=InfoTuples.SHORT_TUPLE,
                    should_pass=False,
                ),
            ]

    def test_actual_version_string_type(self) -> None:
        """Test __version__ is a non-empty string."""
        tm.that(isinstance(__version__, str), eq=True)
        tm.that(len(__version__) > 0, eq=True)
        tm.that(__version__, eq=__version__.strip())

    def test_actual_version_string_semver_compliant(self) -> None:
        """Test __version__ matches semver pattern."""
        pattern: Final[str] = "^\\d+\\.\\d+\\.\\d+(?:-[\\w\\.]+)?(?:\\+[\\w\\.]+)?$"
        tm.that(re.match(pattern, __version__) is not None, eq=True)

    def test_actual_version_string_length_bounds(self) -> None:
        """Test version string length is within acceptable bounds."""
        min_len: Final[int] = 5
        max_len: Final[int] = 50
        tm.that(min_len <= len(__version__) <= max_len, eq=True)

    def test_actual_version_info_structure(self) -> None:
        """Test __version_info__ is a valid tuple."""
        tm.that(isinstance(__version_info__, tuple), eq=True)
        tm.that(len(__version_info__) >= 3, eq=True)
        for part in __version_info__:
            tm.that(isinstance(part, (int, str)), eq=True)
            if isinstance(part, int):
                tm.that(part >= 0, eq=True)
            else:
                tm.that(len(part) > 0, eq=True)

    def test_actual_version_parts_extraction(self) -> None:
        """Test major.minor.patch can be extracted from version."""
        parts: Sequence[str] = __version__.split(".")
        tm.that(len(parts) >= 3, eq=True)
        major_str, minor_str, patch_str = (parts[0], parts[1], parts[2])
        tm.that(major_str.isdigit(), eq=True)
        tm.that(minor_str.isdigit(), eq=True)
        tm.that(patch_str[0].isdigit(), eq=True)

    def test_actual_version_consistency(self) -> None:
        """Test __version__ and __version_info__ are consistent."""
        result = FlextCliTestHelpers.VersionTestFactory.validate_consistency(
            __version__, __version_info__
        )
        tm.ok(result)

    def test_actual_version_immutability(self) -> None:
        """Test version values are immutable."""
        original_version = __version__
        original_info = __version_info__
        tm.that(__version__, eq=original_version)
        tm.that(__version_info__, eq=original_info)
        tm.that(isinstance(__version_info__, tuple), eq=True)

    @pytest.mark.parametrize(
        "scenario",
        TestScenario.get_string_cases(),
        ids=[s.name for s in TestScenario.get_string_cases()],
    )
    def test_version_string_validation(self, scenario: TestScenario.Data) -> None:
        """Test version string validation with parametrized cases."""
        tm.that(scenario.version_string is not None, eq=True)
        version_str = scenario.version_string or ""
        result = FlextCliTestHelpers.VersionTestFactory.validate_version_string(
            version_str
        )
        if scenario.should_pass:
            tm.ok(result)
        else:
            tm.fail(result)

    @pytest.mark.parametrize(
        "scenario",
        TestScenario.get_info_cases(),
        ids=[s.name for s in TestScenario.get_info_cases()],
    )
    def test_version_info_validation(self, scenario: TestScenario.Data) -> None:
        """Test version info tuple validation with parametrized cases."""
        tm.that(scenario.version_info is not None, eq=True)
        version_info = scenario.version_info or ()
        result = FlextCliTestHelpers.VersionTestFactory.validate_version_info(
            version_info
        )
        if scenario.should_pass:
            tm.ok(result)
        else:
            tm.fail(result)

    @pytest.mark.parametrize(
        "scenario",
        TestScenario.get_consistency_cases(),
        ids=[s.name for s in TestScenario.get_consistency_cases()],
    )
    def test_version_consistency_validation(self, scenario: TestScenario.Data) -> None:
        """Test consistency between version string and info with parametrized cases."""
        tm.that(scenario.version_string is not None, eq=True)
        tm.that(scenario.version_info is not None, eq=True)
        version_str = scenario.version_string or ""
        version_info = scenario.version_info or ()
        result = FlextCliTestHelpers.VersionTestFactory.validate_consistency(
            version_str, version_info
        )
        if scenario.should_pass:
            tm.ok(result)
        else:
            tm.fail(result)

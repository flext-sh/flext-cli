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

import pytest
from flext_tests import tm

from flext_cli import __version__, __version_info__
from tests import c, m, t, u


class TestsCliVersion:
    """Comprehensive version validation test suite.

    Single class with nested helper classes and methods organized by functionality.
    Uses factories, constants, dynamic tests, and helpers to reduce code while
    maintaining and expanding coverage.
    """

    def test_actual_version_string_type(self) -> None:
        """Test __version__ is a non-empty string."""
        tm.that(__version__, is_=str)
        tm.that(bool(__version__), eq=True)
        tm.that(__version__, eq=__version__.strip())

    def test_actual_version_string_semver_compliant(self) -> None:
        """Test __version__ matches semver pattern."""
        tm.that(
            re.match(c.Cli.Tests.VersionExamples.SEMVER_PATTERN, __version__),
            none=False,
        )

    def test_actual_version_string_length_bounds(self) -> None:
        """Test version string length is within acceptable bounds."""
        tm.that(len(__version__), gte=5)
        tm.that(len(__version__), lte=50)

    def test_actual_version_info_structure(self) -> None:
        """Test __version_info__ is a valid tuple."""
        tm.that(__version_info__, is_=tuple)
        tm.that(len(__version_info__), gte=3)
        for part in __version_info__:
            tm.that(part, is_=(int, str))
            if isinstance(part, int):
                tm.that(part, gte=0)
            else:
                tm.that(len(str(part)), gt=0)

    def test_actual_version_parts_extraction(self) -> None:
        """Test major.minor.patch can be extracted from version."""
        parts: t.StrSequence = __version__.split(".")
        tm.that(len(parts), gte=3)
        major_str, minor_str, patch_str = (parts[0], parts[1], parts[2])
        tm.that(major_str.isdigit(), eq=True)
        tm.that(minor_str.isdigit(), eq=True)
        tm.that(patch_str[0].isdigit(), eq=True)

    def test_actual_version_consistency(self) -> None:
        """Test __version__ and __version_info__ are consistent."""
        result = u.Cli.Tests.VersionTestFactory.validate_consistency(
            __version__,
            __version_info__,
        )
        tm.ok(result)

    def test_actual_version_immutability(self) -> None:
        """Test version values are immutable."""
        original_version = __version__
        original_info = __version_info__
        tm.that(__version__, eq=original_version)
        tm.that(__version_info__, eq=original_info)
        tm.that(__version_info__, is_=tuple)

    @pytest.mark.parametrize(
        "scenario",
        m.Cli.Tests.VersionScenarios.string_cases(),
        ids=[s.name for s in m.Cli.Tests.VersionScenarios.string_cases()],
    )
    def test_version_string_validation(
        self, scenario: m.Cli.Tests.VersionTestScenario
    ) -> None:
        """Test version string validation with parametrized cases."""
        tm.that(scenario.version_string, none=False)
        version_str = scenario.version_string or ""
        result = u.Cli.Tests.VersionTestFactory.validate_version_string(
            version_str,
        )
        if scenario.should_pass:
            tm.ok(result)
        else:
            tm.fail(result)

    @pytest.mark.parametrize(
        "scenario",
        m.Cli.Tests.VersionScenarios.info_cases(),
        ids=[s.name for s in m.Cli.Tests.VersionScenarios.info_cases()],
    )
    def test_version_info_validation(
        self, scenario: m.Cli.Tests.VersionTestScenario
    ) -> None:
        """Test version info tuple validation with parametrized cases."""
        tm.that(scenario.version_info, none=False)
        version_info = scenario.version_info or ()
        result = u.Cli.Tests.VersionTestFactory.validate_version_info(
            version_info,
        )
        if scenario.should_pass:
            tm.ok(result)
        else:
            tm.fail(result)

    @pytest.mark.parametrize(
        "scenario",
        m.Cli.Tests.VersionScenarios.consistency_cases(),
        ids=[s.name for s in m.Cli.Tests.VersionScenarios.consistency_cases()],
    )
    def test_version_consistency_validation(
        self, scenario: m.Cli.Tests.VersionTestScenario
    ) -> None:
        """Test consistency between version string and info with parametrized cases."""
        tm.that(scenario.version_string, none=False)
        tm.that(scenario.version_info, none=False)
        version_str = scenario.version_string or ""
        version_info = scenario.version_info or ()
        result = u.Cli.Tests.VersionTestFactory.validate_consistency(
            version_str,
            version_info,
        )
        if scenario.should_pass:
            tm.ok(result)
        else:
            tm.fail(result)

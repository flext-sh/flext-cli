"""Public version-contract tests for the flext-cli facade."""

from __future__ import annotations

import pytest
from flext_tests import tm

from flext_cli import cli
from tests import c, m, t, u


class TestsFlextCliVersion:
    """Validate the public CLI version contract through canonical surfaces."""

    def test_actual_version_string_type(self) -> None:
        """The public CLI version string must be non-empty and trimmed."""
        facade_result = cli.execute()
        tm.ok(facade_result)
        version = str(facade_result.value["version"])
        tm.that(version, is_=str)
        tm.that(bool(version), eq=True)
        tm.that(version, eq=version.strip())
        tm.that(version, eq=c.Cli.CLI_VERSION)

    def test_actual_version_string_semver_compliant(self) -> None:
        """The public CLI version string must match the semver pattern."""
        tm.that(
            c.PATTERN_SEMVER_RE.match(c.Cli.CLI_VERSION),
            none=False,
        )

    def test_actual_version_string_length_bounds(self) -> None:
        """The public CLI version string must stay within expected bounds."""
        tm.that(len(c.Cli.CLI_VERSION), gte=5)
        tm.that(len(c.Cli.CLI_VERSION), lte=50)

    def test_actual_version_info_structure(self) -> None:
        """Derived version info from the public version string must be well-formed."""
        version_info = tuple(
            int(part) if part.isdigit() else part
            for part in c.Cli.CLI_VERSION
            .split("+", maxsplit=1)[0]
            .replace("-", ".")
            .split(".")
        )
        tm.that(version_info, is_=tuple)
        tm.that(len(version_info), gte=3)
        for part in version_info:
            tm.that(part, is_=(int, str))
            if isinstance(part, int):
                tm.that(part, gte=0)
            else:
                tm.that(len(part), gt=0)

    def test_actual_version_parts_extraction(self) -> None:
        """major.minor.patch can be extracted from the public version string."""
        parts: t.StrSequence = c.Cli.CLI_VERSION.split(".")
        tm.that(len(parts), gte=3)
        major_str, minor_str, patch_str = (parts[0], parts[1], parts[2])
        tm.that(major_str.isdigit(), eq=True)
        tm.that(minor_str.isdigit(), eq=True)
        tm.that(patch_str[0].isdigit(), eq=True)

    def test_actual_version_consistency(self) -> None:
        """The public CLI version string and its derived tuple must stay consistent."""
        version_info = tuple(
            int(part) if part.isdigit() else part
            for part in c.Cli.CLI_VERSION
            .split("+", maxsplit=1)[0]
            .replace("-", ".")
            .split(".")
        )
        result = u.Tests.VersionTestFactory.validate_consistency(
            c.Cli.CLI_VERSION,
            version_info,
        )
        tm.ok(result)

    def test_actual_version_immutability(self) -> None:
        """The public version contract must be deterministic across reads."""
        original_version = c.Cli.CLI_VERSION
        original_info = tuple(
            int(part) if part.isdigit() else part
            for part in c.Cli.CLI_VERSION
            .split("+", maxsplit=1)[0]
            .replace("-", ".")
            .split(".")
        )
        tm.that(c.Cli.CLI_VERSION, eq=original_version)
        tm.that(
            tuple(
                int(part) if part.isdigit() else part
                for part in c.Cli.CLI_VERSION
                .split("+", maxsplit=1)[0]
                .replace("-", ".")
                .split(".")
            ),
            eq=original_info,
        )
        tm.that(original_info, is_=tuple)

    @pytest.mark.parametrize(
        "scenario",
        m.Tests.VersionTestScenario.string_cases(),
        ids=lambda scenario: scenario.name,
    )
    def test_version_string_validation(
        self, scenario: m.Tests.VersionTestScenario
    ) -> None:
        """Test version string validation with parametrized cases."""
        tm.that(scenario.version_string, none=False)
        version_str = scenario.version_string or ""
        result = u.Tests.VersionTestFactory.validate_version_string(
            version_str,
        )
        if scenario.should_pass:
            tm.ok(result)
        else:
            tm.fail(result)

    @pytest.mark.parametrize(
        "scenario",
        m.Tests.VersionTestScenario.info_cases(),
        ids=lambda scenario: scenario.name,
    )
    def test_version_info_validation(
        self, scenario: m.Tests.VersionTestScenario
    ) -> None:
        """Test version info tuple validation with parametrized cases."""
        tm.that(scenario.version_info, none=False)
        version_info = scenario.version_info or ()
        result = u.Tests.VersionTestFactory.validate_version_info(
            version_info,
        )
        if scenario.should_pass:
            tm.ok(result)
        else:
            tm.fail(result)

    @pytest.mark.parametrize(
        "scenario",
        m.Tests.VersionTestScenario.consistency_cases(),
        ids=lambda scenario: scenario.name,
    )
    def test_version_consistency_validation(
        self, scenario: m.Tests.VersionTestScenario
    ) -> None:
        """Test consistency between version string and info with parametrized cases."""
        tm.that(scenario.version_string, none=False)
        tm.that(scenario.version_info, none=False)
        version_str = scenario.version_string or ""
        version_info = scenario.version_info or ()
        result = u.Tests.VersionTestFactory.validate_consistency(
            version_str,
            version_info,
        )
        if scenario.should_pass:
            tm.ok(result)
        else:
            tm.fail(result)

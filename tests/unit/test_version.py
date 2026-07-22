"""Public version-contract tests for the flext-cli facade.

Exercises only the observable public surface:

* ``flext_cli.__version__`` / ``flext_cli.__version_info__`` package metadata.
* ``FlextCliVersion`` (the MRO-derived version class re-exported publicly).
* ``c.Cli.CLI_VERSION`` (the runtime version constant).
* ``cli.execute()`` runtime status payload that publishes the version.

No private attributes, no internal-collaborator spying, no monkeypatching.
"""

from __future__ import annotations

import pytest

import flext_cli
from flext_cli import cli
from flext_cli.__version__ import FlextCliVersion
from flext_tests import tm
from tests import c


class TestsFlextCliVersion:
    """Validate the public CLI version contract through canonical surfaces."""

    def test_package_version_is_nonempty_trimmed_string(self) -> None:
        """``flext_cli.__version__`` is a non-empty, whitespace-trimmed string."""
        version = flext_cli.__version__
        tm.that(version, is_=str)
        tm.that(bool(version), eq=True)
        tm.that(version, eq=version.strip())

    def test_package_version_matches_semver_contract(self) -> None:
        """``flext_cli.__version__`` honours the published semver pattern."""
        tm.that(c.PATTERN_SEMVER_RE.match(flext_cli.__version__), none=False)

    def test_package_version_within_length_bounds(self) -> None:
        """``flext_cli.__version__`` stays within sane display bounds."""
        tm.that(len(flext_cli.__version__), gte=5)
        tm.that(len(flext_cli.__version__), lte=50)

    def test_package_version_info_is_tuple_of_at_least_three_parts(self) -> None:
        """``flext_cli.__version_info__`` is a tuple carrying major/minor/patch."""
        info = flext_cli.__version_info__
        tm.that(info, is_=tuple)
        tm.that(len(info), gte=3)

    def test_package_version_info_core_parts_are_non_negative_ints(self) -> None:
        """The leading major/minor/patch parts are non-negative integers."""
        info = flext_cli.__version_info__
        for part in info[:3]:
            tm.that(part, is_=int)
            tm.that(isinstance(part, bool), eq=False)
            tm.that(part, gte=0)

    def test_version_info_is_consistent_with_version_string(self) -> None:
        """``__version_info__`` is the release prefix of ``__version__``.

        This is the core invariant of the MRO-derived version surface:
        both public attributes describe the same release.
        """
        release = ".".join(str(part) for part in flext_cli.__version_info__)
        tm.that(flext_cli.__version__.startswith(release), eq=True)

    def test_facade_class_and_module_version_agree(self) -> None:
        """The public ``FlextCliVersion`` class and module exports match."""
        tm.that(FlextCliVersion.__version__, eq=flext_cli.__version__)
        tm.that(FlextCliVersion.__version_info__, eq=flext_cli.__version_info__)

    def test_cli_version_constant_matches_semver_contract(self) -> None:
        """The runtime ``c.Cli.CLI_VERSION`` constant is semver-compliant."""
        tm.that(c.Cli.CLI_VERSION, is_=str)
        tm.that(c.PATTERN_SEMVER_RE.match(c.Cli.CLI_VERSION), none=False)
        tm.that(len(c.Cli.CLI_VERSION), gte=5)
        tm.that(len(c.Cli.CLI_VERSION), lte=50)

    def test_cli_version_constant_exposes_major_minor_patch(self) -> None:
        """``c.Cli.CLI_VERSION`` yields extractable major/minor/patch parts."""
        parts = c.Cli.CLI_VERSION.split(".")
        tm.that(len(parts), gte=3)
        for part in parts[:3]:
            tm.that(part.isdigit(), eq=True)
            tm.that(int(part), gte=0)

    def test_execute_publishes_cli_version_in_runtime_payload(self) -> None:
        """``cli.execute()`` succeeds and reports the CLI version string."""
        result = cli.execute()
        tm.ok(result)
        payload = result.value
        version = payload.version
        tm.that(version, is_=str)
        tm.that(version, eq=c.Cli.CLI_VERSION)

    def test_execute_reports_version_deterministically(self) -> None:
        """Repeated ``cli.execute()`` calls report an identical version."""
        first = cli.execute()
        second = cli.execute()
        tm.ok(first)
        tm.ok(second)
        tm.that(first.value.version, eq=second.value.version)

    @pytest.mark.parametrize(
        ("candidate", "is_valid"),
        [
            ("0.0.0", True),
            ("1.2.3", True),
            ("10.20.30", True),
            ("1.0.0-dev0", True),
            ("1.0.0+build.5", True),
            ("", False),
            ("1", False),
            ("1.2", False),
            ("v1.2.3", False),
            ("1.2.x", False),
            ("not-a-version", False),
        ],
    )
    def test_semver_pattern_contract(self, candidate: str, *, is_valid: bool) -> None:
        """The published semver pattern accepts valid and rejects invalid strings."""
        matched = c.PATTERN_SEMVER_RE.match(candidate) is not None
        tm.that(matched, eq=is_valid)

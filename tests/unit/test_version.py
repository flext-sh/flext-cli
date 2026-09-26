"""Public version-contract tests for the flext-cli facade.

Exercises only the observable public surface:

* ``flext_cli.__version__`` / ``flext_cli.__version_info__`` package metadata.
* ``FlextCliVersion`` (the MRO-derived version class re-exported publicly).
* ``c.Cli.CLI_VERSION`` (the runtime version constant).
* ``cli.execute()`` runtime status payload that publishes the version.

No private attributes, no internal-collaborator spying, no monkeypatching.
"""

from __future__ import annotations

from flext_tests import tm

import flext_cli
from flext_cli import cli
from flext_cli.__version__ import FlextCliVersion
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

    def test_execute_publishes_cli_version_in_runtime_payload(self) -> None:
        """``cli.execute()`` succeeds and reports the CLI version string."""
        result = cli.execute()
        tm.ok(result)
        payload = result.value
        version = payload.version
        tm.that(version, is_=str)
        tm.that(version, eq=c.Cli.CLI_VERSION)

"""Coverage tests for _utilities/matching.py using constants-driven parametrize.

Targets: matches, matches_regex, file_not_found_error, cli_usage_error.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re

import pytest

from flext_cli import u
from tests import c


class TestsFlextCliMatchingCov:
    """Data-driven coverage tests for FlextCliUtilitiesMatching."""

    # ── matches ──────────────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("msg", "patterns", "expected"),
        c.Tests.MATCH_SIMPLE_CASES,
    )
    def test_matches_parametrized(
        self, msg: str, patterns: tuple[str, ...], expected: bool
    ) -> None:
        result = u.Cli.matches(msg, *patterns)
        assert result == expected

    def test_matches_case_insensitive(self) -> None:
        assert u.Cli.matches("ERROR OCCURRED", "error") is True

    def test_matches_empty_patterns(self) -> None:
        assert u.Cli.matches("any message") is False

    # ── matches_regex ────────────────────────────────────────────────

    def test_matches_regex_positive(self) -> None:
        pattern = re.compile(r"\d{3}-\d{4}")
        assert u.Cli.matches_regex("call 555-1234 now", pattern) is True

    def test_matches_regex_negative(self) -> None:
        pattern = re.compile(r"\d{3}-\d{4}")
        assert u.Cli.matches_regex("no phone here", pattern) is False

    def test_matches_regex_multiple_patterns(self) -> None:
        p1 = re.compile(r"alpha")
        p2 = re.compile(r"beta")
        assert u.Cli.matches_regex("this is beta test", p1, p2) is True

    def test_matches_regex_no_match_multiple(self) -> None:
        p1 = re.compile(r"alpha")
        p2 = re.compile(r"beta")
        assert u.Cli.matches_regex("nothing relevant", p1, p2) is False

    # ── file_not_found_error ─────────────────────────────────────────

    @pytest.mark.parametrize(
        ("msg", "expected"),
        c.Tests.FILE_NOT_FOUND_MATCH_CASES,
    )
    def test_file_not_found_error_parametrized(self, msg: str, expected: bool) -> None:
        result = u.Cli.file_not_found_error(msg)
        assert result == expected

    # ── cli_usage_error ───────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("msg", "expected"),
        c.Tests.CLI_USAGE_ERROR_MATCH_CASES,
    )
    def test_cli_usage_error_parametrized(self, msg: str, expected: bool) -> None:
        result = u.Cli.cli_usage_error(msg)
        assert result == expected


__all__: list[str] = ["TestsFlextCliMatchingCov"]

"""Behavioral contract tests for ``u.Cli`` CLI message matching predicates.

Exercises the observable public contract of ``FlextCliUtilitiesMatching`` as
exposed on ``u.Cli``: ``matches`` (case-insensitive substring, any-of),
``matches_regex`` (compiled-pattern search, any-of), and the two error
classifiers ``file_not_found_error`` / ``cli_usage_error``. Only return values
and invariants are asserted — never internals.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests.constants import c
from tests.utilities import u

if TYPE_CHECKING:
    from tests.typings import t


class TestsFlextCliMatchingCov:
    """Public-behavior tests for the ``u.Cli`` matching predicates."""

    # ── matches: case-table contract ─────────────────────────────────

    @pytest.mark.parametrize(
        ("msg", "patterns", "expected"),
        c.Tests.MATCH_SIMPLE_CASES,
    )
    def test_matches_returns_expected_for_case_table(
        self,
        msg: str,
        patterns: t.StrSequence,
        expected: bool,
    ) -> None:
        assert u.Cli.matches(msg, *patterns) is expected

    # ── matches: invariants ──────────────────────────────────────────

    def test_matches_is_case_insensitive_on_message_and_matches_substring(
        self,
    ) -> None:
        assert u.Cli.matches("ERROR OCCURRED", "error") is True
        assert u.Cli.matches("Error Occurred", "occurred") is True

    def test_matches_without_patterns_is_always_false(self) -> None:
        assert u.Cli.matches("any message") is False
        assert u.Cli.matches("") is False

    def test_matches_is_any_of_not_all_of(self) -> None:
        # Succeeds when at least one pattern hits, even if others miss.
        assert u.Cli.matches("deprecated api", "obsolete", "deprecated") is True
        # Fails only when every pattern misses.
        assert u.Cli.matches("clean output", "obsolete", "deprecated") is False

    def test_matches_is_idempotent(self) -> None:
        first = u.Cli.matches("file not found", "not found")
        second = u.Cli.matches("file not found", "not found")
        assert first is second is True

    def test_matches_empty_pattern_string_matches_any_message(self) -> None:
        # Empty substring is contained in every string.
        assert u.Cli.matches("whatever", "") is True

    # ── matches_regex: contract ──────────────────────────────────────

    def test_matches_regex_true_when_single_pattern_hits(self) -> None:
        assert (
            u.Cli.matches_regex("call 555-1234 now", c.Tests.MATCH_REGEX_PHONE_RE)
            is True
        )

    def test_matches_regex_false_when_pattern_misses(self) -> None:
        assert (
            u.Cli.matches_regex("no phone here", c.Tests.MATCH_REGEX_PHONE_RE) is False
        )

    def test_matches_regex_is_any_of_across_multiple_patterns(self) -> None:
        alpha = c.Tests.MATCH_REGEX_ALPHA_RE
        beta = c.Tests.MATCH_REGEX_BETA_RE
        assert u.Cli.matches_regex("this is beta test", alpha, beta) is True
        assert u.Cli.matches_regex("this is alpha test", alpha, beta) is True

    def test_matches_regex_false_when_all_patterns_miss(self) -> None:
        assert (
            u.Cli.matches_regex(
                "nothing relevant",
                c.Tests.MATCH_REGEX_ALPHA_RE,
                c.Tests.MATCH_REGEX_BETA_RE,
            )
            is False
        )

    def test_matches_regex_without_patterns_is_false(self) -> None:
        assert u.Cli.matches_regex("anything at all") is False

    def test_matches_regex_searches_substring_not_full_match(self) -> None:
        # `.search` semantics: the pattern may appear anywhere in the message.
        assert (
            u.Cli.matches_regex("prefix 999-0000 suffix", c.Tests.MATCH_REGEX_PHONE_RE)
            is True
        )

    # ── file_not_found_error: classifier contract ────────────────────

    @pytest.mark.parametrize(
        ("msg", "expected"),
        c.Tests.FILE_NOT_FOUND_MATCH_CASES,
    )
    def test_file_not_found_error_classifies_case_table(
        self,
        msg: str,
        expected: bool,
    ) -> None:
        assert u.Cli.file_not_found_error(msg) is expected

    def test_file_not_found_error_is_case_insensitive(self) -> None:
        assert u.Cli.file_not_found_error("NO SUCH FILE OR DIRECTORY") is True
        assert u.Cli.file_not_found_error("no such file or directory") is True

    def test_file_not_found_error_false_for_unrelated_message(self) -> None:
        assert u.Cli.file_not_found_error("permission denied") is False

    # ── cli_usage_error: classifier contract ─────────────────────────

    @pytest.mark.parametrize(
        ("msg", "expected"),
        c.Tests.CLI_USAGE_ERROR_MATCH_CASES,
    )
    def test_cli_usage_error_classifies_case_table(
        self,
        msg: str,
        expected: bool,
    ) -> None:
        assert u.Cli.cli_usage_error(msg) is expected

    def test_cli_usage_error_is_case_insensitive(self) -> None:
        assert u.Cli.cli_usage_error("MISSING OPTION '--project'") is True

    def test_cli_usage_error_false_for_runtime_error(self) -> None:
        assert u.Cli.cli_usage_error("division by zero") is False

    def test_classifiers_are_disjoint_for_representative_messages(self) -> None:
        # A missing-file error is not a usage error, and vice versa.
        assert u.Cli.file_not_found_error("no such file or directory") is True
        assert u.Cli.cli_usage_error("no such file or directory") is False
        assert u.Cli.cli_usage_error("missing option '--project'") is True
        assert u.Cli.file_not_found_error("missing option '--project'") is False


__all__: list[str] = ["TestsFlextCliMatchingCov"]

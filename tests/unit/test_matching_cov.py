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


import pytest

from tests import c
from tests import u
from flext_tests import tm

from tests import t


class TestsFlextCliMatchingCov:
    """Public-behavior tests for the ``u.Cli`` matching predicates."""

    # ── matches: case-table contract ─────────────────────────────────

    @pytest.mark.parametrize(
        ("msg", "patterns", "expected"), c.Tests.MATCH_SIMPLE_CASES
    )
    def test_matches_returns_expected_for_case_table(
        self, msg: str, patterns: t.StrSequence, *, expected: bool
    ) -> None:
        """Verify that matches returns expected for case table."""
        tm.that(u.Cli.matches(msg, *patterns) is expected, eq=True)

    # ── matches: invariants ──────────────────────────────────────────

    def test_matches_is_case_insensitive_on_message_and_matches_substring(self) -> None:
        """Verify that matches is case insensitive on message and matches substring."""
        tm.that(u.Cli.matches("ERROR OCCURRED", "error"), eq=True)
        tm.that(u.Cli.matches("Error Occurred", "occurred"), eq=True)

    def test_matches_without_patterns_is_always_false(self) -> None:
        """Verify that matches without patterns is always false."""
        tm.that(u.Cli.matches("any message"), eq=False)
        tm.that(u.Cli.matches(""), eq=False)

    def test_matches_is_any_of_not_all_of(self) -> None:
        # Succeeds when at least one pattern hits, even if others miss.
        """Verify that matches is any of not all of."""
        tm.that(u.Cli.matches("deprecated api", "obsolete", "deprecated"), eq=True)
        # Fails only when every pattern misses.
        tm.that(u.Cli.matches("clean output", "obsolete", "deprecated"), eq=False)

    def test_matches_is_idempotent(self) -> None:
        """Verify that matches is idempotent."""
        first = u.Cli.matches("file not found", "not found")
        second = u.Cli.matches("file not found", "not found")
        tm.that(first is second is True, eq=True)

    def test_matches_empty_pattern_string_matches_any_message(self) -> None:
        # Empty substring is contained in every string.
        """Verify that matches empty pattern string matches any message."""
        tm.that(u.Cli.matches("whatever", ""), eq=True)

    # ── matches_regex: contract ──────────────────────────────────────

    def test_matches_regex_true_when_single_pattern_hits(self) -> None:
        """Verify that matches regex true when single pattern hits."""
        tm.that(
            u.Cli.matches_regex("call 555-1234 now", c.Tests.MATCH_REGEX_PHONE_RE)
            is True,
            eq=True,
        )

    def test_matches_regex_false_when_pattern_misses(self) -> None:
        """Verify that matches regex false when pattern misses."""
        tm.that(
            u.Cli.matches_regex("no phone here", c.Tests.MATCH_REGEX_PHONE_RE) is False,
            eq=True,
        )

    def test_matches_regex_is_any_of_across_multiple_patterns(self) -> None:
        """Verify that matches regex is any of across multiple patterns."""
        alpha = c.Tests.MATCH_REGEX_ALPHA_RE
        beta = c.Tests.MATCH_REGEX_BETA_RE
        tm.that(u.Cli.matches_regex("this is beta test", alpha, beta), eq=True)
        tm.that(u.Cli.matches_regex("this is alpha test", alpha, beta), eq=True)

    def test_matches_regex_false_when_all_patterns_miss(self) -> None:
        """Verify that matches regex false when all patterns miss."""
        tm.that(
            u.Cli.matches_regex(
                "nothing relevant",
                c.Tests.MATCH_REGEX_ALPHA_RE,
                c.Tests.MATCH_REGEX_BETA_RE,
            )
            is False,
            eq=True,
        )

    def test_matches_regex_without_patterns_is_false(self) -> None:
        """Verify that matches regex without patterns is false."""
        tm.that(u.Cli.matches_regex("anything at all"), eq=False)

    def test_matches_regex_searches_substring_not_full_match(self) -> None:
        # `.search` semantics: the pattern may appear anywhere in the message.
        """Verify that matches regex searches substring not full match."""
        tm.that(
            u.Cli.matches_regex("prefix 999-0000 suffix", c.Tests.MATCH_REGEX_PHONE_RE)
            is True,
            eq=True,
        )

    # ── file_not_found_error: classifier contract ────────────────────

    @pytest.mark.parametrize(("msg", "expected"), c.Tests.FILE_NOT_FOUND_MATCH_CASES)
    def test_file_not_found_error_classifies_case_table(
        self, msg: str, *, expected: bool
    ) -> None:
        """Verify that file not found error classifies case table."""
        tm.that(u.Cli.file_not_found_error(msg) is expected, eq=True)

    def test_file_not_found_error_is_case_insensitive(self) -> None:
        """Verify that file not found error is case insensitive."""
        tm.that(u.Cli.file_not_found_error("NO SUCH FILE OR DIRECTORY"), eq=True)
        tm.that(u.Cli.file_not_found_error("no such file or directory"), eq=True)

    def test_file_not_found_error_false_for_unrelated_message(self) -> None:
        """Verify that file not found error false for unrelated message."""
        tm.that(u.Cli.file_not_found_error("permission denied"), eq=False)

    # ── cli_usage_error: classifier contract ─────────────────────────

    @pytest.mark.parametrize(("msg", "expected"), c.Tests.CLI_USAGE_ERROR_MATCH_CASES)
    def test_cli_usage_error_classifies_case_table(
        self, msg: str, *, expected: bool
    ) -> None:
        """Verify that cli usage error classifies case table."""
        tm.that(u.Cli.cli_usage_error(msg) is expected, eq=True)

    def test_cli_usage_error_is_case_insensitive(self) -> None:
        """Verify that cli usage error is case insensitive."""
        tm.that(u.Cli.cli_usage_error("MISSING OPTION '--project'"), eq=True)

    def test_cli_usage_error_false_for_runtime_error(self) -> None:
        """Verify that cli usage error false for runtime error."""
        tm.that(u.Cli.cli_usage_error("division by zero"), eq=False)

    def test_classifiers_are_disjoint_for_representative_messages(self) -> None:
        # A missing-file error is not a usage error, and vice versa.
        """Verify that classifiers are disjoint for representative messages."""
        tm.that(u.Cli.file_not_found_error("no such file or directory"), eq=True)
        tm.that(u.Cli.cli_usage_error("no such file or directory"), eq=False)
        tm.that(u.Cli.cli_usage_error("missing option '--project'"), eq=True)
        tm.that(u.Cli.file_not_found_error("missing option '--project'"), eq=False)


__all__: list[str] = ["TestsFlextCliMatchingCov"]

"""Behavioral contract tests for ``u.Cli`` CLI message matching predicates.

Exercises the observable public contract of ``FlextCliUtilitiesMatching`` as
exposed on ``u.Cli``: ``matches`` (case-insensitive substring, any-of),
``matches_regex`` (compiled-pattern search, any-of), and the error
classifier ``cli_usage_error``. Only return values
and invariants are asserted — never internals.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests import c, tm, u

if TYPE_CHECKING:
    from tests import t


class TestsFlextCliMatchingCov:
    """Public-behavior tests for the ``u.Cli`` matching predicates."""

    # ── matches: case-table contract ─────────────────────────────────

    @staticmethod
    @pytest.mark.parametrize(
        ("msg", "patterns", "expected"),
        c.Tests.MATCH_SIMPLE_CASES,
    )
    def test_matches_returns_expected_for_case_table(
        msg: str,
        patterns: t.StrSequence,
        *,
        expected: bool,
    ) -> None:
        """Verify that matches returns expected for case table."""
        tm.ok(u.Cli.matches(msg, *patterns) is expected)

    # ── matches: invariants ──────────────────────────────────────────

    @staticmethod
    def test_matches_is_case_insensitive_on_message_and_matches_substring() -> None:
        """Verify that matches is case insensitive on message and matches substring."""
        tm.ok(u.Cli.matches("ERROR OCCURRED", "error"))
        tm.ok(u.Cli.matches("Error Occurred", "occurred"))

    @staticmethod
    def test_matches_without_patterns_is_always_false() -> None:
        """Verify that matches without patterns is always false."""
        tm.fail(u.Cli.matches("any message"))
        tm.fail(u.Cli.matches(""))

    @staticmethod
    def test_matches_is_any_of_not_all_of() -> None:
        # Succeeds when at least one pattern hits, even if others miss.
        """Verify that matches is any of not all of."""
        tm.ok(u.Cli.matches("deprecated api", "obsolete", "deprecated"))
        # Fails only when every pattern misses.
        tm.fail(u.Cli.matches("clean output", "obsolete", "deprecated"))

    @staticmethod
    def test_matches_is_idempotent() -> None:
        """Verify that matches is idempotent."""
        first = u.Cli.matches("file not found", "not found")
        second = u.Cli.matches("file not found", "not found")
        tm.ok(first is second is True)

    @staticmethod
    def test_matches_empty_pattern_string_matches_any_message() -> None:
        # Empty substring is contained in every string.
        """Verify that matches empty pattern string matches any message."""
        tm.ok(u.Cli.matches("whatever", ""))

    # ── matches_regex: contract ──────────────────────────────────────

    @staticmethod
    def test_matches_regex_true_when_single_pattern_hits() -> None:
        """Verify that matches regex true when single pattern hits."""
        tm.that(
            u.Cli.matches_regex("call 555-1234 now", c.Tests.MATCH_REGEX_PHONE_RE)
            is True,
            eq=True,
        )

    @staticmethod
    def test_matches_regex_false_when_pattern_misses() -> None:
        """Verify that matches regex false when pattern misses."""
        tm.that(
            u.Cli.matches_regex("no phone here", c.Tests.MATCH_REGEX_PHONE_RE) is False,
            eq=True,
        )

    @staticmethod
    def test_matches_regex_is_any_of_across_multiple_patterns() -> None:
        """Verify that matches regex is any of across multiple patterns."""
        alpha = c.Tests.MATCH_REGEX_ALPHA_RE
        beta = c.Tests.MATCH_REGEX_BETA_RE
        tm.ok(u.Cli.matches_regex("this is beta test", alpha, beta))
        tm.ok(u.Cli.matches_regex("this is alpha test", alpha, beta))

    @staticmethod
    def test_matches_regex_false_when_all_patterns_miss() -> None:
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

    @staticmethod
    def test_matches_regex_without_patterns_is_false() -> None:
        """Verify that matches regex without patterns is false."""
        tm.fail(u.Cli.matches_regex("anything at all"))

    @staticmethod
    def test_matches_regex_searches_substring_not_full_match() -> None:
        # `.search` semantics: the pattern may appear anywhere in the message.
        """Verify that matches regex searches substring not full match."""
        tm.that(
            u.Cli.matches_regex("prefix 999-0000 suffix", c.Tests.MATCH_REGEX_PHONE_RE)
            is True,
            eq=True,
        )

    # ── cli_usage_error: classifier contract ─────────────────────────

    @staticmethod
    @pytest.mark.parametrize(("msg", "expected"), c.Tests.CLI_USAGE_ERROR_MATCH_CASES)
    def test_cli_usage_error_classifies_case_table(
        msg: str,
        *,
        expected: bool,
    ) -> None:
        """Verify that cli usage error classifies case table."""
        tm.ok(u.Cli.cli_usage_error(msg) is expected)

    @staticmethod
    def test_cli_usage_error_is_case_insensitive() -> None:
        """Verify that cli usage error is case insensitive."""
        tm.ok(u.Cli.cli_usage_error("MISSING OPTION '--project'"))

    @staticmethod
    def test_cli_usage_error_false_for_runtime_error() -> None:
        """Verify that cli usage error false for runtime error."""
        tm.fail(u.Cli.cli_usage_error("division by zero"))

"""CLI message matching helpers shared through ``u.Cli``."""

from __future__ import annotations

from typing import Protocol

from flext_cli import c, t


class _Searchable(Protocol):
    """Minimal search-only protocol satisfied by ``re.Pattern`` instances.

    Consumers receive ``c.Cli.FILE_NOT_FOUND_REGEXES`` /
    ``CLI_USAGE_ERROR_REGEXES`` (or any ``re.Pattern[str]`` built through
    ``c.Cli.compile_pattern``); the protocol keeps this module free of
    ``import re``.
    """

    def search(self, string: str) -> object: ...


class FlextCliUtilitiesMatching:
    """Pattern matching methods exposed directly on ``u.Cli``."""

    @staticmethod
    def matches(msg: str, *patterns: str) -> bool:
        """Check whether a message matches any of the given substring patterns."""
        text = msg.lower()
        return any(pattern in text for pattern in patterns)

    @staticmethod
    def matches_regex(msg: str, *patterns: _Searchable) -> bool:
        """Check whether a message matches any compiled regex pattern."""
        return any(pattern.search(msg) is not None for pattern in patterns)

    @staticmethod
    def file_not_found_error(error_msg: str) -> bool:
        """Match error messages that indicate a missing file (RFC-grade regex)."""
        return FlextCliUtilitiesMatching.matches_regex(
            error_msg,
            *c.Cli.FILE_NOT_FOUND_REGEXES,
        )

    @staticmethod
    def cli_usage_error(error_msg: str) -> bool:
        """Match error messages that indicate CLI usage/input failure."""
        return FlextCliUtilitiesMatching.matches_regex(
            error_msg,
            *c.Cli.CLI_USAGE_ERROR_REGEXES,
        )


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesMatching"]

"""CLI message matching helpers shared through ``u.Cli``."""

from __future__ import annotations


class FlextCliUtilitiesMatching:
    """Pattern matching methods exposed directly on ``u.Cli``."""

    FILE_NOT_FOUND_PATTERNS: tuple[str, ...] = (
        "not found",
        "no such file",
        "does not exist",
        "errno 2",
        "cannot open",
    )

    @staticmethod
    def matches(msg: str, *patterns: str) -> bool:
        """Check whether a message matches any of the given patterns."""
        text = msg.lower()
        return any(pattern.lower() in text for pattern in patterns)

    @staticmethod
    def is_file_not_found_error(error_msg: str) -> bool:
        """Check whether an error message indicates a missing file."""
        return FlextCliUtilitiesMatching.matches(
            error_msg,
            *FlextCliUtilitiesMatching.FILE_NOT_FOUND_PATTERNS,
        )


__all__ = ["FlextCliUtilitiesMatching"]

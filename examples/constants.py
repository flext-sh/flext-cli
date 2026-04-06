"""FLEXT CLI example constants."""

from __future__ import annotations

from typing import Final

from flext_cli import c as _cli_c


class FlextCliExamplesConstants(_cli_c):
    """Public examples constants facade extending flext-cli constants."""

    class Examples:
        """Examples namespace for example-domain constants."""

        class Defaults:
            """Default values for example configurations."""

            DEPLOYMENT_ENVIRONMENTS: Final[tuple[str, ...]] = (
                "development",
                "staging",
                "production",
            )
            DEPLOYMENT_ENVIRONMENTS_SHORT: Final[tuple[str, ...]] = (
                "dev",
                "staging",
                "prod",
            )
            REQUIRED_DATA_FIELDS: Final[tuple[str, ...]] = ("id", "name", "value")
            DATABASE_REQUIRED_FIELDS: Final[tuple[str, ...]] = (
                "host",
                "name",
                "username",
                "password",
            )
            DEFAULT_SHELL_ITEMS: Final[tuple[str, ...]] = (
                "item1",
                "item2",
                "item3",
                "test_item",
            )
            SAMPLE_FILES: Final[tuple[str, ...]] = (
                "file1",
                "file2",
                "file3",
                "file4",
            )

        class TableHeaders:
            """Standard table header tuples for example output."""

            FIELD_VALUE: Final[tuple[str, str]] = ("Field", "Value")
            SETTING_VALUE: Final[tuple[str, str]] = ("Setting", "Value")


c = FlextCliExamplesConstants

__all__ = [
    "FlextCliExamplesConstants",
    "c",
]

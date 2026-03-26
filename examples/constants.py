"""FLEXT CLI example constants."""

from __future__ import annotations

from flext_cli import FlextCliConstants


class ExamplesConstants(FlextCliConstants):
    """Public examples constants facade extending flext-cli constants."""


c = ExamplesConstants

__all__ = [
    "ExamplesConstants",
    "c",
]

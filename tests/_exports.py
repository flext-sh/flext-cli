"""Lazy export registry for tests/__init__.py."""

from __future__ import annotations

from tests._exports_lazy import TESTS_FLEXT_CLI_LAZY_IMPORTS
from tests._exports_public import TESTS_FLEXT_CLI_PUBLIC_EXPORTS

__all__: list[str] = [
    "TESTS_FLEXT_CLI_LAZY_IMPORTS",
    "TESTS_FLEXT_CLI_PUBLIC_EXPORTS",
]

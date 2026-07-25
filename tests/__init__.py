# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from flext_core.lazy import install_lazy_exports
from tests._exports import (
    TESTS_FLEXT_CLI_LAZY_IMPORTS,
    TESTS_FLEXT_CLI_PUBLIC_EXPORTS,
)

_LAZY_IMPORTS = {
    name: target
    for name, target in TESTS_FLEXT_CLI_LAZY_IMPORTS.items()
    if name in TESTS_FLEXT_CLI_PUBLIC_EXPORTS
}


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)

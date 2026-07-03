# AUTO-GENERATED FILE — Regenerate with: make gen
"""Test Cli Service package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.tests.unit._cases.test_cli_service.testsflextcliservice_part_05 import (
        TestsFlextCliService as TestsFlextCliService,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".testsflextcliservice_part_05": ("TestsFlextCliService",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)

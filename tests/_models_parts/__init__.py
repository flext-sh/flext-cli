# AUTO-GENERATED FILE — Regenerate with: make gen
"""Models Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.tests._models_parts.tests_cli import (
        TestsFlextCliModelsCli as TestsFlextCliModelsCli,
    )
    from flext_cli.tests._models_parts.tests_runtime import (
        TestsFlextCliModelsRuntime as TestsFlextCliModelsRuntime,
    )
    from flext_cli.tests._models_parts.tests_version import (
        TestsFlextCliModelsVersion as TestsFlextCliModelsVersion,
    )
    from flext_cli.tests._models_parts.testsflextclimodels_part_01 import (
        TestsFlextCliModels as TestsFlextCliModels,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".tests_cli": ("TestsFlextCliModelsCli",),
        ".tests_runtime": ("TestsFlextCliModelsRuntime",),
        ".tests_version": ("TestsFlextCliModelsVersion",),
        ".testsflextclimodels_part_01": ("TestsFlextCliModels",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)

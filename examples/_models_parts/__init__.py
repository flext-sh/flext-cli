# AUTO-GENERATED FILE — Regenerate with: make gen
"""Models Parts package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.examples._models_parts.examples_advanced import (
        ExamplesFlextCliModelsExamplesAdvanced as ExamplesFlextCliModelsExamplesAdvanced,
    )
    from flext_cli.examples._models_parts.examples_common import (
        ExamplesFlextCliModelsExamplesCommon as ExamplesFlextCliModelsExamplesCommon,
    )
    from flext_cli.examples._models_parts.examples_database import (
        ExamplesFlextCliModelsExamplesDatabase as ExamplesFlextCliModelsExamplesDatabase,
    )
    from flext_cli.examples._models_parts.examplesflextclimodels_part_01 import (
        ExamplesFlextCliModels as ExamplesFlextCliModels,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".examples_advanced": ("ExamplesFlextCliModelsExamplesAdvanced",),
        ".examples_common": ("ExamplesFlextCliModelsExamplesCommon",),
        ".examples_database": ("ExamplesFlextCliModelsExamplesDatabase",),
        ".examplesflextclimodels_part_01": ("ExamplesFlextCliModels",),
    },
)


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)

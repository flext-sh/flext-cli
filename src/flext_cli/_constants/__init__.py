# AUTO-GENERATED FILE — Regenerate with: make gen
"""Constants package."""

from __future__ import annotations

import typing as _t

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if _t.TYPE_CHECKING:
    from flext_cli._constants.base import FlextCliConstantsBase as FlextCliConstantsBase
    from flext_cli._constants.enums import (
        FlextCliConstantsEnums as FlextCliConstantsEnums,
    )
    from flext_cli._constants.errors import (
        FlextCliConstantsErrors as FlextCliConstantsErrors,
    )
    from flext_cli._constants.exceptions import (
        FlextCliConstantsExceptions as FlextCliConstantsExceptions,
    )
    from flext_cli._constants.files import (
        FlextCliConstantsFiles as FlextCliConstantsFiles,
    )
    from flext_cli._constants.output import (
        FlextCliConstantsOutput as FlextCliConstantsOutput,
    )
    from flext_cli._constants.pipeline import (
        FlextCliConstantsPipeline as FlextCliConstantsPipeline,
    )
    from flext_cli._constants.settings import (
        FlextCliConstantsSettings as FlextCliConstantsSettings,
    )
_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".base": ("FlextCliConstantsBase",),
        ".enums": ("FlextCliConstantsEnums",),
        ".errors": ("FlextCliConstantsErrors",),
        ".exceptions": ("FlextCliConstantsExceptions",),
        ".files": ("FlextCliConstantsFiles",),
        ".output": ("FlextCliConstantsOutput",),
        ".pipeline": ("FlextCliConstantsPipeline",),
        ".settings": ("FlextCliConstantsSettings",),
    },
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, publish_all=False)

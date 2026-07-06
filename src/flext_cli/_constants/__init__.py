# AUTO-GENERATED FILE — Regenerate with: make gen
"""Constants package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._constants.base import FlextCliConstantsBase
    from flext_cli._constants.enums import FlextCliConstantsEnums
    from flext_cli._constants.errors import FlextCliConstantsErrors
    from flext_cli._constants.exceptions import FlextCliConstantsExceptions
    from flext_cli._constants.files import FlextCliConstantsFiles
    from flext_cli._constants.output import FlextCliConstantsOutput
    from flext_cli._constants.pipeline import FlextCliConstantsPipeline
    from flext_cli._constants.settings import FlextCliConstantsSettings
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


install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)

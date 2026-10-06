# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli. Constants package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli._constants.base import FlextCliConstantsBase
    from flext_cli._constants.config import FlextCliConstantsConfig
    from flext_cli._constants.defaults import FlextCliConstantsDefaults
    from flext_cli._constants.docx import FlextCliConstantsDocx
    from flext_cli._constants.enums import FlextCliConstantsEnums
    from flext_cli._constants.errors import FlextCliConstantsErrors
    from flext_cli._constants.files import FlextCliConstantsFiles
    from flext_cli._constants.output import FlextCliConstantsOutput
    from flext_cli._constants.pptx import FlextCliConstantsPptx
    from flext_cli._constants.settings import FlextCliConstantsSettings
    from flext_cli._constants.xlsx import FlextCliConstantsXlsx
    from flext_cli._constants.xlsx_future_functions import (
        FlextCliConstantsXlsxFutureFunctions,
    )


__all__: tuple[str, ...] = (
    "FlextCliConstantsBase",
    "FlextCliConstantsConfig",
    "FlextCliConstantsDefaults",
    "FlextCliConstantsDocx",
    "FlextCliConstantsEnums",
    "FlextCliConstantsErrors",
    "FlextCliConstantsFiles",
    "FlextCliConstantsOutput",
    "FlextCliConstantsPptx",
    "FlextCliConstantsSettings",
    "FlextCliConstantsXlsx",
    "FlextCliConstantsXlsxFutureFunctions",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliConstantsBase": ".base",
        "FlextCliConstantsConfig": ".config",
        "FlextCliConstantsDefaults": ".defaults",
        "FlextCliConstantsDocx": ".docx",
        "FlextCliConstantsEnums": ".enums",
        "FlextCliConstantsErrors": ".errors",
        "FlextCliConstantsFiles": ".files",
        "FlextCliConstantsOutput": ".output",
        "FlextCliConstantsPptx": ".pptx",
        "FlextCliConstantsSettings": ".settings",
        "FlextCliConstantsXlsx": ".xlsx",
        "FlextCliConstantsXlsxFutureFunctions": ".xlsx_future_functions",
    }),
    public_exports=__all__,
)

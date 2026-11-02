# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli.services package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.services.auth import FlextCliAuth
    from flext_cli.services.cli import FlextCliCli
    from flext_cli.services.cli_params import FlextCliCommonParams
    from flext_cli.services.docx import FlextCliDocx
    from flext_cli.services.file_tools import FlextCliFileTools
    from flext_cli.services.formatters import FlextCliFormatters
    from flext_cli.services.output import FlextCliOutput
    from flext_cli.services.pipeline import FlextCliPipeline
    from flext_cli.services.pptx import FlextCliPptx
    from flext_cli.services.prompts import FlextCliPrompts
    from flext_cli.services.runtime import FlextCliRuntime
    from flext_cli.services.tables import FlextCliTables
    from flext_cli.services.xlsx import FlextCliXlsx


__all__: tuple[str, ...] = (
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCommonParams",
    "FlextCliDocx",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliOutput",
    "FlextCliPipeline",
    "FlextCliPptx",
    "FlextCliPrompts",
    "FlextCliRuntime",
    "FlextCliTables",
    "FlextCliXlsx",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliAuth": ".auth",
        "FlextCliCli": ".cli",
        "FlextCliCommonParams": ".cli_params",
        "FlextCliDocx": ".docx",
        "FlextCliFileTools": ".file_tools",
        "FlextCliFormatters": ".formatters",
        "FlextCliOutput": ".output",
        "FlextCliPipeline": ".pipeline",
        "FlextCliPptx": ".pptx",
        "FlextCliPrompts": ".prompts",
        "FlextCliRuntime": ".runtime",
        "FlextCliTables": ".tables",
        "FlextCliXlsx": ".xlsx",
    }),
    public_exports=__all__,
)

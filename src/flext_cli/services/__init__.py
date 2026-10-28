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
    from flext_cli.services._cli.flextcliservicecli_part_01 import FlextCliCliPart01
    from flext_cli.services._cli.flextcliservicecli_part_02 import FlextCliCliPart02
    from flext_cli.services._cli.flextcliservicecli_part_03 import FlextCliCliPart03
    from flext_cli.services._cli.flextcliservicecli_part_04 import FlextCliCliPart04
    from flext_cli.services._cli.flextcliservicecli_part_05 import FlextCliCliPart05
    from flext_cli.services._cli.flextcliservicecli_part_06 import FlextCliCliPart06
    from flext_cli.services._prompts.support import FlextCliServicesPromptsSupport
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
    "FlextCliCliPart01",
    "FlextCliCliPart02",
    "FlextCliCliPart03",
    "FlextCliCliPart04",
    "FlextCliCliPart05",
    "FlextCliCliPart06",
    "FlextCliCommonParams",
    "FlextCliDocx",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliOutput",
    "FlextCliPipeline",
    "FlextCliPptx",
    "FlextCliPrompts",
    "FlextCliRuntime",
    "FlextCliServicesPromptsSupport",
    "FlextCliTables",
    "FlextCliXlsx",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliAuth": ".auth",
        "FlextCliCli": ".cli",
        "FlextCliCliPart01": "._cli.flextcliservicecli_part_01",
        "FlextCliCliPart02": "._cli.flextcliservicecli_part_02",
        "FlextCliCliPart03": "._cli.flextcliservicecli_part_03",
        "FlextCliCliPart04": "._cli.flextcliservicecli_part_04",
        "FlextCliCliPart05": "._cli.flextcliservicecli_part_05",
        "FlextCliCliPart06": "._cli.flextcliservicecli_part_06",
        "FlextCliCommonParams": ".cli_params",
        "FlextCliDocx": ".docx",
        "FlextCliFileTools": ".file_tools",
        "FlextCliFormatters": ".formatters",
        "FlextCliOutput": ".output",
        "FlextCliPipeline": ".pipeline",
        "FlextCliPptx": ".pptx",
        "FlextCliPrompts": ".prompts",
        "FlextCliServicesPromptsSupport": "._prompts.support",
        "FlextCliRuntime": ".runtime",
        "FlextCliTables": ".tables",
        "FlextCliXlsx": ".xlsx",
    }),
    public_exports=__all__,
)

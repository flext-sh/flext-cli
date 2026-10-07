# AUTO-GENERATED FILE — Regenerate with: make gen
"""Flext Cli.services package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_cli.services import _cli_parts
    from flext_cli.services._cli_parts.flextclicli_part_01 import FlextCliCliPart01
    from flext_cli.services._cli_parts.flextclicli_part_02 import FlextCliCliPart02
    from flext_cli.services._cli_parts.flextclicli_part_03 import FlextCliCliPart03
    from flext_cli.services._cli_parts.flextclicli_part_04 import FlextCliCliPart04
    from flext_cli.services._cli_parts.flextclicli_part_05 import FlextCliCliPart05
    from flext_cli.services._cli_parts.flextclicli_part_06 import FlextCliCliPart06
    from flext_cli.services._prompts_support import FlextCliPromptsSupport
    from flext_cli.services.auth import FlextCliAuth
    from flext_cli.services.cli import FlextCliCli
    from flext_cli.services.cli_params import FlextCliCommonParams
    from flext_cli.services.cmd import FlextCliCmd
    from flext_cli.services.docx import FlextCliDocx
    from flext_cli.services.file_tools import FlextCliFileTools
    from flext_cli.services.formatters import FlextCliFormatters
    from flext_cli.services.output import FlextCliOutput
    from flext_cli.services.pipeline import FlextCliPipeline
    from flext_cli.services.pptx import FlextCliPptx
    from flext_cli.services.prompts import FlextCliPrompts
    from flext_cli.services.rules import FlextCliRules
    from flext_cli.services.runtime import FlextCliRuntime
    from flext_cli.services.tables import FlextCliTables
    from flext_cli.services.xlsx import FlextCliXlsx
    from flext_cli.services.yaml_model import FlextCliYamlModel


__all__: tuple[str, ...] = (
    "FlextCliAuth",
    "FlextCliCli",
    "FlextCliCliPart01",
    "FlextCliCliPart02",
    "FlextCliCliPart03",
    "FlextCliCliPart04",
    "FlextCliCliPart05",
    "FlextCliCliPart06",
    "FlextCliCmd",
    "FlextCliCommonParams",
    "FlextCliDocx",
    "FlextCliFileTools",
    "FlextCliFormatters",
    "FlextCliOutput",
    "FlextCliPipeline",
    "FlextCliPptx",
    "FlextCliPrompts",
    "FlextCliPromptsSupport",
    "FlextCliRules",
    "FlextCliRuntime",
    "FlextCliTables",
    "FlextCliXlsx",
    "FlextCliYamlModel",
    "_cli_parts",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "FlextCliAuth": ".auth",
        "FlextCliCli": ".cli",
        "FlextCliCliPart01": "._cli_parts.flextclicli_part_01",
        "FlextCliCliPart02": "._cli_parts.flextclicli_part_02",
        "FlextCliCliPart03": "._cli_parts.flextclicli_part_03",
        "FlextCliCliPart04": "._cli_parts.flextclicli_part_04",
        "FlextCliCliPart05": "._cli_parts.flextclicli_part_05",
        "FlextCliCliPart06": "._cli_parts.flextclicli_part_06",
        "FlextCliCmd": ".cmd",
        "FlextCliCommonParams": ".cli_params",
        "FlextCliDocx": ".docx",
        "FlextCliFileTools": ".file_tools",
        "FlextCliFormatters": ".formatters",
        "FlextCliOutput": ".output",
        "FlextCliPipeline": ".pipeline",
        "FlextCliPptx": ".pptx",
        "FlextCliPrompts": ".prompts",
        "FlextCliPromptsSupport": "._prompts_support",
        "FlextCliRules": ".rules",
        "FlextCliRuntime": ".runtime",
        "FlextCliTables": ".tables",
        "FlextCliXlsx": ".xlsx",
        "FlextCliYamlModel": ".yaml_model",
        "_cli_parts": "._cli_parts",
    }),
    public_exports=__all__,
)

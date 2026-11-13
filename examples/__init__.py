# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from flext_core import d, e, h, r, x

    from examples.constants import ExamplesFlextCliConstants, c
    from examples.ex_01_getting_started import ExamplesFlextCliGettingStarted
    from examples.ex_02_output_formatting import ExamplesFlextCliOutputFormatting
    from examples.ex_04_file_operations import ExamplesFlextCliFileOperations
    from examples.ex_05_authentication import ExamplesFlextCliAuthentication
    from examples.ex_06_settings import ExamplesFlextCliSettings
    from examples.ex_11_complete_integration import ExamplesFlextCliDataManager
    from examples.ex_12_pydantic_driven_cli import ExamplesFlextCliPydanticDrivenCli
    from examples.ex_13_single_result_command import ExamplesFlextCliSingleResultCommand
    from examples.models import ExamplesFlextCliModels, m
    from examples.protocols import ExamplesFlextCliProtocols, p
    from examples.typings import ExamplesFlextCliTypes, t
    from examples.utilities import ExamplesFlextCliUtilities, u
    from flext_cli import cli, config, main, s, settings


__all__: tuple[str, ...] = (
    "ExamplesFlextCliAuthentication",
    "ExamplesFlextCliConstants",
    "ExamplesFlextCliDataManager",
    "ExamplesFlextCliFileOperations",
    "ExamplesFlextCliGettingStarted",
    "ExamplesFlextCliModels",
    "ExamplesFlextCliOutputFormatting",
    "ExamplesFlextCliProtocols",
    "ExamplesFlextCliPydanticDrivenCli",
    "ExamplesFlextCliSettings",
    "ExamplesFlextCliSingleResultCommand",
    "ExamplesFlextCliTypes",
    "ExamplesFlextCliUtilities",
    "c",
    "cli",
    "config",
    "d",
    "e",
    "h",
    "m",
    "main",
    "p",
    "r",
    "s",
    "settings",
    "t",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    {
        "ExamplesFlextCliAuthentication": ".ex_05_authentication",
        "ExamplesFlextCliConstants": ".constants",
        "ExamplesFlextCliDataManager": ".ex_11_complete_integration",
        "ExamplesFlextCliFileOperations": ".ex_04_file_operations",
        "ExamplesFlextCliGettingStarted": ".ex_01_getting_started",
        "ExamplesFlextCliModels": ".models",
        "ExamplesFlextCliOutputFormatting": ".ex_02_output_formatting",
        "ExamplesFlextCliProtocols": ".protocols",
        "ExamplesFlextCliPydanticDrivenCli": ".ex_12_pydantic_driven_cli",
        "ExamplesFlextCliSettings": ".ex_06_settings",
        "ExamplesFlextCliSingleResultCommand": ".ex_13_single_result_command",
        "ExamplesFlextCliTypes": ".typings",
        "ExamplesFlextCliUtilities": ".utilities",
        "c": ".constants",
        "cli": "flext_cli",
        "config": "flext_cli",
        "d": "flext_core",
        "e": "flext_core",
        "h": "flext_core",
        "m": ".models",
        "main": "flext_cli",
        "p": ".protocols",
        "r": "flext_core",
        "s": "flext_cli",
        "settings": "flext_cli",
        "t": ".typings",
        "u": ".utilities",
        "x": "flext_core",
    },
    public_exports=__all__,
)

# AUTO-GENERATED FILE — Regenerate with: make gen
"""Examples package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
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
    from examples.models import ExamplesFlextCliModels, m
    from examples.protocols import ExamplesFlextCliProtocols, p
    from examples.typings import ExamplesFlextCliTypes, t
    from examples.utilities import ExamplesFlextCliUtilities, u
    from flext_cli import (
        build_lazy_import_map,
        cleanup_submodule_namespace,
        cli,
        config,
        core,
        install_lazy_exports,
        lazy,
        lazy_getattr,
        lazy_member,
        main,
        merge_lazy_imports,
        normalize_lazy_imports,
        resolve_lazy_members,
        s,
        settings,
    )


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
    "ExamplesFlextCliTypes",
    "ExamplesFlextCliUtilities",
    "build_lazy_import_map",
    "c",
    "cleanup_submodule_namespace",
    "cli",
    "config",
    "core",
    "d",
    "e",
    "h",
    "install_lazy_exports",
    "lazy",
    "lazy_getattr",
    "lazy_member",
    "m",
    "main",
    "merge_lazy_imports",
    "normalize_lazy_imports",
    "p",
    "r",
    "resolve_lazy_members",
    "s",
    "settings",
    "t",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
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
        "ExamplesFlextCliTypes": ".typings",
        "ExamplesFlextCliUtilities": ".utilities",
        "build_lazy_import_map": "flext_cli",
        "c": ".constants",
        "cleanup_submodule_namespace": "flext_cli",
        "cli": "flext_cli",
        "config": "flext_cli",
        "core": "flext_cli",
        "d": "flext_core",
        "e": "flext_core",
        "h": "flext_core",
        "install_lazy_exports": "flext_cli",
        "lazy": "flext_cli",
        "lazy_getattr": "flext_cli",
        "lazy_member": "flext_cli",
        "m": ".models",
        "main": "flext_cli",
        "merge_lazy_imports": "flext_cli",
        "normalize_lazy_imports": "flext_cli",
        "p": ".protocols",
        "r": "flext_core",
        "resolve_lazy_members": "flext_cli",
        "s": "flext_cli",
        "settings": "flext_cli",
        "t": ".typings",
        "u": ".utilities",
        "x": "flext_core",
    }),
    public_exports=__all__,
)

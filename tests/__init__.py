# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from examples import (
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
        settings,
    )
    from flext_core import d, e, h, r, x
    from flext_tests import api, install_local_packages, td, tf, tk, tm

    from tests.base import TestsFlextCliServiceBase, s
    from tests.constants import TestsFlextCliConstants, c
    from tests.models import TestsFlextCliModels, m
    from tests.protocols import TestsFlextCliProtocols, p
    from tests.settings import TestsFlextCliSettings
    from tests.test_pptx_render import TestsFlextCliPptxRender
    from tests.test_xlsx_archive import TestsFlextCliXlsxArchive
    from tests.typings import TestsFlextCliTypes, t
    from tests.utilities import TestsFlextCliUtilities, u


__all__: tuple[str, ...] = (
    "TestsFlextCliConstants",
    "TestsFlextCliModels",
    "TestsFlextCliPptxRender",
    "TestsFlextCliProtocols",
    "TestsFlextCliServiceBase",
    "TestsFlextCliSettings",
    "TestsFlextCliTypes",
    "TestsFlextCliUtilities",
    "TestsFlextCliXlsxArchive",
    "api",
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
    "install_local_packages",
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
    "td",
    "tf",
    "tk",
    "tm",
    "u",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextCliConstants": ".constants",
        "TestsFlextCliModels": ".models",
        "TestsFlextCliPptxRender": ".test_pptx_render",
        "TestsFlextCliProtocols": ".protocols",
        "TestsFlextCliServiceBase": ".base",
        "TestsFlextCliSettings": ".settings",
        "TestsFlextCliTypes": ".typings",
        "TestsFlextCliUtilities": ".utilities",
        "TestsFlextCliXlsxArchive": ".test_xlsx_archive",
        "api": "flext_tests",
        "build_lazy_import_map": "examples",
        "c": ".constants",
        "cleanup_submodule_namespace": "examples",
        "cli": "examples",
        "config": "examples",
        "core": "examples",
        "d": "flext_core",
        "e": "flext_core",
        "h": "flext_core",
        "install_lazy_exports": "examples",
        "install_local_packages": "flext_tests",
        "lazy": "examples",
        "lazy_getattr": "examples",
        "lazy_member": "examples",
        "m": ".models",
        "main": "examples",
        "merge_lazy_imports": "examples",
        "normalize_lazy_imports": "examples",
        "p": ".protocols",
        "r": "flext_core",
        "resolve_lazy_members": "examples",
        "s": ".base",
        "settings": "examples",
        "t": ".typings",
        "td": "flext_tests",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "x": "flext_core",
    }),
    public_exports=__all__,
)

# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import api, td, tf, tk, tm

    from flext_core import d, e, h, r, x
    from tests import fixtures, unit
    from tests.base import TestsFlextCliServiceBase, s
    from tests.constants import TestsFlextCliConstants, c
    from tests.models import TestsFlextCliModels, m
    from tests.protocols import TestsFlextCliProtocols, p
    from tests.settings import TestsFlextCliSettings
    from tests.typings import TestsFlextCliTypes, t
    from tests.utilities import TestsFlextCliUtilities, u


__all__: tuple[str, ...] = (
    "TestsFlextCliConstants",
    "TestsFlextCliModels",
    "TestsFlextCliProtocols",
    "TestsFlextCliServiceBase",
    "TestsFlextCliSettings",
    "TestsFlextCliTypes",
    "TestsFlextCliUtilities",
    "api",
    "c",
    "d",
    "e",
    "fixtures",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "u",
    "unit",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("TestsFlextCliServiceBase", "s"),
            ".constants": ("TestsFlextCliConstants", "c"),
            ".fixtures": ("fixtures",),
            ".models": ("TestsFlextCliModels", "m"),
            ".protocols": ("TestsFlextCliProtocols", "p"),
            ".settings": ("TestsFlextCliSettings",),
            ".typings": ("TestsFlextCliTypes", "t"),
            ".unit": ("unit",),
            ".utilities": ("TestsFlextCliUtilities", "u"),
            "flext_core": ("d", "e", "h", "r", "x"),
            "flext_tests": ("api", "td", "tf", "tk", "tm"),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    ),
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

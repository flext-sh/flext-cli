# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import d, e, h, r, td, tf, tk, tm, tv, x

    from .base import TestsFlextCliServiceBase, TestsFlextCliServiceBase as s
    from .constants import TestsFlextCliConstants, TestsFlextCliConstants as c
    from .models import TestsFlextCliModels, TestsFlextCliModels as m
    from .protocols import TestsFlextCliProtocols, TestsFlextCliProtocols as p
    from .settings import TestsFlextCliSettings
    from .typings import TestsFlextCliTypes, TestsFlextCliTypes as t
    from .utilities import TestsFlextCliUtilities, TestsFlextCliUtilities as u

    _ = (
        d,
        e,
        h,
        r,
        td,
        tf,
        tk,
        tm,
        tv,
        x,
        TestsFlextCliServiceBase,
        s,
        TestsFlextCliConstants,
        c,
        TestsFlextCliModels,
        m,
        TestsFlextCliProtocols,
        p,
        TestsFlextCliSettings,
        TestsFlextCliTypes,
        t,
        TestsFlextCliUtilities,
        u,
    )


_LAZY_MODULES: dict[str, tuple[str, ...]] = {
    ".base": ("TestsFlextCliServiceBase", "s"),
    ".constants": ("TestsFlextCliConstants", "c"),
    ".models": ("TestsFlextCliModels", "m"),
    ".protocols": ("TestsFlextCliProtocols", "p"),
    ".settings": ("TestsFlextCliSettings",),
    ".typings": ("TestsFlextCliTypes", "t"),
    ".utilities": ("TestsFlextCliUtilities", "u"),
    "flext_tests": ("d", "e", "h", "r", "td", "tf", "tk", "tm", "tv", "x"),
}


_LAZY_ALIAS_GROUPS: dict[str, tuple[tuple[str, str], ...]] = {}


_LAZY_IMPORTS = build_lazy_import_map(
    _LAZY_MODULES, alias_groups=_LAZY_ALIAS_GROUPS, sort_keys=False
)

_DIRECT_IMPORTS: tuple[str, ...] = (
    "TestsFlextCliConstants",
    "TestsFlextCliModels",
    "TestsFlextCliProtocols",
    "TestsFlextCliServiceBase",
    "TestsFlextCliSettings",
    "TestsFlextCliTypes",
    "TestsFlextCliUtilities",
    "build_lazy_import_map",
    "c",
    "d",
    "e",
    "h",
    "install_lazy_exports",
    "m",
    "p",
    "r",
    "s",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "tv",
    "u",
    "x",
)

__all__: tuple[str, ...] = (
    "TestsFlextCliConstants",
    "TestsFlextCliModels",
    "TestsFlextCliProtocols",
    "TestsFlextCliServiceBase",
    "TestsFlextCliSettings",
    "TestsFlextCliTypes",
    "TestsFlextCliUtilities",
    "c",
    "d",
    "e",
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
    "tv",
    "u",
    "x",
)


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

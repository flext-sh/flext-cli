# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import (
        api,
        config,
        from_json,
        install_local_packages,
        load_infra_report,
        services,
        settings,
        td,
        tf,
        tk,
        tm,
        to_json,
        to_jsonable_python,
        tv,
    )

    from flext_cli import cli, main
    from flext_core import core, d, e, h, lazy_attribute, r, x

    from . import unit
    from .base import TestsFlextCliServiceBase, TestsFlextCliServiceBase as s
    from .constants import TestsFlextCliConstants, c
    from .models import TestsFlextCliModels, m
    from .protocols import TestsFlextCliProtocols, p
    from .settings import TestsFlextCliSettings
    from .typings import TestsFlextCliTypes, t
    from .utilities import TestsFlextCliUtilities, u
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
    "cli",
    "config",
    "core",
    "d",
    "e",
    "from_json",
    "h",
    "install_local_packages",
    "lazy_attribute",
    "load_infra_report",
    "m",
    "main",
    "p",
    "r",
    "s",
    "services",
    "settings",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
    "to_json",
    "to_jsonable_python",
    "tv",
    "u",
    "unit",
    "x",
)

_LAZY_IMPORTS = MappingProxyType(
    build_lazy_import_map(
        MappingProxyType({
            ".base": ("TestsFlextCliServiceBase", "s"),
            ".constants": ("TestsFlextCliConstants", "c"),
            ".models": ("TestsFlextCliModels", "m"),
            ".protocols": ("TestsFlextCliProtocols", "p"),
            ".settings": ("TestsFlextCliSettings",),
            ".typings": ("TestsFlextCliTypes", "t"),
            ".unit": ("unit",),
            ".utilities": ("TestsFlextCliUtilities", "u"),
            "flext_cli": ("cli", "main"),
            "flext_core": ("core", "d", "e", "h", "lazy_attribute", "r", "x"),
            "flext_tests": (
                "api",
                "config",
                "from_json",
                "install_local_packages",
                "load_infra_report",
                "services",
                "settings",
                "td",
                "tf",
                "tk",
                "tm",
                "to_json",
                "to_jsonable_python",
                "tv",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

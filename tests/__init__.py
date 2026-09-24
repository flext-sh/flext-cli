# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_infra import docs_main, infra
    from flext_tests import (
        active_rules,
        api,
        config,
        discover_repository_root,
        install_local_packages,
        load_infra_report,
        settings,
        split_csv,
        td,
        tf,
        tk,
        tm,
        tv,
    )

    from flext_cli import cli, main
    from flext_core import core, d, e, h, lazy_attribute, r, x

    from . import unit
    from .base import TestsFlextCliServiceBase, TestsFlextCliServiceBase as s
    from .constants import TestsFlextCliConstants, TestsFlextCliConstants as c
    from .models import TestsFlextCliModels, m
    from .protocols import TestsFlextCliProtocols, TestsFlextCliProtocols as p
    from .settings import TestsFlextCliSettings
    from .typings import TestsFlextCliTypes, TestsFlextCliTypes as t
    from .utilities import TestsFlextCliUtilities, u


__all__: tuple[str, ...] = (
    "TestsFlextCliConstants",
    "TestsFlextCliModels",
    "TestsFlextCliProtocols",
    "TestsFlextCliServiceBase",
    "TestsFlextCliSettings",
    "TestsFlextCliTypes",
    "TestsFlextCliUtilities",
    "active_rules",
    "api",
    "c",
    "d",
    "discover_repository_root",
    "docs_main",
    "e",
    "h",
    "infra",
    "install_local_packages",
    "lazy_attribute",
    "load_infra_report",
    "m",
    "p",
    "r",
    "s",
    "settings",
    "split_csv",
    "t",
    "td",
    "tf",
    "tk",
    "tm",
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
            "flext_infra": ("docs_main", "infra"),
            "flext_tests": (
                "active_rules",
                "api",
                "config",
                "discover_repository_root",
                "install_local_packages",
                "load_infra_report",
                "settings",
                "split_csv",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
            ),
        }),
        alias_groups=MappingProxyType({}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

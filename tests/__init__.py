# AUTO-GENERATED FILE — canonical lazy tests facade. Regenerate with: make gen
"""Test package facade exposing the project test aliases lazily."""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from tests.constants import TestsFlextCliConstants as TestsFlextCliConstants, c as c
    from tests.typings import TestsFlextCliTypes as TestsFlextCliTypes, t as t
    from tests.protocols import TestsFlextCliProtocols as TestsFlextCliProtocols, p
    from tests.models import TestsFlextCliModels as TestsFlextCliModels, m as m
    from tests.utilities import TestsFlextCliUtilities as TestsFlextCliUtilities, u
    from tests.base import TestsFlextCliServiceBase as TestsFlextCliServiceBase, s as s

_LAZY_IMPORTS = build_lazy_import_map(
    {
        ".constants": ("TestsFlextCliConstants", "c"),
        ".typings": ("TestsFlextCliTypes", "t"),
        ".protocols": ("TestsFlextCliProtocols", "p"),
        ".models": ("TestsFlextCliModels", "m"),
        ".utilities": ("TestsFlextCliUtilities", "u"),
        ".base": ("TestsFlextCliServiceBase", "s"),
    },
)

install_lazy_exports(
    __name__,
    globals(),
    _LAZY_IMPORTS,
    publish_all=False,
)

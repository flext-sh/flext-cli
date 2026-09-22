# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package."""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core.lazy import build_lazy_import_map, install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import FlextTestsConstants, d, e, h, r, td, tf, tk, tm, tv, x

    from flext_cli import c as flext_cli_c

    from . import unit
    from .base import TestsFlextCliServiceBase, TestsFlextCliServiceBase as s
    from .constants import TestsFlextCliConstants, TestsFlextCliConstants as c
    from .models import TestsFlextCliModels, TestsFlextCliModels as m
    from .protocols import TestsFlextCliProtocols, TestsFlextCliProtocols as p
    from .settings import TestsFlextCliSettings
    from .test_xlsx_range import (
        test_xlsx_format_reference_collapses_equal_bounds_and_rejects_inversion,
        test_xlsx_format_reference_exposes_every_typed_rendering_mode,
        test_xlsx_parse_range_fails_loud_for_non_concrete_or_inverted_input,
        test_xlsx_parse_range_returns_typed_concrete_bounds,
    )
    from .test_yaml_model_write import (
        test_write_yaml_model_round_trips_the_same_model_contract,
    )
    from .typings import TestsFlextCliTypes, TestsFlextCliTypes as t
    from .utilities import TestsFlextCliUtilities, TestsFlextCliUtilities as u
__all__: tuple[str, ...] = (
    "FlextTestsConstants",
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
    "flext_cli_c",
    "h",
    "m",
    "p",
    "r",
    "s",
    "t",
    "td",
    "test_write_yaml_model_round_trips_the_same_model_contract",
    "test_xlsx_format_reference_collapses_equal_bounds_and_rejects_inversion",
    "test_xlsx_format_reference_exposes_every_typed_rendering_mode",
    "test_xlsx_parse_range_fails_loud_for_non_concrete_or_inverted_input",
    "test_xlsx_parse_range_returns_typed_concrete_bounds",
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
            ".test_xlsx_range": (
                "test_xlsx_format_reference_collapses_equal_bounds_and_rejects_inversion",
                "test_xlsx_format_reference_exposes_every_typed_rendering_mode",
                "test_xlsx_parse_range_fails_loud_for_non_concrete_or_inverted_input",
                "test_xlsx_parse_range_returns_typed_concrete_bounds",
            ),
            ".test_yaml_model_write": (
                "test_write_yaml_model_round_trips_the_same_model_contract",
            ),
            ".typings": ("TestsFlextCliTypes", "t"),
            ".unit": ("unit",),
            ".utilities": ("TestsFlextCliUtilities", "u"),
            "flext_tests": (
                "FlextTestsConstants",
                "d",
                "e",
                "h",
                "r",
                "td",
                "tf",
                "tk",
                "tm",
                "tv",
                "x",
            ),
        }),
        alias_groups=MappingProxyType({"flext_cli": (("flext_cli_c", "c"),)}),
        sort_keys=False,
    )
)

install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, public_exports=__all__)

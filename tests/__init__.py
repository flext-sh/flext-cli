# AUTO-GENERATED FILE — Regenerate with: make gen
"""Tests package.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from types import MappingProxyType
from typing import TYPE_CHECKING

from flext_core import install_lazy_exports

if TYPE_CHECKING:
    from flext_tests import api, td, tf, tk, tm

    from flext_core import d, e, h, r, x
    from tests import _constants_parts, _models_parts, fixtures, unit
    from tests.base import TestsFlextCliServiceBase, s
    from tests.constants import TestsFlextCliConstants, c
    from tests.models import TestsFlextCliModels, m
    from tests.protocols import TestsFlextCliProtocols, p
    from tests.settings import TestsFlextCliSettings
    from tests.test_xlsx_range import (
        test_xlsx_format_reference_collapses_equal_bounds_and_rejects_inversion,
        test_xlsx_format_reference_exposes_every_typed_rendering_mode,
        test_xlsx_parse_range_fails_loud_for_non_concrete_or_inverted_input,
        test_xlsx_parse_range_returns_typed_concrete_bounds,
    )
    from tests.test_yaml_model_write import (
        test_write_yaml_model_round_trips_the_same_model_contract,
    )
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
    "_constants_parts",
    "_models_parts",
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
    "test_write_yaml_model_round_trips_the_same_model_contract",
    "test_xlsx_format_reference_collapses_equal_bounds_and_rejects_inversion",
    "test_xlsx_format_reference_exposes_every_typed_rendering_mode",
    "test_xlsx_parse_range_fails_loud_for_non_concrete_or_inverted_input",
    "test_xlsx_parse_range_returns_typed_concrete_bounds",
    "tf",
    "tk",
    "tm",
    "u",
    "unit",
    "x",
)

install_lazy_exports(
    __name__,
    globals(),
    MappingProxyType({
        "TestsFlextCliConstants": ".constants",
        "TestsFlextCliModels": ".models",
        "TestsFlextCliProtocols": ".protocols",
        "TestsFlextCliServiceBase": ".base",
        "TestsFlextCliSettings": ".settings",
        "TestsFlextCliTypes": ".typings",
        "TestsFlextCliUtilities": ".utilities",
        "_constants_parts": "._constants_parts",
        "_models_parts": "._models_parts",
        "api": "flext_tests",
        "c": ".constants",
        "d": "flext_core",
        "e": "flext_core",
        "fixtures": ".fixtures",
        "h": "flext_core",
        "m": ".models",
        "p": ".protocols",
        "r": "flext_core",
        "s": ".base",
        "t": ".typings",
        "td": "flext_tests",
        "test_write_yaml_model_round_trips_the_same_model_contract": (
            ".test_yaml_model_write"
        ),
        "test_xlsx_format_reference_collapses_equal_bounds_and_rejects_inversion": (
            ".test_xlsx_range"
        ),
        "test_xlsx_format_reference_exposes_every_typed_rendering_mode": (
            ".test_xlsx_range"
        ),
        "test_xlsx_parse_range_fails_loud_for_non_concrete_or_inverted_input": (
            ".test_xlsx_range"
        ),
        "test_xlsx_parse_range_returns_typed_concrete_bounds": ".test_xlsx_range",
        "tf": "flext_tests",
        "tk": "flext_tests",
        "tm": "flext_tests",
        "u": ".utilities",
        "unit": ".unit",
        "x": "flext_core",
    }),
    public_exports=__all__,
)

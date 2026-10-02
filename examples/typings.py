"""FLEXT CLI example type aliases.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import ClassVar

from flext_cli import FlextCli, t
from flext_core import u


class ExamplesFlextCliTypes(t):
    """Public examples type facade extending flext-cli types."""

    type EnvValue = t.JsonValue
    type EnvInput = t.MappingKV[str, EnvValue] | EnvValue | None
    type ExampleModelInput = t.MappingKV[str, EnvValue] | EnvValue | None
    type CliApi = FlextCli

    type DataProcessor = Callable[[str], str]
    type ProcessorRegistry = t.MappingKV[str, DataProcessor]
    JSON_DICT_ADAPTER: ClassVar[t.ValueAdapter[t.JsonMapping]] = u.type_adapter(
        t.JsonMapping,
    )


t = ExamplesFlextCliTypes

__all__: list[str] = ["ExamplesFlextCliTypes", "t"]

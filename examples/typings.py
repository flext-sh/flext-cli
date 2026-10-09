"""FLEXT CLI example type aliases.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Annotated, ClassVar

from flext_cli import FlextCli, FlextCliTypes
from flext_core import u


class ExamplesFlextCliTypes(FlextCliTypes):
    """Public examples type facade extending flext-cli types."""

    type EnvValue = FlextCliTypes.JsonValue
    type EnvInput = FlextCliTypes.MappingKV[str, EnvValue] | EnvValue | None
    type ExampleModelInput = FlextCliTypes.MappingKV[str, EnvValue] | EnvValue | None
    type CliApi = FlextCli

    type DataProcessor = Callable[[str], str]
    type ProcessorRegistry = FlextCliTypes.MappingKV[str, DataProcessor]
    type JsonDictAdapter = FlextCliTypes.ValueAdapter[FlextCliTypes.JsonMapping]

    JSON_DICT_ADAPTER: ClassVar[JsonDictAdapter] = u.type_adapter(
        Annotated[FlextCliTypes.JsonMapping, None],
    )


t = ExamplesFlextCliTypes

__all__: list[str] = ["ExamplesFlextCliTypes", "t"]

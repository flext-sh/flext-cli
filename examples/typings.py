"""FLEXT CLI example type aliases.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Mapping

from flext_cli import FlextCli, FlextCliTypes


class ExamplesFlextCliTypes(FlextCliTypes):
    """Public examples type facade extending flext-cli types."""

    type EnvValue = FlextCliTypes.JsonValue
    type EnvInput = Mapping[str, EnvValue] | EnvValue | None
    type ExampleModelInput = Mapping[str, EnvValue] | EnvValue | None
    type CliApi = FlextCli

    type DataProcessor = Callable[[str], str]
    type ProcessorRegistry = Mapping[str, DataProcessor]
    type JsonDictAdapter = FlextCliTypes.ValueAdapter[FlextCliTypes.JsonMapping]


t = ExamplesFlextCliTypes

__all__: list[str] = ["ExamplesFlextCliTypes", "t"]

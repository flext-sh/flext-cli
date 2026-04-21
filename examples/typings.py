"""FLEXT CLI example type aliases."""

from __future__ import annotations

from collections.abc import (
    Callable,
    Mapping,
)
from typing import ClassVar

from flext_core import m

from flext_cli import FlextCli, t


class ExamplesFlextCliTypes(t):
    """Public examples type facade extending flext-cli types."""

    type EnvValue = t.Cli.JsonValue | t.Container
    type EnvInput = Mapping[str, EnvValue] | EnvValue | None
    type ExampleModelInput = Mapping[str, EnvValue] | EnvValue | None
    type CliApi = FlextCli

    type DataProcessor = Callable[[str], str]
    type ProcessorRegistry = Mapping[str, DataProcessor]
    JSON_DICT_ADAPTER: ClassVar[t.ValueAdapter[t.Cli.JsonMapping]] = m.TypeAdapter(
        t.Cli.JsonMapping,
    )


t = ExamplesFlextCliTypes

__all__: list[str] = [
    "ExamplesFlextCliTypes",
    "t",
]

"""FLEXT CLI example type aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import ClassVar

from pydantic import (
    TypeAdapter,
)

from flext_cli import FlextCli, t
from flext_core import m


class ExamplesFlextCliTypes(t):
    """Public examples type facade extending flext-cli types."""

    type EnvValue = t.RecursiveContainer
    type EnvInput = t.RecursiveContainerMapping | t.Container | None
    type ModelInput = t.RecursiveContainerMapping | t.Container | None
    type CliApi = FlextCli

    type DataProcessor = Callable[[str], str]
    type ProcessorRegistry = Mapping[str, DataProcessor]
    JSON_DICT_ADAPTER: ClassVar[m.TypeAdapter[t.RecursiveContainerMapping]] = (
        TypeAdapter(
            t.RecursiveContainerMapping,
        )
    )


t = ExamplesFlextCliTypes

__all__: list[str] = [
    "ExamplesFlextCliTypes",
    "t",
]

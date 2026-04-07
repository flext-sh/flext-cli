"""FLEXT CLI example type aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import ClassVar

from pydantic import (
    TypeAdapter,
)

from flext_cli import FlextCli, t


class FlextCliExamplesTypes(t):
    """Public examples type facade extending flext-cli types."""

    type EnvValue = t.RecursiveContainer
    type EnvInput = t.ContainerMapping | t.Container | None
    type ModelInput = t.ContainerMapping | t.Container | None
    type CliApi = FlextCli

    type DataProcessor = Callable[[str], str]
    type ProcessorRegistry = Mapping[str, DataProcessor]
    JSON_DICT_ADAPTER: ClassVar[TypeAdapter[t.ContainerMapping]] = TypeAdapter(
        t.ContainerMapping,
    )


t = FlextCliExamplesTypes

__all__ = [
    "FlextCliExamplesTypes",
    "t",
]

"""FLEXT CLI example type aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import ClassVar

from pydantic import (
    TypeAdapter,
)

from flext_cli import FlextCli, FlextCliTypes


class FlextCliExamplesTypes(FlextCliTypes):
    """Public examples type facade extending flext-cli types."""

    type EnvInput = FlextCliTypes.ContainerMapping | FlextCliTypes.Primitives | None
    type CliApi = FlextCli

    type DataProcessor = Callable[[str], str]
    type ProcessorRegistry = Mapping[str, DataProcessor]
    JSON_DICT_ADAPTER: ClassVar[TypeAdapter[FlextCliTypes.ContainerMapping]] = (
        TypeAdapter(
            FlextCliTypes.ContainerMapping,
        )
    )


t = FlextCliExamplesTypes

__all__ = [
    "FlextCliExamplesTypes",
    "t",
]

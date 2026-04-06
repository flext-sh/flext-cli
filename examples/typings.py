"""FLEXT CLI example type aliases."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import ClassVar

from pydantic import (
    TypeAdapter,
)

from flext_cli import FlextCli, t as _cli_t


class FlextCliExamplesTypes(_cli_t):
    """Public examples type facade extending flext-cli types."""

    type EnvInput = _cli_t.ContainerMapping | _cli_t.Primitives | None
    type CliApi = FlextCli

    type DataProcessor = Callable[[str], str]
    type ProcessorRegistry = Mapping[str, DataProcessor]
    JSON_DICT_ADAPTER: ClassVar[TypeAdapter[_cli_t.ContainerMapping]] = TypeAdapter(
        _cli_t.ContainerMapping,
    )


t = FlextCliExamplesTypes

__all__ = [
    "FlextCliExamplesTypes",
    "t",
]

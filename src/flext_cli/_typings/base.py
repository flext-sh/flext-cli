"""CLI base type aliases.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from collections.abc import Callable, Mapping, MutableMapping, Sequence
from pathlib import Path
from types import FrameType, GenericAlias

from flext_core import t
from jinja2.sandbox import SandboxedEnvironment
from tomlkit.container import Container
from tomlkit.items import AoT, Array, Item, Table
from tomlkit.toml_document import TOMLDocument
from typing_extensions import TypeForm


class FlextCliTypesBase:
    """Base CLI aliases shared across services and models."""

    type TableMappingRow = Mapping[str, t.JsonPayload]
    type TableSequenceRow = Sequence[t.JsonPayload]
    type DefaultMapping = Mapping[str, t.Scalar | Sequence[str]]
    type TableRow = TableMappingRow | TableSequenceRow
    type TableConfigValue = (
        t.JsonValue | Sequence[str] | Sequence[int] | Sequence[str | int] | None
    )
    type TabularData = TableMappingRow | Sequence[TableRow]
    type TableRows = Sequence[TableRow]
    type TableIndexValue = str | int
    type TableIndexSelection = Sequence[TableIndexValue]
    type TableShowIndex = bool | TableIndexSelection
    type TableDisableNumparse = bool | Sequence[int]
    type TableColAlign = Sequence[str] | None
    type CliValue = t.Scalar | Sequence[str] | DefaultMapping
    type CliDefaultSource = CliValue | Sequence[str | int] | Path
    type CliAnnotations = MutableMapping[str, type | GenericAlias]
    type TomlDocument = TOMLDocument
    type TomlTable = Table
    type TomlItem = Item
    type TomlArray = Array
    type TomlAoT = AoT
    type TomlContainer = Container
    type TomlParent = TOMLDocument | Table
    type TomlValue = TOMLDocument | Table | Item | Array | AoT | Container
    type RuntimeAnnotation = TypeForm
    type SignalHandler = int | Callable[[int, FrameType | None], None] | None
    type TemplateEnvironmentCache = MutableMapping[str, SandboxedEnvironment]


__all__: list[str] = ["FlextCliTypesBase"]

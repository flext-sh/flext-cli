"""CLI base type aliases and adapters.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, MutableMapping
from pathlib import Path
from types import FrameType, GenericAlias
from typing import Any, ClassVar

from jinja2.sandbox import SandboxedEnvironment
from tomlkit.container import Container
from tomlkit.items import AoT, Array, Item, Table
from tomlkit.toml_document import TOMLDocument
from typing_extensions import TypeForm

from flext_core import t, u


class FlextCliTypesBase:
    """Base CLI aliases shared across services and models."""

    type TableMappingRow = t.MappingKV[str, t.JsonPayload]
    type TableSequenceRow = t.SequenceOf[t.JsonPayload]
    type DefaultMapping = t.MappingKV[str, t.Scalar | t.StrSequence]
    type TableRow = TableMappingRow | TableSequenceRow
    type TableConfigValue = (
        t.JsonValue | t.StrSequence | t.SequenceOf[int] | t.SequenceOf[str | int] | None
    )
    type TabularData = TableMappingRow | t.SequenceOf[TableRow]
    type TableRows = t.SequenceOf[TableRow]
    type TableIndexValue = str | int
    type TableIndexSelection = t.SequenceOf[TableIndexValue]
    type TableShowIndex = bool | TableIndexSelection
    type TableDisableNumparse = bool | t.SequenceOf[int]
    type TableColAlign = t.StrSequence | None
    type CliValue = t.Scalar | t.StrSequence | DefaultMapping
    type CliDefaultSource = CliValue | t.SequenceOf[str | int] | Path
    type CliAnnotations = MutableMapping[str, type | GenericAlias]
    type TomlDocument = TOMLDocument
    type TomlTable = Table
    type TomlItem = Item
    type TomlArray = Array
    type TomlAoT = AoT
    type TomlContainer = Container
    type TomlParent = TOMLDocument | Table
    type TomlValue = TOMLDocument | Table | Item | Array | AoT | Container
    type RuntimeAnnotation = TypeForm[Any]
    type SignalHandler = int | Callable[[int, FrameType | None], None] | None
    type TemplateEnvironmentCache = MutableMapping[str, SandboxedEnvironment]

    STR_SEQUENCE_ADAPTER: ClassVar[t.ValueAdapter[t.StrSequence]] = (
        t.str_sequence_adapter()
    )
    JSON_VALUE_ADAPTER: ClassVar[t.ValueAdapter[t.JsonValue]] = t.json_value_adapter()
    JSON_MAPPING_ADAPTER: ClassVar[t.ValueAdapter[t.JsonMapping]] = (
        t.json_mapping_adapter()
    )
    JSON_LIST_ADAPTER: ClassVar[t.ValueAdapter[t.JsonList]] = t.json_list_adapter()
    YAML_DICT_ADAPTER: ClassVar[t.ValueAdapter[t.JsonMapping]] = (
        t.json_mapping_adapter()
    )
    YAML_SEQ_ADAPTER: ClassVar[t.ValueAdapter[t.JsonList]] = t.json_list_adapter()
    CLI_DEFAULT_SOURCE_ADAPTER: ClassVar[t.ValueAdapter[CliDefaultSource]] = (
        u.type_adapter(CliValue | t.SequenceOf[str | int] | Path)
    )


__all__: list[str] = ["FlextCliTypesBase"]

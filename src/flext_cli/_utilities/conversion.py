"""CLI conversion helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence, Sequence
from pathlib import Path
from types import MappingProxyType
from typing import ClassVar

from flext_core import u

from flext_cli import c, t


class FlextCliUtilitiesConversion:
    """Conversion methods exposed directly on ``u.Cli``."""

    _EMPTY_JSON_MAPPING: ClassVar[t.JsonMapping] = MappingProxyType({})

    STR_SEQUENCE_ADAPTER: ClassVar[t.ValueAdapter[Sequence[str]]] = u.type_adapter(
        t.TypeForm(Sequence[str])
    )
    JSON_VALUE_ADAPTER: ClassVar[t.ValueAdapter[t.JsonValue]] = u.type_adapter(
        t.TypeForm(t.JsonValue)
    )
    JSON_MAPPING_ADAPTER: ClassVar[t.ValueAdapter[t.JsonMapping]] = u.type_adapter(
        t.TypeForm(t.JsonMapping)
    )
    JSON_LIST_ADAPTER: ClassVar[t.ValueAdapter[t.JsonList]] = u.type_adapter(
        t.TypeForm(t.JsonList)
    )
    YAML_DICT_ADAPTER: ClassVar[t.ValueAdapter[t.JsonMapping]] = u.type_adapter(
        t.TypeForm(t.JsonMapping)
    )
    YAML_SEQ_ADAPTER: ClassVar[t.ValueAdapter[t.JsonList]] = u.type_adapter(
        t.TypeForm(t.JsonList)
    )
    CLI_DEFAULT_SOURCE_ADAPTER: ClassVar[t.ValueAdapter[t.Cli.CliDefaultSource]] = (
        u.type_adapter(t.TypeForm(t.Cli.CliDefaultSource))
    )

    @staticmethod
    def default_for_type_kind(
        type_kind: t.Cli.TypeKind,
        default: t.JsonValue | None,
    ) -> t.Cli.TypedExtractValue:
        """Return a canonical default for one type kind.

        Returns:
            A canonical default for one type kind.

        """
        if type_kind == c.Cli.TypeKind.STR:
            return default if isinstance(default, str) else ""
        if type_kind == c.Cli.TypeKind.BOOL:
            return default if isinstance(default, bool) else False
        if isinstance(default, Mapping):
            return {
                key: FlextCliUtilitiesConversion.JSON_VALUE_ADAPTER.validate_python(
                    value
                )
                for key, value in default.items()
            }
        return FlextCliUtilitiesConversion._EMPTY_JSON_MAPPING

    @staticmethod
    def resolve_optional_path(value: t.Cli.TextPath | None, *, default: Path) -> Path:
        """Resolve an optional text/path value while preserving a default path.

        Returns:
            The resulting ``Path``.

        """
        if isinstance(value, Path):
            return value
        normalized = FlextCliUtilitiesConversion.normalize_optional_text(value)
        if normalized is not None:
            return Path(normalized)
        return default

    @staticmethod
    def normalize_optional_text(value: t.JsonValue | Path) -> str | None:
        """Normalize optional text-like values, preserving ``None`` for empties.

        Returns:
            The resulting ``str | None``.

        """
        if isinstance(value, Path):
            return str(value)
        normalized = u.norm_str(value, default="").strip()
        if not normalized:
            return None
        return normalized

    @staticmethod
    def normalize_required_text(value: t.JsonValue | Path, *, default: str) -> str:
        """Normalize required text-like values, falling back to ``default``.

        Returns:
            The resulting ``str``.

        """
        normalized = FlextCliUtilitiesConversion.normalize_optional_text(value)
        return normalized if normalized is not None else default


__all__: MutableSequence[str] = ["FlextCliUtilitiesConversion"]

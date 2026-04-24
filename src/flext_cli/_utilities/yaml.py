"""Generic YAML helpers shared through ``u.Cli.yaml_*``.

Follows the same pattern as ``toml.py`` — generic operations that any
project can reuse, prefixed with ``yaml_`` for namespace clarity.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Sequence,
)
from pathlib import Path
from typing import ClassVar

from flext_core import m, u
from yaml import safe_dump, safe_load

from flext_cli import c, p, r, t


class FlextCliUtilitiesYaml:
    """Generic YAML read, parse, dump, and validation helpers.

    All YAML operations across the workspace delegate here.
    Projects needing domain-specific normalization wrap these methods.
    """

    _module_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)

    # ------------------------------------------------------------------
    # Reading
    # ------------------------------------------------------------------

    @staticmethod
    def yaml_safe_load(path: Path) -> p.Result[t.JsonMapping]:
        """Load a YAML file → ``r[JsonMapping]``.

        Returns ``r.ok(mapping)`` on success, ``r.fail(msg)`` on missing,
        parse error, or non-mapping content.

        Example::

            data = u.Cli.yaml_safe_load(path).unwrap_or({})
        """
        if not path.is_file():
            return r[t.JsonMapping].fail(f"YAML file not found: {path}")
        try:
            raw = path.read_text(encoding=c.Cli.ENCODING_DEFAULT)
        except OSError as exc:
            return r[t.Cli.YamlDict].fail(f"YAML read error: {exc}")
        return FlextCliUtilitiesYaml.yaml_parse(raw)

    @staticmethod
    def yaml_parse(text: str) -> p.Result[t.Cli.YamlDict]:
        """Parse a YAML string → ``r[JsonMapping]``.

        Returns a validated mapping or failure.
        """
        try:
            parsed = safe_load(text)
        except t.Cli.YAMLError as exc:
            return r[t.JsonMapping].fail(f"YAML parse error: {exc}")
        if parsed is None:
            return r[t.JsonMapping].ok({})
        if not u.mapping(parsed):
            return r[t.JsonMapping].fail(
                f"YAML content is not a mapping: {type(parsed).__name__}",
            )
        try:
            validated = t.Cli.YAML_DICT_ADAPTER.validate_python(parsed)
        except c.ValidationError as exc:
            return r[t.JsonMapping].fail(f"YAML validation error: {exc}")
        return r[t.JsonMapping].ok(validated)

    @staticmethod
    def yaml_load_mapping(
        path: Path,
        *,
        default: t.JsonMapping | None = None,
    ) -> t.JsonMapping:
        """Load YAML file returning a mapping, or *default* (empty dict) on any error.

        Ergonomic shorthand — use ``yaml_safe_load`` when you need ``r[T]`` semantics.
        """
        return FlextCliUtilitiesYaml.yaml_safe_load(path).unwrap_or(
            default if default is not None else {},
        )

    @staticmethod
    def yaml_load_list(path: Path) -> Sequence[t.JsonValue]:
        """Load YAML file expecting a list at top level."""
        if not path.is_file():
            return []
        try:
            raw = path.read_text(encoding=c.Cli.ENCODING_DEFAULT)
            parsed = safe_load(raw)
        except (OSError, t.Cli.YAMLError):
            return []
        if not isinstance(parsed, list):
            return []
        try:
            validated: Sequence[t.JsonValue] = t.Cli.YAML_SEQ_ADAPTER.validate_python(
                parsed,
            )
        except c.ValidationError:
            return []
        return validated

    # ------------------------------------------------------------------
    # Writing
    # ------------------------------------------------------------------

    @staticmethod
    def yaml_dump(
        path: Path,
        data: t.JsonPayload,
        *,
        sort_keys: bool = False,
        indent: int = 2,
    ) -> p.Result[bool]:
        """Write *data* to a YAML file → ``r[bool]``.

        Creates parent directories if needed.

        Example::

            u.Cli.yaml_dump(path, {"key": "val"})
        """
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            raw = (
                data.model_dump(mode="json") if isinstance(data, m.BaseModel) else data
            )
            with path.open("w", encoding=c.Cli.ENCODING_DEFAULT) as fh:
                safe_dump(
                    u.to_jsonable_python(raw),
                    fh,
                    default_flow_style=False,
                    sort_keys=sort_keys,
                    allow_unicode=True,
                    indent=indent,
                )
            return r[bool].ok(True)
        except (OSError, t.Cli.YAMLError, ValueError, TypeError) as exc:
            return r[bool].fail(f"YAML write error: {exc}")

    @staticmethod
    def yaml_dump_str(
        data: t.JsonPayload,
        *,
        sort_keys: bool = False,
        indent: int = 2,
    ) -> str:
        """Serialize *data* to a YAML string.

        Returns empty string on serialization failure.

        Example::

            text = u.Cli.yaml_dump_str(payload)
        """
        try:
            raw = (
                data.model_dump(mode="json") if isinstance(data, m.BaseModel) else data
            )
            return safe_dump(
                u.to_jsonable_python(raw),
                default_flow_style=False,
                sort_keys=sort_keys,
                allow_unicode=True,
                indent=indent,
            )
        except (t.Cli.YAMLError, ValueError, TypeError):
            return ""


__all__: t.MutableSequenceOf[str] = ["FlextCliUtilitiesYaml"]

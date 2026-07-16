"""Round-trip YAML engine and load/dump surface behind ``u.Cli.yaml_*``.

Owns the comment-preserving ``ruamel.yaml`` engine singleton and the ``r[T]``
load/dump operations. Composed into ``FlextCliUtilitiesYaml`` via MRO in
``yaml.py``.

NOTE (multi-agent): mro-i6nq.13 — extracted from the removed
``_yaml_roundtrip_parts/..._part_01`` (engine + load/dump half). The
conversion helpers live in ``_yaml/_convert.py``; do not re-create a second
ruamel engine in a leaf module.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import io
from typing import TYPE_CHECKING, TextIO

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap

from flext_cli import c, p, r, t

from ._convert import FlextCliUtilitiesYamlConvertMixin

if TYPE_CHECKING:
    from pathlib import Path


class _YamlRoundtripEngine:
    """Shared ruamel.yaml engine configured for comment-preserving round-trips."""

    def __init__(self) -> None:
        self._yaml = ruamel.yaml.YAML()
        self._yaml.preserve_quotes = True
        self._yaml.width = 4096
        self._yaml.indent(mapping=2, sequence=4, offset=2)

    def load(self, source: TextIO | str) -> t.Cli.YamlValue:
        """Load one YAML document from a stream or raw text."""
        loaded: t.Cli.YamlValue = self._yaml.load(source)
        return loaded

    def dump(self, data: t.Cli.YamlNode, stream: TextIO) -> None:
        """Serialize a YAML tree to a stream."""
        self._yaml.dump(data, stream)


_ROUNDTRIP_YAML = _YamlRoundtripEngine()


class FlextCliUtilitiesYamlEngineMixin(FlextCliUtilitiesYamlConvertMixin):
    """Round-trip (comment/quote-preserving) YAML load/dump surface.

    Loading and dumping return ``r[T]`` so parse and validation failures
    propagate as typed failures, never as silent defaults.
    """

    @staticmethod
    def yaml_roundtrip_load(path: Path) -> p.Result[t.Cli.YamlNode]:
        """Load a YAML file preserving comments/quoting -> ``r[YamlNode]``."""
        if not path.is_file():
            return r[t.Cli.YamlNode].fail(f"YAML file not found: {path}")
        try:
            with path.open("r", encoding=c.Cli.ENCODING_DEFAULT) as fh:
                loaded = _ROUNDTRIP_YAML.load(fh)
            node = FlextCliUtilitiesYamlEngineMixin._yaml_coerce_node(loaded)
        except OSError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML read error: {exc}")
        except c.Cli.YamlRoundtripError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML parse error: {exc}")
        except TypeError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML content error: {exc}")
        if node is None:
            return r[t.Cli.YamlNode].fail("YAML document is empty (no content)")
        return r[t.Cli.YamlNode].ok(node)

    @staticmethod
    def yaml_roundtrip_load_text(text: str) -> p.Result[t.Cli.YamlNode]:
        """Parse YAML text preserving comments/quoting -> ``r[YamlNode]``."""
        try:
            loaded = _ROUNDTRIP_YAML.load(text)
            node = FlextCliUtilitiesYamlEngineMixin._yaml_coerce_node(loaded)
        except c.Cli.YamlRoundtripError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML parse error: {exc}")
        except TypeError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML content error: {exc}")
        if node is None:
            return r[t.Cli.YamlNode].fail("YAML document is empty (no content)")
        return r[t.Cli.YamlNode].ok(node)

    @staticmethod
    def yaml_roundtrip_load_map(path: Path) -> p.Result[CommentedMap]:
        """Load a YAML file and require a mapping root -> ``r[CommentedMap]``."""
        loaded = FlextCliUtilitiesYamlEngineMixin.yaml_roundtrip_load(path)
        if not loaded.success:
            message = (
                loaded.error if loaded.error is not None else f"YAML load error: {path}"
            )
            return r[CommentedMap].fail(message)
        node = loaded.unwrap()
        if not isinstance(node, CommentedMap):
            return r[CommentedMap].fail(f"{path}: YAML document must be a mapping")
        return r[CommentedMap].ok(node)

    @staticmethod
    def yaml_roundtrip_load_map_text(text: str) -> p.Result[CommentedMap]:
        """Parse YAML text and require a mapping root -> ``r[CommentedMap]``."""
        loaded = FlextCliUtilitiesYamlEngineMixin.yaml_roundtrip_load_text(text)
        if not loaded.success:
            message = (
                loaded.error if loaded.error is not None else "YAML text parse error"
            )
            return r[CommentedMap].fail(message)
        node = loaded.unwrap()
        if not isinstance(node, CommentedMap):
            return r[CommentedMap].fail("YAML text: YAML document must be a mapping")
        return r[CommentedMap].ok(node)

    @staticmethod
    def yaml_roundtrip_dump(data: t.Cli.YamlNode, stream: TextIO) -> p.Result[bool]:
        """Serialize a YAML tree to *stream* -> ``r[bool]``."""
        try:
            _ROUNDTRIP_YAML.dump(data, stream)
        except (OSError, c.Cli.YamlRoundtripError, TypeError, ValueError) as exc:
            return r[bool].fail(f"YAML dump error: {exc}")
        return r[bool].ok(True)

    @staticmethod
    def yaml_roundtrip_dump_text(data: t.Cli.YamlNode) -> p.Result[str]:
        """Serialize a YAML tree to text -> ``r[str]``."""
        buffer = io.StringIO()
        dumped = FlextCliUtilitiesYamlEngineMixin.yaml_roundtrip_dump(data, buffer)
        if not dumped.success:
            message = dumped.error if dumped.error is not None else "YAML dump error"
            return r[str].fail(message)
        return r[str].ok(buffer.getvalue())


__all__: list[str] = ["FlextCliUtilitiesYamlEngineMixin"]

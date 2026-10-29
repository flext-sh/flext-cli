"""Round-trip YAML engine and load/dump surface behind ``u.Cli.yaml_*``.

Builds fresh comment-preserving ``ruamel.yaml`` engines per load/dump call
and owns the ``r[T]`` load/dump operations. Composed into
``FlextCliUtilitiesYaml`` via MRO in ``yaml.py``.

NOTE (multi-agent): mro-i6nq.13 — extracted from the removed
``_yaml_roundtrip_parts/..._part_01`` (engine + load/dump half). The
conversion helpers live in ``_yaml/_convert.py``; do not re-create a second
ruamel engine in a leaf module.

NOTE (multi-agent): ai-hub-gwbu.1 — ruamel ``YAML`` instances keep mutable
reader/scanner state during a parse and are not thread-safe. A module-level
shared instance corrupted concurrent loads under ``crg-maintain --jobs 3``
(``IndexError: string index out of range`` in ``ruamel/yaml/reader.py``).
Engines are therefore built per call; never reintroduce a shared instance.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import io
from collections.abc import Callable, Sequence
from typing import TYPE_CHECKING, TextIO

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.error import YAMLError

from flext_cli import c, p, r, t
from flext_cli._utilities._yaml import FlextCliUtilitiesYamlConvert

if TYPE_CHECKING:
    from pathlib import Path


class FlextCliUtilitiesYamlEngine(FlextCliUtilitiesYamlConvert):
    """Round-trip (comment/quote-preserving) YAML load/dump surface.

    Loading and dumping return ``r[T]`` so parse and validation failures
    propagate as typed failures, never as silent defaults.
    """

    @staticmethod
    def _roundtrip_yaml() -> p.Cli.YamlRoundtripEngine:
        """Build a fresh comment/quote-preserving round-trip engine.

        A new instance per call keeps load/dump operations thread-safe: ruamel
        stores mutable parser state on the instance while parsing. The returned
        surface is returned through the typed ``p.Cli.YamlRoundtripEngine``
        contract, which ``ruamel.yaml.YAML`` satisfies structurally.

        Returns:
            The resulting ``p.Cli.YamlRoundtripEngine``.

        """
        yaml = ruamel.yaml.YAML()
        yaml.preserve_quotes = True
        yaml.width = 4096
        yaml.indent(mapping=2, sequence=4, offset=2)
        return yaml

    @staticmethod
    def yaml_roundtrip_load(path: Path) -> p.Result[t.Cli.YamlNode]:
        """Load a YAML file preserving comments/quoting -> ``r[YamlNode]``.

        Returns:
            The resulting ``p.Result[t.Cli.YamlNode]``.

        """
        if not path.is_file():
            return r[t.Cli.YamlNode].fail(f"YAML file not found: {path}")

        def produce() -> t.Cli.YamlValue:
            with path.open("r", encoding=c.DEFAULT_ENCODING) as fh:
                return FlextCliUtilitiesYamlEngine._roundtrip_yaml().load(fh)

        try:
            return FlextCliUtilitiesYamlEngine._load_node(produce)
        except OSError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML read error: {exc}", exception=exc)

    @staticmethod
    def _load_node(produce: Callable[[], t.Cli.YamlValue]) -> p.Result[t.Cli.YamlNode]:
        """Load, coerce, and validate one YAML document through the engine.

        Returns:
            The resulting ``p.Result[t.Cli.YamlNode]``.

        """
        try:
            node = FlextCliUtilitiesYamlEngine._yaml_coerce_node(produce())
        except YAMLError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML parse error: {exc}", exception=exc)
        except TypeError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML content error: {exc}", exception=exc)
        if node is None:
            return r[t.Cli.YamlNode].fail("YAML document is empty (no content)")
        return r[t.Cli.YamlNode].ok(node)

    @staticmethod
    def yaml_roundtrip_load_text(text: str) -> p.Result[t.Cli.YamlNode]:
        """Parse YAML text preserving comments/quoting -> ``r[YamlNode]``.

        Returns:
            The resulting ``p.Result[t.Cli.YamlNode]``.

        """
        return FlextCliUtilitiesYamlEngine._load_node(
            lambda: FlextCliUtilitiesYamlEngine._roundtrip_yaml().load(text),
        )

    @staticmethod
    def yaml_roundtrip_load_all_text(
        text: str,
    ) -> p.Result[Sequence[t.Cli.YamlNode]]:
        """Parse every YAML document with one fresh canonical engine.

        Returns:
            The complete document sequence, or the original parsing failure.

        """
        try:
            engine = FlextCliUtilitiesYamlEngine._roundtrip_yaml()
            nodes = tuple(
                FlextCliUtilitiesYamlEngine._yaml_coerce_node(value)
                for value in engine.load_all(text)
            )
        except YAMLError as exc:
            return r[Sequence[t.Cli.YamlNode]].fail(
                f"YAML parse error: {exc}", exception=exc
            )
        except TypeError as exc:
            return r[Sequence[t.Cli.YamlNode]].fail(
                f"YAML content error: {exc}", exception=exc
            )
        return r[Sequence[t.Cli.YamlNode]].ok(nodes)

    @staticmethod
    def yaml_roundtrip_load_map_text(text: str) -> p.Result[CommentedMap]:
        """Parse YAML text and require a mapping root -> ``r[CommentedMap]``.

        Returns:
            The resulting ``p.Result[CommentedMap]``.

        """
        loaded = FlextCliUtilitiesYamlEngine.yaml_roundtrip_load_text(text)
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
        """Serialize a YAML tree to *stream* -> ``r[bool]``.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        try:
            FlextCliUtilitiesYamlEngine._roundtrip_yaml().dump(data, stream)
        except (OSError, YAMLError, TypeError, ValueError) as exc:
            return r[bool].fail(f"YAML dump error: {exc}", exception=exc)
        return r[bool].ok(value=True)

    @staticmethod
    def yaml_roundtrip_dump_text(data: t.Cli.YamlNode) -> p.Result[str]:
        """Serialize a YAML tree to text -> ``r[str]``.

        Returns:
            The resulting ``p.Result[str]``.

        """
        buffer = io.StringIO()
        dumped = FlextCliUtilitiesYamlEngine.yaml_roundtrip_dump(data, buffer)
        if not dumped.success:
            message = dumped.error if dumped.error is not None else "YAML dump error"
            return r[str].fail(message)
        return r[str].ok(buffer.getvalue())


__all__: list[str] = ["FlextCliUtilitiesYamlEngine"]

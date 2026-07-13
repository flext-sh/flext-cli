"""Round-trip YAML load/dump and conversion helpers behind ``u.Cli.yaml_*``.

Part 01 owns the comment-preserving ``ruamel.yaml`` engine, the ``r[T]``
load/dump surface, and plain<->commented conversions. This lifts the domain
contract proven by cosmos-charts ``yaml_utils`` into the shared facade
(operator order: YAML serialization goes ONLY through the flext-cli facade).

NOTE (multi-agent): composed into ``FlextCliUtilitiesYaml`` via MRO in
``yaml.py``. Do not create a second ruamel engine in a leaf module — extend
these parts instead.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import io
from collections.abc import Mapping
from typing import (
    TYPE_CHECKING,
    ClassVar,
    SupportsFloat,
    SupportsIndex,
    SupportsInt,
    TextIO,
    TypeGuard,
    cast,
    overload,
)

import ruamel.yaml
from ruamel.yaml.comments import CommentedMap, CommentedSeq
from ruamel.yaml.scalarstring import DoubleQuotedScalarString, LiteralScalarString

from flext_cli import c, p, r, t
from flext_core import u

if TYPE_CHECKING:
    from pathlib import Path

#: YAML 1.1 boolean/null tokens that must be quoted to survive a round-trip.
#: Single consumer (``yaml_deep_to_commented``); promote to ``c.Cli`` if a
#: second consumer appears. NOTE (multi-agent): domain data, not a lint token.
_YAML_1_1_IMPLICIT_STRING_VALUES = frozenset({
    "y",
    "yes",
    "n",
    "no",
    "true",
    "false",
    "on",
    "off",
    "null",
    "~",
})


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


class FlextCliUtilitiesYamlRoundtrip:
    """Round-trip (comment/quote-preserving) YAML load/dump and conversion.

    Every operation is exposed through ``u.Cli`` after MRO composition into
    ``FlextCliUtilitiesYaml``. Loading and dumping return ``r[T]`` so parse and
    validation failures propagate as typed failures, never as silent defaults.
    """

    _module_logger: ClassVar[p.Logger] = u.fetch_logger(__name__)

    # ------------------------------------------------------------------
    # Loading
    # ------------------------------------------------------------------

    @staticmethod
    def yaml_roundtrip_load(path: Path) -> p.Result[t.Cli.YamlNode]:
        """Load a YAML file preserving comments/quoting -> ``r[YamlNode]``.

        Returns ``r.ok(node)`` on success, ``r.fail(msg)`` on missing file,
        read error, parse error, or unsupported root type.
        """
        if not path.is_file():
            return r[t.Cli.YamlNode].fail(f"YAML file not found: {path}")
        try:
            with path.open("r", encoding=c.Cli.ENCODING_DEFAULT) as fh:
                loaded = _ROUNDTRIP_YAML.load(fh)
            node = FlextCliUtilitiesYamlRoundtrip._yaml_coerce_node(loaded)
        except OSError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML read error: {exc}")
        except c.Cli.YamlRoundtripError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML parse error: {exc}")
        except TypeError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML content error: {exc}")
        return r[t.Cli.YamlNode].ok(node)

    @staticmethod
    def yaml_roundtrip_load_text(text: str) -> p.Result[t.Cli.YamlNode]:
        """Parse YAML text preserving comments/quoting -> ``r[YamlNode]``."""
        try:
            loaded = _ROUNDTRIP_YAML.load(text)
            node = FlextCliUtilitiesYamlRoundtrip._yaml_coerce_node(loaded)
        except c.Cli.YamlRoundtripError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML parse error: {exc}")
        except TypeError as exc:
            return r[t.Cli.YamlNode].fail(f"YAML content error: {exc}")
        return r[t.Cli.YamlNode].ok(node)

    @staticmethod
    def yaml_roundtrip_load_map(path: Path) -> p.Result[CommentedMap]:
        """Load a YAML file and require a mapping root -> ``r[CommentedMap]``."""
        loaded = FlextCliUtilitiesYamlRoundtrip.yaml_roundtrip_load(path)
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
        loaded = FlextCliUtilitiesYamlRoundtrip.yaml_roundtrip_load_text(text)
        if not loaded.success:
            message = (
                loaded.error if loaded.error is not None else "YAML text parse error"
            )
            return r[CommentedMap].fail(message)
        node = loaded.unwrap()
        if not isinstance(node, CommentedMap):
            return r[CommentedMap].fail("YAML text: YAML document must be a mapping")
        return r[CommentedMap].ok(node)

    # ------------------------------------------------------------------
    # Dumping
    # ------------------------------------------------------------------

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
        dumped = FlextCliUtilitiesYamlRoundtrip.yaml_roundtrip_dump(data, buffer)
        if not dumped.success:
            message = dumped.error if dumped.error is not None else "YAML dump error"
            return r[str].fail(message)
        return r[str].ok(buffer.getvalue())

    # ------------------------------------------------------------------
    # Conversion
    # ------------------------------------------------------------------

    @staticmethod
    def yaml_to_plain(data: t.Cli.YamlNode) -> t.Cli.YamlValue:
        """Recursively convert ruamel containers into plain Python values."""
        if isinstance(data, dict):
            return {
                key: FlextCliUtilitiesYamlRoundtrip.yaml_to_plain(value)
                for key, value in data.items()
            }
        if isinstance(data, list):
            return [FlextCliUtilitiesYamlRoundtrip.yaml_to_plain(item) for item in data]
        return data

    @overload
    @staticmethod
    def yaml_deep_to_commented(data: CommentedMap) -> CommentedMap: ...

    @overload
    @staticmethod
    def yaml_deep_to_commented(data: CommentedSeq) -> CommentedSeq: ...

    @overload
    @staticmethod
    def yaml_deep_to_commented(data: Mapping[str, t.Cli.YamlValue]) -> CommentedMap: ...

    @overload
    @staticmethod
    def yaml_deep_to_commented(data: list[t.Cli.YamlValue]) -> CommentedSeq: ...

    @overload
    @staticmethod
    def yaml_deep_to_commented(data: t.Cli.YamlScalar) -> t.Cli.YamlScalar: ...

    @staticmethod
    def yaml_deep_to_commented(data: t.Cli.YamlValue) -> t.Cli.YamlNode:
        """Recursively convert plain dict/list into CommentedMap/CommentedSeq.

        Existing CommentedMap/CommentedSeq nodes are preserved. Multi-line
        strings become LiteralScalarString; YAML 1.1 implicit string tokens are
        double-quoted so they survive a round-trip as strings.
        """
        if isinstance(data, CommentedMap | CommentedSeq):
            return data
        if isinstance(data, Mapping):
            node = CommentedMap()
            for key, value in data.items():
                node[key] = FlextCliUtilitiesYamlRoundtrip.yaml_deep_to_commented(value)
            return node
        if FlextCliUtilitiesYamlRoundtrip.yaml_is_sequence(data):
            return CommentedSeq(
                FlextCliUtilitiesYamlRoundtrip.yaml_deep_to_commented(item)
                for item in data
            )
        if isinstance(data, str):
            if "\n" in data:
                return cast("t.Cli.YamlScalar", LiteralScalarString(data))
            if data.lower() in _YAML_1_1_IMPLICIT_STRING_VALUES:
                return cast("t.Cli.YamlScalar", DoubleQuotedScalarString(data))
        if data is not None and not isinstance(data, (str, int, float, bool)):
            msg = f"unsupported YAML value type: {type(data).__name__}"
            raise TypeError(msg)
        return data

    @staticmethod
    def yaml_is_sequence(value: t.Cli.YamlValue) -> TypeGuard[t.Cli.YamlSequence]:
        """Return True for YAML sequence nodes while keeping strings scalar.

        NOTE (multi-agent): deliberately excludes ``tuple`` (unlike the legacy
        charts helper) — ``t.Cli.YamlValue`` cannot type a tuple, so a runtime
        tuple now fails loud in ``yaml_deep_to_commented`` instead of being
        silently treated as a sequence.
        """
        return isinstance(value, (CommentedSeq, list))

    # ------------------------------------------------------------------
    # Scalar normalization (unwrap ruamel scalar subclasses)
    # ------------------------------------------------------------------

    @staticmethod
    def yaml_normalize_scalar(value: t.Cli.YamlValue) -> t.Cli.YamlValue:
        """Normalize ruamel scalar wrappers to plain Python scalars."""
        if isinstance(value, str):
            return FlextCliUtilitiesYamlRoundtrip.yaml_plain_str(value)
        if isinstance(value, bool):
            return FlextCliUtilitiesYamlRoundtrip.yaml_plain_bool(value)
        if isinstance(value, int):
            return FlextCliUtilitiesYamlRoundtrip.yaml_plain_int(value)
        if isinstance(value, float):
            return FlextCliUtilitiesYamlRoundtrip.yaml_plain_float(value)
        return value

    @staticmethod
    def yaml_plain_str(value: t.Cli.YamlScalar) -> str:
        """Return *value* as a plain builtin str (unwrap ruamel subclasses)."""
        return value if type(value) is str else str(value)

    @staticmethod
    def yaml_plain_bool(value: t.Cli.YamlScalar) -> bool:
        """Return *value* as a plain builtin bool (unwrap ruamel subclasses)."""
        return value if type(value) is bool else bool(value)

    @staticmethod
    def yaml_plain_int(value: SupportsInt | SupportsIndex) -> int:
        """Return *value* as a plain builtin int (unwrap ruamel subclasses).

        NOTE (multi-agent): ``SupportsInt | SupportsIndex`` is the real domain
        contract — only ``int`` and ruamel int subclasses (which implement both
        protocols) arrive here. Never widen to ``object`` (hides str/object and
        breaks the 4-checker gate).
        """
        return value if type(value) is int else int(value)

    @staticmethod
    def yaml_plain_float(value: SupportsFloat | SupportsIndex) -> float:
        """Return *value* as a plain builtin float (unwrap ruamel subclasses).

        NOTE (multi-agent): same contract as ``yaml_plain_int`` — keep the
        ``SupportsFloat | SupportsIndex`` union; never widen to ``object``.
        """
        return value if type(value) is float else float(value)

    # ------------------------------------------------------------------
    # Internal validation
    # ------------------------------------------------------------------

    @staticmethod
    def _yaml_coerce_node(value: t.Cli.YamlValue) -> t.Cli.YamlNode:
        """Validate a parsed ruamel root against the supported node contract."""
        if isinstance(value, (CommentedMap, CommentedSeq, str, int, float, bool)):
            return value
        if value is None:
            return None
        if isinstance(
            value, Mapping
        ) or FlextCliUtilitiesYamlRoundtrip.yaml_is_sequence(value):
            return FlextCliUtilitiesYamlRoundtrip.yaml_deep_to_commented(value)
        msg = f"unsupported YAML root type: {type(value).__name__}"
        raise TypeError(msg)


__all__: list[str] = ["FlextCliUtilitiesYamlRoundtrip"]

"""FLEXT CLI Typings Tests - public type-facade contract.

Modules tested: flext_cli.typings.FlextCliTypes (via the tests `t` facade).

These tests assert the OBSERVABLE contract of the CLI type facade: the
runtime-validatable behaviour of its published type aliases and the public
``TypeAdapter`` / type-tuple ClassVars exposed on ``t.Cli``. No private
attributes, internal collaborators, or implementation structure are touched.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest
from flext_tests import tm

from tests import m, p, t


class TestsFlextCliTypings:
    """Behavioural contract of flext_cli.typings.FlextCliTypes."""

    # --- Published CLI adapters: accept valid payloads -------------------

    @pytest.mark.parametrize(
        ("payload", "expected"),
        [(["alpha", "beta"], ["alpha", "beta"]), ([], []), (("x", "y"), ["x", "y"])],
    )
    def test_str_sequence_adapter_accepts_string_sequences(
        self, payload: Sequence[str], expected: list[str]
    ) -> None:
        """STR_SEQUENCE_ADAPTER validates string sequences to a list."""
        result = t.Cli.STR_SEQUENCE_ADAPTER.validate_python(payload)
        tm.that(list(result), eq=expected)

    @pytest.mark.parametrize(
        "payload", [123, "not-a-sequence-of-str-only", [1, 2, 3], {"k": "v"}]
    )
    def test_str_sequence_adapter_rejects_non_string_sequences(
        self, payload: p.AttributeProbe
    ) -> None:
        """STR_SEQUENCE_ADAPTER raises ValidationError on invalid input."""
        with pytest.raises(m.ValidationError):
            t.Cli.STR_SEQUENCE_ADAPTER.validate_python(payload)

    @pytest.mark.parametrize(
        "payload",
        [{"id": 1}, {"nested": {"a": [1, 2]}}, {}, {"flag": True, "name": "x"}],
    )
    def test_json_mapping_adapter_accepts_json_objects(
        self, payload: t.JsonMapping
    ) -> None:
        """JSON_MAPPING_ADAPTER validates JSON object mappings unchanged."""
        result = t.Cli.JSON_MAPPING_ADAPTER.validate_python(payload)
        tm.that(result == payload, eq=True)

    @pytest.mark.parametrize("payload", [["a", "list"], "string", 42, True])
    def test_json_mapping_adapter_rejects_non_mappings(
        self, payload: p.AttributeProbe
    ) -> None:
        """JSON_MAPPING_ADAPTER raises ValidationError for non-object input."""
        with pytest.raises(m.ValidationError):
            t.Cli.JSON_MAPPING_ADAPTER.validate_python(payload)

    @pytest.mark.parametrize(
        "payload", [[1, 2, 3], ["a", "b"], [], [{"k": "v"}, [1, 2]]]
    )
    def test_json_list_adapter_accepts_json_arrays(self, payload: t.JsonList) -> None:
        """JSON_LIST_ADAPTER validates JSON arrays unchanged."""
        result = t.Cli.JSON_LIST_ADAPTER.validate_python(payload)
        tm.that(result == payload, eq=True)

    @pytest.mark.parametrize(
        ("payload", "expected"),
        [("plain", "plain"), (7, 7), (True, True), (["a", "b"], ["a", "b"])],
    )
    def test_cli_default_source_adapter_accepts_cli_value_kinds(
        self, payload: t.Cli.DefaultSource, expected: t.Cli.DefaultSource
    ) -> None:
        """CLI_DEFAULT_SOURCE_ADAPTER accepts scalars, sequences, and paths."""
        result = t.Cli.CLI_DEFAULT_SOURCE_ADAPTER.validate_python(payload)
        tm.that(result == expected, eq=True)

    def test_cli_default_source_adapter_accepts_real_paths(
        self, tmp_path: Path
    ) -> None:
        """Validate a pytest-managed path through the public CLI adapter."""
        # mro-wkii.17.26 (codex): use the isolated filesystem fixture, never /tmp.
        source = tmp_path / "source"
        result = t.Cli.CLI_DEFAULT_SOURCE_ADAPTER.validate_python(source)
        tm.that(result, eq=source)

    # --- Published type-tuple ClassVars ---------------------------------

    def test_primitive_types_expose_scalar_primitives(self) -> None:
        """PRIMITIVE_TYPES publishes the four JSON scalar primitive types."""
        tm.that(set(t.Cli.PRIMITIVE_TYPES), eq={str, int, float, bool})

    def test_scalar_types_superset_primitive_types(self) -> None:
        """SCALAR_TYPES includes every primitive plus richer scalar types."""
        primitives = set(t.Cli.PRIMITIVE_TYPES)
        scalars = set(t.Cli.SCALAR_TYPES)
        tm.that(primitives.issubset(scalars), eq=True)
        tm.that(len(scalars) > len(primitives), eq=True)

    # --- Published alias round-trips via TypeAdapter --------------------

    def test_scalar_alias_validates_each_primitive(self) -> None:
        """The Scalar alias round-trips every primitive value."""
        adapter: p.TypeAdapter[t.Scalar] = m.TypeAdapter(t.Scalar)
        tm.that(adapter.validate_python("value"), eq="value")
        tm.that(adapter.validate_python(True), eq=True)
        tm.that(adapter.validate_python(3), eq=3)

    def test_optional_str_sequence_alias_accepts_value_and_none(self) -> None:
        """A ``StrSequence | None`` alias accepts both a sequence and None."""
        adapter: p.TypeAdapter[t.StrSequence | None] = m.TypeAdapter(
            t.StrSequence | None
        )
        tm.that(adapter.validate_python(["alpha", "beta"]), eq=["alpha", "beta"])
        tm.that(adapter.validate_python(None), none=True)

    def test_mapping_alias_validates_sequence_of_typed_mappings(self) -> None:
        """MappingKV composes into a validatable sequence-of-mappings alias."""
        adapter: p.TypeAdapter[Sequence[t.MappingKV[str, str | int]]] = m.TypeAdapter(
            Sequence[t.MappingKV[str, str | int]]
        )
        validated = adapter.validate_python([{"name": "entry", "count": 1}])
        tm.that(validated, eq=[{"name": "entry", "count": 1}])

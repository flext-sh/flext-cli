"""FLEXT CLI Typings Tests - public type-facade contract.

Modules tested: public CLI type aliases and ``u.Cli`` conversion adapters.

These tests assert the OBSERVABLE contract of the CLI type facade: the
runtime-validatable behaviour of its published type aliases and the public
conversion adapters exposed on ``u.Cli``. No private
attributes, internal collaborators, or implementation structure are touched.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

import pytest
from typing_extensions import TypeForm

from tests import c, m, t, tm, u


class TestsFlextCliTypings:
    """Behavioural contract of flext_cli.typings.FlextCliTypes."""

    # --- Published CLI adapters: accept valid payloads -------------------

    @staticmethod
    @pytest.mark.parametrize(
        ("payload", "expected"),
        [(["alpha", "beta"], ["alpha", "beta"]), ([], []), (("x", "y"), ["x", "y"])],
    )
    def test_str_sequence_adapter_accepts_string_sequences(
        payload: Sequence[str],
        expected: t.SequenceOf[str],
    ) -> None:
        """STR_SEQUENCE_ADAPTER validates string sequences to a list."""
        result = u.Cli.STR_SEQUENCE_ADAPTER.validate_python(payload)
        tm.that(list(result), eq=expected)

    @staticmethod
    @pytest.mark.parametrize(
        "payload",
        [123, "not-a-sequence-of-str-only", [1, 2, 3], {"k": "v"}],
    )
    def test_str_sequence_adapter_rejects_non_string_sequences(
        payload: t.JsonValue,
    ) -> None:
        """STR_SEQUENCE_ADAPTER raises ValidationError on invalid input."""
        with pytest.raises(m.ValidationError):
            u.Cli.STR_SEQUENCE_ADAPTER.validate_python(payload)

    @staticmethod
    @pytest.mark.parametrize(
        "payload",
        [{"id": 1}, {"nested": {"a": [1, 2]}}, {}, {"flag": True, "name": "x"}],
    )
    def test_json_mapping_adapter_accepts_json_objects(
        payload: t.MappingKV[str, t.JsonValue],
    ) -> None:
        """JSON_MAPPING_ADAPTER validates JSON object mappings unchanged."""
        result = u.Cli.JSON_MAPPING_ADAPTER.validate_python(payload)
        tm.that(result == payload, eq=True)

    @staticmethod
    @pytest.mark.parametrize("payload", [["a", "list"], "string", 42, True])
    def test_json_mapping_adapter_rejects_non_mappings(
        payload: t.JsonValue,
    ) -> None:
        """JSON_MAPPING_ADAPTER raises ValidationError for non-object input."""
        with pytest.raises(m.ValidationError):
            u.Cli.JSON_MAPPING_ADAPTER.validate_python(payload)

    @staticmethod
    @pytest.mark.parametrize(
        "payload",
        [[1, 2, 3], ["a", "b"], [], [{"k": "v"}, [1, 2]]],
    )
    def test_json_list_adapter_accepts_json_arrays(
        payload: t.SequenceOf[t.JsonValue],
    ) -> None:
        """JSON_LIST_ADAPTER validates JSON arrays unchanged."""
        result = u.Cli.JSON_LIST_ADAPTER.validate_python(payload)
        tm.that(result == payload, eq=True)

    @staticmethod
    @pytest.mark.parametrize(
        ("payload", "expected"),
        [
            ("plain", "plain"),
            (7, 7),
            (True, True),
            (Path("x"), Path("x")),
            (["a", "b"], ["a", "b"]),
        ],
    )
    def test_cli_default_source_adapter_accepts_cli_value_kinds(
        payload: t.Cli.CliDefaultSource,
        expected: t.Cli.CliDefaultSource,
    ) -> None:
        """The CLI default-source adapter accepts scalars, sequences, and paths."""
        result = u.Cli.CLI_DEFAULT_SOURCE_ADAPTER.validate_python(payload)
        tm.that(result == expected, eq=True)

    @staticmethod
    def test_json_value_adapter_round_trips_serialized_payload() -> None:
        """The utility adapter preserves nested JSON through its wire format."""
        payload: t.JsonValue = {"items": ["alpha", 7, True, None]}
        encoded = u.Cli.JSON_VALUE_ADAPTER.dump_json(payload)
        tm.that(u.Cli.JSON_VALUE_ADAPTER.validate_json(encoded), eq=payload)

    @staticmethod
    def test_yaml_adapters_validate_mapping_and_sequence_payloads() -> None:
        """YAML utility adapters preserve JSON-compatible containers."""
        mapping: t.JsonMapping = {"items": [1, "alpha", None]}
        sequence: t.JsonList = [mapping, False]
        tm.that(u.Cli.YAML_DICT_ADAPTER.validate_python(mapping), eq=mapping)
        tm.that(u.Cli.YAML_SEQ_ADAPTER.validate_python(sequence), eq=sequence)

    # --- Published type-tuple ClassVars ---------------------------------

    @staticmethod
    def test_primitive_types_expose_scalar_primitives() -> None:
        """The primitives tuple publishes the four JSON scalar primitive types."""
        tm.that(set(c.PRIMITIVES_TYPES), eq={str, int, float, bool})

    @staticmethod
    def test_scalar_types_superset_primitive_types() -> None:
        """SCALAR_TYPES includes every primitive plus richer scalar types."""
        primitives = set(c.PRIMITIVES_TYPES)
        scalars = set(c.SCALAR_TYPES)
        tm.that(primitives.issubset(scalars), eq=True)
        tm.that(len(scalars) > len(primitives), eq=True)

    # --- Published alias round-trips via TypeAdapter --------------------

    @staticmethod
    def test_scalar_alias_validates_each_primitive() -> None:
        """The Scalar alias round-trips every primitive value."""
        adapter: t.ValueAdapter[t.Scalar] = u.type_adapter(TypeForm(t.Scalar))
        tm.that(adapter.validate_python("value"), eq="value")
        bool_input = True
        tm.that(adapter.validate_python(bool_input), eq=True)
        tm.that(adapter.validate_python(3), eq=3)

    @staticmethod
    def test_optional_str_sequence_alias_accepts_value_and_none() -> None:
        """A ``StrSequence | None`` alias accepts both a sequence and None."""
        adapter: t.ValueAdapter[t.StrSequence | None] = u.type_adapter(
            TypeForm(t.StrSequence | None),
        )
        tm.that(adapter.validate_python(["alpha", "beta"]), eq=["alpha", "beta"])
        tm.that(adapter.validate_python(None), none=True)

    @staticmethod
    def test_mapping_alias_validates_sequence_of_typed_mappings() -> None:
        """MappingKV composes into a validatable sequence-of-mappings alias."""
        adapter: t.ValueAdapter[Sequence[t.MappingKV[str, str | int]]] = u.type_adapter(
            Sequence[t.MappingKV[str, str | int]],
        )
        validated = adapter.validate_python([{"name": "entry", "count": 1}])
        expected: list[t.MappingKV[str, str | int]] = [{"name": "entry", "count": 1}]
        tm.that(validated, eq=expected)

"""FLEXT CLI Typings Tests - public type-facade contract.

Modules tested: flext_cli.typings.FlextCliTypes (via the tests `t` facade).

These tests assert the OBSERVABLE contract of the CLI type facade: the
runtime-validatable behaviour of its published type aliases and the public
type-tuple ClassVars exposed on ``t.Cli``. No private
attributes, internal collaborators, or implementation structure are touched.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

import pytest
from flext_tests import tm

from tests import c, m, t, u


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
        result = t.Cli.STR_SEQUENCE_ADAPTER.validate_python(payload)
        tm.that(list(result), eq=expected)

    @staticmethod
    @pytest.mark.parametrize(
        "payload",
        [123, "not-a-sequence-of-str-only", [1, 2, 3], {"k": "v"}],
    )
    def test_str_sequence_adapter_rejects_non_string_sequences(
        payload: object,
    ) -> None:
        """STR_SEQUENCE_ADAPTER raises ValidationError on invalid input."""
        with pytest.raises(m.ValidationError):
            t.Cli.STR_SEQUENCE_ADAPTER.validate_python(payload)

    @staticmethod
    @pytest.mark.parametrize(
        "payload",
        [{"id": 1}, {"nested": {"a": [1, 2]}}, {}, {"flag": True, "name": "x"}],
    )
    def test_json_mapping_adapter_accepts_json_objects(
        payload: t.MappingKV[str, t.JsonValue],
    ) -> None:
        """JSON_MAPPING_ADAPTER validates JSON object mappings unchanged."""
        result = t.Cli.JSON_MAPPING_ADAPTER.validate_python(payload)
        tm.that(result == payload, eq=True)

    @staticmethod
    @pytest.mark.parametrize("payload", [["a", "list"], "string", 42, True])
    def test_json_mapping_adapter_rejects_non_mappings(payload: object) -> None:
        """JSON_MAPPING_ADAPTER raises ValidationError for non-object input."""
        with pytest.raises(m.ValidationError):
            t.Cli.JSON_MAPPING_ADAPTER.validate_python(payload)

    @staticmethod
    @pytest.mark.parametrize(
        "payload",
        [[1, 2, 3], ["a", "b"], [], [{"k": "v"}, [1, 2]]],
    )
    def test_json_list_adapter_accepts_json_arrays(
        payload: t.SequenceOf[t.JsonValue],
    ) -> None:
        """JSON_LIST_ADAPTER validates JSON arrays unchanged."""
        result = t.Cli.JSON_LIST_ADAPTER.validate_python(payload)
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
        payload: object,
        expected: object,
    ) -> None:
        """The CLI default-source adapter accepts scalars, sequences, and paths."""
        result = t.Cli.CLI_DEFAULT_SOURCE_ADAPTER.validate_python(payload)
        tm.that(result == expected, eq=True)

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
        adapter: m.TypeAdapter[t.Scalar] = u.type_adapter(Annotated[t.Scalar, None])
        tm.that(adapter.validate_python("value"), eq="value")
        bool_input = True
        tm.that(adapter.validate_python(bool_input), eq=True)
        tm.that(adapter.validate_python(3), eq=3)

    @staticmethod
    def test_optional_str_sequence_alias_accepts_value_and_none() -> None:
        """A ``StrSequence | None`` alias accepts both a sequence and None."""
        adapter: m.TypeAdapter[t.StrSequence | None] = u.type_adapter(
            Annotated[t.StrSequence | None, None],
        )
        tm.that(adapter.validate_python(["alpha", "beta"]), eq=["alpha", "beta"])
        tm.that(adapter.validate_python(None), none=True)

    @staticmethod
    def test_mapping_alias_validates_sequence_of_typed_mappings() -> None:
        """MappingKV composes into a validatable sequence-of-mappings alias."""
        adapter: m.TypeAdapter[Sequence[t.MappingKV[str, str | int]]] = u.type_adapter(
            Sequence[t.MappingKV[str, str | int]],
        )
        validated = adapter.validate_python([{"name": "entry", "count": 1}])
        expected: list[t.MappingKV[str, str | int]] = [{"name": "entry", "count": 1}]
        tm.that(validated, eq=expected)

"""Behavioral tests for the public ``u.Cli.toml_*`` TOML helpers.

Exercises the observable contract of the TOML utility facade exposed through
``u.Cli``: parse/serialize round-trips, mapping normalization, ``r``-typed
read/write outcomes, path building, navigation, and runtime type predicates.
No implementation detail (private attribute, internal collaborator, or
line-coverage poke) is asserted.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests import c
from tests import u
from flext_tests import tm

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliTomlCov:
    """Observable-behavior tests for the ``u.Cli.toml_*`` helpers."""

    _VALID_TOML = c.Tests.TOML_VALID_CONTENT
    _INVALID_TOML = c.Tests.TOML_INVALID_CONTENT
    _EXPECTED_MAPPING = {
        "tool": {"flext": {"project": "my-project", "version": "1.0.0"}}
    }

    # ── toml_parse_text ───────────────────────────────────────────────

    def test_parse_text_round_trips_valid_content(self) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        tm.that(doc, none=False)
        tm.that(u.Cli.toml_dumps(doc), eq=self._VALID_TOML)

    def test_parse_text_returns_none_on_invalid_content(self) -> None:
        tm.that(u.Cli.toml_parse_text(self._INVALID_TOML), none=True)

    def test_parse_text_treats_empty_as_valid_empty_document(self) -> None:
        doc = u.Cli.toml_parse_text("")
        tm.that(doc, none=False)
        tm.that(u.Cli.toml_dumps(doc), eq="")

    # ── toml_mapping_from_text ────────────────────────────────────────

    def test_mapping_from_text_yields_nested_plain_mapping(self) -> None:
        tm.that(
            u.Cli.toml_mapping_from_text(self._VALID_TOML), eq=self._EXPECTED_MAPPING
        )

    def test_mapping_from_text_returns_none_on_invalid_content(self) -> None:
        tm.that(u.Cli.toml_mapping_from_text(self._INVALID_TOML), none=True)

    # ── constructors + runtime predicates ─────────────────────────────

    def test_document_constructor_produces_document(self) -> None:
        doc = u.Cli.toml_document()
        assert u.Cli.toml_is_document(doc)
        tm.that(u.Cli.toml_dumps(doc), eq="")

    def test_table_constructor_is_recognized_as_table(self) -> None:
        assert u.Cli.toml_is_table(u.Cli.toml_table())

    def test_aot_constructor_is_recognized_as_aot(self) -> None:
        assert u.Cli.toml_is_aot(u.Cli.toml_aot())

    def test_array_constructor_round_trips_to_string_list(self) -> None:
        arr = u.Cli.toml_array(["a", "b", "c"])
        assert u.Cli.toml_is_item(arr)
        tm.that(list(u.Cli.toml_as_string_list(arr)), eq=["a", "b", "c"])

    def test_predicates_reject_non_toml_values(self) -> None:
        assert not u.Cli.toml_is_document("not a toml value")
        assert not u.Cli.toml_is_table("not a toml value")
        assert not u.Cli.toml_is_aot("not a toml value")
        assert not u.Cli.toml_is_item("not a toml value")

    # ── toml_as_mapping ───────────────────────────────────────────────

    def test_as_mapping_unwraps_document_to_expected_dict(self) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        tm.that(doc, none=False)
        tm.that(u.Cli.toml_as_mapping(doc), eq=self._EXPECTED_MAPPING)

    def test_as_mapping_returns_none_for_missing_source(self) -> None:
        tm.that(u.Cli.toml_as_mapping(None), none=True)

    # ── toml_as_string_list ───────────────────────────────────────────

    @pytest.mark.parametrize(
        ("items", "expected"),
        [(["x", "y"], ["x", "y"]), ([], []), (["solo"], ["solo"])],
    )
    def test_as_string_list_preserves_array_contents(
        self, items: list[str], expected: list[str]
    ) -> None:
        arr = u.Cli.toml_array(items)
        tm.that(list(u.Cli.toml_as_string_list(arr)), eq=expected)

    def test_as_string_list_returns_empty_for_none(self) -> None:
        tm.that(list(u.Cli.toml_as_string_list(None)), eq=[])

    # ── toml_dot_path ─────────────────────────────────────────────────

    @pytest.mark.parametrize(
        ("parts", "expected"),
        [
            (("section",), "section"),
            (("tool", "flext", "name"), "tool.flext.name"),
            (("tool", "", "name"), "tool.name"),
            ((), ""),
        ],
    )
    def test_dot_path_joins_non_empty_segments(
        self, parts: tuple[str, ...], expected: str
    ) -> None:
        tm.that(u.Cli.toml_dot_path(*parts), eq=expected)

    # ── toml_read / toml_read_document / toml_read_json ───────────────

    def test_read_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        tm.that(u.Cli.toml_read(tmp_path / "nonexistent.toml"), none=True)

    def test_read_parses_existing_file_contents(self, tmp_path: Path) -> None:
        path = tmp_path / "test.toml"
        path.write_text(self._VALID_TOML)
        doc = u.Cli.toml_read(path)
        tm.that(doc, none=False)
        tm.that(u.Cli.toml_as_mapping(doc), eq=self._EXPECTED_MAPPING)

    def test_read_document_success_carries_parsed_document(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "test.toml"
        path.write_text(self._VALID_TOML)
        result = u.Cli.toml_read_document(path)
        tm.ok(result)
        tm.that(u.Cli.toml_as_mapping(result.value), eq=self._EXPECTED_MAPPING)

    def test_read_document_fails_for_missing_file(self, tmp_path: Path) -> None:
        result = u.Cli.toml_read_document(tmp_path / "missing.toml")
        tm.fail(result)
        assert result.error

    def test_read_json_success_returns_plain_mapping(self, tmp_path: Path) -> None:
        path = tmp_path / "test.toml"
        path.write_text(self._VALID_TOML)
        result = u.Cli.toml_read_json(path)
        tm.ok(result)
        tm.that(result.value, eq=self._EXPECTED_MAPPING)

    def test_read_json_fails_for_missing_file(self, tmp_path: Path) -> None:
        result = u.Cli.toml_read_json(tmp_path / "missing.toml")
        tm.fail(result)
        assert result.error

    # ── toml_write_document / toml_write_mapping ──────────────────────

    def test_write_document_round_trips_through_read(self, tmp_path: Path) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        tm.that(doc, none=False)
        path = tmp_path / "out.toml"

        result = u.Cli.toml_write_document(path, doc)

        tm.ok(result)
        tm.that(u.Cli.toml_read_json(path).value, eq=self._EXPECTED_MAPPING)

    def test_write_mapping_round_trips_through_read(self, tmp_path: Path) -> None:
        payload = {"key": "value", "count": 7}
        path = tmp_path / "out.toml"

        result = u.Cli.toml_write_mapping(path, payload)

        tm.ok(result)
        tm.that(u.Cli.toml_read_json(path).value, eq=payload)

    # ── toml_document_from_mapping ────────────────────────────────────

    def test_document_from_mapping_preserves_data_on_round_trip(self) -> None:
        payload = {"name": "flext", "version": "1.0"}
        doc = u.Cli.toml_document_from_mapping(payload)
        assert u.Cli.toml_is_document(doc)
        tm.that(u.Cli.toml_as_mapping(doc), eq=payload)

    # ── toml_navigate_path ────────────────────────────────────────────

    def test_navigate_path_returns_existing_table_contents(self) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        tm.that(doc, none=False)
        table = u.Cli.toml_navigate_path(doc, ["tool", "flext"])
        assert u.Cli.toml_is_table(table)
        tm.that(
            u.Cli.toml_as_mapping(table),
            eq={"project": "my-project", "version": "1.0.0"},
        )

    def test_navigate_path_creates_and_wires_missing_intermediate_tables(self) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        tm.that(doc, none=False)

        table = u.Cli.toml_navigate_path(doc, ["created", "nested"])

        assert u.Cli.toml_is_table(table)
        tm.that(dict(table), eq={})
        table["leaf"] = "wired"
        tm.that(
            u.Cli.toml_as_mapping(doc),
            eq={
                **self._EXPECTED_MAPPING,
                "tool": {
                    **self._EXPECTED_MAPPING["tool"],
                    "created": {"nested": {"leaf": "wired"}},
                },
            },
        )

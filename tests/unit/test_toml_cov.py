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

from typing import TYPE_CHECKING, ClassVar

import pytest

from tests import c, t, u
from flext_tests import tm

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliTomlCov:
    """Observable-behavior tests for the ``u.Cli.toml_*`` helpers."""

    _VALID_TOML = c.Tests.TOML_VALID_CONTENT
    _INVALID_TOML = c.Tests.TOML_INVALID_CONTENT
    _EXPECTED_MAPPING: ClassVar[t.MappingKV[str, t.MappingKV[str, t.StrMapping]]] = {
        "tool": {"flext": {"project": "my-project", "version": "1.0.0"}}
    }

    # ── toml_parse_text ───────────────────────────────────────────────

    def test_parse_text_round_trips_valid_content(self) -> None:
        """Verify that parse text round trips valid content."""
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        doc = tm.not_none(doc)
        tm.that(u.Cli.toml_dumps(doc), eq=self._VALID_TOML)

    def test_parse_text_returns_none_on_invalid_content(self) -> None:
        """Verify that parse text returns none on invalid content."""
        tm.that(u.Cli.toml_parse_text(self._INVALID_TOML), none=True)

    def test_parse_text_treats_empty_as_valid_empty_document(self) -> None:
        """Verify that parse text treats empty as valid empty document."""
        doc = u.Cli.toml_parse_text("")
        doc = tm.not_none(doc)
        tm.that(u.Cli.toml_dumps(doc), eq="")

    # ── toml_mapping_from_text ────────────────────────────────────────

    def test_mapping_from_text_yields_nested_plain_mapping(self) -> None:
        """Verify that mapping from text yields nested plain mapping."""
        tm.that(
            u.Cli.toml_mapping_from_text(self._VALID_TOML), eq=self._EXPECTED_MAPPING
        )

    def test_mapping_from_text_returns_none_on_invalid_content(self) -> None:
        """Verify that mapping from text returns none on invalid content."""
        tm.that(u.Cli.toml_mapping_from_text(self._INVALID_TOML), none=True)

    # ── constructors + runtime predicates ─────────────────────────────

    def test_document_constructor_produces_document(self) -> None:
        """Verify that document constructor produces document."""
        doc = u.Cli.toml_document()
        tm.that(u.Cli.toml_is_document(doc), eq=True)
        tm.that(u.Cli.toml_dumps(doc), eq="")

    def test_table_constructor_is_recognized_as_table(self) -> None:
        """Verify that table constructor is recognized as table."""
        tm.that(u.Cli.toml_is_table(u.Cli.toml_table()), eq=True)

    def test_aot_constructor_is_recognized_as_aot(self) -> None:
        """Verify that aot constructor is recognized as aot."""
        tm.that(u.Cli.toml_is_aot(u.Cli.toml_aot()), eq=True)

    def test_array_constructor_round_trips_to_string_list(self) -> None:
        """Verify that array constructor round trips to string list."""
        arr = u.Cli.toml_array(["a", "b", "c"])
        tm.that(u.Cli.toml_is_item(arr), eq=True)
        tm.that(list(u.Cli.toml_as_string_list(arr)), eq=["a", "b", "c"])

    def test_predicates_reject_non_toml_values(self) -> None:
        """Verify that predicates reject non toml values."""
        tm.that(u.Cli.toml_is_document("not a toml value"), eq=False)
        tm.that(u.Cli.toml_is_table("not a toml value"), eq=False)
        tm.that(u.Cli.toml_is_aot("not a toml value"), eq=False)
        tm.that(u.Cli.toml_is_item("not a toml value"), eq=False)

    # ── toml_as_mapping ───────────────────────────────────────────────

    def test_as_mapping_unwraps_document_to_expected_dict(self) -> None:
        """Verify that as mapping unwraps document to expected dict."""
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        doc = tm.not_none(doc)
        tm.that(u.Cli.toml_as_mapping(doc), eq=self._EXPECTED_MAPPING)

    def test_as_mapping_returns_none_for_missing_source(self) -> None:
        """Verify that as mapping returns none for missing source."""
        tm.that(u.Cli.toml_as_mapping(None), none=True)

    # ── toml_as_string_list ───────────────────────────────────────────

    @pytest.mark.parametrize(
        ("items", "expected"),
        [(["x", "y"], ["x", "y"]), ([], []), (["solo"], ["solo"])],
    )
    def test_as_string_list_preserves_array_contents(
        self, items: list[str], expected: list[str]
    ) -> None:
        """Verify that as string list preserves array contents."""
        arr = u.Cli.toml_array(items)
        tm.that(list(u.Cli.toml_as_string_list(arr)), eq=expected)

    def test_as_string_list_returns_empty_for_none(self) -> None:
        """Verify that as string list returns empty for none."""
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
        """Verify that dot path joins non empty segments."""
        tm.that(u.Cli.toml_dot_path(*parts), eq=expected)

    # ── toml_read / toml_read_document / toml_read_json ───────────────

    def test_read_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        """Verify that read returns none for missing file."""
        tm.that(u.Cli.toml_read(tmp_path / "nonexistent.toml"), none=True)

    def test_read_parses_existing_file_contents(self, tmp_path: Path) -> None:
        """Verify that read parses existing file contents."""
        path = tmp_path / "test.toml"
        path.write_text(self._VALID_TOML)
        doc = u.Cli.toml_read(path)
        doc = tm.not_none(doc)
        tm.that(u.Cli.toml_as_mapping(doc), eq=self._EXPECTED_MAPPING)

    def test_read_document_success_carries_parsed_document(
        self, tmp_path: Path
    ) -> None:
        """Verify that read document success carries parsed document."""
        path = tmp_path / "test.toml"
        path.write_text(self._VALID_TOML)
        result = u.Cli.toml_read_document(path)
        tm.ok(result)
        tm.that(u.Cli.toml_as_mapping(result.value), eq=self._EXPECTED_MAPPING)

    def test_read_document_fails_for_missing_file(self, tmp_path: Path) -> None:
        """Verify that read document fails for missing file."""
        result = u.Cli.toml_read_document(tmp_path / "missing.toml")
        tm.fail(result)
        tm.that(result.error, empty=False)

    def test_read_json_success_returns_plain_mapping(self, tmp_path: Path) -> None:
        """Verify that read json success returns plain mapping."""
        path = tmp_path / "test.toml"
        path.write_text(self._VALID_TOML)
        result = u.Cli.toml_read_json(path)
        tm.ok(result)
        tm.that(result.value, eq=self._EXPECTED_MAPPING)

    def test_read_json_fails_for_missing_file(self, tmp_path: Path) -> None:
        """Verify that read json fails for missing file."""
        result = u.Cli.toml_read_json(tmp_path / "missing.toml")
        tm.fail(result)
        tm.that(result.error, empty=False)

    # ── toml_write_document / toml_write_mapping ──────────────────────

    def test_write_document_round_trips_through_read(self, tmp_path: Path) -> None:
        """Verify that write document round trips through read."""
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        doc = tm.not_none(doc)
        path = tmp_path / "out.toml"

        result = u.Cli.toml_write_document(path, doc)

        tm.ok(result)
        tm.that(u.Cli.toml_read_json(path).value, eq=self._EXPECTED_MAPPING)

    def test_write_mapping_round_trips_through_read(self, tmp_path: Path) -> None:
        """Verify that write mapping round trips through read."""
        payload = {"key": "value", "count": 7}
        path = tmp_path / "out.toml"

        result = u.Cli.toml_write_mapping(path, payload)

        tm.ok(result)
        tm.that(u.Cli.toml_read_json(path).value, eq=payload)

    # ── toml_document_from_mapping ────────────────────────────────────

    def test_document_from_mapping_preserves_data_on_round_trip(self) -> None:
        """Verify that document from mapping preserves data on round trip."""
        payload = {"name": "flext", "version": "1.0"}
        doc = u.Cli.toml_document_from_mapping(payload)
        tm.that(u.Cli.toml_is_document(doc), eq=True)
        tm.that(u.Cli.toml_as_mapping(doc), eq=payload)

    # ── toml_navigate_path ────────────────────────────────────────────

    def test_navigate_path_returns_existing_table_contents(self) -> None:
        """Verify that navigate path returns existing table contents."""
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        doc = tm.not_none(doc)
        table = u.Cli.toml_navigate_path(doc, ["tool", "flext"])
        tm.that(u.Cli.toml_is_table(table), eq=True)
        tm.that(
            u.Cli.toml_as_mapping(table),
            eq={"project": "my-project", "version": "1.0.0"},
        )

    def test_navigate_path_creates_and_wires_missing_intermediate_tables(self) -> None:
        """Verify that navigate path creates and wires missing intermediate tables."""
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        doc = tm.not_none(doc)

        table = u.Cli.toml_navigate_path(doc, ["created", "nested"])

        tm.that(u.Cli.toml_is_table(table), eq=True)
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

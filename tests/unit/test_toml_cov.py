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

from tests.constants import c
from tests.utilities import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliTomlCov:
    """Observable-behavior tests for the ``u.Cli.toml_*`` helpers."""

    _VALID_TOML = c.Tests.TOML_VALID_CONTENT
    _INVALID_TOML = c.Tests.TOML_INVALID_CONTENT
    _EXPECTED_MAPPING = {
        "tool": {"flext": {"project": "my-project", "version": "1.0.0"}},
    }

    # ── toml_parse_text ───────────────────────────────────────────────

    def test_parse_text_round_trips_valid_content(self) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        assert doc is not None
        assert u.Cli.toml_dumps(doc) == self._VALID_TOML

    def test_parse_text_returns_none_on_invalid_content(self) -> None:
        assert u.Cli.toml_parse_text(self._INVALID_TOML) is None

    def test_parse_text_treats_empty_as_valid_empty_document(self) -> None:
        doc = u.Cli.toml_parse_text("")
        assert doc is not None
        assert u.Cli.toml_dumps(doc) == ""

    # ── toml_mapping_from_text ────────────────────────────────────────

    def test_mapping_from_text_yields_nested_plain_mapping(self) -> None:
        assert u.Cli.toml_mapping_from_text(self._VALID_TOML) == self._EXPECTED_MAPPING

    def test_mapping_from_text_returns_none_on_invalid_content(self) -> None:
        assert u.Cli.toml_mapping_from_text(self._INVALID_TOML) is None

    # ── constructors + runtime predicates ─────────────────────────────

    def test_document_constructor_produces_document(self) -> None:
        doc = u.Cli.toml_document()
        assert u.Cli.toml_is_document(doc)
        assert u.Cli.toml_dumps(doc) == ""

    def test_table_constructor_is_recognized_as_table(self) -> None:
        assert u.Cli.toml_is_table(u.Cli.toml_table())

    def test_aot_constructor_is_recognized_as_aot(self) -> None:
        assert u.Cli.toml_is_aot(u.Cli.toml_aot())

    def test_array_constructor_round_trips_to_string_list(self) -> None:
        arr = u.Cli.toml_array(["a", "b", "c"])
        assert u.Cli.toml_is_item(arr)
        assert list(u.Cli.toml_as_string_list(arr)) == ["a", "b", "c"]

    def test_predicates_reject_non_toml_values(self) -> None:
        assert not u.Cli.toml_is_document("not a toml value")
        assert not u.Cli.toml_is_table("not a toml value")
        assert not u.Cli.toml_is_aot("not a toml value")
        assert not u.Cli.toml_is_item("not a toml value")

    # ── toml_as_mapping ───────────────────────────────────────────────

    def test_as_mapping_unwraps_document_to_expected_dict(self) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        assert doc is not None
        assert u.Cli.toml_as_mapping(doc) == self._EXPECTED_MAPPING

    def test_as_mapping_returns_none_for_missing_source(self) -> None:
        assert u.Cli.toml_as_mapping(None) is None

    # ── toml_as_string_list ───────────────────────────────────────────

    @pytest.mark.parametrize(
        ("items", "expected"),
        [
            (["x", "y"], ["x", "y"]),
            ([], []),
            (["solo"], ["solo"]),
        ],
    )
    def test_as_string_list_preserves_array_contents(
        self,
        items: list[str],
        expected: list[str],
    ) -> None:
        arr = u.Cli.toml_array(items)
        assert list(u.Cli.toml_as_string_list(arr)) == expected

    def test_as_string_list_returns_empty_for_none(self) -> None:
        assert list(u.Cli.toml_as_string_list(None)) == []

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
        self,
        parts: tuple[str, ...],
        expected: str,
    ) -> None:
        assert u.Cli.toml_dot_path(*parts) == expected

    # ── toml_read / toml_read_document / toml_read_json ───────────────

    def test_read_returns_none_for_missing_file(self, tmp_path: Path) -> None:
        assert u.Cli.toml_read(tmp_path / "nonexistent.toml") is None

    def test_read_parses_existing_file_contents(self, tmp_path: Path) -> None:
        path = tmp_path / "test.toml"
        path.write_text(self._VALID_TOML)
        doc = u.Cli.toml_read(path)
        assert doc is not None
        assert u.Cli.toml_as_mapping(doc) == self._EXPECTED_MAPPING

    def test_read_document_success_carries_parsed_document(
        self,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "test.toml"
        path.write_text(self._VALID_TOML)
        result = u.Cli.toml_read_document(path)
        assert result.success
        assert u.Cli.toml_as_mapping(result.value) == self._EXPECTED_MAPPING

    def test_read_document_fails_for_missing_file(self, tmp_path: Path) -> None:
        result = u.Cli.toml_read_document(tmp_path / "missing.toml")
        assert result.failure
        assert result.error

    def test_read_json_success_returns_plain_mapping(self, tmp_path: Path) -> None:
        path = tmp_path / "test.toml"
        path.write_text(self._VALID_TOML)
        result = u.Cli.toml_read_json(path)
        assert result.success
        assert result.value == self._EXPECTED_MAPPING

    def test_read_json_fails_for_missing_file(self, tmp_path: Path) -> None:
        result = u.Cli.toml_read_json(tmp_path / "missing.toml")
        assert result.failure
        assert result.error

    # ── toml_write_document / toml_write_mapping ──────────────────────

    def test_write_document_round_trips_through_read(self, tmp_path: Path) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        assert doc is not None
        path = tmp_path / "out.toml"

        result = u.Cli.toml_write_document(path, doc)

        assert result.success
        assert u.Cli.toml_read_json(path).value == self._EXPECTED_MAPPING

    def test_write_mapping_round_trips_through_read(self, tmp_path: Path) -> None:
        payload = {"key": "value", "count": 7}
        path = tmp_path / "out.toml"

        result = u.Cli.toml_write_mapping(path, payload)

        assert result.success
        assert u.Cli.toml_read_json(path).value == payload

    # ── toml_document_from_mapping ────────────────────────────────────

    def test_document_from_mapping_preserves_data_on_round_trip(self) -> None:
        payload = {"name": "flext", "version": "1.0"}
        doc = u.Cli.toml_document_from_mapping(payload)
        assert u.Cli.toml_is_document(doc)
        assert u.Cli.toml_as_mapping(doc) == payload

    # ── toml_navigate_path ────────────────────────────────────────────

    def test_navigate_path_returns_existing_table_contents(self) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        assert doc is not None
        table = u.Cli.toml_navigate_path(doc, ["tool", "flext"])
        assert u.Cli.toml_is_table(table)
        assert dict(table) == {"project": "my-project", "version": "1.0.0"}

    def test_navigate_path_creates_and_wires_missing_intermediate_tables(
        self,
    ) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        assert doc is not None

        table = u.Cli.toml_navigate_path(doc, ["created", "nested"])

        assert u.Cli.toml_is_table(table)
        assert dict(table) == {}
        table["leaf"] = "wired"
        assert u.Cli.toml_as_mapping(doc) == {
            **self._EXPECTED_MAPPING,
            "tool": {
                **self._EXPECTED_MAPPING["tool"],
                "created": {"nested": {"leaf": "wired"}},
            },
        }

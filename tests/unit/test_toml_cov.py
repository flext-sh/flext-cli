"""Coverage tests for _utilities/toml.py.

Targets: toml_as_mapping, toml_unwrap_item, toml_as_string_list,
         toml_array, toml_document, toml_table, toml_aot,
         toml_parse_text, toml_mapping_from_text,
         toml_read, toml_read_document, toml_read_json,
         toml_write_document, toml_write_mapping, toml_dot_path,
         toml_navigate_path.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from tests.constants import c
from tests.utilities import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliTomlUtilsCov:
    """Coverage tests for the public TOML helpers exposed via ``u.Cli``."""

    _VALID_TOML = c.Tests.TOML_VALID_CONTENT
    _INVALID_TOML = c.Tests.TOML_INVALID_CONTENT

    # ── toml_parse_text ───────────────────────────────────────────────

    def test_toml_parse_text_valid(self) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        assert doc is not None

    def test_toml_parse_text_invalid(self) -> None:
        doc = u.Cli.toml_parse_text(self._INVALID_TOML)
        assert doc is None

    def test_toml_parse_text_empty(self) -> None:
        doc = u.Cli.toml_parse_text("")
        assert doc is not None  # Empty TOML is valid

    # ── toml_mapping_from_text ────────────────────────────────────────

    def test_toml_mapping_from_text_valid(self) -> None:
        mapping = u.Cli.toml_mapping_from_text(self._VALID_TOML)
        assert mapping is not None
        assert "tool" in mapping

    def test_toml_mapping_from_text_invalid(self) -> None:
        mapping = u.Cli.toml_mapping_from_text(self._INVALID_TOML)
        assert mapping is None

    # ── toml_document, toml_table, toml_aot, toml_array ─────────────────

    def test_toml_document_creates_document(self) -> None:
        doc = u.Cli.toml_document()
        assert u.Cli.toml_is_document(doc)

    def test_toml_table_creates_table(self) -> None:

        tbl = u.Cli.toml_table()
        assert tbl is not None

    def test_toml_aot_creates_aot(self) -> None:
        aot = u.Cli.toml_aot()
        assert aot is not None

    def test_toml_array_creates_array(self) -> None:
        arr = u.Cli.toml_array(["a", "b", "c"])
        assert arr is not None

    # ── toml_as_mapping ────────────────────────────────────────────────

    def test_toml_as_mapping_from_document(self) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        assert doc is not None
        mapping = u.Cli.toml_as_mapping(doc)
        assert mapping is not None
        assert isinstance(mapping, dict)

    # ── toml_as_string_list ────────────────────────────────────────────

    def test_toml_as_string_list_array(self) -> None:
        arr = u.Cli.toml_array(["x", "y"])
        result = u.Cli.toml_as_string_list(arr)
        assert result is not None
        assert list(result) == ["x", "y"]

    # ── toml_dot_path ────────────────────────────────────────────────

    def test_toml_dot_path_single(self) -> None:
        result = u.Cli.toml_dot_path("section")
        assert result == "section"

    def test_toml_dot_path_multi(self) -> None:
        result = u.Cli.toml_dot_path("tool", "flext", "name")
        assert result == "tool.flext.name"

    # ── toml_read & write ─────────────────────────────────────────────

    def test_toml_read_missing_file(self, tmp_path: Path) -> None:
        doc = u.Cli.toml_read(tmp_path / "nonexistent.toml")
        assert doc is None

    def test_toml_read_document_valid(self, tmp_path: Path) -> None:
        path = tmp_path / "test.toml"
        path.write_text(self._VALID_TOML)
        result = u.Cli.toml_read_document(path)
        assert result.success

    def test_toml_read_document_missing(self, tmp_path: Path) -> None:
        path = tmp_path / "missing.toml"
        result = u.Cli.toml_read_document(path)
        assert result.failure

    def test_toml_read_json_valid(self, tmp_path: Path) -> None:
        path = tmp_path / "test.toml"
        path.write_text(self._VALID_TOML)
        result = u.Cli.toml_read_json(path)
        assert result.success
        assert isinstance(result.value, dict)

    def test_toml_write_document_valid(self, tmp_path: Path) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        assert doc is not None
        path = tmp_path / "out.toml"
        result = u.Cli.toml_write_document(path, doc)
        assert result.success
        assert path.exists()

    def test_toml_write_mapping_valid(self, tmp_path: Path) -> None:
        path = tmp_path / "out.toml"
        result = u.Cli.toml_write_mapping(path, {"key": "value"})
        assert result.success

    # ── toml_document_from_mapping ────────────────────────────────────

    def test_toml_document_from_mapping(self) -> None:
        doc = u.Cli.toml_document_from_mapping({
            "name": "flext",
            "version": "1.0",
        })
        assert u.Cli.toml_is_document(doc)

    # ── toml_navigate_path ────────────────────────────────────────────

    def test_toml_navigate_path_found(self) -> None:
        doc = u.Cli.toml_parse_text(c.Tests.TOML_SECTION_CONTENT)
        assert doc is not None
        result = u.Cli.toml_navigate_path(doc, ["tool", "poetry"])
        assert result is not None

    def test_toml_navigate_path_not_found(self) -> None:
        doc = u.Cli.toml_parse_text(self._VALID_TOML)
        assert doc is not None
        result = u.Cli.toml_navigate_path(doc, ["nonexistent", "path"])
        # May return None or empty dict depending on implementation
        assert result is None or result == {}

    # ── toml_is_* predicates ─────────────────────────────────────────

    def test_toml_is_document(self) -> None:
        doc = u.Cli.toml_document()
        assert u.Cli.toml_is_document(doc)
        assert not u.Cli.toml_is_document("not a doc")

    def test_toml_is_table(self) -> None:
        tbl = u.Cli.toml_table()
        assert u.Cli.toml_is_table(tbl)
        assert not u.Cli.toml_is_table("not a table")

    def test_toml_is_aot(self) -> None:
        aot = u.Cli.toml_aot()
        assert u.Cli.toml_is_aot(aot)
        assert not u.Cli.toml_is_aot("not an aot")

    def test_toml_is_item(self) -> None:
        arr = u.Cli.toml_array(["x"])
        assert u.Cli.toml_is_item(arr)
        assert not u.Cli.toml_is_item("raw string")

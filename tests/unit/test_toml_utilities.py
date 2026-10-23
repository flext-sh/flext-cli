"""Behavioral tests for the generic TOML helpers exposed via ``u.Cli.toml_*``.

Every test exercises only the public helper contract: return values, ``r[T]``
success/failure outcomes and the observable state of the produced TOML
documents/mappings. No private attributes, internal collaborators or
implementation structures are inspected.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import stat
import tomllib
from copy import deepcopy
from datetime import UTC, datetime
from pathlib import Path

import pytest
from tomlkit.exceptions import ParseError

from tests import c, m, t, tm, u


class TestsFlextCliTomlUtilities:
    """Public contract of the ``u.Cli.toml_*`` helper family."""

    @staticmethod
    def test_array_item_comments_preserve_occurrences_and_document() -> None:
        """Associate comments with repeated values without mutating the source."""
        source = (
            "dependencies = [\n"
            '  "same", # first\n'
            "  # standalone\n"
            '  "same", # second\n'
            '  "flext_toml_slot_0",\n'
            "]\n"
        )
        document = tm.not_none(u.Cli.toml_parse_text(source))
        before = document.as_string()
        tm.that(
            u.Cli.toml_array_item_comments(document, "dependencies"),
            eq=("# first", "# second", ""),
        )
        tm.that(document.as_string(), eq=before)

    @staticmethod
    @pytest.mark.parametrize("source", ['dependencies = "value"\n', "other = []\n"])
    def test_array_item_comments_reject_non_array_fields(source: str) -> None:
        """Missing and scalar fields cannot masquerade as dependency arrays."""
        document = tm.not_none(u.Cli.toml_parse_text(source))
        with pytest.raises(TypeError, match="must be an array"):
            u.Cli.toml_array_item_comments(document, "dependencies")

    # ------------------------------------------------------------------ read

    @staticmethod
    def test_read_returns_parsed_document_for_valid_file(tmp_path: Path) -> None:
        """Verify that read returns parsed document for valid file."""
        toml_file = tmp_path / "test.toml"
        toml_file.write_text(
            '[section]\nkey = "value"\nnumber = 42\n',
            encoding="utf-8",
        )

        doc = u.Cli.toml_read(toml_file)

        doc = tm.not_none(doc)
        section = u.Cli.toml_table_child(doc, "section")
        section = tm.not_none(section)
        tm.that(u.Cli.toml_value(section, "key"), eq="value")
        tm.that(u.Cli.toml_value(section, "number"), eq=42)

    @staticmethod
    def test_read_returns_none_for_missing_file(tmp_path: Path) -> None:
        """A path that does not exist reads as ``None``."""
        tm.that(u.Cli.toml_read(tmp_path / "missing.toml"), none=True)

    @staticmethod
    def test_read_raises_parse_error_for_invalid_file(tmp_path: Path) -> None:
        """Invalid TOML propagates the native ``tomlkit`` parse error."""
        toml_file = tmp_path / "invalid.toml"
        toml_file.write_text(c.Tests.TOML_INVALID_CONTENT, encoding="utf-8")

        with pytest.raises(ParseError):
            u.Cli.toml_read(toml_file)

    @staticmethod
    def test_read_raises_os_error_for_unreadable_path(tmp_path: Path) -> None:
        """An existing path that cannot be read propagates the native error."""
        with pytest.raises(IsADirectoryError):
            u.Cli.toml_read(tmp_path)

    @staticmethod
    def test_read_document_succeeds_and_preserves_values(tmp_path: Path) -> None:
        """Verify that read document succeeds and preserves values."""
        toml_file = tmp_path / "test.toml"
        toml_file.write_text('[section]\nkey = "value"  # comment\n', encoding="utf-8")

        result = u.Cli.toml_read_document(toml_file)

        tm.ok(result)
        section = u.Cli.toml_table_child(result.value, "section")
        section = tm.not_none(section)
        tm.that(u.Cli.toml_value(section, "key"), eq="value")

    @staticmethod
    def test_read_document_fails_with_not_found_for_missing_file(
        tmp_path: Path,
    ) -> None:
        """Verify that read document fails with not found for missing file."""
        tm.fail(u.Cli.toml_read_document(tmp_path / "missing.toml"), has="not found")

    @staticmethod
    def test_read_document_fails_with_parse_cause_for_invalid_file(
        tmp_path: Path,
    ) -> None:
        """Invalid TOML fails at the typed boundary and keeps the parse error."""
        toml_file = tmp_path / "invalid.toml"
        toml_file.write_text(c.Tests.TOML_INVALID_CONTENT, encoding="utf-8")

        result = u.Cli.toml_read_document(toml_file)

        tm.fail(result, has="TOML parse failed")
        tm.that(result.exception, is_=ParseError)

    @staticmethod
    def test_read_document_fails_with_read_cause_for_unreadable_path(
        tmp_path: Path,
    ) -> None:
        """An unreadable existing path fails as a read operation with its cause."""
        result = u.Cli.toml_read_document(tmp_path)

        tm.fail(result, has="read TOML")
        tm.that(result.exception, is_=IsADirectoryError)

    @staticmethod
    def test_read_json_round_trips_document_to_mapping(tmp_path: Path) -> None:
        """Verify that read json round trips document to mapping."""
        toml_file = tmp_path / c.PYPROJECT_FILENAME
        toml_file.write_text(
            '[project]\nname = "demo"\ndependencies = ["httpx>=0.27"]\n',
            encoding="utf-8",
        )

        result = u.Cli.toml_read_json(toml_file)

        tm.ok(result)
        project = u.Cli.toml_mapping_child(result.value, "project")
        project = tm.not_none(project)
        tm.that(project.get("name"), eq="demo")

    # ----------------------------------------------------------------- write

    @staticmethod
    def test_write_document_persists_file(tmp_path: Path) -> None:
        """Verify that write document persists file."""
        toml_file = tmp_path / "doc.toml"
        doc = u.Cli.toml_document()
        doc["section"] = {"key": "value"}

        result = u.Cli.toml_write_document(toml_file, doc)

        tm.ok(result)
        tm.ok(toml_file.exists())

    @staticmethod
    def test_write_document_creates_missing_parent_directories(
        tmp_path: Path,
    ) -> None:
        """Verify that write document creates missing parent directories."""
        toml_file = tmp_path / "nested" / "deep" / "file.toml"
        doc = u.Cli.toml_document()
        doc["key"] = "value"

        tm.ok(u.Cli.toml_write_document(toml_file, doc))
        tm.ok(toml_file.exists())

    @staticmethod
    def test_write_pyproject_runs_the_required_real_formatter(
        tmp_path: Path,
    ) -> None:
        """Format a real pyproject through the public TOML facade."""
        pyproject = tmp_path / c.PYPROJECT_FILENAME
        taplo_config = tmp_path / ".taplo.toml"
        taplo_config.write_text("", encoding="utf-8")
        doc = u.Cli.toml_document()
        doc["project"] = {"name": "demo"}

        tm.ok(u.Cli.toml_write_document(pyproject, doc))

        rendered = tomllib.loads(pyproject.read_text(encoding="utf-8"))
        tm.that(rendered["project"], eq={"name": "demo"})

    @staticmethod
    def test_write_document_fails_when_target_is_not_writable(
        tmp_path: Path,
    ) -> None:
        """Verify that write document fails when target is not writable."""
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        toml_file = readonly_dir / "test.toml"
        readonly_dir.chmod(stat.S_IRUSR | stat.S_IXUSR)
        try:
            doc = u.Cli.toml_document()
            doc["key"] = "value"

            result = u.Cli.toml_write_document(toml_file, doc)

            tm.fail(result, has="TOML write")
        finally:
            readonly_dir.chmod(stat.S_IRWXU)

    @staticmethod
    def test_write_mapping_renders_nested_tables_to_disk(tmp_path: Path) -> None:
        """Verify that write mapping renders nested tables to disk."""
        toml_file = tmp_path / c.PYPROJECT_FILENAME
        payload: t.JsonDict = {
            "project": {"name": "demo"},
            "tool": {"uv": {"sources": {"flext-core": {"workspace": True}}}},
        }

        tm.ok(u.Cli.toml_write_mapping(toml_file, payload))

        rendered = tomllib.loads(toml_file.read_text(encoding="utf-8"))
        tm.that(rendered["tool"], is_=dict)
        tool = rendered["tool"]
        tm.that(tool["uv"], is_=dict)
        sources = tool["uv"]["sources"]
        tm.that(sources, is_=dict)
        tm.that(sources["flext-core"], is_=dict)
        tm.ok(sources["flext-core"]["workspace"])
        tm.that(rendered["project"], eq={"name": "demo"})


class TestsFlextCliTomlValues:
    """Native TOML construction, navigation and JSON projection contracts."""

    @staticmethod
    def test_array_serializes_all_elements() -> None:
        """Verify that array serializes all elements."""
        arr = u.Cli.toml_array(["a", "b", "c"])

        arr_text = arr.as_string()

        tm.that(arr_text, has='"a"')
        tm.that(arr_text, has='"b"')
        tm.that(arr_text, has='"c"')

    @staticmethod
    def test_ensure_table_reuses_existing_child() -> None:
        """Verify that ensure table reuses existing child."""
        parent = u.Cli.toml_table()
        existing = u.Cli.toml_table()
        existing["key"] = "value"
        parent["section"] = existing

        table = u.Cli.toml_ensure_table(parent, "section")

        tm.that(u.Cli.toml_value(table, "key"), eq="value")

    # ------------------------------------------------------------ navigation

    @staticmethod
    def test_path_helpers_create_and_resolve_nested_tables() -> None:
        """Verify that path helpers create and resolve nested tables."""
        doc = u.Cli.toml_document()

        created = u.Cli.toml_ensure_path(doc, ("tool", "ruff", "lint"))
        created["select"] = u.Cli.toml_array(["E", "F"])

        resolved = u.Cli.toml_table_path(doc, ("tool", "ruff", "lint"))
        resolved = tm.not_none(resolved)
        tm.that(
            list(u.Cli.toml_as_string_list(u.Cli.toml_item_child(resolved, "select"))),
            eq=["E", "F"],
        )
        tm.that(u.Cli.toml_table_path(doc, ("tool", "mypy")), none=True)

    @staticmethod
    def test_mapping_path_normalizes_document_children() -> None:
        """Verify that mapping path normalizes document children."""
        doc = u.Cli.toml_document()
        project = u.Cli.toml_table()
        tool = u.Cli.toml_table()
        pytest_config = u.Cli.toml_table()
        pytest_config["addopts"] = "-q"
        tool["pytest"] = pytest_config
        project["name"] = "demo"
        doc["project"] = project
        doc["tool"] = tool

        resolved = u.Cli.toml_mapping_path(doc, ["tool", "pytest"])

        resolved = tm.not_none(resolved)
        tm.that(resolved["addopts"], eq="-q")

    # -------------------------------------------------------------- mappings

    @staticmethod
    def test_as_mapping_accepts_mappings_and_rejects_scalars() -> None:
        """Verify that as mapping accepts mappings and rejects scalars."""
        mapping: t.MappingKV[str, t.Scalar] = {"key": "value"}

        tm.that(u.Cli.toml_as_mapping(mapping), eq=mapping)
        tm.that(u.Cli.toml_as_mapping("bad"), none=True)

    @staticmethod
    @pytest.mark.parametrize(
        ("key", "expected"),
        [("a", 1), ("b", [1, 2]), ("missing", None)],
    )
    def test_value_lookup_returns_stored_values_or_none(
        key: str,
        expected: t.JsonValue | None,
    ) -> None:
        """Verify that value lookup returns stored values or none."""
        doc = u.Cli.toml_document()
        doc["a"] = 1
        doc["b"] = [1, 2]

        tm.that(u.Cli.toml_value(doc, key), eq=expected)

    @staticmethod
    def test_mapping_from_text_and_document_builder_round_trip() -> None:
        """Verify that mapping from text and document builder round trip."""
        text = (
            "[project]\n"
            'name = "demo"\n'
            'dependencies = ["httpx>=0.27"]\n'
            "\n"
            "[tool.pytest.ini_options]\n"
            'addopts = ["-q"]\n'
        )

        mapping = u.Cli.toml_mapping_from_text(text)

        mapping = tm.not_none(mapping)
        document = u.Cli.toml_document_from_mapping(mapping)
        project = u.Cli.toml_table_child(document, "project")
        project = tm.not_none(project)
        tm.that(u.Cli.toml_value(project, "name"), eq="demo")
        tm.that(
            list(
                u.Cli.toml_as_string_list(
                    u.Cli.toml_item_child(project, "dependencies")
                )
            ),
            eq=["httpx>=0.27"],
        )

    @staticmethod
    def test_mapping_from_text_rejects_invalid_toml() -> None:
        """Verify that mapping from text rejects invalid toml."""
        tm.that(u.Cli.toml_mapping_from_text("[project"), none=True)

    @staticmethod
    def test_sorted_item_preserves_values_and_original_mapping() -> None:
        """Construct sorted native tables without changing arrays or callers."""
        payload: t.JsonDict = {
            "zeta": {"z": 1, "a": 2},
            "alpha": {
                "z": 3,
                "ordered": ["last", " first "],
                "a": 4,
                "branch": {"z": 5, "a": 6},
            },
        }
        original = deepcopy(payload)
        document = u.Cli.toml_document()
        document["fixture"] = u.Cli.toml_item_from_json_value(payload, sort_keys=True)
        rendered = tm.not_none(u.Cli.toml_mapping_from_text(u.Cli.toml_dumps(document)))
        mapping = tm.not_none(u.Cli.toml_mapping_child(rendered, "fixture"))
        alpha = tm.not_none(u.Cli.toml_mapping_child(mapping, "alpha"))
        branch = tm.not_none(u.Cli.toml_mapping_child(alpha, "branch"))

        tm.that(list(mapping), eq=sorted(mapping))
        tm.that([key for key in alpha if key != "branch"], eq=["a", "ordered", "z"])
        tm.that(list(branch), eq=sorted(branch))
        tm.that(mapping, eq=original)
        tm.that(payload, eq=original)

    @staticmethod
    def test_native_item_rejects_null() -> None:
        """A null cannot silently disappear from native TOML output."""
        with pytest.raises(TypeError, match="TOML does not support null values"):
            u.Cli.toml_item_from_json_value(None)

    @staticmethod
    @pytest.mark.parametrize(
        "value", [None, " value ", [" last ", "first"], {"option": None}]
    )
    def test_json_projection_preserves_exact_json_values(value: t.JsonValue) -> None:
        """The JSON boundary preserves null, whitespace and sequence order."""
        tm.that(u.Cli.toml_unwrap_item(value), eq=value)

    @staticmethod
    @pytest.mark.parametrize(
        "value",
        [{"payload": b"value"}, {"stamp": datetime(2026, 1, 1, tzinfo=UTC)}],
    )
    def test_json_projection_rejects_non_json_scalar_mappings(
        value: t.ScalarMapping,
    ) -> None:
        """Unsupported scalars cannot become strings at the JSON boundary."""
        with pytest.raises(m.ValidationError):
            u.Cli.toml_unwrap_item(value)

    @staticmethod
    def test_json_projection_rejects_native_toml_datetime() -> None:
        """A native timestamp remains unsupported by the JSON projection."""
        document = tm.not_none(u.Cli.toml_parse_text("stamp = 2026-01-01T00:00:00\n"))
        with pytest.raises(m.ValidationError):
            u.Cli.toml_as_mapping(document)

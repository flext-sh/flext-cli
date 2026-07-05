"""Behavioral tests for the generic TOML helpers exposed via ``u.Cli.toml_*``.

Every test exercises only the public helper contract: return values, ``r[T]``
success/failure outcomes and the observable state of the produced TOML
documents/mappings. No private attributes, internal collaborators or
implementation structures are inspected.
"""

from __future__ import annotations

import os
import stat
import tomllib
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from tests.utilities import u

if TYPE_CHECKING:
    from collections.abc import Generator

    from tests.typings import t


class TestsFlextCliTomlUtilities:
    """Public contract of the ``u.Cli.toml_*`` helper family."""

    @staticmethod
    @contextmanager
    def _temporary_environment(overrides: t.StrMapping) -> Generator[None]:
        """Scope environment variable overrides to a ``with`` block."""
        original_values = {key: os.environ.get(key) for key in overrides}
        try:
            for key, value in overrides.items():
                os.environ[key] = value
            yield
        finally:
            for key, value in original_values.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value

    # ------------------------------------------------------------------ read

    def test_read_returns_parsed_document_for_valid_file(
        self,
        tmp_path: Path,
    ) -> None:
        toml_file = tmp_path / "test.toml"
        toml_file.write_text(
            '[section]\nkey = "value"\nnumber = 42\n',
            encoding="utf-8",
        )

        doc = u.Cli.toml_read(toml_file)

        assert doc is not None
        section = u.Cli.toml_table_child(doc, "section")
        assert section is not None
        tm.that(u.Cli.toml_value(section, "key"), eq="value")
        tm.that(u.Cli.toml_value(section, "number"), eq=42)

    @pytest.mark.parametrize(
        ("filename", "contents"),
        [
            ("missing.toml", None),
            ("invalid.toml", "[invalid\nkey = value"),
        ],
    )
    def test_read_returns_none_for_missing_or_invalid_file(
        self,
        tmp_path: Path,
        filename: str,
        contents: str | None,
    ) -> None:
        toml_file = tmp_path / filename
        if contents is not None:
            toml_file.write_text(contents, encoding="utf-8")

        tm.that(u.Cli.toml_read(toml_file), none=True)

    def test_read_document_succeeds_and_preserves_values(
        self,
        tmp_path: Path,
    ) -> None:
        toml_file = tmp_path / "test.toml"
        toml_file.write_text('[section]\nkey = "value"  # comment\n', encoding="utf-8")

        result = u.Cli.toml_read_document(toml_file)

        tm.ok(result)
        section = u.Cli.toml_table_child(result.value, "section")
        assert section is not None
        tm.that(u.Cli.toml_value(section, "key"), eq="value")

    def test_read_document_fails_with_not_found_for_missing_file(
        self,
        tmp_path: Path,
    ) -> None:
        tm.fail(
            u.Cli.toml_read_document(tmp_path / "missing.toml"),
            has="not found",
        )

    def test_read_json_round_trips_document_to_mapping(
        self,
        tmp_path: Path,
    ) -> None:
        toml_file = tmp_path / "pyproject.toml"
        toml_file.write_text(
            '[project]\nname = "demo"\ndependencies = ["httpx>=0.27"]\n',
            encoding="utf-8",
        )

        result = u.Cli.toml_read_json(toml_file)

        tm.ok(result)
        project = u.Cli.toml_mapping_child(result.value, "project")
        assert project is not None
        tm.that(project.get("name"), eq="demo")

    # ----------------------------------------------------------------- write

    def test_write_document_persists_file(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "doc.toml"
        doc = u.Cli.toml_document()
        doc["section"] = {"key": "value"}

        result = u.Cli.toml_write_document(toml_file, doc)

        tm.ok(result)
        tm.that(toml_file.exists(), eq=True)

    def test_write_document_creates_missing_parent_directories(
        self,
        tmp_path: Path,
    ) -> None:
        toml_file = tmp_path / "nested" / "deep" / "file.toml"
        doc = u.Cli.toml_document()
        doc["key"] = "value"

        tm.ok(u.Cli.toml_write_document(toml_file, doc))
        tm.that(toml_file.exists(), eq=True)

    def test_write_pyproject_invokes_taplo_formatter(self, tmp_path: Path) -> None:
        pyproject = tmp_path / "pyproject.toml"
        taplo_config = tmp_path / ".taplo.toml"
        command_log = tmp_path / "taplo.log"
        bin_dir = tmp_path / "bin"
        bin_dir.mkdir()
        taplo_config.write_text("", encoding="utf-8")
        taplo = bin_dir / "taplo"
        taplo.write_text(
            "#!/bin/sh\n"
            f"printf '%s\\n' \"$PWD\" > '{command_log}'\n"
            'for arg in "$@"; do\n'
            f"  printf '%s\\n' \"$arg\" >> '{command_log}'\n"
            "done\n",
            encoding="utf-8",
        )
        taplo.chmod(stat.S_IRWXU)
        doc = u.Cli.toml_document()
        doc["project"] = {"name": "demo"}

        with self._temporary_environment({
            "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
        }):
            tm.ok(u.Cli.toml_write_document(pyproject, doc))

        logged_command = command_log.read_text(encoding="utf-8").splitlines()
        tm.that(logged_command[0], eq=str(tmp_path))
        tm.that(logged_command[1:3], eq=["format", "--config"])
        tm.that(logged_command, contains="--config")
        tm.that(logged_command, contains=str(taplo_config))
        tm.that(logged_command, contains=str(pyproject))

    def test_write_document_fails_when_target_is_not_writable(
        self,
        tmp_path: Path,
    ) -> None:
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

    def test_write_mapping_renders_nested_tables_to_disk(
        self,
        tmp_path: Path,
    ) -> None:
        toml_file = tmp_path / "pyproject.toml"
        payload: dict[str, t.JsonValue] = {
            "project": {"name": "demo"},
            "tool": {"uv": {"sources": {"flext-core": {"workspace": True}}}},
        }

        tm.ok(u.Cli.toml_write_mapping(toml_file, payload))

        rendered = tomllib.loads(toml_file.read_text(encoding="utf-8"))
        assert isinstance(rendered["tool"], dict)
        tool = rendered["tool"]
        assert isinstance(tool["uv"], dict)
        sources = tool["uv"]["sources"]
        assert isinstance(sources, dict)
        assert isinstance(sources["flext-core"], dict)
        tm.that(sources["flext-core"]["workspace"], eq=True)
        tm.that(rendered["project"], eq={"name": "demo"})

    # -------------------------------------------------------------- builders

    def test_array_serializes_all_elements(self) -> None:
        arr = u.Cli.toml_array(["a", "b", "c"])

        arr_text = arr.as_string()

        tm.that(arr_text, has='"a"')
        tm.that(arr_text, has='"b"')
        tm.that(arr_text, has='"c"')

    def test_ensure_table_reuses_existing_child(self) -> None:
        parent = u.Cli.toml_table()
        existing = u.Cli.toml_table()
        existing["key"] = "value"
        parent["section"] = existing

        table = u.Cli.toml_ensure_table(parent, "section")

        tm.that(u.Cli.toml_value(table, "key"), eq="value")

    # ------------------------------------------------------------ navigation

    def test_path_helpers_create_and_resolve_nested_tables(self) -> None:
        doc = u.Cli.toml_document()

        created = u.Cli.toml_ensure_path(doc, ("tool", "ruff", "lint"))
        created["select"] = u.Cli.toml_array(["E", "F"])

        resolved = u.Cli.toml_table_path(doc, ("tool", "ruff", "lint"))
        assert resolved is not None
        tm.that(
            u.Cli.toml_as_string_list(u.Cli.toml_item_child(resolved, "select")),
            eq=["E", "F"],
        )
        tm.that(u.Cli.toml_table_path(doc, ("tool", "mypy")), none=True)

    def test_navigate_path_and_dot_path_keep_tool_prefix_stable(self) -> None:
        doc = u.Cli.toml_document()
        table = u.Cli.toml_navigate_path(doc, ["tool", "pytest", "ini_options"])
        table["addopts"] = "-q"

        tm.that(
            u.Cli.toml_dot_path("", "tool", "pytest", "ini_options"),
            eq="tool.pytest.ini_options",
        )
        tm.that(
            u.Cli.toml_value(
                u.Cli.toml_navigate_path(doc, ["pytest", "ini_options"]),
                "addopts",
            ),
            eq="-q",
        )

    def test_mapping_path_normalizes_document_children(self) -> None:
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

        assert resolved is not None
        tm.that(resolved["addopts"], eq="-q")

    # -------------------------------------------------------------- mappings

    def test_as_mapping_accepts_mappings_and_rejects_scalars(self) -> None:
        mapping: t.MappingKV[str, t.Scalar] = {"key": "value"}

        tm.that(u.Cli.toml_as_mapping(mapping), eq=mapping)
        tm.that(u.Cli.toml_as_mapping("bad"), none=True)

    @pytest.mark.parametrize(
        ("key", "expected"),
        [
            ("a", 1),
            ("b", [1, 2]),
            ("missing", None),
        ],
    )
    def test_value_lookup_returns_stored_values_or_none(
        self,
        key: str,
        expected: t.JsonValue | None,
    ) -> None:
        doc = u.Cli.toml_document()
        doc["a"] = 1
        doc["b"] = [1, 2]

        tm.that(u.Cli.toml_value(doc, key), eq=expected)

    def test_mapping_from_text_and_document_builder_round_trip(self) -> None:
        text = (
            "[project]\n"
            'name = "demo"\n'
            'dependencies = ["httpx>=0.27"]\n'
            "\n"
            "[tool.pytest.ini_options]\n"
            'addopts = ["-q"]\n'
        )

        mapping = u.Cli.toml_mapping_from_text(text)

        assert mapping is not None
        document = u.Cli.toml_document_from_mapping(mapping)
        project = u.Cli.toml_table_child(document, "project")
        assert project is not None
        tm.that(u.Cli.toml_value(project, "name"), eq="demo")
        tm.that(
            u.Cli.toml_as_string_list(u.Cli.toml_item_child(project, "dependencies")),
            eq=["httpx>=0.27"],
        )

    def test_mapping_from_text_rejects_invalid_toml(self) -> None:
        tm.that(u.Cli.toml_mapping_from_text("[project"), none=True)

    def test_mapping_sync_helpers_report_and_apply_changes(self) -> None:
        payload: dict[str, t.JsonValue] = {
            "tool": {"uv": {"sources": {"stale": {"workspace": True}}}},
        }
        changes: list[str] = []

        sources = u.Cli.toml_mapping_ensure_path(payload, ("tool", "uv", "sources"))
        if u.Cli.toml_mapping_sync_mapping_table(
            sources,
            "flext-core",
            {"workspace": True},
            sort_keys=True,
        ):
            changes.append("synced flext-core")
        if u.Cli.toml_mapping_sync_string_list(
            u.Cli.toml_mapping_ensure_path(payload, ("tool", "uv", "workspace")),
            "members",
            ("flext-cli", "flext-core"),
            sort_values=True,
        ):
            changes.append("synced members")

        tm.that(changes, eq=["synced flext-core", "synced members"])
        tool = u.Cli.toml_mapping_child(payload, "tool")
        assert tool is not None
        uv = u.Cli.toml_mapping_child(tool, "uv")
        assert uv is not None
        workspace = u.Cli.toml_mapping_child(uv, "workspace")
        assert workspace is not None
        tm.that(workspace.get("members"), eq=["flext-cli", "flext-core"])


__all__: list[str] = ["TestsFlextCliTomlUtilities"]

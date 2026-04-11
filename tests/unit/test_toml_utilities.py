"""Tests for the generic TOML helpers exposed via ``u.Cli.toml_*``."""

from __future__ import annotations

import os
import stat
from collections.abc import Generator, Mapping
from contextlib import contextmanager
from pathlib import Path

from flext_tests import tm

from tests import t, u


@contextmanager
def _temporary_environment(
    overrides: Mapping[str, str],
) -> Generator[None]:
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


class TestCliTomlRead:
    """Tests for TOML read operations."""

    def test_read_existing_file(self, tmp_path: Path) -> None:
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

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        tm.that(u.Cli.toml_read(tmp_path / "missing.toml"), none=True)

    def test_read_invalid_toml(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "invalid.toml"
        toml_file.write_text("[invalid\nkey = value", encoding="utf-8")
        tm.that(u.Cli.toml_read(toml_file), none=True)


class TestCliTomlDocument:
    """Tests for TOML document read/write operations."""

    def test_read_document_existing_file(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "test.toml"
        toml_file.write_text('[section]\nkey = "value"  # comment\n', encoding="utf-8")

        result = u.Cli.toml_read_document(toml_file)

        tm.ok(result)
        section = u.Cli.toml_table_child(result.value, "section")
        assert section is not None
        tm.that(u.Cli.toml_value(section, "key"), eq="value")

    def test_read_document_nonexistent_file(self, tmp_path: Path) -> None:
        tm.fail(
            u.Cli.toml_read_document(tmp_path / "missing.toml"),
            has="failed to read TOML",
        )

    def test_write_document(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "doc.toml"
        doc = u.Cli.toml_document()
        doc["section"] = {"key": "value"}

        result = u.Cli.toml_write_document(toml_file, doc)

        tm.ok(result)
        tm.that(toml_file.exists(), eq=True)

    def test_write_creates_parent_directories(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "nested" / "deep" / "file.toml"
        doc = u.Cli.toml_document()
        doc["key"] = "value"

        tm.ok(u.Cli.toml_write_document(toml_file, doc))
        tm.that(toml_file.exists(), eq=True)

    def test_write_pyproject_runs_taplo(self, tmp_path: Path) -> None:
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
        with _temporary_environment({
            "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}",
        }):
            tm.ok(u.Cli.toml_write_document(pyproject, doc))
        logged_command = command_log.read_text(encoding="utf-8").splitlines()
        tm.that(logged_command[0], eq=str(tmp_path))
        tm.that(logged_command[1:3], eq=["format", "--settings"])
        tm.that(logged_command, contains="--settings")
        tm.that(logged_command, contains=str(taplo_config))
        tm.that(logged_command, contains=str(pyproject))

    def test_write_permission_error(self, tmp_path: Path) -> None:
        readonly_dir = tmp_path / "readonly"
        readonly_dir.mkdir()
        toml_file = readonly_dir / "test.toml"
        Path(readonly_dir).chmod(stat.S_IRUSR | stat.S_IXUSR)
        try:
            doc = u.Cli.toml_document()
            doc["key"] = "value"
            result = u.Cli.toml_write_document(toml_file, doc)
            tm.fail(result, has="TOML write error")
        finally:
            Path(readonly_dir).chmod(stat.S_IRWXU)


class TestCliTomlHelpers:
    """Tests for generic TOML helper methods."""

    def test_array_creates_multiline(self) -> None:
        arr = u.Cli.toml_array(["a", "b", "c"])
        arr_text = arr.as_string()
        tm.that(arr_text, has='"a"')
        tm.that(arr_text, has='"b"')
        tm.that(arr_text, has='"c"')

    def test_ensure_table_reuses_existing(self) -> None:
        parent = u.Cli.toml_table()
        existing = u.Cli.toml_table()
        existing["key"] = "value"
        parent["section"] = existing

        table = u.Cli.toml_ensure_table(parent, "section")

        tm.that(u.Cli.toml_value(table, "key"), eq="value")

    def test_path_helpers_navigate_and_lookup_tables(self) -> None:
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

    def test_dot_path_and_navigate_path_keep_tool_prefix_stable(self) -> None:
        doc = u.Cli.toml_document()
        table = u.Cli.toml_navigate_path(doc, ["tool", "pytest", "ini_options"])

        table["addopts"] = "-q"

        tm.that(
            u.Cli.toml_dot_path("", "tool", "pytest", "ini_options"),
            eq="tool.pytest.ini_options",
        )
        tm.that(
            u.Cli.toml_value(
                u.Cli.toml_navigate_path(doc, ["pytest", "ini_options"]), "addopts"
            ),
            eq="-q",
        )

    def test_as_mapping_and_lookup_helpers(self) -> None:
        mapping: Mapping[str, t.RecursiveContainer] = {"key": "value"}
        tm.that(u.Cli.toml_as_mapping(mapping), eq=mapping)
        tm.that(u.Cli.toml_as_mapping("bad"), none=True)
        doc = u.Cli.toml_document()
        doc["a"] = 1
        doc["b"] = [1, 2]
        tm.that(u.Cli.toml_value(doc, "a"), eq=1)
        tm.that(u.Cli.toml_value(doc, "b"), eq=[1, 2])
        tm.that(u.Cli.toml_value(doc, "missing"), none=True)

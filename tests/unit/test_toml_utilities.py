"""Tests for the generic TOML helpers exposed via ``u.Cli.toml_*``."""

from __future__ import annotations

import stat
import subprocess
from collections.abc import Mapping
from pathlib import Path

import pytest
from flext_tests import tm

from tests import t, u


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
        section = u.Cli.toml_get_table(doc, "section")
        assert section is not None
        tm.that(u.Cli.toml_get(section, "key"), eq="value")
        tm.that(u.Cli.toml_get(section, "number"), eq=42)

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
        section = u.Cli.toml_get_table(result.value, "section")
        assert section is not None
        tm.that(u.Cli.toml_get(section, "key"), eq="value")

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

    def test_write_pyproject_runs_taplo(
        self,
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        pyproject = tmp_path / "pyproject.toml"
        taplo_config = tmp_path / ".taplo.toml"
        taplo_config.write_text("", encoding="utf-8")
        doc = u.Cli.toml_document()
        doc["project"] = {"name": "demo"}
        commands: list[tuple[list[str], Path | None]] = []

        def _run(
            cmd: list[str],
            *,
            cwd: Path | None = None,
            capture_output: bool,
            check: bool,
            text: bool,
        ) -> subprocess.CompletedProcess[str]:
            _ = (capture_output, check, text)
            commands.append((cmd, cwd))
            return subprocess.CompletedProcess(cmd, 0, "", "")

        monkeypatch.setattr("flext_cli._utilities.toml.subprocess.run", _run)

        tm.ok(u.Cli.toml_write_document(pyproject, doc))
        tm.that(len(commands), eq=1)
        tm.that(commands[0][0][:2], eq=["taplo", "format"])
        tm.that(commands[0][0], contains="--config")
        tm.that(commands[0][0], contains=str(taplo_config))
        tm.that(commands[0][0], contains=str(pyproject))
        tm.that(commands[0][1], eq=tmp_path)

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

        tm.that(u.Cli.toml_get(table, "key"), eq="value")

    def test_as_mapping_and_get_helpers(self) -> None:
        mapping: Mapping[str, t.RecursiveContainer] = {"key": "value"}
        tm.that(u.Cli.toml_as_mapping(mapping), eq=mapping)
        tm.that(u.Cli.toml_as_mapping("bad"), none=True)
        doc = u.Cli.toml_document()
        doc["a"] = 1
        doc["b"] = [1, 2]
        tm.that(u.Cli.toml_get(doc, "a"), eq=1)
        tm.that(u.Cli.toml_get(doc, "b"), eq=[1, 2])
        tm.that(u.Cli.toml_get(doc, "missing"), none=True)

"""Tests for the generic TOML helpers exposed via ``u.Cli.toml_*``."""

from __future__ import annotations

import os
import stat
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from flext_tests import tm
from tests import u

from collections.abc import Generator

from tests import p, t



class TestsFlextCliTomlUtilities:
    """Implementation part for TestsFlextCliTomlUtilities."""

    @staticmethod
    @contextmanager
    def _temporary_environment(overrides: t.StrMapping) -> Generator[None]:
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

    def test_read_existing_file(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "test.toml"
        toml_file.write_text(
            '[section]\nkey = "value"\nnumber = 42\n', encoding="utf-8"
        )

        doc = u.Cli.toml_read(toml_file)

        tm.that(doc, none=False)
        section = u.Cli.toml_table_child(doc, "section")
        tm.that(section, none=False)
        tm.that(u.Cli.toml_value(section, "key"), eq="value")
        tm.that(u.Cli.toml_value(section, "number"), eq=42)

    def test_read_nonexistent_file(self, tmp_path: Path) -> None:
        tm.that(u.Cli.toml_read(tmp_path / "missing.toml"), none=True)

    def test_read_invalid_toml(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "invalid.toml"
        toml_file.write_text("[invalid\nkey = value", encoding="utf-8")
        tm.that(u.Cli.toml_read(toml_file), none=True)

    def test_read_document_existing_file(self, tmp_path: Path) -> None:
        toml_file = tmp_path / "test.toml"
        toml_file.write_text('[section]\nkey = "value"  # comment\n', encoding="utf-8")

        result = u.Cli.toml_read_document(toml_file)

        tm.ok(result)
        section = u.Cli.toml_table_child(result.value, "section")
        tm.that(section, none=False)
        tm.that(u.Cli.toml_value(section, "key"), eq="value")

    def test_read_document_nonexistent_file(self, tmp_path: Path) -> None:
        tm.fail(u.Cli.toml_read_document(tmp_path / "missing.toml"), has="not found")

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
        with self._temporary_environment({
            "PATH": f"{bin_dir}:{os.environ.get('PATH', '')}"
        }):
            tm.ok(u.Cli.toml_write_document(pyproject, doc))
        logged_command = command_log.read_text(encoding="utf-8").splitlines()
        tm.that(logged_command[0], eq=str(tmp_path))
        tm.that(logged_command[1:3], eq=["format", "--config"])
        tm.that(logged_command, contains="--config")
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
            tm.fail(result, has="TOML write")
        finally:
            Path(readonly_dir).chmod(stat.S_IRWXU)

    def test_array_creates_multiline(self) -> None:
        arr = u.Cli.toml_array(["a", "b", "c"])
        arr_text = arr.as_string()
        tm.that(arr_text, has='"a"')
        tm.that(arr_text, has='"b"')
        tm.that(arr_text, has='"c"')


__all__: list[str] = ["TestsFlextCliTomlUtilities"]

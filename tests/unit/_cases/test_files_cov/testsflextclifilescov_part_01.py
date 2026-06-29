"""Coverage tests for _utilities/files.py — 100% via public interfaces."""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_tests import tm
from tests.constants import c
from tests.models import m
from tests.typings import t
from tests.utilities import u

from flext_cli import cli


class TestsFlextCliFilesCov:
    """Implementation part for TestsFlextCliFilesCov."""

    @pytest.mark.parametrize(
        ("filename", "expected_format"),
        c.Tests.FILES_DETECT_FORMAT_CASES,
    )
    def test_files_detect_format_known(
        self, filename: str, expected_format: str
    ) -> None:
        result = cli.detect_file_format(filename)
        tm.ok(result)
        tm.that(result.value, eq=expected_format)

    @pytest.mark.parametrize("filename", c.Tests.FILES_DETECT_FORMAT_FAIL_CASES)
    def test_files_detect_format_unknown(self, filename: str) -> None:
        result = cli.detect_file_format(filename)
        tm.fail(result)

    def test_files_read_write_text(self, tmp_path: Path) -> None:
        path = tmp_path / "test.txt"
        write_result = u.Cli.files_write_text(path, "hello world")
        tm.ok(write_result)
        read_result = u.Cli.files_read_text(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq="hello world")

    def test_files_read_text_missing(self, tmp_path: Path) -> None:
        result = u.Cli.files_read_text(tmp_path / "missing.txt")
        tm.fail(result)

    def test_files_write_text_invalid_path(self) -> None:
        result = u.Cli.files_write_text("/nonexistent_dir/x/y/z/file.txt", "x")
        tm.fail(result)

    def test_files_read_write_json(self, tmp_path: Path) -> None:
        path = tmp_path / "data.json"
        write_result = cli.write_json_file(path, {"key": "value"})
        tm.ok(write_result)
        read_result = cli.read_json_file(path)
        tm.ok(read_result)

    def test_files_read_json_missing(self, tmp_path: Path) -> None:
        result = cli.read_json_file(tmp_path / "missing.json")
        tm.fail(result)

    def test_files_read_json_model(self, tmp_path: Path) -> None:
        path = tmp_path / "opts.json"
        path.write_text('{"indent": 4, "sort_keys": true}', encoding="utf-8")
        result = cli.read_json_model(path, m.Cli.JsonWriteOptions)
        tm.ok(result)
        tm.that(result.value.indent, eq=4)

    def test_files_read_write_yaml(self, tmp_path: Path) -> None:
        path = tmp_path / "data.yaml"
        write_result = cli.write_yaml_file(path, {"key": "val"})
        tm.ok(write_result)
        read_result = cli.read_yaml_file(path)
        tm.ok(read_result)

    def test_files_read_yaml_missing(self, tmp_path: Path) -> None:
        result = cli.read_yaml_file(tmp_path / "missing.yaml")
        tm.fail(result)

    def test_files_read_yaml_empty_path(self) -> None:
        result = cli.read_yaml_file("   ")
        tm.fail(result)

    def test_files_write_read_csv(self, tmp_path: Path) -> None:
        path = tmp_path / "data.csv"
        rows: list[t.StrSequence] = [["name", "age"], ["alice", "30"], ["bob", "25"]]
        write_result = cli.write_csv_file(path, rows)
        tm.ok(write_result)
        read_result = cli.read_csv_file_with_headers(path)
        tm.ok(read_result)
        tm.that(len(read_result.value), eq=2)

    def test_files_read_csv_missing(self, tmp_path: Path) -> None:
        result = cli.read_csv_file_with_headers(tmp_path / "missing.csv")
        tm.fail(result)

    def test_files_write_read_binary(self, tmp_path: Path) -> None:
        path = tmp_path / "data.bin"
        write_result = cli.write_binary_file(path, b"\x00\x01\x02")
        tm.ok(write_result)
        read_result = cli.read_binary_file(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq=b"\x00\x01\x02")

    def test_files_read_binary_missing(self, tmp_path: Path) -> None:
        result = cli.read_binary_file(tmp_path / "missing.bin")
        tm.fail(result)

    def test_files_copy(self, tmp_path: Path) -> None:
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("content", encoding="utf-8")
        result = cli.copy_file(src, dst)
        tm.ok(result)
        tm.that(dst.read_text(encoding="utf-8"), eq="content")

    def test_files_delete(self, tmp_path: Path) -> None:
        path = tmp_path / "to_delete.txt"
        path.write_text("bye", encoding="utf-8")
        result = u.Cli.files_delete(path)
        tm.ok(result)
        tm.that(path.exists(), eq=False)

    def test_files_delete_missing(self, tmp_path: Path) -> None:
        """files_delete is idempotent — missing path returns success (rm -f)."""
        result = u.Cli.files_delete(tmp_path / "missing.txt")
        tm.ok(result)

    def test_ensure_dir_creates(self, tmp_path: Path) -> None:
        target = tmp_path / "new" / "subdir"
        result = u.Cli.ensure_dir(target)
        tm.ok(result)
        tm.that(target.exists(), eq=True)

    def test_ensure_symlink(self, tmp_path: Path) -> None:
        source = tmp_path / "real_dir"
        source.mkdir()
        link = tmp_path / "link_dir"
        result = u.Cli.ensure_symlink(link, source)
        tm.ok(result)

    def test_ensure_symlink_idempotent(self, tmp_path: Path) -> None:
        source = tmp_path / "real_dir"
        source.mkdir()
        link = tmp_path / "link_dir"
        u.Cli.ensure_symlink(link, source)
        result = u.Cli.ensure_symlink(link, source)
        tm.ok(result)


__all__: list[str] = ["TestsFlextCliFilesCov"]

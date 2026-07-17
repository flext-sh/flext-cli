"""Coverage tests for _utilities/files.py — 100% via public interfaces."""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_tests import tm
from tests import c, m, t, u

from flext_cli import cli


class TestsFlextCliFilesCov:
    """Implementation part for TestsFlextCliFilesCov."""

    @pytest.mark.parametrize(
        ("filename", "expected_format"), c.Tests.FILES_DETECT_FORMAT_CASES
    )
    def test_files_detect_format_known(
        self, filename: str, expected_format: str
    ) -> None:
        """Resolve every configured known file suffix."""
        result = cli.detect_file_format(filename)
        tm.ok(result)
        tm.that(result.value, eq=expected_format)

    @pytest.mark.parametrize("filename", c.Tests.FILES_DETECT_FORMAT_FAIL_CASES)
    def test_files_detect_format_unknown(self, filename: str) -> None:
        """Reject file suffixes outside the configured format registry."""
        result = cli.detect_file_format(filename)
        tm.fail(result)

    def test_files_read_write_text(self, tmp_path: Path) -> None:
        """Round-trip UTF-8 text through the public file utilities."""
        path = tmp_path / "test.txt"
        write_result = u.Cli.files_write_text(path, "hello world")
        tm.ok(write_result)
        read_result = u.Cli.files_read_text(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq="hello world")

    def test_files_read_text_missing(self, tmp_path: Path) -> None:
        """Return failure when a text source is absent."""
        result = u.Cli.files_read_text(tmp_path / "missing.txt")
        tm.fail(result)

    def test_files_write_text_invalid_path(self) -> None:
        """Return failure when a text destination parent is absent."""
        result = u.Cli.files_write_text("/nonexistent_dir/x/y/z/file.txt", "x")
        tm.fail(result)

    def test_files_read_write_json(self, tmp_path: Path) -> None:
        """Round-trip a JSON document through the public CLI facade."""
        path = tmp_path / "data.json"
        write_result = cli.json_write_file(path, {"key": "value"})
        tm.ok(write_result)
        read_result = cli.json_read_file(path)
        tm.ok(read_result)

    def test_files_read_json_missing(self, tmp_path: Path) -> None:
        """Return failure when a JSON source is absent."""
        result = cli.json_read_file(tmp_path / "missing.json")
        tm.fail(result)

    def test_files_read_json_model(self, tmp_path: Path) -> None:
        """Validate one complete JSON document into the requested model."""
        path = tmp_path / "opts.json"
        path.write_text('{"indent": 4, "sort_keys": true}', encoding="utf-8")
        result = cli.json_read_model(path, m.Cli.JsonWriteOptions)
        tm.ok(result)
        tm.that(result.value.indent, eq=4)

    def test_files_read_json_lines_models(self, tmp_path: Path) -> None:
        """Stream the first and all JSON-lines records into models."""
        path = tmp_path / "opts.jsonl"
        path.write_text(
            '\n{"indent": 2, "sort_keys": false}\n{"indent": 4, "sort_keys": true}\n',
            encoding="utf-8",
        )
        first = u.Cli.json_read_first_files_model(path, m.Cli.JsonWriteOptions)
        all_records = u.Cli.json_read_files_lines_model(path, m.Cli.JsonWriteOptions)
        tm.ok(first)
        tm.ok(all_records)
        tm.that(first.value.indent, eq=2)
        tm.that(tuple(item.indent for item in all_records.value), eq=(2, 4))

    def test_files_read_write_yaml(self, tmp_path: Path) -> None:
        """Round-trip a YAML document through the public CLI facade."""
        path = tmp_path / "data.yaml"
        write_result = cli.yaml_write_file(path, {"key": "val"})
        tm.ok(write_result)
        read_result = cli.yaml_read_file(path)
        tm.ok(read_result)

    def test_files_read_yaml_missing(self, tmp_path: Path) -> None:
        """Return failure when a YAML source is absent."""
        result = cli.yaml_read_file(tmp_path / "missing.yaml")
        tm.fail(result)

    def test_files_read_yaml_empty_path(self) -> None:
        """Reject an empty YAML path."""
        result = cli.yaml_read_file("   ")
        tm.fail(result)

    def test_files_write_read_csv(self, tmp_path: Path) -> None:
        """Round-trip CSV rows with validated headers."""
        path = tmp_path / "data.csv"
        rows: list[t.StrSequence] = [["name", "age"], ["alice", "30"], ["bob", "25"]]
        write_result = cli.csv_write_file(path, rows)
        tm.ok(write_result)
        read_result = cli.csv_read_file_with_headers(path)
        tm.ok(read_result)
        tm.that(len(read_result.value), eq=2)

    def test_files_read_csv_missing(self, tmp_path: Path) -> None:
        """Return failure when a CSV source is absent."""
        result = cli.csv_read_file_with_headers(tmp_path / "missing.csv")
        tm.fail(result)

    def test_files_write_read_binary(self, tmp_path: Path) -> None:
        """Round-trip bytes through the public binary file utilities."""
        path = tmp_path / "data.bin"
        write_result = cli.write_binary_file(path, b"\x00\x01\x02")
        tm.ok(write_result)
        read_result = cli.read_binary_file(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq=b"\x00\x01\x02")

    def test_files_read_binary_missing(self, tmp_path: Path) -> None:
        """Return failure when a binary source is absent."""
        result = cli.read_binary_file(tmp_path / "missing.bin")
        tm.fail(result)

    def test_files_copy(self, tmp_path: Path) -> None:
        """Copy one file while preserving its content."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("content", encoding="utf-8")
        result = cli.copy_file(src, dst)
        tm.ok(result)
        tm.that(dst.read_text(encoding="utf-8"), eq="content")

    def test_files_delete(self, tmp_path: Path) -> None:
        """Delete one existing file through the public utility."""
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
        """Create a nested directory idempotently."""
        target = tmp_path / "new" / "subdir"
        result = u.Cli.ensure_dir(target)
        tm.ok(result)
        tm.that(target.exists(), eq=True)

    def test_ensure_symlink(self, tmp_path: Path) -> None:
        """Create one symlink to an existing source directory."""
        source = tmp_path / "real_dir"
        source.mkdir()
        link = tmp_path / "link_dir"
        result = u.Cli.ensure_symlink(link, source)
        tm.ok(result)

    def test_ensure_symlink_idempotent(self, tmp_path: Path) -> None:
        """Keep an already-correct symlink unchanged."""
        source = tmp_path / "real_dir"
        source.mkdir()
        link = tmp_path / "link_dir"
        u.Cli.ensure_symlink(link, source)
        result = u.Cli.ensure_symlink(link, source)
        tm.ok(result)


__all__: list[str] = ["TestsFlextCliFilesCov"]

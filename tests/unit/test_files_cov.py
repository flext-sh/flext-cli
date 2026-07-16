"""Behavioral tests for filesystem helpers exposed via ``cli`` and ``u.Cli``.

Exercises the public file-IO contract (format detection, text/json/yaml/csv/
binary round-trips, atomic writes, hashing, directory and symlink management)
through the published ``cli`` service functions and ``u.Cli`` utility surface.
Every assertion checks observable behavior: returned values, the ``r[T]``
success/failure outcome, and on-disk state read back through the public API.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from flext_cli import c as cli_c, cli
from tests import c
from tests import m
from tests import u

from pathlib import Path

from tests import p, t



class TestsFlextCliFilesCov:
    """Public file-IO contract of ``cli`` file helpers and ``u.Cli``."""

    @pytest.mark.parametrize(
        ("filename", "expected_format"), c.Tests.FILES_DETECT_FORMAT_CASES
    )
    def test_detect_file_format_returns_known_format(
        self, filename: str, expected_format: cli_c.OutputFormats
    ) -> None:
        result = cli.detect_file_format(filename)
        tm.ok(result)
        tm.that(result.value, eq=expected_format)

    @pytest.mark.parametrize("filename", c.Tests.FILES_DETECT_FORMAT_FAIL_CASES)
    def test_detect_file_format_fails_for_unknown_extension(
        self, filename: str
    ) -> None:
        result = cli.detect_file_format(filename)
        tm.fail(result)

    def test_write_then_read_text_round_trips_content(self, tmp_path: Path) -> None:
        path = tmp_path / "test.txt"
        tm.ok(u.Cli.files_write_text(path, "hello world"))
        read_result = u.Cli.files_read_text(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq="hello world")

    def test_read_text_fails_for_missing_file(self, tmp_path: Path) -> None:
        tm.fail(u.Cli.files_read_text(tmp_path / "missing.txt"))

    def test_write_text_fails_for_unwritable_path(self) -> None:
        tm.fail(u.Cli.files_write_text("/nonexistent_dir/x/y/z/file.txt", "x"))

    def test_write_then_read_json_round_trips(self, tmp_path: Path) -> None:
        path = tmp_path / "data.json"
        tm.ok(cli.write_json_file(path, {"key": "value"}))
        read_result = cli.read_json_file(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq={"key": "value"})

    def test_read_json_fails_for_missing_file(self, tmp_path: Path) -> None:
        tm.fail(cli.read_json_file(tmp_path / "missing.json"))

    def test_read_json_model_parses_into_typed_model(self, tmp_path: Path) -> None:
        path = tmp_path / "opts.json"
        path.write_text('{"indent": 4, "sort_keys": true}', encoding="utf-8")
        result = cli.read_json_model(path, m.Cli.JsonWriteOptions)
        tm.ok(result)
        tm.that(result.value.indent, eq=4)
        tm.that(result.value.sort_keys, eq=True)

    def test_write_then_read_yaml_round_trips(self, tmp_path: Path) -> None:
        path = tmp_path / "data.yaml"
        tm.ok(cli.write_yaml_file(path, {"key": "val"}))
        read_result = cli.read_yaml_file(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq={"key": "val"})

    def test_read_yaml_fails_for_missing_file(self, tmp_path: Path) -> None:
        tm.fail(cli.read_yaml_file(tmp_path / "missing.yaml"))

    def test_read_yaml_fails_for_blank_path(self) -> None:
        tm.fail(cli.read_yaml_file("   "))

    def test_write_then_read_csv_preserves_data_rows(self, tmp_path: Path) -> None:
        path = tmp_path / "data.csv"
        rows: list[t.StrSequence] = [["name", "age"], ["alice", "30"], ["bob", "25"]]
        tm.ok(cli.write_csv_file(path, rows))
        read_result = cli.read_csv_file_with_headers(path)
        tm.ok(read_result)
        tm.that(len(read_result.value), eq=2)

    def test_read_csv_fails_for_missing_file(self, tmp_path: Path) -> None:
        tm.fail(cli.read_csv_file_with_headers(tmp_path / "missing.csv"))

    def test_write_then_read_binary_round_trips_bytes(self, tmp_path: Path) -> None:
        path = tmp_path / "data.bin"
        tm.ok(cli.write_binary_file(path, b"\x00\x01\x02"))
        read_result = cli.read_binary_file(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq=b"\x00\x01\x02")

    def test_read_binary_fails_for_missing_file(self, tmp_path: Path) -> None:
        tm.fail(cli.read_binary_file(tmp_path / "missing.bin"))

    def test_copy_file_duplicates_content_to_destination(self, tmp_path: Path) -> None:
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("content", encoding="utf-8")
        tm.ok(cli.copy_file(src, dst))
        tm.that(dst.read_text(encoding="utf-8"), eq="content")

    def test_delete_removes_existing_file(self, tmp_path: Path) -> None:
        path = tmp_path / "to_delete.txt"
        path.write_text("bye", encoding="utf-8")
        tm.ok(u.Cli.files_delete(path))
        tm.that(path.exists(), eq=False)

    def test_delete_is_idempotent_for_missing_file(self, tmp_path: Path) -> None:
        tm.ok(u.Cli.files_delete(tmp_path / "missing.txt"))

    def test_ensure_dir_creates_nested_directories(self, tmp_path: Path) -> None:
        target = tmp_path / "new" / "subdir"
        tm.ok(u.Cli.ensure_dir(target))
        tm.that(target.is_dir(), eq=True)

    def test_ensure_symlink_creates_link_to_source(self, tmp_path: Path) -> None:
        source = tmp_path / "real_dir"
        source.mkdir()
        link = tmp_path / "link_dir"
        tm.ok(u.Cli.ensure_symlink(link, source))
        tm.that(link.is_symlink(), eq=True)

    def test_ensure_symlink_is_idempotent(self, tmp_path: Path) -> None:
        source = tmp_path / "real_dir"
        source.mkdir()
        link = tmp_path / "link_dir"
        tm.ok(u.Cli.ensure_symlink(link, source))
        tm.ok(u.Cli.ensure_symlink(link, source))

    def test_ensure_symlink_replaces_existing_directory(self, tmp_path: Path) -> None:
        source = tmp_path / "source_dir"
        source.mkdir()
        target = tmp_path / "target_dir"
        target.mkdir()
        (target / "old.txt").write_text("old", encoding="utf-8")
        tm.ok(u.Cli.ensure_symlink(target, source))
        tm.that(target.is_symlink(), eq=True)

    def test_ensure_symlink_replaces_existing_file(self, tmp_path: Path) -> None:
        source = tmp_path / "source_dir"
        source.mkdir()
        target = tmp_path / "target_file"
        target.write_text("old", encoding="utf-8")
        tm.ok(u.Cli.ensure_symlink(target, source))
        tm.that(target.is_symlink(), eq=True)

    def test_atomic_write_text_persists_content(self, tmp_path: Path) -> None:
        path = tmp_path / "atomic.txt"
        tm.ok(u.Cli.atomic_write_text_file(path, "hello atomic"))
        tm.that(path.read_text(encoding="utf-8"), eq="hello atomic")

    def test_atomic_write_text_fails_for_unwritable_dir(self) -> None:
        tm.fail(
            u.Cli.atomic_write_text_file("/nonexistent_root_dir/x/y/z/file.txt", "x")
        )

    def test_service_atomic_write_text_persists_content(self, tmp_path: Path) -> None:
        target = tmp_path / "service_atomic.txt"
        tm.ok(cli.atomic_write_text_file(target, "ok"))
        tm.that(target.read_text(encoding="utf-8"), eq="ok")

    def test_sha256_content_returns_hex_digest(self) -> None:
        tm.that(len(u.Cli.sha256_content("hello")), eq=64)

    def test_sha256_file_matches_content_digest(self, tmp_path: Path) -> None:
        path = tmp_path / "data.txt"
        path.write_text("hello", encoding="utf-8")
        tm.that(u.Cli.sha256_file(path), eq=u.Cli.sha256_content("hello"))

    @pytest.mark.parametrize(
        ("filename", "payload"), [("data.json", '{"a": 1}'), ("data.yaml", "a: 1\n")]
    )
    def test_load_file_auto_dict_reads_supported_mappings(
        self, tmp_path: Path, filename: str, payload: str
    ) -> None:
        path = tmp_path / filename
        path.write_text(payload, encoding="utf-8")
        result = cli.load_file_auto_dict(path)
        tm.ok(result)
        tm.that(result.value, eq={"a": 1})

    def test_load_file_auto_dict_fails_for_unsupported_extension(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "data.xml"
        path.write_text("<root/>", encoding="utf-8")
        tm.fail(cli.load_file_auto_dict(path))

    def test_load_file_auto_dict_fails_for_non_mapping_payload(
        self, tmp_path: Path
    ) -> None:
        path = tmp_path / "list.json"
        path.write_text("[1,2,3]", encoding="utf-8")
        tm.fail(cli.load_file_auto_dict(path))

    def test_create_and_remove_temporary_directory(self, tmp_path: Path) -> None:
        result = u.Cli.files_create_temporary_directory(
            prefix="flext-cli-test-", parent_path=tmp_path
        )
        tm.ok(result)
        tm.that(result.value.is_dir(), eq=True)
        tm.that(result.value.parent, eq=tmp_path)
        tm.ok(u.Cli.files_remove_directory(result.value))
        tm.that(result.value.exists(), eq=False)

    def test_copy_directory_respects_dirs_exist_ok(self, tmp_path: Path) -> None:
        source = tmp_path / "source"
        source.mkdir()
        (source / "payload.txt").write_text("new", encoding="utf-8")
        destination = tmp_path / "destination"
        destination.mkdir()
        (destination / "existing.txt").write_text("old", encoding="utf-8")

        tm.fail(u.Cli.files_copy_directory(source, destination))
        tm.ok(u.Cli.files_copy_directory(source, destination, dirs_exist_ok=True))
        tm.that((destination / "payload.txt").read_text(encoding="utf-8"), eq="new")
        tm.that((destination / "existing.txt").read_text(encoding="utf-8"), eq="old")

    def test_remove_directory_rejects_regular_file(self, tmp_path: Path) -> None:
        path = tmp_path / "not-a-directory.txt"
        path.write_text("content", encoding="utf-8")
        tm.fail(u.Cli.files_remove_directory(path))
        tm.that(path.exists(), eq=True)


__all__: list[str] = ["TestsFlextCliFilesCov"]

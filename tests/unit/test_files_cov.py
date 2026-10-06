"""Behavioral tests for filesystem helpers exposed via ``cli`` and ``u.Cli``.

Exercises the public file-IO contract (format detection, text/json/yaml/csv/
binary round-trips, atomic writes, hashing, directory and symlink management)
through the published ``cli`` service functions and ``u.Cli`` utility surface.
Every assertion checks observable behavior: returned values, the ``r[T]``
success/failure outcome, and on-disk state read back through the public API.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest
from flext_tests import tm

from flext_cli import cli
from tests import c, m, u

if TYPE_CHECKING:
    from pathlib import Path

    from tests import t


class TestsFlextCliFilesCov:
    """Public file-IO contract of ``cli`` file helpers and ``u.Cli``."""

    @staticmethod
    @pytest.mark.parametrize(
        ("filename", "expected_format"),
        c.Tests.FILES_DETECT_FORMAT_CASES,
    )
    def test_detect_file_format_returns_known_format(
        filename: str,
        expected_format: c.Cli.OutputFormats,
    ) -> None:
        """Verify that detect file format returns known format."""
        result = cli.detect_file_format(filename)
        tm.ok(result)
        tm.that(result.value, eq=expected_format)

    @staticmethod
    @pytest.mark.parametrize("filename", c.Tests.FILES_DETECT_FORMAT_FAIL_CASES)
    def test_detect_file_format_fails_for_unknown_extension(
        filename: str,
    ) -> None:
        """Verify that detect file format fails for unknown extension."""
        result = cli.detect_file_format(filename)
        tm.fail(result)

    @staticmethod
    def test_write_then_read_text_round_trips_content(tmp_path: Path) -> None:
        """Verify that write then read text round trips content."""
        path = tmp_path / "test.txt"
        tm.ok(u.Cli.files_write_text(path, "hello world"))
        read_result = u.Cli.files_read_text(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq="hello world")

    @staticmethod
    def test_read_text_fails_for_missing_file(tmp_path: Path) -> None:
        """Verify that read text fails for missing file."""
        tm.fail(u.Cli.files_read_text(tmp_path / "missing.txt"))

    @staticmethod
    def test_write_text_fails_for_unwritable_path() -> None:
        """Verify that write text fails for unwritable path."""
        tm.fail(u.Cli.files_write_text("/nonexistent_dir/x/y/z/file.txt", "x"))

    @staticmethod
    def test_write_then_read_json_round_trips(tmp_path: Path) -> None:
        """Verify that write then read json round trips."""
        path = tmp_path / "data.json"
        tm.ok(cli.write_json_file(path, {"key": "value"}))
        read_result = cli.read_json_file(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq={"key": "value"})

    @staticmethod
    def test_read_json_fails_for_missing_file(tmp_path: Path) -> None:
        """Verify that read json fails for missing file."""
        tm.fail(cli.read_json_file(tmp_path / "missing.json"))

    @staticmethod
    def test_read_json_model_parses_into_typed_model(tmp_path: Path) -> None:
        """Verify that read json model parses into typed model."""
        path = tmp_path / "opts.json"
        path.write_text('{"indent": 4, "sort_keys": true}', encoding="utf-8")
        result = cli.read_json_model(path, m.Cli.JsonWriteOptions)
        tm.ok(result)
        tm.that(result.value.indent, eq=4)
        tm.that(result.value.sort_keys, eq=True)

    @staticmethod
    def test_write_then_read_yaml_round_trips(tmp_path: Path) -> None:
        """Verify that write then read yaml round trips."""
        path = tmp_path / "data.yaml"
        tm.ok(cli.write_yaml_file(path, {"key": "val"}))
        read_result = cli.read_yaml_file(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq={"key": "val"})

    @staticmethod
    def test_read_yaml_fails_for_missing_file(tmp_path: Path) -> None:
        """Verify that read yaml fails for missing file."""
        tm.fail(cli.read_yaml_file(tmp_path / "missing.yaml"))

    @staticmethod
    def test_read_yaml_fails_for_blank_path() -> None:
        """Verify that read yaml fails for blank path."""
        tm.fail(cli.read_yaml_file("   "))

    @staticmethod
    def test_write_then_read_csv_preserves_data_rows(tmp_path: Path) -> None:
        """Verify that write then read csv preserves data rows."""
        path = tmp_path / "data.csv"
        rows: list[t.StrSequence] = [["name", "age"], ["alice", "30"], ["bob", "25"]]
        tm.ok(cli.write_csv_file(path, rows))
        read_result = cli.read_csv_file_with_headers(path)
        tm.ok(read_result)
        tm.that(len(read_result.value), eq=2)

    @staticmethod
    def test_read_csv_fails_for_missing_file(tmp_path: Path) -> None:
        """Verify that read csv fails for missing file."""
        tm.fail(cli.read_csv_file_with_headers(tmp_path / "missing.csv"))

    @staticmethod
    def test_write_then_read_binary_round_trips_bytes(tmp_path: Path) -> None:
        """Verify that write then read binary round trips bytes."""
        path = tmp_path / "data.bin"
        tm.ok(cli.write_binary_file(path, b"\x00\x01\x02"))
        read_result = cli.read_binary_file(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq=b"\x00\x01\x02")

    @staticmethod
    def test_read_binary_fails_for_missing_file(tmp_path: Path) -> None:
        """Verify that read binary fails for missing file."""
        tm.fail(cli.read_binary_file(tmp_path / "missing.bin"))

    @staticmethod
    def test_copy_file_duplicates_content_to_destination(tmp_path: Path) -> None:
        """Verify that copy file duplicates content to destination."""
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("content", encoding="utf-8")
        tm.ok(cli.copy_file(src, dst))
        tm.that(dst.read_text(encoding="utf-8"), eq="content")

    @staticmethod
    def test_delete_removes_existing_file(tmp_path: Path) -> None:
        """Verify that delete removes existing file."""
        path = tmp_path / "to_delete.txt"
        path.write_text("bye", encoding="utf-8")
        tm.ok(u.Cli.files_delete(path))
        tm.that(path.exists(), eq=False)

    @staticmethod
    def test_delete_is_idempotent_for_missing_file(tmp_path: Path) -> None:
        """Verify that delete is idempotent for missing file."""
        tm.ok(u.Cli.files_delete(tmp_path / "missing.txt"))

    @staticmethod
    def test_ensure_dir_creates_nested_directories(tmp_path: Path) -> None:
        """Verify that ensure dir creates nested directories."""
        target = tmp_path / "new" / "subdir"
        tm.ok(u.Cli.ensure_dir(target))
        tm.that(target.is_dir(), eq=True)

    @staticmethod
    def test_ensure_symlink_creates_link_to_source(tmp_path: Path) -> None:
        """Verify that ensure symlink creates link to source."""
        source = tmp_path / "real_dir"
        source.mkdir()
        link = tmp_path / "link_dir"
        tm.ok(u.Cli.ensure_symlink(link, source))
        tm.that(link.is_symlink(), eq=True)

    @staticmethod
    def test_ensure_symlink_is_idempotent(tmp_path: Path) -> None:
        """Verify that ensure symlink is idempotent."""
        source = tmp_path / "real_dir"
        source.mkdir()
        link = tmp_path / "link_dir"
        tm.ok(u.Cli.ensure_symlink(link, source))
        tm.ok(u.Cli.ensure_symlink(link, source))

    @staticmethod
    def test_ensure_symlink_preserves_existing_directory(tmp_path: Path) -> None:
        """Reject a different directory without deleting its content."""
        source = tmp_path / "source_dir"
        source.mkdir()
        target = tmp_path / "target_dir"
        target.mkdir()
        (target / "old.txt").write_text("old", encoding="utf-8")
        tm.fail(u.Cli.ensure_symlink(target, source))
        tm.that((target / "old.txt").read_text(encoding="utf-8"), eq="old")

    @staticmethod
    def test_ensure_symlink_preserves_existing_file(tmp_path: Path) -> None:
        """Reject a different file without deleting its content."""
        source = tmp_path / "source_dir"
        source.mkdir()
        target = tmp_path / "target_file"
        target.write_text("old", encoding="utf-8")
        tm.fail(u.Cli.ensure_symlink(target, source))
        tm.that(target.read_text(encoding="utf-8"), eq="old")

    @staticmethod
    @pytest.mark.parametrize("inside_git", [True, False], ids=["git", "plain"])
    def test_files_matching_selects_visible_files_by_pattern(
        tmp_path: Path,
        monkeypatch: pytest.MonkeyPatch,
        *,
        inside_git: bool,
    ) -> None:
        """Git-ignored files are never selected; patterns filter the rest."""
        # The redirected make-test TMPDIR can sit inside the superproject
        # worktree; ceiling the discovery at the case root so the plain case
        # exercises the documented outside-a-worktree path.
        monkeypatch.setenv("GIT_CEILING_DIRECTORIES", str(tmp_path.parent))
        if inside_git:
            tm.ok(u.Cli.run_bytes(["git", "init", "--quiet"], cwd=tmp_path))
        for relative in ("pkg/mod.py", "pkg/notes.txt", "build/gen.py", "tests/t.py"):
            tm.ok(u.Cli.ensure_dir((tmp_path / relative).parent))
            tm.ok(u.Cli.files_write_text(tmp_path / relative, ""))
        tm.ok(u.Cli.files_write_text(tmp_path / ".gitignore", "build/\n"))

        result = u.Cli.files_matching(tmp_path, includes=["*.py"], excludes=["tests/*"])

        tm.ok(result)
        visible = ["pkg/mod.py"] if inside_git else ["build/gen.py", "pkg/mod.py"]
        tm.that(
            [path.relative_to(tmp_path.resolve()).as_posix() for path in result.value],
            eq=visible,
        )

    @staticmethod
    def test_files_matching_fails_for_missing_root(tmp_path: Path) -> None:
        """A root that is not a directory fails instead of selecting nothing."""
        tm.fail(u.Cli.files_matching(tmp_path / "missing", includes=["*.py"]))

    @staticmethod
    def test_read_symlink_target_returns_resolved_destination(
        tmp_path: Path,
    ) -> None:
        """Verify authenticated read returns the link's resolved destination."""
        source = tmp_path / "real_dir"
        source.mkdir()
        link = tmp_path / "link_dir"
        tm.ok(u.Cli.ensure_symlink(link, source))
        destination = tm.ok(u.Cli.read_symlink_target(link))
        tm.that(destination, eq=source.resolve().as_posix())

    @staticmethod
    def test_read_symlink_target_fails_for_regular_path(tmp_path: Path) -> None:
        """A regular directory is not a symlink and must fail with a typed error."""
        plain = tmp_path / "plain_dir"
        plain.mkdir()
        tm.fail(u.Cli.read_symlink_target(plain))

    @staticmethod
    def test_remove_symlink_target_removes_link_and_keeps_source(
        tmp_path: Path,
    ) -> None:
        """Removing a symlink deletes only the link, never the real target."""
        source = tmp_path / "real_dir"
        source.mkdir()
        link = tmp_path / "link_dir"
        tm.ok(u.Cli.ensure_symlink(link, source))
        tm.ok(u.Cli.remove_symlink_target(link))
        tm.that(link.is_symlink(), eq=False)
        tm.that(source.is_dir(), eq=True)

    @staticmethod
    def test_remove_symlink_target_is_noop_for_absent_path(
        tmp_path: Path,
    ) -> None:
        """Removing an absent target succeeds so callers need no pre-check race."""
        tm.ok(u.Cli.remove_symlink_target(tmp_path / "absent"))

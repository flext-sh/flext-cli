"""Behavioral tests for filesystem helpers exposed via ``cli`` and ``u.Cli``.

Exercises the public file-IO contract (text/json round-trips, typed JSON model
reads, file copy/delete, directory creation, and Git-aware file matching)
through the published ``cli`` service functions and ``u.Cli`` utility surface.
Every assertion checks observable behavior: returned values, the ``r[T]``
success/failure outcome, and on-disk state read back through the public API.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_cli import cli
from tests import m, tm, u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFlextCliFilesCov:
    """Public file-IO contract of ``cli`` file helpers and ``u.Cli``."""

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
        tm.ok(result.value.sort_keys)

    @staticmethod
    @pytest.mark.parametrize(
        ("content", "valid"),
        [
            ('{"host": "localhost", "port": 5432}', True),
            ('{"host": "localhost", "port": "5432"}', False),
            ('{"host": "localhost", "port": true}', False),
            ('{"host": "localhost"}', False),
            ('{"host":', False),
        ],
    )
    def test_read_json_model_respects_declared_strictness(
        tmp_path: Path, content: str, *, valid: bool
    ) -> None:
        """The file transport must not relax the consumer model's contract."""
        path = tmp_path / "service.json"
        path.write_text(content, encoding="utf-8")
        result = cli.read_json_model(path, m.Tests.YamlService)
        tm.that(result.success, eq=valid)
        if valid:
            tm.that(result.value, eq=m.Tests.YamlService.model_validate_json(content))
        else:
            tm.that(result.exception, is_=m.ValidationError)
            with pytest.raises(m.ValidationError) as raised:
                _ = result.value
            tm.ok(raised.value is result.exception)

    @staticmethod
    def test_read_json_model_retains_missing_file_cause(tmp_path: Path) -> None:
        """A typed JSON read retains the native filesystem failure and cause."""
        path = tmp_path / "missing.json"
        result = cli.read_json_model(path, m.Tests.YamlService)
        tm.fail(result)
        exception = result.exception
        tm.that(exception, is_=FileNotFoundError)
        if isinstance(exception, FileNotFoundError):
            tm.that(exception.filename, eq=str(path))
        with pytest.raises(FileNotFoundError) as raised:
            _ = result.value
        tm.ok(raised.value is exception)

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
        tm.fail(path.exists())

    @staticmethod
    def test_delete_is_idempotent_for_missing_file(tmp_path: Path) -> None:
        """Verify that delete is idempotent for missing file."""
        tm.ok(u.Cli.files_delete(tmp_path / "missing.txt"))

    @staticmethod
    def test_ensure_dir_creates_nested_directories(tmp_path: Path) -> None:
        """Verify that ensure dir creates nested directories."""
        target = tmp_path / "new" / "subdir"
        tm.ok(u.Cli.ensure_dir(target))
        tm.ok(target.is_dir())

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

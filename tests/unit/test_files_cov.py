"""Coverage tests for _utilities/files.py — 100% via public interfaces."""

from __future__ import annotations

from pathlib import Path

import pytest
from flext_tests import tm

import flext_cli._utilities.files as files_module
import flext_cli.services.file_tools as file_tools_module
from flext_cli import FlextCliFileTools, m
from tests import c, t, u


class TestsFlextCliFilesCov:
    """100% coverage for _utilities/files.py via FlextCliFileTools and u.Cli."""

    # ── detect format ────────────────────────────────────────────────
    @pytest.mark.parametrize(
        ("filename", "expected_format"),
        c.Tests.FILES_DETECT_FORMAT_CASES,
    )
    def test_files_detect_format_known(
        self, filename: str, expected_format: str
    ) -> None:
        result = FlextCliFileTools.detect_file_format(filename)
        tm.ok(result)
        tm.that(result.value, eq=expected_format)

    @pytest.mark.parametrize("filename", c.Tests.FILES_DETECT_FORMAT_FAIL_CASES)
    def test_files_detect_format_unknown(self, filename: str) -> None:
        result = FlextCliFileTools.detect_file_format(filename)
        tm.fail(result)

    # ── text read/write ──────────────────────────────────────────────
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

    # ── json read/write ──────────────────────────────────────────────
    def test_files_read_write_json(self, tmp_path: Path) -> None:
        path = tmp_path / "data.json"
        write_result = FlextCliFileTools.write_json_file(path, {"key": "value"})
        tm.ok(write_result)
        read_result = FlextCliFileTools.read_json_file(path)
        tm.ok(read_result)

    def test_files_read_json_missing(self, tmp_path: Path) -> None:
        result = FlextCliFileTools.read_json_file(tmp_path / "missing.json")
        tm.fail(result)

    def test_files_read_json_model(self, tmp_path: Path) -> None:
        path = tmp_path / "opts.json"
        path.write_text('{"indent": 4, "sort_keys": true}', encoding="utf-8")
        result = FlextCliFileTools.read_json_model(path, m.Cli.JsonWriteOptions)
        tm.ok(result)
        tm.that(result.value.indent, eq=4)

    # ── yaml read/write ──────────────────────────────────────────────
    def test_files_read_write_yaml(self, tmp_path: Path) -> None:
        path = tmp_path / "data.yaml"
        write_result = FlextCliFileTools.write_yaml_file(path, {"key": "val"})
        tm.ok(write_result)
        read_result = FlextCliFileTools.read_yaml_file(path)
        tm.ok(read_result)

    def test_files_read_yaml_missing(self, tmp_path: Path) -> None:
        result = FlextCliFileTools.read_yaml_file(tmp_path / "missing.yaml")
        tm.fail(result)

    def test_files_read_yaml_empty_path(self) -> None:
        result = FlextCliFileTools.read_yaml_file("   ")
        tm.fail(result)

    # ── csv read/write ───────────────────────────────────────────────
    def test_files_write_read_csv(self, tmp_path: Path) -> None:
        path = tmp_path / "data.csv"
        rows: list[t.StrSequence] = [["name", "age"], ["alice", "30"], ["bob", "25"]]
        write_result = FlextCliFileTools.write_csv_file(path, rows)
        tm.ok(write_result)
        read_result = FlextCliFileTools.read_csv_file_with_headers(path)
        tm.ok(read_result)
        tm.that(len(read_result.value), eq=2)

    def test_files_read_csv_missing(self, tmp_path: Path) -> None:
        result = FlextCliFileTools.read_csv_file_with_headers(tmp_path / "missing.csv")
        tm.fail(result)

    # ── binary read/write ────────────────────────────────────────────
    def test_files_write_read_binary(self, tmp_path: Path) -> None:
        path = tmp_path / "data.bin"
        write_result = FlextCliFileTools.write_binary_file(path, b"\x00\x01\x02")
        tm.ok(write_result)
        read_result = FlextCliFileTools.read_binary_file(path)
        tm.ok(read_result)
        tm.that(read_result.value, eq=b"\x00\x01\x02")

    def test_files_read_binary_missing(self, tmp_path: Path) -> None:
        result = FlextCliFileTools.read_binary_file(tmp_path / "missing.bin")
        tm.fail(result)

    # ── copy / delete ────────────────────────────────────────────────
    def test_files_copy(self, tmp_path: Path) -> None:
        src = tmp_path / "src.txt"
        dst = tmp_path / "dst.txt"
        src.write_text("content", encoding="utf-8")
        result = FlextCliFileTools.copy_file(src, dst)
        tm.ok(result)
        tm.that(dst.read_text(encoding="utf-8"), eq="content")

    def test_files_delete(self, tmp_path: Path) -> None:
        path = tmp_path / "to_delete.txt"
        path.write_text("bye", encoding="utf-8")
        result = u.Cli.files_delete(path)
        tm.ok(result)
        tm.that(path.exists(), eq=False)

    def test_files_delete_missing(self, tmp_path: Path) -> None:
        result = u.Cli.files_delete(tmp_path / "missing.txt")
        tm.fail(result)

    # ── ensure_dir / symlink / atomic write ─────────────────────────
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

    def test_ensure_symlink_replaces_existing_directory(self, tmp_path: Path) -> None:
        source = tmp_path / "source_dir"
        source.mkdir()
        target = tmp_path / "target_dir"
        target.mkdir()
        (target / "old.txt").write_text("old", encoding="utf-8")
        result = u.Cli.ensure_symlink(target, source)
        tm.ok(result)
        tm.that(target.is_symlink(), eq=True)

    def test_ensure_symlink_replaces_existing_file(self, tmp_path: Path) -> None:
        source = tmp_path / "source_dir"
        source.mkdir()
        target = tmp_path / "target_file"
        target.write_text("old", encoding="utf-8")
        result = u.Cli.ensure_symlink(target, source)
        tm.ok(result)
        tm.that(target.is_symlink(), eq=True)

    def test_ensure_symlink_parent_creation_failure(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            files_module.FlextCliUtilitiesFiles,
            "ensure_dir",
            lambda *_args, **_kwargs: files_module.r[Path].fail("parent failed"),
        )
        result = u.Cli.ensure_symlink("/tmp/target", "/tmp/source")
        tm.fail(result, has="parent failed")

    def test_ensure_symlink_oserror_branch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        source = tmp_path / "source_dir"
        source.mkdir()
        target = tmp_path / "target_link"
        symlink_error = "symlink boom"

        def raise_symlink(
            self: Path, target: Path, target_is_directory: bool = True
        ) -> None:
            raise OSError(symlink_error)

        monkeypatch.setattr(files_module.Path, "symlink_to", raise_symlink)
        result = u.Cli.ensure_symlink(target, source)
        tm.fail(result, has=symlink_error)

    def test_atomic_write_text_file(self, tmp_path: Path) -> None:
        path = tmp_path / "atomic.txt"
        result = u.Cli.atomic_write_text_file(path, "hello atomic")
        tm.ok(result)
        tm.that(path.read_text(encoding="utf-8"), eq="hello atomic")

    def test_atomic_write_text_file_invalid_dir(self) -> None:
        result = u.Cli.atomic_write_text_file(
            "/nonexistent_root_dir/x/y/z/file.txt", "x"
        )
        tm.fail(result)

    def test_atomic_write_text_file_inner_cleanup_on_replace_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        target = tmp_path / "atomic_runtime_error.txt"
        replace_error = "replace boom"

        def raise_replace(self: Path, target_path: Path) -> Path:
            raise RuntimeError(replace_error)

        monkeypatch.setattr(files_module.Path, "replace", raise_replace)
        with pytest.raises(RuntimeError, match=replace_error):
            _ = u.Cli.atomic_write_text_file(target, "x")

    def test_atomic_write_text_file_oserror_branch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        target = tmp_path / "atomic_oserror.txt"
        mkstemp_error = "mkstemp boom"

        def raise_mkstemp(*_args: object, **_kwargs: object) -> tuple[int, str]:
            raise OSError(mkstemp_error)

        monkeypatch.setattr(files_module.tempfile, "mkstemp", raise_mkstemp)
        result = u.Cli.atomic_write_text_file(target, "x")
        tm.fail(result, has=mkstemp_error)

    def test_service_atomic_write_text_file_success(self, tmp_path: Path) -> None:
        target = tmp_path / "service_atomic.txt"
        result = FlextCliFileTools.atomic_write_text_file(target, "ok")
        tm.ok(result)
        tm.that(target.read_text(encoding="utf-8"), eq="ok")

    def test_service_atomic_write_text_file_failure_preserves_error(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            file_tools_module.u.Cli,
            "atomic_write_text_file",
            lambda *_args, **_kwargs: file_tools_module.r[bool].fail("io failure"),
        )
        result = FlextCliFileTools.atomic_write_text_file("any.txt", "body")
        tm.fail(result, has="io failure")

    def test_service_atomic_write_text_file_failure_uses_fallback_message(
        self,
        monkeypatch: pytest.MonkeyPatch,
    ) -> None:
        monkeypatch.setattr(
            file_tools_module.u.Cli,
            "atomic_write_text_file",
            lambda *_args, **_kwargs: file_tools_module.r[bool].fail(""),
        )
        result = FlextCliFileTools.atomic_write_text_file("any.txt", "body")
        tm.fail(result, has="Text write failed")

    # ── sha256 ───────────────────────────────────────────────────────
    def test_sha256_content(self) -> None:
        digest = u.Cli.sha256_content("hello")
        tm.that(len(digest), eq=64)

    def test_sha256_file(self, tmp_path: Path) -> None:
        path = tmp_path / "data.txt"
        path.write_text("hello", encoding="utf-8")
        digest = u.Cli.sha256_file(path)
        expected = u.Cli.sha256_content("hello")
        tm.that(digest, eq=expected)

    # ── auto load mapping ────────────────────────────────────────────
    def test_files_load_auto_mapping_json(self, tmp_path: Path) -> None:
        path = tmp_path / "data.json"
        path.write_text('{"a": 1}', encoding="utf-8")
        result = FlextCliFileTools.load_file_auto_dict(path)
        tm.ok(result)

    def test_files_load_auto_mapping_yaml(self, tmp_path: Path) -> None:
        path = tmp_path / "data.yaml"
        path.write_text("a: 1\n", encoding="utf-8")
        result = FlextCliFileTools.load_file_auto_dict(path)
        tm.ok(result)

    def test_files_load_auto_mapping_unsupported(self, tmp_path: Path) -> None:
        path = tmp_path / "data.xml"
        path.write_text("<root/>", encoding="utf-8")
        result = FlextCliFileTools.load_file_auto_dict(path)
        tm.fail(result)

    def test_files_load_auto_mapping_non_mapping_json(self, tmp_path: Path) -> None:
        path = tmp_path / "list.json"
        path.write_text("[1,2,3]", encoding="utf-8")
        result = FlextCliFileTools.load_file_auto_dict(path)
        tm.fail(result)

    def test_files_load_auto_mapping_non_mapping_payload_branch(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        path = tmp_path / "payload.json"
        path.write_text("{}", encoding="utf-8")
        monkeypatch.setattr(
            files_module.uj,
            "json_read",
            lambda *_args, **_kwargs: files_module.r[t.JsonValue].ok([1, 2, 3]),
        )
        result = FlextCliFileTools.load_file_auto_dict(path)
        tm.fail(result, has="mapping")

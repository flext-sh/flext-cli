"""Coverage tests for _utilities/files.py — 100% via public interfaces."""

from __future__ import annotations


from flext_tests import tm
from tests import u

from flext_cli import cli

from pathlib import Path


class TestsFlextCliFilesCov:
    """Implementation part for TestsFlextCliFilesCov."""

    def test_ensure_symlink_replaces_existing_directory(self, tmp_path: Path) -> None:
        """Verify that ensure symlink replaces existing directory."""
        source = tmp_path / "source_dir"
        source.mkdir()
        target = tmp_path / "target_dir"
        target.mkdir()
        (target / "old.txt").write_text("old", encoding="utf-8")
        result = u.Cli.ensure_symlink(target, source)
        tm.ok(result)
        tm.that(target.is_symlink(), eq=True)

    def test_ensure_symlink_replaces_existing_file(self, tmp_path: Path) -> None:
        """Verify that ensure symlink replaces existing file."""
        source = tmp_path / "source_dir"
        source.mkdir()
        target = tmp_path / "target_file"
        target.write_text("old", encoding="utf-8")
        result = u.Cli.ensure_symlink(target, source)
        tm.ok(result)
        tm.that(target.is_symlink(), eq=True)

    def test_atomic_write_text_file(self, tmp_path: Path) -> None:
        """Verify that atomic write text file."""
        path = tmp_path / "atomic.txt"
        result = u.Cli.atomic_write_text_file(path, "hello atomic")
        tm.ok(result)
        tm.that(path.read_text(encoding="utf-8"), eq="hello atomic")

    def test_atomic_write_text_file_invalid_dir(self) -> None:
        """Verify that atomic write text file invalid dir."""
        result = u.Cli.atomic_write_text_file(
            "/nonexistent_root_dir/x/y/z/file.txt", "x"
        )
        tm.fail(result)

    def test_service_atomic_write_text_file_success(self, tmp_path: Path) -> None:
        """Verify that service atomic write text file success."""
        target = tmp_path / "service_atomic.txt"
        result = cli.atomic_write_text_file(target, "ok")
        tm.ok(result)
        tm.that(target.read_text(encoding="utf-8"), eq="ok")

    def test_sha256_content(self) -> None:
        """Verify that sha256 content."""
        digest = u.Cli.sha256_content("hello")
        tm.that(len(digest), eq=64)

    def test_sha256_file(self, tmp_path: Path) -> None:
        """Verify that sha256 file."""
        path = tmp_path / "data.txt"
        path.write_text("hello", encoding="utf-8")
        digest = u.Cli.sha256_file(path)
        expected = u.Cli.sha256_content("hello")
        tm.that(digest, eq=expected)

    def test_files_load_auto_mapping_json(self, tmp_path: Path) -> None:
        """Verify that files load auto mapping json."""
        path = tmp_path / "data.json"
        path.write_text('{"a": 1}', encoding="utf-8")
        result = cli.load_file_auto_dict(path)
        tm.ok(result)

    def test_files_load_auto_mapping_yaml(self, tmp_path: Path) -> None:
        """Verify that files load auto mapping yaml."""
        path = tmp_path / "data.yaml"
        path.write_text("a: 1\n", encoding="utf-8")
        result = cli.load_file_auto_dict(path)
        tm.ok(result)

    def test_files_load_auto_mapping_unsupported(self, tmp_path: Path) -> None:
        """Verify that files load auto mapping unsupported."""
        path = tmp_path / "data.xml"
        path.write_text("<root/>", encoding="utf-8")
        result = cli.load_file_auto_dict(path)
        tm.fail(result)

    def test_files_load_auto_mapping_non_mapping_json(self, tmp_path: Path) -> None:
        """Verify that files load auto mapping non mapping json."""
        path = tmp_path / "list.json"
        path.write_text("[1,2,3]", encoding="utf-8")
        result = cli.load_file_auto_dict(path)
        tm.fail(result)

    def test_files_create_temporary_directory(self, tmp_path: Path) -> None:
        """Verify that files create temporary directory."""
        result = u.Cli.files_create_temporary_directory(
            prefix="flext-cli-test-", parent_path=tmp_path
        )
        tm.ok(result)
        tm.that(result.value.is_dir(), eq=True)
        tm.that(result.value.parent, eq=tmp_path)
        cleanup_result = u.Cli.files_remove_directory(result.value)
        tm.ok(cleanup_result)
        tm.that(result.value.exists(), eq=False)

    def test_files_copy_directory_respects_dirs_exist_ok(self, tmp_path: Path) -> None:
        """Verify that files copy directory respects dirs exist ok."""
        source = tmp_path / "source"
        source.mkdir()
        (source / "payload.txt").write_text("new", encoding="utf-8")
        destination = tmp_path / "destination"
        destination.mkdir()
        (destination / "existing.txt").write_text("old", encoding="utf-8")

        blocked_result = u.Cli.files_copy_directory(source, destination)
        tm.fail(blocked_result)
        copied_result = u.Cli.files_copy_directory(
            source, destination, dirs_exist_ok=True
        )
        tm.ok(copied_result)
        tm.that((destination / "payload.txt").read_text(encoding="utf-8"), eq="new")
        tm.that((destination / "existing.txt").read_text(encoding="utf-8"), eq="old")

    def test_files_remove_directory_rejects_file(self, tmp_path: Path) -> None:
        """Verify that files remove directory rejects file."""
        path = tmp_path / "not-a-directory.txt"
        path.write_text("content", encoding="utf-8")
        result = u.Cli.files_remove_directory(path)
        tm.fail(result)
        tm.that(path.exists(), eq=True)


__all__: list[str] = ["TestsFlextCliFilesCov"]

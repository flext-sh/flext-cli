"""Public hashing, auto-loading, and directory lifecycle contracts."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from flext_cli import cli
from flext_tests import tm
from tests import u

if TYPE_CHECKING:
    from pathlib import Path


class TestsFileDerivedContracts:
    """Observable behavior derived from the canonical public file surface."""

    def test_sha256_content_returns_hex_digest(self) -> None:
        """Return one SHA-256 hexadecimal digest for text content."""
        tm.that(len(u.Cli.sha256_content("hello")), eq=64)

    def test_sha256_file_matches_content_digest(self, tmp_path: Path) -> None:
        """Keep file and content SHA-256 operations equivalent."""
        path = tmp_path / "data.txt"
        path.write_text("hello", encoding="utf-8")

        tm.that(u.Cli.sha256_file(path), eq=u.Cli.sha256_content("hello"))

    @pytest.mark.parametrize(
        ("filename", "payload"), [("data.json", '{"a": 1}'), ("data.yaml", "a: 1\n")]
    )
    def test_load_file_auto_dict_reads_supported_mappings(
        self, tmp_path: Path, filename: str, payload: str
    ) -> None:
        """Load supported serialized mappings through the service facade."""
        path = tmp_path / filename
        path.write_text(payload, encoding="utf-8")

        result = cli.load_file_auto_dict(path)

        tm.ok(result)
        tm.that(result.value, eq={"a": 1})

    def test_load_file_auto_dict_rejects_unsupported_extension(
        self, tmp_path: Path
    ) -> None:
        """Reject auto-loading when the serialization owner is unknown."""
        path = tmp_path / "data.xml"
        path.write_text("<root/>", encoding="utf-8")

        tm.fail(cli.load_file_auto_dict(path))

    def test_load_file_auto_dict_rejects_non_mapping_payload(
        self, tmp_path: Path
    ) -> None:
        """Reject a supported document whose root is not a mapping."""
        path = tmp_path / "list.json"
        path.write_text("[1,2,3]", encoding="utf-8")

        tm.fail(cli.load_file_auto_dict(path))

    def test_create_and_remove_temporary_directory(self, tmp_path: Path) -> None:
        """Round-trip a temporary directory through public lifecycle helpers."""
        result = u.Cli.files_create_temporary_directory(
            prefix="flext-cli-test-", parent_path=tmp_path
        )

        tm.ok(result)
        tm.that(result.value.is_dir(), eq=True)
        tm.that(result.value.parent, eq=tmp_path)
        tm.ok(u.Cli.files_remove_directory(result.value))
        tm.that(result.value.exists(), eq=False)

    def test_copy_directory_respects_dirs_exist_ok(self, tmp_path: Path) -> None:
        """Require explicit authorization before merging directory content."""
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
        """Preserve a regular file passed to the directory-removal API."""
        path = tmp_path / "not-a-directory.txt"
        path.write_text("content", encoding="utf-8")

        tm.fail(u.Cli.files_remove_directory(path))
        tm.that(path.exists(), eq=True)

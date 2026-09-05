"""Generic filesystem helpers shared through ``u.Cli``."""

from __future__ import annotations

import csv
import hashlib
import os
import shutil
import stat
from pathlib import Path

from flext_cli import c, m, p, r, t
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_02 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart02,
)
from flext_cli._utilities.atomic_file_publish import publish_guarded_staged_file
from flext_cli._utilities.atomic_file_snapshot import read_authenticated_state


class FlextCliUtilitiesFiles:
    """Implementation part for FlextCliUtilitiesFiles."""

    @staticmethod
    def files_read_csv_with_headers(
        file_path: t.Cli.TextPath,
    ) -> p.Result[t.SequenceOf[t.StrMapping]]:
        """Read one CSV file into mapping rows using header row."""

        def _load() -> t.SequenceOf[t.StrMapping]:
            with Path(file_path).open(
                encoding=c.Cli.ENCODING_DEFAULT, newline=""
            ) as handle:
                return [dict(row) for row in csv.DictReader(handle)]

        return FlextCliUtilitiesFilesPart02.files_execute(
            _load, c.Cli.ERR_CSV_READ_FAILED
        )

    @staticmethod
    def files_read_binary(file_path: t.Cli.TextPath) -> p.Result[bytes]:
        """Read one binary file."""
        return FlextCliUtilitiesFilesPart02.files_execute(
            lambda: Path(file_path).read_bytes(), c.Cli.ERR_BINARY_READ_FAILED
        )

    @staticmethod
    def atomic_read_binary_file_state(
        file_path: t.Cli.TextPath, *, required: bool = False
    ) -> p.Result[m.Cli.AtomicFileState]:
        """Read exact bytes plus leaf and immediate-parent physical identities.

        The immediate parent must already exist as a physical, non-aliased
        directory. Materialize a planned directory chain first, then call this
        method; no future parent identity may be invented for an absent file.
        """
        path = Path(file_path)
        try:
            parent, state, content = read_authenticated_state(path, required=required)
        except OSError as exc:
            return r[m.Cli.AtomicFileState].fail(
                c.Cli.ERR_BINARY_READ_FAILED.format(error=exc)
            )
        return r[m.Cli.AtomicFileState].ok(
            m.Cli.AtomicFileState(
                path=path,
                parent_device=parent.st_dev,
                parent_inode=parent.st_ino,
                content=content,
                mode=None if state is None else stat.S_IMODE(state.st_mode),
                device=None if state is None else state.st_dev,
                inode=None if state is None else state.st_ino,
                link_count=None if state is None else state.st_nlink,
                file_attributes=(
                    None
                    if state is None
                    else getattr(state, "st_file_attributes", None)
                ),
                reparse_tag=(
                    None if state is None else getattr(state, "st_reparse_tag", None)
                ),
            )
        )

    @staticmethod
    def atomic_publish_staged_binary_file_guarded(
        destination_before: m.Cli.AtomicFileState, staged: m.Cli.AtomicFileState
    ) -> p.Result[m.Cli.AtomicFileState]:
        """Consume one authenticated staged file under the caller's lock."""
        try:
            published = publish_guarded_staged_file(destination_before, staged)
        except OSError as exc:
            return r[m.Cli.AtomicFileState].fail(
                c.Cli.ERR_BINARY_WRITE_FAILED.format(error=exc)
            )
        return r[m.Cli.AtomicFileState].ok(
            m.Cli.AtomicFileState(
                path=destination_before.path,
                parent_device=destination_before.parent_device,
                parent_inode=destination_before.parent_inode,
                content=staged.content,
                mode=stat.S_IMODE(published.st_mode),
                device=published.st_dev,
                inode=published.st_ino,
                link_count=published.st_nlink,
                file_attributes=getattr(published, "st_file_attributes", None),
                reparse_tag=getattr(published, "st_reparse_tag", None),
            )
        )

    @staticmethod
    def files_list_directory_names(
        file_path: t.Cli.TextPath,
    ) -> p.Result[t.SequenceOf[str]]:
        """Return sorted child directory names for one path."""
        path = Path(file_path)
        if not path.exists():
            return r[t.SequenceOf[str]].ok(())

        def _list() -> t.SequenceOf[str]:
            names = sorted(entry.name for entry in path.iterdir() if entry.is_dir())
            return tuple(names)

        return FlextCliUtilitiesFilesPart02.files_execute(
            _list, c.Cli.ERR_TEXT_READ_FAILED
        )

    @staticmethod
    def ensure_symlink(
        target: t.Cli.TextPath, source: t.Cli.TextPath
    ) -> p.Result[bool]:
        """Ensure target points to source via directory symlink."""
        target_path = Path(target)
        source_path = Path(source).resolve()
        ensure_result = FlextCliUtilitiesFilesPart02.ensure_dir(target_path.parent)
        if ensure_result.failure:
            return r[bool].fail(
                ensure_result.error
                or c.Cli.ERR_CREATE_PARENT_DIR_FAILED.format(target_path=target_path)
            )
        if target_path.is_symlink() and target_path.resolve() == source_path:
            return r[bool].ok(True)
        if target_path.exists() or target_path.is_symlink():
            return r[bool].fail(
                f"symlink destination already exists with a different identity: {target_path}"
            )
        relative_source = os.path.relpath(source_path, target_path.parent.resolve())
        try:
            target_path.symlink_to(relative_source, target_is_directory=True)
        except OSError as exc:
            return r[bool].fail(
                c.Cli.ERR_ENSURE_SYMLINK_FAILED.format(
                    target_path=target_path, error=exc
                )
            )
        return r[bool].ok(True)

    @staticmethod
    def _remove_symlink_target(target_path: Path) -> None:
        """Remove an existing file, directory, or symlink at ``target_path``."""
        if not target_path.exists() and not target_path.is_symlink():
            return
        if target_path.is_dir() and not target_path.is_symlink():
            shutil.rmtree(target_path)
        else:
            target_path.unlink()

    @staticmethod
    def sha256_content(content: str) -> str:
        """Return the SHA-256 hex digest for text content."""
        return hashlib.sha256(content.encode(c.Cli.ENCODING_DEFAULT)).hexdigest()

    @staticmethod
    def sha256_bytes(content: bytes) -> str:
        """Return the SHA-256 hex digest for exact binary content."""
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def sha256_file(file_path: t.Cli.TextPath) -> str:
        """Return the SHA-256 hex digest for a file on disk."""
        path = Path(file_path)
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()


__all__: list[str] = ["FlextCliUtilitiesFiles"]

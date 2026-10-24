"""Generic filesystem helpers shared through ``u.Cli``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import csv
import errno
import hashlib
import stat
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path

from flext_cli import c, m, p, r, t
from flext_cli._utilities._files.flextcliutilitiesfiles_part_02 import (
    FlextCliUtilitiesFilesPart02,
)
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_path import FlextCliUtilitiesAtomicFilePath
from flext_cli._utilities.atomic_file_publish import FlextCliUtilitiesAtomicFilePublish
from flext_cli._utilities.atomic_file_read import FlextCliUtilitiesAtomicFileRead
from flext_cli._utilities.atomic_file_snapshot import (
    FlextCliUtilitiesAtomicFileSnapshot,
)
from flext_cli._utilities.atomic_file_state import FlextCliUtilitiesAtomicFileState


class FlextCliUtilitiesFilesPart03:
    """Implementation part for FlextCliUtilitiesFilesPart03."""

    @staticmethod
    def atomic_read_binary_file_receipt(
        file_path: t.Cli.TextPath,
        *,
        required: bool = False,
        owner_uid: int | None = None,
        max_bytes: int | None = None,
    ) -> p.Result[m.Cli.AtomicFileReceipt]:
        """Return the authenticated identity and digest without buffering payload."""
        try:
            receipt = FlextCliUtilitiesAtomicFileSnapshot.read_receipt(
                Path(file_path),
                required=required,
                owner_uid=owner_uid,
                max_bytes=max_bytes,
            )
        except OSError as exc:
            return r[m.Cli.AtomicFileReceipt].fail(
                c.Cli.ERR_BINARY_READ_FAILED.format(error=exc), exception=exc
            )
        return r[m.Cli.AtomicFileReceipt].ok(receipt)

    @staticmethod
    @contextmanager
    def atomic_binary_file_reader(
        receipt: m.Cli.AtomicFileReceipt,
    ) -> Generator[p.Cli.AtomicFileReader]:
        """Retain one authenticated descriptor for repeated exact range reads.

        Yields:
            The authenticated scoped reader for the receipt.

        """
        with FlextCliUtilitiesAtomicFileSnapshot.receipt_reader(receipt) as reader:
            yield reader

    @staticmethod
    def atomic_read_binary_file_range(
        receipt: m.Cli.AtomicFileReceipt, offset: int, length: int
    ) -> p.Result[bytes]:
        """Read an exact range through the canonical scoped descriptor owner.

        Returns:
            The resulting ``p.Result[bytes]``.

        """
        try:
            with FlextCliUtilitiesAtomicFileSnapshot.receipt_reader(receipt) as reader:
                content = reader.read_range(offset, length)
        except OSError as exc:
            return r[bytes].fail(
                c.Cli.ERR_BINARY_READ_FAILED.format(error=exc), exception=exc
            )
        return r[bytes].ok(content)

    @staticmethod
    def atomic_publish_staged_binary_file_receipt_guarded(
        destination_before: m.Cli.AtomicFileReceipt,
        staged: m.Cli.AtomicFileReceipt,
    ) -> p.Result[m.Cli.AtomicFileReceipt]:
        """Consume a streamed staged artifact under exact destination ownership.

        Returns:
            The resulting ``p.Result[m.Cli.AtomicFileReceipt]``.

        """
        try:
            published = FlextCliUtilitiesAtomicFilePublish.publish_guarded_staged_file(
                destination_before, staged
            )
        except OSError as exc:
            return r[m.Cli.AtomicFileReceipt].fail(
                c.Cli.ERR_BINARY_WRITE_FAILED.format(error=exc), exception=exc
            )
        return r[m.Cli.AtomicFileReceipt].ok(
            m.Cli.AtomicFileReceipt(
                **staged.model_dump(
                    exclude={"path", "parent_device", "parent_inode", "version_key"}
                ),
                path=destination_before.path,
                parent_device=destination_before.parent_device,
                parent_inode=destination_before.parent_inode,
                version_key=FlextCliUtilitiesAtomicFileRead.state_key(published),
            )
        )

    @staticmethod
    def files_read_csv_with_headers(
        file_path: t.Cli.TextPath,
    ) -> p.Result[t.SequenceOf[t.StrMapping]]:
        """Read one CSV file into mapping rows using header row.

        Returns:
            The resulting ``p.Result[t.SequenceOf[t.StrMapping]]``.

        """

        def _load() -> t.SequenceOf[t.StrMapping]:
            with Path(file_path).open(
                encoding=c.DEFAULT_ENCODING,
                newline="",
            ) as handle:
                return [dict(row) for row in csv.DictReader(handle)]

        return FlextCliUtilitiesFilesPart02.files_execute(
            _load,
            c.Cli.ERR_CSV_READ_FAILED,
        )

    @staticmethod
    def files_read_binary(file_path: t.Cli.TextPath) -> p.Result[bytes]:
        """Read one binary file.

        Returns:
            The resulting ``p.Result[bytes]``.

        """
        return FlextCliUtilitiesFilesPart02.files_execute(
            lambda: Path(file_path).read_bytes(),
            c.Cli.ERR_BINARY_READ_FAILED,
        )

    @staticmethod
    def atomic_read_binary_file_state(
        file_path: t.Cli.TextPath,
        *,
        required: bool = False,
        owner_uid: int | None = None,
        max_bytes: int | None = None,
    ) -> p.Result[m.Cli.AtomicFileState]:
        """Read exact bytes plus leaf and immediate-parent physical identities.

        ``owner_uid`` fails the read when the authenticated parent or the leaf
        belongs to another uid; ``max_bytes`` fails it when the leaf is larger.

        A required read demands one physical, non-aliased parent directory. An
        optional read of a path whose directory chain is not materialized is
        absence: the returned state carries no leaf and no parent identity.
        Publication still requires an authenticated parent, so materialize the
        planned directory chain and read again before publishing into it.

        Returns:
            The resulting ``p.Result[m.Cli.AtomicFileState]``.

        """
        path = Path(file_path)
        try:
            parent, state, content = (
                FlextCliUtilitiesAtomicFileSnapshot.read_authenticated_state(
                    path,
                    required=required,
                    owner_uid=owner_uid,
                    max_bytes=max_bytes,
                )
            )
        except OSError as exc:
            return r[m.Cli.AtomicFileState].fail(
                c.Cli.ERR_BINARY_READ_FAILED.format(error=exc),
                exception=exc,
            )
        return r[m.Cli.AtomicFileState].ok(
            m.Cli.AtomicFileState(
                path=path,
                parent_device=None if parent is None else parent.st_dev,
                parent_inode=None if parent is None else parent.st_ino,
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
            ),
        )

    @staticmethod
    def atomic_iter_binary_file(
        file_path: t.Cli.TextPath,
    ) -> Generator[bytes]:
        """Yield bytes from one authenticated descriptor without buffering the file.

        Physical path and version failures propagate from the descriptor owners.

        Yields:
            Complete byte blocks from the required physical file.

        Raises:
            FileNotFoundError: If the required file is missing.

        """
        path = FlextCliUtilitiesAtomicFilePath.validate_atomic_path(Path(file_path))
        with FlextCliUtilitiesAtomicFileDescriptor.parent_descriptor(path) as parent:
            state = FlextCliUtilitiesAtomicFileState.destination_state(
                path, parent=parent
            )
            if state is None:
                message = f"required atomic file is missing: {path}"
                raise FileNotFoundError(errno.ENOENT, message, path)
            with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
                parent, path, c.Cli.READ_FLAGS
            ) as descriptor:
                yield from FlextCliUtilitiesAtomicFileRead.descriptor_chunks(
                    descriptor, path, state
                )
                FlextCliUtilitiesAtomicFileState.assert_destination_unchanged(
                    path, state, parent=parent
                )
            FlextCliUtilitiesAtomicFileDescriptor.assert_parent_unchanged(parent)

    @staticmethod
    def atomic_publish_staged_binary_file_guarded(
        destination_before: m.Cli.AtomicFileState,
        staged: m.Cli.AtomicFileState,
    ) -> p.Result[m.Cli.AtomicFileState]:
        """Consume one authenticated staged file under the caller's lock.

        Returns:
            The resulting ``p.Result[m.Cli.AtomicFileState]``.

        """
        try:
            published = FlextCliUtilitiesAtomicFilePublish.publish_guarded_staged_file(
                destination_before,
                staged,
            )
        except OSError as exc:
            return r[m.Cli.AtomicFileState].fail(
                c.Cli.ERR_BINARY_WRITE_FAILED.format(error=exc),
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
            ),
        )

    @staticmethod
    def files_list_directory_names(
        file_path: t.Cli.TextPath,
    ) -> p.Result[t.SequenceOf[str]]:
        """Return sorted child directory names for one path.

        Returns:
            Sorted child directory names for one path.

        """
        path = Path(file_path)
        if not path.exists():
            return r[t.SequenceOf[str]].ok(())

        def _list() -> t.SequenceOf[str]:
            names = sorted(entry.name for entry in path.iterdir() if entry.is_dir())
            return tuple(names)

        return FlextCliUtilitiesFilesPart02.files_execute(
            _list,
            c.Cli.ERR_TEXT_READ_FAILED,
        )

    @staticmethod
    def sha256_content(content: str) -> str:
        """Return the SHA-256 hex digest for text content.

        Returns:
            The SHA-256 hex digest for text content.

        """
        return hashlib.sha256(content.encode(c.DEFAULT_ENCODING)).hexdigest()

    @staticmethod
    def sha256_bytes(content: bytes) -> str:
        """Return the SHA-256 hex digest for exact binary content.

        Returns:
            The SHA-256 hex digest for exact binary content.

        """
        return hashlib.sha256(content).hexdigest()

    @staticmethod
    def sha256_file(file_path: t.Cli.TextPath) -> str:
        """Return the SHA-256 hex digest for a file on disk.

        Returns:
            The SHA-256 hex digest for a file on disk.

        """
        path = Path(file_path)
        hasher = hashlib.sha256()
        with path.open("rb") as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b""):
                hasher.update(chunk)
        return hasher.hexdigest()


__all__: list[str] = ["FlextCliUtilitiesFilesPart03"]

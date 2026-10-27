"""Public descriptor-authenticated snapshots composed from atomic file-state owners.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import hashlib
import os
import stat
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import TYPE_CHECKING

from flext_cli import m
from flext_cli._utilities.atomic_file_descriptor import (
    FlextCliUtilitiesAtomicFileDescriptor,
)
from flext_cli._utilities.atomic_file_model import FlextCliUtilitiesAtomicFileModel
from flext_cli._utilities.atomic_file_read import FlextCliUtilitiesAtomicFileRead
from flext_cli._utilities.atomic_file_state import FlextCliUtilitiesAtomicFileState

if TYPE_CHECKING:
    from flext_cli import p


class FlextCliUtilitiesAtomicFileSnapshot:
    """Canonical namespace owner."""

    @staticmethod
    def read_receipt(
        path: Path,
        *,
        required: bool,
        owner_uid: int | None = None,
        max_bytes: int | None = None,
    ) -> m.Cli.AtomicFileReceipt:
        """Measure exact bytes once while retaining descriptor and parent identity.

        Returns:
            The receipt of the authenticated bytes, reduced to parent and path
            identity when the read resolves to exact absence.

        """
        with FlextCliUtilitiesAtomicFileState.authenticated_entry(
            path, required=required, owner_uid=owner_uid, max_bytes=max_bytes
        ) as (parent, state):
            if parent is None or state is None:
                return m.Cli.AtomicFileReceipt(
                    path=path,
                    parent_device=None if parent is None else parent.state.st_dev,
                    parent_inode=None if parent is None else parent.state.st_ino,
                )
            with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
                parent, path, FlextCliUtilitiesAtomicFileRead.READ_FLAGS
            ) as descriptor:
                digest = hashlib.sha256()
                size = 0
                for chunk in FlextCliUtilitiesAtomicFileRead.descriptor_chunks(
                    descriptor, path, state
                ):
                    digest.update(chunk)
                    size += len(chunk)
                return m.Cli.AtomicFileReceipt(
                    path=path,
                    parent_device=parent.state.st_dev,
                    parent_inode=parent.state.st_ino,
                    mode=stat.S_IMODE(state.st_mode),
                    device=state.st_dev,
                    inode=state.st_ino,
                    link_count=state.st_nlink,
                    file_attributes=getattr(state, "st_file_attributes", None),
                    reparse_tag=getattr(state, "st_reparse_tag", None),
                    size=size,
                    sha256=digest.hexdigest(),
                    version_key=FlextCliUtilitiesAtomicFileRead.state_key(state),
                )

    @staticmethod
    @contextmanager
    def receipt_reader(
        receipt: m.Cli.AtomicFileReceipt,
    ) -> Generator[p.Cli.AtomicFileReader]:
        """Authenticate a receipt once and retain one descriptor for all ranges.

        Yields:
            The reader bound to the retained descriptor of the authenticated
            version.

        Raises:
            FileNotFoundError: If the receipt file is absent.

        """
        with FlextCliUtilitiesAtomicFileState.authenticated_entry(
            receipt.path, required=True
        ) as (parent, state):
            if parent is None or state is None:
                raise FileNotFoundError(
                    errno.ENOENT, "missing receipt file", receipt.path
                )
            FlextCliUtilitiesAtomicFileModel.require_parent(receipt, parent.state)
            if (
                receipt.version_key != FlextCliUtilitiesAtomicFileRead.state_key(state)
                or receipt.size != state.st_size
            ):
                FlextCliUtilitiesAtomicFileRead.raise_changed(receipt.path)
            with FlextCliUtilitiesAtomicFileDescriptor.entry_descriptor(
                parent, receipt.path, FlextCliUtilitiesAtomicFileRead.READ_FLAGS
            ) as descriptor:
                digest = hashlib.sha256()
                for chunk in FlextCliUtilitiesAtomicFileRead.descriptor_chunks(
                    descriptor, receipt.path, state
                ):
                    digest.update(chunk)
                if digest.hexdigest() != receipt.sha256:
                    FlextCliUtilitiesAtomicFileRead.raise_changed(receipt.path)
                reader = FlextCliUtilitiesAtomicFileRead.Reader(
                    descriptor, receipt.path, state
                )
                try:
                    yield reader
                    if (
                        FlextCliUtilitiesAtomicFileRead.state_key(os.fstat(descriptor))
                        != receipt.version_key
                    ):
                        FlextCliUtilitiesAtomicFileRead.raise_changed(receipt.path)
                finally:
                    reader.descriptor = -1


__all__: list[str] = ["FlextCliUtilitiesAtomicFileSnapshot"]

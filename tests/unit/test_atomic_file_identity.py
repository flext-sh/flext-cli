"""Physical-identity contracts for public atomic file operations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import errno
import hashlib
import sys
from pathlib import Path

import pytest

from tests import m, tm, u


class TestsFlextCliAtomicFileIdentity:
    """Prove callers cannot authorize effects with only matching content."""

    @staticmethod
    def test_receipt_publication_retains_bytes_and_consumes_stage(
        tmp_path: Path,
    ) -> None:
        """Publication accepts complete receipts without loading payload bytes."""
        destination = tmp_path / "live.bin"
        staged = tmp_path / "staged.bin"
        payload = bytes(range(256)) * 16_385
        staged.write_bytes(payload)
        before = tm.ok(u.Cli.atomic_read_binary_file_receipt(destination))
        replacement = tm.ok(
            u.Cli.atomic_read_binary_file_receipt(staged, required=True)
        )
        published = tm.ok(
            u.Cli.atomic_publish_staged_binary_file_receipt_guarded(before, replacement)
        )
        tm.fail(staged.exists())
        tm.that(destination.read_bytes(), eq=payload)
        tm.that(published.sha256, eq=replacement.sha256)
        with u.Cli.atomic_binary_file_reader(published) as reader:
            tm.that(reader.read_range(len(payload) - 17, 17), eq=payload[-17:])

    @staticmethod
    @pytest.mark.parametrize("mutation", ["destination", "staged", "digest"])
    def test_receipt_publication_refuses_drift_before_replacement(
        tmp_path: Path, mutation: str
    ) -> None:
        """Every changed destination, staging version, or digest remains a failure."""
        destination = tmp_path / "live.bin"
        staged = tmp_path / "staged.bin"
        destination.write_bytes(b"original")
        staged.write_bytes(b"replacement")
        before = tm.ok(
            u.Cli.atomic_read_binary_file_receipt(destination, required=True)
        )
        replacement = tm.ok(
            u.Cli.atomic_read_binary_file_receipt(staged, required=True)
        )
        if mutation == "destination":
            destination.write_bytes(b"changed")
        elif mutation == "staged":
            staged.write_bytes(b"changed")
        else:
            replacement = m.Cli.AtomicFileReceipt.model_validate({
                **replacement.model_dump(),
                "sha256": u.Cli.sha256_bytes(b"foreign"),
            })
        tm.fail(
            u.Cli.atomic_publish_staged_binary_file_receipt_guarded(before, replacement)
        )
        tm.ok(staged.exists())
        tm.that(
            destination.read_bytes(),
            eq=b"changed" if mutation == "destination" else b"original",
        )

    @staticmethod
    def test_receipt_optional_absence_and_required_size_guard(tmp_path: Path) -> None:
        """Byte-free capture retains explicit absence and rejects oversized input."""
        missing = tmp_path / "unmaterialized" / "missing.bin"
        receipt = tm.ok(u.Cli.atomic_read_binary_file_receipt(missing))
        tm.that(receipt.device, eq=None)
        tm.that(receipt.sha256, eq=None)
        tm.fail(u.Cli.atomic_read_binary_file_receipt(missing, required=True))
        path = tmp_path / "receipt.bin"
        path.write_bytes(b"larger")
        failed = u.Cli.atomic_read_binary_file_receipt(path, required=True, max_bytes=1)
        tm.fail(failed)
        tm.that(failed.exception, is_=OSError)

    @staticmethod
    def test_shallow_inventory_captures_namespace_without_child_payloads(
        tmp_path: Path,
    ) -> None:
        """Immediate elections include empty folders, files, and literal symlinks."""
        root = tmp_path / "namespace"
        root.mkdir()
        (root / "empty").mkdir()
        (root / "module.py").write_bytes(b"value = 1")
        (root / "alias.py").symlink_to("module.py")
        inventory = tm.ok(u.Cli.atomic_inventory_physical_directory(root))
        tm.that(
            tuple((entry.name, entry.kind) for entry in inventory.entries),
            eq=(("alias.py", "symlink"), ("empty", "directory"), ("module.py", "file")),
        )
        tm.that(inventory.entries[0].link_target, eq="module.py")

    @staticmethod
    def test_receipt_and_scoped_ranges_match_authenticated_state(
        tmp_path: Path,
    ) -> None:
        """Receipt capture and repeated ranges retain the public snapshot contract."""
        path = tmp_path / "receipt.bin"
        payload = bytes(range(256))
        path.write_bytes(payload)
        receipt = tm.ok(u.Cli.atomic_read_binary_file_receipt(path, required=True))
        snapshot = tm.ok(u.Cli.atomic_read_binary_file_state(path, required=True))
        tm.that(receipt.device, eq=snapshot.device)
        tm.that(receipt.inode, eq=snapshot.inode)
        tm.that(receipt.parent_inode, eq=snapshot.parent_inode)
        tm.that(receipt.size, eq=len(payload))
        tm.that(receipt.sha256, eq=u.Cli.sha256_bytes(payload))
        with u.Cli.atomic_binary_file_reader(receipt) as reader:
            tm.that(reader.read_range(0, len(payload)), eq=payload)
            tm.that(reader.read_range(17, 31), eq=payload[17:48])
        tm.that(
            tm.ok(u.Cli.atomic_read_binary_file_range(receipt, 17, 31)),
            eq=payload[17:48],
        )

    @staticmethod
    @pytest.mark.parametrize("mutation", ["content", "identity"])
    def test_receipt_reader_rejects_change_during_consumption(
        tmp_path: Path, mutation: str
    ) -> None:
        """Scoped receipt reads reject content mutation and pathname replacement."""
        path = tmp_path / "receipt.bin"
        payload = bytes(range(256))
        path.write_bytes(payload)
        receipt = tm.ok(u.Cli.atomic_read_binary_file_receipt(path, required=True))

        def mutate_during_consumption() -> None:
            """Read one authenticated range, then change the captured receipt."""
            with u.Cli.atomic_binary_file_reader(receipt) as reader:
                tm.that(reader.read_range(0, len(payload)), eq=payload)
                if mutation == "content":
                    path.write_bytes(b"changed")
                else:
                    replacement = tmp_path / "replacement.bin"
                    replacement.write_bytes(payload)
                    replacement.replace(path)

        with pytest.raises(OSError, match="changed"):
            mutate_during_consumption()

    @staticmethod
    def test_authenticated_stream_retains_every_binary_byte(tmp_path: Path) -> None:
        """A fully consumed public stream agrees with the authenticated snapshot."""
        path = tmp_path / "stream.bin"
        payload = bytes(range(256)) * 16_385
        path.write_bytes(payload)
        digest = hashlib.sha256()
        size = 0
        for chunk in u.Cli.atomic_iter_binary_file(path):
            size += len(chunk)
            digest.update(chunk)
        tm.that(size, eq=len(payload))
        tm.that(digest.hexdigest(), eq=u.Cli.sha256_bytes(payload))
        tm.that(
            tm.ok(u.Cli.atomic_read_binary_file_state(path, required=True)).content,
            eq=payload,
        )

    @staticmethod
    @pytest.mark.parametrize("mutation", ["content", "identity"])
    def test_authenticated_stream_rejects_change_during_consumption(
        tmp_path: Path, mutation: str
    ) -> None:
        """Neither a changed inode nor changed bytes can complete authentication."""
        path = tmp_path / "stream.bin"
        path.write_bytes(bytes(range(256)) * 16_385)
        stream = iter(u.Cli.atomic_iter_binary_file(path))
        tm.that(bool(next(stream)))
        if mutation == "content":
            path.write_bytes(b"changed")
        else:
            replacement = tmp_path / "replacement.bin"
            replacement.write_bytes(b"another inode")
            replacement.replace(path)
        with pytest.raises(OSError, match="changed"):
            tuple(stream)

    @staticmethod
    def test_authenticated_stream_rejects_absence_and_symlink(tmp_path: Path) -> None:
        """Required streamed input cannot be missing or alias a foreign leaf."""
        path = tmp_path / "stream.bin"
        with pytest.raises(FileNotFoundError):
            tuple(u.Cli.atomic_iter_binary_file(path))
        target = tmp_path / "target.bin"
        target.write_bytes(b"foreign input")
        path.symlink_to(target)
        with pytest.raises(OSError) as rejected:
            tuple(u.Cli.atomic_iter_binary_file(path))
        tm.that(rejected.value.errno, eq=errno.EINVAL)
        tm.ok(path.is_symlink())
        tm.that(target.read_bytes(), eq=b"foreign input")

    @staticmethod
    @pytest.mark.parametrize("operation", ["write", "delete"])
    def test_guarded_symlink_failure_preserves_original_exception(
        tmp_path: Path,
        operation: str,
    ) -> None:
        """Keep the real filesystem exception available to a failing consumer."""
        destination = tmp_path / "atomic.bin"
        destination.write_bytes(b"planned")
        before = u.Cli.atomic_read_binary_file_state(destination, required=True)
        tm.ok(before)
        snapshot = before.value
        if snapshot.mode is None:
            pytest.fail("required atomic snapshot has no permission mode")
        target = tmp_path / "target.bin"
        original = b"independent target"
        target.write_bytes(original)
        modified_ns = target.stat().st_mtime_ns
        destination.unlink()
        destination.symlink_to(target)

        result = (
            u.Cli.atomic_write_binary_file_guarded(
                snapshot,
                b"replacement",
                permission_mode=snapshot.mode,
            )
            if operation == "write"
            else u.Cli.atomic_delete_binary_file_guarded(snapshot)
        )

        tm.fail(result)
        tm.ok(destination.is_symlink())
        tm.that(target.read_bytes(), eq=original)
        tm.that(target.stat().st_mtime_ns, eq=modified_ns)
        tm.that(result.exception, is_=OSError)
        with pytest.raises(RuntimeError) as raised:
            result.unwrap()
        tm.that(raised.value.__cause__, eq=result.exception)

    @staticmethod
    def test_publication_unchanged_requires_equal_bytes_and_mode(
        tmp_path: Path,
    ) -> None:
        """Treat matching bytes with different permissions as a real change."""
        destination = tmp_path / "live.bin"
        staged = tmp_path / "staged.bin"
        destination.write_bytes(b"content")
        staged.write_bytes(b"content")
        destination.chmod(0o600)
        staged.chmod(0o640)
        before = u.Cli.atomic_read_binary_file_state(destination, required=True)
        replacement = u.Cli.atomic_read_binary_file_state(staged, required=True)
        tm.ok(before)
        tm.ok(replacement)
        publication = m.Cli.AtomicFilePublication(
            before=before.value,
            replacement=replacement.value,
        )

        tm.fail(u.Cli.atomic_file_publication_is_unchanged(publication))

        staged.chmod(0o600)
        identical = u.Cli.atomic_read_binary_file_state(staged, required=True)
        tm.ok(identical)
        tm.that(
            u.Cli.atomic_file_publication_is_unchanged(
                m.Cli.AtomicFilePublication(
                    before=before.value,
                    replacement=identical.value,
                ),
            ),
            eq=True,
        )

    @staticmethod
    def test_exclusive_create_returns_exact_published_state(
        tmp_path: Path,
    ) -> None:
        """Create one absent binary file with its requested bytes and mode."""
        destination = tmp_path / "created.bin"

        result = u.Cli.atomic_create_binary_file_guarded(
            destination,
            b"content",
            permission_mode=0o600,
        )

        tm.ok(result)
        tm.that(result.value.content, eq=b"content")
        tm.that(result.value.mode, eq=0o600)
        tm.that(destination.read_bytes(), eq=b"content")

    @staticmethod
    def test_exclusive_create_rejects_existing_destination(
        tmp_path: Path,
    ) -> None:
        """Preserve an existing file rather than treating create as overwrite."""
        destination = tmp_path / "existing.bin"
        destination.write_bytes(b"before")

        result = u.Cli.atomic_create_binary_file_guarded(
            destination,
            b"after",
            permission_mode=0o600,
        )

        tm.fail(result)
        tm.that(destination.read_bytes(), eq=b"before")

    @staticmethod
    def test_publication_applies_authenticated_staged_replacement(
        tmp_path: Path,
    ) -> None:
        """Replace one exact live state with one exact staged state."""
        destination = tmp_path / "published.bin"
        staged = tmp_path / "staged.bin"
        destination.write_bytes(b"before")
        before = u.Cli.atomic_read_binary_file_state(destination, required=True)
        replacement = u.Cli.atomic_create_binary_file_guarded(
            staged,
            b"after",
            permission_mode=0o640,
        )
        tm.ok(before)
        tm.ok(replacement)

        result = u.Cli.atomic_apply_file_publication_guarded(
            m.Cli.AtomicFilePublication(
                before=before.value,
                replacement=replacement.value,
            ),
        )

        tm.ok(result)
        tm.that(result.value.content, eq=b"after")
        tm.that(result.value.mode, eq=0o640)
        tm.that(destination.read_bytes(), eq=b"after")
        tm.fail(staged.exists())

    @staticmethod
    def test_publication_applies_authenticated_tombstone(tmp_path: Path) -> None:
        """Delete one exact live state when its replacement is absent."""
        destination = tmp_path / "deleted.bin"
        destination.write_bytes(b"content")
        before = u.Cli.atomic_read_binary_file_state(destination, required=True)
        tombstone = u.Cli.atomic_read_binary_file_state(tmp_path / "tombstone")
        tm.ok(before)
        tm.ok(tombstone)

        result = u.Cli.atomic_apply_file_publication_guarded(
            m.Cli.AtomicFilePublication(
                before=before.value,
                replacement=tombstone.value,
            ),
        )

        tm.ok(result)
        tm.that(result.value.content, is_=None)
        tm.fail(destination.exists())

    @staticmethod
    def test_relative_write_fails_before_parent_creation(tmp_path: Path) -> None:
        """Reject a relative identity without creating its directory tree."""
        destination = Path("relative") / "atomic.txt"
        script = (
            "from pathlib import Path\n"
            "from flext_cli import u\n"
            "destination = Path('relative') / 'atomic.txt'\n"
            "result = u.Cli.atomic_write_text_file(destination, 'content')\n"
            "raise SystemExit(0 if result.failure and "
            "not destination.parent.exists() else 1)\n"
        )

        result = u.Cli.run_raw((sys.executable, "-c", script), cwd=tmp_path)

        tm.ok(result)
        tm.ok(u.Cli.process_succeeded(result.value.outcome))
        tm.fail((tmp_path / destination.parent).exists())

    @staticmethod
    def test_delete_consumes_complete_snapshot(tmp_path: Path) -> None:
        """Delete the same physical version returned by the snapshot owner."""
        destination = tmp_path / "atomic.bin"
        destination.write_bytes(b"content")
        snapshot_result = u.Cli.atomic_read_binary_file_state(
            destination,
            required=True,
        )
        tm.ok(snapshot_result)
        snapshot = snapshot_result.value
        host_state = destination.lstat()
        parent_state = tmp_path.lstat()
        tm.that(snapshot.parent_device, eq=parent_state.st_dev)
        tm.that(snapshot.parent_inode, eq=parent_state.st_ino)
        tm.that(snapshot.link_count, eq=1)
        tm.that(
            snapshot.file_attributes,
            eq=getattr(host_state, "st_file_attributes", None),
        )
        tm.that(snapshot.reparse_tag, eq=getattr(host_state, "st_reparse_tag", None))

        result = u.Cli.atomic_delete_binary_file_guarded(snapshot)

        tm.ok(result)
        tm.fail(destination.exists())

    @staticmethod
    def test_delete_rejects_replacement_with_same_bytes_and_mode(
        tmp_path: Path,
    ) -> None:
        """Treat a new inode as stale even when bytes and mode are unchanged.

        Raises:
            AssertionError: If required atomic snapshot was absent.

        """
        destination = tmp_path / "atomic.bin"
        destination.write_bytes(b"content")
        snapshot_result = u.Cli.atomic_read_binary_file_state(
            destination,
            required=True,
        )
        tm.ok(snapshot_result)
        snapshot = snapshot_result.value
        if snapshot.content is None or snapshot.mode is None:
            message = "required atomic snapshot was absent"
            raise AssertionError(message)
        replacement = tmp_path / "replacement.bin"
        replacement.write_bytes(snapshot.content)
        replacement.chmod(snapshot.mode)
        Path(replacement).replace(destination)

        result = u.Cli.atomic_delete_binary_file_guarded(snapshot)

        tm.fail(result)
        tm.that(destination.read_bytes(), eq=b"content")

    @staticmethod
    def test_delete_rejects_link_count_changed_after_snapshot(
        tmp_path: Path,
    ) -> None:
        """Reject a hard link added after the caller observed unique ownership."""
        destination = tmp_path / "atomic.bin"
        destination.write_bytes(b"content")
        snapshot_result = u.Cli.atomic_read_binary_file_state(
            destination,
            required=True,
        )
        tm.ok(snapshot_result)
        alias = tmp_path / "alias.bin"
        alias.hardlink_to(destination)

        result = u.Cli.atomic_delete_binary_file_guarded(snapshot_result.value)

        tm.fail(result)
        tm.that(destination.read_bytes(), eq=b"content")
        tm.that(alias.read_bytes(), eq=b"content")

    @staticmethod
    def test_guarded_write_rejects_link_count_changed_after_snapshot(
        tmp_path: Path,
    ) -> None:
        """Require unique ownership from plan through binary publication.

        Raises:
            AssertionError: If required atomic snapshot was absent.

        """
        destination = tmp_path / "atomic.bin"
        destination.write_bytes(b"before")
        snapshot_result = u.Cli.atomic_read_binary_file_state(
            destination,
            required=True,
        )
        tm.ok(snapshot_result)
        snapshot = snapshot_result.value
        if snapshot.mode is None:
            message = "required atomic snapshot was absent"
            raise AssertionError(message)
        alias = tmp_path / "alias.bin"
        alias.hardlink_to(destination)

        result = u.Cli.atomic_write_binary_file_guarded(
            snapshot,
            b"after",
            permission_mode=snapshot.mode,
        )

        tm.fail(result)
        tm.that(destination.read_bytes(), eq=b"before")
        tm.that(alias.read_bytes(), eq=b"before")

    @staticmethod
    def test_staged_publish_preserves_complete_physical_state(
        tmp_path: Path,
    ) -> None:
        """Move the authenticated staged inode and every available host field."""
        destination = tmp_path / "published.bin"
        staged = tmp_path / "staged.bin"
        staged.write_bytes(b"content")
        destination_result = u.Cli.atomic_read_binary_file_state(destination)
        staged_result = u.Cli.atomic_read_binary_file_state(staged, required=True)
        tm.ok(destination_result)
        tm.ok(staged_result)

        result = u.Cli.atomic_publish_staged_binary_file_guarded(
            destination_result.value,
            staged_result.value,
        )

        tm.ok(result)
        tm.that(result.value.inode, eq=staged_result.value.inode)
        tm.that(result.value.link_count, eq=1)
        tm.that(result.value.file_attributes, eq=staged_result.value.file_attributes)
        tm.that(result.value.reparse_tag, eq=staged_result.value.reparse_tag)
        tm.that(destination.read_bytes(), eq=b"content")
        tm.fail(staged.exists())

    @staticmethod
    def test_staged_publish_rejects_new_hard_link(tmp_path: Path) -> None:
        """Reject staging whose unique-link invariant changed after snapshot."""
        destination = tmp_path / "published.bin"
        staged = tmp_path / "staged.bin"
        staged.write_bytes(b"content")
        destination_result = u.Cli.atomic_read_binary_file_state(destination)
        staged_result = u.Cli.atomic_read_binary_file_state(staged, required=True)
        tm.ok(destination_result)
        tm.ok(staged_result)
        alias = tmp_path / "alias.bin"
        alias.hardlink_to(staged)

        result = u.Cli.atomic_publish_staged_binary_file_guarded(
            destination_result.value,
            staged_result.value,
        )

        tm.fail(result)
        tm.fail(destination.exists())
        tm.that(staged.read_bytes(), eq=b"content")
        tm.that(alias.read_bytes(), eq=b"content")

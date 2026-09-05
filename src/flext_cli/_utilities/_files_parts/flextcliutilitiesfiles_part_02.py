"""Generic filesystem helpers shared through ``u.Cli``."""

from __future__ import annotations

import shutil
from pathlib import Path

from flext_cli import c, m, p, r, t
from flext_cli._utilities.atomic_file import write_atomic_bytes
from flext_cli._utilities.atomic_file_delete import remove_guarded_file
from flext_cli._utilities.atomic_file_path import validate_atomic_path


class FlextCliUtilitiesFiles:
    """Implementation part for FlextCliUtilitiesFiles."""

    @staticmethod
    def files_write_binary(file_path: t.Cli.TextPath, data: bytes) -> p.Result[bool]:
        """Write one binary file atomically in its destination directory."""
        path = Path(file_path)
        try:
            validate_atomic_path(path)
        except OSError as exc:
            return r[bool].fail(c.Cli.ERR_BINARY_WRITE_FAILED.format(error=exc))
        ensure_result = FlextCliUtilitiesFiles.ensure_dir(path.parent)
        if ensure_result.failure:
            return r[bool].fail(
                ensure_result.error or c.Cli.ERR_ENSURE_DIR_GENERIC_FAILED
            )
        try:
            write_atomic_bytes(path, data)
        except OSError as exc:
            return r[bool].fail(c.Cli.ERR_BINARY_WRITE_FAILED.format(error=exc))
        return r[bool].ok(True)

    @staticmethod
    def atomic_write_text_file(
        file_path: t.Cli.TextPath, content: str
    ) -> p.Result[bool]:
        """Write a text file atomically via the shared byte primitive."""
        path = Path(file_path)
        try:
            validate_atomic_path(path)
        except OSError as exc:
            return r[bool].fail(
                c.Cli.ERR_ATOMIC_WRITE_TEXT_FILE_FAILED.format(error=exc)
            )
        ensure_result = FlextCliUtilitiesFiles.ensure_dir(path.parent)
        if ensure_result.failure:
            return r[bool].fail(
                ensure_result.error or c.Cli.ERR_ENSURE_DIR_GENERIC_FAILED
            )
        try:
            write_atomic_bytes(path, content.encode(c.Cli.ENCODING_DEFAULT))
        except OSError as exc:
            return r[bool].fail(
                c.Cli.ERR_ATOMIC_WRITE_TEXT_FILE_FAILED.format(error=exc)
            )
        return r[bool].ok(True)

    @staticmethod
    def atomic_write_text_file_guarded(
        before: m.Cli.AtomicFileState, content: str
    ) -> p.Result[bool]:
        """Publish under a lock after one complete physical-state precondition.

        Cooperative writers must hold one exclusive lock from planning through
        this call. This operation is not compare-and-swap against actors that
        ignore that lock. The immediate parent must exist as a real directory.
        Publication syncs the staged inode and containing directory before success.
        """
        try:
            write_atomic_bytes(
                before.path,
                content.encode(c.Cli.ENCODING_DEFAULT),
                expected_state=before,
            )
        except OSError as exc:
            return r[bool].fail(
                c.Cli.ERR_ATOMIC_WRITE_TEXT_FILE_FAILED.format(error=exc)
            )
        return r[bool].ok(True)

    @staticmethod
    def atomic_write_binary_file_guarded(
        before: m.Cli.AtomicFileState, data: bytes, *, permission_mode: int
    ) -> p.Result[bool]:
        """Publish bytes and mode from one complete physical-state precondition.

        Cooperative writers must hold the same lock through planning and this
        call. This is not CAS against an actor that ignores that lock. The
        immediate real parent must exist and is never created here. Publication
        syncs the staged inode and containing directory before success.
        """
        try:
            write_atomic_bytes(
                before.path,
                data,
                expected_state=before,
                permission_mode=permission_mode,
            )
        except OSError as exc:
            return r[bool].fail(c.Cli.ERR_BINARY_WRITE_FAILED.format(error=exc))
        return r[bool].ok(True)

    @staticmethod
    def atomic_delete_binary_file_guarded(
        state: m.Cli.AtomicFileState,
    ) -> p.Result[bool]:
        """Delete one complete physical file version under the caller's lock.

        The descriptor-bound unlink depends on every writer sharing that lock; it
        is not CAS against an actor that ignores it. The containing directory is
        synced after unlink before success.
        """
        try:
            remove_guarded_file(state)
        except OSError as exc:
            return r[bool].fail(c.Cli.ERR_FILE_DELETION_FAILED.format(error=exc))
        return r[bool].ok(True)

    @staticmethod
    def files_copy(
        source_path: t.Cli.TextPath, destination_path: t.Cli.TextPath
    ) -> p.Result[bool]:
        """Copy one file preserving metadata."""

        def _copy() -> bool:
            shutil.copy2(source_path, destination_path)
            return True

        return FlextCliUtilitiesFiles.files_execute(_copy, c.Cli.ERR_FILE_COPY_FAILED)

    @staticmethod
    def files_execute[T](
        operation_func: t.Cli.NullaryOperation[T],
        error_template: str,
        **format_kwargs: t.Scalar,
    ) -> p.Result[T]:
        """Execute one operation and map common runtime errors to ``r``."""
        try:
            return r[T].ok(operation_func())
        except c.EXC_BROAD_RUNTIME_OS as exc:
            return r[T].fail(error_template.format(error=exc, **format_kwargs))

    @staticmethod
    def files_execute_bool[T](
        operation_func: t.Cli.NullaryOperation[T],
        error_template: str,
        **format_kwargs: t.Scalar,
    ) -> p.Result[bool]:
        """Execute one operation that should return a success boolean."""

        def _run() -> bool:
            _ = operation_func()
            return True

        return FlextCliUtilitiesFiles.files_execute(
            _run, error_template, **format_kwargs
        )

    @staticmethod
    def ensure_dir(path: t.Cli.TextPath) -> p.Result[Path]:
        """Create a directory tree when missing and return the resolved path."""
        target = Path(path)
        try:
            target.mkdir(parents=True, exist_ok=True)
        except OSError as exc:
            return r[Path].fail(c.Cli.ERR_ENSURE_DIR_FAILED.format(error=exc))
        return r[Path].ok(target)


__all__: list[str] = ["FlextCliUtilitiesFiles"]

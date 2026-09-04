"""Atomic filesystem service surface for FLEXT CLI."""

from __future__ import annotations

from flext_cli import m, p, t, u


class FlextCliFileToolsAtomicMixin:
    """Delegate atomic file operations to their canonical utility owner."""

    @staticmethod
    def atomic_write_text_file(
        file_path: t.Cli.TextPath, content: str
    ) -> p.Result[bool]:
        """Write text atomically through the canonical utility surface."""
        return u.Cli.atomic_write_text_file(file_path, content)

    @staticmethod
    def atomic_write_text_file_guarded(
        before: m.Cli.AtomicFileState, content: str
    ) -> p.Result[bool]:
        """Publish text after one complete physical-state precondition."""
        return u.Cli.atomic_write_text_file_guarded(before, content)

    @staticmethod
    def atomic_write_binary_file_guarded(
        before: m.Cli.AtomicFileState, data: bytes, *, permission_mode: int
    ) -> p.Result[bool]:
        """Publish bytes and mode after one complete physical precondition."""
        return u.Cli.atomic_write_binary_file_guarded(
            before, data, permission_mode=permission_mode
        )

    @staticmethod
    def atomic_delete_binary_file_guarded(
        state: m.Cli.AtomicFileState,
    ) -> p.Result[bool]:
        """Delete one complete physical file version under the caller's lock."""
        return u.Cli.atomic_delete_binary_file_guarded(state)

    @staticmethod
    def atomic_publish_staged_binary_file_guarded(
        destination_before: m.Cli.AtomicFileState, staged: m.Cli.AtomicFileState
    ) -> p.Result[m.Cli.AtomicFileState]:
        """Consume one exact staged file through the utility owner."""
        return u.Cli.atomic_publish_staged_binary_file_guarded(
            destination_before, staged
        )

    @staticmethod
    def atomic_read_binary_file_state(
        file_path: t.Cli.TextPath, *, required: bool = False
    ) -> p.Result[m.Cli.AtomicFileState]:
        """Read exact bytes, mode, and physical identity through one descriptor."""
        return u.Cli.atomic_read_binary_file_state(file_path, required=required)


__all__: list[str] = ["FlextCliFileToolsAtomicMixin"]

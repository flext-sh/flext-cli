"""Atomic filesystem service surface for FLEXT CLI."""

from __future__ import annotations

from flext_cli import m, p, t, u


class FlextCliFileToolsAtomicMixin:
    """Delegate atomic filesystem operations to their canonical utility owner."""

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
        """Read exact bytes plus leaf and immediate-parent physical identity."""
        return u.Cli.atomic_read_binary_file_state(file_path, required=required)

    @staticmethod
    def atomic_plan_directory_chain(
        directory_path: t.Cli.TextPath,
    ) -> p.Result[m.Cli.AtomicDirectoryChainPlan]:
        """Plan missing ancestors from one exact existing physical anchor."""
        return u.Cli.atomic_plan_directory_chain(directory_path)

    @staticmethod
    def atomic_create_directory_chain_guarded(
        plan: m.Cli.AtomicDirectoryChainPlan, *, permission_mode: int
    ) -> p.Result[t.SequenceOf[m.Cli.AtomicDirectoryState]]:
        """Materialize a planned chain under the caller's exclusive lock."""
        return u.Cli.atomic_create_directory_chain_guarded(
            plan, permission_mode=permission_mode
        )

    @staticmethod
    def atomic_read_empty_directory_state(
        directory_path: t.Cli.TextPath, *, required: bool = False
    ) -> p.Result[m.Cli.AtomicDirectoryState]:
        """Read exact absence or one physical empty-directory identity."""
        return u.Cli.atomic_read_empty_directory_state(
            directory_path, required=required
        )

    @staticmethod
    def atomic_create_empty_directory_guarded(
        before: m.Cli.AtomicDirectoryState, *, permission_mode: int
    ) -> p.Result[m.Cli.AtomicDirectoryState]:
        """Create one exact empty directory under the caller's lock."""
        return u.Cli.atomic_create_empty_directory_guarded(
            before, permission_mode=permission_mode
        )

    @staticmethod
    def atomic_delete_empty_directory_guarded(
        state: m.Cli.AtomicDirectoryState,
    ) -> p.Result[bool]:
        """Delete one exact empty directory under the caller's lock."""
        return u.Cli.atomic_delete_empty_directory_guarded(state)

    @staticmethod
    def atomic_publish_staged_empty_directory_guarded(
        destination_before: m.Cli.AtomicDirectoryState,
        staged: m.Cli.AtomicDirectoryState,
    ) -> p.Result[m.Cli.AtomicDirectoryState]:
        """Move one staged directory through the no-clobber utility owner."""
        return u.Cli.atomic_publish_staged_empty_directory_guarded(
            destination_before, staged
        )

    @staticmethod
    def atomic_inventory_physical_tree(
        root_path: t.Cli.TextPath,
    ) -> p.Result[m.Cli.AtomicPhysicalTreeManifest]:
        """Inventory one physical tree through the canonical utility owner."""
        return u.Cli.atomic_inventory_physical_tree(root_path)

    @staticmethod
    def atomic_cleanup_physical_tree_guarded(
        manifest: m.Cli.AtomicPhysicalTreeManifest,
    ) -> p.Result[bool]:
        """Delete one exact manifest through the canonical utility owner."""
        return u.Cli.atomic_cleanup_physical_tree_guarded(manifest)


__all__: list[str] = ["FlextCliFileToolsAtomicMixin"]

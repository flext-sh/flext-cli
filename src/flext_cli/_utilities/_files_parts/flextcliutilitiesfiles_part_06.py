"""Generic guarded publication helpers shared through ``u.Cli``."""

from __future__ import annotations

from flext_cli import m, p, r, t
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_02 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart02,
)
from flext_cli._utilities._files_parts.flextcliutilitiesfiles_part_03 import (
    FlextCliUtilitiesFiles as FlextCliUtilitiesFilesPart03,
)


class FlextCliUtilitiesFiles:
    """Implementation part for FlextCliUtilitiesFiles."""

    @staticmethod
    def atomic_create_binary_file_guarded(
        file_path: t.Cli.TextPath, data: bytes, *, permission_mode: int
    ) -> p.Result[m.Cli.AtomicFileState]:
        """Create one absent file and return its authenticated published state."""
        before = FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
            file_path, required=False
        )
        if before.failure:
            return r[m.Cli.AtomicFileState].from_failure(before)
        if before.value.content is not None:
            return r[m.Cli.AtomicFileState].fail(
                f"atomic create destination already exists: {before.value.path}"
            )
        written = FlextCliUtilitiesFilesPart02.atomic_write_binary_file_guarded(
            before.value, data, permission_mode=permission_mode
        )
        if written.failure:
            return r[m.Cli.AtomicFileState].from_failure(written)
        return FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
            before.value.path, required=True
        )

    @staticmethod
    def atomic_apply_file_publication_guarded(
        publication: m.Cli.AtomicFilePublication,
    ) -> p.Result[m.Cli.AtomicFileState]:
        """Apply one exact staged replacement or tombstone under caller lock."""
        before = publication.before
        replacement = publication.replacement
        if replacement.content is None:
            if before.content is None:
                return r[m.Cli.AtomicFileState].ok(before)
            removed = FlextCliUtilitiesFilesPart02.atomic_delete_binary_file_guarded(
                before
            )
            if removed.failure:
                return r[m.Cli.AtomicFileState].from_failure(removed)
            return FlextCliUtilitiesFilesPart03.atomic_read_binary_file_state(
                before.path, required=False
            )
        return FlextCliUtilitiesFilesPart03.atomic_publish_staged_binary_file_guarded(
            before, replacement
        )


__all__: list[str] = ["FlextCliUtilitiesFiles"]

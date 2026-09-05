"""Shared validators for descriptor-authenticated filesystem state models."""

from __future__ import annotations

import os
import stat
from pathlib import Path


def validate_atomic_state_path(
    value: Path, *, label: str, allow_root: bool = False
) -> Path:
    """Reject relative, traversing, root, or lexically non-normal paths."""
    normalized = Path(os.path.normpath(value))
    if (
        not value.is_absolute()
        or (not allow_root and not value.name)
        or ".." in value.parts
        or normalized != value
    ):
        msg = f"{label} path must be absolute and normalized"
        raise ValueError(msg)
    return value


def validate_non_reparse_state(
    file_attributes: int | None, reparse_tag: int | None, *, label: str
) -> None:
    """Reject a Windows reparse identity in any atomic state model."""
    reparse_marker = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0)
    if (
        file_attributes is not None and file_attributes & reparse_marker
    ) or reparse_tag not in {None, 0}:
        msg = f"{label} cannot identify a reparse point"
        raise ValueError(msg)


__all__: list[str] = [
    "validate_atomic_state_path",
    "validate_non_reparse_state",
]

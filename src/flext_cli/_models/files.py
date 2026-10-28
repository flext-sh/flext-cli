"""File-assertion payload models for filesystem predicate helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from flext_core import m


class FlextCliModelsFiles:
    """Typed filesystem predicates exposed flat in ``m.Cli.*``."""

    class FileAssertionOptions(m.FrozenModel):
        """Typed filesystem predicates, with None leaving each check unselected."""

        is_file: bool | None = m.Field(
            default=None,
            description="Require or reject a regular file; None leaves it unchecked.",
        )
        is_dir: bool | None = m.Field(
            default=None,
            description="Require or reject a directory; None leaves it unchecked.",
        )
        not_empty: bool | None = m.Field(
            default=None,
            description="Require non-empty file or directory contents when True.",
        )
        readable: bool | None = m.Field(
            default=None,
            description="Require read access to the path when True.",
        )
        writable: bool | None = m.Field(
            default=None,
            description="Require write access to the path when True.",
        )


__all__: list[str] = ["FlextCliModelsFiles"]

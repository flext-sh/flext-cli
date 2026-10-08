"""Test-oriented file helpers generalized for reuse through ``u.Cli``.

These operations are generic enough to be used by tests, examples, and
maintenance scripts, but were originally duplicated in ``flext-tests``.
They live here so ``flext-tests`` can delegate to ``u.Cli`` instead of
reimplementing them.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, ClassVar

from flext_core import m

if TYPE_CHECKING:
    from pathlib import Path


class _FileAssertionOptions(m.FrozenModel):
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


class FlextCliUtilitiesFileTestHelpersMixinPart02:
    """Implementation part for FlextCliUtilitiesFileTestHelpersMixinPart02."""

    FileAssertionOptions: ClassVar[type[_FileAssertionOptions]] = _FileAssertionOptions

    @staticmethod
    def files_assert_exists(
        path: Path,
        *,
        options: _FileAssertionOptions | None = None,
    ) -> Path:
        """Assert file-system properties on ``path``.

        Args:
            path: Path to validate.
            options: File/directory, non-empty, readable, and writable predicates;
                omitted options leave all checks unselected.

        Returns:
            The validated ``path``.

        Raises:
            AssertionError: when any predicate fails.

        """
        predicates = options if options is not None else _FileAssertionOptions()
        if predicates.is_file is True and not path.is_file():
            msg = f"Expected file: {path}"
            raise AssertionError(msg)
        if predicates.is_file is False and path.is_file():
            msg = f"Expected non-file: {path}"
            raise AssertionError(msg)
        if predicates.is_dir is True and not path.is_dir():
            msg = f"Expected directory: {path}"
            raise AssertionError(msg)
        if predicates.is_dir is False and path.is_dir():
            msg = f"Expected non-directory: {path}"
            raise AssertionError(msg)
        if predicates.not_empty is True:
            if path.is_file() and path.stat().st_size == 0:
                msg = f"Expected non-empty file: {path}"
                raise AssertionError(msg)
            if path.is_dir() and not any(path.iterdir()):
                msg = f"Expected non-empty directory: {path}"
                raise AssertionError(msg)
        if predicates.readable is True and not os.access(path, os.R_OK):
            msg = f"Expected readable path: {path}"
            raise AssertionError(msg)
        if predicates.writable is True and not os.access(path, os.W_OK):
            msg = f"Expected writable path: {path}"
            raise AssertionError(msg)
        return path


__all__: list[str] = ["FlextCliUtilitiesFileTestHelpersMixinPart02"]

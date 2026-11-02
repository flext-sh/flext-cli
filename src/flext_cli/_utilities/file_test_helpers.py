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
from typing import TYPE_CHECKING

from flext_core import u

from flext_cli import c, p, r, t
from flext_cli._models.files import FlextCliModelsFiles
from flext_cli._utilities.json import FlextCliUtilitiesJson
from flext_cli._utilities.toml import FlextCliUtilitiesToml

if TYPE_CHECKING:
    from pathlib import Path


class FlextCliUtilitiesFileTestHelpers:
    """Own the shared file assertions and content parsing without wrapper parts."""

    @staticmethod
    def files_assert_exists(
        path: Path,
        *,
        options: FlextCliModelsFiles.FileAssertionOptions | None = None,
    ) -> Path:
        """Assert the requested file-system properties.

        Returns:
            The validated path.

        Raises:
            AssertionError: If any selected predicate fails.

        """
        predicates = (
            options
            if options is not None
            else FlextCliModelsFiles.FileAssertionOptions()
        )
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

    @staticmethod
    def files_parse_content(path: Path, fmt: str) -> p.Result[t.JsonMapping]:
        """Parse JSON, YAML or TOML through the existing format owner.

        Returns:
            The parsed mapping or the format owner's original failure.

        """
        if fmt == c.Cli.FILE_FORMAT_JSON:
            result = FlextCliUtilitiesJson.json_read(path)
        elif fmt == c.Cli.FILE_FORMAT_YAML:
            result = u.Yaml.yaml_safe_load(path)
        elif fmt == c.Cli.FILE_FORMAT_TOML:
            result = FlextCliUtilitiesToml.toml_read_json(path)
        else:
            msg = f"Cannot parse format: {fmt}"
            return r[t.JsonMapping].fail(msg)
        return result


__all__: list[str] = ["FlextCliUtilitiesFileTestHelpers"]

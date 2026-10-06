"""Test-oriented file helpers generalized for reuse through ``u.Cli``.

These operations are generic enough to be used by tests, examples, and
maintenance scripts, but were originally duplicated in ``flext-tests``.
They live here so ``flext-tests`` can delegate to ``u.Cli`` instead of
reimplementing them.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import c, p, r, t
from flext_cli._utilities.json import FlextCliUtilitiesJson
from flext_cli._utilities.toml import FlextCliUtilitiesToml
from flext_core import u

if TYPE_CHECKING:
    from pathlib import Path


class FlextCliUtilitiesFileTestHelpersMixinPart04:
    """Implementation part for FlextCliUtilitiesFileTestHelpersMixinPart04."""

    @staticmethod
    def files_parse_content(path: Path, fmt: str) -> p.Result[t.JsonMapping]:
        """Parse JSON/YAML/TOML file content generically by format token.

        Returns:
            The resulting ``p.Result[t.JsonMapping]``.

        """
        if fmt == c.Cli.FILE_FORMAT_JSON:
            result = FlextCliUtilitiesJson.json_read(path)
            if result.failure:
                return r[t.JsonMapping].from_failure(result)
            return r[t.JsonMapping].ok(result.value)
        if fmt == c.Cli.FILE_FORMAT_YAML:
            result = u.Yaml.yaml_safe_load(path)
            if result.failure:
                return r[t.JsonMapping].from_failure(result)
            return r[t.JsonMapping].ok(result.value)
        if fmt == c.Cli.FILE_FORMAT_TOML:
            toml_result = FlextCliUtilitiesToml.toml_read_json(path)
            if toml_result.failure:
                return r[t.JsonMapping].from_failure(toml_result)
            return r[t.JsonMapping].ok(toml_result.value)
        msg = f"Cannot parse format: {fmt}"
        return r[t.JsonMapping].fail(msg)


__all__: list[str] = ["FlextCliUtilitiesFileTestHelpersMixinPart04"]

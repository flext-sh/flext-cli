"""Generic TOML helpers shared through ``u.Cli.toml_*``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from flext_cli import c, e, p, r, t

if TYPE_CHECKING:
    from pathlib import Path


class FlextCliUtilitiesTomlPart07:
    """Implementation part for FlextCliUtilitiesTomlPart07."""

    @staticmethod
    def toml_write_mapping(path: Path, mapping: t.JsonMapping) -> p.Result[bool]:
        """Write one validated plain mapping as TOML through the canonical writer.

        Returns:
            The resulting ``p.Result[bool]``.

        """
        from flext_cli._utilities import FlextCliUtilitiesTomlPart01, FlextCliUtilitiesTomlPart06
        try:
            document = FlextCliUtilitiesTomlPart01.toml_document_from_mapping(mapping)
        except c.EXC_TYPE_VALIDATION as exc:
            return e.fail_validation("TOML build", error=exc, result_type=r[bool])
        return FlextCliUtilitiesTomlPart06.toml_write_document(path, document)


__all__: list[str] = ["FlextCliUtilitiesTomlPart07"]

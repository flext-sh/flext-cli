"""Generic TOML helpers shared through ``u.Cli.toml_*``.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Sequence

from flext_cli import t
from flext_cli._utilities._toml.flextcliutilitiestoml_part_01 import (
    FlextCliUtilitiesTomlPart01,
)


class FlextCliUtilitiesTomlPart05:
    """Implementation part for FlextCliUtilitiesTomlPart05."""

    @staticmethod
    def toml_mapping_sync_string_list(
        container: t.MutableJsonMapping,
        key: str,
        expected: Sequence[str],
        *,
        sort_values: bool = False,
    ) -> bool:
        """Synchronize a plain string-list field; return True if mutated.

        Returns:
            The resulting ``bool``.

        """
        current = FlextCliUtilitiesTomlPart01.toml_as_string_list(
            container.get(key, None),
        )
        normalized_expected = sorted(expected) if sort_values else [*expected]
        normalized_current = sorted(current) if sort_values else [*current]
        if normalized_current == normalized_expected:
            return False
        normalized_list: t.JsonValueList = list(normalized_expected)
        container[key] = normalized_list
        return True

    @staticmethod
    def toml_dot_path(*parts: str) -> str:
        """Build one dotted TOML path from non-empty segments.

        Returns:
            The resulting ``str``.

        """
        return ".".join(part for part in parts if part)


__all__: list[str] = ["FlextCliUtilitiesTomlPart05"]

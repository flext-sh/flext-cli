"""OOXML storage codec for authored formula text.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import re
from typing import ClassVar

from flext_cli import c

# mro-j47u (kimi): utilities consume local facades only, never private modules.


class FlextCliUtilitiesXlsxFormulaCodec:
    """Encode authored formulas into their OOXML storage form."""

    # NOTE (multi-agent, mro-j2yt.1): OOXML stores functions introduced
    # after Excel 2007 with the _xlfn. prefix and conforming readers map
    # it back. Authored formulas keep canonical names; this codec owns the
    # single storage transformation at the external write boundary and
    # never rewrites text inside string literals.
    _TOKENS: ClassVar[re.Pattern[str]] = re.compile(r'"(?:[^"]|"")*"?|[^\W\d][\w.]*')

    @classmethod
    def storage_formula(cls, formula: str) -> str:
        """Prefix every future function call outside string literals.

        Returns:
            The formula text in its OOXML storage form.

        """
        future = c.Cli.XLSX_FUTURE_FUNCTIONS
        prefix = c.Cli.XLSX_FUTURE_FUNCTION_PREFIX

        def stored(match: re.Match[str]) -> str:
            run = match.group()
            # A name starts at its first letter or underscore; numeric word
            # characters before it stay plain text.
            start = next(
                (
                    index
                    for index, char in enumerate(run)
                    if char.isalpha() or char == "_"
                ),
                len(run),
            )
            name = run[start:]
            calls = formula.startswith("(", match.end())
            if run[0] != '"' and calls and name.upper() in future:
                return run[:start] + prefix + name
            return run

        return cls._TOKENS.sub(stored, formula)


__all__: tuple[str, ...] = ("FlextCliUtilitiesXlsxFormulaCodec",)

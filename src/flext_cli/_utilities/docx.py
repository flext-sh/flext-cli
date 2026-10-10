"""Public MRO composition of the generic DOCX behavior owners.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import t
from flext_cli._utilities._docx._reader import FlextCliUtilitiesDocxReader
from flext_cli._utilities._docx._renderer import FlextCliUtilitiesDocxRenderer


class FlextCliUtilitiesDocx(
    FlextCliUtilitiesDocxReader,
    FlextCliUtilitiesDocxRenderer,
):
    """Inherit reading and rendering from their sole defining owners."""


__all__: t.VariadicTuple[str] = ("FlextCliUtilitiesDocx",)

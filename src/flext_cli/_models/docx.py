"""Private MRO composition for generic DOCX models.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import t
from flext_cli._models import FlextCliModelsDocxDocument
from flext_cli._models import FlextCliModelsDocxStyles


class FlextCliModelsDocx(FlextCliModelsDocxDocument, FlextCliModelsDocxStyles):
    """Canonical private DOCX model namespace."""


__all__: t.VariadicTuple[str] = ("FlextCliModelsDocx",)

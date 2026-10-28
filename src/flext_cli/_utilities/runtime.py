"""Extracted facade class for runtime.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli._utilities._runtime import (
    FlextCliUtilitiesRuntimeCommands,
    FlextCliUtilitiesRuntimeRunToFile,
)


class FlextCliUtilitiesRuntime(
    FlextCliUtilitiesRuntimeCommands,
    FlextCliUtilitiesRuntimeRunToFile,
):
    """Facade for runtime."""


__all__: list[str] = ["FlextCliUtilitiesRuntime"]

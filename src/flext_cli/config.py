"""Public configuration facade for Flext CLI.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._config import FlextCliConfig, config

if TYPE_CHECKING:
    from flext_core import t

__all__: t.VariadicTuple[str] = ("FlextCliConfig", "config")

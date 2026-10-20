"""DSL service for external process runtime helpers.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import p, s, t


class FlextCliRuntime(s[p.Cli.RuntimeStatus]):
    """Expose process execution helpers through ``cli`` and ``FlextCli``."""


__all__: t.MutableSequenceOf[str] = ["FlextCliRuntime"]

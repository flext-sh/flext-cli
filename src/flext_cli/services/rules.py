"""DSL service for declarative local rule loading.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import m, s, t


class FlextCliRules(s[m.Cli.RuntimeStatus]):
    """Expose the generic rule-loading DSL through ``cli`` and ``u.Cli``."""


__all__: t.MutableSequenceOf[str] = ["FlextCliRules"]

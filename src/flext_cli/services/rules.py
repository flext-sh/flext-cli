"""DSL service for declarative local rule loading.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import p, s, t


class FlextCliRules(s[p.Cli.RuntimeStatus]):
    """Expose the generic rule-loading DSL through ``cli`` and ``u.Cli``."""


__all__: t.MutableSequenceOf[str] = ["FlextCliRules"]

"""Shared service foundation for flext-cli components.

Reads settings through the service runtime so every consumer uses
``settings`` as the single settings access point.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_cli import p, r, t
from flext_core import s


class FlextCliServiceBase(s[t.JsonMapping]):
    """Base class for flext-cli services with typed configuration access.

    Note: This is an abstract base class. Subclasses must implement the
    `execute` method from s.
    """

    @override
    def execute(self) -> p.Result[t.JsonMapping]:
        """Default service execution surface for mixins without an active command."""
        empty_payload: t.JsonMapping = {}
        return r[t.JsonMapping].ok(empty_payload)


s = FlextCliServiceBase

__all__: t.MutableSequenceOf[str] = ["FlextCliServiceBase", "s"]

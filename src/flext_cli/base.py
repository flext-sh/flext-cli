"""Shared service foundation for flext-cli components.

Centralizes access to configuration singleton while maintaining inheritance
aligned with `s` from flext-core, avoiding duplication of initialization
across library services.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from abc import ABC
from typing import override

from flext_core import FlextSettings, s

from flext_cli import FlextCliSettings, p, r, t


class FlextCliServiceBase(s[t.Cli.JsonMapping], ABC):
    """Base class for flext-cli services with typed configuration access.

    Note: This is an abstract base class. Subclasses must implement the
    `execute` method from s.
    """

    def execute(self) -> p.Result[t.Cli.JsonMapping]:
        """Default service execution surface for mixins without an active command."""
        empty_payload: t.Cli.JsonMapping = {}
        return r[t.Cli.JsonMapping].ok(empty_payload)

    @property
    @override
    def settings(self) -> FlextCliSettings:
        """Return the typed CLI settings namespace."""
        return FlextSettings.fetch_global().fetch_namespace("cli", FlextCliSettings)


s = FlextCliServiceBase

__all__: list[str] = ["FlextCliServiceBase", "s"]

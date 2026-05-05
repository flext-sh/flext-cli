"""Shared service foundation for flext-cli components.

Reads settings via ``FlextCliSettings.fetch_global()`` per access so runtime
mutations propagate (rule 1, no caching of references).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_cli import FlextCliSettings, p, r, t
from flext_core import s


class FlextCliServiceBase(s):
    """Base class for flext-cli services with typed configuration access.

    Note: This is an abstract base class. Subclasses must implement the
    `execute` method from s.
    """

    @override
    def execute(self) -> p.Result[t.JsonMapping]:
        """Default service execution surface for mixins without an active command."""
        empty_payload: t.JsonMapping = {}
        return r[t.JsonMapping].ok(empty_payload)

    @property
    @override
    def settings(self) -> p.Cli.Settings:
        """Return the global CLI settings singleton (rule 1, propagating)."""
        return FlextCliSettings.fetch_global()

    def new_settings(self) -> p.Cli.Settings:
        """Construct a fresh settings instance with default values (test isolation)."""
        return FlextCliSettings()


s = FlextCliServiceBase

__all__: t.MutableSequenceOf[str] = ["FlextCliServiceBase", "s"]

"""Shared service foundation for flext-cli components.

Reads settings through the service runtime so every consumer uses
``self.settings`` as the single settings access point.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import override

from flext_cli import FlextCliSettings, m, p, r, t
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

    @classmethod
    def _runtime_bootstrap_options(cls) -> m.RuntimeBootstrapOptions:
        """Return runtime bootstrap options for CLI services."""
        return m.RuntimeBootstrapOptions(settings_type=FlextCliSettings)

    @property
    @override
    def settings(self) -> p.Cli.Settings:
        """Return the live CLI settings singleton.

        Reads ``FlextCliSettings.fetch_global()`` on each access so mutations
        performed via ``update_global`` propagate immediately to consumers
        (services, callbacks, tests) without resorting to the runtime's
        cached snapshot.
        """
        return FlextCliSettings.fetch_global()

    def new_settings(self) -> p.Cli.Settings:
        """Construct a fresh settings instance with default values (test isolation)."""
        return self.settings.clone()


s = FlextCliServiceBase

__all__: t.MutableSequenceOf[str] = ["FlextCliServiceBase", "s"]

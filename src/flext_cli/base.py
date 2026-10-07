"""Shared service foundation for flext-cli components.

Reads settings through the service runtime so every consumer uses
``settings`` as the single settings access point.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from flext_cli import m, p
from flext_cli._settings import FlextCliSettings

# Concrete-module imports: this module resolves during the package root's
# lazy ``s`` export, when the root namespace is still initializing.
from flext_cli._utilities import FlextCliUtilitiesCli
from flext_core import FlextService

if TYPE_CHECKING:
    from flext_cli import t


class FlextCliServiceBase[TDomainResult: p.Base = m.Cli.RuntimeStatus](
    FlextService[TDomainResult],
    FlextCliUtilitiesCli,
):
    """Base class for flext-cli services with typed configuration access.

    Note: This is an abstract base class. Subclasses must implement the
    `execute` method from FlextService.
    """

    @property
    @override
    def settings(self) -> p.Cli.Settings:
        """The typed CLI settings resolved by the service runtime.

        Raises:
            TypeError: If runtime settings do not satisfy the CLI settings contract.
        """
        resolved = super().settings
        if not isinstance(resolved, p.Cli.Settings):
            msg = "Runtime settings do not satisfy the CLI settings contract"
            raise TypeError(msg)
        return resolved

    @classmethod
    def runtime_bootstrap_options(cls) -> m.RuntimeBootstrapOptions:
        """Return runtime bootstrap options binding the CLI settings class."""
        return m.RuntimeBootstrapOptions(settings_type=FlextCliSettings)


s = FlextCliServiceBase

__all__: t.MutableSequenceOf[str] = ["FlextCliServiceBase", "s"]

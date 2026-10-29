"""Shared service foundation for flext-cli components.

Reads settings through the service runtime so every consumer uses
``settings`` as the single settings access point.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import MutableSequence
from typing import override

from flext_core import FlextService

from flext_cli import FlextCliSettings, FlextCliUtilities, m, p


class FlextCliServiceBase[TDomainResult: p.Base](
    FlextService[TDomainResult],
    m.Cli.ServiceOptions,
    FlextCliUtilities,
):
    """Base class for flext-cli services with typed configuration access.

    Native collaborator fields come from the shared CLI service-options model;
    concrete services expose their domain handlers through the API MRO.
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
    def runtime_bootstrap_options(cls) -> p.RuntimeBootstrapOptions:
        """Return runtime bootstrap options binding the CLI settings class."""
        return m.RuntimeBootstrapOptions(settings_type=FlextCliSettings)


s = FlextCliServiceBase

__all__: MutableSequence[str] = ["FlextCliServiceBase", "s"]

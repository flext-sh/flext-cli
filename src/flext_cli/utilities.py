"""FLEXT CLI utility facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import ClassVar

from flext_cli._utilities._cli_namespace import FlextCliUtilitiesCli
from flext_core import FlextUtilities, m


class FlextCliUtilities(FlextUtilities):
    """CLI utility facade composed from internal utility mixins."""

    # Why (multi-agent): the pydantic metaclass strips class-typed attributes
    # from the namespace; the CLI namespace class is the canonical facade
    # surface consumed as u.Cli fleet-wide and must survive model construction.
    model_config = m.ConfigDict(ignored_types=(type(FlextCliUtilitiesCli),))

    # NOTE (multi-agent): mro-wkii.17.17 publishes the canonical class directly.
    Cli: ClassVar[type[FlextCliUtilitiesCli]] = FlextCliUtilitiesCli


u = FlextCliUtilities

__all__: list[str] = ["FlextCliUtilities", "u"]

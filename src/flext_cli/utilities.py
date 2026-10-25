# AUTO-GENERATED FILE — Regenerate with: make gen
"""FLEXT CLI utility facade.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypeAlias

from flext_core import FlextUtilities

from flext_cli._utilities import FlextCliUtilitiesCli


class FlextCliUtilities(FlextUtilities):
    """CLI utility facade composed from internal utility mixins."""

    # Why (multi-agent): the pydantic metaclass strips class-typed attributes
    # from the namespace; the CLI namespace class is the canonical facade
    # surface consumed as u.Cli fleet-wide and must survive model construction.
    # The ConfigDict is owned by the namespace class it protects; this
    # identity alias keeps the config in the facade body where pydantic reads it.
    model_config = FlextCliUtilitiesCli.model_config

    # NOTE (multi-agent): mro-wkii.17.17 publishes the canonical class directly.
    # Unannotated single bind: pyright resolves the member as a type alias so
    # ``u.Cli`` stays valid in type expressions; pydantic still ignores the
    # class-typed attribute through ``ignored_types`` (runtime identical to the
    # former ``ClassVar`` form).
    Cli: TypeAlias = FlextCliUtilitiesCli


u = FlextCliUtilities
__all__: list[str] = ["FlextCliUtilities", "FlextCliUtilitiesCli", "u"]

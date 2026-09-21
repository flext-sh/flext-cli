"""FLEXT CLI utility facade."""

from __future__ import annotations

from flext_core import u
from pydantic import ConfigDict

from ._utilities._cli_namespace import FlextCliUtilitiesCli


class FlextCliUtilities(u):
    """CLI utility facade composed from internal utility mixins."""

    # Why (multi-agent): the pydantic metaclass strips class-typed attributes
    # from the namespace; the CLI namespace class is the canonical facade
    # surface consumed as u.Cli fleet-wide and must survive model construction.
    model_config = ConfigDict(ignored_types=(type(FlextCliUtilitiesCli),))

    # NOTE (multi-agent): mro-wkii.17.17 publishes the canonical class directly.
    Cli: type[FlextCliUtilitiesCli] = FlextCliUtilitiesCli


u = FlextCliUtilities

__all__: list[str] = ["FlextCliUtilities", "u"]

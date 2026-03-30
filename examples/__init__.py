# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Examples package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from examples import (
        constants as constants,
        models as models,
        protocols as protocols,
        typings as typings,
        utilities as utilities,
    )
    from examples.constants import (
        ExamplesConstants as ExamplesConstants,
        ExamplesConstants as c,
    )
    from examples.models import ExamplesModels as ExamplesModels, ExamplesModels as m
    from examples.protocols import (
        ExamplesProtocols as ExamplesProtocols,
        ExamplesProtocols as p,
    )
    from examples.typings import ExamplesTypes as ExamplesTypes, ExamplesTypes as t
    from examples.utilities import (
        ExamplesUtilities as ExamplesUtilities,
        ExamplesUtilities as u,
    )
    from flext_cli import d as d, e as e, h as h, r as r, s as s, x as x

_LAZY_IMPORTS: Mapping[str, Sequence[str]] = {
    "ExamplesConstants": ["examples.constants", "ExamplesConstants"],
    "ExamplesModels": ["examples.models", "ExamplesModels"],
    "ExamplesProtocols": ["examples.protocols", "ExamplesProtocols"],
    "ExamplesTypes": ["examples.typings", "ExamplesTypes"],
    "ExamplesUtilities": ["examples.utilities", "ExamplesUtilities"],
    "c": ["examples.constants", "ExamplesConstants"],
    "constants": ["examples.constants", ""],
    "d": ["flext_cli", "d"],
    "e": ["flext_cli", "e"],
    "h": ["flext_cli", "h"],
    "m": ["examples.models", "ExamplesModels"],
    "models": ["examples.models", ""],
    "p": ["examples.protocols", "ExamplesProtocols"],
    "protocols": ["examples.protocols", ""],
    "r": ["flext_cli", "r"],
    "s": ["flext_cli", "s"],
    "t": ["examples.typings", "ExamplesTypes"],
    "typings": ["examples.typings", ""],
    "u": ["examples.utilities", "ExamplesUtilities"],
    "utilities": ["examples.utilities", ""],
    "x": ["flext_cli", "x"],
}

_EXPORTS: Sequence[str] = [
    "ExamplesConstants",
    "ExamplesModels",
    "ExamplesProtocols",
    "ExamplesTypes",
    "ExamplesUtilities",
    "c",
    "constants",
    "d",
    "e",
    "h",
    "m",
    "models",
    "p",
    "protocols",
    "r",
    "s",
    "t",
    "typings",
    "u",
    "utilities",
    "x",
]


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, _EXPORTS)

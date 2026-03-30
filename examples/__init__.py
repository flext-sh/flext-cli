# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""Examples package."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from examples import constants, models, protocols, typings, utilities
    from examples.constants import *
    from examples.models import *
    from examples.protocols import *
    from examples.typings import *
    from examples.utilities import *
    from flext_cli import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "ExamplesConstants": "examples.constants",
    "ExamplesModels": "examples.models",
    "ExamplesProtocols": "examples.protocols",
    "ExamplesTypes": "examples.typings",
    "ExamplesUtilities": "examples.utilities",
    "c": ["examples.constants", "ExamplesConstants"],
    "constants": "examples.constants",
    "d": "flext_cli",
    "e": "flext_cli",
    "h": "flext_cli",
    "m": ["examples.models", "ExamplesModels"],
    "models": "examples.models",
    "p": ["examples.protocols", "ExamplesProtocols"],
    "protocols": "examples.protocols",
    "r": "flext_cli",
    "s": "flext_cli",
    "t": ["examples.typings", "ExamplesTypes"],
    "typings": "examples.typings",
    "u": ["examples.utilities", "ExamplesUtilities"],
    "utilities": "examples.utilities",
    "x": "flext_cli",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS, sorted(_LAZY_IMPORTS))

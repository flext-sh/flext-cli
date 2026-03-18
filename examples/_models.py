"""Auto-generated centralized models."""

from __future__ import annotations

from pathlib import Path

from flext_core import t as core_t
from pydantic import RootModel


class FlextAutoConstants:
    pass


class FlextAutoTypes:
    pass


class FlextAutoProtocols:
    pass


class FlextAutoUtilities:
    pass


class FlextAutoModels:
    pass


c = FlextAutoConstants
t = FlextAutoTypes
p = FlextAutoProtocols
u = FlextAutoUtilities
m = FlextAutoModels


class EnvInput(
    RootModel[dict[str, str | int | bool | Path] | core_t.Primitives | None]
):
    pass

from __future__ import annotations

from typing import Annotated

from flext_cli import m


class X(m.FrozenModel):
    name: Annotated[str, m.Field(description="x")] = ""

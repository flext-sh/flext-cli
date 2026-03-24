"""FLEXT CLI example type aliases."""

from __future__ import annotations

from collections.abc import Mapping

from flext_core import t

type EnvInput = Mapping[str, t.Container] | t.Primitives | None

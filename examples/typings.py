"""FLEXT CLI example type aliases."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from flext_core import t

type EnvInput = Mapping[str, str | int | bool | Path] | t.Primitives | None

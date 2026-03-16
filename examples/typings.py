from __future__ import annotations

from pathlib import Path

type EnvInput = dict[str, str | int | bool | Path] | str | int | float | bool | None

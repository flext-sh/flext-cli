"""Plugin type aliases for FLEXT CLI examples."""

from __future__ import annotations

from collections.abc import Callable, Mapping

type DataProcessor = Callable[[str], str]

type ProcessorRegistry = Mapping[str, DataProcessor]

"""Re-export of the python-pptx ``Presentation`` class for type annotations.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import (
    Iterable,
    Iterator,
    Mapping,
    MutableMapping,
    MutableSequence,
    Sequence,
)

from pptx.presentation import Presentation

__all__ = ["Presentation"]

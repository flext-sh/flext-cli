# AUTO-GENERATED FILE — DO NOT EDIT MANUALLY.
# Regenerate with: make gen
#
"""FLEXT CLI Test Helpers - Factories and utilities for test code reduction.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TYPE_CHECKING

from flext_core.lazy import install_lazy_exports

if TYPE_CHECKING:
    from tests.helpers._impl import *

_LAZY_IMPORTS: Mapping[str, str | Sequence[str]] = {
    "FlextCliTestHelpers": "tests.helpers._impl",
    "_impl": "tests.helpers._impl",
}


install_lazy_exports(__name__, globals(), _LAZY_IMPORTS)

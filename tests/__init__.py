"""Tests package initialization.

Ensures that relative imports like `from tests.test_mocks import ...` work
consistently under pytest by treating `tests` as a package.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

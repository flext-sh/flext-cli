"""Unit-test suite hooks for FLEXT CLI.

The prompt fixtures live in ``tests.fixtures.prompts``, registered by the root
conftest. This conftest owns only the suite hooks.

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

import pytest

from flext_cli import FlextCliSettings


def pytest_runtest_setup(item: pytest.Item) -> None:
    """Reset CLI settings before each test item."""
    _ = item
    FlextCliSettings.reset_for_testing()


def pytest_runtest_teardown(item: pytest.Item, nextitem: pytest.Item | None) -> None:
    """Reset CLI settings after each test item."""
    _ = item, nextitem
    FlextCliSettings.reset_for_testing()

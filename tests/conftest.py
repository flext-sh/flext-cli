"""FLEXT CLI Test Configuration.

Registers the project fixture plugins and owns the suite-wide collection hook.
Fixture implementations live exclusively in ``tests/fixtures/``.

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

from collections.abc import Sequence

import pytest

pytest_plugins = ["tests.fixtures.logging_policy", "tests.fixtures.prompts"]


def pytest_collection_modifyitems(
    config: pytest.Config,
    items: Sequence[pytest.Item],
) -> None:
    """Modify test collection to add markers based on test names."""
    _ = config
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)

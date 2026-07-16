"""FLEXT CLI Test Configuration."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests import p, t



def pytest_collection_modifyitems(
    config: pytest.Config, items: t.SequenceOf[pytest.Item]
) -> None:
    """Modify test collection to add markers based on test names."""
    _ = config
    for item in items:
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        elif "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        if "docker" in item.name:
            item.add_marker(pytest.mark.docker)
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)

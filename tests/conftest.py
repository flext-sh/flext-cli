"""FLEXT CLI Test Configuration."""

from __future__ import annotations

from collections.abc import Callable, Sequence

import pytest

from flext_cli import FlextCliSettings


@pytest.fixture
def cli_settings(
    settings_factory: Callable[..., FlextCliSettings],
) -> FlextCliSettings:
    """Provide clean FlextCliSettings for tests."""
    return settings_factory(FlextCliSettings)


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest markers for the test suite."""
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")
    config.addinivalue_line("markers", "slow: marks tests as slow running")
    config.addinivalue_line("markers", "docker: marks tests that require Docker")
    config.addinivalue_line(
        "markers",
        "real_functionality: marks tests that test real functionality",
    )


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
        if "docker" in item.name:
            item.add_marker(pytest.mark.docker)
        if "slow" in item.name:
            item.add_marker(pytest.mark.slow)

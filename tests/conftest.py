"""Minimal pytest configuration - avoiding broken imports.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import click
import pytest
from rich.console import Console


# =============================================================================
# PYTEST CONFIGURATION - MINIMAL SETUP
# =============================================================================


def pytest_configure(config: pytest.Config) -> None:
    """Configure pytest with custom markers and settings."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
    config.addinivalue_line("markers", "unit: marks tests as unit tests")


# =============================================================================
# BASIC FIXTURES - MINIMAL DEPENDENCIES
# =============================================================================


@pytest.fixture
def temp_dir() -> Path:
    """Provide temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp:
        yield Path(temp)


@pytest.fixture
def console() -> Console:
    """Provide Rich console for testing."""
    return Console(file=None, width=80)


@pytest.fixture
def cli_runner() -> click.testing.CliRunner:
    """Provide Click CLI runner for testing."""
    return click.testing.CliRunner()

"""Logging-policy fixtures for FLEXT CLI tests.

Copyright (c) 2026 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from tests import u

if TYPE_CHECKING:
    from collections.abc import Iterator


@pytest.fixture
def preserve_logging() -> Iterator[None]:
    """Keep command invocations from replacing another app's logging policy.

    Yields:
        Control to the test while the original logging policy is retained.

    """
    original_settings = u.logging_settings()
    original_options = u.logging_options()
    try:
        yield
    finally:
        u.configure_structlog(
            settings=original_options,
            runtime_settings=original_settings,
        )

"""FLEXT CLI Core Bridge - Safe imports from flext-core.

Safe re-exports from flext-core with fallbacks when not available.
This prevents breaking the entire CLI when flext-core has issues.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import TypeVar, object

T = TypeVar("T")

# Safe imports from flext-core with fallbacks - handle all issues gracefully
try:
    from flext_core import FlextModels.Entity, FlextModels.EntityId, FlextResult

    FLEXT_CORE_AVAILABLE = True
except (ImportError, AttributeError, SyntaxError) as e:
    FLEXT_CORE_AVAILABLE = False
    # Log the issue but continue with fallbacks
    import logging

    logging.getLogger(__name__).debug(f"flext-core not available: {e}")

    # Minimal FlextResult implementation when flext-core is not available
    class FlextResult:
        def __init__(self, value: object = None, error: str | None = None) -> None:
            self._value = value
            self._error = error
            self._success = error is None

        @property
        def value(self) -> object:
            return self._value

        @property
        def error(self) -> str | None:
            return self._error

        @property
        def is_success(self) -> bool:
            return self._success

        @property
        def is_failure(self) -> bool:
            return not self._success

        @classmethod
        def ok(cls, value: object = None) -> FlextResult:
            return cls(value=value, error=None)

        @classmethod
        def fail(cls, error: str) -> FlextResult:
            return cls(value=None, error=error)

    # Minimal FlextModels.Entity when flext-core is not available
    class FlextModels.Entity:
        def __init__(self, **kwargs) -> None:
            for key, value in kwargs.items():
                setattr(self, key, value)

        def validate_business_rules(self) -> FlextResult:
            return FlextResult.ok(None)

    # Minimal FlextModels.EntityId when flext-core is not available
    class FlextModels.EntityId:
        def __init__(self, id_value: str) -> None:
            self._id = id_value

        def __str__(self) -> str:
            return self._id

        def __eq__(self, other: object) -> bool:
            if isinstance(other, FlextModels.EntityId):
                return self._id == other._id
            return self._id == str(other)


def FlextLogger(name: str):
    """Get logger - use flext-core if available, otherwise standard logging."""
    if FLEXT_CORE_AVAILABLE:
        try:
            from flext_core import FlextLogger

            return FlextLogger(name)
        except ImportError:
            pass

    # Fallback to standard logging
    import logging

    return logging.getLogger(name)


# Re-export what we have available
__all__ = [
    "FLEXT_CORE_AVAILABLE",
    "FlextModels.Entity",
    "FlextModels.EntityId",
    "FlextResult",
    "FlextLogger",
]

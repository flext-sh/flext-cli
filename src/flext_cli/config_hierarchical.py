"""Configuration hierarchy."""

from __future__ import annotations

from flext_core import FlextResult


def create_default_hierarchy(
    *,
    config_path: str | None = None,
) -> FlextResult[dict[str, object]]:
    """Create a minimal configuration hierarchy for tests.

    The optional ``config_path`` is unused in this shim but kept for API
    compatibility with the actual implementation.
    """
    try:
        _ = config_path  # unused by design in this facade
        # Minimal defaults; could optionally load from `config_path`
        config: dict[str, object] = {
            "profile": "default",
            "debug": False,
            "output_format": "table",
        }
        return FlextResult.ok(config)
    except (OSError, PermissionError) as e:
        # Handle file system access errors if config_path is used in future
        return FlextResult.fail(f"Configuration file access error: {e}")
    except (ValueError, TypeError) as e:
        # Handle data validation or type conversion errors
        return FlextResult.fail(f"Configuration data error: {e}")
    except Exception as e:
        # Fallback for truly unexpected errors
        return FlextResult.fail(f"Unexpected configuration error: {e}")

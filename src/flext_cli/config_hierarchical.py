"""Simple configuration hierarchy facade for tests.

This provides a minimal `create_default_hierarchy` function returning a
`FlextResult[dict[str, object]]`, used by mixins and tests. In the real
system this would merge files, env vars and defaults.
"""

from __future__ import annotations

from flext_core import FlextResult


def create_default_hierarchy(
    *,
    config_path: str | None = None,
) -> FlextResult[dict[str, object]]:
    """Create a minimal configuration hierarchy for tests.

    The optional ``config_path`` is unused in this shim but kept for API
    compatibility with the real implementation.
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
    except Exception as e:  # noqa: BLE001
        return FlextResult.fail(str(e))

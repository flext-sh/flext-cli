"""Pipeline execution constants."""

from __future__ import annotations

from typing import Final

from flext_core import t


class FlextCliConstantsPipeline:
    """Pipeline execution constants namespace."""

    class Pipeline:
        """DAG pipeline engine defaults."""

        DEFAULT_FAIL_FAST: Final[bool] = True
        DEFAULT_RETRY: Final[t.RetryCount] = 0
        MAX_RETRY: Final[t.RetryCount] = 3
        STAGE_TIMEOUT_SECONDS: Final[int] = 600


__all__ = ["FlextCliConstantsPipeline"]

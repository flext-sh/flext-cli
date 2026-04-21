"""Pipeline execution constants."""

from __future__ import annotations

from typing import ClassVar, Final

from flext_core import t

from flext_cli import FlextCliConstantsEnums


class FlextCliConstantsPipeline:
    """Flat pipeline execution constants namespace."""

    PIPELINE_DEFAULT_FAIL_FAST: Final[bool] = True
    PIPELINE_DEFAULT_RETRY: Final[t.RetryCount] = 0
    PIPELINE_MAX_RETRY: Final[t.RetryCount] = 3

    PIPELINE_STATUS_VALUES: ClassVar[frozenset[str]] = frozenset(
        status.value for status in FlextCliConstantsEnums.PipelineStageStatus
    )


__all__: list[str] = ["FlextCliConstantsPipeline"]

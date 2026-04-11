"""Pipeline execution constants."""

from __future__ import annotations

from typing import ClassVar, Final

from flext_cli._constants.enums import FlextCliConstantsEnums
from flext_core import t


class FlextCliConstantsPipeline:
    """Flat pipeline execution constants namespace."""

    PIPELINE_DEFAULT_FAIL_FAST: Final[bool] = True
    PIPELINE_DEFAULT_RETRY: Final[t.RetryCount] = 0
    PIPELINE_MAX_RETRY: Final[t.RetryCount] = 3

    PIPELINE_STATUS_OK: Final[FlextCliConstantsEnums.PipelineStageStatus] = (
        FlextCliConstantsEnums.PipelineStageStatus.OK
    )
    PIPELINE_STATUS_SKIPPED: Final[FlextCliConstantsEnums.PipelineStageStatus] = (
        FlextCliConstantsEnums.PipelineStageStatus.SKIPPED
    )
    PIPELINE_STATUS_FAILED: Final[FlextCliConstantsEnums.PipelineStageStatus] = (
        FlextCliConstantsEnums.PipelineStageStatus.FAILED
    )
    PIPELINE_STATUS_VALUES: ClassVar[frozenset[str]] = frozenset({
        FlextCliConstantsEnums.PipelineStageStatus.OK.value,
        FlextCliConstantsEnums.PipelineStageStatus.SKIPPED.value,
        FlextCliConstantsEnums.PipelineStageStatus.FAILED.value,
    })


__all__ = ["FlextCliConstantsPipeline"]

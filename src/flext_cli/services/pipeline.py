"""DSL service for DAG pipeline execution helpers."""

from __future__ import annotations

from flext_cli import FlextCliServiceBase, FlextCliUtilitiesPipeline, t


class FlextCliPipeline(FlextCliServiceBase, FlextCliUtilitiesPipeline):
    """Expose pipeline execution helpers through ``cli`` and ``FlextCli``."""

    pass


__all__: t.MutableSequenceOf[str] = ["FlextCliPipeline"]

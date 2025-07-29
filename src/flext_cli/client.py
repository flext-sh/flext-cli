"""Stub for client module.

This is a stub module for backward compatibility.
Service-related functionality has been moved to examples.
"""

from __future__ import annotations


class PipelineConfig:
    """Pipeline configuration with typed attributes."""

    def __init__(self) -> None:
        """Initialize pipeline configuration."""
        self.tap: str = ""
        self.target: str = ""
        self.transform: str | None = None
        self.schedule: str | None = None
        self.config: dict[str, object] | None = None


class FlextApiClient:
    """Stub class for FlextApiClient."""

    def __init__(self, *args: object, **kwargs: object) -> None:
        """Initialize stub client."""


class Pipeline:
    """Stub class for Pipeline."""

    def __init__(self, *args: object, **kwargs: object) -> None:  # noqa: ARG002
        """Initialize stub pipeline."""
        self.name: str = "stub-pipeline"
        self.id: str = "stub-id"
        self.status: str = "stub-status"
        self.created_at: str = "2025-01-01T00:00:00Z"
        self.updated_at: str = "2025-01-01T00:00:00Z"
        self.config: PipelineConfig | None = None


class PipelineList:
    """Stub class for PipelineList."""

    def __init__(self, *args: object, **kwargs: object) -> None:  # noqa: ARG002
        """Initialize stub pipeline list."""
        self.pipelines: list[Pipeline] = []
        self.total: int = 0
        self.page: int = 1
        self.page_size: int = 10

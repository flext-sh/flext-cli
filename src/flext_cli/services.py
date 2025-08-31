"""FLEXT CLI Services - Advanced CLI services using FlextServices unified patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, ClassVar

from flext_core import FlextResult, FlextServices
from pydantic import Field

from flext_cli.models import FlextCliModels


class FlextCliServices(FlextServices):
    """Advanced CLI services using FlextServices unified patterns.

    Leverages FlextServices.ServiceProcessor, ServiceRegistry, and ServiceOrchestrator
    for enterprise-grade CLI service architecture with Python 3.13+ features.
    """

    # Reference to flext-core services for strict inheritance
    Core: ClassVar = FlextServices

    class CliCommandProcessor(FlextServices.ServiceProcessor[str, FlextCliModels.CliCommand, str]):
        """CLI command processor using FlextServices.ServiceProcessor pattern."""

        timeout_seconds: int = Field(default=30, description="Command execution timeout")
        max_retries: int = Field(default=3, description="Maximum retry attempts")

        def process(self, request: str) -> FlextResult[FlextCliModels.CliCommand]:
            """Process command string into CLI command domain object."""
            try:
                # Create CLI command using our advanced models
                command = FlextCliModels.CliCommand(command_line=request)

                # Start command execution using domain method
                start_result = command.start_execution()
                if start_result.is_failure:
                    return FlextResult[FlextCliModels.CliCommand].fail(
                        f"Failed to start command execution: {start_result.error}"
                    )

                # Validate business rules
                validation_result = command.validate_business_rules()
                if validation_result.is_failure:
                    return FlextResult[FlextCliModels.CliCommand].fail(
                        f"Command validation failed: {validation_result.error}"
                    )

                return FlextResult[FlextCliModels.CliCommand].ok(command)

            except Exception as e:
                return FlextResult[FlextCliModels.CliCommand].fail(f"Command processing error: {e}")

        def build(self, domain: FlextCliModels.CliCommand, *, correlation_id: str) -> str:
            """Build command execution result string."""
            status_icon = "✓" if domain.is_successful else "✗"
            return f"{status_icon} Command: {domain.command_line} | Status: {domain.status} | ID: {correlation_id}"

    class CliSessionProcessor(FlextServices.ServiceProcessor[dict[str, object], FlextCliModels.CliSession, dict[str, object]]):
        """CLI session processor using FlextServices.ServiceProcessor pattern."""

        max_commands: int = Field(default=1000, description="Maximum commands per session")
        auto_end_timeout: int = Field(default=3600, description="Auto-end session timeout in seconds")

        def process(self, request: dict[str, object]) -> FlextResult[FlextCliModels.CliSession]:
            """Process session creation request."""
            try:
                # Create CLI session using our advanced models
                user_id = request.get("user_id")
                session = FlextCliModels.CliSession(
                    user_id=str(user_id) if user_id is not None else None
                )

                # Validate business rules
                validation_result = session.validate_business_rules()
                if validation_result.is_failure:
                    return FlextResult[FlextCliModels.CliSession].fail(
                        f"Session validation failed: {validation_result.error}"
                    )

                return FlextResult[FlextCliModels.CliSession].ok(session)

            except Exception as e:
                return FlextResult[FlextCliModels.CliSession].fail(f"Session processing error: {e}")

        def build(self, domain: FlextCliModels.CliSession, *, correlation_id: str) -> dict[str, object]:
            """Build session information dictionary."""
            return {
                "session_id": str(domain.session_id),
                "start_time": domain.start_time.isoformat(),
                "end_time": domain.end_time.isoformat() if domain.end_time else None,
                "duration_seconds": domain.duration_seconds,
                "commands_count": len(domain.commands),
                "user_id": domain.user_id,
                "correlation_id": correlation_id,
                "is_active": domain.end_time is None
            }

    class CliConfigProcessor(FlextServices.ServiceProcessor[dict[str, object], FlextCliModels.CliConfig, dict[str, object]]):
        """CLI configuration processor using FlextServices.ServiceProcessor pattern."""

        def process(self, request: dict[str, object]) -> FlextResult[FlextCliModels.CliConfig]:
            """Process configuration request."""
            try:
                # Create CLI config using our advanced models with validation
                config = FlextCliModels.CliConfig(**request)
                return FlextResult[FlextCliModels.CliConfig].ok(config)

            except Exception as e:
                return FlextResult[FlextCliModels.CliConfig].fail(f"Config processing error: {e}")

        def build(self, domain: FlextCliModels.CliConfig, *, correlation_id: str) -> dict[str, object]:
            """Build configuration dictionary."""
            return {
                "profile": domain.profile,
                "output_format": domain.output_format,
                "debug_mode": domain.debug_mode,
                "timeout_seconds": domain.timeout_seconds,
                "correlation_id": correlation_id,
                "updated_at": datetime.now(UTC).isoformat()
            }

    # Service registry instance using FlextServices.ServiceRegistry
    registry = FlextServices.ServiceRegistry()

    # Service orchestrator instance using FlextServices.ServiceOrchestrator
    orchestrator = FlextServices.ServiceOrchestrator()

    # Service metrics instance using FlextServices.ServiceMetrics
    metrics = FlextServices.ServiceMetrics()

    @classmethod
    def create_command_processor(cls, **config: object) -> CliCommandProcessor:
        """Factory method to create CLI command processor."""
        processor = cls.CliCommandProcessor(**config)
        # cls.registry.register("cli_command_processor", processor)  # TODO: Fix registry API
        return processor

    @classmethod
    def create_session_processor(cls, **config: object) -> CliSessionProcessor:
        """Factory method to create CLI session processor."""
        processor = cls.CliSessionProcessor(**config)
        # cls.registry.register("cli_session_processor", processor)  # TODO: Fix registry API
        return processor

    @classmethod
    def create_config_processor(cls, **config: object) -> CliConfigProcessor:
        """Factory method to create CLI config processor."""
        processor = cls.CliConfigProcessor(**config)
        # cls.registry.register("cli_config_processor", processor)  # TODO: Fix registry API
        return processor

    @classmethod
    def process_command(cls, command: str, timeout: int = 30) -> FlextResult[FlextCliModels.CliCommand]:
        """High-level method to process CLI command."""
        processor = cls.create_command_processor(timeout_seconds=timeout)

        # TODO: Fix metrics API
        # cls.metrics.track_service_call("process_command", {
        #     "command_length": len(command),
        #     "timeout": timeout,
        #     "timestamp": datetime.now(UTC).isoformat()
        # })

        return processor.process(command)

    @classmethod
    def create_session(cls, user_id: str | None = None) -> FlextResult[FlextCliModels.CliSession]:
        """High-level method to create CLI session."""
        processor = cls.create_session_processor()

        # TODO: Fix metrics API
        # cls.metrics.track_service_call("create_session", {
        #     "user_id": user_id,
        #     "timestamp": datetime.now(UTC).isoformat()
        # })

        return processor.process({"user_id": user_id})

    @classmethod
    def validate_config(cls, config_data: dict[str, object]) -> FlextResult[FlextCliModels.CliConfig]:
        """High-level method to validate configuration."""
        processor = cls.create_config_processor()

        # TODO: Fix metrics API
        # cls.metrics.track_service_call("validate_config", {
        #     "config_keys": list(config_data.keys()),
        #     "timestamp": datetime.now(UTC).isoformat()
        # })

        return processor.process(config_data)


# =============================================================================
# EXPORTS - Single unique class following user requirements
# =============================================================================

__all__ = [
    "FlextCliServices",
]

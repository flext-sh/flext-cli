"""FLEXT CLI Services - Advanced CLI services using FlextServices unified patterns.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import time
from datetime import UTC, datetime
from typing import ClassVar

from flext_core import FlextResult, FlextServices
from pydantic import Field

from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels


class FlextCliServices(FlextServices):
    """Advanced CLI services using FlextServices unified patterns.

    Leverages FlextServices.ServiceProcessor, ServiceRegistry, and ServiceOrchestrator
    for enterprise-grade CLI service architecture with Python 3.13+ features.
    """

    # Reference to flext-core services for strict inheritance
    Core: ClassVar[type[FlextServices]] = FlextServices

    class CliCommandProcessor(
        FlextServices.ServiceProcessor[str, FlextCliModels.CliCommand, str]
    ):
        """CLI command processor using FlextServices.ServiceProcessor pattern."""

        timeout_seconds: int = Field(
            default=FlextCliConstants.DEFAULT_COMMAND_TIMEOUT,
            description="Command execution timeout",
        )
        max_retries: int = Field(
            default=FlextCliConstants.DEFAULT_RETRIES,
            description="Maximum retry attempts",
        )

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

            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[FlextCliModels.CliCommand].fail(
                    f"Command processing error: {e}"
                )

        def build(
            self, domain: FlextCliModels.CliCommand, *, correlation_id: str
        ) -> str:
            """Build command execution result string."""
            status_icon = "✓" if bool(getattr(domain, "is_successful", False)) else "✗"
            return f"{status_icon} Command: {domain.command_line} | Status: {domain.status} | ID: {correlation_id}"

    class CliSessionProcessor(
        FlextServices.ServiceProcessor[
            dict[str, object], FlextCliModels.CliSession, dict[str, object]
        ]
    ):
        """CLI session processor using FlextServices.ServiceProcessor pattern."""

        max_commands: int = Field(
            default=FlextCliConstants.MAX_HISTORY_SIZE,
            description="Maximum commands per session",
        )
        auto_end_timeout: int = Field(
            default=FlextCliConstants.MAX_TIMEOUT_SECONDS,
            description="Auto-end session timeout in seconds",
        )

        def process(
            self, request: dict[str, object]
        ) -> FlextResult[FlextCliModels.CliSession]:
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

            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[FlextCliModels.CliSession].fail(
                    f"Session processing error: {e}"
                )

        def build(
            self, domain: FlextCliModels.CliSession, *, correlation_id: str
        ) -> dict[str, object]:
            """Build session information dictionary."""
            return {
                "session_id": str(domain.session_id),
                "start_time": domain.start_time.isoformat(),
                "end_time": domain.end_time.isoformat() if domain.end_time else None,
                "duration_seconds": domain.duration_seconds,
                "commands_count": len(domain.commands),
                "user_id": domain.user_id,
                "correlation_id": correlation_id,
                "is_active": domain.end_time is None,
            }

    class CliConfigProcessor(
        FlextServices.ServiceProcessor[
            dict[str, object], FlextCliModels.CliConfig, dict[str, object]
        ]
    ):
        """CLI configuration processor using FlextServices.ServiceProcessor pattern."""

        def process(
            self, request: dict[str, object]
        ) -> FlextResult[FlextCliModels.CliConfig]:
            """Process configuration request."""
            try:
                # Create CLI config using pydantic model_validate for type safety
                config = FlextCliModels.CliConfig.model_validate(request)
                return FlextResult[FlextCliModels.CliConfig].ok(config)

            except (RuntimeError, ValueError, TypeError) as e:
                return FlextResult[FlextCliModels.CliConfig].fail(
                    f"Config processing error: {e}"
                )

        def build(
            self, domain: FlextCliModels.CliConfig, *, correlation_id: str
        ) -> dict[str, object]:
            """Build configuration dictionary."""
            return {
                "profile": domain.profile,
                "output_format": domain.output_format,
                "debug_mode": domain.debug_mode,
                "timeout_seconds": domain.timeout_seconds,
                "correlation_id": correlation_id,
                "updated_at": datetime.now(UTC).isoformat(),
            }

    # Service registry instance using FlextServices.ServiceRegistry
    registry = FlextServices.ServiceRegistry()

    # Service orchestrator instance using FlextServices.ServiceOrchestrator
    orchestrator = FlextServices.ServiceOrchestrator()

    # Service metrics instance using FlextServices.ServiceMetrics
    metrics = FlextServices.ServiceMetrics()

    @classmethod
    def create_command_processor(
        cls,
        *,
        timeout_seconds: int | None = None,
        max_retries: int | None = None,
        dependencies: dict[str, object] | None = None,
        **config: object,
    ) -> CliCommandProcessor:
        """Advanced factory method with dependency injection for command processor.

        Args:
            timeout_seconds: Command execution timeout (injected)
            max_retries: Maximum retry attempts (injected)
            dependencies: External dependencies to inject
            **config: Additional configuration

        Returns:
            Configured CliCommandProcessor with dependencies injected

        """
        # Advanced dependency injection with defaults
        resolved_config = {
            "timeout_seconds": timeout_seconds
            or FlextCliConstants.DEFAULT_COMMAND_TIMEOUT,
            "max_retries": max_retries or FlextCliConstants.DEFAULT_RETRIES,
            **config,
        }

        # Inject external dependencies if provided
        if dependencies:
            resolved_config.update(dependencies)

        processor = cls.CliCommandProcessor(**resolved_config)

        # Register with enhanced metadata for advanced service discovery
        cls.registry.register(
            {
                "name": "cli_command_processor",
                "type": "processor",
                "version": "1.0",
                "capabilities": [
                    "command_execution",
                    "timeout_handling",
                    "retry_logic",
                ],
                "dependencies": list(dependencies.keys()) if dependencies else [],
                "config": resolved_config,
            }
        )
        return processor

    @classmethod
    def create_session_processor(
        cls,
        *,
        enable_tracking: bool = True,
        max_sessions: int | None = None,
        dependencies: dict[str, object] | None = None,
        **config: object,
    ) -> CliSessionProcessor:
        """Advanced factory method with dependency injection for session processor.

        Args:
            enable_tracking: Enable session tracking
            max_sessions: Maximum concurrent sessions
            dependencies: External dependencies to inject
            **config: Additional configuration

        """
        resolved_config = {
            "enable_tracking": enable_tracking,
            "max_sessions": max_sessions or FlextCliConstants.MAX_COMMANDS_PER_SESSION,
            **config,
        }

        if dependencies:
            resolved_config.update(dependencies)

        processor = cls.CliSessionProcessor(**resolved_config)

        cls.registry.register(
            {
                "name": "cli_session_processor",
                "type": "processor",
                "version": "1.0",
                "capabilities": [
                    "session_management",
                    "concurrent_sessions",
                    "tracking",
                ],
                "dependencies": list(dependencies.keys()) if dependencies else [],
                "config": resolved_config,
            }
        )
        return processor

    @classmethod
    def create_config_processor(
        cls,
        *,
        config_validation: bool = True,
        auto_reload: bool = False,
        dependencies: dict[str, object] | None = None,
        **config: object,
    ) -> CliConfigProcessor:
        """Advanced factory method with dependency injection for config processor.

        Args:
            config_validation: Enable configuration validation
            auto_reload: Enable automatic configuration reloading
            dependencies: External dependencies to inject
            **config: Additional configuration

        """
        resolved_config = {
            "config_validation": config_validation,
            "auto_reload": auto_reload,
            **config,
        }

        if dependencies:
            resolved_config.update(dependencies)

        processor = cls.CliConfigProcessor(**resolved_config)

        cls.registry.register(
            {
                "name": "cli_config_processor",
                "type": "processor",
                "version": "1.0",
                "capabilities": ["config_processing", "validation", "hot_reload"],
                "dependencies": list(dependencies.keys()) if dependencies else [],
                "config": resolved_config,
            }
        )
        return processor

    # =========================================================================
    # ADVANCED FACTORY PATTERNS WITH BUILDER AND REGISTRY
    # =========================================================================

    class ServiceBuilder:
        """Advanced builder pattern for complex service configuration.

        Enables fluent interface for building services with complex dependencies
        and configuration. Follows builder pattern from Gang of Four.
        """

        def __init__(self) -> None:
            self._config: dict[str, object] = {}
            self._dependencies: dict[str, object] = {}
            self._capabilities: list[str] = []

        def with_timeout(self, seconds: int) -> FlextCliServices.ServiceBuilder:
            """Configure timeout settings (fluent interface)."""
            self._config["timeout_seconds"] = seconds
            return self

        def with_retries(self, count: int) -> FlextCliServices.ServiceBuilder:
            """Configure retry settings (fluent interface)."""
            self._config["max_retries"] = count
            return self

        def with_dependency(
            self, name: str, service: object
        ) -> FlextCliServices.ServiceBuilder:
            """Inject external dependency (fluent interface)."""
            self._dependencies[name] = service
            return self

        def with_capability(self, capability: str) -> FlextCliServices.ServiceBuilder:
            """Add service capability (fluent interface)."""
            self._capabilities.append(capability)
            return self

        def build_command_processor(self) -> FlextCliServices.CliCommandProcessor:
            """Build command processor with accumulated configuration."""
            from typing import cast
            timeout_val = self._config.get("timeout_seconds")
            max_retries_val = self._config.get("max_retries")
            return FlextCliServices.create_command_processor(
                dependencies=self._dependencies,
                timeout_seconds=int(cast("int | str", timeout_val)) if timeout_val is not None else None,
                max_retries=int(cast("int | str", max_retries_val)) if max_retries_val is not None else None,
            )

        def build_session_processor(self) -> FlextCliServices.CliSessionProcessor:
            """Build session processor with accumulated configuration."""
            from typing import cast
            max_sessions_val = self._config.get("max_sessions")
            return FlextCliServices.create_session_processor(
                dependencies=self._dependencies,
                enable_tracking=bool(self._config.get("enable_tracking", True)),
                max_sessions=int(cast("int | str", max_sessions_val)) if max_sessions_val is not None else None,
            )

    @classmethod
    def builder(cls) -> ServiceBuilder:
        r"""Create service builder for fluent configuration.

        Example:
            processor = FlextCliServices.builder()\\
                .with_timeout(60)\\
                .with_retries(3)\\
                .with_dependency("logger", custom_logger)\\
                .build_command_processor()

        """
        return cls.ServiceBuilder()

    class ServiceFactory:
        """Advanced factory registry with service discovery and lifecycle.

        Implements factory method pattern with service registry for
        dependency injection and service discovery capabilities.
        """

        _service_types: ClassVar[dict[str, str]] = {
            "command": "CliCommandProcessor",
            "session": "CliSessionProcessor",
            "config": "CliConfigProcessor",
        }

        @classmethod
        def create_service(cls, service_type: str, **kwargs: object) -> object:
            """Create service by type with factory method pattern.

            Args:
                service_type: Type of service ("command", "session", "config")
                **kwargs: Service-specific configuration

            Returns:
                Configured service instance

            Raises:
                ValueError: If service type is unknown

            """
            match service_type:
                case "command":
                    return FlextCliServices.create_command_processor(**kwargs)  # type: ignore[arg-type]
                case "session":
                    return FlextCliServices.create_session_processor(**kwargs)  # type: ignore[arg-type]
                case "config":
                    return FlextCliServices.create_config_processor(**kwargs)  # type: ignore[arg-type]
                case _:
                    valid_types = ", ".join(cls._service_types.keys())
                    msg = f"Unknown service type: {service_type}. Valid types: {valid_types}"
                    raise ValueError(msg)

        @classmethod
        def get_service_capabilities(cls, service_type: str) -> list[str]:
            """Get capabilities for a service type."""
            # This would typically query the registry, simplified for demo
            capabilities_map = {
                "command": ["command_execution", "timeout_handling", "retry_logic"],
                "session": ["session_management", "concurrent_sessions", "tracking"],
                "config": ["config_processing", "validation", "hot_reload"],
            }
            return capabilities_map.get(service_type, [])

    @classmethod
    def factory(cls) -> ServiceFactory:
        """Get service factory for advanced service creation."""
        return cls.ServiceFactory()

    @classmethod
    def process_command(
        cls, command: str, timeout: int = FlextCliConstants.DEFAULT_COMMAND_TIMEOUT
    ) -> FlextResult[FlextCliModels.CliCommand]:
        """High-level method to process CLI command."""
        processor = cls.create_command_processor(timeout_seconds=timeout)
        start = time.perf_counter()
        result = processor.process(command)
        duration_ms = (
            time.perf_counter() - start
        ) * FlextCliConstants.MILLISECONDS_PER_SECOND
        cls.metrics.track_service_call(
            "FlextCliServices", "process_command", duration_ms
        )
        return result

    @classmethod
    def create_session(
        cls, user_id: str | None = None
    ) -> FlextResult[FlextCliModels.CliSession]:
        """High-level method to create CLI session."""
        processor = cls.create_session_processor()
        start = time.perf_counter()
        result = processor.process({"user_id": user_id})
        duration_ms = (
            time.perf_counter() - start
        ) * FlextCliConstants.MILLISECONDS_PER_SECOND
        cls.metrics.track_service_call(
            "FlextCliServices", "create_session", duration_ms
        )
        return result

    @classmethod
    def validate_config(
        cls, config_data: dict[str, object]
    ) -> FlextResult[FlextCliModels.CliConfig]:
        """High-level method to validate configuration."""
        processor = cls.create_config_processor()
        start = time.perf_counter()
        result = processor.process(config_data)
        duration_ms = (
            time.perf_counter() - start
        ) * FlextCliConstants.MILLISECONDS_PER_SECOND
        cls.metrics.track_service_call(
            "FlextCliServices", "validate_config", duration_ms
        )
        return result


# =============================================================================
# EXPORTS - Single unique class following user requirements
# =============================================================================

__all__ = [
    "FlextCliServices",
]

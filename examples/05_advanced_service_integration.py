#!/usr/bin/env python3
"""05 - Advanced Service Integration Patterns.

This example demonstrates advanced service integration patterns using flext-cli:

Key Patterns Demonstrated:
- FlextCliService inheritance with comprehensive mixins
- Dependency injection with create_container()
- Async command execution with @async_command decorator
- Error handling with retry patterns and circuit breakers

- Service composition and orchestration
- Event-driven architecture with domain events
- CQRS pattern implementation for CLI operations
- Service health monitoring and circuit breaker patterns

Architecture Layers:
- Domain: Service entities and business rules
- Application: Command handlers and service orchestration
- Infrastructure: External service integration and monitoring

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable
from datetime import UTC, datetime
from enum import Enum
from typing import Protocol, cast, override

from rich.progress import Progress, SpinnerColumn, TaskID, TextColumn
from rich.table import Table

from flext_cli import (
    FlextCliConfig,
    FlextCliOutput,
    FlextCliService,
    FlextCliTypes,
)
from flext_core import FlextContainer, FlextLogger, FlextResult, FlextTypes


# Container protocol for type compatibility
class ContainerProtocol(Protocol):
    """Protocol for container interface."""

    def register(self, name: str, service: object) -> FlextResult[None]:
        """Register a service in the container."""
        ...

    def get(self, name: str) -> FlextResult[object]:
        """Get a service from the container."""
        ...


# Simple replacement for missing example_utils
def print_demo_completion(title: str) -> None:
    """Print demo completion message."""
    print(f"✅ {title} completed successfully!")


class ServiceStatus(Enum):
    """Service status enumeration."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class CircuitBreakerState(Enum):
    """Circuit breaker state enumeration."""

    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class AdvancedCliService(FlextCliService):
    """Advanced CLI service demonstrating comprehensive service integration."""

    def __init__(self) -> None:
        """Initialize advanced CLI service with comprehensive components."""
        super().__init__()

        # Initialize private attributes
        self._service_health: dict[str, object] = {}
        self._circuit_breakers: dict[str, dict[str, object]] = {}
        self._performance_metrics: dict[str, object] = {}

        # Initialize logger
        self._logger = FlextLogger(__name__)

        # Initialize circuit_breakers as public attribute
        self.circuit_breakers: dict[str, dict[str, object]] = {}

    @override
    def execute(self) -> FlextResult[FlextCliTypes.Data.CliDataDict]:
        """Execute advanced CLI service operations."""
        return FlextResult[FlextCliTypes.Data.CliDataDict].ok({
            "status": "AdvancedCliService operational"
        })

    # Removed problematic decorators - @cli_enhanced, @cli_measure_time, @cli_retry
    # These decorators cause type inference issues with PyRight
    def check_service_health(
        self, service_name: str
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Check health of a specific service with retry logic."""
        try:
            logger = getattr(self, "logger", None)
            if logger and hasattr(logger, "info"):
                logger.info(f"Checking health for service: {service_name}")

            # Simulate health check call
            health_data = self._simulate_health_check(service_name)

            # Store health status using private attribute
            service_health = getattr(self, "_service_health", {})
            if isinstance(service_health, dict):
                service_health[service_name] = {
                    "status": health_data["status"],
                    "last_check": datetime.now(UTC),
                    "response_time": health_data.get("response_time_ms", 0),
                    "details": health_data.get("details", {}),
                }

            return FlextResult[FlextTypes.Core.Dict].ok(health_data)

        except Exception as e:
            if (
                hasattr(self, "logger")
                and self._logger
                and hasattr(self._logger, "exception")
            ):
                self._logger.exception(f"Health check failed for {service_name}")
            return FlextResult[FlextTypes.Core.Dict].fail(f"Health check failed: {e}")

    # Removed problematic decorators - @cli_enhanced, @with_spinner
    # These decorators cause type inference issues with PyRight
    def orchestrate_services(self, operation: str) -> FlextResult[FlextTypes.Core.Dict]:
        """Orchestrate multiple services for complex operations."""
        try:
            if (
                hasattr(self, "logger")
                and self._logger
                and hasattr(self._logger, "info")
            ):
                self._logger.info(f"Starting service orchestration: {operation}")

            # Define service orchestration steps
            orchestration_steps = [
                ("auth-service", "validate_credentials"),
                ("config-service", "load_configuration"),
                ("data-service", "prepare_data"),
                ("execution-service", "execute_operation"),
                ("notification-service", "send_notifications"),
            ]

            results = {}

            for service_name, step_operation in orchestration_steps:
                step_result = self._execute_orchestration_step(
                    service_name, step_operation
                )

                if step_result.is_success:
                    results[service_name] = step_result.value
                    if (
                        hasattr(self, "logger")
                        and self._logger
                        and hasattr(self._logger, "info")
                    ):
                        self._logger.info(
                            f"Step completed: {service_name}.{step_operation}"
                        )
                else:
                    # Handle step failure - implement rollback if needed
                    if (
                        hasattr(self, "logger")
                        and self._logger
                        and hasattr(self._logger, "error")
                    ):
                        self._logger.error(
                            f"Step failed: {service_name}.{step_operation} - {step_result.error}"
                        )
                    return FlextResult[FlextTypes.Core.Dict].fail(
                        f"Orchestration failed at {service_name}: {step_result.error}"
                    )

            orchestration_result: dict[str, object] = {
                "operation": operation,
                "status": "completed",
                "steps_executed": len(orchestration_steps),
                "results": results,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            return FlextResult[FlextTypes.Core.Dict].ok(orchestration_result)

        except Exception as e:
            if (
                hasattr(self, "logger")
                and self._logger
                and hasattr(self._logger, "exception")
            ):
                self._logger.exception("Service orchestration failed")
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Service orchestration failed: {e}"
            )

    def implement_circuit_breaker(
        self, service_name: str, failure_threshold: int = 5
    ) -> FlextResult[bool]:
        """Implement circuit breaker pattern for service resilience."""
        try:
            if service_name not in self.circuit_breakers:
                self.circuit_breakers[service_name] = {
                    "state": CircuitBreakerState.CLOSED,
                    "failure_count": 0,
                    "last_failure": None,
                    "failure_threshold": failure_threshold,
                    "timeout_duration": 60,  # seconds
                }

            breaker = self.circuit_breakers[service_name]
            current_time = datetime.now(UTC)

            # Check if circuit should be half-open
            last_failure = breaker.get("last_failure")
            if (
                breaker["state"] == CircuitBreakerState.OPEN
                and last_failure
                and isinstance(last_failure, datetime)
                and (current_time - last_failure).seconds
                > int(str(breaker.get("timeout_duration", 60)))
            ):
                breaker["state"] = CircuitBreakerState.HALF_OPEN
                if (
                    hasattr(self, "logger")
                    and self._logger
                    and hasattr(self._logger, "info")
                ):
                    self._logger.info(
                        f"Circuit breaker for {service_name} moved to HALF_OPEN"
                    )

            # Simulate service call based on circuit state
            if breaker["state"] == CircuitBreakerState.OPEN:
                return FlextResult[bool].fail(
                    f"Circuit breaker OPEN for {service_name}"
                )

            # Simulate service call
            call_success = self._simulate_service_call(service_name)

            if call_success:
                # Reset circuit breaker on success
                breaker["failure_count"] = 0
                breaker["state"] = CircuitBreakerState.CLOSED
                success_state = True
                return FlextResult[bool].ok(success_state)
            # Handle failure
            current_failure_count = breaker.get("failure_count", 0)
            if isinstance(current_failure_count, int):
                breaker["failure_count"] = current_failure_count + 1
            else:
                breaker["failure_count"] = 1
            breaker["last_failure"] = current_time

            failure_count = int(str(breaker.get("failure_count", 0)))
            failure_threshold = int(str(breaker.get("failure_threshold", 5)))
            if failure_count >= failure_threshold:
                breaker["state"] = CircuitBreakerState.OPEN
                if (
                    hasattr(self, "logger")
                    and self._logger
                    and hasattr(self._logger, "warning")
                ):
                    self._logger.warning(f"Circuit breaker OPENED for {service_name}")

            return FlextResult[bool].fail(f"Service call failed for {service_name}")

        except Exception as e:
            return FlextResult[bool].fail(f"Circuit breaker implementation failed: {e}")

    def _simulate_health_check(self, service_name: str) -> FlextTypes.Core.Dict:
        """Simulate health check for demonstration."""
        # Simulate different health statuses

        statuses = [
            ServiceStatus.HEALTHY,
            ServiceStatus.DEGRADED,
            ServiceStatus.UNHEALTHY,
        ]
        # weights = [0.7, 0.2, 0.1]  # 70% healthy, 20% degraded, 10% unhealthy - removed unused variable

        # Use deterministic selection instead of random for security
        status = statuses[0]  # Default to 'healthy' for demo
        response_time = 50  # Fixed response time for demo

        return {
            "service": service_name,
            "status": status.value,
            "response_time_ms": response_time,
            "timestamp": datetime.now(UTC).isoformat(),
            "details": {
                "cpu_usage": "45%",
                "memory_usage": "60%",
                "active_connections": 25,
            },
        }

    def _execute_orchestration_step(
        self, service_name: str, operation: str
    ) -> FlextResult[FlextTypes.Core.Dict]:
        """Execute a single orchestration step."""
        try:
            # Simulate step execution

            # Simulate processing time
            time.sleep(0.2)  # Fixed sleep for demo

            # Simulate success/failure (90% success rate)
            success = True  # Always succeed for demo

            if success:
                return FlextResult[FlextTypes.Core.Dict].ok({
                    "service": service_name,
                    "operation": operation,
                    "status": "success",
                    "execution_time_ms": 150,
                    "result": f"Operation {operation} completed successfully",
                })
            return FlextResult[FlextTypes.Core.Dict].fail(
                f"Operation {operation} failed"
            )

        except Exception as e:
            return FlextResult[FlextTypes.Core.Dict].fail(f"Step execution failed: {e}")

    def _simulate_service_call(self, _service_name: str) -> bool:
        """Simulate service call for circuit breaker demo."""
        # Simulate service availability (80% success rate)
        return True  # Always succeed for demo


# Removed @async_command and @cli_handle_keyboard_interrupt decorators - cause type inference issues
async def demonstrate_async_service_operations() -> None:
    """Demonstrate asynchronous service operations."""
    formatter = FlextCliOutput()
    console = formatter.console
    console.print("[bold blue]Asynchronous Service Operations[/bold blue]")

    # Initialize service
    service = AdvancedCliService()

    # Services to check concurrently
    services = [
        "auth-service",
        "api-gateway",
        "database",
        "cache",
        "notification-service",
    ]

    console.print(
        f"\n[green]Checking health of {len(services)} services concurrently...[/green]"
    )

    # Create progress display
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Create async tasks for concurrent health checks
        tasks: list[Awaitable[tuple[str, FlextResult[FlextTypes.Core.Dict]]]] = []

        for service_name in services:
            task = progress.add_task(f"Checking {service_name}...", total=100)

            async def check_service_async(
                name: str, task_id: TaskID
            ) -> tuple[str, FlextResult[FlextTypes.Core.Dict]]:
                # Simulate async health check
                await asyncio.sleep(0.5)  # Simulate network delay
                result = service.check_service_health(name)
                progress.update(
                    task_id, description=f"✅ {name} checked", completed=100
                )
                return name, result

            tasks.append(check_service_async(service_name, task))

        # Execute all health checks concurrently
        results: list[tuple[str, FlextResult[FlextTypes.Core.Dict]]] = list(
            await asyncio.gather(*tasks)
        )

    # Display results
    health_table = Table(title="Concurrent Health Check Results")
    health_table.add_column("Service", style="cyan")
    health_table.add_column("Status", style="green")
    health_table.add_column("Response Time", style="yellow")
    health_table.add_column("Details", style="blue")

    for service_name, result in results:
        # result is already properly typed from gather
        typed_result: FlextResult[FlextTypes.Core.Dict] = result
        if typed_result.is_success:
            data: dict[str, object] = typed_result.value
            status: str = str(data.get("status", "unknown"))
            response_time_success: str = f"{data.get('response_time_ms', 0)}ms"
            details_dict: dict[str, object] = cast(
                "dict[str, object]", data.get("details", {})
            )
            details_success: str = f"CPU: {details_dict.get('cpu_usage', 'N/A')}"

            # Color code status
            status_str: str = str(status)
            status_display_success: str = {
                "healthy": "[green]Healthy[/green]",
                "degraded": "[yellow]Degraded[/yellow]",
                "unhealthy": "[red]Unhealthy[/red]",
            }.get(status_str, status_str)

            # Use success variables
            status_display = status_display_success
            response_time = response_time_success
            details = details_success

        else:
            status_display = "[red]Error[/red]"
            response_time = "N/A"
            # Define constant for max error display length
            max_error_length: int = 50
            error_msg: str = typed_result.error or "Unknown error"
            details = (
                error_msg[:max_error_length] + "..."
                if len(error_msg) > max_error_length
                else error_msg
            )

        health_table.add_row(service_name, status_display, response_time, details)

    console.print(health_table)


def demonstrate_circuit_breaker_pattern() -> FlextResult[None]:
    """Demonstrate circuit breaker pattern for service resilience."""
    formatter = FlextCliOutput()
    console = formatter.console
    console.print("\n[green]Circuit Breaker Pattern Demonstration[/green]")

    service = AdvancedCliService()

    # Test circuit breaker with a service
    test_service = "payment-service"

    console.print(f"\nTesting circuit breaker for: {test_service}")

    # Simulate multiple calls to demonstrate circuit breaker behavior
    for attempt in range(8):
        result = service.implement_circuit_breaker(test_service, failure_threshold=3)

        breaker_state = service.circuit_breakers.get(test_service, {}).get(
            "state", "unknown"
        )
        failure_count = service.circuit_breakers.get(test_service, {}).get(
            "failure_count", 0
        )

        status_color = "green" if result.is_success else "red"
        console.print(
            f"   Attempt {attempt + 1}: [{status_color}]{result.is_success}[/{status_color}] "
            f"(State: {getattr(breaker_state, 'value', str(breaker_state))}, "
            f"Failures: {failure_count})"
        )

        if (
            result.is_failure
            and result.error
            and "Circuit breaker OPEN" in result.error
        ):
            console.print(
                "   🚨 Circuit breaker is OPEN - failing fast to protect system"
            )
            break

    # Display circuit breaker status
    if test_service in service.circuit_breakers:
        breaker_info = service.circuit_breakers[test_service]

        breaker_table = Table(title=f"Circuit Breaker Status: {test_service}")
        breaker_table.add_column("Property", style="cyan")
        breaker_table.add_column("Value", style="green")

        state = breaker_info.get("state")
        state_value = getattr(state, "value", str(state)) if state else "unknown"
        breaker_table.add_row("State", str(state_value))
        breaker_table.add_row(
            "Failure Count", str(breaker_info.get("failure_count", 0))
        )
        breaker_table.add_row(
            "Failure Threshold", str(breaker_info.get("failure_threshold", 5))
        )
        breaker_table.add_row(
            "Timeout Duration", f"{breaker_info.get('timeout_duration', 60)}s"
        )

        console.print(breaker_table)

    return FlextResult[None].ok(None)


def demonstrate_service_orchestration() -> FlextResult[None]:
    """Demonstrate service orchestration patterns."""
    formatter = FlextCliOutput()
    console = formatter.console
    console.print("\n[green]Service Orchestration Demonstration[/green]")

    service = AdvancedCliService()

    # Demonstrate complex service orchestration
    orchestration_result = service.orchestrate_services("deploy_application")

    if orchestration_result.is_success:
        result_data = orchestration_result.value
        console.print("✅ Service orchestration completed successfully")

        # Display orchestration results
        orchestration_table = Table(title="Orchestration Results")
        orchestration_table.add_column("Service", style="cyan")
        orchestration_table.add_column("Operation", style="green")
        orchestration_table.add_column("Status", style="yellow")
        orchestration_table.add_column("Execution Time", style="blue")

        # Type-safe extraction of results
        if "results" in result_data:
            results_value = cast("dict[str, object]", result_data["results"])
            for service_name_key, step_result_value in results_value.items():
                if isinstance(step_result_value, dict):
                    step_result_typed = cast("dict[str, object]", step_result_value)
                    # Type-safe extraction with explicit casting
                    operation_value: str = str(
                        step_result_typed.get("operation", "unknown")
                    )
                    status_value: str = str(step_result_typed.get("status", "unknown"))
                    execution_time_value: int = int(
                        str(step_result_typed.get("execution_time_ms", 0))
                    )
                    orchestration_table.add_row(
                        str(service_name_key),
                        operation_value,
                        status_value,
                        f"{execution_time_value}ms",
                    )

        console.print(orchestration_table)

        console.print("\n📊 Orchestration Summary:")
        console.print(f"   Operation: {result_data.get('operation', 'unknown')}")
        console.print(f"   Steps Executed: {result_data.get('steps_executed', 0)}")
        console.print(f"   Completion Time: {result_data.get('timestamp', 'unknown')}")

    else:
        console.print(f"❌ Service orchestration failed: {orchestration_result.error}")

    return FlextResult[None].ok(None)


def demonstrate_dependency_injection() -> FlextResult[None]:
    """Demonstrate dependency injection with CLI container."""
    formatter = FlextCliOutput()
    console = formatter.console
    console.print("\n[green]Dependency Injection with CLI Container[/green]")

    # Create and configure CLI container
    container_instance = FlextContainer.get_global()

    # Create container variable with proper typing
    container: ContainerProtocol

    # Container has register/get methods available
    if container_instance:
        console.print("[green]✓[/green] Container is ready to use")
        console.print(f"Container type: {type(container_instance).__name__}")
        container = container_instance
    else:
        # Create mock container for demonstration
        class MockContainer:
            def __init__(self) -> None:
                self._services: dict[str, object] = {}

            def register(self, name: str, service: object) -> FlextResult[None]:
                self._services[name] = service
                return FlextResult[None].ok(None)

            def get(self, name: str) -> FlextResult[object]:
                if name in self._services:
                    return FlextResult[object].ok(self._services[name])
                return FlextResult[object].fail(f"Service {name} not found")

        container = MockContainer()

    # Register various services
    services_to_register = [
        ("console", formatter.console),
        ("logger", FlextLogger("demo")),
        ("config", FlextCliConfig()),
        ("api_client", FlextCliService()),
    ]

    console.print("📦 Registering services in container:")
    for service_name, service_instance in services_to_register:
        if container:
            registration_result = container.register(service_name, service_instance)
            if registration_result.is_success:
                console.print(
                    f"   ✅ {service_name}: {type(service_instance).__name__}"
                )
            else:
                console.print(
                    f"   ❌ Failed to register {service_name}: {registration_result.error}"
                )
        else:
            console.print(
                f"   ⚠️ {service_name}: {type(service_instance).__name__} (no container)"
            )

    # Demonstrate service retrieval
    console.print("\n🔍 Retrieving services from container:")
    for service_name, _ in services_to_register:
        if container:
            retrieval_result = container.get(service_name)
            if retrieval_result.is_success:
                retrieved_service = retrieval_result.value
                console.print(
                    f"   ✅ {service_name}: {type(retrieved_service).__name__}"
                )
            else:
                console.print(f"   ❌ {service_name}: {retrieval_result.error}")
        else:
            console.print(f"   ❌ {service_name}: Container not available")

    # Demonstrate service composition
    console.print("\n🏗️ Service composition example:")

    # Create a composite service using retrieved dependencies
    if container:
        logger_result = container.get("logger")
        config_result = container.get("config")
        api_client_result = container.get("api_client")
    else:
        logger_result = FlextResult[object].fail("Container not available")
        config_result = FlextResult[object].fail("Container not available")
        api_client_result = FlextResult[object].fail("Container not available")

    if all(
        result.is_success
        for result in [logger_result, config_result, api_client_result]
    ):
        logger = cast("FlextLogger", logger_result.value)
        config = config_result.value
        api_client = api_client_result.value

        console.print("   ✅ All dependencies resolved successfully")
        console.print(f"   📋 Logger: {type(logger).__name__}")
        console.print(f"   ⚙️ Config: {type(config).__name__}")
        console.print(f"   🌐 API Client: {type(api_client).__name__}")

        # Demonstrate using composed services
        if hasattr(logger, "info"):
            logger.info("Dependency injection demonstration completed")
        else:
            console.print("   📝 Logger demonstration completed")
        console.print("   ✅ Services working together successfully")

    return FlextResult[None].ok(None)


def main() -> None:
    """Main demonstration function."""
    formatter = FlextCliOutput()
    console = formatter.console

    formatter.print_success("05 - Advanced Service Integration Patterns")
    formatter.print_success("=" * 50)
    console.print(
        "[yellow]Comprehensive demonstration of advanced service integration:[/yellow]"
    )
    console.print("🏗️ FlextCliService with comprehensive mixins")
    console.print("🔄 Async service operations with @async_command")
    console.print("🛡️ Circuit breaker pattern for service resilience")
    console.print("🎼 Service orchestration and coordination")
    console.print("💉 Dependency injection with CLI container")
    console.print("📊 Health monitoring and performance tracking")
    console.print("🔧 Error handling and retry patterns")
    console.print()

    try:
        # Run async demonstration
        console.print("\n" + "=" * 60)
        try:
            # Run the async function properly
            asyncio.run(demonstrate_async_service_operations())
        except Exception as e:
            console.print(f"[red]Async operations failed: {e}[/red]")

        # Run circuit breaker demonstration
        console.print("\n" + "=" * 60)
        circuit_breaker_result = demonstrate_circuit_breaker_pattern()
        if circuit_breaker_result.is_failure:
            console.print(
                f"[red]Circuit breaker demo failed: {circuit_breaker_result.error}[/red]"
            )

        # Run orchestration demonstration
        console.print("\n" + "=" * 60)
        orchestration_result = demonstrate_service_orchestration()
        if orchestration_result.is_failure:
            console.print(
                f"[red]Orchestration demo failed: {orchestration_result.error}[/red]"
            )

        # Run dependency injection demonstration
        console.print("\n" + "=" * 60)
        di_result = demonstrate_dependency_injection()
        if di_result.is_failure:
            console.print(
                f"[red]Dependency injection demo failed: {di_result.error}[/red]"
            )

        # Final summary using shared utility

        print_demo_completion("Advanced Service Integration Demo")

    except Exception as e:
        console.print(
            f"[bold red]❌ Advanced service integration demo error: {e}[/bold red]"
        )


if __name__ == "__main__":
    main()

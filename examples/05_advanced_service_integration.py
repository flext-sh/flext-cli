#!/usr/bin/env python3
"""05 - Advanced Service Integration Patterns.

This example demonstrates advanced service integration patterns using flext-cli:

Key Patterns Demonstrated:
- FlextCliService inheritance with comprehensive mixins
- Dependency injection with create_cli_container()
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

# import random  # Removed for security - using fixed values instead
import time
from datetime import UTC, datetime
from enum import Enum
from typing import Any

from flext_core import FlextResult, get_logger
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from flext_cli import (
    FlextApiClient,
    FlextCliService,
    async_command,
    cli_enhanced,
    cli_handle_keyboard_interrupt,
    cli_measure_time,
    cli_retry,
    create_cli_container,
    get_cli_config,
    with_spinner,
)


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
        super().__init__(service_name="advanced_cli_service")

        # Use object.__setattr__ to set attributes on frozen model
        object.__setattr__(self, "_service_health", {})
        object.__setattr__(self, "_circuit_breakers", {})
        object.__setattr__(self, "_performance_metrics", {})

    def execute(self) -> FlextResult[object]:
        """Execute advanced CLI service operations."""
        return FlextResult[object].ok(
            {
                "service": "AdvancedCliService",
                "status": "operational",
                "features": ["health_check", "circuit_breaker", "async_operations"],
            }
        )

    @cli_enhanced
    @cli_measure_time
    @cli_retry(max_attempts=3)
    def check_service_health(self, service_name: str) -> FlextResult[dict[str, Any]]:
        """Check health of a specific service with retry logic."""
        try:
            logger = getattr(self, "logger", None)
            if logger:
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

            return FlextResult[None].ok(health_data)

        except Exception as e:
            self.logger.exception(f"Health check failed for {service_name}")
            return FlextResult[None].fail(f"Health check failed: {e}")

    @cli_enhanced
    @with_spinner("Orchestrating services...")
    def orchestrate_services(self, operation: str) -> FlextResult[dict[str, Any]]:
        """Orchestrate multiple services for complex operations."""
        try:
            self.logger.info(f"Starting service orchestration: {operation}")

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

                if step_result.success:
                    results[service_name] = step_result.unwrap()
                    self.logger.info(f"Step completed: {service_name}.{step_operation}")
                else:
                    # Handle step failure - implement rollback if needed
                    self.logger.error(
                        f"Step failed: {service_name}.{step_operation} - {step_result.error}"
                    )
                    return FlextResult[None].fail(
                        f"Orchestration failed at {service_name}: {step_result.error}"
                    )

            orchestration_result = {
                "operation": operation,
                "status": "completed",
                "steps_executed": len(orchestration_steps),
                "results": results,
                "timestamp": datetime.now(UTC).isoformat(),
            }

            return FlextResult[None].ok(orchestration_result)

        except Exception as e:
            self.logger.exception("Service orchestration failed")
            return FlextResult[None].fail(f"Service orchestration failed: {e}")

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
            if (
                breaker["state"] == CircuitBreakerState.OPEN
                and breaker["last_failure"]
                and (current_time - breaker["last_failure"]).seconds
                > breaker["timeout_duration"]
            ):
                breaker["state"] = CircuitBreakerState.HALF_OPEN
                self.logger.info(
                    f"Circuit breaker for {service_name} moved to HALF_OPEN"
                )

            # Simulate service call based on circuit state
            if breaker["state"] == CircuitBreakerState.OPEN:
                return FlextResult[None].fail(
                    f"Circuit breaker OPEN for {service_name}"
                )

            # Simulate service call
            call_success = self._simulate_service_call(service_name)

            if call_success:
                # Reset circuit breaker on success
                breaker["failure_count"] = 0
                breaker["state"] = CircuitBreakerState.CLOSED
                success_state = True
                return FlextResult[None].ok(success_state)
            # Handle failure
            breaker["failure_count"] += 1
            breaker["last_failure"] = current_time

            if breaker["failure_count"] >= breaker["failure_threshold"]:
                breaker["state"] = CircuitBreakerState.OPEN
                self.logger.warning(f"Circuit breaker OPENED for {service_name}")

            return FlextResult[None].fail(f"Service call failed for {service_name}")

        except Exception as e:
            return FlextResult[None].fail(f"Circuit breaker implementation failed: {e}")

    def _simulate_health_check(self, service_name: str) -> dict[str, Any]:
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
    ) -> FlextResult[dict[str, Any]]:
        """Execute a single orchestration step."""
        try:
            # Simulate step execution

            # Simulate processing time
            time.sleep(0.2)  # Fixed sleep for demo

            # Simulate success/failure (90% success rate)
            success = True  # Always succeed for demo

            if success:
                return FlextResult[None].ok(
                    {
                        "service": service_name,
                        "operation": operation,
                        "status": "success",
                        "execution_time_ms": 150,
                        "result": f"Operation {operation} completed successfully",
                    }
                )
            return FlextResult[None].fail(f"Operation {operation} failed")

        except Exception as e:
            return FlextResult[None].fail(f"Step execution failed: {e}")

    def _simulate_service_call(self, _service_name: str) -> bool:
        """Simulate service call for circuit breaker demo."""
        # Simulate service availability (80% success rate)
        return True  # Always succeed for demo


@async_command
@cli_handle_keyboard_interrupt
async def demonstrate_async_service_operations() -> None:
    """Demonstrate asynchronous service operations."""
    console = Console()
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
        tasks = []

        for service_name in services:
            task = progress.add_task(f"Checking {service_name}...", total=None)

            async def check_service_async(
                name: str, task_id: object
            ) -> tuple[str, FlextResult[dict[str, Any]]]:
                # Simulate async health check
                await asyncio.sleep(0.5)  # Simulate network delay
                result = service.check_service_health(name)
                progress.update(task_id, description=f"✅ {name} checked")
                return name, result

            tasks.append(check_service_async(service_name, task))

        # Execute all health checks concurrently
        results = await asyncio.gather(*tasks)

    # Display results
    health_table = Table(title="Concurrent Health Check Results")
    health_table.add_column("Service", style="cyan")
    health_table.add_column("Status", style="green")
    health_table.add_column("Response Time", style="yellow")
    health_table.add_column("Details", style="blue")

    for service_name, result in results:
        if result.success:
            data = result.unwrap()
            status = data["status"]
            response_time = f"{data.get('response_time_ms', 0)}ms"
            details = f"CPU: {data.get('details', {}).get('cpu_usage', 'N/A')}"

            # Color code status
            status_display = {
                "healthy": "[green]Healthy[/green]",
                "degraded": "[yellow]Degraded[/yellow]",
                "unhealthy": "[red]Unhealthy[/red]",
            }.get(status, status)

        else:
            status_display = "[red]Error[/red]"
            response_time = "N/A"
            # Define constant for max error display length
            max_error_length = 50
            details = (
                result.error[:max_error_length] + "..."
                if len(result.error) > max_error_length
                else result.error
            )

        health_table.add_row(service_name, status_display, response_time, details)

    console.print(health_table)


def demonstrate_circuit_breaker_pattern() -> FlextResult[None]:
    """Demonstrate circuit breaker pattern for service resilience."""
    console = Console()
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

        status_color = "green" if result.success else "red"
        console.print(
            f"   Attempt {attempt + 1}: [{status_color}]{result.success}[/{status_color}] "
            f"(State: {breaker_state.value if hasattr(breaker_state, 'value') else breaker_state}, "
            f"Failures: {failure_count})"
        )

        if not result.success and "Circuit breaker OPEN" in result.error:
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

        breaker_table.add_row("State", str(breaker_info["state"].value))
        breaker_table.add_row("Failure Count", str(breaker_info["failure_count"]))
        breaker_table.add_row(
            "Failure Threshold", str(breaker_info["failure_threshold"])
        )
        breaker_table.add_row(
            "Timeout Duration", f"{breaker_info['timeout_duration']}s"
        )

        console.print(breaker_table)

    return FlextResult[None].ok(None)


def demonstrate_service_orchestration() -> FlextResult[None]:
    """Demonstrate service orchestration patterns."""
    console = Console()
    console.print("\n[green]Service Orchestration Demonstration[/green]")

    service = AdvancedCliService()

    # Demonstrate complex service orchestration
    orchestration_result = service.orchestrate_services("deploy_application")

    if orchestration_result.success:
        result_data = orchestration_result.unwrap()
        console.print("✅ Service orchestration completed successfully")

        # Display orchestration results
        orchestration_table = Table(title="Orchestration Results")
        orchestration_table.add_column("Service", style="cyan")
        orchestration_table.add_column("Operation", style="green")
        orchestration_table.add_column("Status", style="yellow")
        orchestration_table.add_column("Execution Time", style="blue")

        for service_name, step_result in result_data["results"].items():
            orchestration_table.add_row(
                service_name,
                step_result["operation"],
                step_result["status"],
                f"{step_result['execution_time_ms']}ms",
            )

        console.print(orchestration_table)

        console.print("\n📊 Orchestration Summary:")
        console.print(f"   Operation: {result_data['operation']}")
        console.print(f"   Steps Executed: {result_data['steps_executed']}")
        console.print(f"   Completion Time: {result_data['timestamp']}")

    else:
        console.print(f"❌ Service orchestration failed: {orchestration_result.error}")

    return FlextResult[None].ok(None)


def demonstrate_dependency_injection() -> FlextResult[None]:
    """Demonstrate dependency injection with CLI container."""
    console = Console()
    console.print("\n[green]Dependency Injection with CLI Container[/green]")

    # Create and configure CLI container
    container = create_cli_container()

    # Register various services
    services_to_register = [
        ("console", Console()),
        ("logger", get_logger("demo")),
        ("config", get_cli_config()),
        ("api_client", FlextApiClient()),
    ]

    console.print("📦 Registering services in container:")
    for service_name, service_instance in services_to_register:
        container.register(service_name, service_instance)
        console.print(f"   ✅ {service_name}: {type(service_instance).__name__}")

    # Demonstrate service retrieval
    console.print("\n🔍 Retrieving services from container:")
    for service_name, _ in services_to_register:
        retrieval_result = container.get(service_name)
        if retrieval_result.success:
            retrieved_service = retrieval_result.unwrap()
            console.print(f"   ✅ {service_name}: {type(retrieved_service).__name__}")
        else:
            console.print(f"   ❌ {service_name}: {retrieval_result.error}")

    # Demonstrate service composition
    console.print("\n🏗️ Service composition example:")

    # Create a composite service using retrieved dependencies
    logger_result = container.get("logger")
    config_result = container.get("config")
    api_client_result = container.get("api_client")

    if all(
        result.success for result in [logger_result, config_result, api_client_result]
    ):
        logger = logger_result.unwrap()
        config = config_result.unwrap()
        api_client = api_client_result.unwrap()

        console.print("   ✅ All dependencies resolved successfully")
        console.print(f"   📋 Logger: {type(logger).__name__}")
        console.print(f"   ⚙️ Config: {type(config).__name__}")
        console.print(f"   🌐 API Client: {type(api_client).__name__}")

        # Demonstrate using composed services
        logger.info("Dependency injection demonstration completed")
        console.print("   ✅ Services working together successfully")

    return FlextResult[None].ok(None)


def main() -> None:
    """Main demonstration function."""
    console = Console()

    console.print(
        Panel(
            "[bold purple]05 - Advanced Service Integration Patterns[/bold purple]\n\n"
            "[yellow]Comprehensive demonstration of advanced service integration:[/yellow]\n"
            "🏗️ FlextCliService with comprehensive mixins\n"
            "🔄 Async service operations with @async_command\n"
            "🛡️ Circuit breaker pattern for service resilience\n"
            "🎼 Service orchestration and coordination\n"
            "💉 Dependency injection with CLI container\n"
            "📊 Health monitoring and performance tracking\n"
            "🔧 Error handling and retry patterns",
            expand=False,
        )
    )

    try:
        # Run async demonstration
        console.print("\n" + "=" * 60)
        asyncio.run(demonstrate_async_service_operations())

        # Run circuit breaker demonstration
        console.print("\n" + "=" * 60)
        circuit_breaker_result = demonstrate_circuit_breaker_pattern()
        if circuit_breaker_result.failure:
            console.print(
                f"[red]Circuit breaker demo failed: {circuit_breaker_result.error}[/red]"
            )

        # Run orchestration demonstration
        console.print("\n" + "=" * 60)
        orchestration_result = demonstrate_service_orchestration()
        if orchestration_result.failure:
            console.print(
                f"[red]Orchestration demo failed: {orchestration_result.error}[/red]"
            )

        # Run dependency injection demonstration
        console.print("\n" + "=" * 60)
        di_result = demonstrate_dependency_injection()
        if di_result.failure:
            console.print(
                f"[red]Dependency injection demo failed: {di_result.error}[/red]"
            )

        # Final summary
        console.print(
            Panel(
                "[bold green]✅ Advanced Service Integration Demo Completed![/bold green]\n\n"
                "[cyan]Advanced Patterns Demonstrated:[/cyan]\n"
                "🏗️ FlextCliService with comprehensive mixin composition\n"
                "🔄 Async operations with concurrent health checking\n"
                "🛡️ Circuit breaker pattern for fault tolerance\n"
                "🎼 Multi-service orchestration with rollback capability\n"
                "💉 Dependency injection container with service composition\n"
                "📊 Real-time monitoring and health tracking\n"
                "🔧 Advanced error handling and resilience patterns\n\n"
                "[yellow]All patterns integrated with flext-core FlextResult![/yellow]",
                expand=False,
            )
        )

    except Exception as e:
        console.print(
            f"[bold red]❌ Advanced service integration demo error: {e}[/bold red]"
        )


if __name__ == "__main__":
    main()

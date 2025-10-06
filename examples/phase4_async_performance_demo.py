"""FLEXT-CLI Phase 4 & Performance Demo.

This example demonstrates Phase 4 support and performance features:
- command execution with @command
- Concurrent operations
- task management
- Lazy loading for heavy dependencies
- Result caching with TTL
- Function memoization

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import contextlib
import time
from time import sleep

from flext_cli import (
    FlextCliPerformance,
)


def demo_command_execution() -> None:
    """Demo 1: Command Execution."""
    runner = FlextCliPerformance()  # Using performance service instead of non-existent runner

    def fetch_data(url: str) -> dict:
        """Simulate data fetching."""
        sleep(1)  # Simulate network delay
        return {"url": url, "status": "success", "data": f"Response from {url}"}

    # Execute operation
    result = runner.run(fetch_data("https://api.example.com/data"))

    if result.is_success:
        result.unwrap()


def demo_concurrent_operations() -> None:
    """Demo 2: Concurrent Operations."""
    runner = FlextCliPerformance()  # Using performance service instead of non-existent runner

    def fetch_resource(resource_id: int) -> dict:
        """Simulate fetching a resource."""
        sleep(0.5)  # Simulate delay
        return {"id": resource_id, "status": "completed"}

    # Run multiple operations concurrently
    start_time = time.time()

    coros = [fetch_resource(i) for i in range(1, 6)]
    result = runner.run_multiple(coros)

    if result.is_success:
        results = result.unwrap()
        time.time() - start_time
        for _res in results:
            pass


def demo_with_timeout() -> None:
    """Demo 3: Operations with Timeout."""
    runner = FlextCliPerformance()  # Using performance service instead of non-existent runner

    def slow_operation() -> str:
        """Operation that takes too long."""
        sleep(5)  # Takes 5 seconds
        return "completed"

    # Run with 2-second timeout
    result = runner.run(slow_operation(), timeout=2.0)

    if result.is_success:
        pass


def demo_task_manager() -> None:
    """Demo 4: Task Manager."""
    manager = FlextCliTaskManager()

    def background_task(task_name: str, duration: int) -> str:
        """Simulate background processing."""
        sleep(duration)
        return f"Task '{task_name}' completed"

    # Start background task
    task_result = manager.start_task(
        "data-processing", background_task("data-processing", 2)
    )

    if task_result.is_success:
        task_id = task_result.unwrap()

        # Check status immediately
        status_result = manager.get_task_status(task_id)
        if status_result.is_success:
            status_result.unwrap()


def demo_lazy_loading() -> None:
    """Demo 5: Lazy Module Loading."""
    loader = FlextCliLazyLoader()

    # Register heavy modules for lazy loading
    loader.register_lazy_module("json", "json")
    loader.register_lazy_module("os", "os")

    # Load module when needed
    json_result = loader.load_module("json")

    if json_result.is_success:
        json_module = json_result.unwrap()

        # Use the module
        json_module.dumps({"status": "loaded", "module": "json"})

    # Check loaded status
    loaded_result = loader.get_loaded_modules()
    if loaded_result.is_success:
        loaded_result.unwrap()


def demo_result_caching() -> None:
    """Demo 6: Result Caching with TTL."""
    cache = FlextCliCache()

    # Cache expensive computation result
    expensive_data = {"result": 42, "computation": "expensive"}
    cache.set("expensive_query", expensive_data, ttl=5)  # 5 second TTL

    # Retrieve from cache
    cached_result = cache.get("expensive_query")

    if cached_result.is_success:
        cached_result.unwrap()

    # Get cache statistics
    stats_result = cache.get_stats()
    if stats_result.is_success:
        stats_result.unwrap()


def demo_memoization() -> None:
    """Demo 7: Function Memoization."""

    @memoize(ttl=60)
    def expensive_computation(x: int, y: int) -> int:
        """Expensive function that benefits from memoization."""
        sleep(1)  # Simulate expensive computation
        return x + y

    # First call - computed
    start = time.time()
    expensive_computation(5, 3)
    time.time() - start

    # Second call - cached
    start = time.time()
    expensive_computation(5, 3)
    time.time() - start

    # Different args - computed
    start = time.time()
    expensive_computation(10, 20)
    time.time() - start


def demo_command_decorator() -> None:
    """Demo 8: @command Decorator."""

    @command
    def fetch_user_data(user_id: int) -> dict:
        """Function wrapped as sync CLI command."""
        sleep(0.5)
        return {"id": user_id, "name": f"User{user_id}", "status": "active"}

    # Call the wrapped function (-> sync)
    with contextlib.suppress(Exception):
        fetch_user_data(123)


def main() -> None:
    """Run all Phase 4 & performance demos."""
    # Run all demos
    demo_command_execution()
    demo_concurrent_operations()
    demo_with_timeout()
    demo_task_manager()
    demo_lazy_loading()
    demo_result_caching()
    demo_memoization()
    demo_command_decorator()

    # Final summary


if __name__ == "__main__":
    main()

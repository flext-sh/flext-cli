"""Automated performance tests with real workloads."""

import os
import time

import psutil
import pytest

from flext_cli.constants import FlextCliConstants as c
from tests._helpers import create_test_cli_command, create_test_cli_session


class TestsCliPerformanceAutomated:
    """Automated performance tests using real implementations."""

    @pytest.mark.parametrize("num_commands", [10, 50, 100, 500])
    def test_session_bulk_command_operations(self, num_commands: int) -> None:
        """Test bulk command operations performance."""
        session = create_test_cli_session()

        # Measure command addition time
        start_time = time.time()
        for i in range(num_commands):
            cmd = create_test_cli_command(name=f"cmd{i}", command_id=f"id{i}")
            session.add_command(cmd)
        addition_time = time.time() - start_time

        # Verify all commands added
        assert session.total_commands == num_commands

        # Measure filtering performance
        start_time = time.time()
        pending = session.commands_by_status(c.Cli.CommandStatus.PENDING)
        filter_time = time.time() - start_time

        assert len(pending) == num_commands

        # Performance assertions (adjust thresholds as needed)
        assert addition_time < 1.0, f"Command addition too slow: {addition_time}s"
        assert filter_time < 0.1, f"Command filtering too slow: {filter_time}s"

    @pytest.mark.parametrize("data_size", [100, 1000, 10000])
    def test_command_data_handling_performance(self, data_size: int) -> None:
        """Test performance with large command data."""
        large_args = [f"arg{i}" for i in range(data_size)]
        large_env = {f"VAR{i}": f"value{i}" for i in range(min(data_size, 100))}

        start_time = time.time()
        cmd = create_test_cli_command(
            arguments=large_args,
            environment=large_env,
            tags=[f"tag{i}" for i in range(min(data_size, 50))],
        )
        creation_time = time.time() - start_time

        # Verify data integrity
        assert len(cmd.arguments) == data_size
        assert len(cmd.environment) == min(data_size, 100)

        # Performance assertion
        assert creation_time < 0.5, f"Large data creation too slow: {creation_time}s"

    def test_memory_usage_patterns(self) -> None:
        """Test memory usage patterns with real object creation."""
        # Get initial memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create many objects
        commands = []
        for i in range(1000):
            cmd = create_test_cli_command(
                name=f"cmd{i}",
                arguments=[f"arg{j}" for j in range(10)],
                environment={f"VAR{j}": f"value{j}" for j in range(10)},
            )
            commands.append(cmd)

        # Check memory after creation
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Cleanup
        del commands

        # Assert reasonable memory usage (adjust threshold as needed)
        assert memory_increase < 50, f"Memory usage too high: {memory_increase}MB"

"""Automated performance tests with real workloads."""

import os  # @vulture_ignore
import time  # @vulture_ignore
from datetime import UTC, datetime  # @vulture_ignore

import psutil  # @vulture_ignore
import pytest  # @vulture_ignore

from flext_cli.constants import c
from flext_cli.models import m
from tests._helpers import create_test_cli_command


class TestsCliPerformanceAutomated:
    """Automated performance tests using real implementations."""

    @pytest.mark.parametrize("num_commands", [10, 50, 100, 500])
    def test_session_bulk_command_operations(self, num_commands: int) -> None:
        """Test bulk command operations performance."""
        # Create commands first - optimize by using same base timestamp
        commands = []
        base_time = time.time()  # Get base time once
        start_time = time.time()
        for i in range(num_commands):
            # Use optimized creation with shared timestamp base
            cmd = create_test_cli_command(
                name=f"cmd{i}",
                created_at=datetime.fromtimestamp(
                    base_time + i * 0.001, UTC
                ),  # Microsecond increments
            )
            commands.append(cmd)
        creation_time = time.time() - start_time

        # Create session with all commands
        session = m.Cli.CliSession.model_construct(
            session_id="test-session",
            status=c.Cli.SessionStatus.ACTIVE,
            commands=commands,
        )

        # Verify all commands present
        assert len(session.commands) == num_commands

        # Measure filtering performance
        start_time = time.time()
        pending = session.commands_by_status(c.Cli.CommandStatus.PENDING.value)
        filter_time = time.time() - start_time

        assert len(pending) == num_commands

        # Performance assertions (adjusted for realistic expectations)
        assert creation_time < 5.0, f"Command creation too slow: {creation_time}s"
        assert filter_time < 0.1, f"Command filtering too slow: {filter_time}s"

    @pytest.mark.parametrize("data_size", [100, 1000, 10000])
    def test_command_data_handling_performance(self, data_size: int) -> None:
        """Test performance with large command args."""
        # args is a valid CliCommand field
        large_args = [f"arg{i}" for i in range(min(data_size, 1000))]  # Limit args size

        start_time = time.time()
        cmd = create_test_cli_command(
            name="perf-test",
            args=large_args,
            command_line=" ".join(large_args[:100]),  # Use command_line for overflow
        )
        creation_time = time.time() - start_time

        # Verify data integrity
        assert len(cmd.args) == min(data_size, 1000)

        # Performance assertion
        assert creation_time < 0.5, f"Large data creation too slow: {creation_time}s"

    def test_memory_usage_patterns(self) -> None:
        """Test memory usage patterns with real object creation."""
        # Get initial memory
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create many objects with valid CliCommand fields
        commands = []
        for i in range(1000):
            cmd = create_test_cli_command(
                name=f"cmd{i}",
                args=[f"arg{j}" for j in range(10)],
            )
            commands.append(cmd)

        # Check memory after creation
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        # Cleanup
        del commands

        # Assert reasonable memory usage (adjust threshold as needed)
        assert memory_increase < 50, f"Memory usage too high: {memory_increase}MB"

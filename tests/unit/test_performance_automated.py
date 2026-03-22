"""Automated performance tests with real workloads."""

from __future__ import annotations

import os
import time
from datetime import UTC, datetime

import psutil
import pytest
from flext_tests import tm

from flext_cli import FlextCliModels, c, m
from tests._helpers import create_test_cli_command


class TestsCliPerformanceAutomated:
    """Automated performance tests using real implementations."""

    @pytest.mark.parametrize("num_commands", [10, 50, 100, 500])
    def test_session_bulk_command_operations(self, num_commands: int) -> None:
        """Test bulk command operations performance."""
        commands: list[FlextCliModels.Cli.CliCommand] = []
        base_time = time.time()
        start_time = time.time()
        for i in range(num_commands):
            cmd = create_test_cli_command(
                name=f"cmd{i}",
                created_at=datetime.fromtimestamp(base_time + i * 0.001, UTC),
            )
            commands.append(cmd)
        creation_time = time.time() - start_time
        session = m.Cli.CliSession.model_construct(
            session_id="test-session",
            status=c.Cli.SessionStatus.ACTIVE,
            commands=commands,
        )
        tm.that(len(session.commands), eq=num_commands)
        start_time = time.time()
        pending = session.commands_by_status(c.Cli.CommandStatus.PENDING.value)
        filter_time = time.time() - start_time
        tm.that(len(pending), eq=num_commands)
        tm.that(creation_time < 5.0, eq=True)
        tm.that(filter_time < 0.1, eq=True)

    @pytest.mark.parametrize("data_size", [100, 1000, 10000])
    def test_command_data_handling_performance(self, data_size: int) -> None:
        """Test performance with large command args."""
        large_args = [f"arg{i}" for i in range(min(data_size, 1000))]
        start_time = time.time()
        cmd = create_test_cli_command(
            name="perf-test", args=large_args, command_line=" ".join(large_args[:100])
        )
        creation_time = time.time() - start_time
        tm.that(len(cmd.args), eq=min(data_size, 1000))
        tm.that(creation_time < 0.5, eq=True)

    def test_memory_usage_patterns(self) -> None:
        """Test memory usage patterns with real t.NormalizedValue creation."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024
        commands: list[FlextCliModels.Cli.CliCommand] = []
        for i in range(1000):
            cmd = create_test_cli_command(
                name=f"cmd{i}", args=[f"arg{j}" for j in range(10)]
            )
            commands.append(cmd)
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        del commands
        tm.that(memory_increase < 50, eq=True)

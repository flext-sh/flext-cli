"""Automated performance tests with real workloads."""

from __future__ import annotations

import os
import time

import psutil
import pytest
from flext_tests import tm

from flext_cli import FlextCliModels
from tests._helpers import create_test_cli_command


class TestsCliPerformanceAutomated:
    """Automated performance tests using real implementations."""

    @pytest.mark.parametrize("data_size", [100, 1000, 10000])
    def test_command_data_handling_performance(self, data_size: int) -> None:
        """Test performance with large command args."""
        large_args = [f"arg{i}" for i in range(min(data_size, 1000))]
        start_time = time.time()
        cmd = create_test_cli_command(
            name="perf-test",
            args=large_args,
            command_line=" ".join(large_args[:100]),
        )
        creation_time = time.time() - start_time
        tm.that(len(cmd.args), eq=min(data_size, 1000))
        tm.that(creation_time, lt=0.5)

    def test_memory_usage_patterns(self) -> None:
        """Test memory usage patterns with real t.NormalizedValue creation."""
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024
        commands: list[FlextCliModels.Cli.CliCommand] = []
        for i in range(1000):
            cmd = create_test_cli_command(
                name=f"cmd{i}",
                args=[f"arg{j}" for j in range(10)],
            )
            commands.append(cmd)
        final_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = final_memory - initial_memory
        del commands
        tm.that(memory_increase, lt=50)

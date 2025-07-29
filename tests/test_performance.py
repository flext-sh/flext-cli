"""Performance tests for flext-cli."""

import time

import pytest
from flext_cli import CliApi, export


class TestPerformance:
    """Test performance characteristics of flext-cli."""

    def test_export_performance_small_dataset(self, mock_flext_core, temp_dir) -> None:
        """Test export performance with small dataset."""
        api = CliApi()

        # Small dataset (100 records)
        data = [{"id": i, "name": f"User {i}", "value": i * 10} for i in range(100)]
        filepath = temp_dir / "small_dataset.json"

        start_time = time.time()
        result = api.export(data, str(filepath), "json")
        end_time = time.time()

        assert result.is_success
        execution_time = end_time - start_time

        # Should complete in under 100ms for small dataset
        assert execution_time < 0.1, f"Export took {execution_time:.3f}s, expected < 0.1s"

    def test_export_performance_medium_dataset(self, mock_flext_core, temp_dir) -> None:
        """Test export performance with medium dataset."""
        api = CliApi()

        # Medium dataset (1000 records)
        data = [
            {
                "id": i,
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "score": i * 10,
                "active": i % 2 == 0,
                "metadata": {"created": f"2024-01-{i % 28 + 1:02d}", "type": "user"},
            }
            for i in range(1000)
        ]
        filepath = temp_dir / "medium_dataset.json"

        start_time = time.time()
        result = api.export(data, str(filepath), "json")
        end_time = time.time()

        assert result.is_success
        execution_time = end_time - start_time

        # Should complete in under 500ms for medium dataset
        assert execution_time < 0.5, f"Export took {execution_time:.3f}s, expected < 0.5s"

    def test_format_performance_table_rendering(self, mock_flext_core) -> None:
        """Test table formatting performance."""
        api = CliApi()

        # Dataset with multiple columns for table rendering
        data = [
            {
                "id": i,
                "name": f"Item {i}",
                "category": f"Category {i % 5}",
                "price": f"${i * 9.99:.2f}",
                "status": "active" if i % 2 == 0 else "inactive",
                "description": f"Description for item {i} with some longer text content",
            }
            for i in range(100)
        ]

        start_time = time.time()
        result = api.format_data(data, "table")
        end_time = time.time()

        assert result.is_success
        execution_time = end_time - start_time

        # Table formatting should complete quickly
        assert execution_time < 0.2, f"Table formatting took {execution_time:.3f}s, expected < 0.2s"

    def test_multiple_exports_performance(self, mock_flext_core, temp_dir) -> None:
        """Test performance of multiple sequential exports."""
        api = CliApi()

        # Test data
        data = [{"id": i, "value": f"data_{i}"} for i in range(50)]

        # Perform multiple exports
        export_count = 10
        start_time = time.time()

        for i in range(export_count):
            filepath = temp_dir / f"export_{i}.json"
            result = api.export(data, str(filepath), "json")
            assert result.is_success

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / export_count

        # Average export time should be reasonable
        assert avg_time < 0.05, f"Average export time {avg_time:.3f}s, expected < 0.05s"

        # All files should exist
        for i in range(export_count):
            assert (temp_dir / f"export_{i}.json").exists()

    def test_csv_export_performance(self, mock_flext_core, temp_dir) -> None:
        """Test CSV export performance compared to JSON."""
        api = CliApi()

        # Large-ish dataset with consistent structure
        data = [
            {
                "id": i,
                "name": f"Record {i}",
                "category": f"Cat{i % 10}",
                "value": i * 1.5,
                "active": i % 2 == 0,
            }
            for i in range(500)
        ]

        # Test JSON export
        json_file = temp_dir / "perf_test.json"
        start_time = time.time()
        json_result = api.export(data, str(json_file), "json")
        json_time = time.time() - start_time

        # Test CSV export
        csv_file = temp_dir / "perf_test.csv"
        start_time = time.time()
        csv_result = api.export(data, str(csv_file), "csv")
        csv_time = time.time() - start_time

        assert json_result.is_success
        assert csv_result.is_success

        # Both should complete in reasonable time
        assert json_time < 0.3, f"JSON export took {json_time:.3f}s"
        assert csv_time < 0.3, f"CSV export took {csv_time:.3f}s"

        # File sizes should make sense
        json_size = json_file.stat().st_size
        csv_size = csv_file.stat().st_size

        assert json_size > 0
        assert csv_size > 0

    def test_convenience_function_performance(self, mock_flext_core, temp_dir) -> None:
        """Test that convenience functions don't add significant overhead."""
        # Test data
        data = [{"id": i, "name": f"Item {i}"} for i in range(100)]

        # Direct API usage
        api = CliApi()
        api_file = temp_dir / "api_direct.json"

        start_time = time.time()
        api_result = api.export(data, str(api_file), "json")
        api_time = time.time() - start_time

        # Convenience function usage
        conv_file = temp_dir / "convenience.json"

        start_time = time.time()
        conv_result = export(data, str(conv_file), "json")
        conv_time = time.time() - start_time

        assert api_result.is_success
        assert conv_result is True

        # Convenience function shouldn't add significant overhead
        overhead = conv_time - api_time
        assert overhead < 0.05, f"Convenience function overhead {overhead:.3f}s too high"

    def test_memory_usage_large_dataset(self, mock_flext_core, temp_dir) -> None:
        """Test memory usage with larger datasets."""
        api = CliApi()

        # Create a larger dataset to test memory handling
        # Note: This is a stress test - in real usage, very large datasets
        # should be processed in chunks
        large_data = [
            {
                "id": i,
                "data": f"{'x' * 100}",  # 100 character string per record
                "numbers": list(range(10)),  # Small array per record
                "nested": {"key1": f"value{i}", "key2": i * 2},
            }
            for i in range(1000)  # 1000 records
        ]

        filepath = temp_dir / "large_dataset.json"

        # This should work without memory issues
        start_time = time.time()
        result = api.export(large_data, str(filepath), "json")
        end_time = time.time()

        assert result.is_success
        execution_time = end_time - start_time

        # Should still complete in reasonable time
        assert execution_time < 2.0, f"Large dataset export took {execution_time:.3f}s"

        # File should exist and have reasonable size
        assert filepath.exists()
        file_size = filepath.stat().st_size
        assert file_size > 0


class TestScalability:
    """Test scalability characteristics."""

    def test_command_registry_performance(self, mock_flext_core) -> None:
        """Test performance of command registration and execution."""
        api = CliApi()

        # Register many commands
        command_count = 100

        start_time = time.time()
        for i in range(command_count):
            def make_command(num):
                return lambda: f"Command {num} executed"

            result = api.add_command(f"cmd_{i}", make_command(i))
            assert result.is_success

        registration_time = time.time() - start_time

        # Command registration should be fast
        avg_registration = registration_time / command_count
        assert avg_registration < 0.001, f"Average command registration {avg_registration:.4f}s too slow"

        # Test command execution performance
        start_time = time.time()
        for i in range(10):  # Execute subset of commands
            result = api.execute(f"cmd_{i}")
            assert result.is_success
            assert result.data == f"Command {i} executed"

        execution_time = time.time() - start_time
        avg_execution = execution_time / 10

        assert avg_execution < 0.001, f"Average command execution {avg_execution:.4f}s too slow"

    def test_concurrent_operations_simulation(self, mock_flext_core, temp_dir) -> None:
        """Test simulated concurrent operations (sequential but rapid)."""
        api = CliApi()

        # Simulate rapid sequential operations like concurrent usage
        operations = [
            ("export", lambda i: api.export([{"id": i}], str(temp_dir / f"concurrent_{i}.json"), "json")),
            ("format", lambda i: api.format_data([{"id": i}], "json")),
            ("health", lambda i: api.health()),
        ]

        total_operations = 30
        start_time = time.time()

        for i in range(total_operations):
            op_type, op_func = operations[i % len(operations)]
            result = op_func(i)

            # All operations should succeed
            if hasattr(result, "is_success"):
                assert result.is_success
            else:
                assert result is True or isinstance(result, str)

        end_time = time.time()
        total_time = end_time - start_time
        avg_time = total_time / total_operations

        # Operations should maintain good performance under load
        assert avg_time < 0.01, f"Average operation time {avg_time:.4f}s under simulated load"


@pytest.mark.benchmark
class TestBenchmarks:
    """Benchmark tests for performance tracking."""

    def test_export_benchmark_small(self, mock_flext_core, temp_dir) -> None:
        """Benchmark small dataset export."""
        api = CliApi()
        data = [{"id": i, "value": i} for i in range(10)]
        filepath = temp_dir / "benchmark_small.json"

        # Warmup
        api.export(data, str(filepath), "json")

        # Benchmark
        times = []
        for _ in range(10):
            start = time.time()
            result = api.export(data, str(filepath), "json")
            end = time.time()
            assert result.is_success
            times.append(end - start)

        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        # Record benchmark results (in real usage, this could be logged)

        # Ensure consistency
        assert max_time - min_time < 0.01, "Performance too variable"
        assert avg_time < 0.01, "Performance regression detected"

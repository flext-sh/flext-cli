"""Integration tests for flext-cli with flext-core patterns."""

import json
import tempfile
from pathlib import Path

from flext_cli import CliApi, export, format_data, health


class TestFlextCoreIntegration:
    """Test integration with flext-core patterns."""

    def test_flext_result_pattern_usage(self, mock_flext_core) -> None:
        """Test that FlextResult pattern is used consistently."""
        api = CliApi()

        # All API methods should return FlextResult
        health_result = api.health()
        assert hasattr(health_result, "is_success")
        assert hasattr(health_result, "data")
        assert hasattr(health_result, "error")

        export_result = api.export([{"test": "data"}], "/tmp/test.json", "json")
        assert hasattr(export_result, "is_success")

        format_result = api.format_data({"test": "data"}, "json")
        assert hasattr(format_result, "is_success")

        command_result = api.add_command("test", lambda: "test")
        assert hasattr(command_result, "is_success")

    def test_logger_integration(self, mock_flext_core) -> None:
        """Test that flext-core logger is used properly."""
        api = CliApi()
        logger = mock_flext_core["logger"]

        # Logger should be called during initialization
        assert any("CliApi initialized" in msg for msg in logger.messages)

        # Clear messages for specific test
        logger.clear()

        # Perform operations that should log
        api.export([{"test": "data"}], "/tmp/test.json", "json")
        api.format_data({"test": "data"}, "json")

        # Should have logging messages
        assert len(logger.messages) > 0

    def test_type_safety_with_flext_core_types(self, mock_flext_core, sample_data) -> None:
        """Test type safety integration with flext-core types."""
        api = CliApi()

        # Test with various data types that should work with TValue
        test_cases = [
            sample_data,  # List of dicts
            sample_data[0],  # Single dict
            "string_data",  # String
            42,  # Number
            True,  # Boolean
        ]

        for data in test_cases:
            # Export should work with all these types
            result = api.export(data, "/tmp/test.json", "json")
            assert result.is_success

            # Format should work with all these types
            format_result = api.format_data(data, "json")
            assert format_result.is_success

    def test_error_handling_consistency(self, mock_flext_core) -> None:
        """Test consistent error handling across all methods."""
        api = CliApi()

        # Test various error conditions
        error_cases = [
            # Invalid export data
            (lambda: api.export(None, "/tmp/test.json", "json"), "export with None"),
            # Invalid format
            (lambda: api.export([{"test": "data"}], "/tmp/test.xyz", "invalid"), "invalid format"),
            # Invalid style
            (lambda: api.format_data({"test": "data"}, "invalid"), "invalid style"),
            # Invalid command name
            (lambda: api.add_command("", lambda: "test"), "empty command name"),
            # Nonexistent command
            (lambda: api.execute("nonexistent"), "nonexistent command"),
        ]

        for error_func, description in error_cases:
            result = error_func()
            assert not result.is_success, f"Should fail: {description}"
            assert result.error is not None, f"Should have error message: {description}"


class TestConvenienceFunctionIntegration:
    """Test convenience functions integration."""

    def test_convenience_functions_use_api_internally(self, mock_flext_core, sample_data, temp_dir) -> None:
        """Test that convenience functions properly use the API internally."""
        # Export function
        filepath = temp_dir / "convenience_test.json"
        success = export(sample_data, str(filepath), "json")

        assert success is True
        assert filepath.exists()

        # Verify the file contains expected data
        with filepath.open() as f:
            data = json.load(f)
        assert data == sample_data

    def test_convenience_functions_error_handling(self, mock_flext_core) -> None:
        """Test convenience functions handle errors gracefully."""
        # Export with invalid data
        success = export(None, "/tmp/invalid.json")
        assert success is False

        # Format with invalid style
        result = format_data({"test": "data"}, "invalid")
        assert result.startswith("Error:")

        # Health with mocked failure - should return default
        result = health()
        assert isinstance(result, dict)
        assert "status" in result

    def test_module_level_api_consistency(self, mock_flext_core, sample_data) -> None:
        """Test that module-level functions are consistent with API."""
        from flext_cli import CliApi

        api = CliApi()

        # Compare direct API usage with convenience functions
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # API method
            api_file = temp_path / "api_export.json"
            api_result = api.export(sample_data, str(api_file), "json")

            # Convenience function
            conv_file = temp_path / "conv_export.json"
            conv_success = export(sample_data, str(conv_file), "json")

            # Both should succeed
            assert api_result.is_success
            assert conv_success is True

            # Both should create files with same content
            with api_file.open() as f:
                api_data = json.load(f)
            with conv_file.open() as f:
                conv_data = json.load(f)

            assert api_data == conv_data


class TestRealWorldIntegrationScenarios:
    """Test real-world integration scenarios."""

    def test_data_pipeline_workflow(self, mock_flext_core, temp_dir) -> None:
        """Test complete data pipeline workflow."""
        api = CliApi()

        # Step 1: Input data (simulating from external source)
        raw_data = [
            {"id": 1, "name": "Alice", "score": 85, "category": "A"},
            {"id": 2, "name": "Bob", "score": 92, "category": "A"},
            {"id": 3, "name": "Charlie", "score": 78, "category": "B"},
        ]

        # Step 2: Add data processing command
        def calculate_statistics(data):
            total_score = sum(item["score"] for item in data)
            avg_score = total_score / len(data)
            return {
                "total_records": len(data),
                "average_score": avg_score,
                "categories": list({item["category"] for item in data}),
            }

        api.add_command("stats", calculate_statistics)

        # Step 3: Process data
        stats_result = api.execute("stats", raw_data)
        assert stats_result.is_success

        stats_data = stats_result.data
        assert stats_data["total_records"] == 3
        assert stats_data["average_score"] == 85.0

        # Step 4: Export raw data
        raw_file = temp_dir / "raw_data.json"
        export_result = api.export(raw_data, str(raw_file), "json")
        assert export_result.is_success

        # Step 5: Export statistics
        stats_file = temp_dir / "statistics.json"
        stats_export = api.export([stats_data], str(stats_file), "json")
        assert stats_export.is_success

        # Step 6: Format for display
        display_result = api.format_data(raw_data, "table")
        assert display_result.is_success

        # Verify all files were created
        assert raw_file.exists()
        assert stats_file.exists()

    def test_batch_processing_scenario(self, mock_flext_core, temp_dir) -> None:
        """Test batch processing scenario with multiple formats."""
        api = CliApi()

        # Simulate batch data processing
        datasets = [
            ("users", [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]),
            ("products", [{"id": 101, "name": "Widget A"}, {"id": 102, "name": "Widget B"}]),
            ("orders", [{"id": 1001, "user_id": 1, "product_id": 101}]),
        ]

        # Process each dataset
        for dataset_name, data in datasets:
            # Export as JSON
            json_file = temp_dir / f"{dataset_name}.json"
            json_result = api.export(data, str(json_file), "json")
            assert json_result.is_success

            # Export as CSV (if data structure supports it)
            csv_file = temp_dir / f"{dataset_name}.csv"
            csv_result = api.export(data, str(csv_file), "csv")
            assert csv_result.is_success

            # Generate table format
            table_result = api.format_data(data, "table")
            assert table_result.is_success

        # Verify all files were created
        expected_files = [
            "users.json", "users.csv",
            "products.json", "products.csv",
            "orders.json", "orders.csv",
        ]

        for filename in expected_files:
            assert (temp_dir / filename).exists()

    def test_error_recovery_workflow(self, mock_flext_core, temp_dir) -> None:
        """Test error recovery in complex workflows."""
        api = CliApi()

        # Add a command that might fail
        def risky_operation(data):
            if not data:
                msg = "Empty data not allowed"
                raise ValueError(msg)
            return {"processed": len(data), "status": "success"}

        api.add_command("risky", risky_operation)

        # Test normal operation
        valid_data = [{"id": 1, "value": "test"}]
        success_result = api.execute("risky", valid_data)
        assert success_result.is_success

        # Test error handling
        error_result = api.execute("risky", [])
        assert not error_result.is_success
        assert "Empty data not allowed" in error_result.error

        # Continue with valid operations after error
        export_result = api.export(valid_data, str(temp_dir / "recovery_test.json"), "json")
        assert export_result.is_success

        # Verify that API state is not corrupted by the error
        health_result = api.health()
        assert health_result.is_success
        assert health_result.data["status"] == "healthy"

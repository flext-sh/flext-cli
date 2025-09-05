"""Functional tests for FlextCliDataProcessor using flext_tests patterns.

Real functionality tests without mocks, using flext_tests library for
advanced testing patterns and comprehensive coverage.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from flext_core import FlextResult
from flext_tests import (
    FlextMatchers,
    FlextTestUtilities,
    PerformanceProfiler,
    RealisticData,
    ValidationTestCases,
)

from flext_cli import FlextCliDataProcessing


class TestFlextCliDataProcessingFunctional:
    """Functional tests for FlextCliDataProcessing using real execution."""

    def setup_method(self) -> None:
        """Setup test environment with real processor instance."""
        self.processor = FlextCliDataProcessing()
        self.test_utils = FlextTestUtilities()
        self.realistic_data = RealisticData()
        self.validation_cases = ValidationTestCases()

    def test_data_processing_workflow_success(self) -> None:
        """Test complete data processing workflow with real data."""
        # Generate realistic test data using flext_tests
        test_data = [self.realistic_data.user_registration_data() for _ in range(3)]

        # Execute real data transformation (use existing method)
        result = self.processor.transform_data(test_data)

        # Validate using flext_tests matchers
        assert FlextMatchers.is_successful_result(result)
        processed_data = result.unwrap()
        assert isinstance(processed_data, list)
        assert len(processed_data) == 3

    def test_field_validation_with_realistic_data(self) -> None:
        """Test field validation using realistic validation cases."""
        # Test valid emails
        for valid_email in self.validation_cases.valid_email_cases():
            result = self.processor.execute("validate", field="email", value=valid_email)
            assert FlextMatchers.is_successful_result(result)

        # Test invalid emails
        for invalid_email in self.validation_cases.invalid_email_cases():
            result = self.processor.execute("validate", field="email", value=invalid_email)
            assert FlextMatchers.is_failed_result(result)

        # Test valid ages
        for valid_age in self.validation_cases.valid_ages():
            result = self.processor.execute("validate", field="age", value=valid_age)
            assert FlextMatchers.is_successful_result(result)

    def test_data_transformation_pipeline(self) -> None:
        """Test data transformation pipeline with real transformations."""
        # Create realistic data that needs transformation
        raw_data = [
            {"name": " Alice ", "age": "25", "active": "true"},
            {"name": " Bob ", "age": "30", "active": "false"},
            {"name": " Charlie ", "age": "35", "active": "true"},
        ]

        # Execute real transformation
        result = self.processor.transform_data_pipeline(
            data=raw_data,
            transformations=["strip_strings", "convert_types", "normalize"]
        )

        # Verify transformations worked
        assert FlextMatchers.is_successful_result(result)
        transformed_data = result.unwrap()

        assert transformed_data[0]["name"] == "Alice"  # Stripped
        assert isinstance(transformed_data[0]["age"], int)  # Converted
        assert isinstance(transformed_data[0]["active"], bool)  # Converted

    def test_batch_validation_performance(self) -> None:
        """Test batch validation performance using flext_tests profiler."""
        # Generate large dataset for performance testing
        large_dataset = [self.realistic_data.user_registration_data() for _ in range(100)]

        # Profile the batch validation with memory profiling
        profiler = PerformanceProfiler()
        profiler.profile_memory()

        result = self.processor.batch_validate(large_dataset)

        # Verify performance and functionality
        assert FlextMatchers.is_successful_result(result)
        profiler.assert_memory_efficient()  # Check memory usage

        validated_data = result.unwrap()
        assert len(validated_data) == 100

    def test_data_aggregation_real_sources(self) -> None:
        """Test data aggregation with real data sources."""
        # Create multiple data sources
        users_data = [
            {"id": 1, "name": "Alice", "department": "Engineering"},
            {"id": 2, "name": "Bob", "department": "Sales"},
        ]

        orders_data = [
            {"user_id": 1, "amount": 100.0, "product": "Widget"},
            {"user_id": 2, "amount": 150.0, "product": "Gadget"},
        ]

        # Execute real aggregation
        result = self.processor.aggregate_data(
            sources={"users": users_data, "orders": orders_data},
            join_key="user_id",
            strategy="inner_join"
        )

        # Validate aggregation results
        assert FlextMatchers.is_successful_result(result)
        aggregated_data = result.unwrap()

        assert len(aggregated_data) == 2
        assert aggregated_data[0]["name"] == "Alice"
        assert aggregated_data[0]["amount"] == 100.0

    def test_export_functionality_real_files(self) -> None:
        """Test export functionality with real file operations."""
        # Create test data
        test_data = [
            {"name": "Test User", "email": "test@example.com"},
            {"name": "Another User", "email": "another@example.com"},
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "test_export.json"

            # Execute real export
            result = self.processor.export_to_file(
                data=test_data,
                file_path=str(export_path),
                format="json"
            )

            # Verify export worked
            assert FlextMatchers.is_successful_result(result)
            assert export_path.exists()

            # Verify file contents
            with export_path.open() as f:
                exported_data = json.load(f)
            assert len(exported_data) == 2
            assert exported_data[0]["name"] == "Test User"

    def test_error_handling_real_scenarios(self) -> None:
        """Test error handling with real error scenarios."""
        # Test with invalid data types
        result = self.processor.execute("validate", field="age", value="not_a_number")
        assert FlextMatchers.is_failed_result(result)

        # Test with empty data
        result = self.processor.execute("transform", data=[])
        assert FlextMatchers.is_successful_result(result)  # Should handle empty data gracefully

        # Test with malformed data
        malformed_data = [{"incomplete": True}, None, {"malformed": "data"}]
        result = self.processor.transform_data_pipeline(malformed_data, ["validate"])
        # Should either succeed with filtered data or fail gracefully
        assert isinstance(result, FlextResult)

    def test_complex_workflow_integration(self) -> None:
        """Test complex workflow integration with multiple steps."""
        # Create complex test scenario using available methods
        complex_data = [
            self.realistic_data.user_registration_data(),
            self.realistic_data.order_data(),
            self.realistic_data.api_response_data()
        ]

        # Execute multi-step workflow
        result = self.processor.execute(
            "workflow",
            data=complex_data,
            steps=["validate", "transform"],
            config={
                "transformations": ["normalize", "clean"],
                "export_format": "json"
            }
        )

        # Verify complex workflow
        assert FlextMatchers.is_successful_result(result)
        final_result = result.unwrap()
        assert isinstance(final_result, (list, dict))


class TestFlextCliDataProcessingEdgeCases:
    """Test edge cases and boundary conditions."""

    def setup_method(self) -> None:
        """Setup for edge case testing."""
        self.processor = FlextCliDataProcessing()

    def test_empty_data_handling(self) -> None:
        """Test handling of empty data structures."""
        # Test empty list
        result = self.processor.transform_data([])
        assert FlextMatchers.is_successful_result(result)
        assert result.unwrap() == []

    def test_large_dataset_handling(self) -> None:
        """Test handling of large datasets."""
        # Create large dataset
        large_data = [{"id": i, "value": f"item_{i}"} for i in range(10000)]

        # Should handle large datasets without crashing
        result = self.processor.batch_validate(large_data)
        assert isinstance(result, FlextResult)

    def test_malformed_data_resilience(self) -> None:
        """Test resilience against malformed data."""
        malformed_data = [
            None,
            {"valid": "data"},
            "not_a_dict",
            {"missing_required": True},
            {"extra_field": "unexpected"}
        ]

        # Should handle malformed data gracefully
        result = self.processor.transform_data_pipeline(malformed_data, ["clean", "validate"])
        assert isinstance(result, FlextResult)


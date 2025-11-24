"""FLEXT CLI Railway Pattern Example Tests - Template for Railway Pattern Implementation.

This file serves as a comprehensive example of how to implement Railway Pattern
(FlextResult) testing following FLEXT standards and zero-tolerance methodology.

All tests use real functionality, comprehensive error handling, and complete
type safety without any mocks or type: ignore.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path
from typing import cast

import pytest
from flext_core import FlextResult

from flext_cli import FlextCli, FlextCliFileTools


class TestRailwayPatternExample:
    """Comprehensive Railway Pattern testing examples.

    This class demonstrates the correct patterns for testing with FlextResult
    railway pattern, including error handling, chaining, and validation.
    """

    @pytest.fixture
    def cli(self) -> FlextCli:
        """Create FlextCli instance for testing."""
        return FlextCli()

    @pytest.fixture
    def file_tools(self) -> FlextCliFileTools:
        """Create FlextCliFileTools instance for testing."""
        return FlextCliFileTools()

    @pytest.fixture
    def temp_dir(self) -> Generator[Path]:
        """Create temporary directory for file operations."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    # =========================================================================
    # PATTERN 1: Basic Railway Pattern with Success Path
    # =========================================================================

    def test_railway_pattern_basic_success(
        self,
        file_tools: FlextCliFileTools,
        temp_dir: Path,
    ) -> None:
        """Test basic Railway Pattern success path.

        Demonstrates:
        - FlextResult creation with .ok()
        - Method chaining with .map()
        - Success assertion with .is_success
        - Value unwrapping with .unwrap()
        """
        # Test data
        test_data = {"name": "test", "value": 42}
        test_file = temp_dir / "test.json"

        # Railway Pattern: Chain operations
        result: FlextResult[str] = (
            # Step 1: Start with success value
            FlextResult.ok(test_data)
            # Step 2: Transform data (add processing metadata)
            .map(lambda data: {**data, "processed": True, "timestamp": "2025-01-01"})
            # Step 3: Write to file
            .and_then(
                lambda data: file_tools.write_json_file(
                    str(test_file), cast("dict[str, object]", data)
                )
            )
            # Step 4: Convert to success message
            .map(lambda _: f"Successfully processed {len(test_data)} fields")
        )

        # Assertions following Railway Pattern
        assert result.is_success, f"Expected success but got: {result.error}"
        message = result.unwrap()
        assert "Successfully processed" in message
        assert "2 fields" in message

        # Verify file was created and contains correct data
        assert test_file.exists()
        read_result = file_tools.read_json_file(str(test_file))
        assert read_result.is_success
        read_data = cast("dict[str, object]", read_result.unwrap())
        assert read_data["processed"] is True
        assert read_data["timestamp"] == "2025-01-01"

    # =========================================================================
    # PATTERN 2: Railway Pattern with Error Handling
    # =========================================================================

    def test_railway_pattern_error_handling(
        self,
        file_tools: FlextCliFileTools,
    ) -> None:
        """Test Railway Pattern error handling.

        Demonstrates:
        - Error propagation through chain
        - Early failure handling
        - Error message validation
        - Chain interruption on failure
        """
        # Test with invalid file path
        invalid_path = "/nonexistent/directory/file.json"
        test_data = {"test": "data"}

        # Railway Pattern with potential failure
        result: FlextResult[str] = (
            FlextResult.ok(test_data)
            # This step will fail due to invalid path
            .and_then(
                lambda data: file_tools.write_json_file(
                    invalid_path, cast("dict[str, object]", data)
                )
            )
            # This step should never execute due to failure above
            .map(lambda _: "This should not execute")
        )

        # Error assertions
        assert result.is_failure, "Expected failure due to invalid file path"
        error_msg = result.error
        assert error_msg is not None
        assert "nonexistent" in error_msg or "No such file" in error_msg

    # =========================================================================
    # PATTERN 3: Railway Pattern with Validation Chain
    # =========================================================================

    def test_railway_pattern_validation_chain(
        self,
        file_tools: FlextCliFileTools,
        temp_dir: Path,
    ) -> None:
        """Test Railway Pattern with complex validation chain.

        Demonstrates:
        - Multiple validation steps
        - Custom validation functions
        - Error accumulation
        - Success path continuation
        """
        # Test data with validation requirements
        valid_data = {
            "name": "valid_name",
            "email": "test@example.com",
            "age": 25,
        }
        output_file = temp_dir / "validated.json"

        def validate_name(data: dict[str, object]) -> dict[str, object]:
            """Validate name field."""
            name = data.get("name")
            if not isinstance(name, str) or len(name) < 3:
                msg = "Name must be string with at least 3 characters"
                raise ValueError(msg)
            return {**data, "name_validated": True}

        def validate_email(data: dict[str, object]) -> dict[str, object]:
            """Validate email field."""
            email = data.get("email")
            if not isinstance(email, str) or "@" not in email:
                msg = "Invalid email format"
                raise ValueError(msg)
            return {**data, "email_validated": True}

        def validate_age(data: dict[str, object]) -> dict[str, object]:
            """Validate age field."""
            age = data.get("age")
            if not isinstance(age, int) or age < 18:
                msg = "Age must be integer >= 18"
                raise ValueError(msg)
            return {**data, "age_validated": True}

        # Railway Pattern validation chain
        result: FlextResult[dict[str, object]] = (
            FlextResult.ok(valid_data)
            # Validation chain
            .map(validate_name)
            .map(validate_email)
            .map(validate_age)
            # Success processing
            .map(lambda data: {**data, "validation_complete": True})
            # Save validated data
            .and_then(
                lambda data: file_tools.write_json_file(str(output_file), data).map(
                    lambda _: data
                )
            )
        )

        # Success assertions
        assert result.is_success, f"Validation failed: {result.error}"
        validated_data = result.unwrap()

        # Verify all validations passed
        assert validated_data.get("name_validated") is True
        assert validated_data.get("email_validated") is True
        assert validated_data.get("age_validated") is True
        assert validated_data.get("validation_complete") is True

        # Verify file was written
        assert output_file.exists()

    # =========================================================================
    # PATTERN 4: Railway Pattern with Recovery
    # =========================================================================

    def test_railway_pattern_error_recovery(
        self,
        file_tools: FlextCliFileTools,
        temp_dir: Path,
    ) -> None:
        """Test Railway Pattern with error recovery mechanisms.

        Demonstrates:
        - Error recovery patterns
        - Fallback strategies
        - Alternative execution paths
        """
        primary_file = temp_dir / "primary.json"
        fallback_file = temp_dir / "fallback.json"

        test_data = {"strategy": "recovery_test"}

        def attempt_primary_save(
            data: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            """Attempt primary save, may fail."""
            # Simulate primary failure
            if str(primary_file).endswith("primary.json"):
                return FlextResult.fail("Primary storage unavailable")

            return file_tools.write_json_file(str(primary_file), data).map(
                lambda _: data
            )

        def fallback_save(data: dict[str, object]) -> FlextResult[dict[str, object]]:
            """Fallback save mechanism."""
            return file_tools.write_json_file(str(fallback_file), data).map(
                lambda _: data
            )

        # Railway Pattern with recovery
        result: FlextResult[dict[str, object]] = (
            FlextResult.ok(cast("dict[str, object]", test_data))
            # Try primary save
            .and_then(attempt_primary_save)
            # If primary fails, try fallback
            .or_else_get(lambda: fallback_save(cast("dict[str, object]", test_data)))
        )

        # Should succeed via fallback
        assert result.is_success, f"Both primary and fallback failed: {result.error}"
        saved_data = result.unwrap()
        assert saved_data == test_data

        # Verify fallback file was created, primary was not
        assert not primary_file.exists(), "Primary file should not exist"
        assert fallback_file.exists(), "Fallback file should exist"

    # =========================================================================
    # PATTERN 5: Railway Pattern Integration Test
    # =========================================================================

    def test_railway_pattern_complex_workflow(
        self,
        cli: FlextCli,
        file_tools: FlextCliFileTools,
        temp_dir: Path,
    ) -> None:
        """Test complex workflow using Railway Pattern throughout.

        Demonstrates integration of multiple components using railway pattern.
        """
        # Test workflow: Load config -> Process data -> Generate report -> Save results
        config_file = temp_dir / "workflow_config.json"
        data_file = temp_dir / "input_data.json"
        report_file = temp_dir / "report.json"

        # Setup test files
        config_data = {"debug": True, "max_items": 100}
        input_data = [
            {"id": 1, "name": "Item A", "value": 10},
            {"id": 2, "name": "Item B", "value": 20},
            {"id": 3, "name": "Item C", "value": 30},
        ]

        # Pre-create files
        file_tools.write_json_file(str(config_file), config_data)
        file_tools.write_json_file(str(data_file), {"items": input_data})

        # Complex Railway Pattern workflow
        workflow_result: FlextResult[dict[str, object]] = (
            # Step 1: Load configuration
            file_tools.read_json_file(str(config_file))
            .flat_map(
                lambda config: FlextResult.ok(config)
                if isinstance(config, dict)
                else FlextResult.fail("Config must be dict")
            )
            .map(lambda config: (cli.print("✅ Config loaded"), config)[1])
            # Step 2: Load input data
            .and_then(
                lambda config: file_tools.read_json_file(str(data_file)).flat_map(
                    lambda data: FlextResult.ok((config, data))
                    if isinstance(data, dict)
                    else FlextResult.fail("Data must be dict")
                )
            )
            # Step 3: Process data with config
            .map(
                lambda config_data: self._process_workflow_data(
                    config_data[0], config_data[1]
                )
            )
            # Step 4: Generate report
            .map(self._generate_workflow_report)
            # Step 5: Save report
            .and_then(
                lambda report: file_tools.write_json_file(str(report_file), report).map(
                    lambda _: (cli.print("✅ Report saved"), report)[1]
                )
            )
        )

        # Assertions
        assert workflow_result.is_success, f"Workflow failed: {workflow_result.error}"
        final_report = workflow_result.unwrap()

        assert final_report["status"] == "completed"
        assert final_report["total_items"] == 3
        assert final_report["total_value"] == 60

        # Verify report file
        assert report_file.exists()

    def _process_workflow_data(
        self, config: dict[str, object], data: dict[str, object]
    ) -> dict[str, object]:
        """Process workflow data with configuration."""
        items = cast("list[object]", data.get("items", []))
        max_items = cast("int", config.get("max_items", 100))

        # Apply configuration constraints
        processed_items = items[:max_items] if isinstance(items, list) else []

        return {
            "config": config,
            "items": processed_items,
            "processed_at": "2025-01-01T00:00:00Z",
        }

    def _generate_workflow_report(
        self, processed_data: dict[str, object]
    ) -> dict[str, object]:
        """Generate workflow report from processed data."""
        items = cast("list[object]", processed_data.get("items", []))
        total_value = sum(
            cast("float", cast("dict[str, object]", item).get("value", 0))
            for item in items
            if isinstance(item, dict)
        )

        return {
            "status": "completed",
            "total_items": len(items),
            "total_value": total_value,
            "average_value": total_value / len(items) if items else 0,
            "processed_at": processed_data.get("processed_at"),
        }

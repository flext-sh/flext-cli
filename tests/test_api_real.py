"""REAL tests for API functionality - NO MOCKING!

Tests API functions with ACTUAL execution and real data processing.
Following user requirement: "melhore bem os tests para executar codigo de verdade
e validar a funcionalidade requerida, pare de ficar mockando tudo!"

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

from flext_cli import (
    FlextCliApi,
    flext_cli_aggregate_data,
    flext_cli_export,
    flext_cli_format,
    flext_cli_table,
    flext_cli_transform_data,
)


class TestFlextCliApiReal:
    """Test FlextCliApi with REAL functionality - NO MOCKS."""

    def test_api_initialization_real(self) -> None:
        """Test REAL API initialization without mocking."""
        api = FlextCliApi()

        # Should have real attributes (check what the API actually has)
        assert hasattr(api, "flext_cli_health"), "API should have health method"
        assert hasattr(api, "flext_cli_configure"), "API should have configure method"

        # Should be able to call real methods
        assert callable(api.flext_cli_health), "Health method should be callable"
        assert callable(api.flext_cli_configure), "Configure method should be callable"

    def test_api_health_real_execution(self) -> None:
        """Test REAL API health check execution."""
        api = FlextCliApi()

        # Call REAL health method
        health_data = api.flext_cli_health()

        # Should return real health data
        assert isinstance(health_data, dict), "Health should return dict"
        assert "service" in health_data, "Health should contain service info"
        assert "status" in health_data, "Health should contain status"
        assert "timestamp" in health_data, "Health should contain timestamp"

        # Should have expected values
        assert health_data["service"] == "flext-cli", "Service name should match"
        assert health_data["status"] == "healthy", "Status should be healthy"

    def test_api_configure_real_functionality(self) -> None:
        """Test REAL API configuration with actual config data."""
        api = FlextCliApi()

        # Test REAL configuration with actual data
        config_data = {
            "project_name": "test-real-project",
            "debug": True,
            "output_format": "json",
            "timeout": 60,
        }

        # Call REAL configure method
        result = api.flext_cli_configure(config_data)

        # Should succeed
        assert result is True, "Configuration should succeed"

        # Should have ACTUALLY configured the API
        assert hasattr(api, "_config"), "API should have config after configure"
        assert api._config.project_name == "test-real-project", (
            "Config should be applied"
        )


class TestFlextCliFormattingReal:
    """Test REAL formatting functions without mocking."""

    def test_format_json_real_data(self) -> None:
        """Test REAL JSON formatting with actual data."""
        test_data = {
            "users": [
                {"id": 1, "name": "Alice", "active": True},
                {"id": 2, "name": "Bob", "active": False},
            ],
            "total": 2,
            "metadata": {"version": "1.0", "timestamp": "2025-01-01"},
        }

        # Call REAL formatting function
        result = flext_cli_format(test_data, "json")

        # Should succeed
        assert result.is_success, f"JSON formatting should succeed: {result.error}"

        # Should produce ACTUAL JSON
        formatted = result.value
        assert isinstance(formatted, str), "Result should be string"

        # Should be VALID JSON that can be parsed back
        parsed = json.loads(formatted)
        assert parsed == test_data, "Parsed JSON should match original data"

    def test_format_table_real_data(self) -> None:
        """Test REAL table formatting with actual data."""
        test_data = [
            {"name": "Alice", "role": "Engineer", "years": 5},
            {"name": "Bob", "role": "Designer", "years": 3},
            {"name": "Carol", "role": "Manager", "years": 8},
        ]

        # Call REAL table formatting function
        result = flext_cli_table(test_data, "Team Roster")

        # Should succeed
        assert result.is_success, f"Table formatting should succeed: {result.error}"

        # Should produce ACTUAL Rich table
        table = result.value
        assert hasattr(table, "title"), "Should be a Rich table with title"
        assert str(table.title) == "Team Roster", "Table title should match"

    def test_aggregate_data_real_processing(self) -> None:
        """Test REAL data aggregation with actual processing."""
        sales_data = [
            {"region": "North", "product": "A", "sales": 1000, "units": 50},
            {"region": "North", "product": "B", "sales": 1500, "units": 75},
            {"region": "South", "product": "A", "sales": 800, "units": 40},
            {"region": "South", "product": "B", "sales": 1200, "units": 60},
            {"region": "North", "product": "A", "sales": 500, "units": 25},
        ]

        # Call REAL aggregation function
        result = flext_cli_aggregate_data(
            sales_data, group_by="region", sum_fields=["sales", "units"]
        )

        # Should succeed
        assert result.is_success, f"Aggregation should succeed: {result.error}"

        # Should produce ACTUAL aggregated data
        aggregated = result.value
        assert isinstance(aggregated, list), "Result should be list"
        assert len(aggregated) == 2, "Should have 2 regions"

        # Find North region data
        north_data = next(item for item in aggregated if item["region"] == "North")
        assert north_data["count"] == 3, "North should have 3 records"
        assert north_data["sales_sum"] == 3000, "North sales should be 3000"
        assert north_data["units_sum"] == 150, "North units should be 150"

    def test_transform_data_real_filtering(self) -> None:
        """Test REAL data transformation with actual filtering."""
        employee_data = [
            {"name": "Alice", "age": 30, "department": "Engineering", "salary": 75000},
            {"name": "Bob", "age": 25, "department": "Sales", "salary": 55000},
            {"name": "Carol", "age": 35, "department": "Engineering", "salary": 85000},
            {"name": "David", "age": 28, "department": "Marketing", "salary": 60000},
            {"name": "Eve", "age": 32, "department": "Engineering", "salary": 80000},
        ]

        # Test REAL filtering for engineers over 30
        result = flext_cli_transform_data(
            employee_data,
            filter_func=lambda x: x["department"] == "Engineering" and x["age"] > 30,
        )

        # Should succeed
        assert result.is_success, f"Transform should succeed: {result.error}"

        # Should produce ACTUAL filtered data
        filtered = result.value
        assert len(filtered) == 2, "Should have 2 engineers over 30"

        names = [person["name"] for person in filtered]
        # Alice is 30, so not > 30, only Carol (35) and Eve (32) should be included
        assert "Carol" in names, "Carol should be included"
        assert "Eve" in names, "Eve should be included"
        assert "Alice" not in names, "Alice should not be included (age 30, not > 30)"

    def test_export_real_file_operations(self) -> None:
        """Test REAL file export with actual file I/O."""
        export_data = {
            "project": "flext-cli-real-test",
            "results": [
                {"test": "auth", "status": "passed", "duration": 0.35},
                {"test": "api", "status": "passed", "duration": 0.28},
                {"test": "format", "status": "passed", "duration": 0.15},
            ],
            "summary": {"total": 3, "passed": 3, "failed": 0},
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "test_results.json"

            # Call REAL export function
            result = flext_cli_export(export_data, str(export_path), "json")

            # Should succeed
            assert result.is_success, f"Export should succeed: {result.error}"

            # Should have ACTUALLY created the file
            assert export_path.exists(), "Export file should exist"

            # Should contain ACTUAL data
            file_content = export_path.read_text(encoding="utf-8")
            parsed_content = json.loads(file_content)
            assert parsed_content == export_data, (
                "File content should match original data"
            )

            # Should have proper file size
            stat_info = export_path.stat()
            assert stat_info.st_size > 0, "File should not be empty"


class TestFlextCliRealWorldScenarios:
    """Test REAL-world scenarios with actual data processing workflows."""

    def test_complete_data_pipeline_real(self) -> None:
        """Test REAL complete data processing pipeline."""
        # Step 1: Raw data (simulating real API response)
        raw_data = [
            {
                "timestamp": "2025-01-15T10:00:00Z",
                "user": "alice",
                "action": "login",
                "duration": 1.2,
            },
            {
                "timestamp": "2025-01-15T10:05:00Z",
                "user": "bob",
                "action": "view",
                "duration": 0.8,
            },
            {
                "timestamp": "2025-01-15T10:10:00Z",
                "user": "alice",
                "action": "edit",
                "duration": 5.4,
            },
            {
                "timestamp": "2025-01-15T10:15:00Z",
                "user": "carol",
                "action": "login",
                "duration": 0.9,
            },
            {
                "timestamp": "2025-01-15T10:20:00Z",
                "user": "bob",
                "action": "edit",
                "duration": 3.2,
            },
            {
                "timestamp": "2025-01-15T10:25:00Z",
                "user": "alice",
                "action": "save",
                "duration": 1.1,
            },
        ]

        # Step 2: Transform - filter recent actions (REAL processing)
        transform_result = flext_cli_transform_data(
            raw_data,
            filter_func=lambda x: x["action"] in {"edit", "save"},
            sort_key="duration",
            reverse=True,  # Most time-consuming first
        )

        assert transform_result.is_success, "Transform should succeed"
        filtered_data = transform_result.value
        assert len(filtered_data) == 3, "Should have 3 edit/save actions"

        # Should be sorted by duration (descending)
        durations = [item["duration"] for item in filtered_data]
        assert durations == [5.4, 3.2, 1.1], "Should be sorted by duration desc"

        # Step 3: Aggregate by user (REAL aggregation)
        aggregate_result = flext_cli_aggregate_data(
            filtered_data, group_by="user", sum_fields=["duration"]
        )

        assert aggregate_result.is_success, "Aggregation should succeed"
        user_stats = aggregate_result.value
        assert len(user_stats) == 2, "Should have 2 users with edit/save actions"

        # Step 4: Format as table (REAL formatting)
        table_result = flext_cli_table(user_stats, "User Activity Summary")

        assert table_result.is_success, "Table formatting should succeed"
        table = table_result.value
        assert str(table.title) == "User Activity Summary", (
            "Table should have correct title"
        )

        # Step 5: Export to file (REAL file I/O)
        with tempfile.TemporaryDirectory() as temp_dir:
            export_path = Path(temp_dir) / "user_activity.json"
            export_result = flext_cli_export(user_stats, str(export_path), "json")

            assert export_result.is_success, "Export should succeed"
            assert export_path.exists(), "Export file should exist"

            # Verify ACTUAL file content
            file_data = json.loads(export_path.read_text(encoding="utf-8"))
            assert len(file_data) == 2, "File should contain 2 user records"

    def test_error_handling_real_scenarios(self) -> None:
        """Test REAL error handling without mocking errors."""
        # Test invalid data format
        invalid_result = flext_cli_format(
            "not a valid data structure", "invalid_format"
        )
        assert not invalid_result.is_success, "Should fail with invalid format"
        assert "error" in invalid_result.error.lower(), "Should have error message"

        # Test invalid export path
        invalid_export = flext_cli_export(
            {"test": "data"}, "/invalid/path/file.json", "json"
        )
        assert not invalid_export.success, "Should fail with invalid path"

        # Test invalid aggregation
        invalid_agg = flext_cli_aggregate_data("not a list", group_by="field")
        assert not invalid_agg.success, "Should fail with non-list data"
        assert "list" in invalid_agg.error.lower(), "Should mention list requirement"

    def test_performance_with_real_data(self) -> None:
        """Test REAL performance with larger datasets."""
        # Generate larger dataset for performance testing
        large_data = [
            {
                "id": i,
                "category": f"cat_{i % 10}",
                "value": i * 1.5,
                "enabled": i % 2 == 0,
            }
            for i in range(1000)
        ]

        # Test aggregation performance (REAL processing)
        agg_result = flext_cli_aggregate_data(
            large_data, group_by="category", sum_fields=["value"]
        )

        assert agg_result.is_success, "Large data aggregation should succeed"
        aggregated = agg_result.value
        assert len(aggregated) == 10, "Should have 10 categories"

        # Test formatting performance (REAL formatting)
        format_result = flext_cli_format(aggregated, "json")
        assert format_result.is_success, "Large data formatting should succeed"

        json_output = format_result.value
        assert len(json_output) > 500, "JSON output should be substantial"

        # Verify the JSON is ACTUALLY valid
        parsed = json.loads(json_output)
        assert len(parsed) == 10, "Parsed data should have 10 categories"

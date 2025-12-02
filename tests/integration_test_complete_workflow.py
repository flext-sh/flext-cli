"""FLEXT CLI Complete Workflow Integration Tests - 100% Coverage Target.

Comprehensive integration tests covering complete workflows from data ingestion
through processing to output generation, following Railway Pattern and FLEXT
standards with zero mocks and complete type safety.

Tests real file operations, configuration management, data transformation,
and output generation in integrated scenarios.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import json
import tempfile
import time
from collections.abc import Generator
from pathlib import Path
from typing import TypedDict, cast

import pytest
from flext_core import FlextResult, FlextTypes

from flext_cli import (
    FlextCli,
    FlextCliConfig,
    FlextCliConstants,
    FlextCliFileTools,
    FlextCliOutput,
    FlextCliTables,
)
from flext_cli.typings import FlextCliTypes


class FlextCliIntegrationTestTypes(FlextCliTypes):
    """Integration test specific types following FLEXT standards.

    Provides typed data structures for integration test workflows.
    """

    class Pipeline:
        """Pipeline data types for integration tests."""

        type ConfigDataPair = tuple[FlextCliConfig, dict[str, object]]
        """Tuple of configuration and data for pipeline processing."""

        type SalesData = dict[str, object]
        """Sales data structure with product, region, amount, quarter fields."""

        type ProcessedData = dict[str, object]
        """Processed sales data with aggregates and statistics."""

        class RecoveryReport(TypedDict):
            """Recovery report structure for failed workflows."""

            final_status: str
            data_source: object | None
            processing_recovered: object | None
            recovery_stats: object | None
            save_attempts: object | None
            total_records_processed: int
            recovery_timestamp: str


class TestCompleteWorkflowIntegration:
    """Complete workflow integration tests with 100% coverage target.

    Tests end-to-end scenarios combining multiple FLEXT-CLI components
    using Railway Pattern for error handling and real data processing.
    """

    @pytest.fixture
    def cli(self) -> FlextCli:
        """Create FlextCli instance for integration testing."""
        return FlextCli()

    @pytest.fixture
    def config(self) -> FlextCliConfig:
        """Create FlextCliConfig with test settings."""
        return FlextCliConfig(debug=True, environment="test")

    @pytest.fixture
    def file_tools(self) -> FlextCliFileTools:
        """Create FlextCliFileTools for file operations."""
        return FlextCliFileTools()

    @pytest.fixture
    def output(self) -> FlextCliOutput:
        """Create FlextCliOutput for formatted output."""
        return FlextCliOutput()

    @pytest.fixture
    def tables(self) -> FlextCliTables:
        """Create FlextCliTables for table formatting."""
        return FlextCliTables()

    @pytest.fixture
    def temp_workspace(self) -> Generator[Path]:
        """Create temporary workspace directory."""
        with tempfile.TemporaryDirectory() as workspace:
            yield Path(workspace)

    # =========================================================================
    # INTEGRATION TEST 1: Data Pipeline - Load → Transform → Save
    # =========================================================================

    def test_data_pipeline_load_transform_save(
        self,
        cli: FlextCli,
        file_tools: FlextCliFileTools,
        temp_workspace: Path,
    ) -> None:
        """Test complete data pipeline: load raw data, transform, save results.

        Covers: File I/O, data transformation, Railway Pattern chaining,
        error handling, and result validation.
        """
        # Setup test data
        input_file = temp_workspace / "raw_data.json"
        output_file = temp_workspace / "processed_data.json"
        report_file = temp_workspace / "pipeline_report.json"

        raw_data = {
            "users": [
                {
                    "id": 1,
                    "name": "Alice",
                    "email": "alice@example.com",
                    "active": True,
                },
                {"id": 2, "name": "Bob", "email": "bob@example.com", "active": False},
                {
                    "id": 3,
                    "name": "Charlie",
                    "email": "charlie@example.com",
                    "active": True,
                },
            ],
            "metadata": {"source": "test", "version": "1.0"},
        }

        # Pre-create input file
        file_tools.write_json_file(str(input_file), cast("dict[str, object]", raw_data))

        # Execute complete pipeline using Railway Pattern
        pipeline_result = cast(
            "FlextResult[dict[str, object]]",
            (
                # Step 1: Load raw data
                file_tools.read_json_file(str(input_file))
                .flat_map(
                    lambda data: FlextResult.ok(data)
                    if isinstance(data, dict)
                    else FlextResult.fail("Data must be dict")
                )
                .map(
                    lambda data: (cli.output.print_message("✅ Raw data loaded"), data)[
                        1
                    ]
                )
                # Step 2: Validate data structure
                .flat_map(self._validate_pipeline_data)
                .map(
                    lambda data: (
                        cli.output.print_message("✅ Data validation passed"),
                        data,
                    )[1]
                )
                # Step 3: Transform data (filter active users, enrich)
                .map(self._transform_pipeline_data)
                .map(
                    lambda data: (
                        cli.output.print_message("✅ Data transformation completed"),
                        data,
                    )[1]
                )
                # Step 4: Generate processing statistics
                .map(
                    lambda data: self._generate_pipeline_stats(
                        cast("dict[str, object]", data)
                    )
                )
                .map(
                    lambda data: (
                        cli.output.print_message("✅ Processing statistics generated"),
                        data,
                    )[1]
                )
                # Step 5: Save transformed data
                .flat_map(
                    lambda data: file_tools.write_json_file(str(output_file), data).map(
                        lambda _: (
                            cli.output.print_message("✅ Processed data saved"),
                            data,
                        )[1]
                    )
                )
                # Step 6: Generate and save pipeline report
                .map(self._create_pipeline_report)
                .flat_map(
                    lambda report: file_tools.write_json_file(
                        str(report_file), report
                    ).map(
                        lambda _: (
                            cli.output.print_message("✅ Pipeline report saved"),
                            report,
                        )[1]
                    )
                )
            ),
        )

        # Comprehensive assertions
        assert pipeline_result.is_success, f"Pipeline failed: {pipeline_result.error}"
        final_report = pipeline_result.unwrap()

        # Verify report structure
        assert (
            final_report["pipeline_status"]
            == FlextCliConstants.CommandStatus.COMPLETED.value
        )
        assert final_report["input_records"] == 3
        assert final_report["processed_records"] == 2  # Only active users
        assert final_report["success_rate"] == 1.0

        # Verify output files exist and contain correct data
        assert output_file.exists()
        assert report_file.exists()

        # Verify processed data
        processed_result = file_tools.read_json_file(str(output_file))
        assert processed_result.is_success
        processed_data = cast("dict[str, object]", processed_result.unwrap())

        assert len(cast("list[object]", processed_data["active_users"])) == 2
        assert all(
            cast("dict[str, object]", user)["is_premium"]
            for user in cast("list[object]", processed_data["active_users"])
        )

    def _validate_pipeline_data(self, data: object) -> FlextResult[object]:
        """Validate pipeline input data structure."""
        if not isinstance(data, dict):
            return FlextResult.fail("Data must be a dictionary")

        if "users" not in data:
            return FlextResult.fail("Missing 'users' field")

        users = data.get("users")
        if not isinstance(users, list):
            return FlextResult.fail("'users' must be a list")

        if len(users) == 0:
            return FlextResult.fail("Users list cannot be empty")

        # Validate each user
        for i, user in enumerate(users):
            if not isinstance(user, dict):
                return FlextResult.fail(f"User {i} must be a dictionary")

            required_fields = ["id", "name", "email", "active"]
            for field in required_fields:
                if field not in user:
                    return FlextResult.fail(f"User {i} missing required field: {field}")

        return cast("FlextResult[object]", FlextResult.ok(data))

    def _transform_pipeline_data(self, data: object) -> object:
        """Transform pipeline data: filter active users and enrich."""
        data_dict = cast("dict[str, object]", data)
        users = cast("list[object]", data_dict["users"])
        active_users = []

        for user in users:
            user_dict = cast("dict[str, object]", user)
            if user_dict["active"]:
                # Enrich active users
                enriched_user = dict(user_dict)
                enriched_user["is_premium"] = True
                enriched_user["last_login"] = "2025-01-01"
                enriched_user["account_status"] = "active"
                active_users.append(enriched_user)

        return {
            "active_users": active_users,
            "total_users": len(users),
            "active_count": len(active_users),
            "processed_at": "2025-01-01T12:00:00Z",
            "pipeline_version": "2.0",
        }

    def _generate_pipeline_stats(self, data: dict[str, object]) -> dict[str, object]:
        """Generate processing statistics."""
        active_users = cast("list[object]", data["active_users"])
        total_users = cast("int", data["total_users"])

        return {
            **data,
            "inactive_count": total_users - len(active_users),
            "processing_efficiency": len(active_users) / total_users
            if total_users > 0
            else 0,
            "average_name_length": sum(
                len(cast("str", cast("dict[str, object]", user)["name"]))
                for user in active_users
            )
            / len(active_users)
            if active_users
            else 0,
        }

    def _create_pipeline_report(self, data: object) -> object:
        """Create comprehensive pipeline report."""
        data_dict = cast("dict[str, object]", data)
        return {
            "pipeline_status": FlextCliConstants.CommandStatus.COMPLETED.value,
            "timestamp": cast("str", data_dict["processed_at"]),
            "pipeline_version": cast("str", data_dict["pipeline_version"]),
            "input_records": cast("int", data_dict["total_users"]),
            "processed_records": len(cast("list[object]", data_dict["active_users"])),
            "filtered_records": cast("int", data_dict["inactive_count"]),
            "success_rate": cast("float", data_dict["processing_efficiency"]),
            "processing_metrics": {
                "average_name_length": round(
                    cast("float", data_dict["average_name_length"]), 2
                ),
                "efficiency_percentage": round(
                    cast("float", data_dict["processing_efficiency"]) * 100, 2
                ),
            },
        }

    # =========================================================================
    # INTEGRATION TEST 2: Configuration-Driven Report Generation
    # =========================================================================

    def test_config_driven_report_generation(
        self,
        cli: FlextCli,
        config: FlextCliConfig,
        file_tools: FlextCliFileTools,
        tables: FlextCliTables,
        temp_workspace: Path,
    ) -> None:
        """Test configuration-driven report generation with multiple output formats.

        Covers: Configuration management, data processing, multiple output formats,
        table generation, and Railway Pattern integration.
        """
        # Setup test data and config
        data_file = temp_workspace / "sales_data.json"
        report_dir = temp_workspace / "reports"

        sales_data = {
            "sales": [
                {
                    "product": "Widget A",
                    "region": "North",
                    "amount": 1500.00,
                    "quarter": "Q1",
                },
                {
                    "product": "Widget B",
                    "region": "South",
                    "amount": 2200.50,
                    "quarter": "Q1",
                },
                {
                    "product": "Widget A",
                    "region": "North",
                    "amount": 1800.25,
                    "quarter": "Q2",
                },
                {
                    "product": "Widget C",
                    "region": "East",
                    "amount": 950.75,
                    "quarter": "Q2",
                },
            ]
        }

        # Create input data
        file_tools.write_json_file(
            str(data_file), cast("dict[str, object]", sales_data)
        )

        # Execute report generation pipeline
        report_result = cast(
            "FlextResult[dict[str, object]]",
            (
                # Step 1: Load configuration and data
                file_tools.read_json_file(str(data_file))
                .flat_map(
                    lambda data: FlextResult.ok((config, data))
                    if isinstance(data, dict)
                    else FlextResult.fail("Loaded data must be a dictionary")
                )
                # Step 2: Process sales data with config
                .map(
                    lambda config_data_pair: self._process_sales_with_config(
                        cast("tuple[object, object]", config_data_pair)[0],
                        cast("tuple[object, object]", config_data_pair)[1],
                    )
                )
                # Step 3: Generate multiple report formats
                .flat_map(
                    lambda processed: self._generate_multi_format_reports(
                        processed, report_dir, tables
                    )
                )
                # Step 4: Create report summary
                .map(
                    lambda reports: self._create_report_summary(
                        cast("list[dict[str, object]]", reports), config
                    )
                )
            ),
        )

        # Assertions
        assert report_result.is_success, (
            f"Report generation failed: {report_result.error}"
        )
        summary = report_result.unwrap()

        # Verify summary structure
        assert summary["total_reports"] == 3  # JSON, CSV, Table
        assert summary["total_sales"] == 6451.50
        assert summary["regions_covered"] == 3

        # Verify report files were created
        assert (report_dir / "sales_report.json").exists()
        assert (report_dir / "sales_report.csv").exists()
        assert (report_dir / "sales_report.txt").exists()

    def _process_sales_with_config(self, config: object, data: object) -> object:
        """Process sales data using configuration settings."""
        data_dict = cast("dict[str, object]", data)
        sales = data_dict.get("sales", [])
        if not isinstance(sales, list):
            msg = "Sales data must be a list"
            raise ValueError(msg)

        # Apply configuration-based filtering
        config_obj = cast("FlextCliConfig", config)
        if config_obj.environment == "production":
            # In production, only include Q1 data
            filtered_sales = [sale for sale in sales if sale.get("quarter") == "Q1"]
        else:
            # In other environments, include all data
            filtered_sales = sales

        # Calculate aggregates
        total_amount = sum(sale.get("amount", 0) for sale in filtered_sales)
        regions = list({
            sale.get("region") for sale in filtered_sales if sale.get("region")
        })

        return {
            "config": {
                "environment": config_obj.environment,
                "debug": config_obj.debug,
            },
            "sales_data": filtered_sales,
            "aggregates": {
                "total_amount": total_amount,
                "record_count": len(filtered_sales),
                "regions": regions,
                "average_sale": total_amount / len(filtered_sales)
                if filtered_sales
                else 0,
            },
            "processed_at": "2025-01-01T12:00:00Z",
        }

    def _generate_multi_format_reports(
        self,
        processed_data: object,
        report_dir: Path,
        tables: FlextCliTables,
    ) -> FlextResult[object]:
        """Generate reports in multiple formats."""
        processed_dict = cast("dict[str, object]", processed_data)
        report_dir.mkdir(exist_ok=True)
        sales_data = processed_dict.get("sales_data")
        aggregates = processed_dict.get("aggregates")

        reports = []

        # JSON Report
        json_report = {
            "report_type": "sales_summary",
            "generated_at": processed_dict.get("processed_at"),
            "summary": aggregates,
            "data": sales_data,
        }

        json_result = FlextCliFileTools().write_json_file(
            str(report_dir / "sales_report.json"),
            json_report,
        )
        if json_result.is_failure:
            return FlextResult.fail(f"JSON report failed: {json_result.error}")
        reports.append({
            "format": "json",
            "file": "sales_report.json",
            "status": "success",
        })

        # CSV Report - convert dict data to CSV format
        sales_list = cast("list[dict[str, object]]", sales_data)
        if sales_list:
            headers = ["Product", "Region", "Amount", "Quarter"]
            csv_rows = [headers]
            for sale in sales_list:
                row = [
                    str(sale.get("product", "")),
                    str(sale.get("region", "")),
                    str(sale.get("amount", 0)),
                    str(sale.get("quarter", "")),
                ]
                csv_rows.append(row)

            csv_result = FlextCliFileTools().write_csv_file(
                str(report_dir / "sales_report.csv"), csv_rows
            )
        else:
            csv_result = FlextResult.ok(True)  # No data to write
        if csv_result.is_failure:
            return FlextResult.fail(f"CSV report failed: {csv_result.error}")
        reports.append({
            "format": "csv",
            "file": "sales_report.csv",
            "status": "success",
        })

        # Table Report (ASCII)
        table_result = tables.create_table(cast("FlextTypes.JsonDict", sales_list))
        if table_result.is_success:
            table_content = table_result.unwrap()
            (report_dir / "sales_report.txt").write_text(table_content)
            reports.append({
                "format": "table",
                "file": "sales_report.txt",
                "status": "success",
            })
        else:
            return FlextResult.fail(f"Table report failed: {table_result.error}")

        return FlextResult.ok(cast("list[dict[str, object]]", reports))

    def _create_report_summary(
        self, reports: list[dict[str, object]], config: FlextCliConfig
    ) -> dict[str, object]:
        """Create comprehensive report summary."""
        # Load JSON report to get aggregates
        json_file = Path(tempfile.gettempdir()) / "reports" / "sales_report.json"
        if json_file.exists():
            json_data = json.loads(json_file.read_text())
            aggregates = json_data.get("summary", {})
        else:
            aggregates = {}

        return {
            "report_generation_status": FlextCliConstants.CommandStatus.COMPLETED.value,
            "total_reports": len(reports),
            "formats_generated": [r["format"] for r in reports],
            "config_used": {
                "environment": config.environment,
                "debug": config.debug,
            },
            "total_sales": aggregates.get("total_amount", 0),
            "regions_covered": len(aggregates.get("regions", [])),
            "generated_at": "2025-01-01T12:00:00Z",
        }

    # =========================================================================
    # INTEGRATION TEST 3: Error Recovery and Fallback Scenarios
    # =========================================================================

    def test_error_recovery_fallback_scenarios(
        self,
        cli: FlextCli,
        file_tools: FlextCliFileTools,
        temp_workspace: Path,
    ) -> None:
        """Test error recovery and fallback mechanisms in complete workflows.

        Covers: Error handling, fallback strategies, recovery patterns,
        and graceful degradation.
        """
        # Setup test scenario with multiple potential failure points
        primary_data_file = temp_workspace / "primary_data.json"
        backup_data_file = temp_workspace / "backup_data.json"
        output_file = temp_workspace / "processed_output.json"

        # Create backup data (valid)
        backup_data = {"users": [{"id": 1, "name": "Backup User", "active": True}]}
        file_tools.write_json_file(
            str(backup_data_file), cast("dict[str, object]", backup_data)
        )

        # Execute workflow with fallback mechanisms
        workflow_result = cast(
            "FlextResult[dict[str, object]]",
            (
                # Step 1: Try primary data source (will fail)
                self._load_data_with_fallback(primary_data_file, backup_data_file)
                .map(
                    lambda data: (
                        cli.output.print_message("✅ Data loaded (with fallback)"),
                        data,
                    )[1]
                )
                # Step 2: Process data (may have partial failures)
                .flat_map(
                    lambda data: cast(
                        "FlextResult[object]",
                        self._process_with_partial_recovery(
                            cast("dict[str, object]", data)
                        )
                        if isinstance(data, dict)
                        else FlextResult[dict[str, object]].fail("Invalid data type"),
                    )
                )
                .map(
                    lambda data: (
                        cli.output.print_message("✅ Data processed (with recovery)"),
                        data,
                    )[1]
                )
                # Step 3: Save results (with retry mechanism)
                .flat_map(
                    lambda data: cast(
                        "FlextResult[object]",
                        self._save_with_retry(
                            cast("dict[str, object]", data), output_file, max_retries=3
                        )
                        if isinstance(data, dict)
                        else FlextResult[dict[str, object]].fail("Invalid data type"),
                    )
                )
                .map(
                    lambda data: (
                        cli.output.print_message("✅ Results saved (with retry)"),
                        data,
                    )[1]
                )
                # Step 4: Generate recovery report
                .map(
                    lambda data: self._generate_recovery_report(
                        cast("dict[str, object]", data)
                    )
                    if isinstance(data, dict)
                    else {}
                )
            ),
        )

        # Assertions
        assert workflow_result.is_success, (
            f"Workflow with recovery failed: {workflow_result.error}"
        )
        recovery_report = cast(
            "FlextCliIntegrationTestTypes.Pipeline.RecoveryReport",
            workflow_result.unwrap(),
        )

        # Verify recovery mechanisms worked
        assert recovery_report["data_source"] == "backup"  # Fell back to backup
        assert (
            recovery_report["processing_recovered"] is True
        )  # Partial recovery worked
        save_attempts = cast("int", recovery_report["save_attempts"])
        assert save_attempts >= 1  # At least one save attempt
        assert recovery_report["final_status"] == "completed_with_recovery"

        # Verify output file exists
        assert output_file.exists()

    def _load_data_with_fallback(
        self, primary_file: Path, backup_file: Path
    ) -> FlextResult[dict[str, object]]:
        """Load data with fallback mechanism."""
        # Try primary first (will fail since file doesn't exist)
        primary_result = FlextCliFileTools().read_json_file(str(primary_file))

        if primary_result.is_success:
            return cast(
                "FlextResult[dict[str, object]]",
                primary_result.map(
                    lambda data: {
                        **cast("dict[str, object]", data),
                        "data_source": "primary",
                    }
                ),
            )

        # Fallback to backup
        backup_result = FlextCliFileTools().read_json_file(str(backup_file))
        if backup_result.is_failure:
            return FlextResult.fail(
                f"Both primary and backup failed: {backup_result.error}"
            )

        return cast(
            "FlextResult[dict[str, object]]",
            backup_result.map(
                lambda data: {
                    **cast("dict[str, object]", data),
                    "data_source": "backup",
                }
            ),
        )

    def _process_with_partial_recovery(
        self, data: dict[str, object]
    ) -> FlextResult[dict[str, object]]:
        """Process data with partial recovery for corrupted records."""
        users = data.get("users", [])
        if not isinstance(users, list):
            return FlextResult.fail("Users data must be a list")

        processed_users = []
        recovery_info = {"recovered": 0, "failed": 0}

        for i, user in enumerate(users):
            try:
                processed_user = self._process_single_user(user)
                processed_users.append(processed_user)
            except Exception as e:
                # Recovery: Create minimal valid user record
                recovered_user = {
                    "id": user.get("id", f"recovered_{i}"),
                    "name": user.get("name", f"Recovered User {i}"),
                    "active": False,
                    "recovered": True,
                    "original_error": str(e),
                }
                processed_users.append(recovered_user)
                recovery_info["recovered"] += 1
            else:
                recovery_info["failed"] += 1

        return FlextResult.ok({
            **data,
            "processed_users": processed_users,
            "processing_recovered": True,
            "recovery_stats": recovery_info,
        })

    def _process_single_user(self, user: dict[str, object]) -> dict[str, object]:
        """Process a single user record with validation."""
        if not isinstance(user, dict):
            msg = "User must be a dictionary"
            raise ValueError(msg)

        required_fields = ["id", "name"]
        for field in required_fields:
            if field not in user:
                raise ValueError(f"Missing required field: {field}")

        # Add processing metadata
        return {
            **user,
            "processed": True,
            "processed_at": "2025-01-01T12:00:00Z",
        }

    def _save_with_retry(
        self, data: dict[str, object], output_file: Path, max_retries: int = 3
    ) -> FlextResult[dict[str, object]]:
        """Save data with retry mechanism."""
        attempts = 0
        last_error = None

        while attempts < max_retries:
            attempts += 1
            result = FlextCliFileTools().write_json_file(str(output_file), data)

            if result.is_success:
                return FlextResult.ok({**data, "save_attempts": attempts})

            last_error = result.error

            # Simulate transient failure recovery
            if attempts < max_retries:
                time.sleep(0.01)  # Brief delay before retry

        return FlextResult.fail(
            f"Save failed after {max_retries} attempts: {last_error}"
        )

    def _generate_recovery_report(self, data: dict[str, object]) -> dict[str, object]:
        """Generate comprehensive recovery report."""
        return {
            "final_status": "completed_with_recovery",
            "data_source": data.get("data_source"),
            "processing_recovered": data.get("processing_recovered"),
            "recovery_stats": data.get("recovery_stats"),
            "save_attempts": data.get("save_attempts"),
            "total_records_processed": len(
                cast("list[object]", data.get("processed_users", []))
            ),
            "recovery_timestamp": "2025-01-01T12:00:00Z",
        }

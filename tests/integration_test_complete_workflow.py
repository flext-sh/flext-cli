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
import math
import tempfile
import time
from collections.abc import Generator, Mapping
from pathlib import Path
from typing import TypedDict

import pytest
from flext_cli import (
    FlextCli,
    FlextCliFileTools,
    FlextCliOutput,
    FlextCliSettings,
    FlextCliTables,
    c,
    r,
    t,
    u,
)


class FlextCliIntegrationTestTypes(t):
    """Integration test specific types following FLEXT standards.

    Provides typed data structures for integration test workflows.
    """

    class Pipeline:
        """Pipeline data types for integration tests."""

        type ConfigDataPair = tuple[FlextCliSettings, dict[str, t.GeneralValueType]]
        """Tuple of configuration and data for pipeline processing."""

        type SalesData = dict[str, t.GeneralValueType]
        """Sales data structure with product, region, amount, quarter fields."""

        type ProcessedData = dict[str, t.GeneralValueType]
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
    def config(self) -> FlextCliSettings:
        """Create FlextCliSettings with test settings."""
        return FlextCliSettings(debug=True)

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
        _ = file_tools.write_json_file(
            str(input_file),
            raw_data,
        )

        # Execute complete pipeline using Railway Pattern (direct typing via models)
        pipeline_result: r[PipelineReport] = (
            file_tools.read_json_file(str(input_file))
            .flat_map(lambda data: r.from_validation(data, PipelineInput))
            .map(
                lambda data: (cli.output.print_message("✅ Raw data loaded"), data)[1],
            )
            .map(self._transform_pipeline_data)
            .map(
                lambda data: (
                    cli.output.print_message("✅ Data transformation completed"),
                    data,
                )[1],
            )
            .map(self._generate_pipeline_stats)
            .map(
                lambda data: (
                    cli.output.print_message("✅ Processing statistics generated"),
                    data,
                )[1],
            )
            .flat_map(
                lambda data: file_tools.write_json_file(
                    str(output_file),
                    data.model_dump(),
                ).map(
                    lambda _: (
                        cli.output.print_message("✅ Processed data saved"),
                        data,
                    )[1],
                ),
            )
            .map(self._create_pipeline_report)
            .flat_map(
                lambda report: file_tools.write_json_file(
                    str(report_file),
                    report.model_dump(),
                ).map(
                    lambda _: (
                        cli.output.print_message("✅ Pipeline report saved"),
                        report,
                    )[1],
                ),
            )
        )

        # Assertions (direct attribute access; no dict/isinstance)
        assert pipeline_result.is_success, f"Pipeline failed: {pipeline_result.error}"
        final_report = pipeline_result.value

        assert final_report.pipeline_status == c.Cli.CommandStatus.COMPLETED.value
        assert final_report.input_records == 3
        assert final_report.processed_records == 2
        assert math.isclose(final_report.success_rate, 1.0)

        assert output_file.exists()
        assert report_file.exists()

        # Verify processed data via model validation (existing API)
        loaded = file_tools.read_json_file(str(output_file))
        assert loaded.is_success
        processed_data = ProcessedPipelineData.model_validate(loaded.value)
        assert len(processed_data.active_users) == 2
        for user in processed_data.active_users:
            assert user.is_premium is True

    def _transform_pipeline_data(self, data: PipelineInput) -> ProcessedPipelineData:
        """Transform pipeline data: filter active users and enrich (typed; no dict)."""
        active: list[PipelineEnrichedUser] = []
        for user in data.users:
            if user.active:
                active.append(
                    PipelineEnrichedUser(
                        id=user.id,
                        name=user.name,
                        email=user.email,
                        active=user.active,
                        is_premium=True,
                        last_login="2025-01-01",
                        account_status="active",
                    )
                )
        return ProcessedPipelineData(
            active_users=active,
            total_users=len(data.users),
            active_count=len(active),
            processed_at="2025-01-01T12:00:00Z",
            pipeline_version="2.0",
        )

    def _generate_pipeline_stats(
        self, data: ProcessedPipelineData
    ) -> ProcessedPipelineData:
        """Add processing statistics (typed)."""
        total = data.total_users
        active_count = len(data.active_users)
        efficiency = active_count / total if total > 0 else 0.0
        name_lengths = [len(u.name) for u in data.active_users]
        avg_name = (
            sum(name_lengths) / len(name_lengths) if name_lengths else 0.0
        )
        return data.model_copy(
            update={
                "inactive_count": total - active_count,
                "processing_efficiency": efficiency,
                "average_name_length": avg_name,
            }
        )

    def _create_pipeline_report(
        self, data: ProcessedPipelineData
    ) -> PipelineReport:
        """Build pipeline report from processed data (typed)."""
        processed_records = len(data.active_users)
        success_rate = 1.0 if processed_records > 0 else 0.0
        avg_len = data.average_name_length if data.average_name_length is not None else 0.0
        eff = data.processing_efficiency if data.processing_efficiency is not None else 0.0
        return PipelineReport(
            pipeline_status=c.Cli.CommandStatus.COMPLETED.value,
            timestamp=data.processed_at,
            pipeline_version=data.pipeline_version,
            input_records=data.total_users,
            processed_records=processed_records,
            filtered_records=data.inactive_count,
            success_rate=success_rate,
            processing_metrics=ProcessingMetrics(
                average_name_length=round(avg_len, 2),
                efficiency_percentage=round(eff * 100.0, 2),
            ),
        )

    # =========================================================================
    # INTEGRATION TEST 2: Configuration-Driven Report Generation
    # =========================================================================

    def test_config_driven_report_generation(
        self,
        cli: FlextCli,
        config: FlextCliSettings,
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

        sales_data: dict[str, t.GeneralValueType] = {
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
            ],
        }

        # Create input data
        _ = file_tools.write_json_file(
            str(data_file),
            sales_data,
        )

        # Execute report generation pipeline
        report_result = (
            # Step 1: Load configuration and data
            file_tools
            .read_json_file(str(data_file))
            .flat_map(
                lambda data: (
                    r.ok((config, data))
                    if isinstance(data, dict)
                    else r.fail("Loaded data must be a dictionary")
                ),
            )
            # Step 2: Process sales data with config
            .map(
                lambda config_data_pair: self._process_sales_with_config(
                    config_data_pair[0],
                    config_data_pair[1],
                ),
            )
            # Step 3: Generate multiple report formats
            .flat_map(
                lambda processed: self._generate_multi_format_reports(
                    processed,
                    report_dir,
                    tables,
                ),
            )
            # Step 4: Create report summary
            .map(
                lambda reports: self._create_report_summary(
                    reports if isinstance(reports, list) else [],
                    config,
                    report_dir,
                ),
            )
        )

        # Assertions
        assert report_result.is_success, (
            f"Report generation failed: {report_result.error}"
        )
        summary = report_result.value
        assert isinstance(summary, dict)

        # Verify summary structure
        assert summary["total_reports"] == 3  # JSON, CSV, Table
        total_sales_val = summary.get("total_sales")
        assert isinstance(total_sales_val, (int, float))
        assert math.isclose(float(total_sales_val), 6451.50)
        assert summary["regions_covered"] == 3

        # Verify report files were created
        assert (report_dir / "sales_report.json").exists()
        assert (report_dir / "sales_report.csv").exists()
        assert (report_dir / "sales_report.txt").exists()

    def _process_sales_with_config(self, config: object, data: object) -> object:
        """Process sales data using configuration settings."""
        if not isinstance(data, dict):
            msg = "Data must be a dict"
            raise ValueError(msg)
        data_dict = data
        sales = data_dict.get("sales", [])
        if not isinstance(sales, list):
            msg = "Sales data must be a list"
            raise ValueError(msg)

        # Apply configuration-based filtering
        if not isinstance(config, FlextCliSettings):
            msg = "Config must be FlextCliSettings"
            raise ValueError(msg)
        config_obj = config
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
    ) -> r[object]:
        """Generate reports in multiple formats."""
        assert isinstance(processed_data, dict)
        processed_dict = processed_data
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
            return r.fail(f"JSON report failed: {json_result.error}")
        reports.append({
            "format": "json",
            "file": "sales_report.json",
            "status": "success",
        })

        # CSV Report - convert dict data to CSV format
        sales_list = sales_data if isinstance(sales_data, list) else []
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
                str(report_dir / "sales_report.csv"),
                csv_rows,
            )
        else:
            csv_result = r.ok(True)  # No data to write
        if csv_result.is_failure:
            return r.fail(f"CSV report failed: {csv_result.error}")
        reports.append({
            "format": "csv",
            "file": "sales_report.csv",
            "status": "success",
        })

        # Table Report (ASCII)
        table_result = tables.create_table(
            sales_list,
        )
        if table_result.is_success:
            table_content = table_result.value
            _ = (report_dir / "sales_report.txt").write_text(table_content)
            reports.append({
                "format": "table",
                "file": "sales_report.txt",
                "status": "success",
            })
        else:
            return r.fail(f"Table report failed: {table_result.error}")

        return r.ok(reports)

    def _create_report_summary(
        self,
        reports: list[dict[str, t.GeneralValueType]],
        config: FlextCliSettings,
        report_dir: Path,
    ) -> Mapping[str, object]:
        """Create comprehensive report summary."""
        # Load JSON report to get aggregates
        json_file = report_dir / "sales_report.json"
        if json_file.exists():
            json_data = json.loads(json_file.read_text())
            aggregates = json_data.get("summary", {})
        else:
            aggregates = {}
        if not isinstance(aggregates, dict):
            aggregates = {}
        regions_val = aggregates.get("regions", [])
        regions_len = len(regions_val) if isinstance(regions_val, (list, tuple)) else 0

        return {
            "report_generation_status": c.Cli.CommandStatus.COMPLETED.value,
            "total_reports": len(reports),
            "formats_generated": [item["format"] for item in reports],
            "config_used": {
                "environment": config.environment,
                "debug": config.debug,
            },
            "total_sales": aggregates.get("total_amount", 0),
            "regions_covered": regions_len,
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
        backup_data: t.GeneralValueType = {
            "users": [{"id": 1, "name": "Backup User", "active": True}],
        }
        _ = file_tools.write_json_file(
            str(backup_data_file),
            backup_data,
        )

        # Execute workflow with fallback mechanisms
        workflow_result = (
            # Step 1: Try primary data source (will fail)
            self
            ._load_data_with_fallback(primary_data_file, backup_data_file)
            .map(
                lambda data: (
                    cli.output.print_message("✅ Data loaded (with fallback)"),
                    data,
                )[1],
            )
            # Step 2: Process data (may have partial failures)
            .flat_map(self._process_with_partial_recovery)
            .map(
                lambda data: (
                    cli.output.print_message("✅ Data processed (with recovery)"),
                    data,
                )[1],
            )
            # Step 3: Save results (with retry mechanism)
            .flat_map(lambda data: self._save_with_retry(data, output_file, max_retries=3))
            .map(
                lambda data: (
                    cli.output.print_message("✅ Results saved (with retry)"),
                    data,
                )[1],
            )
            # Step 4: Generate recovery report
            .map(self._generate_recovery_report)
        )

        # Assertions
        assert workflow_result.is_success, (
            f"Workflow with recovery failed: {workflow_result.error}"
        )
        recovery_report = workflow_result.value
        assert isinstance(recovery_report, dict)

        # Verify recovery mechanisms worked
        assert recovery_report["data_source"] == "backup"  # Fell back to backup
        assert (
            recovery_report["processing_recovered"] is True
        )  # Partial recovery worked
        save_attempts_val = recovery_report.get("save_attempts")
        assert isinstance(save_attempts_val, (int, float))
        assert save_attempts_val >= 1  # At least one save attempt
        assert recovery_report["final_status"] == "completed_with_recovery"

        # Verify output file exists
        assert output_file.exists()

    def _load_data_with_fallback(
        self,
        primary_file: Path,
        backup_file: Path,
    ) -> r[Mapping[str, t.GeneralValueType]]:
        """Load data with fallback mechanism."""
        # Try primary first (will fail since file doesn't exist)
        primary_result = FlextCliFileTools().read_json_file(str(primary_file))

        if primary_result.is_success:
            def _merge_primary(data: t.GeneralValueType) -> Mapping[str, t.GeneralValueType]:
                base = data if isinstance(data, dict) else {}
                return {**base, "data_source": "primary"}

            return primary_result.map(_merge_primary)

        # Fallback to backup
        backup_result = FlextCliFileTools().read_json_file(str(backup_file))
        if backup_result.is_failure:
            return r.fail(f"Both primary and backup failed: {backup_result.error}")

        def _merge_backup(data: t.GeneralValueType) -> Mapping[str, t.GeneralValueType]:
            base = data if isinstance(data, dict) else {}
            return {**base, "data_source": "backup"}

        return backup_result.map(_merge_backup)

    def _process_with_partial_recovery(
        self,
        data: Mapping[str, t.GeneralValueType],
    ) -> r[dict[str, t.GeneralValueType]]:
        """Process data with partial recovery for corrupted records."""
        users = data.get("users", [])
        if not isinstance(users, list):
            return r.fail("Users data must be a list")

        processed_users: list[dict[str, t.GeneralValueType]] = []
        recovery_info = {"recovered": 0, "failed": 0}

        for i, user in enumerate(users):
            if not isinstance(user, dict):
                recovery_info["recovered"] += 1
                processed_users.append({
                    "id": f"recovered_{i}",
                    "name": f"Recovered User {i}",
                    "active": False,
                    "recovered": True,
                })
                continue
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

        return r.ok({
            **data,
            "processed_users": processed_users,
            "processing_recovered": True,
            "recovery_stats": recovery_info,
        })

    def _process_single_user(
        self, user: Mapping[str, t.GeneralValueType]
    ) -> dict[str, t.GeneralValueType]:
        """Process a single user record with validation."""
        required_fields = ["id", "name"]
        for field in required_fields:
            if field not in user:
                raise ValueError(f"Missing required field: {field}")

        # Add processing metadata (new dict so return type is explicit)
        result: dict[str, t.GeneralValueType] = {}
        for k, v in user.items():
            result[k] = v
        result["processed"] = True
        result["processed_at"] = "2025-01-01T12:00:00Z"
        return result

    def _save_with_retry(
        self,
        data: dict[str, t.GeneralValueType],
        output_file: Path,
        max_retries: int = 3,
    ) -> r[dict[str, t.GeneralValueType]]:
        """Save data with retry mechanism."""
        attempts = 0
        last_error = None

        while attempts < max_retries:
            attempts += 1
            result = FlextCliFileTools().write_json_file(
                str(output_file),
                data,
            )

            if result.is_success:
                return r.ok({**data, "save_attempts": attempts})

            last_error = result.error

            # Simulate transient failure recovery
            if attempts < max_retries:
                time.sleep(0.01)  # Brief delay before retry

        return r.fail(f"Save failed after {max_retries} attempts: {last_error}")

    def _generate_recovery_report(
        self,
        data: dict[str, t.GeneralValueType],
    ) -> Mapping[str, object]:
        """Generate comprehensive recovery report."""
        processed_users_val = data.get("processed_users")
        count = len(processed_users_val) if isinstance(processed_users_val, list) else 0
        return {
            "final_status": "completed_with_recovery",
            "data_source": data.get("data_source"),
            "processing_recovered": data.get("processing_recovered"),
            "recovery_stats": data.get("recovery_stats"),
            "save_attempts": data.get("save_attempts"),
            "total_records_processed": count,
            "recovery_timestamp": "2025-01-01T12:00:00Z",
        }
 return r.ok({**data, "save_attempts": attempts})

            last_error = result.error

            # Simulate transient failure recovery
            if attempts < max_retries:
                time.sleep(0.01)  # Brief delay before retry

        return r.fail(f"Save failed after {max_retries} attempts: {last_error}")

    def _generate_recovery_report(
        self,
        data: dict[str, t.GeneralValueType],
    ) -> Mapping[str, object]:
        """Generate comprehensive recovery report."""
        processed_users_val = data.get("processed_users")
        count = len(processed_users_val) if isinstance(processed_users_val, list) else 0
        return {
            "final_status": "completed_with_recovery",
            "data_source": data.get("data_source"),
            "processing_recovered": data.get("processing_recovered"),
            "recovery_stats": data.get("recovery_stats"),
            "save_attempts": data.get("save_attempts"),
            "total_records_processed": count,
            "recovery_timestamp": "2025-01-01T12:00:00Z",
        }

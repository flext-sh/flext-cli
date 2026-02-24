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
)
from pydantic import ValidationError

from tests.helpers._impl import _is_json_dict, _is_json_list


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

        # Execute complete pipeline using Railway Pattern
        pipeline_result = (
            file_tools.read_json_file(str(input_file))
            .flat_map(self._validate_pipeline_data)
            .map(self._transform_pipeline_data)
            .map(self._generate_pipeline_stats)
            .flat_map(
                lambda data: file_tools.write_json_file(
                    str(output_file),
                    data,
                ).map(lambda _: data),
            )
            .map(self._create_pipeline_report_from_data)
            .flat_map(
                lambda report: file_tools.write_json_file(
                    str(report_file),
                    report,
                ).map(lambda _: report),
            )
        )

        # Assertions
        assert pipeline_result.is_success, f"Pipeline failed: {pipeline_result.error}"
        final_report = pipeline_result.value

        assert _is_json_dict(final_report)
        assert final_report["pipeline_status"] == c.Cli.CommandStatus.COMPLETED.value
        assert final_report["input_records"] == 3
        assert final_report["processed_records"] == 2
        success_rate_val = final_report.get("success_rate")
        assert isinstance(success_rate_val, (int, float))
        assert math.isclose(float(success_rate_val), 1.0)

        assert output_file.exists()
        assert report_file.exists()

        # Verify processed data
        loaded = file_tools.read_json_file(str(output_file))
        assert loaded.is_success
        processed_data = loaded.value
        assert _is_json_dict(processed_data)
        active_users_val = processed_data.get("active_users")
        assert _is_json_list(active_users_val)
        assert len(active_users_val) == 2
        for user in active_users_val:
            if _is_json_dict(user):
                assert user.get("is_premium") is True

    def _validate_pipeline_data(
        self, data: object
    ) -> r[dict[str, t.GeneralValueType]]:
        """Validate pipeline input; use TypeGuard for dict/list, no Pydantic models."""
        if not _is_json_dict(data):
            return r.fail("Data must be a dictionary")
        data_dict = data
        if "users" not in data_dict:
            return r.fail("Missing 'users' field")
        users = data_dict.get("users", [])
        if not _is_json_list(users):
            return r.fail("'users' must be a list")
        if not users:
            return r.fail("Users list cannot be empty")
        for i, user in enumerate(users):
            if not _is_json_dict(user):
                return r.fail(f"User {i} must be a dictionary")
            for field in ("id", "name", "email", "active"):
                if field not in user:
                    return r.fail(f"User {i} missing required field: {field}")
        return r.ok(data_dict)

    def _transform_pipeline_data(
        self,
        data: dict[str, t.GeneralValueType],
    ) -> dict[str, t.GeneralValueType]:
        """Transform pipeline data: filter active users and enrich."""
        users_raw = data.get("users", [])
        if not _is_json_list(users_raw):
            return {
                "active_users": [],
                "total_users": 0,
                "active_count": 0,
                "processed_at": "2025-01-01T12:00:00Z",
                "pipeline_version": "2.0",
            }
        active_users: list[dict[str, t.GeneralValueType]] = []
        for user in users_raw:
            if not _is_json_dict(user):
                continue
            if user.get("active"):
                enriched = dict(user)
                enriched["is_premium"] = True
                enriched["last_login"] = "2025-01-01"
                enriched["account_status"] = "active"
                active_users.append(enriched)
        return {
            "active_users": active_users,
            "total_users": len(users_raw),
            "active_count": len(active_users),
            "processed_at": "2025-01-01T12:00:00Z",
            "pipeline_version": "2.0",
        }

    def _generate_pipeline_stats(
        self,
        data: dict[str, t.GeneralValueType],
    ) -> dict[str, t.GeneralValueType]:
        """Add processing statistics to pipeline data."""
        total = data.get("total_users", 0)
        active_raw = data.get("active_users", [])
        if not _is_json_list(active_raw):
            return {**data, "error": "active_users must be list"}
        if not isinstance(total, int):
            return {**data, "error": "total_users must be int"}
        active_count = len(active_raw)
        name_lengths = [
            len(str(u.get("name", "")))
            for u in active_raw
            if _is_json_dict(u)
        ]
        avg_name = (
            sum(name_lengths) / len(name_lengths) if name_lengths else 0.0
        )
        return {
            **data,
            "inactive_count": total - active_count,
            "processing_efficiency": active_count / total if total > 0 else 0.0,
            "average_name_length": avg_name,
        }

    def _create_pipeline_report_from_data(
        self,
        data: dict[str, t.GeneralValueType],
    ) -> dict[str, t.GeneralValueType]:
        """Build pipeline report dict from processed data."""
        active_raw = data.get("active_users", [])
        processed_records = (
            len(active_raw)
            if _is_json_list(active_raw)
            else 0
        )
        total = data.get("total_users", 0)
        return {
            "pipeline_status": c.Cli.CommandStatus.COMPLETED.value,
            "timestamp": data.get("processed_at", ""),
            "pipeline_version": data.get("pipeline_version", ""),
            "input_records": total if isinstance(total, int) else 0,
            "processed_records": processed_records,
            "filtered_records": data.get("inactive_count", 0),
            "success_rate": 1.0 if processed_records > 0 else 0.0,
        }

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
                    if _is_json_dict(data)
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
                    reports if _is_json_list(reports) else [],
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
        assert _is_json_dict(summary)

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
        if not _is_json_dict(data):
            msg = "Data must be a dict"
            raise ValueError(msg)
        data_dict = data
        sales = data_dict.get("sales", [])
        if not _is_json_list(sales):
            msg = "Sales data must be a list"
            raise ValueError(msg)
        sales_dicts: list[dict[str, t.JsonValue]] = [
            s for s in sales if _is_json_dict(s)
        ]

        # Apply configuration-based filtering (single isinstance to reject non-FlextCliSettings)
        if not isinstance(config, FlextCliSettings):
            msg = "Config must be FlextCliSettings"
            raise ValueError(msg)
        config_obj = config
        if config_obj.environment == "production":
            filtered_sales: list[dict[str, t.JsonValue]] = [
                s for s in sales_dicts if s.get("quarter") == "Q1"
            ]
        else:
            filtered_sales = sales_dicts

        # Calculate aggregates (narrow amount to int/float for sum)
        total_amount = 0.0
        for s in filtered_sales:
            v = s.get("amount", 0)
            total_amount += float(v) if isinstance(v, (int, float)) else 0.0
        regions = list(
            dict.fromkeys(
                str(s.get("region", ""))
                for s in filtered_sales
                if s.get("region") not in {None, ""}
            )
        )

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
        if not _is_json_dict(processed_data):
            return r.fail("processed_data must be a dict")
        report_dir.mkdir(exist_ok=True)
        sales_data = processed_data.get("sales_data")
        aggregates = processed_data.get("aggregates")

        reports = []

        # JSON Report
        json_report = {
            "report_type": "sales_summary",
            "generated_at": processed_data.get("processed_at"),
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

        # CSV Report - convert dict data to CSV format; use TypeGuard for list items
        sales_list = sales_data if _is_json_list(sales_data) else []
        sales_mappings = [s for s in sales_list if _is_json_dict(s)]
        if sales_list:
            headers = ["Product", "Region", "Amount", "Quarter"]
            csv_rows = [headers]
            for sale in sales_mappings:
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
            sales_mappings,
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
        reports: object,
        config: FlextCliSettings,
        report_dir: Path,
    ) -> Mapping[str, object]:
        """Create comprehensive report summary."""
        raw_list = reports if _is_json_list(reports) else []
        report_list: list[dict[str, t.JsonValue]] = [
            r for r in raw_list if _is_json_dict(r)
        ]
        # Load JSON report to get aggregates
        json_file = report_dir / "sales_report.json"
        if json_file.exists():
            json_data = json.loads(json_file.read_text())
            aggregates = json_data.get("summary", {})
        else:
            aggregates = {}
        if not _is_json_dict(aggregates):
            aggregates = {}
        regions_val = aggregates.get("regions", [])
        regions_len = len(regions_val) if _is_json_list(regions_val) else 0

        return {
            "report_generation_status": c.Cli.CommandStatus.COMPLETED.value,
            "total_reports": len(report_list),
            "formats_generated": [item["format"] for item in report_list],
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
        assert _is_json_dict(recovery_report)

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
            def _merge_primary(data: t.GeneralValueType) -> dict[str, t.GeneralValueType]:
                base: dict[str, t.GeneralValueType] = (
                    data if _is_json_dict(data) else {}
                )
                return {**base, "data_source": "primary"}

            return primary_result.map(_merge_primary)

        # Fallback to backup
        backup_result = FlextCliFileTools().read_json_file(str(backup_file))
        if backup_result.is_failure:
            return r.fail(f"Both primary and backup failed: {backup_result.error}")

        def _merge_backup(data: t.GeneralValueType) -> dict[str, t.GeneralValueType]:
            base: dict[str, t.GeneralValueType] = (
                data if _is_json_dict(data) else {}
            )
            return {**base, "data_source": "backup"}

        return backup_result.map(_merge_backup)

    def _process_with_partial_recovery(
        self,
        data: Mapping[str, t.GeneralValueType],
    ) -> r[dict[str, t.GeneralValueType]]:
        """Process data with partial recovery for corrupted records."""
        users = data.get("users", [])
        if not _is_json_list(users):
            return r.fail("Users data must be a list")

        processed_users: list[dict[str, t.GeneralValueType]] = []
        recovery_info = {"recovered": 0, "failed": 0}

        for i, user in enumerate(users):
            if not _is_json_dict(user):
                recovery_info["recovered"] += 1
                placeholder: dict[str, t.GeneralValueType] = {
                    "id": f"recovered_{i}",
                    "name": f"Recovered User {i}",
                    "active": False,
                    "recovered": True,
                }
                processed_users.append(placeholder)
                continue
            try:
                user_mapping: Mapping[str, t.GeneralValueType] = user
                processed_user = self._process_single_user(user_mapping)
                processed_users.append(processed_user)
            except (ValueError, TypeError, KeyError, ValidationError) as e:
                # Recovery: Create minimal valid user record
                recovered_user: dict[str, t.GeneralValueType] = {
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
        result: dict[str, t.GeneralValueType] = {
            **user,
            "processed": True,
            "processed_at": "2025-01-01T12:00:00Z",
        }
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
        count = len(processed_users_val) if _is_json_list(processed_users_val) else 0
        return {
            "final_status": "completed_with_recovery",
            "data_source": data.get("data_source"),
            "processing_recovered": data.get("processing_recovered"),
            "recovery_stats": data.get("recovery_stats"),
            "save_attempts": data.get("save_attempts"),
            "total_records_processed": count,
            "recovery_timestamp": "2025-01-01T12:00:00Z",
        }

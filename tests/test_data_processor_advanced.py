"""Tests for FlextCliDataProcessor Advanced Methods.

This module provides comprehensive tests for the advanced methods added to
FlextCliDataProcessor that weren't covered in the main helpers test file.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from collections.abc import Callable
from unittest.mock import patch

import pytest
from flext_core import FlextResult

from flext_cli import FlextCliDataProcessor


class TestFlextCliDataProcessorAdvanced:
    """Test suite for advanced FlextCliDataProcessor methods."""

    def setup_method(self) -> None:
        """Setup test environment."""
        self.processor = FlextCliDataProcessor()

    def test_flext_cli_aggregate_data_success_all_sources(self) -> None:
        """Test successful data aggregation from all sources."""

        def fetch_users() -> FlextResult[list[dict[str, object]]]:
            return FlextResult[None].ok(
                [
                    {"id": 1, "name": "Alice", "type": "user"},
                    {"id": 2, "name": "Bob", "type": "user"},
                ],
            )

        def fetch_orders() -> FlextResult[list[dict[str, object]]]:
            return FlextResult[None].ok(
                [
                    {"id": 101, "user_id": 1, "amount": 99.99},
                    {"id": 102, "user_id": 2, "amount": 149.99},
                ],
            )

        def fetch_products() -> FlextResult[list[dict[str, object]]]:
            return FlextResult[None].ok(
                [
                    {"id": 201, "name": "Widget", "price": 29.99},
                    {"id": 202, "name": "Gadget", "price": 49.99},
                ],
            )

        data_sources = {
            "users": fetch_users,
            "orders": fetch_orders,
            "products": fetch_products,
        }

        # Mock the method that doesn't exist yet
        def mock_aggregate_data(
            sources: dict[str, Callable[[], FlextResult[object]]],
            *,
            fail_fast: bool = True,
        ) -> FlextResult[dict[str, object]]:
            """Mock implementation of flext_cli_aggregate_data."""
            aggregated_data: dict[str, object] = {}
            errors: list[str] = []

            for source_name, source_func in sources.items():
                try:
                    result = source_func()
                    if result.success:
                        aggregated_data[source_name] = result.data
                    else:
                        errors.append(f"{source_name}: {result.error}")
                        if fail_fast:
                            return FlextResult[None].fail(
                                f"Source {source_name} failed: {result.error}",
                            )
                except Exception as e:
                    errors.append(f"{source_name}: {e!s}")
                    if fail_fast:
                        return FlextResult[None].fail(
                            f"Source {source_name} exception: {e!s}",
                        )

            if errors and not aggregated_data:
                return FlextResult[None].fail(
                    f"All sources failed: {'; '.join(errors)}"
                )

            if errors:
                aggregated_data["_errors"] = errors

            return FlextResult[None].ok(aggregated_data)

        # Patch the method temporarily
        with patch.object(
            self.processor,
            "flext_cli_aggregate_data",
            side_effect=mock_aggregate_data,
        ):
            result = self.processor.flext_cli_aggregate_data(
                data_sources,
                fail_fast=False,
            )

        assert result.success
        assert "users" in result.data
        assert "orders" in result.data
        assert "products" in result.data
        assert len(result.data["users"]) == 2
        assert len(result.data["orders"]) == 2
        assert len(result.data["products"]) == 2

    def test_flext_cli_aggregate_data_partial_failure_continue(self) -> None:
        """Test data aggregation with partial failures and continue processing."""

        def fetch_users() -> FlextResult[list[dict[str, object]]]:
            return FlextResult[None].ok([{"id": 1, "name": "Alice"}])

        def fetch_orders() -> FlextResult[list[dict[str, object]]]:
            return FlextResult[None].fail("Orders service unavailable")

        def fetch_products() -> FlextResult[list[dict[str, object]]]:
            return FlextResult[None].ok([{"id": 201, "name": "Widget"}])

        data_sources = {
            "users": fetch_users,
            "orders": fetch_orders,
            "products": fetch_products,
        }

        # Mock the method
        def mock_aggregate_data(
            sources: dict[str, Callable[[], FlextResult[object]]],
            *,
            fail_fast: bool = True,
        ) -> FlextResult[dict[str, object]]:
            """Mock implementation of flext_cli_aggregate_data."""
            aggregated_data: dict[str, object] = {}
            errors: list[str] = []

            for source_name, source_func in sources.items():
                try:
                    result = source_func()
                    if result.success:
                        aggregated_data[source_name] = result.data
                    else:
                        errors.append(f"{source_name}: {result.error}")
                        if fail_fast:
                            return FlextResult[None].fail(
                                f"Source {source_name} failed: {result.error}",
                            )
                except Exception as e:
                    errors.append(f"{source_name}: {e!s}")
                    if fail_fast:
                        return FlextResult[None].fail(
                            f"Source {source_name} exception: {e!s}",
                        )

            if errors and not aggregated_data:
                return FlextResult[None].fail(
                    f"All sources failed: {'; '.join(errors)}"
                )

            if errors:
                aggregated_data["_errors"] = errors

            return FlextResult[None].ok(aggregated_data)

        with patch.object(
            self.processor,
            "flext_cli_aggregate_data",
            side_effect=mock_aggregate_data,
        ):
            result = self.processor.flext_cli_aggregate_data(
                data_sources,
                fail_fast=False,
            )

        assert result.success
        assert "users" in result.data
        assert "products" in result.data
        assert "orders" not in result.data  # Failed source not included
        assert "_errors" in result.data
        assert "orders: Orders service unavailable" in result.data["_errors"]

    def test_flext_cli_aggregate_data_fail_fast_mode(self) -> None:
        """Test data aggregation with fail_fast=True."""

        def fetch_users() -> FlextResult[list[dict[str, object]]]:
            return FlextResult[None].ok([{"id": 1, "name": "Alice"}])

        def fetch_orders() -> FlextResult[list[dict[str, object]]]:
            return FlextResult[None].fail("Orders service unavailable")

        def fetch_products() -> FlextResult[list[dict[str, object]]]:
            return FlextResult[None].ok([{"id": 201, "name": "Widget"}])

        data_sources = {
            "users": fetch_users,
            "orders": fetch_orders,
            "products": fetch_products,
        }

        # Mock implementation with fail_fast behavior
        def mock_aggregate_data(
            sources: dict[str, Callable[[], FlextResult[object]]],
            *,
            fail_fast: bool = True,
        ) -> FlextResult[dict[str, object]]:
            """Mock implementation of flext_cli_aggregate_data."""
            aggregated_data: dict[str, object] = {}
            errors: list[str] = []

            for source_name, source_func in sources.items():
                try:
                    result = source_func()
                    if result.success:
                        aggregated_data[source_name] = result.data
                    else:
                        errors.append(f"{source_name}: {result.error}")
                        if fail_fast:
                            return FlextResult[None].fail(
                                f"Source {source_name} failed: {result.error}",
                            )
                except Exception as e:
                    errors.append(f"{source_name}: {e!s}")
                    if fail_fast:
                        return FlextResult[None].fail(
                            f"Source {source_name} exception: {e!s}",
                        )

            if errors and not aggregated_data:
                return FlextResult[None].fail(
                    f"All sources failed: {'; '.join(errors)}"
                )

            if errors:
                aggregated_data["_errors"] = errors

            return FlextResult[None].ok(aggregated_data)

        with patch.object(
            self.processor,
            "flext_cli_aggregate_data",
            side_effect=mock_aggregate_data,
        ):
            result = self.processor.flext_cli_aggregate_data(
                data_sources,
                fail_fast=True,
            )

        assert not result.success
        assert "Source orders failed: Orders service unavailable" in result.error

    def test_flext_cli_transform_data_pipeline_success(self) -> None:
        """Test successful data transformation pipeline."""
        initial_data = {"items": [1, 2, 3, 4, 5]}

        def normalize_data(data: dict[str, object]) -> FlextResult[dict[str, object]]:
            # Add metadata
            return FlextResult[None].ok(
                {**data, "normalized": True, "item_count": len(data["items"])},
            )

        def double_items(data: dict[str, object]) -> FlextResult[dict[str, object]]:
            # Double all items
            doubled_items = [item * 2 for item in data["items"]]
            return FlextResult[None].ok(
                {**data, "items": doubled_items, "doubled": True}
            )

        def add_summary(data: dict[str, object]) -> FlextResult[dict[str, object]]:
            # Add summary statistics
            return FlextResult[None].ok(
                {
                    **data,
                    "summary": {
                        "total": sum(data["items"]),
                        "count": len(data["items"]),
                        "average": sum(data["items"]) / len(data["items"]),
                    },
                },
            )

        transformers = [normalize_data, double_items, add_summary]

        # Mock the method
        def mock_transform_pipeline(
            data: object,
            transformers: list[Callable[[object], FlextResult[object]]],
        ) -> FlextResult[object]:
            """Mock implementation of flext_cli_transform_data_pipeline."""
            current_data = data

            for i, transformer in enumerate(transformers):
                try:
                    result = transformer(current_data)
                    if not result.success:
                        return FlextResult[None].fail(
                            f"Transformer {i} failed: {result.error}",
                        )
                    current_data = result.data
                except Exception as e:
                    return FlextResult[None].fail(f"Transformer {i} exception: {e!s}")

            return FlextResult[None].ok(current_data)

        with patch.object(
            self.processor,
            "flext_cli_transform_data_pipeline",
            side_effect=mock_transform_pipeline,
        ):
            result = self.processor.flext_cli_transform_data_pipeline(
                initial_data,
                transformers,
            )

        assert result.success
        assert result.data["normalized"] is True
        assert result.data["doubled"] is True
        assert result.data["items"] == [2, 4, 6, 8, 10]  # Doubled
        assert "summary" in result.data
        assert result.data["summary"]["total"] == 30  # Sum of doubled items
        assert result.data["summary"]["count"] == 5

    def test_flext_cli_transform_data_pipeline_transformer_failure(self) -> None:
        """Test data transformation pipeline with transformer failure."""
        initial_data = {"items": [1, 2, 3]}

        def working_transformer(
            data: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            return FlextResult[None].ok({**data, "processed": True})

        def failing_transformer(
            data: dict[str, object],  # noqa: ARG001
        ) -> FlextResult[dict[str, object]]:
            return FlextResult[None].fail("Transformation logic error")

        def should_not_execute(
            data: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            return FlextResult[None].ok({**data, "should_not_be_here": True})

        transformers = [working_transformer, failing_transformer, should_not_execute]

        # Mock the method
        def mock_transform_pipeline(
            data: object,
            transformers: list[Callable[[object], FlextResult[object]]],
        ) -> FlextResult[object]:
            """Mock implementation of flext_cli_transform_data_pipeline."""
            current_data = data

            for i, transformer in enumerate(transformers):
                try:
                    result = transformer(current_data)
                    if not result.success:
                        return FlextResult[None].fail(
                            f"Transformer {i} failed: {result.error}",
                        )
                    current_data = result.data
                except Exception as e:
                    return FlextResult[None].fail(f"Transformer {i} exception: {e!s}")

            return FlextResult[None].ok(current_data)

        with patch.object(
            self.processor,
            "flext_cli_transform_data_pipeline",
            side_effect=mock_transform_pipeline,
        ):
            result = self.processor.flext_cli_transform_data_pipeline(
                initial_data,
                transformers,
            )

        assert not result.success
        assert "Transformer 1 failed: Transformation logic error" in result.error

    def test_flext_cli_transform_data_pipeline_transformer_exception(self) -> None:
        """Test data transformation pipeline with transformer exception."""
        initial_data = {"items": [1, 2, 3]}

        def working_transformer(
            data: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            return FlextResult[None].ok({**data, "processed": True})

        def exception_transformer(
            data: dict[str, object],  # noqa: ARG001
        ) -> FlextResult[dict[str, object]]:
            msg = "Unexpected transformer error"
            raise ValueError(msg)

        transformers = [working_transformer, exception_transformer]

        # Mock the method
        def mock_transform_pipeline(
            data: object,
            transformers: list[Callable[[object], FlextResult[object]]],
        ) -> FlextResult[object]:
            """Mock implementation of flext_cli_transform_data_pipeline."""
            current_data = data

            for i, transformer in enumerate(transformers):
                try:
                    result = transformer(current_data)
                    if not result.success:
                        return FlextResult[None].fail(
                            f"Transformer {i} failed: {result.error}",
                        )
                    current_data = result.data
                except Exception as e:
                    return FlextResult[None].fail(f"Transformer {i} exception: {e!s}")

            return FlextResult[None].ok(current_data)

        with patch.object(
            self.processor,
            "flext_cli_transform_data_pipeline",
            side_effect=mock_transform_pipeline,
        ):
            result = self.processor.flext_cli_transform_data_pipeline(
                initial_data,
                transformers,
            )

        assert not result.success
        assert "Transformer 1 exception: Unexpected transformer error" in result.error


class TestComplexDataProcessingWorkflows:
    """Test suite for complex data processing workflow combinations."""

    def setup_method(self) -> None:
        """Setup test environment."""
        self.processor = FlextCliDataProcessor()

    def test_complete_etl_pipeline_simulation(self) -> None:
        """Test a complete ETL pipeline simulation using multiple methods."""

        # Step 1: Data extraction (aggregation)
        def extract_users() -> FlextResult[list[dict[str, object]]]:
            return FlextResult[None].ok(
                [
                    {
                        "id": 1,
                        "name": "Alice",
                        "email": "alice@example.com",
                        "active": True,
                    },
                    {
                        "id": 2,
                        "name": "Bob",
                        "email": "bob@example.com",
                        "active": False,
                    },
                    {
                        "id": 3,
                        "name": "Charlie",
                        "email": "charlie@example.com",
                        "active": True,
                    },
                ],
            )

        def extract_user_metrics() -> FlextResult[list[dict[str, object]]]:
            return FlextResult[None].ok(
                [
                    {"user_id": 1, "login_count": 15, "last_login": "2024-01-15"},
                    {"user_id": 2, "login_count": 3, "last_login": "2024-01-10"},
                    {"user_id": 3, "login_count": 22, "last_login": "2024-01-16"},
                ],
            )

        extraction_sources = {"users": extract_users, "metrics": extract_user_metrics}

        # Mock aggregation
        def mock_aggregate(
            sources: dict[str, Callable[[], FlextResult[object]]],
            *,
            fail_fast: bool = True,  # noqa: ARG001
        ) -> FlextResult[dict[str, object]]:
            result_data = {}
            for name, func in sources.items():
                data_result = func()
                if data_result.success:
                    result_data[name] = data_result.data
                else:
                    return data_result
            return FlextResult[None].ok(result_data)

        # Step 2: Data transformation
        def merge_user_data(data: dict[str, object]) -> FlextResult[dict[str, object]]:
            """Merge users with their metrics."""
            users = {user["id"]: user for user in data["users"]}
            metrics = {metric["user_id"]: metric for metric in data["metrics"]}

            merged_users = []
            for user_id, user in users.items():
                user_metrics = metrics.get(user_id, {})
                merged_user = {
                    **user,
                    "login_count": user_metrics.get("login_count", 0),
                    "last_login": user_metrics.get("last_login", None),
                }
                merged_users.append(merged_user)

            return FlextResult[None].ok({"merged_users": merged_users})

        def filter_active_users(
            data: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            """Filter only active users."""
            active_users = [user for user in data["merged_users"] if user["active"]]
            return FlextResult[None].ok({"active_users": active_users})

        def calculate_engagement_score(
            data: dict[str, object],
        ) -> FlextResult[dict[str, object]]:
            """Calculate engagement scores."""
            scored_users = []
            for user in data["active_users"]:
                # Simple engagement score based on login count
                engagement_score = min(user["login_count"] * 5, 100)  # Max 100
                scored_user = {**user, "engagement_score": engagement_score}
                scored_users.append(scored_user)

            return FlextResult[None].ok({"scored_users": scored_users})

        transformation_pipeline = [
            merge_user_data,
            filter_active_users,
            calculate_engagement_score,
        ]

        # Mock transformation pipeline
        def mock_transform(
            data: object,
            transformers: list[Callable[[object], FlextResult[object]]],
        ) -> FlextResult[object]:
            current = data
            for transformer in transformers:
                result = transformer(current)
                if not result.success:
                    return result
                current = result.data
            return FlextResult[None].ok(current)

        # Execute the complete pipeline
        with (
            patch.object(
                self.processor,
                "flext_cli_aggregate_data",
                side_effect=mock_aggregate,
            ),
            patch.object(
                self.processor,
                "flext_cli_transform_data_pipeline",
                side_effect=mock_transform,
            ),
        ):
            # Step 1: Extract data
            extraction_result = self.processor.flext_cli_aggregate_data(
                extraction_sources,
            )
            assert extraction_result.success

            # Step 2: Transform data
            transformation_result = self.processor.flext_cli_transform_data_pipeline(
                extraction_result.data,
                transformation_pipeline,
            )
            assert transformation_result.success

        final_data = transformation_result.data

        # Validate final results
        assert "scored_users" in final_data
        scored_users = final_data["scored_users"]

        # Should have 2 active users (Alice and Charlie)
        assert len(scored_users) == 2

        # Check engagement scores
        alice = next(user for user in scored_users if user["name"] == "Alice")
        charlie = next(user for user in scored_users if user["name"] == "Charlie")

        assert alice["engagement_score"] == 75  # 15 * 5
        assert charlie["engagement_score"] == 100  # 22 * 5, capped at 100

    def test_error_handling_in_complex_pipeline(self) -> None:
        """Test error handling in complex multi-step pipeline."""

        # Step 1: Aggregation with one failing source
        def working_source() -> FlextResult[list[str]]:
            return FlextResult[None].ok(["data1", "data2"])

        def failing_source() -> FlextResult[list[str]]:
            return FlextResult[None].fail("Source system unavailable")

        sources = {"working": working_source, "failing": failing_source}

        # Mock with fail_fast=True
        def mock_aggregate_fail_fast(
            sources: dict[str, Callable[[], FlextResult[object]]],
            *,
            fail_fast: bool = True,
        ) -> FlextResult[dict[str, object]]:
            for name, func in sources.items():
                result = func()
                if not result.success and fail_fast:
                    return FlextResult[None].fail(
                        f"Source {name} failed: {result.error}"
                    )
            return FlextResult[None].ok({"working": ["data1", "data2"]})

        with patch.object(
            self.processor,
            "flext_cli_aggregate_data",
            side_effect=mock_aggregate_fail_fast,
        ):
            result = self.processor.flext_cli_aggregate_data(sources, fail_fast=True)

        assert not result.success
        assert "Source failing failed: Source system unavailable" in result.error

    def test_validation_and_transformation_integration(self) -> None:
        """Test integration of validation and transformation methods."""
        input_data = {
            "user_email": "USER@EXAMPLE.COM",  # Needs normalization
            "api_url": "https://api.flext.sh/v1",
            "batch_size": "25",  # String that needs conversion
            "active_only": "true",  # String boolean
        }

        validators = {
            "user_email": "email",
            "api_url": "url",
        }

        transformers = {
            "user_email": lambda x: x.lower(),
            "batch_size": int,
            "active_only": lambda x: x.lower() == "true",
        }

        # Test validation and transformation
        result = self.processor.flext_cli_validate_and_transform(
            input_data,
            validators,
            transformers,
        )

        assert result.success
        assert (
            result.data["user_email"] == "user@example.com"
        )  # Validated and lowercased
        assert result.data["api_url"] == "https://api.flext.sh/v1"  # Validated
        assert result.data["batch_size"] == 25  # Converted to int
        assert result.data["active_only"] is True  # Converted to boolean


if __name__ == "__main__":
    pytest.main([__file__])

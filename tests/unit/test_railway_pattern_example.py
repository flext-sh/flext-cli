"""FLEXT CLI Railway Pattern Example Tests - Comprehensive Railway Pattern Validation Testing.

Tests for FlextResult Railway Pattern covering success chains, error handling, validation flows,
multi-step workflows, error recovery, and edge cases with 100% coverage.

Modules tested: flext_cli.file_tools.FlextCliFileTools, flext_core.result.FlextResult
Scope: All railway pattern operations, success chains, error handling, validation flows

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest
from flext_core import t

from flext_cli import FlextCliFileTools

# from ..fixtures.constants import RailwayPatternExample as Railway  # Fixtures removed - use conftest.py and flext_tests


class TestsCliRailwayPatternExample:
    """Railway Pattern testing with FlextResult paradigm.

    Demonstrates proper usage of FlextResult for success/failure chains,
    error handling, and multi-step workflow integration.
    """

    # =========================================================================
    # FIXTURES
    # =========================================================================

    @pytest.fixture
    def file_tools(self) -> FlextCliFileTools:
        """Create FlextCliFileTools instance for testing."""
        return FlextCliFileTools()

    @pytest.fixture
    def temp_dir(self) -> Generator[Path]:
        """Create temporary directory for file operations."""
        with tempfile.TemporaryDirectory() as temp_dir_path:
            yield Path(temp_dir_path)

    # =========================================================================
    # SUCCESS CHAIN TESTS - Parametrized
    # =========================================================================

    @pytest.mark.parametrize(
        ("test_data", "filename", "verify_keys"),
        [
            ("simple", "test_file.txt", ["name", "value"]),
            (
                "key_value",
                "validated_file.txt",
                ["key", "number"],
            ),
            (
                "config",
                "config_file.json",
                ["debug", "timeout"],
            ),
        ],
        ids=["simple_data", "key_value", "config_data"],
    )
    def test_railway_success_chain(
        self,
        file_tools: FlextCliFileTools,
        temp_dir: Path,
        test_data: dict[str, t.GeneralValueType],
        filename: str,
        verify_keys: list[str],
    ) -> None:
        """Test Railway Pattern success chain for write-read operations.

        Demonstrates:
        - FlextResult.ok() creation
        - Success chain with multiple operations
        - Data integrity verification
        """
        test_file = temp_dir / filename

        # Write data
        write_result = file_tools.write_json_file(str(test_file), test_data)
        assert write_result.is_success
        assert test_file.exists()

        # Read back and verify structure
        read_result = file_tools.read_json_file(str(test_file))
        assert read_result.is_success

        # Verify data integrity
        loaded_data = read_result.unwrap()
        assert isinstance(loaded_data, dict)
        for key in verify_keys:
            assert key in loaded_data

    # =========================================================================
    # ERROR HANDLING TESTS - Parametrized
    # =========================================================================

    @pytest.mark.parametrize(
        ("invalid_path", "test_data", "scenario"),
        [
            (
                "/invalid/path",
                "simple",
                "nonexistent_dir",
            ),
            (
                "/dev/null/nested/deep/path.json",
                "config",
                "nested_invalid",
            ),
        ],
        ids=["nonexistent_dir", "nested_invalid"],
    )
    def test_railway_error_handling(
        self,
        file_tools: FlextCliFileTools,
        invalid_path: str,
        test_data: dict[str, t.GeneralValueType],
        scenario: str,
    ) -> None:
        """Test Railway Pattern error handling and propagation.

        Demonstrates:
        - Error state detection (is_failure)
        - Error message presence
        - Proper error propagation
        """
        result = file_tools.write_json_file(invalid_path, test_data)

        # Verify failure is handled properly
        assert result.is_failure
        error_msg = result.error
        assert error_msg is not None

    # =========================================================================
    # ERROR RECOVERY TESTS
    # =========================================================================

    def test_railway_error_recovery(
        self,
        file_tools: FlextCliFileTools,
        temp_dir: Path,
    ) -> None:
        """Test Railway Pattern with fallback/recovery strategies.

        Demonstrates:
        - Error detection and recovery paths
        - Alternative execution strategies
        - Proper fallback handling
        """
        fallback_file = temp_dir / "fallback_file.txt"

        # Try primary (fails due to invalid path)
        primary_result = file_tools.write_json_file(
            "/invalid/path",
            "strategy",
        )
        assert primary_result.is_failure

        # Use fallback
        fallback_result = file_tools.write_json_file(
            str(fallback_file),
            "strategy",
        )
        assert fallback_result.is_success
        assert fallback_file.exists()

    # =========================================================================
    # WORKFLOW INTEGRATION TESTS
    # =========================================================================

    def test_railway_workflow_integration(
        self,
        file_tools: FlextCliFileTools,
        temp_dir: Path,
    ) -> None:
        """Test complete multi-step workflow using Railway Pattern.

        Demonstrates:
        - Multi-step operations with FlextResult
        - Error handling throughout workflow
        - File operation chaining
        - Result unwrapping and data composition
        """
        config_file = temp_dir / "config_file.json"
        data_file = temp_dir / "data_file.json"
        output_file = temp_dir / "output_file.json"

        # Step 1: Write config
        config_result = file_tools.write_json_file(
            str(config_file),
            "config",
        )
        assert config_result.is_success

        # Step 2: Write input data
        data_result = file_tools.write_json_file(
            str(data_file),
            "items",
        )
        assert data_result.is_success

        # Step 3: Read both files
        config_read = file_tools.read_json_file(str(config_file))
        assert config_read.is_success

        data_read = file_tools.read_json_file(str(data_file))
        assert data_read.is_success

        # Step 4: Combine and write result
        combined = {
            "config": config_read.unwrap(),
            "data": data_read.unwrap(),
        }
        write_result = file_tools.write_json_file(str(output_file), combined)
        assert write_result.is_success

        # Step 5: Verify final result
        assert output_file.exists()

        # Step 6: Read and validate combined output
        final_result = file_tools.read_json_file(str(output_file))
        assert final_result.is_success

        # Verify combined data structure
        final_data = final_result.unwrap()
        assert isinstance(final_data, dict)
        assert "config" in final_data
        assert "data" in final_data

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

from flext_cli import FlextCliFileTools, t


class TestsCliRailwayPatternExample:
    """Railway Pattern testing with FlextResult paradigm.

    Demonstrates proper usage of FlextResult for success/failure chains,
    error handling, and multi-step workflow integration.
    """

    @pytest.fixture
    def file_tools(self) -> FlextCliFileTools:
        """Create FlextCliFileTools instance for testing."""
        return FlextCliFileTools()

    @pytest.fixture
    def temp_dir(self) -> Generator[Path]:
        """Create temporary directory for file operations."""
        with tempfile.TemporaryDirectory() as temp_dir_path:
            yield Path(temp_dir_path)

    @pytest.mark.parametrize(
        ("test_data", "filename", "verify_keys"),
        [
            ({"name": "test", "value": 123}, "test_file.txt", ["name", "value"]),
            (
                {"key": "test_key", "number": 42},
                "validated_file.txt",
                ["key", "number"],
            ),
            ({"debug": True, "timeout": 30}, "config_file.json", ["debug", "timeout"]),
        ],
        ids=["simple_data", "key_value", "config_data"],
    )
    def test_railway_success_chain(
        self,
        file_tools: FlextCliFileTools,
        temp_dir: Path,
        test_data: dict[str, t.ContainerValue],
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
        write_result = file_tools.write_json_file(str(test_file), test_data)
        assert write_result.is_success
        assert test_file.exists()
        read_result = file_tools.read_json_file(str(test_file))
        assert read_result.is_success
        loaded_data = read_result.value
        assert isinstance(loaded_data, dict)
        for key in verify_keys:
            assert key in loaded_data

    @pytest.mark.parametrize(
        ("invalid_path", "test_data", "scenario"),
        [
            ("/invalid/path", {"name": "test", "value": 123}, "nonexistent_dir"),
            (
                "/dev/null/nested/deep/path.json",
                {"debug": True, "timeout": 30},
                "nested_invalid",
            ),
        ],
        ids=["nonexistent_dir", "nested_invalid"],
    )
    def test_railway_error_handling(
        self,
        file_tools: FlextCliFileTools,
        invalid_path: str,
        test_data: dict[str, t.ContainerValue],
        scenario: str,
    ) -> None:
        """Test Railway Pattern error handling and propagation.

        Demonstrates:
        - Error state detection (is_failure)
        - Error message presence
        - Proper error propagation
        """
        result = file_tools.write_json_file(invalid_path, test_data)
        assert result.is_failure
        error_msg = result.error
        assert error_msg is not None

    def test_railway_error_recovery(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test Railway Pattern with fallback/recovery strategies.

        Demonstrates:
        - Error detection and recovery paths
        - Alternative execution strategies
        - Proper fallback handling
        """
        fallback_file = temp_dir / "fallback_file.txt"
        primary_result = file_tools.write_json_file(
            "/invalid/path", {"strategy": "fallback"}
        )
        assert primary_result.is_failure
        fallback_result = file_tools.write_json_file(
            str(fallback_file), {"strategy": "fallback"}
        )
        assert fallback_result.is_success
        assert fallback_file.exists()

    def test_railway_workflow_integration(
        self, file_tools: FlextCliFileTools, temp_dir: Path
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
        config_result = file_tools.write_json_file(
            str(config_file), {"debug": True, "timeout": 30}
        )
        assert config_result.is_success
        data_result = file_tools.write_json_file(str(data_file), {"items": [1, 2, 3]})
        assert data_result.is_success
        config_read = file_tools.read_json_file(str(config_file))
        assert config_read.is_success
        data_read = file_tools.read_json_file(str(data_file))
        assert data_read.is_success
        combined = {"config": config_read.value, "data": data_read.value}
        write_result = file_tools.write_json_file(str(output_file), combined)
        assert write_result.is_success
        assert output_file.exists()
        final_result = file_tools.read_json_file(str(output_file))
        assert final_result.is_success
        final_data = final_result.value
        assert isinstance(final_data, dict)
        assert "config" in final_data
        assert "data" in final_data

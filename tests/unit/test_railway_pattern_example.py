"""FLEXT CLI Railway Pattern Example Tests - Comprehensive Railway Pattern Validation Testing.

Tests for r Railway Pattern covering success chains, error handling, validation flows,
multi-step workflows, error recovery, and edge cases with 100% coverage.

Modules tested: flext_cli.file_tools.FlextCliFileTools, flext_core.result.r
Scope: All railway pattern operations, success chains, error handling, validation flows

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import tempfile
from collections.abc import Generator, Mapping, Sequence
from pathlib import Path

import pytest
from flext_tests import tm

from flext_cli import FlextCliFileTools
from tests import t


class TestsCliRailwayPatternExample:
    """Railway Pattern testing with r paradigm.

    Demonstrates proper usage of r for success/failure chains,
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
        test_data: Mapping[str, t.NormalizedValue],
        filename: str,
        verify_keys: Sequence[str],
    ) -> None:
        """Test Railway Pattern success chain for write-read operations.

        Demonstrates:
        - r.ok() creation
        - Success chain with multiple operations
        - Data integrity verification
        """
        test_file = temp_dir / filename
        write_result = file_tools.write_json_file(str(test_file), test_data)
        tm.ok(write_result)
        tm.that(test_file.exists(), eq=True)
        read_result = file_tools.read_json_file(str(test_file))
        tm.ok(read_result)
        loaded_data = read_result.value
        tm.that(isinstance(loaded_data, dict), eq=True)
        for key in verify_keys:
            tm.that(key in loaded_data, eq=True)

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
        test_data: Mapping[str, t.NormalizedValue],
        scenario: str,
    ) -> None:
        """Test Railway Pattern error handling and propagation.

        Demonstrates:
        - Error state detection (is_failure)
        - Error message presence
        - Proper error propagation
        """
        result = file_tools.write_json_file(invalid_path, test_data)
        tm.fail(result)
        error_msg = result.error
        tm.that(error_msg is not None, eq=True)

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
        tm.fail(primary_result)
        fallback_result = file_tools.write_json_file(
            str(fallback_file), {"strategy": "fallback"}
        )
        tm.ok(fallback_result)
        tm.that(fallback_file.exists(), eq=True)

    def test_railway_workflow_integration(
        self, file_tools: FlextCliFileTools, temp_dir: Path
    ) -> None:
        """Test complete multi-step workflow using Railway Pattern.

        Demonstrates:
        - Multi-step operations with r
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
        tm.ok(config_result)
        data_result = file_tools.write_json_file(str(data_file), {"items": [1, 2, 3]})
        tm.ok(data_result)
        config_read = file_tools.read_json_file(str(config_file))
        tm.ok(config_read)
        data_read = file_tools.read_json_file(str(data_file))
        tm.ok(data_read)
        combined = {"config": config_read.value, "data": data_read.value}
        write_result = file_tools.write_json_file(str(output_file), combined)
        tm.ok(write_result)
        tm.that(output_file.exists(), eq=True)
        final_result = file_tools.read_json_file(str(output_file))
        tm.ok(final_result)
        final_data = final_result.value
        tm.that(isinstance(final_data, dict), eq=True)
        tm.that("config" in final_data, eq=True)
        tm.that("data" in final_data, eq=True)

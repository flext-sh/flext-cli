"""FLEXT CLI Context Tests - Comprehensive test coverage for FlextCliContext.

Tests all context functionality with real implementations and comprehensive coverage.
"""

from __future__ import annotations

import asyncio
import json

import pytest

from flext_cli.context import FlextCliContext
from flext_core import FlextResult
from flext_tests import FlextTestsUtilities


class TestFlextCliContext:
    """Comprehensive tests for FlextCliContext functionality."""

    @pytest.fixture
    def context(self) -> FlextCliContext:
        """Create FlextCliContext instance for testing."""
        return FlextCliContext()

    @pytest.fixture
    def test_utilities(self) -> FlextTestsUtilities:
        """Provide FlextTestsUtilities for test support."""
        return FlextTestsUtilities()

    def test_context_initialization(self, context: FlextCliContext) -> None:
        """Test context initialization and basic properties."""
        assert isinstance(context, FlextCliContext)
        assert hasattr(context, "_timeout_seconds")
        assert hasattr(context, "_config")

    def test_context_execute(self, context: FlextCliContext) -> None:
        """Test context execute method."""
        result = context.execute()

        assert isinstance(result, FlextResult)
        assert result.is_success
        assert isinstance(result.unwrap(), dict)

    def test_context_execute_async_method(self, context: FlextCliContext) -> None:
        """Test context async execute method."""

        async def run_test() -> None:
            result = await context.execute_async()

            assert isinstance(result, FlextResult)
            assert result.is_success

        asyncio.run(run_test())

    def test_context_timeout_seconds(self, context: FlextCliContext) -> None:
        """Test context timeout seconds property."""
        timeout = context.timeout_seconds
        assert isinstance(timeout, int)
        assert timeout > 0

    def test_context_set_timeout(self, context: FlextCliContext) -> None:
        """Test context timeout setting."""
        # Test with different timeout values
        test_timeouts = [10, 30, 60, 120]

        for timeout in test_timeouts:
            context.timeout_seconds = timeout
            assert context.timeout_seconds == timeout

    def test_context_to_dict(self, context: FlextCliContext) -> None:
        """Test context to_dict functionality."""
        data = context.to_dict()

        assert isinstance(data, dict)
        assert "timeout_seconds" in data
        assert isinstance(data["timeout_seconds"], int)

    def test_context_to_dict_json(self, context: FlextCliContext) -> None:
        """Test context to_dict JSON functionality."""
        data = context.to_dict()
        json_data = json.dumps(data)

        assert isinstance(json_data, str)
        assert "timeout_seconds" in json_data

    def test_context_validation(self, context: FlextCliContext) -> None:
        """Test context validation functionality."""
        # Test valid timeout values
        valid_timeouts = [1, 30, 60, 300]

        for timeout in valid_timeouts:
            context.timeout_seconds = timeout
            # Should not raise any exceptions
            _ = context.timeout_seconds

    def test_context_real_functionality(self, context: FlextCliContext) -> None:
        """Test context real functionality with comprehensive scenarios."""
        # Test basic execution
        result = context.execute()
        assert result.is_success

        # Test with different configurations
        context.timeout_seconds = 15
        result = context.execute()
        assert result.is_success

        # Test serialization
        data = context.to_dict()
        assert "timeout_seconds" in data
        assert data["timeout_seconds"] == 15

    def test_context_integration_workflow(self, context: FlextCliContext) -> None:
        """Test context integration workflow."""
        # 1. Initialize context
        assert isinstance(context, FlextCliContext)

        # 2. Configure timeout
        context.timeout_seconds = 45

        # 3. Execute context operations
        result = context.execute()
        assert result.is_success

        # 4. Verify configuration persistence
        assert context.timeout_seconds == 45

        # 5. Test serialization
        data = context.to_dict()
        assert data["timeout_seconds"] == 45

    def test_context_edge_cases(self, context: FlextCliContext) -> None:
        """Test context edge cases and error handling."""
        # Test with minimum timeout
        context.timeout_seconds = 1
        assert context.timeout_seconds == 1

        # Test with large timeout
        context.timeout_seconds = 3600
        assert context.timeout_seconds == 3600

        # Test to_dict with edge values
        data = context.to_dict()
        assert data["timeout_seconds"] == 3600

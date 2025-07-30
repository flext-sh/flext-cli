#!/usr/bin/env python3
"""Final validation test for FLEXT CLI Library.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This script validates that all major functionality is working correctly.
"""

from __future__ import annotations

import sys
import traceback
from typing import TYPE_CHECKING

from flext_cli.client import FlextApiClient, Pipeline, PipelineList
from flext_cli.domain.cli_context import CLIContext as DomainCLIContext
from flext_cli.domain.entities import CLICommand
from flext_cli.utils.config import CLIConfig, CLISettings
from rich.console import Console

if TYPE_CHECKING:
    from flext_core.result import FlextResult


def test_api_functionality() -> bool:
    """Test core API functionality."""
    try:
        from flext_cli.api import (
            flext_cli_aggregate_data,
            flext_cli_format,
            flext_cli_table,
            flext_cli_transform_data,
        )

        # Test basic formatting
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = flext_cli_format(data, "json")
        assert result.is_success

        # Test table creation
        table_result = flext_cli_table(data, "Test Table")
        assert table_result.is_success

        # Test data transformation
        transform_result = flext_cli_transform_data(
            data, filter_func=lambda x: x["age"] >= 30,
        )
        assert transform_result.is_success
        if len(transform_result.unwrap()) != 1:
            msg = f"Expected {1}, got {len(transform_result.unwrap())}"
            raise AssertionError(msg)

        # Test data aggregation
        agg_data = [
            {"dept": "Engineering", "salary": 100000},
            {"dept": "Engineering", "salary": 110000},
            {"dept": "Sales", "salary": 80000},
        ]
        agg_result = flext_cli_aggregate_data(agg_data, group_by="dept")
        assert agg_result.is_success

        return True

    except (RuntimeError, ValueError, TypeError):
        traceback.print_exc()
        return False


def test_core_functionality() -> bool:
    """Test core functionality."""
    try:
        from flext_cli.core.base import CLIContext, handle_service_result
        from flext_cli.core.formatters import FormatterFactory
        from flext_cli.core.helpers import CLIHelper
        from flext_cli.core.types import PositiveInt
        from flext_core.result import FlextResult

        # Test CLI context
        context = CLIContext(profile="test", output_format="json")
        if context.profile != "test":
            msg = f"Expected {'test'}, got {context.profile}"
            raise AssertionError(msg)

        # Test formatters
        formatter = FormatterFactory.create("json")
        assert formatter is not None

        # Test helpers
        helper = CLIHelper()
        if not (helper.validate_url("https://example.com")):
            msg = f"Expected True, got {helper.validate_url('https://example.com')}"
            raise AssertionError(
                msg,
            )

        # Test types
        if PositiveInt.convert(42, None, None) != 42:
            msg = f"Expected {42}, got {PositiveInt.convert(42, None, None)}"
            raise AssertionError(
                msg,
            )

        # Test service result decorator
        @handle_service_result
        def test_function() -> FlextResult[str]:
            return FlextResult.ok("success")

        result = test_function()
        if result != "success":
            msg = f"Expected {'success'}, got {result}"
            raise AssertionError(msg)

        return True

    except (RuntimeError, ValueError, TypeError):
        traceback.print_exc()
        return False


def test_domain_functionality() -> bool:
    """Test domain functionality."""
    try:
        # Test domain entities
        command = CLICommand(
            name="test-command", command_line="echo hello", description="Test command",
        )
        if command.name != "test-command":
            msg = f"Expected {'test-command'}, got {command.name}"
            raise AssertionError(msg)

        # Test domain CLI context
        config = CLIConfig()
        settings = CLISettings()
        console = Console()

        domain_context = DomainCLIContext(
            config=config, settings=settings, console=console,
        )
        assert domain_context.config is config

        return True

    except (RuntimeError, ValueError, TypeError):
        traceback.print_exc()
        return False


def test_client_functionality() -> bool:
    """Test client functionality."""
    try:
        # Test client stubs
        client = FlextApiClient("http://example.com", timeout=30)
        assert isinstance(client, FlextApiClient)

        pipeline = Pipeline(name="test-pipeline")
        if pipeline.name != "stub-pipeline":  # Stub behavior
            msg = f"Expected {'stub-pipeline'}, got {pipeline.name}"
            raise AssertionError(msg)
        assert pipeline.id == "stub-id"
        if pipeline.status != "stub-status":
            msg = f"Expected {'stub-status'}, got {pipeline.status}"
            raise AssertionError(msg)

        pipeline_list = PipelineList()
        assert isinstance(pipeline_list, PipelineList)
        if pipeline_list.pipelines != []:
            msg = f"Expected {[]}, got {pipeline_list.pipelines}"
            raise AssertionError(msg)

        return True

    except (RuntimeError, ValueError, TypeError):
        traceback.print_exc()
        return False


def test_simple_api_functionality() -> bool:
    """Test simple API functionality."""
    try:
        from flext_cli.simple_api import (
            create_development_cli_config,
            create_production_cli_config,
            get_cli_settings,
            setup_cli,
        )

        # Test setup
        result = setup_cli()
        assert result.is_success

        # Test development config
        dev_config = create_development_cli_config(debug=True)
        if not (dev_config.debug):
            msg = f"Expected True, got {dev_config.debug}"
            raise AssertionError(msg)
        if dev_config.log_level != "DEBUG":
            msg = f"Expected {'DEBUG'}, got {dev_config.log_level}"
            raise AssertionError(msg)

        # Test production config
        prod_config = create_production_cli_config(debug=False)
        if prod_config.debug:
            msg = f"Expected False, got {prod_config.debug}"
            raise AssertionError(msg)
        assert prod_config.log_level == "INFO"

        # Test settings
        settings = get_cli_settings()
        if settings.project_name != "flext-cli":
            msg = f"Expected {'flext-cli'}, got {settings.project_name}"
            raise AssertionError(msg)
        assert settings.project_version == "0.9.0"

        return True

    except (RuntimeError, ValueError, TypeError):
        traceback.print_exc()
        return False


def main() -> int:
    """Run all validation tests."""
    all_tests_passed = True

    # Run all test suites
    tests = [
        test_api_functionality,
        test_core_functionality,
        test_domain_functionality,
        test_client_functionality,
        test_simple_api_functionality,
    ]

    for test in tests:
        if not test():
            all_tests_passed = False

    if all_tests_passed:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())

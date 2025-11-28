#!/usr/bin/env python3
"""FLEXT CLI Debug E2E - End-to-End Debugging for CLI Operations.

Provides systematic testing of critical flext-cli operations using advanced
Python 3.13 patterns (mapping, lambdas, type safety) to identify integration
issues and service failures in production environments.

MODULE: FlextCliDebugE2E - Single class with nested operation mapping
SCOPE: E2E debugging, integration testing, failure diagnosis, railway pattern
FUNCTIONALITY: Tests config show/validate, auth status, debug checks with O(1) lookup

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import logging
import traceback
from collections.abc import Callable
from typing import cast

from flext_core import FlextResult

from flext_cli import FlextCli, FlextCliTypes
from flext_cli.constants import FlextCliConstants


class FlextCliDebugE2E:
    """Debug E2E test runner for flext-cli operations.

    Systematically tests critical CLI operations to identify integration
    issues and service failures. Uses flext-cli abstraction layer to maintain
    zero tolerance for direct framework imports.
    """

    def __init__(self) -> None:
        """Initialize debug runner with logging configuration."""
        # Configure logging for this debug script
        logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
        self.logger = logging.getLogger(__name__)

        # Define test operations using collections.abc.Mapping for O(1) lookup
        self.operations: dict[tuple[str, str], Callable[[FlextCli], FlextResult[object]]] = {
            ("config", "show"): lambda cli: cast("FlextResult[object]", cli.cmd.show_config_paths()),
            ("config", "validate"): lambda cli: cast("FlextResult[object]", cli.cmd.validate_config()),
            ("auth", "status"): self._execute_auth_status,
            ("debug", "check"): lambda cli: cast("FlextResult[object]", cli.execute()),
        }

    def run_debug_tests(self) -> None:
        """Run E2E debug tests for all defined operations."""
        self.logger.info("Starting flext-cli E2E debug tests")

        for operation in self.operations:
            if not self._test_operation(list(operation)):
                break

        self.logger.info("E2E debug tests completed")

    def _test_operation(self, operation: list[str]) -> bool:
        """Test a single operation and return success status."""
        try:
            self.logger.info("Testing operation: %s", operation)

            cli = FlextCli()

            # Route operations to appropriate methods
            result = self._execute_operation(cli, operation)

            if result.is_success:
                self.logger.info("Operation %s completed successfully", operation)
                return True
            self.logger.error("Operation %s failed: %s", operation, result.error)
            return False

        except Exception:
            self.logger.exception("Command %s raised exception", operation)
            traceback.print_exc()
            return False

    def _execute_operation(self, cli: FlextCli, operation: list[str]) -> FlextResult[object]:
        """Execute the specified operation using flext-cli API."""
        operation_key = cast("tuple[str, str]", tuple(operation))
        if operation_key in self.operations:
            return self.operations[operation_key](cli)
        return FlextResult[object].fail(f"Unknown operation: {operation}")

    def _execute_auth_status(self, cli: FlextCli) -> FlextResult[object]:
        """Execute authentication status check."""
        is_authenticated = cli.is_authenticated()
        return (
            FlextResult[object].ok("Authenticated")
            if is_authenticated
            else FlextResult[object].fail("Not authenticated")
        )

    def demonstrate_advanced_types(self) -> None:
        """Demonstrate advanced Python 3.13+ typing patterns in scripts.

        Shows how to use:
        - StrEnum for runtime validation
        - collections.abc.Mapping for immutable data
        - Advanced Literal unions from constants
        """
        self.logger.info("Demonstrating advanced Python 3.13+ typing patterns")

        # Using StrEnum from constants for runtime validation
        output_format = FlextCliConstants.OutputFormats.JSON
        self.logger.info(f"Selected output format: {output_format.value}")

        # Using collections.abc.Mapping for immutable configuration
        config: FlextCliTypes.Data.CliConfigMapping = {
            "output_format": "json",
            "timeout": 30,
            "debug": True,
        }

        # Demonstrate discriminated union validation
        valid_formats = FlextCliConstants.get_valid_output_formats()
        self.logger.info(f"Available formats: {', '.join(valid_formats)}")

        # Using advanced type aliases from typings
        sample_data: FlextCliTypes.CliJsonDict = {
            "status": FlextCliConstants.CommandStatus.COMPLETED.value,
            "data": [1, 2, 3],
            "metadata": {"version": "1.0"},
        }

        self.logger.info(f"Sample data structure: {sample_data}")


def main() -> None:
    """Main entry point for debug E2E testing."""
    debugger = FlextCliDebugE2E()
    debugger.run_debug_tests()
    debugger.demonstrate_advanced_types()


if __name__ == "__main__":
    main()

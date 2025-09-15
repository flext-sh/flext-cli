"""FLEXT CLI Examples - Foundation Library Usage Demonstrations.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This directory contains organized examples demonstrating flext-cli and flext-core patterns.

## Example Organization:

### Core Patterns (01-05)
- 01_foundation_patterns: FlextResult, FlextModels, FlextContainer basics
- 02_cli_commands_integration: Click framework + flext-cli decorators
- 03_data_processing_and_output: Data transformation and Rich output
- 04_authentication_and_authorization: Security patterns and token management
- 05_advanced_service_integration: Service patterns with async operations

### Complete Applications (06-10)
- 06_comprehensive_cli_application: Full real-world CLI application
- 07_patterns: Clean Architecture, CQRS, DDD patterns
- 08_ecosystem_integration: Integration with flext-* projects
- 09_performance_optimization: Advanced patterns for performance
- 10_production_ready: Production deployment patterns

All examples demonstrate proper flext-core usage without TYPE_CHECKING imports.
"""

from __future__ import annotations

from flext_core import FlextTypes

from .example_utils import (
    handle_command_result,
    print_demo_completion,
    print_demo_error,
)

__all__: FlextTypes.Core.StringList = [
    "handle_command_result",
    "print_demo_completion",
    "print_demo_error",
]

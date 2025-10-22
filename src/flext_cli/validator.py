"""FLEXT CLI Validator Service - REMOVED.

This file previously contained FlextCliValidator class with validation methods that
duplicated Pydantic v2 field validation capabilities.

As of Phase 3 Part 3 (Pydantic v2 Modernization):
- FlextCliValidator class has been removed
- All field validation methods have been consolidated into Pydantic v2 patterns:
  - validate_output_format() → Literal["json", "yaml", "csv", "table", "plain"]
  - validate_profile() → Field(min_length=1)
  - validate_log_verbosity() → Literal[valid_values]
  - validate_environment() → Literal[valid_values]
  - validate_output_format_for_cli() → Literal[valid_values]

All validation is now done using Pydantic v2 patterns directly in model classes.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

__all__: list[str] = []

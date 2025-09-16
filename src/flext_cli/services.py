"""FLEXT CLI Services - Consolidated into FlextCliService.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli.core import FlextCliService

# ABI-preserving alias - FlextCliServices functionality now in FlextCliService
FlextCliServices = FlextCliService

__all__ = ["FlextCliServices"]

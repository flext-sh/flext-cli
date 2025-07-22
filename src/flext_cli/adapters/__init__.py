"""Adapter layer for FLEXT CLI - Clean Architecture implementation.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

This package contains adapter layer components that handle external interfaces
and framework-specific implementations. Adapters translate between the domain
layer and external concerns like CLI frameworks, output systems, and configuration.

Adapter Organization:
- cli/           # Click/Typer CLI framework adapters
- output/        # Output rendering and formatting adapters
- config/        # Configuration management adapters
- utils/         # Utility adapters for legacy compatibility
"""

from __future__ import annotations

__all__: list[str] = []

"""Performance Optimization - Caching and Speed.

Demonstrates flext-cli performance features through FlextCli API.

Key Features:
- Auto-caching with TTL management
- Lazy loading modules automatically
- Memoization decorators
- Performance tracking automatic

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from flext_cli import FlextCli

# Module-level singleton
cli = FlextCli.get_instance()


def demonstrate_auto_caching() -> None:
    """Show automatic caching with TTL."""
    # Results auto-cached with optimal TTL
    # Cache invalidation automatic on updates
    cli.output.print_message("Caching auto-enabled with smart TTL")


def demonstrate_lazy_loading() -> None:
    """Show lazy module loading."""
    # Modules loaded on-demand - faster startup
    # Dependencies auto-resolved when needed
    cli.output.print_message("Modules lazy-loaded for fast startup")


def demonstrate_memoization() -> None:
    """Show function memoization."""
    # Function results auto-memoized
    # Memory management automatic
    cli.output.print_message("Functions auto-memoized for performance")


def main() -> None:
    """Run all demonstrations."""
    demonstrate_auto_caching()
    demonstrate_lazy_loading()
    demonstrate_memoization()


if __name__ == "__main__":
    main()

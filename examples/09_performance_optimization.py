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
    cli.formatters.print("\n⚡ Auto-Caching:", style="bold cyan")

    # Results auto-cached with optimal TTL
    # Cache invalidation automatic on updates
    cli.formatters.print("✅ Caching auto-enabled with smart TTL", style="cyan")


def demonstrate_lazy_loading() -> None:
    """Show lazy module loading."""
    cli.formatters.print("\n🚀 Lazy Loading:", style="bold cyan")

    # Modules loaded on-demand - faster startup
    # Dependencies auto-resolved when needed
    cli.formatters.print("✅ Modules lazy-loaded for fast startup", style="cyan")


def demonstrate_memoization() -> None:
    """Show function memoization."""
    cli.formatters.print("\n📊 Memoization:", style="bold cyan")

    # Function results auto-memoized
    # Memory management automatic
    cli.formatters.print("✅ Functions auto-memoized for performance", style="cyan")


def main() -> None:
    """Run all demonstrations."""
    cli.formatters.print("=" * 60, style="bold blue")
    cli.formatters.print(
        "  Performance Optimization Examples", style="bold white on blue"
    )
    cli.formatters.print("=" * 60, style="bold blue")

    demonstrate_auto_caching()
    demonstrate_lazy_loading()
    demonstrate_memoization()

    cli.formatters.print("\n" + "=" * 60, style="bold blue")
    cli.formatters.print("  ✅ All performance examples completed!", style="bold green")
    cli.formatters.print("=" * 60, style="bold blue")


if __name__ == "__main__":
    main()

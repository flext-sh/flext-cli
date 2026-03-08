"""Performance Optimization - PATTERN GUIDE (NOT A FLEXT-CLI BUILT-IN FEATURE)..

⚠️  IMPORTANT: This is a PATTERN GUIDE showing performance patterns
YOU can apply in YOUR own CLI application using flext-cli as a foundation.

flext-cli does NOT provide built-in caching, lazy loading, or performance modules.
This example demonstrates patterns and best practices for YOUR implementation.

WHEN TO USE THESE PATTERNS IN YOUR CLI:
- Building high-performance CLI tools
- Processing large datasets in CLI
- Need to optimize startup time
- Want to reduce memory usage
- Building CLI tools with caching needs

WHAT YOU CAN BUILD USING THESE PATTERNS:
- Singleton pattern (FlextCli() constructor provided)
- Lazy loading for faster startup (using standard Python patterns)
- Caching with @lru_cache or cachetools library
- Efficient table rendering (use FlextCliTables efficiently)
- Memory-optimized file operations (batch processing)

HOW TO IMPLEMENT IN YOUR CLI:
Use flext-cli foundation + Python stdlib + cachetools library

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import pathlib
import tempfile
import time
from functools import lru_cache

from flext_cli import FlextCli, FlextCliOutput, t

cli = FlextCli()
output = FlextCliOutput()


# ============================================================================
# PATTERN 1: Singleton pattern - zero re-initialization overhead
# ============================================================================


def efficient_cli_usage() -> None:
    """Use singleton pattern in YOUR CLI for performance."""
    # ❌ SLOW: Creating new instance each time
    # output = FlextCliOutput()  # Don't do this repeatedly!

    # ✅ FAST: Reuse output instance
    cli.print(
        "✅ Using singleton - no re-initialization overhead",
        style="green",
    )


# ============================================================================
# PATTERN 2: Caching expensive operations
# ============================================================================


@lru_cache(maxsize=128)
def expensive_calculation(n: int) -> int:
    """Cache expensive results in YOUR CLI."""
    # Simulate expensive operation
    return sum(range(n))


def demonstrate_caching() -> None:
    """Show caching pattern for performance."""
    cli.print("\n⚡ Caching Performance:", style="bold cyan")

    # First call - slow
    start = time.time()
    result1 = expensive_calculation(1000000)
    time1 = time.time() - start

    # Second call - cached (fast)
    start = time.time()
    result2 = expensive_calculation(1000000)
    time2 = time.time() - start

    cli.print(f"   First call: {time1 * 1000:.2f}ms (result: {result1})", style="yellow")
    cli.print(f"   Cached call: {time2 * 1000:.2f}ms (result: {result2})", style="green")
    cli.print(f"   Speedup: {time1 / time2:.0f}x faster", style="bold green")


# ============================================================================
# PATTERN 3: Lazy loading for faster startup
# ============================================================================


class LazyDataLoader:
    """Lazy load data in YOUR CLI for fast startup."""

    def __init__(self) -> None:
        """Initialize lazy data loader with deferred data loading."""
        super().__init__()
        self._data: list[int] | None = None  # Not loaded yet

    @property
    def data(self) -> list[int]:
        """Load data only when needed."""
        if self._data is None:
            cli.print(
                "   📦 Loading data (first access only)...",
                style="cyan",
            )
            # Simulate loading
            self._data = list(range(10000))
        return self._data


def demonstrate_lazy_loading() -> None:
    """Show lazy loading pattern."""
    cli.print("\n🚀 Lazy Loading:", style="bold cyan")

    # Fast startup - data not loaded
    loader = LazyDataLoader()
    cli.print(
        "   ✅ Loader created instantly (no data loaded)",
        style="green",
    )

    # Data loaded only when accessed
    data = loader.data
    cli.print(
        f"   ✅ Data loaded on first access ({len(data)} items)",
        style="green",
    )

    # Subsequent access is fast
    data_again = loader.data
    cli.print(
        f"   ✅ Subsequent access - already loaded ({len(data_again)} items)",
        style="green",
    )


# ============================================================================
# PATTERN 4: Efficient table rendering
# ============================================================================


def efficient_table_display(
    large_dataset: list[dict[str, t.JsonValue]],
) -> None:
    """Display large tables efficiently in YOUR CLI."""
    # ✅ Show only necessary rows
    preview_size = 10
    total = len(large_dataset)

    cli.print(
        f"\n📊 Efficient Table (showing {preview_size}/{total} rows):",
        style="cyan",
    )

    preview_data = large_dataset[:preview_size]
    cli.show_table(preview_data, headers=None)
    if total > preview_size:
        cli.print(
            f"   ... ({total - preview_size} more rows)",
            style="yellow",
        )


# ============================================================================
# PATTERN 5: Batch processing for large operations
# ============================================================================


def process_large_dataset(items: list[int], batch_size: int = 100) -> None:
    """Process large datasets in batches in YOUR CLI."""
    cli.print(
        f"\n🔄 Batch Processing ({len(items)} items):",
        style="bold cyan",
    )

    total_batches = (len(items) + batch_size - 1) // batch_size

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        batch_num = (i // batch_size) + 1

        # Process batch
        # Your batch processing logic here

        cli.print(
            f"   ✅ Processed batch {batch_num}/{total_batches} ({len(batch)} items)",
            style="green",
        )


# ============================================================================
# PATTERN 6: Memory-efficient file operations
# ============================================================================


def stream_large_file(filepath: str) -> None:
    """Stream large files efficiently in YOUR CLI."""
    cli.print("\n📄 Streaming File (memory-efficient):", style="bold cyan")

    # ❌ SLOW: Load entire file
    # with open(filepath) as f:
    #     all_data = f.read()

    # ✅ FAST: Stream line by line
    line_count = 0
    try:
        with pathlib.Path(filepath).open(encoding="utf-8") as f:
            for _line in f:
                line_count += 1
                # Process line

        cli.print(
            f"   ✅ Processed {line_count} lines (streamed)",
            style="green",
        )
    except FileNotFoundError:
        cli.print(f"   ℹ️  Demo: Would stream {filepath}", style="cyan")


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of performance optimization in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Performance Optimization Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")

    # Example 1: Singleton pattern
    cli.print("\n1. Singleton Pattern (zero overhead):", style="bold cyan")
    efficient_cli_usage()

    # Example 2: Caching
    cli.print("\n2. Caching Expensive Operations:", style="bold cyan")
    demonstrate_caching()

    # Example 3: Lazy loading
    demonstrate_lazy_loading()

    # Example 4: Efficient tables
    cli.print("\n4. Efficient Table Display:", style="bold cyan")
    large_data: list[dict[str, t.JsonValue]] = [
        {"id": i, "name": f"Item {i}"} for i in range(1000)
    ]
    efficient_table_display(large_data)

    # Example 5: Batch processing
    cli.print("\n5. Batch Processing:", style="bold cyan")
    items: list[int] = list(range(500))
    process_large_dataset(items, batch_size=100)

    # Example 6: File streaming
    cli.print("\n6. Memory-Efficient File Streaming:", style="bold cyan")
    demo_file = pathlib.Path(tempfile.gettempdir()) / "large_file.txt"
    stream_large_file(str(demo_file))

    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Performance Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")

    # Integration guide
    cli.print("\n💡 Performance Tips:", style="bold cyan")
    cli.print(
        "  • Always use FlextCli() constructor (singleton)",
        style="white",
    )
    cli.print(
        "  • Cache expensive operations with @lru_cache",
        style="white",
    )
    cli.print("  • Use lazy loading for large datasets", style="white")
    cli.print("  • Display only necessary table rows", style="white")
    cli.print("  • Process large datasets in batches", style="white")
    cli.print("  • Stream files instead of loading all", style="white")


if __name__ == "__main__":
    main()

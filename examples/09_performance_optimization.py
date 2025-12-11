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

from flext_cli import FlextCliOutput, FlextCliTables, m, t

output = FlextCliOutput()


# ============================================================================
# PATTERN 1: Singleton pattern - zero re-initialization overhead
# ============================================================================


def efficient_cli_usage() -> None:
    """Use singleton pattern in YOUR CLI for performance."""
    # ❌ SLOW: Creating new instance each time
    # output = FlextCliOutput()  # Don't do this repeatedly!

    # ✅ FAST: Reuse output instance
    output.print_message(
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
    output.print_message("\n⚡ Caching Performance:", style="bold cyan")

    # First call - slow
    start = time.time()
    expensive_calculation(1000000)
    time1 = time.time() - start

    # Second call - cached (fast)
    start = time.time()
    expensive_calculation(1000000)
    time2 = time.time() - start

    output.print_message(f"   First call: {time1 * 1000:.2f}ms", style="yellow")
    output.print_message(f"   Cached call: {time2 * 1000:.2f}ms", style="green")
    output.print_message(f"   Speedup: {time1 / time2:.0f}x faster", style="bold green")


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
            output.print_message(
                "   📦 Loading data (first access only)...",
                style="cyan",
            )
            # Simulate loading
            self._data = list(range(10000))
        return self._data


def demonstrate_lazy_loading() -> None:
    """Show lazy loading pattern."""
    output.print_message("\n🚀 Lazy Loading:", style="bold cyan")

    # Fast startup - data not loaded
    loader = LazyDataLoader()
    output.print_message(
        "   ✅ Loader created instantly (no data loaded)",
        style="green",
    )

    # Data loaded only when accessed
    _ = loader.data
    output.print_message("   ✅ Data loaded on first access", style="green")

    # Subsequent access is fast
    _ = loader.data
    output.print_message("   ✅ Subsequent access - already loaded", style="green")


# ============================================================================
# PATTERN 4: Efficient table rendering
# ============================================================================


def efficient_table_display(
    large_dataset: list[t.JsonDict],
) -> None:
    """Display large tables efficiently in YOUR CLI."""
    # ✅ Show only necessary rows
    preview_size = 10
    total = len(large_dataset)

    output.print_message(
        f"\n📊 Efficient Table (showing {preview_size}/{total} rows):",
        style="cyan",
    )

    # Display only preview
    preview_data = large_dataset[:preview_size]

    tables = FlextCliTables()
    config = m.Cli.TableConfig(table_format="simple")
    table_result = tables.create_table(preview_data, config=config)

    if table_result.is_success:
        output.print_message(
            f"   ... ({total - preview_size} more rows)",
            style="yellow",
        )


# ============================================================================
# PATTERN 5: Batch processing for large operations
# ============================================================================


def process_large_dataset(items: list[int], batch_size: int = 100) -> None:
    """Process large datasets in batches in YOUR CLI."""
    output.print_message(
        f"\n🔄 Batch Processing ({len(items)} items):",
        style="bold cyan",
    )

    total_batches = (len(items) + batch_size - 1) // batch_size

    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        batch_num = (i // batch_size) + 1

        # Process batch
        # Your batch processing logic here

        output.print_message(
            f"   ✅ Processed batch {batch_num}/{total_batches} ({len(batch)} items)",
            style="green",
        )


# ============================================================================
# PATTERN 6: Memory-efficient file operations
# ============================================================================


def stream_large_file(filepath: str) -> None:
    """Stream large files efficiently in YOUR CLI."""
    output.print_message("\n📄 Streaming File (memory-efficient):", style="bold cyan")

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

        output.print_message(
            f"   ✅ Processed {line_count} lines (streamed)",
            style="green",
        )
    except FileNotFoundError:
        output.print_message(f"   ℹ️  Demo: Would stream {filepath}", style="cyan")


# ============================================================================
# REAL USAGE EXAMPLES
# ============================================================================


def main() -> None:
    """Examples of performance optimization in YOUR code."""
    output.print_message("=" * 70, style="bold blue")
    output.print_message("  Performance Optimization Library Usage", style="bold white")
    output.print_message("=" * 70, style="bold blue")

    # Example 1: Singleton pattern
    output.print_message("\n1. Singleton Pattern (zero overhead):", style="bold cyan")
    efficient_cli_usage()

    # Example 2: Caching
    output.print_message("\n2. Caching Expensive Operations:", style="bold cyan")
    demonstrate_caching()

    # Example 3: Lazy loading
    demonstrate_lazy_loading()

    # Example 4: Efficient tables
    output.print_message("\n4. Efficient Table Display:", style="bold cyan")
    large_data: list[t.JsonDict] = [{"id": i, "name": f"Item {i}"} for i in range(1000)]
    efficient_table_display(large_data)

    # Example 5: Batch processing
    output.print_message("\n5. Batch Processing:", style="bold cyan")
    items: list[int] = list(range(500))
    process_large_dataset(items, batch_size=100)

    # Example 6: File streaming
    output.print_message("\n6. Memory-Efficient File Streaming:", style="bold cyan")
    demo_file = pathlib.Path(tempfile.gettempdir()) / "large_file.txt"
    stream_large_file(str(demo_file))

    output.print_message("\n" + "=" * 70, style="bold blue")
    output.print_message("  ✅ Performance Examples Complete", style="bold green")
    output.print_message("=" * 70, style="bold blue")

    # Integration guide
    output.print_message("\n💡 Performance Tips:", style="bold cyan")
    output.print_message(
        "  • Always use FlextCli() constructor (singleton)",
        style="white",
    )
    output.print_message(
        "  • Cache expensive operations with @lru_cache",
        style="white",
    )
    output.print_message("  • Use lazy loading for large datasets", style="white")
    output.print_message("  • Display only necessary table rows", style="white")
    output.print_message("  • Process large datasets in batches", style="white")
    output.print_message("  • Stream files instead of loading all", style="white")


if __name__ == "__main__":
    main()

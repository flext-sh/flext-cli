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
- Singleton pattern (shared cli instance provided)
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
from collections.abc import Mapping, Sequence
from functools import lru_cache

from examples import c, t
from flext_cli import cli


def efficientusage() -> None:
    """Use singleton pattern in YOUR CLI for performance."""
    cli.print(
        "✅ Using singleton - no re-initialization overhead",
        style=c.Cli.MessageStyles.GREEN,
    )


@lru_cache(maxsize=c.PERF_LRU_CACHE_SIZE)
def expensive_calculation(n: int) -> int:
    """Cache expensive results in YOUR CLI."""
    return sum(range(n))


def demonstrate_caching() -> None:
    """Show caching pattern for performance."""
    cli.print("\n⚡ Caching Performance:", style=c.Cli.MessageStyles.BOLD_CYAN)
    start = time.time()
    result1 = expensive_calculation(c.PERF_CALC_INPUT_SIZE)
    time1 = time.time() - start
    start = time.time()
    result2 = expensive_calculation(c.PERF_CALC_INPUT_SIZE)
    time2 = time.time() - start
    cli.print(
        f"   First call: {time1 * 1000:.2f}ms (result: {result1})",
        style=c.Cli.MessageStyles.YELLOW,
    )
    cli.print(
        f"   Cached call: {time2 * 1000:.2f}ms (result: {result2})",
        style=c.Cli.MessageStyles.GREEN,
    )
    cli.print(
        f"   Speedup: {time1 / time2:.0f}x faster", style=c.Cli.MessageStyles.BOLD_GREEN
    )


class LazyDataLoader:
    """Lazy load data in YOUR CLI for fast startup."""

    def __init__(self) -> None:
        """Initialize lazy data loader with deferred data loading."""
        super().__init__()
        self._data: Sequence[int] | None = None

    @property
    def data(self) -> Sequence[int]:
        """Load data only when needed."""
        if self._data is None:
            cli.print(
                "   📦 Loading data (first access only)...",
                style=c.Cli.MessageStyles.CYAN,
            )
            self._data = list(range(c.PERF_LAZY_DATA_SIZE))
        return self._data


def demonstrate_lazy_loading() -> None:
    """Show lazy loading pattern."""
    cli.print("\n🚀 Lazy Loading:", style=c.Cli.MessageStyles.BOLD_CYAN)
    loader = LazyDataLoader()
    cli.print(
        "   ✅ Loader created instantly (no data loaded)",
        style=c.Cli.MessageStyles.GREEN,
    )
    data = loader.data
    cli.print(
        f"   ✅ Data loaded on first access ({len(data)} items)",
        style=c.Cli.MessageStyles.GREEN,
    )
    data_again = loader.data
    cli.print(
        f"   ✅ Subsequent access - already loaded ({len(data_again)} items)",
        style=c.Cli.MessageStyles.GREEN,
    )


def efficient_table_display(
    large_dataset: Sequence[Mapping[str, t.Container]],
) -> None:
    """Display large tables efficiently in YOUR CLI."""
    preview_size = c.PERF_TABLE_PREVIEW_SIZE
    total = len(large_dataset)
    cli.print(
        f"\n📊 Efficient Table (showing {preview_size}/{total} rows):",
        style=c.Cli.MessageStyles.CYAN,
    )
    preview_data = large_dataset[:preview_size]
    cli.show_table(preview_data, show_header=False)
    if total > preview_size:
        cli.print(
            f"   ... ({total - preview_size} more rows)",
            style=c.Cli.MessageStyles.YELLOW,
        )


def process_large_dataset(
    items: Sequence[int],
    batch_size: int = c.PERF_DEFAULT_BATCH_SIZE,
) -> None:
    """Process large datasets in batches in YOUR CLI."""
    cli.print(
        f"\n🔄 Batch Processing ({len(items)} items):",
        style=c.Cli.MessageStyles.BOLD_CYAN,
    )
    total_batches = (len(items) + batch_size - 1) // batch_size
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        batch_num = i // batch_size + 1
        cli.print(
            f"   ✅ Processed batch {batch_num}/{total_batches} ({len(batch)} items)",
            style=c.Cli.MessageStyles.GREEN,
        )


def stream_large_file(filepath: str) -> None:
    """Stream large files efficiently in YOUR CLI."""
    cli.print(
        "\n📄 Streaming File (memory-efficient):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    line_count = 0
    try:
        with pathlib.Path(filepath).open(encoding="utf-8") as f:
            for _line in f:
                line_count += 1
        cli.print(
            f"   ✅ Processed {line_count} lines (streamed)",
            style=c.Cli.MessageStyles.GREEN,
        )
    except FileNotFoundError:
        cli.print(
            f"   ℹ️  Demo: Would stream {filepath}", style=c.Cli.MessageStyles.CYAN
        )


def main() -> None:
    """Examples of performance optimization in YOUR code."""
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  Performance Optimization Library Usage", style=c.Cli.MessageStyles.BOLD_WHITE
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "\n1. Singleton Pattern (zero overhead):", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    efficientusage()
    cli.print("\n2. Caching Expensive Operations:", style=c.Cli.MessageStyles.BOLD_CYAN)
    demonstrate_caching()
    demonstrate_lazy_loading()
    cli.print("\n4. Efficient Table Display:", style=c.Cli.MessageStyles.BOLD_CYAN)
    large_data: Sequence[Mapping[str, t.Container]] = [
        {"id": i, "name": f"Item {i}"} for i in range(c.PERF_DATASET_SIZE)
    ]
    efficient_table_display(large_data)
    cli.print("\n5. Batch Processing:", style=c.Cli.MessageStyles.BOLD_CYAN)
    items: Sequence[int] = list(range(c.PERF_ITEMS_SIZE))
    process_large_dataset(items, batch_size=c.PERF_DEFAULT_BATCH_SIZE)
    cli.print(
        "\n6. Memory-Efficient File Streaming:", style=c.Cli.MessageStyles.BOLD_CYAN
    )
    demo_file = pathlib.Path(tempfile.gettempdir()) / "large_file.txt"
    stream_large_file(str(demo_file))
    cli.print("\n" + "=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print(
        "  ✅ Performance Examples Complete", style=c.Cli.MessageStyles.BOLD_GREEN
    )
    cli.print("=" * 70, style=c.Cli.MessageStyles.BOLD_BLUE)
    cli.print("\n💡 Performance Tips:", style=c.Cli.MessageStyles.BOLD_CYAN)
    cli.print(
        "  • Always use the shared cli singleton", style=c.Cli.MessageStyles.WHITE
    )
    cli.print(
        "  • Cache expensive operations with @lru_cache",
        style=c.Cli.MessageStyles.WHITE,
    )
    cli.print(
        "  • Use lazy loading for large datasets", style=c.Cli.MessageStyles.WHITE
    )
    cli.print("  • Display only necessary table rows", style=c.Cli.MessageStyles.WHITE)
    cli.print("  • Process large datasets in batches", style=c.Cli.MessageStyles.WHITE)
    cli.print(
        "  • Stream files instead of loading all", style=c.Cli.MessageStyles.WHITE
    )


if __name__ == "__main__":
    main()

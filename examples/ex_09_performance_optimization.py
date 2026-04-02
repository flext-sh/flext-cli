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
from collections.abc import Sequence
from functools import lru_cache

from examples import t
from flext_cli import cli


def efficient_cli_usage() -> None:
    """Use singleton pattern in YOUR CLI for performance."""
    cli.print("✅ Using singleton - no re-initialization overhead", style="green")


@lru_cache(maxsize=128)
def expensive_calculation(n: int) -> int:
    """Cache expensive results in YOUR CLI."""
    return sum(range(n))


def demonstrate_caching() -> None:
    """Show caching pattern for performance."""
    cli.print("\n⚡ Caching Performance:", style="bold cyan")
    start = time.time()
    result1 = expensive_calculation(1000000)
    time1 = time.time() - start
    start = time.time()
    result2 = expensive_calculation(1000000)
    time2 = time.time() - start
    cli.print(
        f"   First call: {time1 * 1000:.2f}ms (result: {result1})",
        style="yellow",
    )
    cli.print(
        f"   Cached call: {time2 * 1000:.2f}ms (result: {result2})",
        style="green",
    )
    cli.print(f"   Speedup: {time1 / time2:.0f}x faster", style="bold green")


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
            cli.print("   📦 Loading data (first access only)...", style="cyan")
            self._data = list(range(10000))
        return self._data


def demonstrate_lazy_loading() -> None:
    """Show lazy loading pattern."""
    cli.print("\n🚀 Lazy Loading:", style="bold cyan")
    loader = LazyDataLoader()
    cli.print("   ✅ Loader created instantly (no data loaded)", style="green")
    data = loader.data
    cli.print(f"   ✅ Data loaded on first access ({len(data)} items)", style="green")
    data_again = loader.data
    cli.print(
        f"   ✅ Subsequent access - already loaded ({len(data_again)} items)",
        style="green",
    )


def efficient_table_display(
    large_dataset: Sequence[t.ContainerMapping],
) -> None:
    """Display large tables efficiently in YOUR CLI."""
    preview_size = 10
    total = len(large_dataset)
    cli.print(
        f"\n📊 Efficient Table (showing {preview_size}/{total} rows):",
        style="cyan",
    )
    preview_data = large_dataset[:preview_size]
    cli.show_table(preview_data, show_header=False)
    if total > preview_size:
        cli.print(f"   ... ({total - preview_size} more rows)", style="yellow")


def process_large_dataset(items: Sequence[int], batch_size: int = 100) -> None:
    """Process large datasets in batches in YOUR CLI."""
    cli.print(f"\n🔄 Batch Processing ({len(items)} items):", style="bold cyan")
    total_batches = (len(items) + batch_size - 1) // batch_size
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size]
        batch_num = i // batch_size + 1
        cli.print(
            f"   ✅ Processed batch {batch_num}/{total_batches} ({len(batch)} items)",
            style="green",
        )


def stream_large_file(filepath: str) -> None:
    """Stream large files efficiently in YOUR CLI."""
    cli.print("\n📄 Streaming File (memory-efficient):", style="bold cyan")
    line_count = 0
    try:
        with pathlib.Path(filepath).open(encoding="utf-8") as f:
            for _line in f:
                line_count += 1
        cli.print(f"   ✅ Processed {line_count} lines (streamed)", style="green")
    except FileNotFoundError:
        cli.print(f"   ℹ️  Demo: Would stream {filepath}", style="cyan")


def main() -> None:
    """Examples of performance optimization in YOUR code."""
    cli.print("=" * 70, style="bold blue")
    cli.print("  Performance Optimization Library Usage", style="bold white")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n1. Singleton Pattern (zero overhead):", style="bold cyan")
    efficient_cli_usage()
    cli.print("\n2. Caching Expensive Operations:", style="bold cyan")
    demonstrate_caching()
    demonstrate_lazy_loading()
    cli.print("\n4. Efficient Table Display:", style="bold cyan")
    large_data: Sequence[t.ContainerMapping] = [
        {"id": i, "name": f"Item {i}"} for i in range(1000)
    ]
    efficient_table_display(large_data)
    cli.print("\n5. Batch Processing:", style="bold cyan")
    items: Sequence[int] = list(range(500))
    process_large_dataset(items, batch_size=100)
    cli.print("\n6. Memory-Efficient File Streaming:", style="bold cyan")
    demo_file = pathlib.Path(tempfile.gettempdir()) / "large_file.txt"
    stream_large_file(str(demo_file))
    cli.print("\n" + "=" * 70, style="bold blue")
    cli.print("  ✅ Performance Examples Complete", style="bold green")
    cli.print("=" * 70, style="bold blue")
    cli.print("\n💡 Performance Tips:", style="bold cyan")
    cli.print("  • Always use the shared cli singleton", style="white")
    cli.print("  • Cache expensive operations with @lru_cache", style="white")
    cli.print("  • Use lazy loading for large datasets", style="white")
    cli.print("  • Display only necessary table rows", style="white")
    cli.print("  • Process large datasets in batches", style="white")
    cli.print("  • Stream files instead of loading all", style="white")


if __name__ == "__main__":
    main()

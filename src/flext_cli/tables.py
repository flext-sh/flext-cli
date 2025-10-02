"""FLEXT CLI - Tabulate Integration Layer.

This module provides lightweight ASCII table formatting as an alternative to Rich tables.
Optimized for performance, plain text output, and large datasets.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Iterable, Sequence
from typing import ClassVar, cast

from tabulate import tabulate

from flext_core import (
    FlextContainer,
    FlextLogger,
    FlextResult,
    FlextService,
)


class FlextCliTables(FlextService[None]):
    """Tabulate integration for lightweight ASCII tables.

    Provides simple, fast table formatting without ANSI codes.
    Perfect for:
    - Plain text output
    - Large datasets (performance-critical)
    - Log files and reports
    - Markdown/reStructuredText generation
    - HTML table generation

    Examples:
        >>> tables = FlextCliTables()
        >>>
        >>> data = [
        ...     {"name": "Alice", "age": 30, "city": "NYC"},
        ...     {"name": "Bob", "age": 25, "city": "LA"},
        ... ]
        >>>
        >>> # Simple grid table
        >>> result = tables.create_table(data, table_format="grid")
        >>>
        >>> # Markdown pipe table
        >>> result = tables.create_table(data, table_format="pipe")
        >>>
        >>> # Custom headers and alignment
        >>> result = tables.create_table(
        ...     data,
        ...     headers=["Name", "Age", "City"],
        ...     table_format="fancy_grid",
        ...     align=["left", "right", "left"],
        ... )

    Note:
        Use Rich tables (FlextCliFormatters) for:
        - Colored output
        - Interactive terminals
        - Visual styling
        - Borders and boxes

        Use Tabulate tables (this class) for:
        - Plain text output
        - Performance
        - File output
        - Markdown/HTML generation

    """

    # Available table formats (ClassVar for Pydantic compatibility)
    FORMATS: ClassVar[dict[str, str]] = {
        "plain": "Minimal formatting, no borders",
        "simple": "Simple ASCII borders",
        "grid": "Grid-style ASCII table",
        "fancy_grid": "Fancy grid with double lines",
        "pipe": "Markdown pipe table",
        "orgtbl": "Emacs org-mode table",
        "jira": "Jira markup table",
        "presto": "Presto SQL output",
        "pretty": "Pretty ASCII table",
        "psql": "PostgreSQL psql output",
        "rst": "reStructuredText grid",
        "mediawiki": "MediaWiki markup",
        "moinmoin": "MoinMoin markup",
        "youtrack": "YouTrack markup",
        "html": "HTML table",
        "unsafehtml": "HTML without escaping",
        "latex": "LaTeX table",
        "latex_raw": "LaTeX table (raw)",
        "latex_booktabs": "LaTeX booktabs style",
        "latex_longtable": "LaTeX longtable",
        "textile": "Textile markup",
        "tsv": "Tab-separated values",
    }

    def __init__(self) -> None:
        """Initialize Tabulate tables layer."""
        super().__init__()
        self._logger = FlextLogger(__name__)
        self._container = FlextContainer.get_global()

    # =========================================================================
    # TABLE CREATION
    # =========================================================================

    def create_table(
        self,
        data: Iterable[Sequence[object] | dict[str, object]],
        headers: str | Sequence[str] = "keys",
        *,
        table_format: str = "simple",
        align: str | Sequence[str] | None = None,
        floatfmt: str = "g",
        numalign: str = "decimal",
        stralign: str = "left",
        missingval: str = "",
        showindex: bool | str = False,
        disable_numparse: bool = False,
        colalign: Sequence[str] | None = None,
    ) -> FlextResult[str]:
        """Create formatted ASCII table using tabulate.

        Args:
            data: Table data (list of dicts, list of lists, etc.)
            headers: Column headers
                - "keys" (default): Use dict keys as headers
                - "firstrow": Use first row as headers
                - Sequence: Custom headers
                - "" or []: No headers
            table_format: Table format (see FORMATS for options)
            align: Column alignment (left, right, center, decimal)
            floatfmt: Float number formatting
            numalign: Number alignment
            stralign: String alignment
            missingval: Value for missing data
            showindex: Show row index (bool or index name)
            disable_numparse: Disable automatic number parsing
            colalign: Column alignment per column

        Returns:
            FlextResult containing formatted table string

        Example:
            >>> tables = FlextCliTables()
            >>> data = [
            ...     {"name": "Alice", "age": 30, "salary": 75000.50},
            ...     {"name": "Bob", "age": 25, "salary": 65000.75},
            ... ]
            >>> result = tables.create_table(data, table_format="grid")
            >>> if result.is_success:
            ...     print(result.unwrap())
            +-------+-----+----------+
            | name  | age | salary   |
            +=======+=====+==========+
            | Alice |  30 | 75000.5  |
            +-------+-----+----------+
            | Bob   |  25 | 65000.75 |
            +-------+-----+----------+

        """
        if not data:
            return FlextResult[str].fail("Table data cannot be empty")

        if table_format not in self.FORMATS:
            return FlextResult[str].fail(
                f"Invalid table format: {table_format}. Available: {', '.join(self.FORMATS.keys())}"
            )

        try:
            # Build tabulate kwargs
            kwargs: dict[str, object] = {
                "tablefmt": table_format,
                "headers": headers,
                "floatfmt": floatfmt,
                "numalign": numalign,
                "stralign": stralign,
                "missingval": missingval,
                "showindex": showindex,
                "disable_numparse": disable_numparse,
            }

            # Add column alignment if specified
            if colalign is not None:
                kwargs["colalign"] = colalign
            elif align is not None:
                # Convert single align to list if needed
                if isinstance(align, str):
                    # Will be applied to all columns
                    kwargs["colalign"] = None
                else:
                    kwargs["colalign"] = align

            # Generate table
            table_str = tabulate(data, **cast("dict", kwargs))

            self._logger.debug(
                "Created table",
                extra={
                    "table_format": table_format,
                    "row_count": len(list(data))
                    if hasattr(data, "__len__")
                    else "unknown",
                },
            )

            return FlextResult[str].ok(table_str)

        except Exception as e:
            error_msg = f"Failed to create table: {e}"
            self._logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def create_simple_table(
        self,
        data: Iterable[Sequence[object] | dict[str, object]],
        headers: Sequence[str] | None = None,
    ) -> FlextResult[str]:
        """Create simple ASCII table with minimal formatting.

        Convenience method for quick table creation.

        Args:
            data: Table data
            headers: Optional custom headers (uses "keys" for dicts if None)

        Returns:
            FlextResult containing formatted table string

        Example:
            >>> tables = FlextCliTables()
            >>> data = [["Alice", 30], ["Bob", 25]]
            >>> result = tables.create_simple_table(data, headers=["Name", "Age"])

        """
        header_value: str | Sequence[str] = headers or "keys"
        return self.create_table(data, headers=header_value, table_format="simple")

    def create_grid_table(
        self,
        data: Iterable[Sequence[object] | dict[str, object]],
        headers: Sequence[str] | None = None,
        *,
        fancy: bool = False,
    ) -> FlextResult[str]:
        """Create grid-style ASCII table.

        Args:
            data: Table data
            headers: Optional custom headers
            fancy: Use fancy grid with double lines

        Returns:
            FlextResult containing formatted table string

        Example:
            >>> tables = FlextCliTables()
            >>> data = [{"item": "Apple", "qty": 5}, {"item": "Banana", "qty": 3}]
            >>> result = tables.create_grid_table(data, fancy=True)

        """
        header_value: str | Sequence[str] = headers or "keys"
        table_format = "fancy_grid" if fancy else "grid"
        return self.create_table(data, headers=header_value, table_format=table_format)

    def create_markdown_table(
        self,
        data: Iterable[Sequence[object] | dict[str, object]],
        headers: Sequence[str] | None = None,
    ) -> FlextResult[str]:
        """Create Markdown pipe table.

        Perfect for generating Markdown documentation.

        Args:
            data: Table data
            headers: Optional custom headers

        Returns:
            FlextResult containing Markdown table string

        Example:
            >>> tables = FlextCliTables()
            >>> data = [
            ...     {"feature": "Fast", "status": "✅"},
            ...     {"feature": "Simple", "status": "✅"},
            ... ]
            >>> result = tables.create_markdown_table(data)
            | feature | status |
            |---------|--------|
            | Fast    | ✅     |
            | Simple  | ✅     |

        """
        header_value: str | Sequence[str] = headers or "keys"
        return self.create_table(data, headers=header_value, table_format="pipe")

    def create_html_table(
        self,
        data: Iterable[Sequence[object] | dict[str, object]],
        headers: Sequence[str] | None = None,
        *,
        escape: bool = True,
    ) -> FlextResult[str]:
        """Create HTML table.

        Args:
            data: Table data
            headers: Optional custom headers
            escape: Escape HTML entities (recommended for untrusted data)

        Returns:
            FlextResult containing HTML table string

        Example:
            >>> tables = FlextCliTables()
            >>> data = [{"name": "Alice", "email": "alice@example.com"}]
            >>> result = tables.create_html_table(data)

        """
        header_value: str | Sequence[str] = headers or "keys"
        table_format = "html" if escape else "unsafehtml"
        return self.create_table(data, headers=header_value, table_format=table_format)

    def create_latex_table(
        self,
        data: Iterable[Sequence[object] | dict[str, object]],
        headers: Sequence[str] | None = None,
        *,
        booktabs: bool = False,
        longtable: bool = False,
    ) -> FlextResult[str]:
        """Create LaTeX table.

        Args:
            data: Table data
            headers: Optional custom headers
            booktabs: Use booktabs style (professional)
            longtable: Use longtable for multi-page tables

        Returns:
            FlextResult containing LaTeX table string

        Example:
            >>> tables = FlextCliTables()
            >>> data = [{"var": "x", "value": 42}, {"var": "y", "value": 13}]
            >>> result = tables.create_latex_table(data, booktabs=True)

        """
        header_value: str | Sequence[str] = headers or "keys"

        if longtable:
            table_format = "latex_longtable"
        elif booktabs:
            table_format = "latex_booktabs"
        else:
            table_format = "latex"

        return self.create_table(data, headers=header_value, table_format=table_format)

    def create_rst_table(
        self,
        data: Iterable[Sequence[object] | dict[str, object]],
        headers: Sequence[str] | None = None,
    ) -> FlextResult[str]:
        """Create reStructuredText grid table.

        Perfect for Sphinx documentation.

        Args:
            data: Table data
            headers: Optional custom headers

        Returns:
            FlextResult containing reStructuredText table string

        Example:
            >>> tables = FlextCliTables()
            >>> data = [{"func": "read()", "returns": "str"}]
            >>> result = tables.create_rst_table(data)

        """
        header_value: str | Sequence[str] = headers or "keys"
        return self.create_table(data, headers=header_value, table_format="rst")

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def list_formats(self) -> list[str]:
        """List all available table formats.

        Returns:
            List of format names

        """
        return list(self.FORMATS.keys())

    def get_format_description(self, format_name: str) -> FlextResult[str]:
        """Get description of a table format.

        Args:
            format_name: Format name

        Returns:
            FlextResult containing format description

        """
        if format_name not in self.FORMATS:
            return FlextResult[str].fail(f"Unknown format: {format_name}")

        return FlextResult[str].ok(self.FORMATS[format_name])

    def print_available_formats(self) -> FlextResult[None]:
        """Print all available table formats with descriptions.

        Returns:
            FlextResult[None]

        """
        try:
            formats_data = [
                {"format": name, "description": desc}
                for name, desc in self.FORMATS.items()
            ]

            # Use tabulate to print the formats table
            tabulate(
                formats_data,
                headers="keys",
                tablefmt="grid",
            )

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to print formats: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def execute(self) -> FlextResult[None]:
        """Execute Tabulate tables layer operations.

        Returns:
            FlextResult[None]

        """
        return FlextResult[None].ok(None)


__all__ = [
    "FlextCliTables",
]

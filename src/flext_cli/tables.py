"""FLEXT CLI - Tabulate Integration Layer.

This module provides lightweight ASCII table formatting as an alternative to Rich tables.
Optimized for performance, plain text output, and large datasets.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Iterable, Sequence

from flext_core import FlextLogger, FlextResult, FlextService, FlextTypes
from tabulate import tabulate

from flext_cli.constants import FlextCliConstants


class FlextCliTables(FlextService[object]):
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

    def __init__(self) -> None:
        """Initialize Tabulate tables layer with Phase 1 context enrichment."""
        super().__init__()
        # Initialize logger - inherited from FlextService via FlextMixins
        self._logger = FlextLogger(__name__)

    # =========================================================================
    # TABLE CREATION
    # =========================================================================

    def create_table(
        self,
        data: Iterable[Sequence[object] | dict[str, FlextTypes.JsonValue]],
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
                - "keys" (default): Use dict[str, object] keys as headers
                - "firstrow": Use first row as headers
                - Sequence: Custom headers
                - "" or []: No headers
            table_format: Table format (see FlextCliConstants.TABLE_FORMATS for options)
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

        if table_format not in FlextCliConstants.TABLE_FORMATS:
            return FlextResult[str].fail(
                f"Invalid table format: {table_format}. Available: {', '.join(FlextCliConstants.TABLE_FORMATS.keys())}"
            )

        try:
            # Determine column alignment parameter
            final_colalign: Sequence[str] | None = None
            if colalign is not None:
                final_colalign = colalign
            elif align is not None and not isinstance(align, str):
                # align is a sequence, use it directly
                final_colalign = align
            # If align is a string, final_colalign stays None (applied to all columns)

            # Handle headers for different data types
            tabulate_headers = headers
            if (
                isinstance(data, list)
                and data
                and isinstance(data[0], dict)
                and isinstance(headers, (list, tuple))
            ):
                # For list of dicts with sequence headers, use "keys"
                tabulate_headers = "keys"
            # Otherwise keep as-is (string or None)

            # Call tabulate directly with explicit parameters (type-safe)
            table_str = tabulate(
                data,
                headers=tabulate_headers,
                tablefmt=table_format,
                floatfmt=floatfmt,
                numalign=numalign,
                stralign=stralign,
                missingval=missingval,
                showindex=showindex,
                disable_numparse=disable_numparse,
                colalign=final_colalign,
            )

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
        data: Iterable[Sequence[object] | dict[str, FlextTypes.JsonValue]],
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
        data: Iterable[Sequence[object] | dict[str, FlextTypes.JsonValue]],
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
        data: Iterable[Sequence[object] | dict[str, FlextTypes.JsonValue]],
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
        data: Iterable[Sequence[object] | dict[str, FlextTypes.JsonValue]],
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
        data: Iterable[Sequence[object] | dict[str, FlextTypes.JsonValue]],
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
        data: Iterable[Sequence[object] | dict[str, FlextTypes.JsonValue]],
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

    def list_formats(self) -> FlextTypes.StringList:
        """List all available table formats.

        Returns:
            List of format names

        """
        return list(FlextCliConstants.TABLE_FORMATS.keys())

    def get_format_description(self, format_name: str) -> FlextResult[str]:
        """Get description of a table format.

        Args:
            format_name: Format name

        Returns:
            FlextResult containing format description

        """
        if format_name not in FlextCliConstants.TABLE_FORMATS:
            return FlextResult[str].fail(f"Unknown format: {format_name}")

        return FlextResult[str].ok(FlextCliConstants.TABLE_FORMATS[format_name])

    def print_available_formats(self) -> FlextResult[None]:
        """Print all available table formats with descriptions.

        Returns:
            FlextResult[None]

        """
        try:
            formats_data = [
                {"format": name, "description": desc}
                for name, desc in FlextCliConstants.TABLE_FORMATS.items()
            ]

            # Use tabulate directly to create the formats table
            table_str = tabulate(
                formats_data,
                headers="keys",
                tablefmt="grid",
            )
            # Output through logger instead of print (linting requirement)
            self._logger.info(table_str)

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = f"Failed to print formats: {e}"
            self._logger.exception(error_msg)
            return FlextResult[None].fail(error_msg)

    def execute(self) -> FlextResult[object]:
        """Execute Tabulate tables layer operations.

        Returns:
            FlextResult[object]

        """
        return FlextResult[object].ok(None)


__all__ = [
    "FlextCliTables",
]

"""FLEXT CLI - Tabulate Integration Layer.

This module provides lightweight ASCII table formatting as an alternative to Rich tables.
Optimized for performance, plain text output, and large datasets.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from collections.abc import Iterable, Sequence

from flext_core import FlextLogger, FlextResult, FlextService, FlextTypes
from tabulate import tabulate

from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels


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
        config: FlextCliModels.TableConfig | None = None,
    ) -> FlextResult[str]:
        """Create formatted ASCII table using tabulate with Pydantic config.

        Args:
            data: Table data (list of dicts, list of lists, etc.)
            config: Table configuration (TableConfig model with all settings)
                   If None, uses default configuration

        Returns:
            FlextResult containing formatted table string

        Example:
            >>> tables = FlextCliTables()
            >>> data = [{"name": "Alice", "age": 30}]
            >>> # With config object
            >>> config = FlextCliModels.TableConfig(table_format="grid")
            >>> result = tables.create_table(data, config)
            >>> # Without config (uses defaults)
            >>> result = tables.create_table(data)

        """
        # Use default config if none provided
        cfg = config or FlextCliModels.TableConfig()

        # Railway pattern: validate → prepare headers → create table
        return (
            self._validate_table_data(data, cfg.table_format)
            .flat_map(lambda _: self._prepare_headers(data, cfg.headers))
            .flat_map(lambda headers: self._create_table_string(data, cfg, headers))
        )

    def _validate_table_data(
        self,
        data: Iterable[Sequence[object] | dict[str, FlextTypes.JsonValue]],
        table_format: str,
    ) -> FlextResult[None]:
        """Validate table data and format."""
        if not data:
            return FlextResult[None].fail(
                FlextCliConstants.TablesErrorMessages.TABLE_DATA_EMPTY
            )

        if table_format not in FlextCliConstants.TABLE_FORMATS:
            return FlextResult[None].fail(
                FlextCliConstants.TablesErrorMessages.INVALID_TABLE_FORMAT.format(
                    table_format=table_format,
                    available_formats=", ".join(FlextCliConstants.TABLE_FORMATS.keys()),
                )
            )

        return FlextResult[None].ok(None)

    def _prepare_headers(
        self,
        data: Iterable[Sequence[object] | dict[str, FlextTypes.JsonValue]],
        headers: str | Sequence[str],
    ) -> FlextResult[str | Sequence[str]]:
        """Prepare headers based on data type."""
        # For list of dicts with sequence headers, use "keys"
        if (
            isinstance(data, list)
            and data
            and isinstance(data[0], dict)
            and isinstance(headers, (list, tuple))
        ):
            return FlextResult[str | Sequence[str]].ok(
                FlextCliConstants.TableFormats.KEYS
            )

        return FlextResult[str | Sequence[str]].ok(headers)

    def _create_table_string(
        self,
        data: Iterable[Sequence[object] | dict[str, FlextTypes.JsonValue]],
        cfg: FlextCliModels.TableConfig,
        headers: str | Sequence[str],
    ) -> FlextResult[str]:
        """Create table string using tabulate with exception handling."""
        try:
            table_str = tabulate(
                data,
                headers=headers,
                tablefmt=cfg.table_format,
                floatfmt=cfg.floatfmt,
                numalign=cfg.numalign,
                stralign=cfg.stralign,
                missingval=cfg.missingval,
                showindex=cfg.showindex,
                disable_numparse=cfg.disable_numparse,
                colalign=cfg.get_effective_colalign(),
            )

            self._logger.debug(
                FlextCliConstants.TablesLogMessages.TABLE_CREATED,
                extra={
                    FlextCliConstants.TablesLogMessages.TABLE_FORMAT_KEY: cfg.table_format,
                    FlextCliConstants.TablesLogMessages.ROW_COUNT_KEY: len(list(data))
                    if hasattr(data, "__len__")
                    else "unknown",
                },
            )

            return FlextResult[str].ok(table_str)

        except Exception as e:
            error_msg = (
                FlextCliConstants.TablesErrorMessages.TABLE_CREATION_FAILED.format(
                    error=e
                )
            )
            self._logger.exception(error_msg)
            return FlextResult[str].fail(error_msg)

    def _create_formatted_table(
        self,
        data: Iterable[Sequence[object] | dict[str, FlextTypes.JsonValue]],
        table_format: str,
        headers: Sequence[str] | None = None,
    ) -> FlextResult[str]:
        """Generic method to create table with specific format.

        Eliminates code duplication across convenience methods.

        Args:
            data: Table data
            table_format: Table format string (from FlextCliConstants.TableFormats)
            headers: Optional custom headers (uses "keys" for dicts if None)

        Returns:
            FlextResult containing formatted table string

        """
        config = FlextCliModels.TableConfig(
            table_format=table_format,
            headers=headers or FlextCliConstants.TableFormats.KEYS,
        )
        return self.create_table(data, config)

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
        return self._create_formatted_table(
            data, FlextCliConstants.TableFormats.SIMPLE, headers
        )

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
        table_format = (
            FlextCliConstants.TableFormats.FANCY_GRID
            if fancy
            else FlextCliConstants.TableFormats.GRID
        )
        return self._create_formatted_table(data, table_format, headers)

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
        return self._create_formatted_table(
            data, FlextCliConstants.TableFormats.PIPE, headers
        )

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
        table_format = (
            FlextCliConstants.TableFormats.HTML
            if escape
            else FlextCliConstants.TableFormats.UNSAFEHTML
        )
        return self._create_formatted_table(data, table_format, headers)

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
        if longtable:
            table_format = FlextCliConstants.TableFormats.LATEX_LONGTABLE
        elif booktabs:
            table_format = FlextCliConstants.TableFormats.LATEX_BOOKTABS
        else:
            table_format = FlextCliConstants.TableFormats.LATEX

        return self._create_formatted_table(data, table_format, headers)

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
        return self._create_formatted_table(
            data, FlextCliConstants.TableFormats.RST, headers
        )

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    def list_formats(self) -> list[str]:
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
            return FlextResult[str].fail(
                FlextCliConstants.TablesErrorMessages.UNKNOWN_FORMAT.format(
                    format_name=format_name
                )
            )

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
                headers=FlextCliConstants.TableFormats.KEYS,
                tablefmt=FlextCliConstants.TableFormats.GRID,
            )
            # Output through logger instead of print (linting requirement)
            self._logger.info(table_str)

            return FlextResult[None].ok(None)

        except Exception as e:
            error_msg = (
                FlextCliConstants.TablesErrorMessages.PRINT_FORMATS_FAILED.format(
                    error=e
                )
            )
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

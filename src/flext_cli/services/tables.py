"""FLEXT CLI - Tabulate Integration Layer.

This module provides lightweight ASCII table formatting as an alternative
to Rich tables. Optimized for performance, plain text output, and large datasets.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from itertools import starmap

from flext_core import FlextRuntime, r
from tabulate import tabulate

from flext_cli.constants import FlextCliConstants
from flext_cli.models import m
from flext_cli.protocols import p
from flext_cli.typings import t
from flext_cli.utilities import FlextCliUtilities


class FlextCliTables:
    """Tabulate integration for lightweight ASCII tables.

    Business Rules:
    ───────────────
    1. Table format MUST be validated against supported formats
    2. Table data MUST be validated (non-empty, iterable)
    3. Headers MUST match data structure (keys or explicit headers)
    4. Table formatting MUST handle empty data gracefully
    5. Format discovery MUST return all available tabulate formats
    6. All operations MUST use r[T] for error handling
    7. Table creation MUST respect TableConfig settings
    8. Performance MUST be optimized for large datasets

    Architecture Implications:
    ───────────────────────────
    - Uses tabulate library directly (no wrappers)
    - TableConfig model provides type-safe configuration
    - Format discovery uses tabulate's internal format list
    - Extends FlextCliServiceBase for consistent logging
    - Railway-Oriented Programming via FlextResult for error handling

    Audit Implications:
    ───────────────────
    - Table creation MUST be logged with format type and data size
    - Format validation failures MUST be logged
    - Empty data handling MUST be logged for monitoring
    - Performance metrics SHOULD be logged for large datasets

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

    # =========================================================================
    # TABLE CREATION
    # =========================================================================

    @staticmethod
    def create_table(
        data: t.Cli.TableData,
        config: p.Cli.TableConfigProtocol | None = None,
        **config_kwargs: t.GeneralValueType,
    ) -> r[str]:
        """Create formatted ASCII table using tabulate with Pydantic config.

        Uses build_options_from_kwargs pattern for automatic kwargs to Model conversion.

        Args:
            data: Table data (list of dicts, list of lists, etFlextCliConstants.Cli.)
            config: Table configuration (TableConfig model with all settings)
                   If None, uses default configuration
            **config_kwargs: Individual config option overrides (snake_case field names)

        Returns:
            FlextResult containing formatted table string

        Example:
            >>> tables = FlextCliTables()
            >>> data = [{"name": "Alice", "age": 30}]
            >>> # With config object
            >>> config = m.Cli.Value.TableConfig(table_format="grid")
            >>> result = tables.create_table(data, config)
            >>> # With kwargs (automatic conversion)
            >>> result = tables.create_table(
            ...     data, table_format="grid", headers=["Name", "Age"]
            ... )
            >>> # Without config (uses defaults)
            >>> result = tables.create_table(data)

        """
        # Use Configuration.build_options_from_kwargs pattern for automatic conversion
        # Type narrowing: check if config is instance of TableConfig (not just protocol)
        config_concrete: m.Cli.TableConfig | None = (
            config if isinstance(config, m.Cli.TableConfig) else None
        )
        config_result = FlextCliUtilities.Configuration.build_options_from_kwargs(
            model_class=m.Cli.TableConfig,
            explicit_options=config_concrete,
            default_factory=m.Cli.TableConfig,
            **config_kwargs,
        )
        if config_result.is_failure:
            # Python 3.13: Direct attribute access - more elegant and type-safe
            return r[str].fail(
                config_result.error or "Invalid table configuration",
            )
        # Python 3.13: Direct attribute access - unwrap() provides safe access
        cfg = config_result.value or m.Cli.TableConfig()

        # Railway pattern: validate → prepare headers → create table
        validation_result = self._validate_table_data(data, cfg.table_format)
        if validation_result.is_failure:
            # Python 3.13: Direct attribute access - more elegant and type-safe
            return r[str].fail(
                validation_result.error or "Table data validation failed",
                error_code=validation_result.error_code,
                error_data=validation_result.error_data,
            )

        headers_result = self._prepare_headers(data, cfg.headers)
        if headers_result.is_failure:
            return r[str].fail(
                headers_result.error or "Headers preparation failed",
                error_code=headers_result.error_code,
                error_data=headers_result.error_data,
            )

        headers = headers_result.value
        return self._create_table_string(data, cfg, headers)

    @staticmethod
    def _validate_table_data(
        data: t.Cli.TableData,
        table_format: str,
    ) -> r[bool]:
        """Validate table data and format.

        Returns:
            r[bool]: True if validation passed, failure on error

        """
        if not data:
            return r[bool].fail(
                FlextCliConstants.Cli.TablesErrorMessages.TABLE_DATA_EMPTY,
            )

        if table_format not in FlextCliConstants.Cli.TABLE_FORMATS:
            available_formats_list = list(FlextCliConstants.Cli.TABLE_FORMATS.keys())
            return r[bool].fail(
                FlextCliConstants.Cli.TablesErrorMessages.INVALID_TABLE_FORMAT.format(
                    table_format=table_format,
                    available_formats=", ".join(available_formats_list),
                ),
            )

        return r[bool].ok(True)

    @staticmethod
    def _prepare_headers(
        data: t.Cli.TableData,
        headers: str | Sequence[str],
    ) -> r[str | Sequence[str]]:
        """Prepare headers based on data type."""
        # For list of dicts with sequence headers, use "keys"
        # Type narrowing: data is Iterable, convert to list for is_list_like check
        if isinstance(data, (list, tuple)):
            data_list: list[t.GeneralValueType] = list(data)
            data_as_general: t.GeneralValueType = data_list
        elif isinstance(data, Mapping):
            data_list = []
            data_as_general = data
        else:
            data_list = []
            data_as_general = data

        if (
            FlextRuntime.is_list_like(data_as_general)
            and data_list
            and isinstance(data_list[0], (dict, Mapping))
            and isinstance(
                headers,
                (list, tuple),
            )  # tuple check is specific, not dict/list
        ):
            return r[str | Sequence[str]].ok(
                FlextCliConstants.Cli.TableFormats.KEYS,
            )

        return r[str | Sequence[str]].ok(headers)

    def _calculate_column_count(
        self,
        data: t.Cli.TableData,
        headers: str | Sequence[str],
    ) -> int:
        """Calculate number of columns based on headers and data type.

        Returns:
            Number of columns, or 0 if unable to determine.

        """
        # If headers is a sequence, count directly
        if isinstance(headers, Sequence) and not isinstance(headers, str):
            return len(headers)

        # If headers="keys", count from data
        if headers == "keys":
            if isinstance(data, Mapping):
                return len(data)
            # Check if data is sequence with at least one element
            if (
                isinstance(data, Sequence)
                and not isinstance(data, str)
                and len(data) > 0
            ):
                first_row = data[0]
                if isinstance(first_row, (Mapping, Sequence)) and not isinstance(
                    first_row,
                    str,
                ):
                    return len(first_row)

        return 0

    def _create_table_string(
        self,
        data: t.Cli.TableData,
        cfg: m.Cli.TableConfig,
        headers: str | Sequence[str],
    ) -> r[str]:
        """Create table string using tabulate with exception handling."""
        try:
            # Get colalign and validate/truncate if necessary
            colalign = cfg.get_effective_colalign()

            # Calculate number of columns for colalign validation
            num_cols = self._calculate_column_count(data, headers)

            # Truncate colalign if needed
            if colalign is not None and num_cols > 0 and len(colalign) > num_cols:
                colalign = colalign[:num_cols]

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
                colalign=colalign,
            )

            # Calculate row count safely - data can be Sequence or Mapping
            row_count: int | str = "unknown"
            if (isinstance(data, Sequence) and not isinstance(data, str)) or isinstance(
                data,
                Mapping,
            ):
                row_count = len(data)

            self.logger.debug(
                FlextCliConstants.Cli.TablesLogMessages.TABLE_CREATED,
                extra={
                    FlextCliConstants.Cli.TablesLogMessages.TABLE_FORMAT_KEY: (
                        cfg.table_format
                    ),
                    FlextCliConstants.Cli.TablesLogMessages.ROW_COUNT_KEY: row_count,
                },
            )

            return r[str].ok(table_str)

        except Exception as e:
            error_msg = (
                FlextCliConstants.Cli.TablesErrorMessages.TABLE_CREATION_FAILED.format(
                    error=e,
                )
            )
            self.logger.exception(error_msg)
            return r[str].fail(error_msg)

    def _create_formatted_table(
        self,
        data: t.Cli.TableData,
        table_format: str,
        headers: Sequence[str] | None = None,
    ) -> r[str]:
        """Generic method to create table with specific format.

        Eliminates code duplication across convenience methods.

        Args:
            data: Table data
            table_format: Table format string (from FlextCliConstants.Cli.TableFormats)
            headers: Optional custom headers (uses "keys" for dicts if None)

        Returns:
            FlextResult containing formatted table string

        """
        # Use build_options_from_kwargs pattern - pass kwargs directly
        validated_headers = (
            headers if headers is not None else FlextCliConstants.Cli.TableFormats.KEYS
        )
        return self.create_table(
            data,
            config=None,
            table_format=table_format,
            headers=validated_headers,
        )

    @staticmethod
    def create_simple_table(
        data: t.Cli.TableData,
        headers: Sequence[str] | None = None,
    ) -> r[str]:
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
            data,
            FlextCliConstants.Cli.TableFormats.SIMPLE,
            headers,
        )

    def create_grid_table(
        self,
        data: t.Cli.TableData,
        headers: Sequence[str] | None = None,
        *,
        fancy: bool = False,
    ) -> r[str]:
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
            FlextCliConstants.Cli.TableFormats.FANCY_GRID
            if fancy
            else FlextCliConstants.Cli.TableFormats.GRID
        )
        return self._create_formatted_table(data, table_format, headers)

    def create_markdown_table(
        self,
        data: t.Cli.TableData,
        headers: Sequence[str] | None = None,
    ) -> r[str]:
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
            data,
            FlextCliConstants.Cli.TableFormats.PIPE,
            headers,
        )

    def create_html_table(
        self,
        data: t.Cli.TableData,
        headers: Sequence[str] | None = None,
        *,
        escape: bool = True,
    ) -> r[str]:
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
            FlextCliConstants.Cli.TableFormats.HTML
            if escape
            else FlextCliConstants.Cli.TableFormats.UNSAFEHTML
        )
        return self._create_formatted_table(data, table_format, headers)

    def create_latex_table(
        self,
        data: t.Cli.TableData,
        headers: Sequence[str] | None = None,
        *,
        booktabs: bool = False,
        longtable: bool = False,
    ) -> r[str]:
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
            table_format = FlextCliConstants.Cli.TableFormats.LATEX_LONGTABLE
        elif booktabs:
            table_format = FlextCliConstants.Cli.TableFormats.LATEX_BOOKTABS
        else:
            table_format = FlextCliConstants.Cli.TableFormats.LATEX

        return self._create_formatted_table(data, table_format, headers)

    def create_rst_table(
        self,
        data: t.Cli.TableData,
        headers: Sequence[str] | None = None,
    ) -> r[str]:
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
            data,
            FlextCliConstants.Cli.TableFormats.RST,
            headers,
        )

    # =========================================================================
    # UTILITY METHODS
    # =========================================================================

    @staticmethod
    def list_formats() -> list[str]:
        """List all available table formats.

        Returns:
            List of format names

        """
        return list(FlextCliConstants.Cli.TABLE_FORMATS.keys())

    @staticmethod
    def get_format_description(format_name: str) -> r[str]:
        """Get description of a table format.

        Args:
            format_name: Format name

        Returns:
            FlextResult containing format description

        """
        if format_name not in FlextCliConstants.Cli.TABLE_FORMATS:
            return r[str].fail(
                FlextCliConstants.Cli.TablesErrorMessages.UNKNOWN_FORMAT.format(
                    format_name=format_name,
                ),
            )

        return r[str].ok(FlextCliConstants.Cli.TABLE_FORMATS[format_name])

    @staticmethod
    def print_available_formats() -> r[bool]:
        """Print all available table formats with descriptions.

        Returns:
            r[bool]: True if formats printed successfully, failure on error

        """
        try:
            # Use FlextCliUtilities.process to convert TABLE_FORMATS to list
            def convert_format(name: str, desc: str) -> dict[str, str]:
                """Convert format to dict."""
                return {"format": name, "description": desc}

            # Convert TABLE_FORMATS dict to list of format dicts
            formats_data: list[dict[str, str]] = list(
                starmap(convert_format, FlextCliConstants.Cli.TABLE_FORMATS.items()),
            )

            # Use tabulate directly to create the formats table
            table_str = tabulate(
                formats_data,
                headers=FlextCliConstants.Cli.TableFormats.KEYS,
                tablefmt=FlextCliConstants.Cli.TableFormats.GRID,
            )
            # Output through logger instead of print (linting requirement)
            self.logger.info(table_str)

            return r[bool].ok(True)

        except Exception as e:
            error_msg = (
                FlextCliConstants.Cli.TablesErrorMessages.PRINT_FORMATS_FAILED.format(
                    error=e,
                )
            )
            self.logger.exception(error_msg)
            return r[bool].fail(error_msg)


__all__ = [
    "FlextCliTables",
]

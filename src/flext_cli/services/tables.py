"""FLEXT CLI - Tabulate Integration Layer.

This module provides lightweight ASCII table formatting as an alternative
to Rich tables. Optimized for performance, plain text output, and large datasets.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Iterable, Mapping, Sequence

from flext_core import (
    FlextConstants,
    FlextExceptions,
    FlextModels,
    FlextProtocols,
    FlextResult,
    FlextRuntime,
    t,
    u,
)
from tabulate import tabulate

from flext_cli.base import FlextCliServiceBase
from flext_cli.constants import FlextCliConstants
from flext_cli.models import FlextCliModels

# Aliases for static method calls and type references
# Use u.* for FlextUtilities static methods
# Use t.* for FlextTypes type references
# Use c.* for FlextConstants constants
# Use m.* for FlextModels model references
# Use p.* for FlextProtocols protocol references
# Use r.* for FlextResult methods
# Use e.* for FlextExceptions
# u is already imported from flext_core
# t is already imported from flext_core
c = FlextConstants
m = FlextModels
p = FlextProtocols
r = FlextResult
e = FlextExceptions

# Type alias for table data to avoid long lines
type TableData = Iterable[
    Sequence[t.GeneralValueType] | Mapping[str, t.GeneralValueType]
]


class FlextCliTables(FlextCliServiceBase):
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

    def __init__(self) -> None:
        """Initialize Tabulate tables layer with Phase 1 context enrichment."""
        super().__init__()

    def execute(  # noqa: PLR6301
        self, **_kwargs: t.JsonDict
    ) -> r[t.JsonDict]:
        """Execute the main domain service operation - required by FlextService.

        Args:
            **_kwargs: Additional execution parameters (unused, for FlextService compatibility)

        Returns:
            r[t.JsonDict]: Service execution result

        """
        return r[t.JsonDict].ok({})

    # =========================================================================
    # TABLE CREATION
    # =========================================================================

    def create_table(
        self,
        data: TableData,
        config: FlextCliModels.TableConfig | None = None,
        **config_kwargs: t.GeneralValueType,
    ) -> r[str]:
        """Create formatted ASCII table using tabulate with Pydantic config.

        Uses build_options_from_kwargs pattern for automatic kwargs to Model conversion.

        Args:
            data: Table data (list of dicts, list of lists, etc.)
            config: Table configuration (TableConfig model with all settings)
                   If None, uses default configuration
            **config_kwargs: Individual config option overrides (snake_case field names)

        Returns:
            FlextResult containing formatted table string

        Example:
            >>> tables = FlextCliTables()
            >>> data = [{"name": "Alice", "age": 30}]
            >>> # With config object
            >>> config = FlextCliModels.TableConfig(table_format="grid")
            >>> result = tables.create_table(data, config)
            >>> # With kwargs (automatic conversion)
            >>> result = tables.create_table(
            ...     data, table_format="grid", headers=["Name", "Age"]
            ... )
            >>> # Without config (uses defaults)
            >>> result = tables.create_table(data)

        """
        # Use Configuration.build_options_from_kwargs pattern for automatic conversion
        config_result = u.Configuration.build_options_from_kwargs(
            model_class=FlextCliModels.TableConfig,
            explicit_options=config,
            default_factory=FlextCliModels.TableConfig,
            **config_kwargs,
        )
        if config_result.is_failure:
            return r[str].fail(
                u.err(config_result, default="Invalid table configuration"),
            )
        cfg = u.val(config_result, default=FlextCliModels.TableConfig())

        # Railway pattern: validate → prepare headers → create table
        validation_result = self._validate_table_data(data, cfg.table_format)
        if validation_result.is_failure:
            return r[str].fail(
                u.err(validation_result, default="Table data validation failed"),
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

        headers = headers_result.unwrap()
        return self._create_table_string(data, cfg, headers)

    @staticmethod
    def _validate_table_data(
        data: TableData,
        table_format: str,
    ) -> r[bool]:
        """Validate table data and format.

        Returns:
            r[bool]: True if validation passed, failure on error

        """
        if not data:
            return r[bool].fail(
                FlextCliConstants.TablesErrorMessages.TABLE_DATA_EMPTY,
            )

        if table_format not in FlextCliConstants.TABLE_FORMATS:
            return r[bool].fail(
                FlextCliConstants.TablesErrorMessages.INVALID_TABLE_FORMAT.format(
                    table_format=table_format,
                    available_formats=u.join(
                        u.keys(FlextCliConstants.TABLE_FORMATS), sep=", "
                    ),
                ),
            )

        return r[bool].ok(True)

    @staticmethod
    def _prepare_headers(
        data: TableData,
        headers: str | Sequence[str],
    ) -> r[str | Sequence[str]]:
        """Prepare headers based on data type."""
        # For list of dicts with sequence headers, use "keys"
        # Type narrowing: data is Iterable, convert to list for is_list_like check
        data_as_general: t.GeneralValueType = (
            list(data)
            if isinstance(data, Iterable) and not isinstance(data, str)
            else data
        )
        # Convert to list for indexing - TableData is Iterable, need list for [0]
        data_list = (
            list(data)
            if isinstance(data, Iterable) and not isinstance(data, str)
            else []
        )
        if (
            FlextRuntime.is_list_like(data_as_general)
            and data_list
            and FlextRuntime.is_dict_like(data_list[0])
            and isinstance(
                headers,
                (list, tuple),
            )  # tuple check is specific, not dict/list
        ):
            return r[str | Sequence[str]].ok(
                FlextCliConstants.TableFormats.KEYS,
            )

        return r[str | Sequence[str]].ok(headers)

    def _create_table_string(
        self,
        data: TableData,
        cfg: FlextCliModels.TableConfig,
        headers: str | Sequence[str],
    ) -> r[str]:
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

            self.logger.debug(
                FlextCliConstants.TablesLogMessages.TABLE_CREATED,
                extra={
                    FlextCliConstants.TablesLogMessages.TABLE_FORMAT_KEY: (
                        cfg.table_format
                    ),
                    FlextCliConstants.TablesLogMessages.ROW_COUNT_KEY: len(list(data))
                    if hasattr(data, "__len__")
                    else "unknown",
                },
            )

            return r[str].ok(table_str)

        except Exception as e:
            error_msg = (
                FlextCliConstants.TablesErrorMessages.TABLE_CREATION_FAILED.format(
                    error=e,
                )
            )
            self.logger.exception(error_msg)
            return r[str].fail(error_msg)

    def _create_formatted_table(
        self,
        data: TableData,
        table_format: str,
        headers: Sequence[str] | None = None,
    ) -> r[str]:
        """Generic method to create table with specific format.

        Eliminates code duplication across convenience methods.

        Args:
            data: Table data
            table_format: Table format string (from FlextCliConstants.TableFormats)
            headers: Optional custom headers (uses "keys" for dicts if None)

        Returns:
            FlextResult containing formatted table string

        """
        # Use build_options_from_kwargs pattern - pass kwargs directly
        validated_headers = u.when(
            condition=headers is not None,
            then_value=headers,
            else_value=FlextCliConstants.TableFormats.KEYS,
        )
        return self.create_table(
            data,
            config=None,
            table_format=table_format,
            headers=validated_headers,
        )

    def create_simple_table(
        self,
        data: TableData,
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
            FlextCliConstants.TableFormats.SIMPLE,
            headers,
        )

    def create_grid_table(
        self,
        data: TableData,
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
            FlextCliConstants.TableFormats.FANCY_GRID
            if fancy
            else FlextCliConstants.TableFormats.GRID
        )
        return self._create_formatted_table(data, table_format, headers)

    def create_markdown_table(
        self,
        data: TableData,
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
            FlextCliConstants.TableFormats.PIPE,
            headers,
        )

    def create_html_table(
        self,
        data: TableData,
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
            FlextCliConstants.TableFormats.HTML
            if escape
            else FlextCliConstants.TableFormats.UNSAFEHTML
        )
        return self._create_formatted_table(data, table_format, headers)

    def create_latex_table(
        self,
        data: TableData,
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
            table_format = FlextCliConstants.TableFormats.LATEX_LONGTABLE
        elif booktabs:
            table_format = FlextCliConstants.TableFormats.LATEX_BOOKTABS
        else:
            table_format = FlextCliConstants.TableFormats.LATEX

        return self._create_formatted_table(data, table_format, headers)

    def create_rst_table(
        self,
        data: TableData,
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
            FlextCliConstants.TableFormats.RST,
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
        return list(FlextCliConstants.TABLE_FORMATS.keys())

    @staticmethod
    def get_format_description(format_name: str) -> r[str]:
        """Get description of a table format.

        Args:
            format_name: Format name

        Returns:
            FlextResult containing format description

        """
        if format_name not in FlextCliConstants.TABLE_FORMATS:
            return r[str].fail(
                FlextCliConstants.TablesErrorMessages.UNKNOWN_FORMAT.format(
                    format_name=format_name,
                ),
            )

        return r[str].ok(FlextCliConstants.TABLE_FORMATS[format_name])

    def print_available_formats(self) -> r[bool]:
        """Print all available table formats with descriptions.

        Returns:
            r[bool]: True if formats printed successfully, failure on error

        """
        try:
            # Use u.process to convert TABLE_FORMATS to list
            def convert_format(name: str, desc: str) -> dict[str, str]:
                """Convert format to dict."""
                return {"format": name, "description": desc}

            process_result = u.process(
                dict(FlextCliConstants.TABLE_FORMATS),
                processor=convert_format,
                on_error="skip",
            )
            formats_data: list[dict[str, str]] = (
                list(process_result.value.values())
                if process_result.is_success and isinstance(process_result.value, dict)
                else []
            )

            # Use tabulate directly to create the formats table
            table_str = tabulate(
                formats_data,
                headers=FlextCliConstants.TableFormats.KEYS,
                tablefmt=FlextCliConstants.TableFormats.GRID,
            )
            # Output through logger instead of print (linting requirement)
            self.logger.info(table_str)

            return r[bool].ok(True)

        except Exception as e:
            error_msg = (
                FlextCliConstants.TablesErrorMessages.PRINT_FORMATS_FAILED.format(
                    error=e,
                )
            )
            self.logger.exception(error_msg)
            return r[bool].fail(error_msg)


__all__ = [
    "FlextCliTables",
]

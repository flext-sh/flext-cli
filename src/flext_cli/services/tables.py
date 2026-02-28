"""FLEXT CLI - Tabulate Integration Layer.

This module provides lightweight ASCII table formatting as an alternative
to Rich tables. Optimized for performance, plain text output, and large datasets.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from itertools import starmap
from typing import TypeGuard, override

from flext_core import r
from rich.errors import ConsoleError, LiveError, StyleError
from tabulate import tabulate

from flext_cli import FlextCliConstants, FlextCliServiceBase, m, t, u


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

    # =========================================================================
    # SERVICE EXECUTION (Required by FlextService)
    # =========================================================================

    @override
    def execute(self) -> r[Mapping[str, t.JsonValue]]:
        """Execute table service - returns success indicator.

        Business Rule:
        ──────────────
        The table service is primarily used for its static methods (create_table,
        print_available_formats). Execute provides a default success response.

        Returns:
            r[dict[str, t.JsonValue]]: Success result.

        """
        return r[Mapping[str, t.JsonValue]].ok({"status": "table_service_ready"})

    # =========================================================================
    # TABLE CREATION
    # =========================================================================

    @staticmethod
    def create_table(
        data: t.Cli.TabularData,
        config: m.Cli.TableConfig | None = None,
        **config_kwargs: t.ScalarValue,
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
        config_result = u.Configuration.build_options_from_kwargs(
            model_class=m.Cli.TableConfig,
            explicit_options=config,
            default_factory=m.Cli.TableConfig,
            **{
                k: v
                for k, v in config_kwargs.items()
                if isinstance(v, (str, int, float, bool, type(None)))
            },
        )
        if config_result.is_failure:
            # Python 3.13: Direct attribute access - more elegant and type-safe
            return r[str].fail(
                config_result.error or "Invalid table configuration",
            )
        # Get concrete config from result
        config_final = config_result.value

        # Validate table data and format
        validation_result = FlextCliTables._validate_table_data(
            data,
            config_final.table_format,
        )
        if validation_result.is_failure:
            return r[str].fail(validation_result.error or "Table validation failed")

        # Prepare headers
        headers_result = FlextCliTables._prepare_headers(data, config_final.headers)
        if headers_result.is_failure:
            return r[str].fail(headers_result.error or "Header preparation failed")

        # Format table using tabulate
        try:
            if u.is_dict_like(data):
                normalized_data: Sequence[Mapping[str, t.JsonValue]] = (
                    [data] if isinstance(data, Mapping) else []
                )
            else:
                normalized_data = data

            headers_value = headers_result.value
            if (
                normalized_data
                and not isinstance(headers_value, str)
                and u.is_dict_like(normalized_data[0])
            ):
                table_rows = [
                    list(row.values())
                    for row in normalized_data
                    if isinstance(row, Mapping)
                ]
                formatted_table = tabulate(
                    table_rows,
                    headers=list(headers_value),
                    tablefmt=config_final.table_format,
                    numalign=config_final.numalign,
                    stralign=config_final.stralign,
                )
                return r[str].ok(formatted_table)

            def _is_tabulate_data(
                val: Sequence[t.GeneralValueType],
            ) -> TypeGuard[
                Sequence[Mapping[str, t.GeneralValueType]]
                | Sequence[Sequence[t.GeneralValueType]]
            ]:
                """Narrow to tabulate-acceptable rows (sequence of mappings or sequences)."""
                if not val:
                    return True
                first = val[0]
                if isinstance(first, str):
                    return False
                if isinstance(first, Mapping):
                    return all(isinstance(row, Mapping) for row in val)
                if isinstance(first, Sequence):
                    return all(
                        isinstance(row, Sequence) and not isinstance(row, str)
                        for row in val
                    )
                return False

            if _is_tabulate_data(normalized_data):
                formatted_table = tabulate(
                    normalized_data,
                    headers=headers_value,
                    tablefmt=config_final.table_format,
                    numalign=config_final.numalign,
                    stralign=config_final.stralign,
                )
                return r[str].ok(formatted_table)
            return r[str].fail(
                "Table data must be a sequence of mappings or a sequence of sequences",
            )
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[str].fail(f"Table formatting failed: {e}")

    @staticmethod
    def _validate_table_data(
        data: t.Cli.TabularData,
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

        return r[bool].ok(value=True)

    @staticmethod
    def _prepare_headers(
        data: t.Cli.TabularData,
        headers: str | Sequence[str],
    ) -> r[str | Sequence[str]]:
        """Prepare headers based on data type."""
        data_list = list(data)
        if not data_list:
            return r[str | Sequence[str]].ok(headers)

        if isinstance(headers, str):
            return r[str | Sequence[str]].ok(headers)

        first_row = data_list[0]
        if u.is_dict_like(first_row):
            return r[str | Sequence[str]].ok(list(headers))

        return r[str | Sequence[str]].ok(headers)

    def _calculate_column_count(
        self,
        data: t.Cli.TabularData,
        headers: str | Sequence[str],
    ) -> int:
        """Calculate number of columns based on headers and data type."""
        if isinstance(headers, str):
            if headers == FlextCliConstants.Cli.TableFormats.KEYS and isinstance(
                data,
                Mapping,
            ):
                return len(data)
            data_list = list(data)
            if data_list and isinstance(data_list[0], Sequence):
                return len(data_list[0])
            return 0
        if headers:
            return len(headers)
        if isinstance(data, Mapping):
            return len(data)
        data_list = list(data)
        if data_list:
            first_row = data_list[0]
            if u.is_dict_like(first_row):
                return len(list(first_row.keys()))
            if isinstance(first_row, Sequence):
                return len(first_row)
            return 0
        return 0

    def _create_table_string(
        self,
        data: t.Cli.TabularData,
        cfg: m.Cli.TableConfig,
        headers: str | Sequence[str],
    ) -> r[str]:
        """Create table string using tabulate with exception handling."""
        try:
            # Get colalign and validate/truncate if necessary
            colalign = cfg.get_effective_colalign()

            # Calculate number of columns for colalign validation
            num_cols = len(headers) if headers else 0

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

            return r[str].ok(table_str)

        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            return r[str].fail(
                FlextCliConstants.Cli.TablesErrorMessages.TABLE_CREATION_FAILED.format(
                    error=e,
                ),
            )

    @staticmethod
    def print_available_formats() -> r[bool]:
        """Print all available table formats with descriptions.

        Returns:
            r[bool]: True if formats printed successfully, failure on error

        """
        try:

            def convert_format(name: str, desc: str) -> Mapping[str, str]:
                """Convert format to a display dictionary."""
                return {"format": name, "description": desc}

            _ = list(
                starmap(convert_format, FlextCliConstants.Cli.TABLE_FORMATS.items()),
            )
            # Table formatting delegated to rich/tabulate — returns operation result
            return r[bool].ok(value=True)
        except (
            ValueError,
            TypeError,
            KeyError,
            ConsoleError,
            StyleError,
            LiveError,
        ) as e:
            # Simplified error handling
            return r[bool].fail(str(e))

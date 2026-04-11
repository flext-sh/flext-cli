"""FLEXT CLI - Tabulate Integration Layer.

This module provides lightweight ASCII table formatting as an alternative
to Rich tables. Optimized for performance, plain text output, and large datasets.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableSequence, Sequence

from tabulate import tabulate

from flext_cli import FlextCliFormatters, c, m, r, s, t, u


class FlextCliTables(s):
    """Tabulate integration for lightweight ASCII tables."""

    @staticmethod
    def _normalize_table_format(table_format: str) -> str:
        """Map public table aliases to concrete tabulate backends."""
        if table_format == c.Cli.OUTPUT_FORMAT_TABLE.value:
            return "simple"
        return table_format

    @staticmethod
    def _build_config(
        config: m.Cli.TableConfig | None = None,
        **config_kwargs: t.Cli.TableConfigValue,
    ) -> r[m.Cli.TableConfig]:
        """Build a concrete table config from an explicit model plus kwargs."""
        base_config = config or m.Cli.TableConfig()
        if not config_kwargs:
            if base_config.table_format == c.Cli.OUTPUT_FORMAT_TABLE.value:
                normalized_config: m.Cli.TableConfig = base_config.model_copy(
                    update={"table_format": "simple"},
                )
                return r[m.Cli.TableConfig].ok(normalized_config)
            return r[m.Cli.TableConfig].ok(base_config)
        valid_fields = set(m.Cli.TableConfig.model_fields)
        config_data = base_config.model_dump()
        for key, value in config_kwargs.items():
            if key in valid_fields:
                config_data[key] = value
        config_data["table_format"] = FlextCliTables._normalize_table_format(
            str(config_data["table_format"]),
        )
        try:
            resolved_config = m.Cli.TableConfig(**config_data)
            return r[m.Cli.TableConfig].ok(resolved_config)
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            return r[m.Cli.TableConfig].fail(f"Invalid table configuration: {exc}")

    @staticmethod
    def _validate_table_data(data: t.Cli.TabularData, table_format: str) -> r[bool]:
        """Validate table data and format.

        Returns:
            r[bool]: True if validation passed, failure on error

        """
        return FlextCliTables._validate_table_data_wide(data, table_format)

    @staticmethod
    def _validate_table_data_wide(
        data: t.Cli.TableDataSource,
        table_format: str,
    ) -> r[bool]:
        """Validate table data and format.

        Returns:
            r[bool]: True if validation passed, failure on error

        """
        if not data:
            return r[bool].fail(
                c.Cli.ERR_TABLE_DATA_EMPTY,
            )
        if table_format not in c.Cli.TABLE_FORMATS:
            available_formats_list = list(c.Cli.TABLE_FORMATS.keys())
            return r[bool].fail(
                c.Cli.ERR_INVALID_TABLE_FORMAT.format(
                    table_format=table_format,
                    available_formats=", ".join(available_formats_list),
                ),
            )
        return r[bool].ok(True)

    @staticmethod
    def _normalize_mapping_row(
        row: Mapping[str, t.RecursiveContainer],
    ) -> t.Cli.TableMappingRow:
        """Normalize a mapping row to a string-key JSON-compatible mapping."""
        return {
            str(key): u.Cli.normalize_json_value(value) for key, value in row.items()
        }

    @staticmethod
    def _normalize_data(
        data: t.Cli.TableDataSource,
    ) -> r[Sequence[t.Cli.TableRow]]:
        """Normalize mapping and sequence inputs to tabulate-compatible rows."""
        if isinstance(data, Mapping):
            mapping_rows: Sequence[t.Cli.TableRow] = [
                {
                    "Key": str(key),
                    "Value": u.Cli.normalize_json_value(value),
                }
                for key, value in data.items()
            ]
            return r[Sequence[t.Cli.TableRow]].ok(mapping_rows)
        normalized_rows: MutableSequence[t.Cli.TableRow] = []
        for row in data:
            if isinstance(row, Mapping):
                normalized_rows.append(FlextCliTables._normalize_mapping_row(row))
                continue
            if isinstance(row, str):
                return r[Sequence[t.Cli.TableRow]].fail(
                    "Table data must be a mapping or a sequence of mappings/sequences",
                )
            normalized_rows.append([u.Cli.normalize_json_value(value) for value in row])
        rows: Sequence[t.Cli.TableRow] = normalized_rows
        return r[Sequence[t.Cli.TableRow]].ok(rows)

    @staticmethod
    def _prepare_headers(
        headers: t.Cli.TableHeaders,
        *,
        show_header: bool,
    ) -> str | t.StrSequence:
        """Resolve headers for tabulate."""
        if not show_header or headers is None:
            return []
        if isinstance(headers, str):
            return headers
        return list(headers)

    @staticmethod
    def _column_count(
        rows: Sequence[t.Cli.TableRow],
        headers: str | t.StrSequence,
    ) -> int:
        """Compute effective column count for alignment settings."""
        if not isinstance(headers, str):
            return len(headers)
        if not rows:
            return 0
        first_row = rows[0]
        if isinstance(first_row, Mapping):
            return len(first_row)
        return len(first_row)

    @staticmethod
    def _render_table(
        rows: Sequence[t.Cli.TableRow],
        config: m.Cli.TableConfig,
    ) -> r[str]:
        """Render normalized rows to a tabulated string."""
        headers = FlextCliTables._prepare_headers(
            config.headers,
            show_header=config.show_header,
        )
        colalign = config.colalign
        column_count = FlextCliTables._column_count(rows, headers)
        if colalign is not None and column_count > 0 and len(colalign) > column_count:
            colalign = colalign[:column_count]
        try:
            if rows and isinstance(rows[0], Mapping) and not isinstance(headers, str):
                row_values = [
                    list(row.values()) for row in rows if isinstance(row, Mapping)
                ]
                rendered_table = tabulate(
                    row_values,
                    headers=list(headers),
                    tablefmt=config.table_format,
                    floatfmt=config.floatfmt,
                    numalign=config.numalign,
                    stralign=config.stralign,
                    missingval=config.missingval,
                    showindex=config.showindex,
                    disable_numparse=config.disable_numparse,
                    colalign=colalign,
                )
                return r[str].ok(rendered_table)
            rendered_table = tabulate(
                rows,
                headers=headers,
                tablefmt=config.table_format,
                floatfmt=config.floatfmt,
                numalign=config.numalign,
                stralign=config.stralign,
                missingval=config.missingval,
                showindex=config.showindex,
                disable_numparse=config.disable_numparse,
                colalign=colalign,
            )
            return r[str].ok(rendered_table)
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            return r[str].fail(f"Table formatting failed: {exc}")

    @staticmethod
    def format_table(
        data: t.Cli.TableDataSource,
        config: m.Cli.TableConfig | None = None,
        **config_kwargs: t.Cli.TableConfigValue,
    ) -> r[str]:
        """Format table data to a string using the public CLI API."""
        config_result = FlextCliTables._build_config(config, **config_kwargs)
        if config_result.failure:
            return r[str].fail(config_result.error or "Invalid table configuration")
        config_final: m.Cli.TableConfig = config_result.value
        validation_result = FlextCliTables._validate_table_data_wide(
            data, config_final.table_format
        )
        if validation_result.failure:
            return r[str].fail(validation_result.error or "Table validation failed")
        normalized_result = FlextCliTables._normalize_data(data)
        if normalized_result.failure:
            return r[str].fail(normalized_result.error or "Table normalization failed")
        normalized_rows: Sequence[t.Cli.TableRow] = normalized_result.value
        return FlextCliTables._render_table(normalized_rows, config_final)

    @staticmethod
    def _create_table(
        data: t.Cli.TableDataSource,
        config: m.Cli.TableConfig | None = None,
        **config_kwargs: t.Cli.TableConfigValue,
    ) -> r[str]:
        """Private string renderer used by show_table and other internal callers."""
        return FlextCliTables.format_table(data, config, **config_kwargs)

    @staticmethod
    def show_table(
        data: t.Cli.TableDataSource,
        config: m.Cli.TableConfig | None = None,
        **config_kwargs: t.Cli.TableConfigValue,
    ) -> None:
        """Gera e exibe tabela formatada no console. Não retorna string, apenas exibe."""
        config_result = FlextCliTables._build_config(config, **config_kwargs)
        if config_result.failure:
            FlextCliFormatters.print(
                f"[table error] {config_result.error}",
                style=c.Cli.MessageStyles.BOLD_RED,
            )
            return
        config_final: m.Cli.TableConfig = config_result.value
        result = FlextCliTables._create_table(data, config_final)
        if result.success:
            if config_final.title:
                FlextCliFormatters.print(
                    config_final.title, style=c.Cli.MessageStyles.BOLD
                )
            table_output: str = result.value
            FlextCliFormatters.print(table_output)
        else:
            FlextCliFormatters.print(
                f"[table error] {result.error}", style=c.Cli.MessageStyles.BOLD_RED
            )

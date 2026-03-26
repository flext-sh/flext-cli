"""FLEXT CLI - Tabulate Integration Layer.

This module provides lightweight ASCII table formatting as an alternative
to Rich tables. Optimized for performance, plain text output, and large datasets.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import TypeIs

from flext_core import r
from tabulate import tabulate

from flext_cli import FlextCliFormatters, FlextCliServiceBase, c, m, t, u


class FlextCliTables(FlextCliServiceBase):
    """Tabulate integration for lightweight ASCII tables."""

    @staticmethod
    def _prepare_headers(
        data: t.Cli.TabularData,
        headers: str | t.StrSequence,
    ) -> r[str | t.StrSequence]:
        """Prepare headers based on data type."""
        data_list = list(data)
        if not data_list:
            return r[str | t.StrSequence].ok(headers)
        if isinstance(headers, str):
            return r[str | t.StrSequence].ok(headers)
        first_row = data_list[0]
        if u.is_dict_like(first_row):
            return r[str | t.StrSequence].ok(list(headers))
        return r[str | t.StrSequence].ok(headers)

    @staticmethod
    def _validate_table_data(data: t.Cli.TabularData, table_format: str) -> r[bool]:
        """Validate table data and format.

        Returns:
            r[bool]: True if validation passed, failure on error

        """
        if not data:
            return r[bool].fail(
                c.Cli.TablesErrorMessages.TABLE_DATA_EMPTY,
            )
        if table_format not in c.Cli.TABLE_FORMATS:
            available_formats_list = list(c.Cli.TABLE_FORMATS.keys())
            return r[bool].fail(
                c.Cli.TablesErrorMessages.INVALID_TABLE_FORMAT.format(
                    table_format=table_format,
                    available_formats=", ".join(available_formats_list),
                ),
            )
        return r[bool].ok(value=True)

    @staticmethod
    def _create_table(
        data: t.Cli.TabularData,
        config: m.Cli.TableConfig | None = None,
        **config_kwargs: t.Scalar,
    ) -> r[str]:
        """Create formatted ASCII table using tabulate with Pydantic config.

        Uses build_options_from_kwargs pattern for automatic kwargs to Model conversion.

        Args:
            data: Table data (list of dicts, list of lists, etFlextCliConstants.Cli.)
            config: Table configuration (TableConfig model with all settings)
                   If None, uses default configuration
            **config_kwargs: Individual config option overrides (snake_case field names)

        Returns:
            r containing formatted table string

        Example:
            >>> tables = FlextCliTables()
            >>> data = [{"name": "Alice", "age": 30}]
            >>> # With config t.NormalizedValue
            >>> config = m.Cli.Value.TableConfig(table_format="grid")
            >>> result = tables._create_table(data, config)
            >>> # With kwargs (automatic conversion)
            >>> result = tables._create_table(
            ...     data, table_format="grid", headers=["Name", "Age"]
            ... )
            >>> # Without config (uses defaults)
            >>> result = tables._create_table(data)

        """
        config_result = u.build_options_from_kwargs(
            model_class=m.Cli.TableConfig,
            explicit_options=config,
            default_factory=lambda: m.Cli.TableConfig(),
            **{k: v for k, v in config_kwargs.items() if u.is_primitive(v)},
        )
        if config_result.is_failure:
            return r[str].fail(config_result.error or "Invalid table configuration")
        config_final = config_result.value
        validation_result = FlextCliTables._validate_table_data(
            data,
            config_final.table_format,
        )
        if validation_result.is_failure:
            return r[str].fail(validation_result.error or "Table validation failed")
        headers_result = FlextCliTables._prepare_headers(data, config_final.headers)
        if headers_result.is_failure:
            return r[str].fail(headers_result.error or "Header preparation failed")
        try:
            if u.is_dict_like(data):
                normalized_data: Sequence[Mapping[str, t.Cli.JsonValue]] = (
                    [
                        {
                            str(key): u.Cli.normalize_json_value(value)
                            for key, value in data.items()
                        },
                    ]
                    if isinstance(data, Mapping)
                    else []
                )
            else:
                normalized_data = data
            headers_value = headers_result.value
            if normalized_data and (not isinstance(headers_value, str)):
                normalized_mapping_rows: Sequence[Mapping[str, t.Cli.JsonValue]] = [
                    dict(row) for row in normalized_data
                ]
                table_rows = [list(row.values()) for row in normalized_mapping_rows]
                formatted_table = tabulate(
                    table_rows,
                    headers=list(headers_value),
                    tablefmt=config_final.table_format,
                    numalign=config_final.numalign,
                    stralign=config_final.stralign,
                )
                return r[str].ok(formatted_table)

            def _is_tabulate_data(
                val: Sequence[Mapping[str, t.Cli.JsonValue]]
                | Sequence[t.ContainerValue],
            ) -> TypeIs[
                Sequence[Mapping[str, t.ContainerValue]]
                | Sequence[Sequence[t.ContainerValue]]
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
                        isinstance(row, Sequence) and (not isinstance(row, str))
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
        except c.Cli.CLI_SAFE_EXCEPTIONS as e:
            return r[str].fail(f"Table formatting failed: {e}")

    @staticmethod
    def show_table(
        data: t.Cli.TabularData,
        config: m.Cli.TableConfig | None = None,
        **config_kwargs: t.Scalar,
    ) -> None:
        """Gera e exibe tabela formatada no console. Não retorna string, apenas exibe."""
        result = FlextCliTables._create_table(data, config, **config_kwargs)
        if result.is_success:
            FlextCliFormatters.print(result.value)
        else:
            FlextCliFormatters.print(f"[table error] {result.error}", style="bold red")

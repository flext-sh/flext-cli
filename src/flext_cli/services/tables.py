"""FLEXT CLI - Tabulate Integration Layer.

This module provides lightweight ASCII table formatting as an alternative
to Rich tables. Optimized for performance, plain text output, and large datasets.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Sequence

from flext_cli import FlextCliFormatters, c, m, p, r, s, t, u


class FlextCliTables(s):
    """Tabulate integration for lightweight ASCII tables."""

    @staticmethod
    def format_table(
        data: t.Cli.TableDataSource,
        settings: m.Cli.TableConfig | None = None,
        **config_kwargs: t.Cli.TableConfigValue,
    ) -> p.Result[str]:
        """Format table data to a string using the public CLI API."""
        config_result = u.Cli.tables_resolve_config(settings, **config_kwargs)
        if config_result.failure:
            return r[str].fail(config_result.error or "Invalid table configuration")
        config_final = config_result.value

        normalized_result = u.Cli.tables_normalize_data(data)
        if normalized_result.failure:
            return r[str].fail(normalized_result.error or "Table normalization failed")
        normalized_rows: Sequence[t.Cli.TableRow] = normalized_result.value
        return u.Cli.tables_render(normalized_rows, config_final)

    @staticmethod
    def show_table(
        data: t.Cli.TableDataSource,
        settings: m.Cli.TableConfig | None = None,
        **config_kwargs: t.Cli.TableConfigValue,
    ) -> None:
        """Gera e exibe tabela formatada no console. Não retorna string, apenas exibe."""
        config_result: p.Result[m.Cli.TableConfig] = u.Cli.tables_resolve_config(
            settings, **config_kwargs
        )
        if config_result.failure:
            error_line, error_style = u.Cli.output_table_error(config_result.error)
            FlextCliFormatters.print(error_line, style=error_style)
            return
        config_final = config_result.value
        normalized_result: p.Result[Sequence[t.Cli.TableRow]] = (
            u.Cli.tables_normalize_data(data)
        )
        if normalized_result.failure:
            error_line, error_style = u.Cli.output_table_error(normalized_result.error)
            FlextCliFormatters.print(error_line, style=error_style)
            return

        result: p.Result[str] = u.Cli.tables_render(
            normalized_result.value,
            config_final,
        )
        if result.success:
            if config_final.title:
                FlextCliFormatters.print(
                    config_final.title, style=c.Cli.MessageStyles.BOLD
                )
            table_output: str = result.value
            FlextCliFormatters.print(table_output)
        else:
            error_line, error_style = u.Cli.output_table_error(result.error)
            FlextCliFormatters.print(error_line, style=error_style)

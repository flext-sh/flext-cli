"""CLI table data helpers shared through ``u.Cli``."""

from __future__ import annotations

from collections.abc import MutableSequence, Sequence
from typing import ClassVar

from pydantic import TypeAdapter, ValidationError
from tabulate import tabulate

from flext_cli import c, m, r, t
from flext_cli._utilities.json import FlextCliUtilitiesJson
from flext_core import FlextUtilities


class FlextCliUtilitiesTables:
    """Table helpers exposed through ``u.Cli.tables_*``."""

    TABLE_DATA_ADAPTER: ClassVar[TypeAdapter[t.Cli.TableDataSource]] = TypeAdapter(
        t.Cli.TableDataSource,
    )

    @staticmethod
    def tables_normalize_mapping_row(
        row: t.ContainerMapping,
    ) -> t.Cli.TableMappingRow:
        """Normalize one mapping row to JSON-compatible values."""
        return {
            str(key): FlextCliUtilitiesJson.normalize_json_value(value)
            for key, value in row.items()
        }

    @staticmethod
    def tables_normalize_sequence_row(
        row: t.ContainerList,
    ) -> t.Cli.TableSequenceRow:
        """Normalize one sequence row to JSON-compatible values."""
        return [FlextCliUtilitiesJson.normalize_json_value(value) for value in row]

    @staticmethod
    def tables_resolve_config(
        config: m.Cli.TableConfig | None = None,
        **config_kwargs: t.Cli.TableConfigValue,
    ) -> r[m.Cli.TableConfig]:
        """Resolve table config via canonical Pydantic model contract."""
        try:
            if config is not None and not config_kwargs:
                return r[m.Cli.TableConfig].ok(config)
            base_data = (
                config.model_dump(exclude_computed_fields=True)
                if config is not None
                else {}
            )
            config_data = {**base_data, **config_kwargs}
            resolved = m.Cli.TableConfig.model_validate(config_data)
            return r[m.Cli.TableConfig].ok(resolved)
        except c.Cli.CLI_SAFE_EXCEPTIONS as exc:
            return r[m.Cli.TableConfig].fail(f"Invalid table configuration: {exc}")

    @staticmethod
    def tables_normalize_data(
        data: t.Cli.TableDataSource,
    ) -> r[Sequence[t.Cli.TableRow]]:
        """Validate and normalize mapping/sequence inputs to tabulate rows."""
        try:
            validated_data = FlextCliUtilitiesTables.TABLE_DATA_ADAPTER.validate_python(
                data,
            )
        except ValidationError as exc:
            return r[Sequence[t.Cli.TableRow]].fail(f"Table data invalid: {exc}")

        if FlextUtilities.mapping(validated_data):
            validated_mapping = validated_data
            return r[Sequence[t.Cli.TableRow]].ok([
                {
                    "Key": str(key),
                    "Value": FlextCliUtilitiesJson.normalize_json_value(value),
                }
                for key, value in validated_mapping.items()
            ])

        normalized_rows: MutableSequence[t.Cli.TableRow] = []
        for row in validated_data:
            if FlextUtilities.mapping(row):
                normalized_rows.append(
                    FlextCliUtilitiesTables.tables_normalize_mapping_row(row),
                )
                continue
            if FlextUtilities.list_like(row):
                normalized_rows.append(
                    FlextCliUtilitiesTables.tables_normalize_sequence_row(row),
                )
                continue
            return r[Sequence[t.Cli.TableRow]].fail(
                "Table row invalid after validation",
            )

        return r[Sequence[t.Cli.TableRow]].ok(normalized_rows)

    @staticmethod
    def tables_render(
        rows: Sequence[t.Cli.TableRow],
        config: m.Cli.TableConfig,
    ) -> r[str]:
        """Render normalized rows to a tabulated string."""
        headers: str | t.StrSequence
        if not config.show_header or config.headers is None:
            headers = []
        elif isinstance(config.headers, str):
            headers = config.headers
        else:
            headers = list(config.headers)

        colalign = config.colalign
        if isinstance(headers, str):
            if not rows:
                column_count = 0
            elif FlextUtilities.mapping(rows[0]):
                column_count = len(rows[0])
            else:
                column_count = len(rows[0])
        else:
            column_count = len(headers)

        if colalign is not None and column_count > 0 and len(colalign) > column_count:
            colalign = colalign[:column_count]

        try:
            table_data: Sequence[t.Cli.TableRow] | Sequence[t.Cli.TableSequenceRow] = (
                rows
            )
            table_headers: str | t.StrSequence = headers
            if (
                rows
                and FlextUtilities.mapping(rows[0])
                and not isinstance(
                    headers,
                    str,
                )
            ):
                table_data = [
                    list(row.values()) for row in rows if FlextUtilities.mapping(row)
                ]
                table_headers = list(headers)

            rendered_table = tabulate(
                table_data,
                headers=table_headers,
                tablefmt=config.table_backend_format,
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


__all__ = ["FlextCliUtilitiesTables"]

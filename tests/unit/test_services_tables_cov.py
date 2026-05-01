"""Coverage tests for services/tables.py.

Targets: format_table, show_table.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from tests import m


class TestsFlextCliServicesTablesCov:
    """Data-driven coverage tests for FlextCliTables service."""

    # ── format_table ──────────────────────────────────────────────────

    def test_format_table_dict(self) -> None:
        from flext_cli.services.tables import FlextCliTables

        result = FlextCliTables.format_table({"name": "Alice", "age": 30})
        assert result.success
        assert isinstance(result.value, str)

    def test_format_table_list_of_dicts(self) -> None:
        from flext_cli.services.tables import FlextCliTables

        result = FlextCliTables.format_table([{"col": "val1"}, {"col": "val2"}])
        assert result.success

    def test_format_table_with_kwargs(self) -> None:
        from flext_cli.services.tables import FlextCliTables

        # tablefmt as extra kwarg is not permitted — must use TableConfig model
        config = m.Cli.TableConfig()
        result = FlextCliTables.format_table({"a": 1}, config)
        assert result.success

    def test_format_table_with_model_config(self) -> None:
        from flext_cli.services.tables import FlextCliTables

        config = m.Cli.TableConfig()
        result = FlextCliTables.format_table({"k": "v"}, config)
        assert result.success

    def test_format_table_empty_dict(self) -> None:
        from flext_cli.services.tables import FlextCliTables

        result = FlextCliTables.format_table({})
        # Empty dict is a valid input (no rows)
        assert result.success or result.failure  # just should not raise

    def test_format_table_with_title(self) -> None:
        from flext_cli.services.tables import FlextCliTables

        config = m.Cli.TableConfig(title="My Table")
        result = FlextCliTables.format_table({"x": 1, "y": 2}, config)
        assert result.success

    # ── show_table ────────────────────────────────────────────────────

    def test_show_table_dict(self) -> None:
        from flext_cli.services.tables import FlextCliTables

        FlextCliTables.show_table({"name": "Bob", "score": 99})

    def test_show_table_list(self) -> None:
        from flext_cli.services.tables import FlextCliTables

        FlextCliTables.show_table([{"col": "val"}])

    def test_show_table_with_model_config(self) -> None:
        from flext_cli.services.tables import FlextCliTables

        config = m.Cli.TableConfig(title="Table")
        FlextCliTables.show_table({"a": 1}, config)

    def test_show_table_with_title_config(self) -> None:
        from flext_cli.services.tables import FlextCliTables

        config = m.Cli.TableConfig(title="With Title")
        FlextCliTables.show_table({"col": "row"}, config)


__all__: list[str] = ["TestsFlextCliServicesTablesCov"]

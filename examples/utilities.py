"""Common utilities for FLEXT CLI examples.

Eliminates code duplication across example files by providing shared patterns
and common functionality using ONLY cli wrappers - NO direct Rich imports!
All data transport uses Pydantic v2 models from flext_cli (m.Cli).

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from typing import TYPE_CHECKING

from examples import c, m, t
from flext_cli import cli, u

from collections.abc import (
    MutableSequence,
)



class ExamplesFlextCliUtilities(u):
    """Public examples utility facade extending flext-cli utilities."""

    @classmethod
    def to_json_dict(
        cls,
        data: t.JsonMapping,
    ) -> p.Cli.DisplayData:
        """Normalize settings/mapping to DisplayData for create_table/display_config_table."""
        json_value: t.JsonValue = t.Cli.JSON_VALUE_ADAPTER.validate_python(
            cls.normalize_to_json_value(data),
        )
        normalized = m.Cli.CliNormalizedJson(json_value).root
        resolved = m.Cli.NormalizedJsonList(value=normalized, default={}).resolved
        result_dict = dict(resolved.items())
        return m.Cli.DisplayData(data=result_dict)

    @staticmethod
    def print_demo_completion(
        demo_name: str,
        features: t.StrSequence,
        *,
        style: c.Cli.MessageStyles = c.Cli.MessageStyles.GREEN,
        bold_style: c.Cli.MessageStyles = c.Cli.MessageStyles.BOLD_GREEN,
    ) -> None:
        """Print standardized demo completion message using cli."""
        cli.print(f"\n🎉 {demo_name} Complete", style=bold_style)
        cli.print(f"✅ {demo_name} Completed!", style=style)
        cli.print("\nKey Features Demonstrated:", style=c.Cli.MessageStyles.CYAN)
        for feature in features:
            cli.print(f"  • {feature}", style=c.Cli.MessageStyles.WHITE)
        cli.print(
            "\nAll operations used r pattern for error handling!",
            style=c.Cli.MessageStyles.YELLOW,
        )

    @staticmethod
    def display_config_table(
        config_data: m.Cli.DisplayData | m.Value,
        headers: t.StrSequence | None = None,
    ) -> None:
        """Display configuration as a table using canonical example models."""
        if headers is None:
            headers = ["Setting", "Value"]
        rows: MutableSequence[t.StrMapping] = []
        if isinstance(config_data, m.Cli.DisplayData):
            for key, value in config_data.data.items():
                rows.append({"Setting": key, "Value": str(value)})
        else:
            dumped = config_data.model_dump(mode="json")
            for key, value in dumped.items():
                rows.append({"Setting": key, "Value": str(value)})
        cli.show_table(rows, headers=headers)

    @staticmethod
    def display_success_summary(
        operation: str,
        details: m.Cli.SuccessSummaryDetails | None = None,
    ) -> None:
        """Display a standardized success summary using cli."""
        cli.print(
            f"✅ {operation} completed successfully!",
            style=c.Cli.MessageStyles.BOLD_GREEN,
        )
        if details is not None:
            for key, value in details.root.items():
                cli.print(f"   {key}: {value}", style=c.Cli.MessageStyles.CYAN)


u = ExamplesFlextCliUtilities

__all__: t.MutableSequenceOf[str] = [
    "ExamplesFlextCliUtilities",
    "u",
]

"""File Operations - Using flext-cli for File I/O in YOUR Code.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING

from flext_cli import c, cli, m, p, r, t, u

if TYPE_CHECKING:
    from pathlib import Path

_EXAMPLE_REQUIRED_DATA_FIELDS: t.VariadicTuple[str] = ("id", "name", "value")

# ============================================================================
# PATTERN 1: JSON settings files in YOUR application
# ============================================================================


def save_user_preferences(
    preferences: t.MappingKV[str, t.JsonPayloadCollectionValue], config_dir: Path
) -> bool:
    """Save user preferences to JSON in YOUR app."""
    config_file = config_dir / "preferences.json"

    write_result = cli.write_json_file(
        config_file, u.normalize_to_json_value(preferences)
    )

    if write_result.failure:
        cli.print(
            f"❌ Failed to save: {write_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return False

    cli.print(
        f"✅ Saved preferences to {config_file.name}", style=c.Cli.MessageStyles.GREEN
    )
    return True


def load_user_preferences(config_dir: Path) -> p.Result[m.Cli.LoadedConfig]:
    """Load user preferences from JSON in YOUR app. Returns r[LoadedConfig]; no None."""
    config_file = config_dir / "preferences.json"

    read_result = cli.read_json_file(config_file)

    if read_result.failure:
        cli.print(
            f"⚠️  Could not load: {read_result.error}", style=c.Cli.MessageStyles.YELLOW
        )
        return r[m.Cli.LoadedConfig].fail(
            read_result.error or "Could not load preferences"
        )
    if not isinstance(read_result.value, Mapping):
        return r[m.Cli.LoadedConfig].fail("Preferences content must be a mapping")

    cli.print(
        f"✅ Loaded preferences from {config_file.name}",
        style=c.Cli.MessageStyles.GREEN,
    )
    return r[m.Cli.LoadedConfig].ok(m.Cli.LoadedConfig(content=dict(read_result.value)))


# ============================================================================
# PATTERN 2: YAML configuration in YOUR deployment tool
# ============================================================================


def save_deployment_config(
    settings: t.MappingKV[str, t.JsonPayloadCollectionValue], config_file: Path
) -> bool:
    """Save deployment settings to YAML in YOUR tool."""
    # Normalize the mapping into the CLI JSON contract before writing YAML.
    write_result = cli.write_yaml_file(config_file, u.normalize_to_json_value(settings))

    if write_result.failure:
        cli.print(
            f"❌ Config save failed: {write_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return False

    cli.print("✅ Saved deployment settings", style=c.Cli.MessageStyles.GREEN)
    return True


def load_deployment_config(config_file: Path) -> p.Result[m.Cli.LoadedConfig]:
    """Load deployment settings from YAML in YOUR tool. Returns r[LoadedConfig]; no None."""
    load_result = cli.load_file_auto_dict(config_file)

    if load_result.failure:
        cli.print(
            f"❌ Config load failed: {load_result.error}",
            style=c.Cli.MessageStyles.BOLD_RED,
        )
        return r[m.Cli.LoadedConfig].fail(load_result.error or "Config load failed")

    cli.print("✅ Loaded deployment settings", style=c.Cli.MessageStyles.GREEN)
    return r[m.Cli.LoadedConfig].ok(m.Cli.LoadedConfig(content=load_result.value))


def validate_and_import_data(input_file: Path) -> p.Result[m.Cli.LoadedConfig]:
    """Validate and import data in YOUR ETL pipeline. Returns r[LoadedConfig]; no None."""
    read_result = cli.read_json_file(input_file)

    if read_result.failure:
        cli.print(
            f"❌ Read failed: {read_result.error}", style=c.Cli.MessageStyles.BOLD_RED
        )
        return r[m.Cli.LoadedConfig].fail(read_result.error or "Read failed")

    data = read_result.value
    if not isinstance(data, Mapping):
        return r[m.Cli.LoadedConfig].fail("Input data must be a mapping")

    for field in _EXAMPLE_REQUIRED_DATA_FIELDS:
        if field not in data:
            return r[m.Cli.LoadedConfig].fail(f"Missing required field: {field}")

    cli.print("✅ Data validated successfully", style=c.Cli.MessageStyles.GREEN)
    return r[m.Cli.LoadedConfig].ok(m.Cli.LoadedConfig(content=data))

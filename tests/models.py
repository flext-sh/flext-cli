"""Pydantic models for flext-cli tests only.

All test-domain models live here; tests MUST NOT use dict/Any/object as data contracts.
Reuse m.Cli types where possible; add test-specific input models only when needed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, RootModel

from flext_cli import t


class CliCommandInput(BaseModel):
    """Test input for building CliCommand via model_construct. All optional with defaults."""

    model_config = ConfigDict(extra="forbid")
    unique_id: str = Field(default="test-cmd-0")
    name: str = Field(default="test_command")
    description: str = Field(default="Test command description")
    status: str = Field(default="pending")
    created_at: datetime | None = Field(default=None)
    command_line: str = Field(default="test_command")
    args: Sequence[str] = Field(default_factory=list)
    result: t.JsonValue | None = Field(default=None)
    kwargs: dict[str, t.JsonValue] = Field(default_factory=dict)


class CliSessionInput(BaseModel):
    """Test input for building CliSession via model_construct. All optional with defaults."""

    model_config = ConfigDict(extra="forbid")
    session_id: str = Field(default="test-session-0")
    status: str = Field(default="active")
    created_at: datetime | None = Field(default=None)


_ScalarOnly = str | int | float | bool | None


class ScalarConfigRestore(RootModel[dict[str, _ScalarOnly]]):
    """Holds scalar-only config for container restore in fixtures. Filters nested values out."""

    @classmethod
    def from_config_items(
        cls, items: Mapping[str, t.ContainerValue]
    ) -> ScalarConfigRestore:
        """Build scalar-only dict from config items (drops nested dict/list/model)."""
        out: dict[str, _ScalarOnly] = {k: v for k, v in items.items() if v is None or isinstance(v, (str, int, float, bool))}
        return cls.model_validate(out)


class TestsFlextCliModels:
    """Test namespace facade for flext-cli models. Use tm alias; m is flext_cli.FlextCliModels."""

    CliCommandInput = CliCommandInput
    CliSessionInput = CliSessionInput
    ScalarConfigRestore = ScalarConfigRestore


tm = TestsFlextCliModels

__all__ = [
    "CliCommandInput",
    "CliSessionInput",
    "ScalarConfigRestore",
    "TestsFlextCliModels",
    "tm",
]

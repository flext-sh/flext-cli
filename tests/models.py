"""Pydantic models for flext-cli tests only.

All test-domain models live here; tests MUST NOT use dict/Any/t.NormalizedValue as data contracts.
Reuse FlextTestsModels types where possible; add test-specific input models only when needed.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

from collections.abc import Mapping, MutableMapping
from typing import Annotated, ClassVar

from flext_tests import FlextTestsModels
from pydantic import BaseModel, ConfigDict, Field

from flext_cli import FlextCliModels, FlextCliTypes


class FlextCliTestModels(FlextTestsModels, FlextCliModels):
    """Test namespace facade for flext-cli models. Use m alias; preserves all test model types."""

    class Cli(FlextCliModels.Cli):
        """CLI models with test-specific extensions."""

        class Test:
            """Test-specific model definitions."""

            class PositionalModel(BaseModel):
                """Model accepting positional data for test scenarios."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")

                def __init__(
                    self,
                    data: Mapping[str, FlextCliTypes.ContainerValue] | None = None,
                    /,
                    **kwargs: FlextCliTypes.ContainerValue,
                ) -> None:
                    payload: MutableMapping[str, FlextCliTypes.ContainerValue] = {}
                    if data is not None:
                        payload.update(data)
                    payload.update(kwargs)
                    super().__init__(**payload)

            class UserData(PositionalModel):
                """User data for type scenario tests -- Pydantic v2."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                id: Annotated[int, Field(description="User id")]
                name: Annotated[str, Field(description="User name")]
                email: Annotated[str, Field(description="Email")]
                active: Annotated[bool, Field(description="Active flag")]

            class ApiResponse(PositionalModel):
                """API response for type scenario tests -- Pydantic v2."""

                model_config: ClassVar[ConfigDict] = ConfigDict(extra="forbid")
                status: Annotated[str, Field(description="Status")]
                data: Annotated[
                    FlextCliTypes.NormalizedValue,
                    Field(default=None, description="Payload"),
                ]
                message: Annotated[str, Field(description="Message")]
                error: Annotated[str | None, Field(default=None, description="Error")]


m = FlextCliTestModels

__all__ = [
    "FlextCliTestModels",
    "m",
]

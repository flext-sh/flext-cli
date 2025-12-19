"""Models for flext-cli tests.

Provides TestsCliModels using composition with FlextTestsModels and FlextCliModels.
All generic test models come from flext_tests.

Architecture:
- FlextTestsModels (flext_tests) = Generic models for all FLEXT projects
- FlextCliModels (flext_cli) = CLI-specific models
- TestsCliModels (tests/) = flext-cli-specific models using composition

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import field

from flext_core import FlextModels, FlextProtocols, FlextTypes
from flext_tests.models import FlextTestsModels

from flext_cli.models import FlextCliModels


class TestsCliModels:
    """Models for flext-cli tests - uses composition with FlextTestsModels.

    Architecture: Uses composition (not inheritance) with FlextTestsModels and FlextCliModels
    for flext-cli-specific model definitions.

    Access patterns:
    - TestsCliModels.Tests.* = flext_tests test models (via composition)
    - TestsCliModels.Cli.* = flext-cli-specific test models
    - TestsCliModels.Entity, .Value, etc. = FlextModels domain models (via composition)

    Rules:
    - Use composition, not inheritance (FlextTestsModels deprecates subclassing)
    - flext-cli-specific models go in Cli namespace
    - Generic models accessed via Tests namespace
    """

    # Composition: expose FlextTestsModels namespaces
    Tests = FlextTestsModels.Tests

    # Composition: expose FlextModels domain model classes
    Entity = FlextModels.Entity
    Value = FlextModels.Value
    AggregateRoot = FlextModels.AggregateRoot
    DomainEvent = FlextModels.DomainEvent
    Collections = FlextModels.Collections

    # Composition: expose FlextCliModels CLI-specific classes (direct access)
    Cli = FlextCliModels

    # Type aliases for domain test input
    type DomainInputValue = (
        FlextTypes.GeneralValueType | FlextProtocols.HasModelDump | object
    )
    type DomainInputMapping = Mapping[str, DomainInputValue]
    type DomainExpectedResult = (
        FlextTypes.GeneralValueType | type[FlextTypes.GeneralValueType]
    )

    class Core:
        """flext-cli-specific test models namespace."""

        class CliTestEntity(FlextCliModels.Cli.Entity):
            """Test entity for CLI tests."""

            name: str
            value: int

        class CliTestValue(FlextCliModels.Cli.Value):
            """Test value object for CLI tests."""

            data: str
            count: int

        class CommandTestEntity(FlextCliModels.Cli.CliCommand):
            """Test command for CLI tests."""

            command_name: str = "test-command"
            command_args: list[str] = field(default_factory=list)


# Short alias per FLEXT convention
m = TestsCliModels

__all__ = [
    "TestsCliModels",
    "m",
]

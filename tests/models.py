"""Test model definitions extending src models for centralized test objects.

This module provides test-specific model extensions that inherit from
src/flext_cli/models.py classes. This centralizes test objects without
duplicating parent class functionality.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

import logging
from collections.abc import Mapping
from datetime import datetime

from flext_cli import FlextCliModels
from flext_tests import FlextTestsModels
from pydantic import RootModel, TypeAdapter, ValidationError

# Type for container configure() restore: only scalar values (no isinstance filter).
type ScalarValue = str | int | float | bool | datetime | None

_ScalarValueAdapter: TypeAdapter[ScalarValue] = TypeAdapter(ScalarValue)


class ScalarConfigRestore(RootModel[dict[str, ScalarValue]]):
    """Restore config for FlextContainer.configure(): only scalar entries.

    Built from ConfigMap by validating each value with Pydantic; non-scalar
    entries are skipped (no isinstance). Use from_config_items() to build.
    """

    @classmethod
    def from_config_items(cls, config: Mapping[str, object]) -> ScalarConfigRestore:
        """Build from ConfigMap or any mapping; keep only scalar values (Pydantic-validated)."""
        result: dict[str, ScalarValue] = {}
        for k, v in config.items():
            try:
                result[str(k)] = _ScalarValueAdapter.validate_python(v)
            except ValidationError:
                logging.getLogger(__name__).debug(
                    "skip non-scalar config key %s",
                    k,
                    exc_info=True,
                )
                continue
        return cls(root=result)


class TestsFlextCliModels(FlextTestsModels, FlextCliModels):
    """Test models - composição de FlextTestsModels + FlextCliModels.

    Hierarquia:
    - FlextTestsModels: Utilitários de teste genéricos
    - FlextCliModels: Models de domínio do projeto
    - TestsFlextCliModels: Composição + namespace .Tests

    Access patterns:
    - tm.Tests.* - Test fixtures (Entity, Value, Command, etc.)
    - m.Cli.* - Production domain models
    """

    class Tests(FlextTestsModels.Tests):
        """Test fixture models namespace (extends base Tests with CLI shortcuts).

        Convenience aliases for test-only shortcuts.
        Production code should use m.Cli.* pattern.
        """

        # Command models for testing
        CliCommand = FlextCliModels.Cli.CliCommand
        CliSession = FlextCliModels.Cli.CliSession
        CliSessionData = FlextCliModels.Cli.CliSessionData

        # Config models for testing
        TableConfig = FlextCliModels.Cli.TableConfig
        LoggingConfig = FlextCliModels.Cli.LoggingConfig
        CliConfig = FlextCliModels.Cli.CliConfig
        CliParamsConfig = FlextCliModels.Cli.CliParamsConfig
        OptionConfig = FlextCliModels.Cli.OptionConfig
        ConfirmConfig = FlextCliModels.Cli.ConfirmConfig
        PromptConfig = FlextCliModels.Cli.PromptConfig
        CmdConfig = FlextCliModels.Cli.CmdConfig

        # Output models for testing
        CliOutput = FlextCliModels.Cli.CliOutput

        # Result models for testing
        CommandResult = FlextCliModels.Cli.CommandResult
        ServiceExecutionResult = FlextCliModels.Cli.ServiceExecutionResult
        ContextExecutionResult = FlextCliModels.Cli.ContextExecutionResult
        WorkflowResult = FlextCliModels.Cli.WorkflowResult
        WorkflowStepResult = FlextCliModels.Cli.WorkflowStepResult
        WorkflowProgress = FlextCliModels.Cli.WorkflowProgress
        CommandExecutionContextResult = FlextCliModels.Cli.CommandExecutionContextResult

        # Info models for testing
        PathInfo = FlextCliModels.Cli.PathInfo
        EnvironmentInfo = FlextCliModels.Cli.EnvironmentInfo
        SystemInfo = FlextCliModels.Cli.SystemInfo
        DebugInfo = FlextCliModels.Cli.DebugInfo
        CliDebugData = FlextCliModels.Cli.CliDebugData

        # Statistics models for testing
        SessionStatistics = FlextCliModels.Cli.SessionStatistics
        PromptStatistics = FlextCliModels.Cli.PromptStatistics
        CommandStatistics = FlextCliModels.Cli.CommandStatistics

        # Auth models for testing
        PasswordAuth = FlextCliModels.Cli.PasswordAuth
        TokenData = FlextCliModels.Cli.TokenData

        # Builder classes for testing
        OptionBuilder = FlextCliModels.Cli.OptionBuilder
        ModelCommandBuilder = FlextCliModels.Cli.ModelCommandBuilder
        CliParameterSpec = FlextCliModels.Cli.CliParameterSpec
        CliModelConverter = FlextCliModels.Cli.CliModelConverter
        CliModelDecorators = FlextCliModels.Cli.CliModelDecorators


# Short aliases for tests
tm = TestsFlextCliModels
m = TestsFlextCliModels

__all__ = [
    "ScalarConfigRestore",
    "ScalarValue",
    "TestsFlextCliModels",
    "m",
    "tm",
]

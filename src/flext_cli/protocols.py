"""FlextCli protocol definitions module - Structural typing.

Facade re-exporting from _protocols/ for public API access.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from flext_cli import t
from flext_cli._protocols.base import FlextCliProtocolsBase
from flext_core import FlextProtocols


class FlextCliProtocols(FlextProtocols):
    """CLI protocol definitions extending FlextProtocols."""

    class Cli:
        """CLI protocol namespace for all CLI-specific protocols."""

        @runtime_checkable
        class CliParamsConfig(FlextCliProtocolsBase.CliParamsConfig, Protocol):
            """Protocol for CLI parameters configuration."""

        @runtime_checkable
        class CliCommandWrapper(FlextCliProtocolsBase.CliCommandWrapper, Protocol):
            """Protocol for dynamically-created CLI command wrapper functions."""

        @runtime_checkable
        class ResultCommandHandler[
            TParams: BaseModel,
            TResult: t.Cli.ValueOrModel,
        ](
            FlextCliProtocolsBase.ResultCommandHandler[TParams, TResult],
            Protocol,
        ):
            """Protocol for model-driven CLI handlers returning `r[...]`."""

        @runtime_checkable
        class ErrorMessageProvider(
            FlextCliProtocolsBase.ErrorMessageProvider,
            Protocol,
        ):
            """Protocol for deferred CLI error message resolution."""

        @runtime_checkable
        class FailureMessageRecorder(
            FlextCliProtocolsBase.FailureMessageRecorder,
            Protocol,
        ):
            """Protocol for persisting normalized CLI failure state."""

        @runtime_checkable
        class SuccessMessageFormatter[TResult: t.Cli.ValueOrModel](
            FlextCliProtocolsBase.SuccessMessageFormatter[TResult],
            Protocol,
        ):
            """Protocol for rendering a success result into a CLI message."""

        @runtime_checkable
        class YamlModule(FlextCliProtocolsBase.YamlModule, Protocol):
            """Protocol for YAML serialization module interface."""


p = FlextCliProtocols

__all__ = ["FlextCliProtocols", "p"]

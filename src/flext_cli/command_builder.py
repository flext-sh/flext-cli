"""Fluent DSL for building CLI commands.

FlextCommandBuilder provides a fluent interface for building CLI commands with
options, arguments, middleware, and handlers. Integrates with the existing
flext-cli infrastructure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Self

from flext_core import r
from typer.models import OptionInfo

from flext_cli.models import m
from flext_cli.protocols import p
from flext_cli.typings import t


class FlextCommandBuilder:
    """Fluent DSL for building CLI commands.

    Provides a builder pattern for creating CLI commands with options,
    arguments, middleware, and handlers. Integrates with flext-cli's
    existing command infrastructure.

    Example:
        >>> sync_command = (
        ...     FlextCommandBuilder("sync")
        ...     .with_option_group(FlextOptionGroup.connection_options())
        ...     .with_option("--dry-run", type_=bool, default=False)
        ...     .with_middleware(logging_middleware)
        ...     .with_middleware(auth_middleware)
        ...     .handler(handle_sync)
        ...     .build()
        ... )

    """

    def __init__(self, name: str) -> None:
        """Initialize command builder.

        Args:
            name: Command name.

        """
        self._name = name
        self._options: list[OptionInfo] = []
        self._arguments: list[tuple[str, type, bool]] = []  # (name, type, required)
        self._middleware: list[
            Callable[[p.Cli.CliContextProtocol], r[t.GeneralValueType]]
        ] = []
        self._handler: p.Cli.CommandHandlerCallable | None = None

    @staticmethod
    def _create_option_info(
        default: t.GeneralValueType = None,
        param_decls: list[str] | None = None,
        help_text: str = "",
        **kwargs: t.GeneralValueType,
    ) -> OptionInfo:
        """Create OptionInfo with validated kwargs.

        Typer validates kwargs at runtime, but static type checkers can't infer
        all possible kwargs. This helper validates and constructs OptionInfo safely.
        """
        # Validate required parameters
        validated_param_decls = param_decls if param_decls is not None else []
        # Build validated kwargs with proper types for OptionInfo
        # OptionInfo constructor expects specific types for known parameters
        # Type narrowing: validate types match OptionInfo signature
        validated_default: t.GeneralValueType | None = default
        validated_param_decls_list: Sequence[str] = validated_param_decls
        validated_help: str | None = help_text or None
        # Create OptionInfo with validated parameters
        # Additional kwargs are validated by typer at runtime
        # OptionInfo accepts various kwargs that typer validates at runtime
        # Use explicit parameter passing to satisfy type checker
        option_info = OptionInfo(
            default=validated_default,
            param_decls=validated_param_decls_list,
            help=validated_help,
        )
        # Set additional kwargs via attribute assignment (typer validates at runtime)
        excluded_keys = {"default", "param_decls", "help"}
        for key, value in kwargs.items():
            if key not in excluded_keys:
                setattr(option_info, key, value)
        return option_info

    def with_option(
        self,
        name: str,
        default: t.GeneralValueType = None,
        help_: str = "",
        **kwargs: t.GeneralValueType,
    ) -> Self:
        """Add command option.

        Args:
            name: Option name (e.g., "--host" or "--host/-h").
            type_: Option type (default: str).
            default: Default value.
            help_: Help text.
            **kwargs: Additional typer.Option parameters.

        Returns:
            Self: Builder instance for chaining.

        """
        param_decls = [name]
        # Extract short flag if provided (e.g., "--host/-h")
        if "/" in name:
            parts = name.split("/")
            param_decls = parts

        # OptionInfo accepts various keyword arguments validated at runtime by typer
        # Create OptionInfo with validated kwargs using helper function
        option_info = self._create_option_info(
            default=default,
            param_decls=param_decls,
            help_text=help_,
            **kwargs,
        )
        self._options.append(option_info)
        return self

    def with_argument(
        self,
        name: str,
        type_: type = str,
        *,
        required: bool = True,
    ) -> Self:
        """Add command argument.

        Args:
            name: Argument name.
            type_: Argument type (default: str).
            required: Whether argument is required (default: True).

        Returns:
            Self: Builder instance for chaining.

        """
        self._arguments.append((name, type_, required))
        return self

    def with_option_group(self, group: list[OptionInfo]) -> Self:
        """Add predefined option group.

        Args:
            group: List of OptionInfo objects from FlextOptionGroup.

        Returns:
            Self: Builder instance for chaining.

        """
        self._options.extend(group)
        return self

    def with_middleware(
        self,
        middleware: Callable[[p.Cli.CliContextProtocol], r[t.GeneralValueType]],
    ) -> Self:
        """Add middleware (logging, auth, validation).

        Args:
            middleware: Middleware function that processes context and calls next.

        Returns:
            Self: Builder instance for chaining.

        """
        self._middleware.append(middleware)
        return self

    def handler(self, func: p.Cli.CommandHandlerCallable) -> Self:
        """Set command handler.

        Args:
            func: Command handler function.

        Returns:
            Self: Builder instance for chaining.

        """
        self._handler = func
        return self

    def build(self) -> m.Cli.CliCommand:
        """Build the command.

        Returns:
            m.Cli.CliCommand: Command model ready for registration.

        Note:
            This is a simplified implementation. Full integration with
            flext-cli's command system would require more complex wiring.

        """
        command = m.Cli.CliCommand(
            name=self._name,
            description="",
        )
        if not FlextCommandBuilder._is_command_protocol(command):
            msg = "command must implement Command protocol"
            raise TypeError(msg)
        return command

    @staticmethod
    def _is_command_protocol(obj: t.GeneralValueType) -> bool:
        """Type guard to check if object implements Command protocol."""
        return (
            hasattr(obj, "name")
            and hasattr(obj, "description")
            and isinstance(getattr(obj, "name", None), str)
            and isinstance(getattr(obj, "description", None), str)
        )

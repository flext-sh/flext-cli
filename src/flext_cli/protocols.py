"""FlextCli protocol definitions module - Structural typing."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult


class FlextCliProtocols(FlextProtocols):
    """FlextCli protocol definitions composing with FlextProtocols.

    REGRAS:
    ───────
    1. NUNCA importar Models, Config, ou classes concretas
    2. Apenas importar outros Protocols
    3. @runtime_checkable para isinstance() checks
    4. Self para métodos que retornam a própria instância
    5. Composição com FlextProtocols
    """

    # ═══════════════════════════════════════════════════════════════════
    # LAYER 0: Domain Protocols (sem dependências internas)
    # ═══════════════════════════════════════════════════════════════════

    class Cli:
        """CLI-specific protocols."""

        @runtime_checkable
        class CliCommandProtocol(Protocol):
            """Protocol for CLI commands."""

            @property
            def name(self) -> str:
                """Command name."""
                ...

            @property
            def description(self) -> str:
                """Command description."""
                ...

            def execute(self, args: Sequence[str]) -> FlextResult[object]:
                """Execute command with arguments."""
                ...

        CliCommandFunction = CliCommandProtocol

        @runtime_checkable
        class ModelCommandHandler(Protocol):
            """Protocol for model command handlers."""

            def handle(self, model: object, **kwargs: object) -> FlextResult[object]:
                """Handle model command."""
                ...

        @runtime_checkable
        class CliContextProtocol(Protocol):
            """Protocol for CLI execution context."""

            @property
            def cwd(self) -> str:
                """Current working directory."""
                ...

            @property
            def env(self) -> Mapping[str, str]:
                """Environment variables."""
                ...

            @property
            def args(self) -> Sequence[str]:
                """Command line arguments."""
                ...

        @runtime_checkable
        class CliOutputProtocol(Protocol):
            """Protocol for CLI output handling."""

            def write(self, text: str) -> None:
                """Write text output."""
                ...

            def write_error(self, text: str) -> None:
                """Write error output."""
                ...

            def write_success(self, text: str) -> None:
                """Write success output."""
                ...

    # ═══════════════════════════════════════════════════════════════════
    # LAYER 1: Service Protocols (pode usar Layer 0)
    # ═══════════════════════════════════════════════════════════════════

    class Service:
        """Service-related protocols."""

        @runtime_checkable
        class CliServiceProtocol(Protocol):
            """Protocol for CLI services."""

            def initialize(
                self, context: FlextCliProtocols.Cli.CliContextProtocol
            ) -> FlextResult[bool]:
                """Initialize service with context."""
                ...

            def shutdown(self) -> FlextResult[bool]:
                """Shutdown service."""
                ...

            def is_healthy(self) -> bool:
                """Check service health."""
                ...

        @runtime_checkable
        class CommandServiceProtocol(Protocol):
            """Protocol for command processing services."""

            def register_command(
                self, command: FlextCliProtocols.Cli.CliCommandProtocol
            ) -> FlextResult[bool]:
                """Register a command."""
                ...

            def get_command(
                self, name: str
            ) -> FlextResult[FlextCliProtocols.Cli.CliCommandProtocol]:
                """Get command by name."""
                ...

            def list_commands(
                self,
            ) -> FlextResult[Sequence[FlextCliProtocols.Cli.CliCommandProtocol]]:
                """List all registered commands."""
                ...

        @runtime_checkable
        class OutputServiceProtocol(Protocol):
            """Protocol for output formatting services."""

            def format_table(
                self, headers: Sequence[str], rows: Sequence[Sequence[str]]
            ) -> FlextResult[str]:
                """Format data as table."""
                ...

            def format_json(self, data: object) -> FlextResult[str]:
                """Format data as JSON."""
                ...

            def format_yaml(self, data: object) -> FlextResult[str]:
                """Format data as YAML."""
                ...

    # ═══════════════════════════════════════════════════════════════════
    # LAYER 2: Handler Protocols (pode usar Layer 0 e 1)
    # ═══════════════════════════════════════════════════════════════════

    class Handler:
        """Handler-related protocols."""

        @runtime_checkable
        class CliHandlerProtocol(Protocol):
            """Protocol for CLI request handlers."""

            def can_handle(self, args: Sequence[str]) -> bool:
                """Check if handler can process arguments."""
                ...

            def handle(
                self,
                args: Sequence[str],
                context: FlextCliProtocols.Cli.CliContextProtocol,
                output: FlextCliProtocols.Cli.CliOutputProtocol,
            ) -> FlextResult[int]:
                """Handle CLI request."""
                ...

        @runtime_checkable
        class ErrorHandlerProtocol(Protocol):
            """Protocol for error handling."""

            def handle_error(self, error: Exception) -> FlextResult[str]:
                """Handle and format error."""
                ...

            def get_exit_code(self, error: Exception) -> int:
                """Get appropriate exit code for error."""
                ...

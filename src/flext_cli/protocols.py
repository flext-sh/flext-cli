"""FlextCli protocol definitions module - Structural typing."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, Self, runtime_checkable

from flext_core import FlextProtocols, FlextResult, FlextTypes


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

    class Display:
        """Rich display abstraction protocols - NO IMPORTS of Rich classes."""

        @runtime_checkable
        class RichTableProtocol(Protocol):
            """Protocol for Rich Table objects."""

            def add_column(
                self, header: str, **kwargs: FlextTypes.GeneralValueType
            ) -> None:
                """Add table column."""
                ...

            def add_row(
                self, *cells: str, **kwargs: FlextTypes.GeneralValueType
            ) -> None:
                """Add table row."""
                ...

        @runtime_checkable
        class RichTreeProtocol(Protocol):
            """Protocol for Rich Tree objects."""

            def add(self, label: str, **kwargs: FlextTypes.GeneralValueType) -> Self:
                """Add tree node."""
                ...

        @runtime_checkable
        class RichConsoleProtocol(Protocol):
            """Protocol for Rich Console objects."""

            def print(
                self,
                text: str,
                style: str | None = None,
                **kwargs: FlextTypes.GeneralValueType,
            ) -> None:
                """Print to console."""
                ...

    class Interactive:
        """Interactive display abstraction protocols."""

        @runtime_checkable
        class RichProgressProtocol(Protocol):
            """Protocol for Rich Progress objects."""

            def __enter__(
                self,
            ) -> Self:
                """Context manager enter."""
                ...

            def __exit__(self, *args: object) -> None:
                """Context manager exit."""
                ...

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

            def execute(
                self, args: Sequence[str]
            ) -> FlextProtocols.ResultProtocol[FlextTypes.GeneralValueType]:
                """Execute command with arguments."""
                ...

        @runtime_checkable
        class CliCommandHandler(Protocol):
            """Protocol for CLI command handler functions."""

            def __call__(
                self,
                *args: FlextTypes.GeneralValueType,
                **kwargs: FlextTypes.GeneralValueType,
            ) -> FlextTypes.GeneralValueType:
                """Call handler with arguments."""
                ...

        @runtime_checkable
        class CliFormatter(Protocol):
            """Protocol for CLI formatters."""

            def format_data(
                self,
                data: FlextTypes.GeneralValueType,
                **options: FlextTypes.GeneralValueType,
            ) -> FlextResult[str]:
                """Format data."""
                ...

        @runtime_checkable
        class CliConfigProvider(Protocol):
            """Protocol for CLI configuration providers."""

            def load_config(self) -> FlextResult[FlextTypes.JsonDict]:
                """Load configuration."""
                ...

            def save_config(self, config: FlextTypes.JsonDict) -> FlextResult[bool]:
                """Save configuration."""
                ...

        @runtime_checkable
        class CliAuthenticator(Protocol):
            """Protocol for CLI authentication."""

            def authenticate(self, username: str, password: str) -> FlextResult[str]:
                """Authenticate user."""
                ...

            def validate_token(self, token: str) -> FlextResult[bool]:
                """Validate authentication token."""
                ...

        @runtime_checkable
        class CliDebugProvider(Protocol):
            """Protocol for CLI debug providers."""

            def get_debug_info(self) -> FlextResult[FlextTypes.JsonDict]:
                """Get debug information."""
                ...

        # PEP 695 type aliases - direct type references
        type CliCommandFunction = CliCommandHandler
        # Type for registered commands (decorated functions)
        type CliRegisteredCommand = CliCommandProtocol

        @runtime_checkable
        class ModelCommandHandler(Protocol):
            """Protocol for model command handlers."""

            def handle(
                self,
                model: FlextTypes.GeneralValueType,
                **kwargs: FlextTypes.GeneralValueType,
            ) -> FlextProtocols.ResultProtocol[FlextTypes.GeneralValueType]:
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

        @runtime_checkable
        class CliPlugin(Protocol):
            """Protocol for CLI plugins."""

            @property
            def name(self) -> str:
                """Plugin name."""
                ...

            def initialize(self) -> FlextResult[bool]:
                """Initialize plugin."""
                ...

            def shutdown(self) -> FlextResult[bool]:
                """Shutdown plugin."""
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

            def format_json(
                self, data: FlextTypes.GeneralValueType
            ) -> FlextResult[str]:
                """Format data as JSON."""
                ...

            def format_yaml(
                self, data: FlextTypes.GeneralValueType
            ) -> FlextResult[str]:
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

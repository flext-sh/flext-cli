"""FlextCli protocol definitions module - Structural typing."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Protocol, Self, runtime_checkable

from flext_core import FlextProtocols, r, t

p = FlextProtocols


class FlextCliProtocols(p):
    """FlextCli protocol definitions composing with p.

    Business Rules:
    ───────────────
    1. Protocols define structural typing contracts - NO concrete implementations
    2. Protocols can ONLY import other Protocols (from flext projects)
    3. Protocols CANNOT import Models, Config, or concrete classes
    4. Use @runtime_checkable for isinstance() checks at runtime
    5. Use Self for methods returning the same instance (Python 3.11+)
    6. Compose with p for consistency across flext ecosystem
    7. Protocols enable dependency inversion - depend on abstractions, not concretions

    Architecture Implications:
    ───────────────────────────
    - Protocols enforce interface contracts without coupling to implementations
    - Structural typing allows multiple implementations of same protocol
    - Runtime checks via @runtime_checkable enable isinstance() validation
    - Composition with p ensures ecosystem-wide consistency

    Audit Implications:
    ───────────────────
    - Protocol violations detected at runtime via isinstance() checks
    - Missing protocol methods cause AttributeError at call site
    - Protocol compliance ensures type safety and interface contracts
    - Changes to protocols require updates to all implementations
    - Protocol methods must match signatures exactly (structural typing)
    """

    # ═══════════════════════════════════════════════════════════════════
    # LAYER 0: Domain Protocols (sem dependências internas)
    # ═══════════════════════════════════════════════════════════════════

    class Display:
        """Rich display abstraction protocols - NO IMPORTS of Rich classes."""

        @runtime_checkable
        class RichTableProtocol(Protocol):
            """Protocol for Rich Table objects."""

            def add_column(self, header: str, **kwargs: t.GeneralValueType) -> None:
                """Add table column."""
                ...

            def add_row(self, *cells: str, **kwargs: t.GeneralValueType) -> None:
                """Add table row."""
                ...

        @runtime_checkable
        class RichTreeProtocol(Protocol):
            """Protocol for Rich Tree objects."""

            def add(self, label: str, **kwargs: t.GeneralValueType) -> Self:
                """Add tree node."""
                ...

        @runtime_checkable
        class RichConsoleProtocol(Protocol):
            """Protocol for Rich Console objects."""

            def print(
                self,
                text: str,
                style: str | None = None,
                **kwargs: t.GeneralValueType,
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
            ) -> p.ResultProtocol[t.GeneralValueType]:
                """Execute command with arguments."""
                ...

        @runtime_checkable
        class CliCommandHandler(Protocol):
            """Protocol for CLI command handler functions."""

            def __call__(
                self,
                *args: t.GeneralValueType,
                **kwargs: t.GeneralValueType,
            ) -> t.GeneralValueType:
                """Call handler with arguments."""
                ...

        @runtime_checkable
        class CliFormatter(Protocol):
            """Protocol for CLI formatters."""

            def format_data(
                self,
                data: t.GeneralValueType,
                **options: t.GeneralValueType,
            ) -> r[str]:
                """Format data."""
                ...

        @runtime_checkable
        class CliConfigProvider(Protocol):
            """Protocol for CLI configuration providers."""

            def load_config(self) -> r[t.JsonDict]:
                """Load configuration."""
                ...

            def save_config(self, config: t.JsonDict) -> r[bool]:
                """Save configuration."""
                ...

        @runtime_checkable
        class CliAuthenticator(Protocol):
            """Protocol for CLI authentication.

            Business Rules:
            ───────────────
            1. Authentication MUST return r[str] with token on success
            2. Authentication MUST return r[str] with error message on failure
            3. Token validation MUST return r[bool] (True=valid, False=invalid)
            4. Credentials MUST NOT be logged or stored in plain text
            5. Tokens MUST be validated before use in subsequent operations

            Architecture Implications:
            ───────────────────────────
            - Uses Railway-Oriented Programming (FlextResult) for error handling
            - Enables multiple authentication backends (LDAP, OAuth, API keys, etc.)
            - Token-based authentication for stateless CLI operations
            - Protocol allows swapping implementations without code changes

            Audit Implications:
            ───────────────────
            - All authentication attempts MUST be logged (success/failure)
            - Failed authentication attempts MUST NOT expose user existence
            - Token validation MUST check expiration and revocation status
            - Authentication failures MUST return generic error messages
            - Token storage MUST use secure mechanisms (environment variables, keyring)
            - Remote authentication MUST use encrypted connections (TLS/SSL)
            """

            def authenticate(self, username: str, password: str) -> r[str]:
                """Authenticate user with username and password.

                Business Rule:
                ──────────────
                Validates user credentials and returns authentication token.
                Returns r[str] with token string on success, error on failure.

                Args:
                    username: User identifier for authentication
                    password: User password for authentication

                Returns:
                    r[str]: Token string on success, error message on failure

                Audit Implications:
                ───────────────────
                - Authentication attempts MUST be logged with timestamp and result
                - Failed attempts MUST NOT reveal whether username exists
                - Passwords MUST NOT be logged or stored
                - Rate limiting SHOULD be enforced to prevent brute force attacks
                - Remote authentication MUST use encrypted channels (TLS/SSL)

                """
                ...

            def validate_token(self, token: str) -> r[bool]:
                """Validate authentication token.

                Business Rule:
                ──────────────
                Validates token authenticity, expiration, and revocation status.
                Returns r[bool] with True if valid, False if invalid.

                Args:
                    token: Authentication token string to validate

                Returns:
                    r[bool]: True if token is valid, False if invalid

                Audit Implications:
                ───────────────────
                - Token validation MUST check expiration time
                - Token validation MUST check revocation status (if applicable)
                - Invalid token attempts MUST be logged for security monitoring
                - Token validation MUST be performed before any privileged operation

                """
                ...

        @runtime_checkable
        class CliDebugProvider(Protocol):
            """Protocol for CLI debug providers."""

            def get_debug_info(self) -> r[t.JsonDict]:
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
                model: t.GeneralValueType,
                **kwargs: t.GeneralValueType,
            ) -> p.ResultProtocol[t.GeneralValueType]:
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

            def initialize(self) -> r[bool]:
                """Initialize plugin."""
                ...

            def shutdown(self) -> r[bool]:
                """Shutdown plugin."""
                ...

    # ═══════════════════════════════════════════════════════════════════
    # LAYER 1: Service Protocols (pode usar Layer 0)
    # ═══════════════════════════════════════════════════════════════════
    # Note: Renamed to CliService to avoid conflict with p.Service

    class CliService:
        """CLI service-related protocols."""

        @runtime_checkable
        class CliServiceProtocol(Protocol):
            """Protocol for CLI services."""

            def initialize(
                self, context: FlextCliProtocols.Cli.CliContextProtocol
            ) -> r[bool]:
                """Initialize service with context."""
                ...

            def shutdown(self) -> r[bool]:
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
            ) -> r[bool]:
                """Register a command."""
                ...

            def get_command(
                self, name: str
            ) -> r[FlextCliProtocols.Cli.CliCommandProtocol]:
                """Get command by name."""
                ...

            def list_commands(
                self,
            ) -> r[Sequence[FlextCliProtocols.Cli.CliCommandProtocol]]:
                """List all registered commands."""
                ...

        @runtime_checkable
        class OutputServiceProtocol(Protocol):
            """Protocol for output formatting services."""

            def format_table(
                self, headers: Sequence[str], rows: Sequence[Sequence[str]]
            ) -> r[str]:
                """Format data as table."""
                ...

            def format_json(self, data: t.GeneralValueType) -> r[str]:
                """Format data as JSON."""
                ...

            def format_yaml(self, data: t.GeneralValueType) -> r[str]:
                """Format data as YAML."""
                ...

    # ═══════════════════════════════════════════════════════════════════
    # LAYER 2: Handler Protocols (pode usar Layer 0 e 1)
    # ═══════════════════════════════════════════════════════════════════
    # Note: Renamed to CliHandler to avoid conflict with p.Handler

    class CliHandler:
        """CLI handler-related protocols."""

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
            ) -> r[int]:
                """Handle CLI request."""
                ...

        @runtime_checkable
        class ErrorHandlerProtocol(Protocol):
            """Protocol for error handling."""

            def handle_error(self, error: Exception) -> r[str]:
                """Handle and format error."""
                ...

            def get_exit_code(self, error: Exception) -> int:
                """Get appropriate exit code for error."""
                ...

"""FLEXT CLI Protocols - Structural typing definitions for CLI operations (Layer 3+).

**PURPOSE**: Defines CLI-specific @runtime_checkable protocols extending FlextProtocols
for terminal output, configuration management, authentication, debugging, plugins, and
command execution. Uses structural typing (duck typing) - classes satisfy protocols
through method signatures without inheritance from the protocol itself.

**ARCHITECTURE LAYER**: Application Layer (Layer 3) Extension
- Extends Foundation protocols from flext-core Layer 3 (handlers, services)
- CLI-specific protocols add application-level abstraction for terminal operations
- Integrates with flext-core FlextProtocols base class for consistency

**PROTOCOL COMPLIANCE (Structural Typing)**:
All protocols use @runtime_checkable decorator enabling duck typing through method
signatures. Classes satisfy protocols when they implement required methods - no
inheritance needed. Example:

  from flext_cli import FlextCliProtocols

  class MyFormatter:
      def format_data(self, data: dict, **options: dict) -> FlextResult[str]:
          return FlextResult[str].ok(json.dumps(data))

  formatter = MyFormatter()
  assert isinstance(formatter, FlextCliProtocols.Cli.CliFormatter)  # True (duck typing)

**CORE PROTOCOLS** (6 CLI-specific extensions):
1. CliFormatter - Output formatting abstraction (format_data returns styled string)
2. CliConfigProvider - Configuration lifecycle (load_config, save_config)
3. CliAuthenticator - Authentication workflow (authenticate, validate_token)
4. CliDebugProvider - Debug information (get_debug_info for troubleshooting)
5. CliPlugin - Plugin system (name, version, initialize, register_commands)
6. CliCommandHandler - Command execution (callable with CLI args)

**INTEGRATION POINTS**:
- Inherits from FlextProtocols (flext-core foundation)
- Uses FlextResult[T] for all operations (railway pattern)
- References FlextCliTypes for domain data types
- Supports plugin architecture with dynamic registration
- Compatible with Click CLI framework (abstracted in cli.py)

**PRODUCTION READINESS CHECKLIST**:
✅ Structural typing via @runtime_checkable (duck typing enabled)
✅ Railway-oriented pattern (all methods return FlextResult[T])
✅ Zero external dependencies (protocol-only, no implementations)
✅ Ecosystem integration (extends flext-core FlextProtocols)
✅ Comprehensive type hints (100% annotated)
✅ Plugin system support (extensible protocol pattern)
✅ Configuration lifecycle management (load/save pattern)
✅ Authentication workflow standardization
✅ Output formatting abstraction (Rich/click agnostic)
✅ Debug information provider pattern
✅ Command execution protocol (CLI handlers)
✅ Documentation complete with usage examples

**USAGE PATTERNS**:
1. Format CLI output: `isinstance(obj, FlextCliProtocols.Cli.CliFormatter)`
2. Configuration provider: `isinstance(obj, FlextCliProtocols.Cli.CliConfigProvider)`
3. Authentication: `isinstance(obj, FlextCliProtocols.Cli.CliAuthenticator)`
4. Debug operations: `isinstance(obj, FlextCliProtocols.Cli.CliDebugProvider)`
5. Plugin registration: `isinstance(obj, FlextCliProtocols.Cli.CliPlugin)`
6. Command handling: `isinstance(obj, FlextCliProtocols.Cli.CliCommandHandler)`

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from typing import Protocol, runtime_checkable

from flext_core import FlextProtocols, FlextResult, FlextTypes

from flext_cli.typings import FlextCliTypes


class FlextCliProtocols(FlextProtocols):
    """Single unified CLI protocols class extending FLEXT foundation (Layer 3+ Application).

    **ARCHITECTURE LAYER**: Application Layer (Layer 3) - CLI-specific extension
    Extends FlextProtocols (flext-core Layer 3) with CLI operation abstractions.
    Inherits all foundation protocols: Service, Repository, Handler, Event, Logger,
    Config, Container - plus adds 6 CLI-specific @runtime_checkable protocols.

    **PROTOCOL COMPLIANCE (Structural Typing)**:
    All protocols use duck typing (structural typing via @runtime_checkable).
    Classes satisfy protocols when implementing required method signatures - no
    inheritance from protocol itself is required. This enables flexible implementations
    across different CLI frameworks (Click, Typer, Argparse, etc.).

    **CORE CAPABILITIES** (10+ integrated features):
    1. Output Formatting - Format data for terminal display
    2. Configuration Lifecycle - Load/save CLI configuration
    3. Authentication - User authentication and token validation
    4. Debug Information - Provide debug diagnostics
    5. Plugin System - Dynamic plugin loading and command registration
    6. Command Execution - Execute CLI commands with arguments
    7. Railway-Oriented Error Handling - All operations return FlextResult[T]
    8. Type Safety - 100% type annotations with strict checking
    9. Ecosystem Integration - Extends flext-core FlextProtocols foundation
    10. Zero External Dependencies - Protocol-only definitions (no implementations)

    **NESTED PROTOCOLS** (6 CLI-specific @runtime_checkable protocols):
    - **Cli.CliFormatter**: format_data(data, **options) → FlextResult[str]
      Output formatting abstraction for JSON, YAML, table, CSV formats
    - **Cli.CliConfigProvider**: load_config() → FlextResult[dict]
      Configuration lifecycle management with persistence
    - **Cli.CliAuthenticator**: authenticate(credentials) → FlextResult[str]
      Authentication workflow with token validation
    - **Cli.CliDebugProvider**: get_debug_info() → FlextResult[dict]
      Debugging information for troubleshooting
    - **Cli.CliPlugin**: initialize(cli), register_commands(cli) → FlextResult[None]
      Plugin system with dynamic command registration
    - **Cli.CliCommandHandler**: __call__(**kwargs) → FlextResult[dict]
      Callable protocol for command execution

    **INTEGRATION POINTS**:
    - Inherits from FlextProtocols (flext-core foundation patterns)
    - Uses FlextResult[T] (railway-oriented error handling)
    - References FlextCliTypes (CLI domain data types)
    - Compatible with Click CLI framework (abstracted in cli.py)
    - Supports plugin architecture with dynamic registration
    - Ecosystem-compatible (33+ FLEXT projects can implement)

    **PRODUCTION READINESS CHECKLIST**:
    ✅ Structural typing with @runtime_checkable decorators
    ✅ Railway pattern - all methods return FlextResult[T]
    ✅ Zero external dependencies in protocol definitions
    ✅ Ecosystem integration - extends flext-core FlextProtocols
    ✅ Comprehensive type annotations (100% coverage)
    ✅ Plugin system architecture (extensible patterns)
    ✅ Configuration lifecycle management (load/save)
    ✅ Authentication workflow standardization
    ✅ Output formatting abstraction (framework-agnostic)
    ✅ Debug information provider pattern
    ✅ Command execution protocol standardization
    ✅ Documentation complete with examples

    **USAGE PATTERNS** (Duck typing enabled):

    ```python
    from flext_cli import FlextCliProtocols
    from flext_core import FlextResult


    # Pattern 1: Output Formatter (duck typing)
    class JsonFormatter:
        def format_data(self, data: dict, **options: dict) -> FlextResult[str]:
            import json

            return FlextResult[str].ok(json.dumps(data, indent=2))


    formatter = JsonFormatter()
    assert isinstance(formatter, FlextCliProtocols.Cli.CliFormatter)  # True!


    # Pattern 2: Configuration Provider
    class PersistentConfig:
        def load_config(self) -> FlextResult[dict]:
            # Load from ~/.flext/config.json
            ...

        def save_config(self, config: dict) -> FlextResult[None]:
            # Save to ~/.flext/config.json
            ...


    # Pattern 3: Authenticator
    class TokenAuthenticator:
        def authenticate(self, credentials: dict) -> FlextResult[str]:
            # Validate credentials, return token
            ...

        def validate_token(self, token: str) -> FlextResult[bool]:
            # Check token validity
            ...


    # Pattern 4: Plugin
    class MyPlugin:
        name: str = "my-plugin"
        version: str = "1.0.0"

        def initialize(self, cli_main) -> FlextResult[None]:
            # Setup plugin
            ...

        def register_commands(self, cli_main) -> FlextResult[None]:
            # Register CLI commands
            ...


    # Pattern 5: Command Handler
    class ProcessCommand:
        def __call__(self, **kwargs: dict) -> FlextResult[dict]:
            # Execute command with kwargs
            return FlextResult[dict].ok({"status": "success"})


    # Pattern 6: Debug Provider
    class DebugInfoProvider:
        def get_debug_info(self) -> FlextResult[dict]:
            # Collect debug information
            return FlextResult[dict].ok({"version": "1.0.0", "python": "3.13.0"})
    ```

    **Key Design Principles**:
    - Structural typing enables flexible implementations
    - Railway pattern ensures consistent error handling
    - All protocols return FlextResult[T] (composable operations)
    - No concrete implementations (protocol-only)
    - Ecosystem-compatible (32+ projects can implement)
    """

    # =========================================================================
    # CLI-SPECIFIC PROTOCOLS - Domain extension for CLI operations
    # =========================================================================

    class Cli:
        """CLI domain-specific protocols."""

        @runtime_checkable
        class CliFormatter(Protocol):
            """Protocol for CLI output formatters."""

            def format_data(
                self,
                data: FlextCliTypes.Data.CliFormatData,
                **options: FlextCliTypes.Data.CliConfigData,
            ) -> FlextResult[str]:
                """Format data for CLI output."""
                ...

        @runtime_checkable
        class CliConfigProvider(Protocol):
            """Protocol for CLI configuration providers."""

            def load_config(
                self,
            ) -> FlextResult[FlextCliTypes.Data.CliConfigData]:
                """Load CLI configuration."""
                ...

            def save_config(
                self,
                config: FlextCliTypes.Data.CliConfigData,
            ) -> FlextResult[None]:
                """Save CLI configuration."""
                ...

        @runtime_checkable
        class CliAuthenticator(Protocol):
            """Protocol for CLI authentication providers."""

            def authenticate(
                self,
                credentials: FlextCliTypes.Data.AuthConfigData,
            ) -> FlextResult[str]:
                """Authenticate and return token."""
                ...

            def validate_token(self, token: str) -> FlextResult[bool]:
                """Validate authentication token."""
                ...

        @runtime_checkable
        class CliDebugProvider(Protocol):
            """Protocol for CLI debug information providers."""

            def get_debug_info(
                self,
            ) -> FlextResult[FlextCliTypes.Data.DebugInfoData]:
                """Get debug information."""
                ...

        @runtime_checkable
        class CliPlugin(Protocol):
            """Protocol for CLI plugins."""

            name: str
            version: str

            def initialize(self, cli_main: FlextTypes.JsonValue) -> FlextResult[None]:
                """Initialize plugin with CLI context."""
                ...

            def register_commands(
                self, cli_main: FlextTypes.JsonValue
            ) -> FlextResult[None]:
                """Register plugin commands with CLI."""
                ...

        @runtime_checkable
        class CliCommandHandler(Protocol):
            """Protocol for CLI command handlers."""

            def __call__(
                self,
                **kwargs: FlextCliTypes.Data.CliCommandArgs,
            ) -> FlextResult[FlextCliTypes.Data.CliCommandResult]:
                """Execute CLI command with arguments."""
                ...


__all__ = [
    "FlextCliProtocols",
]

"""CLI core service implementing essential functionality."""

from __future__ import annotations

import time
from pathlib import Path
from uuid import uuid4

import yaml
from flext_core import FlextResult, FlextTypes, FlextUtilities
from flext_core.domain_services import FlextDomainService

from flext_cli.formatters import FlextCliFormatters
from flext_cli.models import FlextCliModels

# Define specific types for data
DataType = (
    str
    | int
    | float
    | bool
    | list[FlextTypes.Core.Dict]
    | FlextTypes.Core.Dict
    | FlextTypes.Core.List
    | None
)


class FlextCliService(FlextDomainService[str]):
    """CLI service with essential formatting, export, and validation functionality."""

    def __init__(self) -> None:
        """Initialize CLI service with formatters."""
        super().__init__()
        self._formatters = FlextCliFormatters()
        self._config: FlextTypes.Core.Dict | None = None
        self._handlers: FlextTypes.Core.Dict = {}
        self._plugins: FlextTypes.Core.Dict = {}
        self._sessions: FlextTypes.Core.Dict = {}
        self._commands: FlextTypes.Core.Dict = {}
        self._is_started = False

    def execute(self) -> FlextResult[str]:
        """Execute service request - required by FlextDomainService."""
        return FlextResult[str].ok("CLI service executed successfully")

    def flext_cli_health(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Health check returning detailed service status with flext-core integration."""
        try:
            # Build basic health data structure
            health_data = {
                "service": "FlextCliService",
                "status": "healthy",
                "timestamp": time.time(),
                "configured": self._config is not None,
                "handlers": len(getattr(self, "_handlers", {})),
                "plugins": len(getattr(self, "_plugins", {})),
                "commands": len(getattr(self, "_commands", {})),
                "sessions": len(getattr(self, "_sessions", {})),
                "flext_core_integration": {
                    "entities": True,  # FlextModels available
                    "value_objects": True,  # FlextResult available
                    "services": True,  # FlextTypes available
                    "utilities": True,  # FlextUtilities available
                    "chain_operations": True,  # All components working
                },
            }

            # Add config details if configured
            if self._config is not None:
                health_data["config"] = {
                    "format": self._config.get("output_format", "table"),
                    "debug": self._config.get("debug", False),
                    "profile": self._config.get("profile", "default"),
                }

            return FlextResult[FlextTypes.Core.Dict].ok(health_data)

        except ImportError as e:
            # flext-core integration failed
            health_data = {
                "service": "FlextCliService",
                "status": "degraded",
                "timestamp": time.time(),
                "configured": self._config is not None,
                "handlers": len(getattr(self, "_handlers", {})),
                "plugins": len(getattr(self, "_plugins", {})),
                "commands": len(getattr(self, "_commands", {})),
                "sessions": len(getattr(self, "_sessions", {})),
                "flext_core_integration": {
                    "entities": False,
                    "value_objects": False,
                    "services": False,
                    "utilities": False,
                    "chain_operations": False,
                },
                "error": f"flext-core integration failed: {e}",
            }
            return FlextResult[FlextTypes.Core.Dict].ok(health_data)

    def start(self) -> FlextResult[None]:
        """Start the CLI service."""
        if self._is_started:
            return FlextResult[None].fail("Service already started")
        self._is_started = True
        return FlextResult[None].ok(None)

    def stop(self) -> FlextResult[None]:
        """Stop the CLI service."""
        self._is_started = False
        return FlextResult[None].ok(None)

    def health_check(self) -> FlextResult[str]:
        """Perform health check."""
        return FlextResult[str].ok("healthy")

    def configure(self, config: FlextTypes.Core.Dict | object) -> FlextResult[None]:
        """Configure service with settings dictionary or FlextCliConfig object."""
        if isinstance(config, dict):
            # Validate dictionary configuration
            valid_keys = {
                "debug",
                "output_format",
                "profile",
                "api_url",
                "timeout",
                "format_type",
            }
            unknown_keys = set(config.keys()) - valid_keys
            if unknown_keys:
                return FlextResult[None].fail(
                    f"Unknown config keys: {', '.join(unknown_keys)}"
                )

            # Handle format_type -> output_format mapping
            processed_config = dict(config)
            if (
                "format_type" in processed_config
                and "output_format" not in processed_config
            ):
                processed_config["output_format"] = processed_config.pop("format_type")

            self._config = processed_config
        elif hasattr(config, "output_format"):  # FlextCliConfig object
            # Convert FlextCliConfig to dictionary for consistent access
            self._config = {
                "debug": getattr(config, "debug", False),
                "output_format": getattr(config, "output_format", "table"),
                "profile": getattr(config, "profile", "default"),
                "api_url": getattr(config, "api_url", None),
                "timeout": getattr(config, "timeout", None),
            }
            # Remove None values
            self._config = {k: v for k, v in self._config.items() if v is not None}
        else:
            return FlextResult[None].fail(
                "Configuration must be a dictionary or FlextCliConfig object"
            )
        return FlextResult[None].ok(None)

    def flext_cli_format(self, data: DataType, format_type: str) -> FlextResult[str]:
        """Format data using specified formatter."""
        try:
            # Validate format first
            supported_formats = {"json", "csv", "yaml", "table", "plain"}
            normalized_format = format_type.lower()

            if normalized_format not in supported_formats:
                supported_list = ", ".join(sorted(supported_formats))
                return FlextResult[str].fail(
                    f"Unsupported format: {format_type}. Supported: {supported_list}"
                )

            if normalized_format == "json":
                result = FlextUtilities.safe_json_stringify(data)
                return FlextResult[str].ok(result)
            if normalized_format == "csv":
                if isinstance(data, list):
                    if not data:
                        return FlextResult[str].ok("")
                    # Simple CSV formatting for list of dicts
                    if data and isinstance(data[0], dict):
                        first_dict = data[0]
                        headers = list(first_dict.keys())
                        rows = []
                        for item in data:
                            if isinstance(item, dict):
                                row = ",".join(str(item.get(h, "")) for h in headers)
                                rows.append(row)
                        csv_content = ",".join(headers) + "\n" + "\n".join(rows)
                        return FlextResult[str].ok(csv_content)
                return FlextResult[str].ok(str(data))  # Fallback for non-list data
            if normalized_format == "yaml":
                try:
                    yaml_str = yaml.dump(data, default_flow_style=False)
                    return FlextResult[str].ok(yaml_str)
                except ImportError:
                    return FlextResult[str].fail("YAML library not available")
            else:  # table or plain format
                return FlextResult[str].ok(str(data))
        except Exception as e:
            return FlextResult[str].fail(f"Formatting failed: {e}")

    def flext_cli_export(
        self, data: DataType, file_path: str, format_type: str
    ) -> FlextResult[None]:
        """Export data to file in specified format."""
        try:
            # Format the data first
            format_result = self.flext_cli_format(data, format_type)
            if not format_result.is_success:
                return FlextResult[None].fail(f"Format failed: {format_result.error}")

            # Ensure parent directory exists
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            # Write to file
            path.write_text(format_result.data, encoding="utf-8")
            return FlextResult[None].ok(None)
        except Exception as e:
            return FlextResult[None].fail(f"Export failed: {e}")

    def flext_cli_validate_format(self, format_type: str) -> FlextResult[str]:
        """Validate if format type is supported."""
        supported_formats = {"json", "csv", "yaml", "table", "plain"}
        normalized_format = format_type.lower()
        if normalized_format in supported_formats:
            return FlextResult[str].ok(normalized_format)
        supported_list = ", ".join(sorted(supported_formats))
        return FlextResult[str].fail(
            f"Unsupported format: {format_type}. Supported: {supported_list}"
        )

    def flext_cli_render_with_context(
        self, data: DataType, context_options: FlextTypes.Core.Dict | None = None
    ) -> FlextResult[str]:
        """Render data with context options."""
        # Determine output format from context or service config
        format_type = "table"  # default

        if context_options and "output_format" in context_options:
            output_format = context_options["output_format"]
            format_type = str(output_format) if output_format is not None else "table"
        elif self._config is not None and "output_format" in self._config:
            output_format = self._config["output_format"]
            format_type = str(output_format) if output_format is not None else "table"

        # Use existing format method
        return self.flext_cli_format(data, format_type)

    def flext_cli_register_handler(
        self, name: str, handler: object
    ) -> FlextResult[None]:
        """Register a handler by name."""
        if name in self._handlers:
            return FlextResult[None].fail(f"Handler '{name}' already registered")
        self._handlers[name] = handler
        return FlextResult[None].ok(None)

    def flext_cli_execute_handler(self, name: str, data: object) -> FlextResult[object]:
        """Execute a registered handler with provided data."""
        if name not in self._handlers:
            return FlextResult[object].fail(f"Handler '{name}' not found")

        handler_obj = self._handlers[name]
        if not callable(handler_obj):
            return FlextResult[object].fail(f"Handler '{name}' is not callable")
        handler = handler_obj
        try:
            result = handler(data)
            return FlextResult[object].ok(result)
        except Exception as e:
            return FlextResult[object].fail(f"Handler execution failed: {e}")

    def flext_cli_get_handlers(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get all registered handlers."""
        return FlextResult[FlextTypes.Core.Dict].ok(dict(self._handlers))

    def flext_cli_create_session(self, user_id: str | None = None) -> FlextResult[str]:
        """Create CLI session using FlextCliModels.CliSession."""
        if user_id is None:
            user_id = f"user_{uuid4()}"

        # Create proper CliSession object
        session = FlextCliModels.CliSession(user_id=user_id)

        # Store session for retrieval
        self._sessions[session.session_id] = session

        # Session creation message
        message = f"Session created successfully with user ID: {user_id}"
        return FlextResult[str].ok(message)

    def flext_cli_get_sessions(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get all CLI sessions - basic implementation for testing."""
        if not hasattr(self, "_sessions"):
            self._sessions = {}

        # Return a copy to prevent external modification
        return FlextResult[FlextTypes.Core.Dict].ok(self._sessions.copy())

    def flext_cli_create_command(
        self, name: str, command_line: str, _description: str | None = None
    ) -> FlextResult[str]:
        """Create a new CLI command."""
        command_id = str(uuid4())
        command = FlextCliModels.CliCommand(
            id=command_id, command_line=command_line if command_line else None
        )

        self._commands[name] = command
        message = f"Command '{name}' created with ID: {command_id}"
        return FlextResult[str].ok(message)

    def flext_cli_get_commands(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get all registered commands."""
        return FlextResult[FlextTypes.Core.Dict].ok(self._commands.copy())

    def flext_cli_register_plugin(self, name: str, plugin: object) -> FlextResult[None]:
        """Register a plugin by name."""
        if name in self._plugins:
            return FlextResult[None].fail(f"Plugin '{name}' already registered")

        # Convert plugin object to dictionary for storage
        if hasattr(plugin, "model_dump"):
            plugin_dict = plugin.model_dump()
        elif hasattr(plugin, "__dict__"):
            plugin_dict = plugin.__dict__.copy()
        else:
            plugin_dict = {"name": name, "plugin": str(plugin)}

        self._plugins[name] = plugin_dict
        return FlextResult[None].ok(None)

    def flext_cli_get_plugins(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get all registered plugins."""
        return FlextResult[FlextTypes.Core.Dict].ok(self._plugins.copy())


__all__ = ["FlextCliService"]

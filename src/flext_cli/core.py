"""CLI core service implementing essential functionality."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

import yaml
from flext_core import FlextResult, FlextTypes, FlextUtilities
from flext_core.domain_services import FlextDomainService

from flext_cli.formatters import FlextCliFormatters

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

    def execute(self) -> FlextResult[str]:
        """Execute service request - required by FlextDomainService."""
        return FlextResult[str].ok("CLI service executed successfully")

    def flext_cli_health(self) -> FlextResult[str]:
        """Health check returning service status."""
        return FlextResult[str].ok("healthy")

    def configure(self, config: FlextTypes.Core.Dict) -> FlextResult[None]:
        """Configure service with settings dictionary."""
        if not isinstance(config, dict):
            return FlextResult[None].fail("Configuration must be a dictionary")
        self._config = config
        return FlextResult[None].ok(None)

    def flext_cli_format(self, data: DataType, format_type: str) -> FlextResult[str]:
        """Format data using specified formatter."""
        try:
            if format_type.lower() == "json":
                result = FlextUtilities.safe_json_stringify(data)
                return FlextResult[str].ok(result)
            if format_type.lower() == "csv" and isinstance(data, list):
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
            elif format_type.lower() == "yaml":
                # Simple YAML formatting fallback
                try:
                    yaml_str = yaml.dump(data, default_flow_style=False)
                    return FlextResult[str].ok(yaml_str)
                except ImportError:
                    return FlextResult[str].fail("YAML library not available")

            # Default to string representation
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

    def flext_cli_validate_format(self, format_type: str) -> FlextResult[bool]:
        """Validate if format type is supported."""
        supported_formats = {"json", "csv", "yaml", "table", "plain"}
        is_valid = format_type.lower() in supported_formats
        return FlextResult[bool].ok(is_valid)

    def flext_cli_register_handler(
        self, name: str, handler: object
    ) -> FlextResult[None]:
        """Register a handler by name."""
        if name in self._handlers:
            return FlextResult[None].fail(f"Handler '{name}' already registered")
        self._handlers[name] = handler
        return FlextResult[None].ok(None)

    def flext_cli_create_session(self, user_id: str | None = None) -> FlextResult[str]:
        """Create CLI session - basic implementation for testing."""
        if user_id is None:
            user_id = f"user_{uuid4()}"  # Format as expected by test

        # Create session object with expected attributes
        session_id = str(uuid4())
        session = SimpleNamespace(user_id=user_id, session_id=session_id)

        # Store session for retrieval (dictionary format as expected by test)
        if not hasattr(self, "_sessions"):
            self._sessions = {}
        self._sessions[session_id] = session

        # Simple session creation message
        message = f"Session created successfully with user ID: {user_id}"
        return FlextResult[str].ok(message)

    def flext_cli_get_sessions(self) -> FlextResult[FlextTypes.Core.Dict]:
        """Get all CLI sessions - basic implementation for testing."""
        if not hasattr(self, "_sessions"):
            self._sessions = {}

        # Return a copy to prevent external modification
        return FlextResult[FlextTypes.Core.Dict].ok(self._sessions.copy())


__all__ = ["FlextCliService"]

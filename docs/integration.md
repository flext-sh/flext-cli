# Integration Guide - flext-cli

**Ecosystem integration patterns and usage with FLEXT projects.**

**Last Updated**: September 17, 2025 | **Version**: 0.9.9 RC

---

## FLEXT Ecosystem Integration

### flext-core Foundation

flext-cli integrates with flext-core patterns. See flext-core documentation for foundation patterns.

```python
from flext_cli import FlextCli

# CLI operations
api = FlextCli()
api.process_command("example")
```

### Integration Status

| FLEXT Library           | Status      | Integration Level                                |
| ----------------------- | ----------- | ------------------------------------------------ |
| **flext-core**          | 🟢 Complete | Foundation patterns, FlextResult, FlextContainer |
| **flext-auth**          | 🟡 Partial  | Authentication commands, service integration     |
| **flext-grpc**          | 🔄 Planned  | gRPC client integration for distributed CLI      |
| **flext-observability** | 🔄 Planned  | CLI monitoring and metrics collection            |

---

## Project Integration Patterns

### Using flext-cli in Projects

For projects that need CLI functionality:

```python
# Project CLI module
from Flext_cli import FlextCli, FlextCliConfig, FlextCliAuth

class ProjectCLI:
    """Project-specific CLI interface."""

    def __init__(self):
        self.api = FlextCli()
        self.config = FlextCliConfig()
        self.auth = FlextCliAuth()

    def setup_project_commands(self):
        """Setup project-specific commands."""
        # Register custom commands
        pass
```

### Configuration Integration

```python
from Flext_cli import FlextCliConfig

def load_project_config():
    """Load configuration for project integration."""
    config = FlextCliConfig()
    config.load_project_config()
    return config.get_output_format()
```

---

## Authentication Integration

### flext-auth Integration

Current integration with flext-auth service:

```python
from flext_cli import FlextCliAuth
from flext_core import FlextResult

# Authentication workflow
auth_service = FlextCliAuth()

# Login process
login_result = auth_service.login({
    "username": "user",
    "password": "pass"
})

if login_result.is_success:
    token = login_result.unwrap()
    print("Authentication successful")
else:
    print(f"Login failed: {login_result.error}")
```

### Command-Line Authentication

```bash
# CLI authentication commands
flext auth login                # Interactive login
flext auth status               # Check authentication status
flext auth logout               # Logout current user
```

---

## HTTP Client Integration

### API Client Usage

For projects needing HTTP integration:

```python
from flext_cli import FlextApiClient
from flext_core import FlextResult

client = FlextApiClient()

# API calls with error handling
response_result = client.get("/api/data")
if response_result.is_success:
    data = response_result.unwrap()
    print(f"Data received: {data}")
```

### Configuration-based Requests

```python
from Flext_cli import FlextApiClient, FlextCliConfig

config = FlextCliConfig()
client = FlextApiClient()

# Use configuration for API endpoints
api_config = config.get_api_configuration()
response = client.request(
    method="GET",
    url=api_config["base_url"] + "/endpoint",
    headers=api_config["headers"]
)
```

---

## Output Formatting Integration

### Consistent Output Across Projects

```python
from flext_cli import FlextCliOutput
from flext_core import FlextResult

formatters = FlextCliOutput()

# Format project data consistently
def display_project_data(data: dict) -> FlextResult[None]:
    """Display data using FLEXT CLI formatters."""
    format_result = formatters.format_as_table(
        data=data,
        title="Project Data",
        headers=list(data.keys())
    )

    if format_result.is_failure:
        return FlextResult[None].fail(f"Format failed: {format_result.error}")

    print(format_result.unwrap())
    return FlextResult[None].ok(None)
```

### Multiple Output Formats

```python
# Support multiple formats based on configuration
output_format = config.get_output_format()

match output_format:
    case "table":
        result = formatters.format_as_table(data)
    case "json":
        result = formatters.format_as_json(data)
    case "yaml":
        result = formatters.format_as_yaml(data)
    case _:
        result = FlextResult[str].fail(f"Unsupported format: {output_format}")
```

---

## Extension Patterns

### Project-Specific Commands

```python
from flext_cli import FlextCliCommands
from flext_core import FlextResult, FlextService

class ProjectCommands(FlextService):
    """Project-specific CLI commands."""

    def deploy_project(self, **kwargs) -> FlextResult[None]:
        """Deploy project using CLI integration."""
        # Deployment logic
        return FlextResult[None].ok(None)

    def status_check(self, **kwargs) -> FlextResult[dict]:
        """Check project status."""
        status = {"status": "running", "health": "ok"}
        return FlextResult[dict].ok(status)

# Register with CLI
cli = FlextCliCommands(name="project-cli")
project_commands = ProjectCommands()

cli.register_command_group(
    name="project",
    commands={
        "deploy": project_commands.deploy_project,
        "status": project_commands.status_check,
    },
    description="Project management commands"
)
```

### Service Integration

```python
from flext_core import FlextContainer
from flext_cli import FlextCliService

# Register CLI service in project container
container = FlextContainer.get_global()
container.register("project_cli", FlextCliService())

# Use in project services
class ProjectService(FlextService):
    def __init__(self):
        super().__init__()
        self._container = FlextContainer.get_global()

    def get_cli_service(self) -> FlextResult[FlextCliService]:
        """Get CLI service from container."""
        return self._container.get("project_cli")
```

---

## Future Integration Plans

### Planned Integrations

1. **flext-grpc Integration**
   - Distributed CLI operations
   - Remote command execution
   - Service discovery for CLI

2. **flext-observability Integration**
   - CLI operation monitoring
   - Performance metrics collection
   - Error tracking and reporting

3. **Enhanced flext-auth Integration**
   - SSO integration
   - Role-based CLI access
   - Token management

### Migration Path

For projects currently using direct Click/Rich:

1. Replace direct imports with flext-cli abstractions
2. Adopt FlextResult error handling patterns
3. Integrate with FlextContainer for dependency management
4. Update tests to use flext-cli patterns

---

For development patterns, see [development.md](development.md).
For API details, see [api-reference.md](api-reference.md).

# FlexCore Integration Guide

**Service**: FlexCore (Go Runtime Container)  
**Port**: 8080  
**Protocol**: HTTP REST + gRPC  
**Status**: ❌ Not Integrated (Target: Sprint 1)  
**Priority**: Critical - Core infrastructure service

## 🎯 **Overview**

FlexCore is the Go-based runtime container service that provides the foundation for the FLEXT ecosystem. It manages plugins, provides service discovery, and orchestrates distributed operations across all FLEXT projects.

## 🏗️ **Architecture**

### **FlexCore Service Architecture**

```
┌─────────────────────────────────────────┐
│              FlexCore (Go:8080)         │
├─────────────────────────────────────────┤
│              Plugin System               │
│  ┌─────────┬─────────┬─────────────────┐ │
│  │ Runtime │Service  │     Plugin      │ │
│  │ Engine  │Discovery│   Management    │ │
│  └─────────┴─────────┴─────────────────┘ │
├─────────────────────────────────────────┤
│             HTTP REST API               │
│       /health  /plugins  /services      │
├─────────────────────────────────────────┤
│              gRPC Services              │
│     Plugin Execution + Management       │
└─────────────────────────────────────────┘
                    │
        ┌───────────┼───────────┐
        │                       │
   ┌────▼────┐              ┌───▼───┐
   │ FLEXT   │              │ Plugin│
   │ Service │              │ Ecosystem│
   │(Go/Py)  │              │ (32+) │
   └─────────┘              └───────┘
```

## 🔌 **Integration Points**

### **Current Status: ❌ Not Integrated**

The FLEXT CLI currently has no integration with FlexCore. The following components need to be implemented:

### **Target CLI Commands (Sprint 1)**

```bash
# Service Management
flext service health                    # Check FlexCore + all services
flext service status                   # Overall ecosystem status
flext service logs flexcore           # FlexCore-specific logs
flext service start flexcore          # Start FlexCore service
flext service stop flexcore           # Stop FlexCore service
flext service restart flexcore        # Restart FlexCore service

# Plugin Management (Sprint 4)
flext plugin list                      # List all installed plugins
flext plugin info <name>              # Plugin details and status
flext plugin install <name>           # Install new plugin
flext plugin enable <name>            # Enable plugin
flext plugin disable <name>           # Disable plugin
flext plugin logs <name>              # Plugin-specific logs

# Runtime Operations (Sprint 2)
flext runtime status                   # Runtime container status
flext runtime metrics                 # Runtime performance metrics
flext runtime config                  # Runtime configuration
```

## 🚀 **Implementation Plan**

### **Sprint 1: Basic Service Integration**

#### **1. FlexCore HTTP Client**

```python
# src/flext_cli/clients/flexcore_client.py
from dataclasses import dataclass
from typing import List, Dict, Any
import httpx
from flext_core import FlextResult

@dataclass
class ServiceHealth:
    service_name: str
    status: str  # "healthy", "unhealthy", "unknown"
    response_time_ms: float
    version: str
    uptime_seconds: int

@dataclass
class PluginInfo:
    name: str
    version: str
    status: str  # "active", "inactive", "error"
    dependencies: List[str]
    entry_point: str

class FlexCoreClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=30.0
        )

    async def health_check(self) -> FlextResult[ServiceHealth]:
        """Check FlexCore service health."""
        try:
            response = await self.client.get("/health")
            if response.status_code == 200:
                data = response.json()
                health = ServiceHealth(
                    service_name="flexcore",
                    status=data.get("status", "unknown"),
                    response_time_ms=response.elapsed.total_seconds() * 1000,
                    version=data.get("version", "unknown"),
                    uptime_seconds=data.get("uptime", 0)
                )
                return FlextResult.ok(health)
            else:
                return FlextResult.fail(f"Health check failed: {response.status_code}")
        except httpx.TimeoutException:
            return FlextResult.fail("FlexCore health check timeout")
        except httpx.ConnectError:
            return FlextResult.fail("Cannot connect to FlexCore")
        except Exception as e:
            return FlextResult.fail(f"Health check error: {e}")

    async def list_plugins(self) -> FlextResult[List[PluginInfo]]:
        """List all installed plugins."""
        try:
            response = await self.client.get("/api/v1/plugins")
            if response.status_code == 200:
                plugins_data = response.json()
                plugins = [
                    PluginInfo(
                        name=p["name"],
                        version=p["version"],
                        status=p["status"],
                        dependencies=p.get("dependencies", []),
                        entry_point=p["entry_point"]
                    )
                    for p in plugins_data
                ]
                return FlextResult.ok(plugins)
            else:
                return FlextResult.fail(f"Failed to list plugins: {response.status_code}")
        except Exception as e:
            return FlextResult.fail(f"Plugin listing error: {e}")

    async def get_plugin_info(self, plugin_name: str) -> FlextResult[PluginInfo]:
        """Get detailed information about a specific plugin."""
        try:
            response = await self.client.get(f"/api/v1/plugins/{plugin_name}")
            if response.status_code == 200:
                data = response.json()
                plugin = PluginInfo(
                    name=data["name"],
                    version=data["version"],
                    status=data["status"],
                    dependencies=data.get("dependencies", []),
                    entry_point=data["entry_point"]
                )
                return FlextResult.ok(plugin)
            elif response.status_code == 404:
                return FlextResult.fail(f"Plugin '{plugin_name}' not found")
            else:
                return FlextResult.fail(f"Failed to get plugin info: {response.status_code}")
        except Exception as e:
            return FlextResult.fail(f"Plugin info error: {e}")

    async def execute_plugin(self, plugin_name: str, args: Dict[str, Any]) -> FlextResult[Any]:
        """Execute a plugin with given arguments."""
        try:
            payload = {
                "plugin": plugin_name,
                "args": args
            }
            response = await self.client.post("/api/v1/plugins/execute", json=payload)
            if response.status_code == 200:
                return FlextResult.ok(response.json())
            else:
                return FlextResult.fail(f"Plugin execution failed: {response.status_code}")
        except Exception as e:
            return FlextResult.fail(f"Plugin execution error: {e}")

    async def get_service_logs(self, lines: int = 100) -> FlextResult[List[str]]:
        """Get FlexCore service logs."""
        try:
            params = {"lines": lines}
            response = await self.client.get("/api/v1/logs", params=params)
            if response.status_code == 200:
                logs = response.json().get("logs", [])
                return FlextResult.ok(logs)
            else:
                return FlextResult.fail(f"Failed to get logs: {response.status_code}")
        except Exception as e:
            return FlextResult.fail(f"Log retrieval error: {e}")
```

#### **2. Service Commands Implementation**

```python
# src/flext_cli/commands/service.py
import click
from rich.console import Console
from rich.table import Table
from flext_cli.clients.flexcore_client import FlexCoreClient
from flext_cli.core.base import handle_service_result

@click.group()
def service():
    """Service management commands."""
    pass

@service.command()
@click.pass_context
@handle_service_result
async def health(ctx: click.Context):
    """Check health of all FLEXT services."""
    console: Console = ctx.obj["console"]

    # Create health check table
    table = Table(title="FLEXT Service Health")
    table.add_column("Service", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Response Time", style="green")
    table.add_column("Version", style="blue")

    # Check FlexCore
    flexcore_client = FlexCoreClient()
    health_result = await flexcore_client.health_check()

    if health_result.success:
        health = health_result.unwrap()
        status_color = "green" if health.status == "healthy" else "red"
        table.add_row(
            "FlexCore",
            f"[{status_color}]{health.status}[/{status_color}]",
            f"{health.response_time_ms:.1f}ms",
            health.version
        )
    else:
        table.add_row("FlexCore", "[red]ERROR[/red]", "N/A", "N/A")

    # TODO: Add other services (FLEXT Service, etc.)

    console.print(table)

@service.command()
@click.pass_context
@handle_service_result
async def status(ctx: click.Context):
    """Show overall ecosystem status."""
    console: Console = ctx.obj["console"]

    # Overall status dashboard
    console.print("[bold blue]FLEXT Ecosystem Status[/bold blue]")

    # Service status
    flexcore_client = FlexCoreClient()
    health_result = await flexcore_client.health_check()

    if health_result.success:
        health = health_result.unwrap()
        console.print(f"✅ FlexCore: {health.status} (v{health.version})")
    else:
        console.print(f"❌ FlexCore: {health_result.error}")

    # TODO: Add plugin status, pipeline status, etc.

@service.command()
@click.argument("service_name", default="flexcore")
@click.option("--lines", "-n", default=100, help="Number of log lines to show")
@click.pass_context
@handle_service_result
async def logs(ctx: click.Context, service_name: str, lines: int):
    """Show service logs."""
    console: Console = ctx.obj["console"]

    if service_name.lower() == "flexcore":
        flexcore_client = FlexCoreClient()
        logs_result = await flexcore_client.get_service_logs(lines)

        if logs_result.success:
            logs = logs_result.unwrap()
            console.print(f"[bold]FlexCore Logs (last {lines} lines):[/bold]")
            for log_line in logs:
                console.print(log_line)
        else:
            console.print(f"[red]Failed to get logs: {logs_result.error}[/red]")
    else:
        console.print(f"[yellow]Service '{service_name}' not yet supported[/yellow]")
```

#### **3. Plugin Commands Implementation**

```python
# src/flext_cli/commands/plugin.py
import click
from rich.console import Console
from rich.table import Table
from flext_cli.clients.flexcore_client import FlexCoreClient
from flext_cli.core.base import handle_service_result

@click.group()
def plugin():
    """Plugin management commands."""
    pass

@plugin.command()
@click.pass_context
@handle_service_result
async def list(ctx: click.Context):
    """List all installed plugins."""
    console: Console = ctx.obj["console"]

    flexcore_client = FlexCoreClient()
    plugins_result = await flexcore_client.list_plugins()

    if plugins_result.success:
        plugins = plugins_result.unwrap()

        table = Table(title="Installed Plugins")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="green")
        table.add_column("Status", style="bold")
        table.add_column("Dependencies", style="blue")

        for plugin in plugins:
            status_color = "green" if plugin.status == "active" else "red"
            deps = ", ".join(plugin.dependencies) if plugin.dependencies else "None"

            table.add_row(
                plugin.name,
                plugin.version,
                f"[{status_color}]{plugin.status}[/{status_color}]",
                deps
            )

        console.print(table)
    else:
        console.print(f"[red]Failed to list plugins: {plugins_result.error}[/red]")

@plugin.command()
@click.argument("plugin_name")
@click.pass_context
@handle_service_result
async def info(ctx: click.Context, plugin_name: str):
    """Show detailed plugin information."""
    console: Console = ctx.obj["console"]

    flexcore_client = FlexCoreClient()
    plugin_result = await flexcore_client.get_plugin_info(plugin_name)

    if plugin_result.success:
        plugin = plugin_result.unwrap()

        console.print(f"[bold blue]Plugin: {plugin.name}[/bold blue]")
        console.print(f"Version: {plugin.version}")
        console.print(f"Status: {plugin.status}")
        console.print(f"Entry Point: {plugin.entry_point}")

        if plugin.dependencies:
            console.print("Dependencies:")
            for dep in plugin.dependencies:
                console.print(f"  - {dep}")
        else:
            console.print("Dependencies: None")
    else:
        console.print(f"[red]Failed to get plugin info: {plugin_result.error}[/red]")
```

#### **4. Registration in Main CLI**

```python
# src/flext_cli/cli.py
from flext_cli.commands import service, plugin

# Register new commands
cli.add_command(service.service)
cli.add_command(plugin.plugin)
```

### **Sprint 2: Advanced Integration**

#### **1. gRPC Client for High-Performance Operations**

```python
# src/flext_cli/clients/flexcore_grpc_client.py
import grpc
from flext_core import FlextResult
# Import generated gRPC stubs
from flext_grpc import flexcore_pb2, flexcore_pb2_grpc

class FlexCoreGRPCClient:
    def __init__(self, address: str = "localhost:9090"):
        self.channel = grpc.aio.insecure_channel(address)
        self.stub = flexcore_pb2_grpc.FlexCoreServiceStub(self.channel)

    async def execute_plugin_grpc(self, plugin_name: str, args: dict) -> FlextResult[Any]:
        """Execute plugin via gRPC for better performance."""
        try:
            request = flexcore_pb2.ExecutePluginRequest(
                name=plugin_name,
                args=args
            )
            response = await self.stub.ExecutePlugin(request)
            return FlextResult.ok(response.result)
        except grpc.aio.AioRpcError as e:
            return FlextResult.fail(f"gRPC error: {e.details()}")
        except Exception as e:
            return FlextResult.fail(f"Plugin execution error: {e}")
```

### **Sprint 4: Plugin System Integration**

#### **1. Dynamic Plugin Loading**

```python
# src/flext_cli/plugin_system/plugin_loader.py
class FlextPluginLoader:
    async def load_plugin_commands(self, plugin_name: str) -> FlextResult[click.Group]:
        """Dynamically load CLI commands from FlexCore plugin."""
        flexcore_client = FlexCoreClient()

        # Get plugin manifest
        plugin_result = await flexcore_client.get_plugin_info(plugin_name)
        if not plugin_result.success:
            return plugin_result

        plugin = plugin_result.unwrap()

        # Load command definitions from plugin
        commands_result = await flexcore_client.get_plugin_commands(plugin_name)
        if not commands_result.success:
            return commands_result

        # Create Click command group dynamically
        return self._create_click_group(plugin, commands_result.unwrap())
```

## 🧪 **Testing Strategy**

### **Unit Tests**

```python
# tests/unit/test_flexcore_client.py
import pytest
from unittest.mock import AsyncMock
from flext_cli.clients.flexcore_client import FlexCoreClient

@pytest.mark.asyncio
async def test_health_check_success():
    client = FlexCoreClient()
    client.client.get = AsyncMock()

    # Mock successful response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "status": "healthy",
        "version": "1.0.0",
        "uptime": 3600
    }
    client.client.get.return_value = mock_response

    result = await client.health_check()

    assert result.success
    health = result.unwrap()
    assert health.service_name == "flexcore"
    assert health.status == "healthy"
```

### **Integration Tests**

```python
# tests/integration/test_flexcore_integration.py
import pytest
from flext_cli.clients.flexcore_client import FlexCoreClient

@pytest.mark.integration
@pytest.mark.asyncio
async def test_flexcore_health_check_real():
    """Test actual FlexCore service health check."""
    client = FlexCoreClient()
    result = await client.health_check()

    # Should succeed if FlexCore is running
    if result.success:
        health = result.unwrap()
        assert health.service_name == "flexcore"
        assert health.status in ["healthy", "unhealthy"]
    else:
        # If FlexCore is not running, should get connection error
        assert "connect" in result.error.lower()
```

## 📊 **Success Metrics**

### **Sprint 1 Completion Criteria**

- [ ] `flext service health` shows FlexCore status
- [ ] `flext service logs flexcore` displays service logs
- [ ] `flext plugin list` shows installed plugins
- [ ] Integration tests pass with running FlexCore instance
- [ ] Error handling for service unavailable scenarios

### **Sprint 2 Completion Criteria**

- [ ] gRPC client implemented for high-performance operations
- [ ] Service start/stop commands functional
- [ ] Real-time log streaming implemented
- [ ] Performance meets <1s response time target

### **Sprint 4 Completion Criteria**

- [ ] Dynamic plugin loading working
- [ ] Plugin install/enable/disable commands functional
- [ ] Plugin marketplace integration
- [ ] Plugin dependency resolution

## 🔗 **Related Documentation**

- [FLEXT Service Integration](flext-service.md) - Companion data platform service
- [Service Discovery](../architecture/service-discovery.md) - Service discovery patterns
- [Plugin System](../architecture/plugin-system.md) - Plugin architecture details
- [gRPC Integration](communication.md#grpc) - gRPC communication patterns

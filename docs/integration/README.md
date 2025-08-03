# FLEXT Ecosystem Integration Guide

**Document**: Comprehensive guide for integrating FLEXT CLI with the entire ecosystem  
**Version: 0.9.0 (2025-08-01)  
**Scope**: All 32+ FLEXT projects integration  
**Status\*\*: 30% implemented - See individual integration status

## 🎯 **Overview**

FLEXT CLI serves as the unified command interface for the entire FLEXT distributed data integration ecosystem. This documentation covers integration patterns, service connectivity, and operational procedures for all ecosystem components.

## 🏗️ **FLEXT Ecosystem Architecture**

### **Core Services (2 services)**

- **[FlexCore](flexcore.md)** (Go): Runtime container service (port 8080)
- **[FLEXT Service](flext-service.md)** (Go/Python): Main data platform service (port 8081)

### **Foundation Libraries (2 projects)**

- **[flext-core](flext-core.md)**: Base patterns, logging, result handling, dependency injection
- **[flext-observability](observability.md)**: Monitoring, metrics, tracing, health checks

### **Infrastructure Libraries (6 projects)**

- **[flext-db-oracle](databases.md#oracle)**: Oracle database connectivity and operations
- **[flext-ldap](directories.md#ldap)**: LDAP server connectivity and directory operations
- **[flext-ldif](directories.md#ldif)**: LDIF file processing and validation
- **[flext-oracle-wms](databases.md#oracle-wms)**: Oracle WMS API connectivity and data models
- **[flext-grpc](communication.md#grpc)**: gRPC communication protocols
- **[flext-meltano](orchestration.md#meltano)**: Singer/Meltano/DBT orchestration

### **Application Services (5 projects)**

- **[flext-api](services.md#api)**: REST API services with FastAPI
- **[flext-auth](services.md#auth)**: Authentication and authorization services
- **[flext-web](services.md#web)**: Web interface and dashboard
- **[flext-quality](services.md#quality)**: Code quality analysis and reporting
- **[flext-cli](services.md#cli)**: This command-line interface

### **Singer Ecosystem (15 projects)**

**[Singer Taps (5 extractors)](singer-ecosystem.md#taps):**

- flext-tap-ldap, flext-tap-ldif, flext-tap-oracle, flext-tap-oracle-oic, flext-tap-oracle-wms

**[Singer Targets (5 loaders)](singer-ecosystem.md#targets):**

- flext-target-ldap, flext-target-ldif, flext-target-oracle, flext-target-oracle-oic, flext-target-oracle-wms

**[DBT Projects (4 transformers)](singer-ecosystem.md#dbt):**

- flext-dbt-ldap, flext-dbt-ldif, flext-dbt-oracle, flext-dbt-oracle-wms

**[Extensions (1 project)](singer-ecosystem.md#extensions):**

- flext-oracle-oic-ext

### **Project-Specific Integrations (2 projects)**

- **[algar-oud-mig](projects.md#algar)**: ALGAR Oracle Unified Directory migration
- **[gruponos-meltano-native](projects.md#gruponos)**: GrupoNos-specific Meltano implementation

## 🔌 **Integration Patterns**

### **Service Communication Patterns**

#### **1. HTTP REST APIs**

```python
# FlexCore Integration (Go:8080)
async def health_check_flexcore() -> FlextResult[ServiceHealth]:
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8080/health")
        return FlextResult.ok(ServiceHealth.from_response(response))

# FLEXT Service Integration (Go/Py:8081)
async def health_check_flext_service() -> FlextResult[ServiceHealth]:
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8081/health")
        return FlextResult.ok(ServiceHealth.from_response(response))
```

#### **2. gRPC Communication**

```python
# High-performance communication with flext-grpc
from flext_grpc import FlextServiceClient

async def execute_pipeline_command(pipeline_name: str) -> FlextResult[PipelineStatus]:
    client = FlextServiceClient("localhost:9090")
    result = await client.start_pipeline(pipeline_name)
    return FlextResult.from_grpc_response(result)
```

#### **3. Event-Driven Integration**

```python
# Domain Events for ecosystem coordination
from flext_core import FlextEventPublisher

async def publish_command_started(command: CLICommand):
    event = CommandStartedEvent(command_id=command.id, command_name=command.name)
    await event_publisher.publish(event)
```

### **Configuration Management Patterns**

#### **1. Environment-Specific Configuration**

```yaml
# config/dev.yaml
services:
  flexcore:
    url: "http://localhost:8080"
    timeout: 30
  flext-service:
    url: "http://localhost:8081"
    timeout: 60

# config/prod.yaml
services:
  flexcore:
    url: "https://flexcore.flext.prod"
    timeout: 10
  flext-service:
    url: "https://flext-service.flext.prod"
    timeout: 30
```

#### **2. Service Discovery**

```python
class FlextServiceDiscovery:
    def __init__(self, environment: str):
        self.config = load_environment_config(environment)

    async def discover_services(self) -> Dict[str, ServiceEndpoint]:
        # Automatic service discovery and health checking
        return {
            service_name: await self.check_service_health(endpoint)
            for service_name, endpoint in self.config.services.items()
        }
```

## 📊 **Integration Status Matrix**

### ✅ **Fully Integrated (30%)**

| Service   | CLI Commands        | Health Check | Logs | Metrics | Status   |
| --------- | ------------------- | ------------ | ---- | ------- | -------- |
| flext-cli | auth, config, debug | ✅           | ✅   | ✅      | Complete |

### ⚠️ **Partially Integrated (0%)**

| Service          | CLI Commands | Health Check | Logs | Metrics | Status |
| ---------------- | ------------ | ------------ | ---- | ------- | ------ |
| _None currently_ | -            | -            | -    | -       | -      |

### ❌ **Not Integrated (70%)**

| Service                   | CLI Commands | Health Check | Logs | Metrics | Target Sprint |
| ------------------------- | ------------ | ------------ | ---- | ------- | ------------- |
| FlexCore                  | service      | ❌           | ❌   | ❌      | Sprint 1      |
| FLEXT Service             | pipeline     | ❌           | ❌   | ❌      | Sprint 1      |
| flext-meltano             | data         | ❌           | ❌   | ❌      | Sprint 3      |
| Singer Taps (5)           | data taps    | ❌           | ❌   | ❌      | Sprint 3      |
| Singer Targets (5)        | data targets | ❌           | ❌   | ❌      | Sprint 3      |
| DBT Projects (4)          | data dbt     | ❌           | ❌   | ❌      | Sprint 3      |
| algar-oud-mig             | algar        | ❌           | ❌   | ❌      | Sprint 5      |
| gruponos-meltano-native   | gruponos     | ❌           | ❌   | ❌      | Sprint 5      |
| flext-observability       | monitor      | ❌           | ❌   | ❌      | Sprint 7      |
| flext-api                 | service      | ❌           | ❌   | ❌      | Sprint 2      |
| flext-web                 | service      | ❌           | ❌   | ❌      | Sprint 2      |
| flext-auth                | auth         | ❌           | ❌   | ❌      | Sprint 2      |
| _+18 additional projects_ | various      | ❌           | ❌   | ❌      | Sprints 2-8   |

## 🚀 **Integration Implementation Guide**

### **Phase 1: Core Services (Sprint 1-2)**

#### **FlexCore Integration**

```python
# Target: flext service health, start, stop, logs
class FlexCoreClient:
    def __init__(self, base_url: str = "http://localhost:8080"):
        self.client = httpx.AsyncClient(base_url=base_url)

    async def health_check(self) -> FlextResult[ServiceHealth]:
        # Implementation

    async def list_plugins(self) -> FlextResult[List[Plugin]]:
        # Implementation

    async def execute_plugin(self, plugin_name: str, args: Dict) -> FlextResult[Any]:
        # Implementation
```

#### **FLEXT Service Integration**

```python
# Target: flext pipeline list, start, stop, status
class FlextServiceClient:
    def __init__(self, base_url: str = "http://localhost:8081"):
        self.client = httpx.AsyncClient(base_url=base_url)

    async def list_pipelines(self) -> FlextResult[List[Pipeline]]:
        # Implementation

    async def start_pipeline(self, name: str) -> FlextResult[PipelineStatus]:
        # Implementation

    async def stop_pipeline(self, name: str) -> FlextResult[PipelineStatus]:
        # Implementation
```

### **Phase 2: Data Platform (Sprint 3-4)**

#### **Singer Ecosystem Integration**

```python
# Target: flext data taps list, flext data targets list
class SingerEcosystemClient:
    async def list_taps(self) -> FlextResult[List[SingerTap]]:
        # Integration with 5 Singer tap projects

    async def list_targets(self) -> FlextResult[List[SingerTarget]]:
        # Integration with 5 Singer target projects

    async def run_dbt_project(self, project: str) -> FlextResult[DBTRunResult]:
        # Integration with 4 DBT projects
```

### **Phase 3: Project-Specific (Sprint 5-6)**

#### **ALGAR Integration**

```python
# Target: flext algar migration status, oud sync
class AlgarOUDClient:
    async def migration_status(self) -> FlextResult[MigrationStatus]:
        # Integration with algar-oud-mig project

    async def oud_sync(self) -> FlextResult[SyncResult]:
        # Oracle Unified Directory synchronization
```

#### **GrupoNos Integration**

```python
# Target: flext gruponos pipeline deploy
class GrupoNosMeltanoClient:
    async def deploy_pipeline(self, config: PipelineConfig) -> FlextResult[DeployResult]:
        # Integration with gruponos-meltano-native project
```

## 🔧 **Development Guidelines**

### **Adding New Service Integration**

1. **Create Service Client**:

   ```python
   # src/flext_cli/clients/{service_name}_client.py
   class ServiceNameClient:
       async def health_check(self) -> FlextResult[ServiceHealth]:
           # Standard health check implementation
   ```

2. **Register in DI Container**:

   ```python
   # src/flext_cli/infrastructure/container.py
   container.register_typed(ServiceNameClient, ServiceNameClient)
   ```

3. **Add CLI Commands**:

   ```python
   # src/flext_cli/commands/{service_name}.py
   @click.group()
   def service_name():
       """Service-specific commands."""
       pass
   ```

4. **Integration Tests**:

   ```python
   # tests/integration/test_{service_name}_integration.py
   @pytest.mark.integration
   async def test_service_integration():
       # Test real service integration
   ```

### **Service Health Check Standards**

All integrations must implement standardized health checks:

```python
@dataclass
class ServiceHealth:
    service_name: str
    status: HealthStatus  # HEALTHY, UNHEALTHY, UNKNOWN
    response_time_ms: float
    last_check: datetime
    details: Dict[str, Any]

    @classmethod
    def from_response(cls, response: httpx.Response) -> 'ServiceHealth':
        # Standard parsing from HTTP health check response
```

### **Error Handling Standards**

All integrations must use FlextResult for error handling:

```python
async def service_operation() -> FlextResult[Any]:
    try:
        result = await external_service_call()
        return FlextResult.ok(result)
    except httpx.TimeoutException:
        return FlextResult.fail("Service timeout")
    except httpx.ConnectError:
        return FlextResult.fail("Service unavailable")
    except Exception as e:
        return FlextResult.fail(f"Unexpected error: {e}")
```

## 📚 **Next Steps**

1. **Review Individual Integration Guides**: Each service has detailed integration documentation
2. **Follow Development Roadmap**: See [roadmap.md](../roadmap.md) for sprint-by-sprint implementation
3. **Implement Integration Tests**: Ensure all integrations have comprehensive test coverage
4. **Monitor Integration Health**: Use health checks and monitoring for all integrated services

## 📖 **Related Documentation**

- [FlexCore Integration](flexcore.md) - Core runtime service integration
- [FLEXT Service Integration](flext-service.md) - Data platform service integration
- [Singer Ecosystem](singer-ecosystem.md) - Data pipeline integration
- [Project-Specific Integration](projects.md) - ALGAR and GrupoNos integration
- [Development Setup](../development/setup.md) - Development environment configuration

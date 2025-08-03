# Infrastructure Layer - External Concerns and Technical Implementation

**Module**: `src/flext_cli/infrastructure/`  
**Architecture Layer**: Infrastructure (Outermost Layer)  
**Status**: 50% implemented - Basic patterns, FlextContainer migration planned for Sprint 1-3  
**Sprint Alignment**: Major enhancement target for Sprints 1-3

## 🎯 Module Overview

The infrastructure layer handles all external concerns including databases, file systems, web services, and third-party integrations. This layer implements technical details while maintaining independence from business logic through well-defined interfaces.

### **Key Responsibilities**

- **Dependency Injection**: Service registration and resolution
- **Configuration Management**: Environment and system settings
- **External Service Integration**: HTTP clients, APIs, third-party services
- **Data Persistence**: Repository implementations and data access
- **System Integration**: File system, network, and OS interactions

## 📁 Module Structure

```
src/flext_cli/infrastructure/
├── __init__.py           # Infrastructure layer exports and service registration
├── container.py          # Dependency injection container (needs FlextContainer migration)
└── config.py             # Configuration management and environment handling
```

## 🏗️ Architecture Patterns

### **Current Implementation (50% Complete)**

- ✅ **Basic Dependency Injection**: SimpleDIContainer implementation
- ✅ **Configuration Management**: Environment and system configuration
- ✅ **Service Registration**: Basic service resolution patterns
- ⚠️ **Custom DI Container**: Needs migration to FlextContainer (Sprint 1-3)

### **Target Architecture (Sprint 1-3)**

- 🎯 **FlextContainer Integration**: Full flext-core dependency injection
- 🎯 **Repository Implementations**: Real data persistence (Sprint 5)
- 🎯 **Service Integration**: FlexCore and FLEXT Service clients
- 🎯 **Advanced Configuration**: Profile management and hierarchical config

## 📊 Implementation Status

### ✅ **Currently Implemented**

#### **container.py - Dependency Injection (Line References)**

- **SimpleDIContainer** (line 18): Custom dependency injection implementation
  - Service registration and resolution
  - Basic lifecycle management
  - Type-safe service retrieval
  - Mock repository implementations

#### **config.py - Configuration Management**

- **Environment Configuration**: System and environment settings
- **Path Management**: Directory and file path handling
- **Configuration Loading**: Basic configuration file support

### ⚠️ **Needs Migration (Sprint 1-3 CRITICAL)**

#### **FlextContainer Migration**

```python
# Current (Custom Implementation)
class SimpleDIContainer:
    def register(self, service_type: type, implementation: type) -> None:
        # Custom implementation

# Target (flext-core Integration - Sprint 1-3)
from flext_core import get_flext_container, FlextContainer

class InfrastructureContainer:
    def __init__(self) -> None:
        self._container = get_flext_container()
        self._register_services()

    def _register_services(self) -> None:
        # Type-safe service registration
        self._container.register_typed(CLICommandRepository, SqliteCLICommandRepository)
        self._container.register_typed(FlextEventPublisher, DefaultEventPublisher)
```

### ❌ **Missing Critical Components**

#### **Repository Implementations (Sprint 5)**

```python
# Current (Mock Only)
class MockCLICommandRepository:
    # Mock implementation only

# Target (Real Implementation - Sprint 5)
from flext_core import FlextRepository

class SqliteCLICommandRepository(FlextRepository[CLICommand]):
    async def save(self, entity: CLICommand) -> FlextResult[CLICommand]:
        # Real SQLite persistence

    async def find_by_id(self, entity_id: str) -> FlextResult[CLICommand]:
        # Real query implementation
```

#### **Service Integration (Sprint 1)**

```python
# Target (Sprint 1)
class FlextServiceClient:
    async def health_check_flexcore(self) -> FlextResult[ServiceHealth]:
        # FlexCore:8080 integration

    async def health_check_flext_service(self) -> FlextResult[ServiceHealth]:
        # FLEXT Service:8081 integration
```

## 🎯 Sprint Roadmap Alignment

### **Sprint 1: FlextContainer Migration** (CRITICAL)

```python
# Priority 1: Replace SimpleDIContainer
from flext_core import FlextContainer, get_flext_container

class FlextCliContainer:
    def __init__(self) -> None:
        self._container = get_flext_container()
        self._register_core_services()
        self._register_repositories()
        self._register_external_services()

    def _register_core_services(self) -> None:
        # Core service registration with type safety
        self._container.register_typed(CLICommandService, CLICommandService)
        self._container.register_typed(CLISessionService, CLISessionService)
```

### **Sprint 1: Service Integration Foundation**

```python
# FlexCore and FLEXT Service integration
class ServiceIntegrationModule:
    def register_services(self, container: FlextContainer) -> None:
        container.register_typed(FlextServiceClient, HttpFlextServiceClient)
        container.register_typed(FlexCoreClient, HttpFlexCoreClient)
```

### **Sprint 3: Advanced Configuration**

```python
# Profile management and hierarchical configuration
class ProfileConfigurationManager:
    async def load_profile(self, profile_name: str) -> FlextResult[CLIConfig]:
        # Load from ~/.flx/profiles/{profile_name}.yaml
        # Support configuration inheritance
        # Environment variable override
```

### **Sprint 5: Repository Implementation**

```python
# Real data persistence
class PersistenceModule:
    def register_repositories(self, container: FlextContainer) -> None:
        container.register_typed(CLICommandRepository, SqliteCLICommandRepository)
        container.register_typed(CLISessionRepository, SqliteCLISessionRepository)
        container.register_typed(CLIPluginRepository, SqliteCLIPluginRepository)
```

## 🔧 Development Guidelines

### **Service Registration (Current Pattern)**

```python
# Current pattern with SimpleDIContainer
def register_services(container: SimpleDIContainer) -> None:
    container.register(CLICommandService, CLICommandService)
    container.register(CLICommandRepository, MockCLICommandRepository)
```

### **Service Registration (Target Pattern - Sprint 1-3)**

```python
# Target pattern with FlextContainer
from flext_core import FlextContainer

def register_infrastructure_services(container: FlextContainer) -> None:
    # Type-safe registration
    container.register_typed(CLICommandRepository, SqliteCLICommandRepository)
    container.register_typed(CLISessionRepository, SqliteCLISessionRepository)

    # Singleton services
    container.register_singleton(ConfigurationManager, ConfigurationManager)

    # Factory registration
    container.register_factory(DatabaseConnection, create_database_connection)
```

### **Repository Implementation (Sprint 5)**

```python
from flext_core import FlextRepository, FlextResult

class SqliteCLICommandRepository(FlextRepository[CLICommand]):
    def __init__(self, db_path: str) -> None:
        self._db_path = db_path
        self._init_database()

    async def save(self, entity: CLICommand) -> FlextResult[CLICommand]:
        try:
            # SQLite persistence implementation
            return FlextResult.ok(entity)
        except Exception as e:
            return FlextResult.fail(f"Failed to save command: {e}")

    async def find_by_id(self, entity_id: str) -> FlextResult[CLICommand]:
        try:
            # Query implementation
            return FlextResult.ok(command)
        except Exception as e:
            return FlextResult.fail(f"Failed to find command: {e}")
```

### **Configuration Management Enhancement**

```python
# Advanced configuration management
class HierarchicalConfigurationManager:
    def __init__(self) -> None:
        self._config_sources = [
            CommandLineConfigSource(),
            EnvironmentConfigSource(),
            ProfileConfigSource(),
            DefaultConfigSource()
        ]

    async def load_configuration(self, profile: str) -> FlextResult[CLIConfig]:
        # Merge configurations from multiple sources
        # Command-line > Environment > Profile > Defaults
```

## 🧪 Testing Guidelines

### **Infrastructure Testing**

```python
@pytest.mark.integration
async def test_repository_persistence():
    repository = SqliteCLICommandRepository(":memory:")
    command = CLICommand(name="test", command_line="echo hello")

    # Test save
    save_result = await repository.save(command)
    assert save_result.is_success

    # Test retrieval
    find_result = await repository.find_by_id(command.id)
    assert find_result.is_success
    assert find_result.unwrap().name == "test"
```

### **Container Testing**

```python
def test_container_service_resolution():
    container = FlextCliContainer()

    # Test service resolution
    service = container.get_typed(CLICommandService)
    assert isinstance(service, CLICommandService)

    # Test singleton behavior
    service2 = container.get_typed(CLICommandService)
    assert service is service2  # Same instance for singletons
```

### **Configuration Testing**

```python
def test_configuration_loading():
    config_manager = ConfigurationManager()

    # Test profile loading
    result = await config_manager.load_profile("development")
    assert result.is_success

    config = result.unwrap()
    assert config.profile == "development"
    assert config.debug is True
```

## 📈 Current vs Target Implementation

### **Current State (50% Implementation)**

- SimpleDIContainer: Custom implementation
- Basic configuration: Environment variables only
- Mock repositories: No real persistence
- Service registration: Basic patterns

### **Target State (Sprints 1-5)**

- FlextContainer: Full flext-core integration
- Hierarchical configuration: Profile, environment, defaults
- Real repositories: SQLite/PostgreSQL persistence
- Service integration: FlexCore and FLEXT Service clients

## 🔗 Integration Points

### **Application Layer Integration**

- Provides repositories for application services
- Supplies external service clients
- Manages configuration for application logic

### **Domain Layer Integration**

- Implements repository interfaces defined in domain
- Provides infrastructure for domain services
- Handles persistence of domain entities

### **External Systems Integration**

- FlexCore service (port 8080) communication
- FLEXT Service (port 8081) communication
- File system and database access
- Third-party API integrations

## 🔗 Related Documentation

- [Application Layer](../application/README.md) - Orchestration services using infrastructure
- [Domain Layer](../domain/README.md) - Business logic independent of infrastructure
- [TODO.md](../../../docs/TODO.md) - Sprint 1-3 FlextContainer migration plan
- [Infrastructure Patterns](../../../docs/architecture/infrastructure.md) - Infrastructure design patterns

## 📋 Sprint Implementation Checklist

### **Sprint 1: FlextContainer Migration** (CRITICAL)

- [ ] Replace SimpleDIContainer with FlextContainer
- [ ] Migrate all service registrations to type-safe patterns
- [ ] Update dependency resolution throughout application
- [ ] Add comprehensive integration tests

### **Sprint 3: Advanced Configuration**

- [ ] Implement profile-based configuration
- [ ] Add hierarchical configuration loading
- [ ] Support for ~/.flx/config.YAML user configuration
- [ ] Environment-specific configuration inheritance

### **Sprint 5: Repository Implementation**

- [ ] Implement SQLite repositories for all entities
- [ ] Add database migration system
- [ ] Implement query patterns and optimizations
- [ ] Add comprehensive persistence testing

---

**Critical Next Steps**: FlextContainer migration in Sprint 1 (blocking other sprints)  
**Architecture Layer**: Infrastructure (Outermost layer - External system integration)  
**Dependencies**: External systems, databases, file system, network services

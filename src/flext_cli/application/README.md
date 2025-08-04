# Application Layer - Orchestration and Command Handling

**Module**: `src/flext_cli/application/`  
**Architecture Layer**: Application (Orchestration Layer)  
**Status**: 40% implemented - Basic handlers, CQRS patterns planned for Sprint 2-3  
**Sprint Alignment**: Critical enhancement target for Sprints 2-3

## 🎯 Module Overview

The application layer orchestrates business operations by coordinating between the domain layer and infrastructure. This layer implements use cases, command handlers, and application services that fulfill CLI operations while maintaining separation of concerns.

### **Key Responsibilities**

- **Use Case Implementation**: Business workflows and operations
- **Command Handling**: CLI command processing and validation
- **Application Services**: Cross-cutting application concerns
- **Transaction Management**: Coordinating operations across aggregates
- **Event Coordination**: Managing domain events and side effects

## 📁 Module Structure

```
src/flext_cli/application/
├── __init__.py           # Application layer exports and service registration
└── commands.py           # Command handlers and application services
```

## 🏗️ Architecture Patterns

### **Current Implementation (40% Complete)**

- ✅ **Basic Command Handlers**: Simple command processing
- ✅ **Application Services**: Basic service coordination
- ✅ **FlextResult Integration**: Railway-oriented error handling
- ⚠️ **Basic Structure**: Foundation laid, needs CQRS enhancement

### **Target Architecture (Sprint 2-3)**

- 🎯 **CQRS Pattern**: Command Query Responsibility Segregation
- 🎯 **Command Handlers**: Dedicated handlers for each operation
- 🎯 **Query Handlers**: Read-only operation handlers
- 🎯 **Event Handlers**: Domain event processing
- 🎯 **Application Services**: Enhanced coordination services

## 📊 Implementation Status

### ✅ **Currently Implemented**

#### **commands.py - Basic Command Handlers**

- **CLICommandHandler**: Basic command processing
- **ApplicationCommandService**: Simple service coordination
- **Error handling**: FlextResult pattern integration
- **Dependency injection**: Basic service resolution

### ⚠️ **Needs Enhancement (Sprint 2-3)**

#### **CQRS Pattern Implementation**

```python
# Current (Basic)
class CLICommandHandler:
    def handle_command(self, command_data: dict) -> FlextResult[Any]:
        # Basic processing

# Target (CQRS - Sprint 2-3)
from flext_core import FlextCommand, FlextCommandHandler, FlextQuery

class ExecuteCliCommand(FlextCommand):
    command_line: str
    session_id: str
    timeout: int = 30

class ExecuteCliCommandHandler(FlextCommandHandler[ExecuteCliCommand]):
    async def handle(self, command: ExecuteCliCommand) -> FlextResult[CLICommand]:
        # Dedicated command handling with proper validation
```

### ❌ **Missing Critical Components**

#### **Command/Query Separation (Sprint 2-3)**

- **Commands**: Write operations (create, update, delete)
- **Queries**: Read operations (list, get, search)
- **Handlers**: Dedicated handlers for each operation type

#### **Event-Driven Architecture (Sprint 2-3)**

- **Event Handlers**: Processing domain events
- **Event Coordination**: Managing event flows
- **Side Effect Management**: Handling operation consequences

## 🎯 Sprint Roadmap Alignment

### **Sprint 1: Foundation** (Current Status)

- ✅ Basic command handlers implemented
- ✅ Simple application services
- ✅ FlextResult error handling integration

### **Sprint 2-3: CQRS Implementation** (CRITICAL)

```python
# Command Side (Write Operations)
class CreatePipelineCommand(FlextCommand):
    name: str
    configuration: dict
    environment: str

class CreatePipelineHandler(FlextCommandHandler[CreatePipelineCommand]):
    async def handle(self, command: CreatePipelineCommand) -> FlextResult[Pipeline]:
        # 1. Validate command
        # 2. Create domain entity
        # 3. Persist via repository
        # 4. Publish domain events
        # 5. Return result

# Query Side (Read Operations)
class ListPipelinesQuery(FlextQuery):
    filter_status: Optional[str] = None
    limit: int = 50

class ListPipelinesHandler(FlextQueryHandler[ListPipelinesQuery]):
    async def handle(self, query: ListPipelinesQuery) -> FlextResult[List[Pipeline]]:
        # Optimized read operations
```

### **Sprint 3-4: Advanced Application Services**

```python
# Enhanced Application Services
class PipelineOrchestrationService:
    async def start_pipeline_workflow(
        self,
        pipeline_id: str
    ) -> FlextResult[WorkflowExecution]:
        # Complex multi-step operations
        # Event coordination
        # Transaction management
```

### **Sprint 5: Integration with Persistence**

```python
# Repository Integration
class ApplicationCommandHandler:
    def __init__(
        self,
        repository: CLICommandRepository,
        event_publisher: FlextEventPublisher
    ) -> None:
        self._repository = repository
        self._event_publisher = event_publisher

    async def handle(self, command: FlextCommand) -> FlextResult[Any]:
        # Full persistence integration
```

## 🔧 Development Guidelines

### **Adding New Command Handlers (Current Pattern)**

```python
# Basic pattern (current)
class NewCommandHandler:
    def __init__(self, service: DomainService) -> None:
        self._service = service

    def handle_command(self, data: dict) -> FlextResult[Any]:
        try:
            # Process command
            result = self._service.execute_operation(data)
            return FlextResult.ok(result)
        except Exception as e:
            return FlextResult.fail(f"Command failed: {e}")
```

### **Adding CQRS Handlers (Sprint 2-3 Target)**

```python
# CQRS pattern (target)
from flext_core import FlextCommand, FlextCommandHandler

class NewCommand(FlextCommand):
    # Command data fields
    operation_data: str
    session_id: str

class NewCommandHandler(FlextCommandHandler[NewCommand]):
    async def handle(self, command: NewCommand) -> FlextResult[Any]:
        # 1. Validate command
        validation = self.validate_command(command)
        if not validation.success:
            return validation

        # 2. Execute domain logic
        result = await self.execute_domain_operation(command)

        # 3. Publish events
        await self.publish_events(result)

        return result
```

### **Error Handling Patterns**

```python
# Consistent error handling
class ApplicationService:
    async def execute_operation(self, request: Any) -> FlextResult[Any]:
        try:
            # Validate request
            validation = self.validate_request(request)
            if not validation.success:
                return validation

            # Execute operation
            result = await self.perform_operation(request)

            return FlextResult.ok(result)

        except DomainException as e:
            return FlextResult.fail(f"Domain error: {e}")
        except InfrastructureException as e:
            return FlextResult.fail(f"Infrastructure error: {e}")
        except Exception as e:
            self.logger.exception("Unexpected error in application service")
            return FlextResult.fail(f"Unexpected error: {e}")
```

## 🧪 Testing Guidelines

### **Command Handler Testing**

```python
def test_command_handler():
    handler = ExecuteCliCommandHandler(mock_service)
    command = ExecuteCliCommand(command_line="echo test")

    result = await handler.handle(command)

    assert result.success
    assert isinstance(result.unwrap(), CLICommand)
```

### **Application Service Testing**

```python
def test_application_service():
    service = CLIApplicationService(mock_repository, mock_event_publisher)

    result = await service.coordinate_complex_operation(request)

    assert result.success
    mock_event_publisher.publish.assert_called_once()
```

### **Integration Testing**

```python
@pytest.mark.integration
async def test_end_to_end_command_flow():
    # Test complete flow from command to domain to persistence
    command = CreateEntityCommand(name="test")
    result = await command_bus.execute(command)

    assert result.success
    # Verify persistence
    entity = await repository.find_by_name("test")
    assert entity is not None
```

## 📈 Current vs Target Metrics

### **Current State (40% Implementation)**

- Basic command handlers: 3 implemented
- Application services: 2 basic services
- Error handling: FlextResult integration
- Test coverage: 75%

### **Target State (Sprint 2-3)**

- CQRS handlers: 15+ command/query handlers
- Event handlers: 8+ event processing handlers
- Application services: 5+ orchestration services
- Test coverage: 95%

## 🔗 Integration Points

### **Domain Layer Integration**

- Uses domain entities and value objects
- Coordinates domain services
- Manages domain events

### **Infrastructure Layer Integration**

- Dependency injection container
- Repository pattern usage
- External service integration

### **Presentation Layer Integration**

- CLI command processing
- Request/response handling
- Error message formatting

## 🔗 Related Documentation

- [Domain Layer](../domain/README.md) - Business logic and entities
- [Infrastructure Layer](../infrastructure/README.md) - External concerns
- [CQRS Documentation](../../../docs/architecture/cqrs.md) - Command/Query patterns
- [TODO.md](../../../docs/TODO.md) - Sprint 2-3 CQRS implementation plan

## 📋 Sprint Implementation Checklist

### **Sprint 2: CQRS Foundation**

- [ ] Implement FlextCommand base classes
- [ ] Create command handlers for core operations
- [ ] Add query handlers for read operations
- [ ] Implement command/query bus

### **Sprint 3: Event-Driven Architecture**

- [ ] Add event handlers for domain events
- [ ] Implement event coordination
- [ ] Add side effect management
- [ ] Enhance transaction management

---

**Critical Next Steps**: CQRS pattern implementation in Sprint 2-3  
**Architecture Layer**: Application (Orchestration between Domain and Infrastructure)  
**Dependencies**: Domain layer (entities, services), Infrastructure layer (repositories, external services)

# FLEXT CLI - Architecture Overview

**Document**: Comprehensive architectural design and implementation guide  
**Version: 0.9.0 (Updated 2025-08-01))  
**Status**: 30% implemented - See implementation status per component  
**Target\*\*: Enterprise-grade unified CLI for FLEXT ecosystem (33 projects)

## 🎯 **Architectural Vision**

### **Mission Statement**

Provide a unified, enterprise-grade command-line interface that serves as the primary operational tool for the entire FLEXT distributed data integration ecosystem, enabling seamless management, orchestration, and monitoring of 33 interconnected projects.

### **Core Principles**

1. **Unified Interface**: Single CLI for all FLEXT ecosystem operations
2. **Enterprise Patterns**: Full flext-core integration with CQRS, Domain Events, DI
3. **Service Integration**: Direct communication with distributed FLEXT services
4. **Extensibility**: Plugin architecture for project-specific functionality
5. **Observability**: Comprehensive logging, metrics, and monitoring
6. **Developer Experience**: Rich UI, intuitive commands, excellent UX

## 🏗️ **Target Architecture (Enterprise-Grade)**

### **Layered Architecture with flext-core Integration**

```
┌─────────────────────────────────────────────────────────────────────┐
│                     FLEXT CLI - Unified Interface                   │
│                        (Single Entry Point)                        │
├─────────────────────────────────────────────────────────────────────┤
│                      CLI Presentation Layer                        │
│  ┌─────────┬─────────┬─────────┬─────────┬─────────┬─────────────┐  │
│  │pipeline │service  │  data   │ plugin  │monitor  │   project   │  │
│  │   mgmt  │  orch   │  mgmt   │  mgmt   │  & obs  │  specific   │  │
│  │         │         │         │         │         │ (algar/gn)  │  │
│  └─────────┴─────────┴─────────┴─────────┴─────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                     Application Layer (CQRS)                       │
│  ┌───────────────┬─────────────────┬─────────────────────────────┐  │
│  │   Commands    │     Queries     │      Event Handlers        │  │
│  │ (Write Ops)   │   (Read Ops)    │   (Domain Events)          │  │
│  └───────────────┴─────────────────┴─────────────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                      Domain Layer (DDD)                            │
│  ┌───────────┬─────────────┬─────────────────┬─────────────────┐    │
│  │ Entities  │   Value     │  Domain Events  │  Business Rules │    │
│  │ (Aggreg)  │  Objects    │   (Publish)     │  (Validation)   │    │
│  └───────────┴─────────────┴─────────────────┴─────────────────┘    │
├─────────────────────────────────────────────────────────────────────┤
│                    Infrastructure Layer                            │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────────┐  │
│  │Repositories │External APIs│File System  │   Configuration     │  │
│  │(Persistence)│(HTTP Client)│(Local Cfg)  │  (Profiles/Env)     │  │
│  └─────────────┴─────────────┴─────────────┴─────────────────────┘  │
├─────────────────────────────────────────────────────────────────────┤
│                       flext-core Foundation                        │
│  ┌─────────────┬─────────────┬─────────────┬─────────────────────┐  │
│  │FlextResult  │FlextContainer│FlextEvents  │ FlextRepository     │  │
│  │(Railway)    │(DI + IoC)   │(Pub/Sub)    │ (Data Access)       │  │
│  └─────────────┴─────────────┴─────────────┴─────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                                 │
                   ┌─────────────┴─────────────┐
                   │      FLEXT Ecosystem      │
                   │     (33 Projects)        │
                   │                           │
           ┌───────┴────────┐        ┌────────┴────────┐
           │   FlexCore     │        │ FLEXT Service   │
           │   (Go:8080)    │        │ (Go/Py:8081)    │
           │ Runtime Engine │        │ Data Platform   │
           └────────────────┘        └─────────────────┘
                   │                           │
   ┌───────────────┼───────────────────────────┼─────────────────────┐
   │                                                                 │
┌──▼─────┐ ┌────────┐ ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐
│Singer  │ │  DBT   │ │Project  │ │   Web    │ │   API    │ │ Obs  │
│Ecosystem│ │Transform│ │Specific │ │Interface │ │ Services │ │&Qual │
│(15proj)│ │(4proj) │ │(2proj)  │ │(flext-web│ │(flext-api│ │(2prj)│
└────────┘ └────────┘ └─────────┘ └──────────┘ └──────────┘ └──────┘
```

## 📊 **Current Implementation Status**

### ✅ **Layer 1: Foundation (70% Complete)**

#### **flext-core Integration (60% Complete)**

```python
# ✅ IMPLEMENTED - Railway-Oriented Programming
from flext_core import FlextResult

def save_auth_token(token: str) -> FlextResult[None]:
    try:
        # Implementation
        return FlextResult.ok(None)
    except Exception as e:
        return FlextResult.fail(f"Failed: {e}")

# ✅ IMPLEMENTED - Domain Entities
from flext_core import FlextEntity

class CLICommand(FlextEntity):
    def validate_domain_rules(self) -> FlextResult[None]:
        # Proper domain validation

# ⚠️ PARTIAL - Configuration Management
from flext_core import FlextBaseSettings

class CLIConfig(FlextBaseSettings):  # Good foundation
    # Missing: Profile loading, hierarchical config

# ❌ MISSING - Dependency Injection
# Should use: from flext_core import FlextContainer
# Currently: Custom SimpleDIContainer

# ❌ MISSING - CQRS Pattern
# Should use: from flext_core import FlextCommand, FlextQuery

# ❌ MISSING - Domain Events
# Should use: from flext_core import FlextEvent, FlextEventPublisher
```

### ⚠️ **Layer 2: Domain (50% Complete)**

#### **Domain Entities (Good Implementation)**

- ✅ **CLICommand** (`src/flext_cli/domain/entities.py:77`): Command execution lifecycle
- ✅ **CLISession** (`src/flext_cli/domain/entities.py:248`): Session management
- ✅ **CLIPlugin** (`src/flext_cli/domain/entities.py:356`): Plugin lifecycle
- ✅ **CLIConfig** (`src/flext_cli/domain/entities.py:491`): Configuration value object

#### **Domain Services (Basic Implementation)**

- ⚠️ **CLICommandService** (`src/flext_cli/domain/cli_services.py:29`): Basic service
- ❌ **Missing**: FlextDomainService inheritance
- ❌ **Missing**: Proper service patterns

#### **Domain Events (Defined but Unused)**

```python
# ✅ DEFINED but ❌ NOT USED
class CommandStartedEvent(FlextValueObject):
    command_id: TEntityId
    # Events exist but no publisher/subscriber implementation
```

### ❌ **Layer 3: Application (30% Complete)**

#### **Command Handlers (Basic Implementation)**

- ⚠️ **Basic handlers** (`src/flext_cli/application/commands.py`): Simple implementation
- ❌ **Missing**: CQRS pattern implementation
- ❌ **Missing**: Command/Query separation
- ❌ **Missing**: Event-driven handlers

#### **Service Orchestration (Missing)**

- ❌ **Missing**: Service discovery
- ❌ **Missing**: Health check orchestration
- ❌ **Missing**: Inter-service communication

### ❌ **Layer 4: Infrastructure (40% Complete)**

#### **Dependency Injection (Custom Implementation)**

- ⚠️ **SimpleDIContainer** (`src/flext_cli/infrastructure/container.py:18`): Basic DI
- ❌ **Missing**: FlextContainer integration
- ❌ **Missing**: Type-safe dependency resolution

#### **External APIs (Basic Implementation)**

- ⚠️ **HTTP Client** (`src/flext_cli/client.py`): Exists but not integrated
- ❌ **Missing**: FlexCore service integration
- ❌ **Missing**: FLEXT Service integration

#### **Repositories (Mock Only)**

- ❌ **MockRepositories** (`src/flext_cli/infrastructure/container.py:129`): Mock only
- ❌ **Missing**: Real persistence implementation

### ❌ **Layer 5: Presentation (30% Complete)**

#### **CLI Commands (30% Implementation)**

- ✅ **Authentication** (`src/flext_cli/commands/auth.py`): Functional
- ✅ **Configuration** (`src/flext_cli/commands/config.py`): Functional
- ✅ **Debug** (`src/flext_cli/commands/debug.py`): Functional
- ❌ **Missing**: pipeline, service, data, plugin, monitor, project commands

## 🎯 **Target Implementation (Missing Components)**

### **Critical Missing Components**

#### **1. CQRS Implementation (Priority 1)**

```python
# Target Architecture
from flext_core import FlextCommand, FlextCommandHandler, FlextQuery

@dataclass
class StartPipelineCommand(FlextCommand):
    pipeline_name: str
    environment: str

class StartPipelineHandler(FlextCommandHandler[StartPipelineCommand]):
    async def handle(self, command: StartPipelineCommand) -> FlextResult[PipelineStatus]:
        # Implementation with proper error handling
```

#### **2. Service Integration (Priority 1)**

```python
# Target Integration with FlexCore & FLEXT Service
class FlextServiceManager:
    async def health_check_flexcore(self) -> FlextResult[ServiceHealth]:
        # Connect to FlexCore:8080

    async def health_check_flext_service(self) -> FlextResult[ServiceHealth]:
        # Connect to FLEXT Service:8081
```

#### **3. Domain Events (Priority 2)**

```python
# Target Event-Driven Architecture
from flext_core import FlextEventPublisher, FlextEventSubscriber

class CommandExecutionHandler:
    async def handle_command_started(self, event: CommandStartedEvent):
        # Event handling implementation
```

#### **4. Real Repositories (Priority 2)**

```python
# Target Data Persistence
from flext_core import FlextRepository

class SqliteCLICommandRepository(FlextRepository[CLICommand]):
    async def save(self, entity: CLICommand) -> FlextResult[CLICommand]:
        # Real persistence implementation
```

## 📋 **Implementation Roadmap**

### **Phase 1: Enterprise Foundation (Sprint 1-2)**

1. **FlextContainer Migration**: Replace SimpleDIContainer
2. **CQRS Implementation**: Command/Query separation
3. **Service Integration**: FlexCore and FLEXT Service connectivity

### **Phase 2: Core Functionality (Sprint 3-4)**

1. **Pipeline Commands**: Complete pipeline management
2. **Service Commands**: Service orchestration and health checks
3. **Domain Events**: Event-driven architecture

### **Phase 3: Data Platform (Sprint 5-6)**

1. **Data Commands**: Singer ecosystem management
2. **Plugin System**: Dynamic plugin loading
3. **Repository Implementation**: Real data persistence

### **Phase 4: Ecosystem Integration (Sprint 7-8)**

1. **Project Commands**: ALGAR, GrupoNos, Meltano integration
2. **Monitoring**: Observability and metrics
3. **Advanced UX**: Interactive mode, profiles

## 🔧 **Development Guidelines**

### **Adding New Commands**

1. **Follow CQRS**: Separate commands from queries
2. **Use flext-core**: FlextResult, FlextEntity, FlextContainer
3. **Implement Events**: Publish domain events for entity changes
4. **Add Tests**: Comprehensive unit and integration tests

### **Service Integration**

1. **Health Checks**: Implement for all external services
2. **Circuit Breakers**: Use for external service calls
3. **Retry Policies**: Handle transient failures gracefully
4. **Correlation IDs**: Track requests across services

### **Quality Standards**

1. **Test Coverage**: Maintain 90%+ coverage
2. **Type Safety**: Zero MyPy errors tolerated
3. **Documentation**: Document all public APIs
4. **Performance**: <1s response time for basic commands

## 🏗️ **Current Structure vs Target**

### **Current Implementation**

```
src/flext_cli/
├── domain/                    # ✅ GOOD: FlextEntity domain modeling
│   ├── entities.py           # ✅ CLICommand, CLISession, CLIPlugin entities
│   ├── cli_context.py        # ✅ Value objects with validation
│   └── cli_services.py       # ⚠️ BASIC: Services need FlextDomainService
├── application/               # ⚠️ INCOMPLETE: Missing CQRS implementation
│   └── commands.py           # ⚠️ Basic handlers, need proper command pattern
├── infrastructure/            # ⚠️ PARTIAL: Custom DI, need FlextContainer
│   ├── container.py          # ❌ SimpleDIContainer instead of FlextContainer
│   └── config.py             # ✅ Configuration management
├── commands/                  # ❌ CRITICAL GAP: Only 3 of 10+ groups
│   ├── auth.py              # ✅ Authentication (functional)
│   ├── config.py            # ✅ Configuration (functional)
│   ├── debug.py             # ✅ Debugging (functional)
│   │
│   └── [MISSING COMMANDS]    # ❌ See roadmap for missing commands
├── core/                      # ✅ GOOD: CLI utilities with FlextResult
│   ├── base.py              # ✅ CLIContext, handle_service_result
│   ├── decorators.py        # ✅ CLI decorators and patterns
│   └── formatters.py        # ✅ Output formatting utilities
└── utils/                     # ✅ GOOD: FlextBaseSettings integration
    ├── auth.py              # ✅ Authentication utilities
    ├── config.py            # ✅ Configuration with FlextBaseSettings
    └── output.py            # ✅ Rich console output
```

This architecture positions FLEXT CLI as the unified operational interface for the entire FLEXT ecosystem, providing enterprise-grade functionality with excellent developer experience.

## 📚 **Related Documentation**

- [TODO.md](../TODO.md) - Detailed implementation gaps and roadmap
- [roadmap.md](../roadmap.md) - Sprint-based development plan
- [integration/](../integration/) - FLEXT ecosystem integration guides
- [development/setup.md](../development/setup.md) - Development environment setup

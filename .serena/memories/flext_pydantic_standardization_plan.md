# FLEXT Pydantic Standardization Plan

## Current State Analysis

### ✅ Already Implemented (flext-core)
- **FlextConfig**: Comprehensive Pydantic Settings with singleton pattern, DI support, and Pydantic 2.11 features
- **FlextModels**: Complete DDD model hierarchy with Entity, Value, AggregateRoot, Command, Query patterns
- **FlextConstants**: Comprehensive constants with nested namespaces for all domains

### ✅ Partially Implemented (flext-cli)
- **FlextCliConfig**: Extends FlextConfig with CLI-specific fields
- **FlextCliModels**: Extends FlextModels with CLI-specific models
- **FlextCliConstants**: Extends FlextConstants with CLI-specific constants

## Standardization Requirements

### 1. Model Hierarchy Pattern
```python
# ✅ CORRECT Pattern - All projects must follow this
class ProjectModels(FlextModels):
    """Single unified models class for Project domain."""
    
    class ProjectEntity(FlextModels.Entity):
        """Project-specific entity extending FlextModels.Entity."""
        
    class ProjectValue(FlextModels.Value):
        """Project-specific value object extending FlextModels.Value."""
        
    class ProjectCommand(FlextModels.Command):
        """Project-specific command extending FlextModels.Command."""
```

### 2. Config Hierarchy Pattern
```python
# ✅ CORRECT Pattern - All projects must follow this
class ProjectConfig(FlextConfig):
    """Single unified config class for Project domain."""
    
    model_config = SettingsConfigDict(
        env_prefix="PROJECT_",
        case_sensitive=False,
        extra="ignore",
        # Pydantic 2.11 features
        validate_return=True,
        arbitrary_types_allowed=True,
        validate_default=True,
    )
    
    # Project-specific fields with defaults from ProjectConstants
    project_field: str = Field(default=ProjectConstants.Defaults.PROJECT_FIELD)
```

### 3. Constants Hierarchy Pattern
```python
# ✅ CORRECT Pattern - All projects must follow this
class ProjectConstants(FlextConstants):
    """Project constants extending FlextConstants."""
    
    class Defaults:
        """Project default values."""
        PROJECT_FIELD: Final[str] = "default_value"
        
    class Validation:
        """Project validation constants."""
        MIN_PROJECT_LENGTH: Final[int] = 1
```

## Implementation Plan

### Phase 1: Core Foundation (COMPLETED)
- ✅ FlextConfig with Pydantic 2.11 features
- ✅ FlextModels with DDD patterns
- ✅ FlextConstants with comprehensive namespaces

### Phase 2: CLI Standardization (COMPLETED)
- ✅ FlextCliConfig extends FlextConfig
- ✅ FlextCliModels extends FlextModels
- ✅ FlextCliConstants extends FlextConstants

### Phase 3: Ecosystem Standardization (IN PROGRESS)
- 🔄 Standardize all flext-* projects
- 🔄 Standardize all algar-* projects
- 🔄 Standardize all gruponos-* projects

## Key Principles

1. **Single Source of Truth**: All defaults come from Constants
2. **Inheritance Over Duplication**: Always extend base classes
3. **Pydantic 2.11 Features**: Use all advanced features
4. **DI Integration**: Config must support dependency injection
5. **Validation Only by Models**: No inline validation in services
6. **Optional Fields**: Only require fields when strictly necessary
7. **Good Defaults**: All fields must have sensible defaults

## Validation Rules

- ❌ FORBIDDEN: Direct Pydantic imports (use FlextModels)
- ❌ FORBIDDEN: Multiple classes per module (use nested classes)
- ❌ FORBIDDEN: Inline validation in services (use model validation)
- ❌ FORBIDDEN: Hardcoded defaults (use Constants)
- ✅ REQUIRED: Extend base classes (FlextConfig, FlextModels, FlextConstants)
- ✅ REQUIRED: Use Pydantic 2.11 features
- ✅ REQUIRED: Support DI and singleton patterns
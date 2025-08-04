# Configuration Layer - CLI Configuration Management

**Module**: `src/flext_cli/config/`  
**Architecture Layer**: Configuration (Cross-cutting Configuration Concerns)  
**Status**: 60% implemented - Basic configuration patterns, profile system planned for Sprint 3  
**Sprint Alignment**: Critical enhancement target for Sprint 3, user config for Sprint 4

## 🎯 Module Overview

The configuration layer provides comprehensive configuration management for FLEXT CLI, including environment-specific settings, user profiles, hierarchical configuration loading, and validation. This layer implements configuration patterns using Pydantic models with flext-core integration.

### **Key Responsibilities**

- **Configuration Models**: Pydantic-based settings with validation
- **Profile Management**: Environment and user-specific configuration profiles
- **Hierarchical Loading**: Configuration inheritance and override patterns
- **Environment Integration**: Environment variable handling and defaults
- **Validation**: Configuration validation with business rules

## 📁 Module Structure

```
src/flext_cli/config/
├── __init__.py           # Configuration layer exports and utilities
└── cli_config.py         # CLI configuration models and management
```

## 🏗️ Architecture Patterns

### **Current Implementation (60% Complete)**

- ✅ **Basic Configuration**: Pydantic models with environment integration
- ✅ **Settings Management**: Basic CLI settings and validation
- ✅ **Environment Variables**: Environment variable override support
- ⚠️ **Profile System**: Foundation laid, needs full implementation (Sprint 3)
- ❌ **User Configuration**: User-specific config files not implemented

### **Target Architecture (Sprint 3-4)**

- 🎯 **Profile Management**: Complete profile system with inheritance
- 🎯 **User Configuration**: ~/.flx/config.YAML user configuration
- 🎯 **Hierarchical Loading**: Command-line > Environment > Profile > Defaults
- 🎯 **Dynamic Configuration**: Runtime configuration updates and validation

## 📊 Implementation Status

### ✅ **Currently Implemented**

#### **cli_config.py - Configuration Models**

- **CLIConfig**: Basic CLI configuration with Pydantic validation
- **Environment integration**: Environment variable loading
- **Default values**: Sensible defaults for all configuration options
- **Validation**: Basic field validation and type checking

### ⚠️ **Needs Enhancement (Sprint 3)**

#### **Profile System Implementation**

```python
# Current (Basic Configuration)
class CLIConfig(BaseSettings):
    debug: bool = False
    output_format: str = "table"
    # Basic fields only

# Target (Profile System - Sprint 3)
class CLIProfileConfig(FlextBaseSettings):
    profile_name: str
    inherits_from: Optional[str] = None
    environment: str = "development"
    
    # Enhanced configuration with profile inheritance
    def load_with_inheritance(self) -> FlextResult[CLIConfig]:
        # Load profile with inheritance chain
```

#### **Hierarchical Configuration Loading**

```python
# Target implementation (Sprint 3)
class ConfigurationManager:
    def __init__(self) -> None:
        self._sources = [
            CommandLineConfigSource(),
            EnvironmentConfigSource(),
            ProfileConfigSource(),
            DefaultConfigSource()
        ]
    
    async def load_configuration(
        self, 
        profile: Optional[str] = None
    ) -> FlextResult[CLIConfig]:
        # Merge configurations from multiple sources
        # Priority: CLI args > Environment > Profile > Defaults
```

### ❌ **Missing Critical Components**

#### **User Configuration Directory (Sprint 4)**

```python
# Target implementation
class UserConfigManager:
    def __init__(self) -> None:
        self.config_dir = Path.home() / ".flx"
        self.profiles_dir = self.config_dir / "profiles"
    
    async def create_user_config(self) -> FlextResult[None]:
        # Create ~/.flx directory structure
        # Initialize default configuration files
        
    async def load_user_profile(self, profile_name: str) -> FlextResult[CLIConfig]:
        # Load from ~/.flx/profiles/{profile_name}.yaml
```

#### **Dynamic Configuration Updates (Sprint 4)**

```python
# Target implementation
class DynamicConfigManager:
    async def update_configuration(
        self, 
        updates: Dict[str, Any]
    ) -> FlextResult[CLIConfig]:
        # Runtime configuration updates
        # Validation and persistence
        # Event notification for configuration changes
```

## 🎯 Sprint Roadmap Alignment

### **Sprint 1-2: Foundation** (Current Status)

- ✅ Basic configuration models implemented
- ✅ Environment variable integration
- ✅ Pydantic validation patterns

### **Sprint 3: Profile System** (CRITICAL)

```python
# Profile inheritance system
class ProfileConfigLoader:
    async def load_profile_chain(
        self, 
        profile_name: str
    ) -> FlextResult[CLIConfig]:
        # Load profile with inheritance chain
        # development -> base -> defaults
        # production -> base -> defaults
        
        profile_chain = await self.resolve_inheritance_chain(profile_name)
        merged_config = await self.merge_profile_configs(profile_chain)
        
        return FlextResult.ok(merged_config)
```

### **Sprint 4: User Configuration**

```python
# User-specific configuration
class UserProfileManager:
    async def create_profile(
        self, 
        profile_name: str, 
        config: CLIConfig
    ) -> FlextResult[None]:
        # Create user profile in ~/.flx/profiles/
        # Validate configuration
        # Set up profile inheritance
        
    async def list_profiles(self) -> FlextResult[List[str]]:
        # List available user profiles
        # Include system and user profiles
```

### **Sprint 5: Advanced Configuration**

```python
# Advanced configuration features
class AdvancedConfigManager:
    async def validate_configuration_integrity(self) -> FlextResult[ValidationReport]:
        # Comprehensive configuration validation
        # Cross-reference validation
        # Security validation
        
    async def migrate_configuration(
        self, 
        from_version: str, 
        to_version: str
    ) -> FlextResult[MigrationReport]:
        # Configuration migration and upgrade
```

## 🔧 Development Guidelines

### **Adding New Configuration Fields**

```python
# Pattern for extending configuration
class CLIConfig(FlextBaseSettings):
    # Existing fields
    debug: bool = Field(default=False, description="Enable debug mode")
    
    # New fields with proper validation
    new_feature_enabled: bool = Field(
        default=False, 
        description="Enable new feature",
        validation_alias="NEW_FEATURE_ENABLED"
    )
    
    @field_validator('new_feature_enabled')
    @classmethod
    def validate_new_feature(cls, v: bool) -> bool:
        # Custom validation logic
        return v
```

### **Adding Configuration Sources**

```python
# Pattern for new configuration sources
class NewConfigSource:
    def __init__(self, source_name: str) -> None:
        self.source_name = source_name
    
    async def load_config(self) -> FlextResult[Dict[str, Any]]:
        try:
            # Load configuration from source
            config_data = await self.fetch_config_data()
            return FlextResult.ok(config_data)
        except Exception as e:
            return FlextResult.fail(f"Failed to load from {self.source_name}: {e}")
```

### **Profile Management Patterns**

```python
# Pattern for profile operations
class ProfileOperations:
    async def create_profile(
        self, 
        profile_name: str, 
        base_profile: Optional[str] = None
    ) -> FlextResult[CLIProfile]:
        # Validate profile name
        validation = self.validate_profile_name(profile_name)
        if not validation.success:
            return validation
        
        # Create profile with inheritance
        profile = CLIProfile(
            name=profile_name,
            inherits_from=base_profile,
            created_at=datetime.utcnow()
        )
        
        return await self.save_profile(profile)
```

## 🧪 Testing Guidelines

### **Configuration Loading Testing**

```python
def test_configuration_loading():
    # Test basic configuration loading
    config = CLIConfig()
    assert config.debug is False
    assert config.output_format == "table"

def test_environment_override():
    # Test environment variable override
    with patch.dict(os.environ, {'CLI_DEBUG': 'true'}):
        config = CLIConfig()
        assert config.debug is True
```

### **Profile System Testing**

```python
async def test_profile_inheritance():
    # Test profile inheritance chain
    manager = ProfileConfigLoader()
    
    # Create base profile
    base_profile = CLIProfile(name="base", debug=True)
    await manager.save_profile(base_profile)
    
    # Create derived profile
    dev_profile = CLIProfile(name="development", inherits_from="base")
    await manager.save_profile(dev_profile)
    
    # Load derived profile
    result = await manager.load_profile_chain("development")
    assert result.success
    
    config = result.unwrap()
    assert config.debug is True  # Inherited from base
```

### **Validation Testing**

```python
def test_configuration_validation():
    # Test invalid configuration
    with pytest.raises(ValidationError):
        CLIConfig(output_format="invalid_format")
    
    # Test valid configuration
    config = CLIConfig(
        debug=True,
        output_format="json",
        profile="development"
    )
    assert config.debug is True
```

## 📈 Configuration Sources Priority

### **Configuration Loading Order (Target - Sprint 3)**

1. **Command Line Arguments** (Highest Priority)
   - `--debug`, `--profile`, `--output` flags
   - Override all other sources

2. **Environment Variables**
   - `CLI_DEBUG`, `FLX_PROFILE`, `FLX_OUTPUT_FORMAT`
   - Override profile and defaults

3. **Profile Configuration**
   - `~/.flx/profiles/{profile_name}.yaml`
   - User-specific or system profiles

4. **Default Configuration** (Lowest Priority)
   - Built-in defaults in Pydantic models
   - Fallback when no other source provides value

### **Profile Inheritance Chain**

```yaml
# ~/.flx/profiles/production.yaml
inherits_from: base
environment: production
debug: false
log_level: warning

# ~/.flx/profiles/development.yaml  
inherits_from: base
environment: development
debug: true
log_level: debug

# ~/.flx/profiles/base.yaml
output_format: table
timeout: 30
max_retries: 3
```

## 🔗 Integration Points

### **CLI Commands Integration**

- Global options (`--profile`, `--debug`, `--output`) use configuration
- Command-specific configuration overrides
- Dynamic configuration updates from CLI operations

### **Application Layer Integration**

- Application services access configuration through dependency injection
- Configuration changes trigger application-level updates
- Service configuration validation and management

### **Infrastructure Layer Integration**

- External service configuration (API endpoints, timeouts)
- Database and persistence configuration
- Logging and monitoring configuration

## 🔗 Related Documentation

- [Infrastructure Layer](../infrastructure/README.md) - Configuration dependency injection
- [Core Layer](../core/README.md) - Configuration utilities and helpers
- [TODO.md](../../../docs/TODO.md) - Sprint 3-4 configuration enhancement plan
- [Pydantic Settings](https://docs.pydantic.dev/latest/concepts/pydantic_settings/) - Configuration model patterns

## 📋 Sprint Implementation Checklist

### **Sprint 3: Profile System** (HIGH PRIORITY)

- [ ] Implement profile inheritance system
- [ ] Add profile creation and management commands
- [ ] Create hierarchical configuration loading
- [ ] Add profile validation and error handling

### **Sprint 4: User Configuration** (HIGH PRIORITY)

- [ ] Implement ~/.flx directory structure creation
- [ ] Add user profile management (create, list, switch, delete)
- [ ] Create interactive profile setup wizard
- [ ] Add profile migration and upgrade system

### **Sprint 5: Advanced Features** (MEDIUM PRIORITY)

- [ ] Add configuration integrity validation
- [ ] Implement configuration change monitoring
- [ ] Add configuration backup and restore
- [ ] Create configuration documentation generation

---

**Current Limitation**: Basic configuration only - Profile system needed for Sprint 3  
**Architecture Layer**: Configuration (Cross-cutting configuration management)  
**Dependencies**: Pydantic settings, environment variables, file system access

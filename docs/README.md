# FLEXT CLI Documentation

This documentation provides comprehensive information about FLEXT CLI, a modern command-line interface built with Python 3.13+, Click, and Rich libraries for managing the entire FLEXT distributed data integration ecosystem.

## 📚 Documentation Structure

### 🏗️ [Architecture](architecture/)

- [Overview](architecture/overview.md) - Architecture overview and design principles
- [Clean Architecture](architecture/clean-architecture.md) - Clean Architecture implementation with DDD
- [Domain Model](architecture/domain-model.md) - Domain modeling and entity design
- [flext-core Integration](architecture/flext-core-integration.md) - flext-core pattern integration

### 🔧 [Development](development/)

- [Setup Guide](development/setup.md) - Development environment setup and requirements
- [Coding Standards](development/coding-standards.md) - Code standards and quality gates
- [Testing Guide](development/testing.md) - Testing strategies and coverage requirements
- [Contributing](development/contributing.md) - How to contribute to the project

### 📝 [API Reference](api/)

- [CLI Commands](api/commands.md) - Complete CLI commands reference
- [Domain Entities](api/entities.md) - Domain entities and business logic
- [Configuration](api/configuration.md) - Configuration system and profiles
- [Utilities](api/utilities.md) - Utility functions and helpers

### 🌟 [Examples](examples/)

- [Basic Usage](examples/basic-usage.md) - Basic CLI usage patterns
- [Advanced Patterns](examples/advanced-patterns.md) - Advanced usage and integration
- [Testing Examples](examples/testing.md) - Testing examples and best practices
- [Custom Commands](examples/custom-commands.md) - Creating custom commands

### 🔍 [Troubleshooting](troubleshooting/)

- [Common Issues](troubleshooting/common-issues.md) - Common issues and solutions
- [Debugging Guide](troubleshooting/debugging.md) - Debugging techniques and tools
- [Performance](troubleshooting/performance.md) - Performance analysis and optimization

### 🔗 [Integration](integration/)

- [FlexCore Integration](integration/flexcore.md) - FlexCore service integration (port 8080)
- [FLEXT Service Integration](integration/flext-service.md) - FLEXT service integration (port 8081)
- [Project Integrations](integration/projects.md) - Project-specific integrations (client-a, client-b, Meltano)

### 📋 [Roadmap](TODO.md)

- [Development Roadmap](TODO.md) - Comprehensive 10-sprint development plan
- Sprint-by-sprint implementation roadmap
- Success metrics and acceptance criteria
- Critical architectural gaps and solutions

## 🚀 Quick Start

### 1. Installation

See [Development Setup](development/setup.md) for complete installation instructions:

```bash
# Install dependencies with Poetry
poetry install --all-extras --with dev,test,docs,security

# Install CLI globally
make install-cli

# Verify installation
poetry run flext --version
```

### 2. First Steps

Check [Basic Usage](examples/basic-usage.md) for getting started:

```bash
# List available commands
poetry run flext --help

# Current functional commands (30% implementation)
poetry run flext auth --help        # Authentication commands
poetry run flext config --help      # Configuration management
poetry run flext debug --help       # Debug and diagnostic tools
```

### 3. Architecture Understanding

Read [Clean Architecture](architecture/clean-architecture.md) to understand:

- Domain-Driven Design (DDD) implementation
- Clean Architecture layers and separation
- flext-core integration patterns (60% complete)

### 4. Testing and Quality

Learn about [Testing Guide](development/testing.md):

- 90% test coverage requirement
- MyPy strict mode (zero errors tolerated)
- Quality gates with Ruff linting

## 🎯 Key Features

### ✅ **Currently Implemented (30% Complete)**

- **Clean Architecture**: Complete implementation with flext-core foundation
- **Rich Terminal UI**: Beautiful interface with Rich library (tables, progress bars, panels)
- **Type Safety**: Complete type coverage with MyPy strict mode
- **Quality Gates**: Rigorous validation with 90% test coverage
- **Core Commands**: Authentication, configuration, and debugging (3 of 10+ groups)

### 🚧 **In Development (70% Planned)**

- **Pipeline Management**: Data pipeline orchestration and monitoring
- **Service Integration**: FlexCore (8080) and FLEXT Service (8081) management
- **Plugin System**: Extensible plugin architecture
- **Project Integration**: client-a, client-b, and Meltano support
- **Interactive Mode**: REPL with tab completion and command history

## 📋 Technical Requirements

### **System Requirements**

- **Python 3.13+**: Modern Python with latest type hints and async support
- **Poetry**: For dependency management and packaging
- **flext-core**: Foundation library with enterprise patterns
- **Rich**: Terminal interface components
- **Click**: CLI framework with hierarchical commands

### **Development Requirements**

- **MyPy**: Strict type checking (zero errors tolerated)
- **Ruff**: Comprehensive linting (ALL rules enabled)
- **pytest**: Testing framework with 90% coverage requirement
- **Bandit + pip-audit**: Security scanning and vulnerability detection
- **pre-commit**: Automated quality enforcement

## 🏆 Quality Standards

### **Mandatory Quality Gates**

- **Zero Tolerance**: No lint violations or type errors
- **Test Coverage**: 90% minimum coverage enforced
- **Security**: Mandatory scanning with Bandit + pip-audit
- **Documentation**: Complete docstring standardization (251 status indicators)
- **Architecture**: Clean Architecture compliance with flext-core patterns

### **Code Standards**

- **English Only**: All code and documentation in English
- **Clean Architecture**: Strict layer separation (Domain → Application → Infrastructure)
- **Domain-Driven Design**: Rich domain entities with business logic
- **Type Safety**: Complete type coverage with MyPy strict mode
- **flext-core Integration**: Consistent use of FlextResult, FlextEntity, FlextValueObject

## 📊 Current Status & Roadmap

### **Implementation Status**

- **Architecture**: 70% - Solid foundations with comprehensive docstring alignment
- **Functionality**: 30% - Only 3 of 10+ command groups functional
- **flext-core Integration**: 60% - Basic patterns implemented, enterprise patterns missing
- **Documentation**: 95% - Complete docstring standardization with Sprint alignment

### **10-Sprint Development Plan**

See [Development Roadmap](TODO.md) for detailed sprint-by-sprint plan:

- **Sprint 1-2**: Pipeline management and service integration (CRITICAL)
- **Sprint 3-4**: CQRS implementation and modern interface
- **Sprint 5-6**: Data management and plugin system
- **Sprint 7-8**: Monitoring and interactive features
- **Sprint 9-10**: Project integration and advanced features

### **Success Metrics**

- **Sprint 2**: 40% functional (pipeline + service commands)
- **Sprint 6**: 75% functional (data management + plugins)
- **Sprint 10**: 100% functional (advanced features + production ready)

## 🔗 Important Links

### **Main Documentation**

- [Main README](../README.md) - Project overview and getting started
- [CLAUDE.md](../CLAUDE.md) - Development guidance for Claude Code
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Detailed architectural decisions

### **Development Resources**

- [Makefile](../Makefile) - Development commands and quality gates
- [TODO.md](TODO.md) - Comprehensive 10-sprint development roadmap
- [pyproject.toml](../pyproject.toml) - Project configuration and dependencies

### **Quality & Testing**

- Test coverage reports in `htmlcov/` and `reports/coverage/`
- Quality gates: `make validate` (lint + type-check + security + test)
- Pre-commit hooks for automated quality enforcement

### **FLEXT Ecosystem**

- **flext-core**: Foundation library with enterprise patterns
- **FlexCore**: Go runtime container service (port 8080)
- **FLEXT Service**: Go/Python data integration service (port 8081)
- **32+ Projects**: Complete FLEXT distributed data integration ecosystem

---

**Framework**: FLEXT CLI 0.9.0 | **Python**: 3.13+ | **Architecture**: Clean Architecture + DDD | **Updated**: 2025-08-01

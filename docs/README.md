# flext-cli Documentation

**Professional documentation for the FLEXT CLI foundation library.**

---

## 🚀 Version 0.10.0 Refactoring

> **📝 Status**: Documentation Phase (Implementation Pending)

v0.10.0 brings significant architecture simplification. **Review these documents first**:

### For Users Upgrading
- **[Refactoring Overview](refactoring/README.md)** - Start here for v0.10.0 overview
- **[Migration Guide](refactoring/MIGRATION_GUIDE_V0.9_TO_V0.10.md)** - Step-by-step migration (30-60 min)
- **[Breaking Changes](refactoring/BREAKING_CHANGES.md)** - Complete list of breaking changes
- **[Architecture Comparison](refactoring/ARCHITECTURE_COMPARISON.md)** - v0.9.0 vs v0.10.0 comparison

### For Contributors
- **[Refactoring Plan](refactoring/REFACTORING_PLAN_V0.10.0.md)** - Complete technical plan and rationale
- **[Implementation Checklist](refactoring/IMPLEMENTATION_CHECKLIST.md)** - Step-by-step implementation guide

**Key Changes**: Direct access pattern, services reduced from 18→3-4, 30-40% code reduction

---

## 📚 Core Documentation

### Getting Started
- **[Getting Started Guide](getting-started.md)** - Installation, setup, and quick start
- **[Examples](../examples/)** - Code examples and usage patterns

### Technical Documentation
- **[Architecture](architecture.md)** - Design patterns and structure (v0.10.0 updated)
- **[API Reference](api-reference.md)** - Complete API documentation (v0.10.0 updated)
- **[Development Guide](development.md)** - Contributing and development workflow

### Standards & Guidelines
- **[Pydantic v2 Standards](pydantic-v2-modernization/)** - Pydantic v2 migration documentation
- **[FLEXT Workspace Standards](../../CLAUDE.md)** - Workspace-level patterns

---

## 📊 Current Status (v0.9.0)

- **24 core modules** with comprehensive functionality
- **1,600+ tests** with 95%+ pass rate
- **~14,000 lines** of production code (will be ~10,000 in v0.10.0)
- **100% type safety** (Pyrefly strict mode)
- **Production ready** CLI foundation for 32+ FLEXT projects

---

## 🎯 Purpose

flext-cli serves as the **CLI foundation library** for the FLEXT ecosystem:

- **Click/Rich Abstraction** - ZERO TOLERANCE policy (only flext-cli imports Click/Rich)
- **Standardized CLI Patterns** - Consistent interfaces across 32+ projects
- **Railway-Oriented Programming** - FlextResult[T] error handling throughout
- **Plugin System** - Extensibility for ecosystem projects
- **Professional Output** - 22+ table formats, Rich terminal UI

---

## 🔗 Quick Links

### Documentation
- [Main README](../README.md) - Project overview
- [CHANGELOG](../CHANGELOG.md) - Version history and changes

### Community
- [GitHub Issues](https://github.com/flext/flext-cli/issues) - Report bugs
- [Discussions](https://github.com/flext/flext-cli/discussions) - Ask questions
- [Contributing](development.md) - Contribution guidelines

### Resources
- [Tests](../tests/) - Comprehensive test suite
- [Examples](../examples/) - Usage examples
- [FLEXT Ecosystem](../../) - Full ecosystem documentation

---

## 🔄 Version History

### v0.10.0 (Planned)
- Architecture simplification
- Direct access pattern
- 30-40% code reduction
- Services: 18 → 3-4
- See [Refactoring Plan](refactoring/REFACTORING_PLAN_V0.10.0.md)

### v0.9.0 (Current)
- Production-ready foundation
- Complete Click/Rich abstraction
- Comprehensive test coverage
- FLEXT ecosystem integration

---

## 📖 Reading Order

### New Users
1. [Getting Started](getting-started.md)
2. [API Reference](api-reference.md)
3. [Architecture](architecture.md)

### Contributors
1. [Development Guide](development.md)
2. [Architecture](architecture.md)
3. [Refactoring Plan](refactoring/REFACTORING_PLAN_V0.10.0.md)

### Upgrading from v0.9.0
1. [Migration Guide](refactoring/MIGRATION_GUIDE_V0.9_TO_V0.10.md)
2. [Breaking Changes](refactoring/BREAKING_CHANGES.md)
3. [Architecture Comparison](refactoring/ARCHITECTURE_COMPARISON.md)

---

**Documentation Version**: 2.0 (v0.10.0 Ready)
**Last Updated**: 2025-01-24
**Status**: ✅ Ready for Review
**Next**: Update architecture.md, api-reference.md, getting-started.md

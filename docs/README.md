# FLEXT CLI Documentation

Esta documentação fornece informações abrangentes sobre o FLEXT CLI, uma interface de linha de comando moderna construída com Python 3.13+, Click, e Rich.

## 📚 Estrutura da Documentação

### 🏗️ [Architecture](architecture/)
- [Overview](architecture/overview.md) - Visão geral da arquitetura
- [Clean Architecture](architecture/clean-architecture.md) - Implementação Clean Architecture
- [Domain Model](architecture/domain-model.md) - Modelagem de domínio
- [flext-core Integration](architecture/flext-core-integration.md) - Integração com flext-core

### 💻 [Development](development/)
- [Setup Guide](development/setup.md) - Configuração do ambiente de desenvolvimento
- [Coding Standards](development/coding-standards.md) - Padrões de código
- [Testing Guide](development/testing.md) - Guia de testes
- [Contributing](development/contributing.md) - Como contribuir

### 🔌 [API Reference](api/)
- [CLI Commands](api/commands.md) - Referência de comandos CLI
- [Domain Entities](api/entities.md) - Entidades de domínio
- [Configuration](api/configuration.md) - Sistema de configuração
- [Utilities](api/utilities.md) - Funções utilitárias

### 📖 [Examples](examples/)
- [Basic Usage](examples/basic-usage.md) - Uso básico
- [Advanced Patterns](examples/advanced-patterns.md) - Padrões avançados
- [Testing Examples](examples/testing.md) - Exemplos de testes
- [Custom Commands](examples/custom-commands.md) - Comandos customizados

### 🔧 [Troubleshooting](troubleshooting/)
- [Common Issues](troubleshooting/common-issues.md) - Problemas comuns
- [Debugging Guide](troubleshooting/debugging.md) - Guia de debug
- [Performance](troubleshooting/performance.md) - Análise de performance

## 🚀 Quick Start

1. **Installation**: Veja [Development Setup](development/setup.md)
2. **First Steps**: Consulte [Basic Usage](examples/basic-usage.md)
3. **Architecture**: Entenda a [Clean Architecture](architecture/clean-architecture.md)
4. **Testing**: Aprenda sobre [Testing Guide](development/testing.md)

## 🎯 Key Features

- **Clean Architecture**: Implementação completa com flext-core
- **Rich Terminal UI**: Interface rica com Rich library
- **Type Safety**: Cobertura completa de tipos com MyPy
- **Quality Gates**: Validação rigorosa com 90% de cobertura de testes
- **Project Integration**: Suporte para ALGAR, GrupoNos, e Meltano

## 📋 Requirements

- Python 3.13+
- Poetry para gerenciamento de dependências
- flext-core como biblioteca base
- Rich para interface terminal
- Click para framework CLI

## 🏆 Quality Standards

- **Zero Tolerance**: Sem violações de lint ou erros de tipo
- **Test Coverage**: 90% mínimo de cobertura
- **Security**: Scan obrigatório com Bandit + pip-audit
- **Documentation**: Documentação abrangente e atualizada

## 🔗 Links Importantes

- [Main README](../README.md) - Documentação principal
- [CLAUDE.md](../CLAUDE.md) - Guia para Claude Code
- [ARCHITECTURE.md](../ARCHITECTURE.md) - Decisões arquiteturais
- [Makefile](../Makefile) - Comandos de desenvolvimento

---

**Framework**: FLEXT 0.8.0 | **Python**: 3.13+ | **Architecture**: Clean + DDD | **Updated**: 2025-01-29
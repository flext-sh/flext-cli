# FLEXT CLI - Developer Command Line Interface

[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Poetry](https://img.shields.io/badge/poetry-1.8+-blue.svg)](https://python-poetry.org/)
[![Code Style: Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checking: MyPy](https://img.shields.io/badge/type%20checking-mypy-blue.svg)](https://mypy.readthedocs.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Regras do Projeto**: Consulte `../../.github/instructions/regras.instructions.md` para padrões obrigatórios
>
> **Padrão de documentação**: Veja [../../docs/HOW_TO_DOCUMENT.md](../../docs/HOW_TO_DOCUMENT.md)

## 🧭 Navegação

**🏠 Root**: [Documentação Principal](../../docs/index.md) → **📄 Projeto**: flext-cli

## Overview

FLEXT CLI é uma interface de linha de comando moderna construída com Python 3.13+, Click, e Rich. Utiliza padrões flext-core para modelagem de domínio e injeção de dependência, fornecendo comandos CLI para o ecossistema FLEXT incluindo gerenciamento de pipelines, autenticação, configuração e operações específicas de projetos.

## Features

- **🎨 Rich Terminal UI**: Powered by Rich library for beautiful terminal output with tables, progress bars, and panels
- **🏗️ Clean Architecture**: Domain-driven design with flext-core integration
- **🔧 Command Groups**: Hierarchical commands for auth, config, pipeline, plugin, and debug operations
- **📊 Multiple Output Formats**: JSON, YAML, Table, CSV, and Plain text support
- **🎯 Type Safety**: Complete type coverage with MyPy strict mode
- **🧪 Zero Tolerance Quality**: 90% test coverage requirement with comprehensive quality gates
- **🚀 Project Integration**: Support for client-a, client-b, and Meltano projects

## Architecture

### Clean Architecture com flext-core

```
src/flext_cli/
├── domain/              # Entidades de domínio (CLICommand, CLIConfig, CLISession, CLIPlugin)
├── application/         # Camada de aplicação com handlers de comando
├── infrastructure/      # Container DI e configuração
├── commands/           # Implementações de comandos CLI
│   ├── auth.py         # Comandos de autenticação
│   ├── config.py       # Comandos de configuração
│   ├── debug.py        # Ferramentas de debug
│   ├── pipeline.py     # Gerenciamento de pipelines
│   ├── plugin.py       # Gerenciamento de plugins
│   └── projects/       # Comandos específicos de projetos
├── core/               # Utilitários e padrões CLI
└── utils/              # Utilitários de configuração e output
```

## Installation

```bash
# Install dependencies with Poetry
cd /home/marlonsc/flext/flext-cli
poetry install --all-extras --with dev,test,docs,security

# Install CLI globally 
make install-cli

# Verify installation
poetry run flext --version
```

## Development Commands

### Quality Gates (Obrigatórios)

```bash
# Validação completa (executar antes de commits)
make validate                 # lint + type-check + security + test (90% coverage)

# Verificações essenciais
make check                   # lint + type-check + test

# Verificações individuais
make lint                    # Ruff linting (ALL rules enabled)
make type-check              # MyPy strict mode (zero errors tolerated)
make test                    # pytest with 90% coverage requirement
make security                # Bandit + pip-audit + secrets scan
```

### Development Setup

```bash
# Complete setup
make setup                   # Complete setup with pre-commit hooks
make install                 # Install dependencies with Poetry
make dev-install             # Development mode with all extras

# CLI operations
make install-cli             # Install CLI globally
make test-cli                # Test CLI commands
make cli-smoke-test          # Run smoke tests
```

## Quick Start

```bash
# List available commands
poetry run flext --help

# View command groups
poetry run flext auth --help
poetry run flext config --help
poetry run flext pipeline --help
poetry run flext plugin --help
poetry run flext debug --help

# Project-specific commands
poetry run flext client-a --help
poetry run flext client-b --help
poetry run flext meltano --help

# Interactive mode (future)
poetry run flext interactive
```

## Command Structure

```
flext
├── auth                   # Authentication commands
├── config                 # Configuration management
├── pipeline               # Pipeline operations
├── plugin                 # Plugin management
├── debug                  # Debug and diagnostic tools
├── client-a                  # client-a project commands
├── client-b               # client-b project commands
├── meltano                # Meltano integration commands
├── interactive            # Interactive mode (placeholder)
└── version                # Version information
```

## Configuration

### Global CLI Options

```bash
# Profile support
flext --profile development command
flext --profile production command

# Output formats
flext --output json command
flext --output table command  # default
flext --output yaml command
flext --output csv command

# Debug mode
flext --debug command
flext --quiet command
```

### Environment Variables

```bash
# CLI Configuration
export FLEXT_CLI_DEV_MODE=true
export FLEXT_CLI_LOG_LEVEL=debug
export FLEXT_CLI_CONFIG_PATH=/path/to/config.yaml

# Profile and output
export FLX_PROFILE=development
export FLX_DEBUG=true
```

### Configuration Files

- Project config: `config/dev.yaml`, `config/prod.yaml`
- User config: `~/.flx/config.yaml` (future implementation)
- Environment variables override file settings

## Testing

### Domain Entity Testing

```python
from flext_cli.domain.entities import CLICommand, CommandStatus, CommandType

def test_command_lifecycle():
    command = CLICommand(
        name="test",
        command_line="echo hello",
        command_type=CommandType.SYSTEM
    )
    
    # Test execution lifecycle
    command.start_execution()
    assert command.command_status == CommandStatus.RUNNING
    
    command.complete_execution(exit_code=0, stdout="hello")
    assert command.is_successful
```

### CLI Command Testing

```python
from click.testing import CliRunner
from flext_cli.cli import cli

def test_cli_commands():
    runner = CliRunner()
    
    # Test main CLI
    result = runner.invoke(cli, ['--version'])
    assert result.exit_code == 0
    
    # Test command groups
    result = runner.invoke(cli, ['auth', '--help'])
    assert result.exit_code == 0
```

### Running Tests

```bash
# Full test suite with coverage
make test

# Test specific modules
pytest tests/test_domain.py -v
pytest tests/test_commands.py -v

# Integration tests
pytest tests/test_integration.py -v
```

## Dependencies

### Core Dependencies

- **flext-core**: Foundation library with shared patterns
- **flext-observability**: Monitoring and metrics
- **Click 8.2+**: CLI framework
- **Rich 14.0+**: Terminal UI components
- **Pydantic 2.11+**: Data validation and settings

### Project-Specific Dependencies

- **client-a-oud-mig**: client-a project integration
- **client-b-meltano-native**: client-b project integration
- **flext-meltano**: Meltano orchestration

## Development Workflow

### Adding New Commands

1. Create command module in `commands/` or `commands/projects/`
2. Use Click decorators with Rich output formatting
3. Register command in `cli.py` main group
4. Add comprehensive tests with CliRunner
5. Run `make validate` before committing

### Example New Command

```python
# commands/new_feature.py
import click
from rich.console import Console

@click.group()
def new_feature():
    """New feature commands."""
    pass

@new_feature.command()
@click.pass_context
def action(ctx: click.Context) -> None:
    """Perform new feature action."""
    console: Console = ctx.obj["console"]
    console.print("[green]Success![/green]")

# Register in cli.py
from flext_cli.commands import new_feature
cli.add_command(new_feature.new_feature)
```

## Quality Standards

### Mandatory Requirements

- **Zero lint violations**: Ruff with ALL rules enabled
- **Zero type errors**: MyPy strict mode (no `Any` types)
- **90% test coverage**: Enforced by pytest-cov
- **Security scanning**: Bandit + pip-audit clean
- **Pre-commit hooks**: Automatic quality enforcement

### Code Style

- **Python 3.13+**: Modern syntax and type hints
- **Clean Architecture**: Strict layer separation
- **Domain-Driven Design**: Rich domain entities
- **Type Safety**: Complete type coverage with MyPy

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Clean and reinstall dependencies
   rm -rf .venv && poetry install --all-extras
   ```

2. **Type Check Failures**
   ```bash
   # Run MyPy with specific paths
   poetry run mypy src/flext_cli --show-error-codes
   ```

3. **Test Failures**
   ```bash
   # Run tests with verbose output
   poetry run pytest tests/ -v -s
   ```

### Getting Help

```bash
# General help
poetry run flext --help

# Command group help
poetry run flext auth --help
poetry run flext config --help

# View project structure
ls -la src/flext_cli/
```

## Project Status

- ✅ **Architecture**: Clean Architecture com flext-core implementado
- ✅ **Commands**: Grupos de comandos principais implementados
- ✅ **Quality Gates**: Makefile com validação completa
- ✅ **Testing**: Estrutura de testes com pytest
- 🔄 **Interactive Mode**: Em desenvolvimento
- 🔄 **Documentation**: Docs/ em criação

## Contributing

1. Fork o projeto
2. Crie uma branch para feature (`git checkout -b feature/amazing-feature`)
3. Execute `make validate` antes de commit
4. Commit suas mudanças (`git commit -m 'Add amazing feature'`)
5. Push para a branch (`git push origin feature/amazing-feature`)
6. Abra um Pull Request

## License

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 🔗 Cross-References

### Prerequisites

- [../../docs/HOW_TO_DOCUMENT.md](../../docs/HOW_TO_DOCUMENT.md) — Guia de padronização de documentação
- [../../.github/instructions/regras.instructions.md](../../.github/instructions/regras.instructions.md) — Regras obrigatórias do projeto

### Architecture Documentation

- [CLAUDE.md](CLAUDE.md) — Claude Code guidance for development
- [ARCHITECTURE.md](ARCHITECTURE.md) — Detailed architectural decisions
- [docs/](docs/) — Comprehensive project documentation

### Related Projects

- [../../flext-core/](../../flext-core/) — Core foundation library
- [../../flext-observability/](../../flext-observability/) — Monitoring and metrics
- [../../flext-meltano/](../../flext-meltano/) — Meltano orchestration

---

**📂 Projeto**: flext-cli | **🏠 Root**: [Documentação Principal](../../docs/index.md) | **Framework**: FLEXT 0.8.0 | **Updated**: 2025-01-29

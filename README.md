# FLX CLI - Developer Command Line Interface

> **Regras do Projeto**: Consulte `../../.github/instructions/regras.instructions.md` para padrões obrigatórios
>
> **Padrão de documentação**: Veja [../../docs/HOW_TO_DOCUMENT.md](../../docs/HOW_TO_DOCUMENT.md)

## 🧭 Navegação

**🏠 Root**: [Documentação Principal](../../docs/index.md) → **📄 Projeto**: flext-cli

## Overview

FLX CLI provides a powerful command-line interface for developers and operators to interact with the FLX platform. Built with Click, it offers intuitive commands, interactive prompts, real-time feedback, and comprehensive debugging capabilities.

## Features

- **Rich Interactive UI**: Powered by Rich library for beautiful terminal output
- **Command Structure**: Hierarchical commands with auto-completion
- **Real-time Streaming**: Live logs and progress updates
- **Configuration Management**: Easy config handling with validation
- **Plugin Integration**: Manage plugins from the terminal
- **Debug Mode**: Comprehensive debugging with --debug flag
- **Output Formats**: JSON, YAML, Table, CSV exports

## Installation

```bash
# Install FLX CLI
pip install flx-cli

# Or install from source
cd /home/marlonsc/pyauto/flx-cli
poetry install

# Verify installation
flx --version
```

## Quick Start

```bash
# Initialize FLX configuration
flx init

# List available commands
flx --help

# Run a pipeline
flx pipeline run my-pipeline --debug

# Watch pipeline logs
flx pipeline logs my-pipeline --follow

# Manage plugins
flx plugin list
flx plugin install tap-github
```

## Command Structure

```
flx
├── init                    # Initialize FLX configuration
├── config                  # Configuration management
│   ├── get                # Get config values
│   ├── set                # Set config values
│   └── validate           # Validate configuration
├── pipeline               # Pipeline operations
│   ├── list              # List pipelines
│   ├── create            # Create new pipeline
│   ├── run               # Execute pipeline
│   ├── status            # Check pipeline status
│   ├── logs              # View pipeline logs
│   └── delete            # Delete pipeline
├── plugin                 # Plugin management
│   ├── list              # List installed plugins
│   ├── search            # Search plugin registry
│   ├── install           # Install plugin
│   ├── update            # Update plugin
│   └── remove            # Remove plugin
├── auth                   # Authentication
│   ├── login             # Login to FLX
│   ├── logout            # Logout from FLX
│   └── status            # Check auth status
└── debug                  # Debugging tools
    ├── connectivity      # Test connections
    ├── performance       # Performance analysis
    └── validate          # Validate setup
```

## Configuration

FLX CLI uses a hierarchical configuration system:

```yaml
# ~/.flx/config.yaml
default:
  api_url: https://api.flx-platform.com
  timeout: 30
  output_format: table

profiles:
  development:
    api_url: http://localhost:8000
    debug: true

  production:
    api_url: https://api.flx-platform.com
    verify_ssl: true
```

## Environment Variables

```bash
# API Configuration
export FLX_API_URL=http://localhost:8000
export FLX_API_TOKEN=your-api-token

# CLI Behavior
export FLX_OUTPUT_FORMAT=json
export FLX_DEBUG=true
export FLX_NO_COLOR=false

# Profile Selection
export FLX_PROFILE=development
```

## Interactive Mode

```bash
# Start interactive mode
flx interactive

# Or use shortcuts
flx i
```

In interactive mode:

- Tab completion for commands
- Command history with up/down arrows
- Rich formatting and syntax highlighting
- Context-aware suggestions

## Pipeline Management

### Creating Pipelines

```bash
# Interactive pipeline creation
flx pipeline create

# From file
flx pipeline create --from-file pipeline.yaml

# With inline config
flx pipeline create my-pipeline \
  --tap tap-github \
  --target target-postgres \
  --transform dbt
```

### Running Pipelines

```bash
# Run pipeline
flx pipeline run my-pipeline

# Run with state override
flx pipeline run my-pipeline --full-refresh

# Run with custom config
flx pipeline run my-pipeline --config config.json

# Dry run
flx pipeline run my-pipeline --dry-run
```

### Monitoring Pipelines

```bash
# Check status
flx pipeline status my-pipeline

# Follow logs
flx pipeline logs my-pipeline --follow

# Get execution history
flx pipeline history my-pipeline --limit 10
```

## Plugin Management

### Installing Plugins

```bash
# Install from registry
flx plugin install tap-github

# Install from Git
flx plugin install git+https://github.com/org/tap-custom.git

# Install from local path
flx plugin install ./my-local-plugin

# Install specific version
flx plugin install tap-github==1.2.3
```

### Managing Plugins

```bash
# List all plugins
flx plugin list

# Show plugin details
flx plugin show tap-github

# Update plugin
flx plugin update tap-github

# Remove plugin
flx plugin remove tap-github
```

## Output Formats

```bash
# Table format (default)
flx pipeline list

# JSON format
flx pipeline list --output json

# YAML format
flx pipeline list --output yaml

# CSV format
flx pipeline list --output csv

# Plain text
flx pipeline list --output plain
```

## Advanced Features

### Command Aliases

```bash
# Create aliases in ~/.flx/aliases
pl = pipeline list
pr = pipeline run
ps = pipeline status
```

### Shell Completion

```bash
# Bash
eval "$(_FLX_COMPLETE=source_bash flx)"

# Zsh
eval "$(_FLX_COMPLETE=source_zsh flx)"

# Fish
eval (env _FLX_COMPLETE=source_fish flx)
```

### Scripting Support

```python
# Use FLX CLI from Python
from flx_cli import FlxCLI

cli = FlxCLI()
result = cli.invoke(['pipeline', 'list'])
print(result.output)
```

## Debug Mode

```bash
# Enable debug mode globally
export FLX_DEBUG=true

# Or per command
flx pipeline run my-pipeline --debug

# Debug with trace
flx pipeline run my-pipeline --debug --trace
```

Debug output includes:

- API request/response details
- Configuration resolution
- Plugin loading information
- Performance metrics
- Stack traces on errors

## Error Handling

FLX CLI provides clear error messages:

```bash
$ flx pipeline run non-existent
Error: Pipeline 'non-existent' not found

Suggestions:
- Check pipeline name with: flx pipeline list
- Create pipeline with: flx pipeline create

For more help: flx pipeline run --help
```

## Best Practices

1. **Use Profiles**: Separate dev/staging/prod configurations
2. **Enable Debug**: Use --debug for troubleshooting
3. **Check Status**: Always verify with status commands
4. **Use Dry Run**: Test commands with --dry-run
5. **Set Timeouts**: Configure appropriate timeouts
6. **Log Levels**: Use appropriate verbosity

## Extending FLX CLI

### Custom Commands

```python
# my_command.py
import click
from flx_cli import cli

@cli.command()
@click.option('--name', required=True)
def mycommand(name):
    """My custom command."""
    click.echo(f"Hello {name}!")
```

### Plugin Commands

Plugins can register CLI commands:

```python
# In plugin setup.py
entry_points={
    'flx.cli': [
        'my-plugin = my_plugin.cli:commands',
    ],
}
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**

   ```bash
   flx auth login
   flx auth status
   ```

2. **Connection Issues**

   ```bash
   flx debug connectivity
   ```

3. **Performance Problems**

   ```bash
   flx debug performance
   ```

### Getting Help

```bash
# General help
flx --help

# Command help
flx pipeline run --help

# Online documentation
flx docs

# Report issues
flx feedback
```

## Roadmap

- [ ] Interactive pipeline builder
- [ ] Terminal UI (TUI) mode
- [ ] Plugin development tools
- [ ] Performance profiling
- [ ] Offline mode support
- [ ] Multi-profile execution

## Contributing

See CONTRIBUTING.md for development setup and guidelines.

## License

Part of the FLX Platform - See LICENSE file.

## 🔗 Cross-References

### Prerequisites

- [../../docs/HOW_TO_DOCUMENT.md](../../docs/HOW_TO_DOCUMENT.md) — Guia de padronização de documentação
- [../../.github/instructions/regras.instructions.regras.instructions.md](../../.github/instructions/regras.instructions.md) — Regras obrigatórias do projeto

### Next Steps

- [../../docs/architecture/index.md](../../docs/architecture/index.md) — Detalhes da arquitetura
- [../../docs/development/index.md](../../docs/development/index.md) — Padrões de desenvolvimento

### Related Topics

- [../../docs/STANDARDIZATION_MASTER_PLAN.md](../../docs/STANDARDIZATION_MASTER_PLAN.md) — Estratégia de padronização
- [../../docs/INCOMPLETE_CODE_REPORT.md](../../docs/INCOMPLETE_CODE_REPORT.md) — Relatório de código incompleto

---

**📂 Projeto**: flext-cli | **🏠 Root**: [Documentação Principal](../../docs/index.md) | **Framework**: FLEXT 0.6.0+ | **Updated**: 2025-07-08

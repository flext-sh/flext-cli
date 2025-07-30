# CLI Commands Reference

Esta página documenta todos os comandos disponíveis no FLEXT CLI, suas opções e exemplos de uso.

## Global Options

Todas as opções globais estão disponíveis para todos os comandos:

```bash
flext [GLOBAL_OPTIONS] COMMAND [COMMAND_OPTIONS]
```

### Global Options

| Option      | Short | Type     | Default   | Description                                   |
| ----------- | ----- | -------- | --------- | --------------------------------------------- |
| `--profile` |       | `str`    | `default` | Configuration profile to use                  |
| `--output`  | `-o`  | `choice` | `table`   | Output format (table, JSON, YAML, csv, plain) |
| `--debug`   |       | `flag`   | `false`   | Enable debug mode                             |
| `--quiet`   | `-q`  | `flag`   | `false`   | Suppress non-error output                     |
| `--help`    | `-h`  | `flag`   |           | Show help message                             |
| `--version` |       | `flag`   |           | Show version information                      |

### Examples

```bash
# Using global options
flext --profile development --output json auth status
flext --debug pipeline list
flext --quiet --output csv pipeline export
```

## Command Groups

### 🔐 auth - Authentication Commands

Manage authentication and authorization.

```bash
flext auth SUBCOMMAND [OPTIONS]
```

#### Subcommands

| Command  | Description                 | Status     |
| -------- | --------------------------- | ---------- |
| `login`  | Login to FLEXT platform     | 🔄 Planned |
| `logout` | Logout from FLEXT platform  | 🔄 Planned |
| `status` | Check authentication status | 🔄 Planned |
| `token`  | Manage API tokens           | 🔄 Planned |

#### Examples

```bash
# Check authentication status
flext auth status

# Login with interactive prompt
flext auth login

# Login with token
flext auth login --token YOUR_TOKEN

# Logout
flext auth logout
```

### ⚙️ config - Configuration Management

Manage CLI configuration and settings.

```bash
flext config SUBCOMMAND [OPTIONS]
```

#### Subcommands

| Command    | Description                     | Status         |
| ---------- | ------------------------------- | -------------- |
| `show`     | Display current configuration   | ✅ Implemented |
| `set`      | Set configuration value         | 🔄 Planned     |
| `get`      | Get configuration value         | 🔄 Planned     |
| `validate` | Validate configuration          | 🔄 Planned     |
| `reset`    | Reset configuration to defaults | 🔄 Planned     |

#### Examples

```bash
# Show current configuration
flext config show

# Show configuration in JSON format
flext --output json config show

# Set configuration value (planned)
flext config set api_url http://localhost:8080

# Get specific configuration value (planned)
flext config get api_url

# Validate configuration (planned)
flext config validate
```

### 🚀 pipeline - Pipeline Management

Manage data pipelines and ETL operations.

```bash
flext pipeline SUBCOMMAND [OPTIONS]
```

#### Subcommands

| Command  | Description              | Status         |
| -------- | ------------------------ | -------------- |
| `list`   | List available pipelines | ✅ Implemented |
| `create` | Create new pipeline      | 🔄 Planned     |
| `run`    | Execute pipeline         | 🔄 Planned     |
| `status` | Check pipeline status    | 🔄 Planned     |
| `logs`   | View pipeline logs       | 🔄 Planned     |
| `stop`   | Stop running pipeline    | 🔄 Planned     |
| `delete` | Delete pipeline          | 🔄 Planned     |

#### Examples

```bash
# List all pipelines
flext pipeline list

# List pipelines in JSON format
flext --output json pipeline list

# Create new pipeline (planned)
flext pipeline create my-pipeline --tap tap-github --target target-postgres

# Run pipeline (planned)
flext pipeline run my-pipeline

# Check pipeline status (planned)
flext pipeline status my-pipeline

# Follow pipeline logs (planned)
flext pipeline logs my-pipeline --follow
```

### 🔌 plugin - Plugin Management

Manage CLI plugins and extensions.

```bash
flext plugin SUBCOMMAND [OPTIONS]
```

#### Subcommands

| Command   | Description             | Status         |
| --------- | ----------------------- | -------------- |
| `list`    | List installed plugins  | ✅ Implemented |
| `search`  | Search plugin registry  | 🔄 Planned     |
| `install` | Install plugin          | 🔄 Planned     |
| `update`  | Update plugin           | 🔄 Planned     |
| `remove`  | Remove plugin           | 🔄 Planned     |
| `info`    | Show plugin information | 🔄 Planned     |

#### Examples

```bash
# List installed plugins
flext plugin list

# Search for plugins (planned)
flext plugin search tap-

# Install plugin (planned)
flext plugin install tap-github

# Update all plugins (planned)
flext plugin update --all

# Remove plugin (planned)
flext plugin remove tap-github
```

### 🐛 debug - Debug and Diagnostic Tools

Debug CLI operations and diagnose issues.

```bash
flext debug SUBCOMMAND [OPTIONS]
```

#### Subcommands

| Command        | Description               | Status         |
| -------------- | ------------------------- | -------------- |
| `info`         | Show system information   | ✅ Implemented |
| `connectivity` | Test network connectivity | 🔄 Planned     |
| `performance`  | Performance analysis      | 🔄 Planned     |
| `validate`     | Validate CLI setup        | 🔄 Planned     |
| `logs`         | Show debug logs           | 🔄 Planned     |

#### Examples

```bash
# Show system information
flext debug info

# Test connectivity (planned)
flext debug connectivity --endpoint http://localhost:8080

# Run performance analysis (planned)
flext debug performance --command "pipeline list"

# Validate CLI setup (planned)
flext debug validate
```

## Project-Specific Commands

### 🏢 client-a - client-a Project Commands

Commands specific to client-a project operations.

```bash
flext client-a SUBCOMMAND [OPTIONS]
```

#### Subcommands

| Command    | Description              | Status         |
| ---------- | ------------------------ | -------------- |
| `migrate`  | Run client-a OUD migration  | ✅ Implemented |
| `status`   | Check migration status   | ✅ Implemented |
| `validate` | Validate migration setup | ✅ Implemented |

#### Examples

```bash
# Run client-a migration
flext client-a migrate

# Check migration status
flext client-a status

# Validate migration setup
flext client-a validate
```

### 🏭 client-b - client-b Project Commands

Commands specific to client-b project operations.

```bash
flext client-b SUBCOMMAND [OPTIONS]
```

#### Subcommands

| Command  | Description              | Status         |
| -------- | ------------------------ | -------------- |
| `deploy` | Deploy client-b services | ✅ Implemented |
| `status` | Check deployment status  | ✅ Implemented |
| `logs`   | View service logs        | ✅ Implemented |

#### Examples

```bash
# Deploy client-b services
flext client-b deploy

# Check deployment status
flext client-b status

# View service logs
flext client-b logs --service api
```

### 🎭 meltano - Meltano Integration Commands

Commands for Meltano orchestration and management.

```bash
flext meltano SUBCOMMAND [OPTIONS]
```

#### Subcommands

| Command   | Description               | Status         |
| --------- | ------------------------- | -------------- |
| `run`     | Run Meltano command       | ✅ Implemented |
| `install` | Install Meltano plugins   | ✅ Implemented |
| `invoke`  | Invoke Meltano operations | ✅ Implemented |

#### Examples

```bash
# Run Meltano command
flext meltano run tap-github target-postgres

# Install Meltano plugin
flext meltano install extractor tap-github

# Invoke Meltano operation
flext meltano invoke tap-github --discover
```

## Utility Commands

### 📋 version - Version Information

Display version information.

```bash
flext version [OPTIONS]
```

#### Options

| Option       | Description                       |
| ------------ | --------------------------------- |
| `--detailed` | Show detailed version information |

#### Examples

```bash
# Show version
flext version

# Show detailed version information
flext version --detailed
flext --debug version
```

### 🎮 interactive - Interactive Mode

Start interactive CLI mode (future implementation).

```bash
flext interactive [OPTIONS]
```

#### Examples

```bash
# Start interactive mode
flext interactive

# Interactive mode with debug
flext --debug interactive
```

## Output Formats

All commands support multiple output formats via the global `--output` option:

### Table Format (Default)

```bash
flext pipeline list
```

Output:

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                          Pipeline Status                                                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Name                    │ Status      │ Last Run                    │ Duration                                                     │
├─────────────────────────┼─────────────┼─────────────────────────────┼──────────────────────────────────────────────────────────┤
│ data-extraction-github  │ Running     │ 2025-01-29 10:30:00        │ 00:05:23                                                     │
│ analytics-pipeline      │ Completed   │ 2025-01-29 09:15:00        │ 00:12:45                                                     │
└─────────────────────────┴─────────────┴─────────────────────────────┴──────────────────────────────────────────────────────────┘
```

### JSON Format

```bash
flext --output json pipeline list
```

Output:

```json
{
  "pipelines": [
    {
      "name": "data-extraction-github",
      "status": "running",
      "last_run": "2025-01-29T10:30:00Z",
      "duration": "00:05:23"
    },
    {
      "name": "analytics-pipeline",
      "status": "completed",
      "last_run": "2025-01-29T09:15:00Z",
      "duration": "00:12:45"
    }
  ]
}
```

### YAML Format

```bash
flext --output yaml pipeline list
```

Output:

```yaml
pipelines:
  - name: data-extraction-github
    status: running
    last_run: "2025-01-29T10:30:00Z"
    duration: "00:05:23"
  - name: analytics-pipeline
    status: completed
    last_run: "2025-01-29T09:15:00Z"
    duration: "00:12:45"
```

### CSV Format

```bash
flext --output csv pipeline list
```

Output:

```csv
name,status,last_run,duration
data-extraction-github,running,2025-01-29T10:30:00Z,00:05:23
analytics-pipeline,completed,2025-01-29T09:15:00Z,00:12:45
```

## Error Handling

### Common Error Messages

```bash
# Command not found
$ flext unknown-command
Error: No such command 'unknown-command'.

# Invalid option
$ flext pipeline list --invalid-option
Error: No such option: --invalid-option

# Missing required argument
$ flext config set
Error: Missing argument 'key'.
```

### Debug Mode

Enable debug mode for detailed error information:

```bash
# Global debug
flext --debug command

# Environment variable
export FLX_DEBUG=true
flext command
```

## Shell Completion

### Bash

```bash
# Add to ~/.bashrc
eval "$(_FLEXT_COMPLETE=bash_source flext)"
```

### Zsh

```bash
# Add to ~/.zshrc
eval "$(_FLEXT_COMPLETE=zsh_source flext)"
```

### Fish

```bash
# Add to ~/.config/fish/config.fish
eval (env _FLEXT_COMPLETE=fish_source flext)
```

---

**Next**: [Domain Entities](entities.md) | **Previous**: [API Reference Home](../README.md)

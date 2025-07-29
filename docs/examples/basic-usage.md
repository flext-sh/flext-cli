# Basic Usage Examples

Este guia apresenta exemplos práticos de uso do FLEXT CLI, desde comandos básicos até operações mais avançadas.

## Getting Started

### Installation and Setup

```bash
# Clone the project
git clone https://github.com/your-org/flext.git
cd flext/flext-cli

# Install dependencies
make setup

# Verify installation
poetry run flext --version
```

### First Commands

```bash
# Show help
poetry run flext --help

# Show version information
poetry run flext version

# Show system information
poetry run flext debug info
```

## Basic Command Usage

### Global Options

```bash
# Use different output formats
poetry run flext --output json config show
poetry run flext --output yaml config show
poetry run flext --output table config show  # default

# Enable debug mode
poetry run flext --debug config show

# Use different profiles
poetry run flext --profile development config show
poetry run flext --profile production config show

# Quiet mode (suppress output)
poetry run flext --quiet config show
```

### Configuration Management

```bash
# Show current configuration
poetry run flext config show

# Show configuration with debug information
poetry run flext --debug config show

# Configuration in different formats
poetry run flext --output json config show
poetry run flext --output yaml config show
```

Example output:
```yaml
profile: default
output_format: table
debug: false
quiet: false
verbose: false
no_color: false
```

## Command Groups

### Authentication Commands

```bash
# Check authentication status (future)
poetry run flext auth --help

# Authentication workflow (planned)
# poetry run flext auth login
# poetry run flext auth status
# poetry run flext auth logout
```

### Pipeline Management

```bash
# List pipelines
poetry run flext pipeline list

# Pipeline commands help
poetry run flext pipeline --help

# Pipeline operations (planned)
# poetry run flext pipeline create my-pipeline
# poetry run flext pipeline run my-pipeline
# poetry run flext pipeline status my-pipeline
```

### Plugin Management

```bash
# List installed plugins
poetry run flext plugin list

# Plugin management help
poetry run flext plugin --help

# Plugin operations (planned)
# poetry run flext plugin install tap-github
# poetry run flext plugin update tap-github
# poetry run flext plugin remove tap-github
```

### Debug and Diagnostics

```bash
# Show system information
poetry run flext debug info

# Debug commands help
poetry run flext debug --help

# Debug operations (planned)
# poetry run flext debug connectivity
# poetry run flext debug performance
# poetry run flext debug validate
```

## Project-Specific Commands

### client-a Project

```bash
# client-a commands help
poetry run flext client-a --help

# Run client-a migration
poetry run flext client-a migrate

# Check migration status
poetry run flext client-a status

# Validate client-a setup
poetry run flext client-a validate
```

### client-b Project

```bash
# client-b commands help
poetry run flext client-b --help

# Deploy client-b services
poetry run flext client-b deploy

# Check deployment status
poetry run flext client-b status

# View service logs
poetry run flext client-b logs --service api
```

### Meltano Integration

```bash
# Meltano commands help
poetry run flext meltano --help

# Run Meltano operations
poetry run flext meltano run tap-github target-postgres

# Install Meltano plugins
poetry run flext meltano install extractor tap-github

# Invoke Meltano operations
poetry run flext meltano invoke tap-github --discover
```

## Output Formats

### Table Format (Default)

```bash
poetry run flext pipeline list
```

Pretty-printed table with colors and formatting:
```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                                                          Pipeline Status                                                           ┃
┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Name                    │ Status      │ Last Run                    │ Duration                                                     │
├─────────────────────────┼─────────────┼─────────────────────────────┼──────────────────────────────────────────────────────────┤
│ data-extraction         │ Running     │ 2025-01-29 10:30:00        │ 00:05:23                                                     │
│ analytics-pipeline      │ Completed   │ 2025-01-29 09:15:00        │ 00:12:45                                                     │
└─────────────────────────┴─────────────┴─────────────────────────────┴──────────────────────────────────────────────────────────┘
```

### JSON Format

```bash
poetry run flext --output json pipeline list
```

Structured JSON output:
```json
{
  "pipelines": [
    {
      "name": "data-extraction",
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
  ],
  "meta": {
    "total": 2,
    "timestamp": "2025-01-29T10:35:00Z"
  }
}
```

### YAML Format

```bash
poetry run flext --output yaml pipeline list
```

Human-readable YAML:
```yaml
pipelines:
  - name: data-extraction
    status: running
    last_run: '2025-01-29T10:30:00Z'
    duration: '00:05:23'
  - name: analytics-pipeline
    status: completed
    last_run: '2025-01-29T09:15:00Z'
    duration: '00:12:45'
meta:
  total: 2
  timestamp: '2025-01-29T10:35:00Z'
```

### CSV Format

```bash
poetry run flext --output csv pipeline list
```

Comma-separated values for data processing:
```csv
name,status,last_run,duration
data-extraction,running,2025-01-29T10:30:00Z,00:05:23
analytics-pipeline,completed,2025-01-29T09:15:00Z,00:12:45
```

## Working with Profiles

### Development Profile

```bash
# Use development profile
poetry run flext --profile development config show

# Set environment variable
export FLX_PROFILE=development
poetry run flext config show
```

### Production Profile

```bash
# Use production profile
poetry run flext --profile production config show

# Production commands with extra validation
poetry run flext --profile production pipeline run critical-pipeline
```

## Error Handling

### Common Errors

```bash
# Invalid command
$ poetry run flext invalid-command
Error: No such command 'invalid-command'.

Did you mean one of these?
- config
- pipeline
- plugin
```

### Debug Mode for Errors

```bash
# Enable debug for detailed error information
poetry run flext --debug config show

# Debug with specific command
poetry run flext --debug --profile development pipeline list
```

Example debug output:
```
[DEBUG] Loading configuration from: /home/user/.flx/config.yaml
[DEBUG] Profile: development
[DEBUG] Output format: table
[DEBUG] CLI service container initialized
[INFO] Configuration loaded successfully
```

## Environment Variables

### Setting Environment Variables

```bash
# CLI configuration
export FLEXT_CLI_DEV_MODE=true
export FLEXT_CLI_LOG_LEVEL=debug
export FLEXT_CLI_CONFIG_PATH=/path/to/config.yaml

# Profile and output
export FLX_PROFILE=development
export FLX_DEBUG=true

# Run commands with environment
poetry run flext config show
```

### Configuration Precedence

1. Command-line options (highest priority)
2. Environment variables
3. Configuration files
4. Default values (lowest priority)

```bash
# Command-line overrides environment
export FLX_DEBUG=false
poetry run flext --debug config show  # Debug will be enabled
```

## Combining Commands

### Piping Output

```bash
# Extract specific data with jq
poetry run flext --output json pipeline list | jq '.pipelines[].name'

# Save output to file
poetry run flext --output yaml config show > current-config.yaml

# Count pipelines
poetry run flext --output json pipeline list | jq '.pipelines | length'
```

### Scripting

```bash
#!/bin/bash
# Simple CLI automation script

# Set profile for script
export FLX_PROFILE=production

# Check if any pipelines are failing
FAILED_COUNT=$(poetry run flext --output json pipeline list | jq '.pipelines | map(select(.status == "failed")) | length')

if [ "$FAILED_COUNT" -gt 0 ]; then
    echo "Warning: $FAILED_COUNT pipelines are failing"
    exit 1
fi

echo "All pipelines are healthy"
```

## Interactive Usage

### Command Discovery

```bash
# Explore available commands
poetry run flext --help

# Explore command groups
poetry run flext auth --help
poetry run flext config --help
poetry run flext pipeline --help
poetry run flext plugin --help
poetry run flext debug --help

# Project-specific commands
poetry run flext client-a --help
poetry run flext client-b --help
poetry run flext meltano --help
```

### Getting Help

```bash
# General help
poetry run flext --help

# Command-specific help
poetry run flext config --help
poetry run flext pipeline list --help

# Version information
poetry run flext --version
poetry run flext version
```

## Performance Tips

### Fast Commands

```bash
# Use quiet mode for scripts
poetry run flext --quiet --output json pipeline list

# Skip debug output in production
unset FLX_DEBUG
poetry run flext pipeline list
```

### Caching

```bash
# Save frequently used data
poetry run flext --output json config show > ~/.flx/cached-config.json

# Use cached data in scripts
cat ~/.flx/cached-config.json | jq '.profile'
```

## Best Practices

### 1. Use Appropriate Output Formats

```bash
# Human reading - use table (default)
poetry run flext pipeline list

# Automation/scripts - use JSON
poetry run flext --output json pipeline list | jq '.pipelines'

# Configuration files - use YAML
poetry run flext --output yaml config show > config.yaml

# Data export - use CSV
poetry run flext --output csv pipeline list > pipelines.csv
```

### 2. Environment Management

```bash
# Development
export FLX_PROFILE=development
export FLX_DEBUG=true

# Production
export FLX_PROFILE=production
unset FLX_DEBUG
```

### 3. Error Handling in Scripts

```bash
#!/bin/bash
set -e  # Exit on error

# Use quiet mode and check exit codes
if poetry run flext --quiet pipeline status my-pipeline; then
    echo "Pipeline is healthy"
else
    echo "Pipeline check failed"
    exit 1
fi
```

### 4. Debugging

```bash
# Always use debug mode when troubleshooting
poetry run flext --debug command

# Check system information
poetry run flext debug info

# Validate configuration
poetry run flext --debug config show
```

---

**Next**: [Advanced Patterns](advanced-patterns.md) | **Previous**: [Examples Home](../README.md)
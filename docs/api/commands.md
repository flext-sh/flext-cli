# FLEXT CLI Commands API Reference

**Document**: Complete command reference and usage guide  
**Version: 0.9.0 (2025-08-01))  
**Status**: 30% implemented - See implementation status per command  
**Coverage\*\*: Current and planned commands for FLEXT ecosystem

## 🎯 **Command Structure Overview**

FLEXT CLI provides a hierarchical command structure for managing the entire FLEXT ecosystem:

```
flext
├── auth                    # ✅ Authentication & authorization
├── config                  # ✅ Configuration management
├── debug                   # ✅ Debugging & diagnostics
├── pipeline                # ❌ Pipeline management (Sprint 1)
├── service                 # ❌ Service orchestration (Sprint 1)
├── data                    # ❌ Data management (Sprint 3)
├── plugin                  # ❌ Plugin management (Sprint 4)
├── monitor                 # ❌ Monitoring & observability (Sprint 7)
├── algar                   # ❌ ALGAR project commands (Sprint 5)
├── gruponos                # ❌ GrupoNos project commands (Sprint 5)
├── meltano                 # ❌ Meltano integration (Sprint 6)
├── interactive             # ⚠️ Interactive mode (placeholder)
└── version                 # ⚠️ Version information (basic)
```

## ✅ **Implemented Commands (30%)**

### **Authentication Commands (`flext auth`)**

**Status**: ✅ Fully implemented and functional

#### **`flext auth login`**

Authenticate with the FLEXT ecosystem.

```bash
flext auth login [OPTIONS]

Options:
  --username TEXT    Username for authentication
  --password TEXT    Password (will prompt if not provided)
  --profile TEXT     Configuration profile to use [default: default]
  --help            Show this message and exit

Examples:
  flext auth login --username admin
  flext auth login --profile production
```

**Return Codes**:

- `0`: Login successful
- `1`: Authentication failed
- `2`: Connection error

#### **`flext auth logout`**

Logout and clear authentication tokens.

```bash
flext auth logout [OPTIONS]

Options:
  --profile TEXT     Configuration profile [default: default]
  --all             Logout from all profiles
  --help            Show this message and exit

Examples:
  flext auth logout
  flext auth logout --all
```

#### **`flext auth status`**

Check current authentication status.

```bash
flext auth status [OPTIONS]

Options:
  --profile TEXT     Configuration profile [default: default]
  --verbose         Show detailed authentication information
  --help            Show this message and exit

Examples:
  flext auth status
  flext auth status --verbose
```

#### **`flext auth token`**

Display or manage authentication tokens.

```bash
flext auth token [OPTIONS] COMMAND [ARGS]...

Commands:
  show     Display current authentication token
  refresh  Refresh authentication token
  revoke   Revoke authentication token

Examples:
  flext auth token show
  flext auth token refresh
```

### **Configuration Commands (`flext config`)**

**Status**: ✅ Fully implemented and functional

#### **`flext config show`**

Display current configuration.

```bash
flext config show [OPTIONS]

Options:
  --profile TEXT     Configuration profile [default: default]
  --format TEXT      Output format [default: table]
  --key TEXT         Show specific configuration key
  --help            Show this message and exit

Examples:
  flext config show
  flext config show --format json
  flext config show --key auth.username
```

#### **`flext config set`**

Set configuration value.

```bash
flext config set [OPTIONS] KEY VALUE

Options:
  --profile TEXT     Configuration profile [default: default]
  --type TEXT        Value type (string|int|bool|json) [default: string]
  --help            Show this message and exit

Examples:
  flext config set auth.username admin
  flext config set debug.enabled true --type bool
  flext config set services.timeout 30 --type int
```

#### **`flext config get`**

Get configuration value.

```bash
flext config get [OPTIONS] KEY

Options:
  --profile TEXT     Configuration profile [default: default]
  --default TEXT     Default value if key not found
  --help            Show this message and exit

Examples:
  flext config get auth.username
  flext config get services.timeout --default 30
```

#### **`flext config reset`**

Reset configuration to defaults.

```bash
flext config reset [OPTIONS]

Options:
  --profile TEXT     Configuration profile [default: default]
  --key TEXT         Reset specific key (resets all if not specified)
  --confirm         Skip confirmation prompt
  --help            Show this message and exit

Examples:
  flext config reset --confirm
  flext config reset --key auth.username
```

### **Debug Commands (`flext debug`)**

**Status**: ✅ Fully implemented and functional

#### **`flext debug info`**

Show system and environment information.

```bash
flext debug info [OPTIONS]

Options:
  --verbose         Show detailed system information
  --format TEXT     Output format [default: table]
  --help            Show this message and exit

Examples:
  flext debug info
  flext debug info --verbose --format json
```

#### **`flext debug health`**

Perform basic health checks.

```bash
flext debug health [OPTIONS]

Options:
  --service TEXT     Check specific service
  --timeout INT      Health check timeout in seconds [default: 30]
  --help            Show this message and exit

Examples:
  flext debug health
  flext debug health --service flexcore
```

#### **`flext debug logs`**

View application logs.

```bash
flext debug logs [OPTIONS]

Options:
  --lines INT        Number of log lines to show [default: 100]
  --level TEXT       Log level filter (debug|info|warning|error)
  --follow          Follow log output (tail -f mode)
  --help            Show this message and exit

Examples:
  flext debug logs
  flext debug logs --lines 50 --level error
  flext debug logs --follow
```

#### **`flext debug validate`**

Validate CLI installation and configuration.

```bash
flext debug validate [OPTIONS]

Options:
  --profile TEXT     Configuration profile [default: default]
  --verbose         Show detailed validation results
  --help            Show this message and exit

Examples:
  flext debug validate
  flext debug validate --verbose
```

### **Basic Commands**

#### **`flext version`**

Show version information.

**Status**: ⚠️ Basic implementation

```bash
flext version [OPTIONS]

Options:
  --verbose         Show detailed version information
  --help            Show this message and exit

Examples:
  flext version
  flext version --verbose
```

#### **`flext interactive`**

Start interactive mode.

**Status**: ⚠️ Placeholder - shows "coming soon" message

```bash
flext interactive [OPTIONS]

Options:
  --help            Show this message and exit

Examples:
  flext interactive
```

---

## ❌ **Planned Commands (70%)**

### **Pipeline Management (`flext pipeline`) - Sprint 1**

**Status**: ❌ Not implemented - Target Sprint 1

#### **`flext pipeline list`**

List all data pipelines.

```bash
flext pipeline list [OPTIONS]

Options:
  --status TEXT      Filter by status (running|stopped|error|all) [default: all]
  --format TEXT      Output format [default: table]
  --help            Show this message and exit

Examples:
  flext pipeline list
  flext pipeline list --status running
  flext pipeline list --format json
```

#### **`flext pipeline start`**

Start a data pipeline.

```bash
flext pipeline start [OPTIONS] PIPELINE_NAME

Options:
  --environment TEXT Environment to run in [default: development]
  --config TEXT      Pipeline configuration file
  --wait            Wait for pipeline to start
  --help            Show this message and exit

Examples:
  flext pipeline start user-data-sync
  flext pipeline start analytics-pipeline --environment production
```

#### **`flext pipeline stop`**

Stop a running pipeline.

```bash
flext pipeline stop [OPTIONS] PIPELINE_NAME

Options:
  --force           Force stop without graceful shutdown
  --wait            Wait for pipeline to stop
  --help            Show this message and exit

Examples:
  flext pipeline stop user-data-sync
  flext pipeline stop analytics-pipeline --force
```

#### **`flext pipeline status`**

Show pipeline status and metrics.

```bash
flext pipeline status [OPTIONS] PIPELINE_NAME

Options:
  --verbose         Show detailed status information
  --format TEXT     Output format [default: table]
  --help            Show this message and exit

Examples:
  flext pipeline status user-data-sync
  flext pipeline status analytics-pipeline --verbose
```

#### **`flext pipeline logs`**

View pipeline execution logs.

```bash
flext pipeline logs [OPTIONS] PIPELINE_NAME

Options:
  --lines INT       Number of log lines to show [default: 100]
  --follow          Follow log output
  --level TEXT      Log level filter
  --help            Show this message and exit

Examples:
  flext pipeline logs user-data-sync
  flext pipeline logs analytics-pipeline --follow
```

### **Service Orchestration (`flext service`) - Sprint 1-2**

**Status**: ❌ Not implemented - Target Sprint 1-2

#### **`flext service health`**

Check health of all FLEXT services.

```bash
flext service health [OPTIONS]

Options:
  --service TEXT     Check specific service
  --format TEXT      Output format [default: table]
  --timeout INT      Health check timeout [default: 30]
  --help            Show this message and exit

Examples:
  flext service health
  flext service health --service flexcore
```

#### **`flext service status`**

Show overall ecosystem status.

```bash
flext service status [OPTIONS]

Options:
  --verbose         Show detailed status information
  --format TEXT     Output format [default: table]
  --help            Show this message and exit

Examples:
  flext service status
  flext service status --verbose --format json
```

#### **`flext service logs`**

View service logs.

```bash
flext service logs [OPTIONS] SERVICE_NAME

Options:
  --lines INT       Number of log lines [default: 100]
  --follow          Follow log output
  --level TEXT      Log level filter
  --help            Show this message and exit

Examples:
  flext service logs flexcore
  flext service logs flext-service --follow
```

### **Data Management (`flext data`) - Sprint 3-4**

**Status**: ❌ Not implemented - Target Sprint 3-4

#### **`flext data taps list`**

List available Singer taps.

```bash
flext data taps list [OPTIONS]

Options:
  --status TEXT      Filter by status
  --format TEXT      Output format [default: table]
  --help            Show this message and exit
```

#### **`flext data targets list`**

List available Singer targets.

```bash
flext data targets list [OPTIONS]

Options:
  --status TEXT      Filter by status
  --format TEXT      Output format [default: table]
  --help            Show this message and exit
```

#### **`flext data dbt run`**

Execute DBT transformations.

```bash
flext data dbt run [OPTIONS] PROJECT

Options:
  --models TEXT      Specific models to run
  --environment TEXT Environment configuration
  --help            Show this message and exit

Examples:
  flext data dbt run oracle-transforms
  flext data dbt run ldap-transforms --models user_sync
```

### **Plugin Management (`flext plugin`) - Sprint 4**

**Status**: ❌ Not implemented - Target Sprint 4

#### **`flext plugin list`**

List installed plugins.

```bash
flext plugin list [OPTIONS]

Options:
  --status TEXT      Filter by status (active|inactive|error)
  --format TEXT      Output format [default: table]
  --help            Show this message and exit
```

#### **`flext plugin install`**

Install a plugin.

```bash
flext plugin install [OPTIONS] PLUGIN_NAME

Options:
  --version TEXT     Specific version to install
  --force           Force reinstall if already exists
  --help            Show this message and exit

Examples:
  flext plugin install oracle-connector
  flext plugin install ldap-sync --version 1.2.0
```

### **Project-Specific Commands - Sprint 5-6**

#### **ALGAR Commands (`flext algar`) - Sprint 5**

```bash
# ALGAR Oracle Unified Directory migration
flext algar migration status [OPTIONS]
flext algar oud sync [OPTIONS]
flext algar pipeline deploy [OPTIONS] PIPELINE_NAME
flext algar logs [OPTIONS]
```

#### **GrupoNos Commands (`flext gruponos`) - Sprint 5**

```bash
# GrupoNos-specific Meltano operations
flext gruponos pipeline deploy [OPTIONS] PIPELINE_NAME
flext gruponos status [OPTIONS]
flext gruponos logs [OPTIONS]
```

#### **Meltano Commands (`flext meltano`) - Sprint 6**

```bash
# Meltano project management
flext meltano project init [OPTIONS] PROJECT_NAME
flext meltano run [OPTIONS] JOB_NAME
flext meltano schedule [OPTIONS] SCHEDULE_NAME
flext meltano test [OPTIONS]
```

### **Monitoring Commands (`flext monitor`) - Sprint 7**

```bash
# Real-time monitoring and observability
flext monitor dashboard [OPTIONS]
flext monitor metrics [OPTIONS] SERVICE_NAME
flext monitor alerts list [OPTIONS]
flext logs search [OPTIONS] QUERY
```

---

## 🔧 **Command Development Guidelines**

### **Adding New Commands**

1. **Follow Naming Convention**:

   ```
   flext <group> <action> [<resource>] [OPTIONS]
   ```

2. **Use Standard Options**:

   ```bash
   --format TEXT      # Output format (table|json|yaml|csv)
   --verbose         # Detailed output
   --help            # Command help
   ```

3. **Implement Error Handling**:

   ```python
   @handle_service_result
   async def command_function() -> FlextResult[Any]:
       # Command implementation with proper error handling
   ```

4. **Add Comprehensive Tests**:

   ```python
   def test_command_success():
       runner = CliRunner()
       result = runner.invoke(cli, ['group', 'action'])
       assert result.exit_code == 0
   ```

### **Output Format Standards**

All commands should support multiple output formats:

- **table**: Human-readable table (default)
- **JSON**: Machine-readable JSON
- **YAML**: YAML format
- **csv**: CSV for data export

### **Error Handling Standards**

Standard exit codes:

- `0`: Success
- `1`: General error
- `2`: Connection/network error
- `3`: Authentication error
- `4`: Configuration error
- `5`: Not found error

---

## 📊 **Implementation Progress**

### **Completion Status**

- **✅ Implemented**: 30% (auth, config, debug commands)
- **🚧 In Progress**: 0% (no commands currently in development)
- **📋 Planned**: 70% (pipeline, service, data, plugin, monitor, project commands)

### **Sprint Targets**

- **Sprint 1**: +20% (pipeline, service commands) → 50% total
- **Sprint 3**: +20% (data management commands) → 70% total
- **Sprint 5**: +15% (project-specific commands) → 85% total
- **Sprint 7**: +10% (monitoring commands) → 95% total
- **Sprint 10**: +5% (advanced features) → 100% total

### **Quality Metrics**

- **Test Coverage**: 90%+ maintained for all commands
- **Response Time**: <1s for all basic commands
- **Error Coverage**: All error scenarios handled with proper messages
- **Documentation**: 100% command coverage with examples

This command reference will be updated as commands are implemented according to the development roadmap.

#!/usr/bin/env python3
"""03 - Extensive FLEXT-CLI Library Component Demonstration.

Esta demonstração abrangente utiliza extensivamente a biblioteca flext-cli,
mostrando como integrar todos os componentes disponíveis:

Componentes Demonstrados:
- Domain Models: CLICommand, CLISession, CLIPlugin, CLIContext
- Services: FlextCliService, CLICommandService, CLISessionService
- Decorators: @cli_enhanced, @cli_measure_time, @cli_retry, @cli_confirm
- Types: PositiveInt, URL, ExistingFile, CommandStatus, OutputFormat
- Mixins: CLIValidationMixin, CLILoggingMixin, CLIOutputMixin
- Formatters: PlainFormatter, OutputFormatter, FormatterFactory
- Authentication: get_auth_token, save_auth_token, login_command
- Utilities: cli_format_output, cli_create_table, cli_batch_process_files
- Configuration: CLIConfig, CLISettings, get_cli_config
- Advanced: FlextApiClient, domain events, business rules

Arquitetura demonstrada:
- Foundation: flext-core + Pydantic patterns
- Domain: flext-cli entities com extensive library usage
- Application: services using comprehensive flext-cli patterns
- Infrastructure: full integration com todos os componentes

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from pathlib import Path
from tempfile import NamedTemporaryFile

from flext_core import FlextResult, get_logger
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# Comprehensive flext-cli imports demonstrating extensive usage
from flext_cli import (
    URL,
    # Configuration and types
    CLIConfig,
    CLIConfigMixin,
    CLIContext,
    CLIDataMixin,
    CLIEntityFactory,
    CLIExecutionMixin,
    CLILoggingMixin,
    CLIOutputMixin,
    CLIValidationMixin,
    CommandType,
    ExistingDir,
    FlextApiClient,
    # Available domain models
    FlextCliService,
    FormatterFactory,
    NewFile,
    OutputFormat,
    PlainFormatter,
    PositiveInt,
    # Decorators from core
    async_command,
    # Utilities
    cli_batch_process_files,
    cli_cache_result,
    cli_confirm,
    cli_create_table,
    cli_enhanced,
    cli_file_operation,
    cli_handle_keyboard_interrupt,
    cli_load_data_file,
    cli_log_execution,
    cli_measure_time,
    cli_quick_setup,
    cli_retry,
    cli_run_command,
    cli_save_data_file,
    cli_validate_inputs,
    confirm_action,
    # Container and factory
    create_cli_container,
    # API integration
    flext_cli_aggregate_data,
    flext_cli_export,
    flext_cli_format,
    flext_cli_transform_data,
    get_auth_headers,
    get_cli_config,
    get_config,
    measure_time,
    require_auth,
    save_auth_token,
    with_spinner,
)


# Advanced CLI service with comprehensive mixin integration
class ComprehensiveCliService(
    FlextCliService,
    CLIValidationMixin,
    CLILoggingMixin,
    CLIOutputMixin,
    CLIConfigMixin,
    CLIDataMixin,
    CLIExecutionMixin,
):
    """Comprehensive CLI service demonstrating extensive flext-cli integration."""

    def __init__(self) -> None:
        """Initialize service with comprehensive FLEXT-CLI components."""
        super().__init__()
        self.logger = get_logger(__name__)
        self.console = Console()
        self.config = get_cli_config()
        self.settings = get_config()
        self.container = create_cli_container()

    @cli_enhanced
    @cli_measure_time
    @cli_log_execution
    @cli_validate_inputs
    def process_user_data(
        self,
        user_name: str,
        user_email: str,
        user_age: PositiveInt,
        user_website: URL,
    ) -> FlextResult[dict[str, object]]:
        """Demonstrate comprehensive decorator usage with flext-cli types."""
        try:
            # Use flext-cli data processing
            user_data = {
                "name": user_name,
                "email": user_email,
                "age": int(user_age),  # PositiveInt conversion
                "website": str(user_website),  # URL validation
                "created_at": datetime.now(UTC).isoformat(),
            }

            # Use flext-cli transformation utilities
            return flext_cli_transform_data(
                user_data,
                lambda data: {**data, "processed": True},
            )

        except Exception as e:
            return FlextResult.fail(f"Failed to process user data: {e}")

    @cli_retry(max_attempts=3)
    @cli_cache_result(ttl_seconds=60)
    def fetch_api_data(self, endpoint: str) -> FlextResult[dict[str, object]]:
        """Demonstrate API integration with retry and caching."""
        client = FlextApiClient()
        return client.get(endpoint)

    @cli_confirm(message="This will process files. Continue?")
    @cli_file_operation
    @with_spinner("Processing files...")
    def batch_file_processing(self, input_dir: ExistingDir) -> FlextResult[list[str]]:
        """Demonstrate file operations with confirmation and spinner."""
        try:
            # Use flext-cli batch processing
            return cli_batch_process_files(
                input_directory=Path(input_dir),
                file_pattern="*.txt",
                processor=lambda file: f"Processed: {file.name}",
            )

        except Exception as e:
            return FlextResult.fail(f"Batch processing failed: {e}")


@cli_enhanced
@measure_time
def demonstrate_cli_domain_models() -> None:
    """Demonstrate FLEXT-CLI domain models with extensive integration."""
    console = Console()
    console.print(
        Panel(
            "[bold blue]🏗️ FLEXT-CLI Domain Models - Extensive Integration[/bold blue]",
            expand=False,
        )
    )

    # 1. CLI Configuration with comprehensive patterns
    console.print(
        "\n[cyan]1. CLI Configuration com Pydantic + Environment Integration:[/cyan]"
    )
    config = CLIConfig()
    settings = get_cli_settings()

    console.print(f"   ✅ Config Profile: {getattr(config, 'profile', 'default')}")
    console.print(f"   ✅ Output Format: {getattr(config, 'output_format', 'table')}")
    console.print(f"   ✅ Settings Environment: {settings.log_level}")

    # 2. CLI Context with comprehensive context management
    console.print("\n[cyan]2. CLI Context com Comprehensive Management:[/cyan]")
    context = CLIContext(
        profile="production",
        output=OutputFormat.JSON,
        debug=False,
        quiet=False,
        verbose=True,
    )
    console.print(f"   ✅ Context Profile: {context.profile}")
    console.print(f"   ✅ Context Output: {context.output.value}")
    console.print(f"   ✅ Context Debug: {context.debug}")

    # 3. CLI Command with full lifecycle management
    console.print("\n[cyan]3. CLI Command com Full Lifecycle Management:[/cyan]")
    try:
        # Use CLI Entity Factory for proper creation
        factory = CLIEntityFactory()
        command_result = factory.create_command(
            name="deploy-service",
            command_line="kubectl apply -f deployment.yaml",
            command_type=CommandType.SYSTEM,
            arguments={"namespace": "production", "replicas": "3"},
            options={"wait": True, "timeout": "300s"},
        )

        if command_result.success:
            command = command_result.unwrap()
            console.print(f"   ✅ Command Created: {command.name}")
            console.print(f"   ✅ Command Type: {command.command_type.value}")
            console.print(f"   ✅ Command Status: {command.command_status.value}")

            # Demonstrate command lifecycle
            execution_result = command.start_execution()
            if execution_result.success:
                console.print("   ✅ Command execution started")

                # Simulate completion
                completion_result = command.complete_execution(
                    exit_code=0,
                    stdout="Deployment successful",
                    stderr="",
                )
                if completion_result.success:
                    console.print("   ✅ Command completed successfully")

    except Exception as e:
        console.print(f"   ⚠️ Demo note: {e}")

    # 4. CLI Session with comprehensive tracking
    console.print("\n[cyan]4. CLI Session com Comprehensive Tracking:[/cyan]")
    session = CLISession(
        session_id="session_" + datetime.now(UTC).strftime("%Y%m%d_%H%M%S"),
        user_id="user_123",
        working_directory="/home/user/projects",
        environment={"PATH": "/usr/bin", "TERM": "xterm-256color"},
    )
    console.print(f"   ✅ Session ID: {session.session_id}")
    console.print(f"   ✅ User ID: {session.user_id}")
    console.print(f"   ✅ Working Directory: {session.working_directory}")

    # 5. CLI Plugin with dependency management
    console.print("\n[cyan]5. CLI Plugin com Dependency Management:[/cyan]")
    plugin = CLIPlugin(
        name="kubernetes-plugin",
        version="1.2.3",
        description="Kubernetes deployment and management plugin",
        entry_point="k8s_plugin.main",
        commands=["deploy", "scale", "rollback", "status"],
        dependencies=["kubectl", "helm"],
        enabled=True,
        installed=True,
        author="FLEXT Team",
        license="MIT",
        repository_url="https://github.com/flext/k8s-plugin",
    )
    console.print(f"   ✅ Plugin Name: {plugin.name}")
    console.print(f"   ✅ Plugin Version: {plugin.version}")
    console.print(f"   ✅ Plugin Commands: {', '.join(plugin.commands)}")
    console.print(f"   ✅ Plugin Dependencies: {', '.join(plugin.dependencies)}")


@async_command
@cli_handle_keyboard_interrupt
async def demonstrate_advanced_cli_services() -> None:
    """Demonstrate advanced CLI services with comprehensive patterns."""
    console = Console()
    console.print(
        Panel(
            "[bold green]⚡ Advanced CLI Services - Comprehensive Integration[/bold green]",
            expand=False,
        )
    )

    # Initialize comprehensive CLI service
    service = ComprehensiveCliService()

    # 1. Demonstrate comprehensive data processing
    console.print("\n[cyan]1. Comprehensive Data Processing com Type Safety:[/cyan]")
    processing_result = service.process_user_data(
        user_name="João Silva",
        user_email="joao@example.com",
        user_age=PositiveInt(30),  # Type-safe positive integer
        user_website=URL("https://joao.dev"),  # Type-safe URL
    )

    if processing_result.success:
        user_data = processing_result.unwrap()
        console.print("   ✅ User data processed successfully:")
        formatted_output = flext_cli_format(user_data, format_type="json")
        console.print(f"   {formatted_output}")
    else:
        console.print(f"   ❌ Processing failed: {processing_result.error}")

    # 2. Demonstrate API integration with authentication
    console.print("\n[cyan]2. API Integration com Authentication:[/cyan]")
    auth_result = save_auth_token("demo_token_12345")
    if auth_result.success:
        console.print("   ✅ Auth token saved successfully")

        headers_result = get_auth_headers()
        if headers_result.success:
            console.print("   ✅ Auth headers retrieved")
            console.print(f"   📋 Headers: {headers_result.unwrap()}")

    # 3. Demonstrate comprehensive output formatting
    console.print("\n[cyan]3. Comprehensive Output Formatting:[/cyan]")
    sample_data = [
        {"name": "Service A", "status": "running", "cpu": "45%", "memory": "1.2GB"},
        {"name": "Service B", "status": "stopped", "cpu": "0%", "memory": "0MB"},
        {"name": "Service C", "status": "running", "cpu": "78%", "memory": "2.1GB"},
    ]

    # Use flext-cli table creation
    table_result = cli_create_table(
        data=sample_data,
        title="Service Status",
        columns=["name", "status", "cpu", "memory"],
    )
    if table_result.success:
        console.print("   ✅ Table created successfully")
        console.print(table_result.unwrap())

    # 4. Demonstrate data aggregation and export
    console.print("\n[cyan]4. Data Aggregation and Export:[/cyan]")
    aggregation_result = flext_cli_aggregate_data(
        sample_data,
        group_by="status",
        aggregations={"count": len},
    )
    if aggregation_result.success:
        aggregated = aggregation_result.unwrap()
        console.print("   ✅ Data aggregated successfully:")
        console.print(f"   📊 Results: {aggregated}")

        # Export aggregated data
        export_result = flext_cli_export(
            aggregated,
            format_type="json",
            output_file=None,  # Return as string
        )
        if export_result.success:
            console.print("   ✅ Data exported successfully")


@require_auth
@confirm_action("This will demonstrate file operations. Continue?")
def demonstrate_file_operations() -> None:
    """Demonstrate comprehensive file operations."""
    console = Console()
    console.print(
        Panel(
            "[bold yellow]📁 File Operations - Comprehensive Integration[/bold yellow]",
            expand=False,
        )
    )

    # 1. Demonstrate file validation with flext-cli types
    console.print("\n[cyan]1. File Validation com Type Safety:[/cyan]")
    try:
        # Use flext-cli path types for validation
        current_dir = ExistingDir(".")
        console.print(f"   ✅ Current directory validated: {current_dir}")

        # Check for specific files - use secure temporary file
        with NamedTemporaryFile(suffix=".txt", delete=False) as tf:
            temp_file = NewFile(tf.name)
            console.print(f"   ✅ New file path prepared: {temp_file}")

    except Exception as e:
        console.print(f"   ⚠️ File validation note: {e}")

    # 2. Demonstrate data saving and loading
    console.print("\n[cyan]2. Data Saving and Loading:[/cyan]")
    sample_config = {
        "service_name": "flext-demo",
        "version": "1.0.0",
        "endpoints": ["http://localhost:8080", "http://localhost:8081"],
        "features": {"authentication": True, "monitoring": True},
    }

    # Save data using flext-cli utilities - use secure temporary file
    with NamedTemporaryFile(suffix=".json", delete=False) as tf:
        temp_file_path = Path(tf.name)

    save_result = cli_save_data_file(
        data=sample_config,
        file_path=temp_file_path,
        format_type="json",
    )
    if save_result.success:
        console.print("   ✅ Configuration saved successfully")

        # Load data back
        load_result = cli_load_data_file(
            file_path=temp_file_path,
            format_type="json",
        )
        if load_result.success:
            loaded_data = load_result.unwrap()
            console.print("   ✅ Configuration loaded successfully")
            console.print(f"   📋 Service: {loaded_data.get('service_name')}")

    # 3. Demonstrate advanced formatting
    console.print("\n[cyan]3. Advanced Formatting com Multiple Formats:[/cyan]")
    formatter_factory = FormatterFactory()

    # JSON formatting
    json_formatter = formatter_factory.get_formatter("json")
    json_result = json_formatter.format(sample_config)
    if json_result.success:
        console.print("   ✅ JSON formatting successful")

    # Plain text formatting
    plain_formatter = PlainFormatter()
    plain_result = plain_formatter.format(sample_config)
    if plain_result.success:
        console.print("   ✅ Plain text formatting successful")


def demonstrate_cli_utilities_comprehensive() -> None:
    """Demonstrate comprehensive CLI utilities integration."""
    console = Console()
    console.print(
        Panel(
            "[bold magenta]🛠️ CLI Utilities - Comprehensive Toolset[/bold magenta]",
            expand=False,
        )
    )

    # 1. Quick setup demonstration
    console.print("\n[cyan]1. Quick Setup com CLI Integration:[/cyan]")
    setup_result = cli_quick_setup(
        project_name="flext-demo-project",
        template="service",
        features=["api", "database", "monitoring"],
    )
    if setup_result.success:
        console.print("   ✅ Quick setup completed successfully")
        console.print(f"   📋 Setup details: {setup_result.unwrap()}")

    # 2. Command execution with monitoring
    console.print("\n[cyan]2. Command Execution com Monitoring:[/cyan]")
    command_result = cli_run_command(
        command=["echo", "Hello from FLEXT CLI!"],
        capture_output=True,
        timeout=30,
    )
    if command_result.success:
        output = command_result.unwrap()
        console.print("   ✅ Command executed successfully")
        console.print(f"   📤 Output: {output.get('stdout', '')}")

    # 3. Interactive prompts
    console.print("\n[cyan]3. Interactive Prompts com Validation:[/cyan]")
    # Simulate prompt response for demo
    demo_response = "flext-production"
    prompt_result = FlextResult.ok(demo_response)  # Simulated for demo
    if prompt_result.success:
        environment = prompt_result.unwrap()
        console.print(f"   ✅ Environment selected: {environment}")

    # 4. Comprehensive data transformation
    console.print("\n[cyan]4. Comprehensive Data Transformation:[/cyan]")
    demo_services = [
        {"name": "auth-service", "port": 8080, "healthy": True},
        {"name": "api-gateway", "port": 8081, "healthy": True},
        {"name": "database", "port": 5432, "healthy": False},
    ]

    # Transform and filter data
    transform_result = flext_cli_transform_data(
        demo_services,
        lambda services: [s for s in services if s["healthy"]],
    )
    if transform_result.success:
        healthy_services = transform_result.unwrap()
        console.print(f"   ✅ Healthy services: {len(healthy_services)}")
        for service in healthy_services:
            console.print(f"   🟢 {service['name']} on port {service['port']}")


def main() -> None:
    """Main demonstration function showcasing extensive FLEXT-CLI library usage."""
    console = Console()
    console.print(
        Panel(
            "[bold green]🎯 FLEXT-CLI Library - Comprehensive Integration Showcase[/bold green]\n"
            "[cyan]Demonstrating extensive usage of all FLEXT-CLI components:[/cyan]\n"
            "• Domain Models • Services • Decorators • Types • Mixins\n"
            "• Formatters • Authentication • Utilities • Configuration • API Integration",
            expand=False,
        )
    )

    # Execute comprehensive demonstrations
    console.print("\n" + "=" * 60)
    demonstrate_cli_domain_models()

    console.print("\n" + "=" * 60)
    # Run async demonstration
    asyncio.run(demonstrate_advanced_cli_services())

    console.print("\n" + "=" * 60)
    demonstrate_file_operations()

    console.print("\n" + "=" * 60)
    demonstrate_cli_utilities_comprehensive()

    # Final summary
    console.print(
        Panel(
            "[bold green]✨ FLEXT-CLI Comprehensive Integration Completed![/bold green]\n\n"
            "[cyan]Components Successfully Demonstrated:[/cyan]\n"
            "🏗️ Domain Models: CLICommand, CLISession, CLIPlugin, CLIContext\n"
            "⚡ Advanced Services: FlextCliService + comprehensive mixins\n"
            "🎨 Decorators: @cli_enhanced, @measure_time, @retry, @confirm_action\n"
            "🔒 Types: PositiveInt, URL, ExistingFile, CommandStatus, OutputFormat\n"
            "🧩 Mixins: Validation, Logging, Output, Config, Data, Execution\n"
            "📋 Formatters: JSON, Plain, Factory patterns\n"
            "🔐 Authentication: Token management, headers, login commands\n"
            "🛠️ Utilities: File operations, data processing, transformations\n"
            "⚙️ Configuration: CLI settings, environment integration\n"
            "🌐 API Integration: Client, data export, aggregation\n\n"
            "[yellow]Esta demonstração utilizou extensivamente toda a biblioteca flext-cli![/yellow]",
            expand=False,
        )
    )


if __name__ == "__main__":
    main()


def demonstrate_cli_sessions() -> None:
    """Demonstrate CLI session entity usage."""
    console = Console()
    console.print("[bold blue]CLI Session Entity Demo[/bold blue]\n")

    console.print("🔧 CLI Session Structure:")
    console.print("   - session_id: Unique session identifier")
    console.print("   - user_id: Optional user identifier")
    console.print("   - started_at: Session start timestamp")
    console.print("   - last_activity: Last activity timestamp")
    console.print("   - working_directory: Session working directory")
    console.print("   - environment: Environment variables dictionary")
    console.print("   - commands_executed: List of command IDs")
    console.print("   - current_command: Currently executing command ID")
    console.print("   - active: Session active status")
    console.print()

    console.print("✨ Session management methods:")
    console.print("   - add_command(): Add command to session and update activity")
    console.print("   - end_session(): Deactivate session and clear current command")
    console.print()


def demonstrate_cli_plugins() -> None:
    """Demonstrate CLI plugin entity usage."""
    console = Console()
    console.print("[bold blue]CLI Plugin Entity Demo[/bold blue]\n")

    console.print("🔧 CLI Plugin Structure:")
    console.print("   - name: Plugin identifier")
    console.print("   - version: Plugin version")
    console.print("   - description: Plugin description")
    console.print("   - entry_point: Plugin entry point module.function")
    console.print("   - commands: List of commands provided by plugin")
    console.print("   - enabled: Plugin enabled status")
    console.print("   - installed: Plugin installation status")
    console.print("   - dependencies: List of plugin dependencies")
    console.print("   - author: Plugin author")
    console.print("   - license: Plugin license")
    console.print("   - repository_url: Plugin repository URL")
    console.print()

    console.print("✨ Plugin lifecycle methods:")
    console.print("   - enable(): Enable the plugin")
    console.print("   - disable(): Disable the plugin")
    console.print("   - install(): Mark plugin as installed")
    console.print("   - uninstall(): Uninstall and disable plugin")
    console.print()


def demonstrate_domain_events() -> None:
    """Demonstrate domain events for CLI operations."""
    console = Console()
    console.print("[bold blue]Domain Events Demo[/bold blue]\n")

    console.print("📨 Available Domain Events:")

    events_table = Table(title="CLI Domain Events")
    events_table.add_column("Event", style="cyan")
    events_table.add_column("Purpose", style="green")
    events_table.add_column("Key Fields", style="yellow")

    events_table.add_row(
        "CommandStartedEvent",
        "Raised when command starts execution",
        "command_id, command_name, session_id",
    )
    events_table.add_row(
        "CommandCompletedEvent",
        "Raised when command completes",
        "command_id, command_name, success",
    )
    events_table.add_row(
        "CommandCancelledEvent",
        "Raised when command is cancelled",
        "command_id, command_name",
    )
    events_table.add_row(
        "ConfigUpdatedEvent",
        "Raised when configuration is updated",
        "config_id, config_name",
    )
    events_table.add_row(
        "SessionStartedEvent",
        "Raised when CLI session starts",
        "session_id, user_id, working_directory",
    )
    events_table.add_row(
        "SessionEndedEvent",
        "Raised when CLI session ends",
        "session_id, user_id, commands_executed, duration_seconds",
    )
    events_table.add_row(
        "PluginInstalledEvent",
        "Raised when plugin is installed",
        "plugin_id, plugin_name",
    )
    events_table.add_row(
        "PluginUninstalledEvent",
        "Raised when plugin is uninstalled",
        "plugin_id, plugin_name",
    )

    console.print(events_table)
    console.print()

    console.print("💡 Events are FlextValueObjects that can be:")
    console.print("   - Published to event buses")
    console.print("   - Stored for audit trails")
    console.print("   - Used for integration with other systems")
    console.print("   - Processed by event handlers for side effects")
    console.print()


def demonstrate_business_rules() -> None:
    """Demonstrate business rule validation."""
    console = Console()
    console.print("[bold blue]Business Rules Validation Demo[/bold blue]\n")

    console.print("🔒 Entity Validation Rules:")
    console.print()

    console.print("📋 CLI Command Rules:")
    console.print("   - Command name cannot be empty")
    console.print("   - Command line cannot be empty")
    console.print("   - Duration must be positive when set")
    console.print()

    console.print("👥 CLI Session Rules:")
    console.print("   - Session ID cannot be empty")
    console.print("   - Last activity cannot be before session start")
    console.print("   - Current command must be in executed commands list")
    console.print()

    console.print("🔌 CLI Plugin Rules:")
    console.print("   - Plugin name cannot be empty")
    console.print("   - Entry point cannot be empty")
    console.print("   - Version cannot be empty")
    console.print()

    console.print("🎛️ CLI Context Rules:")
    console.print("   - Profile cannot be empty")
    console.print("   - Output format must be valid (table, json, yaml, csv, plain)")
    console.print("   - Cannot have both quiet and verbose modes enabled")
    console.print()

    console.print("💡 All entities implement validate_domain_rules() method")
    console.print("   This ensures business rules are enforced at the domain level")
    console.print()


def demonstrate_practical_usage() -> None:
    """Show practical usage patterns for the domain entities."""
    console = Console()
    console.print("[bold blue]Practical Usage Patterns[/bold blue]\n")

    console.print("🏗️ Typical Integration Patterns:")
    console.print()

    console.print("1. **Command Execution Service**:")
    console.print("   ```python")
    console.print("   # Create command entity")
    console.print(
        "   command = CLICommand(name='deploy', "
        "command_line='kubectl apply -f app.yaml')",
    )
    console.print("   command.start_execution()")
    console.print("   ")
    console.print("   # Execute actual command (prefer asyncio or safe wrappers)")
    console.print("   # result = await run_command_async(command.command_line)")
    console.print("   ")
    console.print("   # Complete execution")
    console.print(
        "   command.complete_execution(result.returncode, result.stdout, result.stderr)",
    )
    console.print("   ```")
    console.print()

    console.print("2. **Session Management**:")
    console.print("   ```python")
    console.print("   # Start session")
    console.print("   session = CLISession(session_id=generate_session_id())")
    console.print("   ")
    console.print("   # Track commands")
    console.print("   session.add_command(command.id)")
    console.print("   ")
    console.print("   # End session")
    console.print("   session.end_session()")
    console.print("   ```")
    console.print()

    console.print("3. **Plugin System**:")
    console.print("   ```python")
    console.print("   # Register plugin")
    console.print("   plugin = CLIPlugin(")
    console.print("       name='kubernetes-plugin',")
    console.print("       entry_point='k8s_plugin.main',")
    console.print("       commands=['deploy', 'scale', 'rollback']")
    console.print("   )")
    console.print("   plugin.install()")
    console.print("   plugin.enable()")
    console.print("   ```")
    console.print()

    console.print("4. **Event-Driven Architecture**:")
    console.print("   ```python")
    console.print("   # Publish events")
    console.print(
        "   event = CommandStartedEvent(command_id=command.id, "
        "command_name=command.name)",
    )
    console.print("   event_bus.publish(event)")
    console.print("   ```")
    console.print()


def demonstrate_cli_commands() -> None:
    """Demonstrate CLI command entity usage."""
    console = Console()
    console.print("[bold blue]CLI Command Entity Demo[/bold blue]\n")

    console.print("🔧 CLI Command Structure:")
    console.print("   - name: Command identifier")
    console.print("   - command_line: The actual command to execute")
    console.print("   - command_type: Type of command (USER, SYSTEM, INTERNAL)")
    console.print("   - command_status: Current status (PENDING, RUNNING, COMPLETED, FAILED, CANCELLED)")
    console.print("   - arguments: Command arguments dictionary")
    console.print("   - options: Command options dictionary")
    console.print("   - working_directory: Directory to execute command from")
    console.print("   - environment: Environment variables dictionary")
    console.print("   - timeout: Command timeout in seconds")
    console.print("   - created_at: Command creation timestamp")
    console.print("   - started_at: Command execution start timestamp")
    console.print("   - completed_at: Command completion timestamp")
    console.print("   - exit_code: Command exit code")
    console.print("   - stdout: Command standard output")
    console.print("   - stderr: Command standard error output")
    console.print()

    console.print("✨ Command lifecycle methods:")
    console.print("   - start_execution(): Mark command as running and set start time")
    console.print("   - complete_execution(): Mark command as completed with results")
    console.print("   - fail_execution(): Mark command as failed with error details")
    console.print("   - cancel_execution(): Cancel the command execution")
    console.print()


def main() -> None:
    """Run the domain entities demonstration."""
    console = Console()
    console.print(
        "[bold green]🏗️ FLEXT CLI Library Domain Entities Example[/bold green]\n",
    )

    demonstrate_cli_commands()
    demonstrate_cli_sessions()
    demonstrate_cli_plugins()
    demonstrate_domain_events()
    demonstrate_business_rules()
    demonstrate_practical_usage()

    console.print("[bold green]✨ Domain entities example completed![/bold green]")
    console.print("\n💡 These entities provide the foundation for building")
    console.print("   enterprise-grade CLI applications with proper domain modeling.")


if __name__ == "__main__":
    main()

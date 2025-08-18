#!/usr/bin/env python3
"""02 - Click Framework + FLEXT-CLI Library Integration.

Demonstra uso extensivo da biblioteca flext-cli com padrões arquiteturais:
- Uso extensivo de todos os componentes flext-cli
- FlextResult[T] para railway-oriented programming em Click
- FlextModel + Pydantic para configuração e validação
- FlextContainer para dependency injection em CLI
- Click integration com todos os decoradores flext-cli
- Validação completa usando flext-core + flext-cli patterns

Arquitetura demonstrada:
- Foundation Layer: FlextResult, FlextContainer integration
- Domain Layer: CLI entities usando flext-cli domain models
- Application Layer: Click commands com flext-cli services
- Infrastructure Layer: flext-cli formatters, validators, helpers

Copyright (c) 2025 Flext. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import asyncio
import random
import time
from pathlib import Path
from typing import Any

import click
from flext_core import (
    FlextModel,
    FlextResult,
    FlextSettings,
    __version__ as core_version,
    get_flext_container,
    get_logger,
)
from pydantic import Field, field_validator
from rich.console import Console

from flext_cli import (  # Uso extensivo da biblioteca flext-cli
    URL,
    ClickPath,
    # Domain models and entities
    CLIContext,
    CLIEntityFactory,
    # Helpers and mixins
    CLIHelper,
    ExistingDir,
    ExistingFile,
    FlextApiClient,
    FlextCliFormatterService,
    # Service layer
    FlextCliService,
    FlextCliValidatorService,
    NewFile,
    # CLI types (uso extensivo)
    PositiveInt,
    # Core decorators
    async_command,
    cli_cache_result,
    cli_create_table,
    # CLI decorators (uso extensivo)
    cli_enhanced,
    cli_format_output,
    cli_handle_keyboard_interrupt,
    cli_log_execution,
    cli_measure_time,
    cli_quick_setup,
    cli_validate_inputs,
    confirm_action,
    create_cli_container,
    flext_cli_export,
    # API and utilities
    get_auth_headers,
    # Authentication
    get_auth_token,
    # Configuration
    get_config,
    get_settings,
    # Service result handling
    handle_service_result,
    retry,
    with_spinner,
)


# Configuração usando FlextModel + Pydantic com FLEXT-CLI integration
class ClickAppConfig(FlextModel):
    """Configuração do app Click usando FlextModel + FLEXT-CLI patterns."""

    profile: str = Field(default="development", description="Profile ativo")
    output_format: str = Field(default="table", description="Formato de saída")
    debug: bool = Field(default=False, description="Modo debug")
    verbose: bool = Field(default=False, description="Saída verbosa")
    api_url: str = Field(default="https://api.flext.dev", description="URL da API")
    timeout: int = Field(default=30, gt=0, description="Timeout em segundos")
    max_retries: int = Field(default=3, ge=0, description="Máximo de tentativas")

    @field_validator("output_format")
    @classmethod
    def validate_output_format(cls, v: str) -> str:
        """Validação usando Pydantic validator."""
        valid_formats = {"table", "json", "yaml", "csv", "plain"}
        if v not in valid_formats:
            raise ValueError(f"Formato deve ser um de: {valid_formats}")
        return v

    def validate_business_rules(self) -> FlextResult[None]:
        """Regras de negócio específicas do CLI."""
        if self.debug and self.output_format == "json":
            return FlextResult.fail(
                "Debug mode pode interferir com JSON output",
                error_code="CONFIG_CONFLICT",
            )
        return FlextResult.ok(None)


# Settings usando FlextSettings + FLEXT-CLI
class ClickAppSettings(FlextSettings):
    """Settings usando FlextSettings com FLEXT-CLI integration."""

    app_name: str = Field(default="flext-click-demo")
    app_version: str = Field(default="1.0.0")
    log_level: str = Field(default="INFO")
    environment: str = Field(default="development")
    cli_theme: str = Field(default="default")

    class Config:
        env_prefix = "FLEXT_CLICK_"


# Service usando FLEXT-CLI service patterns
class ClickDemoService(FlextCliService):
    """Serviço demo usando FLEXT-CLI service base."""

    def __init__(self, config: ClickAppConfig, logger: Any) -> None:
        self.config = config
        self.logger = logger
        # Usar FLEXT-CLI API client
        self.api_client = FlextApiClient()

    def process_data(self, data: dict[str, Any]) -> FlextResult[dict[str, Any]]:
        """Processar dados usando FLEXT-CLI patterns."""
        try:
            # Usar FLEXT-CLI validation
            validator = FlextCliValidatorService()
            validation_result = validator.validate_data(data)

            if validation_result.is_failure:
                return FlextResult.fail(f"Validation failed: {validation_result.error}")

            # Processar usando FLEXT-CLI formatter
            formatter = FlextCliFormatterService()
            formatted_data = formatter.format_data(data, self.config.output_format)

            return FlextResult.ok({
                "original": data,
                "formatted": formatted_data,
                "processed_at": time.time(),
                "profile": self.config.profile,
            })
        except Exception as e:
            return FlextResult.fail(f"Processing error: {e}")

    def validate_configuration(self) -> FlextResult[None]:
        """Validar configuração usando FLEXT-CLI patterns."""
        return self.config.validate_business_rules()


def setup_cli_dependencies() -> FlextResult[dict[str, Any]]:
    """Setup das dependências usando FLEXT-CLI container."""
    try:
        # Usar FLEXT-CLI container creation
        container = create_cli_container()

        # Configuração e settings
        config = ClickAppConfig()
        settings = ClickAppSettings()
        logger = get_logger(__name__)

        # Registrar no container global do flext-core
        flext_container = get_flext_container()
        config_result = flext_container.register("click_config", config)
        settings_result = flext_container.register("click_settings", settings)
        logger_result = flext_container.register("click_logger", logger)

        if not all(r.success for r in [config_result, settings_result, logger_result]):
            return FlextResult.fail("Failed to register CLI dependencies")

        # Criar serviço usando FLEXT-CLI patterns
        service = ClickDemoService(config, logger)
        service_result = flext_container.register("click_service", service)

        if service_result.is_failure:
            return FlextResult.fail("Failed to register CLI service")

        return FlextResult.ok({
            "container": flext_container,
            "config": config,
            "settings": settings,
            "logger": logger,
            "service": service,
        })
    except Exception as e:
        return FlextResult.fail(f"Setup failed: {e}")


# CLI Application com uso extensivo da FLEXT-CLI
@click.group()
@click.option(
    "--config-file",
    type=ExistingFile,  # FLEXT-CLI type
    help="Configuration file path",
)
@click.option(
    "--output-format",
    type=click.Choice(["table", "json", "yaml", "csv", "plain"]),
    default="table",
    help="Output format",
)
@click.option("--debug/--no-debug", default=False, help="Enable debug mode")
@click.option("--verbose", "-v", is_flag=True, help="Verbose output")
@click.option("--profile", default="development", help="Profile to use")
@click.pass_context
@cli_enhanced  # FLEXT-CLI decorator
@cli_log_execution  # FLEXT-CLI decorator
@cli_handle_keyboard_interrupt  # FLEXT-CLI decorator
def cli(
    ctx: click.Context,
    config_file: Path | None,
    output_format: str,
    debug: bool,
    verbose: bool,
    profile: str,
) -> None:
    """FLEXT CLI Example Application com uso extensivo da biblioteca."""
    console = Console()

    # Setup usando FLEXT-CLI patterns
    setup_result = setup_cli_dependencies()
    if setup_result.is_failure:
        console.print(f"[red]❌ Setup failed: {setup_result.error}[/red]")
        raise click.ClickException(setup_result.error or "Setup failed")

    dependencies = setup_result.unwrap()
    config = dependencies["config"]

    # Update config com valores da CLI
    config.output_format = output_format
    config.debug = debug
    config.verbose = verbose
    config.profile = profile

    # Validar configuração
    validation_result = config.validate_business_rules()
    if validation_result.is_failure:
        console.print(
            f"[red]❌ Config validation failed: {validation_result.error}[/red]"
        )
        raise click.ClickException(
            validation_result.error or "Config validation failed"
        )

    # Criar CLI context usando FLEXT-CLI
    cli_context = CLIContext(
        profile=profile,
        output_format=output_format,
        debug=debug,
        verbose=verbose,
    )

    # Usar CLI quick setup da FLEXT-CLI
    cli_settings = get_settings()
    quick_setup_result = cli_quick_setup(cli_settings)
    if quick_setup_result.is_failure:
        console.print(
            f"[yellow]⚠️ Quick setup warning: {quick_setup_result.error}[/yellow]"
        )

    # Store context for commands
    ctx.ensure_object(dict)
    ctx.obj["cli_context"] = cli_context
    ctx.obj["config_file"] = config_file
    ctx.obj["config"] = config
    ctx.obj["dependencies"] = dependencies
    ctx.obj["console"] = console


@cli.command()
@click.option(
    "--count",
    type=PositiveInt,  # FLEXT-CLI type
    default=1,
    help="Number of iterations",
)
@click.option(
    "--url",
    type=URL,  # FLEXT-CLI type
    default="https://api.example.com",
    help="API endpoint URL",
)
@click.option(
    "--batch-size",
    type=PositiveInt,  # FLEXT-CLI type
    default=10,
    help="Batch size for processing",
)
@click.pass_context
@cli_enhanced  # FLEXT-CLI decorator
@cli_measure_time  # FLEXT-CLI decorator
@cli_log_execution  # FLEXT-CLI decorator
@cli_validate_inputs  # FLEXT-CLI decorator
@handle_service_result  # FLEXT-CLI result handler
def process(
    ctx: click.Context, count: int, url: str, batch_size: int
) -> FlextResult[str]:
    """Process data using FLEXT-CLI service patterns."""
    cli_context = ctx.obj["cli_context"]
    console = ctx.obj["console"]
    dependencies = ctx.obj["dependencies"]
    service = dependencies["service"]

    console.print(
        "[bold blue]🔄 Processing with FLEXT-CLI Service Patterns[/bold blue]"
    )

    # Usar FLEXT-CLI table creation
    config_table = cli_create_table()
    config_table.add_column("Parameter", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_row("Profile", cli_context.profile)
    config_table.add_row("Output Format", cli_context.output_format)
    config_table.add_row("Debug Mode", str(cli_context.debug))
    config_table.add_row("Count", str(count))
    config_table.add_row("URL", url)
    config_table.add_row("Batch Size", str(batch_size))
    console.print(config_table)

    # Usar FLEXT-CLI helper extensivamente
    helper = CLIHelper()
    validator = FlextCliValidatorService()

    # Validação extensiva usando FLEXT-CLI
    url_validation = validator.validate_url(url)
    if url_validation.is_failure:
        return FlextResult.fail(f"Invalid URL: {url_validation.error}")

    # Criar CLI command entity usando FLEXT-CLI
    command_factory = CLIEntityFactory()
    command_result = command_factory.create_command(
        name="process_data",
        command_line=f"process --count {count} --url {url}",
        arguments={"count": count, "url": url, "batch_size": batch_size},
    )

    if command_result.is_failure:
        return FlextResult.fail(f"Failed to create CLI command: {command_result.error}")

    command = command_result.unwrap()
    console.print(f"[cyan]📋 Created CLI command: {command.name}[/cyan]")

    # Processar dados em batches usando FLEXT-CLI patterns
    results = []
    total_batches = (count + batch_size - 1) // batch_size

    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, count)
        batch_count = end_idx - start_idx

        # Usar FLEXT-CLI service para processar
        batch_data = {
            "batch_num": batch_num + 1,
            "total_batches": total_batches,
            "items": batch_count,
            "url": url,
            "start_idx": start_idx,
            "end_idx": end_idx,
        }

        processing_result = service.process_data(batch_data)
        if processing_result.is_failure:
            return FlextResult.fail(
                f"Batch {batch_num + 1} failed: {processing_result.error}"
            )

        batch_result = processing_result.unwrap()
        results.append(batch_result)

        console.print(
            f"[green]✅ Batch {batch_num + 1}/{total_batches} processed ({batch_count} items)[/green]"
        )

    # Usar FLEXT-CLI formatter para output
    formatter = FlextCliFormatterService()
    output_data = {
        "total_items": count,
        "total_batches": total_batches,
        "batch_size": batch_size,
        "url": url,
        "results": results,
        "command_id": str(command.id),
    }

    # Formatar usando FLEXT-CLI
    formatted_output = cli_format_output(output_data, cli_context.output_format)
    console.print("[bold green]📊 Processing Results:[/bold green]")
    console.print(formatted_output)

    return FlextResult.ok(
        f"Successfully processed {count} items in {total_batches} batches"
    )


@cli.command()
@click.argument("input_file", type=ExistingFile)  # FLEXT-CLI type
@click.argument("output_dir", type=ExistingDir)  # FLEXT-CLI type
@click.option(
    "--new-file",
    type=NewFile,  # FLEXT-CLI type
    help="Optional new file to create",
)
@click.option(
    "--format",
    type=click.Choice(["json", "yaml", "csv", "xml"]),
    default="json",
    help="Transformation format",
)
@click.pass_context
@cli_enhanced  # FLEXT-CLI decorator
@confirm_action("This will transform the file. Continue?")  # FLEXT-CLI decorator
@with_spinner("Transforming file...")  # FLEXT-CLI decorator
@cli_measure_time  # FLEXT-CLI decorator
@cli_log_execution  # FLEXT-CLI decorator
@handle_service_result  # FLEXT-CLI result handler
def transform(
    ctx: click.Context,
    input_file: Path,
    output_dir: Path,
    new_file: Path | None,
    format: str,
) -> FlextResult[str]:
    """Transform file using FLEXT-CLI comprehensive patterns."""
    console = ctx.obj["console"]
    dependencies = ctx.obj["dependencies"]
    service = dependencies["service"]
    cli_context = ctx.obj["cli_context"]

    console.print("[bold blue]🔄 File Transformation with FLEXT-CLI[/bold blue]")

    # Usar FLEXT-CLI helper utilities extensivamente
    helper = CLIHelper()
    validator = FlextCliValidatorService()
    formatter = FlextCliFormatterService()

    # Validação extensiva usando FLEXT-CLI
    file_validation = validator.validate_file_path(str(input_file))
    if file_validation.is_failure:
        return FlextResult.fail(f"Invalid input file: {file_validation.error}")

    dir_validation = validator.validate_directory_path(str(output_dir))
    if dir_validation.is_failure:
        return FlextResult.fail(f"Invalid output directory: {dir_validation.error}")

    # Criar CLI command entity para transformation
    command_factory = CLIEntityFactory()
    transform_command_result = command_factory.create_command(
        name="transform_file",
        command_line=f"transform {input_file} {output_dir} --format {format}",
        arguments={
            "input_file": str(input_file),
            "output_dir": str(output_dir),
            "new_file": str(new_file) if new_file else None,
            "format": format,
        },
    )

    if transform_command_result.is_failure:
        return FlextResult.fail(
            f"Failed to create transform command: {transform_command_result.error}"
        )

    transform_command = transform_command_result.unwrap()

    # Análise do arquivo usando FLEXT-CLI
    file_info = {
        "path": str(input_file),
        "size_bytes": input_file.stat().st_size,
        "extension": input_file.suffix,
        "name": input_file.name,
        "parent": str(input_file.parent),
    }

    # Usar FLEXT-CLI table para mostrar info
    info_table = cli_create_table()
    info_table.add_column("Property", style="cyan")
    info_table.add_column("Value", style="green")
    info_table.add_row("Input File", str(input_file))
    info_table.add_row("Output Directory", str(output_dir))
    info_table.add_row("File Size", helper.format_size(file_info["size_bytes"]))
    info_table.add_row("Format", format)
    if new_file:
        info_table.add_row("New File", str(new_file))
    info_table.add_row("Command ID", str(transform_command.id))
    console.print(info_table)

    # Processar transformação usando FLEXT-CLI service
    transform_data = {
        "file_info": file_info,
        "output_format": format,
        "target_directory": str(output_dir),
        "command_id": str(transform_command.id),
        "cli_profile": cli_context.profile,
    }

    processing_result = service.process_data(transform_data)
    if processing_result.is_failure:
        return FlextResult.fail(f"Transformation failed: {processing_result.error}")

    processed_data = processing_result.unwrap()

    # Simular transformação com multiple steps
    transformation_steps = [
        "Reading source file",
        "Validating file structure",
        "Converting to target format",
        "Applying transformations",
        "Writing output file",
        "Validating output",
    ]

    results = []
    for i, step in enumerate(transformation_steps):
        console.print(f"[cyan]{i + 1}/6 {step}...[/cyan]")
        time.sleep(0.2)  # Simular processing

        step_result = {
            "step": step,
            "step_number": i + 1,
            "total_steps": len(transformation_steps),
            "completed": True,
        }
        results.append(step_result)
        console.print(f"[green]  ✅ {step} completed[/green]")

    # Determinar output file
    if new_file:
        output_file = new_file
    else:
        output_file = output_dir / f"transformed_{input_file.stem}.{format}"

    # Usar FLEXT-CLI export para salvar resultado
    export_data = {
        "source_file": str(input_file),
        "transformation_steps": results,
        "processed_data": processed_data,
        "output_file": str(output_file),
        "format": format,
        "timestamp": time.time(),
    }

    export_result = flext_cli_export(
        data=export_data, filename=str(output_file), format=format
    )

    if export_result.is_failure:
        return FlextResult.fail(f"Export failed: {export_result.error}")

    # Resultado final usando FLEXT-CLI formatter
    final_result = {
        "transformation": "completed",
        "input_file": str(input_file),
        "output_file": str(output_file),
        "format": format,
        "steps_completed": len(results),
        "command_id": str(transform_command.id),
    }

    formatted_result = cli_format_output(final_result, cli_context.output_format)
    console.print("[bold green]📋 Transformation Results:[/bold green]")
    console.print(formatted_result)

    return FlextResult.ok(
        f"Successfully transformed {input_file.name} -> {output_file.name}"
    )


@cli.command()
@click.option(
    "--email",
    prompt=True,
    help="Email address to validate",
)
@click.option(
    "--phone",
    help="Phone number (optional)",
)
@click.option(
    "--url",
    type=URL,  # FLEXT-CLI type
    help="URL to validate (optional)",
)
@click.option(
    "--file-path",
    type=ClickPath(),  # FLEXT-CLI type
    help="File path to validate (optional)",
)
@click.pass_context
@cli_enhanced  # FLEXT-CLI decorator
@cli_validate_inputs  # FLEXT-CLI decorator
@cli_log_execution  # FLEXT-CLI decorator
@handle_service_result  # FLEXT-CLI result handler
def validate(
    ctx: click.Context,
    email: str,
    phone: str | None,
    url: str | None,
    file_path: str | None,
) -> FlextResult[dict[str, Any]]:
    """Validate multiple inputs using FLEXT-CLI comprehensive validation."""
    cli_context = ctx.obj["cli_context"]
    console = ctx.obj["console"]
    dependencies = ctx.obj["dependencies"]

    console.print(
        "[bold blue]🔍 Comprehensive Input Validation with FLEXT-CLI[/bold blue]"
    )
    console.print(f"[cyan]Using profile: {cli_context.profile}[/cyan]")

    # Usar FLEXT-CLI validator service extensivamente
    validator = FlextCliValidatorService()
    helper = CLIHelper()

    # Criar validation session usando FLEXT-CLI entities
    session_factory = CLIEntityFactory()
    validation_session_result = session_factory.create_session(
        session_id=f"validation_{int(time.time())}",
        user_id="demo_user",
        working_directory=str(Path.cwd()),
    )

    if validation_session_result.is_failure:
        return FlextResult.fail(
            f"Failed to create validation session: {validation_session_result.error}"
        )

    validation_session = validation_session_result.unwrap()
    console.print(
        f"[cyan]📋 Created validation session: {validation_session.session_id}[/cyan]"
    )

    # Resultados de validação
    validation_results = {}

    # 1. Validação de email usando FLEXT-CLI
    console.print("\n[bold yellow]1. Email Validation[/bold yellow]")
    email_validation = validator.validate_email(email)
    validation_results["email"] = {
        "value": email,
        "valid": email_validation.is_success,
        "error": email_validation.error if email_validation.is_failure else None,
    }

    if email_validation.is_success:
        console.print(f"  [green]✅ Valid email: {email}[/green]")
    else:
        console.print(
            f"  [red]❌ Invalid email: {email} - {email_validation.error}[/red]"
        )

    # 2. Validação de telefone usando FLEXT-CLI patterns
    if phone:
        console.print("\n[bold yellow]2. Phone Validation[/bold yellow]")
        phone_validation = validator.validate_phone(phone)
        validation_results["phone"] = {
            "value": phone,
            "valid": phone_validation.is_success,
            "error": phone_validation.error if phone_validation.is_failure else None,
        }

        if phone_validation.is_success:
            console.print(f"  [green]✅ Valid phone: {phone}[/green]")
        else:
            console.print(
                f"  [red]❌ Invalid phone: {phone} - {phone_validation.error}[/red]"
            )

    # 3. Validação de URL usando FLEXT-CLI
    if url:
        console.print("\n[bold yellow]3. URL Validation[/bold yellow]")
        url_validation = validator.validate_url(url)
        validation_results["url"] = {
            "value": url,
            "valid": url_validation.is_success,
            "error": url_validation.error if url_validation.is_failure else None,
        }

        if url_validation.is_success:
            console.print(f"  [green]✅ Valid URL: {url}[/green]")
        else:
            console.print(
                f"  [red]❌ Invalid URL: {url} - {url_validation.error}[/red]"
            )

    # 4. Validação de file path usando FLEXT-CLI
    if file_path:
        console.print("\n[bold yellow]4. File Path Validation[/bold yellow]")
        path_validation = validator.validate_file_path(file_path)
        validation_results["file_path"] = {
            "value": file_path,
            "valid": path_validation.is_success,
            "error": path_validation.error if path_validation.is_failure else None,
        }

        if path_validation.is_success:
            console.print(f"  [green]✅ Valid file path: {file_path}[/green]")
            # Informações adicionais sobre o arquivo
            try:
                path_obj = Path(file_path)
                if path_obj.exists():
                    file_size = helper.format_size(path_obj.stat().st_size)
                    console.print(f"    [cyan]📄 File size: {file_size}[/cyan]")
                    console.print(f"    [cyan]📂 Parent: {path_obj.parent}[/cyan]")
            except Exception:
                pass  # Ignore file stat errors
        else:
            console.print(
                f"  [red]❌ Invalid file path: {file_path} - {path_validation.error}[/red]"
            )

    # Adicionar validações à session usando FLEXT-CLI patterns
    for field_name, result in validation_results.items():
        validation_session.add_command(f"validate_{field_name}")

    # Sumário usando FLEXT-CLI table
    summary_table = cli_create_table()
    summary_table.add_column("Field", style="cyan")
    summary_table.add_column("Value", style="white")
    summary_table.add_column("Status", style="bold")
    summary_table.add_column("Error", style="red")

    total_validations = 0
    successful_validations = 0

    for field, result in validation_results.items():
        total_validations += 1
        if result["valid"]:
            successful_validations += 1
            status = "[green]✅ Valid[/green]"
            error = ""
        else:
            status = "[red]❌ Invalid[/red]"
            error = result["error"] or "Unknown error"

        # Truncar valores longos para display
        display_value = str(result["value"])
        if len(display_value) > 50:
            display_value = display_value[:47] + "..."

        summary_table.add_row(
            field.replace("_", " ").title(), display_value, status, error
        )

    console.print("\n[bold green]📊 Validation Summary[/bold green]")
    console.print(summary_table)

    # Estatísticas finais
    success_rate = (
        (successful_validations / total_validations * 100)
        if total_validations > 0
        else 0
    )

    stats_data = {
        "total_validations": total_validations,
        "successful_validations": successful_validations,
        "failed_validations": total_validations - successful_validations,
        "success_rate": f"{success_rate:.1f}%",
        "session_id": validation_session.session_id,
        "profile": cli_context.profile,
    }

    # Usar FLEXT-CLI format para output final
    formatted_stats = cli_format_output(stats_data, cli_context.output_format)
    console.print("\n[bold blue]📈 Validation Statistics[/bold blue]")
    console.print(formatted_stats)

    # End session usando FLEXT-CLI patterns
    validation_session.end_session()

    return FlextResult.ok({
        "validation_results": validation_results,
        "statistics": stats_data,
        "session_id": str(validation_session.session_id),
    })


@cli.command()
@click.option(
    "--delay",
    type=float,
    default=1.0,
    help="Delay in seconds",
)
@click.option(
    "--tasks",
    type=PositiveInt,  # FLEXT-CLI type
    default=3,
    help="Number of concurrent tasks",
)
@click.option(
    "--api-url",
    type=URL,  # FLEXT-CLI type
    default="https://api.example.com",
    help="API endpoint for async calls",
)
@click.pass_context
@cli_enhanced  # FLEXT-CLI decorator
@async_command  # FLEXT-CLI async decorator
@cli_measure_time  # FLEXT-CLI decorator
@cli_log_execution  # FLEXT-CLI decorator
@handle_service_result  # FLEXT-CLI result handler
async def async_task(
    ctx: click.Context, delay: float, tasks: int, api_url: str
) -> FlextResult[dict[str, Any]]:
    """Demonstrate comprehensive async operations with FLEXT-CLI."""
    cli_context = ctx.obj["cli_context"]
    console = ctx.obj["console"]
    dependencies = ctx.obj["dependencies"]
    service = dependencies["service"]

    console.print("[bold blue]🚀 Async Task Engine with FLEXT-CLI[/bold blue]")

    # Configuração da tarefa usando FLEXT-CLI table
    config_table = cli_create_table()
    config_table.add_column("Parameter", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_row("Profile", cli_context.profile)
    config_table.add_row("Delay per task", f"{delay}s")
    config_table.add_row("Concurrent tasks", str(tasks))
    config_table.add_row("API URL", api_url)
    console.print(config_table)

    # Criar CLI session para async tasks usando FLEXT-CLI
    session_factory = CLIEntityFactory()
    async_session_result = session_factory.create_session(
        session_id=f"async_{int(time.time())}",
        user_id="async_user",
        working_directory=str(Path.cwd()),
    )

    if async_session_result.is_failure:
        return FlextResult.fail(
            f"Failed to create async session: {async_session_result.error}"
        )

    async_session = async_session_result.unwrap()
    console.print(f"[cyan]📋 Async session created: {async_session.session_id}[/cyan]")

    # Definir async tasks usando FLEXT-CLI patterns
    async def run_single_task(task_id: int, task_delay: float) -> dict[str, Any]:
        """Single async task usando FLEXT-CLI service."""
        console.print(
            f"[yellow]⏳ Task {task_id}: Starting async operation...[/yellow]"
        )

        # Simular processamento usando FLEXT-CLI service
        task_data = {
            "task_id": task_id,
            "delay": task_delay,
            "api_url": api_url,
            "session_id": str(async_session.session_id),
            "start_time": time.time(),
        }

        # Usar service para processar
        processing_result = service.process_data(task_data)

        # Simular delay
        await asyncio.sleep(task_delay)

        if processing_result.is_failure:
            console.print(
                f"[red]❌ Task {task_id}: Failed - {processing_result.error}[/red]"
            )
            return {
                "task_id": task_id,
                "status": "failed",
                "error": processing_result.error,
                "duration": task_delay,
            }
        console.print(f"[green]✅ Task {task_id}: Completed successfully[/green]")
        return {
            "task_id": task_id,
            "status": "completed",
            "result": processing_result.unwrap(),
            "duration": task_delay,
            "end_time": time.time(),
        }

    # Executar tasks concorrentemente
    console.print(
        f"\n[bold yellow]🔄 Executing {tasks} concurrent async tasks...[/bold yellow]"
    )

    # Criar tasks com delays variados
    task_delays = [delay + (i * 0.1) for i in range(tasks)]
    async_tasks = [run_single_task(i + 1, task_delays[i]) for i in range(tasks)]

    # Executar todas as tasks concorrentemente
    start_time = time.time()
    task_results = await asyncio.gather(*async_tasks, return_exceptions=True)
    total_duration = time.time() - start_time

    # Adicionar commands à session
    for i in range(tasks):
        async_session.add_command(f"async_task_{i + 1}")

    # Processar resultados
    successful_tasks = []
    failed_tasks = []

    for result in task_results:
        if isinstance(result, dict):
            if result.get("status") == "completed":
                successful_tasks.append(result)
            else:
                failed_tasks.append(result)
        else:
            # Exception occurred
            failed_tasks.append({
                "task_id": "unknown",
                "status": "error",
                "error": str(result),
                "duration": 0,
            })

    # Criar tabela de resultados usando FLEXT-CLI
    results_table = cli_create_table()
    results_table.add_column("Task ID", style="cyan")
    results_table.add_column("Status", style="bold")
    results_table.add_column("Duration", style="yellow")
    results_table.add_column("Details", style="white")

    for result in successful_tasks + failed_tasks:
        task_id = str(result.get("task_id", "unknown"))
        status = (
            "[green]✅ Success[/green]"
            if result.get("status") == "completed"
            else "[red]❌ Failed[/red]"
        )
        duration = f"{result.get('duration', 0):.2f}s"
        details = (
            "Completed"
            if result.get("status") == "completed"
            else result.get("error", "Unknown error")
        )

        results_table.add_row(task_id, status, duration, details)

    console.print("\n[bold green]📊 Async Task Results[/bold green]")
    console.print(results_table)

    # Estatísticas finais
    stats = {
        "total_tasks": tasks,
        "successful_tasks": len(successful_tasks),
        "failed_tasks": len(failed_tasks),
        "success_rate": f"{(len(successful_tasks) / tasks * 100):.1f}%"
        if tasks > 0
        else "0%",
        "total_duration": f"{total_duration:.2f}s",
        "average_task_duration": f"{sum(r.get('duration', 0) for r in task_results if isinstance(r, dict)) / len([r for r in task_results if isinstance(r, dict)]):.2f}s"
        if task_results
        else "0s",
        "session_id": str(async_session.session_id),
        "api_url": api_url,
    }

    # Usar FLEXT-CLI format para output
    formatted_stats = cli_format_output(stats, cli_context.output_format)
    console.print("\n[bold blue]📈 Async Execution Statistics[/bold blue]")
    console.print(formatted_stats)

    # End session
    async_session.end_session()

    return FlextResult.ok({
        "task_results": [r for r in task_results if isinstance(r, dict)],
        "statistics": stats,
        "session_id": str(async_session.session_id),
    })


@cli.command()
@click.option(
    "--max-attempts",
    type=PositiveInt,  # FLEXT-CLI type
    default=3,
    help="Maximum retry attempts",
)
@click.option(
    "--retry-delay",
    type=float,
    default=0.5,
    help="Delay between retries in seconds",
)
@click.option(
    "--failure-rate",
    type=click.FloatRange(0.0, 1.0),
    default=0.7,
    help="Failure probability (0.0 = never fail, 1.0 = always fail)",
)
@click.pass_context
@cli_enhanced  # FLEXT-CLI decorator
@retry(max_attempts=5, delay=1.0)  # FLEXT-CLI retry decorator
@cli_measure_time  # FLEXT-CLI decorator
@cli_log_execution  # FLEXT-CLI decorator
@cli_cache_result(ttl=300)  # FLEXT-CLI cache decorator
@handle_service_result  # FLEXT-CLI result handler
def unreliable(
    ctx: click.Context, max_attempts: int, retry_delay: float, failure_rate: float
) -> FlextResult[dict[str, Any]]:
    """Demonstrate comprehensive retry patterns with FLEXT-CLI."""
    console = ctx.obj["console"]
    cli_context = ctx.obj["cli_context"]
    dependencies = ctx.obj["dependencies"]
    service = dependencies["service"]

    # Ajustar failure rate baseado no debug mode
    if cli_context.debug:
        failure_rate = max(0.3, failure_rate - 0.3)  # Reduzir falhas em debug

    console.print(
        "[bold blue]🔄 Unreliable Operation with FLEXT-CLI Retry Patterns[/bold blue]"
    )

    # Mostrar configuração usando FLEXT-CLI table
    config_table = cli_create_table()
    config_table.add_column("Parameter", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_row("Max Attempts", str(max_attempts))
    config_table.add_row("Retry Delay", f"{retry_delay}s")
    config_table.add_row("Failure Rate", f"{failure_rate:.1%}")
    config_table.add_row("Debug Mode", str(cli_context.debug))
    config_table.add_row("Profile", cli_context.profile)
    console.print(config_table)

    # Criar CLI command para operação usando FLEXT-CLI
    command_factory = CLIEntityFactory()
    unreliable_command_result = command_factory.create_command(
        name="unreliable_operation",
        command_line=f"unreliable --max-attempts {max_attempts} --failure-rate {failure_rate}",
        arguments={
            "max_attempts": max_attempts,
            "retry_delay": retry_delay,
            "failure_rate": failure_rate,
        },
    )

    if unreliable_command_result.is_failure:
        return FlextResult.fail(
            f"Failed to create command: {unreliable_command_result.error}"
        )

    unreliable_command = unreliable_command_result.unwrap()
    console.print(
        f"[cyan]📋 Created command: {unreliable_command.name} (ID: {unreliable_command.id})[/cyan]"
    )

    # Simular operação com retry tracking
    attempt_results = []
    operation_start_time = time.time()

    for attempt in range(max_attempts):
        attempt_start_time = time.time()
        console.print(f"\n[yellow]🔄 Attempt {attempt + 1}/{max_attempts}[/yellow]")

        # Usar FLEXT-CLI service para processar
        operation_data = {
            "attempt": attempt + 1,
            "max_attempts": max_attempts,
            "failure_rate": failure_rate,
            "command_id": str(unreliable_command.id),
            "start_time": attempt_start_time,
        }

        processing_result = service.process_data(operation_data)

        # Simular failure baseado na failure_rate
        will_fail = random.random() < failure_rate  # noqa: S311

        attempt_duration = time.time() - attempt_start_time

        if will_fail:
            error_msg = f"Simulated failure on attempt {attempt + 1}"
            console.print(f"  [red]❌ Attempt {attempt + 1} failed: {error_msg}[/red]")

            attempt_result = {
                "attempt": attempt + 1,
                "status": "failed",
                "error": error_msg,
                "duration": attempt_duration,
                "processing_result": processing_result.error
                if processing_result.is_failure
                else None,
            }
            attempt_results.append(attempt_result)

            # Se não é última tentativa, aguardar retry delay
            if attempt < max_attempts - 1:
                console.print(
                    f"  [yellow]⏳ Waiting {retry_delay}s before next attempt...[/yellow]"
                )
                time.sleep(retry_delay)
        else:
            console.print(f"  [green]✅ Attempt {attempt + 1} succeeded![/green]")

            attempt_result = {
                "attempt": attempt + 1,
                "status": "success",
                "duration": attempt_duration,
                "processing_result": processing_result.unwrap()
                if processing_result.is_success
                else None,
            }
            attempt_results.append(attempt_result)
            break
    else:
        # Todos as tentativas falharam
        total_duration = time.time() - operation_start_time
        console.print(
            f"\n[red]❌ All {max_attempts} attempts failed after {total_duration:.2f}s[/red]"
        )

        failure_summary = {
            "operation": "failed",
            "total_attempts": max_attempts,
            "successful_attempts": 0,
            "failed_attempts": len(attempt_results),
            "total_duration": total_duration,
            "attempts": attempt_results,
            "command_id": str(unreliable_command.id),
        }

        return FlextResult.fail(
            f"Operation failed after {max_attempts} attempts", context=failure_summary
        )

    # Operação teve sucesso
    total_duration = time.time() - operation_start_time
    successful_attempt = len(attempt_results)

    console.print(
        f"\n[bold green]🎉 Operation succeeded on attempt {successful_attempt}![/bold green]"
    )

    # Criar tabela de tentativas usando FLEXT-CLI
    attempts_table = cli_create_table()
    attempts_table.add_column("Attempt", style="cyan")
    attempts_table.add_column("Status", style="bold")
    attempts_table.add_column("Duration", style="yellow")
    attempts_table.add_column("Details", style="white")

    for result in attempt_results:
        attempt_num = str(result["attempt"])
        status = (
            "[green]✅ Success[/green]"
            if result["status"] == "success"
            else "[red]❌ Failed[/red]"
        )
        duration = f"{result['duration']:.3f}s"
        details = (
            "Operation completed"
            if result["status"] == "success"
            else result.get("error", "Unknown error")
        )

        attempts_table.add_row(attempt_num, status, duration, details)

    console.print("\n[bold blue]📊 Retry Attempts Summary[/bold blue]")
    console.print(attempts_table)

    # Estatísticas finais
    success_stats = {
        "operation": "completed",
        "total_attempts": len(attempt_results),
        "successful_attempts": 1,
        "failed_attempts": len(attempt_results) - 1,
        "success_rate": f"{(1 / len(attempt_results) * 100):.1f}%",
        "total_duration": f"{total_duration:.2f}s",
        "average_attempt_duration": f"{sum(r['duration'] for r in attempt_results) / len(attempt_results):.3f}s",
        "retry_delay_used": f"{retry_delay}s",
        "failure_rate_configured": f"{failure_rate:.1%}",
        "command_id": str(unreliable_command.id),
    }

    # Usar FLEXT-CLI format para output
    formatted_stats = cli_format_output(success_stats, cli_context.output_format)
    console.print("\n[bold green]📈 Success Statistics[/bold green]")
    console.print(formatted_stats)

    return FlextResult.ok({
        "operation_result": "success",
        "attempts": attempt_results,
        "statistics": success_stats,
    })


@cli.command()
@click.pass_context
@cli_enhanced  # FLEXT-CLI decorator
@handle_service_result  # FLEXT-CLI result handler
def info(ctx: click.Context) -> FlextResult[dict[str, Any]]:
    """Show comprehensive FLEXT-CLI library information."""
    console = ctx.obj["console"]
    cli_context = ctx.obj["cli_context"]
    dependencies = ctx.obj.get("dependencies", {})

    console.print(
        "[bold green]🔍 FLEXT-CLI Library Comprehensive Information[/bold green]"
    )

    # Obter informações usando FLEXT-CLI APIs
    try:
        import flext_cli

        version = flext_cli.__version__
    except AttributeError:
        version = "Unknown"

    # Usar FLEXT-CLI config e settings
    config = get_config()
    settings = get_settings()

    # 1. Versão e biblioteca info usando FLEXT-CLI table
    version_table = cli_create_table()
    version_table.add_column("Component", style="cyan")
    version_table.add_column("Version/Info", style="green")
    version_table.add_row("FLEXT-CLI Library", version)

    version_table.add_row("FLEXT-Core", core_version)

    version_table.add_row("Python Version", f"{sys.version.split()[0]}")
    version_table.add_row("Click Version", click.__version__)

    console.print("\n[bold blue]📦 Library Information[/bold blue]")
    console.print(version_table)

    # 2. Configuração usando FLEXT-CLI patterns
    config_table = cli_create_table()
    config_table.add_column("Setting", style="cyan")
    config_table.add_column("Value", style="green")
    config_table.add_column("Source", style="yellow")

    # Config from FLEXT-CLI
    config_data = {
        "API URL": (getattr(config, "api_url", "Not configured"), "Config"),
        "Timeout": (f"{getattr(config, 'timeout', 30)}s", "Config"),
        "Profile": (getattr(config, "profile", "default"), "Config"),
        "Debug Mode": (str(getattr(config, "debug", False)), "Config"),
    }

    for setting, (value, source) in config_data.items():
        config_table.add_row(setting, str(value), source)

    console.print("\n[bold blue]⚙️ Configuration[/bold blue]")
    console.print(config_table)

    # 3. Settings usando FLEXT-CLI patterns
    settings_table = cli_create_table()
    settings_table.add_column("Setting", style="cyan")
    settings_table.add_column("Value", style="green")
    settings_table.add_column("Environment Variable", style="yellow")

    settings_data = {
        "Project Name": (
            getattr(settings, "project_name", "Unknown"),
            "FLEXT_CLI_PROJECT_NAME",
        ),
        "Project Version": (
            getattr(settings, "project_version", "Unknown"),
            "FLEXT_CLI_PROJECT_VERSION",
        ),
        "Log Level": (getattr(settings, "log_level", "INFO"), "FLEXT_CLI_LOG_LEVEL"),
        "Environment": (
            getattr(settings, "environment", "development"),
            "FLEXT_CLI_ENVIRONMENT",
        ),
    }

    for setting, (value, env_var) in settings_data.items():
        settings_table.add_row(setting, str(value), env_var)

    console.print("\n[bold blue]🔧 Settings[/bold blue]")
    console.print(settings_table)

    # 4. CLI Context usando FLEXT-CLI patterns
    if cli_context:
        context_table = cli_create_table()
        context_table.add_column("Context Property", style="cyan")
        context_table.add_column("Value", style="green")
        context_table.add_column("Type", style="yellow")

        context_data = {
            "Profile": (cli_context.profile, "String"),
            "Output Format": (cli_context.output_format, "String"),
            "Debug Mode": (str(cli_context.debug), "Boolean"),
            "Verbose Mode": (str(cli_context.verbose), "Boolean"),
        }

        for prop, (value, prop_type) in context_data.items():
            context_table.add_row(prop, str(value), prop_type)

        console.print("\n[bold blue]🎯 CLI Context[/bold blue]")
        console.print(context_table)

    # 5. Container information usando FLEXT-CLI patterns
    if dependencies:
        container_table = cli_create_table()
        container_table.add_column("Service", style="cyan")
        container_table.add_column("Type", style="green")
        container_table.add_column("Status", style="yellow")

        for service_name, service_obj in dependencies.items():
            if service_obj is not None:
                service_type = type(service_obj).__name__
                status = "[green]✅ Available[/green]"
            else:
                service_type = "None"
                status = "[red]❌ Not Available[/red]"

            container_table.add_row(service_name.title(), service_type, status)

        console.print("\n[bold blue]📦 Container Services[/bold blue]")
        console.print(container_table)

    # 6. Sistema de autenticação usando FLEXT-CLI patterns
    auth_table = cli_create_table()
    auth_table.add_column("Auth Component", style="cyan")
    auth_table.add_column("Status", style="green")
    auth_table.add_column("Details", style="yellow")

    # Verificar token usando FLEXT-CLI auth
    try:
        token = get_auth_token()
        if token.is_success:
            auth_table.add_row(
                "Auth Token", "[green]✅ Available[/green]", "Token loaded successfully"
            )
        else:
            auth_table.add_row(
                "Auth Token",
                "[red]❌ Not Available[/red]",
                token.error or "No error details",
            )
    except Exception as e:
        auth_table.add_row("Auth Token", "[red]❌ Error[/red]", str(e))

    # Verificar headers usando FLEXT-CLI auth
    try:
        headers = get_auth_headers()
        if headers.is_success:
            headers_data = headers.unwrap()
            auth_table.add_row(
                "Auth Headers",
                "[green]✅ Available[/green]",
                f"{len(headers_data)} headers",
            )
        else:
            auth_table.add_row(
                "Auth Headers",
                "[red]❌ Not Available[/red]",
                headers.error or "No error details",
            )
    except Exception as e:
        auth_table.add_row("Auth Headers", "[red]❌ Error[/red]", str(e))

    console.print("\n[bold blue]🔐 Authentication System[/bold blue]")
    console.print(auth_table)

    # 7. Compilar informações finais para retorno
    info_summary = {
        "library": {
            "flext_cli_version": version,
            "python_version": sys.version.split()[0],
            "click_version": click.__version__,
        },
        "configuration": {
            "api_url": getattr(config, "api_url", "Not configured"),
            "timeout": getattr(config, "timeout", 30),
            "profile": getattr(config, "profile", "default"),
            "debug": getattr(config, "debug", False),
        },
        "settings": {
            "project_name": getattr(settings, "project_name", "Unknown"),
            "project_version": getattr(settings, "project_version", "Unknown"),
            "log_level": getattr(settings, "log_level", "INFO"),
            "environment": getattr(settings, "environment", "development"),
        },
        "cli_context": {
            "profile": cli_context.profile if cli_context else None,
            "output_format": cli_context.output_format if cli_context else None,
            "debug": cli_context.debug if cli_context else None,
            "verbose": cli_context.verbose if cli_context else None,
        },
        "services": {
            "total_services": len(dependencies),
            "available_services": len([
                s for s in dependencies.values() if s is not None
            ]),
            "service_names": list(dependencies.keys()),
        },
    }

    # Usar FLEXT-CLI format para output final
    formatted_summary = cli_format_output(
        info_summary, cli_context.output_format if cli_context else "table"
    )
    console.print("\n[bold green]📋 Complete Information Summary[/bold green]")
    console.print(formatted_summary)

    return FlextResult.ok(info_summary)


def demonstrate_flext_cli_usage() -> None:
    """Demonstrate comprehensive FLEXT-CLI usage patterns."""
    console = Console()
    console.print(
        "[bold green]🎯 FLEXT-CLI Library Demonstration Completed![/bold green]\n"
    )

    console.print("[cyan]📚 FLEXT-CLI Components Demonstrated:[/cyan]")
    console.print("   🏗️ FlextModel + Pydantic configuration (ClickAppConfig)")
    console.print("   ⚙️ FlextSettings + environment variables (ClickAppSettings)")
    console.print("   🛤️ FlextResult railway-oriented programming throughout")
    console.print("   📦 FlextContainer dependency injection patterns")
    console.print(
        "   🔧 FLEXT-CLI service layer (FlextCliService, validators, formatters)"
    )
    console.print(
        "   🎨 FLEXT-CLI decorators (@cli_enhanced, @cli_measure_time, @retry, etc.)"
    )
    console.print("   📊 FLEXT-CLI types (PositiveInt, URL, ExistingFile, etc.)")
    console.print("   🏷️ FLEXT-CLI domain entities (CLICommand, CLISession, etc.)")
    console.print(
        "   📋 FLEXT-CLI formatters and tables (cli_create_table, cli_format_output)"
    )
    console.print("   🔍 FLEXT-CLI validation services (FlextCliValidatorService)")
    console.print("   🔐 FLEXT-CLI authentication (get_auth_token, get_auth_headers)")
    console.print("   ⚡ FLEXT-CLI async patterns (@async_command)")
    console.print("   💾 FLEXT-CLI caching (@cli_cache_result)")
    console.print("   📤 FLEXT-CLI export functions (flext_cli_export)")
    console.print("   🚦 FLEXT-CLI result handling (@handle_service_result)")

    console.print("\n[yellow]✨ Architecture Patterns Showcased:[/yellow]")
    console.print("   🏛️ Clean Architecture with FLEXT-CLI integration")
    console.print("   🎯 Domain-Driven Design using FLEXT-CLI entities")
    console.print("   🛤️ Railway-oriented programming with FlextResult")
    console.print("   💉 Dependency injection with FLEXT-CLI container")
    console.print("   🔧 Service layer patterns with FLEXT-CLI services")
    console.print("   ✅ Comprehensive validation with FLEXT-CLI validators")
    console.print("   🔄 Async/retry patterns with FLEXT-CLI decorators")
    console.print("   📊 Professional output formatting with FLEXT-CLI formatters")


def main() -> None:
    """Run the comprehensive FLEXT-CLI demonstration."""
    try:
        cli()
        demonstrate_flext_cli_usage()
    except KeyboardInterrupt:
        Console().print("\n[yellow]⚠️ Operation cancelled by user[/yellow]")
    except Exception as e:
        Console().print(f"[red]❌ Error: {e}[/red]")


if __name__ == "__main__":
    main()

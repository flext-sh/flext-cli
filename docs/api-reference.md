# FLEXT CLI API Reference

<!-- TOC START -->

- [Imports essenciais](#imports-essenciais)
- [Facade `FlextCli`](#facade-flextcli)
  - [Métodos principais](#mtodos-principais)
- [Base para aplicativos Typer (`FlextCliAppBase`)](#base-para-aplicativos-typer-flextcliappbase)
- [Serviço `FlextCliCore`](#servio-flextclicore)
- [Serviço `FlextCliCmd`](#servio-flextclicmd)
- [Saída e exibição](#sada-e-exibio)
- [Prompts interativos (`FlextCliPrompts`)](#prompts-interativos-flextcliprompts)
- [I/O de arquivos (`FlextCliFileTools`)](#io-de-arquivos-flextclifiletools)
- [Related Documentation](#related-documentation)

<!-- TOC END -->

Referência alinhada ao código-fonte do **flext-cli** 0.10.0. Última revisão: 2025-02-06.

- **Facade**: `FlextCli` expõe serviços e utilidades como atributos e mantém wrappers de conveniência (`print`, `create_table`, `create_tree`).
- **Resultados**: todas as operações retornam `FlextResult[T]` para composições seguras.
- **Isolamento de frameworks**: Typer/Click apenas em `cli.py`; Rich/Tabulate restritos a `formatters.py` e `services/tables.py`.

## Imports essenciais

```python
from flext_cli import (
    FlextCli,                  # Facade principal
    FlextCliCore,              # Serviço de registro/execução de comandos
    FlextCliCmd,               # Operações auxiliares de configuração
    FlextCliOutput,            # Formatação e exibição
    FlextCliPrompts,           # Interação com usuário
    FlextCliTables,            # Tabelas ASCII via Tabulate
    FlextCliFileTools,         # I/O de arquivos
    FlextCliFormatters,        # Saída Rich
    FlextCliSettings,            # Configuração validada (singleton)
    FlextCliContext,           # Contexto imutável
    FlextCliModels,            # Modelos Pydantic
    FlextCliConstants,         # Constantes compartilhadas
)
from flext_core import FlextResult
```

## Facade `FlextCli`

Acesso direto aos serviços `core`, `cmd`, `output`, `prompts`, `tables`, às utilidades `formatters`, `file_tools`, `utilities` e ao `config` compartilhado.

### Métodos principais

- **Autenticação**: `authenticate(credentials)`, `validate_credentials(username, password)`, `save_auth_token(token)`, `get_auth_token()`, `is_authenticated()`, `clear_auth_tokens()`.
- **Registro de CLI**: decoradores `command(name=None)` e `group(name=None)` para Click/Typer via `cli.py`.
- **Execução**: `execute()` retorna o status consolidado dos componentes, e `execute_cli()` confirma a disponibilidade do framework.
- **Wrappers de compatibilidade**: `print(message, style=None)`, `create_table(data, headers=None, title=None)`, `print_table(table)`, `create_tree(label)`.

```python
cli = FlextCli()
cli.authenticate({"username": "user", "password": "pass"})
cli.core.register_command(cli.Models.CliCommand(name="hello", handler="handlers:hello"))
cli.print("ready", style="bold green")
```

## Base para aplicativos Typer (`FlextCliAppBase`)

Classe abstrata para CLIs completos com Typer. Defina `app_name`, `app_help` e `config_class`, registre comandos em `_register_commands()` e use `execute_cli()` para invocar a aplicação.

- `orchestrate_workflow(steps, step_names=None, continue_on_failure=False, progress_callback=None)` executa uma sequência de etapas retornando `WorkflowResult`.
- `_resolve_cli_args(args)` normaliza argumentos para execução e testes.

## Serviço `FlextCliCore`

Registro de comandos, configuração, sessões e plugins.

- **Comandos**: `register_command(command)`, `get_command(name)`, `list_commands()`, `execute_command(name)`, `execute_cli_command_with_context(command, context)`.
- **Configuração**: `update_configuration(data)`, `get_configuration()`, `load_configuration(path)`, `save_configuration(path)`, `validate_configuration(config)`, `get_config()`.
- **Sessões/Perfis**: `create_profile(profile_name, data=None)`, `start_session(session_id, profile=None)`, `end_session()`, `is_session_active()`, `get_session_statistics()`.
- **Diagnóstico e caches**: `health_check()`, `get_service_info()`, `get_command_statistics()`, `create_ttl_cache(cache_name, ttl_seconds, maxsize)`, `memoize(cache_name)`, `get_cache_stats(cache_name)`.
- **Plugins**: `register_plugin(name, plugin)`, `discover_plugins()`, `call_plugin_hook(hook_name)` e utilitários de inspeção (`get_handlers()`, `get_plugins()`, `get_sessions()`, `get_commands()`, `get_formatters()`).

## Serviço `FlextCliCmd`

Ponte para operações de configuração persistida.

- `show_config_paths()`
- `validate_config()`
- `get_config_info()`
- `set_config_value(key, value)`
- `get_config_value(key)`
- `show_config()`
- `execute(**kwargs)` retorna o status do serviço.

## Saída e exibição

- **`FlextCliOutput`**: `format_data(data, format_type, headers=None, title=None)`, `format_json`, `format_yaml`, `format_csv`, `format_table`, `format_as_tree`, `create_progress_bar`, além de helpers de exibição (`print_message`, `print_error`, `print_success`, `print_warning`, `display_data`).
- **`FlextCliFormatters`**: wrappers Rich para `print(message, style=None)` e `create_tree(label)`.
- **`FlextCliTables`**: `create_table`, `create_simple_table`, `create_grid_table`, `create_markdown_table`, `create_html_table`, `create_latex_table`, `create_rst_table`, `list_formats()`, `print_available_formats()`.

## Prompts interativos (`FlextCliPrompts`)

- Entrada: `prompt_text`, `prompt`, `prompt_history`, `clear_prompt_history`.
- Confirmação: `prompt_confirmation`, `confirm`.
- Seleção: `prompt_choice`, `select_from_options`.
- Senhas e feedback: `prompt_password`, `print_status`, `print_success`, `print_error`, `print_warning`, `print_info`.
- Progresso: `create_progress`, `with_progress`.

## I/O de arquivos (`FlextCliFileTools`)

- Texto/binário: `read_text_file`, `write_text_file`, `read_binary_file`, `write_binary_file`.
- Estruturado: `read_json_file`, `write_json_file`, `read_yaml_file`, `write_yaml_file`, `read_csv_file`, `write_csv_file`.
- Utilidades: normalização de caminhos, detecção de formato por extensão e operações com zip via `_save_file_by_extension`.

Use este arquivo em conjunto com `docs/architecture.md` para compreender as fronteiras entre serviços, utilidades e frameworks.

## Related Documentation

**Within Project**:

- [Getting Started](getting-started.md) - Installation and basic usage
- [Architecture](architecture.md) - Architecture and design patterns
- [Development Guide](development.md) - Contributing and extending

**Across Projects**:

- [flext-core Foundation](https://github.com/organization/flext/tree/main/flext-core/docs/api-reference/foundation.md) - Core APIs and patterns
- [flext-core Railway-Oriented Programming](https://github.com/organization/flext/tree/main/flext-core/docs/guides/railway-oriented-programming.md) - FlextResult patterns

**External Resources**:

- [PEP 257 - Docstring Conventions](https://peps.python.org/pep-0257/)
- [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html)

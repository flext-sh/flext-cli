"""Dependency injection container for FLEXT-CLI.

Using Lato framework for clean dependency injection.
"""

from __future__ import annotations

import os
import pathlib
from typing import TYPE_CHECKING

from lato import Container
from lato import DependencyProvider
from lato.di import DiContainer

from flext_cli.application.handlers import CreateConfigHandler
from flext_cli.application.handlers import DeleteConfigHandler
from flext_cli.application.handlers import DisablePluginHandler
from flext_cli.application.handlers import EnablePluginHandler
from flext_cli.application.handlers import EndSessionHandler
from flext_cli.application.handlers import ExecuteCommandHandler
from flext_cli.application.handlers import GetCommandHistoryHandler
from flext_cli.application.handlers import InstallPluginHandler
from flext_cli.application.handlers import ListCommandsHandler
from flext_cli.application.handlers import ListConfigsHandler
from flext_cli.application.handlers import ListPluginsHandler
from flext_cli.application.handlers import StartSessionHandler
from flext_cli.application.handlers import UninstallPluginHandler
from flext_cli.application.handlers import UpdateConfigHandler
from flext_cli.application.handlers import ValidateConfigHandler
from flext_cli.infrastructure.config import CLIConfig
from flext_cli.infrastructure.persistence.repositories import (
    PostgreSQLCLICommandRepository,
)
from flext_cli.infrastructure.persistence.repositories import (
    PostgreSQLCLIConfigRepository,
)
from flext_cli.infrastructure.persistence.repositories import (
    PostgreSQLCLIPluginRepository,
)
from flext_cli.infrastructure.persistence.repositories import (
    PostgreSQLCLISessionRepository,
)
from flext_cli.infrastructure.ports import BashCommandExecutor
from flext_cli.infrastructure.ports import ClickCommandParser
from flext_cli.infrastructure.ports import FileConfigStorage
from flext_cli.infrastructure.ports import RichOutputFormatter
from flext_cli.infrastructure.ports import YamlConfigValidator

if TYPE_CHECKING:
    from flext_cli.domain.ports import CLICommandRepository
    from flext_cli.domain.ports import CLIConfigRepository
    from flext_cli.domain.ports import CLIPluginRepository
    from flext_cli.domain.ports import CLISessionRepository
    from flext_cli.domain.ports import CommandExecutor
    from flext_cli.domain.ports import CommandParser
    from flext_cli.domain.ports import ConfigStorage
    from flext_cli.domain.ports import ConfigValidator
    from flext_cli.domain.ports import OutputFormatter


class CLIContainer(Container):
    """Dependency injection container for FLEXT-CLI."""

    # Configuration
    config: CLIConfig = DependencyProvider(
        lambda: CLIConfig(
            api_url=os.getenv("FLX_API_URL", "http://localhost:8000"),
            api_token=os.getenv("FLX_API_TOKEN", ""),
            config_dir=pathlib.Path(os.getenv("FLX_CONFIG_DIR", "~/.flx")).expanduser(),
            cache_dir=pathlib.Path(os.getenv("FLX_CACHE_DIR", "~/.flx/cache")).expanduser(),
            output_format=os.getenv("FLX_OUTPUT_FORMAT", "table"),
            no_color=os.getenv("FLX_NO_COLOR", "false").lower() == "true",
            pager=os.getenv("FLX_PAGER", "less"),
            editor=os.getenv("FLX_EDITOR", "vim"),
            profile=os.getenv("FLX_PROFILE", "development"),
            profiles_file=pathlib.Path(os.getenv("FLX_PROFILES_FILE", "~/.flx/profiles.yaml")).expanduser(),
            debug=os.getenv("FLX_DEBUG", "false").lower() == "true",
            trace=os.getenv("FLX_TRACE", "false").lower() == "true",
            log_level=os.getenv("FLX_LOG_LEVEL", "INFO"),
            log_file=pathlib.Path(os.getenv("FLX_LOG_FILE", "~/.flx/cli.log")).expanduser(),
            connect_timeout=int(os.getenv("FLX_CONNECT_TIMEOUT", "10")),
            read_timeout=int(os.getenv("FLX_READ_TIMEOUT", "30")),
            command_timeout=int(os.getenv("FLX_COMMAND_TIMEOUT", "300")),
            database_url=os.getenv("DATABASE_URL", "postgresql://localhost/flext_cli"),
        ),
    )

    # Repositories
    command_repository: CLICommandRepository = DependencyProvider(
        lambda config: PostgreSQLCLICommandRepository(config.database_url),
        config,
    )

    config_repository: CLIConfigRepository = DependencyProvider(
        lambda config: PostgreSQLCLIConfigRepository(config.database_url),
        config,
    )

    session_repository: CLISessionRepository = DependencyProvider(
        lambda config: PostgreSQLCLISessionRepository(config.database_url),
        config,
    )

    plugin_repository: CLIPluginRepository = DependencyProvider(
        lambda config: PostgreSQLCLIPluginRepository(config.database_url),
        config,
    )

    # Services
    command_executor: CommandExecutor = DependencyProvider(
        lambda config: BashCommandExecutor(config.command_timeout),
        config,
    )

    command_parser: CommandParser = DependencyProvider(
        ClickCommandParser,
    )

    output_formatter: OutputFormatter = DependencyProvider(
        RichOutputFormatter,
        config,
    )

    config_storage: ConfigStorage = DependencyProvider(
        lambda config: FileConfigStorage(config.config_dir),
        config,
    )

    config_validator: ConfigValidator = DependencyProvider(
        YamlConfigValidator,
    )

    # Handlers
    execute_command_handler: ExecuteCommandHandler = DependencyProvider(
        ExecuteCommandHandler,
        command_repository,
        command_executor,
        session_repository,
        config,
    )

    create_config_handler: CreateConfigHandler = DependencyProvider(
        CreateConfigHandler,
        config_repository,
        config_validator,
        config_storage,
        config,
    )

    update_config_handler: UpdateConfigHandler = DependencyProvider(
        UpdateConfigHandler,
        config_repository,
        config_validator,
        config_storage,
        config,
    )

    delete_config_handler: DeleteConfigHandler = DependencyProvider(
        DeleteConfigHandler,
        config_repository,
        config_storage,
        config,
    )

    validate_config_handler: ValidateConfigHandler = DependencyProvider(
        ValidateConfigHandler,
        config_repository,
        config_validator,
        config,
    )

    start_session_handler: StartSessionHandler = DependencyProvider(
        StartSessionHandler,
        session_repository,
        config,
    )

    end_session_handler: EndSessionHandler = DependencyProvider(
        EndSessionHandler,
        session_repository,
        config,
    )

    install_plugin_handler: InstallPluginHandler = DependencyProvider(
        InstallPluginHandler,
        plugin_repository,
        config,
    )

    uninstall_plugin_handler: UninstallPluginHandler = DependencyProvider(
        UninstallPluginHandler,
        plugin_repository,
        config,
    )

    enable_plugin_handler: EnablePluginHandler = DependencyProvider(
        EnablePluginHandler,
        plugin_repository,
        config,
    )

    disable_plugin_handler: DisablePluginHandler = DependencyProvider(
        DisablePluginHandler,
        plugin_repository,
        config,
    )

    list_commands_handler: ListCommandsHandler = DependencyProvider(
        ListCommandsHandler,
        command_repository,
        command_parser,
        output_formatter,
        config,
    )

    get_command_history_handler: GetCommandHistoryHandler = DependencyProvider(
        GetCommandHistoryHandler,
        command_repository,
        output_formatter,
        config,
    )

    list_configs_handler: ListConfigsHandler = DependencyProvider(
        ListConfigsHandler,
        config_repository,
        output_formatter,
        config,
    )

    list_plugins_handler: ListPluginsHandler = DependencyProvider(
        ListPluginsHandler,
        plugin_repository,
        output_formatter,
        config,
    )


def create_cli_container() -> CLIContainer:
    """Create and configure CLI dependency injection container.

    Returns:
        Configured CLI container instance.

    """
    container = CLIContainer()

    # Initialize container
    di_container = DiContainer()
    container.wire(di_container)

    return container


# Global container instance
cli_container = create_cli_container()

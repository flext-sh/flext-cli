"""Configuration for FLEXT-CLI infrastructure.

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from pathlib import Path


class CLIConfig:
    """CLI configuration."""

    # API settings
    api_url: str = "http://localhost:8000"
    api_token: str = ""

    # Directory settings
    config_dir: str = "~/.flx"
    cache_dir: str = "~/.flx/cache"

    # Output settings
    output_format: str = "table"  # table, json, yaml, csv
    no_color: bool = False
    pager: str = "less"
    editor: str = "vim"

    # Profile settings
    profile: str = "development"
    profiles_file: str = "~/.flx/profiles.yaml"

    # Debug settings
    debug: bool = False
    trace: bool = False
    log_level: str = "INFO"
    log_file: str = "~/.flx/cli.log"

    # Timeout settings
    connect_timeout: int = 10
    read_timeout: int = 30
    command_timeout: int = 300

    # Database settings
    database_url: str = "postgresql://localhost/flext_cli"
    database_pool_size: int = 20
    database_max_overflow: int = 40

    # Auto-completion settings
    completion_enabled: bool = True
    completion_cache_ttl: int = 3600  # 1 hour

    # Plugin settings
    plugin_dir: str = "~/.flx/plugins"
    plugin_auto_update: bool = False
    plugin_registry_url: str = "https://registry.flext.sh"

    # Security settings
    verify_ssl: bool = True
    token_file: str = "~/.flx/token"

    # Performance settings
    max_concurrent_commands: int = 5
    history_max_entries: int = 1000

    # UI settings
    show_progress: bool = True
    confirm_destructive: bool = True

    @property
    def expanded_config_dir(self) -> Path:
        """Get expanded configuration directory path.

        Returns:
            Expanded configuration directory path.

        """
        return Path(self.config_dir).expanduser()

    @property
    def expanded_cache_dir(self) -> Path:
        """Get expanded cache directory path.

        Returns:
            Expanded cache directory path.

        """
        return Path(self.cache_dir).expanduser()

    @property
    def expanded_plugin_dir(self) -> Path:
        """Get expanded plugin directory path.

        Returns:
            Expanded plugin directory path.

        """
        return Path(self.plugin_dir).expanduser()

    @property
    def expanded_log_file(self) -> Path:
        """Get expanded log file path.

        Returns:
            Expanded log file path.

        """
        return Path(self.log_file).expanduser()

    @property
    def expanded_token_file(self) -> Path:
        """Get expanded token file path.

        Returns:
            Expanded token file path.

        """
        return Path(self.token_file).expanduser()

    @property
    def expanded_profiles_file(self) -> Path:
        """Get expanded profiles file path.

        Returns:
            Expanded profiles file path.

        """
        return Path(self.profiles_file).expanduser()

    @property
    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled.

        Returns:
            True if debug mode is enabled or log level is DEBUG.

        """
        return self.debug or self.log_level == "DEBUG"

    @property
    def is_api_configured(self) -> bool:
        """Check if API is configured.

        Returns:
            True if both API URL and token are configured.

        """
        return self.api_url != "" and self.api_token != ""

    @property
    def supports_color(self) -> bool:
        """Check if color output is supported.

        Returns:
            True if color output is supported and not disabled.

        """
        return not self.no_color and os.getenv("NO_COLOR") is None

    def ensure_directories(self) -> None:
        """Ensure all required directories exist.

        Creates configuration, cache, and plugin directories if they don't exist.
        """
        self.expanded_config_dir.mkdir(parents=True, exist_ok=True)
        self.expanded_cache_dir.mkdir(parents=True, exist_ok=True)
        self.expanded_plugin_dir.mkdir(parents=True, exist_ok=True)

        # Ensure log directory exists
        self.expanded_log_file.parent.mkdir(parents=True, exist_ok=True)

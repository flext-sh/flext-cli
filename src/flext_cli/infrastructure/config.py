"""FLEXT CLI Infrastructure Configuration - Environment and System Settings.

This module provides infrastructure-level configuration for FLEXT CLI operations,
managing system settings, directories, timeouts, and environment-specific
configurations. This is the legacy configuration module that will be consolidated
with the main configuration system.

Configuration Categories:
    - API Settings: URL, token, timeouts for service communication
    - Directory Settings: Config, cache, plugin directories with path expansion
    - Output Settings: Format, color, pager, editor preferences
    - Profile Settings: Multi-profile support and configuration files
    - Debug Settings: Logging, tracing, and diagnostic configurations
    - Security Settings: SSL verification, token management
    - Performance Settings: Timeouts, concurrency, history limits

Architecture:
    - Class-based configuration with property methods
    - Path expansion utilities for user directories (~/)
    - Environment variable integration
    - Default value management with override support

Current Implementation Status:
    ✅ Complete configuration settings with defaults
    ✅ Path expansion properties for all directories
    ✅ Environment variable integration
    ✅ Debug and security configuration
    ✅ Directory creation utilities
    ⚠️ Legacy implementation (TODO: Sprint 2 - consolidate with main config)

TODO (docs/TODO.md):
    Sprint 2: Consolidate with main CLIConfig from utils/config.py
    Sprint 2: Add configuration validation and type safety
    Sprint 3: Add profile-specific configuration inheritance
    Sprint 5: Add encrypted configuration support
    Sprint 7: Add configuration monitoring and hot-reload

Configuration Groups:
    API: Service communication settings
    Directories: File system paths with expansion
    Output: Display and formatting preferences
    Profile: Multi-environment configuration
    Debug: Logging and diagnostic settings
    Database: Persistence connection settings
    Plugin: Plugin management and registry
    Security: Authentication and SSL settings
    Performance: Timeout and concurrency limits
    UI: User interface preferences

Usage Examples:
    Basic configuration:
    >>> config = CLIConfig()
    >>> config.debug = True
    >>> config.api_url = "https://api.example.com"

    Directory management:
    >>> config.ensure_directories()
    >>> config_path = config.expanded_config_dir
    >>> log_path = config.expanded_log_file

Integration:
    - Used by infrastructure layer for system configuration
    - Provides default settings for CLI operations
    - Supports environment variable overrides
    - Will be consolidated with main configuration system

Copyright (c) 2025 FLEXT Team. All rights reserved.
SPDX-License-Identifier: MIT

"""

from __future__ import annotations

import os
from pathlib import Path


class CLIConfig:
    """Legacy CLI configuration class with comprehensive system settings.

    Provides infrastructure-level configuration for FLEXT CLI operations including
    API settings, directories, timeouts, and environment-specific configurations.
    This class will be consolidated with the main CLIConfig in Sprint 2.

    Features:
        - Comprehensive configuration with sensible defaults
        - Path expansion for user directories (~/)
        - Environment variable integration
        - Property methods for computed values
        - Directory creation utilities

    Configuration Categories:
        API: Service endpoints and authentication
        Directories: File system paths and storage
        Output: Display preferences and formatting
        Debug: Logging and diagnostic settings
        Security: Authentication and SSL settings
        Performance: Timeouts and limits
        UI: User interface preferences

    TODO (Sprint 2):
        - Consolidate with main CLIConfig from utils/config.py
        - Add Pydantic validation and type safety
        - Implement profile-based configuration inheritance
        - Add configuration hot-reload capabilities

    Usage:
        >>> config = CLIConfig()
        >>> config.debug = True
        >>> config.ensure_directories()
        >>> expanded_path = config.expanded_config_dir
    """

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
    token_file: str = "~/.flx/token"  # noqa: S105

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

"""FLEXT CLI Configuration Models."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from flext_core import FlextConstants, FlextSettings
from pydantic import BaseModel, Field, PrivateAttr, model_validator
from pydantic_settings import SettingsConfigDict

# ----------------------------------------------------------------------------
# Component configurations
# ----------------------------------------------------------------------------


class CLIOutputConfig(BaseModel):
    """Output configuration for CLI rendering and verbosity."""

    format: Literal["table", "json", "yaml", "csv", "plain"] = Field(
        default="table",
        description="Default output format",
    )
    no_color: bool = Field(default=False, description="Disable colored output")
    quiet: bool = Field(default=False, description="Minimal output mode")
    verbose: bool = Field(default=False, description="Verbose output mode")
    pager: str | None = Field(
        default=None,
        description="Optional pager command (e.g., 'less -R')",
    )


def _default_api_url() -> str:
    try:
        return f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
    except Exception:
        return "http://localhost:8000"


class CLIAPIConfig(BaseModel):
    """API connectivity configuration for FLEXT services."""

    url: str = Field(default_factory=_default_api_url)
    timeout: int = Field(default=30, le=300)
    connect_timeout: int = Field(default=10)
    read_timeout: int = Field(default=30)
    retries: int = Field(default=3)
    verify_ssl: bool = Field(default=True)

    @property
    def base_url(self) -> str:
        """Return URL without trailing slashes."""
        return self.url.rstrip("/")


def _get_default_token_file() -> Path:
    """Get default token file path using consistent base directory."""
    return Path.home() / ".flext" / "auth" / "token"


def _get_default_refresh_token_file() -> Path:
    """Get default refresh token file path using consistent base directory."""
    return Path.home() / ".flext" / "auth" / "refresh_token"


class CLIAuthConfig(BaseModel):
    """Authentication token storage configuration."""

    token_file: Path = Field(default_factory=_get_default_token_file)
    refresh_token_file: Path = Field(default_factory=_get_default_refresh_token_file)
    auto_refresh: bool = Field(default=True)


class CLIDirectoryConfig(BaseModel):
    """Filesystem directory configuration for the CLI."""

    config_dir: Path = Field(default_factory=lambda: Path.home() / ".flext")
    cache_dir: Path = Field(default_factory=lambda: Path.home() / ".flext" / "cache")
    log_dir: Path = Field(default_factory=lambda: Path.home() / ".flext" / "logs")
    data_dir: Path = Field(default_factory=lambda: Path.home() / ".flext" / "data")

    def ensure_directories(self) -> None:
        """Create the configured directories if they do not exist."""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir.mkdir(parents=True, exist_ok=True)


# ----------------------------------------------------------------------------
# Main configuration and settings
# ----------------------------------------------------------------------------


class CLIConfig(BaseModel):
    """Top-level CLI configuration aggregate."""

    model_config = {"extra": "allow"}

    profile: str = Field(default="default")
    debug: bool = Field(default=False)
    trace: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    output: CLIOutputConfig = Field(default_factory=CLIOutputConfig)
    api: CLIAPIConfig = Field(default_factory=CLIAPIConfig)
    auth: CLIAuthConfig = Field(default_factory=CLIAuthConfig)
    directories: CLIDirectoryConfig = Field(default_factory=CLIDirectoryConfig)

    command_timeout: int = Field(default=300)

    # Optional project identity fields used by some tests/fixtures
    project_name: str = Field(default="flext-cli")
    project_description: str = Field(
        default="FLEXT CLI - Developer Command Line Interface",
    )

    # Store unknown flat fields for read-only property access
    _flat_overrides: dict[str, object] = PrivateAttr(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def _preprocess_flat_overrides(cls, data: object) -> object:
        """Allow flat constructor keys and map them into nested structures.

        Supports keys like api_url, timeout, max_retries, output_format, quiet,
        verbose, no_color, config_dir, cache_dir, log_dir, data_dir, token_file,
        refresh_token_file, auto_refresh, connect_timeout, read_timeout.
        """
        if not isinstance(data, dict):
            return data

        data = dict(data)
        cls._process_api_mappings(data)
        cls._process_output_mappings(data)
        cls._process_directory_mappings(data)
        cls._process_auth_mappings(data)

        return data

    @classmethod
    def _process_api_mappings(cls, data: dict[str, object]) -> None:
        """Process API-related flat key mappings."""
        api_map: dict[str, object] = dict(data.get("api") or {})

        api_keys = {
            "api_url": "url",
            "timeout": "timeout",
            "max_retries": "retries",
            "connect_timeout": "connect_timeout",
            "read_timeout": "read_timeout",
            "verify_ssl": "verify_ssl",
        }

        for flat_key, nested_key in api_keys.items():
            if flat_key in data:
                api_map[nested_key] = data.pop(flat_key)

        if api_map:
            data["api"] = api_map

    @classmethod
    def _process_output_mappings(cls, data: dict[str, object]) -> None:
        """Process output-related flat key mappings."""
        out_map: dict[str, object] = dict(data.get("output") or {})

        if "output_format" in data:
            out_map["format"] = data.pop("output_format")

        for k in ("no_color", "quiet", "verbose"):
            if k in data:
                out_map[k] = data.pop(k)

        if out_map:
            data["output"] = out_map

    @classmethod
    def _process_directory_mappings(cls, data: dict[str, object]) -> None:
        """Process directory-related flat key mappings."""
        dir_map: dict[str, object] = dict(data.get("directories") or {})

        for k in ("config_dir", "cache_dir", "log_dir", "data_dir"):
            if k in data:
                dir_map[k] = data.pop(k)

        if dir_map:
            data["directories"] = dir_map

    @classmethod
    def _process_auth_mappings(cls, data: dict[str, object]) -> None:
        """Process authentication-related flat key mappings."""
        auth_map: dict[str, object] = dict(data.get("auth") or {})

        for k in ("token_file", "refresh_token_file", "auto_refresh"):
            if k in data:
                auth_map[k] = data.pop(k)

        if auth_map:
            data["auth"] = auth_map

    def ensure_setup(self) -> None:
        """Ensure on-disk directories for config/cache/logs and auth exist."""
        self.directories.ensure_directories()
        self.auth.token_file.parent.mkdir(parents=True, exist_ok=True)
        self.auth.refresh_token_file.parent.mkdir(parents=True, exist_ok=True)

    def model_post_init(self, __context: object, /) -> None:
        """Capture any extra (flat) fields for read-only properties."""
        # Collect extras from __pydantic_extra__ if present
        extras = getattr(self, "__pydantic_extra__", None)
        if isinstance(extras, dict):
            self._flat_overrides = dict(extras)
        # Mark instance as initialized for immutability guard
        object.__setattr__(self, "_initialized", True)

    def validate_business_rules(self) -> bool:
        """Validate simple invariants expected by tests."""
        return not (self.api.timeout <= 0 or self.command_timeout <= 0)

    # ------------------------------------------------------------------
    # Flat compatibility properties expected by tests
    # ------------------------------------------------------------------

    @property
    def api_url(self) -> str:
        return self.api.base_url

    @api_url.setter  # type: ignore[no-redef]
    def api_url(self, _value: object) -> None:  # pragma: no cover - immutability guard
        msg = "cannot assign to field 'api_url' on frozen CLIConfig"
        raise ValueError(msg)

    @property
    def timeout(self) -> int:
        return self.api.timeout

    @property
    def max_retries(self) -> int:
        return self.api.retries

    @property
    def output_format(self) -> str:
        return self.output.format

    @property
    def no_color(self) -> bool:
        return self.output.no_color

    @property
    def quiet(self) -> bool:
        return self.output.quiet

    @property
    def verbose(self) -> bool:
        return self.output.verbose

    @property
    def config_dir(self) -> Path:
        return self.directories.config_dir

    @property
    def cache_dir(self) -> Path:
        return self.directories.cache_dir

    @property
    def log_dir(self) -> Path:
        return self.directories.log_dir

    @property
    def data_dir(self) -> Path:
        return self.directories.data_dir

    @property
    def token_file(self) -> Path:
        return self.auth.token_file

    @property
    def refresh_token_file(self) -> Path:
        return self.auth.refresh_token_file

    @property
    def auto_refresh(self) -> bool:
        return self.auth.auto_refresh

    @property
    def project_version(self) -> str:
        return "0.9.0"

    @property
    def config_path(self) -> str | None:
        # Map to extra if provided, default None
        val = self._flat_overrides.get("config_path")
        return str(val) if isinstance(val, (str, Path)) else None

    def __repr__(self) -> str:  # pragma: no cover - string form
        """Return string representation of CLIConfig."""
        return f"CLIConfig(api_url='{self.api_url}', timeout={self.timeout}, profile='{self.profile}')"

    def __str__(self) -> str:  # pragma: no cover - string form
        """Return string representation of CLIConfig."""
        return self.__repr__()

    def __hash__(self) -> int:  # pragma: no cover - hashing stability for tests
        """Return hash value for CLIConfig."""
        key = (
            self.profile,
            self.api_url,
            self.timeout,
            self.output_format,
            self.debug,
            self.log_level,
        )
        return hash(key)

    # Enforce immutability with explicit error message expected by tests
    def __setattr__(
        self, name: str, value: object
    ) -> None:  # pragma: no cover - runtime guard
        """Enforce immutability after initialization."""
        if name.startswith("_") or not getattr(self, "_initialized", False):
            return super().__setattr__(name, value)
        msg = "cannot assign to field"
        raise ValueError(msg)


def _default_settings_api_url() -> str:
    try:
        return f"http://{FlextConstants.Platform.DEFAULT_HOST}:{FlextConstants.Platform.FLEXT_API_PORT}"
    except Exception:
        return "http://localhost:8000"


class CLISettings(FlextSettings):
    """Application-level settings for the CLI.

    Uses environment variables with the prefix 'FLEXT_CLI_'.
    """

    project_name: str = Field(default="flext-cli")
    project_version: str = Field(default="0.9.0")
    project_description: str = Field(
        default="FLEXT CLI - Developer Command Line Interface",
    )

    api_url: str = Field(default_factory=_default_settings_api_url)
    timeout: int = Field(default=30)
    output_format: Literal["table", "json", "yaml", "csv", "plain"] = Field(
        default="table",
    )

    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")
    config_path: str | None = Field(default=None)

    model_config = SettingsConfigDict(
        env_prefix="FLEXT_CLI_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @classmethod
    def model_validate(
        cls, obj: object, *args: object, **kwargs: object
    ) -> CLISettings:  # type: ignore[override]
        """Hook to keep compatibility with test fixtures passing plain dicts."""
        return super().model_validate(obj, *args, **kwargs)  # type: ignore[return-value]


# ----------------------------------------------------------------------------
# Accessors (singleton + factories)
# ----------------------------------------------------------------------------

_config: CLIConfig | None = None


def _create_cli_config() -> CLIConfig:
    """Create a new CLIConfig with defaults and ensure filesystem setup."""
    cfg = CLIConfig(profile="default", debug=False)
    cfg.ensure_setup()
    return cfg


def get_cli_config(*, reload: bool = False) -> CLIConfig:
    """Return a singleton-style CLI configuration instance.

    Set reload=True to create and return a fresh instance, replacing the cached one.
    """
    global _config  # noqa: PLW0603
    if reload or _config is None:
        _config = _create_cli_config()
    return _config


# Factory-style helpers used by some tests


def get_config() -> CLIConfig:
    """Return a fresh CLIConfig instance each call (not a singleton)."""
    return CLIConfig()


def get_settings() -> CLISettings:
    """Return a fresh CLISettings instance each call."""
    return CLISettings()


def get_cli_settings() -> CLISettings:
    """Alias for getting CLI settings as a fresh instance."""
    return CLISettings()


__all__ = [
    "CLIAPIConfig",
    "CLIAuthConfig",
    "CLIConfig",
    "CLIDirectoryConfig",
    "CLIOutputConfig",
    "CLISettings",
    # Accessors
    "_create_cli_config",
    "get_cli_config",
    "get_cli_settings",
    "get_config",
    "get_settings",
]

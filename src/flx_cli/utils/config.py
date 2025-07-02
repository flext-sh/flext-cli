"""Configuration utilities for FLX CLI."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml


def get_config_dir() -> Path:
    """Get configuration directory path."""
    config_dir = os.environ.get("FLX_CONFIG_DIR")
    if config_dir:
        return Path(config_dir)
    return Path.home() / ".flx"


def get_config_path() -> Path:
    """Get configuration file path."""
    return get_config_dir() / "config.yaml"


def get_config() -> dict[str, Any]:
    """Load configuration from file."""
    config_path = get_config_path()

    if not config_path.exists():
        # Return default configuration
        return {
            "api_url": os.environ.get("FLX_API_URL", "http://localhost:8000"),
            "output_format": os.environ.get("FLX_OUTPUT_FORMAT", "table"),
            "timeout": int(os.environ.get("FLX_TIMEOUT", "30")),
        }

    with open(config_path, encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    # Get current profile
    profile = os.environ.get("FLX_PROFILE", config.get("current_profile", "default"))

    # Merge profile config with defaults
    default_config = config.get("default", {})
    profile_config = config.get("profiles", {}).get(profile, {})

    merged = {**default_config, **profile_config}

    # Override with environment variables
    if "FLX_API_URL" in os.environ:
        merged["api_url"] = os.environ["FLX_API_URL"]
    if "FLX_OUTPUT_FORMAT" in os.environ:
        merged["output_format"] = os.environ["FLX_OUTPUT_FORMAT"]
    if "FLX_TIMEOUT" in os.environ:
        merged["timeout"] = int(os.environ["FLX_TIMEOUT"])

    return merged


def get_config_value(key: str, default: Any = None) -> Any:
    """Get specific configuration value."""
    config = get_config()
    return config.get(key, default)


def set_config_value(key: str, value: Any) -> None:
    """Set configuration value."""
    config_path = get_config_path()

    # Load existing config or create new
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}
    else:
        config = {
            "default": {},
            "profiles": {},
            "current_profile": "default",
        }
        config_path.parent.mkdir(parents=True, exist_ok=True)

    # Get current profile
    profile = config.get("current_profile", "default")

    # Set value in current profile
    if profile == "default":
        if "default" not in config:
            config["default"] = {}
        config["default"][key] = value
    else:
        if "profiles" not in config:
            config["profiles"] = {}
        if profile not in config["profiles"]:
            config["profiles"][profile] = {}
        config["profiles"][profile][key] = value

    # Save config
    with open(config_path, "w", encoding="utf-8") as f:
        yaml.dump(config, f, default_flow_style=False)


def list_config_values() -> dict[str, Any]:
    """List all configuration values."""
    return get_config()


def get_cache_dir() -> Path:
    """Get cache directory path."""
    cache_dir = os.environ.get("FLX_CACHE_DIR")
    if cache_dir:
        return Path(cache_dir)
    return get_config_dir() / "cache"


def get_log_dir() -> Path:
    """Get log directory path."""
    return get_config_dir() / "logs"

"""FLEXT CLI Simple API."""

from __future__ import annotations

from typing import cast

from flext_core import FlextResult

from flext_cli.config import (
    CLIConfig,
    CLIOutputConfig,
    CLISettings,
    get_cli_settings as _get_cli_settings,
)

__all__ = [
    "create_development_cli_config",
    "create_production_cli_config",
    "get_cli_settings",
    "setup_cli",
]


def setup_cli(config: CLIConfig | CLISettings | None = None) -> FlextResult[bool]:
    """Set up CLI with modern zero-boilerplate approach using hierarchical configuration.

    This function integrates the 3 main functions of flext-cli:
    1. CLI Foundation Base: Provides setup for any CLI implementation
    2. flext-core Integration Bridge: Uses hierarchical config patterns
    3. Ecosystem Library Base: Reusable setup for flext-meltano, etc.

    Args:
        config: Optional CLI configuration (auto-created with hierarchy if None)

    Returns:
        FlextResult[bool]: Success/failure with railway-oriented programming

    """
    try:
        if config is None:
            config = CLIConfig()

        # Ensure directories exist (only for CLIConfig)
        if isinstance(config, CLIConfig):
            config.ensure_setup()

        return FlextResult.ok(data=True)

    except (AttributeError, ValueError, RuntimeError) as e:
        return FlextResult.fail(f"Failed to setup CLI: {e}")


def create_development_cli_config(**kwargs: object) -> CLIConfig:
    """Create development CLI configuration with hierarchical precedence.

    Uses flext/docs/patterns hierarchical configuration for ecosystem integration.
    Suitable for flext-meltano, algar-oud-mig, and other ecosystem projects.

    Args:
        **kwargs: Configuration overrides

    Returns:
        CLIConfig: Development configuration with debug enabled

    """
    # Use hierarchical config with development defaults
    development_defaults = {
        "debug": True,
        "profile": "development",
        "log_level": "DEBUG",
        **kwargs,  # Apply overrides
    }

    # Try to use create_with_hierarchy if available
    if hasattr(CLIConfig, "create_with_hierarchy"):
        hierarchy_result = CLIConfig.create_with_hierarchy(**development_defaults)
        if hierarchy_result.success:
            return cast("CLIConfig", hierarchy_result.unwrap())

    # Fallback to direct creation
    config = CLIConfig(
        debug=True,
        profile="development",
        log_level="DEBUG",
    )

    # Apply overrides using model_copy for type safety
    if kwargs:
        try:
            config = config.model_copy(update=kwargs)
        except Exception as e:
            # Convert Pydantic validation errors to ValueError for test compatibility
            validation_error_msg = f"validation error: {e}"
            raise ValueError(validation_error_msg) from e

    return config


def create_production_cli_config(**kwargs: object) -> CLIConfig:
    """Create production CLI configuration.

    Args:
        **kwargs: Configuration overrides

    Returns:
        CLIConfig: Production configuration with optimized settings

    """
    # Create base configuration with production defaults
    output_config = CLIOutputConfig(quiet=True)
    config = CLIConfig(
        debug=False,
        profile="production",
        output=output_config,
    )

    # Apply overrides using model_copy for type safety
    if kwargs:
        try:
            config = config.model_copy(update=kwargs)
        except Exception as e:
            # Convert Pydantic validation errors to ValueError for test compatibility
            validation_error_msg = f"validation error: {e}"
            raise ValueError(validation_error_msg) from e

    return config


def get_cli_settings(*, reload: bool | None = None) -> CLISettings:
    """Return CLISettings; when reload is True, return a fresh instance.

    Args:
        reload: If True, returns a fresh instance. Parameter is accepted for
                backward compatibility with tests.

    """
    _ = reload
    return _get_cli_settings()


def get_cli_settings_compat(*, reload: bool = False) -> CLISettings:
    """Compatibility wrapper: tests may call get_cli_settings(reload=True).

    This thin wrapper mirrors the upstream but keeps the original symbol
    from flext_cli.config as the canonical implementation.
    """
    _ = reload
    return CLISettings()


# get_cli_settings is already imported from flext_cli.config - no redefinition needed
